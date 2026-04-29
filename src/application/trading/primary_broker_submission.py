"""
Helpers for canonical primary broker submission handoff.
"""

from __future__ import annotations

from typing import Any, Callable, Dict

from src.application.dto.trading_dto import CreateOrderRequest
from src.application.trading.broker_order_correlation import LOCAL_ANCHOR_BROKER_CHANNEL
from src.application.trading.broker_reconciliation import AWAITING_BROKER_ACKNOWLEDGEMENT, BROKER_ACKNOWLEDGED
from src.application.trading.miniqmt_primary_runtime import (
    BRIDGE_TASK_ACCEPTED,
    BROKER_ACKNOWLEDGED_SUBMISSION,
    SUBMISSION_FAILED,
)
from src.domain.trading.model.order import Order

LOCAL_ORDER_SUBMISSION_ADAPTER_PATH = "src.application.trading.order_mgmt_service.OrderManagementService.place_order"


def resolve_local_submission_id(order: Order, request: CreateOrderRequest) -> str:
    return request.idempotency_key or request.request_id or order.id.value


def persist_primary_broker_correlation(
    *,
    broker_correlation_store: Any,
    primary_broker_runtime: Any,
    order: Order,
    request: CreateOrderRequest,
    local_submission_id: str,
) -> None:
    broker_channel = LOCAL_ANCHOR_BROKER_CHANNEL
    adapter_path = LOCAL_ORDER_SUBMISSION_ADAPTER_PATH
    account_scope = "unscoped"
    session_scope = request.request_id

    if primary_broker_runtime is not None:
        submission_context = primary_broker_runtime.describe_submission(
            request=request,
            local_submission_id=local_submission_id,
        )
        broker_channel = str(submission_context["broker_channel"])
        adapter_path = str(submission_context["adapter_path"])
        account_scope = str(submission_context["account_scope"])
        session_scope = submission_context.get("session_scope")

    broker_correlation_store.upsert_submission(
        order_id=order.id.value,
        local_submission_id=local_submission_id,
        broker_channel=broker_channel,
        adapter_path=adapter_path,
        account_scope=account_scope,
        session_scope=session_scope,
        acknowledgement_status=AWAITING_BROKER_ACKNOWLEDGEMENT,
    )


def process_primary_broker_submission(
    *,
    primary_broker_runtime: Any,
    broker_submission_attempt_store: Any,
    broker_correlation_store: Any,
    order: Order,
    request: CreateOrderRequest,
    local_submission_id: str,
    emit_existing_order_audit: Callable[..., None],
) -> None:
    if primary_broker_runtime is None:
        return

    submission_result = primary_broker_runtime.submit_order(
        order=order,
        request=request,
        local_submission_id=local_submission_id,
    )
    broker_submission_attempt_store.append(submission_result)

    submission_status = submission_result["submission_status"]
    if submission_status == BROKER_ACKNOWLEDGED_SUBMISSION and submission_result.get("external_order_id"):
        broker_correlation_store.bind_external_order_id(
            order_id=order.id.value,
            external_order_id=str(submission_result["external_order_id"]),
            acknowledgement_status=BROKER_ACKNOWLEDGED,
        )
        emit_existing_order_audit(
            decision_outcome="broker_primary_acknowledged_immediately",
            order=order,
            actor_id=request.actor_id,
            source_id=submission_result.get("source_name"),
            reason="primary_broker_acknowledged_on_submit",
            extra_payload={
                "broker_channel": submission_result["broker_channel"],
                "broker_submission_status": submission_status,
                "broker_external_order_id": submission_result["external_order_id"],
                "bridge_task_id": submission_result.get("bridge_task_id"),
                "bridge_contract_version": submission_result.get("bridge_contract_version"),
            },
        )
        return

    if submission_status == BRIDGE_TASK_ACCEPTED:
        emit_existing_order_audit(
            decision_outcome="broker_primary_submission_queued",
            order=order,
            actor_id=request.actor_id,
            source_id=submission_result.get("source_name"),
            reason="bridge_task_accepted_awaiting_broker_acknowledgement",
            extra_payload={
                "broker_channel": submission_result["broker_channel"],
                "broker_submission_status": submission_status,
                "bridge_task_id": submission_result.get("bridge_task_id"),
                "bridge_contract_version": submission_result.get("bridge_contract_version"),
            },
        )
        return

    if submission_status == SUBMISSION_FAILED:
        emit_existing_order_audit(
            decision_outcome="broker_primary_submission_failed",
            order=order,
            actor_id=request.actor_id,
            source_id=submission_result.get("source_name"),
            reason=str(submission_result.get("failure_reason") or "primary_broker_submission_failed"),
            extra_payload={
                "broker_channel": submission_result["broker_channel"],
                "broker_submission_status": submission_status,
                "bridge_task_id": submission_result.get("bridge_task_id"),
                "reason_code": submission_result.get("reason_code"),
                "reason_detail": submission_result.get("reason_detail"),
                "failure_class": submission_result.get("failure_class"),
                "bridge_contract_version": submission_result.get("bridge_contract_version"),
            },
        )
