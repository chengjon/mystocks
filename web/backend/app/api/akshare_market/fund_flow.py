"""
资金流向路由 (Fund Flow)
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query
from app.core.responses import ErrorCodes, create_error_response, create_success_response
from app.core.security import User, get_current_user
from .base import akshare_market_adapter

router = APIRouter()

@router.get("/fund-flow/hsgt-summary", summary="获取沪深港通资金流向汇总")
async def get_hsgt_fund_flow_summary(
    start_date: str = Query(..., description="开始日期", example="2024-01-01"),
    end_date: str = Query(..., description="结束日期", example="2024-01-05"),
    current_user: User = Depends(get_current_user),
):
    """
    获取沪深港通资金流向汇总 (akshare.stock_hsgt_fund_flow_summary_em)

    返回北向资金、南向资金的每日流向汇总数据
    """
    try:
        df = await akshare_market_adapter.get_stock_hsgt_fund_flow_summary_em(start_date, end_date)

        if df.empty:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No HSGT fund flow summary data found for date range {start_date} to {end_date}"
            )

        result = {
            "data": df.to_dict('records'),
            "count": len(df),
            "columns": list(df.columns),
            "date_range": {"start": start_date, "end": end_date},
            "source": "akshare",
            "provider": "em"
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get HSGT fund flow summary: {str(e)}"
        )


@router.get("/fund-flow/hsgt-detail", summary="获取沪深港通资金流向明细")
async def get_hsgt_fund_flow_detail(
    start_date: str = Query(..., description="开始日期", example="2024-01-01"),
    end_date: str = Query(..., description="结束日期", example="2024-01-05"),
    current_user: User = Depends(get_current_user),
):
    """
    获取沪深港通资金流向明细 (akshare.stock_hsgt_fund_flow_detail_em)

    返回沪深港通资金流向的详细分类数据
    """
    try:
        df = await akshare_market_adapter.get_stock_hsgt_fund_flow_detail_em(start_date, end_date)

        if df.empty:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No HSGT fund flow detail data found for date range {start_date} to {end_date}"
            )

        result = {
            "data": df.to_dict('records'),
            "count": len(df),
            "columns": list(df.columns),
            "date_range": {"start": start_date, "end": end_date},
            "source": "akshare",
            "provider": "em"
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get HSGT fund flow detail: {str(e)}"
        )


@router.get("/fund-flow/north-daily", summary="获取北向资金每日统计")
async def get_north_fund_daily(
    start_date: str = Query(..., description="开始日期", example="2024-01-01"),
    end_date: str = Query(..., description="结束日期", example="2024-01-05"),
    current_user: User = Depends(get_current_user),
):
    """
    获取北向资金每日统计 (akshare.stock_hsgt_north_net_flow_in_em)

    返回北向资金每日流入流出统计数据
    """
    try:
        df = await akshare_market_adapter.get_stock_hsgt_north_net_flow_in_em(start_date, end_date)

        if df.empty:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No north fund daily data found for date range {start_date} to {end_date}"
            )

        result = {
            "data": df.to_dict('records'),
            "count": len(df),
            "columns": list(df.columns),
            "date_range": {"start": start_date, "end": end_date},
            "fund_direction": "north",
            "source": "akshare",
            "provider": "em"
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get north fund daily data: {str(e)}"
        )


@router.get("/fund-flow/south-daily", summary="获取南向资金每日统计")
async def get_south_fund_daily(
    start_date: str = Query(..., description="开始日期", example="2024-01-01"),
    end_date: str = Query(..., description="结束日期", example="2024-01-05"),
    current_user: User = Depends(get_current_user),
):
    """
    获取南向资金每日统计 (akshare.stock_hsgt_south_net_flow_in_em)

    返回南向资金每日流入流出统计数据
    """
    try:
        df = await akshare_market_adapter.get_stock_hsgt_south_net_flow_in_em(start_date, end_date)

        if df.empty:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No south fund daily data found for date range {start_date} to {end_date}"
            )

        result = {
            "data": df.to_dict('records'),
            "count": len(df),
            "columns": list(df.columns),
            "date_range": {"start": start_date, "end": end_date},
            "fund_direction": "south",
            "source": "akshare",
            "provider": "em"
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get south fund daily data: {str(e)}"
        )


@router.get("/fund-flow/north-stock/{symbol}", summary="获取北向资金个股统计")
async def get_north_fund_stock(
    symbol: str,
    current_user: User = Depends(get_current_user),
):
    """
    获取北向资金个股统计 (akshare.stock_hsgt_north_acc_flow_in_em)

    返回指定股票的北向资金持股情况
    """
    try:
        df = await akshare_market_adapter.get_stock_hsgt_north_acc_flow_in_em(symbol)

        if df.empty:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No north fund stock data found for symbol {symbol}"
            )

        result = {
            "symbol": symbol,
            "data": df.to_dict('records'),
            "count": len(df),
            "columns": list(df.columns),
            "fund_direction": "north",
            "source": "akshare",
            "provider": "em"
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get north fund stock data for {symbol}: {str(e)}"
        )


@router.get("/fund-flow/south-stock/{symbol}", summary="获取南向资金个股统计")
async def get_south_fund_stock(
    symbol: str,
    current_user: User = Depends(get_current_user),
):
    """
    获取南向资金个股统计 (akshare.stock_hsgt_south_acc_flow_in_em)

    返回指定股票的南向资金持股情况
    """
    try:
        df = await akshare_market_adapter.get_stock_hsgt_south_acc_flow_in_em(symbol)

        if df.empty:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No south fund stock data found for symbol {symbol}"
            )

        result = {
            "symbol": symbol,
            "data": df.to_dict('records'),
            "count": len(df),
            "columns": list(df.columns),
            "fund_direction": "south",
            "source": "akshare",
            "provider": "em"
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get south fund stock data for {symbol}: {str(e)}"
        )


@router.get("/fund-flow/hsgt-holdings/{symbol}", summary="获取沪深港通持股明细")
async def get_hsgt_holdings(
    symbol: str,
    current_user: User = Depends(get_current_user),
):
    """
    获取沪深港通持股明细 (akshare.stock_hsgt_hold_stock_em)

    返回指定股票的沪深港通持股明细数据
    """
    try:
        df = await akshare_market_adapter.get_stock_hsgt_hold_stock_em(symbol)

        if df.empty:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No HSGT holdings data found for symbol {symbol}"
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
            f"Failed to get HSGT holdings data for {symbol}: {str(e)}"
        )


@router.get("/fund-flow/big-deal", summary="获取资金流向大单统计")
async def get_fund_flow_big_deal(
    current_user: User = Depends(get_current_user),
):
    """
    获取资金流向大单统计 (akshare.stock_fund_flow_big_deal)

    返回全市场资金流向大单统计数据
    """
    try:
        df = await akshare_market_adapter.get_stock_fund_flow_big_deal()

        if df.empty:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                "No fund flow big deal data found"
            )

        result = {
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
            f"Failed to get fund flow big deal data: {str(e)}"
        )


