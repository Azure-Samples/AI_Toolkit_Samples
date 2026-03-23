"""
ShopEval — CustomerBot RAG Agent
=================================
Real LLM (GitHub Models / Foundry Local) + Real RAGAS evaluation.

Environment variables:
  GitHub Models (default):
    export LLM_PROVIDER=github
    export GITHUB_TOKEN=github_pat_...
    export LLM_MODEL=openai/gpt-4o-mini

  Foundry Local:
    export LLM_PROVIDER=foundry
    export FOUNDRY_MODEL_ALIAS=phi-3.5-mini

To run:
    pip install -r requirements.txt
    uvicorn main:app --reload --port 8000
"""

import json
import os
import sys
from typing import Optional

# Load .env file automatically if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed — fall back to system environment variables

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI

# Add parent directory to path so ragas_eval.py is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ragas_eval import evaluate_with_ragas

# ── LLM CLIENT SETUP ─────────────────────────────────────────────
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "github").lower()

def _init_client():
    if LLM_PROVIDER == "foundry":
        try:
            from foundry_local import FoundryLocalManager
            alias   = os.getenv("FOUNDRY_MODEL_ALIAS", "phi-3.5-mini")
            manager = FoundryLocalManager(alias)
            client  = OpenAI(base_url=manager.endpoint, api_key=manager.api_key)
            model   = manager.get_model_info(alias).id
            print(f"[Foundry Local] model: {model}")
            return client, model
        except Exception as e:
            print(f"[Foundry] init failed: {e}")
            return None, "unavailable"
    else:
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            print("[GitHub Models] GITHUB_TOKEN not set — heuristic fallback active")
            return None, "unavailable"
        model = os.getenv("LLM_MODEL", "openai/gpt-4o-mini")
        client = OpenAI(base_url="https://models.github.ai/inference", api_key=token)
        print(f"[GitHub Models] model: {model}")
        return client, model

llm_client, LLM_MODEL = _init_client()

# ── APP ───────────────────────────────────────────────────────────
app = FastAPI(title="ShopEval API", version="3.0.0")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = BASE_DIR

with open(os.path.join(DATA_DIR, "knowledge_base.json")) as f:
    KNOWLEDGE_BASE = json.load(f)

with open(os.path.join(DATA_DIR, "test_dataset.json")) as f:
    TEST_DATASET = json.load(f)


# ── RETRIEVAL ─────────────────────────────────────────────────────
def retrieve_chunks(query: str, top_k: int = 3) -> list[dict]:
    """
    Keyword retrieval over the knowledge base.
    Replace with FAISS / Chroma + embeddings in production.
    """
    q_words = set(query.lower().split())
    scored = []
    for doc in KNOWLEDGE_BASE:
        overlap = len(q_words & set((doc["content"] + " " + doc["title"]).lower().split()))
        scored.append({**doc, "relevance_score": round(overlap / (len(q_words) + 1), 3)})
    scored.sort(key=lambda x: x["relevance_score"], reverse=True)
    return scored[:top_k]


# ── REAL LLM ANSWER GENERATION ────────────────────────────────────
def generate_answer(question: str, chunks: list[dict]) -> str:
    """
    Calls the LLM with a strict RAG prompt grounded in retrieved chunks.
    Falls back to returning the top chunk text if LLM is unavailable.
    """
    if not llm_client or not chunks or chunks[0]["relevance_score"] == 0:
        return chunks[0]["content"][:400] if chunks else "No relevant information found."

    context = "\n\n".join(f"[{c['title']}]\n{c['content']}" for c in chunks)

    try:
        resp = llm_client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful e-commerce customer support assistant for ShopBot. "
                        "Answer ONLY using the provided context. "
                        "If the answer is not clearly in the context, say so honestly. "
                        "Be concise, friendly, and accurate. "
                        "Do not make up policies or prices not mentioned in the context."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Context:\n{context}\n\nCustomer question: {question}\n\nAnswer:",
                },
            ],
            max_tokens=300,
            temperature=0.2,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"[LLM error] {e}")
        return chunks[0]["content"][:400]


# ── MODELS ────────────────────────────────────────────────────────
class QueryRequest(BaseModel):
    question: str
    top_k: Optional[int] = 3


# ── ROUTES ────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {
        "status":   "ShopEval API running ✅",
        "provider": LLM_PROVIDER,
        "model":    LLM_MODEL,
        "ragas":    "llm_judge (real RAGAS)" if llm_client else "keyword_heuristic (fallback)",
    }

@app.get("/knowledge-base")
def get_kb():
    return {"documents": KNOWLEDGE_BASE, "total": len(KNOWLEDGE_BASE)}

@app.get("/test-dataset")
def get_tests():
    return {"tests": TEST_DATASET, "total": len(TEST_DATASET)}

@app.post("/ask")
def ask(req: QueryRequest):
    chunks = retrieve_chunks(req.question, req.top_k)
    answer = generate_answer(req.question, chunks)
    return {"question": req.question, "answer": answer, "retrieved_chunks": chunks}

@app.post("/evaluate/single")
def evaluate_single(req: QueryRequest):
    # Look up ground truth from the test set
    ground_truth = next(
        (t["ground_truth"] for t in TEST_DATASET if t["question"].lower() == req.question.lower()),
        ""
    )

    chunks  = retrieve_chunks(req.question, req.top_k)
    answer  = generate_answer(req.question, chunks)

    # Pass plain text contexts (list[str]) to RAGAS
    contexts = [c["content"] for c in chunks]

    result = evaluate_with_ragas(
        question     = req.question,
        answer       = answer,
        contexts     = contexts,
        ground_truth = ground_truth or answer,   # use answer as fallback if no GT
        llm_client   = llm_client,
        llm_model    = LLM_MODEL,
        llm_provider = LLM_PROVIDER,
    )

    return {
        "question":         req.question,
        "answer":           answer,
        "ground_truth":     ground_truth or None,
        "retrieved_chunks": chunks,
        "metrics":          result.to_dict(),
        "passed":           result.ragas_score >= 0.70,
    }

@app.post("/evaluate/run")
def evaluate_run():
    results = []
    for test in TEST_DATASET:
        chunks   = retrieve_chunks(test["question"])
        answer   = generate_answer(test["question"], chunks)
        contexts = [c["content"] for c in chunks]

        result = evaluate_with_ragas(
            question     = test["question"],
            answer       = answer,
            contexts     = contexts,
            ground_truth = test["ground_truth"],
            llm_client   = llm_client,
            llm_model    = LLM_MODEL,
            llm_provider = LLM_PROVIDER,
        )

        results.append({
            "id":               test["id"],
            "question":         test["question"],
            "category":         test["category"],
            "answer":           answer,
            "ground_truth":     test["ground_truth"],
            "retrieved_chunks": chunks,
            "metrics":          result.to_dict(),
            "passed":           result.ragas_score >= 0.70,
        })

    total  = len(results)
    passed = sum(1 for r in results if r["passed"])
    avg    = lambda k: round(sum(r["metrics"][k] for r in results) / total, 3)
    method = results[0]["metrics"]["eval_method"] if results else "unknown"

    return {
        "summary": {
            "total_tests":  total,
            "passed":       passed,
            "failed":       total - passed,
            "pass_rate":    round(passed / total, 3),
            "eval_method":  method,
            "avg_metrics": {
                "faithfulness":      avg("faithfulness"),
                "answer_relevancy":  avg("answer_relevancy"),
                "context_precision": avg("context_precision"),
                "context_recall":    avg("context_recall"),
                "ragas_score":       avg("ragas_score"),
            },
        },
        "results": results,
    }
