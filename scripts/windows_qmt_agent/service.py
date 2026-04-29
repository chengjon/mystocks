from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from threading import Lock
from typing import Any, Mapping, Protocol
from uuid import uuid4

from .config import (
    PROVIDER_MODE_MINIQMT_SDK,
    PROVIDER_MODE_MOCK,
    WindowsQmtAgentSettings,
)
from .models import ExecuteTaskRequest

QMT_PROVIDER = "qmt"
QMT_SUBMIT_ORDER_METHOD = "submit_order"
BRIDGE_CONTRACT_VERSION_HEADER = "X-Bridge-Contract-Version"
BRIDGE_AUTH_SCHEME = "Bearer"

LIVE_BRIDGE_AUTH_FAILED = "live_bridge_auth_failed"
LIVE_BRIDGE_UNSUPPORTED_CONTRACT_VERSION = "live_bridge_unsupported_contract_version"
LIVE_BRIDGE_UNSUPPORTED_METHOD = "live_bridge_unsupported_method"
LIVE_BRIDGE_UNAVAILABLE = "live_bridge_unavailable"

HTTP_ACCEPTED = 202
HTTP_AUTH_FAILED = 401
HTTP_UNSUPPORTED_CONTRACT_VERSION = 409
HTTP_UNSUPPORTED_METHOD = 405
HTTP_PROVIDER_UNAVAILABLE = 503


@dataclass(slots=True)
class ProviderTaskPlan:
    available_at: datetime
    terminal_http_status: int
    terminal_result_status: str
    result_payload: dict[str, Any] | None = None
    reason_code: str | None = None
    reason_detail: str | None = None


@dataclass(slots=True)
class TaskRecord:
    task_id: str
    provider: str
    method: str
    provider_mode: str
    receipt_timestamp: datetime
    bridge_contract_version: str
    source_name: str
    plan: ProviderTaskPlan


class ReferenceProvider(Protocol):
    mode: str

    def build_task_plan(
        self,
        *,
        task_id: str,
        request: ExecuteTaskRequest,
        settings: WindowsQmtAgentSettings,
        now: datetime,
    ) -> ProviderTaskPlan:
        ...


class InMemoryTaskRegistry:
    def __init__(self) -> None:
        self._records: dict[str, TaskRecord] = {}
        self._lock = Lock()

    def put(self, record: TaskRecord) -> None:
        with self._lock:
            self._records[record.task_id] = record

    def get(self, task_id: str) -> TaskRecord | None:
        with self._lock:
            return self._records.get(task_id)


class MockReferenceProvider:
    mode = PROVIDER_MODE_MOCK

    def build_task_plan(
        self,
        *,
        task_id: str,
        request: ExecuteTaskRequest,
        settings: WindowsQmtAgentSettings,
        now: datetime,
    ) -> ProviderTaskPlan:
        params = request.params
        delay_seconds = _float_param(
            params,
            "mock_delay_seconds",
            default=settings.default_pending_delay_seconds,
        )
        available_at = now + timedelta(seconds=max(delay_seconds, 0.0))
        outcome = _normalize_choice(params.get("mock_outcome")) or "acknowledgement"
        account_scope = _string_param(params, "account_scope", default=settings.default_account_scope)
        local_submission_id = (
            _string_param(params, "local_submission_id")
            or _string_param(params, "client_order_id")
            or f"submission-{task_id}"
        )

        if outcome in {"provider_failure", "unavailable"}:
            return ProviderTaskPlan(
                available_at=available_at,
                terminal_http_status=HTTP_PROVIDER_UNAVAILABLE,
                terminal_result_status="failed",
                reason_code=LIVE_BRIDGE_UNAVAILABLE,
                reason_detail="mock provider is configured to emulate an unavailable miniQMT endpoint",
            )

        result_payload = {
            "client_order_id": _string_param(params, "client_order_id", default=local_submission_id),
            "local_submission_id": local_submission_id,
            "account_scope": account_scope,
            "symbol": _string_param(params, "symbol", default="000001"),
            "side": _string_param(params, "side", default="BUY"),
            "order_type": _string_param(params, "order_type", default="LIMIT"),
            "event_id": _string_param(params, "event_id", default=f"mock-event-{task_id}"),
            "source_name": settings.source_name,
            "provider_mode": self.mode,
        }

        if outcome in {"execution", "filled"}:
            result_payload.update(
                {
                    "status": "filled",
                    "broker_event_type": "execution",
                    "external_order_id": _string_param(params, "external_order_id", default=f"mock-order-{task_id}"),
                    "sequence_id": _string_param(params, "sequence_id", default=f"mock-seq-{task_id}"),
                    "filled_quantity": int(params.get("quantity", 100) or 100),
                    "fill_price": float(params.get("price", 10.5) or 10.5),
                }
            )
            return ProviderTaskPlan(
                available_at=available_at,
                terminal_http_status=200,
                terminal_result_status="completed",
                result_payload=result_payload,
            )

        if outcome in {"reject", "rejected"}:
            result_payload.update(
                {
                    "status": "rejected",
                    "broker_event_type": "reject",
                    "reason_code": _string_param(params, "reason_code", default="mock_reject"),
                    "reason_detail": _string_param(
                        params,
                        "reason_detail",
                        default="mock provider rejected the order",
                    ),
                }
            )
            return ProviderTaskPlan(
                available_at=available_at,
                terminal_http_status=200,
                terminal_result_status="rejected",
                result_payload=result_payload,
            )

        if outcome in {"cancel", "cancelled"}:
            result_payload.update(
                {
                    "status": "cancelled",
                    "broker_event_type": "cancel",
                    "external_order_id": _string_param(params, "external_order_id", default=f"mock-order-{task_id}"),
                    "sequence_id": _string_param(params, "sequence_id", default=f"mock-seq-{task_id}"),
                }
            )
            return ProviderTaskPlan(
                available_at=available_at,
                terminal_http_status=200,
                terminal_result_status="cancelled",
                result_payload=result_payload,
            )

        result_payload.update(
            {
                "status": "accepted",
                "broker_event_type": "acknowledgement",
                "external_order_id": _string_param(params, "external_order_id", default=f"mock-order-{task_id}"),
                "sequence_id": _string_param(params, "sequence_id", default=f"mock-seq-{task_id}"),
            }
        )
        return ProviderTaskPlan(
            available_at=available_at,
            terminal_http_status=200,
            terminal_result_status="completed",
            result_payload=result_payload,
        )


