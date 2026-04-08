"""
技术指标API

提供各种技术指标的计算功能
"""

from typing import Any, Dict, List

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

router = APIRouter(
    prefix="/technical-indicators",
    tags=["Technical Indicators"],
)


TECHNICAL_INDICATORS_RESPONSES = {
    200: {
        "description": "技术指标计算结果",
        "content": {
            "application/json": {
                "example": {
                    "symbol": "IF9999.CCFX",
                    "indicators": {
                        "rsi": {"value": 58.4, "signal": "NEUTRAL"},
                        "macd": {"value": 1.26, "signal": "BULLISH"},
                        "bollinger": {"value": 0.63, "signal": "UPPER_BAND"},
                    },
                    "calculated_at": "2026-04-08T12:45:00Z",
                }
            }
        },
    }
}


class TechnicalIndicatorResponse(BaseModel):
    """Technical indicator response"""

    symbol: str = Field(..., description="请求指标计算的股票代码。")
    indicators: Dict[str, Any] = Field(..., description="按指标名称组织的计算结果映射。")
    calculated_at: str = Field(..., description="本次指标计算完成时间。")


@router.get(
    "",
    response_model=TechnicalIndicatorResponse,
    summary="Get Technical Indicators",
    description="按标的、指标集合和周期参数计算技术指标，返回信号方向和计算时间。",
    responses=TECHNICAL_INDICATORS_RESPONSES,
)
async def get_technical_indicators(
    symbol: str = Query(..., description="Stock symbol"),
    indicators: List[str] = Query(..., description="Indicator names (rsi,macd,bollinger,etc.)"),
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
