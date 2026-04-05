"""
上海证券交易所数据路由 (SSE Data)
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


SSE_OVERVIEW_RESPONSES = {
    **_error_response_spec(
        404,
        "未找到上交所市场总貌数据",
        {"success": False, "error_code": "DATA_NOT_FOUND", "message": "No SSE overview data found"},
    ),
    **_error_response_spec(
        500,
        "上交所市场总貌查询失败",
        {"success": False, "error_code": "INTERNAL_ERROR", "message": "SSE overview query failed"},
    ),
    **_success_response_spec(
        "上交所市场总貌数据",
        {
            "success": True,
            "data": {
                "data": [{"证券类别": "股票", "上市数": 2267, "总市值": 51230000000000.0}],
                "count": 1,
                "columns": ["证券类别", "上市数", "总市值"],
                "timestamp": "2026-04-05T08:55:00",
                "source": "akshare",
                "exchange": "SSE",
            },
        },
    ),
}

SSE_DAILY_DEAL_RESPONSES = {
    **_error_response_spec(
        404,
        "未找到指定日期的上交所每日概况",
        {"success": False, "error_code": "DATA_NOT_FOUND", "message": "No SSE daily deal found for 2024-01-15"},
    ),
    **_error_response_spec(
        500,
        "上交所每日概况查询失败",
        {"success": False, "error_code": "INTERNAL_ERROR", "message": "SSE daily deal query failed"},
    ),
    **_success_response_spec(
        "上交所每日概况数据",
        {
            "success": True,
            "data": {
                "data": [{"项目": "成交金额", "数值": 428900000000.0}],
                "count": 1,
                "date": "2024-01-15",
                "timestamp": "2026-04-05T08:55:00",
                "source": "akshare",
                "exchange": "SSE",
            },
        },
    ),
}


@router.get(
    "/sse/overview",
    summary="获取上海证券交易所市场总貌",
    description="查询上交所市场总貌统计，返回上市数量、市值等总览信息，用于 A 股交易所级别盘面概览。",
    responses=SSE_OVERVIEW_RESPONSES,
)
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

@router.get(
    "/sse/daily-deal",
    summary="获取上海交易所每日概况",
    description="按交易日查询上交所每日概况数据，返回成交额等交易所级统计，用于市场日度复盘。",
    responses=SSE_DAILY_DEAL_RESPONSES,
)
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
