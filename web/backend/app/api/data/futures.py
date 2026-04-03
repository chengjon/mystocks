"""
股指期货数据路由 (Futures)
"""
from typing import Any, Dict
from fastapi import APIRouter, Depends, Query, HTTPException
from app.core.security import User, get_current_user

router = APIRouter()

@router.get(
    "/futures/index/daily",
    description="查询股指期货日线数据，支持按合约代码和日期范围筛选历史行情。",
)
async def get_futures_index_daily(
    symbol: str = Query(..., description="期货合约代码。"),
    start_date: str = Query(..., description="查询开始日期，格式为 YYYY-MM-DD。"),
    end_date: str = Query(..., description="查询结束日期，格式为 YYYY-MM-DD。"),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    try:
        from app.services.data_source_factory import get_data_source_factory
        factory = await get_data_source_factory()
        result = await factory.get_data("data", "futures/index/daily", {"symbol": symbol, "start_date": start_date, "end_date": end_date})
        return {"success": True, "data": result.get("data", []), "symbol": symbol}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/futures/index/realtime",
    description="查询股指期货实时行情快照，适用于盘中监控和即时行情展示。",
)
async def get_futures_index_realtime(
    symbol: str = Query(..., description="期货合约代码。"),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    try:
        from app.services.data_source_factory import get_data_source_factory
        factory = await get_data_source_factory()
        result = await factory.get_data("data", "futures/index/realtime", {"symbol": symbol})
        return {"success": True, "data": result.get("data", []), "symbol": symbol}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
