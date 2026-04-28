"""
Normalize Tongdaxin supplemental lifecycle payloads into the shared broker lifecycle envelope.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

from src.application.trading.broker_lifecycle_event import BrokerLifecycleEvent
from src.application.trading.broker_order_correlation import TDX_MANUAL_BROKER_CHANNEL

TDX_MANUAL_SOURCE_NAME = "tdx/manual"

_TDX_MANUAL_EVENT_TYPE_MAP = {
    "accept": "acknowledgement",
    "accepted": "acknowledgement",
    "ack": "acknowledgement",
    "acknowledged": "acknowledgement",
    "submitted": "acknowledgement",
    "report": "acknowledgement",
    "reported": "acknowledgement",
    "cancel": "cancel",
    "cancelled": "cancel",
    "canceled": "cancel",
    "reject": "reject",
    "rejected": "reject",
    "filled": "execution",
    "executed": "execution",
    "execution": "execution",
    "matched": "execution",
    "partial_filled": "execution",
    "partially_filled": "execution",
}


def normalize_tdx_manual_lifecycle_payload(payload: Mapping[str, Any]) -> BrokerLifecycleEvent:
    event_type = _normalize_tdx_manual_event_type(payload)
    source_timestamp = _extract_datetime(
        payload,
        "source_timestamp",
        "captured_at",
        "updated_at",
        "timestamp",
        "ts",
    )
    if source_timestamp is None:
        raise ValueError("Tongdaxin manual lifecycle payload missing source timestamp")

    operator_note = _extract_str(payload, "reason_detail", "operator_note", "message", "note")
    return BrokerLifecycleEvent(
        event_type=event_type,
        broker_channel=TDX_MANUAL_BROKER_CHANNEL,
        source_timestamp=source_timestamp,
        source_name=_extract_str(payload, "source_name") or TDX_MANUAL_SOURCE_NAME,
        external_order_id=_extract_str(payload, "external_order_id", "tdx_order_ref", "broker_order_id", "entrust_no"),
        local_submission_id=_extract_str(
            payload,
            "local_submission_id",
            "client_order_id",
            "manual_ticket_id",
            "request_id",
        ),
        local_order_id=_extract_str(payload, "local_order_id", "order_id"),
        event_id=_extract_str(payload, "event_id", "capture_id", "manual_capture_id"),
        sequence_id=_extract_str(payload, "sequence_id", "sequence_no", "capture_sequence"),
        filled_quantity=_extract_int(payload, "filled_quantity", "filled_qty", "deal_qty"),
        fill_price=_extract_float(payload, "fill_price", "filled_price", "deal_price", "avg_price"),
        reason_code=_extract_str(payload, "reason_code", "operator_reason_code", "status_code"),
        reason_detail=operator_note,
    )


def _normalize_tdx_manual_event_type(payload: Mapping[str, Any]) -> str:
    direct_event_type = _extract_str(payload, "event_type")
    if direct_event_type is not None:
        normalized = _TDX_MANUAL_EVENT_TYPE_MAP.get(_normalize_lookup_key(direct_event_type), direct_event_type)
        if normalized in {"acknowledgement", "reject", "cancel", "execution"}:
            return normalized

    raw_status = _extract_str(payload, "status", "status_name")
    if raw_status is None:
        raise ValueError("Tongdaxin manual lifecycle payload missing event_type/status")

    normalized = _TDX_MANUAL_EVENT_TYPE_MAP.get(_normalize_lookup_key(raw_status))
    if normalized is None:
        raise ValueError(f"Unsupported Tongdaxin manual lifecycle status: {raw_status}")
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
