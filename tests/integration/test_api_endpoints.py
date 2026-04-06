"""
Application-level contract tests for live FastAPI endpoints.

These tests import the real backend app and validate the currently exposed
routes without module-level skips, fallback apps, or placeholder assertions.
"""

from __future__ import annotations

import functools
import importlib
import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "web" / "backend"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(1, str(BACKEND_ROOT))

# Keep the pytest timing plugin stable when this file runs in isolation.
(PROJECT_ROOT / "var" / "reports").mkdir(parents=True, exist_ok=True)

os.environ.setdefault("POSTGRESQL_HOST", "localhost")
os.environ.setdefault("POSTGRESQL_PORT", "5432")
os.environ.setdefault("POSTGRESQL_USER", "postgres")
os.environ.setdefault("POSTGRESQL_PASSWORD", "postgres")
os.environ.setdefault("POSTGRESQL_DATABASE", "mystocks")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key")
os.environ.setdefault("BACKEND_PORT", "8020")
os.environ.setdefault("BACKEND_BACKUP_PORT", "8021")
os.environ.setdefault("TDENGINE_HOST", "localhost")
os.environ.setdefault("TDENGINE_PORT", "6030")
os.environ.setdefault("TDENGINE_USER", "root")
os.environ.setdefault("TDENGINE_PASSWORD", "taosdata")
os.environ.setdefault("TDENGINE_DATABASE", "market_data")
os.environ.setdefault("CORS_ORIGINS", "http://localhost:3020,http://localhost:3021")
os.environ.setdefault("TESTING", "false")


@functools.lru_cache(maxsize=1)
def load_backend_app_module():
    import dotenv

    original_load_dotenv = dotenv.load_dotenv
    dotenv.load_dotenv = lambda *args, **kwargs: False
    try:
        return importlib.import_module("app.main")
    finally:
        dotenv.load_dotenv = original_load_dotenv


@pytest.fixture(scope="module")
def backend_app_module():
    return load_backend_app_module()


@pytest.fixture
def test_client(monkeypatch: pytest.MonkeyPatch, backend_app_module):
    security_module = importlib.import_module("app.core.security")

    monkeypatch.setattr(security_module, "_get_redis_for_tokens", lambda: None)
    monkeypatch.setattr(backend_app_module.csrf_manager, "_get_redis", lambda: None)
    backend_app_module.csrf_manager.tokens.clear()
    security_module._revoked_tokens_fallback.clear()

    client = TestClient(backend_app_module.app)
    yield client
    client.close()

    backend_app_module.csrf_manager.tokens.clear()
    security_module._revoked_tokens_fallback.clear()


class TestLiveAPIContracts:
    def test_actual_backend_app_registers_expected_routes(self, backend_app_module) -> None:
        registered_paths = {route.path for route in backend_app_module.app.routes}

        assert {
            "/api/health",
            "/api/csrf-token",
            "/api/v1/auth/me",
            "/api/dashboard/summary",
        }.issubset(registered_paths)

    def test_health_endpoint_returns_current_public_contract(self, test_client) -> None:
        response = test_client.get("/api/health")
        payload = response.json()

        assert response.status_code == 200
        assert payload == {
            "status": "healthy",
            "timestamp": payload["timestamp"],
            "version": "1.0.0",
        }
        assert isinstance(payload["timestamp"], float)

    def test_health_endpoint_adds_request_tracing_headers(self, test_client) -> None:
        response = test_client.get("/api/health")

        assert response.headers["content-type"].startswith("application/json")
        assert response.headers["x-request-id"]
        assert float(response.headers["x-process-time"]) >= 0

    def test_allowed_origin_preflight_is_accepted(self, test_client, backend_app_module) -> None:
        allowed_origin = backend_app_module.settings.cors_origins[0]
        response = test_client.options(
            "/api/health",
            headers={
                "Origin": allowed_origin,
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Content-Type,Authorization",
            },
        )

        assert response.status_code == 200
        assert response.headers["access-control-allow-origin"] == allowed_origin
        assert response.headers["access-control-allow-credentials"] == "true"
        assert "GET" in response.headers["access-control-allow-methods"]
        assert "Content-Type" in response.headers["access-control-allow-headers"]
        assert "Authorization" in response.headers["access-control-allow-headers"]

    def test_disallowed_origin_gets_no_cors_header(self, test_client) -> None:
        response = test_client.get("/api/health", headers={"Origin": "http://malicious-site.com"})

        assert "access-control-allow-origin" not in response.headers

    def test_csrf_token_endpoint_returns_unified_response(self, test_client) -> None:
        response = test_client.get("/api/csrf-token")
        payload = response.json()

        assert response.status_code == 200
        assert payload["success"] is True
        assert payload["code"] == 200
        assert payload["data"]["token_type"] == "Bearer"
        assert payload["data"]["expires_in"] == 3600
        assert len(payload["data"]["csrf_token"]) > 30

    def test_csrf_token_endpoint_rejects_unsupported_post_method(self, test_client) -> None:
        response = test_client.post("/api/csrf-token")

        assert response.status_code == 405
        assert response.json() == {"detail": "Method Not Allowed"}

    def test_auth_me_without_credentials_returns_403(self, test_client) -> None:
        response = test_client.get("/api/v1/auth/me")

        assert response.status_code == 403
        assert response.json() == {"code": 6001, "message": "Not authenticated"}

    def test_auth_me_with_invalid_bearer_token_returns_401(self, test_client) -> None:
        response = test_client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalid-token"})
        payload = response.json()

        assert response.status_code == 401
        assert payload["code"] == 6000
        assert "Invalid credentials" in payload["message"]

    def test_dashboard_summary_requires_user_id(self, test_client) -> None:
        response = test_client.get("/api/dashboard/summary")

        assert response.status_code == 422
        assert response.json() == {"code": 1001, "message": "输入参数验证失败"}

    def test_unknown_api_route_returns_not_found(self, test_client) -> None:
        response = test_client.get("/api/nonexistent")

        assert response.status_code == 404
        assert response.json() == {"detail": "Not Found"}
