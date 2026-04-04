"""
股指期货数据路由 (Futures)
"""
from typing import Any, Dict

from fastapi import APIRouter, Depends, Query

from app.core.exceptions import BusinessException
from app.core.security import User, get_current_user
from app.openapi_config import COMMON_RESPONSES

router = APIRouter()


def _success_response_spec(description: str, example: dict[str, Any]) -> dict[int, dict[str, Any]]:
    return {
        200: {
            "description": description,
            "content": {
                "application/json": {
                    "example": example,
                }
            },
        }
    }


FUTURES_INDEX_ERROR_RESPONSES = {
    422: COMMON_RESPONSES[422],
    500: COMMON_RESPONSES[500],
}

FUTURES_INDEX_DAILY_RESPONSES = {
    **FUTURES_INDEX_ERROR_RESPONSES,
    **_success_response_spec(
        "股指期货日线结果",
        {
            "success": True,
            "data": [
                {
                    "trade_date": "2026-04-03",
                    "open": 3528.2,
                    "close": 3546.8,
                    "high": 3551.4,
                    "low": 3519.6,
                    "volume": 128934,
                }
            ],
            "symbol": "IF2404",
        },
    ),
}

FUTURES_INDEX_REALTIME_RESPONSES = {
    **FUTURES_INDEX_ERROR_RESPONSES,
    **_success_response_spec(
        "股指期货实时快照结果",
        {
            "success": True,
            "data": [
                {
                    "symbol": "IF2404",
                    "last_price": 3548.6,
                    "change_pct": 0.64,
                    "bid_price": 3548.4,
                    "ask_price": 3548.8,
                    "volume": 32875,
                }
            ],
            "symbol": "IF2404",
        },
    ),
}


@router.get(
    "/futures/index/daily",
    summary="查询股指期货日线行情",
    description="查询项目范围内股指期货合约的日线数据，支持按合约代码和日期范围筛选历史行情。",
    responses=FUTURES_INDEX_DAILY_RESPONSES,
)
async def get_futures_index_daily(
    symbol: str = Query(..., description="股指期货合约代码，例如 IF2404、IH2404 或 IC2404。"),
    start_date: str = Query(..., description="查询开始日期，格式为 YYYY-MM-DD。"),
    end_date: str = Query(..., description="查询结束日期，格式为 YYYY-MM-DD。"),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    try:
        from app.services.data_source_factory import get_data_source_factory

        factory = await get_data_source_factory()
        result = await factory.get_data(
            "data",
            "futures/index/daily",
            {"symbol": symbol, "start_date": start_date, "end_date": end_date},
        )
        return {"success": True, "data": result.get("data", []), "symbol": symbol}
    except Exception as e:
        raise BusinessException(detail=f"获取股指期货日线失败: {str(e)}", status_code=500, error_code="DATA_RETRIEVAL_FAILED")

@router.get(
    "/futures/index/realtime",
    summary="查询股指期货实时快照",
    description="查询项目范围内股指期货合约的实时行情快照，适用于盘中监控和即时行情展示。",
    responses=FUTURES_INDEX_REALTIME_RESPONSES,
)
async def get_futures_index_realtime(
    symbol: str = Query(..., description="股指期货合约代码，例如 IF2404、IH2404 或 IC2404。"),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    try:
        from app.services.data_source_factory import get_data_source_factory

        factory = await get_data_source_factory()
        result = await factory.get_data("data", "futures/index/realtime", {"symbol": symbol})
        return {"success": True, "data": result.get("data", []), "symbol": symbol}
    except Exception as e:
        raise BusinessException(
            detail=f"获取股指期货实时快照失败: {str(e)}",
            status_code=500,
            error_code="DATA_RETRIEVAL_FAILED",
        )
