#!/usr/bin/env python3
"""
Phase 0: 垂直切片端到端测试
Vertical Slice End-to-End Test

测试完整流程：创建策略 -> 获取Mock数据 -> 生成信号 -> 创建订单
"""

import os
import sys
import time

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.domain.strategy.model.rule import Rule
from src.domain.strategy.model.strategy import Strategy
from src.domain.trading.model.order import OrderStatus
from src.infrastructure.market_data.mock_repository import MockMarketDataRepository


def print_section(title: str):
    """打印测试分节标题"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def test_phase_0_vertical_slice():
    """
    Phase 0 垂直切片测试

    流程：
        1. 创建SimpleStrategy（RSI > 70 策略）
        2. 获取Mock市场数据
        3. 执行策略，生成Signal
        4. 将Signal转化为Order
        5. 验证Order状态
    """

    checks_passed = 0  # 初始化计数器

    print_section("Phase 0: 垂直切片端到端测试")

    # ========================================
    # Step 1: 创建SimpleStrategy
    # ========================================
    print_section("Step 1: 创建SimpleStrategy（RSI > 70 卖出策略）")

    strategy = Strategy.create(name="Simple RSI Strategy", description="当RSI指标大于70时，生成卖出信号")

    # 添加规则：RSI > 70 -> SELL
    rsi_rule = Rule(indicator_name="RSI", operator=">", threshold=70.0, action="SELL")
    strategy.add_rule(rsi_rule)

    print(f"✓ 创建策略: {strategy}")
    print(f"  - ID: {strategy.id}")
    print(f"  - 规则: {strategy.rules[0]}")

    # 激活策略
    strategy.activate()
    print(f"✓ 策略已激活: {strategy.is_active}")

    # ========================================
    # Step 2: 获取Mock市场数据
    # ========================================
    print_section("Step 2: 获取Mock市场数据")

    mock_repo = MockMarketDataRepository()
    market_snapshot = mock_repo.get_market_snapshot("000001.SZ")

    print("✓ 获取市场快照:")
    print(f"  - 标的: {market_snapshot['symbol']}")
    print(f"  - 价格: {market_snapshot['price']}")
    print(f"  - 时间: {market_snapshot['timestamp']}")
    print("  - 指标:")
    for indicator, value in market_snapshot["indicators"].items():
        print(f"    * {indicator}: {value}")

    # ========================================
    # Step 3: 执行策略，生成Signal
    # ========================================
    print_section("Step 3: 执行策略，生成Signal")

    start_time = time.time()
    signals = strategy.execute(market_snapshot)
    execution_time = (time.time() - start_time) * 1000  # 转换为毫秒

    print("✓ 策略执行完成:")
    print(f"  - 执行时间: {execution_time:.2f} ms")
    print(f"  - 生成信号数量: {len(signals)}")

    for signal in signals:
        print("\n  Signal:")
        print(f"    - ID: {signal.signal_id}")
        print(f"    - 策略ID: {signal.strategy_id}")
        print(f"    - 标的: {signal.symbol}")
        print(f"    - 方向: {signal.side}")
        print(f"    - 价格: {signal.price}")
        print(f"    - 数量: {signal.quantity}")
        print(f"    - 原因: {signal.reason}")

    # ========================================
    # Step 4: 将Signal转化为Order
    # ========================================
    print_section("Step 4: 将Signal转化为Order")

    orders = strategy.convert_signals_to_orders(signals)

    print(f"✓ 创建订单数量: {len(orders)}")

    for order in orders:
        print("\n  Order:")
        print(f"    - ID: {order.id}")
        print(f"    - 标的: {order.symbol}")
        print(f"    - 方向: {order.side}")
        print(f"    - 数量: {order.quantity}")
        print(f"    - 价格: {order.price}")
        print(f"    - 状态: {order.status.value}")

    # ========================================
    # Step 5: 验证Order状态和事件
    # ========================================
    print_section("Step 5: 验证Order状态和事件")

    # 检查3: 订单创建成功（在成交前检查）
    # 保存订单初始状态用于统计
    initial_order_status = orders[0].status if len(orders) > 0 else None

    if len(orders) > 0 and orders[0].status == OrderStatus.SUBMITTED:
        print("✓ 检查3: 订单创建成功 - 通过")
        print(f"  订单状态: {orders[0].status.value}")
        checks_passed += 1
    else:
        print("✗ 检查3: 订单创建成功 - 失败")

    # 保存第一个订单的事件引用（用于后续检查）
    first_order_events = None

    for order in orders:
        print(f"\n✓ 验证订单 {order.id}:")

        # 测试订单成交
        print(f"  - 初始状态: {order.status.value}")
        print(f"  - 已成交数量: {order.filled_quantity}/{order.quantity}")

        # 模拟完全成交
        order.fill(order.quantity, order.price)
        print(f"  - 成交后状态: {order.status.value}")
        print(f"  - 成交比例: {order.fill_ratio:.1%}")

        # 检查领域事件
        events = order.get_domain_events()
        print(f"  - 领域事件数量: {len(events)}")

        # 保存第一个订单的事件
        if first_order_events is None and len(events) > 0:
            first_order_events = events

        for event in events:
            print(f"    * {event}")

    # ========================================
    # Step 6: 验收标准检查
    # ========================================
    print_section("Step 6: 验收标准检查")

    checks_total = 5

    # 检查1: 完整链路打通
    if len(signals) > 0 and len(orders) > 0:
        print("✓ 检查1: 完整链路打通 - 通过")
        print("  Domain (Strategy) -> Signal -> Order")
    else:
        print("✗ 检查1: 完整链路打通 - 失败")

    # 检查2: 信号生成正确
    if len(signals) > 0 and signals[0].side.value == "SELL":
        print("✓ 检查2: 信号生成正确 - 通过")
        print(f"  RSI ({market_snapshot['indicators']['RSI']}) > 70 -> SELL")
    else:
        print("✗ 检查2: 信号生成正确 - 失败")

    # 检查3: 已在Step 5中完成

    # 检查4: 性能基准（< 100ms）
    if execution_time < 100:
        print(f"✓ 检查4: 性能基准 - 通过 ({execution_time:.2f} ms < 100 ms)")
    else:
        print(f"✗ 检查4: 性能基准 - 失败 ({execution_time:.2f} ms >= 100 ms)")

    # 检查5: 领域事件触发
    events = first_order_events if first_order_events is not None else []
    if len(events) > 0 and events[0].event_name() == "OrderFilledEvent":
        print("✓ 检查5: 领域事件触发 - 通过")
        print(f"  事件类型: {events[0].event_name()}")
    else:
        print("✗ 检查5: 领域事件触发 - 失败")

    # 统计通过的检查
    checks_passed = sum(
        [
            len(signals) > 0 and len(orders) > 0,  # 检查1
            len(signals) > 0 and signals[0].side.value == "SELL",  # 检查2
            initial_order_status == OrderStatus.SUBMITTED,  # 检查3（使用初始状态）
            execution_time < 100,  # 检查4
            len(events) > 0 and events[0].event_name() == "OrderFilledEvent",  # 检查5
        ]
    )

    # ========================================
    # 总结
    # ========================================
    print_section("测试总结")
    print(f"通过检查: {checks_passed}/{checks_total}")

    if checks_passed == checks_total:
        print("\n🎉 Phase 0 验证成功！DDD架构垂直切片已打通。")
        print("\n下一步:")
        print("  1. 开始 Phase 1: 创建完整目录结构")
        print("  2. 实现 Phase 2: 共享内核（事件总线）")
        print("  3. 实现 Phase 3: 策略上下文完整实现")
        return True
    else:
        print("\n❌ Phase 0 验证失败，请检查上述失败项。")
        return False


if __name__ == "__main__":
    try:
        success = test_phase_0_vertical_slice()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 测试执行出错: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
