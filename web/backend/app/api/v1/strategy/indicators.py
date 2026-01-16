"""
技术指标API

提供各种技术指标的计算功能
"""

from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import List, Dict, Any

router = APIRouter(
    prefix="/technical-indicators",
    tags=["Technical Indicators"],
)


class TechnicalIndicatorResponse(BaseModel):
    """Technical indicator response"""

    symbol: str
    indicators: Dict[str, Any]
    calculated_at: str


@router.get(
    "", response_model=TechnicalIndicatorResponse, summary="Get Technical Indicators"
)
async def get_technical_indicators(
    symbol: str = Query(..., description="Stock symbol"),
    indicators: List[str] = Query(
        ..., description="Indicator names (rsi,macd,bollinger,etc.)"
    ),
    period: int = Query(14, description="Calculation period"),
):
    """
    计算技术指标

    Calculates various technical indicators for given symbol and time period.
    """
    mock_indicators = {}
    for indicator in indicators:
        mock_indicators[indicator] = {"value": 0.5, "signal": "NEUTRAL"}

    return TechnicalIndicatorResponse(
        symbol=symbol,
        indicators=mock_indicators,
        calculated_at="2025-01-20T10:30:00Z",
    )
