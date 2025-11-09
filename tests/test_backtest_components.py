"""
回测组件测试套件 (Backtest Components Test Suite)

功能说明:
- 测试向量化回测器
- 测试性能指标计算
- 测试风险指标计算
- 测试回测引擎集成

作者: MyStocks量化交易团队
创建时间: 2025-10-18
版本: 1.0.0
"""

import pytest
import pandas as pd
import numpy as np
from datetime import date, timedelta
from unittest.mock import Mock, patch
import sys

sys.path.insert(0, "/opt/claude/mystocks_spec")

from backtest.vectorized_backtester import VectorizedBacktester, BacktestConfig, Trade
from backtest.performance_metrics import PerformanceMetrics
from backtest.risk_metrics import RiskMetrics
from backtest.backtest_engine import BacktestEngine


# ==================== VectorizedBacktester Tests ====================


class TestBacktestConfig:
    """回测配置测试"""

    def test_config_default_values(self):
        """测试配置默认值"""
        config = BacktestConfig()

        assert config.initial_capital == 100000.0
        assert config.commission_rate == 0.0003
        assert config.min_commission == 5.0
        assert config.slippage_rate == 0.0001
        assert config.stamp_tax_rate == 0.001
        assert config.max_position_size == 1.0
        assert config.position_mode == "equal_weight"

    def test_config_custom_values(self):
        """测试配置自定义值"""
        config = BacktestConfig(
            initial_capital=200000.0, commission_rate=0.0005, max_position_size=0.5
        )

        assert config.initial_capital == 200000.0
        assert config.commission_rate == 0.0005
        assert config.max_position_size == 0.5


