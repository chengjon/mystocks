"""
性能指标计算模块 (Performance Metrics)

功能说明:
- 计算回测的各种性能指标
- 支持年化收益率、夏普比率、索提诺比率等
- 提供可视化的性能报告

作者: MyStocks量化交易团队
创建时间: 2025-10-18
版本: 1.0.0
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
from datetime import datetime, timedelta
import logging


class PerformanceMetrics:
    """
    性能指标计算器

    提供常用的回测性能指标计算方法
    """

    def __init__(self, risk_free_rate: float = 0.03):
        """
        初始化性能指标计算器

        参数:
            risk_free_rate: 无风险利率（年化）默认3%
        """
        self.risk_free_rate = risk_free_rate

        # 日志配置
        self.logger = logging.getLogger(f"{__name__}.PerformanceMetrics")
        self.logger.setLevel(logging.INFO)

    def calculate_all_metrics(
        self,
        equity_curve: pd.DataFrame,
        daily_returns: pd.Series,
        trades: list,
        initial_capital: float,
        benchmark_returns: Optional[pd.Series] = None,
    ) -> Dict:
        """
        计算所有性能指标

        参数:
            equity_curve: 权益曲线DataFrame
            daily_returns: 每日收益率Series
            trades: 交易记录列表
            initial_capital: 初始资金
            benchmark_returns: 基准收益率（可选）

        返回:
            dict: 所有性能指标
        """
        metrics = {}

        # 基础指标
        metrics["initial_capital"] = initial_capital
        metrics["final_capital"] = equity_curve["equity"].iloc[-1]
        metrics["total_return"] = self.total_return(equity_curve, initial_capital)
        metrics["annualized_return"] = self.annualized_return(daily_returns)

        # 风险调整指标
        metrics["sharpe_ratio"] = self.sharpe_ratio(daily_returns)
        metrics["sortino_ratio"] = self.sortino_ratio(daily_returns)
        metrics["calmar_ratio"] = self.calmar_ratio(daily_returns, equity_curve)

        # 回撤指标
        metrics["max_drawdown"] = self.max_drawdown(equity_curve)
        metrics["max_drawdown_duration"] = self.max_drawdown_duration(equity_curve)

        # 交易统计
        if trades:
            metrics.update(self._trade_statistics(trades))

        # 基准比较（如果提供）
        if benchmark_returns is not None:
            metrics["alpha"] = self.alpha(daily_returns, benchmark_returns)
            metrics["beta"] = self.beta(daily_returns, benchmark_returns)
            metrics["information_ratio"] = self.information_ratio(
                daily_returns, benchmark_returns
            )

        # 其他指标
        metrics["volatility"] = self.volatility(daily_returns)
        metrics["var_95"] = self.value_at_risk(daily_returns, 0.95)
        metrics["cvar_95"] = self.conditional_var(daily_returns, 0.95)

        return metrics

    def total_return(self, equity_curve: pd.DataFrame, initial_capital: float) -> float:
        """
        总收益率

        参数:
            equity_curve: 权益曲线
            initial_capital: 初始资金

        返回:
            float: 总收益率
        """
        final_value = equity_curve["equity"].iloc[-1]
        return (final_value - initial_capital) / initial_capital

    def annualized_return(self, daily_returns: pd.Series) -> float:
        """
        年化收益率

        参数:
            daily_returns: 每日收益率

        返回:
            float: 年化收益率
        """
        # 计算累积收益率
        total_return = (1 + daily_returns).prod() - 1

        # 计算交易日数
        n_days = len(daily_returns)

        # 假设一年252个交易日
        n_years = n_days / 252.0

        if n_years > 0:
            annualized = (1 + total_return) ** (1 / n_years) - 1
        else:
            annualized = 0.0

        return annualized

    def sharpe_ratio(self, daily_returns: pd.Series) -> float:
        """
        夏普比率 (Sharpe Ratio)

        衡量单位风险的超额收益

        参数:
            daily_returns: 每日收益率

        返回:
            float: 夏普比率
        """
        # 计算超额收益
        excess_returns = daily_returns - self.risk_free_rate / 252.0

        # 如果标准差为0，返回0
        if excess_returns.std() == 0:
            return 0.0

        # 年化夏普比率
        sharpe = excess_returns.mean() / excess_returns.std() * np.sqrt(252)

        return sharpe

    def sortino_ratio(self, daily_returns: pd.Series) -> float:
        """
        索提诺比率 (Sortino Ratio)

        仅考虑下行风险的夏普比率

        参数:
            daily_returns: 每日收益率

        返回:
            float: 索提诺比率
        """
        # 计算超额收益
        excess_returns = daily_returns - self.risk_free_rate / 252.0

        # 计算下行标准差（只考虑负收益）
        downside_returns = excess_returns[excess_returns < 0]

        if len(downside_returns) == 0 or downside_returns.std() == 0:
            return 0.0

        # 年化索提诺比率
        sortino = excess_returns.mean() / downside_returns.std() * np.sqrt(252)

        return sortino

    def max_drawdown(self, equity_curve: pd.DataFrame) -> float:
        """
        最大回撤 (Maximum Drawdown)

        参数:
            equity_curve: 权益曲线

        返回:
            float: 最大回撤比例（正数）
        """
        # 计算累积最高值
        cummax = equity_curve["equity"].cummax()

        # 计算回撤
        drawdown = (equity_curve["equity"] - cummax) / cummax

        # 返回最大回撤（转为正数）
        return abs(drawdown.min())

    def max_drawdown_duration(self, equity_curve: pd.DataFrame) -> int:
        """
        最大回撤持续时间

        参数:
            equity_curve: 权益曲线

        返回:
            int: 最大回撤持续天数
        """
        # 计算累积最高值
        cummax = equity_curve["equity"].cummax()

        # 计算回撤
        drawdown = (equity_curve["equity"] - cummax) / cummax

        # 找出回撤期
        is_drawdown = drawdown < 0

        # 计算连续回撤天数
        max_duration = 0
        current_duration = 0

        for dd in is_drawdown:
            if dd:
                current_duration += 1
                max_duration = max(max_duration, current_duration)
            else:
                current_duration = 0

        return max_duration

    def calmar_ratio(
        self, daily_returns: pd.Series, equity_curve: pd.DataFrame
    ) -> float:
        """
        卡尔玛比率 (Calmar Ratio)

        年化收益率 / 最大回撤

        参数:
            daily_returns: 每日收益率
            equity_curve: 权益曲线

        返回:
            float: 卡尔玛比率
        """
        ann_return = self.annualized_return(daily_returns)
        max_dd = self.max_drawdown(equity_curve)

        if max_dd == 0:
            return 0.0

        return ann_return / max_dd

    def volatility(self, daily_returns: pd.Series) -> float:
        """
        波动率（年化标准差）

        参数:
            daily_returns: 每日收益率

        返回:
            float: 年化波动率
        """
        return daily_returns.std() * np.sqrt(252)

    def value_at_risk(
        self, daily_returns: pd.Series, confidence: float = 0.95
    ) -> float:
        """
        风险价值 (Value at Risk, VaR)

        给定置信水平下的最大损失

        参数:
            daily_returns: 每日收益率
            confidence: 置信水平（默认95%）

        返回:
            float: VaR值（负数表示损失）
        """
        return daily_returns.quantile(1 - confidence)

    def conditional_var(
        self, daily_returns: pd.Series, confidence: float = 0.95
    ) -> float:
        """
        条件风险价值 (Conditional VaR, CVaR)

        超过VaR的平均损失

        参数:
            daily_returns: 每日收益率
            confidence: 置信水平（默认95%）

        返回:
            float: CVaR值
        """
        var = self.value_at_risk(daily_returns, confidence)
        return daily_returns[daily_returns <= var].mean()

    def alpha(self, strategy_returns: pd.Series, benchmark_returns: pd.Series) -> float:
        """
        Alpha - 超额收益

        参数:
            strategy_returns: 策略收益率
            benchmark_returns: 基准收益率

        返回:
            float: Alpha值（年化）
        """
        # 对齐数据
        aligned = pd.DataFrame(
            {"strategy": strategy_returns, "benchmark": benchmark_returns}
        ).dropna()

        if len(aligned) == 0:
            return 0.0

        # 计算年化超额收益
        strategy_ann = self.annualized_return(aligned["strategy"])
        benchmark_ann = self.annualized_return(aligned["benchmark"])

        return strategy_ann - benchmark_ann

    def beta(self, strategy_returns: pd.Series, benchmark_returns: pd.Series) -> float:
        """
        Beta - 系统性风险

        参数:
            strategy_returns: 策略收益率
            benchmark_returns: 基准收益率

        返回:
            float: Beta值
        """
        # 对齐数据
        aligned = pd.DataFrame(
            {"strategy": strategy_returns, "benchmark": benchmark_returns}
        ).dropna()

        if len(aligned) < 2:
            return 0.0

        # 计算协方差和方差
        covariance = aligned["strategy"].cov(aligned["benchmark"])
        variance = aligned["benchmark"].var()

        if variance == 0:
            return 0.0

        return covariance / variance

    def information_ratio(
        self, strategy_returns: pd.Series, benchmark_returns: pd.Series
    ) -> float:
        """
        信息比率 (Information Ratio)

        超额收益 / 跟踪误差

        参数:
            strategy_returns: 策略收益率
            benchmark_returns: 基准收益率

        返回:
            float: 信息比率
        """
        # 对齐数据
        aligned = pd.DataFrame(
            {"strategy": strategy_returns, "benchmark": benchmark_returns}
        ).dropna()

        if len(aligned) == 0:
            return 0.0

        # 计算超额收益
        excess_returns = aligned["strategy"] - aligned["benchmark"]

        # 计算跟踪误差
        tracking_error = excess_returns.std()

        if tracking_error == 0:
            return 0.0

        # 年化信息比率
        return excess_returns.mean() / tracking_error * np.sqrt(252)

    def _trade_statistics(self, trades: list) -> Dict:
        """计算交易统计"""
        if not trades:
            return {}

        winning_trades = [t for t in trades if t.pnl > 0]
        losing_trades = [t for t in trades if t.pnl < 0]

        stats = {
            "total_trades": len(trades),
            "winning_trades": len(winning_trades),
            "losing_trades": len(losing_trades),
            "win_rate": len(winning_trades) / len(trades) if trades else 0,
            "avg_trade_return": np.mean([t.pnl_pct for t in trades]),
            "avg_win": (
                np.mean([t.pnl for t in winning_trades]) if winning_trades else 0
            ),
            "avg_loss": np.mean([t.pnl for t in losing_trades]) if losing_trades else 0,
            "largest_win": (
                max([t.pnl for t in winning_trades]) if winning_trades else 0
            ),
            "largest_loss": min([t.pnl for t in losing_trades]) if losing_trades else 0,
            "avg_holding_days": np.mean([t.holding_days for t in trades]),
            "max_holding_days": max([t.holding_days for t in trades]),
            "min_holding_days": min([t.holding_days for t in trades]),
        }

        # 盈亏比
        total_wins = sum(t.pnl for t in winning_trades) if winning_trades else 0
        total_losses = abs(sum(t.pnl for t in losing_trades)) if losing_trades else 1
        stats["profit_factor"] = total_wins / total_losses if total_losses > 0 else 0

        # 期望值
        stats["expectancy"] = (
            stats["win_rate"] * stats["avg_win"]
            + (1 - stats["win_rate"]) * stats["avg_loss"]
        )

        return stats

    def generate_report(self, metrics: Dict) -> str:
        """
        生成性能报告

        参数:
            metrics: 性能指标字典

        返回:
            str: 格式化的报告文本
        """
        report = []
        report.append("=" * 70)
        report.append("回测性能报告")
        report.append("=" * 70)

        report.append("\n【收益指标】")
        report.append(
            f"  初始资金:          {metrics.get('initial_capital', 0):>15,.2f}"
        )
        report.append(f"  最终资金:          {metrics.get('final_capital', 0):>15,.2f}")
        report.append(f"  总收益率:          {metrics.get('total_return', 0):>15.2%}")
        report.append(
            f"  年化收益率:        {metrics.get('annualized_return', 0):>15.2%}"
        )

        report.append("\n【风险指标】")
        report.append(f"  波动率(年化):      {metrics.get('volatility', 0):>15.2%}")
        report.append(f"  最大回撤:          {metrics.get('max_drawdown', 0):>15.2%}")
        report.append(
            f"  最大回撤持续:      {metrics.get('max_drawdown_duration', 0):>12} 天"
        )

        report.append("\n【风险调整收益】")
        report.append(f"  夏普比率:          {metrics.get('sharpe_ratio', 0):>15.3f}")
        report.append(f"  索提诺比率:        {metrics.get('sortino_ratio', 0):>15.3f}")
        report.append(f"  卡尔玛比率:        {metrics.get('calmar_ratio', 0):>15.3f}")

        report.append("\n【交易统计】")
        report.append(f"  总交易次数:        {metrics.get('total_trades', 0):>15}")
        report.append(f"  盈利次数:          {metrics.get('winning_trades', 0):>15}")
        report.append(f"  亏损次数:          {metrics.get('losing_trades', 0):>15}")
        report.append(f"  胜率:              {metrics.get('win_rate', 0):>15.2%}")
        report.append(f"  盈亏比:            {metrics.get('profit_factor', 0):>15.2f}")
        report.append(
            f"  平均持仓天数:      {metrics.get('avg_holding_days', 0):>15.1f}"
        )

        if "alpha" in metrics:
            report.append("\n【基准比较】")
            report.append(f"  Alpha:             {metrics['alpha']:>15.2%}")
            report.append(f"  Beta:              {metrics['beta']:>15.3f}")
            report.append(f"  信息比率:          {metrics['information_ratio']:>15.3f}")

        report.append("\n" + "=" * 70)

        return "\n".join(report)


if __name__ == "__main__":
    # 测试代码
    print("性能指标计算测试")
    print("=" * 70)

    # 生成测试数据
    np.random.seed(42)
    n = 252
    dates = pd.date_range("2024-01-01", periods=n, freq="D")

    # 模拟权益曲线
    returns = np.random.randn(n) * 0.01 + 0.0005  # 日收益率
    equity = 100000 * (1 + returns).cumprod()

    equity_curve = pd.DataFrame(
        {"equity": equity, "cash": 50000, "position": 500, "price": 100}, index=dates
    )

    daily_returns = pd.Series(returns, index=dates)

    # 创建性能指标计算器
    metrics_calc = PerformanceMetrics(risk_free_rate=0.03)

    # 计算所有指标
    metrics = metrics_calc.calculate_all_metrics(
        equity_curve=equity_curve,
        daily_returns=daily_returns,
        trades=[],
        initial_capital=100000,
    )

    # 生成报告
    report = metrics_calc.generate_report(metrics)
    print(report)

    print("\n测试通过！")
