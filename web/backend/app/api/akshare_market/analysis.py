"""
分析与预测路由 (Analysis & Forecast)
"""
from fastapi import APIRouter, Depends, Path, Query
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


CHIP_DISTRIBUTION_RESPONSES = {
    **_error_response_spec(
        404,
        "未找到指定股票的筹码分布数据",
        {"success": False, "error_code": "DATA_NOT_FOUND", "message": "No chip distribution data found for symbol 600519"},
    ),
    **_error_response_spec(
        500,
        "筹码分布数据查询失败",
        {"success": False, "error_code": "INTERNAL_ERROR", "message": "Failed to get chip distribution data for 600519"},
    ),
    **_success_response_spec(
        "筹码分布分析数据",
        {
            "success": True,
            "data": {
                "symbol": "600519",
                "data": [{"日期": "2024-01-15", "价格": 1688.0, "获利比例": 0.72}],
                "count": 1,
                "columns": ["日期", "价格", "获利比例"],
                "source": "akshare",
                "provider": "em",
            },
        },
    ),
}

PROFIT_FORECAST_EM_RESPONSES = {
    **_error_response_spec(
        404,
        "未找到指定股票的东方财富盈利预测数据",
        {"success": False, "error_code": "DATA_NOT_FOUND", "message": "No profit forecast data found for stock 600519 from EM"},
    ),
    **_error_response_spec(
        500,
        "东方财富盈利预测查询失败",
        {"success": False, "error_code": "INTERNAL_ERROR", "message": "Failed to get profit forecast from EM for 600519"},
    ),
    **_success_response_spec(
        "东方财富盈利预测数据",
        {
            "success": True,
            "data": {
                "symbol": "600519",
                "data": [{"年份": "2024", "每股收益": 58.6, "机构家数": 32}],
                "count": 1,
                "columns": ["年份", "每股收益", "机构家数"],
                "source": "akshare",
                "provider": "em",
                "forecast_type": "profit",
            },
        },
    ),
}

PROFIT_FORECAST_THS_RESPONSES = {
    **_error_response_spec(
        404,
        "未找到指定股票的同花顺盈利预测数据",
        {"success": False, "error_code": "DATA_NOT_FOUND", "message": "No profit forecast data found for stock 600519 from THS"},
    ),
    **_error_response_spec(
        500,
        "同花顺盈利预测查询失败",
        {"success": False, "error_code": "INTERNAL_ERROR", "message": "Failed to get profit forecast from THS for 600519"},
    ),
    **_success_response_spec(
        "同花顺盈利预测数据",
        {
            "success": True,
            "data": {
                "symbol": "600519",
                "data": [{"年份": "2024", "净利润预测": 74500000000.0, "机构家数": 28}],
                "count": 1,
                "columns": ["年份", "净利润预测", "机构家数"],
                "source": "akshare",
                "provider": "ths",
                "forecast_type": "profit",
            },
        },
    ),
}

TECHNICAL_INDICATORS_EM_RESPONSES = {
    **_error_response_spec(
        404,
        "未找到指定股票的技术指标数据",
        {"success": False, "error_code": "DATA_NOT_FOUND", "message": "No technical indicator data found for stock 600519"},
    ),
    **_error_response_spec(
        500,
        "技术指标查询失败",
        {"success": False, "error_code": "INTERNAL_ERROR", "message": "Failed to get technical indicators for 600519"},
    ),
    **_success_response_spec(
        "技术指标分析数据",
        {
            "success": True,
            "data": {
                "symbol": "600519",
                "data": [{"日期": "2024-01-15", "MA5": 1680.2, "MACD": 12.6, "RSI": 58.4}],
                "count": 1,
                "columns": ["日期", "MA5", "MACD", "RSI"],
                "source": "akshare",
                "provider": "em",
                "indicator_types": ["ma", "macd", "rsi", "kdj", "boll"],
            },
        },
    ),
}


@router.get(
    "/chip-distribution/{symbol}",
    summary="获取筹码分布数据",
    description="按股票代码查询筹码分布数据，返回获利比例等筹码结构指标，用于 A 股持仓成本分析。",
    responses=CHIP_DISTRIBUTION_RESPONSES,
)
async def get_chip_distribution(
    symbol: str = Path(..., description="股票代码，例如 600519"),
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

@router.get(
    "/forecast/profit/em/{symbol}",
    summary="获取盈利预测-东方财富",
    description="按股票代码查询东方财富盈利预测数据，返回机构预期指标，用于基本面预期跟踪。",
    responses=PROFIT_FORECAST_EM_RESPONSES,
)
async def get_profit_forecast_em(
    symbol: str = Path(..., description="股票代码，例如 600519"),
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


@router.get(
    "/forecast/profit/ths/{symbol}",
    summary="获取盈利预测-同花顺",
    description="按股票代码查询同花顺盈利预测数据，返回盈利预期与机构覆盖情况，用于预期对比分析。",
    responses=PROFIT_FORECAST_THS_RESPONSES,
)
async def get_profit_forecast_ths(
    symbol: str = Path(..., description="股票代码，例如 600519"),
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


@router.get(
    "/technical/indicators/em/{symbol}",
    summary="获取技术指标数据",
    description="按股票代码查询技术指标分析数据，返回均线、MACD、RSI 等结果，用于技术面诊断。",
    responses=TECHNICAL_INDICATORS_EM_RESPONSES,
)
async def get_technical_indicators_em(
    symbol: str = Path(..., description="股票代码，例如 600519"),
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
