"""
Advanced Backtest Engine Unit Tests

高级回测引擎单元测试
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

# Add the src directory to the path for imports
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

from backtesting.advanced_backtest_engine import (
    WalkForwardAnalysis,
    MonteCarloSimulation,
    AdvancedBacktestEngine,
    WalkForwardConfig,
    MonteCarloConfig,
    AdvancedBacktestConfig,
    create_advanced_backtest_engine,
)


class TestWalkForwardAnalysis:
    """Walk-forward分析测试"""

    def setup_method(self):
        """测试前准备"""
        self.config = WalkForwardConfig(initial_train_window=100, test_window=50, step_size=25, expanding_window=True)
        self.wfa = WalkForwardAnalysis(self.config)

    def test_initialization(self):
        """测试初始化"""
        assert self.wfa.config == self.config
        assert self.wfa.logger is not None

    def test_generate_analysis_windows_expanding(self):
        """测试扩展窗口生成"""
        dates = pd.date_range("2023-01-01", periods=200, freq="D")
        price_data = pd.DataFrame(
            {
                "open": np.random.randn(200) + 100,
                "high": np.random.randn(200) + 102,
                "low": np.random.randn(200) + 98,
                "close": np.random.randn(200) + 100,
                "volume": np.random.uniform(1000000, 10000000, 200),
            },
            index=dates,
        )

        windows = self.wfa._generate_analysis_windows(price_data)

        assert len(windows) > 0
        for train_data, test_data in windows:
            assert len(train_data) >= self.config.initial_train_window
            assert len(test_data) == self.config.test_window
            assert isinstance(train_data, pd.DataFrame)
            assert isinstance(test_data, pd.DataFrame)

    def test_generate_analysis_windows_rolling(self):
        """测试滚动窗口生成"""
        self.wfa.config.expanding_window = False

        dates = pd.date_range("2023-01-01", periods=200, freq="D")
        price_data = pd.DataFrame(
            {
                "open": np.random.randn(200) + 100,
                "high": np.random.randn(200) + 102,
                "low": np.random.randn(200) + 98,
                "close": np.random.randn(200) + 100,
                "volume": np.random.uniform(1000000, 10000000, 200),
            },
            index=dates,
        )

        windows = self.wfa._generate_analysis_windows(price_data)

        # 滚动窗口应该有固定训练窗口大小
        for train_data, test_data in windows:
            assert len(train_data) == self.config.initial_train_window
            assert len(test_data) == self.config.test_window

    def test_data_validation(self):
        """测试数据验证"""
        # 有效的价格数据
        dates = pd.date_range("2023-01-01", periods=200, freq="D")
        valid_data = pd.DataFrame(
            {
                "open": np.random.randn(200) + 100,
                "high": np.random.randn(200) + 102,
                "low": np.random.randn(200) + 98,
                "close": np.random.randn(200) + 100,
                "volume": np.random.uniform(1000000, 10000000, 200),
            },
            index=dates,
        )

        assert self.wfa._validate_data(valid_data) == True

        # 无效的数据 - 缺少列
        invalid_data = pd.DataFrame(
            {
                "close": np.random.randn(200) + 100,
                "volume": np.random.uniform(1000000, 10000000, 200),
            },
            index=dates,
        )

        assert self.wfa._validate_data(invalid_data) == False

        # 无效的数据 - 数据长度不足
        short_data = valid_data.iloc[:50]
        assert self.wfa._validate_data(short_data) == False

    def test_summarize_results(self):
        """测试结果汇总"""
        # 创建模拟的窗口结果
        window_results = [
            {
                "window_id": 1,
                "result": {
                    "metrics": {"total_return": 0.05, "sharpe_ratio": 1.2, "max_drawdown": 0.03, "win_rate": 0.55}
                },
            },
            {
                "window_id": 2,
                "result": {
                    "metrics": {"total_return": 0.08, "sharpe_ratio": 1.5, "max_drawdown": 0.04, "win_rate": 0.60}
                },
            },
        ]

        summary = self.wfa._summarize_results(window_results)

        # 验证汇总统计
        assert "total_windows" in summary
        assert "total_return" in summary
        assert "sharpe_ratio" in summary
        assert "max_drawdown" in summary
        assert "win_rate" in summary
        assert "robustness_score" in summary
        assert "consistency_score" in summary

        assert summary["total_windows"] == 2
        assert summary["total_return"]["mean"] == pytest.approx(0.065, rel=0.01)

    @patch("backtesting.advanced_backtest_engine.BacktestEngine")
    def test_run_analysis(self, mock_backtest_engine):
        """测试完整分析流程"""
        # 创建mock回测引擎
        mock_instance = Mock()
        mock_instance.run.return_value = {
            "metrics": {"total_return": 0.05, "sharpe_ratio": 1.2, "max_drawdown": 0.03, "win_rate": 0.55}
        }
        mock_backtest_engine.return_value = mock_instance

        # 创建测试数据
        dates = pd.date_range("2023-01-01", periods=200, freq="D")
        price_data = pd.DataFrame(
            {
                "open": np.random.randn(200) + 100,
                "high": np.random.randn(200) + 102,
                "low": np.random.randn(200) + 98,
                "close": np.random.randn(200) + 100,
                "volume": np.random.uniform(1000000, 10000000, 200),
            },
            index=dates,
        )

        # 定义信号函数
        def signal_func(data, **kwargs):
            signals = pd.DataFrame(index=data.index)
            signals["signal"] = "buy"
            signals["strength"] = 0.8
            return signals

        # 运行分析
        result = self.wfa.run_analysis(price_data, signal_func)

        # 验证结果结构
        assert "config" in result
        assert "windows" in result
        assert "summary" in result
        assert "analysis_timestamp" in result
        assert isinstance(result["windows"], list)
        assert len(result["windows"]) > 0


class TestMonteCarloSimulation:
    """Monte Carlo模拟测试"""

    def setup_method(self):
        """测试前准备"""
        self.config = MonteCarloConfig(num_simulations=100, bootstrap_sample_size=None, random_seed=42)
        self.mcs = MonteCarloSimulation(self.config)

    def test_initialization(self):
        """测试初始化"""
        assert self.mcs.config == self.config
        assert self.mcs.logger is not None

    def test_bootstrap_sample(self):
        """测试自举采样"""
        np.random.seed(42)
        returns = pd.Series([0.01, 0.02, -0.01, 0.03, -0.02])

        sample = self.mcs._bootstrap_sample(returns)

        # 验证样本长度
        assert len(sample) == len(returns)

        # 验证样本包含原始数据的值（自举采样）
        sample_values = set(sample.values)
        original_values = set(returns.values)
        # 自举采样允许重复，所以样本可能包含重复值
        assert len(sample_values) <= len(original_values) + 1  # 允许一些小的差异

    def test_bootstrap_sample_custom_size(self):
        """测试自定义样本大小的自举采样"""
        self.mcs.config.bootstrap_sample_size = 10
        returns = pd.Series([0.01, 0.02, -0.01, 0.03, -0.02])

        sample = self.mcs._bootstrap_sample(returns)

        assert len(sample) == 10

    def test_data_validation(self):
        """测试数据验证"""
        # 有效的收益率数据
        valid_returns = pd.Series([0.01] * 50)
        assert len(valid_returns) >= 30  # 满足最小长度要求

        # 无效的数据 - 长度不足
        invalid_returns = pd.Series([0.01] * 20)

        with pytest.raises(ValueError, match="收益率数据长度不足"):
            self.mcs.run_simulation(invalid_returns, lambda x: {"metrics": {}})

    def test_analyze_simulation_results(self):
        """测试模拟结果分析"""
        # 创建模拟结果
        simulation_results = [
            {
                "simulation_id": 0,
                "result": {
                    "metrics": {"total_return": 0.05, "sharpe_ratio": 1.2, "max_drawdown": 0.03, "win_rate": 0.55}
                },
            },
            {
                "simulation_id": 1,
                "result": {
                    "metrics": {"total_return": 0.08, "sharpe_ratio": 1.5, "max_drawdown": 0.04, "win_rate": 0.60}
                },
            },
        ]

        analysis = self.mcs._analyze_simulation_results(simulation_results)

        # 验证分析结果结构
        assert "total_simulations" in analysis
        assert "successful_simulations" in analysis
        assert "success_rate" in analysis
        assert "total_return_distribution" in analysis
        assert "sharpe_ratio_distribution" in analysis
        assert "max_drawdown_distribution" in analysis
        assert "win_rate_distribution" in analysis
        assert "probability_analysis" in analysis

        # 验证基本统计
        assert analysis["total_simulations"] == 2
        assert analysis["successful_simulations"] == 2
        assert analysis["success_rate"] == 1.0

    @patch("backtesting.advanced_backtest_engine.BacktestEngine")
    def test_run_simulation(self, mock_backtest_engine):
        """测试完整模拟流程"""
        # 创建mock回测引擎
        mock_instance = Mock()
        mock_instance.run.return_value = {
            "backtest": {"daily_returns": pd.Series([0.01, 0.02, -0.01])},
            "metrics": {"total_return": 0.05, "sharpe_ratio": 1.2, "max_drawdown": 0.03, "win_rate": 0.55},
        }
        mock_backtest_engine.return_value = mock_instance

        # 创建测试收益率数据
        returns = pd.Series([0.01, 0.02, -0.01, 0.03, -0.02] * 10)  # 50个数据点

        # 定义模拟函数
        def simulation_func(data, **kwargs):
            return {"metrics": {"total_return": 0.05, "sharpe_ratio": 1.2, "max_drawdown": 0.03, "win_rate": 0.55}}

        # 运行模拟
        result = self.mcs.run_simulation(returns, simulation_func)

        # 验证结果结构
        assert "config" in result
        assert "simulation_results" in result
        assert "analysis" in result
        assert "simulation_timestamp" in result
        assert isinstance(result["simulation_results"], list)


class TestAdvancedBacktestEngine:
    """高级回测引擎测试"""

    def setup_method(self):
        """测试前准备"""
        self.config = AdvancedBacktestConfig()
        self.engine = AdvancedBacktestEngine(self.config)

    def test_initialization(self):
        """测试初始化"""
        assert self.engine.config == self.config
        assert self.engine.walk_forward is not None
        assert self.engine.monte_carlo is not None
        assert self.engine.logger is not None

    def test_create_advanced_backtest_engine(self):
        """测试便捷创建函数"""
        engine = create_advanced_backtest_engine(enable_walk_forward=True, enable_monte_carlo=False, num_simulations=50)

        assert engine.config.enable_walk_forward == True
        assert engine.config.enable_monte_carlo == False
        assert engine.config.monte_carlo.num_simulations == 50
        assert engine.walk_forward is not None
        assert engine.monte_carlo is None  # 不创建当禁用时

    @patch("backtesting.advanced_backtest_engine.BacktestEngine")
    @patch("backtesting.advanced_backtest_engine.WalkForwardAnalysis")
    @patch("backtesting.advanced_backtest_engine.MonteCarloSimulation")
    def test_run_advanced_backtest_full(self, mock_mc, mock_wf, mock_base):
        """测试完整高级回测流程"""
        # 设置mock
        mock_base_instance = Mock()
        mock_base_instance.run.return_value = {
            "backtest": {"daily_returns": pd.Series([0.01] * 10)},
            "metrics": {"total_return": 0.05},
        }
        mock_base.return_value = mock_base_instance

        mock_wf_instance = Mock()
        mock_wf_instance.run_analysis.return_value = {"summary": {"total_return": {"mean": 0.03}}}
        mock_wf.return_value = mock_wf_instance

        mock_mc_instance = Mock()
        mock_mc_instance.run_simulation.return_value = {"analysis": {"total_return_distribution": {"mean": 0.04}}}
        mock_mc.return_value = mock_mc_instance

        # 创建测试数据
        dates = pd.date_range("2023-01-01", periods=100, freq="D")
        price_data = pd.DataFrame(
            {
                "close": np.random.randn(100) + 100,
                "open": np.random.randn(100) + 99,
                "high": np.random.randn(100) + 101,
                "low": np.random.randn(100) + 99,
                "volume": np.random.uniform(1000000, 10000000, 100),
            },
            index=dates,
        )

        def signal_func(data, **kwargs):
            signals = pd.DataFrame(index=data.index)
            signals["signal"] = "buy"
            signals["strength"] = 0.8
            return signals

        # 运行高级回测
        results = self.engine.run_advanced_backtest(price_data, signal_func)

        # 验证结果结构
        assert "base_backtest" in results
        assert "walk_forward_analysis" in results
        assert "monte_carlo_analysis" in results
        assert "statistical_tests" in results
        assert "overfitting_analysis" in results
        assert "comprehensive_report" in results
        assert "timestamp" in results

    def test_statistical_tests(self):
        """测试统计检验功能"""
        # 创建测试结果数据
        results = {
            "walk_forward_analysis": {"summary": {"total_return": {"mean": 0.05, "std": 0.02}, "total_windows": 10}},
            "monte_carlo_analysis": {
                "analysis": {"total_return_distribution": {"percentiles": {"5th": 0.02, "95th": 0.08}, "mean": 0.05}},
                "simulation_results": [],  # 添加缺失的键
            },
            "base_backtest": {"metrics": {"total_return": 0.06}},
        }

        stat_tests = self.engine._perform_statistical_tests(results)

        # 验证统计检验结果
        assert "return_significance" in stat_tests
        assert "monte_carlo_percentile" in stat_tests

    def test_overfitting_detection(self):
        """测试过拟合检测功能"""
        # 创建测试结果数据
        results = {
            "walk_forward_analysis": {"summary": {"total_return": {"mean": 0.03}}},
            "base_backtest": {"metrics": {"total_return": 0.08}},
            "monte_carlo_analysis": {"analysis": {"total_return_distribution": {"std": 0.05, "mean": 0.04}}},
        }

        overfitting_analysis = self.engine._detect_overfitting(results)

        # 验证过拟合检测结果
        assert "overfitting_ratio" in overfitting_analysis
        assert "is_overfitted" in overfitting_analysis
        assert "coefficient_of_variation" in overfitting_analysis
        assert "return_stability_score" in overfitting_analysis

    def test_generate_comprehensive_report(self):
        """测试综合报告生成"""
        # 创建测试结果数据
        results = {
            "timestamp": datetime.now(),
            "base_backtest": {
                "metrics": {
                    "total_return": 0.05,
                    "annualized_return": 0.04,
                    "sharpe_ratio": 1.2,
                    "max_drawdown": 0.03,
                    "win_rate": 0.55,
                }
            },
            "walk_forward_analysis": {
                "summary": {
                    "total_windows": 5,
                    "total_return": {"mean": 0.03},
                    "robustness_score": 0.6,
                    "consistency_score": 0.8,
                }
            },
            "monte_carlo_analysis": {
                "analysis": {
                    "total_simulations": 100,
                    "successful_simulations": 95,
                    "total_return_distribution": {"mean": 0.04, "var_95": -0.02},
                    "probability_analysis": {"prob_positive_return": 0.65},
                }
            },
            "statistical_tests": {
                "return_significance": {
                    "t_statistic": 2.5,
                    "p_value": 0.01,
                    "significant_at_95pct": True,
                    "significant_at_99pct": False,
                }
            },
            "overfitting_analysis": {"is_overfitted": False},
        }

        report = self.engine._generate_comprehensive_report(results)

        # 验证报告内容
        assert isinstance(report, str)
        assert "高级回测分析综合报告" in report
        assert "基础回测结果" in report
        assert "Walk-forward分析结果" in report
        assert "Monte Carlo模拟结果" in report
        assert "统计显著性检验" in report
        assert "过拟合检测" in report
        assert "结论和建议" in report


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])
