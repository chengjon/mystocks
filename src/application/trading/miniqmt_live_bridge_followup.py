"""
Polling-first live bridge follow-up for miniQMT primary-path results.
"""

from __future__ import annotations

from typing import Any, Dict, Mapping

from src.application.trading.broker_order_correlation import MINIQMT_BROKER_CHANNEL, TDX_MANUAL_BROKER_CHANNEL
from src.application.trading.broker_reconciliation import (
    AWAITING_BROKER_ACKNOWLEDGEMENT,
    BROKER_ACKNOWLEDGED,
    REVIEW_OWNER_TRADING_OPERATIONS,
    REVIEW_REQUIRED,
)
from src.application.trading import primary_broker_followup as broker_followup
from src.application.trading.tdx_manual_lifecycle_ingestion import TDX_MANUAL_SOURCE_NAME
from src.domain.trading.model.order import Order

BRIDGE_RESULT_PAYLOAD = "bridge_result_payload"
BRIDGE_RESULT_TIMEOUT = "bridge_result_timeout"
BRIDGE_RESULT_UNAVAILABLE = "bridge_result_unavailable"
BRIDGE_RESULT_INVALID = "bridge_result_invalid"
BRIDGE_RESULT_AUTH_FAILED = "bridge_result_auth_failed"
BRIDGE_RESULT_UNSUPPORTED_CONTRACT_VERSION = "bridge_result_unsupported_contract_version"
BRIDGE_RESULT_UNSUPPORTED_METHOD = "bridge_result_unsupported_method"

LIVE_BRIDGE_TIMEOUT_INCIDENT = "live_bridge_timeout"
LIVE_BRIDGE_UNAVAILABLE_INCIDENT = "live_bridge_unavailable"
LIVE_BRIDGE_INVALID_RESULT_INCIDENT = "live_bridge_invalid_result"
LIVE_BRIDGE_IDENTITY_MISMATCH_INCIDENT = "live_bridge_identity_mismatch"
LIVE_BRIDGE_BRIDGE_RESULT_ONLY_INCIDENT = "live_bridge_bridge_result_only"
LIVE_BRIDGE_AUTH_FAILED_INCIDENT = "live_bridge_auth_failed"
LIVE_BRIDGE_UNSUPPORTED_CONTRACT_VERSION_INCIDENT = "live_bridge_unsupported_contract_version"
LIVE_BRIDGE_UNSUPPORTED_METHOD_INCIDENT = "live_bridge_unsupported_method"

LIVE_BRIDGE_REVIEW_NEXT_ACTION = "operator_review_or_tdx_supplemental_handoff"
LIVE_BRIDGE_REQUIRED_EVIDENCE = "bridge_task_receipt_and_live_result_contract"
LIVE_BRIDGE_RESULT_ADAPTER_PATH = (
    "src.application.trading.order_mgmt_service.OrderManagementService.poll_miniqmt_live_bridge_result"
)


def poll_miniqmt_live_bridge_result(
    *,
    task_id: str,
    primary_broker_live_bridge: Any,
    broker_submission_attempt_store: Any,
    broker_divergence_store: Any,
    record_broker_lifecycle_event: Any,
    timeout_seconds: float | None = None,
    poll_interval_seconds: float | None = None,
) -> Dict[str, Any]:
    attempt_record = _resolve_attempt_record(
        broker_submission_attempt_store=broker_submission_attempt_store,
        task_id=task_id,
    )
    if attempt_record is None:
        incident = _build_live_bridge_review_incident(
            category=LIVE_BRIDGE_INVALID_RESULT_INCIDENT,
            attempt_record=None,
            task_id=task_id,
            result_payload={
                "contract_state": BRIDGE_RESULT_INVALID,
                "reason_code": "unknown_bridge_task_id",
                "reason_detail": f"miniQMT live bridge task receipt is not recorded: {task_id}",
            },
        )
        broker_divergence_store.append(incident)
        return incident

    result_payload = primary_broker_live_bridge.poll_task_result(
        task_id,
        timeout_seconds=timeout_seconds,
        poll_interval_seconds=poll_interval_seconds,
    )
    contract_state = str(result_payload.get("contract_state") or "")
    if contract_state != BRIDGE_RESULT_PAYLOAD:
        incident = _build_live_bridge_review_incident(
            category=_resolve_incident_category(contract_state),
            attempt_record=attempt_record,
            task_id=task_id,
            result_payload=result_payload,
        )
        broker_divergence_store.append(incident)
        return incident

    mismatch = _build_identity_mismatch_incident(
        attempt_record=attempt_record,
        task_id=task_id,
        result_payload=result_payload,
    )
    if mismatch is not None:
        broker_divergence_store.append(mismatch)
        return mismatch

    if result_payload.get("broker_event_type") is None:
        incident = _build_live_bridge_review_incident(
            category=LIVE_BRIDGE_BRIDGE_RESULT_ONLY_INCIDENT,
            attempt_record=attempt_record,
            task_id=task_id,
            result_payload={
                **dict(result_payload),
                "reason_code": "bridge_result_requires_broker_lifecycle_followup",
                "reason_detail": (
                    "live bridge result is contract-valid but does not yet carry broker lifecycle evidence"
                ),
            },
        )
        broker_divergence_store.append(incident)
        return incident

    bridge_payload = _build_bridge_result_ingestion_payload(result_payload)
    return broker_followup.ingest_miniqmt_bridge_result_payload(
        payload=bridge_payload,
        broker_submission_attempt_store=broker_submission_attempt_store,
        broker_divergence_store=broker_divergence_store,
        record_broker_lifecycle_event=record_broker_lifecycle_event,
    )


