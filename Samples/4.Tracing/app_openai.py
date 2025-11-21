
#Using OpenAI SDK with OpenTelemetry Instrumentation

#For using the OpenAI SDK with local models

import os
from dotenv import load_dotenv

load_dotenv()

# Set environment variable for content recording
os.environ["OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT"] = "true"

from opentelemetry import trace, _events
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk._events import EventLoggerProvider
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter

# Set up resource
resource = Resource(attributes={
    "service.name": "opentelemetry-instrumentation-openai"
})

# Set up tracer provider
provider = TracerProvider(resource=resource)
otlp_exporter = OTLPSpanExporter(
    endpoint="http://localhost:4318/v1/traces"
)
processor = BatchSpanProcessor(otlp_exporter)
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

# Set up logger provider
logger_provider = LoggerProvider(resource=resource)
logger_provider.add_log_record_processor(
    BatchLogRecordProcessor(OTLPLogExporter(endpoint="http://localhost:4318/v1/logs"))
)
_events.set_event_logger_provider(EventLoggerProvider(logger_provider))

# Instrument OpenAI SDK (not Azure AI Inference)
from opentelemetry.instrumentation.openai_v2 import OpenAIInstrumentor
OpenAIInstrumentor().instrument()

print("OpenTelemetry tracing configured for OpenAI SDK")

import streamlit as st
from openai import OpenAI

client = OpenAI(
    base_url="http://127.0.0.1:5272/v1/",
    api_key="xyz"  # required by API but not used
)

st.title("Chat with Qwen Model")
query = st.chat_input("Enter query:")

if query:
    with st.chat_message("user"):
        st.write(query)

    #Use "system" role for system message
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful assistant and provides structured answers."},
            {"role": "user", "content": query}
        ],
        model="qwen2.5-1.5b-instruct-generic-cpu:3",
    )
    
    with st.chat_message("assistant"):
        st.write(chat_completion.choices[0].message.content)



#--- End of app_openai.py ---