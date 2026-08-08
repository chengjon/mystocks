#!/usr/bin/env python3
"""
Phase 4 Validation Test: Trading Context
Phase 4验证测试：交易上下文

验证Trading Context的实现质量。
"""

import os
import sys
from datetime import datetime

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)


def test_trading_context_imports():
    """测试交易上下文导入"""
    print("\n" + "=" * 60)
    print("  测试1: Trading Context模块导入")
    print("=" * 60)

    passed = 0
    failed = 0

    tests = [
        ("OrderType value object", "from src.domain.trading.value_objects.order_type import OrderType"),
        ("OrderSide value object", "from src.domain.trading.value_objects.order_side import OrderSide"),
        ("OrderStatus enum", "from src.domain.trading.model.order_status import OrderStatus"),
        ("Order aggregate root", "from src.domain.trading.model.order import Order"),
        ("Position aggregate root", "from src.domain.trading.model.position import Position"),
        ("IOrderRepository interface", "from src.domain.trading.repository.iorder_repository import IOrderRepository"),
        (
            "IPositionRepository interface",
            "from src.domain.trading.repository.iposition_repository import IPositionRepository",
        ),
        (
            "Position events",
            "from src.domain.trading.model.position import PositionOpenedEvent, PositionIncreasedEvent, PositionDecreasedEvent, StopLossTriggeredEvent",
        ),
    ]

    for test_name, import_statement in tests:
        try:
            exec(import_statement)
            print(f"✅ {test_name}")
            passed += 1
        except Exception as e:
            print(f"❌ {test_name}: {e}")
            failed += 1

    print(f"\n导入测试结果: {passed} 通过, {failed} 失败")
    return passed, failed


def test_order_type():
    """测试OrderType值对象"""
    print("\n" + "=" * 60)
    print("  测试2: OrderType值对象")
    print("=" * 60)

    passed = 0
    failed = 0

    try:
        from src.domain.trading.value_objects.order_type import OrderType

        # 测试所有订单类型
        market = OrderType.MARKET
        limit = OrderType.LIMIT
        stop_market = OrderType.STOP_MARKET
        stop_limit = OrderType.STOP_LIMIT

        assert market.is_market_order()
        print("✅ MARKET订单识别正确")
        passed += 1

        assert limit.is_limit_order()
        print("✅ LIMIT订单识别正确")
        passed += 1

        assert stop_market.is_stop_order()
        assert stop_market.is_market_order()
        print("✅ STOP_MARKET订单识别正确")
        passed += 1

        assert stop_limit.is_stop_order()
        assert stop_limit.is_limit_order()
        print("✅ STOP_LIMIT订单识别正确")
        passed += 1

        # 测试枚举值
        assert OrderType.MARKET.value == "MARKET"
        print("✅ 枚举值正确")
        passed += 1

    except Exception as e:
        print(f"❌ OrderType测试失败: {e}")
        failed += 1

    print(f"\nOrderType测试结果: {passed} 通过, {failed} 失败")
    return passed, failed


