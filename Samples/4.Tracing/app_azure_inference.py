#Using Azure AI Inference SDK (Recommended for GitHub Models)


import os
from dotenv import load_dotenv

load_dotenv()
github_token = os.environ.get("GITHUB_TOKEN")

### Set up for OpenTelemetry tracing ###
os.environ["AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED"] = "true"
os.environ["AZURE_SDK_TRACING_IMPLEMENTATION"] = "opentelemetry"

from opentelemetry import trace, _events
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk._events import EventLoggerProvider
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter

resource = Resource(attributes={
    "service.name": "opentelemetry-instrumentation-azure-ai-inference"
})

provider = TracerProvider(resource=resource)
otlp_exporter = OTLPSpanExporter(
    endpoint="http://localhost:4318/v1/traces",
)
processor = BatchSpanProcessor(otlp_exporter)
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

logger_provider = LoggerProvider(resource=resource)
logger_provider.add_log_record_processor(
    BatchLogRecordProcessor(OTLPLogExporter(endpoint="http://localhost:4318/v1/logs"))
)
_events.set_event_logger_provider(EventLoggerProvider(logger_provider))

from azure.ai.inference.tracing import AIInferenceInstrumentor
AIInferenceInstrumentor().instrument()

print("OpenTelemetry tracing configured for Azure AI Inference")

### End OpenTelemetry setup ###

import streamlit as st
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential

# Use Azure AI Inference client
client = ChatCompletionsClient(
    endpoint="https://models.inference.ai.azure.com",
    credential=AzureKeyCredential(github_token),
)

st.title("Chat with GPT-4")
query = st.chat_input("Enter query:")

if query:
    with st.chat_message("user"):
        st.write(query)

    response = client.complete(
        messages=[
            SystemMessage(content="You are a helpful assistant and provides structured answers."),
            UserMessage(content=query)
        ],
        model="gpt-4o",  
        temperature=0.7,
        max_tokens=1000
    )
    
    with st.chat_message("assistant"):
        st.write(response.choices[0].message.content)