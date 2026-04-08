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
from app.openapi_config import COMMON_RESPONSES
from app.schema import StockSymbolModel, TechnicalIndicatorQueryModel  # 导入P0改进的验证模型
from app.services.data_source_factory import DataSourceFactory

logger = logging.getLogger(__name__)

router = APIRouter(tags=["technical-analysis"])
router.include_router(technical_patterns_router)

SYMBOL_PATH_DESCRIPTION = "股票代码，支持证券代码或带交易所后缀的标准格式，例如 600519.SH。"


# ============================================================================
# Enhanced Pydantic Models with Validation
# ============================================================================


class TechnicalAnalysisRequest(BaseModel):
    """技术分析请求参数"""

    symbol: str = Field(..., description="股票代码", min_length=1, max_length=20, pattern=r"^[A-Z0-9.]+$")
    period: str = Field("daily", description="数据周期", pattern=r"^(daily|weekly|monthly)$")
    start_date: Optional[str] = Field(None, description="开始日期 YYYY-MM-DD", pattern=r"^\d{4}-\d{2}-\d{2}$")
    end_date: Optional[str] = Field(None, description="结束日期 YYYY-MM-DD", pattern=r"^\d{4}-\d{2}-\d{2}$")
    limit: Optional[int] = Field(None, description="数据点数量限制", ge=10, le=5000)

    @field_validator("symbol")
    @classmethod
    def validate_symbol(cls, v: str) -> str:
        """验证股票代码格式"""
        if v.startswith("."):
            raise ValueError("股票代码不能以点开头")
        if ".." in v:
            raise ValueError("股票代码不能包含连续的点")
        return v.upper()

    @field_validator("start_date", "end_date")
    @classmethod
    def validate_dates(cls, v: Optional[str], field) -> Optional[str]:
        """验证日期格式和范围"""
        if v is None:
            return v

        try:
            parsed_date = datetime.strptime(v, "%Y-%m-%d").date()
            today = date.today()

            # 检查日期不能是未来
            if parsed_date > today:
                raise ValueError(f"{field.name}不能是未来日期")

            # 检查日期不能太久远
            if parsed_date.year < 1990:
                raise ValueError(f"{field.name}不能早于1990年")

            return v
        except ValueError as e:
            if "does not match format" in str(e):
                raise ValueError("日期格式错误，请使用 YYYY-MM-DD 格式")
            raise

    @field_validator("end_date")
    @classmethod
    def validate_date_range(cls, v: Optional[str], values) -> Optional[str]:
        """验证结束日期必须大于开始日期"""
        if v is None or "start_date" not in values or values["start_date"] is None:
            return v

        try:
            end_date = datetime.strptime(v, "%Y-%m-%d").date()
            start_date = datetime.strptime(values["start_date"], "%Y-%m-%d").date()

            if end_date <= start_date:
                raise ValueError("结束日期必须大于开始日期")

            return v
        except ValueError:
            raise ValueError("日期范围无效，结束日期必须大于开始日期")

    @field_validator("limit")
    @classmethod
    def validate_limit_for_period(cls, v: Optional[int], values) -> Optional[int]:
        """根据周期验证数据量限制"""
        if v is None:
            return v

        period = values.get("period", "daily")

        # 根据周期设置合理的上限
        if period == "daily" and v > 5000:
            raise ValueError("日线数据最多返回5000个数据点")
        elif period == "weekly" and v > 1000:
            raise ValueError("周线数据最多返回1000个数据点")
        elif period == "monthly" and v > 300:
            raise ValueError("月线数据最多返回300个数据点")

        return v


class TrendIndicatorsRequest(BaseModel):
    """趋势指标请求参数"""

    symbol: str = Field(..., description="股票代码", min_length=1, max_length=20, pattern=r"^[A-Z0-9.]+$")
    period: str = Field("daily", description="数据周期", pattern=r"^(daily|weekly|monthly)$")
    ma_periods: Optional[List[int]] = Field(None, description="自定义移动平均线周期")

    @field_validator("ma_periods")
    @classmethod
    def validate_ma_periods(cls, v: Optional[List[int]]) -> Optional[List[int]]:
        """验证移动平均线周期"""
        if v is None:
            return v

        if len(v) > 10:  # 限制最多10个MA周期
            raise ValueError("移动平均线周期数量不能超过10个")

        for period in v:
            if period < 1 or period > 500:
                raise ValueError(f"移动平均线周期 {period} 必须在1-500之间")

        return sorted(set(v))  # 去重并排序


