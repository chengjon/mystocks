"""
Trading Context Domain Events
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from src.domain.shared.event import DomainEvent
from .value_objects import OrderSide, OrderType, OrderStatus

@dataclass
class OrderCreatedEvent(DomainEvent):
    """订单创建事件"""
    order_id: str
    symbol: str
    quantity: int
    price: Optional[float]
    side: OrderSide
    order_type: OrderType
    created_at: datetime

@dataclass
class OrderSubmittedEvent(DomainEvent):
    """订单提交事件"""
    order_id: str
    submitted_at: datetime

@dataclass
class OrderFilledEvent(DomainEvent):
    """
    订单成交事件 (关键事件)
    Portfolio Context 监听此事件以更新持仓和资金
    """
    order_id: str
    symbol: str
    filled_quantity: int
    filled_price: float
    side: OrderSide
    commission: float
    filled_at: datetime
    is_fully_filled: bool

@dataclass
class OrderCancelledEvent(DomainEvent):
    """订单撤销事件"""
    order_id: str
    reason: str
    cancelled_at: datetime

@dataclass
class OrderRejectedEvent(DomainEvent):
    """订单拒绝事件"""
    order_id: str
    reason: str
    rejected_at: datetime

@dataclass
class StopLossTriggeredEvent(DomainEvent):
    """止损触发事件"""
    position_id: str
    symbol: str
    trigger_price: float
    current_price: float
    triggered_at: datetime
