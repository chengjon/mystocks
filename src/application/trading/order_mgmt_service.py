"""
Order Management Application Service
订单管理应用服务
"""

import logging
from typing import Optional

from src.application.dto.trading_dto import CreateOrderRequest, OrderResponse
from src.domain.trading.model.order import Order
from src.domain.trading.repository import IOrderRepository
from src.domain.trading.value_objects import OrderId, OrderSide, OrderType

logger = logging.getLogger(__name__)


class OrderManagementService:
    def __init__(self, order_repo: IOrderRepository, event_bus: Optional[object] = None):
        self.order_repo = order_repo
        self.event_bus = event_bus

    def place_order(self, request: CreateOrderRequest) -> OrderResponse:
        """
        用例：下单流程
        1. 验证业务规则
        2. 创建领域对象
        3. 持久化
        4. 触发后续动作 (如提交柜台)
        """
        try:
            order = Order.create(
                symbol=request.symbol,
                quantity=request.quantity,
                side=OrderSide(request.side),
                order_type=OrderType(request.order_type),
                price=request.price,
            )

            order.submit()

            self.order_repo.save(order)
            self._publish_events(order)

            logger.info("Order placed successfully: {order.id")

            return self._map_to_response(order)

        except Exception:
            logger.error("Failed to place order: %(e)s")
            raise

    def handle_execution_report(self, order_id: str, filled_qty: int, price: float):
        """
        用例：处理成交回报
        """
        order = self.order_repo.get_by_id(OrderId(order_id))
        if not order:
            raise ValueError(f"Order not found: {order_id}")

        order.fill(filled_qty, price)

        self.order_repo.save(order)

        self._publish_events(order)

        return self._map_to_response(order)

    def _publish_events(self, order: Order) -> None:
        """发布订单的领域事件"""
        if not self.event_bus:
            return

        if not hasattr(order, "_domain_events"):
            return

        events = list(order._domain_events)
        order._domain_events.clear()

        for event in events:
            try:
                self.event_bus.publish(event)
            except Exception:
                logger.error("Failed to publish event: %(e)s")

    def _map_to_response(self, order: Order) -> OrderResponse:
        return OrderResponse(
            order_id=order.id.value,
            symbol=order.symbol,
            quantity=order.quantity,
            filled_quantity=order.filled_quantity,
            status=order.status.value,
            side=order.side.value,
            price=order.price,
            average_fill_price=order.average_fill_price,
            created_at=order.created_at,
        )
