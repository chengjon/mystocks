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


def _load_trade_package():
    sys.modules.pop("app.api.trade.execution_tracking_routes", None)
    sys.modules.pop("app.api.trade", None)
    return importlib.import_module("app.api.trade")


def _build_client(package):
    app = FastAPI()
    app.include_router(package.router, prefix="/api/v1/trade")
    return TestClient(app)


def test_execution_tracking_list_aggregates_internal_rows_and_bridge_evidence(monkeypatch):
    package = _load_trade_package()
    routes_module = importlib.import_module("app.api.trade.execution_tracking_routes")

    monkeypatch.setattr(
        routes_module,
        "query_internal_statements",
        lambda **kwargs: {
            "account_id": kwargs["account_id"],
            "items": [
                {
                    "account_id": "backtest:7",
                    "trade_id": "101",
                    "order_id": "backtest-7-101",
                    "symbol": "600519.SH",
                    "direction": "buy",
                    "trade_time": "2026-05-06T09:31:00",
                    "price": "1750.00",
                    "quantity": 100,
                    "amount": "175000.00",
                    "commission": "52.50",
                }
            ],
            "summary": {"total_count": 1, "total_amount": "175000.00", "total_commission": "52.50"},
            "total_count": 1,
            "page": kwargs["page"],
            "page_size": kwargs["page_size"],
            "source": "backtest_trades",
        },
    )

    routes_module.record_execution_trigger(
        {
            "account_id": "backtest:7",
            "order_id": "backtest-7-101",
            "symbol": "600519.SH",
            "direction": "buy",
            "quantity": 100,
            "price": "1750.00",
            "bridge_task_id": "mini-task-101",
            "submission_status": "bridge_task_accepted",
        }
    )

    client = _build_client(package)
    response = client.get("/api/v1/trade/execution-tracking", params={"account_id": "backtest:7"})

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["resource"] == "execution_tracking"
    assert data["items"][0]["order_id"] == "backtest-7-101"
    assert data["items"][0]["bridge_evidence"]["bridge_task_id"] == "mini-task-101"
    assert data["items"][0]["broker_state"] == "review_required"
    assert data["items"][0]["reconciliation_status"] == "not_imported"
    assert data["summary"]["review_required_count"] == 1


def test_execution_tracking_trigger_returns_external_trigger_receipt_only():
    package = _load_trade_package()
    client = _build_client(package)

    response = client.post(
        "/api/v1/trade/execution-tracking/trigger",
        json={
            "account_id": "backtest:7",
            "symbol": "600519.SH",
            "direction": "buy",
            "quantity": 100,
            "price": "1750.00",
            "requested_by": "operator-a",
        },
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["resource"] == "execution_trigger"
    assert data["accepted"] is True
    assert data["submission_status"] == "bridge_task_accepted"
    assert data["bridge_receipt"]["bridge_task_id"].startswith("miniqmt-task-")
    assert data["broker_state"] == "review_required"
    assert "broker_acknowledged" not in response.text
    assert "filled" not in response.text


def test_execution_tracking_detail_keeps_bridge_terminal_result_review_required():
    package = _load_trade_package()
    routes_module = importlib.import_module("app.api.trade.execution_tracking_routes")

    trigger = routes_module.record_execution_trigger(
        {
            "account_id": "backtest:7",
            "order_id": "backtest-7-201",
            "symbol": "300750.SZ",
            "direction": "sell",
            "quantity": 200,
            "price": "212.50",
            "bridge_task_id": "mini-task-201",
            "submission_status": "bridge_task_accepted",
            "bridge_result_status": "success",
        }
    )

    client = _build_client(package)
    response = client.get(f"/api/v1/trade/execution-tracking/{trigger['tracking_id']}")

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["item"]["bridge_evidence"]["result_status"] == "success"
    assert data["item"]["broker_state"] == "review_required"
    assert data["item"]["broker_correlation"]["external_order_id"] is None
    assert [event["event_type"] for event in data["evidence_timeline"]] == [
        "external_trigger_request",
        "bridge_submission_receipt",
        "bridge_task_terminal_result",
    ]
