"""
完整可视化示例 (Complete Visualization Example)

功能说明:
- 演示策略执行、回测和可视化的完整流程
- 生成K线图、信号图、回测性能图表
- 展示最佳实践

作者: MyStocks量化交易团队
创建时间: 2025-10-18
版本: 1.0.0
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from datetime import date

# 导入策略和回测模块
from strategy.templates.momentum_template import MomentumStrategy
from backtest.backtest_engine import BacktestEngine, BacktestConfig
from src.visualization.chart_generator import ChartGenerator
from src.visualization.backtest_visualizer import BacktestVisualizer


def generate_sample_data(n=252):
    """生成示例数据"""
    np.random.seed(42)
    dates = pd.date_range("2024-01-01", periods=n, freq="D")

    # 生成趋势向上的价格数据
    close_prices = 100 + np.cumsum(np.random.randn(n) * 0.5 + 0.02)

    price_data = pd.DataFrame(
        {
            "open": close_prices + np.random.randn(n) * 0.5,
            "high": close_prices + np.abs(np.random.randn(n)),
            "low": close_prices - np.abs(np.random.randn(n)),
            "close": close_prices,
            "volume": np.random.uniform(1000000, 10000000, n),
        },
        index=dates,
    )

    return price_data


def main():
    """完整示例流程"""
    print("=" * 80)
    print("MyStocks量化交易系统 - 完整可视化示例")
    print("=" * 80)

    # ========== 第1步: 生成测试数据 ==========
    print("\n【第1步】生成测试数据...")
    price_data = generate_sample_data(n=252)
    print(f"  ✓ 生成了{len(price_data)}天的K线数据")

    # ========== 第2步: 创建策略并生成信号 ==========
    print("\n【第2步】创建动量策略并生成信号...")
    strategy = MomentumStrategy(
        unified_manager=None,
        ma_short=5,
        ma_long=20,
        rsi_period=14,
        rsi_oversold=30,
        rsi_overbought=70,
    )

    signals = strategy.generate_signals(price_data)
    valid_signals = signals[signals["signal"].notna()]

    print(f"  策略名称: {strategy.name}")
    print(f"  策略版本: {strategy.version}")
    print(f"  ✓ 生成了{len(valid_signals)}个信号")
    print(f"     - 买入: {len(valid_signals[valid_signals['signal'] == 'buy'])}")
    print(f"     - 卖出: {len(valid_signals[valid_signals['signal'] == 'sell'])}")

    # ========== 第3步: 执行回测 ==========
    print("\n【第3步】执行回测...")
    config = BacktestConfig(
        initial_capital=100000,
        commission_rate=0.0003,
        slippage_rate=0.0001,
        stamp_tax_rate=0.001,
    )

    engine = BacktestEngine(config=config, risk_free_rate=0.03)
    result = engine.run(price_data, signals)

    print(f"  ✓ 回测完成")
    print(f"     - 总收益率: {result['metrics'].get('total_return', 0):.2%}")
    print(f"     - 年化收益率: {result['metrics'].get('annualized_return', 0):.2%}")
    print(f"     - 夏普比率: {result['metrics'].get('sharpe_ratio', 0):.3f}")
    print(f"     - 最大回撤: {result['metrics'].get('max_drawdown', 0):.2%}")
    print(f"     - 交易次数: {result['metrics'].get('total_trades', 0)}")
    print(f"     - 胜率: {result['metrics'].get('win_rate', 0):.2%}")

    # ========== 第4步: 生成K线和信号图表 ==========
    print("\n【第4步】生成K线和信号图表...")
    chart_gen = ChartGenerator(style="china")

    # 计算技术指标用于图表
    ma5 = price_data["close"].rolling(5).mean()
    ma20 = price_data["close"].rolling(20).mean()

    from indicators.tdx_functions import RSI

    rsi = pd.Series(RSI(price_data["close"].values, 14), index=price_data.index)

    indicators = {"MA5": ma5, "MA20": ma20, "RSI": rsi}

    # 4.1 基础K线图
    chart_gen.plot_kline(
        price_data,
        title="Test Stock - Candlestick Chart",
        save_path="temp/example_kline.png",
    )
    print("  ✓ 保存了K线图: temp/example_kline.png")

    # 4.2 带信号的K线图
    chart_gen.plot_with_signals(
        price_data,
        signals,
        title="Momentum Strategy - K-line + Signals",
        save_path="temp/example_signals.png",
    )
    print("  ✓ 保存了信号图: temp/example_signals.png")

    # 4.3 完整图表（K线+信号+指标）
    chart_gen.plot_complete(
        price_data,
        signals=signals,
        indicators=indicators,
        title="Momentum Strategy - Complete Analysis",
        save_path="temp/example_complete.png",
    )
    print("  ✓ 保存了完整图表: temp/example_complete.png")

    # ========== 第5步: 生成回测性能图表 ==========
    print("\n【第5步】生成回测性能图表...")
    backtest_viz = BacktestVisualizer()

    # 5.1 权益曲线
    backtest_viz.plot_equity_curve(
        result["backtest"]["equity_curve"],
        title="Momentum Strategy - Equity Curve",
        save_path="temp/example_equity.png",
    )
    print("  ✓ 保存了权益曲线: temp/example_equity.png")

    # 5.2 回撤分析
    backtest_viz.plot_drawdown(
        result["backtest"]["equity_curve"],
        title="Momentum Strategy - Drawdown Analysis",
        save_path="temp/example_drawdown.png",
    )
    print("  ✓ 保存了回撤图: temp/example_drawdown.png")

    # 5.3 收益分布
    backtest_viz.plot_returns_distribution(
        result["backtest"]["daily_returns"],
        title="Momentum Strategy - Returns Distribution",
        save_path="temp/example_returns_dist.png",
    )
    print("  ✓ 保存了收益分布图: temp/example_returns_dist.png")

    # 5.4 月度收益热力图
    backtest_viz.plot_monthly_returns(
        result["backtest"]["daily_returns"],
        title="Momentum Strategy - Monthly Returns Heatmap",
        save_path="temp/example_monthly.png",
    )
    print("  ✓ 保存了月度收益图: temp/example_monthly.png")

    # 5.5 综合性能仪表盘
    backtest_viz.plot_dashboard(
        result,
        title="Momentum Strategy - Performance Dashboard",
        save_path="temp/example_dashboard.png",
    )
    print("  ✓ 保存了性能仪表盘: temp/example_dashboard.png")

    # ========== 第6步: 保存回测报告 ==========
    print("\n【第6步】保存回测报告...")
    report_path = "temp/example_report.txt"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(result["report"])
    print(f"  ✓ 保存了文字报告: {report_path}")

    # 保存交易记录
    trades_df = engine.get_trades_df()
    if not trades_df.empty:
        trades_path = "temp/example_trades.csv"
        trades_df.to_csv(trades_path, index=False)
        print(f"  ✓ 保存了交易记录: {trades_path}")
        print(f"     共{len(trades_df)}笔交易")

    # ========== 总结 ==========
    print("\n" + "=" * 80)
    print("完整示例执行成功！")
    print("=" * 80)
    print("\n生成的文件列表:")
    print("  K线图表:")
    print("    - temp/example_kline.png           (基础K线图)")
    print("    - temp/example_signals.png         (K线 + 交易信号)")
    print("    - temp/example_complete.png        (K线 + 信号 + 指标)")
    print("\n  回测性能图表:")
    print("    - temp/example_equity.png          (权益曲线)")
    print("    - temp/example_drawdown.png        (回撤分析)")
    print("    - temp/example_returns_dist.png    (收益分布)")
    print("    - temp/example_monthly.png         (月度收益热力图)")
    print("    - temp/example_dashboard.png       (综合性能仪表盘)")
    print("\n  数据文件:")
    print("    - temp/example_report.txt          (详细回测报告)")
    if not trades_df.empty:
        print("    - temp/example_trades.csv          (交易记录)")

    print("\n关键性能指标:")
    print(f"  总收益率:   {result['metrics'].get('total_return', 0):>10.2%}")
    print(f"  年化收益率: {result['metrics'].get('annualized_return', 0):>10.2%}")
    print(f"  夏普比率:   {result['metrics'].get('sharpe_ratio', 0):>10.3f}")
    print(f"  最大回撤:   {result['metrics'].get('max_drawdown', 0):>10.2%}")
    print(f"  胜率:       {result['metrics'].get('win_rate', 0):>10.2%}")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
