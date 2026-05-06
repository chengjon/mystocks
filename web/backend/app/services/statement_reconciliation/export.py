from __future__ import annotations

import csv
import io
from typing import Any


CSV_COLUMNS = [
    "match_status",
    "internal_trade_id",
    "internal_order_id",
    "internal_account_id",
    "internal_symbol",
    "internal_direction",
    "internal_trade_time",
    "internal_price",
    "internal_quantity",
    "internal_amount",
    "internal_commission",
    "broker_trade_id",
    "broker_order_id",
    "broker_account_id",
    "broker_symbol",
    "broker_direction",
    "broker_trade_time",
    "broker_price",
    "broker_quantity",
    "broker_amount",
    "broker_commission",
    "broker_source_type",
    "broker_raw_row_number",
    "mismatch_fields",
]


def _stringify(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def build_reconciliation_export_csv(results: list[dict[str, Any]]) -> str:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=CSV_COLUMNS, lineterminator="\n")
    writer.writeheader()

    for result in results:
        internal_row = result["internal_row"]
        broker_row = result.get("broker_row") or {}
        writer.writerow(
            {
                "match_status": _stringify(result["match_status"]),
                "internal_trade_id": _stringify(internal_row.get("trade_id")),
                "internal_order_id": _stringify(internal_row.get("order_id")),
                "internal_account_id": _stringify(internal_row.get("account_id")),
                "internal_symbol": _stringify(internal_row.get("symbol")),
                "internal_direction": _stringify(internal_row.get("direction")),
                "internal_trade_time": _stringify(internal_row.get("trade_time")),
                "internal_price": _stringify(internal_row.get("price")),
                "internal_quantity": _stringify(internal_row.get("quantity")),
                "internal_amount": _stringify(internal_row.get("amount")),
                "internal_commission": _stringify(internal_row.get("commission")),
                "broker_trade_id": _stringify(broker_row.get("trade_id")),
                "broker_order_id": _stringify(broker_row.get("order_id")),
                "broker_account_id": _stringify(broker_row.get("account_id")),
                "broker_symbol": _stringify(broker_row.get("symbol")),
                "broker_direction": _stringify(broker_row.get("direction")),
                "broker_trade_time": _stringify(broker_row.get("trade_time")),
                "broker_price": _stringify(broker_row.get("price")),
                "broker_quantity": _stringify(broker_row.get("quantity")),
                "broker_amount": _stringify(broker_row.get("amount")),
                "broker_commission": _stringify(broker_row.get("commission")),
                "broker_source_type": _stringify(broker_row.get("source_type")),
                "broker_raw_row_number": _stringify(broker_row.get("raw_row_number")),
                "mismatch_fields": ";".join(result.get("mismatch_fields", [])),
            }
        )

    return buffer.getvalue()
