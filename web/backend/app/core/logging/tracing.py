"""
Distributed Tracing Module for MyStocks
Integration with Grafana Tempo for trace collection and analysis
"""

import logging
import os
import uuid
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any, Dict, Optional

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.sampling import ParentBasedTraceIdRatioBasedSampler
from opentelemetry.semconv.resource import ResourceAttributes

logger = logging.getLogger(__name__)

trace_id_var: ContextVar[Optional[str]] = ContextVar("trace_id", default=None)
span_id_var: ContextVar[Optional[str]] = ContextVar("span_id", default=None)


def setup_telemetry(service_name: str = "mystocks-api") -> trace.Tracer:
    """Setup OpenTelemetry tracing"""
    resource = Resource.create(
        {
            ResourceAttributes.SERVICE_NAME: service_name,
            ResourceAttributes.SERVICE_VERSION: "1.0.0",
            "deployment.environment": "production",
        }
    )

    # Configure sampling rate (default 10% for production efficiency)
    sampling_ratio = float(os.getenv("OTEL_TRACES_SAMPLER_ARG", "0.1"))
    sampler = ParentBasedTraceIdRatioBasedSampler(sampling_ratio)

    provider = TracerProvider(resource=resource, sampler=sampler)

    # Configure OTLP exporter for Tempo
    otlp_exporter = OTLPSpanExporter(
        endpoint="http://tempo:4317",
        insecure=True,
    )
    span_processor = BatchSpanProcessor(otlp_exporter)
    provider.add_span_processor(span_processor)

    trace.set_tracer_provider(provider)

    return trace.get_tracer(__name__)


class TracingMiddleware:
    """Tracing middleware for FastAPI"""

    def __init__(self, tracer: trace.Tracer):
        self.tracer = tracer

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_id = self._get_request_id(scope)

        with self.tracer.start_as_current_span(
            f"{scope['method']} {scope['path']}",
            attributes={
                "http.method": scope["method"],
                "http.url": scope["path"],
                "http.request_id": request_id,
                "http.user_agent": scope.get("headers", {}).get("user-agent", ""),
            },
        ) as span:
            await self.app(scope, receive, send)

            status_code = self._get_status_code(send)
            span.set_attribute("http.status_code", status_code)

            if status_code >= 400:
                span.set_status(trace.StatusCode.ERROR)

    def _get_request_id(self, scope) -> str:
        """Extract request ID from scope"""
        headers = dict(scope.get("headers", {}))
        return headers.get("x-request-id", f"trace-{uuid.uuid4().hex[:16]}")

    def _get_status_code(self, send) -> int:
        """Extract status code from send"""
        for message in send:
            if message["type"] == "http.response.start":
                return message["status"]
        return 200

    async def app(self, scope, receive, send):
        """ASGI app"""


class TracingClient:
    """Client for trace operations"""

    def __init__(self, tracer: trace.Tracer):
        self.tracer = tracer

    def start_span(
        self,
        name: str,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> trace.Span:
        """Start a new span"""
        return self.tracer.start_span(name, attributes=attributes)

    def start_child_span(
        self,
        name: str,
        parent: Optional[trace.Span] = None,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> trace.Span:
        """Start a child span"""
        ctx = trace.set_span_in_context(parent) if parent else None
        return self.tracer.start_span(name, context=ctx, attributes=attributes)

    def add_event(self, name: str, attributes: Optional[Dict[str, Any]] = None):
        """Add event to current span"""
        span = trace.get_current_span()
        span.add_event(name, attributes=attributes)

    def set_attribute(self, key: str, value: Any):
        """Set attribute on current span"""
        span = trace.get_current_span()
        span.set_attribute(key, value)

    def set_status(self, status_code: trace.StatusCode, description: str = ""):
        """Set status on current span"""
        span = trace.get_current_span()
        span.set_status(trace.Status(status_code, description))

    def record_exception(self, exception: Exception):
        """Record exception on current span"""
        span = trace.get_current_span()
        span.record_exception(exception)
        span.set_status(trace.StatusCode.ERROR, str(exception))


def get_current_trace_id() -> Optional[str]:
    """Get current trace ID"""
    span = trace.get_current_span()
    if span:
        ctx = span.get_span_context()
        if ctx.is_valid:
            return format(ctx.trace_id, "032x")
    return None


def get_current_span_id() -> Optional[str]:
    """Get current span ID"""
    span = trace.get_current_span()
    if span:
        ctx = span.get_span_context()
        if ctx.is_valid:
            return format(ctx.span_id, "016x")
    return None


_global_tracer: Optional[trace.Tracer] = None
_global_client: Optional[TracingClient] = None


def get_tracer() -> trace.Tracer:
    """Get global tracer"""
    global _global_tracer
    if _global_tracer is None:
        _global_tracer = setup_telemetry()
    return _global_tracer


def get_tracing_client() -> TracingClient:
    """Get global tracing client"""
    global _global_client
    if _global_client is None:
        _global_client = TracingClient(get_tracer())
    return _global_client


@contextmanager
def trace_operation(name: str, attributes: Optional[Dict[str, Any]] = None):
    """Context manager for tracing an operation"""
    client = get_tracing_client()
    with client.start_span(name, attributes=attributes) as span:
        yield span
