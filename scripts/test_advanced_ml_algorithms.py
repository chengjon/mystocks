"""测试高级ML算法 - LSTM和Transformer
Test Advanced ML Algorithms - LSTM and Transformer

验证LSTM和Transformer交易策略的实现和功能。
Validates the implementation and functionality of LSTM and Transformer trading strategies.
"""

import asyncio
import logging
import os
import sys

import numpy as np
import pandas as pd


# Setup project path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.ml_strategy.strategy.lstm_trading_strategy import LSTMTradingStrategy
from src.ml_strategy.strategy.transformer_trading_strategy import TransformerTradingStrategy


# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_mock_market_data(num_points: int = 1000) -> pd.DataFrame:
    """创建模拟市场数据用于测试"""
    np.random.seed(42)

    # 生成基础价格序列
    base_price = 100.0
    returns = np.random.normal(0.0001, 0.02, num_points)  # 轻微上涨趋势 + 波动
    prices = base_price * np.cumprod(1 + returns)

    # 生成成交量
    volumes = np.random.lognormal(10, 0.5, num_points)

    # 创建时间戳
    dates = pd.date_range(start="2024-01-01", periods=num_points, freq="1H")

    # 创建DataFrame
    data = pd.DataFrame(
        {
            "timestamp": dates,
            "open": prices * (1 + np.random.normal(0, 0.005, num_points)),
            "high": prices * (1 + np.random.normal(0.005, 0.01, num_points)),
            "low": prices * (1 + np.random.normal(-0.01, 0.005, num_points)),
            "close": prices,
            "volume": volumes,
        },
    )

    # 确保high >= max(open, close), low <= min(open, close)
    data["high"] = data[["open", "close", "high"]].max(axis=1)
    data["low"] = data[["open", "close", "low"]].min(axis=1)

    # 设置索引
    data.set_index("timestamp", inplace=True)

    return data


async def test_lstm_strategy():
    """测试LSTM策略"""
    logger.info("🧪 测试LSTM交易策略...")

    try:
        # 创建策略
        strategy = LSTMTradingStrategy(
            strategy_name="Test_LSTM",
            sequence_length=30,  # 较短的序列用于测试
            epochs=5,  # 较少的训练轮数
            batch_size=16,
        )

        # 创建模拟数据
        market_data = create_mock_market_data(200)  # 较少的数据点用于快速测试

        logger.info("创建了模拟市场数据: %d 条记录", len(market_data))

        # 准备特征
        features = await strategy.prepare_features(market_data)
        logger.info("特征准备完成: %d 个特征列", len(features.columns))

        # 训练模型 (简化测试，只训练1轮)
        logger.info("开始训练LSTM模型...")
        # 临时减少epochs进行快速测试
        original_epochs = strategy.epochs
        strategy.epochs = 1
        try:
            model_key = await strategy.train_ml_model(market_data)
            logger.info("模型训练完成: %s", model_key)
        finally:
            strategy.epochs = original_epochs

        # 生成预测
        logger.info("生成预测...")
        predictions = await strategy.get_ml_prediction(market_data)
        logger.info("生成 %d 个预测", len(predictions))

        # 解释信号
        signals_df = await strategy.interpret_ml_signals(predictions, market_data)
        logger.info("生成 %d 个交易信号", len(signals_df))

        # 获取策略信息
        info = strategy.get_strategy_info()
        logger.info("策略信息: %s", {k: v for k, v in info.items() if not k.startswith("_")})

        # 验证结果
        assert model_key != "training_failed", "LSTM模型训练失败"
        assert len(predictions) > 0, "未生成预测"
        assert len(signals_df) > 0, "未生成信号"

        logger.info("✅ LSTM策略测试成功!")
        return True

    except Exception as e:
        logger.error("❌ LSTM策略测试失败: %s", e)
        import traceback

        traceback.print_exc()
        return False


async def test_transformer_strategy():
    """测试Transformer策略"""
    logger.info("🧪 测试Transformer交易策略...")

    try:
        # 创建策略
        strategy = TransformerTradingStrategy(
            strategy_name="Test_Transformer",
            sequence_length=30,  # 较短的序列用于测试
            epochs=3,  # 较少的训练轮数
            batch_size=16,
        )

        # 创建模拟数据
        market_data = create_mock_market_data(200)

        logger.info("创建了模拟市场数据: %d 条记录", len(market_data))

        # 准备特征
        features = await strategy.prepare_features(market_data)
        logger.info("特征准备完成: %d 个特征列", len(features.columns))

        # 训练模型 (简化测试，只训练1轮)
        logger.info("开始训练Transformer模型...")
        # 临时减少epochs进行快速测试
        original_epochs = strategy.epochs
        strategy.epochs = 1
        try:
            model_key = await strategy.train_ml_model(market_data)
            logger.info("模型训练完成: %s", model_key)
        finally:
            strategy.epochs = original_epochs

        # 生成预测
        logger.info("生成预测...")
        predictions = await strategy.get_ml_prediction(market_data)
        logger.info("生成 %d 个预测", len(predictions))

        # 解释信号
        signals_df = await strategy.interpret_ml_signals(predictions, market_data)
        logger.info("生成 %d 个交易信号", len(signals_df))

        # 获取策略信息
        info = strategy.get_strategy_info()
        logger.info("策略信息: %s", {k: v for k, v in info.items() if not k.startswith("_")})

        # 验证结果
        assert model_key != "training_failed", "Transformer模型训练失败"
        assert len(predictions) > 0, "未生成预测"
        assert len(signals_df) > 0, "未生成信号"

        logger.info("✅ Transformer策略测试成功!")
        return True

    except Exception as e:
        logger.error("❌ Transformer策略测试失败: %s", e)
        import traceback

        traceback.print_exc()
        return False


