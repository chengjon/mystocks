from __future__ import annotations

import importlib
import sys
from datetime import date
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = ROOT / "web" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


def _load_module():
    sys.modules.pop("app.services.statement_reconciliation.internal_statement_source", None)
    return importlib.import_module("app.services.statement_reconciliation.internal_statement_source")


def test_build_statement_account_id_projects_backtest_identity():
    module = _load_module()

    assert module.build_statement_account_id(7) == "backtest:7"


def test_parse_statement_account_id_rejects_unsupported_prefix():
    module = _load_module()

    try:
        module.parse_statement_account_id("broker:7")
    except ValueError as exc:
        assert "unsupported reconciliation account_id" in str(exc)
    else:
        raise AssertionError("parse_statement_account_id should reject unsupported prefixes")


def test_list_reconciliation_accounts_returns_descending_backtest_accounts(monkeypatch):
    module = _load_module()

    class _FakeQuery:
        def distinct(self):
            return self

        def order_by(self, *_args, **_kwargs):
            return self

        def all(self):
            return [(9,), (7,)]

    class _FakeSession:
        def query(self, model):
            assert model is module.BacktestTradeModel.backtest_id
            return _FakeQuery()

        def close(self):
            return None

    monkeypatch.setattr(module, "SessionLocal", lambda: _FakeSession())

    accounts = module.list_reconciliation_accounts()

    assert accounts == [
        {
            "account_id": "backtest:9",
            "label": "Backtest #9",
            "account_type": "backtest",
        },
        {
            "account_id": "backtest:7",
            "label": "Backtest #7",
            "account_type": "backtest",
        },
    ]


def test_query_internal_statements_maps_filtered_backtest_rows(monkeypatch):
    module = _load_module()

    class _TradeRow:
        def __init__(
            self,
            row_id: int,
            trade_date_value: date,
            quantity: int,
            total_cost: str,
            commission: str,
            created_at_value: datetime | None,
        ):
            self.id = row_id
            self.backtest_id = 7
            self.trade_date = trade_date_value
            self.symbol = "600519.SH"
            self.direction = "buy"
            self.amount = quantity
            self.price = Decimal("1750.00")
            self.commission = Decimal(commission)
            self.total_cost = Decimal(total_cost)
            self.created_at = created_at_value

    rows = [
        _TradeRow(101, date(2026, 5, 6), 100, "175000.00", "52.50", datetime(2026, 5, 6, 9, 30, 0)),
        _TradeRow(102, date(2026, 5, 7), 100, "180000.00", "52.50", datetime(2026, 5, 7, 9, 31, 0)),
    ]

    class _FakeQuery:
        def __init__(self, data):
            self._data = data

        def filter(self, *_args, **_kwargs):
            return self

        def order_by(self, *_args, **_kwargs):
            return self

        def all(self):
            return list(self._data)

    class _FakeSession:
        def query(self, model):
            assert model is module.BacktestTradeModel
            return _FakeQuery(rows)

        def close(self):
            return None

    monkeypatch.setattr(module, "SessionLocal", lambda: _FakeSession())

    payload = module.query_internal_statements(
        account_id="backtest:7",
        start_date=date(2026, 5, 1),
        end_date=date(2026, 5, 31),
        page=1,
        page_size=1,
    )

    assert payload["account_id"] == "backtest:7"
    assert payload["total_count"] == 2
    assert payload["page"] == 1
    assert payload["page_size"] == 1
    assert payload["source"] == "backtest_trades"
    assert payload["summary"] == {
        "total_count": 2,
        "total_amount": "355000.00",
        "total_commission": "105.00",
    }
    assert payload["items"] == [
        {
            "account_id": "backtest:7",
            "trade_id": "102",
            "order_id": "backtest-7-102",
            "symbol": "600519.SH",
            "direction": "buy",
            "trade_time": "2026-05-07T09:31:00",
            "price": "1750.00",
            "quantity": 100,
            "amount": "180000.00",
            "commission": "52.50",
        }
    ]


