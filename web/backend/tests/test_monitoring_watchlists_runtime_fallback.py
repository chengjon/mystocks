import importlib
import os
import sys
import types
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

os.environ.setdefault("POSTGRESQL_HOST", "localhost")
os.environ.setdefault("POSTGRESQL_USER", "tester")
os.environ.setdefault("POSTGRESQL_PASSWORD", "tester")
os.environ.setdefault("POSTGRESQL_DATABASE", "tester")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key")
os.environ.setdefault("BACKEND_PORT", "8128")
os.environ.setdefault("BACKEND_BACKUP_PORT", "8129")
os.environ.setdefault("TESTING", "true")

PROJECT_ROOT = Path(__file__).resolve().parents[3]
BACKEND_APP_ROOT = PROJECT_ROOT / "web/backend/app"


def _load_watchlists_api():
    import app  # noqa: F401

    api_package = types.ModuleType("app.api")
    api_package.__path__ = [str(BACKEND_APP_ROOT / "api")]
    sys.modules["app.api"] = api_package

    module_name = "app.api.monitoring_watchlists"
    module_path = BACKEND_APP_ROOT / "api/monitoring_watchlists.py"
    spec = spec_from_file_location(module_name, module_path)
    module = module_from_spec(spec)
    assert spec is not None
    assert spec.loader is not None
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


watchlists_api = _load_watchlists_api()
postgres_module = importlib.import_module("src.monitoring.infrastructure.postgresql_async_v3")


class _DisconnectedPostgres:
    def is_connected(self):
        return False


def _payload(result):
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result


def _build_client(monkeypatch):
    monkeypatch.setattr(postgres_module, "get_postgres_async", lambda: _DisconnectedPostgres())
    app = FastAPI()
    app.include_router(watchlists_api.router, prefix="/api/v1/monitoring/watchlists")
    return TestClient(app)


def _reset_runtime_state(monkeypatch):
    monkeypatch.setattr(watchlists_api, "_runtime_watchlists", None, raising=False)
    monkeypatch.setattr(watchlists_api, "_runtime_watchlist_stocks", None, raising=False)


async def test_list_watchlists_returns_runtime_fallback_when_db_unavailable(monkeypatch):
    _reset_runtime_state(monkeypatch)
    monkeypatch.setenv("TESTING", "true")
    monkeypatch.setattr(postgres_module, "get_postgres_async", lambda: _DisconnectedPostgres())

    result = await watchlists_api.list_watchlists(user_id=1)
    payload = _payload(result)

    assert len(payload["data"]) >= 1
    assert payload["data"][0]["name"] == "核心止损监控"
    assert payload["data"][0]["stocks_count"] >= 1


async def test_create_watchlist_returns_runtime_fallback_when_db_unavailable(monkeypatch):
    _reset_runtime_state(monkeypatch)
    monkeypatch.setenv("TESTING", "true")
    monkeypatch.setattr(postgres_module, "get_postgres_async", lambda: _DisconnectedPostgres())

    result = await watchlists_api.create_watchlist(
        request=watchlists_api.CreateWatchlistRequest(name="Route Test List", watchlist_type="manual"),
        user_id=1,
    )
    payload = _payload(result)

    assert payload["data"]["name"] == "Route Test List"
    assert payload["data"]["watchlist_type"] == "manual"
    assert payload["data"]["stocks_count"] == 0


async def test_list_watchlist_stocks_returns_runtime_fallback_when_db_unavailable(monkeypatch):
    _reset_runtime_state(monkeypatch)
    monkeypatch.setenv("TESTING", "true")
    monkeypatch.setattr(postgres_module, "get_postgres_async", lambda: _DisconnectedPostgres())

    result = await watchlists_api.list_watchlist_stocks(watchlist_id=1, user_id=1)
    payload = _payload(result)

    assert len(payload["data"]) >= 1
    assert payload["data"][0]["stock_code"] == "000001"
    assert payload["data"][0]["stop_loss_price"] > 0


async def test_get_watchlist_returns_runtime_fallback_when_db_unavailable(monkeypatch):
    _reset_runtime_state(monkeypatch)
    monkeypatch.setenv("TESTING", "true")
    monkeypatch.setattr(postgres_module, "get_postgres_async", lambda: _DisconnectedPostgres())

    result = await watchlists_api.get_watchlist(watchlist_id=1, user_id=1)
    payload = _payload(result)

    assert payload["data"]["id"] == 1
    assert payload["data"]["name"] == "核心止损监控"
    assert payload["data"]["stocks_count"] >= 1


