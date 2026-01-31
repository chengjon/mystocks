"""
Shared Kernel
共享内核

包含所有限界上下文共享的核心概念、值对象和领域事件。
"""

from .domain_events import (
    OrderCreatedEvent,
    OrderFilledEvent,
    PortfolioRebalancedEvent,
    PositionClosedEvent,
    SignalGeneratedEvent,
    StrategyActivatedEvent,
    StrategyDeactivatedEvent,
)
from .event import DomainEvent
from .event_bus import IEventBus

__all__ = [
    # Event Base
    "DomainEvent",
    "IEventBus",
    # Core Domain Events
    "SignalGeneratedEvent",
    "OrderCreatedEvent",
    "OrderFilledEvent",
    "PositionClosedEvent",
    "PortfolioRebalancedEvent",
    "StrategyActivatedEvent",
    "StrategyDeactivatedEvent",
]
