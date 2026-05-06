from __future__ import annotations

from datetime import datetime
from typing import TypeVar

from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile
from pydantic import BaseModel

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
from app.services.statement_reconciliation.import_batch_store import create_import_batch
from app.services.statement_reconciliation.parsers.miniqmt import parse_miniqmt_csv
from app.services.statement_reconciliation.parsers.normalized_template import parse_normalized_template_csv

router = APIRouter(prefix="/reconciliation", tags=["trade-reconciliation"])
ResponsePayloadT = TypeVar("ResponsePayloadT", bound=BaseModel)


def _success_reconciliation_response(
    message: str,
    data_model: ResponsePayloadT,
) -> UnifiedResponse[ResponsePayloadT]:
    return create_unified_success_response(data=data_model, message=message)


def _parse_query_date(value: str | None, field_name: str):
    if value is None:
        return None

    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=create_error_response(
                error_code=ErrorCodes.VALIDATION_ERROR,
                message=f"{field_name} 格式错误，应为 YYYY-MM-DD",
            ).model_dump(mode="json"),
        ) from exc


@router.get("/accounts", response_model=UnifiedResponse[ReconciliationAccountsPayload])
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


@router.get("/statements", response_model=UnifiedResponse[ReconciliationStatementsPayload])
async def get_reconciliation_statements(
    account_id: str = Query(..., description="Synthetic reconciliation account id"),
    start_date: str | None = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: str | None = Query(None, description="结束日期 YYYY-MM-DD"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
) -> UnifiedResponse[ReconciliationStatementsPayload]:
    start_date_obj = _parse_query_date(start_date, "start_date")
    end_date_obj = _parse_query_date(end_date, "end_date")

    if start_date_obj and end_date_obj and start_date_obj > end_date_obj:
        raise HTTPException(
            status_code=400,
            detail=create_error_response(
                error_code=ErrorCodes.VALIDATION_ERROR,
                message="start_date 不能晚于 end_date",
            ).model_dump(mode="json"),
        )

    try:
        payload = query_internal_statements(
            account_id=account_id,
            start_date=start_date_obj,
            end_date=end_date_obj,
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


@router.post("/import", response_model=UnifiedResponse[ReconciliationImportBatchPayload])
async def import_reconciliation_csv(
    file: UploadFile = File(...),
    source_type: str = Form(...),
    account_id: str | None = Form(None),
) -> UnifiedResponse[ReconciliationImportBatchPayload]:
    csv_bytes = await file.read()

    try:
        if source_type == "normalized_template":
            rows = parse_normalized_template_csv(csv_bytes)
            batch_account_id = None
        elif source_type == "miniqmt":
            if not account_id:
                raise HTTPException(
                    status_code=422,
                    detail=create_error_response(
                        error_code=ErrorCodes.VALIDATION_ERROR,
                        message="account_id is required for miniqmt imports",
                    ).model_dump(mode="json"),
                )
            rows = parse_miniqmt_csv(csv_bytes, account_id=account_id)
            batch_account_id = account_id
        else:
            raise HTTPException(
                status_code=422,
                detail=create_error_response(
                    error_code=ErrorCodes.VALIDATION_ERROR,
                    message="unsupported source_type",
                ).model_dump(mode="json"),
            )
    except ValueError as exc:
        raise HTTPException(
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
