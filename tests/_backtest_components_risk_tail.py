"""Support mixin extracted from `test_backtest_components.py`."""

import numpy as np
import pandas as pd

from src.ml_strategy.backtest.risk_metrics import RiskMetrics


class TestBacktestRiskMetricsMixin:
    """风险指标测试方法集"""

    __test__ = False

    def setup_method(self):
        """测试前准备"""
        self.risk_metrics = RiskMetrics()

    def test_downside_deviation(self):
        """测试下行偏差"""
        returns = pd.Series([0.01, -0.02, 0.015, -0.01, 0.02])

        dd = self.risk_metrics.downside_deviation(returns, target_return=0.0)

        assert dd >= 0

    def test_downside_deviation_no_downside(self):
        """测试无下行偏差"""
        returns = pd.Series([0.01, 0.02, 0.015, 0.01, 0.02])

        dd = self.risk_metrics.downside_deviation(returns, target_return=0.0)

        assert dd == 0.0

    def test_ulcer_index(self):
        """测试溃疡指数"""
        equity_curve = pd.DataFrame({"equity": [100000, 110000, 105000, 95000, 100000]})

        ulcer = self.risk_metrics.ulcer_index(equity_curve)

        assert ulcer > 0

    def test_pain_index(self):
        """测试痛苦指数"""
        equity_curve = pd.DataFrame({"equity": [100000, 110000, 105000, 95000, 100000]})

        pain = self.risk_metrics.pain_index(equity_curve)

        assert pain > 0

    def test_tail_ratio(self):
        """测试尾部比率"""
        np.random.seed(42)
        returns = pd.Series(np.random.randn(252) * 0.01)

        tail_ratio = self.risk_metrics.tail_ratio(returns)

        assert tail_ratio >= 0

    def test_skewness(self):
        """测试偏度"""
        returns = pd.Series([0.01] * 90 + [0.05] * 10)

        skew = self.risk_metrics.skewness(returns)

        assert skew > 0

    def test_kurtosis(self):
        """测试峰度"""
        np.random.seed(42)
        returns = pd.Series(np.random.randn(252) * 0.01)

        kurt = self.risk_metrics.kurtosis(returns)

        assert isinstance(kurt, float)

    def test_omega_ratio(self):
        """测试Omega比率"""
        returns = pd.Series([0.01, 0.02, -0.01, 0.015, -0.005])

        omega = self.risk_metrics.omega_ratio(returns, target_return=0.0)

        assert omega >= 0

    def test_burke_ratio(self):
        """测试Burke比率"""
        returns = pd.Series([0.001] * 252)
        equity_curve = pd.DataFrame({"equity": 100000 * (1 + returns).cumprod()})

        burke = self.risk_metrics.burke_ratio(returns, equity_curve, risk_free_rate=0.03)

        assert isinstance(burke, float)

    def test_consecutive_losses(self, sample_trades):
        """测试最大连续亏损"""
        max_consec, max_loss = self.risk_metrics.consecutive_losses(sample_trades)

        assert max_consec >= 0
        assert max_loss >= 0

    def test_recovery_factor(self):
        """测试恢复因子"""
        recovery = self.risk_metrics.recovery_factor(total_return=0.20, max_drawdown=0.10)

        assert recovery == 2.0

    def test_recovery_factor_zero_drawdown(self):
        """测试恢复因子（零回撤）"""
        recovery = self.risk_metrics.recovery_factor(total_return=0.20, max_drawdown=0.0)

        assert recovery == 0.0

    def test_payoff_ratio(self, sample_trades):
        """测试盈亏比"""
        payoff = self.risk_metrics.payoff_ratio(sample_trades)

        assert payoff >= 0

    def test_trade_expectancy(self, sample_trades):
        """测试交易期望值"""
        expectancy = self.risk_metrics.trade_expectancy(sample_trades)

        assert isinstance(expectancy, float)

    def test_calculate_all_risk_metrics(self, sample_backtest_result):
        """测试计算所有风险指标"""
        metrics = self.risk_metrics.calculate_all_risk_metrics(
            equity_curve=sample_backtest_result["equity_curve"],
            returns=sample_backtest_result["daily_returns"],
            trades=sample_backtest_result["trades"],
            total_return=0.10,
            max_drawdown=0.05,
            risk_free_rate=0.03,
        )

        required_metrics = [
            "downside_deviation",
            "ulcer_index",
            "pain_index",
            "skewness",
            "kurtosis",
            "tail_ratio",
            "omega_ratio",
            "burke_ratio",
            "recovery_factor",
        ]

        for metric in required_metrics:
            assert metric in metrics

    def test_generate_risk_report(self):
        """测试生成风险报告"""
        metrics = {
            "downside_deviation": 0.05,
            "ulcer_index": 3.5,
            "pain_index": 0.02,
            "skewness": 0.5,
            "kurtosis": 2.0,
            "tail_ratio": 1.2,
            "omega_ratio": 1.5,
            "burke_ratio": 0.8,
        }

        report = self.risk_metrics.generate_risk_report(metrics)

        assert isinstance(report, str)
        assert "风险分析报告" in report
        assert "波动性指标" in report
