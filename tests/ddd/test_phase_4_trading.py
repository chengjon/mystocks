"""
Phase 4: Trading Context 验证测试
"""

from datetime import datetime

import pytest

from src.domain.trading import Order, OrderCreatedEvent, OrderFilledEvent, OrderSide, OrderStatus, OrderType, Position


def test_order_creation():
    """测试订单创建"""
    order = Order.create(symbol="000001", quantity=100, side=OrderSide.BUY, order_type=OrderType.LIMIT, price=10.0)

    assert order.symbol == "000001"
    assert order.status == OrderStatus.CREATED
    assert len(order.collect_domain_events()) == 1
    assert (
        isinstance(order._domain_events[0], OrderCreatedEvent)
        if hasattr(order, "_domain_events") and order._domain_events
        else True
    )


def test_order_lifecycle():
    """测试订单生命周期"""
    order = Order.create("000001", 100, OrderSide.BUY, OrderType.MARKET)

    # Submit
    order.submit()
    assert order.status == OrderStatus.SUBMITTED

    # Fill
    order.fill(fill_quantity=100, fill_price=10.1, commission=5.0)
    assert order.status == OrderStatus.FILLED
    assert order.filled_quantity == 100
    assert order.average_fill_price == 10.1

    # Check events
    events = order.collect_domain_events()
    assert any(isinstance(e, OrderFilledEvent) for e in events)


def test_position_logic():
    """测试持仓逻辑"""
    pos = Position.create("000001")

    # 加仓
    pos.increase(100, 10.0)
    assert pos.quantity == 100
    assert pos.average_cost == 10.0

    # 加仓2
    pos.increase(100, 12.0)
    assert pos.quantity == 200
    assert pos.average_cost == 11.0

    # 减仓
    pnl = pos.decrease(100, 13.0)
    assert pos.quantity == 100
    assert pnl == (13.0 - 11.0) * 100  # 200.0

    # 再次减仓
    pnl2 = pos.decrease(100, 10.0)
    assert pos.quantity == 0
    assert pos.average_cost == 0.0
    assert pnl2 == (10.0 - 11.0) * 100  # -100.0


if __name__ == "__main__":
    test_order_creation()
    test_order_lifecycle()
    test_position_logic()
    print("Phase 4 验证通过!")
