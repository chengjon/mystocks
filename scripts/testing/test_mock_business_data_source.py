"""
测试MockBusinessDataSource完整功能

验证所有10个业务数据接口方法:
- get_dashboard_summary()
- get_sector_performance()
- execute_backtest()
- get_backtest_results()
- calculate_risk_metrics()
- check_risk_alerts()
- analyze_trading_signals()
- get_portfolio_analysis()
- perform_attribution_analysis()
- execute_stock_screener()

版本: 1.0.0
日期: 2025-11-21
"""

import sys
import os
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, project_root)

from src.data_sources import get_business_source


def test_dashboard_summary():
    """测试仪表盘摘要"""
    print("\n" + "=" * 80)
    print("测试 1/10: get_dashboard_summary()")
    print("=" * 80)

    biz_source = get_business_source()

    dashboard = biz_source.get_dashboard_summary(user_id=1)

    assert "market_overview" in dashboard, "缺少市场概览数据"
    assert "watchlist_performance" in dashboard, "缺少自选股表现数据"
    assert "top_fund_flow" in dashboard, "缺少资金流向数据"
    assert "data_status" in dashboard, "缺少数据状态"
    assert "user_stats" in dashboard, "缺少用户统计"

    print(f"✅ 市场概览: {dashboard['market_overview']['total_stocks']}只股票")
    print(f"✅ 自选股表现: {len(dashboard['watchlist_performance'])}只自选股")
    print(f"✅ 资金流向: {len(dashboard['top_fund_flow'])}只股票")
    print(f"✅ 数据状态: {dashboard['data_status']['market_status']}")
    print(
        f"✅ 用户统计: {dashboard['user_stats']['watchlist_count']}只自选股, {dashboard['user_stats']['strategy_count']}个策略"
    )

    return True


def test_sector_performance():
    """测试板块表现"""
    print("\n" + "=" * 80)
    print("测试 2/10: get_sector_performance()")
    print("=" * 80)

    biz_source = get_business_source()

    # 测试行业表现
    industry_result = biz_source.get_sector_performance(sector_type="industry", limit=5)

    assert "sectors" in industry_result
    industry_perf = industry_result["sectors"]
    assert len(industry_perf) <= 5, "行业表现数据数量不正确"

    print("\n行业表现 (前5):")
    for sector in industry_perf[:5]:
        assert "sector_name" in sector
        assert "sector_code" in sector
        assert "avg_change_percent" in sector
        print(f"  - {sector['sector_name']}: {sector['avg_change_percent']:.2f}%")

    # 测试概念表现
    concept_result = biz_source.get_sector_performance(sector_type="concept", limit=3)

    assert "sectors" in concept_result
    concept_perf = concept_result["sectors"]
    assert len(concept_perf) <= 3, "概念表现数据数量不正确"
    print(f"\n✅ 行业表现: {len(industry_perf)}个行业")
    print(f"✅ 概念表现: {len(concept_perf)}个概念")

    return True


def test_backtest_execution():
    """测试回测执行"""
    print("\n" + "=" * 80)
    print("测试 3/10: execute_backtest()")
    print("=" * 80)

    biz_source = get_business_source()

    # 执行回测
    strategy_config = {
        "name": "双均线策略",
        "type": "ma_cross",
        "parameters": {
            "short_window": 5,
            "long_window": 20,
            "stop_loss": 0.05,
            "take_profit": 0.10,
        },
    }

    symbols = ["600000", "000001", "600519"]
    start_date = (datetime.now() - timedelta(days=365)).date()
    end_date = datetime.now().date()

    result = biz_source.execute_backtest(
        user_id=1,
        strategy_config=strategy_config,
        symbols=symbols,
        start_date=start_date,
        end_date=end_date,
        initial_capital=100000.0,
    )

    assert "backtest_id" in result
    assert "equity_curve" in result
    assert "trades" in result
    assert "positions" in result
    assert "total_return" in result

    print("\n回测结果:")
    print(f"  - 回测ID: {result['backtest_id']}")
    print(f"  - 总收益率: {result['total_return']:.2f}%")
    print(f"  - 年化收益率: {result['annual_return']:.2f}%")
    print(f"  - 最大回撤: {result['max_drawdown']:.2f}%")
    print(f"  - 夏普比率: {result['sharpe_ratio']:.2f}")
    print(f"  - 胜率: {result['win_rate']:.2f}%")
    print(f"  - 交易次数: {len(result['trades'])}笔")
    print(f"  - 持仓数: {len(result['positions'])}只")
    print(f"  - 权益曲线点数: {len(result['equity_curve'])}个")

    print("\n✅ 回测执行成功")

    return result["backtest_id"]


