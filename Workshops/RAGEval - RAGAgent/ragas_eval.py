"""
ragas_eval.py — Real RAGAS Evaluation Module
=============================================
Install:
    pip install ragas==0.2.15 langchain-openai==0.2.14 datasets==3.1.0

Root cause of "OPENAI_API_KEY must be set" error
-------------------------------------------------
ragas.evaluate() loops through metrics and calls llm_factory() /
embedding_factory() for any metric where .llm or .embeddings is None.
Both factories call ChatOpenAI() / OpenAIEmbeddings() with NO arguments
— they read ONLY from environment variables (OPENAI_API_KEY, OPENAI_BASE_URL).

Fix: two-pronged approach
  1. Set OPENAI_API_KEY=<github_token> and OPENAI_BASE_URL=<github_endpoint>
     in the environment BEFORE any ragas/langchain code runs, so every
     internal client creation succeeds.
  2. Instantiate every metric with llm= and embeddings= explicitly at
     construction time so metric.llm / metric.embeddings are never None
     and the factory functions are never called at all.
"""

from __future__ import annotations
import os

# ── TOP-LEVEL RAGAS IMPORTS ───────────────────────────────────────
try:
    from ragas import evaluate, EvaluationDataset
    from ragas.llms import LangchainLLMWrapper
    from ragas.embeddings import LangchainEmbeddingsWrapper
    from ragas.metrics import (
        Faithfulness,
        ResponseRelevancy,
        LLMContextPrecisionWithoutReference,
        LLMContextRecall,
    )
    from langchain_openai import ChatOpenAI, OpenAIEmbeddings
    RAGAS_AVAILABLE = True
    print("[RAGAS] ✅  ragas + langchain_openai loaded successfully")
except ImportError as e:
    RAGAS_AVAILABLE = False
    print(f"[RAGAS] ⚠️  Import failed ({e})")
    print("[RAGAS]     Run: pip install ragas==0.2.15 langchain-openai==0.2.14 datasets==3.1.0")


# ── RESULT ────────────────────────────────────────────────────────
class RAGASResult:
    def __init__(self, faithfulness, answer_relevancy,
                 context_precision, context_recall, eval_method):
        self.faithfulness        = round(faithfulness,      3)
        self.answer_relevancy    = round(answer_relevancy,  3)
        self.context_precision   = round(context_precision, 3)
        self.context_recall      = round(context_recall,    3)
        self.ragas_score         = round(
            (faithfulness + answer_relevancy + context_precision + context_recall) / 4, 3
        )
        self.eval_method = eval_method  # "ragas_llm_judge" | "keyword_heuristic"

    def to_dict(self):
        return {
            "faithfulness":      self.faithfulness,
            "answer_relevancy":  self.answer_relevancy,
            "context_precision": self.context_precision,
            "context_recall":    self.context_recall,
            "ragas_score":       self.ragas_score,
            "eval_method":       self.eval_method,
        }


# ── PUBLIC ENTRY POINT ────────────────────────────────────────────
def evaluate_with_ragas(
    question: str,
    answer: str,
    contexts: list,         # list[str] — retrieved chunk texts
    ground_truth: str,
    llm_client,             # openai.OpenAI instance — confirms LLM is live
    llm_model: str,         # e.g. "openai/gpt-4o-mini"
    llm_provider: str = "github",
) -> RAGASResult:
    if RAGAS_AVAILABLE and llm_client:
        try:
            return _run_real_ragas(
                question, answer, contexts, ground_truth,
                llm_model, llm_provider
            )
        except Exception as e:
            print(f"[RAGAS] Real eval error: {e} — falling back to heuristic")

    return _keyword_heuristic(question, answer, contexts, ground_truth)