def record_tdx_supplemental_handoff(
    *,
    order: Order,
    reason: str,
    actor_id: str | None,
    source_id: str | None,
    broker_correlation_store: Any,
    broker_submission_attempt_store: Any,
    broker_divergence_store: Any,
    emit_existing_order_audit: Any,
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
    prior_live_bridge_evidence = _find_prior_live_bridge_evidence(
        broker_divergence_store=broker_divergence_store,
        order_id=order.id.value,
        local_submission_id=local_submission_id,
        bridge_task_id=prior_attempt.get("bridge_task_id") if prior_attempt is not None else None,
    )

    handoff_record = {
        "order_id": order.id.value,
        "local_submission_id": local_submission_id,
        "broker_channel": TDX_MANUAL_BROKER_CHANNEL,
        "adapter_path": broker_followup.TDX_SUPPLEMENTAL_HANDOFF_ADAPTER_PATH,
        "account_scope": str(correlation_record.get("account_scope") or "operator_assisted"),
        "session_scope": correlation_record.get("session_scope"),
        "submission_status": broker_followup.SUPPLEMENTAL_HANDOFF_REQUESTED,
        "transport_status": None,
        "bridge_task_id": prior_attempt.get("bridge_task_id") if prior_attempt is not None else None,
        "external_order_id": None,
        "source_name": TDX_MANUAL_SOURCE_NAME,
        "failure_reason": None,
        "handoff_status": broker_followup.SUPPLEMENTAL_HANDOFF_REVIEW_REQUIRED,
        "handoff_reason": reason,
        "raw_response": {
            "handoff_actor_id": actor_id,
            "handoff_source_id": source_id,
            "prior_primary_correlation": correlation_record,
            "prior_primary_submission_attempt": prior_attempt,
            "prior_live_bridge_evidence": prior_live_bridge_evidence,
        },
    }
    persisted_record = broker_submission_attempt_store.append(handoff_record)
    broker_correlation_store.upsert_submission(
        order_id=order.id.value,
        local_submission_id=local_submission_id,
        broker_channel=TDX_MANUAL_BROKER_CHANNEL,
        adapter_path=broker_followup.TDX_SUPPLEMENTAL_HANDOFF_ADAPTER_PATH,
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
            "handoff_status": broker_followup.SUPPLEMENTAL_HANDOFF_REVIEW_REQUIRED,
            "prior_live_bridge_incident": prior_live_bridge_evidence.get("divergence_category")
            if isinstance(prior_live_bridge_evidence, Mapping)
            else None,
        },
    )
    return persisted_record


