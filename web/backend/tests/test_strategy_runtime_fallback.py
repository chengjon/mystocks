import importlib
import os

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

os.environ.setdefault("POSTGRESQL_HOST", "localhost")
os.environ.setdefault("POSTGRESQL_USER", "tester")
os.environ.setdefault("POSTGRESQL_PASSWORD", "tester")
os.environ.setdefault("POSTGRESQL_DATABASE", "tester")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key")
os.environ.setdefault("BACKEND_PORT", "8121")
os.environ.setdefault("BACKEND_BACKUP_PORT", "8122")
os.environ.setdefault("TESTING", "true")

strategy_api = importlib.import_module("web.backend.app.api.strategy_management.get_monitoring_db")


class _EmptyFrame:
    def __len__(self):
        return 0


class _MonitoringNoop:
    def log_operation(self, *args, **kwargs):
        return True


class _SpyManager:
    def __init__(self):
        self.load_calls = []

    def load_data_by_classification(self, **kwargs):
        self.load_calls.append(kwargs)
        return _EmptyFrame()


class _FailingManager:
    def load_data_by_classification(self, **_kwargs):
        raise RuntimeError("db unavailable")

    def save_data_by_classification(self, **_kwargs):
        raise RuntimeError("db unavailable")


class _FalseSavingManager:
    def load_data_by_classification(self, **_kwargs):
        return _EmptyFrame()

    def save_data_by_classification(self, **_kwargs):
        return False


@pytest.fixture(autouse=True)
def reset_runtime_fallback(monkeypatch):
    monkeypatch.setattr(strategy_api, "_runtime_strategy_store", [], raising=False)
    monkeypatch.setattr(strategy_api, "get_monitoring_db", lambda: _MonitoringNoop())


def _build_client(monkeypatch, manager_cls):
    monkeypatch.setattr(strategy_api, "MyStocksUnifiedManager", manager_cls)
    app = FastAPI()
    app.include_router(strategy_api.router)
    return TestClient(app)


def _payload(result):
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result


@pytest.mark.asyncio
async def test_list_strategies_reads_same_store_as_strategy_crud(monkeypatch):
    manager = _SpyManager()

    monkeypatch.setenv("USE_MOCK_DATA", "false")
    monkeypatch.setattr(strategy_api, "MyStocksUnifiedManager", lambda: manager)

    result = await strategy_api.list_strategies(status=None, page=1, page_size=20)
    payload = _payload(result)

    assert payload["data"] == {"items": [], "total": 0, "page": 1, "page_size": 20}
    assert len(manager.load_calls) == 1
    assert manager.load_calls[0]["classification"] == strategy_api.DataClassification.MODEL_OUTPUT
    assert manager.load_calls[0]["table_name"] == "strategies"


@pytest.mark.asyncio
async def test_create_strategy_uses_runtime_fallback_when_db_unavailable_in_testing(monkeypatch):
    monkeypatch.setenv("USE_MOCK_DATA", "false")
    monkeypatch.setenv("TESTING", "true")
    monkeypatch.setattr(strategy_api, "MyStocksUnifiedManager", _FailingManager)

    result = await strategy_api.create_strategy(
        {
            "name": "Alpha",
            "description": "Fallback test",
            "strategy_type": "trend_following",
            "parameters": {"custom": {"window": 20}},
        }
    )
    payload = _payload(result)

    assert payload["message"] == "策略创建成功"
    assert payload["data"]["strategy_name"] == "Alpha"
    assert payload["data"]["strategy_type"] == "trend_following"
    assert payload["data"]["status"] == "draft"


@pytest.mark.asyncio
async def test_list_strategies_returns_runtime_fallback_after_create(monkeypatch):
    monkeypatch.setenv("USE_MOCK_DATA", "false")
    monkeypatch.setenv("TESTING", "true")
    monkeypatch.setattr(strategy_api, "MyStocksUnifiedManager", _FailingManager)

    create_result = await strategy_api.create_strategy(
        {
            "name": "Beta",
            "description": "Persist fallback row",
            "strategy_type": "mean_reversion",
        }
    )
    create_payload = _payload(create_result)

    result = await strategy_api.list_strategies(status=None, page=1, page_size=20)
    payload = _payload(result)

    assert payload["data"]["total"] == 1
    assert len(payload["data"]["items"]) == 1
    assert payload["data"]["items"][0]["strategy_name"] == create_payload["data"]["strategy_name"]
    assert payload["data"]["items"][0]["strategy_type"] == "mean_reversion"


