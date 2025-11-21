#Adding Custom Spans for Better Visibility

import os
from dotenv import load_dotenv

load_dotenv()

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

resource = Resource(attributes={
    "service.name": "streamlit-chat-app"
})

provider = TracerProvider(resource=resource)
otlp_exporter = OTLPSpanExporter(endpoint="http://localhost:4318/v1/traces")
processor = BatchSpanProcessor(otlp_exporter)
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

logger_provider = LoggerProvider(resource=resource)
logger_provider.add_log_record_processor(
    BatchLogRecordProcessor(OTLPLogExporter(endpoint="http://localhost:4318/v1/logs"))
)
_events.set_event_logger_provider(EventLoggerProvider(logger_provider))

from opentelemetry.instrumentation.openai_v2 import OpenAIInstrumentor
OpenAIInstrumentor().instrument()

print("Tracing configured")

import streamlit as st
from openai import OpenAI

# Get tracer for custom spans
tracer = trace.get_tracer(__name__)

client = OpenAI(
    #base_url="http://127.0.0.1:5272/v1/",
    base_url="http://127.0.0.1:53491/v1/",
    api_key="xyz"
)

st.title("Chat with GenAI Model")
query = st.chat_input("Enter query:")

if query:
    # Create a custom span for the entire chat interaction
    with tracer.start_as_current_span("chat_interaction") as span:
        span.set_attribute("user_query", query)
        span.set_attribute("model", "qwen2.5-1.5b-instruct-generic-cpu:3")
        
        with st.chat_message("user"):
            st.write(query)
        
        # The OpenAI call will be automatically traced within this span
        with tracer.start_as_current_span("llm_completion") as llm_span:
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a helpful assistant and provides structured answers."},
                    {"role": "user", "content": query}
                ],
                #model="qwen2.5-1.5b-instruct-generic-cpu:3",
                model="qwen2.5-0.5b-instruct-cuda-gpu:3",
                # stream=True,
            )
            
            response_text = chat_completion.choices[0].message.content
            llm_span.set_attribute("response_length", len(response_text))
            llm_span.add_event("Response generated")
        
        with st.chat_message("assistant"):
            st.write(response_text)
        
        span.add_event("Chat interaction complete")

print(" Check AI Toolkit --> Tracing for telemetry data")

