#!/usr/bin/env python3
"""
完整策略模板系统演示

展示所有8个预置策略模板的功能
- 原有4个: Momentum, MeanReversion, Breakout, Grid
- 新增4个: DualMA, Turtle, MACD, BollingerBreakout
"""
import sys
import os
from datetime import datetime, timedelta
from decimal import Decimal

# 添加项目路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'web', 'backend'))

from app.backtest.strategies.factory import StrategyFactory
from app.backtest.strategies.base import SignalType


def print_header(title):
    """打印标题"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_strategy_info(strategy):
    """打印策略信息"""
    print(f"\n策略: {strategy.name}")
    print(f"描述: {strategy.description}")
    print(f"版本: {strategy.version}")
    print(f"参数数量: {len(strategy.parameters)}")


def generate_market_data(base_price, days, volatility=0.02):
    """生成模拟市场数据"""
    import random
    random.seed(42)

    data = []
    price = base_price

    for i in range(days):
        change = random.uniform(-volatility, volatility)
        price = price * (1 + change)

        high = price * (1 + abs(random.uniform(0, volatility/2)))
        low = price * (1 - abs(random.uniform(0, volatility/2)))
        volume = 1000000 + random.randint(-200000, 200000)

        data.append({
            'date': datetime.now() - timedelta(days=days-i-1),
            'open': price,
            'high': high,
            'low': low,
            'close': price,
            'volume': volume
        })

    return data


def demo_strategy_factory():
    """演示策略工厂"""
    print_header("📦 策略工厂 - 8个预置策略模板")

    strategies = StrategyFactory.get_available_strategies()

    print(f"\n✅ 已注册 {len(strategies)} 个策略模板:\n")

    for i, strategy in enumerate(strategies, 1):
        print(f"{i}. {strategy['type']}")
        print(f"   名称: {strategy['name']}")
        print(f"   描述: {strategy['description'][:50]}...")
        print()


def demo_dual_ma():
    """演示双均线策略"""
    print_header("📈 双均线策略 (Dual Moving Average)")

    strategy = StrategyFactory.create_strategy('dual_ma', {
        'short_period': 10,
        'long_period': 30,
        'ma_type': 'sma',
        'volume_filter': True
    })

    print_strategy_info(strategy)

    symbol = 'TEST001'
    data_list = generate_market_data(10.0, 35, 0.03)

    # 构建历史
    for data in data_list[:-1]:
        strategy.update_history(symbol, data)

    # 模拟金叉
    current_data = {
        'date': datetime.now(),
        'open': 10.8,
        'high': 11.0,
        'low': 10.7,
        'close': 10.9,  # 价格上涨，可能触发金叉
        'volume': 1500000
    }

    signal = strategy.generate_signal(symbol, current_data)

    if signal:
        print(f"\n✅ 生成信号:")
        print(f"   类型: {signal.signal_type.value}")
        print(f"   强度: {signal.strength:.2f}")
        print(f"   原因: {signal.reason}")
    else:
        print("\n⚠️ 未生成信号 (可能需要更多数据)")


def demo_turtle():
    """演示海龟策略"""
    print_header("🐢 海龟策略 (Turtle Trading)")

    strategy = StrategyFactory.create_strategy('turtle', {
        'system': 1,  # System 1 (快速)
        'entry_period_s1': 20,
        'exit_period_s1': 10,
        'atr_period': 20,
        'max_units': 4
    })

    print_strategy_info(strategy)

    symbol = 'TEST002'

    # 生成盘整后突破的数据
    data_list = []
    import random
    random.seed(100)

    # 前20天盘整
    for i in range(20):
        price = 100 + random.uniform(-3, 3)
        data_list.append({
            'date': datetime.now() - timedelta(days=20-i),
            'open': price,
            'high': price * 1.02,
            'low': price * 0.98,
            'close': price,
            'volume': 1000000
        })

    # 构建历史
    for data in data_list:
        strategy.update_history(symbol, data)

    # 突破20日高点
    breakout_data = {
        'date': datetime.now(),
        'open': 105,
        'high': 108,
        'low': 104,
        'close': 107,  # 突破前期高点
        'volume': 2000000
    }

    signal = strategy.generate_signal(symbol, breakout_data)

    if signal:
        print(f"\n✅ 生成海龟入场信号:")
        print(f"   类型: {signal.signal_type.value}")
        print(f"   强度: {signal.strength:.2f}")
        print(f"   原因: {signal.reason}")
        if signal.stop_loss:
            print(f"   止损: {signal.stop_loss}")
        if signal.metadata:
            print(f"   N值: {signal.metadata.get('n_value', 'N/A')}")
    else:
        print("\n⚠️ 未生成信号")


def demo_macd():
    """演示MACD策略"""
    print_header("📊 MACD策略 (Moving Average Convergence Divergence)")

    strategy = StrategyFactory.create_strategy('macd', {
        'fast_period': 12,
        'slow_period': 26,
        'signal_period': 9,
        'zero_line_filter': True
    })

    print_strategy_info(strategy)

    symbol = 'TEST003'
    data_list = generate_market_data(50.0, 30, 0.02)

    for data in data_list:
        strategy.update_history(symbol, data)

    # 模拟金叉数据
    current_data = {
        'date': datetime.now(),
        'open': 52.0,
        'high': 53.0,
        'low': 51.8,
        'close': 52.5,
        'volume': 1500000
    }

    signal = strategy.generate_signal(symbol, current_data)

    if signal:
        print(f"\n✅ 生成MACD信号:")
        print(f"   类型: {signal.signal_type.value}")
        print(f"   强度: {signal.strength:.2f}")
        print(f"   原因: {signal.reason}")
        if signal.metadata:
            print(f"   MACD: {signal.metadata.get('macd', 'N/A'):.4f}")
            print(f"   Signal: {signal.metadata.get('signal', 'N/A'):.4f}")
            print(f"   Histogram: {signal.metadata.get('histogram', 'N/A'):.4f}")
    else:
        print("\n⚠️ 未生成信号 (需要更多数据)")


def demo_bollinger_breakout():
    """演示布林带突破策略"""
    print_header("🎯 布林带突破策略 (Bollinger Bands Breakout)")

    strategy = StrategyFactory.create_strategy('bollinger_breakout', {
        'bb_period': 20,
        'bb_std': 2.0,
        'strategy_mode': 'mixed',  # 混合模式
        'use_bandwidth_filter': True
    })

    print_strategy_info(strategy)

    symbol = 'TEST004'
    data_list = generate_market_data(100.0, 25, 0.015)

    for data in data_list:
        strategy.update_history(symbol, data)

    # 模拟突破上轨
    breakout_data = {
        'date': datetime.now(),
        'open': 105,
        'high': 107,
        'low': 104,
        'close': 106,  # 可能突破上轨
        'volume': 2000000
    }

    signal = strategy.generate_signal(symbol, breakout_data)

    if signal:
        print(f"\n✅ 生成布林带信号:")
        print(f"   类型: {signal.signal_type.value}")
        print(f"   强度: {signal.strength:.2f}")
        print(f"   原因: {signal.reason}")
        if signal.metadata:
            meta = signal.metadata
            print(f"   上轨: {meta.get('upper', 'N/A'):.2f}")
            print(f"   中轨: {meta.get('middle', 'N/A'):.2f}")
            print(f"   下轨: {meta.get('lower', 'N/A'):.2f}")
            print(f"   带宽: {meta.get('bandwidth', 'N/A'):.4f}")
    else:
        print("\n⚠️ 未生成信号")


def demo_strategy_comparison():
    """策略对比分析"""
    print_header("📊 策略对比分析")

    strategies_info = [
        {
            'type': 'dual_ma',
            'name': '双均线',
            'category': '趋势跟踪',
            '适用': '单边趋势行情',
            '优势': '简单经典，信号明确',
            '风险': '震荡市频繁交易'
        },
        {
            'type': 'turtle',
            'name': '海龟',
            'category': '趋势跟踪',
            '适用': '中长期趋势',
            '优势': '严格风控，金字塔加仓',
            '风险': '需要大资金，回撤较大'
        },
        {
            'type': 'macd',
            'name': 'MACD',
            'category': '趋势+动量',
            '适用': '趋势转折点',
            '优势': '双重确认，滞后较小',
            '风险': '假突破风险'
        },
        {
            'type': 'bollinger_breakout',
            'name': '布林带突破',
            'category': '波动率突破',
            '适用': '盘整后突破',
            '优势': '自适应波动率',
            '风险': '假突破频繁'
        },
        {
            'type': 'momentum',
            'name': '动量',
            'category': '趋势跟踪',
            '适用': '强势股追涨',
            '优势': '捕捉强势行情',
            '风险': '追高风险'
        },
        {
            'type': 'mean_reversion',
            'name': '均值回归',
            'category': '反向交易',
            '适用': '震荡整理',
            '优势': '低买高卖',
            '风险': '趋势市亏损'
        },
        {
            'type': 'breakout',
            'name': '突破',
            'category': '突破跟随',
            '适用': '盘整后突破',
            '优势': 'ATR止损止盈',
            '风险': '假突破损失'
        },
        {
            'type': 'grid',
            'name': '网格',
            'category': '区间套利',
            '适用': '箱体震荡',
            '优势': '多次交易获利',
            '风险': '单边市套牢'
        },
    ]

    print("\n策略分类对比表:\n")
    print(f"{'策略':<15} {'类型':<12} {'适用场景':<15} {'核心优势':<20}")
    print("-" * 70)

    for info in strategies_info:
        print(f"{info['name']:<15} {info['category']:<12} {info['适用']:<15} {info['优势']:<20}")

    print("\n\n策略组合建议:\n")
    print("1. 趋势市场: Turtle + DualMA + MACD")
    print("   - 海龟负责主趋势，双均线快速响应，MACD确认")
    print()
    print("2. 震荡市场: Grid + MeanReversion")
    print("   - 网格套利，均值回归低买高卖")
    print()
    print("3. 突破行情: Breakout + BollingerBreakout")
    print("   - 双重突破确认，提高成功率")
    print()
    print("4. 全天候组合: Turtle + Grid + MACD")
    print("   - 趋势+震荡+确认，适应不同市场状态")


def demo_parameter_validation():
    """演示参数验证"""
    print_header("✅ 参数验证功能")

    # 有效参数
    valid_params = {
        'system': 1,
        'entry_period_s1': 20,
        'max_units': 4
    }

    is_valid, error = StrategyFactory.validate_parameters('turtle', valid_params)
    print(f"\n1. 海龟策略参数验证:")
    print(f"   参数: {valid_params}")
    print(f"   结果: {'✅ 通过' if is_valid else '❌ 失败'}")

    # 无效参数
    invalid_params = {
        'fast_period': 100,  # 超过最大值20
        'slow_period': 26
    }

    is_valid, error = StrategyFactory.validate_parameters('macd', invalid_params)
    print(f"\n2. MACD策略参数验证:")
    print(f"   参数: {invalid_params}")
    print(f"   结果: {'✅ 通过' if is_valid else '❌ 失败'}")
    if not is_valid:
        print(f"   错误: {error}")


def demo_all_strategies_summary():
    """展示所有策略总结"""
    print_header("📋 策略模板系统总结")

    strategies = StrategyFactory.get_available_strategies()

    print(f"\n✅ 策略模板系统完成:")
    print(f"   - 总策略数: {len(strategies)}")
    print(f"   - 原有策略: 4 (Momentum, MeanReversion, Breakout, Grid)")
    print(f"   - 新增策略: 4 (DualMA, Turtle, MACD, BollingerBreakout)")
    print()
    print("✅ 核心功能:")
    print("   - 策略工厂: 统一创建和管理")
    print("   - 参数验证: 类型和范围检查")
    print("   - 技术指标: SMA, EMA, RSI, ATR, BB等")
    print("   - 信号生成: 标准化的交易信号")
    print("   - 仓位管理: 动态仓位计算")
    print("   - 风险控制: 止损止盈机制")
    print()
    print("✅ 扩展能力:")
    print("   - 轻松添加新策略 (继承BaseStrategy)")
    print("   - 灵活参数配置 (get_default_parameters)")
    print("   - 自动注册机制 (StrategyFactory)")
    print()
    print("📚 使用场景:")
    print("   - 量化回测系统")
    print("   - 策略研究平台")
    print("   - 交易信号生成")
    print("   - 策略组合优化")


def main():
    """主函数"""
    print("\n" + "🎯 " * 25)
    print("完整策略模板系统演示 - 8个预置策略")
    print("🎯 " * 25)

    # 1. 策略工厂
    demo_strategy_factory()

    # 2. 新增策略演示
    demo_dual_ma()
    demo_turtle()
    demo_macd()
    demo_bollinger_breakout()

    # 3. 策略对比
    demo_strategy_comparison()

    # 4. 参数验证
    demo_parameter_validation()

    # 5. 总结
    demo_all_strategies_summary()

    print("\n" + "=" * 70)
    print("🎉 演示完成！策略模板系统已包含8个预置策略")
    print("=" * 70 + "\n")


if __name__ == '__main__':
    main()
