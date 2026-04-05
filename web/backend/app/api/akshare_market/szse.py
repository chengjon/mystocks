"""
深圳证券交易所数据路由 (SZSE Data)
"""
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from app.core.responses import ErrorCodes, create_error_response, create_success_response
from app.core.security import User, get_current_user
from .base import akshare_market_adapter

router = APIRouter()


def _success_response_spec(description: str, example: dict) -> dict[int, dict]:
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


def _error_response_spec(status_code: int, description: str, example: dict) -> dict[int, dict]:
    return {
        status_code: {
            "description": description,
            "content": {
                "application/json": {
                    "example": example,
                }
            },
        }
    }


SZSE_OVERVIEW_RESPONSES = {
    **_error_response_spec(
        404,
        "未找到指定日期的深交所市场总貌",
        {"success": False, "error_code": "DATA_NOT_FOUND", "message": "No SZSE overview for 2024-01-15"},
    ),
    **_error_response_spec(
        500,
        "深交所市场总貌查询失败",
        {"success": False, "error_code": "INTERNAL_ERROR", "message": "SZSE overview query failed"},
    ),
    **_success_response_spec(
        "深交所市场总貌数据",
        {
            "success": True,
            "data": {
                "data": [{"证券类别": "股票", "上市数": 2874, "总市值": 38650000000000.0}],
                "count": 1,
                "date": "2024-01-15",
                "timestamp": "2026-04-05T08:55:00",
                "source": "akshare",
                "exchange": "SZSE",
            },
        },
    ),
}

SZSE_AREA_TRADING_RESPONSES = {
    **_error_response_spec(
        404,
        "未找到指定日期的深市地区交易排行",
        {"success": False, "error_code": "DATA_NOT_FOUND", "message": "No SZSE area trading for 2024-01-15"},
    ),
    **_error_response_spec(
        500,
        "深市地区交易排行查询失败",
        {"success": False, "error_code": "INTERNAL_ERROR", "message": "SZSE area trading query failed"},
    ),
    **_success_response_spec(
        "深市地区交易排行数据",
        {
            "success": True,
            "data": {
                "data": [{"地区": "广东", "成交金额": 182300000000.0}],
                "count": 1,
                "date": "2024-01-15",
                "timestamp": "2026-04-05T08:55:00",
                "source": "akshare",
                "region": "SZSE",
            },
        },
    ),
}

SZSE_SECTOR_TRADING_RESPONSES = {
    **_error_response_spec(
        404,
        "未找到指定日期的深市行业成交数据",
        {"success": False, "error_code": "DATA_NOT_FOUND", "message": "No SZSE sector trading for BK0477 on 2024-01-15"},
    ),
    **_error_response_spec(
        500,
        "深市行业成交数据查询失败",
        {"success": False, "error_code": "INTERNAL_ERROR", "message": "SZSE sector trading query failed"},
    ),
    **_success_response_spec(
        "深市行业成交数据",
        {
            "success": True,
            "data": {
                "data": [{"证券代码": "000001", "证券简称": "平安银行", "成交金额": 2340000000.0}],
                "count": 1,
                "date": "2024-01-15",
                "symbol": "BK0477",
                "timestamp": "2026-04-05T08:55:00",
                "source": "akshare",
                "region": "SZSE",
            },
        },
    ),
}


@router.get(
    "/szse/overview",
    summary="获取深圳证券交易所市场总貌",
    description="按交易日查询深交所市场总貌统计，返回上市数量、市值等交易所级别概览信息。",
    responses=SZSE_OVERVIEW_RESPONSES,
)
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

@router.get(
    "/szse/area-trading",
    summary="获取深圳地区交易排序数据",
    description="按交易日查询深市各地区成交排行，用于观察 A 股区域资金活跃度和交易集中度。",
    responses=SZSE_AREA_TRADING_RESPONSES,
)
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

@router.get(
    "/szse/sector-trading",
    summary="获取深圳行业成交数据",
    description="按行业代码和交易日查询深市行业成交数据，用于板块热度监控和行业成交结构分析。",
    responses=SZSE_SECTOR_TRADING_RESPONSES,
)
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
