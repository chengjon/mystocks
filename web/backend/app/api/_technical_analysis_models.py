"""Auto-extracted Pydantic models for technical analysis."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator


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

