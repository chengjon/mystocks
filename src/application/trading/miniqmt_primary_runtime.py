"""
Canonical repo-facing runtime contract for the miniQMT primary broker path.
"""

from __future__ import annotations

import asyncio
from typing import Any, Mapping, Protocol, runtime_checkable

from src.application.dto.trading_dto import CreateOrderRequest
from src.application.trading.broker_order_correlation import MINIQMT_BROKER_CHANNEL
from src.domain.trading.model.order import Order

MINIQMT_PRIMARY_RUNTIME_ADAPTER_PATH = "web.backend.app.services.windows_bridge_adapter.qmt.submit"
MINIQMT_PRIMARY_RUNTIME_SOURCE_NAME = "miniqmt/windows_bridge"
BRIDGE_TASK_ACCEPTED = "bridge_task_accepted"
BROKER_ACKNOWLEDGED_SUBMISSION = "broker_acknowledged"
SUBMISSION_FAILED = "submission_failed"


@runtime_checkable
class MiniQMTSubmissionTransport(Protocol):
    def submit_order(self, payload: Mapping[str, Any]) -> Mapping[str, Any]:
        """Submit a normalized order payload to the primary miniQMT path."""


class WindowsBridgeMiniQMTTransport:
    """
    Sync facade over the existing async Windows bridge adapter.

    This keeps `OrderManagementService` synchronous while preserving a thin transport-only
    boundary around the generic bridge client.
    """

    def __init__(self, bridge_adapter: Any, *, endpoint: str = "qmt/submit_order") -> None:
        self.bridge_adapter = bridge_adapter
        self.endpoint = endpoint

    def submit_order(self, payload: Mapping[str, Any]) -> Mapping[str, Any]:
        coroutine = self.bridge_adapter.get_data(self.endpoint, params=dict(payload))
        return _run_async_submission(coroutine)


class MiniQMTPrimaryBrokerRuntime:
    def __init__(
        self,
        transport: MiniQMTSubmissionTransport,
        *,
        adapter_path: str = MINIQMT_PRIMARY_RUNTIME_ADAPTER_PATH,
        account_scope: str = "unscoped",
        source_name: str = MINIQMT_PRIMARY_RUNTIME_SOURCE_NAME,
    ) -> None:
        self.transport = transport
        self.adapter_path = adapter_path
        self.account_scope = account_scope
        self.source_name = source_name

    def describe_submission(
        self,
        *,
        request: CreateOrderRequest,
        local_submission_id: str,
    ) -> dict[str, Any]:
        return {
            "local_submission_id": local_submission_id,
            "broker_channel": MINIQMT_BROKER_CHANNEL,
            "adapter_path": self.adapter_path,
            "account_scope": self.account_scope,
            "session_scope": request.request_id,
            "source_name": self.source_name,
        }

    def submit_order(
        self,
        *,
        order: Order,
        request: CreateOrderRequest,
        local_submission_id: str,
    ) -> dict[str, Any]:
        context = self.describe_submission(request=request, local_submission_id=local_submission_id)
        payload = build_miniqmt_submission_payload(
            order=order,
            request=request,
            local_submission_id=local_submission_id,
        )

        try:
            raw_result = dict(self.transport.submit_order(payload))
        except Exception as exc:
            return build_miniqmt_submission_result(
                order_id=order.id.value,
                context=context,
                raw_result={"status": "error", "error_message": str(exc)},
            )

        return build_miniqmt_submission_result(
            order_id=order.id.value,
            context=context,
            raw_result=raw_result,
        )


def build_miniqmt_submission_payload(
    *,
    order: Order,
    request: CreateOrderRequest,
    local_submission_id: str,
) -> dict[str, Any]:
    return {
        "order_id": order.id.value,
        "client_order_id": local_submission_id,
        "symbol": order.symbol,
        "quantity": order.quantity,
        "side": order.side.value,
        "order_type": order.order_type.value,
        "price": order.price,
        "request_id": request.request_id,
        "portfolio_id": request.portfolio_id,
        "strategy_id": request.strategy_id,
        "actor_id": request.actor_id,
        "source_id": request.source_id,
    }


def build_miniqmt_submission_result(
    *,
    order_id: str,
    context: Mapping[str, Any],
    raw_result: Mapping[str, Any],
) -> dict[str, Any]:
    external_order_id = _extract_str(raw_result, "external_order_id", "broker_order_id", "entrust_no", "order_sys_id")
    bridge_task_id = _extract_str(raw_result, "bridge_task_id", "task_id", "receipt_id")
    transport_status = _extract_str(raw_result, "status", "transport_status")
    reason_code = _extract_str(raw_result, "reason_code", "error_code", "status_code")
    reason_detail = _extract_str(raw_result, "reason_detail", "error_message", "message", "reason")
    failure_class = _extract_str(raw_result, "failure_class", "failure_reason")
    bridge_contract_version = _extract_str(raw_result, "bridge_contract_version", "contract_version")
    failure_reason = reason_detail or reason_code

    if external_order_id is not None:
        submission_status = BROKER_ACKNOWLEDGED_SUBMISSION
    elif _is_explicit_failure(
        transport_status=transport_status,
        reason_code=reason_code,
        reason_detail=reason_detail,
        failure_class=failure_class,
    ):
        submission_status = SUBMISSION_FAILED
    elif _is_success_like_status(transport_status) or bridge_task_id is not None:
        submission_status = BRIDGE_TASK_ACCEPTED
    else:
        submission_status = SUBMISSION_FAILED

    if submission_status != SUBMISSION_FAILED:
        failure_reason = None

    return {
        "order_id": order_id,
        "local_submission_id": context["local_submission_id"],
        "broker_channel": context["broker_channel"],
        "adapter_path": context["adapter_path"],
        "account_scope": context["account_scope"],
        "session_scope": context["session_scope"],
        "submission_status": submission_status,
        "transport_status": transport_status,
        "bridge_task_id": bridge_task_id,
        "external_order_id": external_order_id,
        "source_name": context.get("source_name") or MINIQMT_PRIMARY_RUNTIME_SOURCE_NAME,
        "failure_reason": failure_reason,
        "reason_code": reason_code,
        "reason_detail": reason_detail,
        "failure_class": failure_class,
        "bridge_contract_version": bridge_contract_version,
        "handoff_status": None,
        "handoff_reason": None,
        "raw_response": dict(raw_result),
    }


def _extract_str(payload: Mapping[str, Any], *keys: str) -> str | None:
    for key in keys:
        value = payload.get(key)
        if value is None:
            continue
        normalized = str(value).strip()
        if normalized:
            return normalized
    return None


def _is_success_like_status(status: str | None) -> bool:
    if status is None:
        return False
    normalized = status.strip().lower().replace("-", "_").replace(" ", "_")
    return normalized in {"success", "accepted", "queued", "submitted", "ok"}


def _is_explicit_failure(
    *,
    transport_status: str | None,
    reason_code: str | None,
    reason_detail: str | None,
    failure_class: str | None,
) -> bool:
    normalized_status = transport_status.strip().lower().replace("-", "_").replace(" ", "_") if transport_status else None
    if normalized_status in {"error", "failed", "invalid", "forbidden", "unauthorized", "rejected"}:
        return True
    if reason_code or reason_detail or failure_class:
        return True
    return False


def _run_async_submission(coroutine: Any) -> Mapping[str, Any]:
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coroutine)

    raise RuntimeError(
        "WindowsBridgeMiniQMTTransport cannot synchronously submit while an event loop is already running"
    )
