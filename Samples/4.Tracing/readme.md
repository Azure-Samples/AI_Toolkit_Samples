# 💬 Traced LLM Chat App (Streamlit & OpenTelemetry)

A basic Streamlit chat application demonstrating **OpenTelemetry** tracing integration for different Large Language Model (LLM) providers. It provides two main options for instrumenting an LLM chat flow to send telemetry data (traces and logs) to an OTLP endpoint (e.g., AI Toolkit, or an observability platform).

---

## Features

* **OpenTelemetry Setup:** Configures OTLP traces and logs using the `OTLPSpanExporter` and `OTLPLogExporter` to send data to `http://localhost:4318`.
* **Provider Options:** Includes configurations for both **OpenAI SDK** (for local/custom endpoints) and **Azure AI Inference SDK** (recommended for GitHub-hosted models).
* **Custom Spans:** Example showing how to add manual, high-level **custom spans** (`chat_interaction`, `llm_completion`) to better visualize the application flow.
* **Streamlit UI:** A simple web interface for chat interaction.

---

## Setup

### Prerequisites

1.  **Python Environment:** Python 3.8+
2.  **Observability Backend:** A local OTLP collector (e.g., AI Toolkit) running on `http://localhost:4318` to receive traces/logs.
3.  **LLM Backend:**
    * **Option 1:** A locally running model exposing an OpenAI-compatible endpoint (e.g., via **Foundry Local** or **AI Toolkit**).
    * **Option 2:** Access to the Azure AI Inference API, requiring a `GITHUB_TOKEN` for authentication.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-link>
    cd <your-repo-name>
    ```

2.  **Install dependencies:**
    ```bash
    pip install streamlit openai azure-ai-inference opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp opentelemetry-instrumentation-openai-v2 azure-ai-inference-tracing python-dotenv
    ```

3.  **Environment Variables:**
    Create a `.env` file in the root directory and add the following:
    ```
    # For Option 2
    GITHUB_TOKEN="<Your-GitHub-Token-for-Azure-AI-Inference>" 
    # Or other necessary secrets
    ```

---

## Usage

The provided code file contains three main sections, all commented out. **Choose and uncomment only one section** based on your target LLM provider and tracing requirements.

### Option 1: Tracing with OpenAI SDK (Local Models)

* **Target:** Local/custom LLM endpoints that are OpenAI-compatible.
* **Uncomment:** The first large block using `from openai import OpenAI`.
* **Run:**
    ```bash
    streamlit run <your-file-name>.py
    ```

### Option 2: Tracing with Azure AI Inference SDK (GitHub Models)

* **Target:** Models hosted via the Azure AI Inference API (e.g., `gpt-4o`).
* **Uncomment:** The second large block using `from azure.ai.inference import ChatCompletionsClient`.
* **Run:**
    ```bash
    streamlit run <your-file-name>.py
    ```

### Option 3: Adding Custom Spans

* **Target:** To add custom, detailed application logic tracing **on top of** the automatic instrumentation (uses OpenAI SDK).
* **Uncomment:** The third large block that defines a `tracer` and uses `tracer.start_as_current_span(...)`.
* **Run:**
    ```bash
    streamlit run <your-file-name>.py
    ```

---

## Viewing Traces

Once the application is running and you interact with the chat:

1.  Check the logs of your **OTLP Collector** (on AI Toolkit) running on `http://localhost:4318`.
2.  The traces will be visible, showing the `chat_interaction` (if used), `llm_completion` (if used), and the automatic **`openai.chat.completions.create`** or **`azure.ai.inference.chat_completions.complete`** span, providing details like latency, model name, and message content.

