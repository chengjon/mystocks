"""
Performance Metrics - Calculate backtest performance metrics

Provides standard quantitative finance metrics:
- Total Return, Annualized Return
- Sharpe Ratio, Sortino Ratio
- Maximum Drawdown, Calmar Ratio
- Win Rate, Profit Factor
- Volatility (Annualized)

Author: JohnC & Claude
Version: 3.1.0 (Simplified MVP)
"""

from typing import Dict, Any
import pandas as pd
import numpy as np


class PerformanceMetrics:
    """
    Performance Metrics Calculator (Simplified)

    Calculate standard quantitative trading metrics from backtest results.

    Example:
        >>> metrics = PerformanceMetrics(daily_results)
        >>> stats = metrics.calculate_all()
        >>> print(f"Sharpe Ratio: {stats['sharpe_ratio']:.2f}")
    """

    def __init__(self, daily_results: pd.DataFrame, risk_free_rate: float = 0.03):
        """
        Initialize metrics calculator

        Args:
            daily_results: DataFrame with columns ['date', 'portfolio_value', 'returns']
            risk_free_rate: Annual risk-free rate (default 3%)
        """
        self.daily_results = daily_results.copy()
        self.risk_free_rate = risk_free_rate

        # Calculate daily returns if not present
        if 'returns' not in self.daily_results.columns:
            self.daily_results['returns'] = (
                self.daily_results['portfolio_value'].pct_change()
            )

    def total_return(self) -> float:
        """Calculate total return"""
        initial_value = self.daily_results['portfolio_value'].iloc[0]
        final_value = self.daily_results['portfolio_value'].iloc[-1]
        return (final_value - initial_value) / initial_value

    def annualized_return(self, trading_days_per_year: int = 252) -> float:
        """Calculate annualized return"""
        total_ret = self.total_return()
        n_days = len(self.daily_results)
        years = n_days / trading_days_per_year
        return (1 + total_ret) ** (1 / years) - 1 if years > 0 else 0

    def volatility(self, trading_days_per_year: int = 252) -> float:
        """Calculate annualized volatility (standard deviation of returns)"""
        daily_vol = self.daily_results['returns'].std()
        return daily_vol * np.sqrt(trading_days_per_year)

    def sharpe_ratio(self, trading_days_per_year: int = 252) -> float:
        """
        Calculate Sharpe Ratio

        Sharpe = (Return - RiskFreeRate) / Volatility
        """
        ann_return = self.annualized_return(trading_days_per_year)
        ann_vol = self.volatility(trading_days_per_year)

        if ann_vol == 0:
            return 0.0

        return (ann_return - self.risk_free_rate) / ann_vol

    def sortino_ratio(self, trading_days_per_year: int = 252) -> float:
        """
        Calculate Sortino Ratio

        Sortino = (Return - RiskFreeRate) / DownsideDeviation
        Only considers downside volatility
        """
        ann_return = self.annualized_return(trading_days_per_year)

        # Calculate downside deviation
        negative_returns = self.daily_results['returns'][
            self.daily_results['returns'] < 0
        ]

        if len(negative_returns) == 0:
            return float('inf')

        downside_std = negative_returns.std()
        downside_vol = downside_std * np.sqrt(trading_days_per_year)

        if downside_vol == 0:
            return 0.0

        return (ann_return - self.risk_free_rate) / downside_vol

    def max_drawdown(self) -> float:
        """
        Calculate maximum drawdown

        Max Drawdown = max((Peak - Trough) / Peak)
        """
        portfolio_values = self.daily_results['portfolio_value']

        # Calculate running maximum
        running_max = portfolio_values.expanding().max()

        # Calculate drawdown at each point
        drawdowns = (portfolio_values - running_max) / running_max

        return abs(drawdowns.min())

    def calmar_ratio(self, trading_days_per_year: int = 252) -> float:
        """
        Calculate Calmar Ratio

        Calmar = AnnualizedReturn / MaxDrawdown
        """
        ann_return = self.annualized_return(trading_days_per_year)
        max_dd = self.max_drawdown()

        if max_dd == 0:
            return float('inf')

        return ann_return / max_dd

    def win_rate(self, trades: list) -> float:
        """
        Calculate win rate from trade history

        Win Rate = Winning Trades / Total Trades

        Args:
            trades: List of trade dicts with 'direction' and 'price' or profit info
        """
        if not trades or len(trades) == 0:
            return 0.0

        # Simplified: count sell trades with profit
        # Assumes trades list contains profit information
        winning_trades = sum(
            1 for trade in trades
            if trade.get('direction') == 'sell' and
               trade.get('total_revenue', 0) > trade.get('stock_value', 0)
        )

        total_trades = len([t for t in trades if t.get('direction') == 'sell'])

        return winning_trades / total_trades if total_trades > 0 else 0.0

    def profit_factor(self, trades: list) -> float:
        """
        Calculate profit factor

        Profit Factor = Gross Profit / Gross Loss

        Args:
            trades: List of trade dicts
        """
        if not trades or len(trades) == 0:
            return 0.0

        gross_profit = sum(
            trade.get('total_revenue', 0) - trade.get('stock_value', 0)
            for trade in trades
            if trade.get('direction') == 'sell' and
               trade.get('total_revenue', 0) > trade.get('stock_value', 0)
        )

        gross_loss = abs(sum(
            trade.get('total_revenue', 0) - trade.get('stock_value', 0)
            for trade in trades
            if trade.get('direction') == 'sell' and
               trade.get('total_revenue', 0) < trade.get('stock_value', 0)
        ))

        if gross_loss == 0:
            return float('inf') if gross_profit > 0 else 0.0

        return gross_profit / gross_loss

    def calculate_all(self, trades: list = None, trading_days_per_year: int = 252) -> Dict[str, Any]:
        """
        Calculate all metrics

        Args:
            trades: Optional trade history for win rate / profit factor
            trading_days_per_year: Trading days per year (default 252)

        Returns:
            Dict of all metrics
        """
        metrics = {
            'total_return': self.total_return(),
            'annualized_return': self.annualized_return(trading_days_per_year),
            'volatility': self.volatility(trading_days_per_year),
            'sharpe_ratio': self.sharpe_ratio(trading_days_per_year),
            'sortino_ratio': self.sortino_ratio(trading_days_per_year),
            'max_drawdown': self.max_drawdown(),
            'calmar_ratio': self.calmar_ratio(trading_days_per_year),
        }

        # Add trade-based metrics if trades provided
        if trades:
            metrics['win_rate'] = self.win_rate(trades)
            metrics['profit_factor'] = self.profit_factor(trades)

        return metrics
