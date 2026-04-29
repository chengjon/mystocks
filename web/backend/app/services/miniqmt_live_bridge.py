"""
Repository-owned live bridge contract for the primary miniQMT path.
"""

from __future__ import annotations

import asyncio
import inspect
import time
from datetime import datetime, timezone
from typing import Any, Callable, Mapping

from src.utils.trading_runtime_config import (
    get_trading_miniqmt_live_bridge_poll_interval_seconds,
    get_trading_miniqmt_live_bridge_timeout_seconds,
    get_trading_qmt_bridge_contract_version,
)

MINIQMT_LIVE_BRIDGE_PROVIDER = "qmt"
MINIQMT_LIVE_BRIDGE_SUBMIT_METHOD = "submit_order"
MINIQMT_LIVE_BRIDGE_RESULT_METHOD = "task_result"

BRIDGE_SUBMISSION_RECEIPT = "bridge_submission_receipt"
BRIDGE_SUBMISSION_INVALID = "bridge_submission_invalid"
BRIDGE_SUBMISSION_AUTH_FAILED = "bridge_submission_auth_failed"
BRIDGE_SUBMISSION_UNSUPPORTED_CONTRACT_VERSION = "bridge_submission_unsupported_contract_version"
BRIDGE_SUBMISSION_UNSUPPORTED_METHOD = "bridge_submission_unsupported_method"
BRIDGE_RESULT_PENDING = "bridge_result_pending"
BRIDGE_RESULT_PAYLOAD = "bridge_result_payload"
BRIDGE_RESULT_TIMEOUT = "bridge_result_timeout"
BRIDGE_RESULT_UNAVAILABLE = "bridge_result_unavailable"
BRIDGE_RESULT_INVALID = "bridge_result_invalid"
BRIDGE_RESULT_AUTH_FAILED = "bridge_result_auth_failed"
BRIDGE_RESULT_UNSUPPORTED_CONTRACT_VERSION = "bridge_result_unsupported_contract_version"
BRIDGE_RESULT_UNSUPPORTED_METHOD = "bridge_result_unsupported_method"

_PENDING_RESULT_STATUSES = {"accepted", "pending", "processing", "queued", "running", "submitted"}
_TERMINAL_RESULT_STATUSES = {"cancelled", "completed", "error", "failed", "rejected", "succeeded", "success"}
_BROKER_EVENT_TYPES = {"acknowledgement", "reject", "cancel", "execution"}
_BROKER_EVENT_TYPE_MAP = {
    "accept": "acknowledgement",
    "accepted": "acknowledgement",
    "ack": "acknowledgement",
    "acknowledged": "acknowledgement",
    "all_traded": "execution",
    "cancel": "cancel",
    "cancelled": "cancel",
    "canceled": "cancel",
    "error": "reject",
    "executed": "execution",
    "execution": "execution",
    "filled": "execution",
    "match": "execution",
    "part_traded_queueing": "execution",
    "partial_filled": "execution",
    "partially_filled": "execution",
    "reject": "reject",
    "rejected": "reject",
    "reported": "acknowledgement",
    "submitted": "acknowledgement",
    "traded": "execution",
}
_FAILURE_REASON_TO_SUBMISSION_STATE = {
    "live_bridge_auth_failed": BRIDGE_SUBMISSION_AUTH_FAILED,
    "live_bridge_unsupported_contract_version": BRIDGE_SUBMISSION_UNSUPPORTED_CONTRACT_VERSION,
    "live_bridge_unsupported_method": BRIDGE_SUBMISSION_UNSUPPORTED_METHOD,
}
_FAILURE_REASON_TO_RESULT_STATE = {
    "live_bridge_auth_failed": BRIDGE_RESULT_AUTH_FAILED,
    "live_bridge_unsupported_contract_version": BRIDGE_RESULT_UNSUPPORTED_CONTRACT_VERSION,
    "live_bridge_unsupported_method": BRIDGE_RESULT_UNSUPPORTED_METHOD,
}


