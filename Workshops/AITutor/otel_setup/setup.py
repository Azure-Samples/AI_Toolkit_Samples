"""
otel_setup/setup.py
──────────────────────────────────────────────────────────────────────────────
OpenTelemetry initialisation — delegated to MAF's configure_otel_providers().

Lessons learned (all confirmed by inspecting MAF source + live exporter state):

  1. VS_CODE_EXTENSION_PORT hardcodes protocol="grpc" → always fails on 4318.
     Do not use it.

  2. OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf requires the package
     opentelemetry-exporter-otlp-proto-http to be installed. If missing,
     MAF silently falls back to gRPC. requirements.txt now pins both.

  3. OTEL_EXPORTER_OTLP_ENDPOINT (base URL) is passed directly to the
     exporter constructor — the SDK's auto /v1/* path appending is bypassed.
     Sending to http://localhost:4318 (no path) produces HTTP 404.
     Use signal-specific vars with explicit full paths instead:
       OTEL_EXPORTER_OTLP_TRACES_ENDPOINT=http://localhost:4318/v1/traces
       OTEL_EXPORTER_OTLP_METRICS_ENDPOINT=http://localhost:4318/v1/metrics
       OTEL_EXPORTER_OTLP_LOGS_ENDPOINT=http://localhost:4318/v1/logs
──────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)


def setup_telemetry() -> None:
    """
    Initialise OTel by delegating to MAF's configure_otel_providers().
    Called once at FastAPI startup from the lifespan hook in main.py.
    """
    _preflight_check()
    _log_config()

    try:
        from agent_framework.observability import configure_otel_providers
        configure_otel_providers()
        logger.info("MAF configure_otel_providers() completed successfully")
    except Exception as exc:
        logger.error("configure_otel_providers() failed: %s", exc)
        raise

    # Optional: Azure Monitor
    app_insights_cs = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING", "")
    if app_insights_cs:
        try:
            from azure.monitor.opentelemetry import configure_azure_monitor
            from agent_framework.observability import enable_instrumentation
            configure_azure_monitor(connection_string=app_insights_cs)
            enable_instrumentation()
            logger.info("Azure Monitor active")
        except Exception as exc:
            logger.warning("Azure Monitor setup failed (non-fatal): %s", exc)


def _preflight_check() -> None:
    """Fail fast with a clear message if the HTTP OTLP package is missing."""
    protocol = os.getenv("OTEL_EXPORTER_OTLP_PROTOCOL", "grpc")
    traces_ep = os.getenv("OTEL_EXPORTER_OTLP_TRACES_ENDPOINT", "")

    if protocol == "http/protobuf" or "4318" in traces_ep:
        try:
            from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter  # noqa: F401
        except ImportError:
            raise RuntimeError(
                "\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "MISSING: opentelemetry-exporter-otlp-proto-http\n\n"
                "Without it, MAF silently falls back to gRPC → UNAVAILABLE.\n\n"
                "Fix:  .venv\\Scripts\\pip install opentelemetry-exporter-otlp-proto-http\n"
                "      (or re-run start_backend.sh — it's pinned in requirements.txt)\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            )


def _log_config() -> None:
    """Log active OTel config at startup so misconfigurations are obvious."""
    logger.info("─── OTel Config ─────────────────────────────────────────────")
    for var in [
        "ENABLE_INSTRUMENTATION", "ENABLE_SENSITIVE_DATA",
        "OTEL_EXPORTER_OTLP_PROTOCOL",
        "OTEL_EXPORTER_OTLP_TRACES_ENDPOINT",
        "OTEL_EXPORTER_OTLP_METRICS_ENDPOINT",
        "OTEL_EXPORTER_OTLP_LOGS_ENDPOINT",
        "OTEL_SERVICE_NAME",
    ]:
        logger.info("  %-42s = %s", var, os.getenv(var, "not set"))
    logger.info("─────────────────────────────────────────────────────────────")


def get_tracer(name: str = "ai_tutor"):
    """Return MAF's tracer — same provider as invoke_agent/chat/execute_tool spans."""
    try:
        from agent_framework.observability import get_tracer as _maf_tracer
        return _maf_tracer()
    except Exception:
        from opentelemetry import trace
        return trace.get_tracer(name)


def get_meter(name: str = "ai_tutor"):
    """Return MAF's meter — same provider as MAF metric spans."""
    try:
        from agent_framework.observability import get_meter as _maf_meter
        return _maf_meter()
    except Exception:
        from opentelemetry import metrics
        return metrics.get_meter(name)
