from __future__ import annotations

import importlib
import sys
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = ROOT / "web" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


def _load_module():
    sys.modules.pop("app.services.statement_reconciliation.matcher", None)
    return importlib.import_module("app.services.statement_reconciliation.matcher")


def _internal_row(**overrides):
    row = {
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
    row.update(overrides)
    return row


def _broker_row(**overrides):
    row = {
        "account_id": "backtest:7",
        "trade_id": "101",
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
    }
    row.update(overrides)
    return row


def test_match_reconciliation_rows_marks_exact_order_id_match_as_matched():
    module = _load_module()
    internal_rows = [_internal_row()]
    broker_rows = [_broker_row()]
    internal_before = deepcopy(internal_rows)
    broker_before = deepcopy(broker_rows)

    results = module.match_reconciliation_rows(internal_rows, broker_rows)

    assert results == [
        {
            "match_status": "matched",
            "internal_row": internal_before[0],
            "broker_row": broker_before[0],
            "mismatch_fields": [],
        }
    ]
    assert internal_rows == internal_before
    assert broker_rows == broker_before


def test_match_reconciliation_rows_marks_order_id_amount_or_commission_differences_as_mismatched():
    module = _load_module()

    results = module.match_reconciliation_rows(
        [_internal_row(amount="175000.00", commission="52.50")],
        [_broker_row(amount="175100.00", commission="53.00")],
    )

    assert results == [
        {
            "match_status": "mismatched",
            "internal_row": _internal_row(amount="175000.00", commission="52.50"),
            "broker_row": _broker_row(amount="175100.00", commission="53.00"),
            "mismatch_fields": ["amount", "commission"],
        }
    ]


def test_match_reconciliation_rows_marks_missing_broker_record_when_no_pair_exists():
    module = _load_module()

    results = module.match_reconciliation_rows([_internal_row()], [])

    assert results == [
        {
            "match_status": "missing_broker_record",
            "internal_row": _internal_row(),
            "broker_row": None,
            "mismatch_fields": [],
        }
    ]


def test_match_reconciliation_rows_falls_back_to_normalized_timestamp_key():
    module = _load_module()

    results = module.match_reconciliation_rows(
        [_internal_row(order_id="internal-101")],
        [_broker_row(order_id="broker-201", trade_time="2026-05-06T09:31:00.123456Z")],
    )

    assert results[0]["match_status"] == "matched"
    assert results[0]["broker_row"]["trade_time"] == "2026-05-06T09:31:00.123456Z"


def test_match_reconciliation_rows_does_not_reuse_one_broker_row_for_multiple_internal_rows():
    module = _load_module()
    internal_rows = [
        _internal_row(trade_id="101", order_id="internal-101"),
        _internal_row(trade_id="102", order_id="internal-102"),
    ]
    broker_rows = [_broker_row(order_id="broker-201")]

    results = module.match_reconciliation_rows(internal_rows, broker_rows)

    assert [item["match_status"] for item in results] == ["matched", "missing_broker_record"]
    assert results[0]["broker_row"] == broker_rows[0]
    assert results[1]["broker_row"] is None


def test_match_reconciliation_rows_prefers_trade_id_within_same_fallback_key():
    module = _load_module()
    internal_rows = [
        _internal_row(trade_id="101", order_id="internal-101"),
        _internal_row(trade_id="102", order_id="internal-102"),
    ]
    broker_rows = [
        _broker_row(trade_id="102", order_id="broker-202"),
        _broker_row(trade_id="101", order_id="broker-201"),
    ]

    results = module.match_reconciliation_rows(internal_rows, broker_rows)

    assert [item["broker_row"]["trade_id"] for item in results] == ["101", "102"]
