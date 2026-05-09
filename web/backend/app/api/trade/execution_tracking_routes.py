from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Literal, TypeVar
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.core.responses import ErrorCodes, UnifiedResponse, create_error_response, create_unified_success_response
from app.services.trade.execution_tracking_evidence import ExecutionTrackingEvidenceService
from app.services.statement_reconciliation.internal_statement_source import query_internal_statements
from src.application.trading.broker_divergence import build_default_trading_broker_divergence_store
from src.application.trading.broker_submission_attempt import build_default_trading_broker_submission_attempt_store

router = APIRouter(prefix="/execution-tracking", tags=["trade-execution-tracking"])
ResponsePayloadT = TypeVar("ResponsePayloadT", bound=BaseModel)
ExecutionChannel = Literal["miniqmt", "tdxquant", "external"]
SubmissionStatus = Literal["bridge_task_accepted", "broker_acknowledged", "submission_failed"]
BrokerState = Literal["review_required", "broker_acknowledged"]

_EXECUTION_TRIGGERS: dict[str, dict[str, Any]] = {}


class ExecutionBridgeEvidence(BaseModel):
    bridge_task_id: str | None = Field(description="External bridge task identity when available")
    receipt_status: str | None = Field(description="Bridge submission receipt status")
    result_status: str | None = Field(description="Bridge task result status, not broker truth by itself")
    source_name: str | None = Field(description="Bridge or adapter evidence source")


class ExecutionBrokerCorrelation(BaseModel):
    external_order_id: str | None = Field(description="Broker lifecycle identity when available")
    broker_event_type: str | None = Field(description="Broker lifecycle event type when available")
    identity_status: str = Field(description="Correlation identity quality")


class ExecutionTrackingItem(BaseModel):
    tracking_id: str = Field(description="Execution tracking identity")
    account_id: str = Field(description="Account scope used by the external trigger")
    order_id: str = Field(description="Internal order or statement order identity")
    symbol: str = Field(description="Security symbol")
    direction: str = Field(description="Trade direction")
    quantity: int = Field(description="Requested or internal quantity")
    price: Decimal = Field(description="Requested or internal price")
    requested_at: str = Field(description="External trigger or internal statement timestamp")
    channel: ExecutionChannel = Field(description="External execution channel")
    submission_status: SubmissionStatus = Field(description="External submission state")
    broker_state: BrokerState = Field(description="Broker truth state")
    reconciliation_status: str = Field(description="Read-only reconciliation status")
    bridge_evidence: ExecutionBridgeEvidence = Field(description="Bridge evidence attached to this chain")
    broker_correlation: ExecutionBrokerCorrelation = Field(description="Broker correlation evidence")


class ExecutionTrackingSummary(BaseModel):
    total_count: int
    bridge_accepted_count: int
    broker_acknowledged_count: int
    review_required_count: int
    reconciled_count: int


class ExecutionTrackingListPayload(BaseModel):
    status: str
    endpoint: str
    resource: str
    items: list[ExecutionTrackingItem]
    summary: ExecutionTrackingSummary
    total_count: int
    page: int
    page_size: int


class ExecutionEvidenceEvent(BaseModel):
    event_type: str
    occurred_at: str
    summary: str
    evidence: dict[str, Any]


class ExecutionTrackingDetailPayload(BaseModel):
    status: str
    endpoint: str
    resource: str
    item: ExecutionTrackingItem
    evidence_timeline: list[ExecutionEvidenceEvent]


class ExecutionTriggerRequest(BaseModel):
    account_id: str = Field(default="backtest:7")
    channel: ExecutionChannel = Field(default="miniqmt")
    symbol: str = Field(min_length=1)
    direction: Literal["buy", "sell"]
    quantity: int = Field(gt=0)
    price: Decimal = Field(gt=Decimal("0"))
    requested_by: str | None = None
    client_request_id: str | None = None


class ExecutionTriggerPayload(BaseModel):
    status: str
    endpoint: str
    resource: str
    tracking_id: str
    accepted: bool
    channel: ExecutionChannel
    submission_status: SubmissionStatus
    broker_state: BrokerState
    bridge_receipt: ExecutionBridgeEvidence