class TrendIndicatorsResponse(BaseModel):
    """趋势指标响应"""

    ma5: Optional[float] = None
    ma10: Optional[float] = None
    ma20: Optional[float] = None
    ma30: Optional[float] = None
    ma60: Optional[float] = None
    ma120: Optional[float] = None
    ma250: Optional[float] = None
    ema12: Optional[float] = None
    ema26: Optional[float] = None
    ema50: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_hist: Optional[float] = None
    adx: Optional[float] = None
    plus_di: Optional[float] = None
    minus_di: Optional[float] = None
    sar: Optional[float] = None


class MomentumIndicatorsResponse(BaseModel):
    """动量指标响应"""

    rsi6: Optional[float] = None
    rsi12: Optional[float] = None
    rsi24: Optional[float] = None
    kdj_k: Optional[float] = None
    kdj_d: Optional[float] = None
    kdj_j: Optional[float] = None
    cci: Optional[float] = None
    willr: Optional[float] = None
    roc: Optional[float] = None


class VolatilityIndicatorsResponse(BaseModel):
    """波动性指标响应"""

    bb_upper: Optional[float] = None
    bb_middle: Optional[float] = None
    bb_lower: Optional[float] = None
    bb_width: Optional[float] = None
    atr: Optional[float] = None
    atr_percent: Optional[float] = None
    kc_upper: Optional[float] = None
    kc_middle: Optional[float] = None
    kc_lower: Optional[float] = None
    stddev: Optional[float] = None


class VolumeIndicatorsResponse(BaseModel):
    """成交量指标响应"""

    obv: Optional[float] = None
    vwap: Optional[float] = None
    volume_ma5: Optional[float] = None
    volume_ma10: Optional[float] = None
    volume_ratio: Optional[float] = None


class AllIndicatorsResponse(BaseModel):
    """所有指标综合响应"""

    symbol: str = Field(..., description="请求的股票代码。")
    latest_price: float = Field(..., description="最新收盘价或最新成交价。")
    latest_date: str = Field(..., description="最新指标对应的交易日期。")
    data_points: int = Field(..., description="参与指标计算的数据点数量。")
    total_indicators: int = Field(..., description="返回的指标总数。")
    trend: Dict[str, Any] = Field(..., description="趋势类指标结果集合。")
    momentum: Dict[str, Any] = Field(..., description="动量类指标结果集合。")
    volatility: Dict[str, Any] = Field(..., description="波动率类指标结果集合。")
    volume: Dict[str, Any] = Field(..., description="成交量类指标结果集合。")


class TradingSignalItem(BaseModel):
    """单个交易信号"""

    type: str
    signal: str  # buy, sell, hold
    strength: float  # 0-1


class TradingSignalsResponse(BaseModel):
    """交易信号响应"""

    overall_signal: str
    signal_strength: float
    signals: List[TradingSignalItem]
    signal_count: Dict


TECHNICAL_ANALYSIS_503_RESPONSE = {
    "description": "技术分析服务暂时不可用",
    "content": {
        "application/json": {
            "example": {
                "success": False,
                "message": "技术分析服务暂不可用，请稍后重试",
                "error_code": "TECHNICAL_ANALYSIS_SERVICE_UNAVAILABLE",
                "timestamp": "2026-04-08T04:20:00Z",
            }
        }
    },
}

