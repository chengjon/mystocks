"""
Performance Metrics Calculator

计算回测性能指标，包括夏普比率、最大回撤、收益率等
"""

import numpy as np
from typing import List, Dict, Any, Optional
from decimal import Decimal
from datetime import datetime


class PerformanceMetrics:
    """
    性能指标计算器

    计算各种回测性能指标
    """

    def __init__(self, risk_free_rate: float = 0.03):
        """
        初始化性能指标计算器

        Args:
            risk_free_rate: 无风险利率（年化），默认3%
        """
        self.risk_free_rate = risk_free_rate

    def calculate_all_metrics(
        self,
        equity_curve: List[Dict[str, Any]],
        trades: List[Dict[str, Any]],
        initial_capital: Decimal,
        benchmark_curve: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        计算所有性能指标

        Args:
            equity_curve: 资金曲线 [{'date': datetime, 'equity': Decimal, 'drawdown': Decimal}]
            trades: 交易记录列表
            initial_capital: 初始资金
            benchmark_curve: 基准曲线（可选）

        Returns:
            包含所有性能指标的字典
        """
        if not equity_curve or len(equity_curve) == 0:
            return self._empty_metrics()

        # 提取数据
        equity_values = [float(point["equity"]) for point in equity_curve]
        dates = [point["date"] for point in equity_curve]

        # 计算基础指标
        total_return = self._calculate_total_return(equity_values, float(initial_capital))
        annualized_return = self._calculate_annualized_return(equity_values, dates, float(initial_capital))

        # 计算风险指标
        volatility = self._calculate_volatility(equity_values, dates)
        sharpe_ratio = self._calculate_sharpe_ratio(annualized_return, volatility)
        max_drawdown = self._calculate_max_drawdown(equity_curve)
        max_drawdown_duration = self._calculate_max_drawdown_duration(equity_curve)

        # 计算交易指标
        trade_metrics = self._calculate_trade_metrics(trades)

        # 计算其他指标
        calmar_ratio = self._calculate_calmar_ratio(annualized_return, max_drawdown)
        sortino_ratio = self._calculate_sortino_ratio(equity_values, dates)

        # 如果有基准，计算相对指标
        alpha = None
        beta = None
        information_ratio = None
        if benchmark_curve and len(benchmark_curve) > 0:
            benchmark_values = [float(point["equity"]) for point in benchmark_curve]
            alpha, beta = self._calculate_alpha_beta(equity_values, benchmark_values, dates)
            information_ratio = self._calculate_information_ratio(equity_values, benchmark_values)

        return {
            # 收益指标
            "total_return": round(total_return, 4),
            "annualized_return": round(annualized_return, 4),
            "cumulative_return": round(total_return, 4),
            # 风险指标
            "volatility": round(volatility, 4),
            "sharpe_ratio": round(sharpe_ratio, 4),
            "sortino_ratio": round(sortino_ratio, 4),
            "max_drawdown": round(max_drawdown, 4),
            "max_drawdown_duration": max_drawdown_duration,
            # 风险调整收益
            "calmar_ratio": round(calmar_ratio, 4) if calmar_ratio else None,
            # 交易指标
            **trade_metrics,
            # 相对指标（vs基准）
            "alpha": round(alpha, 4) if alpha is not None else None,
            "beta": round(beta, 4) if beta is not None else None,
            "information_ratio": round(information_ratio, 4) if information_ratio else None,
            # 其他信息
            "total_trades": len(trades),
            "trading_days": len(equity_curve),
        }

    def _empty_metrics(self) -> Dict[str, Any]:
        """返回空的指标字典"""
        return {
            "total_return": 0.0,
            "annualized_return": 0.0,
            "cumulative_return": 0.0,
            "volatility": 0.0,
            "sharpe_ratio": 0.0,
            "sortino_ratio": 0.0,
            "max_drawdown": 0.0,
            "max_drawdown_duration": 0,
            "calmar_ratio": None,
            "win_rate": 0.0,
            "profit_factor": 0.0,
            "avg_win": 0.0,
            "avg_loss": 0.0,
            "avg_win_loss_ratio": 0.0,
            "alpha": None,
            "beta": None,
            "information_ratio": None,
            "total_trades": 0,
            "trading_days": 0,
        }

    def _calculate_total_return(self, equity_values: List[float], initial_capital: float) -> float:
        """计算总收益率"""
        if initial_capital == 0:
            return 0.0
        final_equity = equity_values[-1]
        return (final_equity - initial_capital) / initial_capital

    def _calculate_annualized_return(
        self, equity_values: List[float], dates: List[datetime], initial_capital: float
    ) -> float:
        """计算年化收益率"""
        if len(dates) < 2 or initial_capital == 0:
            return 0.0

        total_return = self._calculate_total_return(equity_values, initial_capital)
        days = (dates[-1] - dates[0]).days

        if days == 0:
            return 0.0

        years = days / 365.25
        annualized = (1 + total_return) ** (1 / years) - 1
        return annualized

    def _calculate_volatility(self, equity_values: List[float], dates: List[datetime]) -> float:
        """计算年化波动率"""
        if len(equity_values) < 2:
            return 0.0

        # 计算日收益率
        returns = []
        for i in range(1, len(equity_values)):
            if equity_values[i - 1] != 0:
                daily_return = (equity_values[i] - equity_values[i - 1]) / equity_values[i - 1]
                returns.append(daily_return)

        if len(returns) == 0:
            return 0.0

        # 年化波动率
        daily_volatility = np.std(returns, ddof=1)
        annualized_volatility = daily_volatility * np.sqrt(252)  # 假设252个交易日
        return float(annualized_volatility)

    def _calculate_sharpe_ratio(self, annualized_return: float, volatility: float) -> float:
        """计算夏普比率"""
        if volatility == 0:
            return 0.0
        return (annualized_return - self.risk_free_rate) / volatility

    def _calculate_max_drawdown(self, equity_curve: List[Dict[str, Any]]) -> float:
        """计算最大回撤"""
        if not equity_curve:
            return 0.0

        equity_values = [float(point["equity"]) for point in equity_curve]
        peak = equity_values[0]
        max_dd = 0.0

        for equity in equity_values:
            if equity > peak:
                peak = equity
            dd = (peak - equity) / peak if peak != 0 else 0
            max_dd = max(max_dd, dd)

        return max_dd

    def _calculate_max_drawdown_duration(self, equity_curve: List[Dict[str, Any]]) -> int:
        """计算最大回撤持续时间（天数）"""
        if not equity_curve:
            return 0

        equity_values = [float(point["equity"]) for point in equity_curve]
        peak_idx = 0
        max_duration = 0
        current_duration = 0

        for i, equity in enumerate(equity_values):
            if equity >= equity_values[peak_idx]:
                # 新高点
                peak_idx = i
                max_duration = max(max_duration, current_duration)
                current_duration = 0
            else:
                # 回撤中
                current_duration = i - peak_idx

        return max(max_duration, current_duration)

    def _calculate_calmar_ratio(self, annualized_return: float, max_drawdown: float) -> Optional[float]:
        """计算Calmar比率"""
        if max_drawdown == 0:
            return None
        return annualized_return / max_drawdown

    def _calculate_sortino_ratio(self, equity_values: List[float], dates: List[datetime]) -> float:
        """计算Sortino比率（只考虑下行波动）"""
        if len(equity_values) < 2:
            return 0.0

        # 计算日收益率
        returns = []
        for i in range(1, len(equity_values)):
            if equity_values[i - 1] != 0:
                daily_return = (equity_values[i] - equity_values[i - 1]) / equity_values[i - 1]
                returns.append(daily_return)

        if len(returns) == 0:
            return 0.0

        # 计算平均收益
        avg_return = np.mean(returns)

        # 下行偏差（只考虑负收益）
        downside_returns = [r for r in returns if r < 0]
        if len(downside_returns) == 0:
            return 0.0

        downside_deviation = np.std(downside_returns, ddof=1) * np.sqrt(252)

        if downside_deviation == 0:
            return 0.0

        # 年化收益
        annualized_avg_return = avg_return * 252

        return (annualized_avg_return - self.risk_free_rate) / downside_deviation

    def _calculate_trade_metrics(self, trades: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算交易相关指标"""
        if not trades:
            return {
                "win_rate": 0.0,
                "profit_factor": 0.0,
                "avg_win": 0.0,
                "avg_loss": 0.0,
                "avg_win_loss_ratio": 0.0,
            }

        # 提取盈亏
        pnls = [float(trade.get("profit_loss", 0)) for trade in trades if trade.get("profit_loss")]

        if not pnls:
            return {
                "win_rate": 0.0,
                "profit_factor": 0.0,
                "avg_win": 0.0,
                "avg_loss": 0.0,
                "avg_win_loss_ratio": 0.0,
            }

        wins = [pnl for pnl in pnls if pnl > 0]
        losses = [abs(pnl) for pnl in pnls if pnl < 0]

        win_rate = len(wins) / len(pnls) if pnls else 0.0
        avg_win = np.mean(wins) if wins else 0.0
        avg_loss = np.mean(losses) if losses else 0.0

        total_wins = sum(wins)
        total_losses = sum(losses)
        profit_factor = total_wins / total_losses if total_losses != 0 else 0.0

        avg_win_loss_ratio = avg_win / avg_loss if avg_loss != 0 else 0.0

        return {
            "win_rate": round(win_rate, 4),
            "profit_factor": round(profit_factor, 4),
            "avg_win": round(avg_win, 2),
            "avg_loss": round(avg_loss, 2),
            "avg_win_loss_ratio": round(avg_win_loss_ratio, 4),
        }

    def _calculate_alpha_beta(
        self,
        portfolio_values: List[float],
        benchmark_values: List[float],
        dates: List[datetime],
    ) -> tuple[Optional[float], Optional[float]]:
        """计算Alpha和Beta（CAPM模型）"""
        if len(portfolio_values) != len(benchmark_values) or len(portfolio_values) < 2:
            return None, None

        # 计算收益率
        portfolio_returns = []
        benchmark_returns = []

        for i in range(1, len(portfolio_values)):
            if portfolio_values[i - 1] != 0 and benchmark_values[i - 1] != 0:
                p_ret = (portfolio_values[i] - portfolio_values[i - 1]) / portfolio_values[i - 1]
                b_ret = (benchmark_values[i] - benchmark_values[i - 1]) / benchmark_values[i - 1]
                portfolio_returns.append(p_ret)
                benchmark_returns.append(b_ret)

        if len(portfolio_returns) < 2:
            return None, None

        # 计算Beta（协方差 / 方差）
        covariance = np.cov(portfolio_returns, benchmark_returns)[0][1]
        variance = np.var(benchmark_returns, ddof=1)

        if variance == 0:
            return None, None

        beta = covariance / variance

        # 计算Alpha（年化）
        avg_portfolio_return = np.mean(portfolio_returns) * 252
        avg_benchmark_return = np.mean(benchmark_returns) * 252
        alpha = avg_portfolio_return - (self.risk_free_rate + beta * (avg_benchmark_return - self.risk_free_rate))

        return alpha, beta

    def _calculate_information_ratio(
        self, portfolio_values: List[float], benchmark_values: List[float]
    ) -> Optional[float]:
        """计算信息比率"""
        if len(portfolio_values) != len(benchmark_values) or len(portfolio_values) < 2:
            return None

        # 计算超额收益
        excess_returns = []
        for i in range(1, len(portfolio_values)):
            if portfolio_values[i - 1] != 0 and benchmark_values[i - 1] != 0:
                p_ret = (portfolio_values[i] - portfolio_values[i - 1]) / portfolio_values[i - 1]
                b_ret = (benchmark_values[i] - benchmark_values[i - 1]) / benchmark_values[i - 1]
                excess_returns.append(p_ret - b_ret)

        if len(excess_returns) < 2:
            return None

        # 年化超额收益和跟踪误差
        avg_excess_return = np.mean(excess_returns) * 252
        tracking_error = np.std(excess_returns, ddof=1) * np.sqrt(252)

        if tracking_error == 0:
            return None

        return avg_excess_return / tracking_error
