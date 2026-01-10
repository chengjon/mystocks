"""
Tick Value Object
分笔数据值对象

表示逐笔成交数据。
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class Tick:
    """
    分笔数据值对象

    职责：
    - 表示逐笔成交数据
    - 提供分笔数据验证
    - 支持买卖方向标识

    属性：
    - symbol: 标的代码
    - timestamp: 时间戳（精确到毫秒）
    - price: 成交价格
    - volume: 成交数量
    - amount: 成交额
    - direction: 买卖方向（1=买入, -1=卖出, 0=未知）

    不变量：
    - 成交价格必须为正数
    - 成交数量必须为正数
    - 成交额必须为正数
    - 买卖方向必须在{-1, 0, 1}范围内
    """

    symbol: str
    timestamp: datetime
    price: float
    volume: int
    amount: float
    direction: int = 0  # 1=买, -1=卖, 0=未知

    def __post_init__(self):
        """验证分笔数据"""
        if self.price <= 0:
            raise ValueError(f"Price must be positive: {self.price}")

        if self.volume <= 0:
            raise ValueError(f"Volume must be positive: {self.volume}")

        if self.amount <= 0:
            raise ValueError(f"Amount must be positive: {self.amount}")

        # 验证买卖方向
        if self.direction not in {-1, 0, 1}:
            raise ValueError(f"Direction must be -1, 0, or 1: {self.direction}")

    @property
    def is_buy(self) -> bool:
        """是否为买入"""
        return self.direction == 1

    @property
    def is_sell(self) -> bool:
        """是否为卖出"""
        return self.direction == -1

    @property
    def avg_price(self) -> float:
        """平均价格（成交额 / 成交量）"""
        return self.amount / self.volume if self.volume > 0 else 0.0

    def __str__(self) -> str:
        direction_str = {1: "BUY", -1: "SELL", 0: "UNKNOWN"}.get(self.direction, "UNKNOWN")
        return (
            f"Tick(symbol={self.symbol}, timestamp={self.timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}, "
            f"price={self.price:.2f}, volume={self.volume}, {direction_str})"
        )
