"""
Event Types for Event-Driven Backtesting

定义回测系统中的所有事件类型
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from decimal import Decimal


class EventType(str, Enum):
    """事件类型枚举"""

    MARKET = "market"  # 市场数据事件
    SIGNAL = "signal"  # 交易信号事件
    ORDER = "order"  # 订单事件
    FILL = "fill"  # 成交事件


class Event:
    """
    基础事件类

    所有事件的基类
    """

    def __init__(self, event_type: EventType):
        self.event_type = event_type
        self.timestamp = datetime.now()


class MarketEvent(Event):
    """
    市场数据事件

    当新的市场数据到达时触发
    """

    def __init__(
        self,
        symbol: str,
        trade_date: datetime,
        open_price: Decimal,
        high_price: Decimal,
        low_price: Decimal,
        close_price: Decimal,
        volume: int,
        adj_close: Optional[Decimal] = None,
    ):
        super().__init__(EventType.MARKET)
        self.symbol = symbol
        self.trade_date = trade_date
        self.open = open_price
        self.high = high_price
        self.low = low_price
        self.close = close_price
        self.volume = volume
        self.adj_close = adj_close or close_price

    def __repr__(self):
        return (
            f"MarketEvent(symbol={self.symbol}, date={self.trade_date}, " f"close={self.close}, volume={self.volume})"
        )


class SignalEvent(Event):
    """
    交易信号事件

    策略生成的交易信号
    """

    def __init__(
        self,
        symbol: str,
        trade_date: datetime,
        signal_type: str,  # 'LONG', 'SHORT', 'EXIT'
        strength: float = 1.0,  # 信号强度 0-1
        reason: Optional[str] = None,
    ):
        super().__init__(EventType.SIGNAL)
        self.symbol = symbol
        self.trade_date = trade_date
        self.signal_type = signal_type
        self.strength = strength
        self.reason = reason

    def __repr__(self):
        return (
            f"SignalEvent(symbol={self.symbol}, date={self.trade_date}, "
            f"type={self.signal_type}, strength={self.strength})"
        )


class OrderEvent(Event):
    """
    订单事件

    由信号生成的订单
    """

    def __init__(
        self,
        symbol: str,
        trade_date: datetime,
        order_type: str,  # 'MARKET', 'LIMIT', 'STOP'
        action: str,  # 'BUY', 'SELL'
        quantity: int,
        price: Optional[Decimal] = None,  # For LIMIT/STOP orders
        strategy_id: Optional[int] = None,
    ):
        super().__init__(EventType.ORDER)
        self.symbol = symbol
        self.trade_date = trade_date
        self.order_type = order_type
        self.action = action
        self.quantity = quantity
        self.price = price
        self.strategy_id = strategy_id

    def __repr__(self):
        return (
            f"OrderEvent(symbol={self.symbol}, date={self.trade_date}, "
            f"{self.action} {self.quantity}@{self.order_type})"
        )


class FillEvent(Event):
    """
    成交事件

    订单执行后的成交记录
    """

    def __init__(
        self,
        symbol: str,
        trade_date: datetime,
        action: str,  # 'BUY', 'SELL'
        quantity: int,
        fill_price: Decimal,  # 实际成交价格
        commission: Decimal,  # 手续费
        slippage: Decimal = Decimal("0"),  # 滑点
        strategy_id: Optional[int] = None,
    ):
        super().__init__(EventType.FILL)
        self.symbol = symbol
        self.trade_date = trade_date
        self.action = action
        self.quantity = quantity
        self.fill_price = fill_price
        self.commission = commission
        self.slippage = slippage
        self.strategy_id = strategy_id

        # 计算总金额（包含手续费）
        self.amount = (fill_price * Decimal(quantity)) + commission

    def __repr__(self):
        return (
            f"FillEvent(symbol={self.symbol}, date={self.trade_date}, "
            f"{self.action} {self.quantity}@{self.fill_price}, "
            f"commission={self.commission})"
        )


class ProgressEvent(Event):
    """
    进度更新事件（用于WebSocket推送）
    """

    def __init__(
        self,
        backtest_id: int,
        progress: float,  # 0-100
        current_date: datetime,
        message: str,
    ):
        super().__init__(EventType.MARKET)  # 复用MARKET类型
        self.backtest_id = backtest_id
        self.progress = progress
        self.current_date = current_date
        self.message = message

    def to_dict(self):
        """转换为字典用于JSON序列化"""
        return {
            "backtest_id": self.backtest_id,
            "progress": round(self.progress, 2),
            "current_date": self.current_date.isoformat(),
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
        }
