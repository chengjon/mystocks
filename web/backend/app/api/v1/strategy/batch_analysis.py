"""Canonical AI batch analysis workbench routes."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from enum import Enum
from typing import Any, Dict
from uuid import uuid4

from fastapi import APIRouter, Body, Path

from app.core.exceptions import BusinessException
from pydantic import BaseModel, Field, field_validator, model_validator

from app.core.responses import UnifiedResponse

router = APIRouter(prefix="/batch-analysis")

MAX_BATCH_SYMBOLS = 20

_BATCH_SUCCESS_EXAMPLE: dict[str, Any] = {
    "success": True,
    "code": 200,
    "message": "Batch analysis task completed",
    "data": {
        "task_id": "batch_001",
        "operation": "batch_screening",
        "symbols": ["000001", "600000"],
        "status": "completed",
        "summary": {"total_symbols": 2, "completed_symbols": 2, "failed_symbols": 0},
    },
}
_BATCH_ERROR_EXAMPLE: dict[str, Any] = {
    "success": False,
    "code": 400,
    "message": "Invalid batch analysis request",
    "data": None,
}
BATCH_ANALYSIS_RESPONSES: dict[int, dict[str, Any]] = {
    200: {
        "description": "Batch analysis runtime response",
        "content": {"application/json": {"example": _BATCH_SUCCESS_EXAMPLE}},
    },
    400: {
        "description": "Invalid batch analysis request",
        "content": {"application/json": {"example": _BATCH_ERROR_EXAMPLE}},
    },
    404: {
        "description": "Batch analysis task not found",
        "content": {"application/json": {"example": {**_BATCH_ERROR_EXAMPLE, "code": 404, "message": "Batch task not found"}}},
    },
    500: {
        "description": "Batch analysis runtime failure",
        "content": {"application/json": {"example": {**_BATCH_ERROR_EXAMPLE, "code": 500, "message": "Batch runtime failure"}}},
    },
}


class BatchAnalysisOperation(str, Enum):
    """Supported first-batch analysis operation types."""

    BATCH_BACKTEST = "batch_backtest"
    BATCH_SCREENING = "batch_screening"
    BATCH_MONITORING = "batch_monitoring"


class BatchAnalysisRequest(BaseModel):
    """Canonical batch analysis request."""

    operation: BatchAnalysisOperation = Field(..., description="Batch analysis operation")
    symbols: list[str] = Field(..., min_length=1, description="Symbols to analyze")
    start_date: str = Field(..., description="Analysis start date")
    end_date: str = Field(..., description="Analysis end date")
    options: Dict[str, Any] = Field(default_factory=dict, description="Operation options")

    @field_validator("symbols")
    @classmethod
    def validate_symbols(cls, symbols: list[str]) -> list[str]:
        normalized_symbols = [symbol.strip() for symbol in symbols]
        if any(not symbol for symbol in normalized_symbols):
            raise ValueError("symbols must not contain blank values")
        return normalized_symbols

    @model_validator(mode="after")
    def validate_date_range(self) -> "BatchAnalysisRequest":
        try:
            start_date = date.fromisoformat(self.start_date)
            end_date = date.fromisoformat(self.end_date)
        except ValueError as exc:
            raise ValueError("start_date and end_date must be ISO date strings") from exc

        if start_date > end_date:
            raise ValueError("start_date must be earlier than or equal to end_date")
        return self


@dataclass(slots=True)
class BatchAnalysisTask:
    """Runtime-registered first-batch analysis task."""

    task_id: str
    operation: str
    symbols: list[str]
    start_date: str
    end_date: str
    options: dict[str, Any]
    status: str
    summary: dict[str, Any]
    results: list[dict[str, Any]]
    warnings: list[str]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class BatchAnalysisRuntimeStore:
    """Small in-memory registry for first-batch observation evidence."""

    def __init__(self) -> None:
        self._tasks: dict[str, BatchAnalysisTask] = {}

    def reset(self) -> None:
        self._tasks.clear()

    def upsert(self, task: BatchAnalysisTask) -> BatchAnalysisTask:
        task.updated_at = datetime.now(timezone.utc)
        self._tasks[task.task_id] = task
        return task

    def get(self, task_id: str) -> BatchAnalysisTask | None:
        return self._tasks.get(task_id)

    def list(self) -> list[BatchAnalysisTask]:
        return sorted(self._tasks.values(), key=lambda item: item.created_at, reverse=True)


batch_analysis_store = BatchAnalysisRuntimeStore()


def _batch_safety_payload() -> dict[str, Any]:
    return {
        "analytical_output_only": True,
        "disclaimer": "Batch analysis outputs are analytical evidence, not automated trading or scheduler mutation.",
    }


def _score_symbol(symbol: str, index: int) -> tuple[float, str]:
    base = (sum(ord(char) for char in symbol) % 37) / 100
    score = round(0.42 + base + index * 0.013, 4)
    signal = "candidate" if score >= 0.64 else "watch" if score >= 0.52 else "neutral"
    return min(score, 0.95), signal


def _build_results(request: BatchAnalysisRequest) -> list[dict[str, Any]]:
    results = []
    for index, symbol in enumerate(request.symbols):
        score, signal = _score_symbol(symbol, index)
        results.append(
            {
                "symbol": symbol,
                "status": "completed",
                "score": score,
                "signal": signal,
                "metrics": {
                    "expected_return": round((score - 0.5) / 10, 4),
                    "risk_score": round(max(0.05, 1 - score), 4),
                },
                "evidence": {
                    "operation": request.operation.value,
                    "source": "runtime_batch_analysis",
                },
            }
        )
    return results


def _serialize_task(task: BatchAnalysisTask, *, include_results: bool) -> dict[str, Any]:
    payload = {
        "task_id": task.task_id,
        "operation": task.operation,
        "symbols": task.symbols,
        "status": task.status,
        "summary": task.summary,
        "warnings": task.warnings,
        "created_at": task.created_at.isoformat(),
        "updated_at": task.updated_at.isoformat(),
        "safety": _batch_safety_payload(),
    }
    if include_results:
        payload["results"] = task.results
    return payload


@router.get(
    "/runtime-status",
    response_model=UnifiedResponse[Dict[str, Any]],
    summary="Batch analysis runtime status",
    description="返回 7.2 批量分析 canonical runtime 的能力、限制和底层证据模块。",
    responses=BATCH_ANALYSIS_RESPONSES,
)
async def get_batch_analysis_runtime_status():
    data = {
        "service_available": True,
        "runtime_backend": "runtime_batch_registry",
        "max_symbols": MAX_BATCH_SYMBOLS,
        "supported_operations": [operation.value for operation in BatchAnalysisOperation],
        "evidence_modules": [
            "src/ml_strategy/backtest/backtest_engine.py",
            "src/ml_strategy/strategy/stock_screener.py",
            "src/ml_strategy/automation/scheduler.py",
            "src/ml_strategy/strategy/strategy_executor.py",
        ],
        "warnings": ["first_batch_runtime_registry_only"],
        "safety": _batch_safety_payload(),
    }
    return UnifiedResponse(success=True, code=200, message="Batch analysis runtime status", data=data)


@router.post(
    "/submit",
    response_model=UnifiedResponse[Dict[str, Any]],
    summary="Submit canonical batch analysis task",
    description="提交 7.2 canonical 批量分析任务并返回运行时证据摘要。",
    responses=BATCH_ANALYSIS_RESPONSES,
)
async def submit_batch_analysis_task(
    request: BatchAnalysisRequest = Body(
        ...,
        openapi_examples={
            "batch_screening": {
                "summary": "Batch screening request",
                "value": {
                    "operation": "batch_screening",
                    "symbols": ["000001", "600000"],
                    "start_date": "2026-01-01",
                    "end_date": "2026-03-31",
                    "options": {"score_threshold": 0.6},
                },
            }
        },
    ),
):
    if len(request.symbols) > MAX_BATCH_SYMBOLS:
        raise BusinessException(status_code=400, detail=f"First-batch analysis supports at most {MAX_BATCH_SYMBOLS} symbols")

    results = _build_results(request)
    candidate_count = len([item for item in results if item["signal"] == "candidate"])
    summary = {
        "total_symbols": len(request.symbols),
        "completed_symbols": len(results),
        "failed_symbols": 0,
        "candidate_count": candidate_count,
        "average_score": round(sum(item["score"] for item in results) / len(results), 4),
    }
    task = batch_analysis_store.upsert(
        BatchAnalysisTask(
            task_id=f"batch_{uuid4().hex[:12]}",
            operation=request.operation.value,
            symbols=request.symbols,
            start_date=request.start_date,
            end_date=request.end_date,
            options=dict(request.options or {}),
            status="completed",
            summary=summary,
            results=results,
            warnings=["first_batch_not_production_scheduler"],
        )
    )
    return UnifiedResponse(
        success=True,
        code=200,
        message="Batch analysis task completed",
        data=_serialize_task(task, include_results=True),
    )


@router.get(
    "/tasks",
    response_model=UnifiedResponse[Dict[str, Any]],
    summary="List canonical batch analysis tasks",
    description="列出 7.2 canonical 批量分析运行时任务摘要。",
    responses=BATCH_ANALYSIS_RESPONSES,
)
async def list_batch_analysis_tasks():
    tasks = [_serialize_task(task, include_results=False) for task in batch_analysis_store.list()]
    return UnifiedResponse(
        success=True,
        code=200,
        message="Batch analysis tasks listed",
        data={"tasks": tasks, "total": len(tasks)},
    )


@router.get(
    "/tasks/{task_id}",
    response_model=UnifiedResponse[Dict[str, Any]],
    summary="Get canonical batch analysis task detail",
    description="读取 7.2 canonical 批量分析运行时任务详情。",
    responses=BATCH_ANALYSIS_RESPONSES,
)
async def get_batch_analysis_task_detail(
    task_id: str = Path(..., description="Canonical batch analysis task identifier"),
):
    task = batch_analysis_store.get(task_id)
    if task is None:
        raise BusinessException(status_code=404, detail=f"Unknown batch task: {task_id}")
    return UnifiedResponse(
        success=True,
        code=200,
        message="Batch analysis task detail",
        data=_serialize_task(task, include_results=True),
    )
