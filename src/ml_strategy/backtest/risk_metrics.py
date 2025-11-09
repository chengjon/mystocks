"""
风险指标计算模块 (Risk Metrics)

功能说明:
- 计算各种风险度量指标
- 提供风险敞口分析
- 生成风险报告

作者: MyStocks量化交易团队
创建时间: 2025-10-18
版本: 1.0.0
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from scipy import stats
import logging


class RiskMetrics:
    """
    风险指标计算器

    提供全面的风险分析指标
    """

    def __init__(self):
        """初始化风险指标计算器"""
        self.logger = logging.getLogger(f"{__name__}.RiskMetrics")
        self.logger.setLevel(logging.INFO)

    def downside_deviation(
        self, returns: pd.Series, target_return: float = 0.0
    ) -> float:
        """
        下行偏差 (Downside Deviation)

        只考虑低于目标收益的波动

        参数:
            returns: 收益率序列
            target_return: 目标收益率

        返回:
            float: 年化下行偏差
        """
        downside_diff = returns - target_return
        downside_diff = downside_diff[downside_diff < 0]

        if len(downside_diff) == 0:
            return 0.0

        return downside_diff.std() * np.sqrt(252)

    def ulcer_index(self, equity_curve: pd.DataFrame) -> float:
        """
        溃疡指数 (Ulcer Index)

        衡量回撤的深度和持续时间

        参数:
            equity_curve: 权益曲线

        返回:
            float: 溃疡指数
        """
        # 计算累积最高值
        cummax = equity_curve["equity"].cummax()

        # 计算回撤百分比
        drawdown_pct = ((equity_curve["equity"] - cummax) / cummax) * 100

        # 计算溃疡指数
        ulcer = np.sqrt(np.mean(drawdown_pct**2))

        return abs(ulcer)

    def pain_index(self, equity_curve: pd.DataFrame) -> float:
        """
        痛苦指数 (Pain Index)

        平均回撤深度

        参数:
            equity_curve: 权益曲线

        返回:
            float: 痛苦指数
        """
        # 计算累积最高值
        cummax = equity_curve["equity"].cummax()

        # 计算回撤
        drawdown = (equity_curve["equity"] - cummax) / cummax

        # 返回平均回撤（取绝对值）
        return abs(drawdown.mean())

    def tail_ratio(self, returns: pd.Series) -> float:
        """
        尾部比率 (Tail Ratio)

        右尾(95分位)与左尾(5分位)的比率

        参数:
            returns: 收益率序列

        返回:
            float: 尾部比率
        """
        right_tail = returns.quantile(0.95)
        left_tail = returns.quantile(0.05)

        if abs(left_tail) < 1e-10:
            return 0.0

        return abs(right_tail / left_tail)

    def skewness(self, returns: pd.Series) -> float:
        """
        偏度 (Skewness)

        收益分布的不对称性
        - 正值: 右偏（正收益较多）
        - 负值: 左偏（负收益较多）

        参数:
            returns: 收益率序列

        返回:
            float: 偏度
        """
        return stats.skew(returns.dropna())

    def kurtosis(self, returns: pd.Series) -> float:
        """
        峰度 (Kurtosis)

        收益分布的尖峭程度
        - 正值: 尖峭（极端值较多）
        - 负值: 平坦

        参数:
            returns: 收益率序列

        返回:
            float: 峰度（超额峰度）
        """
        return stats.kurtosis(returns.dropna())

    def omega_ratio(self, returns: pd.Series, target_return: float = 0.0) -> float:
        """
        Omega比率

        高于目标收益的概率加权收益 / 低于目标收益的概率加权损失

        参数:
            returns: 收益率序列
            target_return: 目标收益率

        返回:
            float: Omega比率
        """
        # 超过目标的收益
        gains = returns[returns > target_return] - target_return
        # 低于目标的损失
        losses = target_return - returns[returns < target_return]

        if losses.sum() == 0:
            return 0.0

        return gains.sum() / losses.sum()

    def burke_ratio(
        self,
        returns: pd.Series,
        equity_curve: pd.DataFrame,
        risk_free_rate: float = 0.03,
    ) -> float:
        """
        Burke比率

        超额收益 / 回撤平方和的平方根

        参数:
            returns: 收益率序列
            equity_curve: 权益曲线
            risk_free_rate: 无风险利率

        返回:
            float: Burke比率
        """
        # 计算年化超额收益
        annualized_return = (1 + returns).prod() ** (252 / len(returns)) - 1
        excess_return = annualized_return - risk_free_rate

        # 计算回撤
        cummax = equity_curve["equity"].cummax()
        drawdowns = (equity_curve["equity"] - cummax) / cummax

        # 回撤平方和的平方根
        burke_denominator = np.sqrt((drawdowns**2).sum())

        if burke_denominator == 0:
            return 0.0

        return excess_return / burke_denominator

    def consecutive_losses(self, trades: List) -> Tuple[int, float]:
        """
        最大连续亏损

        参数:
            trades: 交易记录列表

        返回:
            tuple: (最大连续亏损次数, 最大连续亏损金额)
        """
        if not trades:
            return 0, 0.0

        max_consecutive = 0
        current_consecutive = 0
        max_loss_amount = 0.0
        current_loss_amount = 0.0

        for trade in trades:
            if trade.pnl < 0:
                current_consecutive += 1
                current_loss_amount += trade.pnl
                max_consecutive = max(max_consecutive, current_consecutive)
                max_loss_amount = min(max_loss_amount, current_loss_amount)
            else:
                current_consecutive = 0
                current_loss_amount = 0.0

        return max_consecutive, abs(max_loss_amount)

    def recovery_factor(self, total_return: float, max_drawdown: float) -> float:
        """
        恢复因子

        总收益 / 最大回撤

        参数:
            total_return: 总收益率
            max_drawdown: 最大回撤

        返回:
            float: 恢复因子
        """
        if max_drawdown == 0:
            return 0.0

        return total_return / max_drawdown

    def payoff_ratio(self, trades: List) -> float:
        """
        盈亏比 (Payoff Ratio)

        平均盈利 / 平均亏损

        参数:
            trades: 交易记录列表

        返回:
            float: 盈亏比
        """
        if not trades:
            return 0.0

        winning_trades = [t.pnl for t in trades if t.pnl > 0]
        losing_trades = [t.pnl for t in trades if t.pnl < 0]

        if not losing_trades or not winning_trades:
            return 0.0

        avg_win = np.mean(winning_trades)
        avg_loss = abs(np.mean(losing_trades))

        if avg_loss == 0:
            return 0.0

        return avg_win / avg_loss

    def trade_expectancy(self, trades: List) -> float:
        """
        交易期望值

        (胜率 × 平均盈利) - (败率 × 平均亏损)

        参数:
            trades: 交易记录列表

        返回:
            float: 期望值
        """
        if not trades:
            return 0.0

        winning_trades = [t.pnl for t in trades if t.pnl > 0]
        losing_trades = [t.pnl for t in trades if t.pnl < 0]

        win_rate = len(winning_trades) / len(trades)
        loss_rate = len(losing_trades) / len(trades)

        avg_win = np.mean(winning_trades) if winning_trades else 0
        avg_loss = abs(np.mean(losing_trades)) if losing_trades else 0

        return (win_rate * avg_win) - (loss_rate * avg_loss)

    def calculate_all_risk_metrics(
        self,
        equity_curve: pd.DataFrame,
        returns: pd.Series,
        trades: List,
        total_return: float,
        max_drawdown: float,
        risk_free_rate: float = 0.03,
    ) -> Dict:
        """
        计算所有风险指标

        参数:
            equity_curve: 权益曲线
            returns: 收益率序列
            trades: 交易记录列表
            total_return: 总收益率
            max_drawdown: 最大回撤
            risk_free_rate: 无风险利率

        返回:
            dict: 所有风险指标
        """
        metrics = {}

        # 波动性指标
        metrics["downside_deviation"] = self.downside_deviation(returns)
        metrics["ulcer_index"] = self.ulcer_index(equity_curve)
        metrics["pain_index"] = self.pain_index(equity_curve)

        # 分布特征
        metrics["skewness"] = self.skewness(returns)
        metrics["kurtosis"] = self.kurtosis(returns)
        metrics["tail_ratio"] = self.tail_ratio(returns)

        # 风险调整指标
        metrics["omega_ratio"] = self.omega_ratio(returns)
        metrics["burke_ratio"] = self.burke_ratio(returns, equity_curve, risk_free_rate)
        metrics["recovery_factor"] = self.recovery_factor(total_return, max_drawdown)

        # 交易风险
        if trades:
            metrics["payoff_ratio"] = self.payoff_ratio(trades)
            metrics["trade_expectancy"] = self.trade_expectancy(trades)
            max_consec, max_consec_loss = self.consecutive_losses(trades)
            metrics["max_consecutive_losses"] = max_consec
            metrics["max_consecutive_loss_amount"] = max_consec_loss

        return metrics

    def generate_risk_report(self, metrics: Dict) -> str:
        """
        生成风险报告

        参数:
            metrics: 风险指标字典

        返回:
            str: 格式化的风险报告
        """
        report = []
        report.append("=" * 70)
        report.append("风险分析报告")
        report.append("=" * 70)

        report.append("\n【波动性指标】")
        report.append(
            f"  下行偏差:          {metrics.get('downside_deviation', 0):>15.2%}"
        )
        report.append(f"  溃疡指数:          {metrics.get('ulcer_index', 0):>15.3f}")
        report.append(f"  痛苦指数:          {metrics.get('pain_index', 0):>15.2%}")

        report.append("\n【分布特征】")
        report.append(f"  偏度:              {metrics.get('skewness', 0):>15.3f}")
        report.append(f"  峰度:              {metrics.get('kurtosis', 0):>15.3f}")
        report.append(f"  尾部比率:          {metrics.get('tail_ratio', 0):>15.3f}")

        report.append("\n【风险调整收益】")
        report.append(f"  Omega比率:         {metrics.get('omega_ratio', 0):>15.3f}")
        report.append(f"  Burke比率:         {metrics.get('burke_ratio', 0):>15.3f}")
        report.append(
            f"  恢复因子:          {metrics.get('recovery_factor', 0):>15.3f}"
        )

        if "payoff_ratio" in metrics:
            report.append("\n【交易风险】")
            report.append(
                f"  盈亏比:            {metrics.get('payoff_ratio', 0):>15.3f}"
            )
            report.append(
                f"  交易期望值:        {metrics.get('trade_expectancy', 0):>15,.2f}"
            )
            report.append(
                f"  最大连续亏损:      {metrics.get('max_consecutive_losses', 0):>12} 次"
            )
            report.append(
                f"  最大连续亏损额:    {metrics.get('max_consecutive_loss_amount', 0):>15,.2f}"
            )

        report.append("\n" + "=" * 70)

        return "\n".join(report)


if __name__ == "__main__":
    # 测试代码
    print("风险指标计算测试")
    print("=" * 70)

    # 生成测试数据
    np.random.seed(42)
    n = 252
    dates = pd.date_range("2024-01-01", periods=n, freq="D")

    # 模拟收益率（带有负偏）
    returns = np.random.randn(n) * 0.015 + 0.0003
    equity = 100000 * (1 + returns).cumprod()

    equity_curve = pd.DataFrame({"equity": equity}, index=dates)

    returns_series = pd.Series(returns, index=dates)

    # 创建风险指标计算器
    risk_calc = RiskMetrics()

    # 计算所有风险指标
    total_return = (equity[-1] - 100000) / 100000
    cummax = equity_curve["equity"].cummax()
    max_dd = abs(((equity_curve["equity"] - cummax) / cummax).min())

    risk_metrics = risk_calc.calculate_all_risk_metrics(
        equity_curve=equity_curve,
        returns=returns_series,
        trades=[],
        total_return=total_return,
        max_drawdown=max_dd,
    )

    # 生成报告
    report = risk_calc.generate_risk_report(risk_metrics)
    print(report)

    print("\n测试通过！")
