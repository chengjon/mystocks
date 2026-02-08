"""
分析与预测路由 (Analysis & Forecast)
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query
from app.core.responses import ErrorCodes, create_error_response, create_success_response
from app.core.security import User, get_current_user
from .base import akshare_market_adapter

router = APIRouter()

@router.get("/chip-distribution/{symbol}", summary="获取筹码分布数据")
async def get_chip_distribution(
    symbol: str,
    current_user: User = Depends(get_current_user),
):
    """
    获取筹码分布数据 (akshare.stock_cyq_em)

    返回指定股票的筹码分布分析数据
    """
    try:
        df = await akshare_market_adapter.get_stock_cyq_em(symbol)

        if df.empty:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No chip distribution data found for symbol {symbol}"
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
            f"Failed to get chip distribution data for {symbol}: {str(e)}"
        )


# ============================================================================
# Phase 4: 预测和分析数据API
# ============================================================================

@router.get("/forecast/profit/em/{symbol}", summary="获取盈利预测-东方财富")
async def get_profit_forecast_em(
    symbol: str,
    current_user: User = Depends(get_current_user),
):
    """
    获取盈利预测-东方财富 (akshare.stock_profit_forecast_em)

    返回指定股票的东方财富盈利预测数据
    """
    try:
        df = await akshare_market_adapter.get_stock_profit_forecast_em(symbol)

        if df.empty:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No profit forecast data found for stock {symbol} from EM"
            )

        result = {
            "symbol": symbol,
            "data": df.to_dict('records'),
            "count": len(df),
            "columns": list(df.columns),
            "source": "akshare",
            "provider": "em",
            "forecast_type": "profit"
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get profit forecast from EM for {symbol}: {str(e)}"
        )


@router.get("/forecast/profit/ths/{symbol}", summary="获取盈利预测-同花顺")
async def get_profit_forecast_ths(
    symbol: str,
    current_user: User = Depends(get_current_user),
):
    """
    获取盈利预测-同花顺 (akshare.stock_profit_forecast_ths)

    返回指定股票的同花顺盈利预测数据
    """
    try:
        df = await akshare_market_adapter.get_stock_profit_forecast_ths(symbol)

        if df.empty:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No profit forecast data found for stock {symbol} from THS"
            )

        result = {
            "symbol": symbol,
            "data": df.to_dict('records'),
            "count": len(df),
            "columns": list(df.columns),
            "source": "akshare",
            "provider": "ths",
            "forecast_type": "profit"
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get profit forecast from THS for {symbol}: {str(e)}"
        )


@router.get("/technical/indicators/em/{symbol}", summary="获取技术指标数据")
async def get_technical_indicators_em(
    symbol: str,
    current_user: User = Depends(get_current_user),
):
    """
    获取技术指标数据 (akshare.stock_technical_indicator_em)

    返回指定股票的技术指标数据（均线、MACD、RSI、KDJ、布林带等）
    """
    try:
        df = await akshare_market_adapter.get_stock_technical_indicator_em(symbol)

        if df.empty:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No technical indicator data found for stock {symbol}"
            )

        result = {
            "symbol": symbol,
            "data": df.to_dict('records'),
            "count": len(df),
            "columns": list(df.columns),
            "source": "akshare",
            "provider": "em",
            "indicator_types": ["ma", "macd", "rsi", "kdj", "boll"]
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get technical indicators for {symbol}: {str(e)}"
        )


@router.get("/market/account-statistics", summary="获取股票账户统计月度")
async def get_account_statistics_em(
    date: str = Query(..., description="查询月份", example="2024-01"),
    current_user: User = Depends(get_current_user),
):
    """
    获取股票账户统计月度 (akshare.stock_account_statistics_em)

    返回指定月份的股票账户统计数据
    """
    try:
        df = await akshare_market_adapter.get_stock_account_statistics_em(date)

        if df.empty:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No account statistics data found for month {date}"
            )

        result = {
            "data": df.to_dict('records'),
            "count": len(df),
            "columns": list(df.columns),
            "query_month": date,
            "source": "akshare",
            "provider": "em",
            "statistics_type": "account"
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get account statistics for {date}: {str(e)}"
        )


# ============================================================================
# Phase 5: 板块和行业数据API
# ============================================================================

