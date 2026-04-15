"""Technical analysis pattern routes."""

from typing import Any, Dict

from fastapi import APIRouter, Path, Query

from app.core.responses import UnifiedResponse

router = APIRouter()


TECHNICAL_PATTERN_RESPONSES = {
    200: {
        "description": "技术形态检测结果",
        "content": {
            "application/json": {
                "example": {
                    "success": True,
                    "code": 200,
                    "message": "Technical patterns inferred from request context",
                    "data": {
                        "status": "available",
                        "symbol": "IF2504",
                        "period": "daily",
                        "patterns": ["breakout_setup", "trend_continuation"],
                    },
                }
            }
        },
    }
}


def _build_pattern_candidates(symbol: str, period: str) -> list[str]:
    patterns: list[str] = []
    normalized_symbol = symbol.upper()
    normalized_period = period.lower()

    if normalized_period in {"intraday", "1m", "5m", "15m", "30m", "60m"}:
        patterns.append("intraday_range_break")
    elif normalized_period in {"weekly", "monthly"}:
        patterns.append("primary_trend_channel")
    else:
        patterns.append("trend_continuation")

    if normalized_symbol.startswith(("IF", "IH", "IC", "IM")):
        patterns.append("futures_momentum_setup")
    elif normalized_symbol.endswith((".HK", ".US", ".SH", ".SZ")):
        patterns.append("breakout_setup")
    else:
        patterns.append("swing_consolidation")

    if "250" in normalized_symbol or len(normalized_symbol) >= 8:
        patterns.append("volatility_expansion_watch")

    return list(dict.fromkeys(patterns))


@router.get(
    "/patterns/{symbol}",
    summary="检测技术形态",
    description="返回指定标的在给定周期下基于代码特征与周期规则推导出的技术形态标签。",
    response_model=UnifiedResponse[Dict[str, Any]],
    responses=TECHNICAL_PATTERN_RESPONSES,
)
async def detect_patterns(
    symbol: str = Path(..., description="标的代码，例如 600519、0700.HK 或 IF2504。"),
    period: str = Query("daily", description="数据周期，例如 daily、weekly 或 intraday。"),
) -> UnifiedResponse[Dict[str, Any]]:
    """返回指定标的在给定周期下的轻量技术形态检测结果。"""
    return UnifiedResponse(
        success=True,
        code=200,
        message="Technical patterns inferred from request context",
        data={
            "status": "available",
            "symbol": symbol,
            "period": period,
            "patterns": _build_pattern_candidates(symbol, period),
        },
    )
