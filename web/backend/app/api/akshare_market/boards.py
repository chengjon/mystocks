"""
板块与行业路由 (Boards & Sectors)
"""
from fastapi import APIRouter, Depends, Query
from app.core.responses import ErrorCodes, create_error_response, create_success_response
from app.core.security import User, get_current_user
from .base import akshare_market_adapter

router = APIRouter()

@router.get("/board/concept/cons/{symbol}", summary="获取概念板块成分股")
async def get_concept_board_constituents(
    symbol: str,
    current_user: User = Depends(get_current_user),
):
    """
    获取概念板块成分股 (akshare.stock_board_concept_cons_em)

    返回指定概念板块的成分股列表
    """
    try:
        df = await akshare_market_adapter.get_stock_board_concept_cons_em(symbol)

        if df.empty:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No concept board constituents found for symbol {symbol}"
            )

        result = {
            "symbol": symbol,
            "data": df.to_dict('records'),
            "count": len(df),
            "columns": list(df.columns),
            "source": "akshare",
            "provider": "em",
            "board_type": "concept"
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get concept board constituents for {symbol}: {str(e)}"
        )


@router.get("/board/concept/history/{symbol}", summary="获取概念板块行情")
async def get_concept_board_history(
    symbol: str,
    start_date: str = Query(None, description="开始日期", example="2024-01-01"),
    end_date: str = Query(None, description="结束日期", example="2024-01-05"),
    current_user: User = Depends(get_current_user),
):
    """
    获取概念板块行情 (akshare.stock_board_concept_hist_em)

    返回指定概念板块的历史行情数据
    """
    try:
        df = await akshare_market_adapter.get_stock_board_concept_hist_em(symbol, start_date, end_date)

        if df.empty:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No concept board history data found for symbol {symbol}"
            )

        result = {
            "symbol": symbol,
            "data": df.to_dict('records'),
            "count": len(df),
            "columns": list(df.columns),
            "date_range": {"start": start_date, "end": end_date} if start_date and end_date else None,
            "source": "akshare",
            "provider": "em",
            "board_type": "concept",
            "data_type": "daily"
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get concept board history for {symbol}: {str(e)}"
        )


@router.get("/board/concept/minute/{symbol}", summary="获取概念板块分钟行情")
async def get_concept_board_minute(
    symbol: str,
    current_user: User = Depends(get_current_user),
):
    """
    获取概念板块历史行情-分钟 (akshare.stock_board_concept_hist_min_em)

    返回指定概念板块的分钟行情数据
    """
    try:
        df = await akshare_market_adapter.get_stock_board_concept_hist_min_em(symbol)

        if df.empty:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No concept board minute data found for symbol {symbol}"
            )

        result = {
            "symbol": symbol,
            "data": df.to_dict('records'),
            "count": len(df),
            "columns": list(df.columns),
            "source": "akshare",
            "provider": "em",
            "board_type": "concept",
            "data_type": "minute"
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get concept board minute data for {symbol}: {str(e)}"
        )


@router.get("/board/industry/cons/{symbol}", summary="获取行业板块成分股")
async def get_industry_board_constituents(
    symbol: str,
    current_user: User = Depends(get_current_user),
):
    """
    获取行业板块成分股 (akshare.stock_board_industry_cons_em)

    返回指定行业板块的成分股列表
    """
    try:
        df = await akshare_market_adapter.get_stock_board_industry_cons_em(symbol)

        if df.empty:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No industry board constituents found for symbol {symbol}"
            )

        result = {
            "symbol": symbol,
            "data": df.to_dict('records'),
            "count": len(df),
            "columns": list(df.columns),
            "source": "akshare",
            "provider": "em",
            "board_type": "industry"
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get industry board constituents for {symbol}: {str(e)}"
        )


@router.get("/board/industry/history/{symbol}", summary="获取行业板块行情")
async def get_industry_board_history(
    symbol: str,
    start_date: str = Query(None, description="开始日期", example="2024-01-01"),
    end_date: str = Query(None, description="结束日期", example="2024-01-05"),
    current_user: User = Depends(get_current_user),
):
    """
    获取行业板块行情 (akshare.stock_board_industry_hist_em)

    返回指定行业板块的历史行情数据
    """
    try:
        df = await akshare_market_adapter.get_stock_board_industry_hist_em(symbol, start_date, end_date)

        if df.empty:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No industry board history data found for symbol {symbol}"
            )

        result = {
            "symbol": symbol,
            "data": df.to_dict('records'),
            "count": len(df),
            "columns": list(df.columns),
            "date_range": {"start": start_date, "end": end_date} if start_date and end_date else None,
            "source": "akshare",
            "provider": "em",
            "board_type": "industry",
            "data_type": "daily"
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get industry board history for {symbol}: {str(e)}"
        )


@router.get("/board/industry/minute/{symbol}", summary="获取行业板块分钟行情")
async def get_industry_board_minute(
    symbol: str,
    current_user: User = Depends(get_current_user),
):
    """
    获取行业板块历史行情-分钟 (akshare.stock_board_industry_hist_min_em)

    返回指定行业板块的分钟行情数据
    """
    try:
        df = await akshare_market_adapter.get_stock_board_industry_hist_min_em(symbol)

        if df.empty:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No industry board minute data found for symbol {symbol}"
            )

        result = {
            "symbol": symbol,
            "data": df.to_dict('records'),
            "count": len(df),
            "columns": list(df.columns),
            "source": "akshare",
            "provider": "em",
            "board_type": "industry",
            "data_type": "minute"
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get industry board minute data for {symbol}: {str(e)}"
        )


@router.get("/sector/hot-ranking", summary="获取热门行业排行")
async def get_sector_hot_ranking(
    current_user: User = Depends(get_current_user),
):
    """
    获取热门行业排行 (akshare.stock_sector_spot_em)

    返回全市场热门行业的排行数据
    """
    try:
        df = await akshare_market_adapter.get_stock_sector_spot_em()

        if df.empty:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                "No sector hot ranking data found"
            )

        result = {
            "data": df.to_dict('records'),
            "count": len(df),
            "columns": list(df.columns),
            "source": "akshare",
            "provider": "em",
            "ranking_type": "hot_sector"
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get sector hot ranking: {str(e)}"
        )


@router.get("/sector/fund-flow-ranking", summary="获取行业资金流向")
async def get_sector_fund_flow_ranking(
    current_user: User = Depends(get_current_user),
):
    """
    获取行业资金流向 (akshare.stock_sector_fund_flow_rank_em)

    返回全市场行业资金流向排行数据
    """
    try:
        df = await akshare_market_adapter.get_stock_sector_fund_flow_rank_em()

        if df.empty:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                "No sector fund flow ranking data found"
            )

        result = {
            "data": df.to_dict('records'),
            "count": len(df),
            "columns": list(df.columns),
            "source": "akshare",
            "provider": "em",
            "ranking_type": "fund_flow"
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get sector fund flow ranking: {str(e)}"
        )


# ============================================================================
# 上海交易所每日概况
# ============================================================================

