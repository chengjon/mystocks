"""
Shared broker acknowledgement and reconciliation helpers.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from src.application.trading.broker_lifecycle_event import BrokerLifecycleEvent
from src.application.trading.broker_order_correlation import MINIQMT_BROKER_CHANNEL, TDX_MANUAL_BROKER_CHANNEL
from src.domain.trading.model.order import Order
from src.domain.trading.value_objects import OrderStatus

AWAITING_BROKER_ACKNOWLEDGEMENT = "awaiting_broker_acknowledgement"
BROKER_ACKNOWLEDGED = "acknowledged"
SEQUENCING_METADATA_PRESENT = "sequencing_metadata_present"
SEQUENCING_METADATA_MISSING = "sequencing_metadata_missing"
REVIEW_REQUIRED = "review_required"
REVIEW_OWNER_TRADING_OPERATIONS = "trading_operations"
AWAITING_BROKER_ACKNOWLEDGEMENT_DIVERGENCE = "awaiting_broker_acknowledgement"
UNMATCHED_EXTERNAL_ORDER_DIVERGENCE = "unmatched_external_order"
LOCALLY_TERMINAL_EXTERNALLY_OPEN_DIVERGENCE = "locally_terminal_externally_open"
EXTERNALLY_TERMINAL_LOCALLY_OPEN_DIVERGENCE = "externally_terminal_locally_open"
QUANTITY_OR_FILL_DIVERGENCE = "quantity_or_fill_divergence"
SUPPLEMENTAL_CHANNEL_REVIEW_REQUIRED_DIVERGENCE = "supplemental_channel_review_required"
AUTO_RESOLVED = "auto_resolved"
REPLAY_SUPPRESSION_ELIGIBLE = "eligible"
REPLAY_SUPPRESSION_BLOCKED = "blocked"
REPLAY_SUPPRESSION_SUPPRESSED_DUPLICATE = "suppressed_duplicate"
AUTO_RESOLUTION_APPLIED = "applied"
AUTO_RESOLUTION_BLOCKED = "blocked"
REPLAY_SUPPRESSION_ELIGIBLE = "eligible"
REPLAY_SUPPRESSION_BLOCKED = "blocked"
AUTO_RESOLUTION_APPLIED = "applied"
AUTO_RESOLUTION_BLOCKED = "blocked"

LOCAL_TERMINAL_ORDER_STATUSES = {
    OrderStatus.CANCELLED.value,
    OrderStatus.REJECTED.value,
    OrderStatus.EXPIRED.value,
    OrderStatus.FILLED.value,
}
LOCAL_OPEN_ORDER_STATUSES = {
    OrderStatus.CREATED.value,
    OrderStatus.SUBMITTED.value,
    OrderStatus.PARTIALLY_FILLED.value,
}


def _channel_allows_automated_authority(broker_channel: str | None) -> bool:
    return broker_channel is None or broker_channel == MINIQMT_BROKER_CHANNEL


def resolve_broker_correlation_for_event(
    event: BrokerLifecycleEvent,
    broker_correlation_store: Any,
) -> tuple[Optional[Dict[str, Any]], str]:
    broker_channel = event.broker_channel
    if event.local_order_id is not None:
        correlation_record = broker_correlation_store.get_order_correlation(event.local_order_id)
        if correlation_record is not None:
            return correlation_record, "matched_local_order_id"
        return None, "unmatched_local_order_id"

    if event.local_submission_id is not None and hasattr(broker_correlation_store, "get_by_local_submission_id"):
        correlation_record = broker_correlation_store.get_by_local_submission_id(
            event.local_submission_id,
            broker_channel=broker_channel,
        )
        if correlation_record is not None:
            return correlation_record, "matched_local_submission_id"
        return None, "unmatched_local_submission_id"

    if event.external_order_id is not None:
        correlation_record = broker_correlation_store.get_by_external_order_id(
            event.external_order_id,
            broker_channel=broker_channel,
        )
        if correlation_record is not None:
            return correlation_record, "matched_external_order_id"
        return None, "unmatched_external_order_id"

    return None, "missing_identity"


def classify_broker_event_sequencing(event: BrokerLifecycleEvent) -> str:
    if event.event_id is not None or event.sequence_id is not None:
        return SEQUENCING_METADATA_PRESENT
    return SEQUENCING_METADATA_MISSING


def build_broker_lifecycle_payload(
    *,
    event: BrokerLifecycleEvent,
    order_id: str | None,
    correlation_record: Optional[Dict[str, Any]],
    identity_status: str,
    sequencing_status: str,
) -> Dict[str, Any]:
    return {
        "event_type": event.event_type,
        "order_id": order_id,
        "broker_channel": event.broker_channel or (correlation_record.get("broker_channel") if correlation_record else None),
        "external_order_id": event.external_order_id,
        "local_submission_id": event.local_submission_id,
        "local_order_id": event.local_order_id,
        "source_timestamp": event.source_timestamp.isoformat(),
        "source_name": event.source_name,
        "event_id": event.event_id,
        "sequence_id": event.sequence_id,
        "identity_status": identity_status,
        "sequencing_status": sequencing_status,
        "fill_quantity": event.filled_quantity,
        "fill_price": event.fill_price,
        "reason_code": event.reason_code,
        "reason_detail": event.reason_detail,
        "adapter_path": correlation_record.get("adapter_path") if correlation_record is not None else None,
        "account_scope": correlation_record.get("account_scope") if correlation_record is not None else None,
        "session_scope": correlation_record.get("session_scope") if correlation_record is not None else None,
    }


def build_broker_divergence_record(
    *,
    event: BrokerLifecycleEvent,
    correlation_record: Optional[Dict[str, Any]],
    identity_status: str,
    sequencing_status: str,
    order_id: str | None,
    local_order: Optional[Order],
    local_order_status: str | None,
) -> Optional[Dict[str, Any]]:
    divergence_category: str | None = None
    reason_code = event.reason_code
    reason_detail = event.reason_detail

    if event.event_type == "execution" and identity_status in {
        "missing_identity",
        "unmatched_local_order_id",
        "unmatched_local_submission_id",
        "unmatched_external_order_id",
    }:
        divergence_category = UNMATCHED_EXTERNAL_ORDER_DIVERGENCE
        reason_code = reason_code or "unmatched_external_order"
        reason_detail = reason_detail or "execution event could not be matched safely to a local order"
    elif event.event_type == "execution" and local_order_status in LOCAL_TERMINAL_ORDER_STATUSES:
        divergence_category = LOCALLY_TERMINAL_EXTERNALLY_OPEN_DIVERGENCE
        reason_code = reason_code or "local_order_terminal_broker_execution_observed"
        reason_detail = reason_detail or f"broker execution observed while local order status is {local_order_status}"
    elif event.event_type in {"cancel", "reject"} and local_order_status in LOCAL_OPEN_ORDER_STATUSES:
        divergence_category = EXTERNALLY_TERMINAL_LOCALLY_OPEN_DIVERGENCE
        reason_code = reason_code or "broker_terminal_fact_local_order_open"
        reason_detail = reason_detail or f"broker {event.event_type} observed while local order status is {local_order_status}"
    elif has_quantity_or_fill_divergence(local_order, event):
        divergence_category = QUANTITY_OR_FILL_DIVERGENCE
        reason_code = reason_code or "reported_fill_quantity_exceeds_local_order_quantity"
        reason_detail = reason_detail or "reported broker fill quantity exceeds local order quantity"
    elif (
        correlation_record is not None
        and correlation_record.get("acknowledgement_status") == AWAITING_BROKER_ACKNOWLEDGEMENT
        and event.event_type != "acknowledgement"
        and event.external_order_id is None
    ):
        divergence_category = AWAITING_BROKER_ACKNOWLEDGEMENT_DIVERGENCE
        reason_code = reason_code or "awaiting_broker_acknowledgement"
        reason_detail = reason_detail or "broker lifecycle event arrived before external identity binding"
    elif event.broker_channel == TDX_MANUAL_BROKER_CHANNEL:
        divergence_category = SUPPLEMENTAL_CHANNEL_REVIEW_REQUIRED_DIVERGENCE
        reason_code = reason_code or "supplemental_channel_review_required"
        reason_detail = reason_detail or "supplemental Tongdaxin lifecycle evidence requires operator review"

    if divergence_category is None:
        return None

    return {
        "divergence_category": divergence_category,
        "review_status": REVIEW_REQUIRED,
        "review_owner": REVIEW_OWNER_TRADING_OPERATIONS,
        "next_action": "manual_reconciliation_required",
        "required_evidence": required_evidence_for_divergence(divergence_category),
        "order_id": order_id,
        "broker_channel": event.broker_channel or (correlation_record.get("broker_channel") if correlation_record else None),
        "event_type": event.event_type,
        "external_order_id": event.external_order_id,
        "local_submission_id": event.local_submission_id,
        "local_order_id": event.local_order_id,
        "local_order_status": local_order_status,
        "identity_status": identity_status,
        "sequencing_status": sequencing_status,
        "reported_filled_quantity": event.filled_quantity,
        "reported_fill_price": event.fill_price,
        "reason_code": reason_code,
        "reason_detail": reason_detail,
        "adapter_path": correlation_record.get("adapter_path") if correlation_record is not None else None,
        "account_scope": correlation_record.get("account_scope") if correlation_record is not None else None,
        "session_scope": correlation_record.get("session_scope") if correlation_record is not None else None,
    }


def evaluate_replay_suppression_policy(
    *,
    event: BrokerLifecycleEvent,
    identity_status: str,
    sequencing_status: str,
) -> Dict[str, Optional[str]]:
    if not _channel_allows_automated_authority(event.broker_channel):
        return {
            "replay_suppression_status": REPLAY_SUPPRESSION_BLOCKED,
            "replay_suppression_basis": None,
            "replay_suppression_reason": "broker_channel_not_replay_authorized",
        }

    if identity_status not in {
        "matched_local_order_id",
        "matched_local_submission_id",
        "matched_external_order_id",
    }:
        return {
            "replay_suppression_status": REPLAY_SUPPRESSION_BLOCKED,
            "replay_suppression_basis": None,
            "replay_suppression_reason": "missing_matched_broker_identity",
        }

    if sequencing_status != SEQUENCING_METADATA_PRESENT:
        return {
            "replay_suppression_status": REPLAY_SUPPRESSION_BLOCKED,
            "replay_suppression_basis": None,
            "replay_suppression_reason": "missing_broker_sequence_identity",
        }

    if event.event_id is not None:
        basis = "event_id"
    elif event.sequence_id is not None:
        basis = "sequence_id"
    else:
        basis = None

    if basis is None:
        return {
            "replay_suppression_status": REPLAY_SUPPRESSION_BLOCKED,
            "replay_suppression_basis": None,
            "replay_suppression_reason": "missing_broker_sequence_identity",
        }

    return {
        "replay_suppression_status": REPLAY_SUPPRESSION_ELIGIBLE,
        "replay_suppression_basis": basis,
        "replay_suppression_reason": "explicit_broker_identity_and_sequence_evidence_present",
    }


def find_duplicate_broker_lifecycle_event(
    *,
    event: BrokerLifecycleEvent,
    order_id: str | None,
    external_order_id: str | None,
    broker_lifecycle_event_store: Any,
) -> Optional[Dict[str, Any]]:
    if not hasattr(broker_lifecycle_event_store, "fetch_recent"):
        return None

    recent_records = broker_lifecycle_event_store.fetch_recent(limit=100)
    for record in recent_records:
        if record.get("event_type") != event.event_type:
            continue
        if event.broker_channel is not None and record.get("broker_channel") != event.broker_channel:
            continue
        if order_id is not None and record.get("order_id") != order_id:
            continue
        if external_order_id is not None and record.get("external_order_id") != external_order_id:
            continue
        if event.event_id is not None and record.get("event_id") == event.event_id:
            return record
        if event.sequence_id is not None and record.get("sequence_id") == event.sequence_id:
            return record

    return None


def evaluate_auto_resolution_policy(
    *,
    event: BrokerLifecycleEvent,
    local_order: Optional[Order],
    divergence_record: Dict[str, Any],
    identity_status: str,
    sequencing_status: str,
) -> Dict[str, Optional[str]]:
    if not _channel_allows_automated_authority(event.broker_channel):
        return {
            "auto_resolution_status": AUTO_RESOLUTION_BLOCKED,
            "auto_resolution_basis": None,
            "auto_resolution_reason": "broker_channel_not_auto_resolution_authorized",
        }

    divergence_category = str(divergence_record["divergence_category"])
    if divergence_category != EXTERNALLY_TERMINAL_LOCALLY_OPEN_DIVERGENCE:
        return {
            "auto_resolution_status": AUTO_RESOLUTION_BLOCKED,
            "auto_resolution_basis": None,
            "auto_resolution_reason": "divergence_category_not_auto_resolvable",
        }

    if identity_status != "matched_external_order_id":
        return {
            "auto_resolution_status": AUTO_RESOLUTION_BLOCKED,
            "auto_resolution_basis": None,
            "auto_resolution_reason": "missing_matched_external_order_identity",
        }

    if sequencing_status != SEQUENCING_METADATA_PRESENT or event.sequence_id is None:
        return {
            "auto_resolution_status": AUTO_RESOLUTION_BLOCKED,
            "auto_resolution_basis": None,
            "auto_resolution_reason": "missing_broker_sequence_identity",
        }

    if local_order is None:
        return {
            "auto_resolution_status": AUTO_RESOLUTION_BLOCKED,
            "auto_resolution_basis": None,
            "auto_resolution_reason": "local_order_not_loaded",
        }

    if local_order.status != OrderStatus.SUBMITTED or local_order.filled_quantity != 0:
        return {
            "auto_resolution_status": AUTO_RESOLUTION_BLOCKED,
            "auto_resolution_basis": None,
            "auto_resolution_reason": "local_order_not_simple_submitted_state",
        }

    if event.event_type not in {"cancel", "reject"}:
        return {
            "auto_resolution_status": AUTO_RESOLUTION_BLOCKED,
            "auto_resolution_basis": None,
            "auto_resolution_reason": "event_type_not_auto_resolvable",
        }

    return {
        "auto_resolution_status": AUTO_RESOLUTION_APPLIED,
        "auto_resolution_basis": "matched_external_order_id+sequence_id",
        "auto_resolution_reason": "explicit_broker_terminal_fact_authorizes_bounded_local_resolution",
    }


def has_quantity_or_fill_divergence(local_order: Optional[Order], event: BrokerLifecycleEvent) -> bool:
    if local_order is None or event.event_type != "execution":
        return False

    return event.filled_quantity is not None and event.filled_quantity > local_order.quantity


def required_evidence_for_divergence(divergence_category: str) -> str:
    if divergence_category == AWAITING_BROKER_ACKNOWLEDGEMENT_DIVERGENCE:
        return "broker_acknowledgement_or_terminal_fact"
    if divergence_category == UNMATCHED_EXTERNAL_ORDER_DIVERGENCE:
        return "external_order_identity_and_manual_match"
    if divergence_category == LOCALLY_TERMINAL_EXTERNALLY_OPEN_DIVERGENCE:
        return "broker_execution_fact_and_local_terminal_audit"
    if divergence_category == EXTERNALLY_TERMINAL_LOCALLY_OPEN_DIVERGENCE:
        return "broker_terminal_fact_and_local_order_review"
    if divergence_category == SUPPLEMENTAL_CHANNEL_REVIEW_REQUIRED_DIVERGENCE:
        return "operator_confirmation_and_broker_artifact"
    return "broker_fill_fact_and_local_fill_reconciliation"


def evaluate_replay_suppression_policy(
    *,
    event: BrokerLifecycleEvent,
    identity_status: str,
    sequencing_status: str,
) -> Dict[str, Optional[str]]:
    if not _channel_allows_automated_authority(event.broker_channel):
        return {
            "replay_suppression_status": REPLAY_SUPPRESSION_BLOCKED,
            "replay_suppression_basis": None,
            "replay_suppression_reason": "broker_channel_not_replay_authorized",
        }

    if identity_status not in {
        "matched_local_order_id",
        "matched_local_submission_id",
        "matched_external_order_id",
    }:
        return {
            "replay_suppression_status": REPLAY_SUPPRESSION_BLOCKED,
            "replay_suppression_basis": None,
            "replay_suppression_reason": "missing_matched_broker_identity",
        }

    if sequencing_status != SEQUENCING_METADATA_PRESENT:
        return {
            "replay_suppression_status": REPLAY_SUPPRESSION_BLOCKED,
            "replay_suppression_basis": None,
            "replay_suppression_reason": "missing_broker_sequence_identity",
        }

    if event.event_id is not None:
        basis = "event_id"
    elif event.sequence_id is not None:
        basis = "sequence_id"
    else:
        basis = None

    if basis is None:
        return {
            "replay_suppression_status": REPLAY_SUPPRESSION_BLOCKED,
            "replay_suppression_basis": None,
            "replay_suppression_reason": "missing_broker_sequence_identity",
        }

    return {
        "replay_suppression_status": REPLAY_SUPPRESSION_ELIGIBLE,
        "replay_suppression_basis": basis,
        "replay_suppression_reason": "explicit_broker_identity_and_sequence_evidence_present",
    }


def find_duplicate_broker_lifecycle_event(
    *,
    broker_lifecycle_event_store: Any,
    event: BrokerLifecycleEvent,
    order_id: str | None,
    external_order_id: str | None,
) -> Optional[Dict[str, Any]]:
    if not hasattr(broker_lifecycle_event_store, "fetch_recent"):
        return None

    recent_records = broker_lifecycle_event_store.fetch_recent(limit=100)
    for record in recent_records:
        if record.get("event_type") != event.event_type:
            continue
        if event.broker_channel is not None and record.get("broker_channel") != event.broker_channel:
            continue
        if order_id is not None and record.get("order_id") != order_id:
            continue
        if external_order_id is not None and record.get("external_order_id") != external_order_id:
            continue
        if event.event_id is not None and record.get("event_id") == event.event_id:
            return record
        if event.sequence_id is not None and record.get("sequence_id") == event.sequence_id:
            return record

    return None


def evaluate_auto_resolution_policy(
    *,
    event: BrokerLifecycleEvent,
    local_order: Optional[Order],
    divergence_record: Dict[str, Any],
    identity_status: str,
    sequencing_status: str,
) -> Dict[str, Optional[str]]:
    if not _channel_allows_automated_authority(event.broker_channel):
        return {
            "auto_resolution_status": AUTO_RESOLUTION_BLOCKED,
            "auto_resolution_basis": None,
            "auto_resolution_reason": "broker_channel_not_auto_resolution_authorized",
        }

    divergence_category = str(divergence_record["divergence_category"])
    if divergence_category != EXTERNALLY_TERMINAL_LOCALLY_OPEN_DIVERGENCE:
        return {
            "auto_resolution_status": AUTO_RESOLUTION_BLOCKED,
            "auto_resolution_basis": None,
            "auto_resolution_reason": "divergence_category_not_auto_resolvable",
        }

    if identity_status != "matched_external_order_id":
        return {
            "auto_resolution_status": AUTO_RESOLUTION_BLOCKED,
            "auto_resolution_basis": None,
            "auto_resolution_reason": "missing_matched_external_order_identity",
        }

    if sequencing_status != SEQUENCING_METADATA_PRESENT or event.sequence_id is None:
        return {
            "auto_resolution_status": AUTO_RESOLUTION_BLOCKED,
            "auto_resolution_basis": None,
            "auto_resolution_reason": "missing_broker_sequence_identity",
        }

    if local_order is None:
        return {
            "auto_resolution_status": AUTO_RESOLUTION_BLOCKED,
            "auto_resolution_basis": None,
            "auto_resolution_reason": "local_order_not_loaded",
        }

    if local_order.status != OrderStatus.SUBMITTED or local_order.filled_quantity != 0:
        return {
            "auto_resolution_status": AUTO_RESOLUTION_BLOCKED,
            "auto_resolution_basis": None,
            "auto_resolution_reason": "local_order_not_simple_submitted_state",
        }

    if event.event_type not in {"cancel", "reject"}:
        return {
            "auto_resolution_status": AUTO_RESOLUTION_BLOCKED,
            "auto_resolution_basis": None,
            "auto_resolution_reason": "event_type_not_auto_resolvable",
        }

    return {
        "auto_resolution_status": AUTO_RESOLUTION_APPLIED,
        "auto_resolution_basis": "matched_external_order_id+sequence_id",
        "auto_resolution_reason": "explicit_broker_terminal_fact_authorizes_bounded_local_resolution",
    }
