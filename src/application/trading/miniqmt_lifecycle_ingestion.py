"""
Normalize miniQMT lifecycle payloads into the shared broker lifecycle envelope.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

from src.application.trading.broker_lifecycle_event import BrokerLifecycleEvent
from src.application.trading.broker_order_correlation import MINIQMT_BROKER_CHANNEL

MINIQMT_WINDOWS_BRIDGE_SOURCE_NAME = "miniqmt/windows_bridge"

_MINIQMT_EVENT_TYPE_MAP = {
    "accept": "acknowledgement",
    "accepted": "acknowledgement",
    "ack": "acknowledgement",
    "acknowledged": "acknowledgement",
    "submitted": "acknowledgement",
    "reported": "acknowledgement",
    "cancel": "cancel",
    "cancelled": "cancel",
    "canceled": "cancel",
    "reject": "reject",
    "rejected": "reject",
    "error": "reject",
    "filled": "execution",
    "executed": "execution",
    "execution": "execution",
    "match": "execution",
    "partial_filled": "execution",
    "partially_filled": "execution",
    "part_traded_queueing": "execution",
    "traded": "execution",
    "all_traded": "execution",
}


def normalize_miniqmt_lifecycle_payload(payload: Mapping[str, Any]) -> BrokerLifecycleEvent:
    event_type = _normalize_miniqmt_event_type(payload)
    source_timestamp = _extract_datetime(
        payload,
        "source_timestamp",
        "occurred_at",
        "updated_at",
        "timestamp",
        "ts",
    )
    if source_timestamp is None:
        raise ValueError("miniQMT lifecycle payload missing source timestamp")

    return BrokerLifecycleEvent(
        event_type=event_type,
        broker_channel=MINIQMT_BROKER_CHANNEL,
        source_timestamp=source_timestamp,
        source_name=_extract_str(payload, "source_name") or MINIQMT_WINDOWS_BRIDGE_SOURCE_NAME,
        external_order_id=_extract_str(payload, "external_order_id", "broker_order_id", "entrust_no", "order_sys_id"),
        local_submission_id=_extract_str(
            payload,
            "local_submission_id",
            "client_order_id",
            "client_request_id",
            "remark",
            "request_id",
        ),
        local_order_id=_extract_str(payload, "local_order_id", "order_id"),
        event_id=_extract_str(payload, "event_id", "event_uid", "message_id"),
        sequence_id=_extract_str(payload, "sequence_id", "sequence_no", "seq"),
        filled_quantity=_extract_int(payload, "filled_quantity", "filled_qty", "deal_qty"),
        fill_price=_extract_float(payload, "fill_price", "filled_price", "deal_price", "avg_price"),
        reason_code=_extract_str(payload, "reason_code", "error_code", "status_code"),
        reason_detail=_extract_str(payload, "reason_detail", "error_message", "message", "status_message"),
    )


def _normalize_miniqmt_event_type(payload: Mapping[str, Any]) -> str:
    direct_event_type = _extract_str(payload, "event_type")
    if direct_event_type is not None:
        normalized = _MINIQMT_EVENT_TYPE_MAP.get(_normalize_lookup_key(direct_event_type), direct_event_type)
        if normalized in {"acknowledgement", "reject", "cancel", "execution"}:
            return normalized

    raw_status = _extract_str(payload, "status", "order_status", "status_name")
    if raw_status is None:
        raise ValueError("miniQMT lifecycle payload missing event_type/status")

    normalized = _MINIQMT_EVENT_TYPE_MAP.get(_normalize_lookup_key(raw_status))
    if normalized is None:
        raise ValueError(f"Unsupported miniQMT lifecycle status: {raw_status}")
    return normalized


def _normalize_lookup_key(value: str) -> str:
    return value.strip().lower().replace("-", "_").replace(" ", "_")


def _extract_str(payload: Mapping[str, Any], *keys: str) -> str | None:
    for key in keys:
        value = payload.get(key)
        if value is None:
            continue
        normalized = str(value).strip()
        if normalized:
            return normalized
    return None


def _extract_int(payload: Mapping[str, Any], *keys: str) -> int | None:
    value = _extract_numeric(payload, *keys)
    if value is None:
        return None
    return int(value)


def _extract_float(payload: Mapping[str, Any], *keys: str) -> float | None:
    value = _extract_numeric(payload, *keys)
    if value is None:
        return None
    return float(value)


def _extract_numeric(payload: Mapping[str, Any], *keys: str) -> float | None:
    for key in keys:
        value = payload.get(key)
        if value is None or value == "":
            continue
        return float(value)
    return None


def _extract_datetime(payload: Mapping[str, Any], *keys: str) -> datetime | None:
    for key in keys:
        value = payload.get(key)
        if value is None or value == "":
            continue
        if isinstance(value, datetime):
            return value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)
        if isinstance(value, (int, float)):
            return datetime.fromtimestamp(value, tz=timezone.utc)

        normalized = str(value).strip()
        if normalized.endswith("Z"):
            normalized = f"{normalized[:-1]}+00:00"
        return datetime.fromisoformat(normalized)
    return None
