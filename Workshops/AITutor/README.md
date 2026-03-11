# 🎓 AI Tutor — Microsoft Agent Framework

> **Enterprise-grade AI Tutor with RAG, Q&A Evaluation, and OpenTelemetry Observability**
>
> Built on **Microsoft Agent Framework (RC)** · **FastAPI** · **ChromaDB** · **OpenTelemetry**

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (HTML/CSS/JS)                   │
│  ┌──────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │  RAG Section │  │  Q&A Evaluator   │  │  Observability   │  │
│  │  Upload docs │  │  Submit answer   │  │  Live trace feed │  │
│  │  Ask queries │  │  Get feedback    │  │  Metric cards    │  │
│  └──────┬───────┘  └────────┬─────────┘  └────────┬─────────┘  │
└─────────┼──────────────────┼──────────────────────┼────────────┘
          │   HTTP / REST     │                       │
┌─────────▼──────────────────▼───────────────────────▼────────────┐
│                     FastAPI Backend (main.py)                    │
│                                                                  │
│  /api/rag/upload    →  rag_store.ingest_document()              │
│  /api/rag/query     →  agents.answer_rag_query()                │
│  /api/eval/submit   →  agents.evaluate_answer()                 │
│  /api/telemetry/*   →  in-memory trace/metric ring buffer       │
└───────────┬──────────────────────────────────────────────────────┘
            │
┌───────────▼──────────────────────────────────────────────────────┐
│              Microsoft Agent Framework Agents                    │
│                                                                  │
│  ┌─────────────────────────┐  ┌─────────────────────────────┐   │
│  │     RagTutorAgent       │  │      EvaluatorAgent         │   │
│  │  @tool search_documents │  │  @tool fetch_rubric         │   │
│  │  → ChromaDB retrieve    │  │  → Score 0-10 + feedback    │   │
│  └─────────┬───────────────┘  └──────────────────────────────┘  │
│            │  OpenAI / Azure OpenAI ChatClient                   │
│            ▼                                                     │
│  ┌─────────────────────────────────────────────────────────┐     │
│  │               OpenTelemetry SDK                         │     │
│  │  invoke_agent span → chat span → execute_tool span      │     │
│  │  + custom: rag.retrieve, ai_tutor.rag_query …           │     │
│  └──────────┬────────────────────────────────────────────  ┘     │
└─────────────┼────────────────────────────────────────────────────┘
              │
    ┌─────────▼──────────────────────────────────┐
    │         Telemetry Backends (optional)       │
    │  • Console (always on)                      │
    │  • OTLP → Jaeger / VS Code AI Toolkit       │
    │  • Azure Monitor → Application Insights     │
    └────────────────────────────────────────────┘
```

---

## Quick Start

### Prerequisites

- Python 3.10+
- OpenAI API key **or** Azure OpenAI credentials
- (Optional) Jaeger / VS Code AI Toolkit for OTLP traces

### 1. Configure environment

```bash
cd ai_tutor
cp .env.example .env
# Edit .env and set your OPENAI_API_KEY (or Azure OpenAI values)
```

### 2. Start the backend

```bash
chmod +x start_backend.sh
./start_backend.sh
```

The server starts at **http://localhost:8000**  
API docs (Swagger): **http://localhost:8000/docs**

### 3. Open the frontend

Open `frontend/index.html` in your browser.  
Use a simple HTTP server to avoid CORS issues:

```bash
cd frontend
python3 -m http.server 5500
# Then open http://localhost:5500
```

---

## Key Files

```
ai_tutor/
├── main.py                    # FastAPI app — routes, lifespan, CORS
├── requirements.txt           # All Python dependencies
├── .env.example               # Environment template
├── start_backend.sh           # One-command startup script
│
├── backend/
│   ├── agents.py              # MAF Agent definitions (RAG + Evaluator)
│   └── rag_store.py           # ChromaDB vector store (ingest + retrieve)
│
├── telemetry/
│   └── setup.py               # OpenTelemetry SDK init + exporters
│
├── frontend/
│   └── index.html             # Complete SPA (HTML/CSS/JS)
│
└── data/
    └── sample_study_material.txt  # Demo document for upload
```

---

## Microsoft Agent Framework — Key Concepts Used

| Concept | Usage in AI Tutor |
|---|---|
| `agent_framework.Agent` | Both RagTutorAgent and EvaluatorAgent |
| `@tool` decorator | `search_documents`, `fetch_rubric` |
| `AzureOpenAIChatClient` / `OpenAIChatClient` | LLM backend |
| Built-in OTel integration | `setup_observability()` for auto-spans |
| `invoke_agent` span | Emitted per agent call |
| `chat` span | Emitted per LLM call (with prompt/response if ENABLE_SENSITIVE_DATA=true) |
| `execute_tool` span | Emitted per tool call |

---

## OpenTelemetry Span Hierarchy

```
invoke_agent RagTutorAgent                    [ai_tutor.rag_query span]
├── chat gpt-4o-mini                          [MAF auto-instrumented]
│   └── execute_tool search_documents         [MAF auto-instrumented]
│       └── rag.retrieve                      [custom span in rag_store.py]
└── chat gpt-4o-mini (final synthesis)

invoke_agent EvaluatorAgent                   [ai_tutor.evaluate_answer span]
├── chat gpt-4o-mini
│   └── execute_tool fetch_rubric
└── chat gpt-4o-mini (final scoring)
```

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Liveness + telemetry config |
| POST | `/api/rag/upload` | Upload document to vector store |
| GET | `/api/rag/documents` | List ingested documents |
| POST | `/api/rag/query` | RAG question answering |
| DELETE | `/api/rag/clear` | Wipe vector store |
| POST | `/api/eval/submit` | Evaluate learner answer |
| GET | `/api/telemetry/traces` | Last N trace events |
| GET | `/api/telemetry/metrics` | Runtime metric snapshot |

---

## Observability Setup — VS Code AI Toolkit

1. Install **VS Code AI Toolkit** extension
2. Enable the built-in OTLP collector (listens on `localhost:4317`)
3. Set `OTLP_ENDPOINT=http://localhost:4317` in `.env`
4. Set `ENABLE_SENSITIVE_DATA=true` to capture prompts/responses in spans
5. Restart the backend — traces appear in the AI Toolkit panel

---

## Feature Roadmap

- [ ] Multi-document comparison agent
- [ ] Adaptive quiz generation from uploaded notes
- [ ] Student performance tracking (per-session)
- [ ] Azure AI Foundry integration for project-level tracing
- [ ] Graph-based workflow (MAF Workflow engine) for multi-step tutoring
