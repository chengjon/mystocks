"""
Performance Monitoring Middleware for Prometheus Metrics
Provides request latency, count, and active request metrics for all API endpoints
"""

import time
from typing import Callable

from fastapi import Response
from prometheus_client import Counter, Gauge, Histogram, Info, REGISTRY, generate_latest


def _get_or_create(metric_cls, name: str, *args, **kwargs):
    existing = REGISTRY._names_to_collectors.get(name)
    if existing:
        return existing
    return metric_cls(name, *args, **kwargs)

REQUEST_LATENCY = _get_or_create(
    Histogram,
    "http_request_duration_seconds",
    "HTTP请求延迟(秒)",
    ["method", "endpoint", "status_code"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

REQUEST_COUNT = _get_or_create(
    Counter,
    "http_requests_total",
    "HTTP请求总数",
    ["method", "endpoint", "status_code"],
)

ACTIVE_REQUESTS = _get_or_create(
    Gauge,
    "http_requests_active",
    "当前活跃HTTP请求数",
    ["method", "endpoint"],
)

REQUEST_IN_PROGRESS = _get_or_create(
    Gauge,
    "http_requests_in_progress",
    "当前处理中的请求数",
    ["method", "endpoint"],
)

REQUEST_LATENCY_SECONDS = _get_or_create(
    Histogram,
    "http_request_duration_seconds_total",
    "HTTP请求总延迟(秒)",
    ["method", "endpoint"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
)

SLOW_REQUESTS = _get_or_create(
    Counter,
    "slow_http_requests_total",
    "慢请求计数(>300ms)",
    ["method", "endpoint"],
)

APP_INFO = _get_or_create(Info, "mystocks_app", "MyStocks Application Information")


def get_endpoint_name(path: str) -> str:
    """Convert path to endpoint name for metrics"""
    if path.startswith("/api/"):
        parts = path.split("/")
        if len(parts) >= 4:
            return f"/api/{parts[2]}/{{id}}"
    if path.startswith("/api"):
        return "/api/{endpoint}"
    return path


class PerformanceMiddleware:
    """Performance monitoring middleware for FastAPI"""

    def __init__(self, app=None):
        self.app = app
        self._initialized = False

    def setup(self) -> None:
        """Initialize middleware state"""
        if not self._initialized:
            APP_INFO.info(
                {
                    "version": "1.0.0",
                    "environment": "production",
                    "service": "mystocks-api",
                }
            )
            self._initialized = True

    async def __call__(self, scope: dict, receive: Callable, send: Callable) -> None:
        """Process incoming request and track metrics"""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        self.setup()

        method = scope["method"]
        path = scope["path"]
        endpoint = get_endpoint_name(path)

        start_time = time.perf_counter()
        active_requests = ACTIVE_REQUESTS.labels(method=method, endpoint=endpoint)
        in_progress = REQUEST_IN_PROGRESS.labels(method=method, endpoint=endpoint)

        active_requests.inc()
        in_progress.inc()

        response_started = False

        async def send_wrapper(message: dict) -> None:
            nonlocal response_started
            if message["type"] == "http.response.start":
                response_started = True
                status_code = message["status"]
                latency = time.perf_counter() - start_time

                REQUEST_LATENCY.labels(
                    method=method,
                    endpoint=endpoint,
                    status_code=str(status_code),
                ).observe(latency)

                REQUEST_COUNT.labels(
                    method=method,
                    endpoint=endpoint,
                    status_code=str(status_code),
                ).inc()

                REQUEST_LATENCY_SECONDS.labels(
                    method=method,
                    endpoint=endpoint,
                ).observe(latency)

                if latency > 0.3:
                    SLOW_REQUESTS.labels(
                        method=method,
                        endpoint=endpoint,
                    ).inc()

                ACTIVE_REQUESTS.labels(method=method, endpoint=endpoint).dec()
                in_progress.dec()

            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        except Exception:
            latency = time.perf_counter() - start_time
            status_code = 500

            REQUEST_LATENCY.labels(
                method=method,
                endpoint=endpoint,
                status_code=str(status_code),
            ).observe(latency)

            REQUEST_COUNT.labels(
                method=method,
                endpoint=endpoint,
                status_code=str(status_code),
            ).inc()

            ACTIVE_REQUESTS.labels(method=method, endpoint=endpoint).dec()
            in_progress.dec()

            raise
        finally:
            if not response_started:
                ACTIVE_REQUESTS.labels(method=method, endpoint=endpoint).dec()
                in_progress.dec()


def metrics_endpoint() -> Response:
    """Prometheus metrics endpoint"""
    return Response(
        content=generate_latest(),
        media_type="text/plain; version=0.0.4; charset=utf-8",
    )


def track_performance(endpoint: str):
    """Decorator to track custom performance metrics"""

    def decorator(func: Callable):
        async def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            try:
                result = await func(*args, **kwargs)
                latency = time.perf_counter() - start_time

                REQUEST_LATENCY_SECONDS.labels(
                    method="custom",
                    endpoint=endpoint,
                ).observe(latency)

                if latency > 0.3:
                    SLOW_REQUESTS.labels(
                        method="custom",
                        endpoint=endpoint,
                    ).inc()

                return result
            except Exception:
                latency = time.perf_counter() - start_time
                SLOW_REQUESTS.labels(
                    method="custom",
                    endpoint=endpoint,
                ).inc()
                raise

        return wrapper

    return decorator
