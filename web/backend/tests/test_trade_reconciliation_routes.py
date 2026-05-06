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
    sys.modules.pop("app.api.trade.reconciliation_routes", None)
    sys.modules.pop("app.api.trade", None)
    return importlib.import_module("app.api.trade")


def _build_client(package):
    app = FastAPI()
    app.include_router(package.router, prefix="/api/v1/trade")
    return TestClient(app)


def test_trade_package_router_exposes_reconciliation_accounts(monkeypatch):
    package = _load_trade_package()
    routes_module = importlib.import_module("app.api.trade.reconciliation_routes")

    monkeypatch.setattr(
        routes_module,
        "list_reconciliation_accounts",
        lambda: [{"account_id": "backtest:7", "label": "Backtest #7", "account_type": "backtest"}],
    )

    client = _build_client(package)
    response = client.get("/api/v1/trade/reconciliation/accounts")

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "code": 200,
        "message": "Reconciliation accounts loaded",
        "data": {
            "status": "available",
            "endpoint": "trade",
            "resource": "reconciliation_accounts",
            "items": [{"account_id": "backtest:7", "label": "Backtest #7", "account_type": "backtest"}],
            "total_count": 1,
        },
        "timestamp": response.json()["timestamp"],
        "request_id": None,
        "errors": None,
    }


def test_reconciliation_statements_reject_invalid_start_date():
    package = _load_trade_package()
    client = _build_client(package)

    response = client.get(
        "/api/v1/trade/reconciliation/statements",
        params={"account_id": "backtest:7", "start_date": "2026/05/01"},
    )

    assert response.status_code == 400
    detail = response.json()["detail"]
    assert detail["success"] is False
    assert detail["message"] == "start_date 格式错误，应为 YYYY-MM-DD"


def test_reconciliation_statements_reject_invalid_end_date():
    package = _load_trade_package()
    client = _build_client(package)

    response = client.get(
        "/api/v1/trade/reconciliation/statements",
        params={"account_id": "backtest:7", "end_date": "2026/05/31"},
    )

    assert response.status_code == 400
    assert response.json()["detail"]["message"] == "end_date 格式错误，应为 YYYY-MM-DD"


def test_reconciliation_statements_reject_start_date_after_end_date():
    package = _load_trade_package()
    client = _build_client(package)

    response = client.get(
        "/api/v1/trade/reconciliation/statements",
        params={
            "account_id": "backtest:7",
            "start_date": "2026-05-31",
            "end_date": "2026-05-01",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"]["message"] == "start_date 不能晚于 end_date"


def test_reconciliation_statements_reject_invalid_account_id(monkeypatch):
    package = _load_trade_package()
    routes_module = importlib.import_module("app.api.trade.reconciliation_routes")

    def _fake_query_internal_statements(**_kwargs):
        raise ValueError("unsupported reconciliation account_id: broker:7")

    monkeypatch.setattr(routes_module, "query_internal_statements", _fake_query_internal_statements)

    client = _build_client(package)
    response = client.get("/api/v1/trade/reconciliation/statements", params={"account_id": "broker:7"})

    assert response.status_code == 400
    assert response.json()["detail"]["message"] == "unsupported reconciliation account_id: broker:7"


def test_reconciliation_statements_forwards_query_to_internal_statement_source(monkeypatch):
    package = _load_trade_package()
    routes_module = importlib.import_module("app.api.trade.reconciliation_routes")
    captured = {}

    def _fake_query_internal_statements(**kwargs):
        captured.update(kwargs)
        return {
            "account_id": kwargs["account_id"],
            "items": [],
            "summary": {
                "total_count": 0,
                "total_amount": "0.00",
                "total_commission": "0.00",
            },
            "total_count": 0,
            "page": kwargs["page"],
            "page_size": kwargs["page_size"],
            "source": "backtest_trades",
        }

    monkeypatch.setattr(routes_module, "query_internal_statements", _fake_query_internal_statements)

    client = _build_client(package)
    response = client.get(
        "/api/v1/trade/reconciliation/statements",
        params={
            "account_id": "backtest:7",
            "start_date": "2026-05-01",
            "end_date": "2026-05-31",
            "page": 2,
            "page_size": 50,
        },
    )

    assert response.status_code == 200
    assert captured == {
        "account_id": "backtest:7",
        "start_date": routes_module.datetime.strptime("2026-05-01", "%Y-%m-%d").date(),
        "end_date": routes_module.datetime.strptime("2026-05-31", "%Y-%m-%d").date(),
        "page": 2,
        "page_size": 50,
    }
    assert response.json()["data"] == {
        "status": "available",
        "endpoint": "trade",
        "resource": "reconciliation_statements",
        "account_id": "backtest:7",
        "items": [],
        "summary": {
            "total_count": 0,
            "total_amount": "0.00",
            "total_commission": "0.00",
        },
        "total_count": 0,
        "page": 2,
        "page_size": 50,
        "source": "backtest_trades",
    }
