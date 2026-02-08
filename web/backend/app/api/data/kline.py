"""
K线与行情数据路由 (KLine Data)
"""
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
import pandas as pd
from fastapi import APIRouter, Depends, Query, HTTPException

from app.core.database import db_service
from app.core.exceptions import BusinessException, ValidationException
from app.core.responses import ErrorCodes, create_error_response
from app.core.security import User, get_current_user
from src.utils.data_format_converter import normalize_api_response_format, normalize_stock_data_format

router = APIRouter()

@router.get("/stocks/daily")
async def get_daily_kline(
    symbol: str = Query(..., description="股票代码"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """获取股票日线数据"""
    try:
        from app.services.data_source_factory import get_data_source_factory
        factory = await get_data_source_factory()
        
        if not end_date: end_date = datetime.now().strftime("%Y-%m-%d")
        if not start_date: start_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
        
        params = {"symbol": symbol, "start_date": start_date, "end_date": end_date, "limit": limit}
        result = await factory.get_data("data", "stocks/daily", params)
        
        if result.get("status") == "success":
            return {
                "success": True, "data": result.get("data", []),
                "symbol": symbol, "total": result.get("total", 0),
                "timestamp": datetime.now().isoformat(),
            }
        raise BusinessException(detail="获取失败", status_code=500)
    except Exception as e:
        raise BusinessException(detail=str(e), status_code=500)

@router.get("/kline")
async def get_kline(
    symbol: str = Query(...),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """获取股票K线数据（日线别名）"""
    return await get_daily_kline(symbol, start_date, end_date, limit, current_user)

@router.get("/stocks/kline")
async def get_kline_data(
    symbol: str = Query(...),
    start_date: str = Query(...),
    end_date: str = Query(...),
    period: str = "day",
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """标准化K线数据接口"""
    try:
        cache_key = f"kline:{symbol}:{start_date}:{end_date}:{period}"
        cached_data = db_service.get_cache_data(cache_key)
        if cached_data: return cached_data

        df = db_service.query_daily_kline(symbol, start_date, end_date)
        if df.empty: return {"success": True, "data": [], "total": 0}

        df["date"] = pd.to_datetime(df["trade_date"] if "trade_date" in df.columns else df["date"])
        df = df.sort_values("date")
        
        # Format conversion
        data_records = []
        for _, row in df.iterrows():
            data_records.append({
                "date": row["date"].strftime("%Y-%m-%d"),
                "open": float(row["open"]), "close": float(row["close"]),
                "high": float(row["high"]), "low": float(row["low"]),
                "volume": int(row["volume"])
            })
            
        result = {"success": True, "data": data_records, "total": len(data_records), "timestamp": datetime.now().isoformat()}
        db_service.set_cache_data(cache_key, result, ttl=600)
        return result
    except Exception as e:
        return {"success": False, "msg": str(e)}

@router.get("/stocks/intraday")
async def get_intraday_data(
    symbol: str = Query(...),
    date: Optional[str] = None,
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """获取股票分时数据"""
    try:
        from app.services.data_source_factory import get_data_source_factory
        factory = await get_data_source_factory()
        if not date: date = datetime.now().strftime("%Y-%m-%d")
        result = await factory.get_data("data", "stocks/intraday", {"symbol": symbol, "date": date})
        return {"success": True, "data": result.get("data", []), "symbol": symbol, "date": date}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))