"""
技术分析 API 端点
Enhanced Technical Analysis
"""

import logging
from datetime import date, datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Path, Query
from pydantic import BaseModel, Field, ValidationError, field_validator

from app.api._technical_patterns_router import router as technical_patterns_router
from app.core.circuit_breaker_manager import get_circuit_breaker  # 导入熔断器
from app.core.exceptions import BusinessException, ValidationException
from app.core.responses import create_error_response, create_success_response
from app.schema import StockSymbolModel, TechnicalIndicatorQueryModel  # 导入P0改进的验证模型
from app.services.data_source_factory import DataSourceFactory

logger = logging.getLogger(__name__)

router = APIRouter(tags=["technical-analysis"])
router.include_router(technical_patterns_router)

SYMBOL_PATH_DESCRIPTION = "股票代码，支持证券代码或带交易所后缀的标准格式，例如 600519.SH。"


# ============================================================================
# Enhanced Pydantic Models with Validation
# ============================================================================


from app.api._technical_analysis_models import (
    AllIndicatorsResponse,
    MomentumIndicatorsResponse,
    TechnicalAnalysisRequest,
    TradingSignalItem,
    TradingSignalsResponse,
    TrendIndicatorsRequest,
    TrendIndicatorsResponse,
    VolatilityIndicatorsResponse,
    VolumeIndicatorsResponse,
)
from _technical_analysis_responses import (
    ALL_INDICATORS_RESPONSE_EXAMPLE,
    MOMENTUM_INDICATORS_RESPONSE_EXAMPLE,
    TECHNICAL_BATCH_INDICATORS_RESPONSE_EXAMPLE,
    TECHNICAL_HISTORY_RESPONSE_EXAMPLE,
    TRADING_SIGNALS_RESPONSE_EXAMPLE,
    TREND_INDICATORS_RESPONSE_EXAMPLE,
    VOLATILITY_INDICATORS_RESPONSE_EXAMPLE,
    VOLUME_INDICATORS_RESPONSE_EXAMPLE,
    ALL_INDICATORS_RESPONSES,
    TREND_INDICATORS_RESPONSES,
    MOMENTUM_INDICATORS_RESPONSES,
    VOLATILITY_INDICATORS_RESPONSES,
    VOLUME_INDICATORS_RESPONSES,
    TRADING_SIGNALS_RESPONSES,
    TECHNICAL_HISTORY_RESPONSES,
    TECHNICAL_BATCH_INDICATORS_RESPONSES,
)

