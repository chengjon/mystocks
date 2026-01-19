"""
Order Aggregate Root
订单聚合根，包含完整的状态机逻辑
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from src.domain.shared.event import DomainEvent
from ..value_objects import OrderId, OrderSide, OrderType, OrderStatus, TimeInForce
from ..events import OrderCreatedEvent, OrderSubmittedEvent, OrderFilledEvent, OrderCancelledEvent, OrderRejectedEvent


@dataclass
class OrderFill:
    """订单成交记录值对象"""

    fill_id: str
    quantity: int
    price: float
    commission: float
    filled_at: datetime


@dataclass
class Order:
    """
    订单聚合根

    职责:
    - 管理订单生命周期状态机
    - 记录成交明细
    - 生成领域事件
    """

    id: OrderId
    symbol: str
    quantity: int
    price: Optional[float]  # 市价单可能为None
    side: OrderSide
    order_type: OrderType
    status: OrderStatus = field(default=OrderStatus.CREATED)
    time_in_force: TimeInForce = field(default=TimeInForce.DAY)
    filled_quantity: int = field(default=0)
    average_fill_price: float = field(default=0.0)
    commission_paid: float = field(default=0.0)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    fills: List[OrderFill] = field(default_factory=list)

    # 领域事件缓冲区
    _domain_events: List[DomainEvent] = field(default_factory=list, init=False, repr=False)

    def __post_init__(self):
        # 确保初始化时有 _domain_events
        if not hasattr(self, "_domain_events"):
            self._domain_events = []

    @classmethod
    def create(cls, symbol: str, quantity: int, side: OrderSide, order_type: OrderType, price: float = None) -> "Order":
        """工厂方法：创建新订单"""
        if quantity <= 0:
            raise ValueError("Order quantity must be positive")
        if order_type == OrderType.LIMIT and (price is None or price <= 0):
            raise ValueError("Limit order must have a positive price")

        order_id = OrderId(str(uuid4()))
        order = cls(id=order_id, symbol=symbol, quantity=quantity, price=price, side=side, order_type=order_type)

        # 记录创建事件
        order.add_domain_event(
            OrderCreatedEvent(
                order_id=order_id.value,
                symbol=symbol,
                quantity=quantity,
                price=price,
                side=side,
                order_type=order_type,
                created_at=order.created_at,
            )
        )

        return order

    def submit(self) -> None:
        """提交订单"""
        if self.status != OrderStatus.CREATED:
            raise RuntimeError(f"Cannot submit order in status {self.status}")

        self.status = OrderStatus.SUBMITTED
        self.updated_at = datetime.now()

        self.add_domain_event(OrderSubmittedEvent(order_id=self.id.value, submitted_at=self.updated_at))

    def fill(self, fill_quantity: int, fill_price: float, commission: float = 0.0) -> None:
        """
        处理成交回报
        """
        if self.status in [OrderStatus.CANCELLED, OrderStatus.REJECTED, OrderStatus.EXPIRED]:
            raise RuntimeError(f"Cannot fill order in status {self.status}")

        if fill_quantity <= 0:
            raise ValueError("Fill quantity must be positive")

        if self.filled_quantity + fill_quantity > self.quantity:
            raise ValueError("Fill quantity exceeds remaining quantity")

        # 更新成交统计
        total_value = (self.filled_quantity * self.average_fill_price) + (fill_quantity * fill_price)
        self.filled_quantity += fill_quantity
        self.average_fill_price = total_value / self.filled_quantity
        self.commission_paid += commission

        # 记录成交明细
        fill = OrderFill(
            fill_id=str(uuid4()),
            quantity=fill_quantity,
            price=fill_price,
            commission=commission,
            filled_at=datetime.now(),
        )
        self.fills.append(fill)
        self.updated_at = fill.filled_at

        # 更新状态
        is_fully_filled = self.filled_quantity == self.quantity
        if is_fully_filled:
            self.status = OrderStatus.FILLED
        else:
            self.status = OrderStatus.PARTIALLY_FILLED

        # 触发关键领域事件
        self.add_domain_event(
            OrderFilledEvent(
                order_id=self.id.value,
                symbol=self.symbol,
                filled_quantity=fill_quantity,
                filled_price=fill_price,
                side=self.side,
                commission=commission,
                filled_at=self.updated_at,
                is_fully_filled=is_fully_filled,
            )
        )

    def cancel(self, reason: str = "") -> None:
        """撤销订单"""
        if self.status in [OrderStatus.FILLED, OrderStatus.CANCELLED, OrderStatus.REJECTED]:
            raise RuntimeError(f"Cannot cancel order in status {self.status}")

        self.status = OrderStatus.CANCELLED
        self.updated_at = datetime.now()

        self.add_domain_event(OrderCancelledEvent(order_id=self.id.value, reason=reason, cancelled_at=self.updated_at))

    def reject(self, reason: str) -> None:
        """拒绝订单"""
        self.status = OrderStatus.REJECTED
        self.updated_at = datetime.now()

        self.add_domain_event(OrderRejectedEvent(order_id=self.id.value, reason=reason, rejected_at=self.updated_at))

    def add_domain_event(self, event: DomainEvent):
        if not hasattr(self, "_domain_events"):
            self._domain_events = []
        self._domain_events.append(event)

    def collect_domain_events(self) -> List[DomainEvent]:
        if not hasattr(self, "_domain_events"):
            return []
        events = list(self._domain_events)
        self._domain_events.clear()
        return events
