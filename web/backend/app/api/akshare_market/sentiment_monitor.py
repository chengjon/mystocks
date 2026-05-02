"""
行情与情绪监控路由 (Sentiment & Change Monitor)
"""

from typing import Any, Dict

from fastapi import APIRouter, Depends, Query

from app.core.responses import ErrorCodes, UnifiedResponse, create_error_response, create_success_response
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


STOCK_HOT_FOLLOW_XQ_RESPONSES = {
    **_error_response_spec(
        404,
        "未找到股票热度排行数据",
        {"success": False, "error_code": "DATA_NOT_FOUND", "message": "No hot-follow data found for scope 最热门"},
    ),
    **_error_response_spec(
        500,
        "股票热度排行查询失败",
        {"success": False, "error_code": "INTERNAL_ERROR", "message": "Failed to get stock hot-follow data for 最热门"},
    ),
    **_success_response_spec(
        "股票热度排行数据",
        {
            "success": True,
            "data": {
                "scope": "最热门",
                "data": [{"symbol": "600519", "stock_name": "贵州茅台", "follow_count": 128450, "latest_price": 1688.88}],
                "count": 1,
                "columns": ["symbol", "stock_name", "follow_count", "latest_price"],
                "source": "akshare",
                "provider": "xq",
            },
        },
    ),
}


STOCK_CHANGES_EM_RESPONSES = {
    **_error_response_spec(
        404,
        "未找到盘口异动数据",
        {"success": False, "error_code": "DATA_NOT_FOUND", "message": "No stock changes data found for type 大笔买入"},
    ),
    **_error_response_spec(
        500,
        "盘口异动查询失败",
        {"success": False, "error_code": "INTERNAL_ERROR", "message": "Failed to get stock changes data for 大笔买入"},
    ),
    **_success_response_spec(
        "盘口异动数据",
        {
            "success": True,
            "data": {
                "change_type": "大笔买入",
                "data": [{"change_time": "09:35:21", "symbol": "600519", "stock_name": "贵州茅台", "change_type": "大笔买入"}],
                "count": 1,
                "columns": ["change_time", "symbol", "stock_name", "change_type"],
                "source": "akshare",
                "provider": "em",
            },
        },
    ),
}


BOARD_CHANGE_EM_RESPONSES = {
    **_error_response_spec(
        404,
        "未找到板块异动数据",
        {"success": False, "error_code": "DATA_NOT_FOUND", "message": "No board change data found"},
    ),
    **_error_response_spec(
        500,
        "板块异动查询失败",
        {"success": False, "error_code": "INTERNAL_ERROR", "message": "Failed to get board change data"},
    ),
    **_success_response_spec(
        "板块异动数据",
        {
            "success": True,
            "data": {
                "data": [{"board_name": "证券", "change_percent": 3.25, "main_net_inflow": 1860000000.0}],
                "count": 1,
                "columns": ["board_name", "change_percent", "main_net_inflow"],
                "source": "akshare",
                "provider": "em",
                "data_type": "board_change",
            },
        },
    ),
}


@router.get(
    "/stock/hot-follow/xq",
    summary="获取股票热度排行",
    response_model=UnifiedResponse[Dict[str, Any]],
    responses=STOCK_HOT_FOLLOW_XQ_RESPONSES,
)
async def get_stock_hot_follow_xq(
    symbol: str = Query("最热门", description="热度榜类型，可选：最热门、本周新增", example="最热门"),
    current_user: User = Depends(get_current_user),
):
    """
    获取股票热度排行 (akshare.stock_hot_follow_xq)

    返回雪球维度的股票热度排行数据
    """
    try:
        df = await akshare_market_adapter.get_stock_hot_follow_xq(symbol)

        if df.empty:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No hot-follow data found for scope {symbol}"
            )

        result = {
            "scope": symbol,
            "data": df.to_dict("records"),
            "count": len(df),
            "columns": list(df.columns),
            "source": "akshare",
            "provider": "xq",
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get stock hot-follow data for {symbol}: {str(e)}"
        )


@router.get(
    "/stock/changes/em",
    summary="获取盘口异动",
    response_model=UnifiedResponse[Dict[str, Any]],
    responses=STOCK_CHANGES_EM_RESPONSES,
)
async def get_stock_changes_em(
    symbol: str = Query("大笔买入", description="盘口异动类型", example="大笔买入"),
    current_user: User = Depends(get_current_user),
):
    """
    获取盘口异动 (akshare.stock_changes_em)

    返回个股盘口异动明细数据
    """
    try:
        df = await akshare_market_adapter.get_stock_changes_em(symbol)

        if df.empty:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No stock changes data found for type {symbol}"
            )

        result = {
            "change_type": symbol,
            "data": df.to_dict("records"),
            "count": len(df),
            "columns": list(df.columns),
            "source": "akshare",
            "provider": "em",
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get stock changes data for {symbol}: {str(e)}"
        )


@router.get(
    "/board/change/em",
    summary="获取板块异动详情",
    response_model=UnifiedResponse[Dict[str, Any]],
    responses=BOARD_CHANGE_EM_RESPONSES,
)
async def get_board_change_em(
    current_user: User = Depends(get_current_user),
):
    """
    获取板块异动详情 (akshare.stock_board_change_em)

    返回全市场板块异动明细数据
    """
    try:
        df = await akshare_market_adapter.get_stock_board_change_em()

        if df.empty:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                "No board change data found"
            )

        result = {
            "data": df.to_dict("records"),
            "count": len(df),
            "columns": list(df.columns),
            "source": "akshare",
            "provider": "em",
            "data_type": "board_change",
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get board change data: {str(e)}"
        )
