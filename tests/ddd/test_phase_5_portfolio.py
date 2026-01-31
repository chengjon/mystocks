"""
Phase 5: Portfolio Context 验证测试
"""

from datetime import datetime

import pytest

from src.domain.portfolio import Portfolio, PositionInfo, RebalancerService
from src.domain.trading.events import OrderFilledEvent
from src.domain.trading.value_objects import OrderSide


def test_portfolio_transaction_flow():
    """测试组合资金流转"""
    # 1. 创建组合 (100万初始资金)
    p = Portfolio.create(name="Growth Fund", initial_capital=1000000.0)
    assert p.cash == 1000000.0
    assert len(p.positions) == 0

    # 2. 模拟买入成交 (买入 1000股 @ 100元, 佣金5元)
    buy_event = OrderFilledEvent(
        order_id="o1",
        symbol="000001",
        filled_quantity=1000,
        filled_price=100.0,
        side=OrderSide.BUY,
        commission=5.0,
        filled_at=datetime.now(),
        is_fully_filled=True,
    )
    p.handle_order_filled(buy_event)

    # 验证：现金减少，持仓增加
    expected_cash = 1000000.0 - (1000 * 100.0 + 5.0)
    assert p.cash == expected_cash
    assert "000001" in p.positions
    assert p.positions["000001"].quantity == 1000
    assert p.positions["000001"].average_cost == 100.005  # (100000 + 5)/1000
    assert len(p.transactions) == 1

    # 3. 模拟卖出成交 (卖出 500股 @ 110元, 佣金5元)
    sell_event = OrderFilledEvent(
        order_id="o2",
        symbol="000001",
        filled_quantity=500,
        filled_price=110.0,
        side=OrderSide.SELL,
        commission=5.0,
        filled_at=datetime.now(),
        is_fully_filled=True,
    )
    p.handle_order_filled(sell_event)

    # 验证：现金回流，持仓减少
    expected_cash += 500 * 110.0 - 5.0
    assert p.cash == expected_cash
    assert p.positions["000001"].quantity == 500

    # 4. 验证绩效计算 (假设当前价格 120)
    p.update_market_prices({"000001": 120.0})
    metrics = p.calculate_performance()

    # 市值 = 现金 + (500 * 120)
    expected_total = p.cash + 60000.0
    assert metrics.total_value == expected_total
    assert metrics.total_return > 0  # 应该是正收益


def test_rebalancer_service():
    """测试再平衡逻辑"""
    p = Portfolio.create("Rebalance Test", 100000.0)
    # 持仓: A股 500股 @ 10元 (市值5000), 现金 95000
    p.positions["StockA"] = PositionInfo("StockA", 500, 10.0, current_price=10.0)
    p.cash = 95000.0

    # 目标: StockA 占比 50% (目标市值 50000)
    # 需要买入: (50000 - 5000) / 10 = 4500 股
    target_weights = {"StockA": 0.5}

    service = RebalancerService()
    orders = service.calculate_rebalance_orders(p, target_weights)

    assert len(orders) == 1
    req = orders[0]
    assert req.symbol == "StockA"
    assert req.side == OrderSide.BUY
    assert req.quantity == 4500


if __name__ == "__main__":
    test_portfolio_transaction_flow()
    test_rebalancer_service()
    print("Phase 5 验证通过!")
