"""Focused contract tests for strategy backtest status routes."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from importlib import import_module
from pathlib import Path
import sys
import types
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

import app  # noqa: E402


def _prepare_router_imports():
    api_package = types.ModuleType("app.api")
    api_package.__path__ = [str(BACKEND_ROOT / "app" / "api")]
    sys.modules["app.api"] = api_package

    strategy_management_package = types.ModuleType("app.api.strategy_management")
    strategy_management_package.__path__ = [str(BACKEND_ROOT / "app" / "api" / "strategy_management")]
    sys.modules["app.api.strategy_management"] = strategy_management_package

    mock_module = types.ModuleType("app.mock.unified_mock_data")

    def _get_mock_data_manager():
        raise RuntimeError("mock data manager is not used in focused status contract tests")

    def _get_backtest_data():
        return {
            "task_id": "focused-contract-task",
            "status": "completed",
            "summary": None,
            "equity_curve": [],
            "trades": [],
            "error_message": None,
        }

    mock_module.get_mock_data_manager = _get_mock_data_manager
    mock_module.get_backtest_data = _get_backtest_data
    sys.modules["app.mock.unified_mock_data"] = mock_module

    task_tail_module = types.ModuleType("app.api.strategy_management._strategy_management_task_tail")

    def _noop_task(*args, **kwargs):
        return None

    task_tail_module.run_backtest_task = _noop_task
    task_tail_module.train_model_task = _noop_task
    sys.modules["app.api.strategy_management._strategy_management_task_tail"] = task_tail_module

    unified_manager_module = types.ModuleType("unified_manager")

    class _FocusedMyStocksUnifiedManager:
        pass

    unified_manager_module.MyStocksUnifiedManager = _FocusedMyStocksUnifiedManager
    sys.modules["unified_manager"] = unified_manager_module

    strategy_management_module = import_module("app.api.strategy_management.get_monitoring_db")
    strategy_mgmt_module = import_module("app.api.strategy_mgmt")
    return strategy_management_module, strategy_mgmt_module


STRATEGY_MANAGEMENT_MODULE, STRATEGY_MGMT_MODULE = _prepare_router_imports()


def _unwrap_payload(response) -> dict[str, Any]:
    payload = response.json()
    if isinstance(payload, dict) and isinstance(payload.get("data"), dict):
        return payload["data"]
    return payload


@dataclass
class _FakeBacktest:
    backtest_id: int
    status: Any
    created_at: datetime | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error_message: str | None = None
    performance_metrics: dict[str, Any] | None = None


class _FakeStatus:
    def __init__(self, value: str):
        self.value = value


class _FakeBacktestRepository:
    def __init__(self, records: dict[int, _FakeBacktest]):
        self._records = records

    def get_backtest(self, backtest_id: int) -> _FakeBacktest | None:
        return self._records.get(backtest_id)


@pytest.fixture
def focused_app():
    test_app = FastAPI()
    test_app.include_router(STRATEGY_MANAGEMENT_MODULE.router)
    test_app.include_router(STRATEGY_MGMT_MODULE.router)
    yield test_app
    test_app.dependency_overrides.clear()


@pytest.fixture
def client(focused_app):
    with TestClient(focused_app) as test_client:
        yield test_client


@pytest.fixture
def override_backtest_status_repositories(focused_app):

    def _apply(records: dict[int, _FakeBacktest]) -> None:
        def _override_repo() -> _FakeBacktestRepository:
            return _FakeBacktestRepository(records)

        v1_dependency = getattr(STRATEGY_MANAGEMENT_MODULE, "get_backtest_repository", None)
        if v1_dependency is not None:
            focused_app.dependency_overrides[v1_dependency] = _override_repo

        focused_app.dependency_overrides[STRATEGY_MGMT_MODULE.get_backtest_repository] = _override_repo

    yield _apply
    focused_app.dependency_overrides.clear()


def test_v1_backtest_status_route_is_published_in_openapi(client):
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert "/api/v1/strategy/backtest/status/{backtest_id}" in response.json()["paths"]


def test_v1_backtest_status_openapi_documents_response_contract(client):
    response = client.get("/openapi.json")

    assert response.status_code == 200
    schema = (
        response.json()["paths"]["/api/v1/strategy/backtest/status/{backtest_id}"]["get"]["responses"]["200"][
            "content"
        ]["application/json"]["schema"]
    )

    assert schema["$ref"] == "#/components/schemas/BacktestStatusResponse"

    response_schema = response.json()["components"]["schemas"]["BacktestStatusResponse"]
    assert set(response_schema["properties"]) >= {
        "backtest_id",
        "status",
        "created_at",
        "started_at",
        "completed_at",
        "error_message",
        "has_results",
    }


def test_legacy_backtest_status_route_is_marked_deprecated_in_openapi(client):
    response = client.get("/openapi.json")

    assert response.status_code == 200
    operation = response.json()["paths"]["/api/strategy-mgmt/backtest/status/{backtest_id}"]["get"]
    assert operation["deprecated"] is True
    assert operation["responses"]["200"]["content"]["application/json"]["schema"]["$ref"] == (
        "#/components/schemas/BacktestStatusResponse"
    )


@pytest.mark.parametrize("status_value", ["pending", "running", "completed", "failed"])
def test_v1_backtest_status_returns_contract_shape_for_supported_statuses(
    client, override_backtest_status_repositories, status_value: str
):
    backtest_id = 321
    override_backtest_status_repositories(
        {
            backtest_id: _FakeBacktest(
                backtest_id=backtest_id,
                status=_FakeStatus(status_value),
                created_at=datetime(2026, 3, 10, 9, 0, 0),
                performance_metrics={"sharpe_ratio": 1.1} if status_value == "completed" else None,
            )
        }
    )

    response = client.get(f"/api/v1/strategy/backtest/status/{backtest_id}")

    assert response.status_code == 200
    payload = _unwrap_payload(response)
    assert payload["backtest_id"] == backtest_id
    assert payload["status"] == status_value


def test_v1_backtest_status_returns_not_found_for_missing_backtest(client, override_backtest_status_repositories):
    override_backtest_status_repositories({})

    response = client.get("/api/v1/strategy/backtest/status/999999")

    assert response.status_code == 404


def test_legacy_backtest_status_route_still_exists_for_compatibility(client, override_backtest_status_repositories):
    backtest_id = 654
    override_backtest_status_repositories(
        {
            backtest_id: _FakeBacktest(
                backtest_id=backtest_id,
                status=_FakeStatus("running"),
                created_at=datetime(2026, 3, 10, 9, 0, 0),
                started_at=datetime(2026, 3, 10, 9, 1, 0),
            )
        }
    )

    response = client.get(f"/api/strategy-mgmt/backtest/status/{backtest_id}")

    assert response.status_code == 200
    payload = _unwrap_payload(response)
    assert payload["backtest_id"] == backtest_id
    assert payload["status"] == "running"


def test_v1_and_legacy_status_routes_return_compatible_payloads(client, override_backtest_status_repositories):
    backtest_id = 888
    record = _FakeBacktest(
        backtest_id=backtest_id,
        status=_FakeStatus("completed"),
        created_at=datetime(2026, 3, 10, 9, 0, 0),
        started_at=datetime(2026, 3, 10, 9, 1, 0),
        completed_at=datetime(2026, 3, 10, 9, 2, 0),
        error_message=None,
        performance_metrics={"sharpe_ratio": 1.8},
    )
    override_backtest_status_repositories({backtest_id: record})

    v1_response = client.get(f"/api/v1/strategy/backtest/status/{backtest_id}")
    legacy_response = client.get(f"/api/strategy-mgmt/backtest/status/{backtest_id}")

    assert v1_response.status_code == 200
    assert legacy_response.status_code == 200

    v1_payload = _unwrap_payload(v1_response)
    legacy_payload = _unwrap_payload(legacy_response)

    assert v1_payload == legacy_payload
    assert v1_payload == {
        "backtest_id": backtest_id,
        "status": "completed",
        "created_at": "2026-03-10T09:00:00",
        "started_at": "2026-03-10T09:01:00",
        "completed_at": "2026-03-10T09:02:00",
        "error_message": None,
        "has_results": True,
    }