def test_position_lifecycle():
    """测试Position聚合根生命周期"""
    print("\n" + "=" * 60)
    print("  测试3: Position聚合根生命周期")
    print("=" * 60)

    passed = 0
    failed = 0

    try:
        from src.domain.trading.model.position import Position
        from src.domain.trading.value_objects.order_side import OrderSide

        # 测试开仓
        print("\n📍 测试开仓...")
        position = Position.open_position(
            portfolio_id="portfolio_1",
            symbol="000001.SZ",
            quantity=1000,
            price=10.50,
            side=OrderSide.BUY,
            stop_loss=10.00,
            take_profit=11.50,
        )

        assert position.quantity == 1000
        assert position.avg_price == 10.50
        assert position.is_long
        assert position.stop_loss_price == 10.00
        assert position.take_profit_price == 11.50
        print("✅ 开仓成功")
        passed += 1

        # 检查开仓事件
        events = position.get_domain_events()
        assert len(events) == 1
        assert events[0].event_name() == "PositionOpenedEvent"
        print("✅ 开仓事件触发")
        passed += 1

        # 测试加仓
        print("\n📍 测试加仓...")
        position.increase_position(added_quantity=500, price=10.80)

        # 新平均成本 = (1000*10.50 + 500*10.80) / 1500 = 10.60
        expected_avg = (1000 * 10.50 + 500 * 10.80) / 1500
        assert abs(position.avg_price - expected_avg) < 0.01
        assert position.quantity == 1500
        print("✅ 加仓成功，平均成本更新正确")
        passed += 1

        # 检查加仓事件
        events = position.get_domain_events()
        assert len(events) == 1
        assert events[0].event_name() == "PositionIncreasedEvent"
        print("✅ 加仓事件触发")
        passed += 1

        # 测试减仓
        print("\n📍 测试减仓...")
        realized_profit = position.decrease_position(decreased_quantity=500, price=11.00)

        # 实现盈亏 = (11.00 - 10.60) * 500 = 200.00
        expected_profit = (11.00 - expected_avg) * 500
        assert abs(realized_profit - expected_profit) < 0.01
        assert position.quantity == 1000
        print(f"✅ 减仓成功，实现盈亏: {realized_profit:.2f}")
        passed += 1

        # 检查减仓事件
        events = position.get_domain_events()
        assert len(events) == 1
        assert events[0].event_name() == "PositionDecreasedEvent"
        print("✅ 减仓事件触发")
        passed += 1

        # 测试止损检查
        print("\n📍 测试止损检查...")
        position.set_stop_loss(10.20)

        # 价格低于止损价应触发
        assert position.check_stop_loss(current_price=10.10) == True
        print("✅ 止损触发正确")
        passed += 1

        # 检查止损事件
        events = position.get_domain_events()
        assert len(events) == 1
        assert events[0].event_name() == "StopLossTriggeredEvent"
        print("✅ 止损事件触发")
        passed += 1

        # 测试未实现盈亏计算
        unrealized = position.unrealized_profit(current_price=11.00)
        expected_unrealized = (11.00 - expected_avg) * 1000
        assert abs(unrealized - expected_unrealized) < 0.01
        print(f"✅ 未实现盈亏计算正确: {unrealized:.2f}")
        passed += 1

        # 测试盈亏比例
        profit_ratio = position.profit_ratio(current_price=11.00)
        # (11.00 - 10.60) / 10.60 * 100 = 3.77%
        assert 0 < profit_ratio < 10  # 应该是正数且合理范围
        print(f"✅ 盈亏比例计算正确: {profit_ratio:.2f}%")
        passed += 1

    except Exception as e:
        print(f"❌ Position生命周期测试失败: {e}")
        import traceback

        traceback.print_exc()
        failed += 1

    print(f"\nPosition生命周期测试结果: {passed} 通过, {failed} 失败")
    return passed, failed


def test_position_validation():
    """测试Position验证逻辑"""
    print("\n" + "=" * 60)
    print("  测试4: Position验证逻辑")
    print("=" * 60)

    passed = 0
    failed = 0

    try:
        from src.domain.trading.model.position import Position
        from src.domain.trading.value_objects.order_side import OrderSide

        # 测试多头止损价验证
        position = Position.open_position(
            portfolio_id="portfolio_1",
            symbol="000001.SZ",
            quantity=1000,
            price=10.50,
            side=OrderSide.BUY,
        )

        # 多头止损价必须低于成本价
        try:
            position.set_stop_loss(10.60)  # 高于成本价
            print("❌ 多头止损价验证失败（应该抛出异常）")
            failed += 1
        except ValueError:
            print("✅ 多头止损价验证正确")
            passed += 1

        # 测试多头止盈价验证
        try:
            position.set_take_profit(10.40)  # 低于成本价
            print("❌ 多头止盈价验证失败（应该抛出异常）")
            failed += 1
        except ValueError:
            print("✅ 多头止盈价验证正确")
            passed += 1

        # 测试空头持仓
        short_position = Position.open_position(
            portfolio_id="portfolio_1",
            symbol="000001.SZ",
            quantity=1000,
            price=10.50,
            side=OrderSide.SELL,
        )

        assert short_position.is_short
        assert short_position.quantity == -1000
        print("✅ 空头持仓创建成功")
        passed += 1

        # 空头止损价必须高于成本价
        try:
            short_position.set_stop_loss(10.40)  # 低于成本价
            print("❌ 空头止损价验证失败（应该抛出异常）")
            failed += 1
        except ValueError:
            print("✅ 空头止损价验证正确")
            passed += 1

    except Exception as e:
        print(f"❌ Position验证测试失败: {e}")
        import traceback

        traceback.print_exc()
        failed += 1

    print(f"\nPosition验证测试结果: {passed} 通过, {failed} 失败")
    return passed, failed


