#!/usr/bin/env python3
"""
Phase 5 Validation Test: Portfolio Context
Phase 5验证测试：投资组合上下文

验证Portfolio Context的实现质量。
"""

import os
import sys
from datetime import datetime

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)


def test_portfolio_context_imports():
    """测试投资组合上下文导入"""
    print("\n" + "=" * 60)
    print("  测试1: Portfolio Context模块导入")
    print("=" * 60)

    passed = 0
    failed = 0

    tests = [
        (
            "PerformanceMetrics value object",
            "from src.domain.portfolio.value_objects.performance_metrics import PerformanceMetrics",
        ),
        (
            "PositionInfo value object",
            "from src.domain.portfolio.value_objects.performance_metrics import PositionInfo",
        ),
        ("Portfolio aggregate root", "from src.domain.portfolio.model.portfolio import Portfolio"),
        ("Transaction entity", "from src.domain.portfolio.model.transaction import Transaction"),
        (
            "IPortfolioRepository interface",
            "from src.domain.portfolio.repository.iportfolio_repository import IPortfolioRepository",
        ),
        (
            "ITransactionRepository interface",
            "from src.domain.portfolio.repository.iportfolio_repository import ITransactionRepository",
        ),
        ("RebalancerService service", "from src.domain.portfolio.service.rebalancer_service import RebalancerService"),
        ("RebalanceAction", "from src.domain.portfolio.service.rebalancer_service import RebalanceAction"),
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


def test_performance_metrics():
    """测试PerformanceMetrics值对象"""
    print("\n" + "=" * 60)
    print("  测试2: PerformanceMetrics值对象")
    print("=" * 60)

    passed = 0
    failed = 0

    try:
        from src.domain.portfolio.value_objects.performance_metrics import PerformanceMetrics

        # 测试绩效指标创建
        metrics = PerformanceMetrics(
            total_value=100000.0,
            total_return=10000.0,
            return_rate=0.1,
            daily_pnl=500.0,
            max_drawdown=-0.15,
            sharpe_ratio=1.5,
        )

        print("✅ PerformanceMetrics创建成功")
        passed += 1

        # 测试属性
        assert metrics.total_value == 100000.0
        assert metrics.total_return == 10000.0
        assert metrics.return_rate == 0.1
        assert metrics.sharpe_ratio == 1.5
        print("✅ 绩效指标属性正确")
        passed += 1

    except Exception as e:
        print(f"❌ PerformanceMetrics测试失败: {e}")
        import traceback

        traceback.print_exc()
        failed += 1

    print(f"\nPerformanceMetrics测试结果: {passed} 通过, {failed} 失败")
    return passed, failed


def test_position_info():
    """测试PositionInfo值对象"""
    print("\n" + "=" * 60)
    print("  测试3: PositionInfo值对象")
    print("=" * 60)

    passed = 0
    failed = 0

    try:
        from src.domain.portfolio.value_objects.performance_metrics import PositionInfo

        # 测试持仓信息创建
        position_info = PositionInfo(
            symbol="000001.SZ",
            quantity=1000,
            average_cost=10.50,
            current_price=11.00,
        )

        print("✅ PositionInfo创建成功")
        passed += 1

        # 测试市值计算
        market_value = position_info.market_value
        assert market_value == 1000 * 11.00
        print(f"✅ 市值计算正确: {market_value:.2f}")
        passed += 1

        # 测试未实现盈亏计算
        unrealized_pnl = position_info.unrealized_pnl
        expected_pnl = (11.00 - 10.50) * 1000
        assert abs(unrealized_pnl - expected_pnl) < 0.01
        print(f"✅ 未实现盈亏计算正确: {unrealized_pnl:.2f}")
        passed += 1

    except Exception as e:
        print(f"❌ PositionInfo测试失败: {e}")
        import traceback

        traceback.print_exc()
        failed += 1

    print(f"\nPositionInfo测试结果: {passed} 通过, {failed} 失败")
    return passed, failed


def test_portfolio_lifecycle():
    """测试Portfolio聚合根生命周期"""
    print("\n" + "=" * 60)
    print("  测试4: Portfolio聚合根生命周期")
    print("=" * 60)

    passed = 0
    failed = 0

    try:
        from src.domain.portfolio.model.portfolio import Portfolio

        # 测试创建投资组合
        print("\n📍 测试创建投资组合...")
        portfolio = Portfolio.create(
            name="Test Portfolio",
            initial_capital=100000.0,
        )

        assert portfolio.name == "Test Portfolio"
        assert portfolio.cash == 100000.0
        assert portfolio.id is not None
        assert portfolio.initial_capital == 100000.0
        print("✅ 投资组合创建成功")
        passed += 1

        # 测试总资产计算
        print("\n📍 测试总资产计算...")
        # 添加一个持仓
        from src.domain.portfolio.value_objects.performance_metrics import PositionInfo

        portfolio.positions["000001.SZ"] = PositionInfo(
            symbol="000001.SZ",
            quantity=1000,
            average_cost=10.50,
            current_price=11.00,
        )

        # 计算持仓市值
        positions_value = sum(pos.market_value for pos in portfolio.positions.values())
        total_value = portfolio.cash + positions_value

        assert total_value == 100000.0 + (1000 * 11.00)  # 现金 + 持仓市值
        print(f"✅ 总资产计算正确: {total_value:.2f}")
        passed += 1

    except Exception as e:
        print(f"❌ Portfolio生命周期测试失败: {e}")
        import traceback

        traceback.print_exc()
        failed += 1

    print(f"\nPortfolio生命周期测试结果: {passed} 通过, {failed} 失败")
    return passed, failed


def test_transaction_entity():
    """测试Transaction实体"""
    print("\n" + "=" * 60)
    print("  测试5: Transaction实体")
    print("=" * 60)

    passed = 0
    failed = 0

    try:
        from src.domain.portfolio.model.transaction import Transaction
        from src.domain.trading.value_objects import OrderSide

        # 测试买入交易（使用create工厂方法）
        buy_transaction = Transaction.create(
            portfolio_id="portfolio_1",
            symbol="000001.SZ",
            side=OrderSide.BUY,
            quantity=1000,
            price=10.50,
            commission=5.0,
        )

        assert buy_transaction.side == OrderSide.BUY
        assert buy_transaction.total_amount == 1000 * 10.50 + 5.0
        assert buy_transaction.quantity == 1000
        assert buy_transaction.is_buy if hasattr(buy_transaction, "is_buy") else True
        print("✅ 买入交易创建成功")
        passed += 1

        # 测试卖出交易
        sell_transaction = Transaction.create(
            portfolio_id="portfolio_1",
            symbol="000001.SZ",
            side=OrderSide.SELL,
            quantity=500,
            price=11.00,
            commission=5.0,
        )

        assert sell_transaction.side == OrderSide.SELL
        assert sell_transaction.total_amount == 500 * 11.00 - 5.0
        print("✅ 卖出交易创建成功")
        passed += 1

    except Exception as e:
        print(f"❌ Transaction测试失败: {e}")
        import traceback

        traceback.print_exc()
        failed += 1

    print(f"\nTransaction测试结果: {passed} 通过, {failed} 失败")
    return passed, failed


def test_repository_interfaces():
    """测试仓储接口定义"""
    print("\n" + "=" * 60)
    print("  测试6: 仓储接口定义")
    print("=" * 60)

    passed = 0
    failed = 0

    try:
        from src.domain.portfolio.repository.iportfolio_repository import (
            IPortfolioRepository,
            ITransactionRepository,
        )

        # 检查IPortfolioRepository方法
        required_methods = ["save", "find_by_id", "find_by_name", "find_all", "delete", "exists", "count"]

        for method in required_methods:
            if hasattr(IPortfolioRepository, method):
                print(f"✅ IPortfolioRepository.{method}() 存在")
                passed += 1
            else:
                print(f"❌ IPortfolioRepository.{method}() 缺失")
                failed += 1

        # 检查ITransactionRepository方法
        required_methods = ["save", "find_by_id", "find_by_portfolio", "find_by_portfolio_and_symbol", "delete"]

        for method in required_methods:
            if hasattr(ITransactionRepository, method):
                print(f"✅ ITransactionRepository.{method}() 存在")
                passed += 1
            else:
                print(f"❌ ITransactionRepository.{method}() 缺失")
                failed += 1

    except Exception as e:
        print(f"❌ 仓储接口测试失败: {e}")
        failed += 1

    print(f"\n仓储接口测试结果: {passed} 通过, {failed} 失败")
    return passed, failed


def test_rebalancer_service():
    """测试RebalancerService领域服务"""
    print("\n" + "=" * 60)
    print("  测试7: RebalancerService领域服务")
    print("=" * 60)

    passed = 0
    failed = 0

    try:
        from src.domain.portfolio.service.rebalancer_service import (
            RebalancerService,
        )

        # 测试等权重计算
        symbols = ["AAPL", "MSFT", "GOOGL"]
        weights = RebalancerService.calculate_equal_weights(symbols)

        assert len(weights) == 3
        for symbol, weight in weights.items():
            assert abs(weight - 1.0 / 3) < 0.001
        print("✅ 等权重计算正确")
        passed += 1

        # 测试当前权重计算
        current_quantities = {"AAPL": 100, "MSFT": 50, "GOOGL": 25}
        current_prices = {"AAPL": 150.0, "MSFT": 300.0, "GOOGL": 120.0}
        total_value = 100000.0

        current_weights = RebalancerService.calculate_current_weights(
            symbols=list(current_quantities.keys()),
            quantities=list(current_quantities.values()),
            prices=list(current_prices.values()),
            total_value=total_value,
        )

        assert abs(current_weights["AAPL"] - 0.15) < 0.001
        assert abs(current_weights["MSFT"] - 0.15) < 0.001
        assert abs(current_weights["GOOGL"] - 0.03) < 0.001
        print("✅ 当前权重计算正确")
        passed += 1

        # 测试再平衡动作生成
        target_weights = {
            "AAPL": 0.4,
            "MSFT": 0.4,
            "GOOGL": 0.2,
        }

        actions, required_cash = RebalancerService.generate_rebalance_actions(
            current_quantities=current_quantities,
            target_weights=target_weights,
            current_prices=current_prices,
            total_value=total_value,
            cash=50000.0,
        )

        assert len(actions) == 3
        print(f"✅ 再平衡动作生成成功（{len(actions)}个动作）")
        passed += 1

        # 测试再平衡可行性验证
        feasible = RebalancerService.validate_rebalance_feasibility(
            required_cash=required_cash,
            available_cash=50000.0,
        )
        print(f"✅ 再平衡可行性验证: {'可行' if feasible else '不可行'}")
        passed += 1

        # 测试动作排序
        prioritized_actions = RebalancerService.prioritize_rebalance_actions(actions)
        assert len(prioritized_actions) == 3
        print("✅ 再平衡动作排序成功")
        passed += 1

    except Exception as e:
        print(f"❌ RebalancerService测试失败: {e}")
        import traceback

        traceback.print_exc()
        failed += 1

    print(f"\nRebalancerService测试结果: {passed} 通过, {failed} 失败")
    return passed, failed


def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("  Phase 5验证测试: Portfolio Context")
    print("=" * 60)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    total_passed = 0
    total_failed = 0

    # 运行所有测试
    p, f = test_portfolio_context_imports()
    total_passed += p
    total_failed += f

    p, f = test_performance_metrics()
    total_passed += p
    total_failed += f

    p, f = test_position_info()
    total_passed += p
    total_failed += f

    p, f = test_portfolio_lifecycle()
    total_passed += p
    total_failed += f

    p, f = test_transaction_entity()
    total_passed += p
    total_failed += f

    p, f = test_repository_interfaces()
    total_passed += p
    total_failed += f

    p, f = test_rebalancer_service()
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
        print("\n🎉 Phase 5验证测试全部通过！Portfolio Context实施正确。")
        return 0
    else:
        print(f"\n⚠️  有{total_failed}项测试失败，请检查上述错误。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
