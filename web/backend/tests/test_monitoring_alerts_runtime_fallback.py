import importlib
import os

from fastapi import FastAPI
from fastapi.testclient import TestClient

os.environ.setdefault("POSTGRESQL_HOST", "localhost")
os.environ.setdefault("POSTGRESQL_USER", "tester")
os.environ.setdefault("POSTGRESQL_PASSWORD", "tester")
os.environ.setdefault("POSTGRESQL_DATABASE", "tester")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key")
os.environ.setdefault("BACKEND_PORT", "8132")
os.environ.setdefault("BACKEND_BACKUP_PORT", "8133")
os.environ.setdefault("TESTING", "true")

monitoring_api = importlib.import_module("web.backend.app.api.monitoring")


def _payload(result):
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result


def _build_client():
    app = FastAPI()
    app.include_router(monitoring_api.router, prefix="/api/v1/monitoring")
    app.dependency_overrides[monitoring_api.get_current_user] = lambda: None
    return TestClient(app)


async def test_get_alert_rules_returns_runtime_fallback_when_db_unavailable(monkeypatch):
    monkeypatch.setenv("TESTING", "true")
    monkeypatch.setattr(
        monitoring_api.monitoring_service,
        "get_alert_rules",
        lambda **_kwargs: (_ for _ in ()).throw(RuntimeError("db unavailable")),
    )

    result = await monitoring_api.get_alert_rules(current_user=None)
    payload = _payload(result)

    assert payload["success"] is True
    assert len(payload["data"]) >= 1
    assert payload["data"][0]["rule_name"] == "核心仓位跌破止损线"


async def test_get_alert_records_returns_runtime_fallback_when_db_unavailable(monkeypatch):
    monkeypatch.setenv("DEVELOPMENT_MODE", "true")
    monkeypatch.setattr(
        monitoring_api.monitoring_service,
        "get_alert_records",
        lambda **_kwargs: (_ for _ in ()).throw(RuntimeError("db unavailable")),
    )

    result = await monitoring_api.get_alert_records(current_user=None)
    payload = _payload(result)

    assert payload["success"] is True
    assert payload["total"] >= 1
    assert payload["data"][0]["symbol"] == "600519"
    assert payload["data"][0]["alert_level"] == "critical"


def test_monitoring_alert_read_endpoints_keep_page_contract_in_fallback(monkeypatch):
    monkeypatch.setenv("TESTING", "true")
    monkeypatch.setattr(
        monitoring_api.monitoring_service,
        "get_alert_rules",
        lambda **_kwargs: (_ for _ in ()).throw(RuntimeError("db unavailable")),
    )
    monkeypatch.setattr(
        monitoring_api.monitoring_service,
        "get_alert_records",
        lambda **_kwargs: (_ for _ in ()).throw(RuntimeError("db unavailable")),
    )

    with _build_client() as client:
        rules_response = client.get("/api/v1/monitoring/alert-rules")
        alerts_response = client.get("/api/v1/monitoring/alerts?page=1&page_size=50")

    rules_payload = rules_response.json()
    alerts_payload = alerts_response.json()

    assert rules_response.status_code == 200
    assert rules_payload["success"] is True
    assert isinstance(rules_payload["data"], list)

    assert alerts_response.status_code == 200
    assert alerts_payload["success"] is True
    assert isinstance(alerts_payload["data"], list)
    assert alerts_payload["total"] >= 1
