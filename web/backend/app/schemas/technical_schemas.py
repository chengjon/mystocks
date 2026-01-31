"""
技术指标API Schemas (Pydantic模型)

用于FastAPI请求验证和响应序列化:
- OverlayIndicator: 主图叠加指标 (MA/EMA/BOLL)
- OscillatorIndicator: 震荡指标 (MACD/KDJ/RSI)
- IndicatorRequest: 技术指标计算请求
- IndicatorResponse: 技术指标响应
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

# ==================== Overlay Indicators (主图叠加指标) ====================


class MAParams(BaseModel):
    """移动平均线参数"""

    period: int = Field(default=20, ge=1, le=500, description="MA周期")
    price_type: str = Field(default="close", description="价格类型 (close/open/high/low)")


class EMAParams(BaseModel):
    """指数移动平均线参数"""

    period: int = Field(default=20, ge=1, le=500, description="EMA周期")
    price_type: str = Field(default="close", description="价格类型 (close/open/high/low)")


class BOLLParams(BaseModel):
    """布林带参数"""

    period: int = Field(default=20, ge=1, le=500, description="BOLL周期")
    std_dev: float = Field(default=2.0, ge=0.1, le=5.0, description="标准差倍数")


class OverlayIndicatorRequest(BaseModel):
    """主图叠加指标计算请求"""

    symbol: str = Field(..., description="股票代码", examples=["000001.SZ", "600519.SH"])
    indicator_type: str = Field(..., description="指标类型 (MA/EMA/BOLL)", pattern="^(MA|EMA|BOLL)$")
    params: Dict[str, Any] = Field(default_factory=dict, description="指标参数")
    start_date: Optional[str] = Field(None, description="开始日期 YYYY-MM-DD")
    end_date: Optional[str] = Field(None, description="结束日期 YYYY-MM-DD")

    @field_validator("indicator_type")
    @classmethod
    def validate_indicator_type(cls, v):
        """验证指标类型"""
        valid_types = ["MA", "EMA", "BOLL"]
        if v not in valid_types:
            raise ValueError(f"无效的指标类型,支持: {valid_types}")
        return v


class OverlayIndicatorValue(BaseModel):
    """主图叠加指标数值"""

    timestamp: int = Field(description="Unix时间戳 (毫秒)")
    value: float = Field(description="指标值")

    # BOLL特有字段
    upper: Optional[float] = Field(None, description="上轨 (仅BOLL)")
    middle: Optional[float] = Field(None, description="中轨 (仅BOLL)")
    lower: Optional[float] = Field(None, description="下轨 (仅BOLL)")


class OverlayIndicatorResponse(BaseModel):
    """主图叠加指标响应"""

    symbol: str = Field(description="股票代码")
    indicator_type: str = Field(description="指标类型")
    indicator_name: str = Field(description="指标名称")
    values: List[OverlayIndicatorValue] = Field(description="指标数值列表")
    params: Dict[str, Any] = Field(description="使用的参数")
    calculated_at: datetime = Field(default_factory=datetime.now, description="计算时间")

    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "000001.SZ",
                "indicator_type": "MA",
                "indicator_name": "MA20",
                "values": [{"timestamp": 1640995200000, "value": 10.5}],
                "params": {"period": 20, "price_type": "close"},
            }
        }


# ==================== Oscillator Indicators (震荡指标) ====================


class MACDParams(BaseModel):
    """MACD参数"""

    fast_period: int = Field(default=12, ge=1, le=100, description="快线周期")
    slow_period: int = Field(default=26, ge=1, le=200, description="慢线周期")
    signal_period: int = Field(default=9, ge=1, le=50, description="信号线周期")


class KDJParams(BaseModel):
    """KDJ参数"""

    n: int = Field(default=9, ge=1, le=100, description="KDJ周期")
    m1: int = Field(default=3, ge=1, le=50, description="K平滑参数")
    m2: int = Field(default=3, ge=1, le=50, description="D平滑参数")


class RSIParams(BaseModel):
    """RSI参数"""

    period: int = Field(default=14, ge=1, le=100, description="RSI周期")


class OscillatorIndicatorRequest(BaseModel):
    """震荡指标计算请求"""

    symbol: str = Field(..., description="股票代码")
    indicator_type: str = Field(..., description="指标类型 (MACD/KDJ/RSI)", pattern="^(MACD|KDJ|RSI)$")
    params: Optional[Dict[str, Any]] = Field(default_factory=dict, description="指标参数")
    start_date: Optional[str] = Field(None, description="开始日期")
    end_date: Optional[str] = Field(None, description="结束日期")


class OscillatorIndicatorValue(BaseModel):
    """震荡指标数值"""

    timestamp: int = Field(description="Unix时间戳 (毫秒)")

    # MACD字段
    dif: Optional[float] = Field(None, description="DIF线 (仅MACD)")
    dea: Optional[float] = Field(None, description="DEA线 (仅MACD)")
    macd: Optional[float] = Field(None, description="MACD柱 (仅MACD)")

    # KDJ字段
    k: Optional[float] = Field(None, description="K值 (仅KDJ)")
    d: Optional[float] = Field(None, description="D值 (仅KDJ)")
    j: Optional[float] = Field(None, description="J值 (仅KDJ)")

    # RSI字段
    rsi: Optional[float] = Field(None, description="RSI值 (仅RSI)")


class OscillatorIndicatorResponse(BaseModel):
    """震荡指标响应"""

    symbol: str = Field(description="股票代码")
    indicator_type: str = Field(description="指标类型")
    indicator_name: str = Field(description="指标名称")
    values: List[OscillatorIndicatorValue] = Field(description="指标数值列表")
    params: Dict[str, Any] = Field(description="使用的参数")
    calculated_at: datetime = Field(default_factory=datetime.now, description="计算时间")


# ==================== Multi Indicator Request ====================


class IndicatorSpec(BaseModel):
    """指标规格"""

    indicator_type: str = Field(..., description="指标类型 (MA/EMA/BOLL/MACD/KDJ/RSI)")
    params: Optional[Dict[str, Any]] = Field(default_factory=dict, description="指标参数")


class MultiIndicatorRequest(BaseModel):
    """多指标计算请求"""

    symbol: str = Field(..., description="股票代码")
    indicators: List[IndicatorSpec] = Field(..., min_length=1, max_length=10, description="指标列表 (最多10个)")
    start_date: Optional[str] = Field(None, description="开始日期")
    end_date: Optional[str] = Field(None, description="结束日期")

    @field_validator("indicators")
    @classmethod
    def validate_indicators(cls, v):
        """验证指标列表"""
        indicator_types = [ind.indicator_type for ind in v]
        # 检查是否有重复类型
        if len(indicator_types) != len(set(indicator_types)):
            raise ValueError("指标列表中存在重复类型")
        return v


class IndicatorResponseItem(BaseModel):
    """单个指标响应项"""

    indicator_type: str = Field(description="指标类型")
    indicator_name: str = Field(description="指标名称")
    data: List[Dict[str, Any]] = Field(description="指标数据")
    params: Dict[str, Any] = Field(description="使用的参数")


class MultiIndicatorResponse(BaseModel):
    """多指标响应"""

    symbol: str = Field(description="股票代码")
    indicators: List[IndicatorResponseItem] = Field(description="指标列表")
    calculated_at: datetime = Field(default_factory=datetime.now, description="计算时间")


# ==================== Indicator Registry ====================


class IndicatorInfo(BaseModel):
    """指标信息"""

    indicator_type: str = Field(description="指标类型 (MA/EMA/BOLL/MACD/KDJ/RSI)")
    indicator_name: str = Field(description="指标中文名称")
    category: str = Field(description="分类 (overlay/oscillator)")
    description: str = Field(description="指标描述")
    default_params: Dict[str, Any] = Field(description="默认参数")
    output_fields: List[str] = Field(description="输出字段说明")


class IndicatorRegistryResponse(BaseModel):
    """指标库响应"""

    indicators: List[IndicatorInfo] = Field(description="支持的指标列表")
    total_count: int = Field(description="指标总数")
    last_updated: datetime = Field(default_factory=datetime.now, description="最后更新时间")