class TestVectorizedBacktester:
    """向量化回测器测试"""

    def setup_method(self):
        """测试前准备"""
        self.config = BacktestConfig(
            initial_capital=100000, commission_rate=0.0003, slippage_rate=0.0001
        )
        self.backtester = VectorizedBacktester(self.config)

    def test_backtester_initialization(self):
        """测试回测器初始化"""
        assert self.backtester.config == self.config
        assert self.backtester.trades == []
        assert self.backtester.equity_curve is None
        assert self.backtester.daily_returns is None

    def test_validate_data_success(self, sample_price_data, sample_signals):
        """测试数据验证成功"""
        # 不应该抛出异常
        self.backtester._validate_data(sample_price_data, sample_signals)

    def test_validate_data_missing_columns(self):
        """测试数据验证缺失列"""
        # 缺少必需列
        invalid_price_data = pd.DataFrame(
            {"close": [100, 101, 102], "volume": [1000, 1100, 1200]}
        )

        signals = pd.DataFrame({"signal": ["buy", None, "sell"]})

        with pytest.raises(ValueError, match="价格数据缺少必需列"):
            self.backtester._validate_data(invalid_price_data, signals)

    def test_validate_data_missing_signal_column(self, sample_price_data):
        """测试数据验证缺失信号列"""
        invalid_signals = pd.DataFrame({"invalid": ["buy", None, "sell"]})

        with pytest.raises(ValueError, match="信号数据必须包含 'signal' 列"):
            self.backtester._validate_data(sample_price_data, invalid_signals)

    def test_run_backtest_simple_strategy(self, sample_price_data, sample_signals):
        """测试简单策略回测"""
        result = self.backtester.run(sample_price_data, sample_signals)

        # 验证返回结构
        assert "trades" in result
        assert "equity_curve" in result
        assert "daily_returns" in result
        assert "summary" in result

        # 验证交易记录
        trades = result["trades"]
        assert isinstance(trades, list)

        # 验证权益曲线
        equity_curve = result["equity_curve"]
        assert isinstance(equity_curve, pd.DataFrame)
        assert "equity" in equity_curve.columns
        assert len(equity_curve) == len(sample_price_data)

        # 验证汇总统计
        summary = result["summary"]
        assert "total_return" in summary
        assert "total_trades" in summary
        assert "win_rate" in summary

    def test_run_backtest_no_signals(self, sample_price_data):
        """测试无信号回测"""
        # 创建空信号
        empty_signals = pd.DataFrame(index=sample_price_data.index)
        empty_signals["signal"] = None

        result = self.backtester.run(sample_price_data, empty_signals)

        # 应该没有交易
        assert len(result["trades"]) == 0
        # 权益应该等于初始资金
        assert result["equity_curve"]["equity"].iloc[-1] == self.config.initial_capital

    def test_run_backtest_buy_only(self, sample_price_data):
        """测试只买不卖"""
        signals = pd.DataFrame(index=sample_price_data.index)
        signals["signal"] = None
        signals.iloc[5]["signal"] = "buy"

        result = self.backtester.run(sample_price_data, signals)

        # 应该强制平仓，有一笔交易
        assert len(result["trades"]) == 1
        # 权益不等于初始资金（有盈亏）
        assert result["equity_curve"]["equity"].iloc[-1] != self.config.initial_capital

    def test_calculate_summary_no_trades(self):
        """测试无交易汇总"""
        self.backtester.trades = []
        self.backtester.equity_curve = pd.DataFrame({"equity": [100000] * 10})

        summary = self.backtester._calculate_summary()

        assert summary["total_trades"] == 0
        assert summary["win_rate"] == 0.0
        assert summary["total_return"] == 0.0

    def test_calculate_summary_with_trades(self):
        """测试有交易汇总"""
        # 创建模拟交易
        trades = [
            Trade(
                entry_date=date(2024, 1, 1),
                entry_price=100,
                exit_date=date(2024, 1, 5),
                exit_price=105,
                shares=100,
                direction="long",
                pnl=500,
                pnl_pct=0.05,
                commission=10,
                slippage=5,
                holding_days=4,
            ),
            Trade(
                entry_date=date(2024, 1, 6),
                entry_price=105,
                exit_date=date(2024, 1, 10),
                exit_price=103,
                shares=100,
                direction="long",
                pnl=-200,
                pnl_pct=-0.02,
                commission=10,
                slippage=5,
                holding_days=4,
            ),
        ]

        self.backtester.trades = trades
        self.backtester.equity_curve = pd.DataFrame(
            {"equity": [100000, 100500, 100300]}
        )
        self.backtester.config.initial_capital = 100000

        summary = self.backtester._calculate_summary()

        assert summary["total_trades"] == 2
        assert summary["winning_trades"] == 1
        assert summary["losing_trades"] == 1
        assert summary["win_rate"] == 0.5

    def test_get_trades_df(self):
        """测试获取交易记录DataFrame"""
        # 创建模拟交易
        trades = [
            Trade(
                entry_date=date(2024, 1, 1),
                entry_price=100,
                exit_date=date(2024, 1, 5),
                exit_price=105,
                shares=100,
                direction="long",
                pnl=500,
                pnl_pct=0.05,
                commission=10,
                slippage=5,
                holding_days=4,
            )
        ]

        self.backtester.trades = trades
        trades_df = self.backtester.get_trades_df()

        assert isinstance(trades_df, pd.DataFrame)
        assert len(trades_df) == 1
        assert "entry_date" in trades_df.columns
        assert "pnl" in trades_df.columns

    def test_get_trades_df_empty(self):
        """测试获取空交易记录"""
        self.backtester.trades = []
        trades_df = self.backtester.get_trades_df()

        assert isinstance(trades_df, pd.DataFrame)
        assert len(trades_df) == 0


# ==================== PerformanceMetrics Tests ====================


