#!/usr/bin/env python3
"""回测引擎功能演示脚本

演示以下核心功能：
1. 性能指标计算 - 夏普比率、最大回撤、胜率等15+种指标
2. 风险控制 - 止损/止盈、仓位限制
"""

import os
import sys
from datetime import datetime, timedelta
from decimal import Decimal


# 添加项目路径
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
)
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "web", "backend"))

from app.backtest.events import MarketEvent, OrderEvent
from app.backtest.performance_metrics import PerformanceMetrics
from app.backtest.portfolio_manager import PortfolioManager, Position
from app.backtest.risk_manager import RiskManager


def demo_performance_metrics():
    """演示性能指标计算功能"""
    print("\n" + "=" * 60)
    print("📊 性能指标计算演示")
    print("=" * 60)

    # 创建性能指标计算器
    metrics = PerformanceMetrics(risk_free_rate=0.03)  # 3% 无风险利率

    # 模拟资金曲线数据 (180天)
    initial_capital = Decimal(100000)
    equity_curve = []
    base_date = datetime(2024, 1, 1)

    # 生成模拟资金曲线 (波动但整体上涨)
    import random

    random.seed(42)  # 固定随机种子以便复现

    equity = float(initial_capital)
    peak = equity

    for i in range(180):
        # 模拟每日收益率 (-2% to +2.5%)
        daily_return = random.uniform(-0.02, 0.025)
        equity *= 1 + daily_return

        # 计算回撤
        peak = max(peak, equity)
        drawdown = (peak - equity) / peak if peak > 0 else 0

        equity_curve.append(
            {
                "date": base_date + timedelta(days=i),
                "equity": Decimal(str(round(equity, 2))),
                "drawdown": Decimal(str(round(drawdown, 4))),
            },
        )

    # 模拟交易记录
    trades = [
        {"profit_loss": 1500, "symbol": "000001"},  # 赢
        {"profit_loss": -800, "symbol": "000002"},  # 输
        {"profit_loss": 2200, "symbol": "000001"},  # 赢
        {"profit_loss": -500, "symbol": "000003"},  # 输
        {"profit_loss": 1800, "symbol": "000002"},  # 赢
        {"profit_loss": -1200, "symbol": "000001"},  # 输
        {"profit_loss": 3000, "symbol": "000004"},  # 赢
        {"profit_loss": 900, "symbol": "000002"},  # 赢
        {"profit_loss": -600, "symbol": "000003"},  # 输
        {"profit_loss": 2500, "symbol": "000001"},  # 赢
    ]

    # 计算所有性能指标
    print("\n🔄 计算性能指标...\n")
    results = metrics.calculate_all_metrics(
        equity_curve=equity_curve,
        trades=trades,
        initial_capital=initial_capital,
    )

    # 显示收益指标
    print("📈 收益指标:")
    print(f"  • 总收益率: {results['total_return'] * 100:.2f}%")
    print(f"  • 年化收益率: {results['annualized_return'] * 100:.2f}%")
    print(f"  • 最终资金: {float(equity_curve[-1]['equity']):,.2f}")

    # 显示风险指标
    print("\n📉 风险指标:")
    print(f"  • 年化波动率: {results['volatility'] * 100:.2f}%")
    print(f"  • 最大回撤: {results['max_drawdown'] * 100:.2f}%")
    print(f"  • 最大回撤持续天数: {results['max_drawdown_duration']} 天")

    # 显示风险调整收益
    print("\n⚖️ 风险调整收益:")
    print(f"  • 夏普比率: {results['sharpe_ratio']:.4f}")
    print(f"  • Sortino比率: {results['sortino_ratio']:.4f}")
    if results["calmar_ratio"]:
        print(f"  • Calmar比率: {results['calmar_ratio']:.4f}")

    # 显示交易指标
    print("\n💼 交易指标:")
    print(f"  • 总交易次数: {results['total_trades']}")
    print(f"  • 胜率: {results['win_rate'] * 100:.1f}%")
    print(f"  • 盈亏比: {results['profit_factor']:.2f}")
    print(f"  • 平均盈利: {results['avg_win']:.2f}")
    print(f"  • 平均亏损: {results['avg_loss']:.2f}")
    print(f"  • 盈亏比(金额): {results['avg_win_loss_ratio']:.2f}")

    print(
        f"\n✅ 性能指标计算完成！共计算 {len([k for k in results.keys() if results[k] is not None])} 个指标",
    )

    return results