def test_backtest_results(backtest_id):
    """测试回测结果检索"""
    print("\n" + "=" * 80)
    print("测试 4/10: get_backtest_results()")
    print("=" * 80)

    biz_source = get_business_source()

    # 按ID查询
    results = biz_source.get_backtest_results(user_id=1, backtest_id=backtest_id)
    assert len(results) > 0, "未找到回测结果"
    assert results[0]["backtest_id"] == backtest_id
    print(f"✅ 按ID查询成功: {backtest_id}")

    # 按用户查询
    results = biz_source.get_backtest_results(user_id=1, limit=10)
    assert len(results) > 0, "用户没有回测结果"
    print(f"✅ 按用户查询成功: 找到{len(results)}个回测结果")

    return True


def test_risk_metrics():
    """测试风险指标计算"""
    print("\n" + "=" * 80)
    print("测试 5/10: calculate_risk_metrics()")
    print("=" * 80)

    biz_source = get_business_source()

    portfolio = [
        {"symbol": "600000", "quantity": 1000, "price": 10.5, "avg_cost": 10.0},
        {"symbol": "000001", "quantity": 2000, "price": 16.0, "avg_cost": 15.0},
        {"symbol": "600519", "quantity": 100, "price": 1850.0, "avg_cost": 1800.0},
    ]

    risk_metrics = biz_source.calculate_risk_metrics(user_id=1, portfolio=portfolio)

    assert "var_1day" in risk_metrics
    assert "var_5day" in risk_metrics
    assert "volatility_annual" in risk_metrics
    assert "concentration_risk" in risk_metrics
    assert "industry_exposure" in risk_metrics

    print("\n风险指标:")
    print(f"  - 1日VaR: ¥{risk_metrics['var_1day']:.2f}")
    print(f"  - 5日VaR: ¥{risk_metrics['var_5day']:.2f}")
    print(f"  - 波动率(年化): {risk_metrics['volatility_annual']:.2f}")
    print(f"  - Beta: {risk_metrics.get('beta', 0):.2f}")
    print(
        f"  - 集中度风险 (Top1): {risk_metrics['concentration_risk']['top1_weight']:.2f}"
    )
    print(f"  - 行业暴露: {len(risk_metrics['industry_exposure'])}个行业")

    print("\n✅ 风险指标计算成功")

    return True


def test_risk_alerts():
    """测试风险预警检查"""
    print("\n" + "=" * 80)
    print("测试 6/10: check_risk_alerts()")
    print("=" * 80)

    biz_source = get_business_source()

    portfolio = [
        {"symbol": "600000", "quantity": 1000, "price": 10.5, "avg_cost": 10.0},
        {"symbol": "000001", "quantity": 2000, "price": 16.0, "avg_cost": 15.0},
    ]

    alerts = biz_source.check_risk_alerts(user_id=1, portfolio=portfolio)

    assert isinstance(alerts, list)

    if alerts:
        print("\n触发的预警:")
        for alert in alerts:
            print(
                f"  - [{alert['severity']}] {alert['alert_name']}: {alert['message']}"
            )
            print(
                f"    触发值: {alert['triggered_value']}, 阈值: {alert['threshold_value']}"
            )
    else:
        print("✅ 没有触发的预警")

    print(f"\n✅ 预警检查完成: {len(alerts)}个触发预警")

    return True


