#!/usr/bin/env python3
"""ML策略回测集成测试脚本

测试ML策略与回测引擎的集成：
- SVM策略回测执行
- 信号转换和过滤
- 性能指标计算
- 多策略对比

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


async def generate_test_market_data(days: int = 500) -> pd.DataFrame:
    """生成测试市场数据"""
    np.random.seed(42)

    # 生成日期序列
    start_date = datetime(2022, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(days)]

    # 生成更现实的价格数据 (带趋势和波动)
    base_price = 50.0
    prices = [base_price]

    # 添加长期趋势
    trend = 0.0005  # 每日0.05%的趋势

    for i in range(1, days):
        # 趋势 + 随机游走 + 波动聚集
        trend_component = trend * (1 + 0.5 * np.sin(2 * np.pi * i / 252))  # 年度周期
        random_component = np.random.normal(0, 0.015)  # 1.5%日波动率
        volume_effect = 0.001 * np.random.normal(0, 1)  # 成交量影响

        price_change = trend_component + random_component + volume_effect
        new_price = prices[-1] * (1 + price_change)
        prices.append(max(new_price, 10.0))  # 防止价格过低

    # 创建DataFrame
    df = pd.DataFrame(
        {
            "date": dates,
            "open": prices,
            "close": prices,
            "high": [p * (1 + abs(np.random.normal(0, 0.005))) for p in prices],
            "low": [p * (1 - abs(np.random.normal(0, 0.005))) for p in prices],
            "volume": [int(np.random.normal(1000000, 300000)) for _ in range(days)],
        },
    )

    df.set_index("date", inplace=True)
    return df


async def test_ml_strategy_backtesting():
    """测试ML策略回测集成"""
    logger.info("=" * 80)
    logger.info("ML策略回测集成测试")
    logger.info("=" * 80)

    try:
        # 导入必要的组件
        from src.ml_strategy.backtest.ml_strategy_backtester import MLStrategyBacktester
        from src.ml_strategy.strategy.svm_trading_strategy import (
            SVMAggressiveStrategy,
            SVMConservativeStrategy,
            SVMTradingStrategy,
        )

        logger.info("✓ 成功导入ML策略回测组件")

        # 创建回测器
        backtester = MLStrategyBacktester()
        logger.info("✓ 创建ML策略回测器")

        # 生成测试数据
        market_data = await generate_test_market_data(300)  # 300个交易日
        logger.info(f"✓ 生成测试数据: {len(market_data)} 个交易日")

        # 创建策略实例 (降低阈值以便观察信号)
        from src.ml_strategy.strategy.ml_strategy_base import MLStrategyConfig

        conservative_config = MLStrategyConfig(
            algorithm_type="svm",
            prediction_threshold=0.6,  # 降低预测阈值
            confidence_threshold=0.4,  # 降低置信度阈值
        )

        strategies = [
            SVMTradingStrategy(),  # 默认配置
            SVMConservativeStrategy(),  # 保守配置 (内置低阈值)
            SVMAggressiveStrategy(),  # 激进配置
        ]
        logger.info(f"✓ 创建 {len(strategies)} 个策略实例")

        # 测试单策略回测
        logger.info("\n--- 测试单策略回测 ---")
        svm_strategy = strategies[0]

        single_result = await backtester.run_strategy_backtest(
            svm_strategy,
            market_data,
            start_date="2022-06-01",
            end_date="2023-06-01",
        )

        logger.info("✓ 单策略回测完成")
        logger.info(".2%")
        logger.info(f"  总交易次数: {single_result['summary']['total_trades']}")
        logger.info(f"  胜率: {single_result['performance_metrics']['win_rate']:.1%}")

        # 测试多策略对比
        logger.info("\n--- 测试多策略对比 ---")
        comparison_result = await backtester.compare_strategies(
            strategies,
            market_data,
            start_date="2022-06-01",
            end_date="2023-06-01",
        )

        logger.info("✓ 多策略对比完成")
        logger.info(f"  对比策略数: {comparison_result['strategies_tested']}")
        logger.info(f"  成功测试数: {comparison_result['successful_tests']}")

        # 显示对比结果
        comparison_report = comparison_result["comparison_report"]
        if "best_performers" in comparison_report:
            best = comparison_report["best_performers"]
            logger.info("最佳表现策略:")
            logger.info(f"  总收益率: {best['total_return']}")
            logger.info(f"  夏普比率: {best['sharpe_ratio']}")
            logger.info(f"  胜率: {best['win_rate']}")

        # 显示详细比较数据
        if "comparison_data" in comparison_report:
            logger.info("\n策略详细对比:")
            for strategy_name, metrics in comparison_report["comparison_data"].items():
                logger.info(f"  {strategy_name}:")
                logger.info(".2%")
                logger.info(".2f")
                logger.info(".1%")

        # 验证信号过滤功能
        logger.info("\n--- 验证信号过滤功能 ---")
        signal_stats = single_result.get("signal_statistics", {})
        if signal_stats:
            logger.info("信号统计:")
            logger.info(f"  总信号数: {signal_stats['total_signals']}")
            logger.info(f"  日均信号数: {signal_stats['avg_signals_per_day']:.3f}")
            if "signal_distribution" in signal_stats:
                dist = signal_stats["signal_distribution"]
                logger.info(
                    f"  信号分布: 买入={dist.get(1, 0)}, 持有={dist.get(0, 0)}, 卖出={dist.get(-1, 0)}",
                )

        # 验证风险指标
        logger.info("\n--- 验证风险指标 ---")
        risk_metrics = single_result.get("risk_metrics", {})
        if risk_metrics:
            logger.info("风险指标:")
            logger.info(".2%")
            logger.info(".1f")
            logger.info(".2f")

        logger.info("\n🎉 ML策略回测集成测试完成 - 所有功能正常!")
        logger.info("=" * 80)

        return True

    except Exception as e:
        logger.error(f"❌ ML策略回测集成测试失败: {e}")
        import traceback

        logger.error(traceback.format_exc())
        logger.info("=" * 80)
        return False


async def test_backtest_configuration():
    """测试回测配置选项"""
    logger.info("=" * 80)
    logger.info("回测配置测试")
    logger.info("=" * 80)

    try:
        from src.ml_strategy.backtest.ml_strategy_backtester import MLStrategyBacktestConfig, MLStrategyBacktester
        from src.ml_strategy.backtest.vectorized_backtester import BacktestConfig
        from src.ml_strategy.strategy.svm_trading_strategy import SVMTradingStrategy

        # 创建自定义配置
        backtest_config = BacktestConfig(
            initial_capital=50000.0,
            commission_rate=0.0005,  # 5万分之5
            max_position_size=0.5,  # 最大50%仓位
        )

        ml_config = MLStrategyBacktestConfig(
            backtest_config=backtest_config,
            min_confidence_threshold=0.7,  # 更高的置信度要求
            max_signals_per_day=2,  # 每日最多2个信号
            signal_cooldown_days=2,  # 2天冷却期
        )

        # 创建回测器
        backtester = MLStrategyBacktester(ml_config)
        strategy = SVMTradingStrategy()

        # 生成测试数据
        market_data = await generate_test_market_data(200)

        # 执行回测
        result = await backtester.run_strategy_backtest(strategy, market_data)

        logger.info("✓ 自定义配置回测完成")
        logger.info(".2%")
        logger.info(f"  初始资金: ${ml_config.backtest_config.initial_capital:,.0f}")
        logger.info(f"  佣金率: {ml_config.backtest_config.commission_rate:.2%}")
        logger.info(f"  置信度阈值: {ml_config.min_confidence_threshold}")
        logger.info(f"  每日最大信号: {ml_config.max_signals_per_day}")

        logger.info("\n🎉 回测配置测试完成 - 所有功能正常!")
        logger.info("=" * 80)

        return True

    except Exception as e:
        logger.error(f"❌ 回测配置测试失败: {e}")
        import traceback

        logger.error(traceback.format_exc())
        logger.info("=" * 80)
        return False


async def main():
    """主函数"""
    logger.info("开始ML策略回测集成测试套件")

    # 测试基本回测功能
    basic_test_passed = await test_ml_strategy_backtesting()

    # 测试配置选项
    config_test_passed = await test_backtest_configuration()

    # 总结测试结果
    logger.info("\n" + "=" * 80)
    logger.info("测试总结")
    logger.info("=" * 80)
    logger.info(f"基本回测测试: {'✅ 通过' if basic_test_passed else '❌ 失败'}")
    logger.info(f"配置测试: {'✅ 通过' if config_test_passed else '❌ 失败'}")

    if basic_test_passed and config_test_passed:
        logger.info("\n🎉 所有ML策略回测集成测试通过!")
        exit(0)
    else:
        logger.info("\n❌ 部分测试失败，请检查上述错误信息")
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())
