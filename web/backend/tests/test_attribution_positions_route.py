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
    sys.modules.pop("app.api.v1.trading.positions", None)
    return importlib.import_module("app.api.v1.trading.positions")


def _build_client(router) -> TestClient:
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    return TestClient(app)


def _seed_positions(module):
    module.runtime_store.reset()
    session = module.runtime_store.create_session(
        symbol="portfolio",
        strategy_id="strategy_attribution_test",
        initial_capital=1_000_000.0,
        position_size=0.8,
        risk_threshold=0.05,
    )
    first = module.runtime_store.create_position(symbol="600000.SH", quantity=1000, price=10.0)
    second = module.runtime_store.create_position(symbol="600519.SH", quantity=100, price=1200.0)
    first.current_price = 10.8
    first.market_value = 10_800.0
    first.unrealized_pnl = 800.0
    second.current_price = 1188.0
    second.market_value = 118_800.0
    second.unrealized_pnl = -1_200.0
    module.runtime_store._recalculate_session(session.session_id)
    return session


def test_position_attribution_route_returns_current_stale_snapshot():
    module = _load_module()
    _seed_positions(module)

    client = _build_client(module.router)
    response = client.get("/api/v1/positions/attribution")

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["message"] == "Position attribution retrieved"
    data = payload["data"]
    assert data["snapshot_meta"]["constituent_count"] == 2
    assert data["snapshot_meta"]["stale"] is True
    assert data["snapshot_meta"]["stale_reason"] == "runtime_position_prices"
    assert "brinson" in data
    assert "factor_attribution" in data
    assert data["top_contributors"][0]["contribution_value"] >= data["top_contributors"][1]["contribution_value"]


def test_position_attribution_route_returns_date_scoped_snapshot():
    module = _load_module()
    _seed_positions(module)

    client = _build_client(module.router)
    response = client.get("/api/v1/positions/attribution?date=2026-05-08")

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["analysis_date"] == "2026-05-08"
    assert data["snapshot_meta"]["analysis_date"] == "2026-05-08"
    assert data["snapshot_meta"]["stale"] is False
    assert data["snapshot_meta"]["stale_reason"] is None


def test_position_attribution_route_returns_not_found_for_empty_portfolio():
    module = _load_module()
    module.runtime_store.reset()

    client = _build_client(module.router)
    response = client.get("/api/v1/positions/attribution")

    assert response.status_code == 404
    payload = response.json()
    assert payload["detail"]["message"] == "No positions available for attribution"
