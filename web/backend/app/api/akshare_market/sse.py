"""上海证券交易所数据路由 (SSE Data)"""

import asyncio
from datetime import datetime

from fastapi import APIRouter, Depends, Query

from app.core.config import settings
from app.core.responses import ErrorCodes, create_error_response, create_success_response
from app.core.security import User, get_current_user
from src.services.openstock import OpenStockClient, DataCategory


router = APIRouter()

# 模块级 client 单例(懒初始化)
_client: OpenStockClient | None = None


def _get_client() -> OpenStockClient:
    global _client
    if _client is None:
        _client = OpenStockClient(
            base_url=settings.openstock_base_url,
            api_key=settings.openstock_api_key,
        )
    return _client


@router.get("/sse/overview", summary="获取上海证券交易所市场总貌")
async def get_sse_market_overview(current_user: User = Depends(get_current_user)):
    """获取上海证券交易所市场总貌 (OpenStock SSE_SUMMARY)

    返回上交所市场总貌数据。
    """
    try:
        result = await asyncio.to_thread(
            _get_client().fetch,
            DataCategory.SSE_SUMMARY,
            {},
        )
        data = result.get("data", [])
        if not data:
            return create_error_response(ErrorCodes.DATA_NOT_FOUND, "No SSE overview data found")
        result = {
            "data": data,
            "count": len(data),
            "columns": list(data[0].keys()) if data else [],
            "timestamp": datetime.now().isoformat(),
            "source": "openstock",
            "provider": "openstock_gateway",
            "exchange": "SSE",
        }
        return create_success_response(result)
    except Exception as e:
        return create_error_response(ErrorCodes.INTERNAL_ERROR, str(e))


@router.get("/sse/daily-deal", summary="获取上海交易所每日概况")
async def get_sse_daily_deal(
    date: str = Query(..., description="查询日期", example="2024-01-15"),
    current_user: User = Depends(get_current_user),
):
    """获取上海交易所每日概况 (OpenStock SSE_DAILY_DEAL)

    返回上交所每日成交概况数据。
    """
    try:
        result = await asyncio.to_thread(
            _get_client().fetch,
            DataCategory.SSE_DAILY_DEAL,
            {"date": date},
        )
        data = result.get("data", [])
        if not data:
            return create_error_response(ErrorCodes.DATA_NOT_FOUND, f"No SSE daily deal found for {date}")
        result = {
            "data": data,
            "count": len(data),
            "columns": list(data[0].keys()) if data else [],
            "date": date,
            "timestamp": datetime.now().isoformat(),
            "source": "openstock",
            "provider": "openstock_gateway",
            "exchange": "SSE",
        }
        return create_success_response(result)
    except Exception as e:
        return create_error_response(ErrorCodes.INTERNAL_ERROR, str(e))
