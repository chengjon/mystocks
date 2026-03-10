"""Technical analysis pattern placeholder routes."""

from fastapi import APIRouter, Query

router = APIRouter()


@router.get("/patterns/{symbol}")
async def detect_patterns(symbol: str, period: str = Query("daily", description="数据周期")):
    """检测技术形态占位接口。"""
    return {
        "success": False,
        "message": "Pattern recognition feature is under development",
        "symbol": symbol,
    }