def test_trading_signals():
    """测试交易信号分析"""
    print("\n" + "=" * 80)
    print("测试 7/10: analyze_trading_signals()")
    print("=" * 80)

    biz_source = get_business_source()

    # 首先创建几个策略
    relational = biz_source.rel
    relational.save_strategy_config(
        user_id=1,
        strategy_name="均线策略1",
        strategy_type="ma_cross",
        parameters={"short": 5, "long": 20, "symbols": ["600000", "000001"]},
    )
    relational.save_strategy_config(
        user_id=1,
        strategy_name="MACD策略",
        strategy_type="macd",
        parameters={"fast": 12, "slow": 26, "signal": 9, "symbols": ["600519"]},
    )

    strategies = relational.get_strategy_configs(user_id=1)
    strategy_ids = [s["id"] for s in strategies if s["status"] == "active"]

    signals = biz_source.analyze_trading_signals(user_id=1, strategy_ids=strategy_ids)

    assert isinstance(signals, list)

    buy_signals = [s for s in signals if s["signal_type"] == "buy"]
    sell_signals = [s for s in signals if s["signal_type"] == "sell"]
    hold_signals = [s for s in signals if s["signal_type"] == "hold"]

    print("\n交易信号:")
    print(f"  - 买入信号: {len(buy_signals)}个")
    print(f"  - 卖出信号: {len(sell_signals)}个")
    print(f"  - 持有信号: {len(hold_signals)}个")

    if buy_signals:
        print("\n  买入信号详情:")
        for sig in buy_signals[:3]:  # 显示前3个
            print(
                f"    - {sig['symbol']}: {sig['reason']} (强度: {sig['signal_strength']:.2f})"
            )

    print(f"\n✅ 交易信号分析完成: {len(signals)}个信号")

    return True


def test_portfolio_analysis():
    """测试组合分析"""
    print("\n" + "=" * 80)
    print("测试 8/10: get_portfolio_analysis()")
    print("=" * 80)

    biz_source = get_business_source()

    portfolio = [
        {"symbol": "600000", "quantity": 1000, "price": 10.5, "avg_cost": 10.0},
        {"symbol": "000001", "quantity": 2000, "price": 16.0, "avg_cost": 15.0},
        {"symbol": "600519", "quantity": 100, "price": 1850.0, "avg_cost": 1800.0},
    ]

    analysis = biz_source.get_portfolio_analysis(
        user_id=1, portfolio=portfolio, benchmark="sh000001"
    )

    assert "holdings" in analysis
    assert "total_value" in analysis
    assert "benchmark_comparison" in analysis

    print("\n组合分析:")
    print(f"  - 持仓数: {len(analysis['holdings'])}只")
    print(f"  - 总市值: ¥{analysis['total_value']:,.2f}")
    print(f"  - 总成本: ¥{analysis['total_cost']:,.2f}")
    print(f"  - 总盈亏: ¥{analysis['total_profit']:,.2f}")
    print(f"  - 盈亏率: {analysis['total_return']:.2f}%")

    if analysis["holdings"]:
        print("\n  持仓明细 (前3只):")
        for holding in analysis["holdings"][:3]:
            print(
                f"    - {holding['symbol']}: "
                f"{holding['quantity']}股, "
                f"盈亏 ¥{holding['profit_loss']:,.2f} ({holding['profit_loss_percent']:.2f}%)"
            )

    comp = analysis["benchmark_comparison"]
    print("\n  基准比较:")
    print(f"    - 组合收益: {comp['portfolio_return']:.2f}%")
    print(f"    - 基准收益: {comp['benchmark_return']:.2f}%")
    print(f"    - Alpha: {comp['alpha']:.2f}%")

    print("\n✅ 组合分析完成")

    return True