@router.get(
    "/{symbol}/indicators",
    response_model=AllIndicatorsResponse,
    summary="获取全量技术指标概览",
    responses=ALL_INDICATORS_RESPONSES,
)
async def get_all_indicators(
    symbol: str = Path(..., description="股票代码", min_length=1, max_length=20),
    period: str = Query("daily", description="数据周期: daily, weekly, monthly", pattern=r"^(daily|weekly|monthly)$"),
    start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
    limit: Optional[int] = Query(None, description="数据点数量限制", ge=10, le=5000),
):
    """
    获取股票的所有技术指标

    参数:
    - symbol: 股票代码 (如: 600519)
    - period: 数据周期 (daily, weekly, monthly)
    - start_date: 开始日期 (可选)
    - end_date: 结束日期 (可选)
    - limit: 数据点数量限制 (可选)

    返回:
    - 包含趋势、动量、波动性、成交量指标的综合数据

    **验证**: P0改进 Task 2 - 使用TechnicalIndicatorQueryModel验证参数

    示例:
    - GET /api/technical/600519/indicators
    - GET /api/technical/600519/indicators?period=weekly
    - GET /api/technical/600519/indicators?start_date=2024-01-01&end_date=2025-10-23
    """
    try:
        from datetime import datetime as dt_convert

        # P0改进: 使用TechnicalIndicatorQueryModel验证输入参数
        try:
            # 默认技术指标列表
            default_indicators = ["MA", "EMA", "MACD", "RSI", "KDJ", "BOLL", "ATR"]

            validated_params = TechnicalIndicatorQueryModel(
                symbol=symbol,
                indicators=default_indicators,
                period=limit or 20,  # 使用limit作为期间长度，默认20
                start_date=dt_convert.strptime(start_date, "%Y-%m-%d").date() if start_date else None,
                end_date=dt_convert.strptime(end_date, "%Y-%m-%d").date() if end_date else None,
            )
        except ValidationError as ve:
            # P0改进: 标准化验证错误响应
            error_details = [{"field": str(err["loc"][0]), "message": err["msg"]} for err in ve.errors()]
            return create_error_response(
                error_code="VALIDATION_ERROR", message="输入参数验证失败", details=error_details
            )

        # P0改进 Task 3: 使用熔断器保护外部API调用
        circuit_breaker = get_circuit_breaker("technical_analysis")

        if circuit_breaker.is_open():
            logger.warning("⚠️ Circuit breaker for technical_analysis is OPEN")
            raise BusinessException(
                detail="技术分析服务暂不可用，请稍后重试",
                status_code=503,
                error_code="TECHNICAL_ANALYSIS_SERVICE_UNAVAILABLE",
            )

        # 使用数据源工厂
        data_source_factory = DataSourceFactory()
        try:
            technical_analysis_adapter = await data_source_factory.get_data_source("technical_analysis")

            params = {
                "symbol": validated_params.symbol,
                "period": period,
                "start_date": validated_params.start_date.strftime("%Y-%m-%d") if validated_params.start_date else None,
                "end_date": validated_params.end_date.strftime("%Y-%m-%d") if validated_params.end_date else None,
            }

            result = await technical_analysis_adapter.get_data("indicators", params)
            circuit_breaker.record_success()
        except Exception as api_error:
            circuit_breaker.record_failure()
            logger.error(
                f"❌ Technical analysis API failed: {str(api_error)}, failures: {circuit_breaker.failure_count}"
            )
            raise

        if "error" in result:
            raise BusinessException(detail=result["error"], status_code=500, error_code="TECHNICAL_ANALYSIS_ERROR")

        # 转换为AllIndicatorsResponse格式
        response_data = result.get("data", {})
        return AllIndicatorsResponse(
            symbol=response_data.get("symbol", symbol),
            latest_price=response_data.get("latest_price", 0.0),
            latest_date=response_data.get("latest_date", ""),
            data_points=response_data.get("data_points", 0),
            total_indicators=response_data.get("total_indicators", 0),
            trend=response_data.get("trend", {}),
            momentum=response_data.get("momentum", {}),
            volatility=response_data.get("volatility", {}),
            volume=response_data.get("volume", {}),
        )

    except (BusinessException, ValidationException):
        raise
    except Exception as e:
        raise BusinessException(detail=str(e), status_code=500, error_code="TECHNICAL_ANALYSIS_OPERATION_FAILED")


@router.get("/{symbol}/trend", response_model=Dict, summary="获取趋势指标", responses=TREND_INDICATORS_RESPONSES)
async def get_trend_indicators(
    symbol: str = Path(..., description="股票代码", min_length=1, max_length=20, pattern=r"^[A-Z0-9.]+$"),
    period: str = Query("daily", description="数据周期", pattern=r"^(daily|weekly|monthly)$"),
    ma_periods: Optional[str] = Query(None, description="自定义MA周期，逗号分隔，如: 5,10,20"),
):
    """
    获取趋势指标

    包括:
    - MA (移动平均线): 5, 10, 20, 30, 60, 120, 250日
    - EMA (指数移动平均线): 12, 26, 50日
    - MACD (指数平滑异同移动平均线)
    - DMI (动向指标): ADX, +DI, -DI
    - SAR (抛物线转向指标)

    **验证**: P0改进 Task 2 - 使用StockSymbolModel验证股票代码

    示例:
    - GET /api/technical/600519/trend
    """
    import structlog

    logger = structlog.get_logger()
    logger.info("TREND_ENDPOINT_START", symbol=symbol, period=period)

    try:
        # P0改进: 使用StockSymbolModel验证股票代码
        try:
            validated_symbol = StockSymbolModel(symbol=symbol)
        except ValidationError as ve:
            error_details = [{"field": str(err["loc"][0]), "message": err["msg"]} for err in ve.errors()]
            return create_error_response(
                error_code="VALIDATION_ERROR", message="股票代码验证失败", details=error_details
            )

        # 使用数据源工厂
        data_source_factory = DataSourceFactory()
        technical_analysis_adapter = await data_source_factory.get_data_source("technical_analysis")

        params = {"symbol": validated_symbol.symbol, "period": period}

        result = await technical_analysis_adapter.get_data("trend", params)
        logger.info("TREND_ADAPTER_RESULT", result_keys=list(result.keys()) if result else None)

        if "error" in result:
            raise BusinessException(detail=result["error"], status_code=500, error_code="EXTERNAL_SERVICE_ERROR")

        data = result.get("data", {})

        response = create_success_response(
            data={
                "symbol": validated_symbol.symbol,
                "indicators": data.get("indicators", {}),
                "count": data.get("count", 0),
                "period": period,
            },
            message=f"获取{validated_symbol.symbol}趋势指标成功",
        )
        logger.info("TREND_ENDPOINT_SUCCESS")
        return response

    except (BusinessException, ValidationException):
        raise
    except Exception as e:
        logger.error("TREND_ENDPOINT_ERROR", error=str(e), exc_info=True)
        raise BusinessException(
            detail=f"获取趋势指标失败: {str(e)}", status_code=500, error_code="INTERNAL_SERVER_ERROR"
        )


