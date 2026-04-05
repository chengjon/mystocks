"""Technical analysis pattern placeholder routes."""

from fastapi import APIRouter, Path, Query

router = APIRouter()


TECHNICAL_PATTERN_RESPONSES = {
    200: {
        "description": "技术形态检测占位结果",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "message": "Pattern recognition feature is under development",
                    "symbol": "IF2504",
                }
            }
        },
    }
}


@router.get(
    "/patterns/{symbol}",
    summary="检测技术形态",
    description="返回指定标的在给定周期下的技术形态检测占位结果，用于前后端联调和后续形态识别功能接入。",
    responses=TECHNICAL_PATTERN_RESPONSES,
)
async def detect_patterns(
    symbol: str = Path(..., description="标的代码，例如 600519、0700.HK 或 IF2504。"),
    period: str = Query("daily", description="数据周期，例如 daily、weekly 或 intraday。"),
):
    """返回指定标的在给定周期下的技术形态检测占位结果。"""
    return {
        "success": False,
        "message": "Pattern recognition feature is under development",
        "symbol": symbol,
    }