def test_repository_interfaces():
    """测试仓储接口定义"""
    print("\n" + "=" * 60)
    print("  测试5: 仓储接口定义")
    print("=" * 60)

    passed = 0
    failed = 0

    try:
        from src.domain.trading.repository.iorder_repository import IOrderRepository
        from src.domain.trading.repository.iposition_repository import IPositionRepository

        # 检查IOrderRepository方法
        required_methods = [
            "save",
            "find_by_id",
            "find_by_portfolio",
            "find_by_symbol",
            "find_by_status",
            "find_pending_orders",
            "find_recent_orders",
            "delete",
            "exists",
            "count_by_status",
        ]

        for method in required_methods:
            if hasattr(IOrderRepository, method):
                print(f"✅ IOrderRepository.{method}() 存在")
                passed += 1
            else:
                print(f"❌ IOrderRepository.{method}() 缺失")
                failed += 1

        # 检查IPositionRepository方法
        required_methods = [
            "save",
            "find_by_id",
            "find_by_portfolio",
            "find_by_portfolio_and_symbol",
            "find_open_positions",
            "find_by_symbol",
            "delete",
            "exists",
            "count_by_portfolio",
        ]

        for method in required_methods:
            if hasattr(IPositionRepository, method):
                print(f"✅ IPositionRepository.{method}() 存在")
                passed += 1
            else:
                print(f"❌ IPositionRepository.{method}() 缺失")
                failed += 1

    except Exception as e:
        print(f"❌ 仓储接口测试失败: {e}")
        failed += 1

    print(f"\n仓储接口测试结果: {passed} 通过, {failed} 失败")
    return passed, failed


def test_domain_events_completeness():
    """测试领域事件完整性"""
    print("\n" + "=" * 60)
    print("  测试6: Trading Context领域事件")
    print("=" * 60)

    passed = 0
    failed = 0

    try:
        from src.domain.trading.model.position import (
            PositionDecreasedEvent,
            PositionIncreasedEvent,
            PositionOpenedEvent,
            StopLossTriggeredEvent,
        )

        events_to_test = [
            (PositionOpenedEvent, "PositionOpenedEvent"),
            (PositionIncreasedEvent, "PositionIncreasedEvent"),
            (PositionDecreasedEvent, "PositionDecreasedEvent"),
            (StopLossTriggeredEvent, "StopLossTriggeredEvent"),
        ]

        for event_class, expected_name in events_to_test:
            # 创建事件实例
            if event_class == PositionOpenedEvent:
                event = PositionOpenedEvent(
                    position_id="test_position",
                    portfolio_id="test_portfolio",
                    symbol="000001.SZ",
                    quantity=1000,
                    price=10.50,
                )
            elif event_class == PositionIncreasedEvent:
                event = PositionIncreasedEvent(
                    position_id="test_position",
                    symbol="000001.SZ",
                    added_quantity=500,
                    new_total_quantity=1500,
                    new_avg_price=10.60,
                )
            elif event_class == PositionDecreasedEvent:
                event = PositionDecreasedEvent(
                    position_id="test_position",
                    symbol="000001.SZ",
                    decreased_quantity=500,
                    remaining_quantity=1000,
                    realized_profit=200.00,
                )
            elif event_class == StopLossTriggeredEvent:
                event = StopLossTriggeredEvent(
                    position_id="test_position",
                    portfolio_id="test_portfolio",
                    symbol="000001.SZ",
                    stop_loss_price=10.00,
                    current_price=9.90,
                    quantity=1000,
                )

            assert event.event_name() == expected_name
            print(f"✅ {expected_name} 创建成功")
            passed += 1

    except Exception as e:
        print(f"❌ 领域事件测试失败: {e}")
        import traceback

        traceback.print_exc()
        failed += 1

    print(f"\n领域事件测试结果: {passed} 通过, {failed} 失败")
    return passed, failed


def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("  Phase 4验证测试: Trading Context")
    print("=" * 60)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    total_passed = 0
    total_failed = 0

    # 运行所有测试
    p, f = test_trading_context_imports()
    total_passed += p
    total_failed += f

    p, f = test_order_type()
    total_passed += p
    total_failed += f

    p, f = test_position_lifecycle()
    total_passed += p
    total_failed += f

    p, f = test_position_validation()
    total_passed += p
    total_failed += f

    p, f = test_repository_interfaces()
    total_passed += p
    total_failed += f

    p, f = test_domain_events_completeness()
    total_passed += p
    total_failed += f

    # 总结
    print("\n" + "=" * 60)
    print("  测试总结")
    print("=" * 60)
    print(f"总通过: {total_passed}")
    print(f"总失败: {total_failed}")
    print(f"成功率: {total_passed/(total_passed+total_failed)*100:.1f}%")

    if total_failed == 0:
        print("\n🎉 Phase 4验证测试全部通过！Trading Context实施正确。")
        return 0
    else:
        print(f"\n⚠️  有{total_failed}项测试失败，请检查上述错误。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
