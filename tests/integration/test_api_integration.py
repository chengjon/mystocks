"""
Application-level integration contracts for current versioned API routes.

This file replaces the historical subprocess/requests smoke tests that relied
on a mismatched port, legacy unversioned routes, and `ConnectionError`-based
skips. The current tests import the real backend app and validate the active
route surface directly.
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

# Keep pytest timing output stable when this file runs in isolation.
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
def test_client(backend_app_module):
    backend_app_module.csrf_manager.tokens.clear()
    client = TestClient(backend_app_module.app)
    yield client
    client.close()
    backend_app_module.csrf_manager.tokens.clear()


class TestAPIIntegration:
    def test_openapi_exposes_current_versioned_routes_and_not_legacy_paths(self, backend_app_module) -> None:
        schema_paths = set(backend_app_module.app.openapi()["paths"])

        assert "/api/health" in schema_paths
        assert "/api/v1/data/stocks/basic" in schema_paths
        assert "/api/v1/technical/{symbol}/indicators" in schema_paths
        assert "/api/v1/monitoring/realtime" in schema_paths
        assert "/api/v1/strategy/definitions" in schema_paths

        assert "/api/stocks/health" not in schema_paths
        assert "/api/stocks/list" not in schema_paths
        assert "/api/monitoring/realtime" not in schema_paths
        assert "/api/strategy/definitions" not in schema_paths

    def test_health_endpoint_uses_current_public_route(self, test_client) -> None:
        response = test_client.get("/api/health")
        payload = response.json()

        assert response.status_code == 200
        assert payload["status"] == "healthy"
        assert payload["version"] == "1.0.0"
        assert isinstance(payload["timestamp"], float)

    def test_legacy_stock_and_strategy_paths_are_gone(self, test_client) -> None:
        legacy_paths = [
            "/api/stocks/health",
            "/api/stocks/list?page=1&limit=10",
            "/api/monitoring/realtime",
            "/api/strategy/definitions",
            "/api/technical/000001/indicators",
        ]

        for path in legacy_paths:
            response = test_client.get(path)
            assert response.status_code == 404
            assert response.json() == {"detail": "Not Found"}

    def test_versioned_stock_list_route_requires_authentication(self, test_client) -> None:
        response = test_client.get("/api/v1/data/stocks/basic")

        assert response.status_code == 401
        assert response.json() == {"code": 6000, "message": "Not authenticated"}

    def test_versioned_technical_indicator_route_returns_current_shape(self, test_client) -> None:
        response = test_client.get("/api/v1/technical/000001/indicators")
        payload = response.json()

        assert response.status_code == 200
        assert payload["symbol"] == "000001"
        assert {
            "latest_price",
            "latest_date",
            "data_points",
            "total_indicators",
            "trend",
            "momentum",
            "volatility",
            "volume",
        }.issubset(payload.keys())

    def test_versioned_monitoring_routes_require_authentication(self, test_client) -> None:
        list_response = test_client.get("/api/v1/monitoring/realtime")
        symbol_response = test_client.get("/api/v1/monitoring/realtime/600519")

        assert list_response.status_code == 401
        assert symbol_response.status_code == 401
        assert list_response.json() == {"code": 6000, "message": "Not authenticated"}
        assert symbol_response.json() == {"code": 6000, "message": "Not authenticated"}

    def test_strategy_definitions_route_returns_live_contract(self, test_client) -> None:
        response = test_client.get("/api/v1/strategy/definitions")
        payload = response.json()

        assert response.status_code == 200
        assert payload["success"] is True
        assert isinstance(payload["data"]["definitions"], list)
        assert payload["data"]["total"] == len(payload["data"]["definitions"])
        assert any(item["code"] == "volume_surge" for item in payload["data"]["definitions"])

    def test_strategy_run_single_rejects_get_requests(self, test_client) -> None:
        response = test_client.get("/api/v1/strategy/run/single")

        assert response.status_code == 405
        assert response.json() == {"detail": "Method Not Allowed"}