ALL_INDICATORS_RESPONSE_EXAMPLE = {
    "symbol": "600519.SH",
    "latest_price": 1750.32,
    "latest_date": "2026-04-07",
    "data_points": 120,
    "total_indicators": 28,
    "trend": {
        "ma5": 1742.18,
        "ma10": 1735.66,
        "ma20": 1718.42,
        "ema12": 1738.55,
        "macd": 12.43,
        "macd_signal": 9.87,
        "macd_hist": 2.56,
        "adx": 24.11,
        "plus_di": 27.35,
        "minus_di": 18.41,
        "sar": 1702.48,
    },
    "momentum": {
        "rsi6": 63.25,
        "rsi12": 58.71,
        "rsi24": 54.86,
        "kdj_k": 72.18,
        "kdj_d": 68.34,
        "kdj_j": 79.86,
        "cci": 118.44,
        "willr": -21.08,
        "roc": 4.32,
    },
    "volatility": {
        "bb_upper": 1788.42,
        "bb_middle": 1725.18,
        "bb_lower": 1661.94,
        "bb_width": 7.33,
        "atr": 35.42,
        "atr_percent": 2.02,
        "kc_upper": 1790.66,
        "kc_middle": 1724.77,
        "kc_lower": 1658.88,
        "stddev": 31.62,
    },
    "volume": {
        "obv": 154326700.0,
        "vwap": 1731.45,
        "volume_ma5": 4987654.0,
        "volume_ma10": 4765123.0,
        "volume_ratio": 1.24,
    },
}

TREND_INDICATORS_RESPONSE_EXAMPLE = {
    "success": True,
    "data": {
        "symbol": "600519.SH",
        "indicators": {
            "ma5": 1742.18,
            "ma10": 1735.66,
            "ma20": 1718.42,
            "ema12": 1738.55,
            "macd": 12.43,
            "macd_signal": 9.87,
            "macd_hist": 2.56,
            "adx": 24.11,
            "plus_di": 27.35,
            "minus_di": 18.41,
            "sar": 1702.48,
        },
        "count": 11,
        "period": "daily",
    },
    "message": "获取600519.SH趋势指标成功",
    "timestamp": "2026-04-08T04:20:00Z",
    "request_id": "req-technical-trend-001",
}

MOMENTUM_INDICATORS_RESPONSE_EXAMPLE = {
    "success": True,
    "symbol": "600519.SH",
    "indicators": {
        "rsi6": 63.25,
        "rsi12": 58.71,
        "rsi24": 54.86,
        "kdj_k": 72.18,
        "kdj_d": 68.34,
        "kdj_j": 79.86,
        "cci": 118.44,
        "willr": -21.08,
        "roc": 4.32,
    },
    "count": 9,
}

VOLATILITY_INDICATORS_RESPONSE_EXAMPLE = {
    "success": True,
    "symbol": "600519.SH",
    "indicators": {
        "bb_upper": 1788.42,
        "bb_middle": 1725.18,
        "bb_lower": 1661.94,
        "bb_width": 7.33,
        "atr": 35.42,
        "atr_percent": 2.02,
        "kc_upper": 1790.66,
        "kc_middle": 1724.77,
        "kc_lower": 1658.88,
        "stddev": 31.62,
    },
    "count": 10,
}

VOLUME_INDICATORS_RESPONSE_EXAMPLE = {
    "success": True,
    "symbol": "600519.SH",
    "indicators": {
        "obv": 154326700.0,
        "vwap": 1731.45,
        "volume_ma5": 4987654.0,
        "volume_ma10": 4765123.0,
        "volume_ratio": 1.24,
    },
    "count": 5,
}

TRADING_SIGNALS_RESPONSE_EXAMPLE = {
    "success": True,
    "data": {
        "symbol": "600519.SH",
        "signals": {
            "overall_signal": "buy",
            "signal_strength": 0.73,
            "signals": [
                {"type": "macd_golden_cross", "signal": "buy", "strength": 0.7},
                {"type": "rsi_oversold", "signal": "buy", "strength": 0.76},
            ],
            "signal_count": {"buy": 2, "sell": 0, "total": 2},
        },
        "period": "daily",
    },
    "message": "获取600519.SH交易信号成功",
    "timestamp": "2026-04-08T04:20:00Z",
    "request_id": "req-technical-signals-001",
}

