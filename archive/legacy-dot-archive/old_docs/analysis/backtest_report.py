"""
Backtest Report - Generate formatted backtest reports

Provides formatted output of backtest results including:
- Summary statistics
- Performance metrics
- Trade analysis
- Visual tables

Author: JohnC & Claude
Version: 3.1.0 (Simplified MVP)
"""

from typing import Dict, Any
import pandas as pd
from .performance_metrics import PerformanceMetrics


class BacktestReport:
    """
    Backtest Report Generator (Simplified)

    Generate formatted reports from backtest results.

    Example:
        >>> report = BacktestReport(results)
        >>> report.print_summary()
        >>> report.save_to_file('backtest_report.txt')
    """

    def __init__(self, backtest_results: Dict[str, Any]):
        """
        Initialize report generator

        Args:
            backtest_results: Dict containing:
                - daily_results: DataFrame
                - trades: List[Dict]
                - metrics: Dict
                - cost_summary: Dict
        """
        self.results = backtest_results
        self.daily_results = backtest_results.get("daily_results", pd.DataFrame())
        self.trades = backtest_results.get("trades", [])
        self.basic_metrics = backtest_results.get("metrics", {})
        self.cost_summary = backtest_results.get("cost_summary", {})

        # Calculate advanced metrics
        if not self.daily_results.empty:
            pm = PerformanceMetrics(self.daily_results)
            self.advanced_metrics = pm.calculate_all(self.trades)
        else:
            self.advanced_metrics = {}

    def generate_summary_section(self) -> str:
        """Generate summary section"""
        lines = []
        lines.append("=" * 70)
        lines.append("BACKTEST SUMMARY")
        lines.append("=" * 70)

        if not self.daily_results.empty:
            start_date = self.daily_results["date"].iloc[0]
            end_date = self.daily_results["date"].iloc[-1]
            lines.append(f"Period: {start_date} to {end_date}")
            lines.append(f"Trading Days: {len(self.daily_results)}")

        if self.basic_metrics:
            lines.append(
                f"\nInitial Portfolio: {self.basic_metrics.get('final_value', 0) / (1 + self.basic_metrics.get('total_return', 0)):,.2f}"
            )
            lines.append(
                f"Final Portfolio: {self.basic_metrics.get('final_value', 0):,.2f}"
            )
            lines.append(
                f"Total Return: {self.basic_metrics.get('total_return', 0) * 100:.2f}%"
            )

        return "\n".join(lines)

    def generate_performance_section(self) -> str:
        """Generate performance metrics section"""
        lines = []
        lines.append("\n" + "=" * 70)
        lines.append("PERFORMANCE METRICS")
        lines.append("=" * 70)

        if self.advanced_metrics:
            lines.append("\nRisk-Adjusted Returns:")
            lines.append(
                f"  Sharpe Ratio: {self.advanced_metrics.get('sharpe_ratio', 0):.3f}"
            )
            lines.append(
                f"  Sortino Ratio: {self.advanced_metrics.get('sortino_ratio', 0):.3f}"
            )
            lines.append(
                f"  Calmar Ratio: {self.advanced_metrics.get('calmar_ratio', 0):.3f}"
            )

            lines.append("\nReturn Metrics:")
            lines.append(
                f"  Annualized Return: {self.advanced_metrics.get('annualized_return', 0) * 100:.2f}%"
            )
            lines.append(
                f"  Volatility (Annual): {self.advanced_metrics.get('volatility', 0) * 100:.2f}%"
            )

            lines.append("\nRisk Metrics:")
            lines.append(
                f"  Max Drawdown: {self.advanced_metrics.get('max_drawdown', 0) * 100:.2f}%"
            )

            if "win_rate" in self.advanced_metrics:
                lines.append("\nTrade Statistics:")
                lines.append(
                    f"  Win Rate: {self.advanced_metrics.get('win_rate', 0) * 100:.2f}%"
                )
                lines.append(
                    f"  Profit Factor: {self.advanced_metrics.get('profit_factor', 0):.3f}"
                )

        return "\n".join(lines)

    def generate_cost_section(self) -> str:
        """Generate cost analysis section"""
        lines = []
        lines.append("\n" + "=" * 70)
        lines.append("COST ANALYSIS")
        lines.append("=" * 70)

        if self.cost_summary:
            lines.append(
                f"\nTotal Trading Cost: {self.cost_summary.get('total_cost', 0):,.2f}"
            )
            lines.append(
                f"  Commission: {self.cost_summary.get('total_commission', 0):,.2f}"
            )
            lines.append(
                f"  Stamp Tax: {self.cost_summary.get('total_stamp_tax', 0):,.2f}"
            )
            lines.append(f"\nTotal Trades: {self.cost_summary.get('trade_count', 0)}")
            lines.append(
                f"Average Cost per Trade: {self.cost_summary.get('avg_cost_per_trade', 0):,.2f}"
            )

            # Calculate cost as % of returns
            if self.basic_metrics.get("total_return", 0) != 0:
                init_value = self.basic_metrics.get("final_value", 0) / (
                    1 + self.basic_metrics.get("total_return", 0)
                )
                cost_pct = (self.cost_summary.get("total_cost", 0) / init_value) * 100
                lines.append(f"\nCost as % of Initial Capital: {cost_pct:.2f}%")

        return "\n".join(lines)

    def generate_trade_section(self, max_trades: int = 10) -> str:
        """Generate trade history section"""
        lines = []
        lines.append("\n" + "=" * 70)
        lines.append("TRADE HISTORY (Recent)")
        lines.append("=" * 70)

        if self.trades:
            # Show last N trades
            recent_trades = self.trades[-max_trades:]

            lines.append(
                f"\nShowing last {len(recent_trades)} of {len(self.trades)} trades:\n"
            )

            # Create DataFrame for nice formatting
            df_trades = pd.DataFrame(recent_trades)
            if not df_trades.empty:
                # Select key columns
                cols = ["timestamp", "symbol", "direction", "amount", "price"]
                display_cols = [c for c in cols if c in df_trades.columns]

                if display_cols:
                    lines.append(df_trades[display_cols].to_string(index=False))
        else:
            lines.append("\nNo trades executed.")

        return "\n".join(lines)

    def generate_full_report(self) -> str:
        """Generate complete report"""
        sections = [
            self.generate_summary_section(),
            self.generate_performance_section(),
            self.generate_cost_section(),
            self.generate_trade_section(),
        ]

        report = "\n".join(sections)
        report += "\n\n" + "=" * 70
        report += "\nEND OF REPORT"
        report += "\n" + "=" * 70 + "\n"

        return report

    def print_summary(self):
        """Print report to console"""
        print(self.generate_full_report())

    def save_to_file(self, file_path: str):
        """Save report to file"""
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(self.generate_full_report())

        print(f"✅ Report saved to: {file_path}")

    def to_dict(self) -> Dict[str, Any]:
        """Export report data as dictionary"""
        return {
            "basic_metrics": self.basic_metrics,
            "advanced_metrics": self.advanced_metrics,
            "cost_summary": self.cost_summary,
            "trade_count": len(self.trades),
            "trading_days": len(self.daily_results),
        }
