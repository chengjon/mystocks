"""深圳证券交易所数据路由 (SZSE Data)"""

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


@router.get("/szse/overview", summary="获取深圳证券交易所市场总貌")
async def get_szse_market_overview(
    date: str = Query(..., description="查询日期", example="2024-01-15"),
    current_user: User = Depends(get_current_user),
):
    """获取深圳证券交易所市场总貌 (OpenStock SZSE_SUMMARY)

    返回深交所市场总貌数据。
    """
    try:
        result = await asyncio.to_thread(
            _get_client().fetch,
            DataCategory.SZSE_SUMMARY,
            {"date": date},
        )
        data = result.get("data", [])
        if not data:
            return create_error_response(ErrorCodes.DATA_NOT_FOUND, f"No SZSE overview for {date}")
        result = {
            "data": data,
            "count": len(data),
            "columns": list(data[0].keys()) if data else [],
            "date": date,
            "timestamp": datetime.now().isoformat(),
            "source": "openstock",
            "provider": "openstock_gateway",
            "exchange": "SZSE",
        }
        return create_success_response(result)
    except Exception as e:
        return create_error_response(ErrorCodes.INTERNAL_ERROR, str(e))


@router.get("/szse/area-trading", summary="获取深圳地区交易排序数据")
async def get_szse_area_trading(
    date: str = Query(..., description="查询日期", example="2024-01-15"),
    current_user: User = Depends(get_current_user),
):
    """获取深圳地区交易排序数据 (OpenStock SZSE_AREA_TRADING)

    返回深交所地区交易排序数据。
    """
    try:
        result = await asyncio.to_thread(
            _get_client().fetch,
            DataCategory.SZSE_AREA_TRADING,
            {"date": date},
        )
        data = result.get("data", [])
        if not data:
            return create_error_response(ErrorCodes.DATA_NOT_FOUND, f"No SZSE area trading for {date}")
        result = {
            "data": data,
            "count": len(data),
            "columns": list(data[0].keys()) if data else [],
            "date": date,
            "timestamp": datetime.now().isoformat(),
            "source": "openstock",
            "provider": "openstock_gateway",
            "region": "SZSE",
        }
        return create_success_response(result)
    except Exception as e:
        return create_error_response(ErrorCodes.INTERNAL_ERROR, str(e))


@router.get("/szse/sector-trading", summary="获取深圳行业成交数据")
async def get_szse_sector_trading(
    symbol: str = Query(..., description="行业代码", example="BK0477"),
    date: str = Query(..., description="查询日期", example="2024-01-15"),
    current_user: User = Depends(get_current_user),
):
    """获取深圳行业成交数据 (OpenStock SZSE_SECTOR_TRADING)

    返回深交所指定行业的成交统计数据。
    """
    try:
        result = await asyncio.to_thread(
            _get_client().fetch,
            DataCategory.SZSE_SECTOR_TRADING,
            {"sector_symbol": symbol, "date": date},
        )
        data = result.get("data", [])
        if not data:
            return create_error_response(ErrorCodes.DATA_NOT_FOUND, f"No SZSE sector trading for {symbol} on {date}")
        result = {
            "data": data,
            "count": len(data),
            "columns": list(data[0].keys()) if data else [],
            "date": date,
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "source": "openstock",
            "provider": "openstock_gateway",
            "region": "SZSE",
        }
        return create_success_response(result)
    except Exception as e:
        return create_error_response(ErrorCodes.INTERNAL_ERROR, str(e))
