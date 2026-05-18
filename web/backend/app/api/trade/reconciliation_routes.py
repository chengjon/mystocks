from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Literal, TypeVar

from fastapi import APIRouter, File, Form, Query, Response, UploadFile
from app.core.exceptions import BusinessException
from pydantic import BaseModel, Field

from app.core.responses import ErrorCodes, UnifiedResponse, create_error_response, create_unified_success_response
from app.api.trade.reconciliation_models import (
    InternalStatementRow,
    InternalStatementSummary,
    ReconciliationAccountDescriptor,
    ReconciliationAccountsPayload,
    ReconciliationImportBatchPayload,
    ReconciliationStatementsPayload,
)
from app.services.statement_reconciliation.internal_statement_source import (
    list_reconciliation_accounts,
    query_internal_statements,
)
from app.services.statement_reconciliation.export import build_reconciliation_export_csv
from app.services.statement_reconciliation.import_batch_store import create_import_batch, get_import_batch
from app.services.statement_reconciliation.matcher import match_reconciliation_rows
from app.services.statement_reconciliation.parsers.miniqmt import parse_miniqmt_csv
from app.services.statement_reconciliation.parsers.normalized_template import parse_normalized_template_csv

router = APIRouter(prefix="/reconciliation", tags=["trade-reconciliation"])
ResponsePayloadT = TypeVar("ResponsePayloadT", bound=BaseModel)
MatchStatus = Literal["matched", "mismatched", "missing_broker_record"]


class BrokerStatementRow(BaseModel):
    """Broker-side statement row imported for reconciliation."""

    account_id: str = Field(description="Synthetic reconciliation account id")
    trade_id: str = Field(description="Broker trade identifier")
    order_id: str = Field(description="Broker order identifier")
    symbol: str = Field(description="Security symbol")
    direction: str = Field(description="Trade direction")
    trade_time: str = Field(description="Broker trade timestamp")
    price: Decimal = Field(description="Trade price")
    quantity: int = Field(description="Trade quantity")
    amount: Decimal = Field(description="Trade amount")
    commission: Decimal = Field(description="Trade commission")
    source_type: str = Field(description="Imported source type")
    raw_row_number: int = Field(description="Original CSV row number")


class ReconciliationResultItem(BaseModel):
    """Single reconciliation match result between internal truth and broker statement rows."""

    match_status: MatchStatus = Field(description="Deterministic match status")
    internal_row: InternalStatementRow = Field(description="Internal statement row")
    broker_row: BrokerStatementRow | None = Field(description="Matched broker row if available")
    mismatch_fields: list[str] = Field(description="Canonical fields that differ between paired rows")


class ReconciliationResultsPayload(BaseModel):
    """Paginated reconciliation result payload."""

    status: str = Field(description="Availability status")
    endpoint: str = Field(description="Owning endpoint family")
    resource: str = Field(description="Resource identifier")
    account_id: str = Field(description="Selected synthetic reconciliation account")
    import_batch_id: str = Field(description="In-memory import batch identifier")
    items: list[ReconciliationResultItem] = Field(description="Paginated reconciliation results")
    total_count: int = Field(description="Filtered result count")
    page: int = Field(description="Current page number")
    page_size: int = Field(description="Current page size")
    source: str = Field(description="Underlying internal truth source")
    match_status: MatchStatus | None = Field(description="Applied match-status filter")


def _success_reconciliation_response(
    message: str,
    data_model: ResponsePayloadT,
) -> UnifiedResponse[ResponsePayloadT]:
    return create_unified_success_response(data=data_model, message=message)


_ERROR_RESPONSE_EXAMPLE: dict[str, Any] = {
    "success": False,
    "code": 404,
    "message": "Reconciliation resource not found",
    "data": None,
    "request_id": "contract-example",
    "errors": [{"field": "account_id", "code": "NOT_FOUND", "message": "Unknown reconciliation account"}],
}


def _json_response_examples(description: str, data: dict[str, Any]) -> dict[int, dict[str, Any]]:
    success_example = {
        "success": True,
        "code": 200,
        "message": description,
        "data": data,
        "request_id": "contract-example",
        "errors": None,
    }
    return {
        200: {
            "description": description,
            "content": {"application/json": {"example": success_example}},
        },
        404: {
            "description": "Reconciliation resource not found",
            "content": {"application/json": {"example": _ERROR_RESPONSE_EXAMPLE}},
        },
        422: {
            "description": "Invalid reconciliation request",
            "content": {
                "application/json": {
                    "example": {**_ERROR_RESPONSE_EXAMPLE, "code": 422, "message": "Invalid reconciliation request"}
                }
            },
        },
        500: {
            "description": "Reconciliation service failure",
            "content": {
                "application/json": {
                    "example": {**_ERROR_RESPONSE_EXAMPLE, "code": 500, "message": "Reconciliation service failure"}
                }
            },
        },
    }


