#!/usr/bin/env python3
"""ML策略验证框架测试脚本

测试策略验证和对比功能：
- 单策略验证
- 多策略对比
- 统计显著性检验
- 风险调整分析
- 验证报告生成

作者: MyStocks量化交易团队
创建时间: 2026-01-12
"""

import asyncio
import logging
import sys
from datetime import datetime, timedelta

import numpy as np
import pandas as pd


# 添加项目根目录到路径
project_root = "/opt/claude/mystocks_spec"
sys.path.insert(0, project_root)

# 配置日志
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


async def generate_test_market_data(days: int = 400) -> pd.DataFrame:
    """生成测试市场数据"""
    np.random.seed(42)

    # 生成日期序列
    start_date = datetime(2021, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(days)]

    # 生成复杂的多趋势市场数据
    base_price = 100.0
    prices = [base_price]

    for i in range(1, days):
        # 多周期趋势
        long_trend = 0.0002 * np.sin(2 * np.pi * i / 365)  # 年周期
        medium_trend = 0.0008 * np.sin(2 * np.pi * i / 30)  # 月周期
        short_noise = np.random.normal(0, 0.015)  # 日噪声

        # 市场结构变化
        if i < days * 0.25:
            structural = 0.001  # 牛市前期
        elif i < days * 0.5:
            structural = 0.0005  # 牛市中期
        elif i < days * 0.75:
            structural = -0.0003  # 熊市调整
        else:
            structural = -0.0008  # 熊市后期

        price_change = long_trend + medium_trend + short_noise + structural
        new_price = prices[-1] * (1 + price_change)
        prices.append(max(new_price, 20.0))  # 防止价格过低

    # 创建DataFrame
    df = pd.DataFrame(
        {
            "date": dates,
            "open": prices,
            "close": prices,
            "high": [p * (1 + abs(np.random.normal(0, 0.005))) for p in prices],
            "low": [p * (1 - abs(np.random.normal(0, 0.005))) for p in prices],
            "volume": [
                int(np.random.normal(2000000, 500000) * (1 + 0.3 * np.random.normal(0, 1))) for _ in range(days)
            ],
        },
    )

    df.set_index("date", inplace=True)
    return df


async def test_single_strategy_validation():
    """测试单策略验证"""
    logger.info("=" * 80)
    logger.info("单策略验证测试")
    logger.info("=" * 80)

    try:
        from src.ml_strategy.strategy.svm_trading_strategy import SVMTradingStrategy
        from src.ml_strategy.validation.ml_strategy_validator import MLStrategyValidator

        # 创建验证器
        validator = MLStrategyValidator()
        logger.info("✓ 创建ML策略验证器")

        # 创建策略
        strategy = SVMTradingStrategy()
        logger.info("✓ 创建SVM策略")

        # 生成测试数据
        market_data = await generate_test_market_data(300)
        logger.info(f"✓ 生成测试数据: {len(market_data)} 个交易日")

        # 验证策略
        validation_result = await validator.validate_strategy(
            strategy,
            market_data,
            validation_periods=3,
            train_test_split=0.7,
        )

        logger.info("✓ 策略验证完成")
        logger.info(f"  策略名称: {validation_result.strategy_name}")
        logger.info(".3f")
        logger.info(".3f")
        logger.info(".3f")
        logger.info(".3f")
        logger.info(".1%")
        logger.info(".3f")
        logger.info(".3f")
        logger.info(".1%")

        return True

    except Exception as e:
        logger.error(f"❌ 单策略验证测试失败: {e}")
        import traceback

        logger.error(traceback.format_exc())
        logger.info("=" * 80)
        return False