def _success_execution_response(
    message: str,
    data_model: ResponsePayloadT,
) -> UnifiedResponse[ResponsePayloadT]:
    return create_unified_success_response(data=data_model, message=message)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _as_decimal(value: Any, fallback: str = "0") -> Decimal:
    if value is None or value == "":
        return Decimal(fallback)
    return Decimal(str(value))


def _as_int(value: Any, fallback: int = 0) -> int:
    if value is None or value == "":
        return fallback
    return int(value)


def _broker_state_for(record: dict[str, Any]) -> BrokerState:
    if record.get("broker_state") in {"review_required", "broker_acknowledged"}:
        return record["broker_state"]
    if record.get("external_order_id") and record.get("broker_event_type"):
        return "broker_acknowledged"
    return "review_required"


def _tracking_id_for(payload: dict[str, Any]) -> str:
    existing = str(payload.get("tracking_id") or "").strip()
    return existing or f"track-{uuid4().hex[:12]}"


def record_execution_trigger(payload: dict[str, Any]) -> dict[str, Any]:
    requested_at = str(payload.get("requested_at") or _utc_now_iso())
    tracking_id = _tracking_id_for(payload)
    order_id = str(payload.get("order_id") or f"external-{tracking_id}")
    bridge_task_id = payload.get("bridge_task_id") or payload.get("task_id")

    record = {
        "tracking_id": tracking_id,
        "account_id": str(payload.get("account_id") or "backtest:7"),
        "order_id": order_id,
        "symbol": str(payload.get("symbol") or ""),
        "direction": str(payload.get("direction") or "buy"),
        "quantity": _as_int(payload.get("quantity")),
        "price": _as_decimal(payload.get("price")),
        "requested_at": requested_at,
        "channel": str(payload.get("channel") or "miniqmt"),
        "submission_status": str(payload.get("submission_status") or "bridge_task_accepted"),
        "bridge_task_id": str(bridge_task_id) if bridge_task_id else None,
        "receipt_status": str(payload.get("receipt_status") or payload.get("transport_status") or "accepted"),
        "bridge_result_status": (
            str(payload.get("bridge_result_status") or payload.get("result_status"))
            if payload.get("bridge_result_status") or payload.get("result_status")
            else None
        ),
        "source_name": str(payload.get("source_name") or "miniqmt/windows_bridge"),
        "external_order_id": str(payload.get("external_order_id")) if payload.get("external_order_id") else None,
        "broker_event_type": str(payload.get("broker_event_type")) if payload.get("broker_event_type") else None,
        "requested_by": str(payload.get("requested_by")) if payload.get("requested_by") else None,
        "client_request_id": str(payload.get("client_request_id")) if payload.get("client_request_id") else None,
    }
    _EXECUTION_TRIGGERS[tracking_id] = record
    return dict(record)


def _build_tracking_item(record: dict[str, Any]) -> ExecutionTrackingItem:
    broker_state = _broker_state_for(record)
    return ExecutionTrackingItem(
        tracking_id=str(record["tracking_id"]),
        account_id=str(record["account_id"]),
        order_id=str(record["order_id"]),
        symbol=str(record["symbol"]),
        direction=str(record["direction"]),
        quantity=_as_int(record.get("quantity")),
        price=_as_decimal(record.get("price")),
        requested_at=str(record["requested_at"]),
        channel=record.get("channel") if record.get("channel") in {"miniqmt", "tdxquant", "external"} else "external",
        submission_status=(
            record.get("submission_status")
            if record.get("submission_status") in {"bridge_task_accepted", "broker_acknowledged", "submission_failed"}
            else "submission_failed"
        ),
        broker_state=broker_state,
        reconciliation_status=str(record.get("reconciliation_status") or "not_imported"),
        bridge_evidence=ExecutionBridgeEvidence(
            bridge_task_id=record.get("bridge_task_id"),
            receipt_status=record.get("receipt_status"),
            result_status=record.get("bridge_result_status"),
            source_name=record.get("source_name"),
        ),
        broker_correlation=ExecutionBrokerCorrelation(
            external_order_id=record.get("external_order_id"),
            broker_event_type=record.get("broker_event_type"),
            identity_status=str(
                record.get("identity_status")
                or ("matched_broker_identity" if broker_state == "broker_acknowledged" else "missing_broker_identity")
            ),
        ),
    )


