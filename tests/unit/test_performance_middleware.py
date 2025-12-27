"""
Unit Tests for Performance Middleware
Tests for Prometheus metrics collection and middleware functionality
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from prometheus_client import REGISTRY

from src.core.middleware.performance import (
    metrics_endpoint,
    get_endpoint_name,
    REQUEST_COUNT,
    REQUEST_LATENCY,
    ACTIVE_REQUESTS,
)


class TestGetEndpointName:
    """Tests for endpoint name extraction"""

    def test_api_endpoint_with_id(self):
        """Test converting API endpoint with ID parameter"""
        result = get_endpoint_name("/api/stocks/000001")
        assert result == "/api/stocks/{id}"

    def test_api_endpoint_without_id(self):
        """Test converting API endpoint without ID"""
        result = get_endpoint_name("/api/market/overview")
        assert result == "/api/{endpoint}"

    def test_root_endpoint(self):
        """Test root endpoint"""
        result = get_endpoint_name("/")
        assert result == "/"

    def test_health_endpoint(self):
        """Test health check endpoint"""
        result = get_endpoint_name("/health")
        assert result == "/health"


class TestMetricsEndpoint:
    """Tests for metrics endpoint"""

    def test_metrics_returns_prometheus_format(self):
        """Test that metrics endpoint returns Prometheus format"""
        app = FastAPI()

        @app.get("/metrics")
        def get_metrics():
            return metrics_endpoint()

        client = TestClient(app)
        response = client.get("/metrics")

        assert response.status_code == 200
        assert "text/plain" in response.headers["content-type"]
        assert "http_request_duration_seconds" in response.text


class TestPerformanceMiddleware:
    """Tests for PerformanceMiddleware"""

    def setup_method(self):
        """Setup test fixtures"""
        self.app = FastAPI()
        self.client = TestClient(self.app)
        REGISTRY.remove(REQUEST_COUNT)
        REGISTRY.remove(REQUEST_LATENCY)
        REGISTRY.remove(ACTIVE_REQUESTS)

    def teardown_method(self):
        """Cleanup after tests"""
        REGISTRY.remove(REQUEST_COUNT)
        REGISTRY.remove(REQUEST_LATENCY)
        REGISTRY.remove(ACTIVE_REQUESTS)

    def test_middleware_tracks_request_count(self):
        """Test that middleware tracks request count"""

        @self.app.get("/test")
        def test_endpoint():
            return {"message": "ok"}

        self.client.get("/test")

        metrics_text = self.client.get("/metrics").text
        assert 'http_requests_total{method="GET",endpoint="/test"' in metrics_text

    def test_middleware_tracks_request_latency(self):
        """Test that middleware tracks request latency"""

        @self.app.get("/test")
        def test_endpoint():
            return {"message": "ok"}

        self.client.get("/test")

        metrics_text = self.client.get("/metrics").text
        assert "http_request_duration_seconds_bucket{" in metrics_text

    def test_middleware_tracks_status_code(self):
        """Test that middleware tracks status codes"""

        @self.app.get("/test")
        def test_endpoint():
            return {"message": "ok"}

        self.client.get("/test")

        metrics_text = self.client.get("/metrics").text
        assert 'status_code="200"' in metrics_text

    def test_middleware_tracks_4xx_errors(self):
        """Test that middleware tracks 4xx errors"""

        @self.app.get("/test")
        def test_endpoint():
            from fastapi import HTTPException

            raise HTTPException(status_code=400, detail="Bad request")

        self.client.get("/test")

        metrics_text = self.client.get("/metrics").text
        assert 'status_code="400"' in metrics_text

    def test_middleware_tracks_5xx_errors(self):
        """Test that middleware tracks 5xx errors"""

        @self.app.get("/test")
        def test_endpoint():
            raise Exception("Server error")

        self.client.get("/test")

        metrics_text = self.client.get("/metrics").text
        assert 'status_code="500"' in metrics_text

    def test_slow_request_tracking(self):
        """Test that slow requests are tracked separately"""
        import time

        @self.app.get("/slow")
        def slow_endpoint():
            time.sleep(0.5)
            return {"message": "ok"}

        self.client.get("/slow")

        metrics_text = self.client.get("/metrics").text
        assert "slow_http_requests_total{" in metrics_text

    def test_active_requests_gauge(self):
        """Test that active requests are tracked"""

        @self.app.get("/test")
        def test_endpoint():
            return {"message": "ok"}

        self.client.get("/test")

        metrics_text = self.client.get("/metrics").text
        assert "http_requests_active{" in metrics_text


class TestPerformanceDecorator:
    """Tests for performance tracking decorator"""

    def test_track_performance_decorator(self):
        """Test that track_performance decorator works"""
        from src.core.middleware.performance import track_performance

        @track_performance("test_function")
        async def test_function():
            return {"result": "ok"}

        import asyncio

        result = asyncio.run(test_function())
        assert result == {"result": "ok"}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
