"""
上海证券交易所数据路由 (SSE Data)
"""
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from app.core.responses import ErrorCodes, create_error_response, create_success_response
from app.core.security import User, get_current_user
from .base import akshare_market_adapter

router = APIRouter()

@router.get("/sse/overview", summary="获取上海证券交易所市场总貌")
async def get_sse_market_overview(current_user: User = Depends(get_current_user)):
    try:
        df = await akshare_market_adapter.get_market_overview_sse()
        if df.empty: return create_error_response(ErrorCodes.DATA_NOT_FOUND, "No SSE overview data found")
        result = {
            "data": df.to_dict('records'), "count": len(df), "columns": list(df.columns),
            "timestamp": datetime.now().isoformat(), "source": "akshare", "exchange": "SSE"
        }
        return create_success_response(result)
    except Exception as e:
        return create_error_response(ErrorCodes.INTERNAL_ERROR, str(e))

@router.get("/sse/daily-deal", summary="获取上海交易所每日概况")
async def get_sse_daily_deal(
    date: str = Query(..., description="查询日期", example="2024-01-15"),
    current_user: User = Depends(get_current_user),
):
    try:
        df = await akshare_market_adapter.get_market_sse_daily_deal(date)
        if df.empty: return create_error_response(ErrorCodes.DATA_NOT_FOUND, f"No SSE daily deal found for {date}")
        result = {
            "data": df.to_dict('records'), "count": len(df), "date": date,
            "timestamp": datetime.now().isoformat(), "source": "akshare", "exchange": "SSE"
        }
        return create_success_response(result)
    except Exception as e:
        return create_error_response(ErrorCodes.INTERNAL_ERROR, str(e))