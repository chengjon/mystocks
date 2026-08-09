"""板块与行业路由 (Boards & Sectors)"""

import asyncio

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


@router.get("/board/concept/cons/{symbol}", summary="获取概念板块成分股")
async def get_concept_board_constituents(
    symbol: str,
    current_user: User = Depends(get_current_user),
):
    """获取概念板块成分股 (OpenStock SECTOR_CONSTITUENTS)

    返回指定概念板块的成分股列表
    """
    try:
        result = await asyncio.to_thread(
            _get_client().fetch,
            DataCategory.SECTOR_CONSTITUENTS,
            {"sector_type": "concept", "sector": symbol},
        )

        data = result.get("data", [])
        if not data:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No concept board constituents found for symbol {symbol}",
            )

        result = {
            "symbol": symbol,
            "data": data,
            "count": len(data),
            "columns": list(data[0].keys()) if data else [],
            "source": "openstock",
            "provider": "openstock_gateway",
            "board_type": "concept",
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get concept board constituents for {symbol}: {e!s}",
        )


@router.get("/board/concept/history/{symbol}", summary="获取概念板块行情")
async def get_concept_board_history(
    symbol: str,
    start_date: str = Query(None, description="开始日期", example="2024-01-01"),
    end_date: str = Query(None, description="结束日期", example="2024-01-05"),
    current_user: User = Depends(get_current_user),
):
    """获取概念板块行情 (OpenStock SECTOR_KLINES)

    返回指定概念板块的历史行情数据
    """
    try:
        params = {"sector_type": "concept", "sector": symbol, "period": "daily"}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date

        result = await asyncio.to_thread(
            _get_client().fetch,
            DataCategory.SECTOR_KLINES,
            params,
        )

        data = result.get("data", [])
        if not data:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No concept board history data found for symbol {symbol}",
            )

        result = {
            "symbol": symbol,
            "data": data,
            "count": len(data),
            "columns": list(data[0].keys()) if data else [],
            "date_range": {"start": start_date, "end": end_date} if start_date and end_date else None,
            "source": "openstock",
            "provider": "openstock_gateway",
            "board_type": "concept",
            "data_type": "daily",
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get concept board history for {symbol}: {e!s}",
        )


@router.get("/board/concept/minute/{symbol}", summary="获取概念板块分钟行情")
async def get_concept_board_minute(
    symbol: str,
    current_user: User = Depends(get_current_user),
):
    """获取概念板块分钟行情 (OpenStock SECTOR_KLINES period=minute)

    返回指定概念板块的分钟级行情数据。
    """
    try:
        result = await asyncio.to_thread(
            _get_client().fetch,
            DataCategory.SECTOR_KLINES,
            {"sector_type": "concept", "sector": symbol, "period": "minute"},
        )

        data = result.get("data", [])
        if not data:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No concept board minute data found for symbol {symbol}",
            )

        result = {
            "symbol": symbol,
            "data": data,
            "count": len(data),
            "columns": list(data[0].keys()) if data else [],
            "source": "openstock",
            "provider": "openstock_gateway",
            "board_type": "concept",
            "data_type": "minute",
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get concept board minute data for {symbol}: {e!s}",
        )


@router.get("/board/industry/cons/{symbol}", summary="获取行业板块成分股")
async def get_industry_board_constituents(
    symbol: str,
    current_user: User = Depends(get_current_user),
):
    """获取行业板块成分股 (OpenStock SECTOR_CONSTITUENTS)

    返回指定行业板块的成分股列表
    """
    try:
        result = await asyncio.to_thread(
            _get_client().fetch,
            DataCategory.SECTOR_CONSTITUENTS,
            {"sector_type": "industry", "sector": symbol},
        )

        data = result.get("data", [])
        if not data:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No industry board constituents found for symbol {symbol}",
            )

        result = {
            "symbol": symbol,
            "data": data,
            "count": len(data),
            "columns": list(data[0].keys()) if data else [],
            "source": "openstock",
            "provider": "openstock_gateway",
            "board_type": "industry",
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get industry board constituents for {symbol}: {e!s}",
        )


