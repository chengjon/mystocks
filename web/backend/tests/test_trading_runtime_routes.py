from fastapi.testclient import TestClient
import pytest

from app.api import trading_runtime
from app.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_runtime_state():
    trading_runtime._RUNTIME_STATE.update(
        {
            "is_running": False,
            "session_id": None,
            "active_positions": 0,
            "total_pnl": 0.0,
            "daily_pnl": 0.0,
            "current_drawdown": 0.0,
            "market_data": {
                "000001.SH": {
                    "price": 12.50,
                    "change": 0.08,
                    "change_percent": 0.64,
                }
            },
        }
    )
    trading_runtime._RUNTIME_STATE["strategies"] = [
        {
            "id": "demo-momentum",
            "name": "Demo Momentum",
            "type": "momentum",
            "pnl": 0.0,
            "win_rate": 0.0,
        }
    ]


@pytest.mark.parametrize(
    "path",
    [
        "/api/trading/status",
        "/api/trading/strategies/performance",
        "/api/trading/market/snapshot",
        "/api/trading/risk/metrics",
        "/api/v1/trade/positions",
        "/api/v1/trade/signals?limit=20",
    ],
)
def test_trading_runtime_routes_are_available(path: str, client: TestClient):
    response = client.get(path)
    assert response.status_code == 200, f"{path} should return 200, got {response.status_code}"


def test_runtime_write_requires_auth_when_not_testing(client: TestClient, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(trading_runtime.settings, "testing", False)
    monkeypatch.setattr(trading_runtime.settings, "csrf_enabled", False)

    response = client.post("/api/trading/start")

    assert response.status_code == 401


def test_runtime_write_allowed_in_testing_mode(client: TestClient, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(trading_runtime.settings, "testing", True)

    response = client.post("/api/trading/start")

    assert response.status_code == 200
    assert response.json()["success"] is True


def test_runtime_start_status_stop_flow_in_testing_mode(client: TestClient, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(trading_runtime.settings, "testing", True)

    start_resp = client.post("/api/trading/start")
    assert start_resp.status_code == 200
    start_data = start_resp.json()["data"]
    assert start_data["is_running"] is True
    assert start_data["session_id"] is not None

    status_resp = client.get("/api/trading/status")
    assert status_resp.status_code == 200
    status_data = status_resp.json()["data"]
    assert status_data["is_running"] is True
    assert status_data["session_id"] == start_data["session_id"]

    stop_resp = client.post("/api/trading/stop")
    assert stop_resp.status_code == 200
    stop_data = stop_resp.json()["data"]
    assert stop_data["is_running"] is False

    final_status_resp = client.get("/api/trading/status")
    assert final_status_resp.status_code == 200
    final_status_data = final_status_resp.json()["data"]
    assert final_status_data["is_running"] is False
    assert final_status_data["session_id"] is None