def demo_risk_control():
    """演示风险控制功能"""
    print("\n" + "=" * 60)
    print("🛡️ 风险控制功能演示")
    print("=" * 60)

    # 创建风险管理器
    risk_manager = RiskManager(
        max_position_size=0.10,  # 单股票最大仓位10%
        max_total_position=0.95,  # 总仓位上限95%
        stop_loss_pct=0.05,  # 止损5%
        take_profit_pct=0.15,  # 止盈15%
        max_daily_loss=0.03,  # 单日最大亏损3%
    )

    # 创建组合管理器
    portfolio = PortfolioManager(
        initial_capital=Decimal(100000),
        commission_rate=Decimal("0.0003"),
        slippage_rate=Decimal("0.001"),
    )

    print("\n📋 风险控制参数配置:")
    print("  • 单股票最大仓位: 10%")
    print("  • 总仓位上限: 95%")
    print("  • 止损比例: 5%")
    print("  • 止盈比例: 15%")
    print("  • 单日最大亏损: 3%")

    # 测试1: 仓位限制检查
    print("\n\n📌 测试1: 仓位限制检查")
    print("-" * 40)

    # 模拟市场数据更新
    market_event = MarketEvent(
        symbol="000001",
        trade_date=datetime.now(),
        open_price=Decimal(50),
        high_price=Decimal(51),
        low_price=Decimal(49),
        close_price=Decimal(50),
        volume=1000000,
    )
    portfolio.update_market_data(market_event)

    # 创建一个超出仓位限制的订单
    large_order = OrderEvent(
        symbol="000001",
        trade_date=datetime.now(),
        order_type="MARKET",
        action="BUY",
        quantity=3000,  # 3000 * 50 = 150000 > 100000 * 10%
        strategy_id=1,
    )

    is_valid, reason = risk_manager.validate_order(
        large_order,
        portfolio,
        Decimal(50),
    )

    if not is_valid:
        print(f"  ❌ 订单被拒绝: {reason}")
    else:
        print("  ✅ 订单通过验证")

    # 创建一个合理的订单
    small_order = OrderEvent(
        symbol="000001",
        trade_date=datetime.now(),
        order_type="MARKET",
        action="BUY",
        quantity=100,  # 100 * 50 = 5000 < 100000 * 10%
        strategy_id=1,
    )

    is_valid, reason = risk_manager.validate_order(
        small_order,
        portfolio,
        Decimal(50),
    )

    if is_valid:
        print("  ✅ 小额订单通过验证")
    else:
        print(f"  ❌ 订单被拒绝: {reason}")

    # 测试2: 止损检查
    print("\n\n📌 测试2: 止损检查")
    print("-" * 40)

    # 创建一个亏损的持仓
    position = Position("000002")
    position.quantity = 1000
    position.avg_cost = Decimal(100)

    # 场景1: 亏损3% (未触发止损)
    current_price = Decimal(97)
    result = risk_manager.check_stop_loss_take_profit("000002", position, current_price)
    if result:
        print(f"  价格97元 (亏损3%): ❌ {result}")
    else:
        print("  价格97元 (亏损3%): ✅ 未触发止损")

    # 场景2: 亏损6% (触发止损)
    current_price = Decimal(94)
    result = risk_manager.check_stop_loss_take_profit("000002", position, current_price)
    if result:
        print(f"  价格94元 (亏损6%): 🛑 {result}")
    else:
        print("  价格94元 (亏损6%): ✅ 未触发止损")

    # 测试3: 止盈检查
    print("\n\n📌 测试3: 止盈检查")
    print("-" * 40)

    # 场景1: 盈利10% (未触发止盈)
    current_price = Decimal(110)
    result = risk_manager.check_stop_loss_take_profit("000002", position, current_price)
    if result:
        print(f"  价格110元 (盈利10%): 💰 {result}")
    else:
        print("  价格110元 (盈利10%): ✅ 未触发止盈")

    # 场景2: 盈利16% (触发止盈)
    current_price = Decimal(116)
    result = risk_manager.check_stop_loss_take_profit("000002", position, current_price)
    if result:
        print(f"  价格116元 (盈利16%): 💰 {result}")
    else:
        print("  价格116元 (盈利16%): ✅ 未触发止盈")

    # 测试4: 获取风险摘要
    print("\n\n📌 测试4: 风险状态摘要")
    print("-" * 40)

    risk_summary = risk_manager.get_risk_summary(portfolio)
    print(f"  • 当前仓位比例: {risk_summary['current_position_ratio'] * 100:.1f}%")
    print(f"  • 当前回撤: {risk_summary['current_drawdown'] * 100:.2f}%")
    print(f"  • 持仓数量: {risk_summary['num_positions']}")

    print("\n✅ 风险控制功能演示完成！")


def main():
    """主函数"""
    print("\n" + "🚀 " * 20)
    print("回测引擎核心功能演示")
    print("🚀 " * 20)

    # 演示性能指标计算
    metrics_results = demo_performance_metrics()

    # 演示风险控制
    demo_risk_control()

    # 总结
    print("\n" + "=" * 60)
    print("📋 演示总结")
    print("=" * 60)
    print("\n✅ 性能指标计算:")
    print("   - 收益指标: 总收益率、年化收益率")
    print("   - 风险指标: 波动率、最大回撤、回撤持续时间")
    print("   - 风险调整收益: 夏普比率、Sortino比率、Calmar比率")
    print("   - 交易指标: 胜率、盈亏比、平均盈亏")

    print("\n✅ 风险控制功能:")
    print("   - 仓位限制: 单股票和总仓位限制")
    print("   - 止损止盈: 自动检测并触发平仓信号")
    print("   - 风险摘要: 实时监控风险状态")

    print("\n" + "🎉 " * 20)


if __name__ == "__main__":
    main()