@router.get(
    "/{symbol}/momentum",
    response_model=Dict,
    summary="获取动量指标",
    responses=MOMENTUM_INDICATORS_RESPONSES,
)
async def get_momentum_indicators(
    symbol: str = Path(..., description=SYMBOL_PATH_DESCRIPTION),
    period: str = Query("daily", description="数据周期"),
):
    """
    获取动量指标

    包括:
    - RSI (相对强弱指标): 6, 12, 24日
    - KDJ (随机指标): K, D, J
    - CCI (顺势指标)
    - WR (威廉指标)
    - ROC (变动率指标)

    **验证**: P0改进 Task 2 - 使用StockSymbolModel验证股票代码

    示例:
    - GET /api/technical/600519/momentum
    """
    try:
        # P0改进: 使用StockSymbolModel验证股票代码
        try:
            validated_symbol = StockSymbolModel(symbol=symbol)
        except ValidationError as ve:
            error_details = [{"field": str(err["loc"][0]), "message": err["msg"]} for err in ve.errors()]
            return create_error_response(
                error_code="VALIDATION_ERROR", message="股票代码验证失败", details=error_details
            )

        # 使用数据源工厂
        data_source_factory = DataSourceFactory()
        technical_analysis_adapter = await data_source_factory.get_data_source("technical_analysis")

        params = {"symbol": validated_symbol.symbol, "period": period}

        result = await technical_analysis_adapter.get_data("momentum", params)

        if "error" in result:
            raise BusinessException(detail=result["error"], status_code=500, error_code="TECHNICAL_ANALYSIS_ERROR")

        return {
            "success": True,
            "symbol": validated_symbol.symbol,
            "indicators": result.get("data", {}).get("indicators", {}),
            "count": result.get("data", {}).get("count", 0),
        }

    except (BusinessException, ValidationException):
        raise
    except Exception as e:
        raise BusinessException(detail=str(e), status_code=500, error_code="TECHNICAL_ANALYSIS_OPERATION_FAILED")


