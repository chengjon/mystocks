"""Logging Module for MyStocks"""

from .structured import (
    StructuredLogger,
    LogContext,
    RequestLoggingMiddleware,
    get_logger,
    get_trace_id,
    get_request_id,
    set_trace_id,
    set_request_id,
    set_user_id,
    clear_context,
    trace_id_var,
    request_id_var,
    user_id_var,
)

from .tracing import (
    TracingMiddleware,
    TracingClient,
    setup_telemetry,
    get_tracer,
    get_tracing_client,
    get_current_trace_id,
    get_current_span_id,
    trace_operation,
)

__all__ = [
    "StructuredLogger",
    "LogContext",
    "RequestLoggingMiddleware",
    "get_logger",
    "get_trace_id",
    "get_request_id",
    "set_trace_id",
    "set_request_id",
    "set_user_id",
    "clear_context",
    "trace_id_var",
    "request_id_var",
    "user_id_var",
    "TracingMiddleware",
    "TracingClient",
    "setup_telemetry",
    "get_tracer",
    "get_tracing_client",
    "get_current_trace_id",
    "get_current_span_id",
    "trace_operation",
]
