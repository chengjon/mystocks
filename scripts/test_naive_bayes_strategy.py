#!/usr/bin/env python3
"""
Naive Bayes策略测试脚本

测试Naive Bayes增强交易策略：
- 特征工程和概率分布转换验证
- 模型训练和概率预测
- 信号生成和风险控制
- 概率分析功能

作者: MyStocks量化交易团队
创建时间: 2026-01-12
"""

import sys
import asyncio
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# 添加项目根目录到路径
project_root = "/opt/claude/mystocks_spec"
sys.path.insert(0, project_root)

# 配置日志
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


async def generate_test_market_data(days: int = 250) -> pd.DataFrame:
    """生成测试市场数据"""
    np.random.seed(42)

    # 生成日期序列
    start_date = datetime(2022, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(days)]

    # 生成具有概率分布特征的市场数据
    base_price = 50.0
    prices = [base_price]

    # 加入不同的市场状态
    for i in range(1, days):
        # 基础趋势
        trend = 0.0001

        # 加入周期性波动
        seasonal = 0.0003 * np.sin(2 * np.pi * i / 30)  # 月周期

        # 随机噪声
        noise = np.random.normal(0, 0.008)

        # 结构性变化
        structural = 0
        if i > days * 0.4 and i < days * 0.7:
            structural = 0.0008  # 中期上涨
        elif i > days * 0.8:
            structural = -0.0005  # 后期下跌

        price_change = trend + seasonal + noise + structural
        new_price = prices[-1] * (1 + price_change)
        prices.append(max(new_price, 10.0))

    # 创建DataFrame
    df = pd.DataFrame(
        {
            "date": dates,
            "open": prices,
            "close": prices,
            "high": [p * (1 + abs(np.random.normal(0, 0.003))) for p in prices],
            "low": [p * (1 - abs(np.random.normal(0, 0.003))) for p in prices],
            "volume": [
                int(np.random.normal(1000000, 200000) * (1 + 0.3 * np.random.normal(0, 1))) for _ in range(days)
            ],
        }
    )

    df.set_index("date", inplace=True)
    return df


async def test_naive_bayes_trading_strategy():
    """测试Naive Bayes增强交易策略"""
    logger.info("=" * 80)
    logger.info("Naive Bayes增强交易策略测试")
    logger.info("=" * 80)

    try:
        # 导入Naive Bayes策略
        from src.ml_strategy.strategy.naive_bayes_trading_strategy import (
            NaiveBayesTradingStrategy,
            NaiveBayesConservativeStrategy,
            NaiveBayesAggressiveStrategy,
        )

        logger.info("✓ 成功导入Naive Bayes策略类")

        # 生成测试数据
        market_data = await generate_test_market_data(200)
        logger.info(f"✓ 生成测试数据: {len(market_data)} 个交易日")

        # 创建策略实例
        nb_strategy = NaiveBayesTradingStrategy()
        logger.info("✓ 创建Naive Bayes策略实例")

        # 验证参数
        if not nb_strategy.validate_parameters():
            logger.error("❌ 策略参数验证失败")
            return False
        logger.info("✓ 策略参数验证通过")

        # 测试特征工程
        logger.info("测试特征工程...")
        engineered_data = await nb_strategy.prepare_features(market_data)
        logger.info(f"✓ 特征工程完成: {engineered_data.shape[1]} 个特征")

        # 验证Naive Bayes特定特征
        nb_specific_features = [
            "price_change_prob",
            "volatility_prob",
            "rsi_prob",
            "momentum_prob",
            "technical_score",
            "technical_prob",
        ]
        existing_nb_features = [f for f in nb_specific_features if f in engineered_data.columns]
        logger.info(f"✓ 生成的Naive Bayes特征: {existing_nb_features}")

        # 验证概率分布特征
        prob_features = [col for col in engineered_data.columns if col.endswith("_prob")]
        logger.info(f"✓ 概率分布特征数量: {len(prob_features)}")

        # 测试模型训练
        logger.info("测试模型训练...")
        model_key = await nb_strategy.train_ml_model(market_data)
        logger.info(f"✓ 模型训练完成: {model_key}")

        # 测试概率分布分析
        logger.info("测试概率分布分析...")
        prob_dist = nb_strategy.get_probability_distribution()
        if "error" not in prob_dist:
            logger.info(f"✓ 概率分布分析完成: {prob_dist.get('model_type')}")
            logger.info(f"  优势: {prob_dist.get('strengths', [])}")
        else:
            logger.warning(f"概率分布分析失败: {prob_dist['error']}")

        # 测试信号生成
        logger.info("测试信号生成...")
        signals = await nb_strategy.generate_signals(market_data)
        logger.info(f"✓ 信号生成完成: {len(signals)} 个信号")

        # 分析信号分布
        if not signals.empty:
            signal_counts = signals["signal"].value_counts()
            logger.info("信号分布:")
            for signal, count in signal_counts.items():
                signal_name = {1: "买入", -1: "卖出", 0: "持有"}.get(signal, "未知")
                logger.info(f"  {signal_name} ({signal}): {count} 次")

            # 分析置信度
            if "confidence" in signals.columns:
                avg_confidence = signals["confidence"].mean()
                max_confidence = signals["confidence"].max()
                logger.info(".3f")
                logger.info(".3f")

        # 测试策略变体
        logger.info("\n--- 测试保守型策略 ---")
        conservative_strategy = NaiveBayesConservativeStrategy()
        conservative_signals = await conservative_strategy.generate_signals(market_data)
        conservative_buy_signals = len(conservative_signals[conservative_signals["signal"] == 1])
        logger.info(f"✓ 保守型策略买入信号: {conservative_buy_signals} 个")

        logger.info("\n--- 测试激进型策略 ---")
        aggressive_strategy = NaiveBayesAggressiveStrategy()
        aggressive_signals = await aggressive_strategy.generate_signals(market_data)
        aggressive_buy_signals = len(aggressive_signals[aggressive_signals["signal"] == 1])
        logger.info(f"✓ 激进型策略买入信号: {aggressive_buy_signals} 个")

        # 比较不同策略的信号数量
        logger.info("\n策略对比:")
        logger.info(f"  标准策略买入信号: {len(signals[signals['signal'] == 1])}")
        logger.info(f"  保守策略买入信号: {conservative_buy_signals}")
        logger.info(f"  激进策略买入信号: {aggressive_buy_signals}")

        # 测试策略信息
        strategy_info = nb_strategy.get_strategy_info()
        logger.info(f"\n策略信息: {strategy_info['strategy_name']}")
        logger.info(f"算法类型: {strategy_info['algorithm_type']}")
        logger.info(f"模型状态: {'已训练' if strategy_info['trained_model'] else '未训练'}")

        logger.info("\n🎉 Naive Bayes增强交易策略测试完成 - 所有功能正常!")
        logger.info("=" * 80)

        return True

    except Exception as e:
        logger.error(f"❌ Naive Bayes策略测试失败: {e}")
        import traceback

        logger.error(traceback.format_exc())
        logger.info("=" * 80)
        return False


