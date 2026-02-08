"""
深圳证券交易所数据路由 (SZSE Data)
"""
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from app.core.responses import ErrorCodes, create_error_response, create_success_response
from app.core.security import User, get_current_user
from .base import akshare_market_adapter

router = APIRouter()

@router.get("/szse/overview", summary="获取深圳证券交易所市场总貌")
async def get_szse_market_overview(
    date: str = Query(..., description="查询日期", example="2024-01-15"),
    current_user: User = Depends(get_current_user),
):
    try:
        df = await akshare_market_adapter.get_market_overview_szse(date)
        if df.empty: return create_error_response(ErrorCodes.DATA_NOT_FOUND, f"No SZSE overview for {date}")
        result = {
            "data": df.to_dict('records'), "count": len(df), "date": date,
            "timestamp": datetime.now().isoformat(), "source": "akshare", "exchange": "SZSE"
        }
        return create_success_response(result)
    except Exception as e:
        return create_error_response(ErrorCodes.INTERNAL_ERROR, str(e))

@router.get("/szse/area-trading", summary="获取深圳地区交易排序数据")
async def get_szse_area_trading(
    date: str = Query(..., description="查询日期", example="2024-01-15"),
    current_user: User = Depends(get_current_user),
):
    try:
        df = await akshare_market_adapter.get_szse_area_trading_summary(date)
        if df.empty: return create_error_response(ErrorCodes.DATA_NOT_FOUND, f"No SZSE area trading for {date}")
        result = {
            "data": df.to_dict('records'), "count": len(df), "date": date,
            "timestamp": datetime.now().isoformat(), "source": "akshare", "region": "SZSE"
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
    try:
        df = await akshare_market_adapter.get_market_szse_sector_trading(symbol, date)
        if df.empty: return create_error_response(ErrorCodes.DATA_NOT_FOUND, f"No SZSE sector trading for {symbol} on {date}")
        result = {
            "data": df.to_dict('records'), "count": len(df), "date": date, "symbol": symbol,
            "timestamp": datetime.now().isoformat(), "source": "akshare", "region": "SZSE"
        }
        return create_success_response(result)
    except Exception as e:
        return create_error_response(ErrorCodes.INTERNAL_ERROR, str(e))