async def test_update_watchlist_returns_runtime_fallback_when_db_unavailable(monkeypatch):
    _reset_runtime_state(monkeypatch)
    monkeypatch.setenv("TESTING", "true")
    monkeypatch.setattr(postgres_module, "get_postgres_async", lambda: _DisconnectedPostgres())

    result = await watchlists_api.update_watchlist(
        watchlist_id=1,
        request=watchlists_api.UpdateWatchlistRequest(
            name="趋势跟踪池",
            watchlist_type="strategy",
            risk_profile={"risk_tolerance": 70},
            is_active=False,
        ),
        user_id=1,
    )
    payload = _payload(result)

    assert payload["data"]["id"] == 1
    assert payload["data"]["name"] == "趋势跟踪池"
    assert payload["data"]["watchlist_type"] == "strategy"
    assert payload["data"]["risk_profile"] == {"risk_tolerance": 70}
    assert payload["data"]["is_active"] is False
    assert payload["data"]["stocks_count"] >= 1


async def test_add_stock_to_watchlist_uses_runtime_fallback_when_db_unavailable(monkeypatch):
    _reset_runtime_state(monkeypatch)
    monkeypatch.setenv("TESTING", "true")
    monkeypatch.setattr(postgres_module, "get_postgres_async", lambda: _DisconnectedPostgres())

    result = await watchlists_api.add_stock_to_watchlist(
        watchlist_id=1,
        request=watchlists_api.AddStockRequest(
            stock_code="300750.SZ",
            entry_price=210.35,
            stop_loss_price=198.0,
            target_price=228.0,
            weight=0.15,
        ),
        user_id=1,
    )
    payload = _payload(result)

    assert payload["data"]["stock_code"] == "300750.SZ"
    assert payload["data"]["watchlist_id"] == 1
    assert payload["data"]["stop_loss_price"] == 198.0


async def test_remove_stock_from_watchlist_uses_runtime_fallback_when_db_unavailable(monkeypatch):
    _reset_runtime_state(monkeypatch)
    monkeypatch.setenv("TESTING", "true")
    monkeypatch.setattr(postgres_module, "get_postgres_async", lambda: _DisconnectedPostgres())

    await watchlists_api.add_stock_to_watchlist(
        watchlist_id=1,
        request=watchlists_api.AddStockRequest(
            stock_code="300750.SZ",
            entry_price=210.35,
            stop_loss_price=198.0,
            target_price=228.0,
            weight=0.15,
        ),
        user_id=1,
    )

    result = await watchlists_api.remove_stock_from_watchlist(
        watchlist_id=1,
        stock_code="300750.SZ",
        user_id=1,
    )
    payload = _payload(result)

    assert payload["message"] == "移除股票成功"

    stock_rows = await watchlists_api.list_watchlist_stocks(watchlist_id=1, user_id=1)
    stock_payload = _payload(stock_rows)
    assert all(item["stock_code"] != "300750.SZ" for item in stock_payload["data"])


async def test_delete_watchlist_uses_runtime_fallback_when_db_unavailable(monkeypatch):
    _reset_runtime_state(monkeypatch)
    monkeypatch.setenv("TESTING", "true")
    monkeypatch.setattr(postgres_module, "get_postgres_async", lambda: _DisconnectedPostgres())

    result = await watchlists_api.delete_watchlist(watchlist_id=1, user_id=1)
    payload = _payload(result)

    assert payload["message"] == "删除清单成功"

    watchlists = await watchlists_api.list_watchlists(user_id=1)
    watchlists_payload = _payload(watchlists)
    assert all(item["id"] != 1 for item in watchlists_payload["data"])


def test_watchlist_read_endpoints_keep_unified_response_shape_in_fallback(monkeypatch):
    _reset_runtime_state(monkeypatch)
    monkeypatch.setenv("TESTING", "true")

    with _build_client(monkeypatch) as client:
        watchlists_response = client.get("/api/v1/monitoring/watchlists")
        stocks_response = client.get("/api/v1/monitoring/watchlists/1/stocks")

    watchlists_payload = watchlists_response.json()
    stocks_payload = stocks_response.json()

    assert watchlists_response.status_code == 200
    assert watchlists_payload["success"] is True
    assert watchlists_payload["data"][0]["name"] == "核心止损监控"

    assert stocks_response.status_code == 200
    assert stocks_payload["success"] is True
    assert stocks_payload["data"][0]["stock_code"] == "000001"


def test_watchlist_update_endpoint_keeps_unified_response_shape_in_fallback(monkeypatch):
    _reset_runtime_state(monkeypatch)
    monkeypatch.setenv("TESTING", "true")

    with _build_client(monkeypatch) as client:
        update_response = client.put(
            "/api/v1/monitoring/watchlists/1",
            json={
                "name": "趋势跟踪池",
                "watchlist_type": "strategy",
                "risk_profile": {"risk_tolerance": 80},
                "is_active": False,
            },
        )

    payload = update_response.json()

    assert update_response.status_code == 200
    assert payload["success"] is True
    assert payload["data"]["id"] == 1
    assert payload["data"]["name"] == "趋势跟踪池"
    assert payload["data"]["watchlist_type"] == "strategy"