@router.get(
    "/{symbol}/volatility",
    response_model=Dict,
    summary="获取波动性指标",
    responses=VOLATILITY_INDICATORS_RESPONSES,
)
async def get_volatility_indicators(
    symbol: str = Path(..., description=SYMBOL_PATH_DESCRIPTION),
    period: str = Query("daily", description="数据周期"),
):
    """
    获取波动性指标

    包括:
    - Bollinger Bands (布林带): upper, middle, lower, width
    - ATR (平均真实波幅)
    - Keltner Channel (肯特纳通道)
    - Standard Deviation (标准差)

    **验证**: P0改进 Task 2 - 使用StockSymbolModel验证股票代码

    示例:
    - GET /api/technical/600519/volatility
    """
    try:
        # P0改进: 使用StockSymbolModel验证股票代码
        try:
            validated_symbol = StockSymbolModel(symbol=symbol)
        except ValidationError as ve:
            error_details = [{"field": str(err["loc"][0]), "message": err["msg"]} for err in ve.errors()]
            return create_error_response(
                error_code="VALIDATION_ERROR", message="股票代码验证失败", details=error_details
            )

        # 使用数据源工厂
        data_source_factory = DataSourceFactory()
        technical_analysis_adapter = await data_source_factory.get_data_source("technical_analysis")

        params = {"symbol": validated_symbol.symbol, "period": period}

        result = await technical_analysis_adapter.get_data("volatility", params)

        if "error" in result:
            raise BusinessException(detail=result["error"], status_code=500, error_code="TECHNICAL_ANALYSIS_ERROR")

        return {
            "success": True,
            "symbol": validated_symbol.symbol,
            "indicators": result.get("data", {}).get("indicators", {}),
            "count": result.get("data", {}).get("count", 0),
        }

    except (BusinessException, ValidationException):
        raise
    except Exception as e:
        raise BusinessException(detail=str(e), status_code=500, error_code="TECHNICAL_ANALYSIS_OPERATION_FAILED")


@router.get(
    "/{symbol}/volume",
    response_model=Dict,
    summary="获取成交量指标",
    responses=VOLUME_INDICATORS_RESPONSES,
)
async def get_volume_indicators(
    symbol: str = Path(..., description=SYMBOL_PATH_DESCRIPTION),
    period: str = Query("daily", description="数据周期"),
):
    """
    获取成交量指标

    包括:
    - OBV (能量潮指标)
    - VWAP (成交量加权平均价)
    - Volume MA (成交量均线): 5, 10日
    - Volume Ratio (量比)

    **验证**: P0改进 Task 2 - 使用StockSymbolModel验证股票代码

    示例:
    - GET /api/technical/600519/volume
    """
    try:
        # P0改进: 使用StockSymbolModel验证股票代码
        try:
            validated_symbol = StockSymbolModel(symbol=symbol)
        except ValidationError as ve:
            error_details = [{"field": str(err["loc"][0]), "message": err["msg"]} for err in ve.errors()]
            return create_error_response(
                error_code="VALIDATION_ERROR", message="股票代码验证失败", details=error_details
            )

        # 使用数据源工厂
        data_source_factory = DataSourceFactory()
        technical_analysis_adapter = await data_source_factory.get_data_source("technical_analysis")

        params = {"symbol": validated_symbol.symbol, "period": period}

        result = await technical_analysis_adapter.get_data("volume", params)

        if "error" in result:
            raise BusinessException(detail=result["error"], status_code=500, error_code="TECHNICAL_ANALYSIS_ERROR")

        return {
            "success": True,
            "symbol": validated_symbol.symbol,
            "indicators": result.get("data", {}).get("indicators", {}),
            "count": result.get("data", {}).get("count", 0),
        }

    except (BusinessException, ValidationException):
        raise
    except Exception as e:
        raise BusinessException(detail=str(e), status_code=500, error_code="TECHNICAL_ANALYSIS_OPERATION_FAILED")


@router.get(
    "/{symbol}/signals",
    response_model=Dict,
    summary="获取技术交易信号",
    responses=TRADING_SIGNALS_RESPONSES,
)
async def get_trading_signals(
    symbol: str = Path(..., description=SYMBOL_PATH_DESCRIPTION),
    period: str = Query("daily", description="数据周期"),
):
    """
    获取交易信号

    基于技术指标生成买入/卖出/持有信号

    信号类型:
    - macd_golden_cross: MACD金叉 (买入信号)
    - macd_death_cross: MACD死叉 (卖出信号)
    - rsi_oversold: RSI超卖 (买入信号)
    - rsi_overbought: RSI超买 (卖出信号)

    **验证**: P0改进 Task 2 - 使用StockSymbolModel验证股票代码

    示例:
    - GET /api/technical/600519/signals
    """
    try:
        # P0改进: 使用StockSymbolModel验证股票代码
        try:
            validated_symbol = StockSymbolModel(symbol=symbol)
        except ValidationError as ve:
            error_details = [{"field": str(err["loc"][0]), "message": err["msg"]} for err in ve.errors()]
            return create_error_response(
                error_code="VALIDATION_ERROR", message="股票代码验证失败", details=error_details
            )

        # 使用数据源工厂
        data_source_factory = DataSourceFactory()
        technical_analysis_adapter = await data_source_factory.get_data_source("technical_analysis")

        params = {"symbol": validated_symbol.symbol, "period": period}

        result = await technical_analysis_adapter.get_data("signals", params)

        if "error" in result:
            raise BusinessException(detail=result["error"], status_code=500, error_code="EXTERNAL_SERVICE_ERROR")

        signals_data = result.get("data", {})

        return create_success_response(
            data={"symbol": validated_symbol.symbol, "signals": signals_data, "period": period},
            message=f"获取{validated_symbol.symbol}交易信号成功",
        ).model_dump(mode="json")

    except (BusinessException, ValidationException):
        raise
    except Exception as e:
        raise BusinessException(
            detail=f"获取交易信号失败: {str(e)}", status_code=500, error_code="INTERNAL_SERVER_ERROR"
        )