def get_execution_tracking_evidence_service() -> ExecutionTrackingEvidenceService:
    return ExecutionTrackingEvidenceService(
        submission_attempt_store=build_default_trading_broker_submission_attempt_store(),
        divergence_store=build_default_trading_broker_divergence_store(),
        session_trigger_records=_EXECUTION_TRIGGERS,
    )


def _internal_statement_to_record(row: dict[str, Any], account_id: str) -> dict[str, Any]:
    order_id = str(row.get("order_id") or row.get("trade_id") or f"internal-{uuid4().hex[:8]}")
    matching_trigger = next(
        (
            record
            for record in _EXECUTION_TRIGGERS.values()
            if record.get("account_id") == account_id and record.get("order_id") == order_id
        ),
        None,
    )
    if matching_trigger:
        return {**matching_trigger, **{key: matching_trigger.get(key) for key in matching_trigger}}

    return {
        "tracking_id": f"internal-{order_id}",
        "account_id": account_id,
        "order_id": order_id,
        "symbol": str(row.get("symbol") or ""),
        "direction": str(row.get("direction") or ""),
        "quantity": _as_int(row.get("quantity")),
        "price": _as_decimal(row.get("price")),
        "requested_at": str(row.get("trade_time") or _utc_now_iso()),
        "channel": "external",
        "submission_status": "submission_failed",
        "bridge_task_id": None,
        "receipt_status": None,
        "bridge_result_status": None,
        "source_name": None,
        "external_order_id": None,
        "broker_event_type": None,
    }


def _load_execution_records(
    *,
    account_id: str,
    order_id: str | None,
    bridge_task_id: str | None,
    page: int,
    page_size: int,
) -> list[dict[str, Any]]:
    try:
        internal_payload = query_internal_statements(
            account_id=account_id,
            start_date=None,
            end_date=None,
            page=page,
            page_size=page_size,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=create_error_response(
                error_code=ErrorCodes.VALIDATION_ERROR,
                message=str(exc),
            ).model_dump(mode="json"),
        ) from exc

    records = [_internal_statement_to_record(dict(row), account_id) for row in internal_payload.get("items", [])]
    known_ids = {record["tracking_id"] for record in records}
    records.extend(
        record
        for record in _EXECUTION_TRIGGERS.values()
        if record.get("account_id") == account_id and record.get("tracking_id") not in known_ids
    )
    records.extend(
        record
        for record in get_execution_tracking_evidence_service().load_records(
            account_id=account_id,
            order_id=order_id,
            bridge_task_id=bridge_task_id,
            page=page,
            page_size=page_size,
        )
        if record.get("tracking_id") not in known_ids
    )

    if order_id:
        records = [record for record in records if record.get("order_id") == order_id]
    if bridge_task_id:
        records = [record for record in records if record.get("bridge_task_id") == bridge_task_id]

    return records


def _build_summary(items: list[ExecutionTrackingItem]) -> ExecutionTrackingSummary:
    return ExecutionTrackingSummary(
        total_count=len(items),
        bridge_accepted_count=sum(1 for item in items if item.submission_status == "bridge_task_accepted"),
        broker_acknowledged_count=sum(1 for item in items if item.broker_state == "broker_acknowledged"),
        review_required_count=sum(1 for item in items if item.broker_state == "review_required"),
        reconciled_count=sum(1 for item in items if item.reconciliation_status == "matched"),
    )


