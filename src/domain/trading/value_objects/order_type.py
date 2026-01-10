"""
Order Type Value Object
订单类型值对象

定义订单的类型枚举。
"""

from enum import Enum


class OrderType(Enum):
    """
    订单类型

    职责：
    - 定义不同类型的订单
    - 提供订单类型验证

    类型说明：
    - MARKET: 市价单，立即以当前市场价格成交
    - LIMIT: 限价单，指定价格成交
    - STOP_MARKET: 止损市价单，触发后转为市价单
    - STOP_LIMIT: 止损限价单，触发后转为限价单
    """

    MARKET = "MARKET"  # 市价单
    LIMIT = "LIMIT"  # 限价单
    STOP_MARKET = "STOP_MARKET"  # 止损市价单
    STOP_LIMIT = "STOP_LIMIT"  # 止损限价单

    def is_market_order(self) -> bool:
        """是否为市价单"""
        return self in {OrderType.MARKET, OrderType.STOP_MARKET}

    def is_limit_order(self) -> bool:
        """是否为限价单"""
        return self in {OrderType.LIMIT, OrderType.STOP_LIMIT}

    def is_stop_order(self) -> bool:
        """是否为止损订单"""
        return self in {OrderType.STOP_MARKET, OrderType.STOP_LIMIT}

    def __str__(self) -> str:
        return self.value