@router.get(
    "/{symbol}/history",
    summary="获取技术分析历史行情",
    responses=TECHNICAL_HISTORY_RESPONSES,
)
async def get_stock_history(
    symbol: str = Path(..., description=SYMBOL_PATH_DESCRIPTION),
    period: str = Query("daily", description="数据周期"),
    start_date: Optional[str] = Query(None, description="开始日期"),
    end_date: Optional[str] = Query(None, description="结束日期"),
    limit: int = Query(100, ge=10, le=1000, description="返回数据点数量"),
):
    """
    获取股票历史行情数据

    用于前端绘制 K 线图和指标图表

    参数:
    - symbol: 股票代码
    - period: 周期 (daily, weekly, monthly)
    - start_date: 开始日期 (可选)
    - end_date: 结束日期 (可选)
    - limit: 返回数据点数量 (默认100，最多1000)

    返回:
    - OHLCV 数据及基础指标

    示例:
    - GET /api/technical/600519/history?limit=200
    - GET /api/technical/600519/history?start_date=2024-01-01
    """
    try:
        # 使用数据源工厂
        data_source_factory = DataSourceFactory()
        technical_analysis_adapter = await data_source_factory.get_data_source("technical_analysis")

        params = {"symbol": symbol, "period": period, "start_date": start_date, "end_date": end_date, "limit": limit}

        result = await technical_analysis_adapter.get_data("history", params)

        if "error" in result:
            raise BusinessException(detail=result["error"], status_code=500, error_code="TECHNICAL_ANALYSIS_ERROR")

        return {"success": True, **result.get("data", {})}

    except (BusinessException, ValidationException):
        raise
    except Exception as e:
        raise BusinessException(detail=str(e), status_code=500, error_code="TECHNICAL_ANALYSIS_OPERATION_FAILED")


@router.post(
    "/batch/indicators",
    summary="批量获取技术指标",
    responses=TECHNICAL_BATCH_INDICATORS_RESPONSES,
)
async def get_batch_indicators(
    symbols: List[str] = Query(..., description="股票代码列表"),
    period: str = Query("daily", description="数据周期"),
):
    """
    批量获取多只股票的技术指标

    参数:
    - symbols: 股票代码列表 (最多20只)

    示例:
    - POST /api/technical/batch/indicators?symbols=600519&symbols=000001&symbols=600000
    """
    try:
        if len(symbols) > 20:
            raise ValidationException(detail="Maximum 20 symbols allowed", field="symbols")

        # 使用数据源工厂
        data_source_factory = DataSourceFactory()
        technical_analysis_adapter = await data_source_factory.get_data_source("technical_analysis")

        params = {"symbols": symbols, "period": period}

        result = await technical_analysis_adapter.get_data("batch_indicators", params)

        if "error" in result:
            raise BusinessException(detail=result["error"], status_code=500, error_code="TECHNICAL_ANALYSIS_ERROR")

        return {"success": True, **result.get("data", {})}

    except (BusinessException, ValidationException):
        raise
    except Exception as e:
        raise BusinessException(detail=str(e), status_code=500, error_code="TECHNICAL_ANALYSIS_OPERATION_FAILED")