class MiniQMTLiveBridgeClient:
    """Polling-first bridge client for repo-owned miniQMT live contract."""

    def __init__(
        self,
        bridge_adapter: Any,
        *,
        provider: str = MINIQMT_LIVE_BRIDGE_PROVIDER,
        submit_method: str = MINIQMT_LIVE_BRIDGE_SUBMIT_METHOD,
        result_method: str = MINIQMT_LIVE_BRIDGE_RESULT_METHOD,
        contract_version: str | None = None,
        timeout_seconds: float | None = None,
        poll_interval_seconds: float | None = None,
        time_fn: Callable[[], float] | None = None,
        sleep_fn: Callable[[float], None] | None = None,
    ) -> None:
        self.bridge_adapter = bridge_adapter
        self.provider = provider
        self.submit_method = submit_method
        self.result_method = result_method
        self.contract_version = contract_version or get_trading_qmt_bridge_contract_version()
        self.timeout_seconds = (
            timeout_seconds
            if timeout_seconds is not None
            else get_trading_miniqmt_live_bridge_timeout_seconds()
        )
        self.poll_interval_seconds = (
            poll_interval_seconds
            if poll_interval_seconds is not None
            else get_trading_miniqmt_live_bridge_poll_interval_seconds()
        )
        self._time_fn = time_fn or time.monotonic
        self._sleep_fn = sleep_fn or time.sleep

    def submit_order(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        try:
            raw_receipt = _run_bridge_call(
                self.bridge_adapter.get_data(
                    f"{self.provider}/{self.submit_method}",
                    params=dict(payload),
                )
            )
        except Exception as exc:
            return {
                "contract_state": BRIDGE_SUBMISSION_INVALID,
                "provider": self.provider,
                "method": self.submit_method,
                "task_id": None,
                "transport_status": "error",
                "receipt_timestamp": _utc_now().isoformat(),
                "reason_code": "bridge_submission_error",
                "reason_detail": str(exc),
                "bridge_contract_version": None,
                "raw_payload": {"error_message": str(exc)},
            }

        return normalize_live_submission_receipt(
            raw_receipt,
            provider=self.provider,
            method=self.submit_method,
            expected_contract_version=self.contract_version,
        )

    def fetch_task_result(self, task_id: str) -> dict[str, Any]:
        if not hasattr(self.bridge_adapter, "get_task_result"):
            return {
                "contract_state": BRIDGE_RESULT_UNAVAILABLE,
                "provider": self.provider,
                "method": self.result_method,
                "task_id": task_id,
                "reason_code": "live_bridge_unavailable",
                "reason_detail": "bridge adapter does not expose get_task_result",
                "bridge_contract_version": None,
                "raw_payload": None,
            }

        try:
            raw_payload = _run_bridge_call(
                self.bridge_adapter.get_task_result(
                    provider_name=self.provider,
                    task_id=task_id,
                )
            )
        except Exception as exc:
            return {
                "contract_state": BRIDGE_RESULT_UNAVAILABLE,
                "provider": self.provider,
                "method": self.result_method,
                "task_id": task_id,
                "reason_code": "live_bridge_unavailable",
                "reason_detail": str(exc),
                "bridge_contract_version": None,
                "raw_payload": {"error_message": str(exc)},
            }

        return normalize_live_result_payload(
            raw_payload,
            task_id=task_id,
            provider=self.provider,
            method=self.result_method,
            expected_contract_version=self.contract_version,
        )

    def poll_task_result(
        self,
        task_id: str,
        *,
        timeout_seconds: float | None = None,
        poll_interval_seconds: float | None = None,
    ) -> dict[str, Any]:
        deadline = self._time_fn() + (timeout_seconds if timeout_seconds is not None else self.timeout_seconds)
        interval = poll_interval_seconds if poll_interval_seconds is not None else self.poll_interval_seconds

        while True:
            normalized_payload = self.fetch_task_result(task_id)
            contract_state = normalized_payload["contract_state"]
            if contract_state != BRIDGE_RESULT_PENDING:
                return normalized_payload
            if self._time_fn() >= deadline:
                return {
                    "contract_state": BRIDGE_RESULT_TIMEOUT,
                    "provider": self.provider,
                    "method": self.result_method,
                    "task_id": task_id,
                    "reason_code": "bridge_result_timeout",
                    "reason_detail": (
                        f"miniQMT live bridge result did not reach a terminal state within "
                        f"{timeout_seconds if timeout_seconds is not None else self.timeout_seconds:.2f}s"
                    ),
                    "bridge_contract_version": normalized_payload.get("bridge_contract_version"),
                    "last_payload": normalized_payload,
                }
            self._sleep_fn(max(interval, 0.0))


def normalize_live_submission_receipt(
    raw_receipt: Any,
    *,
    provider: str,
    method: str,
    expected_contract_version: str | None = None,
) -> dict[str, Any]:
    if not isinstance(raw_receipt, Mapping):
        return {
            "contract_state": BRIDGE_SUBMISSION_INVALID,
            "provider": provider,
            "method": method,
            "task_id": None,
            "transport_status": None,
            "receipt_timestamp": _utc_now().isoformat(),
            "reason_code": "bridge_submission_non_mapping",
            "reason_detail": "live submission receipt must be a mapping payload",
            "bridge_contract_version": None,
            "raw_payload": raw_receipt,
        }

    bridge_contract_version = _extract_str(raw_receipt, "bridge_contract_version", "contract_version")
    contract_failure_state = _resolve_contract_failure_state(
        payload=raw_receipt,
        bridge_contract_version=bridge_contract_version,
        expected_contract_version=expected_contract_version,
        stage="submission",
    )
    if contract_failure_state is not None:
        reason_code = _normalize_lookup_key(_extract_str(raw_receipt, "reason_code", "error_code", "failure_class"))
        if reason_code is None and contract_failure_state == BRIDGE_SUBMISSION_UNSUPPORTED_CONTRACT_VERSION:
            reason_code = "live_bridge_unsupported_contract_version"
        reason_detail = _extract_str(raw_receipt, "reason_detail", "error_message", "message", "detail")
        if reason_detail is None and contract_failure_state == BRIDGE_SUBMISSION_UNSUPPORTED_CONTRACT_VERSION:
            reason_detail = (
                f"miniQMT live bridge receipt echoed contract version {bridge_contract_version or '<missing>'} "
                f"but expected {expected_contract_version}"
            )
        return {
            "contract_state": contract_failure_state,
            "provider": provider,
            "method": method,
            "task_id": _extract_str(raw_receipt, "task_id", "bridge_task_id", "receipt_id"),
            "transport_status": _normalize_status(_extract_str(raw_receipt, "status", "transport_status")),
            "receipt_timestamp": (
                _extract_datetime(raw_receipt, "receipt_timestamp", "timestamp", "updated_at", "occurred_at")
                or _utc_now()
            ).isoformat(),
            "reason_code": reason_code or "bridge_submission_contract_failure",
            "reason_detail": reason_detail or "miniQMT live bridge submission receipt contract failure",
            "bridge_contract_version": bridge_contract_version,
            "raw_payload": dict(raw_receipt),
        }

    task_id = _extract_str(raw_receipt, "task_id", "bridge_task_id", "receipt_id")
    receipt_timestamp = _extract_datetime(raw_receipt, "receipt_timestamp", "timestamp", "updated_at", "occurred_at")
    transport_status = _normalize_status(_extract_str(raw_receipt, "status", "transport_status"))

    if task_id is None or receipt_timestamp is None:
        missing_fields: list[str] = []
        if task_id is None:
            missing_fields.append("task_id")
        if receipt_timestamp is None:
            missing_fields.append("receipt_timestamp")
        return {
            "contract_state": BRIDGE_SUBMISSION_INVALID,
            "provider": provider,
            "method": method,
            "task_id": task_id,
            "transport_status": transport_status,
            "receipt_timestamp": receipt_timestamp.isoformat() if receipt_timestamp else _utc_now().isoformat(),
            "reason_code": "bridge_submission_missing_fields",
            "reason_detail": f"live submission receipt missing canonical fields: {', '.join(missing_fields)}",
            "missing_fields": missing_fields,
            "bridge_contract_version": bridge_contract_version,
            "raw_payload": dict(raw_receipt),
        }

    return {
        "contract_state": BRIDGE_SUBMISSION_RECEIPT,
        "provider": provider,
        "method": method,
        "task_id": task_id,
        "transport_status": transport_status,
        "receipt_timestamp": receipt_timestamp.isoformat(),
        "source_name": _extract_str(raw_receipt, "source_name", "source") or f"{provider}/windows_bridge",
        "bridge_contract_version": bridge_contract_version,
        "raw_payload": dict(raw_receipt),
    }


def normalize_live_result_payload(
    raw_payload: Any,
    *,
    task_id: str,
    provider: str,
    method: str,
    expected_contract_version: str | None = None,
) -> dict[str, Any]:
    if not isinstance(raw_payload, Mapping):
        return {
            "contract_state": BRIDGE_RESULT_INVALID,
            "provider": provider,
            "method": method,
            "task_id": task_id,
            "reason_code": "bridge_result_non_mapping",
            "reason_detail": "live bridge result payload must be a mapping payload",
            "bridge_contract_version": None,
            "raw_payload": raw_payload,
        }

    bridge_contract_version = _extract_str(raw_payload, "bridge_contract_version", "contract_version")
    contract_failure_state = _resolve_contract_failure_state(
        payload=raw_payload,
        bridge_contract_version=bridge_contract_version,
        expected_contract_version=expected_contract_version,
        stage="result",
    )
    if contract_failure_state is not None:
        reason_code = _normalize_lookup_key(_extract_str(raw_payload, "reason_code", "error_code", "failure_class"))
        if reason_code is None and contract_failure_state == BRIDGE_RESULT_UNSUPPORTED_CONTRACT_VERSION:
            reason_code = "live_bridge_unsupported_contract_version"
        reason_detail = _extract_str(raw_payload, "reason_detail", "error_message", "message", "detail")
        if reason_detail is None and contract_failure_state == BRIDGE_RESULT_UNSUPPORTED_CONTRACT_VERSION:
            reason_detail = (
                f"miniQMT live bridge result echoed contract version {bridge_contract_version or '<missing>'} "
                f"but expected {expected_contract_version}"
            )
        return {
            "contract_state": contract_failure_state,
            "provider": provider,
            "method": method,
            "task_id": task_id,
            "reason_code": reason_code or "bridge_result_contract_failure",
            "reason_detail": reason_detail or "miniQMT live bridge result contract failure",
            "bridge_contract_version": bridge_contract_version,
            "raw_payload": dict(raw_payload),
        }

    envelope_status = _normalize_status(_extract_str(raw_payload, "result_status", "status", "task_status"))
    if envelope_status in _PENDING_RESULT_STATUSES:
        return {
            "contract_state": BRIDGE_RESULT_PENDING,
            "provider": provider,
            "method": method,
            "task_id": task_id,
            "result_status": envelope_status,
            "bridge_contract_version": bridge_contract_version,
            "raw_payload": dict(raw_payload),
        }

    if envelope_status is None:
        return {
            "contract_state": BRIDGE_RESULT_INVALID,
            "provider": provider,
            "method": method,
            "task_id": task_id,
            "reason_code": "bridge_result_missing_status",
            "reason_detail": "live bridge result payload missing canonical result status",
            "bridge_contract_version": bridge_contract_version,
            "raw_payload": dict(raw_payload),
        }

    payload = _extract_result_payload(raw_payload)
    occurred_at = _extract_datetime(payload, "occurred_at", "updated_at", "timestamp", "source_timestamp") or _extract_datetime(
        raw_payload,
        "occurred_at",
        "updated_at",
        "timestamp",
    )

    broker_event_type = _extract_broker_event_type(payload)
    local_submission_id = _extract_str(
        payload,
        "local_submission_id",
        "client_order_id",
        "client_request_id",
        "remark",
        "request_id",
    )
    account_scope = _extract_str(payload, "account_scope", "account_id", "account")

    if envelope_status not in _TERMINAL_RESULT_STATUSES and broker_event_type is None:
        return {
            "contract_state": BRIDGE_RESULT_INVALID,
            "provider": provider,
            "method": method,
            "task_id": task_id,
            "reason_code": "bridge_result_unsupported_status",
            "reason_detail": f"unsupported live bridge result status: {envelope_status}",
            "bridge_contract_version": bridge_contract_version,
            "raw_payload": dict(raw_payload),
        }

    if broker_event_type is None or occurred_at is None or account_scope is None:
        missing_fields: list[str] = []
        if broker_event_type is None:
            missing_fields.append("broker_event_type")
        if occurred_at is None:
            missing_fields.append("occurred_at")
        if account_scope is None:
            missing_fields.append("account_scope")
        return {
            "contract_state": BRIDGE_RESULT_INVALID,
            "provider": provider,
            "method": method,
            "task_id": task_id,
            "result_status": envelope_status,
            "reason_code": "bridge_result_missing_fields",
            "reason_detail": f"live bridge result missing canonical fields: {', '.join(missing_fields)}",
            "missing_fields": missing_fields,
            "bridge_contract_version": bridge_contract_version,
            "raw_payload": dict(raw_payload),
        }

    return {
        "contract_state": BRIDGE_RESULT_PAYLOAD,
        "provider": provider,
        "method": method,
        "task_id": task_id,
        "result_status": envelope_status,
        "occurred_at": occurred_at.isoformat(),
        "broker_event_type": broker_event_type,
        "local_submission_id": local_submission_id,
        "client_order_id": _extract_str(payload, "client_order_id") or local_submission_id,
        "account_scope": account_scope,
        "source_name": _extract_str(payload, "source_name", "source") or f"{provider}/windows_bridge",
        "external_order_id": _extract_str(payload, "external_order_id", "broker_order_id", "entrust_no", "order_sys_id"),
        "sequence_id": _extract_str(payload, "sequence_id", "sequence_no", "seq"),
        "reason_code": _extract_str(payload, "reason_code", "error_code", "status_code"),
        "reason_detail": _extract_str(payload, "reason_detail", "error_message", "message", "status_message"),
        "filled_quantity": _extract_int(payload, "filled_quantity", "filled_qty", "deal_qty"),
        "fill_price": _extract_float(payload, "fill_price", "filled_price", "deal_price", "avg_price"),
        "bridge_contract_version": bridge_contract_version,
        "raw_payload": dict(raw_payload),
    }


def _extract_result_payload(raw_payload: Mapping[str, Any]) -> Mapping[str, Any]:
    for key in ("result", "payload", "data"):
        value = raw_payload.get(key)
        if isinstance(value, Mapping):
            return value
    return raw_payload


def _extract_broker_event_type(payload: Mapping[str, Any]) -> str | None:
    direct_event_type = _extract_str(payload, "broker_event_type", "event_type")
    if direct_event_type is not None:
        normalized = _BROKER_EVENT_TYPE_MAP.get(_normalize_lookup_key(direct_event_type), direct_event_type)
        if normalized in _BROKER_EVENT_TYPES:
            return normalized

    raw_status = _extract_str(payload, "status", "order_status", "status_name")
    if raw_status is None:
        return None

    normalized = _BROKER_EVENT_TYPE_MAP.get(_normalize_lookup_key(raw_status))
    if normalized in _BROKER_EVENT_TYPES:
        return normalized
    return None


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


def _normalize_status(status: str | None) -> str | None:
    if status is None:
        return None
    return _normalize_lookup_key(status)


def _normalize_lookup_key(value: str | None) -> str | None:
    if value is None:
        return None
    return value.strip().lower().replace("-", "_").replace(" ", "_")


def _resolve_contract_failure_state(
    *,
    payload: Mapping[str, Any],
    bridge_contract_version: str | None,
    expected_contract_version: str | None,
    stage: str,
) -> str | None:
    reason_code = _normalize_lookup_key(_extract_str(payload, "reason_code", "error_code", "failure_class"))
    if stage == "submission" and reason_code in _FAILURE_REASON_TO_SUBMISSION_STATE:
        return _FAILURE_REASON_TO_SUBMISSION_STATE[reason_code]
    if stage == "result" and reason_code in _FAILURE_REASON_TO_RESULT_STATE:
        return _FAILURE_REASON_TO_RESULT_STATE[reason_code]
    if expected_contract_version is None:
        return None
    if bridge_contract_version == expected_contract_version:
        return None
    if stage == "submission":
        return BRIDGE_SUBMISSION_UNSUPPORTED_CONTRACT_VERSION
    return BRIDGE_RESULT_UNSUPPORTED_CONTRACT_VERSION


def _run_bridge_call(result: Any) -> Any:
    if inspect.isawaitable(result):
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(result)
        raise RuntimeError("MiniQMTLiveBridgeClient cannot synchronously call an async bridge while an event loop is running")
    return result


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)
