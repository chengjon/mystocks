"""Technical analysis pattern routes."""

from __future__ import annotations

from typing import get_args

from fastapi import APIRouter, HTTPException, Path, Query, status

from app.api._technical_patterns_models import PatternDetection, PatternDetectionData, PatternPeriod
from app.core.responses import UnifiedResponse
from app.openapi_config import COMMON_RESPONSES

router = APIRouter()
SUPPORTED_PATTERN_PERIODS = get_args(PatternPeriod)


TECHNICAL_PATTERN_RESPONSES = {
    200: {
        "description": "技术形态检测结果",
        "content": {
            "application/json": {
                "example": {
                    "success": True,
                    "code": 200,
                    "message": "Technical patterns evaluated",
                    "data": {
                        "status": "empty",
                        "symbol": "600519.SH",
                        "period": "weekly",
                        "patterns": [],
                    },
                }
            }
        },
    },
    422: COMMON_RESPONSES[422],
    500: COMMON_RESPONSES[500],
    503: {
        "description": "技术形态分析当前不可用",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "code": 503,
                    "message": "Technical pattern detection is currently unavailable",
                    "data": None,
                    "timestamp": "2026-05-05T08:00:00+00:00",
                }
            }
        },
    },
}


async def _detect_patterns_for_symbol(symbol: str, period: str) -> list[PatternDetection]:
    """Task 1 keeps the reviewed route contract stable; Task 2 provides real detections."""
    _ = (symbol, period)
    return []


def _normalize_pattern_period(period: str) -> str:
    normalized_period = period.lower()
    if normalized_period not in SUPPORTED_PATTERN_PERIODS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Unsupported period '{period}'. Expected one of: {', '.join(SUPPORTED_PATTERN_PERIODS)}.",
        )
    return normalized_period


@router.get(
    "/patterns/{symbol}",
    summary="检测技术形态",
    description="返回指定标的在给定周期下的结构化技术形态检测结果；若无形态命中则返回空结果，而不是推导式标签。",
    response_model=UnifiedResponse[PatternDetectionData],
    responses=TECHNICAL_PATTERN_RESPONSES,
)
async def detect_patterns(
    symbol: str = Path(..., description="标的代码，例如 600519.SH、0700.HK 或 IF2504。"),
    period: str = Query(
        "daily",
        description="检测周期，仅支持 daily、weekly、monthly；大小写不敏感。",
        json_schema_extra={"enum": list(SUPPORTED_PATTERN_PERIODS)},
    ),
) -> UnifiedResponse[PatternDetectionData]:
    """返回指定标的在给定周期下的 reviewed 技术形态检测结果。"""
    normalized_symbol = symbol.upper()
    normalized_period = _normalize_pattern_period(period)
    detections = await _detect_patterns_for_symbol(symbol=normalized_symbol, period=normalized_period)
    payload = PatternDetectionData(
        status="available" if detections else "empty",
        symbol=normalized_symbol,
        period=normalized_period,
        patterns=detections,
    )
    return UnifiedResponse(
        success=True,
        code=status.HTTP_200_OK,
        message="Technical patterns evaluated",
        data=payload,
    )