RECONCILIATION_ACCOUNTS_RESPONSES = _json_response_examples(
    "Reconciliation accounts loaded",
    {
        "status": "available",
        "endpoint": "trade",
        "resource": "reconciliation_accounts",
        "items": [{"account_id": "backtest:7", "label": "Backtest account 7", "account_type": "backtest"}],
        "total_count": 1,
    },
)
RECONCILIATION_STATEMENTS_RESPONSES = _json_response_examples(
    "Reconciliation statements loaded",
    {
        "status": "available",
        "endpoint": "trade",
        "resource": "reconciliation_statements",
        "account_id": "backtest:7",
        "items": [],
        "summary": {"total_count": 0, "total_amount": "0", "total_commission": "0"},
        "total_count": 0,
        "page": 1,
        "page_size": 20,
        "source": "internal_statement_store",
    },
)
RECONCILIATION_RESULTS_RESPONSES = _json_response_examples(
    "Reconciliation results loaded",
    {
        "status": "available",
        "endpoint": "trade",
        "resource": "reconciliation_results",
        "account_id": "backtest:7",
        "import_batch_id": "batch-001",
        "items": [],
        "total_count": 0,
        "page": 1,
        "page_size": 20,
        "source": "internal_statement_store",
        "match_status": None,
    },
)
RECONCILIATION_IMPORT_RESPONSES = _json_response_examples(
    "Reconciliation import batch created",
    {
        "status": "available",
        "endpoint": "trade",
        "resource": "reconciliation_import_batch",
        "import_batch_id": "batch-001",
        "account_id": "backtest:7",
        "source_type": "miniqmt",
        "row_count": 2,
    },
)
RECONCILIATION_EXPORT_RESPONSES: dict[int, dict[str, Any]] = {
    200: {
        "description": "Reconciliation CSV export",
        "content": {"text/csv": {"example": "match_status,order_id,symbol\nmatched,order-001,000001\n"}},
    },
    **{code: spec for code, spec in RECONCILIATION_RESULTS_RESPONSES.items() if code != 200},
}


def _parse_query_date(value: str | None, field_name: str):
    if value is None:
        return None

    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise BusinessException(
            status_code=400,
            detail=create_error_response(
                error_code=ErrorCodes.VALIDATION_ERROR,
                message=f"{field_name} 格式错误，应为 YYYY-MM-DD",
            ).model_dump(mode="json"),
        ) from exc


def _parse_reconciliation_date_range(start_date: str | None, end_date: str | None):
    start_date_obj = _parse_query_date(start_date, "start_date")
    end_date_obj = _parse_query_date(end_date, "end_date")

    if start_date_obj and end_date_obj and start_date_obj > end_date_obj:
        raise BusinessException(
            status_code=400,
            detail=create_error_response(
                error_code=ErrorCodes.VALIDATION_ERROR,
                message="start_date 不能晚于 end_date",
            ).model_dump(mode="json"),
        )

    return start_date_obj, end_date_obj


def _query_internal_statement_rows(
    *,
    account_id: str,
    start_date: str | None,
    end_date: str | None,
    page: int,
    page_size: int,
) -> dict[str, Any]:
    start_date_obj, end_date_obj = _parse_reconciliation_date_range(start_date, end_date)

    try:
        return query_internal_statements(
            account_id=account_id,
            start_date=start_date_obj,
            end_date=end_date_obj,
            page=page,
            page_size=page_size,
        )
    except ValueError as exc:
        raise BusinessException(
            status_code=400,
            detail=create_error_response(
                error_code=ErrorCodes.VALIDATION_ERROR,
                message=str(exc),
            ).model_dump(mode="json"),
        ) from exc


def _query_all_internal_statement_rows(
    *,
    account_id: str,
    start_date: str | None,
    end_date: str | None,
    page_size: int = 10000,
) -> dict[str, Any]:
    first_page = _query_internal_statement_rows(
        account_id=account_id,
        start_date=start_date,
        end_date=end_date,
        page=1,
        page_size=page_size,
    )

    total_count = int(first_page["total_count"])
    items = list(first_page["items"])
    if len(items) >= total_count:
        return {**first_page, "items": items}

    current_page = 2
    while len(items) < total_count:
        next_page = _query_internal_statement_rows(
            account_id=account_id,
            start_date=start_date,
            end_date=end_date,
            page=current_page,
            page_size=page_size,
        )
        next_items = list(next_page["items"])
        if not next_items:
            break
        items.extend(next_items)
        current_page += 1

    return {**first_page, "items": items}