class MiniQmtSdkReferenceProvider:
    mode = PROVIDER_MODE_MINIQMT_SDK

    def build_task_plan(
        self,
        *,
        task_id: str,
        request: ExecuteTaskRequest,
        settings: WindowsQmtAgentSettings,
        now: datetime,
    ) -> ProviderTaskPlan:
        detail = (
            "miniqmt_sdk provider is not yet configured in this repo-owned Windows qmt reference service"
        )
        if settings.miniqmt_sdk_enabled:
            detail = (
                "miniqmt_sdk mode is enabled but no live miniQMT SDK adapter is implemented in this reference service"
            )
        return ProviderTaskPlan(
            available_at=now,
            terminal_http_status=HTTP_PROVIDER_UNAVAILABLE,
            terminal_result_status="failed",
            reason_code=LIVE_BRIDGE_UNAVAILABLE,
            reason_detail=detail,
        )


class WindowsQmtReferenceService:
    def __init__(
        self,
        settings: WindowsQmtAgentSettings,
        *,
        registry: InMemoryTaskRegistry | None = None,
        task_id_factory: Any | None = None,
        providers: Mapping[str, ReferenceProvider] | None = None,
    ) -> None:
        self.settings = settings
        self.registry = registry or InMemoryTaskRegistry()
        self.task_id_factory = task_id_factory or (lambda: str(uuid4()))
        self.providers = dict(
            providers
            or {
                PROVIDER_MODE_MOCK: MockReferenceProvider(),
                PROVIDER_MODE_MINIQMT_SDK: MiniQmtSdkReferenceProvider(),
            }
        )

    def contract_headers(self) -> dict[str, str]:
        return {BRIDGE_CONTRACT_VERSION_HEADER: self.settings.bridge_contract_version}

    def health_payload(self) -> dict[str, Any]:
        return {
            "status": "online" if self.settings.bridge_token else "degraded",
            "node": self.settings.node_name,
            "provider_mode": self.settings.provider_mode,
            "bridge_contract_version": self.settings.bridge_contract_version,
            "bridge_auth_configured": bool(self.settings.bridge_token),
            "source_name": self.settings.source_name,
            "time": _utc_now().isoformat(),
        }

    def validate_boundary(
        self,
        *,
        authorization: str | None,
        contract_version: str | None,
        provider: str | None = None,
        method: str | None = None,
    ) -> tuple[int, dict[str, Any]] | None:
        if not self.settings.bridge_token:
            return self._error_response(
                status_code=HTTP_PROVIDER_UNAVAILABLE,
                reason_code=LIVE_BRIDGE_UNAVAILABLE,
                reason_detail="Windows qmt reference service bridge token is not configured",
                provider=provider,
                method=method,
            )

        expected_auth = f"{BRIDGE_AUTH_SCHEME} {self.settings.bridge_token}"
        if authorization != expected_auth:
            return self._error_response(
                status_code=HTTP_AUTH_FAILED,
                reason_code=LIVE_BRIDGE_AUTH_FAILED,
                reason_detail="Windows qmt reference service authentication failed",
                provider=provider,
                method=method,
            )

        if contract_version != self.settings.bridge_contract_version:
            return self._error_response(
                status_code=HTTP_UNSUPPORTED_CONTRACT_VERSION,
                reason_code=LIVE_BRIDGE_UNSUPPORTED_CONTRACT_VERSION,
                reason_detail=(
                    f"Windows qmt reference service expects contract version "
                    f"{self.settings.bridge_contract_version}, got {contract_version or '<missing>'}"
                ),
                provider=provider,
                method=method,
            )
        return None

    def validate_execute_target(self, request: ExecuteTaskRequest) -> tuple[int, dict[str, Any]] | None:
        provider = request.provider.strip().lower()
        method = request.method.strip()
        if provider == QMT_PROVIDER and method == QMT_SUBMIT_ORDER_METHOD:
            return None
        return self._error_response(
            status_code=HTTP_UNSUPPORTED_METHOD,
            reason_code=LIVE_BRIDGE_UNSUPPORTED_METHOD,
            reason_detail=f"Unsupported reference-service target: {request.provider}/{request.method}",
            provider=request.provider,
            method=request.method,
        )

    def create_task(self, request: ExecuteTaskRequest) -> tuple[int, dict[str, Any]]:
        now = _utc_now()
        task_id = self.task_id_factory()
        provider = self.providers[self.settings.provider_mode]
        plan = provider.build_task_plan(
            task_id=task_id,
            request=request,
            settings=self.settings,
            now=now,
        )
        record = TaskRecord(
            task_id=task_id,
            provider=QMT_PROVIDER,
            method=QMT_SUBMIT_ORDER_METHOD,
            provider_mode=provider.mode,
            receipt_timestamp=now,
            bridge_contract_version=self.settings.bridge_contract_version,
            source_name=self.settings.source_name,
            plan=plan,
        )
        self.registry.put(record)
        return (
            HTTP_ACCEPTED,
            {
                "task_id": task_id,
                "status": "accepted",
                "timestamp": now.isoformat(),
                "source": QMT_PROVIDER,
                "source_name": self.settings.source_name,
                "bridge_contract_version": self.settings.bridge_contract_version,
                "provider_mode": provider.mode,
            },
        )

    def get_task_result(self, task_id: str) -> tuple[int, dict[str, Any]]:
        record = self.registry.get(task_id)
        if record is None:
            return self._error_response(
                status_code=HTTP_PROVIDER_UNAVAILABLE,
                reason_code=LIVE_BRIDGE_UNAVAILABLE,
                reason_detail=f"Unknown task_id '{task_id}' in Windows qmt reference service",
                provider=QMT_PROVIDER,
                method=QMT_SUBMIT_ORDER_METHOD,
                task_id=task_id,
            )

        now = _utc_now()
        if now < record.plan.available_at:
            return (
                200,
                {
                    "task_id": task_id,
                    "provider": record.provider,
                    "method": record.method,
                    "status": "pending",
                    "result_status": "pending",
                    "bridge_contract_version": record.bridge_contract_version,
                    "provider_mode": record.provider_mode,
                    "source_name": record.source_name,
                },
            )

        if record.plan.terminal_http_status >= 400:
            return self._error_response(
                status_code=record.plan.terminal_http_status,
                reason_code=record.plan.reason_code or LIVE_BRIDGE_UNAVAILABLE,
                reason_detail=record.plan.reason_detail or "Windows qmt reference service provider failed",
                provider=record.provider,
                method=record.method,
                task_id=task_id,
                provider_mode=record.provider_mode,
            )

        result_payload = dict(record.plan.result_payload or {})
        occurred_at = result_payload.get("occurred_at") or result_payload.get("updated_at") or now.isoformat()
        result_payload.setdefault("updated_at", occurred_at)
        result_payload.setdefault("occurred_at", occurred_at)
        result_payload.setdefault("source_name", record.source_name)
        result_payload.setdefault("provider_mode", record.provider_mode)
        result_payload.setdefault("account_scope", self.settings.default_account_scope)

        return (
            200,
            {
                "task_id": task_id,
                "provider": record.provider,
                "method": record.method,
                "status": record.plan.terminal_result_status,
                "result_status": record.plan.terminal_result_status,
                "bridge_contract_version": record.bridge_contract_version,
                "provider_mode": record.provider_mode,
                "source_name": record.source_name,
                "result": result_payload,
            },
        )

    def _error_response(
        self,
        *,
        status_code: int,
        reason_code: str,
        reason_detail: str,
        provider: str | None,
        method: str | None,
        task_id: str | None = None,
        provider_mode: str | None = None,
    ) -> tuple[int, dict[str, Any]]:
        return (
            status_code,
            {
                "status": "error",
                "task_id": task_id,
                "provider": provider or QMT_PROVIDER,
                "method": method or QMT_SUBMIT_ORDER_METHOD,
                "reason_code": reason_code,
                "reason_detail": reason_detail,
                "bridge_contract_version": self.settings.bridge_contract_version,
                "provider_mode": provider_mode or self.settings.provider_mode,
                "source_name": self.settings.source_name,
            },
        )


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _string_param(payload: Mapping[str, Any], key: str, *, default: str | None = None) -> str | None:
    value = payload.get(key)
    if value is None:
        return default
    normalized = str(value).strip()
    return normalized or default


def _float_param(payload: Mapping[str, Any], key: str, *, default: float = 0.0) -> float:
    value = payload.get(key)
    if value in (None, ""):
        return float(default)
    return float(value)


def _normalize_choice(value: Any) -> str | None:
    if value is None:
        return None
    normalized = str(value).strip().lower()
    return normalized or None
