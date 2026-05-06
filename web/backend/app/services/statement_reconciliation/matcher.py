from __future__ import annotations

from collections import defaultdict, deque
from copy import deepcopy
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any


def _normalize_text(value: Any) -> str:
    return str(value).strip()


def _normalize_decimal(value: Any) -> Decimal:
    return Decimal(str(value).strip())


def _normalize_quantity(value: Any) -> int:
    return int(str(value).strip())


def _normalize_trade_time(value: Any) -> str:
    if isinstance(value, datetime):
        trade_time = value
    else:
        text = _normalize_text(value)
        if text.endswith("Z"):
            text = f"{text[:-1]}+00:00"
        trade_time = datetime.fromisoformat(text)

    if trade_time.tzinfo is not None:
        trade_time = trade_time.astimezone(UTC).replace(tzinfo=None)

    return trade_time.replace(microsecond=0).isoformat(timespec="seconds")


def _fallback_key(row: dict[str, Any]) -> tuple[str, str, str, int, Decimal]:
    return (
        _normalize_text(row["symbol"]).upper(),
        _normalize_text(row["direction"]).lower(),
        _normalize_trade_time(row["trade_time"]),
        _normalize_quantity(row["quantity"]),
        _normalize_decimal(row["price"]),
    )


def _mismatch_fields(
    internal_row: dict[str, Any],
    broker_row: dict[str, Any],
) -> list[str]:
    mismatches: list[str] = []
    if _normalize_text(internal_row["symbol"]).upper() != _normalize_text(broker_row["symbol"]).upper():
        mismatches.append("symbol")
    if _normalize_text(internal_row["direction"]).lower() != _normalize_text(broker_row["direction"]).lower():
        mismatches.append("direction")
    if _normalize_trade_time(internal_row["trade_time"]) != _normalize_trade_time(broker_row["trade_time"]):
        mismatches.append("trade_time")
    if _normalize_quantity(internal_row["quantity"]) != _normalize_quantity(broker_row["quantity"]):
        mismatches.append("quantity")
    if _normalize_decimal(internal_row["price"]) != _normalize_decimal(broker_row["price"]):
        mismatches.append("price")
    if _normalize_decimal(internal_row["amount"]) != _normalize_decimal(broker_row["amount"]):
        mismatches.append("amount")
    if _normalize_decimal(internal_row["commission"]) != _normalize_decimal(broker_row["commission"]):
        mismatches.append("commission")
    return mismatches


def _pop_first_unused(candidates: deque[int], used_indexes: set[int]) -> int | None:
    while candidates:
        broker_index = candidates.popleft()
        if broker_index not in used_indexes:
            return broker_index
    return None


def _pop_preferred_broker_index(
    *,
    internal_row: dict[str, Any],
    candidates: deque[int],
    broker_rows: list[dict[str, Any]],
    used_indexes: set[int],
) -> int | None:
    preferred_trade_id = _normalize_text(internal_row.get("trade_id", ""))
    if preferred_trade_id:
        for broker_index in list(candidates):
            if broker_index in used_indexes:
                continue
            if _normalize_text(broker_rows[broker_index].get("trade_id", "")) == preferred_trade_id:
                candidates.remove(broker_index)
                return broker_index

    return _pop_first_unused(candidates, used_indexes)


def match_reconciliation_rows(
    internal_rows: list[dict[str, Any]],
    broker_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    order_id_index: dict[str, deque[int]] = defaultdict(deque)
    fallback_index: dict[tuple[str, str, str, int, Decimal], deque[int]] = defaultdict(deque)

    for broker_index, broker_row in enumerate(broker_rows):
        order_id = _normalize_text(broker_row.get("order_id", ""))
        if order_id:
            order_id_index[order_id].append(broker_index)
        fallback_index[_fallback_key(broker_row)].append(broker_index)

    used_broker_indexes: set[int] = set()
    results: list[dict[str, Any]] = []

    for internal_row in internal_rows:
        broker_index = None
        order_id = _normalize_text(internal_row.get("order_id", ""))
        if order_id:
            broker_index = _pop_first_unused(order_id_index[order_id], used_broker_indexes)
        if broker_index is None:
            broker_index = _pop_preferred_broker_index(
                internal_row=internal_row,
                candidates=fallback_index[_fallback_key(internal_row)],
                broker_rows=broker_rows,
                used_indexes=used_broker_indexes,
            )

        if broker_index is None:
            results.append(
                {
                    "match_status": "missing_broker_record",
                    "internal_row": deepcopy(internal_row),
                    "broker_row": None,
                    "mismatch_fields": [],
                }
            )
            continue

        used_broker_indexes.add(broker_index)
        broker_row = broker_rows[broker_index]
        mismatch_fields = _mismatch_fields(internal_row, broker_row)
        results.append(
            {
                "match_status": "matched" if not mismatch_fields else "mismatched",
                "internal_row": deepcopy(internal_row),
                "broker_row": deepcopy(broker_row),
                "mismatch_fields": mismatch_fields,
            }
        )

    return results
