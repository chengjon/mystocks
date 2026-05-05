from __future__ import annotations

import asyncio
import importlib
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api._technical_patterns_models import PatternAnchorPoint, PatternDetection, PatternDetectionData


def _import_patterns_router_module():
    backend_root = Path("web/backend").resolve()
    backend_root_str = str(backend_root)
    if backend_root_str not in sys.path:
        sys.path.insert(0, backend_root_str)

    sys.modules.pop("app.api._technical_patterns_router", None)
    return importlib.import_module("app.api._technical_patterns_router")


def test_detect_patterns_returns_empty_structured_payload_when_service_finds_nothing(monkeypatch):
    module = _import_patterns_router_module()

    async def _fake_detect(*_args, **_kwargs):
        return []

    monkeypatch.setattr(module, "_detect_patterns_for_symbol", _fake_detect)

    response = asyncio.run(module.detect_patterns(symbol="600519.SH", period="weekly"))

    assert response.success is True
    assert response.code == 200
    assert isinstance(response.data, PatternDetectionData)
    assert response.data.status == "empty"
    assert response.data.symbol == "600519.SH"
    assert response.data.period == "weekly"
    assert response.data.patterns == []


def test_detect_patterns_normalizes_uppercase_period_query(monkeypatch):
    module = _import_patterns_router_module()

    async def _fake_detect(*_args, **_kwargs):
        return []

    monkeypatch.setattr(module, "_detect_patterns_for_symbol", _fake_detect)

    app = FastAPI()
    app.include_router(module.router)
    client = TestClient(app)

    response = client.get("/patterns/600519.SH", params={"period": "WEEKLY"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["symbol"] == "600519.SH"
    assert payload["data"]["period"] == "weekly"
    assert payload["data"]["status"] == "empty"
    assert payload["data"]["patterns"] == []


def test_detect_patterns_openapi_documents_supported_period_values():
    module = _import_patterns_router_module()

    app = FastAPI()
    app.include_router(module.router)

    operation = app.openapi()["paths"]["/patterns/{symbol}"]["get"]
    period_parameter = next(parameter for parameter in operation["parameters"] if parameter["name"] == "period")

    assert period_parameter["schema"]["enum"] == ["daily", "weekly", "monthly"]


def test_detect_patterns_rejects_unsupported_period_query():
    module = _import_patterns_router_module()

    app = FastAPI()
    app.include_router(module.router)
    client = TestClient(app)

    response = client.get("/patterns/600519.SH", params={"period": "quarterly"})

    assert response.status_code == 422
    assert "Unsupported period" in response.json()["detail"]


def test_detect_patterns_returns_503_when_detection_service_fails(monkeypatch):
    module = _import_patterns_router_module()

    async def _raise_failure(*_args, **_kwargs):
        raise RuntimeError("synthetic detector outage")

    monkeypatch.setattr(module.TechnicalPatternDetectionService, "detect_for_symbol", _raise_failure)

    app = FastAPI()
    app.include_router(module.router)
    client = TestClient(app)

    response = client.get("/patterns/600519.SH", params={"period": "daily"})

    assert response.status_code == 503
    assert response.json()["detail"] == "Pattern analysis unavailable"


def test_detect_patterns_returns_available_structured_payload_when_service_finds_detection(monkeypatch):
    module = _import_patterns_router_module()

    async def _fake_detect(*_args, **_kwargs):
        return [
            PatternDetection(
                pattern_name="double_top",
                direction="bearish",
                confidence=0.81,
                anchor_points=[
                    PatternAnchorPoint(role="left_peak", timestamp=1767225600000, value=11.5),
                    PatternAnchorPoint(role="neckline", timestamp=1767312000000, value=10.0),
                    PatternAnchorPoint(role="right_peak", timestamp=1767398400000, value=11.4),
                ],
            )
        ]

    monkeypatch.setattr(module, "_detect_patterns_for_symbol", _fake_detect)

    app = FastAPI()
    app.include_router(module.router)
    client = TestClient(app)

    response = client.get("/patterns/600519.SH", params={"period": "daily"})

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["status"] == "available"
    assert payload["symbol"] == "600519.SH"
    assert payload["period"] == "daily"
    assert payload["patterns"][0]["pattern_name"] == "double_top"
    assert payload["patterns"][0]["direction"] == "bearish"
    assert payload["patterns"][0]["anchor_points"][0]["role"] == "left_peak"