@router.get("/board/industry/history/{symbol}", summary="获取行业板块行情")
async def get_industry_board_history(
    symbol: str,
    start_date: str = Query(None, description="开始日期", example="2024-01-01"),
    end_date: str = Query(None, description="结束日期", example="2024-01-05"),
    current_user: User = Depends(get_current_user),
):
    """获取行业板块行情 (OpenStock SECTOR_KLINES)

    返回指定行业板块的历史行情数据
    """
    try:
        params = {"sector_type": "industry", "sector": symbol, "period": "daily"}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date

        result = await asyncio.to_thread(
            _get_client().fetch,
            DataCategory.SECTOR_KLINES,
            params,
        )

        data = result.get("data", [])
        if not data:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No industry board history data found for symbol {symbol}",
            )

        result = {
            "symbol": symbol,
            "data": data,
            "count": len(data),
            "columns": list(data[0].keys()) if data else [],
            "date_range": {"start": start_date, "end": end_date} if start_date and end_date else None,
            "source": "openstock",
            "provider": "openstock_gateway",
            "board_type": "industry",
            "data_type": "daily",
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get industry board history for {symbol}: {e!s}",
        )


@router.get("/board/industry/minute/{symbol}", summary="获取行业板块分钟行情")
async def get_industry_board_minute(
    symbol: str,
    current_user: User = Depends(get_current_user),
):
    """获取行业板块分钟行情 (OpenStock SECTOR_KLINES period=minute)

    返回指定行业板块的分钟级行情数据。
    """
    try:
        result = await asyncio.to_thread(
            _get_client().fetch,
            DataCategory.SECTOR_KLINES,
            {"sector_type": "industry", "sector": symbol, "period": "minute"},
        )

        data = result.get("data", [])
        if not data:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No industry board minute data found for symbol {symbol}",
            )

        result = {
            "symbol": symbol,
            "data": data,
            "count": len(data),
            "columns": list(data[0].keys()) if data else [],
            "source": "openstock",
            "provider": "openstock_gateway",
            "board_type": "industry",
            "data_type": "minute",
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get industry board minute data for {symbol}: {e!s}",
        )


@router.get("/sector/hot-ranking", summary="获取热门行业排行")
async def get_sector_hot_ranking(
    current_user: User = Depends(get_current_user),
):
    """获取热门行业排行 (OpenStock SECTOR_QUOTES)

    返回全市场热门行业的排行数据
    """
    try:
        result = await asyncio.to_thread(
            _get_client().fetch,
            DataCategory.SECTOR_QUOTES,
            {"sector_type": "industry"},
        )

        data = result.get("data", [])
        if not data:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                "No sector hot ranking data found",
            )

        result = {
            "data": data,
            "count": len(data),
            "columns": list(data[0].keys()) if data else [],
            "source": "openstock",
            "provider": "openstock_gateway",
            "ranking_type": "hot_sector",
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get sector hot ranking: {e!s}",
        )


@router.get("/sector/fund-flow-ranking", summary="获取行业资金流向")
async def get_sector_fund_flow_ranking(
    current_user: User = Depends(get_current_user),
):
    """获取行业资金流向 (OpenStock SECTOR_FUND_FLOW)

    返回全市场行业资金流向排行数据
    """
    try:
        result = await asyncio.to_thread(
            _get_client().fetch,
            DataCategory.SECTOR_FUND_FLOW,
            {"sector_type": "industry"},
        )

        data = result.get("data", [])
        if not data:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                "No sector fund flow ranking data found",
            )

        result = {
            "data": data,
            "count": len(data),
            "columns": list(data[0].keys()) if data else [],
            "source": "openstock",
            "provider": "openstock_gateway",
            "ranking_type": "fund_flow",
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get sector fund flow ranking: {e!s}",
        )


# ============================================================================
# 上海交易所每日概况
# ============================================================================