async def test_multi_strategy_comparison():
    """测试多策略对比"""
    logger.info("=" * 80)
    logger.info("多策略对比测试")
    logger.info("=" * 80)

    try:
        from src.ml_strategy.strategy.decision_tree_trading_strategy import DecisionTreeTradingStrategy
        from src.ml_strategy.strategy.naive_bayes_trading_strategy import NaiveBayesTradingStrategy
        from src.ml_strategy.strategy.svm_trading_strategy import SVMTradingStrategy
        from src.ml_strategy.validation.ml_strategy_validator import MLStrategyValidator

        # 创建验证器
        validator = MLStrategyValidator()
        logger.info("✓ 创建ML策略验证器")

        # 创建多个策略
        strategies = [
            SVMTradingStrategy(),
            DecisionTreeTradingStrategy(),
            NaiveBayesTradingStrategy(),
        ]
        logger.info(f"✓ 创建 {len(strategies)} 个策略")

        # 生成测试数据
        market_data = await generate_test_market_data(250)
        logger.info(f"✓ 生成测试数据: {len(market_data)} 个交易日")

        # 对比策略
        comparison_result = await validator.compare_strategies(strategies, market_data)

        logger.info("✓ 多策略对比完成")

        # 显示对比结果
        comparison_report = comparison_result.get("comparison_report", {})
        if comparison_report and "rankings" in comparison_report:
            rankings = comparison_report["rankings"]
            logger.info("\n策略排名:")
            for metric, ranking in rankings.items():
                metric_name = {
                    "total_return": "总收益率",
                    "sharpe_ratio": "夏普比率",
                    "win_rate": "胜率",
                    "stability_score": "稳定性",
                    "risk_adjusted_score": "风险调整分数",
                }.get(metric, metric)

                sorted_ranks = sorted(ranking.items(), key=lambda x: x[1])
                logger.info(f"  {metric_name}: {', '.join([f'{name}(第{rank}名)' for name, rank in sorted_ranks])}")

        # 显示最佳策略
        if "best_strategies" in comparison_report:
            best = comparison_report["best_strategies"]
            logger.info("\n最佳策略:")
            for metric, strategy in best.items():
                metric_name = {"total_return": "总收益率", "sharpe_ratio": "夏普比率", "win_rate": "胜率"}.get(
                    metric,
                    metric,
                )
                logger.info(f"  {metric_name}: {strategy}")

        # 显示统计检验
        statistical_tests = comparison_result.get("statistical_tests", {})
        if statistical_tests and "t_test_vs_benchmark" in statistical_tests:
            t_test = statistical_tests["t_test_vs_benchmark"]
            logger.info("\n统计检验:")
            logger.info(
                f"  t检验显著性: {'是' if t_test.get('significant', False) else '否'} (p={t_test.get('p_value', 'N/A'):.3f})",
            )

        return True

    except Exception as e:
        logger.error(f"❌ 多策略对比测试失败: {e}")
        import traceback

        logger.error(traceback.format_exc())
        logger.info("=" * 80)
        return False


async def test_validation_report_generation():
    """测试验证报告生成"""
    logger.info("=" * 80)
    logger.info("验证报告生成测试")
    logger.info("=" * 80)

    try:
        from src.ml_strategy.strategy.svm_trading_strategy import SVMTradingStrategy
        from src.ml_strategy.validation.ml_strategy_validator import MLStrategyValidator

        # 创建验证器和策略
        validator = MLStrategyValidator()
        strategies = [SVMTradingStrategy()]

        # 生成数据并运行验证
        market_data = await generate_test_market_data(200)
        comparison_result = await validator.compare_strategies(strategies, market_data)

        # 生成验证报告
        report = validator.generate_validation_report(comparison_result)

        logger.info("✓ 验证报告生成完成")
        logger.info("报告预览:")
        logger.info("-" * 40)
        # 只显示前几行
        report_lines = report.split("\n")[:10]
        for line in report_lines:
            logger.info(line)
        logger.info("...")

        return True

    except Exception as e:
        logger.error(f"❌ 验证报告生成测试失败: {e}")
        import traceback

        logger.error(traceback.format_exc())
        logger.info("=" * 80)
        return False


