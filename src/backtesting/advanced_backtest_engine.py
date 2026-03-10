"""
高级回测引擎 (Advanced Backtest Engine)

包含 Walk-forward 分析、Monte Carlo 模拟、统计显著性检验与过拟合检测。
"""

from __future__ import annotations

import logging
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from src.backtesting.advanced_backtest_reporting import (
    distribution_stats,
    generate_comprehensive_report,
    t_cdf,
)
from src.ml_strategy.backtest.backtest_engine import BacktestConfig, BacktestEngine
from src.ml_strategy.backtest.performance_metrics import PerformanceMetrics
from src.ml_strategy.backtest.risk_metrics import RiskMetrics

logger = logging.getLogger(__name__)


@dataclass
class WalkForwardConfig:
    """Walk-forward 分析配置。"""

    initial_train_window: int = 252
    test_window: int = 63
    step_size: int = 21
    expanding_window: bool = True
    min_train_window: int = 126
    max_train_window: int = 504


@dataclass
class MonteCarloConfig:
    """Monte Carlo 模拟配置。"""

    num_simulations: int = 1000
    bootstrap_sample_size: Optional[int] = None
    random_seed: int = 42
    parallel_processes: Optional[int] = None


@dataclass
class AdvancedBacktestConfig:
    """高级回测总配置。"""

    walk_forward: WalkForwardConfig = field(default_factory=WalkForwardConfig)
    monte_carlo: MonteCarloConfig = field(default_factory=MonteCarloConfig)
    base_config: BacktestConfig = field(default_factory=BacktestConfig)
    enable_walk_forward: bool = True
    enable_monte_carlo: bool = True
    confidence_level: float = 0.95