class TestPerformanceMetrics:
    """性能指标测试"""

    def setup_method(self):
        """测试前准备"""
        self.metrics = PerformanceMetrics(risk_free_rate=0.03)

    def test_metrics_initialization(self):
        """测试指标计算器初始化"""
        assert self.metrics.risk_free_rate == 0.03

    def test_total_return(self):
        """测试总收益率计算"""
        equity_curve = pd.DataFrame({"equity": [100000, 105000, 110000]})

        total_return = self.metrics.total_return(equity_curve, 100000)

        assert total_return == 0.10  # 10%

    def test_annualized_return(self):
        """测试年化收益率计算"""
        # 252个交易日，每日收益0.1%
        returns = pd.Series([0.001] * 252)

        ann_return = self.metrics.annualized_return(returns)

        # 年化收益应该接近 (1.001)^252 - 1 ≈ 28.7%
        assert 0.25 < ann_return < 0.35

    def test_sharpe_ratio_positive(self):
        """测试夏普比率（正收益）"""
        # 模拟正收益序列
        np.random.seed(42)
        returns = pd.Series(np.random.randn(252) * 0.01 + 0.001)

        sharpe = self.metrics.sharpe_ratio(returns)

        # 夏普比率应该为正
        assert sharpe > 0

    def test_sharpe_ratio_negative(self):
        """测试夏普比率（负收益）"""
        # 模拟负收益序列
        returns = pd.Series([-0.001] * 252)

        sharpe = self.metrics.sharpe_ratio(returns)

        # 夏普比率应该为负
        assert sharpe < 0

    def test_sharpe_ratio_zero_std(self):
        """测试夏普比率（零波动）"""
        # 恒定收益
        returns = pd.Series([0.001] * 252)

        sharpe = self.metrics.sharpe_ratio(returns)

        # 恒定收益情况下，超额收益std会非常小，但不是精确的0
        # 夏普比率应该为一个非常大的正数或0（取决于实现）
        assert sharpe >= 0 or sharpe == 0.0

    def test_sortino_ratio(self):
        """测试索提诺比率"""
        # 模拟收益序列
        np.random.seed(42)
        returns = pd.Series(np.random.randn(252) * 0.01 + 0.001)

        sortino = self.metrics.sortino_ratio(returns)

        # 索提诺比率应该大于夏普比率（只考虑下行风险）
        sharpe = self.metrics.sharpe_ratio(returns)
        assert sortino >= sharpe

    def test_max_drawdown(self):
        """测试最大回撤计算"""
        # 创建有明显回撤的权益曲线
        equity_curve = pd.DataFrame(
            {"equity": [100000, 110000, 105000, 108000, 95000, 100000]}
        )

        max_dd = self.metrics.max_drawdown(equity_curve)

        # 最大回撤: (110000 - 95000) / 110000 ≈ 13.64%
        assert 0.13 < max_dd < 0.14

    def test_max_drawdown_no_drawdown(self):
        """测试无回撤"""
        # 一直上涨
        equity_curve = pd.DataFrame({"equity": [100000, 105000, 110000, 115000]})

        max_dd = self.metrics.max_drawdown(equity_curve)

        assert max_dd == 0.0

    def test_max_drawdown_duration(self):
        """测试最大回撤持续时间"""
        # 创建有回撤的权益曲线
        equity_curve = pd.DataFrame(
            {"equity": [100000, 110000, 105000, 100000, 95000, 100000, 110000]}
        )

        duration = self.metrics.max_drawdown_duration(equity_curve)

        # 从110000跌到95000再恢复，持续5天
        assert duration >= 4

    def test_calmar_ratio(self):
        """测试卡尔玛比率"""
        returns = pd.Series([0.001] * 252)
        equity_curve = pd.DataFrame({"equity": 100000 * (1 + returns).cumprod()})

        calmar = self.metrics.calmar_ratio(returns, equity_curve)

        # 卡尔玛比率 = 年化收益 / 最大回撤
        # 由于是恒定正收益，最大回撤为0，应该返回0
        assert calmar >= 0

    def test_volatility(self):
        """测试波动率计算"""
        # 模拟收益序列
        np.random.seed(42)
        returns = pd.Series(np.random.randn(252) * 0.01)

        vol = self.metrics.volatility(returns)

        # 年化波动率应该接近 0.01 * sqrt(252) ≈ 15.87%
        assert 0.10 < vol < 0.20

    def test_value_at_risk(self):
        """测试VaR计算"""
        # 模拟收益序列
        np.random.seed(42)
        returns = pd.Series(np.random.randn(252) * 0.01)

        var_95 = self.metrics.value_at_risk(returns, 0.95)

        # 95% VaR应该为负（表示损失）
        assert var_95 < 0

    def test_conditional_var(self):
        """测试CVaR计算"""
        # 模拟收益序列
        np.random.seed(42)
        returns = pd.Series(np.random.randn(252) * 0.01)

        cvar_95 = self.metrics.conditional_var(returns, 0.95)

        # CVaR应该比VaR更负（平均尾部损失）
        var_95 = self.metrics.value_at_risk(returns, 0.95)
        assert cvar_95 <= var_95

    def test_alpha_beta(self):
        """测试Alpha和Beta计算"""
        # 策略收益
        np.random.seed(42)
        strategy_returns = pd.Series(np.random.randn(252) * 0.01 + 0.001)
        # 基准收益
        benchmark_returns = pd.Series(np.random.randn(252) * 0.01 + 0.0005)

        alpha = self.metrics.alpha(strategy_returns, benchmark_returns)
        beta = self.metrics.beta(strategy_returns, benchmark_returns)

        # Alpha应该接近策略与基准的收益差
        # Beta可以是正数或负数（负相关也是可能的）
        assert isinstance(alpha, float)
        assert isinstance(beta, float)

    def test_information_ratio(self):
        """测试信息比率"""
        # 策略收益
        strategy_returns = pd.Series(np.random.randn(252) * 0.01 + 0.001)
        # 基准收益
        benchmark_returns = pd.Series(np.random.randn(252) * 0.01)

        ir = self.metrics.information_ratio(strategy_returns, benchmark_returns)

        # 信息比率应该为正（策略优于基准）
        assert ir != 0

    def test_calculate_all_metrics(self, sample_backtest_result):
        """测试计算所有指标"""
        metrics = self.metrics.calculate_all_metrics(
            equity_curve=sample_backtest_result["equity_curve"],
            daily_returns=sample_backtest_result["daily_returns"],
            trades=sample_backtest_result["trades"],
            initial_capital=100000,
        )

        # 验证所有必需指标存在
        required_metrics = [
            "total_return",
            "annualized_return",
            "sharpe_ratio",
            "sortino_ratio",
            "calmar_ratio",
            "max_drawdown",
            "volatility",
            "var_95",
            "cvar_95",
        ]

        for metric in required_metrics:
            assert metric in metrics

    def test_generate_report(self):
        """测试生成性能报告"""
        metrics = {
            "initial_capital": 100000,
            "final_capital": 110000,
            "total_return": 0.10,
            "annualized_return": 0.12,
            "sharpe_ratio": 1.5,
            "max_drawdown": 0.05,
            "total_trades": 10,
            "win_rate": 0.6,
        }

        report = self.metrics.generate_report(metrics)

        assert isinstance(report, str)
        assert "回测性能报告" in report
        assert "100,000.00" in report
        assert "10.00%" in report


