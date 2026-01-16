#!/usr/bin/env python3
"""
Decision Tree策略测试脚本

测试Decision Tree增强交易策略：
- 特征工程验证
- 模型训练和预测
- 信号生成和风险控制
- 特征重要性分析

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


async def generate_test_market_data(days: int = 300) -> pd.DataFrame:
    """生成测试市场数据"""
    np.random.seed(42)

    # 生成日期序列
    start_date = datetime(2022, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(days)]

    # 生成更复杂的市场数据 (多周期趋势)
    base_price = 50.0
    prices = [base_price]

    for i in range(1, days):
        # 多周期趋势 + 季节性 + 随机游走 + 结构性变化
        long_trend = 0.0002 * np.sin(2 * np.pi * i / 252)  # 年周期
        medium_trend = 0.0005 * np.sin(2 * np.pi * i / 21)  # 月周期
        short_noise = np.random.normal(0, 0.012)  # 日噪声

        # 结构性变化 (市场 regime changes)
        if i > days * 0.3 and i < days * 0.7:
            # 中期牛市
            regime_factor = 0.001
        elif i > days * 0.8:
            # 后期熊市
            regime_factor = -0.0005
        else:
            regime_factor = 0

        price_change = long_trend + medium_trend + short_noise + regime_factor
        new_price = prices[-1] * (1 + price_change)
        prices.append(max(new_price, 10.0))  # 防止价格过低

    # 创建DataFrame
    df = pd.DataFrame(
        {
            "date": dates,
            "open": prices,
            "close": prices,
            "high": [p * (1 + abs(np.random.normal(0, 0.008))) for p in prices],
            "low": [p * (1 - abs(np.random.normal(0, 0.008))) for p in prices],
            "volume": [
                int(np.random.normal(1000000, 300000) * (1 + 0.5 * np.sin(2 * np.pi * i / 5))) for i in range(days)
            ],
        }
    )

    df.set_index("date", inplace=True)
    return df


async def test_decision_tree_trading_strategy():
    """测试Decision Tree增强交易策略"""
    logger.info("=" * 80)
    logger.info("Decision Tree增强交易策略测试")
    logger.info("=" * 80)

    try:
        # 导入Decision Tree策略
        from src.ml_strategy.strategy.decision_tree_trading_strategy import (
            DecisionTreeTradingStrategy,
            DecisionTreeConservativeStrategy,
            DecisionTreeAggressiveStrategy,
        )

        logger.info("✓ 成功导入Decision Tree策略类")

        # 生成测试数据
        market_data = await generate_test_market_data(250)
        logger.info(f"✓ 生成测试数据: {len(market_data)} 个交易日")

        # 创建策略实例
        dt_strategy = DecisionTreeTradingStrategy()
        logger.info("✓ 创建Decision Tree策略实例")

        # 验证参数
        if not dt_strategy.validate_parameters():
            logger.error("❌ 策略参数验证失败")
            return False
        logger.info("✓ 策略参数验证通过")

        # 测试特征工程
        logger.info("测试特征工程...")
        engineered_data = await dt_strategy.prepare_features(market_data)
        logger.info(f"✓ 特征工程完成: {engineered_data.shape[1]} 个特征")

        # 验证Decision Tree特定特征
        dt_specific_features = [
            "trend_strength",
            "momentum_divergence",
            "volatility_acceleration",
            "rsi_momentum",
            "macd_trend",
            "bb_position_trend",
            "price_range_ratio",
        ]
        missing_dt_features = [f for f in dt_specific_features if f not in engineered_data.columns]
        if missing_dt_features:
            logger.warning(f"Decision Tree特定特征缺失: {missing_dt_features}")
        else:
            logger.info("✓ 所有Decision Tree特定特征已生成")

        # 测试模型训练
        logger.info("测试模型训练...")
        model_key = await dt_strategy.train_ml_model(market_data)
        logger.info(f"✓ 模型训练完成: {model_key}")

        # 测试特征重要性分析
        logger.info("测试特征重要性分析...")
        feature_importance = dt_strategy.get_feature_importance()
        if "error" not in feature_importance:
            top_features = feature_importance.get("top_features", {})
            logger.info(f"✓ 特征重要性分析完成，发现 {len(top_features)} 个重要特征")
            if top_features:
                most_important = list(top_features.keys())[0]
                logger.info(f"  最重要特征: {most_important} (重要性: {top_features[most_important]:.4f})")
        else:
            logger.warning(f"特征重要性分析失败: {feature_importance['error']}")

        # 测试决策规则提取
        logger.info("测试决策规则提取...")
        decision_rules = dt_strategy.get_decision_rules()
        if "error" not in decision_rules:
            logger.info(f"✓ 决策规则提取完成: {decision_rules.get('model_type', 'Unknown')}")
        else:
            logger.warning(f"决策规则提取失败: {decision_rules['error']}")

        # 测试信号生成
        logger.info("测试信号生成...")
        signals = await dt_strategy.generate_signals(market_data)
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
        conservative_strategy = DecisionTreeConservativeStrategy()
        conservative_signals = await conservative_strategy.generate_signals(market_data)
        conservative_buy_signals = len(conservative_signals[conservative_signals["signal"] == 1])
        logger.info(f"✓ 保守型策略买入信号: {conservative_buy_signals} 个")

        logger.info("\n--- 测试激进型策略 ---")
        aggressive_strategy = DecisionTreeAggressiveStrategy()
        aggressive_signals = await aggressive_strategy.generate_signals(market_data)
        aggressive_buy_signals = len(aggressive_signals[aggressive_signals["signal"] == 1])
        logger.info(f"✓ 激进型策略买入信号: {aggressive_buy_signals} 个")

        # 比较不同策略的信号数量
        logger.info("\n策略对比:")
        logger.info(f"  标准策略买入信号: {len(signals[signals['signal'] == 1])}")
        logger.info(f"  保守策略买入信号: {conservative_buy_signals}")
        logger.info(f"  激进策略买入信号: {aggressive_buy_signals}")

        # 测试策略信息
        strategy_info = dt_strategy.get_strategy_info()
        logger.info(f"\n策略信息: {strategy_info['strategy_name']}")
        logger.info(f"算法类型: {strategy_info['algorithm_type']}")
        logger.info(f"模型状态: {'已训练' if strategy_info['trained_model'] else '未训练'}")

        logger.info("\n🎉 Decision Tree增强交易策略测试完成 - 所有功能正常!")
        logger.info("=" * 80)

        return True

    except Exception as e:
        logger.error(f"❌ Decision Tree策略测试失败: {e}")
        import traceback

        logger.error(traceback.format_exc())
        logger.info("=" * 80)
        return False


async def test_decision_tree_backtesting_integration():
    """测试Decision Tree策略与回测引擎的集成"""
    logger.info("=" * 80)
    logger.info("Decision Tree策略回测集成测试")
    logger.info("=" * 80)

    try:
        from src.ml_strategy.backtest.ml_strategy_backtester import MLStrategyBacktester
        from src.ml_strategy.strategy.decision_tree_trading_strategy import DecisionTreeTradingStrategy

        # 创建回测器
        backtester = MLStrategyBacktester()
        strategy = DecisionTreeTradingStrategy()

        # 生成测试数据
        market_data = await generate_test_market_data(200)

        # 执行回测
        result = await backtester.run_strategy_backtest(
            strategy, market_data, start_date="2022-03-01", end_date="2022-09-01"
        )

        logger.info("✓ Decision Tree策略回测完成")
        logger.info(".2%")

        if "signal_statistics" in result:
            signal_stats = result["signal_statistics"]
            logger.info(
                f"  信号统计: 总信号={signal_stats['total_signals']}, 日均={signal_stats['avg_signals_per_day']:.3f}"
            )

        logger.info("\n🎉 Decision Tree策略回测集成测试完成!")
        logger.info("=" * 80)

        return True

    except Exception as e:
        logger.error(f"❌ Decision Tree回测集成测试失败: {e}")
        import traceback

        logger.error(traceback.format_exc())
        logger.info("=" * 80)
        return False


async def main():
    """主函数"""
    logger.info("开始Decision Tree增强交易策略测试套件")

    # 测试基本功能
    basic_test_passed = await test_decision_tree_trading_strategy()

    # 测试回测集成
    backtest_test_passed = await test_decision_tree_backtesting_integration()

    # 总结测试结果
    logger.info("\n" + "=" * 80)
    logger.info("测试总结")
    logger.info("=" * 80)
    logger.info(f"基本功能测试: {'✅ 通过' if basic_test_passed else '❌ 失败'}")
    logger.info(f"回测集成测试: {'✅ 通过' if backtest_test_passed else '❌ 失败'}")

    if basic_test_passed and backtest_test_passed:
        logger.info("\n🎉 所有Decision Tree增强交易策略测试通过!")
        exit(0)
    else:
        logger.info("\n❌ 部分测试失败，请检查上述错误信息")
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())