def service_poll_miniqmt_live_bridge_result(
    self,
    task_id: str,
    *,
    timeout_seconds: float | None = None,
    poll_interval_seconds: float | None = None,
) -> Dict[str, Any]:
    if self.primary_broker_live_bridge is None:
        raise ValueError("miniQMT live bridge client is not configured")
    return poll_miniqmt_live_bridge_result(
        task_id=task_id,
        primary_broker_live_bridge=self.primary_broker_live_bridge,
        broker_submission_attempt_store=self.broker_submission_attempt_store,
        broker_divergence_store=self.broker_divergence_store,
        record_broker_lifecycle_event=self.record_broker_lifecycle_event,
        timeout_seconds=timeout_seconds,
        poll_interval_seconds=poll_interval_seconds,
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
        broker_divergence_store=self.broker_divergence_store,
        emit_existing_order_audit=self._emit_existing_order_audit,
    )


def _resolve_attempt_record(*, broker_submission_attempt_store: Any, task_id: str) -> Dict[str, Any] | None:
    if not hasattr(broker_submission_attempt_store, "get_by_bridge_task_id"):
        return None
    return broker_submission_attempt_store.get_by_bridge_task_id(
        task_id,
        broker_channel=MINIQMT_BROKER_CHANNEL,
    )


def _resolve_incident_category(contract_state: str) -> str:
    if contract_state == BRIDGE_RESULT_TIMEOUT:
        return LIVE_BRIDGE_TIMEOUT_INCIDENT
    if contract_state == BRIDGE_RESULT_AUTH_FAILED:
        return LIVE_BRIDGE_AUTH_FAILED_INCIDENT
    if contract_state == BRIDGE_RESULT_UNSUPPORTED_CONTRACT_VERSION:
        return LIVE_BRIDGE_UNSUPPORTED_CONTRACT_VERSION_INCIDENT
    if contract_state == BRIDGE_RESULT_UNSUPPORTED_METHOD:
        return LIVE_BRIDGE_UNSUPPORTED_METHOD_INCIDENT
    if contract_state == BRIDGE_RESULT_UNAVAILABLE:
        return LIVE_BRIDGE_UNAVAILABLE_INCIDENT
    return LIVE_BRIDGE_INVALID_RESULT_INCIDENT


def _build_bridge_result_ingestion_payload(result_payload: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "task_id": result_payload.get("task_id"),
        "account_scope": result_payload.get("account_scope"),
        "source_name": result_payload.get("source_name"),
        "event_type": result_payload.get("broker_event_type"),
        "occurred_at": result_payload.get("occurred_at"),
        "local_submission_id": result_payload.get("local_submission_id"),
        "client_order_id": result_payload.get("client_order_id"),
        "external_order_id": result_payload.get("external_order_id"),
        "event_id": result_payload.get("event_id"),
        "sequence_id": result_payload.get("sequence_id"),
        "filled_quantity": result_payload.get("filled_quantity"),
        "fill_price": result_payload.get("fill_price"),
        "reason_code": result_payload.get("reason_code"),
        "reason_detail": result_payload.get("reason_detail"),
        "bridge_contract_version": result_payload.get("bridge_contract_version"),
    }


def _build_identity_mismatch_incident(
    *,
    attempt_record: Mapping[str, Any],
    task_id: str,
    result_payload: Mapping[str, Any],
) -> Dict[str, Any] | None:
    expected_submission_id = str(attempt_record.get("local_submission_id"))
    actual_submission_id = str(
        result_payload.get("local_submission_id")
        or result_payload.get("client_order_id")
        or ""
    ).strip()
    if not actual_submission_id:
        return _build_live_bridge_review_incident(
            category=LIVE_BRIDGE_INVALID_RESULT_INCIDENT,
            attempt_record=attempt_record,
            task_id=task_id,
            result_payload={
                **dict(result_payload),
                "reason_code": "missing_identity_echo",
                "reason_detail": "live bridge result did not echo client_order_id or local_submission_id",
            },
        )
    if actual_submission_id != expected_submission_id:
        return _build_live_bridge_review_incident(
            category=LIVE_BRIDGE_IDENTITY_MISMATCH_INCIDENT,
            attempt_record=attempt_record,
            task_id=task_id,
            result_payload={
                **dict(result_payload),
                "reason_code": "local_submission_id_mismatch",
                "reason_detail": (
                    f"live bridge result echoed local submission id {actual_submission_id} "
                    f"but expected {expected_submission_id}"
                ),
            },
        )

    expected_account_scope = str(attempt_record.get("account_scope") or "").strip()
    actual_account_scope = str(result_payload.get("account_scope") or "").strip()
    if expected_account_scope and actual_account_scope and actual_account_scope != expected_account_scope:
        return _build_live_bridge_review_incident(
            category=LIVE_BRIDGE_IDENTITY_MISMATCH_INCIDENT,
            attempt_record=attempt_record,
            task_id=task_id,
            result_payload={
                **dict(result_payload),
                "reason_code": "account_scope_mismatch",
                "reason_detail": (
                    f"live bridge result echoed account scope {actual_account_scope} "
                    f"but expected {expected_account_scope}"
                ),
            },
        )
    return None


