"""
Signal Definition Value Object
信号定义值对象

定义交易信号的详细规格。
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from enum import Enum


class OrderSide(Enum):
    """订单方向（本地定义，避免跨上下文依赖）"""

    BUY = "BUY"
    SELL = "SELL"


class SignalStrength(Enum):
    """信号强度"""

    WEAK = "weak"  # 弱信号
    MODERATE = "moderate"  # 中等信号
    STRONG = "strong"  # 强信号


@dataclass(frozen=True)
class SignalDefinition:
    """
    信号定义值对象

    职责：
    - 定义交易信号的规格
    - 指定信号的方向和强度
    - 提供信号验证逻辑

    不变性：
    - 一旦创建不可修改
    - 信号规格完整有效
    """

    signal_type: str  # 信号类型，如 "BUY_SIGNAL", "SELL_SIGNAL"
    side: OrderSide  # 信号方向
    strength: SignalStrength  # 信号强度
    confidence: float  # 置信度 (0.0 - 1.0)
    reason_template: str  # 原因模板，如 "RSI({rsi_value}) > {threshold}"
    metadata: Dict[str, Any]  # 额外元数据

    def __post_init__(self):
        """验证信号定义"""
        if not self.signal_type:
            raise ValueError("signal_type cannot be empty")

        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError(f"confidence must be between 0.0 and 1.0, got {self.confidence}")

        if not self.reason_template:
            raise ValueError("reason_template cannot be empty")

    def format_reason(self, **kwargs) -> str:
        """
        格式化原因字符串

        Args:
            **kwargs: 模板变量

        Returns:
            格式化后的原因字符串
        """
        try:
            return self.reason_template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing template variable: {e}")

    @property
    def is_buy(self) -> bool:
        """是否为买入信号"""
        return self.side == OrderSide.BUY

    @property
    def is_sell(self) -> bool:
        """是否为卖出信号"""
        return self.side == OrderSide.SELL

    @classmethod
    def buy_signal(
        cls,
        strength: SignalStrength = SignalStrength.MODERATE,
        confidence: float = 0.8,
        reason_template: str = "Buy signal generated",
        **metadata,
    ) -> "SignalDefinition":
        """创建买入信号定义"""
        return cls(
            signal_type="BUY_SIGNAL",
            side=OrderSide.BUY,
            strength=strength,
            confidence=confidence,
            reason_template=reason_template,
            metadata=metadata,
        )

    @classmethod
    def sell_signal(
        cls,
        strength: SignalStrength = SignalStrength.MODERATE,
        confidence: float = 0.8,
        reason_template: str = "Sell signal generated",
        **metadata,
    ) -> "SignalDefinition":
        """创建卖出信号定义"""
        return cls(
            signal_type="SELL_SIGNAL",
            side=OrderSide.SELL,
            strength=strength,
            confidence=confidence,
            reason_template=reason_template,
            metadata=metadata,
        )

    def __str__(self) -> str:
        return (
            f"SignalDefinition(type={self.signal_type}, side={self.side.value}, "
            f"strength={self.strength.value}, confidence={self.confidence:.2f})"
        )
