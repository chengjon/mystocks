"""分析与预测路由 (Analysis & Forecast)"""

import asyncio

from fastapi import APIRouter, Depends, Query

from app.core.config import settings
from app.core.responses import ErrorCodes, create_error_response, create_success_response
from app.core.security import User, get_current_user
from src.services.openstock import OpenStockClient, DataCategory

from .base import akshare_market_adapter  # OPENSTOCK_GAP: technical/indicators (永久 GAP)


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


@router.get("/chip-distribution/{symbol}", summary="获取筹码分布数据")
async def get_chip_distribution(
    symbol: str,
    current_user: User = Depends(get_current_user),
):
    """获取筹码分布数据 (OpenStock CHIP_DISTRIBUTION)

    返回指定股票的筹码分布（成本分布）数据。
    """
    try:
        result = await asyncio.to_thread(
            _get_client().fetch,
            DataCategory.CHIP_DISTRIBUTION,
            {"symbol": symbol},
        )

        data = result.get("data", [])
        if not data:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No chip distribution data found for symbol {symbol}",
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
            f"Failed to get chip distribution data for {symbol}: {e!s}",
        )


# ============================================================================
# Phase 4: 预测和分析数据API
# ============================================================================


@router.get("/forecast/profit/em/{symbol}", summary="获取盈利预测-东方财富")
async def get_profit_forecast_em(
    symbol: str,
    current_user: User = Depends(get_current_user),
):
    """获取盈利预测 (OpenStock F10_DATA profit_forecast)

    返回指定股票的东方财富盈利预测数据
    """
    try:
        result = await asyncio.to_thread(
            _get_client().fetch,
            DataCategory.F10_DATA,
            {"symbol": symbol, "f10_type": "profit_forecast"},
        )

        data = result.get("data", [])
        if not data:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No profit forecast data found for stock {symbol}",
            )

        result = {
            "symbol": symbol,
            "data": data,
            "count": len(data),
            "columns": list(data[0].keys()) if data else [],
            "source": "openstock",
            "provider": "openstock_gateway",
            "forecast_type": "profit",
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get profit forecast for {symbol}: {e!s}",
        )


@router.get("/forecast/profit/ths/{symbol}", summary="获取盈利预测-同花顺")
async def get_profit_forecast_ths(
    symbol: str,
    current_user: User = Depends(get_current_user),
):
    """获取盈利预测-同花顺 (OpenStock PROFIT_FORECAST_THS)

    返回同花顺平台的个股盈利预测数据。
    """
    try:
        result = await asyncio.to_thread(
            _get_client().fetch,
            DataCategory.PROFIT_FORECAST_THS,
            {"symbol": symbol},
        )

        data = result.get("data", [])
        if not data:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No profit forecast data found for stock {symbol} from THS",
            )

        result = {
            "symbol": symbol,
            "data": data,
            "count": len(data),
            "columns": list(data[0].keys()) if data else [],
            "source": "openstock",
            "provider": "openstock_gateway",
            "forecast_type": "profit",
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get profit forecast from THS for {symbol}: {e!s}",
        )


@router.get("/technical/indicators/em/{symbol}", summary="获取技术指标数据")
async def get_technical_indicators_em(
    symbol: str,
    current_user: User = Depends(get_current_user),
):
    """获取技术指标数据 (akshare.stock_technical_indicator_em)

    OPENSTOCK_GAP: 技术指标(MA/MACD/RSI/KDJ/BOLL)为 akshare 特有计算, OpenStock 无对应 category.
    保留原 adapter 调用, 待 OpenStock 实现后迁移.
    """
    try:
        df = await akshare_market_adapter.get_stock_technical_indicator_em(symbol)

        if df.empty:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No technical indicator data found for stock {symbol}",
            )

        result = {
            "symbol": symbol,
            "data": df.to_dict("records"),
            "count": len(df),
            "columns": list(df.columns),
            "source": "akshare",
            "provider": "em",
            "indicator_types": ["ma", "macd", "rsi", "kdj", "boll"],
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get technical indicators for {symbol}: {e!s}",
        )


@router.get("/market/account-statistics", summary="获取股票账户统计月度")
async def get_account_statistics_em(
    date: str = Query(..., description="查询月份", example="2024-01"),
    current_user: User = Depends(get_current_user),
):
    """获取股票账户统计月度 (OpenStock ACCOUNT_STATISTICS)

    返回按月份过滤的股票账户统计数据。
    """
    try:
        result = await asyncio.to_thread(
            _get_client().fetch,
            DataCategory.ACCOUNT_STATISTICS,
            {"month": date},
        )

        data = result.get("data", [])
        if not data:
            return create_error_response(
                ErrorCodes.DATA_NOT_FOUND,
                f"No account statistics data found for month {date}",
            )

        result = {
            "data": data,
            "count": len(data),
            "columns": list(data[0].keys()) if data else [],
            "query_month": date,
            "source": "openstock",
            "provider": "openstock_gateway",
            "statistics_type": "account",
        }

        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            ErrorCodes.INTERNAL_ERROR,
            f"Failed to get account statistics for {date}: {e!s}",
        )


# ============================================================================
# Phase 5: 板块和行业数据API
# ============================================================================