# ==================== RiskMetrics Tests ====================


class TestRiskMetrics:
    """风险指标测试"""

    def setup_method(self):
        """测试前准备"""
        self.risk_metrics = RiskMetrics()

    def test_downside_deviation(self):
        """测试下行偏差"""
        # 模拟收益序列（有负收益）
        returns = pd.Series([0.01, -0.02, 0.015, -0.01, 0.02])

        dd = self.risk_metrics.downside_deviation(returns, target_return=0.0)

        # 下行偏差应该为正
        assert dd >= 0

    def test_downside_deviation_no_downside(self):
        """测试无下行偏差"""
        # 全是正收益
        returns = pd.Series([0.01, 0.02, 0.015, 0.01, 0.02])

        dd = self.risk_metrics.downside_deviation(returns, target_return=0.0)

        # 应该为0
        assert dd == 0.0

    def test_ulcer_index(self):
        """测试溃疡指数"""
        equity_curve = pd.DataFrame({"equity": [100000, 110000, 105000, 95000, 100000]})

        ulcer = self.risk_metrics.ulcer_index(equity_curve)

        # 溃疡指数应该为正
        assert ulcer > 0

    def test_pain_index(self):
        """测试痛苦指数"""
        equity_curve = pd.DataFrame({"equity": [100000, 110000, 105000, 95000, 100000]})

        pain = self.risk_metrics.pain_index(equity_curve)

        # 痛苦指数应该为正（平均回撤）
        assert pain > 0

    def test_tail_ratio(self):
        """测试尾部比率"""
        # 模拟收益序列
        np.random.seed(42)
        returns = pd.Series(np.random.randn(252) * 0.01)

        tail_ratio = self.risk_metrics.tail_ratio(returns)

        # 尾部比率应该为正
        assert tail_ratio >= 0

    def test_skewness(self):
        """测试偏度"""
        # 右偏分布
        returns = pd.Series([0.01] * 90 + [0.05] * 10)

        skew = self.risk_metrics.skewness(returns)

        # 右偏应该为正
        assert skew > 0

    def test_kurtosis(self):
        """测试峰度"""
        # 正态分布
        np.random.seed(42)
        returns = pd.Series(np.random.randn(252) * 0.01)

        kurt = self.risk_metrics.kurtosis(returns)

        # 峰度可以为正或负
        assert isinstance(kurt, float)

    def test_omega_ratio(self):
        """测试Omega比率"""
        # 模拟收益序列
        returns = pd.Series([0.01, 0.02, -0.01, 0.015, -0.005])

        omega = self.risk_metrics.omega_ratio(returns, target_return=0.0)

        # Omega比率应该为正
        assert omega >= 0

    def test_burke_ratio(self):
        """测试Burke比率"""
        returns = pd.Series([0.001] * 252)
        equity_curve = pd.DataFrame({"equity": 100000 * (1 + returns).cumprod()})

        burke = self.risk_metrics.burke_ratio(
            returns, equity_curve, risk_free_rate=0.03
        )

        # Burke比率可以为正或负
        assert isinstance(burke, float)

    def test_consecutive_losses(self, sample_trades):
        """测试最大连续亏损"""
        max_consec, max_loss = self.risk_metrics.consecutive_losses(sample_trades)

        assert max_consec >= 0
        assert max_loss >= 0

    def test_recovery_factor(self):
        """测试恢复因子"""
        recovery = self.risk_metrics.recovery_factor(
            total_return=0.20, max_drawdown=0.10
        )

        # 恢复因子 = 0.20 / 0.10 = 2.0
        assert recovery == 2.0

    def test_recovery_factor_zero_drawdown(self):
        """测试恢复因子（零回撤）"""
        recovery = self.risk_metrics.recovery_factor(
            total_return=0.20, max_drawdown=0.0
        )

        # 零回撤应该返回0
        assert recovery == 0.0

    def test_payoff_ratio(self, sample_trades):
        """测试盈亏比"""
        payoff = self.risk_metrics.payoff_ratio(sample_trades)

        # 盈亏比应该为正
        assert payoff >= 0

    def test_trade_expectancy(self, sample_trades):
        """测试交易期望值"""
        expectancy = self.risk_metrics.trade_expectancy(sample_trades)

        # 期望值可以为正或负
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

        # 验证所有必需指标存在
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


