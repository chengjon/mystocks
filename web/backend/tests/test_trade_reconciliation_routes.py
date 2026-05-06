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


def test_reconciliation_import_rejects_unsupported_source_type():
    package = _load_trade_package()
    client = _build_client(package)

    response = client.post(
        "/api/v1/trade/reconciliation/import",
        data={"source_type": "unknown"},
        files={"file": ("reconciliation.csv", b"header\nvalue\n", "text/csv")},
    )

    assert response.status_code == 422
    assert response.json()["detail"]["message"] == "unsupported source_type"


def test_reconciliation_import_requires_account_id_for_miniqmt():
    package = _load_trade_package()
    client = _build_client(package)

    response = client.post(
        "/api/v1/trade/reconciliation/import",
        data={"source_type": "miniqmt"},
        files={
            "file": (
                "reconciliation.csv",
                (
                    "证券代码,买卖方向,成交价格,成交数量,成交金额,手续费,委托编号,成交编号,成交时间\n"
                    "600519.SH,买入,1750.00,100,175000.00,52.50,backtest-7-101,101,2026-05-06 09:31:00\n"
                ).encode("utf-8-sig"),
                "text/csv",
            )
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"]["message"] == "account_id is required for miniqmt imports"


def test_reconciliation_import_requires_file_payload():
    package = _load_trade_package()
    client = _build_client(package)

    response = client.post(
        "/api/v1/trade/reconciliation/import",
        data={"source_type": "normalized_template"},
    )

    assert response.status_code == 422
    assert isinstance(response.json()["detail"], list)


def test_reconciliation_import_rejects_unknown_miniqmt_direction():
    package = _load_trade_package()
    client = _build_client(package)

    response = client.post(
        "/api/v1/trade/reconciliation/import",
        data={"source_type": "miniqmt", "account_id": "backtest:7"},
        files={
            "file": (
                "reconciliation.csv",
                (
                    "证券代码,买卖方向,成交价格,成交数量,成交金额,手续费,委托编号,成交编号,成交时间\n"
                    "600519.SH,撤单,1750.00,100,175000.00,52.50,backtest-7-101,101,2026-05-06 09:31:00\n"
                ).encode("utf-8-sig"),
                "text/csv",
            )
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"]["message"] == "unsupported miniQMT direction: 撤单"


def test_reconciliation_import_returns_batch_payload(monkeypatch):
    package = _load_trade_package()
    routes_module = importlib.import_module("app.api.trade.reconciliation_routes")

    monkeypatch.setattr(
        routes_module,
        "parse_normalized_template_csv",
        lambda csv_bytes: [
            {
                "account_id": "backtest:7",
                "trade_time": "2026-05-06 09:31:00",
                "symbol": "600519.SH",
                "direction": "buy",
                "price": "1750.00",
                "quantity": "100",
                "amount": "175000.00",
                "commission": "52.50",
                "order_id": "backtest-7-101",
                "trade_id": "101",
                "source_type": "normalized_template",
                "raw_row_number": 2,
            }
        ],
        raising=False,
    )
    monkeypatch.setattr(
        routes_module,
        "create_import_batch",
        lambda **kwargs: {
            "import_batch_id": "batch-001",
            "account_id": kwargs["rows"][0]["account_id"],
            "source_type": kwargs["source_type"],
            "row_count": len(kwargs["rows"]),
        },
        raising=False,
    )

    client = _build_client(package)
    response = client.post(
        "/api/v1/trade/reconciliation/import",
        data={"source_type": "normalized_template"},
        files={
            "file": (
                "reconciliation.csv",
                (
                    "account_id,trade_date,trade_time,symbol,direction,price,quantity,amount,commission,order_id,trade_id\n"
                    "backtest:7,2026-05-06,09:31:00,600519.SH,buy,1750.00,100,175000.00,52.50,backtest-7-101,101\n"
                ).encode("utf-8"),
                "text/csv",
            )
        },
    )

    assert response.status_code == 200
    assert response.json()["data"] == {
        "status": "available",
        "endpoint": "trade",
        "resource": "reconciliation_import_batch",
        "import_batch_id": "batch-001",
        "account_id": "backtest:7",
        "source_type": "normalized_template",
        "row_count": 1,
    }


def test_reconciliation_import_normalized_template_does_not_override_row_account_id(monkeypatch):
    package = _load_trade_package()
    routes_module = importlib.import_module("app.api.trade.reconciliation_routes")
    captured = {}

    monkeypatch.setattr(
        routes_module,
        "parse_normalized_template_csv",
        lambda csv_bytes: [
            {
                "account_id": "backtest:7",
                "trade_time": "2026-05-06 09:31:00",
                "symbol": "600519.SH",
                "direction": "buy",
                "price": "1750.00",
                "quantity": "100",
                "amount": "175000.00",
                "commission": "52.50",
                "order_id": "backtest-7-101",
                "trade_id": "101",
                "source_type": "normalized_template",
                "raw_row_number": 2,
            }
        ],
        raising=False,
    )
    monkeypatch.setattr(
        routes_module,
        "create_import_batch",
        lambda **kwargs: (
            captured.update(kwargs)
            or {
                "import_batch_id": "batch-002",
                "account_id": "backtest:7",
                "source_type": kwargs["source_type"],
                "row_count": len(kwargs["rows"]),
            }
        ),
        raising=False,
    )

    client = _build_client(package)
    response = client.post(
        "/api/v1/trade/reconciliation/import",
        data={"source_type": "normalized_template", "account_id": "backtest:999"},
        files={
            "file": (
                "reconciliation.csv",
                (
                    "account_id,trade_date,trade_time,symbol,direction,price,quantity,amount,commission,order_id,trade_id\n"
                    "backtest:7,2026-05-06,09:31:00,600519.SH,buy,1750.00,100,175000.00,52.50,backtest-7-101,101\n"
                ).encode("utf-8"),
                "text/csv",
            )
        },
    )

    assert response.status_code == 200
    assert captured["account_id"] is None


def test_reconciliation_results_paginate_and_filter_by_match_status(monkeypatch):
    package = _load_trade_package()
    routes_module = importlib.import_module("app.api.trade.reconciliation_routes")
    captured = {}

    def _fake_query_internal_statements(**kwargs):
        captured["statement_query"] = kwargs
        return {
            "account_id": kwargs["account_id"],
            "items": [
                {
                    "account_id": kwargs["account_id"],
                    "trade_id": "103",
                    "order_id": "backtest-7-103",
                    "symbol": "000001.SZ",
                    "direction": "sell",
                    "trade_time": "2026-05-06T09:33:00",
                    "price": "12.00",
                    "quantity": 100,
                    "amount": "1200.00",
                    "commission": "1.20",
                }
            ],
            "summary": {
                "total_count": 1,
                "total_amount": "1200.00",
                "total_commission": "1.20",
            },
            "total_count": 1,
            "page": kwargs["page"],
            "page_size": kwargs["page_size"],
            "source": "backtest_trades",
        }

    monkeypatch.setattr(routes_module, "query_internal_statements", _fake_query_internal_statements)
    monkeypatch.setattr(
        routes_module,
        "get_import_batch",
        lambda import_batch_id: {
            "import_batch_id": import_batch_id,
            "account_id": "backtest:7",
            "rows": [{"order_id": "backtest-7-103"}],
        },
        raising=False,
    )
    monkeypatch.setattr(
        routes_module,
        "match_reconciliation_rows",
        lambda internal_rows, broker_rows: [
            {
                "match_status": "matched",
                "internal_row": {
                    **internal_rows[0],
                    "trade_id": "101",
                    "order_id": "backtest-7-101",
                },
                "broker_row": {
                    "account_id": "backtest:7",
                    "trade_id": "201",
                    "order_id": "backtest-7-101",
                    "symbol": "600519.SH",
                    "direction": "buy",
                    "trade_time": "2026-05-06 09:31:00",
                    "price": "1750.00",
                    "quantity": "100",
                    "amount": "175000.00",
                    "commission": "52.50",
                    "source_type": "normalized_template",
                    "raw_row_number": 2,
                },
                "mismatch_fields": [],
            },
            {
                "match_status": "mismatched",
                "internal_row": {
                    **internal_rows[0],
                    "trade_id": "102",
                    "order_id": "backtest-7-102",
                },
                "broker_row": {
                    "account_id": "backtest:7",
                    "trade_id": "202",
                    "order_id": "backtest-7-102",
                    "symbol": "600519.SH",
                    "direction": "buy",
                    "trade_time": "2026-05-06 09:32:00",
                    "price": "1750.00",
                    "quantity": "100",
                    "amount": "175100.00",
                    "commission": "52.50",
                    "source_type": "normalized_template",
                    "raw_row_number": 3,
                },
                "mismatch_fields": ["amount"],
            },
            {
                "match_status": "matched",
                "internal_row": internal_rows[0],
                "broker_row": {
                    "account_id": "backtest:7",
                    "trade_id": "203",
                    "order_id": "backtest-7-103",
                    "symbol": "000001.SZ",
                    "direction": "sell",
                    "trade_time": "2026-05-06 09:33:00",
                    "price": "12.00",
                    "quantity": "100",
                    "amount": "1200.00",
                    "commission": "1.20",
                    "source_type": "normalized_template",
                    "raw_row_number": 4,
                },
                "mismatch_fields": [],
            },
        ],
        raising=False,
    )

    client = _build_client(package)
    response = client.get(
        "/api/v1/trade/reconciliation/results",
        params={
            "account_id": "backtest:7",
            "import_batch_id": "batch-001",
            "match_status": "matched",
            "page": 2,
            "page_size": 1,
        },
    )

    assert response.status_code == 200
    assert captured["statement_query"] == {
        "account_id": "backtest:7",
        "start_date": None,
        "end_date": None,
        "page": 1,
        "page_size": 10000,
    }
    assert response.json()["data"] == {
        "status": "available",
        "endpoint": "trade",
        "resource": "reconciliation_results",
        "account_id": "backtest:7",
        "import_batch_id": "batch-001",
        "items": [
            {
                "match_status": "matched",
                "internal_row": {
                    "account_id": "backtest:7",
                    "trade_id": "103",
                    "order_id": "backtest-7-103",
                    "symbol": "000001.SZ",
                    "direction": "sell",
                    "trade_time": "2026-05-06T09:33:00",
                    "price": "12.00",
                    "quantity": 100,
                    "amount": "1200.00",
                    "commission": "1.20",
                },
                "broker_row": {
                    "account_id": "backtest:7",
                    "trade_id": "203",
                    "order_id": "backtest-7-103",
                    "symbol": "000001.SZ",
                    "direction": "sell",
                    "trade_time": "2026-05-06 09:33:00",
                    "price": "12.00",
                    "quantity": 100,
                    "amount": "1200.00",
                    "commission": "1.20",
                    "source_type": "normalized_template",
                    "raw_row_number": 4,
                },
                "mismatch_fields": [],
            }
        ],
        "total_count": 2,
        "page": 2,
        "page_size": 1,
        "source": "backtest_trades",
        "match_status": "matched",
    }


def test_reconciliation_export_returns_csv_attachment(monkeypatch):
    package = _load_trade_package()
    routes_module = importlib.import_module("app.api.trade.reconciliation_routes")

    monkeypatch.setattr(
        routes_module,
        "query_internal_statements",
        lambda **kwargs: {
            "account_id": kwargs["account_id"],
            "items": [
                {
                    "account_id": kwargs["account_id"],
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
            "summary": {
                "total_count": 1,
                "total_amount": "175000.00",
                "total_commission": "52.50",
            },
            "total_count": 1,
            "page": kwargs["page"],
            "page_size": kwargs["page_size"],
            "source": "backtest_trades",
        },
        raising=False,
    )
    monkeypatch.setattr(
        routes_module,
        "get_import_batch",
        lambda import_batch_id: {
            "import_batch_id": import_batch_id,
            "account_id": "backtest:7",
            "rows": [{"order_id": "backtest-7-101"}],
        },
        raising=False,
    )
    monkeypatch.setattr(
        routes_module,
        "match_reconciliation_rows",
        lambda internal_rows, broker_rows: [
            {
                "match_status": "matched",
                "internal_row": internal_rows[0],
                "broker_row": {
                    "account_id": "backtest:7",
                    "trade_id": "201",
                    "order_id": "backtest-7-101",
                    "symbol": "600519.SH",
                    "direction": "buy",
                    "trade_time": "2026-05-06 09:31:00",
                    "price": "1750.00",
                    "quantity": "100",
                    "amount": "175000.00",
                    "commission": "52.50",
                    "source_type": "normalized_template",
                    "raw_row_number": 2,
                },
                "mismatch_fields": [],
            }
        ],
        raising=False,
    )

    client = _build_client(package)
    response = client.get(
        "/api/v1/trade/reconciliation/export",
        params={"account_id": "backtest:7", "import_batch_id": "batch-001"},
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    assert response.headers["content-disposition"] == (
        'attachment; filename="reconciliation-backtest_7-batch-001-page-all.csv"'
    )
    assert "match_status,internal_trade_id,internal_order_id" in response.text
    assert "matched,101,backtest-7-101" in response.text
