import importlib
import os

from fastapi import FastAPI
from fastapi.testclient import TestClient

os.environ.setdefault("POSTGRESQL_HOST", "localhost")
os.environ.setdefault("POSTGRESQL_PORT", "5432")
os.environ.setdefault("POSTGRESQL_USER", "tester")
os.environ.setdefault("POSTGRESQL_PASSWORD", "tester")
os.environ.setdefault("POSTGRESQL_DATABASE", "tester")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key")
os.environ.setdefault("BACKEND_PORT", "8134")
os.environ.setdefault("BACKEND_BACKUP_PORT", "8135")
os.environ.setdefault("TESTING", "true")

strategy_api = importlib.import_module("web.backend.app.api.strategy_management.get_monitoring_db")


class _MonitoringNoop:
    def log_operation(self, *args, **kwargs):
        return True


class _FailingManager:
    def load_data_by_classification(self, **_kwargs):
        raise RuntimeError("db unavailable")

    def save_data_by_classification(self, **_kwargs):
        raise RuntimeError("db unavailable")


def _build_client(monkeypatch):
    monkeypatch.setattr(strategy_api, "MyStocksUnifiedManager", _FailingManager)
    monkeypatch.setattr(strategy_api, "get_monitoring_db", lambda: _MonitoringNoop())
    app = FastAPI()
    app.include_router(strategy_api.router)
    return TestClient(app)


def test_backtest_runtime_fallback_flow_keeps_run_status_result_chain(monkeypatch):
    monkeypatch.setenv("TESTING", "true")
    monkeypatch.setattr(strategy_api, "_runtime_backtest_store", [], raising=False)

    with _build_client(monkeypatch) as client:
        run_response = client.post(
            "/api/v1/strategy/backtest/run",
            json={
                "strategy_name": "API Availability Probe",
                "symbols": ["ALL"],
                "start_date": "2025-01-01",
                "end_date": "2025-12-31",
                "initial_capital": 1000000,
                "parameters": {"benchmark": "csi300", "period": "1y", "strategy_id": "900001"},
            },
        )

        run_payload = run_response.json()
        backtest_id = run_payload["backtest_id"]

        status_response = client.get(f"/api/v1/strategy/backtest/status/{backtest_id}")
        result_response = client.get(f"/api/v1/strategy/backtest/results/{backtest_id}")
        list_response = client.get("/api/v1/strategy/backtest/results")

    status_payload = status_response.json()
    result_payload = result_response.json()
    list_payload = list_response.json()

    assert run_response.status_code == 200
    assert backtest_id >= 950001

    assert status_response.status_code == 200
    assert status_payload["backtest_id"] == backtest_id
    assert status_payload["status"] == "completed"
    assert status_payload["has_results"] is True

    assert result_response.status_code == 200
    assert result_payload["id"] == backtest_id
    assert result_payload["performance"]["total_return"] > 0
    assert result_payload["start_date"] == "2025-01-01"
    assert result_payload["end_date"] == "2025-12-31"

    assert list_response.status_code == 200
    assert list_payload["total"] == 1
    assert list_payload["items"][0]["id"] == backtest_id
