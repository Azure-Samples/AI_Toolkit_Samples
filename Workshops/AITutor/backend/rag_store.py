"""
backend/rag_store.py
──────────────────────────────────────────────────────────────────────────────
Simple RAG layer built on ChromaDB (in-memory / ephemeral) that the
RAG Agent uses as a retrieval tool.

Responsibilities:
  1. Ingest text documents (or PDF text) – chunk → embed → upsert into Chroma
  2. Retrieve top-k relevant chunks for a query
  3. Expose helpers used by the FastAPI upload endpoint

OpenTelemetry spans:
  • rag.ingest   – document upload / chunking / upsert
  • rag.retrieve – semantic search
──────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

# ── Path fix ──────────────────────────────────────────────────────────────────
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent.resolve()))
# ─────────────────────────────────────────────────────────────────────────────

import hashlib
import logging
import os
import time
from typing import Any

import chromadb
from chromadb.utils import embedding_functions

from otel_setup import get_tracer
from opentelemetry.trace import SpanKind, Status, StatusCode

logger = logging.getLogger(__name__)
tracer = get_tracer(__name__)

# ── ChromaDB client (ephemeral / in-process) ──────────────────────────────
_client = chromadb.Client()  # in-memory; swap to PersistentClient("/data") for prod

_EMBED_FN = embedding_functions.DefaultEmbeddingFunction()  # SentenceTransformers mini

_COLLECTION_NAME = "ai_tutor_docs"
_collection: chromadb.Collection | None = None


def _get_collection() -> chromadb.Collection:
    global _collection
    if _collection is None:
        _collection = _client.get_or_create_collection(
            name=_COLLECTION_NAME,
            embedding_function=_EMBED_FN,
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


# ── Chunking ──────────────────────────────────────────────────────────────

def _chunk_text(text: str, chunk_size: int = 400, overlap: int = 60) -> list[str]:
    """Split text into overlapping fixed-size character chunks."""
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end].strip())
        start += chunk_size - overlap
    return [c for c in chunks if len(c) > 20]


# ── Public API ────────────────────────────────────────────────────────────

def ingest_document(filename: str, text: str) -> dict[str, Any]:
    """
    Chunk `text`, embed, and upsert into ChromaDB.
    Returns a summary dict with span info.
    """
    with tracer.start_as_current_span(
        "rag.ingest",
        kind=SpanKind.INTERNAL,
        attributes={
            "rag.filename": filename,
            "rag.text_length": len(text),
        },
    ) as span:
        t0 = time.perf_counter()
        try:
            col = _get_collection()
            chunks = _chunk_text(text)

            ids, docs, metas = [], [], []
            for i, chunk in enumerate(chunks):
                uid = hashlib.sha256(f"{filename}:{i}:{chunk[:40]}".encode()).hexdigest()[:16]
                ids.append(uid)
                docs.append(chunk)
                metas.append({"source": filename, "chunk_index": i})

            col.upsert(ids=ids, documents=docs, metadatas=metas)

            elapsed = round((time.perf_counter() - t0) * 1000, 1)
            span.set_attribute("rag.chunks_ingested", len(chunks))
            span.set_attribute("rag.ingest_ms", elapsed)
            span.set_status(Status(StatusCode.OK))

            logger.info("Ingested '%s' → %d chunks in %s ms", filename, len(chunks), elapsed)
            return {"filename": filename, "chunks": len(chunks), "ingest_ms": elapsed}

        except Exception as exc:
            span.record_exception(exc)
            span.set_status(Status(StatusCode.ERROR, str(exc)))
            raise


def retrieve_chunks(query: str, top_k: int = 4) -> list[dict[str, Any]]:
    """
    Semantic search over ingested documents.
    Returns a list of dicts: {text, source, score}
    """
    with tracer.start_as_current_span(
        "rag.retrieve",
        kind=SpanKind.INTERNAL,
        attributes={"rag.query": query, "rag.top_k": top_k},
    ) as span:
        t0 = time.perf_counter()
        try:
            col = _get_collection()
            count = col.count()
            if count == 0:
                span.set_attribute("rag.doc_count", 0)
                span.set_status(Status(StatusCode.OK))
                return []

            results = col.query(
                query_texts=[query],
                n_results=min(top_k, count),
                include=["documents", "metadatas", "distances"],
            )

            elapsed = round((time.perf_counter() - t0) * 1000, 1)
            docs_out = results["documents"][0]
            metas_out = results["metadatas"][0]
            distances = results["distances"][0]

            chunks = [
                {
                    "text": doc,
                    "source": meta.get("source", "unknown"),
                    "score": round(1 - dist, 4),  # cosine similarity
                }
                for doc, meta, dist in zip(docs_out, metas_out, distances)
            ]

            span.set_attribute("rag.retrieved_count", len(chunks))
            span.set_attribute("rag.retrieve_ms", elapsed)
            span.set_status(Status(StatusCode.OK))

            return chunks

        except Exception as exc:
            span.record_exception(exc)
            span.set_status(Status(StatusCode.ERROR, str(exc)))
            raise


def list_documents() -> list[str]:
    """Return unique source filenames currently in the vector store."""
    col = _get_collection()
    if col.count() == 0:
        return []
    all_metas = col.get(include=["metadatas"])["metadatas"]
    return sorted({m["source"] for m in all_metas})


def clear_store() -> None:
    """Wipe all documents from the collection."""
    global _collection
    _client.delete_collection(_COLLECTION_NAME)
    _collection = None
    logger.info("RAG store cleared.")
