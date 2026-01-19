"""
订单方向值对象
Order Side Value Object

表示买入或卖出的方向。
"""

from enum import Enum


class OrderSide(Enum):
    """订单方向枚举"""

    BUY = "BUY"
    SELL = "SELL"

    def __str__(self) -> str:
        return self.value

    @classmethod
    def from_string(cls, value: str) -> "OrderSide":
        """从字符串创建OrderSide"""
        if value.upper() == "BUY":
            return cls.BUY
        elif value.upper() == "SELL":
            return cls.SELL
        else:
            raise ValueError(f"Invalid OrderSide: {value}")
