"""
交易信号实体
Signal Entity

表示策略生成的交易信号（买入/卖出建议）。
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from ...trading.value_objects.order_side import OrderSide
from ..value_objects.strategy_id import StrategyId


@dataclass
class Signal:
    """
    交易信号实体

    职责：
    - 表示策略生成的交易建议
    - 包含信号的所有关键信息
    - 可被Trading Context消费并转化为Order

    Attributes:
        signal_id: 信号唯一标识
        strategy_id: 生成信号的策略ID
        symbol: 交易标的代码
        side: 交易方向（买入/卖出）
        price: 建议价格
        quantity: 建议数量
        confidence: 信号置信度（0-1）
        reason: 信号生成原因
        created_at: 信号生成时间
    """

    signal_id: str
    strategy_id: StrategyId
    symbol: str
    side: OrderSide
    price: float
    quantity: int
    confidence: float = 1.0
    reason: Optional[str] = None
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

        # 验证置信度范围
        if not 0 <= self.confidence <= 1:
            raise ValueError(f"Confidence must be between 0 and 1, got {self.confidence}")

        # 验证价格和数量
        if self.price <= 0:
            raise ValueError(f"Price must be positive, got {self.price}")

        if self.quantity <= 0:
            raise ValueError(f"Quantity must be positive, got {self.quantity}")

    def is_buy(self) -> bool:
        """是否为买入信号"""
        return self.side == OrderSide.BUY

    def is_sell(self) -> bool:
        """是否为卖出信号"""
        return self.side == OrderSide.SELL

    def __str__(self) -> str:
        return (
            f"Signal(id={self.signal_id}, "
            f"symbol={self.symbol}, "
            f"side={self.side}, "
            f"price={self.price}, "
            f"quantity={self.quantity}, "
            f"confidence={self.confidence:.2f})"
        )
