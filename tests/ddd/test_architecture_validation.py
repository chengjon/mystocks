#!/usr/bin/env python3
"""
DDD Architecture Validation Test
DDD架构验证测试

验证Phase 0-3实施的完整性和正确性。
"""

import os
import sys
from datetime import datetime

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)


def test_imports():
    """测试所有模块导入"""
    print("\n" + "=" * 60)
    print("  测试1: 模块导入验证")
    print("=" * 60)

    passed = 0
    failed = 0

    # 测试共享内核导入
    tests = [
        ("Shared Kernel - DomainEvent", "from src.domain.shared import DomainEvent"),
        ("Shared Kernel - IEventBus", "from src.domain.shared import IEventBus"),
        (
            "Shared Kernel - DomainEvents",
            "from src.domain.shared.domain_events import SignalGeneratedEvent, OrderCreatedEvent, OrderFilledEvent",
        ),
        ("Strategy Context - StrategyId", "from src.domain.strategy.value_objects.strategy_id import StrategyId"),
        (
            "Strategy Context - InstrumentPool",
            "from src.domain.strategy.value_objects.instrument_pool import InstrumentPool",
        ),
        (
            "Strategy Context - IndicatorConfig",
            "from src.domain.strategy.value_objects.indicator_config import IndicatorConfig",
        ),
        (
            "Strategy Context - SignalDefinition",
            "from src.domain.strategy.value_objects.signal_definition import SignalDefinition",
        ),
        ("Strategy Context - Rule", "from src.domain.strategy.model.rule import Rule"),
        ("Strategy Context - Parameter", "from src.domain.strategy.model.parameter import Parameter"),
        ("Strategy Context - Strategy", "from src.domain.strategy.model.strategy import Strategy"),
        (
            "Strategy Context - IIndicatorCalculator",
            "from src.domain.strategy.service.indicator_calculator import IIndicatorCalculator",
        ),
        (
            "Strategy Context - SignalGenerationService",
            "from src.domain.strategy.service.signal_generation_service import SignalGenerationService",
        ),
        (
            "Strategy Context - IStrategyRepository",
            "from src.domain.strategy.repository.istrategy_repository import IStrategyRepository",
        ),
        ("Trading Context - OrderSide", "from src.domain.trading.value_objects.order_side import OrderSide"),
        ("Trading Context - OrderStatus", "from src.domain.trading.model.order_status import OrderStatus"),
        ("Trading Context - Order", "from src.domain.trading.model.order import Order"),
        ("Trading Context - Signal", "from src.domain.strategy.model.signal import Signal"),
        ("Market Data - Bar", "from src.domain.market_data.model.bar import Bar"),
        (
            "Market Data - IMarketDataRepository",
            "from src.domain.market_data.repository.imarket_data_repository import IMarketDataRepository",
        ),
        (
            "Infrastructure - MockMarketDataRepository",
            "from src.infrastructure.market_data.mock_repository import MockMarketDataRepository",
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


def test_value_objects():
    """测试值对象创建"""
    print("\n" + "=" * 60)
    print("  测试2: 值对象创建验证")
    print("=" * 60)

    passed = 0
    failed = 0

    try:
        from src.domain.strategy.value_objects.indicator_config import IndicatorConfig
        from src.domain.strategy.value_objects.instrument_pool import AssetClass, InstrumentPool
        from src.domain.strategy.value_objects.signal_definition import SignalDefinition, SignalStrength

        # 测试InstrumentPool
        pool = InstrumentPool.from_list(
            name="A股测试池", symbols=["000001.SZ", "600519.SH"], asset_class=AssetClass.EQUITY, max_positions=10
        )
        assert pool.size == 2
        assert pool.contains("000001.SZ")
        print("✅ InstrumentPool创建成功")
        passed += 1

        # 测试IndicatorConfig
        rsi_config = IndicatorConfig.rsi(period=14, overbought=70.0)
        assert rsi_config.name == "RSI"
        assert rsi_config.get_parameter("period") == 14
        print("✅ IndicatorConfig创建成功")
        passed += 1

        # 测试SignalDefinition
        signal_def = SignalDefinition.buy_signal(
            strength=SignalStrength.STRONG, confidence=0.9, reason_template="RSI({rsi}) > 70"
        )
        assert signal_def.is_buy
        assert signal_def.confidence == 0.9
        print("✅ SignalDefinition创建成功")
        passed += 1

    except Exception as e:
        print(f"❌ 值对象测试失败: {e}")
        failed += 1

    print(f"\n值对象测试结果: {passed} 通过, {failed} 失败")
    return passed, failed


def test_domain_events():
    """测试领域事件"""
    print("\n" + "=" * 60)
    print("  测试3: 领域事件验证")
    print("=" * 60)

    passed = 0
    failed = 0

    try:
        from src.domain.shared.domain_events import (
            OrderCreatedEvent,
            OrderFilledEvent,
            SignalGeneratedEvent,
        )

        # 测试SignalGeneratedEvent
        signal_event = SignalGeneratedEvent(
            signal_id="test_signal", strategy_id="strategy_1", symbol="000001.SZ", side="BUY", price=10.5, quantity=100
        )
        assert signal_event.event_name() == "SignalGeneratedEvent"
        print("✅ SignalGeneratedEvent创建成功")
        passed += 1

        # 测试OrderCreatedEvent
        order_event = OrderCreatedEvent(
            order_id="order_1", portfolio_id="portfolio_1", symbol="000001.SZ", side="BUY", quantity=100, price=10.5
        )
        assert order_event.event_name() == "OrderCreatedEvent"
        print("✅ OrderCreatedEvent创建成功")
        passed += 1

        # 测试OrderFilledEvent
        filled_event = OrderFilledEvent(order_id="order_1", symbol="000001.SZ", filled_quantity=100, filled_price=10.5)
        assert filled_event.event_name() == "OrderFilledEvent"
        print("✅ OrderFilledEvent创建成功")
        passed += 1

    except Exception as e:
        print(f"❌ 领域事件测试失败: {e}")
        failed += 1

    print(f"\n领域事件测试结果: {passed} 通过, {failed} 失败")
    return passed, failed


def test_parameter_entity():
    """测试参数实体"""
    print("\n" + "=" * 60)
    print("  测试4: 参数实体验证")
    print("=" * 60)

    passed = 0
    failed = 0

    try:
        from src.domain.strategy.model.parameter import Parameter

        # 测试整数参数
        int_param = Parameter.create_int_parameter(
            name="period", value=14, min_value=1, max_value=100, description="RSI周期"
        )
        assert int_param.value == 14
        assert int_param.parameter_type == "int"
        print("✅ 整数参数创建成功")
        passed += 1

        # 测试浮点数参数
        float_param = Parameter.create_float_parameter(
            name="threshold", value=70.0, min_value=0.0, max_value=100.0, description="RSI阈值"
        )
        assert float_param.value == 70.0
        assert float_param.parameter_type == "float"
        print("✅ 浮点数参数创建成功")
        passed += 1

        # 测试参数更新
        int_param.update(20)
        assert int_param.value == 20
        assert len(int_param.get_domain_events()) == 1  # 应该有1个变更事件
        print("✅ 参数更新成功，领域事件触发")
        passed += 1

    except Exception as e:
        print(f"❌ 参数实体测试失败: {e}")
        failed += 1

    print(f"\n参数实体测试结果: {passed} 通过, {failed} 失败")
    return passed, failed


def test_directory_structure():
    """测试目录结构"""
    print("\n" + "=" * 60)
    print("  测试5: 目录结构验证")
    print("=" * 60)

    passed = 0
    failed = 0

    required_dirs = [
        "src/domain/strategy/model",
        "src/domain/strategy/value_objects",
        "src/domain/strategy/service",
        "src/domain/strategy/repository",
        "src/domain/trading/model",
        "src/domain/trading/value_objects",
        "src/domain/trading/repository",
        "src/domain/portfolio/model",
        "src/domain/portfolio/value_objects",
        "src/domain/portfolio/service",
        "src/domain/portfolio/repository",
        "src/domain/market_data/model",
        "src/domain/market_data/value_objects",
        "src/domain/market_data/repository",
        "src/domain/monitoring/model",
        "src/domain/monitoring/value_objects",
        "src/domain/monitoring/service",
        "src/domain/shared",
        "src/application/strategy",
        "src/application/trading",
        "src/application/portfolio",
        "src/application/dto",
        "src/infrastructure/persistence/models",
        "src/infrastructure/persistence/repositories",
        "src/infrastructure/messaging",
        "src/infrastructure/calculation",
        "src/infrastructure/market_data",
        "src/interfaces/api",
        "src/interfaces/websocket",
    ]

    for dir_path in required_dirs:
        full_path = os.path.join(project_root, dir_path)
        if os.path.exists(full_path):
            init_file = os.path.join(full_path, "__init__.py")
            if os.path.exists(init_file):
                print(f"✅ {dir_path}/__init__.py")
                passed += 1
            else:
                print(f"⚠️  {dir_path}/ (缺少__init__.py)")
                failed += 1
        else:
            print(f"❌ {dir_path}/ (不存在)")
            failed += 1

    print(f"\n目录结构测试结果: {passed} 通过, {failed} 失败")
    return passed, failed


def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("  DDD架构验证测试")
    print("=" * 60)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    total_passed = 0
    total_failed = 0

    # 运行所有测试
    p, f = test_imports()
    total_passed += p
    total_failed += f

    p, f = test_value_objects()
    total_passed += p
    total_failed += f

    p, f = test_domain_events()
    total_passed += p
    total_failed += f

    p, f = test_parameter_entity()
    total_passed += p
    total_failed += f

    p, f = test_directory_structure()
    total_passed += p
    total_failed += f

    # 总结
    print("\n" + "=" * 60)
    print("  测试总结")
    print("=" * 60)
    print(f"总通过: {total_passed}")
    print(f"总失败: {total_failed}")
    print(f"成功率: {total_passed / (total_passed + total_failed) * 100:.1f}%")

    if total_failed == 0:
        print("\n🎉 所有验证测试通过！DDD架构实施正确。")
        return 0
    else:
        print(f"\n⚠️  有{total_failed}项测试失败，请检查上述错误。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
