"""
main.py  –  AI Tutor Backend
──────────────────────────────────────────────────────────────────────────────
FastAPI application powered by Microsoft Agent Framework (RC).

Endpoints:
  GET  /health                       – liveness probe + telemetry status
  POST /api/rag/upload               – upload a text/PDF file into the vector store
  GET  /api/rag/documents            – list ingested documents
  POST /api/rag/query                – RAG question answering
  DELETE /api/rag/clear              – wipe the vector store

  POST /api/eval/submit              – evaluate a learner's answer
  GET  /api/telemetry/traces         – last N in-memory trace summaries (dev UI)
  GET  /api/telemetry/metrics        – current metric snapshot

Startup order:
  1. OpenTelemetry (telemetry.setup_telemetry)
  2. FastAPI OTel instrumentation
  3. Agent lazy-loading (first request)

Run:
  uvicorn main:app --host 0.0.0.0 --port 8000 --reload
──────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

# ── Path fix ──────────────────────────────────────────────────────────────────
# Ensure the project root (the folder containing main.py) is always on
# sys.path so that `import otel_setup` and `import backend` resolve correctly
# regardless of the working directory uvicorn is launched from.
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.resolve()))
# ─────────────────────────────────────────────────────────────────────────────

import io
import json
import logging
import os
import time
from collections import deque
from contextlib import asynccontextmanager
from typing import Any

from dotenv import load_dotenv

load_dotenv()

import uvicorn
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# ── Telemetry first ───────────────────────────────────────────────────────
from otel_setup import setup_telemetry, get_tracer, get_meter

tracer = get_tracer(__name__)

# In-memory ring buffer for the Dev Dashboard  (last 200 trace events)
_trace_log: deque[dict] = deque(maxlen=200)
_metrics_snapshot: dict[str, Any] = {
    "rag_queries": 0,
    "eval_queries": 0,
    "avg_rag_latency_ms": 0.0,
    "avg_eval_latency_ms": 0.0,
    "errors": 0,
    "startup_time": None,
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


# ── Lifespan ──────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    t0 = time.perf_counter()
    logger.info("▶  AI Tutor starting …")

    # 1. Telemetry
    setup_telemetry()

    # 2. Instrument FastAPI
    try:
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        FastAPIInstrumentor.instrument_app(app)
        logger.info("FastAPI OTel instrumentation active")
    except ImportError:
        logger.warning("opentelemetry-instrumentation-fastapi not installed – skipping")

    elapsed = round((time.perf_counter() - t0) * 1000, 1)
    _metrics_snapshot["startup_time"] = elapsed
    logger.info("▶  AI Tutor ready in %s ms", elapsed)

    yield

    logger.info("◀  AI Tutor shutting down …")


# ── FastAPI app ───────────────────────────────────────────────────────────

app = FastAPI(
    title="AI Tutor – Microsoft Agent Framework",
    description=(
        "Enterprise-grade AI Tutor with RAG, Q&A evaluation, "
        "and OpenTelemetry observability via Microsoft Agent Framework."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

cors_origin = os.getenv("CORS_ORIGIN", "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[cors_origin, "http://localhost:5500", "http://127.0.0.1:5500",
                   "http://localhost:3000", "http://127.0.0.1:8000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request / Response models ─────────────────────────────────────────────

class RagQueryRequest(BaseModel):
    question: str


class EvalSubmitRequest(BaseModel):
    question: str
    student_answer: str
    topic: str = ""


# ── Helper: trace logging to ring buffer ─────────────────────────────────

def _log_trace(event_type: str, data: dict[str, Any]) -> None:
    _trace_log.append(
        {
            "timestamp": time.strftime("%H:%M:%S"),
            "type": event_type,
            **data,
        }
    )


# ──────────────────────────────────────────────────────────────────────────
# Routes
# ──────────────────────────────────────────────────────────────────────────

@app.get("/api/provider", tags=["System"])
async def get_provider():
    """Return information about the currently active model provider."""
    from backend.agents import active_provider_info
    info = active_provider_info()
    return {
        "active": info,
        "available_providers": [
            {
                "id": "github_models",
                "label": "GitHub Models",
                "description": "Free inference via models.github.ai — needs GITHUB_TOKEN",
                "local": False,
            },
            {
                "id": "foundry_local",
                "label": "Foundry Local",
                "description": "On-device inference via Microsoft Foundry Local — no cloud required",
                "local": True,
            },
            {
                "id": "azure_openai",
                "label": "Azure OpenAI",
                "description": "Azure-hosted OpenAI models — needs AZURE_OPENAI_ENDPOINT",
                "local": False,
            },
            {
                "id": "openai",
                "label": "OpenAI",
                "description": "OpenAI API — needs OPENAI_API_KEY",
                "local": False,
            },
        ],
    }


class SwitchProviderRequest(BaseModel):
    provider: str


@app.post("/api/provider/switch", tags=["System"])
async def switch_provider(req: SwitchProviderRequest):
    """
    Hot-switch the model provider at runtime without restarting the server.
    Updates MODEL_PROVIDER in the process environment and resets agent singletons.
    Note: this does NOT persist across server restarts — edit .env for that.
    """
    valid = {"github_models", "foundry_local", "azure_openai", "openai"}
    if req.provider not in valid:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown provider '{req.provider}'. Must be one of: {sorted(valid)}",
        )
    os.environ["MODEL_PROVIDER"] = req.provider
    from backend.agents import reset_agents, active_provider_info
    reset_agents()
    info = active_provider_info()
    _log_trace("PROVIDER_SWITCH", {"new_provider": req.provider, **info})
    logger.info("Provider switched to: %s", req.provider)
    return {"status": "switched", "active": info}


@app.get("/health", tags=["System"])
async def health():
    return {
        "status": "ok",
        "service": "ai-tutor",
        "version": "1.0.0",
        "telemetry": {
            "otel_enabled": True,
            "otlp_endpoint": os.getenv("OTLP_ENDPOINT", "not configured"),
            "sensitive_data": os.getenv("ENABLE_SENSITIVE_DATA", "false"),
        },
    }


# ── RAG routes ────────────────────────────────────────────────────────────

@app.post("/api/rag/upload", tags=["RAG"])
async def upload_document(file: UploadFile = File(...)):
    """Upload a .txt or .pdf file into the RAG knowledge base."""
    with tracer.start_as_current_span("api.rag.upload") as span:
        span.set_attribute("file.name", file.filename or "unknown")
        span.set_attribute("file.content_type", file.content_type or "unknown")

        content = await file.read()
        filename = file.filename or "unknown.txt"

        # Decode text
        if filename.lower().endswith(".pdf"):
            # Try pdfminer for PDF text extraction
            try:
                from pdfminer.high_level import extract_text_to_fp
                from pdfminer.layout import LAParams

                output = io.StringIO()
                extract_text_to_fp(
                    io.BytesIO(content), output, laparams=LAParams(), output_type="text"
                )
                text = output.getvalue()
            except ImportError:
                # Fallback: treat bytes as UTF-8
                text = content.decode("utf-8", errors="replace")
        else:
            text = content.decode("utf-8", errors="replace")

        if not text.strip():
            raise HTTPException(status_code=400, detail="Document is empty or unreadable.")

        from backend.rag_store import ingest_document

        result = ingest_document(filename, text)
        _log_trace("RAG_INGEST", result)
        return JSONResponse({"status": "ingested", **result})


@app.get("/api/rag/documents", tags=["RAG"])
async def list_documents():
    from backend.rag_store import list_documents as _list
    return {"documents": _list()}


@app.delete("/api/rag/clear", tags=["RAG"])
async def clear_rag():
    from backend.rag_store import clear_store
    clear_store()
    _log_trace("RAG_CLEAR", {"message": "Vector store cleared"})
    return {"status": "cleared"}


@app.post("/api/rag/query", tags=["RAG"])
async def rag_query(req: RagQueryRequest):
    """Ask a question answered from the uploaded documents."""
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    t0 = time.perf_counter()
    _log_trace("RAG_QUERY_START", {"question": req.question[:120]})

    try:
        from backend.agents import answer_rag_query
        result = await answer_rag_query(req.question)

        _metrics_snapshot["rag_queries"] += 1
        prev_avg = _metrics_snapshot["avg_rag_latency_ms"]
        n = _metrics_snapshot["rag_queries"]
        _metrics_snapshot["avg_rag_latency_ms"] = round(
            prev_avg + (result["latency_ms"] - prev_avg) / n, 1
        )

        _log_trace(
            "RAG_QUERY_DONE",
            {
                "question": req.question[:80],
                "latency_ms": result["latency_ms"],
                "answer_length": len(result["answer"]),
            },
        )
        return result

    except Exception as exc:
        _metrics_snapshot["errors"] += 1
        _log_trace("RAG_QUERY_ERROR", {"error": str(exc)})
        logger.exception("RAG query failed")
        raise HTTPException(status_code=500, detail=str(exc))


# ── Evaluation routes ─────────────────────────────────────────────────────

@app.post("/api/eval/submit", tags=["Evaluation"])
async def submit_answer(req: EvalSubmitRequest):
    """Evaluate a learner's answer to a question using the Evaluator Agent."""
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    _log_trace(
        "EVAL_START",
        {
            "question": req.question[:80],
            "answer_length": len(req.student_answer),
            "topic": req.topic,
        },
    )

    try:
        from backend.agents import evaluate_answer
        result = await evaluate_answer(req.question, req.student_answer, req.topic)

        _metrics_snapshot["eval_queries"] += 1
        prev_avg = _metrics_snapshot["avg_eval_latency_ms"]
        n = _metrics_snapshot["eval_queries"]
        _metrics_snapshot["avg_eval_latency_ms"] = round(
            prev_avg + (result.get("latency_ms", 0) - prev_avg) / n, 1
        )

        _log_trace(
            "EVAL_DONE",
            {
                "score": result.get("score"),
                "grade": result.get("grade"),
                "latency_ms": result.get("latency_ms"),
            },
        )
        return result

    except Exception as exc:
        _metrics_snapshot["errors"] += 1
        _log_trace("EVAL_ERROR", {"error": str(exc)})
        logger.exception("Evaluation failed")
        raise HTTPException(status_code=500, detail=str(exc))


# ── Telemetry / Dev Dashboard routes ─────────────────────────────────────

@app.get("/api/telemetry/traces", tags=["Observability"])
async def get_traces(limit: int = 50):
    """Return the last N trace events from the in-memory ring buffer."""
    events = list(_trace_log)[-limit:]
    return {"traces": events[::-1], "total": len(_trace_log)}


@app.get("/api/telemetry/metrics", tags=["Observability"])
async def get_metrics():
    """Return a snapshot of current runtime metrics."""
    return {
        **_metrics_snapshot,
        "trace_buffer_size": len(_trace_log),
        "otel_service": "ai-tutor",
        "otlp_endpoint": os.getenv("OTLP_ENDPOINT", "not configured"),
    }


# ── Entry point ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    host = os.getenv("BACKEND_HOST", "0.0.0.0")
    port = int(os.getenv("BACKEND_PORT", "8000"))
    uvicorn.run("main:app", host=host, port=port, reload=True)