async def test_algorithm_comparison():
    """测试算法对比"""
    logger.info("🔍 测试算法对比...")

    try:
        # 创建两个策略
        lstm_strategy = LSTMTradingStrategy("Compare_LSTM", epochs=2)
        transformer_strategy = TransformerTradingStrategy("Compare_Transformer", epochs=2)

        # 使用相同的数据
        market_data = create_mock_market_data(150)

        strategies = [("LSTM", lstm_strategy), ("Transformer", transformer_strategy)]

        results = {}

        for name, strategy in strategies:
            logger.info("训练 %s 策略...", name)

            # 训练
            model_key = await strategy.train_ml_model(market_data)

            # 预测
            predictions = await strategy.get_ml_prediction(market_data)

            # 信号
            signals = await strategy.interpret_ml_signals(predictions, market_data)

            results[name] = {
                "model_key": model_key,
                "predictions_count": len(predictions),
                "signals_count": len(signals),
                "buy_signals": len(signals[signals["signal"] == 1]) if len(signals) > 0 else 0,
                "sell_signals": len(signals[signals["signal"] == -1]) if len(signals) > 0 else 0,
                "avg_confidence": signals["confidence"].mean() if len(signals) > 0 else 0,
            }

        # 对比结果
        logger.info("算法对比结果:")
        for name, result in results.items():
            logger.info(
                "  %s: 预测=%d, 信号=%d, 买入=%d, 卖出=%d, 平均置信度=%.2f",
                name,
                result["predictions_count"],
                result["signals_count"],
                result["buy_signals"],
                result["sell_signals"],
                result["avg_confidence"],
            )

        # 验证两个算法都能正常工作
        for name, result in results.items():
            assert result["predictions_count"] > 0, f"{name} 未生成预测"
            assert result["signals_count"] > 0, f"{name} 未生成信号"

        logger.info("✅ 算法对比测试成功!")
        return True

    except Exception as e:
        logger.error("❌ 算法对比测试失败: %s", e)
        return False


async def test_fallback_behavior():
    """测试fallback行为（当PyTorch不可用时）"""
    logger.info("🔄 测试Fallback行为...")

    try:
        # 强制禁用PyTorch来测试fallback
        import src.ml_strategy.strategy.lstm_trading_strategy as lstm_module

        original_torch_available = lstm_module.TORCH_AVAILABLE
        lstm_module.TORCH_AVAILABLE = False

        try:
            strategy = LSTMTradingStrategy("Fallback_Test", epochs=1)
            market_data = create_mock_market_data(50)

            # 训练（应该使用fallback）
            model_key = await strategy.train_ml_model(market_data)
            logger.info("Fallback训练结果: %s", model_key)

            # 预测（应该使用fallback）
            predictions = await strategy.get_ml_prediction(market_data)
            logger.info("Fallback预测结果: %d 个预测", len(predictions))

            # 验证fallback工作
            assert len(predictions) > 0, "Fallback预测未生成结果"

        finally:
            # 恢复原始状态
            lstm_module.TORCH_AVAILABLE = original_torch_available

        logger.info("✅ Fallback行为测试成功!")
        return True

    except Exception as e:
        logger.error("❌ Fallback行为测试失败: %s", e)
        return False


async def run_all_tests():
    """运行所有测试"""
    logger.info("🚀 运行高级ML算法完整测试套件...")

    results = []

    # 测试1: LSTM策略
    logger.info("\n" + "=" * 50)
    logger.info("TEST 1: LSTM交易策略")
    logger.info("=" * 50)
    result1 = await test_lstm_strategy()
    results.append(("LSTM Strategy", result1))

    # 测试2: Transformer策略
    logger.info("\n" + "=" * 50)
    logger.info("TEST 2: Transformer交易策略")
    logger.info("=" * 50)
    result2 = await test_transformer_strategy()
    results.append(("Transformer Strategy", result2))

    # 测试3: 算法对比
    logger.info("\n" + "=" * 50)
    logger.info("TEST 3: 算法对比")
    logger.info("=" * 50)
    result3 = await test_algorithm_comparison()
    results.append(("Algorithm Comparison", result3))

    # 测试4: Fallback行为
    logger.info("\n" + "=" * 50)
    logger.info("TEST 4: Fallback行为")
    logger.info("=" * 50)
    result4 = await test_fallback_behavior()
    results.append(("Fallback Behavior", result4))

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
        logger.info("🎉 所有测试通过! 高级ML算法已准备就绪。")
        logger.info("LSTM和Transformer策略已成功实现并测试。")
        return True
    logger.warning("⚠️ 某些测试失败。请检查实现。")
    return False


if __name__ == "__main__":
    # 运行测试
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)
