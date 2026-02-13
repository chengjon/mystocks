"""
个股信息与新闻路由 (Stock Info & News)
"""
from fastapi import APIRouter, Depends, Query
from app.core.responses import ErrorCodes, create_error_response, create_success_response
from app.core.security import User, get_current_user
from .base import akshare_market_adapter

router = APIRouter()

@router.get("/stock/individual-info/em", summary="获取个股信息查询-东财")
async def get_stock_individual_info_em(
    symbol: str = Query(..., description="股票代码", example="000001"),
    current_user: User = Depends(get_current_user),
):
    """
    获取个股信息查询-东财 (akshare.stock_individual_info_em)

    返回个股基本信息，包括公司概况、财务数据、行业分类等
    """
    try:
        info_dict = await akshare_market_adapter.get_stock_individual_info_em(symbol)

        if "error" in info_dict:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No individual info found for stock {symbol}: {info_dict.get('error')}"
            )

        result = {
            "symbol": symbol,
            "data": info_dict,
            "source": "akshare",
            "provider": "em"
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get stock individual info for {symbol}: {str(e)}"
        )


@router.get("/stock/individual-info/xq", summary="获取个股信息查询-雪球")
async def get_stock_individual_info_xq(
    symbol: str = Query(..., description="股票代码", example="SZ000001"),
    current_user: User = Depends(get_current_user),
):
    """
    获取个股信息查询-雪球 (akshare.stock_individual_basic_info_xq)

    返回雪球平台的个股基本信息
    """
    try:
        info_dict = await akshare_market_adapter.get_stock_individual_basic_info_xq(symbol)

        if "error" in info_dict:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No individual info found for stock {symbol}: {info_dict.get('error')}"
            )

        result = {
            "symbol": symbol,
            "data": info_dict,
            "source": "akshare",
            "provider": "xq"
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get stock individual info from Xueqiu for {symbol}: {str(e)}"
        )


@router.get("/stock/business-intro/ths", summary="获取主营介绍-同花顺")
async def get_stock_business_intro_ths(
    symbol: str = Query(..., description="股票代码", example="000001"),
    current_user: User = Depends(get_current_user),
):
    """
    获取主营介绍-同花顺 (akshare.stock_zyjs_ths)

    返回同花顺的主营介绍信息
    """
    try:
        info_dict = await akshare_market_adapter.get_stock_zyjs_ths(symbol)

        if "error" in info_dict:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No business intro found for stock {symbol}: {info_dict.get('error')}"
            )

        result = {
            "symbol": symbol,
            "data": info_dict,
            "source": "akshare",
            "provider": "ths"
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get business intro from THS for {symbol}: {str(e)}"
        )


@router.get("/stock/business-composition/em", summary="获取主营构成-东财")
async def get_stock_business_composition_em(
    symbol: str = Query(..., description="股票代码", example="000001"),
    current_user: User = Depends(get_current_user),
):
    """
    获取主营构成-东财 (akshare.stock_zygc_em)

    返回东财的主营构成数据
    """
    try:
        df = await akshare_market_adapter.get_stock_zygc_em(symbol)

        if df.empty:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No business composition data found for stock {symbol}"
            )

        result = {
            "symbol": symbol,
            "data": df.to_dict('records'),
            "count": len(df),
            "columns": list(df.columns),
            "source": "akshare",
            "provider": "em"
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get business composition from EM for {symbol}: {str(e)}"
        )


@router.get("/stock/comment/em", summary="获取千股千评")
async def get_stock_comment_em(
    symbol: str = Query(..., description="股票代码", example="000001"),
    current_user: User = Depends(get_current_user),
):
    """
    获取千股千评 (akshare.stock_comment_em)

    返回个股的分析师评级汇总数据
    """
    try:
        df = await akshare_market_adapter.get_stock_comment_em(symbol)

        if df.empty:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No comment data found for stock {symbol}"
            )

        result = {
            "symbol": symbol,
            "data": df.to_dict('records'),
            "count": len(df),
            "columns": list(df.columns),
            "source": "akshare",
            "provider": "em"
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get stock comment for {symbol}: {str(e)}"
        )


@router.get("/stock/comment-detail/em", summary="获取千股千评详情-机构评级")
async def get_stock_comment_detail_em(
    symbol: str = Query(..., description="股票代码", example="000001"),
    current_user: User = Depends(get_current_user),
):
    """
    获取千股千评详情-机构评级 (akshare.stock_comment_detail_zlkp_jgcyd_em)

    返回个股的详细机构评级数据
    """
    try:
        df = await akshare_market_adapter.get_stock_comment_detail_zlkp_jgcyd_em(symbol)

        if df.empty:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No comment detail data found for stock {symbol}"
            )

        result = {
            "symbol": symbol,
            "data": df.to_dict('records'),
            "count": len(df),
            "columns": list(df.columns),
            "source": "akshare",
            "provider": "em"
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get stock comment detail for {symbol}: {str(e)}"
        )


@router.get("/stock/news/em", summary="获取个股新闻")
async def get_stock_news_em(
    symbol: str = Query(..., description="股票代码", example="000001"),
    current_user: User = Depends(get_current_user),
):
    """
    获取个股新闻 (akshare.stock_news_em)

    返回个股相关的新闻数据
    """
    try:
        df = await akshare_market_adapter.get_stock_news_em(symbol)

        if df.empty:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No news data found for stock {symbol}"
            )

        result = {
            "symbol": symbol,
            "data": df.to_dict('records'),
            "count": len(df),
            "columns": list(df.columns),
            "source": "akshare",
            "provider": "em"
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get stock news for {symbol}: {str(e)}"
        )


@router.get("/stock/bid-ask/em", summary="获取行情报价-五档报价")
async def get_stock_bid_ask_em(
    symbol: str = Query(..., description="股票代码", example="000001"),
    current_user: User = Depends(get_current_user),
):
    """
    获取行情报价-五档报价 (akshare.stock_bid_ask_em)

    返回个股的五档买卖报价数据
    """
    try:
        df = await akshare_market_adapter.get_stock_bid_ask_em(symbol)

        if df.empty:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No bid-ask data found for stock {symbol}"
            )

        result = {
            "symbol": symbol,
            "data": df.to_dict('records'),
            "count": len(df),
            "columns": list(df.columns),
            "source": "akshare",
            "provider": "em"
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get bid-ask data for {symbol}: {str(e)}"
        )


# ============================================================================
# Phase 3: 资金流向数据API
# ============================================================================