def _load_import_batch(import_batch_id: str) -> dict[str, Any]:
    try:
        return get_import_batch(import_batch_id)
    except KeyError as exc:
        raise BusinessException(
            status_code=404,
            detail=create_error_response(
                error_code=ErrorCodes.NOT_FOUND,
                message=f"unknown import_batch_id: {import_batch_id}",
            ).model_dump(mode="json"),
        ) from exc


def _filter_import_rows_for_account(
    *,
    account_id: str,
    batch_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    return [row for row in batch_rows if str(row.get("account_id", "")).strip() == account_id]


def _load_reconciliation_rows(
    *,
    account_id: str,
    import_batch_id: str,
    start_date: str | None,
    end_date: str | None,
    match_status: MatchStatus | None,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    internal_payload = _query_all_internal_statement_rows(
        account_id=account_id,
        start_date=start_date,
        end_date=end_date,
    )
    batch = _load_import_batch(import_batch_id)
    broker_rows = _filter_import_rows_for_account(
        account_id=account_id,
        batch_rows=list(batch.get("rows", [])),
    )
    results = match_reconciliation_rows(internal_payload["items"], broker_rows)
    if match_status is not None:
        results = [row for row in results if row["match_status"] == match_status]
    return internal_payload, results


@router.get(
    "/accounts",
    response_model=UnifiedResponse[ReconciliationAccountsPayload],
    summary="List reconciliation accounts",
    description="Return the synthetic accounts available for broker statement reconciliation.",
    responses=RECONCILIATION_ACCOUNTS_RESPONSES,
)
async def get_reconciliation_accounts() -> UnifiedResponse[ReconciliationAccountsPayload]:
    accounts = [
        ReconciliationAccountDescriptor.model_validate(item).model_dump(mode="json")
        for item in list_reconciliation_accounts()
    ]
    payload = ReconciliationAccountsPayload(
        status="available",
        endpoint="trade",
        resource="reconciliation_accounts",
        items=[ReconciliationAccountDescriptor.model_validate(item) for item in accounts],
        total_count=len(accounts),
    )
    return _success_reconciliation_response(
        message="Reconciliation accounts loaded",
        data_model=payload,
    )


@router.get(
    "/statements",
    response_model=UnifiedResponse[ReconciliationStatementsPayload],
    summary="List internal reconciliation statements",
    description="Return paginated internal statement rows that act as the reconciliation truth source.",
    responses=RECONCILIATION_STATEMENTS_RESPONSES,
)
async def get_reconciliation_statements(
    account_id: str = Query(..., description="Synthetic reconciliation account id"),
    start_date: str | None = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: str | None = Query(None, description="结束日期 YYYY-MM-DD"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
) -> UnifiedResponse[ReconciliationStatementsPayload]:
    payload = _query_internal_statement_rows(
        account_id=account_id,
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=page_size,
    )

    payload = {
        **payload,
        "items": [InternalStatementRow.model_validate(item).model_dump(mode="json") for item in payload["items"]],
        "summary": InternalStatementSummary.model_validate(payload["summary"]).model_dump(mode="json"),
    }
    response_payload = ReconciliationStatementsPayload(
        status="available",
        endpoint="trade",
        resource="reconciliation_statements",
        account_id=payload["account_id"],
        items=[InternalStatementRow.model_validate(item) for item in payload["items"]],
        summary=InternalStatementSummary.model_validate(payload["summary"]),
        total_count=payload["total_count"],
        page=payload["page"],
        page_size=payload["page_size"],
        source=payload["source"],
    )

    return _success_reconciliation_response(
        message="Reconciliation statements loaded",
        data_model=response_payload,
    )


@router.get(
    "/results",
    response_model=UnifiedResponse[ReconciliationResultsPayload],
    summary="List reconciliation match results",
    description="Return deterministic match results between internal statement rows and an imported broker batch.",
    responses=RECONCILIATION_RESULTS_RESPONSES,
)
async def get_reconciliation_results(
    account_id: str = Query(..., description="Synthetic reconciliation account id"),
    import_batch_id: str = Query(..., description="In-memory import batch identifier"),
    start_date: str | None = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: str | None = Query(None, description="结束日期 YYYY-MM-DD"),
    match_status: MatchStatus | None = Query(None, description="Deterministic reconciliation status filter"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
) -> UnifiedResponse[ReconciliationResultsPayload]:
    internal_payload, filtered_results = _load_reconciliation_rows(
        account_id=account_id,
        import_batch_id=import_batch_id,
        start_date=start_date,
        end_date=end_date,
        match_status=match_status,
    )

    total_count = len(filtered_results)
    offset = (page - 1) * page_size
    paged_results = filtered_results[offset : offset + page_size]
    response_payload = ReconciliationResultsPayload(
        status="available",
        endpoint="trade",
        resource="reconciliation_results",
        account_id=account_id,
        import_batch_id=import_batch_id,
        items=[ReconciliationResultItem.model_validate(item) for item in paged_results],
        total_count=total_count,
        page=page,
        page_size=page_size,
        source=str(internal_payload["source"]),
        match_status=match_status,
    )
    return _success_reconciliation_response(
        message="Reconciliation results loaded",
        data_model=response_payload,
    )


@router.get(
    "/export",
    response_class=Response,
    summary="Export reconciliation match results",
    description="Export reconciliation match results as a CSV file for audit and offline review.",
    responses=RECONCILIATION_EXPORT_RESPONSES,
)
async def export_reconciliation_results(
    account_id: str = Query(..., description="Synthetic reconciliation account id"),
    import_batch_id: str = Query(..., description="In-memory import batch identifier"),
    start_date: str | None = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: str | None = Query(None, description="结束日期 YYYY-MM-DD"),
    match_status: MatchStatus | None = Query(None, description="Deterministic reconciliation status filter"),
) -> Response:
    _internal_payload, filtered_results = _load_reconciliation_rows(
        account_id=account_id,
        import_batch_id=import_batch_id,
        start_date=start_date,
        end_date=end_date,
        match_status=match_status,
    )
    csv_content = build_reconciliation_export_csv(filtered_results)
    safe_account_id = account_id.replace(":", "_")
    filename = f"reconciliation-{safe_account_id}-{import_batch_id}-page-all.csv"
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post(
    "/import",
    response_model=UnifiedResponse[ReconciliationImportBatchPayload],
    summary="Import broker reconciliation CSV",
    description="Import a broker statement CSV and create an in-memory reconciliation batch for deterministic matching.",
    responses=RECONCILIATION_IMPORT_RESPONSES,
    openapi_extra={
        "requestBody": {
            "content": {
                "multipart/form-data": {
                    "examples": {
                        "miniqmt_statement": {
                            "summary": "miniQMT broker statement",
                            "value": {"file": "statement.csv", "source_type": "miniqmt", "account_id": "backtest:7"},
                        }
                    }
                }
            }
        }
    },
)
async def import_reconciliation_csv(
    file: UploadFile = File(..., description="Broker statement CSV file"),
    source_type: str = Form(..., description="CSV source type, such as miniqmt or normalized_template"),
    account_id: str | None = Form(None, description="Synthetic account id required by miniqmt imports"),
) -> UnifiedResponse[ReconciliationImportBatchPayload]:
    csv_bytes = await file.read()

    try:
        if source_type == "normalized_template":
            rows = parse_normalized_template_csv(csv_bytes)
            batch_account_id = None
        elif source_type == "miniqmt":
            if not account_id:
                raise BusinessException(
                    status_code=422,
                    detail=create_error_response(
                        error_code=ErrorCodes.VALIDATION_ERROR,
                        message="account_id is required for miniqmt imports",
                    ).model_dump(mode="json"),
                )
            rows = parse_miniqmt_csv(csv_bytes, account_id=account_id)
            batch_account_id = account_id
        else:
            raise BusinessException(
                status_code=422,
                detail=create_error_response(
                    error_code=ErrorCodes.VALIDATION_ERROR,
                    message="unsupported source_type",
                ).model_dump(mode="json"),
            )
    except ValueError as exc:
        raise BusinessException(
            status_code=422,
            detail=create_error_response(
                error_code=ErrorCodes.VALIDATION_ERROR,
                message=str(exc),
            ).model_dump(mode="json"),
        ) from exc

    batch = create_import_batch(
        account_id=batch_account_id,
        source_type=source_type,
        rows=rows,
    )
    response_payload = ReconciliationImportBatchPayload(
        status="available",
        endpoint="trade",
        resource="reconciliation_import_batch",
        import_batch_id=str(batch["import_batch_id"]),
        account_id=batch["account_id"] if batch["account_id"] is None else str(batch["account_id"]),
        source_type=str(batch["source_type"]),
        row_count=int(batch["row_count"]),
    )
    return _success_reconciliation_response(
        message="Reconciliation import batch created",
        data_model=response_payload,
    )
