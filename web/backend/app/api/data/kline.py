"""
K线与行情数据路由 (KLine Data)
"""
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import pandas as pd
from fastapi import APIRouter, Depends, Query

from app.core.database import db_service
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


KLINE_ERROR_RESPONSES = {
    422: COMMON_RESPONSES[422],
    500: COMMON_RESPONSES[500],
}

DAILY_KLINE_RESPONSES = {
    **KLINE_ERROR_RESPONSES,
    **_success_response_spec(
        "股票日线行情结果",
        {
            "success": True,
            "data": [
                {
                    "date": "2026-04-03",
                    "open": 1702.1,
                    "close": 1710.88,
                    "high": 1718.0,
                    "low": 1695.5,
                    "volume": 325800,
                }
            ],
            "symbol": "600519",
            "total": 1,
            "timestamp": "2026-04-04T14:10:00",
        },
    ),
}

KLINE_ALIAS_RESPONSES = {
    **KLINE_ERROR_RESPONSES,
    **_success_response_spec(
        "股票 K 线别名结果",
        {
            "success": True,
            "data": [
                {
                    "date": "2026-04-03",
                    "open": 1702.1,
                    "close": 1710.88,
                    "high": 1718.0,
                    "low": 1695.5,
                    "volume": 325800,
                }
            ],
            "symbol": "600519",
            "total": 1,
            "timestamp": "2026-04-04T14:10:00",
        },
    ),
}

STANDARD_KLINE_RESPONSES = {
    **KLINE_ERROR_RESPONSES,
    **_success_response_spec(
        "标准化股票 K 线结果",
        {
            "success": True,
            "data": [
                {
                    "date": "2026-04-01",
                    "open": 1688.0,
                    "close": 1699.5,
                    "high": 1701.2,
                    "low": 1678.3,
                    "volume": 412300,
                },
                {
                    "date": "2026-04-02",
                    "open": 1700.0,
                    "close": 1708.2,
                    "high": 1713.6,
                    "low": 1692.4,
                    "volume": 389100,
                },
            ],
            "total": 2,
            "timestamp": "2026-04-04T14:10:00",
        },
    ),
}

INTRADAY_RESPONSES = {
    **KLINE_ERROR_RESPONSES,
    **_success_response_spec(
        "股票分时行情结果",
        {
            "success": True,
            "data": [
                {"time": "09:30:00", "price": 1701.2, "volume": 3200},
                {"time": "09:31:00", "price": 1702.8, "volume": 2800},
            ],
            "symbol": "600519",
            "date": "2026-04-04",
        },
    ),
}


@router.get(
    "/stocks/daily",
    summary="查询股票日线行情",
    description="查询股票日线行情，支持日期范围过滤，并在未传日期时回退到最近默认窗口。",
    responses=DAILY_KLINE_RESPONSES,
)
async def get_daily_kline(
    symbol: str = Query(..., description="股票代码。"),
    start_date: Optional[str] = Query(None, description="返回结果的开始日期，格式为 YYYY-MM-DD。"),
    end_date: Optional[str] = Query(None, description="返回结果的结束日期，格式为 YYYY-MM-DD。"),
    limit: int = Query(100, description="单次请求返回的最大日线记录数。"),
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

@router.get(
    "/kline",
    summary="查询股票 K 线别名接口",
    description="查询股票 K 线别名接口，行为与股票日线查询保持一致，便于兼容旧调用方。",
    responses=KLINE_ALIAS_RESPONSES,
)
async def get_kline(
    symbol: str = Query(..., description="股票代码。"),
    start_date: Optional[str] = Query(None, description="返回结果的开始日期，格式为 YYYY-MM-DD。"),
    end_date: Optional[str] = Query(None, description="返回结果的结束日期，格式为 YYYY-MM-DD。"),
    limit: int = Query(100, description="单次请求返回的最大 K 线记录数。"),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """获取股票K线数据（日线别名）"""
    return await get_daily_kline(symbol, start_date, end_date, limit, current_user)

@router.get(
    "/stocks/kline",
    summary="查询标准化股票 K 线",
    description="返回标准化股票 K 线结构，适用于图表组件和统一行情消费端直接使用。",
    responses=STANDARD_KLINE_RESPONSES,
)
async def get_kline_data(
    symbol: str = Query(..., description="股票代码。"),
    start_date: str = Query(..., description="查询开始日期，格式为 YYYY-MM-DD。"),
    end_date: str = Query(..., description="查询结束日期，格式为 YYYY-MM-DD。"),
    period: str = Query("day", description="K 线周期，当前接口默认支持 day。"),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """标准化K线数据接口"""
    try:
        cache_key = f"kline:{symbol}:{start_date}:{end_date}:{period}"
        cached_data = db_service.get_cache_data(cache_key)
        if cached_data:
            return cached_data

        df = db_service.query_daily_kline(symbol, start_date, end_date)
        if df.empty:
            return {"success": True, "data": [], "total": 0}

        df["date"] = pd.to_datetime(df["trade_date"] if "trade_date" in df.columns else df["date"])
        df = df.sort_values("date")

        # Format conversion
        data_records = []
        for _, row in df.iterrows():
            data_records.append(
                {
                    "date": row["date"].strftime("%Y-%m-%d"),
                    "open": float(row["open"]),
                    "close": float(row["close"]),
                    "high": float(row["high"]),
                    "low": float(row["low"]),
                    "volume": int(row["volume"]),
                }
            )

        result = {
            "success": True,
            "data": data_records,
            "total": len(data_records),
            "timestamp": datetime.now().isoformat(),
        }
        db_service.set_cache_data(cache_key, result, ttl=600)
        return result
    except Exception as e:
        raise BusinessException(detail=f"获取标准化K线数据失败: {str(e)}", status_code=500, error_code="DATABASE_ERROR")

@router.get(
    "/stocks/intraday",
    summary="查询股票分时行情",
    description="返回指定交易日的分钟级分时行情，适用于盘中走势展示和实时监控场景。",
    responses=INTRADAY_RESPONSES,
)
async def get_intraday_data(
    symbol: str = Query(..., description="股票代码。"),
    date: Optional[str] = Query(None, description="交易日期，格式为 YYYY-MM-DD；不传时默认取当天。"),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """获取股票分时数据"""
    try:
        from app.services.data_source_factory import get_data_source_factory
        factory = await get_data_source_factory()
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        result = await factory.get_data("data", "stocks/intraday", {"symbol": symbol, "date": date})
        return {"success": True, "data": result.get("data", []), "symbol": symbol, "date": date}
    except Exception as e:
        raise BusinessException(detail=f"获取分时行情失败: {str(e)}", status_code=500, error_code="DATA_RETRIEVAL_FAILED")
