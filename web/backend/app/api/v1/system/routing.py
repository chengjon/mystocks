"""
数据路由API

提供智能数据路由选择功能
"""

from datetime import date
from typing import Any, Dict, Optional

from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel, Field

from app.core.responses import UnifiedResponse
from src.core.data_classification import DataClassification
from src.core.infrastructure.data_router import DataRouter

router = APIRouter(
    prefix="/data",
    tags=["Data Routing"],
)


DATA_ROUTING_SUCCESS_EXAMPLE = {
    "success": True,
    "code": 200,
    "message": "数据路由决策成功",
    "data": {
        "route_selected": "tdengine",
        "estimated_records": 44640,
        "query_complexity": "high_frequency",
        "recommended_strategy": "time_series_scan",
        "classification": "minute_kline",
    },
}

DATA_ROUTING_RESPONSES = {
    200: {
        "description": "数据路由结果",
        "content": {
            "application/json": {
                "example": DATA_ROUTING_SUCCESS_EXAMPLE,
            }
        },
    }
}

DATA_ROUTING_REQUEST_EXAMPLE = {
    "data_category": "market_data",
    "symbol": "IF9999.CCFX",
    "date_range": {"start": "2025-03-01", "end": "2025-03-31"},
}

_CATEGORY_TO_CLASSIFICATION = {
    "reference_data": DataClassification.SYMBOLS_INFO,
    "derived_data": DataClassification.TECHNICAL_INDICATORS,
    "transaction_data": DataClassification.TRADE_RECORDS,
    "metadata": DataClassification.SYSTEM_CONFIG,
}

_ROUTER = DataRouter()


class DataRoutingRequest(BaseModel):
    """Data routing request"""

    data_category: str = Field(
        ...,
        description="Data category (market_data|reference_data|derived_data|transaction_data|metadata)",
    )
    symbol: Optional[str] = Field(None, description="Stock symbol")
    date_range: Optional[Dict[str, str]] = Field(None, description="Date range filter")


class DataRoutingResponse(BaseModel):
    """Data routing response"""

    route_selected: str = Field(..., description="Selected database route")
    estimated_records: int = Field(..., description="Estimated record count")
    query_complexity: str = Field(..., description="Query complexity level")
    recommended_strategy: str = Field(..., description="Recommended query strategy")
    classification: str = Field(..., description="Resolved internal data classification")


def _parse_date(value: Optional[str]) -> Optional[date]:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid ISO date: {value}") from exc


def _resolve_market_classification(request: DataRoutingRequest) -> DataClassification:
    date_range = request.date_range or {}
    start = _parse_date(date_range.get("start"))
    end = _parse_date(date_range.get("end"))

    if start and end and end < start:
        raise HTTPException(status_code=400, detail="date_range.end must be on or after date_range.start")

    if start and end:
        range_days = (end - start).days + 1
        if range_days <= 31:
            return DataClassification.MINUTE_KLINE
        return DataClassification.DAILY_KLINE

    if request.symbol:
        return DataClassification.MINUTE_KLINE
    return DataClassification.DAILY_KLINE


def _resolve_classification(request: DataRoutingRequest) -> DataClassification:
    category = request.data_category.strip().lower()
    if category == "market_data":
        return _resolve_market_classification(request)

    classification = _CATEGORY_TO_CLASSIFICATION.get(category)
    if classification is None:
        raise HTTPException(status_code=400, detail=f"Unsupported data_category: {request.data_category}")
    return classification


def _estimate_records(classification: DataClassification, request: DataRoutingRequest) -> int:
    date_range = request.date_range or {}
    start = _parse_date(date_range.get("start"))
    end = _parse_date(date_range.get("end"))
    if start and end:
        range_days = (end - start).days + 1
    else:
        range_days = 1

    if classification == DataClassification.MINUTE_KLINE:
        return max(range_days, 1) * 24 * 60
    if classification == DataClassification.DAILY_KLINE:
        return max(range_days, 1)
    if classification == DataClassification.TECHNICAL_INDICATORS:
        return max(range_days, 1) * 16
    if classification == DataClassification.TRADE_RECORDS:
        return max(range_days, 1) * 32
    if classification == DataClassification.SYMBOLS_INFO:
        return 1 if request.symbol else 5000
    return 1


def _build_strategy(target: str, classification: DataClassification) -> tuple[str, str]:
    if target == "tdengine":
        return "high_frequency", "time_series_scan"
    if classification in {DataClassification.TECHNICAL_INDICATORS, DataClassification.TRADE_RECORDS}:
        return "analytical", "partition_pruning"
    if classification == DataClassification.SYMBOLS_INFO:
        return "lookup", "indexed_lookup"
    return "relational", "direct_query"


@router.post(
    "/route",
    response_model=UnifiedResponse[Dict[str, Any]],
    summary="Data Routing Decision",
    description="根据数据类别、标的和时间范围推断查询路由，当前实现基于运行时 DataRouter 规则返回真实数据库路由建议。",
    responses=DATA_ROUTING_RESPONSES,
)
async def get_data_route(request: DataRoutingRequest = Body(..., example=DATA_ROUTING_REQUEST_EXAMPLE)):
    """
    根据数据特性和查询条件智能选择数据库路由。

    Uses the runtime DataRouter mapping to resolve an internal data classification
    and recommend the backing database plus a matching query strategy.
    """
    classification = _resolve_classification(request)
    target = _ROUTER.get_target_database(classification)
    route_selected = target.value.lower()
    query_complexity, recommended_strategy = _build_strategy(route_selected, classification)

    response = DataRoutingResponse(
        route_selected=route_selected,
        estimated_records=_estimate_records(classification, request),
        query_complexity=query_complexity,
        recommended_strategy=recommended_strategy,
        classification=classification.value,
    )
    return UnifiedResponse(success=True, code=200, message="数据路由决策成功", data=response.model_dump())
