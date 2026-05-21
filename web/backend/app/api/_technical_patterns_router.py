"""Technical analysis pattern routes."""

from __future__ import annotations

import logging
from typing import get_args

from fastapi import APIRouter, Depends, Path, Query, status

from app.core.exceptions import BusinessException

from app.api._technical_patterns_models import PatternDetection, PatternDetectionData, PatternPeriod
from app.core.responses import UnifiedResponse
from app.openapi_config import COMMON_RESPONSES
from app.services.technical_pattern_detection_service import TechnicalPatternDetectionService

logger = logging.getLogger(__name__)
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


def get_technical_pattern_detection_service() -> TechnicalPatternDetectionService:
    """Return the technical pattern detection service for route-level DI."""
    return TechnicalPatternDetectionService()


async def _detect_patterns_for_symbol(
    symbol: str,
    period: str,
    service: TechnicalPatternDetectionService,
) -> list[PatternDetection]:
    """Return reviewed pattern detections for the requested symbol and period."""
    try:
        return await service.detect_for_symbol(symbol=symbol, period=period)
    except BusinessException:
        raise
    except Exception as exc:
        logger.warning("Pattern analysis unavailable for %s/%s: %s", symbol, period, exc)
        raise BusinessException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Pattern analysis unavailable",
        ) from exc


def _normalize_pattern_period(period: str) -> str:
    normalized_period = period.lower()
    if normalized_period not in SUPPORTED_PATTERN_PERIODS:
        raise BusinessException(
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
    service: TechnicalPatternDetectionService = Depends(get_technical_pattern_detection_service),
) -> UnifiedResponse[PatternDetectionData]:
    """返回指定标的在给定周期下的 reviewed 技术形态检测结果。"""
    normalized_symbol = symbol.upper()
    normalized_period = _normalize_pattern_period(period)
    detections = await _detect_patterns_for_symbol(
        symbol=normalized_symbol,
        period=normalized_period,
        service=service,
    )
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