# ── REAL RAGAS ────────────────────────────────────────────────────
def _run_real_ragas(question, answer, contexts, ground_truth,
                    llm_model, llm_provider):

    # ── Step 1: resolve endpoint + key ───────────────────────────
    if llm_provider == "foundry":
        from foundry_local import FoundryLocalManager
        alias    = os.getenv("FOUNDRY_MODEL_ALIAS", "phi-3.5-mini")
        manager  = FoundryLocalManager(alias)
        base_url = manager.endpoint
        api_key  = manager.api_key
    else:
        base_url = "https://models.github.ai/inference"
        api_key  = os.getenv("GITHUB_TOKEN", "")

    # ── Step 2: patch environment so ALL internal ragas/langchain
    #   client creation (including inside factories) uses our key ──
    _orig = {
        "OPENAI_API_KEY":  os.environ.get("OPENAI_API_KEY"),
        "OPENAI_BASE_URL": os.environ.get("OPENAI_BASE_URL"),
    }
    os.environ["OPENAI_API_KEY"]  = api_key
    os.environ["OPENAI_BASE_URL"] = base_url

    try:
        return _execute(question, answer, contexts, ground_truth,
                        llm_model, base_url, api_key)
    finally:
        # Restore originals even if eval throws
        for k, v in _orig.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def _execute(question, answer, contexts, ground_truth,
             llm_model, base_url, api_key):

    # ── Step 3: build judge LLM — pass BOTH old-style (openai_api_base /
    #   openai_api_key) AND new-style (base_url / api_key) params.
    #   langchain-openai 0.2.x accepts both; this future-proofs the code. ──
    langchain_llm = ChatOpenAI(
        model=llm_model,
        openai_api_base=base_url,
        openai_api_key=api_key,
        temperature=0,
        max_retries=2,
    )
    judge_llm = LangchainLLMWrapper(langchain_llm)

    # ── Step 4: build embeddings judge — same dual-param approach.
    #   Needed by ResponseRelevancy to measure semantic similarity. ──
    langchain_emb = OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_base=base_url,
        openai_api_key=api_key,
    )
    judge_emb = LangchainEmbeddingsWrapper(langchain_emb)

    # ── Step 5: instantiate every metric with llm= / embeddings= set
    #   at construction time. This ensures metric.llm is NEVER None
    #   when evaluate() runs its loop — so llm_factory() and
    #   embedding_factory() are never called at all. ──
    metrics = [
        Faithfulness(llm=judge_llm),
        ResponseRelevancy(llm=judge_llm, embeddings=judge_emb),
        LLMContextPrecisionWithoutReference(llm=judge_llm),
        LLMContextRecall(llm=judge_llm),
    ]

    # ── Step 6: build dataset ─────────────────────────────────────
    dataset = EvaluationDataset.from_list([{
        "user_input":         question,
        "response":           answer,
        "retrieved_contexts": contexts,   # list[str]
        "reference":          ground_truth,
    }])

    # ── Step 7: run evaluation, also passing llm + embeddings at the
    #   evaluate() level as a final safety net ──────────────────────
    result = evaluate(
        dataset=dataset,
        metrics=metrics,
        llm=judge_llm,
        embeddings=judge_emb,
        raise_exceptions=False,
    )

    # ── Step 8: extract scores ────────────────────────────────────
    row = result.to_pandas().iloc[0]

    faith = float(row.get("faithfulness",                            0) or 0)
    relev = float(row.get("response_relevancy",                      0) or 0)
    prec  = float(row.get("llm_context_precision_without_reference", 0) or 0)
    recl  = float(row.get("context_recall",                          0) or 0)

    print(f"[RAGAS] ✅  faith={faith:.2f}  relev={relev:.2f}  "
          f"prec={prec:.2f}  recl={recl:.2f}")

    return RAGASResult(faith, relev, prec, recl, "ragas_llm_judge")


# ── KEYWORD HEURISTIC FALLBACK ────────────────────────────────────
def _keyword_heuristic(question, answer, contexts, ground_truth):
    """
    Word-overlap proxy — used only when RAGAS is unavailable.
    Labelled 'keyword_heuristic' so you always know which path ran.
    """
    def safe_div(a, b):
        return a / b if b > 0 else 0.0

    a_w = set(answer.lower().split())
    c_w = set(w for ctx in contexts for w in ctx.lower().split())
    q_w = set(question.lower().split())
    g_w = set(ground_truth.lower().split())

    faith = min(safe_div(len(a_w & c_w), len(a_w)) * 2.2, 1.0)
    relev = min(safe_div(len(q_w & a_w), len(q_w)) * 3.5, 1.0)
    prec_scores = [safe_div(len(q_w & set(ctx.lower().split())), len(q_w)) for ctx in contexts]
    prec  = min(safe_div(sum(prec_scores), len(prec_scores)) * 2.5 if prec_scores else 0.0, 1.0)
    recl  = min(safe_div(len(g_w & c_w), len(g_w)) * 2.0, 1.0)

    return RAGASResult(faith, relev, prec, recl, "keyword_heuristic")
