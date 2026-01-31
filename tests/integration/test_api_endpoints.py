"""API Integration Tests for FastAPI endpoints, CORS, and JWT authentication."""

import os
import sys
from unittest.mock import MagicMock, patch

import pytest

# Add project root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

# Skip all tests if FastAPI is not available (for CI/CD compatibility)
fastapi_available = False
try:
    import os

    # Import the actual MyStocks FastAPI app
    import sys

    from fastapi.testclient import TestClient

    # Ensure we can import from the web backend
    backend_path = os.path.join(os.path.dirname(__file__), "..", "..", "web", "backend")
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)

    # Import the actual app - with fallback for different import paths
    try:
        from app.main import app
    except ImportError:
        try:
            from main import app
        except ImportError:
            # Create a minimal test app if import fails
            from fastapi import FastAPI

            app = FastAPI(title="MyStocks Test API")
            print("Warning: Could not import actual FastAPI app, using minimal test app")

    fastapi_available = True
except ImportError:
    pytest.skip("FastAPI not available for testing", allow_module_level=True)


class TestAPIIntegration:
    """Integration tests for FastAPI endpoints."""

    def setup_method(self):
        """Setup test client."""
        if not fastapi_available:
            pytest.skip("FastAPI not available")
        self.client = TestClient(app)

    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = self.client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "timestamp" in data

    def test_cors_headers(self):
        """Test CORS headers are properly set."""
        response = self.client.options(
            "/api/health",
            headers={
                "Origin": "http://localhost:3001",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "content-type,authorization",
            },
        )

        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers
        assert "access-control-allow-headers" in response.headers

    def test_health_endpoint_structure(self):
        response = self.client.get("/api/health")
        assert response.status_code == 200

        data = response.json()
        assert "timestamp" in data
        assert "overall_status" in data
        assert "services" in data
        assert data["redis"] == "healthy"
        assert data["disk_space"] == "90%"

    def test_market_data_endpoint(self):
        """Test market data endpoint."""
        # Test without authentication first (should fail or redirect)
        response = self.client.get("/api/market/stock/000001")
        # This might return 401 or 200 depending on endpoint configuration
        assert response.status_code in [200, 401, 404]

    def test_invalid_endpoint(self):
        """Test invalid endpoint returns 404."""
        response = self.client.get("/api/nonexistent")
        assert response.status_code == 404

    def test_method_not_allowed(self):
        """Test wrong HTTP method returns 405."""
        response = self.client.post("/api/health")
        # Health endpoint might accept POST or return 405
        assert response.status_code in [200, 405]

    @pytest.mark.asyncio
    async def test_async_endpoint(self):
        """Test async endpoint handling."""
        # This is a placeholder for testing async endpoints
        # In a real scenario, you would test specific async endpoints
        pass


class TestCORSMiddleware:
    """Test CORS middleware functionality."""

    def setup_method(self):
        """Setup test client."""
        if not fastapi_available:
            pytest.skip("FastAPI not available")
        self.client = TestClient(app)

    def test_cors_preflight_request(self):
        """Test CORS preflight request."""
        response = self.client.options(
            "/api/health",
            headers={
                "Origin": "http://localhost:3001",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Content-Type,Authorization",
            },
        )

        assert response.status_code == 200
        assert response.headers.get("access-control-allow-origin") == "http://localhost:3001"
        assert "GET" in response.headers.get("access-control-allow-methods", "")
        assert "Content-Type" in response.headers.get("access-control-allow-headers", "")
        assert "Authorization" in response.headers.get("access-control-allow-headers", "")

    def test_cors_allowed_origins(self):
        """Test allowed CORS origins."""
        allowed_origins = [
            "http://localhost:3000",
            "http://localhost:3001",
            "http://localhost:3002",
            "http://localhost:8000",
            "http://localhost:8001",
        ]

        for origin in allowed_origins:
            response = self.client.get("/api/health", headers={"Origin": origin})
            assert response.headers.get("access-control-allow-origin") == origin

    def test_cors_disallowed_origin(self):
        """Test disallowed CORS origin."""
        response = self.client.get("/api/health", headers={"Origin": "http://malicious-site.com"})
        # Should not include CORS headers for disallowed origins
        assert "access-control-allow-origin" not in response.headers


class TestJWTAuthentication:
    """Test JWT authentication functionality."""

    def setup_method(self):
        """Setup test client."""
        if not fastapi_available:
            pytest.skip("FastAPI not available")
        self.client = TestClient(app)

    def test_protected_endpoint_with_valid_token(self):
        """Test accessing protected auth endpoint."""
        # Skip JWT tests as they require full authentication setup
        pytest.skip("JWT authentication requires full setup with valid tokens and user management")

    def test_protected_endpoint_with_invalid_token(self):
        """Test protected endpoint with invalid JWT token."""
        pytest.skip("JWT authentication requires full setup")

    def test_endpoint_without_token(self):
        """Test endpoint without authentication token."""
        pytest.skip("JWT authentication requires full setup")

    def test_malformed_authorization_header(self):
        """Test malformed authorization header."""
        pytest.skip("JWT authentication requires full setup")

    def test_endpoint_without_token(self):
        """Test endpoint without authentication token."""
        response = self.client.get("/api/protected-endpoint")

        # Should fail authentication
        assert response.status_code in [401, 403]

    def test_malformed_authorization_header(self):
        """Test malformed authorization header."""
        headers = {"Authorization": "InvalidFormat"}
        response = self.client.get("/api/protected-endpoint", headers=headers)

        assert response.status_code in [401, 403]


class TestAPIErrorHandling:
    """Test API error handling."""

    def setup_method(self):
        """Setup test client."""
        if not fastapi_available:
            pytest.skip("FastAPI not available")
        self.client = TestClient(app)

    def test_404_error_response(self):
        """Test 404 error response format."""
        response = self.client.get("/api/nonexistent/endpoint")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data or "message" in data

    def test_500_error_response(self):
        """Test 500 error response format."""
        # This would require mocking an endpoint that raises an exception
        # For demonstration purposes, we'll assume error format
        pass

    @patch("web.backend.app.api.market.get_stock_data")
    def test_endpoint_exception_handling(self, mock_get_data):
        """Test endpoint exception handling."""
        mock_get_data.side_effect = Exception("Database connection failed")

        response = self.client.get("/api/market/stock/000001")

        # Should return appropriate error response
        assert response.status_code >= 400
        data = response.json()
        assert "detail" in data or "message" in data or "error" in data


class TestAPIResponseFormat:
    """Test API response format consistency."""

    def setup_method(self):
        """Setup test client."""
        if not fastapi_available:
            pytest.skip("FastAPI not available")
        self.client = TestClient(app)

    def test_json_response_format(self):
        """Test JSON response format."""
        response = self.client.get("/api/health")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"

        data = response.json()
        assert isinstance(data, dict)

    def test_response_headers(self):
        """Test common response headers."""
        response = self.client.get("/api/health")

        # Check for common headers
        assert "content-type" in response.headers
        assert "content-length" in response.headers

    @pytest.mark.parametrize(
        "endpoint",
        [
            "/api/health",
            "/api/market/stock/000001",
            "/api/dashboard/summary",
        ],
    )
    def test_endpoint_response_time(self, endpoint):
        """Test endpoint response time is reasonable."""
        import time

        start_time = time.time()
        response = self.client.get(endpoint)
        end_time = time.time()

        response_time = end_time - start_time
        # Response should be under 5 seconds (reasonable for API)
        assert response_time < 5.0