def test_attribution_analysis():
    """测试归因分析"""
    print("\n" + "=" * 80)
    print("测试 9/10: perform_attribution_analysis()")
    print("=" * 80)

    biz_source = get_business_source()

    portfolio = [
        {"symbol": "600000", "quantity": 1000, "price": 10.5, "avg_cost": 10.0},
        {"symbol": "000001", "quantity": 2000, "price": 16.0, "avg_cost": 15.0},
        {"symbol": "600519", "quantity": 100, "price": 1850.0, "avg_cost": 1800.0},
    ]

    attribution = biz_source.perform_attribution_analysis(
        user_id=1,
        portfolio=portfolio,
        start_date=(datetime.now() - timedelta(days=90)).date(),
        end_date=datetime.now().date(),
    )

    assert "sector_attribution" in attribution
    assert "stock_attribution" in attribution
    assert "total_return" in attribution

    print("\n归因分析:")
    print(f"  - 总收益: {attribution['total_return']:.2f}%")
    print(f"  - 配置效应: {attribution['allocation_effect']:.2f}%")
    print(f"  - 选择效应: {attribution['selection_effect']:.2f}%")

    print("\n  行业归因:")
    for sector_name, contribution in attribution["sector_attribution"].items():
        print(f"    - {sector_name}: 贡献 {contribution:.2f}%")

    print("\n  个股归因 (前5):")
    for stock in attribution["stock_attribution"][:5]:
        print(f"    - {stock['symbol']}: 贡献 {stock['contribution']:.2f}%")

    print("\n✅ 归因分析完成")

    return True


def test_stock_screener():
    """测试选股器"""
    print("\n" + "=" * 80)
    print("测试 10/10: execute_stock_screener()")
    print("=" * 80)

    biz_source = get_business_source()

    criteria = {
        "pe_min": 0,
        "pe_max": 30,
        "pb_min": 0,
        "pb_max": 5,
        "roe_min": 10,
        "market_cap_min": 10,  # 10亿
    }

    results = biz_source.execute_stock_screener(
        criteria=criteria, sort_by="score", limit=10
    )

    assert isinstance(results, list)
    assert len(results) <= 10

    print(f"\n选股结果 (共{len(results)}只):")
    for i, stock in enumerate(results[:5], 1):
        print(f"\n  {i}. {stock['symbol']} {stock['name']}")
        print(f"     - 综合评分: {stock['score']:.2f}")
        print(
            f"     - PE: {stock['pe_ratio']:.2f}, PB: {stock['pb_ratio']:.2f}, ROE: {stock['roe'] * 100:.2f}%"
        )
        print(f"     - 市值: ¥{stock['market_cap'] / 100000000:.2f}亿")

    print(f"\n✅ 选股器执行完成: {len(results)}只股票")

    return True


def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 80)
    print(" MockBusinessDataSource 功能测试")
    print("=" * 80)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    tests = [
        ("仪表盘摘要", test_dashboard_summary),
        ("板块表现", test_sector_performance),
        ("回测执行", test_backtest_execution),
        ("回测结果检索", None),  # 需要前一个测试的ID
        ("风险指标计算", test_risk_metrics),
        ("风险预警检查", test_risk_alerts),
        ("交易信号分析", test_trading_signals),
        ("组合分析", test_portfolio_analysis),
        ("归因分析", test_attribution_analysis),
        ("选股器", test_stock_screener),
    ]

    passed = 0
    failed = 0

    try:
        # 测试1-3
        for name, test_func in tests[:3]:
            try:
                result = test_func()
                if result:
                    passed += 1
            except Exception as e:
                print(f"❌ {name}测试失败: {str(e)}")
                failed += 1
                raise

        # 测试4需要回测ID
        try:
            backtest_id = result  # 从测试3获取
            if test_backtest_results(backtest_id):
                passed += 1
        except Exception as e:
            print(f"❌ 回测结果检索测试失败: {str(e)}")
            failed += 1
            raise

        # 测试5-10
        for name, test_func in tests[4:]:
            try:
                if test_func():
                    passed += 1
            except Exception as e:
                print(f"❌ {name}测试失败: {str(e)}")
                failed += 1
                raise

        # 总结
        print("\n" + "=" * 80)
        print(" 测试总结")
        print("=" * 80)
        print(f"✅ 通过: {passed}/10")
        print(f"❌ 失败: {failed}/10")
        print(f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        if failed == 0:
            print("\n🎉 所有测试通过！MockBusinessDataSource功能完整！")
            return True
        else:
            print(f"\n⚠️  有{failed}个测试失败")
            return False

    except Exception as e:
        print("\n" + "=" * 80)
        print(f"❌ 测试异常终止: {str(e)}")
        print("=" * 80)
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
