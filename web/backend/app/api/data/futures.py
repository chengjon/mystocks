"""
股指期货数据路由 (Futures)
"""
from typing import Any, Dict
from fastapi import APIRouter, Depends, Query, HTTPException
from app.core.security import User, get_current_user

router = APIRouter()

@router.get("/futures/index/daily")
async def get_futures_index_daily(
    symbol: str = Query(...),
    start_date: str = Query(...),
    end_date: str = Query(...),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    try:
        from app.services.data_source_factory import get_data_source_factory
        factory = await get_data_source_factory()
        result = await factory.get_data("data", "futures/index/daily", {"symbol": symbol, "start_date": start_date, "end_date": end_date})
        return {"success": True, "data": result.get("data", []), "symbol": symbol}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/futures/index/realtime")
async def get_futures_index_realtime(
    symbol: str = Query(...),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    try:
        from app.services.data_source_factory import get_data_source_factory
        factory = await get_data_source_factory()
        result = await factory.get_data("data", "futures/index/realtime", {"symbol": symbol})
        return {"success": True, "data": result.get("data", []), "symbol": symbol}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