TECHNICAL_HISTORY_RESPONSE_EXAMPLE = {
    "success": True,
    "symbol": "600519.SH",
    "period": "daily",
    "count": 2,
    "records": [
        {
            "date": "2026-04-03",
            "open": 1738.5,
            "high": 1756.8,
            "low": 1732.1,
            "close": 1750.32,
            "volume": 5123400,
            "amount": 8954320000.0,
            "change_percent": 1.24,
            "change_amount": 21.42,
            "turnover_rate": 0.62,
        },
        {
            "date": "2026-04-07",
            "open": 1746.8,
            "high": 1761.2,
            "low": 1740.5,
            "close": 1754.66,
            "volume": 4876500,
            "amount": 8521180000.0,
            "change_percent": 0.25,
            "change_amount": 4.34,
            "turnover_rate": 0.58,
        },
    ],
}

TECHNICAL_BATCH_INDICATORS_RESPONSE_EXAMPLE = {
    "success": True,
    "results": {
        "600519.SH": {
            "symbol": "600519.SH",
            "latest_price": 1750.32,
            "latest_date": "2026-04-07",
            "data_points": 120,
            "total_indicators": 28,
            "trend": {"ma5": 1742.18, "ema12": 1738.55, "macd": 12.43},
            "momentum": {"rsi6": 63.25, "kdj_k": 72.18, "roc": 4.32},
            "volatility": {"bb_upper": 1788.42, "atr": 35.42, "stddev": 31.62},
            "volume": {"obv": 154326700.0, "vwap": 1731.45, "volume_ratio": 1.24},
        },
        "000001.SZ": {
            "symbol": "000001.SZ",
            "latest_price": 12.64,
            "latest_date": "2026-04-07",
            "data_points": 120,
            "total_indicators": 24,
            "trend": {"ma5": 12.52, "ema12": 12.48, "macd": 0.12},
            "momentum": {"rsi6": 57.34, "kdj_k": 66.21, "roc": 1.98},
            "volatility": {"bb_upper": 12.91, "atr": 0.21, "stddev": 0.18},
            "volume": {"obv": 223456700.0, "vwap": 12.47, "volume_ratio": 1.09},
        },
    },
}


def _success_response_spec(
    description: str,
    example: Dict[str, Any],
    extra_responses: Optional[Dict[int, Dict[str, Any]]] = None,
) -> Dict[int, Dict[str, Any]]:
    responses: Dict[int, Dict[str, Any]] = {
        200: {
            "description": description,
            "content": {
                "application/json": {
                    "example": example,
                }
            },
        },
        422: COMMON_RESPONSES[422],
        500: COMMON_RESPONSES[500],
    }

    if extra_responses:
        responses.update(extra_responses)

    return responses


ALL_INDICATORS_RESPONSES = _success_response_spec(
    "股票全量技术指标查询成功。",
    ALL_INDICATORS_RESPONSE_EXAMPLE,
    extra_responses={503: TECHNICAL_ANALYSIS_503_RESPONSE},
)
TREND_INDICATORS_RESPONSES = _success_response_spec("趋势指标计算成功。", TREND_INDICATORS_RESPONSE_EXAMPLE)
MOMENTUM_INDICATORS_RESPONSES = _success_response_spec("动量指标计算成功。", MOMENTUM_INDICATORS_RESPONSE_EXAMPLE)
VOLATILITY_INDICATORS_RESPONSES = _success_response_spec("波动性指标计算成功。", VOLATILITY_INDICATORS_RESPONSE_EXAMPLE)
VOLUME_INDICATORS_RESPONSES = _success_response_spec("成交量指标计算成功。", VOLUME_INDICATORS_RESPONSE_EXAMPLE)
TRADING_SIGNALS_RESPONSES = _success_response_spec("技术交易信号生成成功。", TRADING_SIGNALS_RESPONSE_EXAMPLE)
TECHNICAL_HISTORY_RESPONSES = _success_response_spec("技术分析历史行情查询成功。", TECHNICAL_HISTORY_RESPONSE_EXAMPLE)
TECHNICAL_BATCH_INDICATORS_RESPONSES = _success_response_spec(
    "批量技术指标查询成功。", TECHNICAL_BATCH_INDICATORS_RESPONSE_EXAMPLE
)


# ============================================================================
# API Endpoints
# ============================================================================


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
        )

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
