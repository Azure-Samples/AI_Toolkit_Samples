"""
backend/agents.py
──────────────────────────────────────────────────────────────────────────────
Microsoft Agent Framework – AI Tutor agents

Correct MAF imports per official docs:
  from agent_framework.openai import OpenAIChatClient        ← OpenAI / GitHub Models / Foundry Local
  from agent_framework.azure import AzureOpenAIChatClient    ← Azure OpenAI
  from agent_framework import Agent, tool                    ← Agent + tool decorator

  Agent takes:  client=  (NOT chat_client=)

MODEL_PROVIDER env var controls which client is built:
  github_models  →  OpenAIChatClient(base_url=..., api_key=GITHUB_TOKEN)
  foundry_local  →  OpenAIChatClient(base_url=http://localhost:5272/v1)
  azure_openai   →  AzureOpenAIChatClient(...)
  openai         →  OpenAIChatClient()   ← default, reads OPENAI_API_KEY env var
──────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

# ── Path fix ──────────────────────────────────────────────────────────────────
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent.resolve()))
# ─────────────────────────────────────────────────────────────────────────────

import json
import logging
import os
import re
import time
from typing import Annotated, Any

from pydantic import Field

from otel_setup import get_tracer, get_meter
from opentelemetry.trace import SpanKind, Status, StatusCode

logger = logging.getLogger(__name__)
tracer = get_tracer(__name__)
meter  = get_meter(__name__)

# ── Metrics ────────────────────────────────────────────────────────────────
_rag_query_counter = meter.create_counter(
    "ai_tutor.rag.queries",         description="Total RAG queries processed"
)
_eval_counter = meter.create_counter(
    "ai_tutor.eval.answers_scored", description="Total learner answers evaluated"
)
_latency_histogram = meter.create_histogram(
    "ai_tutor.agent.latency_ms",    description="Agent invocation latency (ms)"
)


# ══════════════════════════════════════════════════════════════════════════════
# CHAT CLIENT FACTORY
# Correct submodule imports per official MAF documentation:
#   agent_framework.openai  → OpenAIChatClient
#   agent_framework.azure   → AzureOpenAIChatClient
# ══════════════════════════════════════════════════════════════════════════════

def _build_chat_client():
    """
    Build the correct MAF chat client based on MODEL_PROVIDER env var.

    ┌─────────────────┬──────────────────────────────────────────────────────┐
    │ MODEL_PROVIDER  │ Client class + required env vars                     │
    ├─────────────────┼──────────────────────────────────────────────────────┤
    │ github_models   │ OpenAIChatClient(base_url, api_key=GITHUB_TOKEN)     │
    │ foundry_local   │ OpenAIChatClient(base_url=localhost:5272/v1)         │
    │ azure_openai    │ AzureOpenAIChatClient(endpoint, api_key or cred)     │
    │ openai          │ OpenAIChatClient()  ← reads OPENAI_API_KEY auto      │
    └─────────────────┴──────────────────────────────────────────────────────┘
    """
    provider = os.getenv("MODEL_PROVIDER", "openai").strip().lower()
    logger.info("Building MAF chat client — provider: %s", provider)

    # ── 1. GitHub Models ──────────────────────────────────────────────────
    if provider == "github_models":
        from agent_framework.openai import OpenAIChatClient

        token    = os.getenv("GITHUB_TOKEN")
        model_id = os.getenv("GITHUB_MODEL_ID", "gpt-4o-mini")
        endpoint = os.getenv("GITHUB_ENDPOINT", "https://models.github.ai/inference")

        if not token:
            raise EnvironmentError(
                "MODEL_PROVIDER=github_models requires GITHUB_TOKEN.\n"
                "Get a Personal Access Token at https://gh.io/models"
            )

        logger.info("GitHub Models → endpoint=%s  model=%s", endpoint, model_id)
        # OpenAIChatClient supports base_url for any OpenAI-compatible endpoint
        # This is the exact pattern from the official MAF integrations docs
        return OpenAIChatClient(
            api_key=token,
            model_id=model_id,
            base_url=endpoint,
        )

    # ── 2. Foundry Local (on-device) ─────────────────────────────────────
    if provider == "foundry_local":
        from agent_framework.openai import OpenAIChatClient

        model_id = os.getenv("FOUNDRYLOCAL_MODEL_DEPLOYMENT_NAME", "phi-3.5-mini")
        endpoint = os.getenv("FOUNDRYLOCAL_ENDPOINT", "http://localhost:5272/v1")

        logger.info("Foundry Local → endpoint=%s  model=%s", endpoint, model_id)
        # Foundry Local exposes an OpenAI-compatible endpoint.
        # OpenAIChatClient with base_url is the correct MAF pattern for this.
        return OpenAIChatClient(
            api_key="local",       # Foundry Local ignores the key value
            model_id=model_id,
            base_url=endpoint,
        )

    # ── 3. Azure OpenAI ───────────────────────────────────────────────────
    if provider == "azure_openai":
        from agent_framework.azure import AzureOpenAIChatClient

        endpoint   = os.getenv("AZURE_OPENAI_ENDPOINT")
        deployment = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME", "gpt-4o-mini")
        api_key    = os.getenv("AZURE_OPENAI_API_KEY")

        if not endpoint:
            raise EnvironmentError(
                "MODEL_PROVIDER=azure_openai requires AZURE_OPENAI_ENDPOINT"
            )

        logger.info("Azure OpenAI → endpoint=%s  deployment=%s", endpoint, deployment)

        if api_key:
            return AzureOpenAIChatClient(
                endpoint=endpoint,
                api_key=api_key,
                deployment_name=deployment,
            )
        # Keyless — Managed Identity / DefaultAzureCredential
        from azure.identity import DefaultAzureCredential
        return AzureOpenAIChatClient(
            endpoint=endpoint,
            credential=DefaultAzureCredential(),
            deployment_name=deployment,
        )

    # ── 4. OpenAI (default) ───────────────────────────────────────────────
    # OpenAIChatClient() automatically reads OPENAI_API_KEY and
    # OPENAI_CHAT_MODEL_ID from environment — no args needed.
    from agent_framework.openai import OpenAIChatClient

    model_id = os.getenv("OPENAI_CHAT_MODEL_ID", "gpt-4o-mini")
    api_key  = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise EnvironmentError(
            "MODEL_PROVIDER=openai (default) requires OPENAI_API_KEY."
        )

    logger.info("OpenAI → model=%s", model_id)
    return OpenAIChatClient(api_key=api_key, model_id=model_id)


# ══════════════════════════════════════════════════════════════════════════════
# TOOLS
# @tool decorator imported from agent_framework (top-level)
# ══════════════════════════════════════════════════════════════════════════════

def _make_rag_tools():
    from backend.rag_store import retrieve_chunks
    from agent_framework import tool

    @tool
    def search_documents(
        query: Annotated[
            str,
            Field(description="Search query to look up in the uploaded knowledge base"),
        ]
    ) -> str:
        """Search the uploaded study documents for relevant information."""
        chunks = retrieve_chunks(query, top_k=4)
        if not chunks:
            return (
                "No documents found in the knowledge base. "
                "Please upload study materials first via the RAG section."
            )
        parts = [
            f"[Source {i}: {c['source']} | relevance {c['score']}]\n{c['text']}"
            for i, c in enumerate(chunks, 1)
        ]
        return "\n\n---\n\n".join(parts)

    return [search_documents]


def _make_eval_tools():
    from agent_framework import tool

    @tool
    def fetch_rubric(
        topic: Annotated[
            str,
            Field(description="The topic or concept being tested"),
        ]
    ) -> str:
        """Retrieve the grading rubric for a given topic."""
        return (
            f"Grading rubric for topic: '{topic}'\n"
            "• Accuracy      (0-4 pts): Is the answer factually correct?\n"
            "• Completeness  (0-3 pts): Does it cover the key points?\n"
            "• Clarity       (0-2 pts): Is it clearly and concisely explained?\n"
            "• Examples      (0-1 pt ): Are concrete examples or evidence provided?\n"
            "Total: /10\n\n"
            "Grade bands: A >= 9, B >= 7, C >= 5, D >= 3, F < 3"
        )

    return [fetch_rubric]


# ══════════════════════════════════════════════════════════════════════════════
# AGENT SINGLETONS
# Agent takes:  client=  (not chat_client=)
# Per official MAF GitHub samples:
#   agent = Agent(client=OpenAIChatClient(), instructions="...", tools=[...])
# ══════════════════════════════════════════════════════════════════════════════

_rag_agent  = None
_eval_agent = None


def get_rag_agent():
    global _rag_agent
    if _rag_agent is None:
        from agent_framework import Agent
        _rag_agent = Agent(
            client=_build_chat_client(),
            name="RagTutorAgent",
            instructions=(
                "You are an expert AI Tutor. "
                "Always call `search_documents` first before answering — "
                "your response MUST be grounded in the uploaded study materials. "
                "Cite the source filename and relevance score for every key claim. "
                "If the documents don't contain enough information, say so honestly. "
                "Be encouraging, clear, and pedagogically sound."
            ),
            tools=_make_rag_tools(),
        )
        logger.info("RagTutorAgent ready (provider=%s)", os.getenv("MODEL_PROVIDER", "openai"))
    return _rag_agent


def get_eval_agent():
    global _eval_agent
    if _eval_agent is None:
        from agent_framework import Agent
        _eval_agent = Agent(
            client=_build_chat_client(),
            name="EvaluatorAgent",
            instructions=(
                "You are a rigorous but encouraging academic evaluator.\n"
                "When given a QUESTION and STUDENT ANSWER:\n"
                "1. Call `fetch_rubric` with the topic.\n"
                "2. Score the answer against the rubric.\n"
                "3. Return ONLY valid JSON (no markdown fences) matching this schema:\n"
                '{"score":<int 0-10>,"grade":"<A|B|C|D|F>",'
                '"strengths":["..."],"improvements":["..."],'
                '"detailed_feedback":"...","hint":"..."}\n'
                "Be specific and constructive. Score 0 if no answer is provided."
            ),
            tools=_make_eval_tools(),
        )
        logger.info("EvaluatorAgent ready (provider=%s)", os.getenv("MODEL_PROVIDER", "openai"))
    return _eval_agent


def reset_agents() -> None:
    """Drop cached agents — forces re-creation with current env vars."""
    global _rag_agent, _eval_agent
    _rag_agent = _eval_agent = None
    logger.info("Agent singletons reset.")


def active_provider_info() -> dict[str, str]:
    provider = os.getenv("MODEL_PROVIDER", "openai").strip().lower()
    info: dict[str, str] = {"provider": provider}
    if provider == "github_models":
        info["model"]    = os.getenv("GITHUB_MODEL_ID", "gpt-4o-mini")
        info["endpoint"] = os.getenv("GITHUB_ENDPOINT", "https://models.github.ai/inference")
    elif provider == "foundry_local":
        info["model"]    = os.getenv("FOUNDRYLOCAL_MODEL_DEPLOYMENT_NAME", "phi-3.5-mini")
        info["endpoint"] = os.getenv("FOUNDRYLOCAL_ENDPOINT", "http://localhost:5272/v1")
    elif provider == "azure_openai":
        info["model"]    = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME", "gpt-4o-mini")
        info["endpoint"] = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    else:
        info["model"]    = os.getenv("OPENAI_CHAT_MODEL_ID", "gpt-4o-mini")
        info["endpoint"] = "https://api.openai.com"
    return info


# ══════════════════════════════════════════════════════════════════════════════
# HIGH-LEVEL WRAPPERS  (custom OTel spans + metrics)
# ══════════════════════════════════════════════════════════════════════════════

async def answer_rag_query(question: str) -> dict[str, Any]:
    with tracer.start_as_current_span(
        "ai_tutor.rag_query", kind=SpanKind.SERVER,
        attributes={
            "question.length":  len(question),
            "question.preview": question[:120],
            "model.provider":   os.getenv("MODEL_PROVIDER", "openai"),
        },
    ) as span:
        t0 = time.perf_counter()
        _rag_query_counter.add(1)
        try:
            result  = await get_rag_agent().run(question)
            answer  = str(result)
            elapsed = round((time.perf_counter() - t0) * 1000, 1)
            _latency_histogram.record(elapsed, {"agent": "RagTutorAgent"})
            span.set_attribute("answer.length", len(answer))
            span.set_attribute("latency_ms",    elapsed)
            span.set_status(Status(StatusCode.OK))
            return {"answer": answer, "latency_ms": elapsed}
        except Exception as exc:
            span.record_exception(exc)
            span.set_status(Status(StatusCode.ERROR, str(exc)))
            raise


async def evaluate_answer(
    question: str, student_answer: str, topic: str = ""
) -> dict[str, Any]:
    with tracer.start_as_current_span(
        "ai_tutor.evaluate_answer", kind=SpanKind.SERVER,
        attributes={
            "eval.question_preview": question[:120],
            "eval.answer_length":    len(student_answer),
            "eval.topic":            topic or "general",
            "model.provider":        os.getenv("MODEL_PROVIDER", "openai"),
        },
    ) as span:
        t0 = time.perf_counter()
        _eval_counter.add(1)
        try:
            prompt = (
                f"TOPIC: {topic or 'General'}\n"
                f"QUESTION: {question}\n"
                f"STUDENT ANSWER: {student_answer or '[No answer provided]'}"
            )
            result      = await get_eval_agent().run(prompt)
            result_text = str(result)
            elapsed     = round((time.perf_counter() - t0) * 1000, 1)
            _latency_histogram.record(elapsed, {"agent": "EvaluatorAgent"})

            json_match = re.search(r"\{.*\}", result_text, re.DOTALL)
            parsed: dict[str, Any] = {}
            if json_match:
                try:
                    parsed = json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass

            if not parsed:
                parsed = {
                    "score": 0, "grade": "N/A",
                    "strengths": [],
                    "improvements": ["Could not parse evaluation. Please try again."],
                    "detailed_feedback": result_text,
                    "hint": "",
                }

            span.set_attribute("eval.score", parsed.get("score", 0))
            span.set_attribute("eval.grade", parsed.get("grade",  "?"))
            span.set_attribute("latency_ms", elapsed)
            span.set_status(Status(StatusCode.OK))
            return {**parsed, "latency_ms": elapsed}

        except Exception as exc:
            span.record_exception(exc)
            span.set_status(Status(StatusCode.ERROR, str(exc)))
            raise
