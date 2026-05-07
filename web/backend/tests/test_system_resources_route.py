from __future__ import annotations

import importlib
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = ROOT / "web" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


def _load_module():
    sys.modules.pop("app.api.v1.system.resources", None)
    return importlib.import_module("app.api.v1.system.resources")


def _load_v1_router():
    sys.modules.pop("app.api.v1.router", None)
    return importlib.import_module("app.api.v1.router")


def _build_client(router) -> TestClient:
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    return TestClient(app)


def test_api_v1_router_registers_system_resources_path():
    module = _load_v1_router()
    app = FastAPI()
    app.include_router(module.api_v1_router)

    paths = {route.path for route in app.routes}

    assert "/api/v1/system/resources" in paths


def test_system_resources_route_returns_unified_contract(monkeypatch):
    module = _load_module()
    captured: dict[str, object] = {}
    expected = {
        "node": {
            "node_id": "local-runtime",
            "scope": "single-node",
            "window_minutes": 30,
            "sampled_at": "2026-05-07T00:00:00+00:00",
            "polling_interval_seconds": 15,
        },
        "host": {
            "cpu": {
                "metric_key": "cpu_percent",
                "label": "CPU",
                "unit": "%",
                "current_value": 35.0,
                "status": "normal",
                "warning_threshold": 70.0,
                "critical_threshold": 90.0,
                "series": [{"timestamp": "2026-05-07T00:00:00+00:00", "value": 35.0}],
            }
        },
        "processes": [],
        "dependencies": [],
        "thresholds": {"host.cpu_percent": {"warning": 70.0, "critical": 90.0, "unit": "%"}},
    }

    async def _fake_collect_resource_metrics(**kwargs):
        captured.update(kwargs)
        return expected

    monkeypatch.setattr(module, "collect_resource_metrics", _fake_collect_resource_metrics)

    client = _build_client(module.router)
    response = client.get(
        "/api/v1/system/resources",
        params={"window_minutes": 30, "include_processes": "false"},
    )

    assert response.status_code == 200
    assert captured == {
        "window_minutes": 30,
        "include_processes": False,
        "include_dependencies": True,
    }
    assert response.json()["data"] == expected


def test_system_resources_openapi_docs_have_examples_and_error_responses():
    module = _load_module()
    app = FastAPI()
    app.include_router(module.router, prefix="/api/v1")
    schema = app.openapi()

    operation = schema["paths"]["/api/v1/system/resources"]["get"]
    success_json = operation["responses"]["200"]["content"]["application/json"]
    parameter_names = {param["name"] for param in operation.get("parameters", [])}

    assert operation.get("summary")
    assert len(operation.get("description", "")) >= 20
    assert {"window_minutes", "include_processes", "include_dependencies"} <= parameter_names
    assert "example" in success_json or "examples" in success_json
    assert any(status.startswith("5") for status in operation["responses"])
