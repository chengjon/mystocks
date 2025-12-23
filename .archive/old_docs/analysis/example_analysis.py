"""
Analysis Layer Example - Demonstrates backtest analysis and reporting

Shows how to use PerformanceMetrics and BacktestReport with backtest results.

Author: JohnC & Claude
Version: 3.1.0 (Simplified MVP)
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from analysis import PerformanceMetrics, BacktestReport


def generate_mock_backtest_results():
    """Generate mock backtest results for demonstration"""
    # Generate 100 trading days
    n_days = 100
    dates = pd.date_range("2024-01-01", periods=n_days, freq="D")

    # Simulate portfolio values with some growth and volatility
    np.random.seed(42)
    returns = np.random.randn(n_days) * 0.02  # 2% daily volatility
    returns[0] = 0  # No return on first day

    portfolio_values = 1000000 * (1 + returns).cumprod()

    # Create daily results DataFrame
    daily_results = pd.DataFrame(
        {
            "date": dates,
            "portfolio_value": portfolio_values,
            "returns": returns,
            "cash": portfolio_values * 0.3,  # 30% cash
            "positions": [{"stock1": 100, "stock2": 200}] * n_days,
        }
    )

    # Generate mock trades
    trades = []
    for i in range(10):
        # Buy trade
        trades.append(
            {
                "timestamp": dates[i * 10],
                "symbol": f"stock{i % 3}",
                "direction": "buy",
                "amount": 100,
                "price": 10.0 + i,
                "stock_value": (10.0 + i) * 100,
                "commission": 5.0,
                "stamp_tax": 0.0,
                "total_cost": (10.0 + i) * 100 + 5.0,
            }
        )

        # Sell trade
        if i > 0:
            profit = np.random.randn() * 100
            sell_price = 10.0 + i + profit / 100
            trades.append(
                {
                    "timestamp": dates[i * 10 + 5],
                    "symbol": f"stock{i % 3}",
                    "direction": "sell",
                    "amount": 100,
                    "price": sell_price,
                    "stock_value": sell_price * 100,
                    "commission": 5.0,
                    "stamp_tax": sell_price * 100 * 0.001,
                    "total_revenue": sell_price * 100 - 5.0 - sell_price * 100 * 0.001,
                }
            )

    # Calculate basic metrics
    initial_value = daily_results["portfolio_value"].iloc[0]
    final_value = daily_results["portfolio_value"].iloc[-1]
    total_return = (final_value - initial_value) / initial_value

    # Calculate cost summary
    total_commission = sum(t.get("commission", 0) for t in trades)
    total_stamp_tax = sum(t.get("stamp_tax", 0) for t in trades)

    return {
        "daily_results": daily_results,
        "trades": trades,
        "metrics": {
            "total_return": total_return,
            "final_value": final_value,
            "total_cost": total_commission + total_stamp_tax,
            "trade_count": len(trades),
        },
        "cost_summary": {
            "total_commission": total_commission,
            "total_stamp_tax": total_stamp_tax,
            "total_cost": total_commission + total_stamp_tax,
            "trade_count": len(trades),
            "avg_cost_per_trade": (total_commission + total_stamp_tax) / len(trades),
        },
    }


def test_performance_metrics():
    """Test PerformanceMetrics module"""
    print("=" * 70)
    print("Test 1: Performance Metrics")
    print("=" * 70)

    # Generate mock data
    results = generate_mock_backtest_results()
    daily_results = results["daily_results"]
    trades = results["trades"]

    # Create PerformanceMetrics instance
    print("\n1. Creating PerformanceMetrics instance...")
    pm = PerformanceMetrics(daily_results, risk_free_rate=0.03)
    print("   ✅ Instance created")

    # Calculate individual metrics
    print("\n2. Calculating individual metrics...")
    print(f"   Total Return: {pm.total_return() * 100:.2f}%")
    print(f"   Annualized Return: {pm.annualized_return() * 100:.2f}%")
    print(f"   Volatility: {pm.volatility() * 100:.2f}%")
    print(f"   Sharpe Ratio: {pm.sharpe_ratio():.3f}")
    print(f"   Sortino Ratio: {pm.sortino_ratio():.3f}")
    print(f"   Max Drawdown: {pm.max_drawdown() * 100:.2f}%")
    print(f"   Calmar Ratio: {pm.calmar_ratio():.3f}")

    # Calculate all metrics at once
    print("\n3. Calculating all metrics with trades...")
    all_metrics = pm.calculate_all(trades)

    print("\n   All Metrics:")
    for key, value in all_metrics.items():
        if isinstance(value, float):
            if "ratio" in key or "rate" in key:
                print(f"   {key}: {value:.3f}")
            else:
                print(
                    f"   {key}: {value * 100:.2f}%"
                    if value < 10
                    else f"   {key}: {value:,.2f}"
                )

    print("\n✅ Performance Metrics test complete!")


def test_backtest_report():
    """Test BacktestReport module"""
    print("\n" + "=" * 70)
    print("Test 2: Backtest Report")
    print("=" * 70)

    # Generate mock data
    results = generate_mock_backtest_results()

    # Create BacktestReport instance
    print("\n1. Creating BacktestReport instance...")
    report = BacktestReport(results)
    print("   ✅ Instance created")

    # Generate and print full report
    print("\n2. Generating full report...\n")
    report.print_summary()

    # Save to file
    print("\n3. Saving report to file...")
    report_path = "analysis_report_test.txt"
    report.save_to_file(report_path)

    # Export to dict
    print("\n4. Exporting report data as dictionary...")
    report_dict = report.to_dict()
    print(f"   Report contains {len(report_dict)} sections")
    print(f"   Trading days: {report_dict['trading_days']}")
    print(f"   Total trades: {report_dict['trade_count']}")

    print("\n✅ Backtest Report test complete!")


def test_integrated_workflow():
    """Test integrated workflow: Backtest → Analysis → Report"""
    print("\n" + "=" * 70)
    print("Test 3: Integrated Workflow")
    print("=" * 70)

    print("\n1. Simulating backtest execution...")
    results = generate_mock_backtest_results()
    print("   ✅ Backtest complete")

    print("\n2. Calculating performance metrics...")
    pm = PerformanceMetrics(results["daily_results"])
    metrics = pm.calculate_all(results["trades"])
    print(f"   ✅ Metrics calculated: {len(metrics)} metrics")

    print("\n3. Generating backtest report...")
    report = BacktestReport(results)
    print("   ✅ Report generated")

    print("\n4. Key Results:")
    print(f"   Total Return: {metrics['total_return'] * 100:.2f}%")
    print(f"   Sharpe Ratio: {metrics['sharpe_ratio']:.3f}")
    print(f"   Max Drawdown: {metrics['max_drawdown'] * 100:.2f}%")
    print(f"   Total Cost: {results['cost_summary']['total_cost']:,.2f}")

    print("\n✅ Integrated workflow test complete!")


if __name__ == "__main__":
    print("=" * 70)
    print("MyStocks Analysis Layer - Examples")
    print("=" * 70)

    try:
        test_performance_metrics()
    except Exception as e:
        print(f"\n❌ Performance Metrics test failed: {e}")
        import traceback

        traceback.print_exc()

    try:
        test_backtest_report()
    except Exception as e:
        print(f"\n❌ Backtest Report test failed: {e}")
        import traceback

        traceback.print_exc()

    try:
        test_integrated_workflow()
    except Exception as e:
        print(f"\n❌ Integrated workflow test failed: {e}")
        import traceback

        traceback.print_exc()

    print("\n" + "=" * 70)
    print("✅ All tests complete!")
    print("=" * 70)