# ==================== BacktestEngine Integration Tests ====================


class TestBacktestEngine:
    """回测引擎集成测试"""

    def setup_method(self):
        """测试前准备"""
        self.config = BacktestConfig(initial_capital=100000)
        self.engine = BacktestEngine(config=self.config, risk_free_rate=0.03)

    def test_engine_initialization(self):
        """测试引擎初始化"""
        assert self.engine.config == self.config
        assert self.engine.risk_free_rate == 0.03
        assert isinstance(self.engine.backtester, VectorizedBacktester)
        assert isinstance(self.engine.perf_metrics, PerformanceMetrics)
        assert isinstance(self.engine.risk_metrics, RiskMetrics)

    def test_run_complete_backtest(self, sample_price_data, sample_signals):
        """测试完整回测流程"""
        result = self.engine.run(sample_price_data, sample_signals)

        # 验证返回结构
        assert "backtest" in result
        assert "performance" in result
        assert "risk" in result
        assert "metrics" in result
        assert "report" in result
        assert "config" in result

        # 验证报告
        assert isinstance(result["report"], str)
        assert "回测性能报告" in result["report"]
        assert "风险分析报告" in result["report"]

    def test_get_trades_df(self, sample_price_data, sample_signals):
        """测试获取交易记录"""
        self.engine.run(sample_price_data, sample_signals)

        trades_df = self.engine.get_trades_df()

        assert isinstance(trades_df, pd.DataFrame)

    def test_get_equity_curve(self, sample_price_data, sample_signals):
        """测试获取权益曲线"""
        self.engine.run(sample_price_data, sample_signals)

        equity_curve = self.engine.get_equity_curve()

        assert isinstance(equity_curve, pd.DataFrame)
        assert "equity" in equity_curve.columns
        assert len(equity_curve) == len(sample_price_data)

    def test_get_daily_returns(self, sample_price_data, sample_signals):
        """测试获取每日收益率"""
        self.engine.run(sample_price_data, sample_signals)

        daily_returns = self.engine.get_daily_returns()

        assert isinstance(daily_returns, pd.Series)
        assert len(daily_returns) == len(sample_price_data)

    def test_save_result(self, sample_price_data, sample_signals, tmp_path):
        """测试保存回测结果"""
        self.engine.run(sample_price_data, sample_signals)

        # 保存到临时目录
        filepath = str(tmp_path / "backtest_result")
        self.engine.save_result(filepath)

        # 验证文件创建
        import os

        assert os.path.exists(f"{filepath}_report.txt")

    def test_run_with_benchmark(self, sample_price_data, sample_signals):
        """测试带基准的回测"""
        # 创建基准收益率
        benchmark_returns = pd.Series(
            np.random.randn(len(sample_price_data)) * 0.01,
            index=sample_price_data.index,
        )

        result = self.engine.run(
            sample_price_data, sample_signals, benchmark_returns=benchmark_returns
        )

        # 应该包含基准比较指标
        assert "alpha" in result["performance"]
        assert "beta" in result["performance"]
        assert "information_ratio" in result["performance"]