def _build_timeline(record: dict[str, Any]) -> list[ExecutionEvidenceEvent]:
    timeline = [
        ExecutionEvidenceEvent(
            event_type="external_trigger_request",
            occurred_at=str(record["requested_at"]),
            summary="外部触发请求已记录，真实下单由外部程序处理",
            evidence={
                "account_id": record.get("account_id"),
                "order_id": record.get("order_id"),
                "requested_by": record.get("requested_by"),
                "client_request_id": record.get("client_request_id"),
            },
        )
    ]
    if record.get("bridge_task_id"):
        timeline.append(
            ExecutionEvidenceEvent(
                event_type="bridge_submission_receipt",
                occurred_at=str(record["requested_at"]),
                summary="miniQMT bridge 接收任务回执，不等于券商确认",
                evidence={
                    "bridge_task_id": record.get("bridge_task_id"),
                    "receipt_status": record.get("receipt_status"),
                    "source_name": record.get("source_name"),
                },
            )
        )
    if record.get("bridge_result_status"):
        timeline.append(
            ExecutionEvidenceEvent(
                event_type="bridge_task_terminal_result",
                occurred_at=str(record["requested_at"]),
                summary="bridge 任务已返回终态，但缺少 broker lifecycle identity 时仍需复核",
                evidence={
                    "bridge_task_id": record.get("bridge_task_id"),
                    "result_status": record.get("bridge_result_status"),
                    "external_order_id": record.get("external_order_id"),
                },
            )
        )
    return timeline


@router.get("", response_model=UnifiedResponse[ExecutionTrackingListPayload])
async def get_execution_tracking(
    account_id: str = Query("backtest:7", description="Execution tracking account scope"),
    order_id: str | None = Query(None, description="Internal order id filter"),
    bridge_task_id: str | None = Query(None, description="miniQMT bridge task id filter"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
) -> UnifiedResponse[ExecutionTrackingListPayload]:
    records = _load_execution_records(
        account_id=account_id,
        order_id=order_id,
        bridge_task_id=bridge_task_id,
        page=page,
        page_size=page_size,
    )
    items = [_build_tracking_item(record) for record in records]
    payload = ExecutionTrackingListPayload(
        status="available",
        endpoint="trade",
        resource="execution_tracking",
        items=items,
        summary=_build_summary(items),
        total_count=len(items),
        page=page,
        page_size=page_size,
    )
    return _success_execution_response("Execution tracking loaded", payload)


@router.post("/trigger", response_model=UnifiedResponse[ExecutionTriggerPayload])
async def trigger_external_execution(
    request: ExecutionTriggerRequest,
) -> UnifiedResponse[ExecutionTriggerPayload]:
    now = _utc_now_iso()
    task_id = f"miniqmt-task-{uuid4().hex[:12]}"
    record = record_execution_trigger(
        {
            "account_id": request.account_id,
            "channel": request.channel,
            "symbol": request.symbol.strip(),
            "direction": request.direction,
            "quantity": request.quantity,
            "price": request.price,
            "requested_at": now,
            "requested_by": request.requested_by,
            "client_request_id": request.client_request_id,
            "bridge_task_id": task_id,
            "receipt_status": "accepted",
            "submission_status": "bridge_task_accepted",
        }
    )
    bridge_receipt = ExecutionBridgeEvidence(
        bridge_task_id=record["bridge_task_id"],
        receipt_status=record["receipt_status"],
        result_status=None,
        source_name=record["source_name"],
    )
    payload = ExecutionTriggerPayload(
        status="available",
        endpoint="trade",
        resource="execution_trigger",
        tracking_id=record["tracking_id"],
        accepted=True,
        channel=request.channel,
        submission_status="bridge_task_accepted",
        broker_state="review_required",
        bridge_receipt=bridge_receipt,
    )
    return _success_execution_response("External execution trigger recorded", payload)


@router.get("/{tracking_id}", response_model=UnifiedResponse[ExecutionTrackingDetailPayload])
async def get_execution_tracking_detail(
    tracking_id: str,
) -> UnifiedResponse[ExecutionTrackingDetailPayload]:
    evidence_service = get_execution_tracking_evidence_service()
    record = evidence_service.load_record_by_tracking_id(tracking_id) or _EXECUTION_TRIGGERS.get(tracking_id)
    if record is None:
        raise HTTPException(
            status_code=404,
            detail=create_error_response(
                error_code=ErrorCodes.NOT_FOUND,
                message=f"unknown execution tracking id: {tracking_id}",
            ).model_dump(mode="json"),
        )

    payload = ExecutionTrackingDetailPayload(
        status="available",
        endpoint="trade",
        resource="execution_tracking_detail",
        item=_build_tracking_item(record),
        evidence_timeline=[
            ExecutionEvidenceEvent(**event) for event in evidence_service.build_timeline(record)
        ],
    )
    return _success_execution_response("Execution tracking detail loaded", payload)
