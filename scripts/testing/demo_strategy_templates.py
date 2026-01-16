#!/usr/bin/env python3
"""
策略模板系统演示脚本

演示4个预置策略模板的功能
"""

import sys
import os
from datetime import datetime, timedelta

# 添加项目路径
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "web", "backend"))

from app.backtest.strategies.factory import StrategyFactory


def print_header(title):
    """打印标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def demo_strategy_factory():
    """演示策略工厂功能"""
    print_header("📦 策略工厂功能演示")

    # 获取所有可用策略
    strategies = StrategyFactory.get_available_strategies()

    print(f"\n✅ 已注册 {len(strategies)} 个策略模板:\n")

    for i, strategy in enumerate(strategies, 1):
        print(f"{i}. {strategy['type']}")
        print(f"   名称: {strategy['name']}")
        print(f"   描述: {strategy['description']}")
        print(f"   版本: {strategy['version']}")
        print(f"   默认参数数量: {len(strategy['default_parameters'])}")
        print()


def demo_momentum_strategy():
    """演示动量策略"""
    print_header("📈 动量策略演示 (Momentum Strategy)")

    # 创建策略实例
    strategy = StrategyFactory.create_strategy(
        "momentum", {"ma_period": 20, "breakout_pct": 0.02, "rsi_period": 14}
    )

    print("\n策略信息:")
    print(f"  名称: {strategy.name}")
    print(f"  描述: {strategy.description}")
    print(f"  参数: {strategy.parameters}")

    # 模拟市场数据
    print("\n📊 模拟市场数据...")
    symbol = "000001"

    # 生成20天历史数据 + 当前数据
    import random

    random.seed(42)
    base_price = 10.0

    for i in range(21):
        price = base_price + random.uniform(-0.5, 0.5)
        data = {
            "date": datetime.now() - timedelta(days=20 - i),
            "open": price,
            "high": price * 1.02,
            "low": price * 0.98,
            "close": price,
            "volume": 1000000 + random.randint(-100000, 100000),
        }
        strategy.update_history(symbol, data)

    # 生成突破信号
    breakout_data = {
        "date": datetime.now(),
        "open": 10.5,
        "high": 10.8,
        "low": 10.4,
        "close": 10.7,  # 突破20日均线
        "volume": 2000000,  # 放量
    }

    signal = strategy.generate_signal(symbol, breakout_data)

    if signal:
        print("\n✅ 生成交易信号:")
        print(f"  股票: {signal.symbol}")
        print(f"  信号类型: {signal.signal_type.value}")
        print(f"  信号强度: {signal.strength:.2f}")
        print(f"  原因: {signal.reason}")
    else:
        print("\n⚠️ 未生成信号")


def demo_mean_reversion_strategy():
    """演示均值回归策略"""
    print_header("🔄 均值回归策略演示 (Mean Reversion Strategy)")

    strategy = StrategyFactory.create_strategy(
        "mean_reversion", {"bb_period": 20, "bb_std": 2.0, "entry_std": 2.0}
    )

    print("\n策略信息:")
    print(f"  名称: {strategy.name}")
    print(f"  描述: {strategy.description}")

    # 模拟数据
    symbol = "000002"
    base_price = 50.0

    import random

    random.seed(100)

    # 生成围绕均值波动的数据
    for i in range(20):
        price = base_price + random.uniform(-5, 5)
        data = {
            "date": datetime.now() - timedelta(days=19 - i),
            "close": price,
            "open": price,
            "high": price * 1.01,
            "low": price * 0.99,
            "volume": 1000000,
        }
        strategy.update_history(symbol, data)

    # 生成超卖信号（价格跌破下轨）
    oversold_data = {
        "date": datetime.now(),
        "close": 40.0,  # 远低于均值
        "open": 41.0,
        "high": 42.0,
        "low": 40.0,
        "volume": 1500000,
    }

    signal = strategy.generate_signal(symbol, oversold_data)

    if signal:
        print("\n✅ 生成交易信号:")
        print(f"  信号类型: {signal.signal_type.value}")
        print(f"  信号强度: {signal.strength:.2f}")
        print(f"  原因: {signal.reason}")
        if signal.target_price:
            print(f"  目标价: {signal.target_price}")
    else:
        print("\n⚠️ 未生成信号")


def demo_breakout_strategy():
    """演示突破策略"""
    print_header("🚀 突破策略演示 (Breakout Strategy)")

    strategy = StrategyFactory.create_strategy(
        "breakout",
        {"lookback_period": 20, "breakout_confirm_pct": 0.01, "volume_multiplier": 1.5},
    )

    print("\n策略信息:")
    print(f"  名称: {strategy.name}")
    print(f"  描述: {strategy.description}")

    # 模拟盘整后突破的数据
    symbol = "000003"
    import random

    random.seed(200)

    # 前19天在 9.5 - 10.5 区间盘整
    for i in range(20):
        price = 10.0 + random.uniform(-0.5, 0.5)
        data = {
            "date": datetime.now() - timedelta(days=19 - i),
            "close": price,
            "open": price,
            "high": price * 1.01,
            "low": price * 0.99,
            "volume": 1000000,
        }
        strategy.update_history(symbol, data)

    # 第20天放量突破
    breakout_data = {
        "date": datetime.now(),
        "close": 11.0,  # 突破前期高点
        "open": 10.5,
        "high": 11.2,
        "low": 10.4,
        "volume": 2000000,  # 成交量翻倍
    }

    signal = strategy.generate_signal(symbol, breakout_data)

    if signal:
        print("\n✅ 生成突破信号:")
        print(f"  信号类型: {signal.signal_type.value}")
        print(f"  信号强度: {signal.strength:.2f}")
        print(f"  原因: {signal.reason}")
        if signal.stop_loss:
            print(f"  止损价: {signal.stop_loss}")
        if signal.take_profit:
            print(f"  止盈价: {signal.take_profit}")
    else:
        print("\n⚠️ 未生成信号")


def demo_grid_strategy():
    """演示网格策略"""
    print_header("📊 网格策略演示 (Grid Strategy)")

    strategy = StrategyFactory.create_strategy(
        "grid", {"grid_count": 10, "grid_spacing_pct": 0.02, "base_quantity": 100}
    )

    print("\n策略信息:")
    print(f"  名称: {strategy.name}")
    print(f"  描述: {strategy.description}")

    # 模拟震荡行情
    symbol = "000004"
    import random

    random.seed(300)

    base_price = 100.0
    for i in range(20):
        # 围绕100元震荡
        price = base_price + random.uniform(-5, 5)
        data = {
            "date": datetime.now() - timedelta(days=19 - i),
            "close": price,
            "open": price,
            "high": price * 1.01,
            "low": price * 0.99,
            "volume": 1000000,
        }
        strategy.update_history(symbol, data)

    print("\n📏 网格设置:")
    print(f"  网格数量: {strategy.parameters['grid_count']}")
    print(f"  网格间距: {strategy.parameters['grid_spacing_pct'] * 100}%")
    if strategy.grid_levels:
        print(f"  网格线: {strategy.grid_levels[::2]}")  # 显示部分网格线

    # 价格下跌到网格线
    buy_signal_data = {
        "date": datetime.now(),
        "close": 96.0,  # 触及下方网格线
        "open": 97.0,
        "high": 97.5,
        "low": 95.8,
        "volume": 1200000,
    }

    signal = strategy.generate_signal(symbol, buy_signal_data)

    if signal:
        print("\n✅ 生成网格信号:")
        print(f"  信号类型: {signal.signal_type.value}")
        print(f"  信号强度: {signal.strength:.2f}")
        print(f"  原因: {signal.reason}")
    else:
        print("\n⚠️ 未生成信号")


def demo_parameter_validation():
    """演示参数验证"""
    print_header("✔️ 参数验证演示")

    # 有效参数
    valid_params = {"ma_period": 20, "breakout_pct": 0.02}

    is_valid, error = StrategyFactory.validate_parameters("momentum", valid_params)
    print("\n✅ 有效参数验证:")
    print(f"  参数: {valid_params}")
    print(f"  结果: {'通过' if is_valid else '失败'}")

    # 无效参数（超出范围）
    invalid_params = {
        "ma_period": 300,  # 超过最大值200
        "breakout_pct": 0.02,
    }

    is_valid, error = StrategyFactory.validate_parameters("momentum", invalid_params)
    print("\n❌ 无效参数验证:")
    print(f"  参数: {invalid_params}")
    print(f"  结果: {'通过' if is_valid else '失败'}")
    if not is_valid:
        print(f"  错误: {error}")


def main():
    """主函数"""
    print("\n" + "🎯 " * 20)
    print("策略模板系统演示")
    print("🎯 " * 20)

    # 1. 策略工厂
    demo_strategy_factory()

    # 2. 动量策略
    demo_momentum_strategy()

    # 3. 均值回归策略
    demo_mean_reversion_strategy()

    # 4. 突破策略
    demo_breakout_strategy()

    # 5. 网格策略
    demo_grid_strategy()

    # 6. 参数验证
    demo_parameter_validation()

    # 总结
    print_header("📋 演示总结")
    print("\n✅ 策略模板系统功能:")
    print("   - 策略工厂: 统一管理和创建策略")
    print("   - 动量策略: 追涨杀跌，趋势跟踪")
    print("   - 均值回归: 低买高卖，区间操作")
    print("   - 突破策略: 关键位突破，顺势而为")
    print("   - 网格策略: 震荡套利，多次交易")
    print("   - 参数验证: 确保参数有效性")

    print("\n🎉 策略模板系统演示完成！\n")


if __name__ == "__main__":
    main()