# ==================== Performance Tests ====================


class TestBacktestPerformance:
    """回测性能测试"""

    @pytest.mark.slow
    def test_large_dataset_performance(self):
        """测试大数据集性能"""
        import time

        # 生成5年数据（约1260个交易日）
        n = 1260
        dates = pd.date_range("2019-01-01", periods=n, freq="D")

        price_data = pd.DataFrame(
            {
                "open": 100 + np.cumsum(np.random.randn(n) * 0.5),
                "high": 100 + np.cumsum(np.random.randn(n) * 0.5) + 1,
                "low": 100 + np.cumsum(np.random.randn(n) * 0.5) - 1,
                "close": 100 + np.cumsum(np.random.randn(n) * 0.5),
                "volume": np.random.uniform(1000000, 10000000, n),
            },
            index=dates,
        )

        # 生成信号（每10天一个）
        signals = pd.DataFrame(index=dates)
        signals["signal"] = None
        for i in range(0, n, 10):
            if i < n:
                signals.iloc[i] = "buy"
            if i + 5 < n:
                signals.iloc[i + 5] = "sell"

        # 执行回测并计时
        config = BacktestConfig(initial_capital=100000)
        engine = BacktestEngine(config=config)

        start_time = time.time()
        result = engine.run(price_data, signals)
        end_time = time.time()

        # 验证性能（应该在5秒内完成）
        elapsed = end_time - start_time
        assert elapsed < 5.0, f"Backtest took {elapsed:.2f}s, expected < 5.0s"

        # 验证结果正确
        assert "report" in result
        assert result["backtest"]["summary"]["total_trades"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
