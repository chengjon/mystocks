"""个股信息与新闻路由 (Stock Info & News)"""

import asyncio

from fastapi import APIRouter, Depends, Query

from app.core.config import settings
from app.core.responses import ErrorCodes, create_error_response, create_success_response
from app.core.security import User, get_current_user
from src.services.openstock import OpenStockClient, DataCategory

from .base import akshare_market_adapter  # OPENSTOCK_GAP: xq/ths/rating


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


@router.get("/stock/individual-info/em", summary="获取个股信息查询-东财")
async def get_stock_individual_info_em(
    symbol: str = Query(..., description="股票代码", example="000001"),
    current_user: User = Depends(get_current_user),
):
    """获取个股信息 (OpenStock F10_DATA stock_info)

    返回个股基本信息，包括公司概况、财务数据、行业分类等
    """
    try:
        result = await asyncio.to_thread(
            _get_client().fetch,
            DataCategory.F10_DATA,
            {"symbol": symbol, "f10_type": "stock_info"},
        )

        data = result.get("data", [])
        if not data:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No individual info found for stock {symbol}",
            )

        result = {
            "symbol": symbol,
            "data": data,
            "count": len(data),
            "columns": list(data[0].keys()) if data else [],
            "source": "openstock",
            "provider": "openstock_gateway",
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get stock individual info for {symbol}: {e!s}",
        )


@router.get("/stock/individual-info/xq", summary="获取个股信息查询-雪球")
async def get_stock_individual_info_xq(
    symbol: str = Query(..., description="股票代码", example="SZ000001"),
    current_user: User = Depends(get_current_user),
):
    """获取个股信息查询-雪球 (akshare.stock_individual_basic_info_xq)

    OPENSTOCK_GAP: 雪球平台专属数据源, OpenStock 无对应 category.
    保留原 adapter 调用, 待 OpenStock 实现后迁移.
    """
    try:
        info_dict = await akshare_market_adapter.get_stock_individual_basic_info_xq(symbol)

        if "error" in info_dict:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No individual info found for stock {symbol}: {info_dict.get('error')}",
            )

        result = {
            "symbol": symbol,
            "data": info_dict,
            "source": "akshare",
            "provider": "xq",
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get stock individual info from Xueqiu for {symbol}: {e!s}",
        )


@router.get("/stock/business-intro/ths", summary="获取主营介绍-同花顺")
async def get_stock_business_intro_ths(
    symbol: str = Query(..., description="股票代码", example="000001"),
    current_user: User = Depends(get_current_user),
):
    """获取主营介绍-同花顺 (akshare.stock_zyjs_ths)

    OPENSTOCK_GAP: 同花顺平台专属数据源, OpenStock 无对应 category.
    保留原 adapter 调用, 待 OpenStock 实现后迁移.
    """
    try:
        info_dict = await akshare_market_adapter.get_stock_zyjs_ths(symbol)

        if "error" in info_dict:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No business intro found for stock {symbol}: {info_dict.get('error')}",
            )

        result = {
            "symbol": symbol,
            "data": info_dict,
            "source": "akshare",
            "provider": "ths",
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get business intro from THS for {symbol}: {e!s}",
        )


@router.get("/stock/business-composition/em", summary="获取主营构成-东财")
async def get_stock_business_composition_em(
    symbol: str = Query(..., description="股票代码", example="000001"),
    current_user: User = Depends(get_current_user),
):
    """获取主营构成 (OpenStock F10_DATA business_composition)

    返回东财的主营构成数据
    """
    try:
        result = await asyncio.to_thread(
            _get_client().fetch,
            DataCategory.F10_DATA,
            {"symbol": symbol, "f10_type": "business_composition"},
        )

        data = result.get("data", [])
        if not data:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No business composition data found for stock {symbol}",
            )

        result = {
            "symbol": symbol,
            "data": data,
            "count": len(data),
            "columns": list(data[0].keys()) if data else [],
            "source": "openstock",
            "provider": "openstock_gateway",
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get business composition for {symbol}: {e!s}",
        )


@router.get("/stock/comment/em", summary="获取千股千评")
async def get_stock_comment_em(
    symbol: str = Query(..., description="股票代码", example="000001"),
    current_user: User = Depends(get_current_user),
):
    """获取千股千评 (akshare.stock_comment_em)

    OPENSTOCK_GAP: OpenStock STOCK_RATING(eltdx) 返回空; 东财千股千评为独立数据源.
    保留原 adapter 调用, 待 OpenStock 实现后迁移.
    """
    try:
        df = await akshare_market_adapter.get_stock_comment_em(symbol)

        if df.empty:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No comment data found for stock {symbol}",
            )

        result = {
            "symbol": symbol,
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
            f"Failed to get stock comment for {symbol}: {e!s}",
        )


@router.get("/stock/comment-detail/em", summary="获取千股千评详情-机构评级")
async def get_stock_comment_detail_em(
    symbol: str = Query(..., description="股票代码", example="000001"),
    current_user: User = Depends(get_current_user),
):
    """获取千股千评详情-机构评级 (akshare.stock_comment_detail_zlkp_jgcyd_em)

    OPENSTOCK_GAP: OpenStock STOCK_RATING(eltdx) 返回空; 东财机构评级为独立数据源.
    保留原 adapter 调用, 待 OpenStock 实现后迁移.
    """
    try:
        df = await akshare_market_adapter.get_stock_comment_detail_zlkp_jgcyd_em(symbol)

        if df.empty:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No comment detail data found for stock {symbol}",
            )

        result = {
            "symbol": symbol,
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
            f"Failed to get stock comment detail for {symbol}: {e!s}",
        )


@router.get("/stock/news/em", summary="获取个股新闻")
async def get_stock_news_em(
    symbol: str = Query(..., description="股票代码", example="000001"),
    current_user: User = Depends(get_current_user),
):
    """获取个股新闻 (OpenStock STOCK_NEWS)

    返回个股相关的新闻数据
    """
    try:
        result = await asyncio.to_thread(
            _get_client().fetch,
            DataCategory.STOCK_NEWS,
            {"symbol": symbol},
        )

        data = result.get("data", [])
        if not data:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No news data found for stock {symbol}",
            )

        result = {
            "symbol": symbol,
            "data": data,
            "count": len(data),
            "columns": list(data[0].keys()) if data else [],
            "source": "openstock",
            "provider": "openstock_gateway",
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get stock news for {symbol}: {e!s}",
        )


@router.get("/stock/bid-ask/em", summary="获取行情报价-五档报价")
async def get_stock_bid_ask_em(
    symbol: str = Query(..., description="股票代码", example="000001"),
    current_user: User = Depends(get_current_user),
):
    """获取行情报价-五档报价 (OpenStock MARKET_DEPTH)

    返回个股的五档买卖报价数据
    """
    try:
        result = await asyncio.to_thread(
            _get_client().fetch,
            DataCategory.MARKET_DEPTH,
            {"symbol": symbol},
        )

        data = result.get("data", [])
        if not data:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No bid-ask data found for stock {symbol}",
            )

        result = {
            "symbol": symbol,
            "data": data,
            "count": len(data),
            "columns": list(data[0].keys()) if data else [],
            "source": "openstock",
            "provider": "openstock_gateway",
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get bid-ask data for {symbol}: {e!s}",
        )


# ============================================================================
# Phase 3: 资金流向数据API
# ============================================================================