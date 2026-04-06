"""
Security contract tests for CSRF and frontend security wiring.

These tests validate the current backend and frontend contracts without relying
on the older `os.chdir()`-based setup or historical frontend assumptions.
"""

import functools
import importlib
import os
import sys
import time
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "web" / "backend"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(1, str(BACKEND_ROOT))

# Keep the timing plugin happy even when this file runs in isolation.
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
os.environ.setdefault("TESTING", "false")


def read_text(relative_path: str) -> str:
    return (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")


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
def in_memory_csrf_manager(monkeypatch, backend_app_module):
    manager = backend_app_module.CSRFTokenManager()
    monkeypatch.setattr(manager, "_get_redis", lambda: None)
    return manager


@pytest.fixture
def test_client(monkeypatch, backend_app_module):
    monkeypatch.setattr(backend_app_module.csrf_manager, "_get_redis", lambda: None)
    backend_app_module.csrf_manager.tokens.clear()
    client = TestClient(backend_app_module.app)
    yield client
    client.close()
    backend_app_module.csrf_manager.tokens.clear()


class TestCSRFTokenManager:
    def test_token_generation_is_unique_and_tracks_metadata(self, in_memory_csrf_manager) -> None:
        token_one = in_memory_csrf_manager.generate_token()
        token_two = in_memory_csrf_manager.generate_token()

        assert isinstance(token_one, str)
        assert isinstance(token_two, str)
        assert token_one != token_two
        assert len(token_one) > 30
        assert token_one in in_memory_csrf_manager.tokens
        assert in_memory_csrf_manager.tokens[token_one]["used"] is False
        assert isinstance(in_memory_csrf_manager.tokens[token_one]["created_at"], float)

    def test_valid_token_is_one_time_use(self, in_memory_csrf_manager) -> None:
        token = in_memory_csrf_manager.generate_token()

        assert in_memory_csrf_manager.validate_token(token) is True
        assert in_memory_csrf_manager.tokens[token]["used"] is True
        assert in_memory_csrf_manager.validate_token(token) is False

    def test_invalid_token_returns_false(self, in_memory_csrf_manager) -> None:
        assert in_memory_csrf_manager.validate_token("invalid-token") is False
        assert in_memory_csrf_manager.validate_token("") is False
        assert in_memory_csrf_manager.validate_token(None) is False

    def test_expired_token_is_removed(self, in_memory_csrf_manager) -> None:
        token = in_memory_csrf_manager.generate_token()
        in_memory_csrf_manager.tokens[token]["created_at"] = time.time() - (in_memory_csrf_manager.token_timeout + 1)

        assert in_memory_csrf_manager.validate_token(token) is False
        assert token not in in_memory_csrf_manager.tokens

    def test_cleanup_expired_tokens_only_removes_stale_entries(self, in_memory_csrf_manager) -> None:
        expired_token = in_memory_csrf_manager.generate_token()
        fresh_token = in_memory_csrf_manager.generate_token()
        in_memory_csrf_manager.tokens[expired_token]["created_at"] = (
            time.time() - (in_memory_csrf_manager.token_timeout + 1)
        )

        in_memory_csrf_manager.cleanup_expired_tokens()

        assert expired_token not in in_memory_csrf_manager.tokens
        assert fresh_token in in_memory_csrf_manager.tokens


class TestCSRFMiddleware:
    def test_csrf_token_endpoint_returns_unified_response(self, test_client) -> None:
        response = test_client.get("/api/csrf-token")
        payload = response.json()

        assert response.status_code == 200
        assert payload["success"] is True
        assert payload["data"]["token_type"] == "Bearer"
        assert payload["data"]["expires_in"] == 3600
        assert len(payload["data"]["csrf_token"]) > 30

    def test_post_without_csrf_token_is_rejected(self, test_client) -> None:
        response = test_client.post("/api/data/example", json={"data": "test"})

        assert response.status_code == 403
        assert response.json() == {
            "code": "CSRF_TOKEN_MISSING",
            "message": "CSRF token is required for this request",
            "data": None,
        }

    def test_post_with_invalid_csrf_token_is_rejected(self, test_client) -> None:
        response = test_client.post(
            "/api/data/example",
            json={"data": "test"},
            headers={"x-csrf-token": "invalid-token"},
        )

        assert response.status_code == 403
        assert response.json() == {
            "code": "CSRF_TOKEN_INVALID",
            "message": "CSRF token is invalid or expired",
            "data": None,
        }

    def test_valid_csrf_token_allows_request_to_reach_next_handler(self, test_client) -> None:
        token = test_client.get("/api/csrf-token").json()["data"]["csrf_token"]

        response = test_client.post(
            "/api/data/example",
            json={"data": "test"},
            headers={"x-csrf-token": token},
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Not Found"

    def test_csrf_token_cannot_be_reused(self, test_client) -> None:
        token = test_client.get("/api/csrf-token").json()["data"]["csrf_token"]

        first_response = test_client.post("/api/data/example", json={}, headers={"x-csrf-token": token})
        second_response = test_client.post("/api/data/example", json={}, headers={"x-csrf-token": token})

        assert first_response.status_code == 404
        assert second_response.status_code == 403
        assert second_response.json()["code"] == "CSRF_TOKEN_INVALID"


class TestFrontendSecurityWiring:
    def test_index_html_keeps_csrf_meta_and_csp_documentation(self) -> None:
        html_content = read_text("web/frontend/index.html")

        assert '<meta name="csrf-token" content="">' in html_content
        assert "Content-Security-Policy" in html_content
        assert "CSP temporarily disabled for debugging" in html_content
        assert "strict-origin-when-cross-origin" in html_content

    def test_http_client_remains_backward_compatible_security_shim(self) -> None:
        js_content = read_text("web/frontend/src/services/httpClient.js")

        assert "class HttpClient" in js_content
        assert "this.csrfToken = null" in js_content
        assert "getCsrfToken()" in js_content
        assert "export async function initializeSecurity()" in js_content
        assert "security bootstrap now handled by apiClient interceptors" in js_content
        assert "apiClient.post" in js_content
        assert "apiClient.put" in js_content
        assert "apiClient.patch" in js_content
        assert "apiClient.delete" in js_content

    def test_api_client_fetches_csrf_token_and_injects_mutation_header(self) -> None:
        api_client = read_text("web/frontend/src/api/apiClient.ts")

        assert "createCSRFTokenResolver" in api_client
        assert "axios.get('/api/csrf-token'" in api_client
        assert "withCredentials: true" in api_client
        assert "config.method?.toUpperCase() !== 'GET'" in api_client
        assert "config.headers['X-CSRF-Token'] = token" in api_client

    def test_main_js_initializes_security_non_blocking(self) -> None:
        js_content = read_text("web/frontend/src/main.js")

        assert "import { initializeSecurity } from './services/httpClient.js'" in js_content
        assert "app.mount('#app')" in js_content
        assert "Promise.race([" in js_content
        assert "initializeSecurity().catch" in js_content
        assert "Security initialization timed out (non-blocking)" in js_content


class TestSecurityBestPractices:
    def test_csrf_token_manager_uses_secure_defaults(self, in_memory_csrf_manager) -> None:
        tokens = [in_memory_csrf_manager.generate_token() for _ in range(50)]

        assert len(set(tokens)) == 50
        assert all(len(token) > 30 for token in tokens)
        assert in_memory_csrf_manager.token_timeout == 3600

    def test_no_hardcoded_runtime_secrets_in_security_entrypoints(self) -> None:
        backend_main = read_text("web/backend/app/main.py")
        http_client = read_text("web/frontend/src/services/httpClient.js")
        api_client = read_text("web/frontend/src/api/apiClient.ts")

        assert "sk-proj-" not in backend_main
        assert "sk-proj-" not in http_client
        assert "sk-proj-" not in api_client
        assert "test-secret-key" not in backend_main
        assert "test-secret-key" not in http_client
        assert "test-secret-key" not in api_client


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