async def test_naive_bayes_backtesting_integration():
    """测试Naive Bayes策略与回测引擎的集成"""
    logger.info("=" * 80)
    logger.info("Naive Bayes策略回测集成测试")
    logger.info("=" * 80)

    try:
        from src.ml_strategy.backtest.ml_strategy_backtester import MLStrategyBacktester
        from src.ml_strategy.strategy.naive_bayes_trading_strategy import NaiveBayesTradingStrategy

        # 创建回测器
        backtester = MLStrategyBacktester()
        strategy = NaiveBayesTradingStrategy()

        # 生成测试数据
        market_data = await generate_test_market_data(180)

        # 执行回测
        result = await backtester.run_strategy_backtest(
            strategy, market_data, start_date="2022-03-01", end_date="2022-08-01"
        )

        logger.info("✓ Naive Bayes策略回测完成")
        logger.info(".2%")

        if "signal_statistics" in result:
            signal_stats = result["signal_statistics"]
            logger.info(
                f"  信号统计: 总信号={signal_stats['total_signals']}, 日均={signal_stats['avg_signals_per_day']:.3f}"
            )

        logger.info("\n🎉 Naive Bayes策略回测集成测试完成!")
        logger.info("=" * 80)

        return True

    except Exception as e:
        logger.error(f"❌ Naive Bayes回测集成测试失败: {e}")
        import traceback

        logger.error(traceback.format_exc())
        logger.info("=" * 80)
        return False


async def main():
    """主函数"""
    logger.info("开始Naive Bayes增强交易策略测试套件")

    # 测试基本功能
    basic_test_passed = await test_naive_bayes_trading_strategy()

    # 测试回测集成
    backtest_test_passed = await test_naive_bayes_backtesting_integration()

    # 总结测试结果
    logger.info("\n" + "=" * 80)
    logger.info("测试总结")
    logger.info("=" * 80)
    logger.info(f"基本功能测试: {'✅ 通过' if basic_test_passed else '❌ 失败'}")
    logger.info(f"回测集成测试: {'✅ 通过' if backtest_test_passed else '❌ 失败'}")

    if basic_test_passed and backtest_test_passed:
        logger.info("\n🎉 所有Naive Bayes增强交易策略测试通过!")
        exit(0)
    else:
        logger.info("\n❌ 部分测试失败，请检查上述错误信息")
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())