@pytest.mark.asyncio
async def test_create_strategy_uses_runtime_fallback_when_manager_returns_false(monkeypatch):
    monkeypatch.setenv("USE_MOCK_DATA", "false")
    monkeypatch.setenv("TESTING", "true")
    monkeypatch.setattr(strategy_api, "MyStocksUnifiedManager", _FalseSavingManager)

    result = await strategy_api.create_strategy(
        {
            "name": "Gamma",
            "description": "False result fallback",
            "strategy_type": "breakout",
        }
    )
    payload = _payload(result)

    assert payload["message"] == "策略创建成功"
    assert payload["data"]["strategy_name"] == "Gamma"
    assert payload["data"]["strategy_type"] == "breakout"


@pytest.mark.asyncio
async def test_list_strategies_prefers_runtime_store_when_database_returns_empty(monkeypatch):
    monkeypatch.setenv("USE_MOCK_DATA", "false")
    monkeypatch.setenv("TESTING", "true")
    monkeypatch.setattr(strategy_api, "MyStocksUnifiedManager", _FalseSavingManager)

    await strategy_api.create_strategy(
        {
            "name": "Delta",
            "description": "Runtime store list fallback",
            "strategy_type": "grid",
        }
    )

    result = await strategy_api.list_strategies(status=None, page=1, page_size=20)
    payload = _payload(result)

    assert payload["data"]["total"] == 1
    assert payload["data"]["items"][0]["strategy_name"] == "Delta"
    assert payload["data"]["items"][0]["strategy_type"] == "grid"


def test_http_strategy_crud_responses_use_unified_response_shape(monkeypatch):
    monkeypatch.setenv("USE_MOCK_DATA", "false")
    monkeypatch.setenv("TESTING", "true")

    with _build_client(monkeypatch, _FalseSavingManager) as client:
        create_response = client.post(
            "/api/v1/strategy/strategies",
            json={
                "name": "HTTP Contract Strategy",
                "description": "Contract probe",
                "strategy_type": "trend_following",
            },
        )
        list_response = client.get("/api/v1/strategy/strategies")

    create_payload = create_response.json()
    list_payload = list_response.json()

    assert create_response.status_code == 200
    assert create_payload["success"] is True
    assert create_payload["data"]["strategy_name"] == "HTTP Contract Strategy"

    assert list_response.status_code == 200
    assert list_payload["success"] is True
    assert list_payload["data"]["total"] == 1


def test_http_strategy_lifecycle_endpoints_update_runtime_fallback_status(monkeypatch):
    monkeypatch.setenv("USE_MOCK_DATA", "false")
    monkeypatch.setenv("TESTING", "true")

    with _build_client(monkeypatch, _FailingManager) as client:
        create_response = client.post(
            "/api/v1/strategy/strategies",
            json={
                "name": "Lifecycle Contract Strategy",
                "description": "Lifecycle probe",
                "strategy_type": "trend_following",
                "status": "archived",
            },
        )

        created_payload = create_response.json()
        strategy_id = created_payload["data"]["strategy_id"]

        start_response = client.post(f"/api/v1/strategy/{strategy_id}/start")
        pause_response = client.post(f"/api/v1/strategy/{strategy_id}/pause")
        resume_response = client.post(f"/api/v1/strategy/{strategy_id}/resume")
        stop_response = client.post(f"/api/v1/strategy/{strategy_id}/stop")

    assert start_response.status_code == 200
    assert start_response.json()["success"] is True
    assert start_response.json()["data"]["status"] == "active"

    assert pause_response.status_code == 200
    assert pause_response.json()["success"] is True
    assert pause_response.json()["data"]["status"] == "paused"

    assert resume_response.status_code == 200
    assert resume_response.json()["success"] is True
    assert resume_response.json()["data"]["status"] == "active"

    assert stop_response.status_code == 200
    assert stop_response.json()["success"] is True
    assert stop_response.json()["data"]["status"] == "archived"