def test_query_internal_statements_stably_orders_same_day_rows_by_created_at(monkeypatch):
    module = _load_module()

    class _TradeRow:
        def __init__(self, row_id: int, created_at_value: datetime):
            self.id = row_id
            self.backtest_id = 7
            self.trade_date = date(2026, 5, 7)
            self.symbol = "600519.SH"
            self.direction = "buy"
            self.amount = 100
            self.price = Decimal("1750.00")
            self.commission = Decimal("52.50")
            self.total_cost = Decimal("175000.00")
            self.created_at = created_at_value

    rows = [
        _TradeRow(101, datetime(2026, 5, 7, 9, 30, 0)),
        _TradeRow(102, datetime(2026, 5, 7, 9, 31, 0)),
    ]

    class _FakeQuery:
        def __init__(self, data):
            self._data = data

        def filter(self, *_args, **_kwargs):
            return self

        def order_by(self, *_args, **_kwargs):
            return self

        def all(self):
            return list(self._data)

    class _FakeSession:
        def query(self, model):
            assert model is module.BacktestTradeModel
            return _FakeQuery(rows)

        def close(self):
            return None

    monkeypatch.setattr(module, "SessionLocal", lambda: _FakeSession())

    payload = module.query_internal_statements(
        account_id="backtest:7",
        start_date=None,
        end_date=None,
        page=1,
        page_size=2,
    )

    assert [item["trade_id"] for item in payload["items"]] == ["102", "101"]


def test_query_internal_statements_falls_back_to_trade_date_when_created_at_missing(monkeypatch):
    module = _load_module()

    class _TradeRow:
        def __init__(self):
            self.id = 101
            self.backtest_id = 7
            self.trade_date = date(2026, 5, 9)
            self.symbol = "600519.SH"
            self.direction = "buy"
            self.amount = 100
            self.price = Decimal("1750.00")
            self.commission = Decimal("52.50")
            self.total_cost = Decimal("175000.00")
            self.created_at = None

    class _FakeQuery:
        def filter(self, *_args, **_kwargs):
            return self

        def order_by(self, *_args, **_kwargs):
            return self

        def all(self):
            return [_TradeRow()]

    class _FakeSession:
        def query(self, model):
            assert model is module.BacktestTradeModel
            return _FakeQuery()

        def close(self):
            return None

    monkeypatch.setattr(module, "SessionLocal", lambda: _FakeSession())

    payload = module.query_internal_statements(
        account_id="backtest:7",
        start_date=None,
        end_date=None,
        page=1,
        page_size=20,
    )

    assert payload["items"][0]["trade_time"] == "2026-05-09T00:00:00"


def test_query_internal_statements_normalizes_timezone_aware_created_at_before_sorting(monkeypatch):
    module = _load_module()

    class _TradeRow:
        def __init__(self, row_id: int, trade_date_value: date, created_at_value):
            self.id = row_id
            self.backtest_id = 7
            self.trade_date = trade_date_value
            self.symbol = "600519.SH"
            self.direction = "buy"
            self.amount = 100
            self.price = Decimal("1750.00")
            self.commission = Decimal("52.50")
            self.total_cost = Decimal("175000.00")
            self.created_at = created_at_value

    rows = [
        _TradeRow(101, date(2026, 5, 7), datetime(2026, 5, 7, 9, 31, tzinfo=timezone.utc)),
        _TradeRow(102, date(2026, 5, 8), None),
    ]

    class _FakeQuery:
        def __init__(self, data):
            self._data = data

        def filter(self, *_args, **_kwargs):
            return self

        def order_by(self, *_args, **_kwargs):
            return self

        def all(self):
            return list(self._data)

    class _FakeSession:
        def query(self, model):
            assert model is module.BacktestTradeModel
            return _FakeQuery(rows)

        def close(self):
            return None

    monkeypatch.setattr(module, "SessionLocal", lambda: _FakeSession())

    payload = module.query_internal_statements(
        account_id="backtest:7",
        start_date=None,
        end_date=None,
        page=1,
        page_size=2,
    )

    assert [item["trade_id"] for item in payload["items"]] == ["102", "101"]
