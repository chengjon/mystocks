"""
Core Domain Events
核心领域事件

定义系统中的核心领域事件，用于跨上下文的通信。
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import uuid4

from .event import DomainEvent


@dataclass
class SignalGeneratedEvent:
    """
    信号生成事件

    当策略生成交易信号时发布。
    """
    signal_id: str
    strategy_id: str
    symbol: str
    side: str  # 'BUY' or 'SELL'
    price: float
    quantity: int
    confidence: float = 1.0
    reason: Optional[str] = None
    event_id: str = field(default_factory=lambda: str(uuid4()))
    occurred_on: datetime = field(default_factory=datetime.now)

    def event_name(self) -> str:
        return "SignalGeneratedEvent"


@dataclass
class OrderCreatedEvent:
    """
    订单创建事件

    当订单被创建并提交时发布。
    """
    order_id: str
    portfolio_id: str
    symbol: str
    side: str  # 'BUY' or 'SELL'
    quantity: int
    price: float
    order_type: str = "MARKET"  # MARKET or LIMIT
    event_id: str = field(default_factory=lambda: str(uuid4()))
    occurred_on: datetime = field(default_factory=datetime.now)

    def event_name(self) -> str:
        return "OrderCreatedEvent"


@dataclass
class OrderFilledEvent:
    """
    订单成交事件

    当订单完全成交时发布。
    注意：此事件在 Trading Context 中已定义，这里提供共享版本。
    """
    order_id: str
    symbol: str
    filled_quantity: int
    filled_price: float
    portfolio_id: Optional[str] = None
    event_id: str = field(default_factory=lambda: str(uuid4()))
    occurred_on: datetime = field(default_factory=datetime.now)

    def event_name(self) -> str:
        return "OrderFilledEvent"


@dataclass
class PositionClosedEvent:
    """
    持仓平仓事件

    当持仓完全平仓时发布。
    """
    portfolio_id: str
    symbol: str
    closed_quantity: int
    avg_price: float
    total_cost: float
    total_proceeds: float
    realized_profit: float
    event_id: str = field(default_factory=lambda: str(uuid4()))
    occurred_on: datetime = field(default_factory=datetime.now)

    def event_name(self) -> str:
        return "PositionClosedEvent"


@dataclass
class PortfolioRebalancedEvent:
    """
    投资组合再平衡事件

    当投资组合完成再平衡操作时发布。
    """
    portfolio_id: str
    rebalance_id: str
    total_trades: int = 0
    total_value_before: float = 0.0
    total_value_after: float = 0.0
    event_id: str = field(default_factory=lambda: str(uuid4()))
    occurred_on: datetime = field(default_factory=datetime.now)

    def event_name(self) -> str:
        return "PortfolioRebalancedEvent"


@dataclass
class StrategyActivatedEvent:
    """
    策略激活事件

    当策略被激活时发布。
    """
    strategy_id: str
    strategy_name: str
    event_id: str = field(default_factory=lambda: str(uuid4()))
    activated_at: datetime = field(default_factory=datetime.now)

    def event_name(self) -> str:
        return "StrategyActivatedEvent"


@dataclass
class StrategyDeactivatedEvent:
    """
    策略停用事件

    当策略被停用时发布。
    """
    strategy_id: str
    strategy_name: str
    reason: Optional[str] = None
    event_id: str = field(default_factory=lambda: str(uuid4()))
    deactivated_at: datetime = field(default_factory=datetime.now)

    def event_name(self) -> str:
        return "StrategyDeactivatedEvent"