async def test_risk_adjusted_analysis():
    """测试风险调整分析"""
    logger.info("=" * 80)
    logger.info("风险调整分析测试")
    logger.info("=" * 80)

    try:
        from src.ml_strategy.validation.ml_strategy_validator import MLStrategyValidator, ValidationResult

        # 创建模拟验证结果
        mock_results = {
            "SVM_Strategy": ValidationResult(
                strategy_name="SVM_Strategy",
                total_return=0.15,
                annualized_return=0.18,
                volatility=0.25,
                sharpe_ratio=1.8,
                max_drawdown=-0.12,
                win_rate=0.62,
                profit_factor=1.8,
                calmar_ratio=1.5,
                sortino_ratio=2.1,
                alpha=0.08,
                beta=0.9,
                information_ratio=0.7,
                statistical_significance=0.95,
                stability_score=0.85,
                risk_adjusted_score=0.78,
            ),
            "DecisionTree_Strategy": ValidationResult(
                strategy_name="DecisionTree_Strategy",
                total_return=0.12,
                annualized_return=0.15,
                volatility=0.22,
                sharpe_ratio=1.6,
                max_drawdown=-0.15,
                win_rate=0.58,
                profit_factor=1.6,
                calmar_ratio=1.2,
                sortino_ratio=1.9,
                alpha=0.05,
                beta=1.1,
                information_ratio=0.5,
                statistical_significance=0.88,
                stability_score=0.82,
                risk_adjusted_score=0.72,
            ),
        }

        # 创建验证器并运行风险调整分析
        validator = MLStrategyValidator()
        risk_analysis = validator._analyze_risk_adjusted_performance(mock_results)

        logger.info("✓ 风险调整分析完成")

        if "best_strategies" in risk_analysis:
            best = risk_analysis["best_strategies"]
            logger.info("最佳风险调整策略:")
            logger.info(f"  夏普比率: {best['sharpe_ratio']}")
            logger.info(f"  索提诺比率: {best['sortino_ratio']}")
            logger.info(f"  卡尔玛比率: {best['calmar_ratio']}")

        if "risk_efficiency_analysis" in risk_analysis:
            efficiency = risk_analysis["risk_efficiency_analysis"]
            logger.info(f"  平均夏普比率: {efficiency['avg_sharpe']:.2f}")
            logger.info(f"  高效策略数量: {len(efficiency['efficient_strategies'])}")

        return True

    except Exception as e:
        logger.error(f"❌ 风险调整分析测试失败: {e}")
        import traceback

        logger.error(traceback.format_exc())
        logger.info("=" * 80)
        return False


async def main():
    """主函数"""
    logger.info("开始ML策略验证框架测试套件")

    # 测试各个功能模块
    single_test_passed = await test_single_strategy_validation()
    multi_test_passed = await test_multi_strategy_comparison()
    report_test_passed = await test_validation_report_generation()
    risk_test_passed = await test_risk_adjusted_analysis()

    # 总结测试结果
    logger.info("\n" + "=" * 80)
    logger.info("测试总结")
    logger.info("=" * 80)
    logger.info(f"单策略验证测试: {'✅ 通过' if single_test_passed else '❌ 失败'}")
    logger.info(f"多策略对比测试: {'✅ 通过' if multi_test_passed else '❌ 失败'}")
    logger.info(f"验证报告生成测试: {'✅ 通过' if report_test_passed else '❌ 失败'}")
    logger.info(f"风险调整分析测试: {'✅ 通过' if risk_test_passed else '❌ 失败'}")

    total_passed = sum([single_test_passed, multi_test_passed, report_test_passed, risk_test_passed])
    total_tests = 4

    logger.info(f"\n总体结果: {total_passed}/{total_tests} 个测试通过")

    if total_passed == total_tests:
        logger.info("\n🎉 所有ML策略验证框架测试通过!")
        exit(0)
    else:
        logger.info("\n❌ 部分测试失败，请检查上述错误信息")
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())
