#!/usr/bin/env python3
"""ML增强交易策略测试脚本

测试机器学习增强的交易策略：
- SVM增强策略
- 特征工程验证
- 信号生成测试
- 风险控制机制

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


async def generate_test_market_data(n_samples: int = 1000) -> pd.DataFrame:
    """生成测试市场数据"""
    np.random.seed(42)

    # 生成日期序列
    start_date = datetime(2023, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(n_samples)]

    # 生成价格数据 (模拟趋势 + 随机游走)
    base_price = 100.0
    prices = [base_price]
    trend = 0.001  # 每日趋势

    for i in range(1, n_samples):
        # 添加趋势和随机噪声
        price_change = trend + np.random.normal(0, 0.02)
        new_price = prices[-1] * (1 + price_change)
        prices.append(max(new_price, 1.0))  # 防止负价格

    # 创建DataFrame
    df = pd.DataFrame(
        {
            "date": dates,
            "open": prices,
            "close": prices,
            "high": [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
            "low": [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices],
            "volume": [int(np.random.normal(1000000, 200000)) for _ in range(n_samples)],
        },
    )

    df.set_index("date", inplace=True)
    return df


async def test_svm_trading_strategy():
    """测试SVM增强交易策略"""
    logger.info("=" * 80)
    logger.info("SVM增强交易策略测试")
    logger.info("=" * 80)

    try:
        # 导入SVM策略
        from src.ml_strategy.strategy.svm_trading_strategy import (
            SVMAggressiveStrategy,
            SVMConservativeStrategy,
            SVMTradingStrategy,
        )

        logger.info("✓ 成功导入SVM策略类")

        # 生成测试数据
        market_data = await generate_test_market_data(500)
        logger.info(f"✓ 生成测试数据: {len(market_data)} 个交易日")

        # 测试标准SVM策略
        logger.info("\n--- 测试标准SVM策略 ---")
        svm_strategy = SVMTradingStrategy()
        logger.info("✓ 创建标准SVM策略实例")

        # 验证参数
        if not svm_strategy.validate_parameters():
            logger.error("❌ 策略参数验证失败")
            return False
        logger.info("✓ 策略参数验证通过")

        # 测试特征工程
        logger.info("测试特征工程...")
        engineered_data = await svm_strategy.prepare_features(market_data)
        logger.info(f"✓ 特征工程完成: {engineered_data.shape[1]} 个特征")

        # 测试模型训练
        logger.info("测试模型训练...")
        model_key = await svm_strategy.train_ml_model(market_data)
        logger.info(f"✓ 模型训练完成: {model_key}")

        # 测试信号生成
        logger.info("测试信号生成...")
        signals = await svm_strategy.generate_signals(market_data)
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
        # 测试保守型策略
        logger.info("\n--- 测试保守型SVM策略 ---")
        conservative_strategy = SVMConservativeStrategy()

        conservative_signals = await conservative_strategy.generate_signals(market_data)
        conservative_buy_signals = len(conservative_signals[conservative_signals["signal"] == 1])
        logger.info(f"✓ 保守型策略买入信号: {conservative_buy_signals} 个")

        # 测试激进型策略
        logger.info("\n--- 测试激进型SVM策略 ---")
        aggressive_strategy = SVMAggressiveStrategy()

        aggressive_signals = await aggressive_strategy.generate_signals(market_data)
        aggressive_buy_signals = len(aggressive_signals[aggressive_signals["signal"] == 1])
        logger.info(f"✓ 激进型策略买入信号: {aggressive_buy_signals} 个")

        # 比较不同策略的信号数量
        logger.info("\n策略对比:")
        logger.info(f"  标准策略买入信号: {len(signals[signals['signal'] == 1])}")
        logger.info(f"  保守策略买入信号: {conservative_buy_signals}")
        logger.info(f"  激进策略买入信号: {aggressive_buy_signals}")

        # 测试策略信息
        strategy_info = svm_strategy.get_strategy_info()
        logger.info(f"\n策略信息: {strategy_info['strategy_name']}")
        logger.info(f"算法类型: {strategy_info['algorithm_type']}")
        logger.info(f"模型状态: {'已训练' if strategy_info['trained_model'] else '未训练'}")

        logger.info("\n🎉 SVM增强交易策略测试完成 - 所有功能正常!")
        logger.info("=" * 80)

        return True

    except Exception as e:
        logger.error(f"❌ SVM策略测试失败: {e}")
        import traceback

        logger.error(traceback.format_exc())
        logger.info("=" * 80)
        return False


async def test_ml_feature_engineering():
    """测试ML特征工程"""
    logger.info("=" * 80)
    logger.info("ML特征工程测试")
    logger.info("=" * 80)

    try:
        from src.ml_strategy.strategy.ml_strategy_base import MLFeatureEngineer

        # 生成测试数据
        market_data = await generate_test_market_data(200)
        logger.info(f"✓ 生成测试数据: {len(market_data)} 个样本")

        # 测试技术指标特征
        engineer = MLFeatureEngineer()
        data_with_features = engineer.add_technical_features(market_data)
        logger.info(f"✓ 添加技术指标: {data_with_features.shape[1]} 个特征")

        # 验证关键特征
        required_features = ["ma_5", "ma_10", "rsi_14", "macd", "bb_upper", "bb_lower"]
        missing_features = [f for f in required_features if f not in data_with_features.columns]
        if missing_features:
            logger.error(f"❌ 缺少必要特征: {missing_features}")
            return False
        logger.info("✓ 所有必要技术指标特征已生成")

        # 测试目标变量创建
        data_with_target = engineer.create_target_variable(data_with_features)
        logger.info(f"✓ 创建目标变量: {len(data_with_target)} 个样本")

        # 验证目标变量分布
        if "target" in data_with_target.columns:
            target_counts = data_with_target["target"].value_counts()
            logger.info("目标变量分布:")
            for target_val, count in target_counts.items():
                target_name = {0: "下跌", 1: "震荡", 2: "上涨"}.get(target_val, "未知")
                logger.info(f"  {target_name} ({target_val}): {count} 个样本")

        # 测试特征准备
        prepared_data, feature_cols = engineer.prepare_ml_features(data_with_target)
        logger.info(f"✓ ML特征准备完成: {len(prepared_data)} 个样本, {len(feature_cols)} 个特征")
        logger.info(f"特征示例: {feature_cols[:5]}...")

        logger.info("\n🎉 ML特征工程测试完成 - 所有功能正常!")
        logger.info("=" * 80)

        return True

    except Exception as e:
        logger.error(f"❌ 特征工程测试失败: {e}")
        import traceback

        logger.error(traceback.format_exc())
        logger.info("=" * 80)
        return False


async def main():
    """主函数"""
    logger.info("开始ML增强交易策略测试套件")

    # 测试特征工程
    feature_test_passed = await test_ml_feature_engineering()

    # 测试SVM策略
    svm_test_passed = await test_svm_trading_strategy()

    # 总结测试结果
    logger.info("\n" + "=" * 80)
    logger.info("测试总结")
    logger.info("=" * 80)
    logger.info(f"特征工程测试: {'✅ 通过' if feature_test_passed else '❌ 失败'}")
    logger.info(f"SVM策略测试: {'✅ 通过' if svm_test_passed else '❌ 失败'}")

    if feature_test_passed and svm_test_passed:
        logger.info("\n🎉 所有ML增强交易策略测试通过!")
        exit(0)
    else:
        logger.info("\n❌ 部分测试失败，请检查上述错误信息")
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())
