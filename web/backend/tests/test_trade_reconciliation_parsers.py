from __future__ import annotations

import importlib
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = ROOT / "web" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


def _load_normalized_template_module():
    sys.modules.pop("app.services.statement_reconciliation.parsers.normalized_template", None)
    return importlib.import_module("app.services.statement_reconciliation.parsers.normalized_template")


def _load_miniqmt_module():
    sys.modules.pop("app.services.statement_reconciliation.parsers.miniqmt", None)
    return importlib.import_module("app.services.statement_reconciliation.parsers.miniqmt")


def test_parse_normalized_template_csv_returns_canonical_rows():
    module = _load_normalized_template_module()
    csv_bytes = (
        "account_id,trade_date,trade_time,symbol,direction,price,quantity,amount,commission,order_id,trade_id\n"
        "backtest:7,2026-05-06,09:31:00,600519.SH,buy,1750.00,100,175000.00,52.50,backtest-7-101,101\n"
    ).encode("utf-8")

    rows = module.parse_normalized_template_csv(csv_bytes)

    assert rows == [
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
    ]


def test_parse_normalized_template_csv_rejects_missing_required_columns():
    module = _load_normalized_template_module()
    csv_bytes = (
        "account_id,trade_date,trade_time,symbol,direction,price,quantity,amount,commission,order_id\n"
        "backtest:7,2026-05-06,09:31:00,600519.SH,buy,1750.00,100,175000.00,52.50,backtest-7-101\n"
    ).encode("utf-8")

    try:
        module.parse_normalized_template_csv(csv_bytes)
    except ValueError as exc:
        assert "missing required columns: trade_id" == str(exc)
    else:
        raise AssertionError("parse_normalized_template_csv should reject missing required columns")


def test_parse_normalized_template_csv_rejects_header_only_csv():
    module = _load_normalized_template_module()
    csv_bytes = (
        "account_id,trade_date,trade_time,symbol,direction,price,quantity,amount,commission,order_id,trade_id\n"
    ).encode("utf-8")

    try:
        module.parse_normalized_template_csv(csv_bytes)
    except ValueError as exc:
        assert "csv contains no data rows" == str(exc)
    else:
        raise AssertionError("parse_normalized_template_csv should reject header-only CSV")


def test_parse_normalized_template_csv_rejects_row_with_missing_cell():
    module = _load_normalized_template_module()
    csv_bytes = (
        "account_id,trade_date,trade_time,symbol,direction,price,quantity,amount,commission,order_id,trade_id\n"
        "backtest:7,2026-05-06,09:31:00,600519.SH,buy,1750.00,100,175000.00,52.50,backtest-7-101\n"
    ).encode("utf-8")

    try:
        module.parse_normalized_template_csv(csv_bytes)
    except ValueError as exc:
        assert "row 2 missing required value: trade_id" == str(exc)
    else:
        raise AssertionError("parse_normalized_template_csv should reject rows with missing cells")


def test_parse_miniqmt_csv_maps_supported_headers():
    module = _load_miniqmt_module()
    csv_bytes = (
        "证券代码,买卖方向,成交价格,成交数量,成交金额,手续费,委托编号,成交编号,成交时间\n"
        "600519.SH,买入,1750.00,100,175000.00,52.50,backtest-7-101,101,2026-05-06 09:31:00\n"
    ).encode("utf-8-sig")

    rows = module.parse_miniqmt_csv(csv_bytes, account_id="backtest:7")

    assert rows == [
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
            "source_type": "miniqmt",
            "raw_row_number": 2,
        }
    ]


def test_parse_miniqmt_csv_rejects_missing_supported_headers():
    module = _load_miniqmt_module()
    csv_bytes = (
        "证券代码,买卖方向,成交价格,成交数量,成交金额,手续费,委托编号,成交时间\n"
        "600519.SH,买入,1750.00,100,175000.00,52.50,backtest-7-101,2026-05-06 09:31:00\n"
    ).encode("utf-8-sig")

    try:
        module.parse_miniqmt_csv(csv_bytes, account_id="backtest:7")
    except ValueError as exc:
        assert "missing supported miniQMT columns: 成交编号" == str(exc)
    else:
        raise AssertionError("parse_miniqmt_csv should reject missing supported headers")


def test_parse_miniqmt_csv_rejects_header_only_csv():
    module = _load_miniqmt_module()
    csv_bytes = (
        "证券代码,买卖方向,成交价格,成交数量,成交金额,手续费,委托编号,成交编号,成交时间\n"
    ).encode("utf-8-sig")

    try:
        module.parse_miniqmt_csv(csv_bytes, account_id="backtest:7")
    except ValueError as exc:
        assert "csv contains no data rows" == str(exc)
    else:
        raise AssertionError("parse_miniqmt_csv should reject header-only CSV")


def test_parse_miniqmt_csv_rejects_unknown_direction():
    module = _load_miniqmt_module()
    csv_bytes = (
        "证券代码,买卖方向,成交价格,成交数量,成交金额,手续费,委托编号,成交编号,成交时间\n"
        "600519.SH,撤单,1750.00,100,175000.00,52.50,backtest-7-101,101,2026-05-06 09:31:00\n"
    ).encode("utf-8-sig")

    try:
        module.parse_miniqmt_csv(csv_bytes, account_id="backtest:7")
    except ValueError as exc:
        assert "unsupported miniQMT direction: 撤单" == str(exc)
    else:
        raise AssertionError("parse_miniqmt_csv should reject unsupported directions")
