"""
RAGEval — Bring Your Own Docs RAG Evaluator
============================================
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
import io
import os
import re
import sys
import time
from typing import Optional

# Load .env file automatically if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed — fall back to system environment variables

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI

import pypdf
import docx as python_docx

# Shared RAGAS module (ragas_eval.py lives alongside main.py)
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
        model  = os.getenv("LLM_MODEL", "openai/gpt-4o-mini")
        client = OpenAI(base_url="https://models.github.ai/inference", api_key=token)
        print(f"[GitHub Models] model: {model}")
        return client, model

llm_client, LLM_MODEL = _init_client()

# ── APP ───────────────────────────────────────────────────────────
app = FastAPI(title="RAGEval API", version="3.0.0")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

store: dict = {"documents": [], "test_cases": [], "last_run": None}


# ── FILE PARSING ──────────────────────────────────────────────────
def parse_pdf(data: bytes) -> str:
    reader = pypdf.PdfReader(io.BytesIO(data))
    return "\n\n".join(p.extract_text() for p in reader.pages if p.extract_text())

def parse_docx(data: bytes) -> str:
    doc = python_docx.Document(io.BytesIO(data))
    return "\n\n".join(p.text for p in doc.paragraphs if p.text.strip())

def parse_txt(data: bytes) -> str:
    return data.decode("utf-8", errors="ignore")

def chunk_text(text: str, chunk_size: int = 400, overlap: int = 80) -> list[str]:
    words = text.split()
    chunks, i = [], 0
    while i < len(words):
        chunk = " ".join(words[i: i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
        i += chunk_size - overlap
    return chunks


# ── REAL LLM: QUESTION GENERATION ────────────────────────────────
def generate_questions_llm(chunk: str, doc_title: str, n: int = 2) -> list[dict]:
    """
    Calls the LLM to produce n grounded Q&A pairs from a chunk.
    Returns list of dicts: {question, ground_truth, source_doc}
    Falls back to heuristic if LLM unavailable or fails.
    """
    if not llm_client:
        return _heuristic_questions(chunk, doc_title, n)

    prompt = (
        f"You are creating evaluation test cases for a RAG system.\n\n"
        f"Document: {doc_title}\n\n"
        f"Text:\n{chunk[:900]}\n\n"
        f"Generate exactly {n} question-answer pairs based ONLY on the text above.\n"
        f"Rules:\n"
        f"  - Questions must be answerable from this text alone\n"
        f"  - Ground truth answers should be 1-3 sentences, pulled from the text\n"
        f"  - Vary the question style (what/how/when/why)\n\n"
        f"Respond with valid JSON only (no markdown, no explanation):\n"
        f'[{{"question": "...", "ground_truth": "..."}}]'
    )

    try:
        resp = llm_client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": "You output valid JSON only. No markdown, no explanation."},
                {"role": "user",   "content": prompt},
            ],
            max_tokens=700,
            temperature=0.5,
        )
        raw = resp.choices[0].message.content.strip()
        # Strip markdown fences if model includes them
        raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.MULTILINE)
        raw = re.sub(r"\s*```$", "", raw, flags=re.MULTILINE).strip()

        pairs = json.loads(raw)
        return [
            {
                "question":    p["question"].strip(),
                "ground_truth": p["ground_truth"].strip(),
                "source_doc":  doc_title,
            }
            for p in pairs[:n]
            if "question" in p and "ground_truth" in p
            and len(p["question"]) > 10 and len(p["ground_truth"]) > 10
        ]
    except Exception as e:
        print(f"[Q-gen LLM error] {e} — using heuristic")
        return _heuristic_questions(chunk, doc_title, n)


def _heuristic_questions(chunk: str, doc_title: str, n: int) -> list[dict]:
    """Sentence-extraction fallback for question generation."""
    sentences = [s.strip() for s in re.split(r"[.!?]", chunk) if len(s.strip()) > 50]
    pairs = []
    for sent in sentences[:n * 2]:
        words = sent.split()
        if len(words) < 6:
            continue
        key = " ".join(words[:6]).lower().strip(",:;")
        pairs.append({
            "question":    f"What does the document say about {key}?",
            "ground_truth": sent.strip(),
            "source_doc":  doc_title,
        })
        if len(pairs) >= n:
            break
    return pairs


# ── RETRIEVAL ─────────────────────────────────────────────────────
def retrieve_chunks(query: str, top_k: int = 3) -> list[dict]:
    if not store["documents"]:
        return []
    q_words = set(query.lower().split())
    scored  = []
    for doc in store["documents"]:
        for chunk in doc["chunks"]:
            overlap = len(q_words & set(chunk.lower().split()))
            score   = round(overlap / (len(q_words) + 1), 3)
            scored.append({
                "id":              doc["id"],
                "title":           doc["title"],
                "content":         chunk,
                "relevance_score": score,
            })
    scored.sort(key=lambda x: x["relevance_score"], reverse=True)
    # One chunk per document to avoid redundancy
    seen, result = set(), []
    for item in scored:
        key = item["title"] + item["content"][:40]
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result[:top_k]


# ── REAL LLM ANSWER GENERATION ────────────────────────────────────
def generate_answer(question: str, chunks: list[dict]) -> str:
    if not llm_client or not chunks or chunks[0]["relevance_score"] == 0:
        if chunks:
            best = chunks[0]["content"]
            return best[:400] + ("..." if len(best) > 400 else "")
        return "I could not find relevant information in the uploaded documents."

    context = "\n\n".join(f"[{c['title']}]\n{c['content']}" for c in chunks)

    try:
        resp = llm_client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant that answers questions based on uploaded documents. "
                        "Answer ONLY using the provided context. "
                        "If the answer is not clearly in the context, say so. "
                        "Be concise and accurate."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Context:\n{context}\n\nQuestion: {question}\n\nAnswer:",
                },
            ],
            max_tokens=400,
            temperature=0.2,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"[LLM answer error] {e}")
        return chunks[0]["content"][:400] if chunks else "Error generating answer."


# ── PYDANTIC MODELS ───────────────────────────────────────────────
class TestCase(BaseModel):
    id: str
    question: str
    ground_truth: str
    source_doc: Optional[str] = ""

class TestCasesUpdate(BaseModel):
    test_cases: list[TestCase]

class AskRequest(BaseModel):
    question: str
    top_k: Optional[int] = 3

class EvalRequest(BaseModel):
    question: str
    ground_truth: str
    top_k: Optional[int] = 3


# ── ROUTES ────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {
        "status":      "RAGEval API running ✅",
        "provider":    LLM_PROVIDER,
        "model":       LLM_MODEL,
        "docs_loaded": len(store["documents"]),
        "test_cases":  len(store["test_cases"]),
        "ragas":       "llm_judge (real RAGAS)" if llm_client else "keyword_heuristic (fallback)",
    }

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    data     = await file.read()
    filename = file.filename or "unknown"
    ext      = filename.rsplit(".", 1)[-1].lower()

    try:
        if ext == "pdf":
            text = parse_pdf(data)
        elif ext == "docx":
            text = parse_docx(data)
        elif ext == "txt":
            text = parse_txt(data)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: .{ext}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Could not parse file: {e}")

    if not text.strip():
        raise HTTPException(status_code=422, detail="File is empty or unreadable.")

    chunks = chunk_text(text)
    doc_id = f"doc_{int(time.time())}_{len(store['documents'])}"
    title  = filename.rsplit(".", 1)[0].replace("_", " ").replace("-", " ").title()

    store["documents"].append({
        "id": doc_id, "title": title, "filename": filename,
        "text": text, "chunks": chunks,
        "char_count": len(text), "chunk_count": len(chunks),
    })

    return {
        "id": doc_id, "title": title, "filename": filename,
        "char_count": len(text), "chunk_count": len(chunks),
        "preview": text[:300] + ("..." if len(text) > 300 else ""),
    }

@app.get("/documents")
def list_documents():
    return {
        "documents": [
            {
                "id":          d["id"],
                "title":       d["title"],
                "filename":    d["filename"],
                "char_count":  d["char_count"],
                "chunk_count": d["chunk_count"],
                "preview":     d["text"][:200] + "...",
            }
            for d in store["documents"]
        ],
        "total": len(store["documents"]),
    }

@app.delete("/documents/{doc_id}")
def delete_document(doc_id: str):
    before = len(store["documents"])
    store["documents"] = [d for d in store["documents"] if d["id"] != doc_id]
    if len(store["documents"]) == before:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"deleted": doc_id}

@app.delete("/documents")
def clear_all():
    store.update({"documents": [], "test_cases": [], "last_run": None})
    return {"status": "cleared"}

@app.post("/generate-questions")
def generate_questions():
    if not store["documents"]:
        raise HTTPException(status_code=400, detail="No documents uploaded yet.")

    generated = []
    for doc in store["documents"]:
        # Sample up to 3 chunks spread across the document
        n_chunks = len(doc["chunks"])
        if n_chunks <= 3:
            sample = doc["chunks"]
        else:
            indices = [0, n_chunks // 2, n_chunks - 1]
            sample  = [doc["chunks"][i] for i in indices]

        for i, chunk in enumerate(sample):
            pairs = generate_questions_llm(chunk, doc["title"], n=2)
            for j, pair in enumerate(pairs):
                pair["id"] = f"q_{doc['id']}_{i}_{j}"
                generated.append(pair)

    generated = generated[:10]  # cap for demo manageability
    store["test_cases"] = generated

    return {
        "test_cases": generated,
        "total":      len(generated),
        "gen_method": "llm" if llm_client else "heuristic",
    }

@app.get("/test-cases")
def get_test_cases():
    return {"test_cases": store["test_cases"], "total": len(store["test_cases"])}

@app.put("/test-cases")
def update_test_cases(body: TestCasesUpdate):
    store["test_cases"] = [tc.dict() for tc in body.test_cases]
    return {"saved": len(store["test_cases"])}

@app.post("/ask")
def ask(req: AskRequest):
    if not store["documents"]:
        raise HTTPException(status_code=400, detail="No documents uploaded yet.")
    chunks = retrieve_chunks(req.question, req.top_k)
    answer = generate_answer(req.question, chunks)
    return {"question": req.question, "answer": answer, "retrieved_chunks": chunks}

@app.post("/evaluate/single")
def evaluate_single(req: EvalRequest):
    if not store["documents"]:
        raise HTTPException(status_code=400, detail="No documents uploaded yet.")

    chunks   = retrieve_chunks(req.question, req.top_k)
    answer   = generate_answer(req.question, chunks)
    contexts = [c["content"] for c in chunks]

    result = evaluate_with_ragas(
        question     = req.question,
        answer       = answer,
        contexts     = contexts,
        ground_truth = req.ground_truth,
        llm_client   = llm_client,
        llm_model    = LLM_MODEL,
        llm_provider = LLM_PROVIDER,
    )

    return {
        "question":         req.question,
        "answer":           answer,
        "ground_truth":     req.ground_truth,
        "retrieved_chunks": chunks,
        "metrics":          result.to_dict(),
        "passed":           result.ragas_score >= 0.70,
    }

@app.post("/evaluate/run")
def evaluate_run():
    if not store["documents"]:
        raise HTTPException(status_code=400, detail="No documents uploaded.")
    if not store["test_cases"]:
        raise HTTPException(status_code=400, detail="No test cases. Generate questions first.")

    results = []
    for tc in store["test_cases"]:
        chunks   = retrieve_chunks(tc["question"])
        answer   = generate_answer(tc["question"], chunks)
        contexts = [c["content"] for c in chunks]

        result = evaluate_with_ragas(
            question     = tc["question"],
            answer       = answer,
            contexts     = contexts,
            ground_truth = tc["ground_truth"],
            llm_client   = llm_client,
            llm_model    = LLM_MODEL,
            llm_provider = LLM_PROVIDER,
        )

        results.append({
            "id":               tc["id"],
            "question":         tc["question"],
            "ground_truth":     tc["ground_truth"],
            "source_doc":       tc.get("source_doc", ""),
            "answer":           answer,
            "retrieved_chunks": chunks,
            "metrics":          result.to_dict(),
            "passed":           result.ragas_score >= 0.70,
        })

    total  = len(results)
    passed = sum(1 for r in results if r["passed"])
    avg    = lambda k: round(sum(r["metrics"][k] for r in results) / total, 3)
    method = results[0]["metrics"]["eval_method"] if results else "unknown"

    store["last_run"] = {
        "summary": {
            "total_tests": total,
            "passed":      passed,
            "failed":      total - passed,
            "pass_rate":   round(passed / total, 3),
            "eval_method": method,
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
    return store["last_run"]
