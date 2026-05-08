from __future__ import annotations

import importlib
import sys
from pathlib import Path
from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = ROOT / "web" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


def _load_module():
    sys.modules.pop("app.api.v1.analysis.backtest", None)
    return importlib.import_module("app.api.v1.analysis.backtest")


def _build_client(router) -> TestClient:
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    return TestClient(app)


def _sample_result(module):
    attribution_module = importlib.import_module("app.services.attribution.engine")
    return attribution_module.AttributionEngine().analyze(
        portfolio=[
            attribution_module.PortfolioConstituentSnapshot(
                analysis_date="2026-05-08",
                symbol="600000.SH",
                weight=0.6,
                market_value=600000.0,
                return_rate=0.10,
                industry="银行",
            ),
            attribution_module.PortfolioConstituentSnapshot(
                analysis_date="2026-05-08",
                symbol="600519.SH",
                weight=0.4,
                market_value=400000.0,
                return_rate=-0.02,
                industry="食品饮料",
            ),
        ],
        benchmark=[
            attribution_module.BenchmarkConstituentSnapshot(
                analysis_date="2026-05-08",
                symbol="600000.SH",
                weight=0.5,
                return_rate=0.08,
                industry="银行",
            ),
            attribution_module.BenchmarkConstituentSnapshot(
                analysis_date="2026-05-08",
                symbol="600519.SH",
                weight=0.5,
                return_rate=0.01,
                industry="食品饮料",
            ),
        ],
        factors=attribution_module.FactorExposureSnapshot(
            analysis_date="2026-05-08",
            portfolio={"size": 0.2, "value": 0.1, "momentum": 0.4, "volatility": -0.1, "quality": 0.3},
            benchmark={"size": 0.1, "value": 0.0, "momentum": 0.2, "volatility": 0.0, "quality": 0.1},
        ),
    )


def test_backtest_attribution_route_returns_unified_contract(monkeypatch):
    module = _load_module()
    monkeypatch.setattr(
        module,
        "_load_backtest_result",
        lambda backtest_id: SimpleNamespace(backtest_id=backtest_id),
    )
    monkeypatch.setattr(module, "_run_backtest_attribution", lambda _backtest: _sample_result(module))

    client = _build_client(module.router)
    response = client.get("/api/v1/backtest/42/attribution")

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["analysis_date"] == "2026-05-08"
    assert "brinson" in payload["data"]
    assert "factor_attribution" in payload["data"]


def test_backtest_attribution_route_returns_not_found(monkeypatch):
    module = _load_module()
    monkeypatch.setattr(module, "_load_backtest_result", lambda _backtest_id: None)

    client = _build_client(module.router)
    response = client.get("/api/v1/backtest/42/attribution")

    assert response.status_code == 404
    assert response.json()["detail"]["message"] == "Backtest not found"


def test_backtest_attribution_route_hard_fails_on_dependency_error(monkeypatch):
    module = _load_module()
    monkeypatch.setattr(
        module,
        "_load_backtest_result",
        lambda backtest_id: SimpleNamespace(backtest_id=backtest_id),
    )
    monkeypatch.setattr(
        module,
        "_run_backtest_attribution",
        lambda _backtest: (_ for _ in ()).throw(module.AttributionDependencyError("missing benchmark data")),
    )

    client = _build_client(module.router)
    response = client.get("/api/v1/backtest/42/attribution")

    assert response.status_code == 503
    assert response.json()["detail"]["message"] == "missing benchmark data"
