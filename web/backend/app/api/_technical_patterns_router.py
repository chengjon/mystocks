"""Technical analysis pattern placeholder routes."""

from typing import Any, Dict

from fastapi import APIRouter, Path, Query

from app.core.responses import UnifiedResponse

router = APIRouter()


TECHNICAL_PATTERN_RESPONSES = {
    200: {
        "description": "技术形态检测兼容占位结果",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "code": 503,
                    "message": "Pattern recognition feature is under development",
                    "data": {
                        "status": "placeholder",
                        "symbol": "IF2504",
                        "period": "daily",
                        "patterns": [],
                    },
                }
            }
        },
    }
}


@router.get(
    "/patterns/{symbol}",
    summary="检测技术形态",
    description="返回指定标的在给定周期下的技术形态兼容占位结果，显式标记当前接口仍未接入真实形态识别引擎。",
    response_model=UnifiedResponse[Dict[str, Any]],
    responses=TECHNICAL_PATTERN_RESPONSES,
)
async def detect_patterns(
    symbol: str = Path(..., description="标的代码，例如 600519、0700.HK 或 IF2504。"),
    period: str = Query("daily", description="数据周期，例如 daily、weekly 或 intraday。"),
) -> UnifiedResponse[Dict[str, Any]]:
    """返回指定标的在给定周期下的技术形态检测占位结果。"""
    return UnifiedResponse(
        success=False,
        code=503,
        message="Pattern recognition feature is under development",
        data={
            "status": "placeholder",
            "symbol": symbol,
            "period": period,
            "patterns": [],
        },
    )
