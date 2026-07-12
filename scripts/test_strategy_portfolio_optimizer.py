"""测试策略投资组合优化器
Test Strategy Portfolio Optimizer

验证投资组合优化算法和风险管理功能。
Validates portfolio optimization algorithms and risk management features.
"""

import asyncio
import logging
import os
import sys
from datetime import datetime

import pandas as pd


# Setup project path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.portfolio.strategy_portfolio_optimizer import (
    PortfolioConstraints,
    StrategyInfo,
    StrategyPortfolioOptimizer,
)


# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_portfolio_optimizer():
    """测试投资组合优化器"""
    logger.info("🧪 开始测试策略投资组合优化器...")

    try:
        # 创建优化器
        constraints = PortfolioConstraints(
            max_weight=0.4,  # 最大权重40%
            min_weight=0.05,  # 最小权重5%
            max_volatility=0.20,  # 最大波动率20%
            min_sharpe_ratio=0.8,  # 最小夏普比率0.8
            max_drawdown_limit=0.12,  # 最大回撤12%
        )

        optimizer = StrategyPortfolioOptimizer(constraints)
        logger.info("✅ 投资组合优化器创建成功")

        # 添加测试策略
        strategies_data = [
            {
                "name": "SVM_Trend",
                "expected_return": 0.15,  # 15%年化收益
                "volatility": 0.18,  # 18%波动率
                "sharpe_ratio": 1.2,
                "max_drawdown": 0.08,
                "win_rate": 0.62,
                "avg_trade_pnl": 0.003,
                "total_trades": 150,
            },
            {
                "name": "DecisionTree_Momentum",
                "expected_return": 0.12,
                "volatility": 0.22,
                "sharpe_ratio": 0.9,
                "max_drawdown": 0.15,
                "win_rate": 0.58,
                "avg_trade_pnl": 0.002,
                "total_trades": 120,
            },
            {
                "name": "NaiveBayes_Value",
                "expected_return": 0.18,
                "volatility": 0.25,
                "sharpe_ratio": 1.1,
                "max_drawdown": 0.20,
                "win_rate": 0.65,
                "avg_trade_pnl": 0.004,
                "total_trades": 95,
            },
            {
                "name": "LSTM_Pattern",
                "expected_return": 0.22,
                "volatility": 0.30,
                "sharpe_ratio": 1.3,
                "max_drawdown": 0.18,
                "win_rate": 0.68,
                "avg_trade_pnl": 0.005,
                "total_trades": 80,
            },
        ]

        for strategy_data in strategies_data:
            strategy_info = StrategyInfo(
                name=strategy_data["name"],
                expected_return=strategy_data["expected_return"],
                volatility=strategy_data["volatility"],
                sharpe_ratio=strategy_data["sharpe_ratio"],
                max_drawdown=strategy_data["max_drawdown"],
                win_rate=strategy_data["win_rate"],
                avg_trade_pnl=strategy_data["avg_trade_pnl"],
                total_trades=strategy_data["total_trades"],
                last_updated=datetime.now(),
            )
            optimizer.add_strategy(strategy_info)

        logger.info("✅ 添加了 %d 个测试策略", len(strategies_data))

        # 测试MPT优化 (最大化夏普比率)
        logger.info("📊 测试MPT优化 (最大化夏普比率)...")
        mpt_allocation = optimizer.optimize_portfolio_mpt()
        logger.info(
            "MPT优化结果: 预期收益=%.2f%%, 波动率=%.2f%%, 夏普比率=%.2f",
            mpt_allocation.expected_return * 100,
            mpt_allocation.expected_volatility * 100,
            mpt_allocation.sharpe_ratio,
        )

        # 测试风险平价优化
        logger.info("📊 测试风险平价优化...")
        risk_parity_allocation = optimizer.optimize_portfolio_risk_parity()
        logger.info(
            "风险平价优化结果: 预期收益=%.2f%%, 波动率=%.2f%%",
            risk_parity_allocation.expected_return * 100,
            risk_parity_allocation.expected_volatility * 100,
        )

        # 测试MPT优化 (目标收益)
        logger.info("📊 测试MPT优化 (目标收益15%)...")
        target_allocation = optimizer.optimize_portfolio_mpt(target_return=0.15)
        logger.info(
            "目标收益优化结果: 波动率=%.2f%%, 夏普比率=%.2f",
            target_allocation.expected_volatility * 100,
            target_allocation.sharpe_ratio,
        )

        # 获取投资组合指标
        logger.info("📈 获取投资组合指标...")
        metrics = optimizer.get_portfolio_metrics()
        logger.info(
            "投资组合指标: 策略数量=%d, 分散化比率=%.2f",
            metrics["strategy_count"],
            metrics["portfolio_metrics"]["diversification_ratio"],
        )

        # 测试策略更新
        logger.info("🔄 测试策略性能更新...")
        updated_performance = {
            "expected_return": 0.20,  # 提高预期收益
            "volatility": 0.19,
            "sharpe_ratio": 1.4,
        }
        optimizer.update_strategy_performance("SVM_Trend", updated_performance)
        logger.info("✅ 策略性能更新成功")

        # 测试再平衡
        logger.info("⚖️ 测试投资组合再平衡...")
        rebalance_result = optimizer.rebalance_portfolio()
        if rebalance_result:
            logger.info("🔄 触发了再平衡: 新夏普比率=%.2f", rebalance_result.sharpe_ratio)
        else:
            logger.info("✅ 不需要再平衡")

        # 测试投资组合回测
        logger.info("📈 测试投资组合回测...")
        backtest_result = optimizer.backtest_portfolio_allocation(
            mpt_allocation,
            pd.DataFrame(),  # 空DataFrame作为占位符
            "2024-01-01",
            "2024-12-31",
        )
        logger.info(
            "回测结果: 年化收益=%.2f%%, 年化波动率=%.2f%%, 夏普比率=%.2f",
            backtest_result["annualized_return"] * 100,
            backtest_result["annualized_volatility"] * 100,
            backtest_result["sharpe_ratio"],
        )

        logger.info("🎉 策略投资组合优化器测试完成!")

        # 输出最终结果摘要
        final_metrics = optimizer.get_portfolio_metrics()
        print("\n" + "=" * 60)
        print("📊 最终投资组合摘要")
        print("=" * 60)
        print(f"策略数量: {final_metrics['strategy_count']}")
        print(f"预期年化收益: {final_metrics['portfolio_metrics']['expected_return']:.2%}")
        print(f"预期年化波动率: {final_metrics['portfolio_metrics']['expected_volatility']:.2%}")
        print(f"夏普比率: {final_metrics['portfolio_metrics']['sharpe_ratio']:.2f}")
        print(f"最大回撤: {final_metrics['portfolio_metrics']['max_drawdown']:.2%}")
        print(f"分散化比率: {final_metrics['portfolio_metrics']['diversification_ratio']:.2f}")
        print("\n策略权重分配:")
        for strategy, weight in final_metrics["allocation"].items():
            print("4.1f")
        print("=" * 60)

        return True

    except Exception as e:
        logger.error("❌ 策略投资组合优化器测试失败: %s", e)
        import traceback

        traceback.print_exc()
        return False


