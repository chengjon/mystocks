"""
Indicator Configuration Value Object
技术指标配置值对象

定义技术指标的配置参数。
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional


class IndicatorType(Enum):
    """指标类型"""

    TREND = "trend"  # 趋势指标（MA, EMA, MACD）
    MOMENTUM = "momentum"  # 动量指标（RSI, KDJ）
    VOLATILITY = "volatility"  # 波动率指标（Bollinger, ATR）
    VOLUME = "volume"  # 成交量指标（OBV, VWAP）
    CUSTOM = "custom"  # 自定义指标


@dataclass(frozen=True)
class IndicatorConfig:
    """
    技术指标配置值对象

    职责：
    - 定义技术指标的类型和参数
    - 提供指标参数验证
    - 支持指标配置序列化

    不变性：
    - 一旦创建不可修改
    - 参数配置完整且有效
    """

    name: str  # 指标名称，如 "RSI", "MACD", "MA"
    indicator_type: IndicatorType  # 指标类型
    parameters: Dict[str, Any]  # 指标参数，如 {"period": 14, "overbought": 70}
    source: Optional[str] = None  # 数据源，如 "close", "high", "low"

    def __post_init__(self):
        """验证指标配置"""
        if not self.name:
            raise ValueError("Indicator name cannot be empty")

        if not self.parameters:
            raise ValueError(f"Indicator {self.name} parameters cannot be empty")

        # 验证必需参数
        required_params = self._get_required_parameters()
        for param in required_params:
            if param not in self.parameters:
                raise ValueError(f"Indicator {self.name} missing required parameter: {param}")

    def _get_required_parameters(self) -> set[str]:
        """获取指标必需参数"""
        common_required = {"period"} if "period" in str(self.parameters) else set()
        return common_required

    def get_parameter(self, key: str, default: Any = None) -> Any:
        """获取参数值"""
        return self.parameters.get(key, default)

    @classmethod
    def rsi(cls, period: int = 14, overbought: float = 70.0, oversold: float = 30.0) -> "IndicatorConfig":
        """创建RSI指标配置"""
        return cls(
            name="RSI",
            indicator_type=IndicatorType.MOMENTUM,
            parameters={
                "period": period,
                "overbought": overbought,
                "oversold": oversold,
            },
            source="close",
        )

    @classmethod
    def macd(
        cls,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9,
    ) -> "IndicatorConfig":
        """创建MACD指标配置"""
        return cls(
            name="MACD",
            indicator_type=IndicatorType.TREND,
            parameters={
                "fast_period": fast_period,
                "slow_period": slow_period,
                "signal_period": signal_period,
            },
            source="close",
        )

    @classmethod
    def ma(cls, period: int = 20, ma_type: str = "SMA") -> "IndicatorConfig":
        """创建移动平均线指标配置"""
        return cls(
            name=f"{ma_type}",
            indicator_type=IndicatorType.TREND,
            parameters={"period": period, "type": ma_type},
            source="close",
        )

    def __str__(self) -> str:
        return f"IndicatorConfig(name={self.name}, type={self.indicator_type.value})"
