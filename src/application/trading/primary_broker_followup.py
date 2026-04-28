"""
Helpers for deferred primary-path broker evidence and explicit supplemental handoff.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, Mapping

from src.application.trading.broker_order_correlation import MINIQMT_BROKER_CHANNEL, TDX_MANUAL_BROKER_CHANNEL
from src.application.trading.broker_reconciliation import (
    AWAITING_BROKER_ACKNOWLEDGEMENT,
    BROKER_ACKNOWLEDGED,
    REVIEW_OWNER_TRADING_OPERATIONS,
    REVIEW_REQUIRED,
)
from src.application.trading.miniqmt_lifecycle_ingestion import normalize_miniqmt_lifecycle_payload
from src.application.trading.tdx_manual_lifecycle_ingestion import TDX_MANUAL_SOURCE_NAME
from src.domain.trading.model.order import Order

UNMATCHED_DEFERRED_BRIDGE_RESULT = "unmatched_deferred_bridge_result"
SUPPLEMENTAL_HANDOFF_REQUESTED = "supplemental_handoff_requested"
SUPPLEMENTAL_HANDOFF_REVIEW_REQUIRED = "review_required"
TDX_SUPPLEMENTAL_HANDOFF_ADAPTER_PATH = (
    "src.application.trading.order_mgmt_service.OrderManagementService.record_tdx_supplemental_handoff"
)


def ingest_miniqmt_bridge_result_payload(
    *,
    payload: Mapping[str, Any],
    broker_submission_attempt_store: Any,
    broker_divergence_store: Any,
    record_broker_lifecycle_event: Callable[[Any], Dict[str, Any]],
) -> Dict[str, Any]:
    bridge_payload = dict(payload)
    attempt_record = _resolve_miniqmt_attempt_record(bridge_payload, broker_submission_attempt_store)
    if attempt_record is not None:
        bridge_payload.setdefault("local_submission_id", attempt_record["local_submission_id"])
        bridge_payload.setdefault("client_order_id", attempt_record["local_submission_id"])
        bridge_payload.setdefault("source_name", attempt_record.get("source_name"))

    lifecycle_event = normalize_miniqmt_lifecycle_payload(bridge_payload)
    persisted_record = record_broker_lifecycle_event(lifecycle_event)

    if _needs_deferred_bridge_review(persisted_record, event_type=lifecycle_event.event_type):
        broker_divergence_store.append(
            _build_unmatched_deferred_bridge_result(
                persisted_record=persisted_record,
                attempt_record=attempt_record,
                bridge_task_id=_extract_bridge_task_id(bridge_payload),
            )
        )

    return persisted_record


def record_tdx_supplemental_handoff(
    *,
    order: Order,
    reason: str,
    actor_id: str | None,
    source_id: str | None,
    broker_correlation_store: Any,
    broker_submission_attempt_store: Any,
    emit_existing_order_audit: Callable[..., None],
) -> Dict[str, Any]:
    correlation_record = broker_correlation_store.get_order_correlation(order.id.value)
    if correlation_record is None:
        raise ValueError(f"Broker order correlation not found: {order.id.value}")
    if correlation_record.get("broker_channel") != MINIQMT_BROKER_CHANNEL:
        raise ValueError("Tongdaxin supplemental handoff requires an active miniQMT primary correlation")
    if correlation_record.get("acknowledgement_status") == BROKER_ACKNOWLEDGED or correlation_record.get("external_order_id"):
        raise ValueError("Tongdaxin supplemental handoff is blocked after broker acknowledgement is already confirmed")

    prior_attempt = broker_submission_attempt_store.get_latest_for_order(
        order.id.value,
        broker_channel=MINIQMT_BROKER_CHANNEL,
    )
    local_submission_id = str(correlation_record["local_submission_id"])
    handoff_record = {
        "order_id": order.id.value,
        "local_submission_id": local_submission_id,
        "broker_channel": TDX_MANUAL_BROKER_CHANNEL,
        "adapter_path": TDX_SUPPLEMENTAL_HANDOFF_ADAPTER_PATH,
        "account_scope": str(correlation_record.get("account_scope") or "operator_assisted"),
        "session_scope": correlation_record.get("session_scope"),
        "submission_status": SUPPLEMENTAL_HANDOFF_REQUESTED,
        "transport_status": None,
        "bridge_task_id": prior_attempt.get("bridge_task_id") if prior_attempt is not None else None,
        "external_order_id": None,
        "source_name": TDX_MANUAL_SOURCE_NAME,
        "failure_reason": None,
        "handoff_status": SUPPLEMENTAL_HANDOFF_REVIEW_REQUIRED,
        "handoff_reason": reason,
        "raw_response": {
            "handoff_actor_id": actor_id,
            "handoff_source_id": source_id,
            "prior_primary_correlation": correlation_record,
            "prior_primary_submission_attempt": prior_attempt,
        },
    }
    persisted_record = broker_submission_attempt_store.append(handoff_record)
    broker_correlation_store.upsert_submission(
        order_id=order.id.value,
        local_submission_id=local_submission_id,
        broker_channel=TDX_MANUAL_BROKER_CHANNEL,
        adapter_path=TDX_SUPPLEMENTAL_HANDOFF_ADAPTER_PATH,
        account_scope=str(correlation_record.get("account_scope") or "operator_assisted"),
        session_scope=correlation_record.get("session_scope"),
        acknowledgement_status=AWAITING_BROKER_ACKNOWLEDGEMENT,
    )
    emit_existing_order_audit(
        decision_outcome="broker_supplemental_handoff_requested",
        order=order,
        actor_id=actor_id,
        source_id=source_id or TDX_MANUAL_SOURCE_NAME,
        reason=reason,
        extra_payload={
            "broker_channel": TDX_MANUAL_BROKER_CHANNEL,
            "prior_broker_channel": correlation_record.get("broker_channel"),
            "prior_bridge_task_id": prior_attempt.get("bridge_task_id") if prior_attempt is not None else None,
            "handoff_status": SUPPLEMENTAL_HANDOFF_REVIEW_REQUIRED,
        },
    )
    return persisted_record


def service_ingest_miniqmt_bridge_result_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
    return ingest_miniqmt_bridge_result_payload(
        payload=payload,
        broker_submission_attempt_store=self.broker_submission_attempt_store,
        broker_divergence_store=self.broker_divergence_store,
        record_broker_lifecycle_event=self.record_broker_lifecycle_event,
    )


def service_record_tdx_supplemental_handoff(
    self,
    order_id: str,
    *,
    reason: str,
    actor_id: str | None = None,
    source_id: str | None = None,
) -> Dict[str, Any]:
    order = self._get_existing_order_or_raise(order_id)
    return record_tdx_supplemental_handoff(
        order=order,
        reason=reason,
        actor_id=actor_id,
        source_id=source_id,
        broker_correlation_store=self.broker_correlation_store,
        broker_submission_attempt_store=self.broker_submission_attempt_store,
        emit_existing_order_audit=self._emit_existing_order_audit,
    )


def _resolve_miniqmt_attempt_record(payload: Mapping[str, Any], broker_submission_attempt_store: Any) -> Dict[str, Any] | None:
    bridge_task_id = _extract_bridge_task_id(payload)
    if bridge_task_id is None or not hasattr(broker_submission_attempt_store, "get_by_bridge_task_id"):
        return None
    return broker_submission_attempt_store.get_by_bridge_task_id(
        bridge_task_id,
        broker_channel=MINIQMT_BROKER_CHANNEL,
    )


def _needs_deferred_bridge_review(persisted_record: Mapping[str, Any], *, event_type: str) -> bool:
    if event_type == "execution":
        return False
    return persisted_record.get("identity_status") in {
        "missing_identity",
        "unmatched_local_order_id",
        "unmatched_local_submission_id",
        "unmatched_external_order_id",
    }


def _build_unmatched_deferred_bridge_result(
    *,
    persisted_record: Mapping[str, Any],
    attempt_record: Mapping[str, Any] | None,
    bridge_task_id: str | None,
) -> Dict[str, Any]:
    return {
        "divergence_category": UNMATCHED_DEFERRED_BRIDGE_RESULT,
        "review_status": REVIEW_REQUIRED,
        "review_owner": REVIEW_OWNER_TRADING_OPERATIONS,
        "next_action": "manual_reconciliation_required",
        "required_evidence": "bridge_task_receipt_and_channel_scoped_submission_identity",
        "order_id": persisted_record.get("order_id") or (attempt_record.get("order_id") if attempt_record else None),
        "broker_channel": MINIQMT_BROKER_CHANNEL,
        "event_type": str(persisted_record["event_type"]),
        "external_order_id": persisted_record.get("external_order_id"),
        "local_submission_id": persisted_record.get("local_submission_id")
        or (attempt_record.get("local_submission_id") if attempt_record else None),
        "local_order_id": None,
        "local_order_status": None,
        "identity_status": str(persisted_record["identity_status"]),
        "sequencing_status": str(persisted_record["sequencing_status"]),
        "reported_filled_quantity": persisted_record.get("fill_quantity"),
        "reported_fill_price": persisted_record.get("fill_price"),
        "reason_code": "unmatched_deferred_bridge_result",
        "reason_detail": _build_unmatched_deferred_bridge_reason(attempt_record, bridge_task_id),
        "adapter_path": persisted_record.get("adapter_path") or (attempt_record.get("adapter_path") if attempt_record else None),
        "account_scope": persisted_record.get("account_scope") or (attempt_record.get("account_scope") if attempt_record else None),
        "session_scope": persisted_record.get("session_scope") or (attempt_record.get("session_scope") if attempt_record else None),
    }


def _build_unmatched_deferred_bridge_reason(
    attempt_record: Mapping[str, Any] | None,
    bridge_task_id: str | None,
) -> str:
    if attempt_record is None:
        if bridge_task_id is not None:
            return f"deferred miniQMT bridge result could not be matched to a recorded task receipt: {bridge_task_id}"
        return "deferred miniQMT bridge result arrived without a recorded task receipt or safe submission identity"
    return "deferred miniQMT bridge result no longer matches the active channel-scoped correlation surface"


def _extract_bridge_task_id(payload: Mapping[str, Any]) -> str | None:
    for key in ("bridge_task_id", "task_id", "receipt_id"):
        value = payload.get(key)
        if value is None:
            continue
        normalized = str(value).strip()
        if normalized:
            return normalized
    return None