async def test_edge_cases():
    """测试边界情况"""
    logger.info("🔍 测试边界情况...")

    try:
        # 测试空优化器
        optimizer = StrategyPortfolioOptimizer()
        metrics = optimizer.get_portfolio_metrics()
        assert metrics["status"] == "no_allocation"
        logger.info("✅ 空优化器测试通过")

        # 测试单个策略
        strategy_info = StrategyInfo(
            name="Single_Strategy",
            expected_return=0.10,
            volatility=0.15,
            sharpe_ratio=1.0,
            max_drawdown=0.05,
            win_rate=0.60,
            avg_trade_pnl=0.002,
            total_trades=100,
            last_updated=datetime.now(),
        )
        optimizer.add_strategy(strategy_info)

        # 单个策略应该无法进行MPT优化
        try:
            optimizer.optimize_portfolio_mpt()
            logger.error("❌ 单个策略MPT优化应该失败")
            return False
        except ValueError as e:
            if "至少需要2个策略" in str(e):
                logger.info("✅ 单个策略MPT优化正确拒绝")
            else:
                raise

        # 测试风险平价优化 (单个策略)
        try:
            optimizer.optimize_portfolio_risk_parity()
            logger.error("❌ 单个策略风险平价优化应该失败")
            return False
        except ValueError as e:
            if "至少需要2个策略" in str(e):
                logger.info("✅ 单个策略风险平价优化正确拒绝")
            else:
                raise

        # 测试策略移除
        optimizer.remove_strategy("Single_Strategy")
        assert len(optimizer.strategies) == 0
        logger.info("✅ 策略移除测试通过")

        logger.info("🎉 边界情况测试完成!")
        return True

    except Exception as e:
        logger.error("❌ 边界情况测试失败: %s", e)
        return False


async def run_all_tests():
    """运行所有测试"""
    logger.info("🚀 运行策略投资组合优化器完整测试套件...")

    results = []

    # 测试1: 主要功能
    logger.info("\n" + "=" * 50)
    logger.info("TEST 1: 投资组合优化器主要功能")
    logger.info("=" * 50)
    result1 = await test_portfolio_optimizer()
    results.append(("Portfolio Optimizer Main Features", result1))

    # 测试2: 边界情况
    logger.info("\n" + "=" * 50)
    logger.info("TEST 2: 边界情况测试")
    logger.info("=" * 50)
    result2 = await test_edge_cases()
    results.append(("Edge Cases", result2))

    # 总结
    logger.info("\n" + "=" * 50)
    logger.info("📊 测试结果汇总")
    logger.info("=" * 50)

    passed = 0
    total = len(results)

    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        logger.info("%s: %s", test_name, status)
        if success:
            passed += 1

    logger.info("总体: %d/%d 测试通过", passed, total)

    if passed == total:
        logger.info("🎉 所有测试通过! 策略投资组合优化器已准备就绪。")
        return True
    logger.warning("⚠️ 某些测试失败。请检查实现。")
    return False


if __name__ == "__main__":
    # 运行测试
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)