def _build_live_bridge_review_incident(
    *,
    category: str,
    attempt_record: Mapping[str, Any] | None,
    task_id: str,
    result_payload: Mapping[str, Any],
) -> Dict[str, Any]:
    contract_state = str(result_payload.get("contract_state") or BRIDGE_RESULT_INVALID)
    identity_status = _resolve_identity_status(category=category, contract_state=contract_state)
    sequencing_status = "not_applicable"

    return {
        "divergence_category": category,
        "review_status": REVIEW_REQUIRED,
        "review_owner": REVIEW_OWNER_TRADING_OPERATIONS,
        "next_action": LIVE_BRIDGE_REVIEW_NEXT_ACTION,
        "required_evidence": LIVE_BRIDGE_REQUIRED_EVIDENCE,
        "order_id": attempt_record.get("order_id") if attempt_record else None,
        "broker_channel": MINIQMT_BROKER_CHANNEL,
        "event_type": str(result_payload.get("broker_event_type") or "bridge_result"),
        "external_order_id": result_payload.get("external_order_id"),
        "local_submission_id": (attempt_record.get("local_submission_id") if attempt_record else None)
        or result_payload.get("local_submission_id"),
        "local_order_id": None,
        "local_order_status": None,
        "identity_status": identity_status,
        "sequencing_status": sequencing_status,
        "reported_filled_quantity": result_payload.get("filled_quantity"),
        "reported_fill_price": result_payload.get("fill_price"),
        "reason_code": str(result_payload.get("reason_code") or category),
        "reason_detail": str(result_payload.get("reason_detail") or category),
        "failure_class": str(result_payload.get("failure_class") or result_payload.get("reason_code") or category),
        "adapter_path": (attempt_record.get("adapter_path") if attempt_record else None) or LIVE_BRIDGE_RESULT_ADAPTER_PATH,
        "account_scope": attempt_record.get("account_scope") if attempt_record else result_payload.get("account_scope"),
        "session_scope": attempt_record.get("session_scope") if attempt_record else None,
        "bridge_task_id": task_id,
        "bridge_contract_version": result_payload.get("bridge_contract_version"),
        "live_contract_state": contract_state,
        "raw_response": dict(result_payload),
    }


def _resolve_identity_status(*, category: str, contract_state: str) -> str:
    if category == LIVE_BRIDGE_TIMEOUT_INCIDENT:
        return "bridge_result_timeout"
    if category == LIVE_BRIDGE_UNAVAILABLE_INCIDENT:
        return "bridge_result_unavailable"
    if category == LIVE_BRIDGE_AUTH_FAILED_INCIDENT:
        return "bridge_auth_failed"
    if category == LIVE_BRIDGE_UNSUPPORTED_CONTRACT_VERSION_INCIDENT:
        return "bridge_contract_version_mismatch"
    if category == LIVE_BRIDGE_UNSUPPORTED_METHOD_INCIDENT:
        return "bridge_method_not_allowed"
    if category == LIVE_BRIDGE_IDENTITY_MISMATCH_INCIDENT:
        return "mismatched_bridge_identity"
    if contract_state == BRIDGE_RESULT_INVALID:
        return "missing_identity"
    return "bridge_result_review_required"


def _find_prior_live_bridge_evidence(
    *,
    broker_divergence_store: Any,
    order_id: str,
    local_submission_id: str,
    bridge_task_id: str | None,
) -> Dict[str, Any] | None:
    if broker_divergence_store is None or not hasattr(broker_divergence_store, "fetch_recent"):
        return None
    for record in broker_divergence_store.fetch_recent(limit=50):
        if record.get("broker_channel") != MINIQMT_BROKER_CHANNEL:
            continue
        if record.get("order_id") == order_id:
            return record
        if record.get("local_submission_id") == local_submission_id:
            return record
        if bridge_task_id and record.get("bridge_task_id") == bridge_task_id:
            return record
    return None