class WalkForwardAnalysis:
    """Walk-forward 分析引擎。"""

    def __init__(self, config: WalkForwardConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.WalkForwardAnalysis")

    def run_analysis(self, price_data: pd.DataFrame, signals_func: Callable[..., Any], **kwargs) -> Dict[str, Any]:
        """执行 Walk-forward 分析。"""
        self.logger.info("开始Walk-forward分析")
        if not self._validate_data(price_data):
            raise ValueError("价格数据验证失败")

        window_results: List[Dict[str, Any]] = []
        for index, (train_data, test_data) in enumerate(self._generate_analysis_windows(price_data), start=1):
            self.logger.info("执行窗口 %s", index)
            test_signals = signals_func(test_data, **kwargs)
            result = BacktestEngine().run(test_data, test_signals)
            window_results.append(
                {
                    "window_id": index,
                    "train_period": (train_data.index[0], train_data.index[-1]),
                    "test_period": (test_data.index[0], test_data.index[-1]),
                    "train_size": len(train_data),
                    "test_size": len(test_data),
                    "result": result,
                }
            )

        return {
            "config": self.config,
            "windows": window_results,
            "summary": self._summarize_results(window_results),
            "analysis_timestamp": datetime.now(),
        }

    def _validate_data(self, price_data: pd.DataFrame) -> bool:
        required_columns = ["open", "high", "low", "close", "volume"]
        if not all(column in price_data.columns for column in required_columns):
            self.logger.error("缺少必需列: %s", required_columns)
            return False

        minimum_periods = self.config.initial_train_window + self.config.test_window
        if len(price_data) < minimum_periods:
            self.logger.error("数据长度不足: 需要至少%s个周期", minimum_periods)
            return False

        return True

    def _generate_analysis_windows(self, price_data: pd.DataFrame) -> List[Tuple[pd.DataFrame, pd.DataFrame]]:
        windows: List[Tuple[pd.DataFrame, pd.DataFrame]] = []
        total_periods = len(price_data)
        start_idx = 0
        minimum_train_window = min(self.config.min_train_window, self.config.initial_train_window)

        while True:
            if self.config.expanding_window:
                train_start_idx = 0
                train_end_idx = start_idx + self.config.initial_train_window
            else:
                train_start_idx = start_idx
                train_end_idx = train_start_idx + self.config.initial_train_window

            test_start_idx = train_end_idx
            test_end_idx = test_start_idx + self.config.test_window

            if test_end_idx > total_periods:
                break

            train_data = price_data.iloc[train_start_idx:train_end_idx]
            if len(train_data) > self.config.max_train_window:
                train_data = train_data.iloc[-self.config.max_train_window :]

            if len(train_data) < minimum_train_window:
                break

            test_data = price_data.iloc[test_start_idx:test_end_idx]
            windows.append((train_data, test_data))
            start_idx += self.config.step_size

        return windows

    def _summarize_results(self, window_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        metric_values = {"total_return": [], "sharpe_ratio": [], "max_drawdown": [], "win_rate": []}

        for window in window_results:
            metrics = window.get("result", {}).get("metrics", {})
            for key in metric_values:
                metric_values[key].append(float(metrics.get(key, 0)))

        total_returns = metric_values["total_return"]
        return {
            "total_windows": len(window_results),
            "total_return": distribution_stats(total_returns),
            "sharpe_ratio": distribution_stats(metric_values["sharpe_ratio"]),
            "max_drawdown": distribution_stats(metric_values["max_drawdown"]),
            "win_rate": distribution_stats(metric_values["win_rate"]),
            "robustness_score": self._calculate_robustness_score(total_returns),
            "consistency_score": self._calculate_consistency_score(total_returns),
        }

    def _calculate_robustness_score(self, returns: List[float]) -> float:
        positive_returns = [value for value in returns if value > 0]
        return len(positive_returns) / len(returns) if returns else 0.0

    def _calculate_consistency_score(self, returns: List[float]) -> float:
        if not returns:
            return 0.0
        std_value = float(np.std(returns))
        return 0.0 if std_value == 0 else 1 / std_value


class MonteCarloSimulation:
    """Monte Carlo 模拟引擎。"""

    def __init__(self, config: MonteCarloConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.MonteCarloSimulation")
        np.random.seed(self.config.random_seed)
        if self.config.parallel_processes is None:
            self.config.parallel_processes = max(1, multiprocessing.cpu_count() - 1)

    def run_simulation(self, returns: pd.Series, simulation_func: Callable[..., Any], **kwargs) -> Dict[str, Any]:
        """执行 Monte Carlo 模拟。"""
        self.logger.info("开始Monte Carlo模拟: %s 次", self.config.num_simulations)
        if len(returns) < 30:
            raise ValueError("收益率数据长度不足，至少需要30个观测值")

        simulation_results = self._run_sequential_simulations(returns, simulation_func, **kwargs)
        return {
            "config": self.config,
            "simulation_results": simulation_results,
            "analysis": self._analyze_simulation_results(simulation_results),
            "simulation_timestamp": datetime.now(),
        }

    def _run_parallel_simulations(self, returns: pd.Series, simulation_func: Callable[..., Any], **kwargs) -> List[Dict]:
        results: List[Dict[str, Any]] = []
        with ProcessPoolExecutor(max_workers=self.config.parallel_processes) as executor:
            future_map = {
                executor.submit(self._single_simulation, returns, simulation_func, sim_id, **kwargs): sim_id
                for sim_id in range(self.config.num_simulations)
            }
            for future in as_completed(future_map):
                sim_id = future_map[future]
                try:
                    results.append(future.result())
                except Exception as error:
                    self.logger.error("模拟 %s 失败: %s", sim_id, error)
                    results.append({"simulation_id": sim_id, "error": str(error)})
        return sorted(results, key=lambda item: item.get("simulation_id", 0))

    def _run_sequential_simulations(self, returns: pd.Series, simulation_func: Callable[..., Any], **kwargs) -> List[Dict]:
        results: List[Dict[str, Any]] = []
        for sim_id in range(self.config.num_simulations):
            try:
                results.append(self._single_simulation(returns, simulation_func, sim_id, **kwargs))
            except Exception as error:
                self.logger.error("模拟 %s 失败: %s", sim_id, error)
                results.append({"simulation_id": sim_id, "error": str(error)})
        return results

    def _single_simulation(
        self,
        returns: pd.Series,
        simulation_func: Callable[..., Any],
        sim_id: int,
        **kwargs,
    ) -> Dict[str, Any]:
        bootstrap_returns = self._bootstrap_sample(returns)
        return {
            "simulation_id": sim_id,
            "bootstrap_returns": bootstrap_returns,
            "result": simulation_func(bootstrap_returns, **kwargs),
        }

    def _bootstrap_sample(self, returns: pd.Series) -> pd.Series:
        sample_size = self.config.bootstrap_sample_size or len(returns)
        indices = np.random.choice(len(returns), size=sample_size, replace=True)
        return returns.iloc[indices].reset_index(drop=True)

    def _analyze_simulation_results(self, results: List[Dict]) -> Dict[str, Any]:
        successful_results = [item for item in results if "result" in item and "metrics" in item["result"]]
        total_returns = [float(item["result"]["metrics"].get("total_return", 0)) for item in successful_results]
        sharpe_ratios = [float(item["result"]["metrics"].get("sharpe_ratio", 0)) for item in successful_results]
        max_drawdowns = [float(item["result"]["metrics"].get("max_drawdown", 0)) for item in successful_results]
        win_rates = [float(item["result"]["metrics"].get("win_rate", 0)) for item in successful_results]

        total_simulations = len(results)
        successful_simulations = len(successful_results)
        success_rate = successful_simulations / total_simulations if total_simulations else 0.0

        return {
            "total_simulations": total_simulations,
            "successful_simulations": successful_simulations,
            "success_rate": success_rate,
            "total_return_distribution": distribution_stats(total_returns),
            "sharpe_ratio_distribution": distribution_stats(sharpe_ratios),
            "max_drawdown_distribution": distribution_stats(max_drawdowns),
            "win_rate_distribution": distribution_stats(win_rates),
            "probability_analysis": {
                "prob_positive_return": float(np.mean(np.array(total_returns) > 0)) if total_returns else 0.0,
                "prob_sharpe_above_1": float(np.mean(np.array(sharpe_ratios) > 1)) if sharpe_ratios else 0.0,
                "prob_drawdown_below_10pct": float(np.mean(np.array(max_drawdowns) < 0.1)) if max_drawdowns else 0.0,
            },
        }


class AdvancedBacktestEngine:
    """高级回测引擎主控制器。"""

    def __init__(self, config: AdvancedBacktestConfig):
        self.config = config
        self.walk_forward = WalkForwardAnalysis(config.walk_forward) if config.enable_walk_forward else None
        self.monte_carlo = MonteCarloSimulation(config.monte_carlo) if config.enable_monte_carlo else None
        self.logger = logging.getLogger(f"{__name__}.AdvancedBacktestEngine")
        self.base_engine = BacktestEngine(config.base_config)
        self.perf_metrics = PerformanceMetrics()
        self.risk_metrics = RiskMetrics()

    def run_advanced_backtest(
        self,
        price_data: pd.DataFrame,
        signals_func: Callable[..., Any],
        benchmark_returns: Optional[pd.Series] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """执行高级回测分析。"""
        self.logger.info("开始高级回测分析")
        results: Dict[str, Any] = {
            "config": self.config,
            "timestamp": datetime.now(),
            "base_backtest": None,
            "walk_forward_analysis": None,
            "monte_carlo_analysis": None,
            "statistical_tests": None,
            "overfitting_analysis": None,
            "comprehensive_report": None,
        }

        try:
            base_signals = signals_func(price_data, **kwargs)
            base_engine = BacktestEngine(self.config.base_config)
            base_result = base_engine.run(price_data, base_signals, benchmark_returns)
            results["base_backtest"] = base_result

            if self.config.enable_walk_forward:
                walk_forward_engine = WalkForwardAnalysis(self.config.walk_forward)
                results["walk_forward_analysis"] = walk_forward_engine.run_analysis(price_data, signals_func, **kwargs)

            if self.config.enable_monte_carlo:
                monte_carlo_engine = MonteCarloSimulation(self.config.monte_carlo)
                daily_returns = base_result.get("backtest", {}).get("daily_returns", pd.Series(dtype=float))
                simulation_func = self._create_simulation_function()
                results["monte_carlo_analysis"] = monte_carlo_engine.run_simulation(daily_returns, simulation_func)

            results["statistical_tests"] = self._perform_statistical_tests(results)
            results["overfitting_analysis"] = self._detect_overfitting(results)
            results["comprehensive_report"] = self._generate_comprehensive_report(results)
        except Exception as error:
            self.logger.error("高级回测分析失败: %s", error)
            results["error"] = str(error)

        self.logger.info("高级回测分析完成")
        return results

    def _create_simulation_function(self) -> Callable[..., Dict[str, Any]]:
        def simulation_func(returns: pd.Series, **_kwargs) -> Dict[str, Any]:
            returns_series = pd.Series(returns).fillna(0.0)
            total_return = float((1 + returns_series).prod() - 1) if not returns_series.empty else 0.0
            std_value = float(returns_series.std()) if len(returns_series) > 1 else 0.0
            mean_value = float(returns_series.mean()) if not returns_series.empty else 0.0
            sharpe_ratio = mean_value / std_value if std_value else 0.0
            cumulative_returns = (1 + returns_series).cumprod()
            rolling_peak = cumulative_returns.cummax()
            drawdowns = (rolling_peak - cumulative_returns) / rolling_peak.replace(0, np.nan)
            max_drawdown = float(drawdowns.fillna(0).max()) if not returns_series.empty else 0.0
            win_rate = float((returns_series > 0).mean()) if not returns_series.empty else 0.0
            return {
                "metrics": {
                    "total_return": total_return,
                    "sharpe_ratio": sharpe_ratio,
                    "max_drawdown": max_drawdown,
                    "win_rate": win_rate,
                }
            }

        return simulation_func

    def _perform_statistical_tests(self, results: Dict[str, Any]) -> Dict[str, Any]:
        tests: Dict[str, Any] = {}
        walk_forward_summary = results.get("walk_forward_analysis", {}).get("summary")
        if walk_forward_summary:
            mean_return = walk_forward_summary["total_return"]["mean"]
            std_return = walk_forward_summary["total_return"].get("std", 0.0)
            total_windows = walk_forward_summary["total_windows"]
            if std_return > 0 and total_windows > 1:
                t_statistic = mean_return / (std_return / np.sqrt(total_windows))
                p_value = 2 * (1 - t_cdf(abs(t_statistic), total_windows - 1))
            else:
                t_statistic = 0.0
                p_value = 1.0

            tests["return_significance"] = {
                "t_statistic": float(t_statistic),
                "p_value": float(p_value),
                "significant_at_95pct": p_value < 0.05,
                "significant_at_99pct": p_value < 0.01,
            }

        monte_carlo_analysis = results.get("monte_carlo_analysis", {}).get("analysis")
        base_metrics = results.get("base_backtest", {}).get("metrics", {})
        if monte_carlo_analysis and base_metrics:
            distribution = monte_carlo_analysis["total_return_distribution"]
            base_return = float(base_metrics.get("total_return", 0))
            tests["monte_carlo_percentile"] = {
                "base_return": base_return,
                "percentile_5th": distribution["percentiles"]["5th"],
                "percentile_95th": distribution["percentiles"]["95th"],
                "within_90pct_confidence": distribution["percentiles"]["5th"]
                <= base_return
                <= distribution["percentiles"]["95th"],
            }

        return tests

    def _detect_overfitting(self, results: Dict[str, Any]) -> Dict[str, Any]:
        base_return = float(results.get("base_backtest", {}).get("metrics", {}).get("total_return", 0))
        walk_forward_mean = float(
            results.get("walk_forward_analysis", {}).get("summary", {}).get("total_return", {}).get("mean", 0)
        )
        monte_carlo_distribution = results.get("monte_carlo_analysis", {}).get("analysis", {}).get(
            "total_return_distribution",
            {},
        )

        denominator = abs(walk_forward_mean) if walk_forward_mean else 1e-9
        overfitting_ratio = base_return / denominator
        monte_carlo_mean = float(monte_carlo_distribution.get("mean", 0))
        monte_carlo_std = float(monte_carlo_distribution.get("std", 0))
        coefficient_of_variation = abs(monte_carlo_std / monte_carlo_mean) if monte_carlo_mean else 0.0
        return_stability_score = 1 / (1 + coefficient_of_variation) if coefficient_of_variation >= 0 else 0.0

        return {
            "overfitting_ratio": float(overfitting_ratio),
            "is_overfitted": overfitting_ratio > 1.5 or coefficient_of_variation > 1.0,
            "coefficient_of_variation": float(coefficient_of_variation),
            "return_stability_score": float(return_stability_score),
        }

    def _generate_comprehensive_report(self, results: Dict[str, Any]) -> str:
        return generate_comprehensive_report(results)


def create_advanced_backtest_engine(
    enable_walk_forward: bool = True,
    enable_monte_carlo: bool = True,
    num_simulations: int = 1000,
    initial_train_window: int = 252,
    test_window: int = 63,
) -> AdvancedBacktestEngine:
    """创建高级回测引擎便捷函数。"""
    config = AdvancedBacktestConfig(
        walk_forward=WalkForwardConfig(initial_train_window=initial_train_window, test_window=test_window),
        monte_carlo=MonteCarloConfig(num_simulations=num_simulations),
        enable_walk_forward=enable_walk_forward,
        enable_monte_carlo=enable_monte_carlo,
    )
    return AdvancedBacktestEngine(config)


__all__ = [
    "AdvancedBacktestConfig",
    "AdvancedBacktestEngine",
    "BacktestEngine",
    "MonteCarloConfig",
    "MonteCarloSimulation",
    "WalkForwardAnalysis",
    "WalkForwardConfig",
    "create_advanced_backtest_engine",
]
