"""
高级回测引擎 (Advanced Backtest Engine)

Phase 5: 高级分析功能
- Walk-forward分析：滚动窗口验证
- Monte Carlo模拟：鲁棒性测试
- 统计显著性检验
- 过拟合检测

作者: MyStocks量化交易团队
创建时间: 2025-01-12
版本: 1.0.0
"""

import logging
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from src.ml_strategy.backtest.backtest_engine import BacktestConfig, BacktestEngine
from src.ml_strategy.backtest.performance_metrics import PerformanceMetrics
from src.ml_strategy.backtest.risk_metrics import RiskMetrics


@dataclass
class WalkForwardConfig:
    """Walk-forward分析配置"""

    initial_train_window: int = 252  # 初始训练窗口（交易日）
    test_window: int = 63  # 测试窗口（交易日）
    step_size: int = 21  # 步长（交易日）
    expanding_window: bool = True  # 是否使用扩展窗口
    min_train_window: int = 126  # 最小训练窗口
    max_train_window: int = 504  # 最大训练窗口


@dataclass
class MonteCarloConfig:
    """Monte Carlo模拟配置"""

    num_simulations: int = 1000  # 模拟次数
    bootstrap_sample_size: Optional[int] = None  # 自举样本大小
    random_seed: int = 42  # 随机种子
    parallel_processes: Optional[int] = None  # 并行进程数


@dataclass
class AdvancedBacktestConfig:
    """高级回测配置"""

    walk_forward: WalkForwardConfig = field(default_factory=WalkForwardConfig)
    monte_carlo: MonteCarloConfig = field(default_factory=MonteCarloConfig)
    base_config: BacktestConfig = field(default_factory=BacktestConfig)
    enable_walk_forward: bool = True
    enable_monte_carlo: bool = True
    confidence_level: float = 0.95  # 置信水平


class WalkForwardAnalysis:
    """
    Walk-forward分析引擎

    功能：
    - 滚动窗口验证
    - 扩展窗口验证
    - 多周期回测
    - 过拟合检测
    """


def __init__(self, config: WalkForwardConfig):
    self.config = config
    self.logger = logging.getLogger(f"{__name__}.WalkForwardAnalysis")


def run_analysis(self, price_data: pd.DataFrame, signals_func: callable, **kwargs) -> Dict[str, Any]:
    """
    执行Walk-forward分析

    参数：
        price_data: 价格数据
        signals_func: 信号生成函数
        **kwargs: 传递给信号函数的参数

    返回：
        dict: 分析结果
    """
    self.logger.info("开始Walk-forward分析")

    # 数据验证
    if not self._validate_data(price_data):
        raise ValueError("价格数据验证失败")

    # 生成分析窗口
    windows = self._generate_analysis_windows(price_data)

    # 执行逐窗口回测
    window_results = []
    for i, (train_data, test_data) in enumerate(windows):
        self.logger.info("执行窗口 {i + 1}/%s")

        # 生成测试信号
        test_signals = signals_func(test_data, **kwargs)

        # 执行回测
        backtest_engine = BacktestEngine()
        result = backtest_engine.run(test_data, test_signals)

        # 记录窗口信息
        window_result = {
            "window_id": i + 1,
            "train_period": (train_data.index[0], train_data.index[-1]),
            "test_period": (test_data.index[0], test_data.index[-1]),
            "train_size": len(train_data),
            "test_size": len(test_data),
            "result": result,
        }
        window_results.append(window_result)

    # 汇总分析结果
    summary = self._summarize_results(window_results)

    result = {
        "config": self.config,
        "windows": window_results,
        "summary": summary,
        "analysis_timestamp": datetime.now(),
    }

    self.logger.info("Walk-forward分析完成")
    return result


def _validate_data(self, price_data: pd.DataFrame) -> bool:
    """验证价格数据"""
    required_columns = ["open", "high", "low", "close", "volume"]
    if not all(col in price_data.columns for col in required_columns):
        self.logger.error("缺少必需列: %(required_columns)s")
        return False

    min_required_periods = self.config.initial_train_window + self.config.test_window
    if len(price_data) < min_required_periods:
        self.logger.error("数据长度不足: 需要至少%(min_required_periods)s个周期")
        return False

    return True


def _generate_analysis_windows(self, price_data: pd.DataFrame) -> List[Tuple[pd.DataFrame, pd.DataFrame]]:
    """生成分析窗口"""
    windows = []
    total_periods = len(price_data)

    start_idx = 0

    while True:
        if self.config.expanding_window:
            # 扩展窗口：训练窗口逐渐扩大
            train_end_idx = min(start_idx + self.config.initial_train_window, total_periods)
        else:
            # 滚动窗口：训练窗口固定大小
            train_end_idx = start_idx + self.config.initial_train_window

        test_end_idx = train_end_idx + self.config.test_window

        if test_end_idx > total_periods:
            break

        train_data = price_data.iloc[start_idx:train_end_idx]
        test_data = price_data.iloc[train_end_idx:test_end_idx]

        windows.append((train_data, test_data))

        start_idx += self.config.step_size

    self.logger.info("生成了 {len(windows)} 个分析窗口")
    return windows


def _summarize_results(self, window_results: List[Dict]) -> Dict[str, Any]:
    """汇总分析结果"""
    if not window_results:
        return {}

    # 提取各项指标
    total_returns = []
    sharpe_ratios = []
    max_drawdowns = []
    win_rates = []

    for w in window_results:
        metrics = w["result"]["metrics"]
        total_returns.append(metrics.get("total_return", 0))
        sharpe_ratios.append(metrics.get("sharpe_ratio", 0))
        max_drawdowns.append(metrics.get("max_drawdown", 0))
        win_rates.append(metrics.get("win_rate", 0))

    # 计算统计指标
    summary = {
        "total_windows": len(window_results),
        "total_return": {
            "mean": np.mean(total_returns),
            "std": np.std(total_returns),
            "min": np.min(total_returns),
            "max": np.max(total_returns),
            "median": np.median(total_returns),
        },
        "sharpe_ratio": {
            "mean": np.mean(sharpe_ratios),
            "std": np.std(sharpe_ratios),
            "min": np.min(sharpe_ratios),
            "max": np.max(sharpe_ratios),
            "median": np.median(sharpe_ratios),
        },
        "max_drawdown": {
            "mean": np.mean(max_drawdowns),
            "std": np.std(max_drawdowns),
            "min": np.min(max_drawdowns),
            "max": np.max(max_drawdowns),
            "median": np.median(max_drawdowns),
        },
        "win_rate": {
            "mean": np.mean(win_rates),
            "std": np.std(win_rates),
            "min": np.min(win_rates),
            "max": np.max(win_rates),
            "median": np.median(win_rates),
        },
        "robustness_score": self._calculate_robustness_score(total_returns),
        "consistency_score": self._calculate_consistency_score(total_returns),
    }

    return summary


def _calculate_robustness_score(self, returns: List[float]) -> float:
    """计算鲁棒性得分（正收益窗口比例）"""
    positive_returns = [r for r in returns if r > 0]
    return len(positive_returns) / len(returns) if returns else 0


def _calculate_consistency_score(self, returns: List[float]) -> float:
    """计算一致性得分（收益标准差的倒数）"""
    if not returns or np.std(returns) == 0:
        return 0
    return 1 / np.std(returns)


class MonteCarloSimulation:
    """
    Monte Carlo模拟引擎

    功能：
    - 自举重采样
    - 收益分布分析
    - 风险概率估计
    - 并行处理支持
    """


def __init__(self, config: MonteCarloConfig):
    self.config = config
    self.logger = logging.getLogger(f"{__name__}.MonteCarloSimulation")

    # 设置随机种子
    np.random.seed(self.config.random_seed)

    # 设置并行进程数
    if self.config.parallel_processes is None:
        self.config.parallel_processes = max(1, multiprocessing.cpu_count() - 1)


def run_simulation(self, returns: pd.Series, simulation_func: callable, **kwargs) -> Dict[str, Any]:
    """
    执行Monte Carlo模拟

    参数：
        returns: 历史收益率序列
        simulation_func: 模拟函数
        **kwargs: 传递给模拟函数的参数

    返回：
        dict: 模拟结果
    """
    self.logger.info("开始Monte Carlo模拟: {self.config.num_simulations} 次")

    # 数据验证
    if len(returns) < 30:
        raise ValueError("收益率数据长度不足，至少需要30个观测值")

    # 执行模拟（暂时使用顺序执行以避免multiprocessing问题）
    results = self._run_sequential_simulations(returns, simulation_func, **kwargs)

    # 分析结果
    analysis = self._analyze_simulation_results(results)

    result = {
        "config": self.config,
        "simulation_results": results,
        "analysis": analysis,
        "simulation_timestamp": datetime.now(),
    }

    self.logger.info("Monte Carlo模拟完成")
    return result


def _run_parallel_simulations(self, returns: pd.Series, simulation_func: callable, **kwargs) -> List[Dict]:
    """并行执行模拟"""
    results = []

    with ProcessPoolExecutor(max_workers=self.config.parallel_processes) as executor:
        # 提交所有模拟任务
        future_to_sim = {
            executor.submit(self._single_simulation, returns, simulation_func, sim_id, **kwargs): sim_id
            for sim_id in range(self.config.num_simulations)
        }

        # 收集结果
        for future in as_completed(future_to_sim):
            sim_id = future_to_sim[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as exc:
                self.logger.error("模拟 %(sim_id)s 失败: %(exc)s")
                results.append({"simulation_id": sim_id, "error": str(exc)})

    return sorted(results, key=lambda x: x.get("simulation_id", 0))


def _run_sequential_simulations(self, returns: pd.Series, simulation_func: callable, **kwargs) -> List[Dict]:
    """顺序执行模拟"""
    results = []

    for sim_id in range(self.config.num_simulations):
        try:
            result = self._single_simulation(returns, simulation_func, sim_id, **kwargs)
            results.append(result)
        except Exception as exc:
            self.logger.error("模拟 %(sim_id)s 失败: %(exc)s")
            results.append({"simulation_id": sim_id, "error": str(exc)})

    return results


def _single_simulation(self, returns: pd.Series, simulation_func: callable, sim_id: int, **kwargs) -> Dict:
    """单个模拟执行"""
    # 自举重采样
    bootstrap_returns = self._bootstrap_sample(returns)

    # 执行模拟函数
    result = simulation_func(bootstrap_returns, **kwargs)

    return {
        "simulation_id": sim_id,
        "bootstrap_returns": bootstrap_returns,
        "result": result,
    }


def _bootstrap_sample(self, returns: pd.Series) -> pd.Series:
    """自举重采样"""
    sample_size = self.config.bootstrap_sample_size or len(returns)
    indices = np.random.choice(len(returns), size=sample_size, replace=True)
    return returns.iloc[indices].reset_index(drop=True)


def _analyze_simulation_results(self, results: List[Dict]) -> Dict[str, Any]:
    """分析模拟结果"""
    # 过滤出成功的模拟
    successful_results = [r for r in results if "error" not in r]

    if not successful_results:
        return {"error": "所有模拟都失败了"}

    # 提取各项指标
    total_returns = []
    sharpe_ratios = []
    max_drawdowns = []
    win_rates = []

    for result in successful_results:
        metrics = result["result"].get("metrics", {})
        total_returns.append(metrics.get("total_return", 0))
        sharpe_ratios.append(metrics.get("sharpe_ratio", 0))
        max_drawdowns.append(metrics.get("max_drawdown", 0))
        win_rates.append(metrics.get("win_rate", 0))

    # 计算统计分布
    analysis = {
        "total_simulations": len(results),
        "successful_simulations": len(successful_results),
        "success_rate": len(successful_results) / len(results),
        "total_return_distribution": {
            "mean": np.mean(total_returns),
            "std": np.std(total_returns),
            "percentiles": {
                "5th": np.percentile(total_returns, 5),
                "25th": np.percentile(total_returns, 25),
                "50th": np.percentile(total_returns, 50),
                "75th": np.percentile(total_returns, 75),
                "95th": np.percentile(total_returns, 95),
            },
            "var_95": np.percentile(total_returns, 5),  # Value at Risk
            "cvar_95": np.mean([r for r in total_returns if r <= np.percentile(total_returns, 5)]),  # Conditional VaR
        },
        "sharpe_ratio_distribution": {
            "mean": np.mean(sharpe_ratios),
            "std": np.std(sharpe_ratios),
            "percentiles": {
                "5th": np.percentile(sharpe_ratios, 5),
                "25th": np.percentile(sharpe_ratios, 25),
                "50th": np.percentile(sharpe_ratios, 50),
                "75th": np.percentile(sharpe_ratios, 75),
                "95th": np.percentile(sharpe_ratios, 95),
            },
        },
        "max_drawdown_distribution": {
            "mean": np.mean(max_drawdowns),
            "std": np.std(max_drawdowns),
            "worst_case": np.max(max_drawdowns),
            "percentiles": {
                "5th": np.percentile(max_drawdowns, 5),
                "25th": np.percentile(max_drawdowns, 25),
                "50th": np.percentile(max_drawdowns, 50),
                "75th": np.percentile(max_drawdowns, 75),
                "95th": np.percentile(max_drawdowns, 95),
            },
        },
        "win_rate_distribution": {
            "mean": np.mean(win_rates),
            "std": np.std(win_rates),
            "percentiles": {
                "5th": np.percentile(win_rates, 5),
                "25th": np.percentile(win_rates, 25),
                "50th": np.percentile(win_rates, 50),
                "75th": np.percentile(win_rates, 75),
                "95th": np.percentile(win_rates, 95),
            },
        },
        "probability_analysis": {
            "prob_positive_return": np.mean([1 if r > 0 else 0 for r in total_returns]),
            "prob_sharpe_gt_1": np.mean([1 if r > 1 else 0 for r in sharpe_ratios]),
            "prob_max_dd_lt_20pct": np.mean([1 if r < 0.20 else 0 for r in max_drawdowns]),
        },
    }

    return analysis


def _create_simulation_function(self, price_data: pd.DataFrame, signals_func: callable, **kwargs):
    """创建可序列化的模拟函数（用于Monte Carlo并行处理）"""

    # 为了避免multiprocessing的pickle问题，我们返回一个静态方法
    def simulation_wrapper(bootstrap_returns, **sim_kwargs):
        # 使用相同的信号函数进行模拟
        simulated_signals = signals_func(price_data, **sim_kwargs)
        # 执行回测
        backtest_engine = BacktestEngine()
        sim_result = backtest_engine.run(price_data, simulated_signals)
        return sim_result

    return simulation_wrapper


class AdvancedBacktestEngine:
    """
    高级回测引擎主控制器

    功能：
    - 整合Walk-forward分析和Monte Carlo模拟
    - 统计显著性检验
    - 过拟合检测
    - 综合报告生成
    """


def __init__(self, config: AdvancedBacktestConfig):
    self.config = config
    self.walk_forward = WalkForwardAnalysis(config.walk_forward) if config.enable_walk_forward else None
    self.monte_carlo = MonteCarloSimulation(config.monte_carlo) if config.enable_monte_carlo else None

    self.logger = logging.getLogger(f"{__name__}.AdvancedBacktestEngine")

    # 基础组件
    self.base_engine = BacktestEngine(config.base_config)
    self.perf_metrics = PerformanceMetrics()
    self.risk_metrics = RiskMetrics()


def run_advanced_backtest(
    self,
    price_data: pd.DataFrame,
    signals_func: callable,
    benchmark_returns: Optional[pd.Series] = None,
    **kwargs,
) -> Dict[str, Any]:
    """
    执行高级回测分析

    参数：
        price_data: 价格数据
        signals_func: 信号生成函数
        benchmark_returns: 基准收益率
        **kwargs: 传递给信号函数的参数

    返回：
        dict: 完整高级回测结果
    """
    self.logger.info("开始高级回测分析")

    results = {
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
        self.logger.info("执行基础回测")
        base_signals = signals_func(price_data, **kwargs)
        base_result = self.base_engine.run(price_data, base_signals, benchmark_returns)
        results["base_backtest"] = base_result

        if self.walk_forward:
            self.logger.info("执行Walk-forward分析")
            wf_result = self.walk_forward.run_analysis(price_data, signals_func, **kwargs)
            results["walk_forward_analysis"] = wf_result

        if self.monte_carlo:
            self.logger.info("执行Monte Carlo模拟")
            daily_returns = base_result["backtest"]["daily_returns"]

            # 创建可序列化的模拟函数
            simulation_func = self._create_simulation_function(price_data, signals_func, **kwargs)
            mc_result = self.monte_carlo.run_simulation(daily_returns, simulation_func, **kwargs)
            results["monte_carlo_analysis"] = mc_result

        self.logger.info("执行统计显著性检验")
        stat_tests = self._perform_statistical_tests(results)
        results["statistical_tests"] = stat_tests

        self.logger.info("执行过拟合检测")
        overfitting_analysis = self._detect_overfitting(results)
        results["overfitting_analysis"] = overfitting_analysis

        self.logger.info("生成综合报告")
        comprehensive_report = self._generate_comprehensive_report(results)
        results["comprehensive_report"] = comprehensive_report

    except Exception as e:
        self.logger.error("高级回测分析失败: %(e)s")
        results["error"] = str(e)

    self.logger.info("高级回测分析完成")
    return results


def _perform_statistical_tests(self, results: Dict[str, Any]) -> Dict[str, Any]:
    """执行统计显著性检验"""
    tests = {}

    if results.get("walk_forward_analysis"):
        wf_summary = results["walk_forward_analysis"]["summary"]

        # t检验：检验平均收益率是否显著大于0
        mean_return = wf_summary["total_return"]["mean"]
        std_return = wf_summary["total_return"]["std"]
        n_windows = wf_summary["total_windows"]

        if std_return > 0:
            t_stat = mean_return / (std_return / np.sqrt(n_windows))
            p_value = 2 * (1 - self._t_cdf(abs(t_stat), n_windows - 1))

            tests["return_significance"] = {
                "t_statistic": t_stat,
                "p_value": p_value,
                "significant_at_95pct": p_value < 0.05,
                "significant_at_99pct": p_value < 0.01,
            }

    if results.get("monte_carlo_analysis"):
        mc_analysis = results["monte_carlo_analysis"]["analysis"]
        base_return = results["base_backtest"]["metrics"]["total_return"]

        # 计算在Monte Carlo分布中的分位数
        return_distribution = mc_analysis["total_return_distribution"]
        percentile_5th = return_distribution["percentiles"]["5th"]
        percentile_95th = return_distribution["percentiles"]["95th"]

        tests["monte_carlo_percentile"] = {
            "base_return": base_return,
            "percentile_5th": percentile_5th,
            "percentile_95th": percentile_95th,
            "within_90pct_confidence": percentile_5th <= base_return <= percentile_95th,
            "probability_better_than_random": np.mean(
                [
                    1 if r > 0 else 0
                    for r in [
                        result["result"]["metrics"]["total_return"]
                        for result in results["monte_carlo_analysis"]["simulation_results"]
                        if "result" in result
                    ]
                ]
            ),
        }

    return tests


def _detect_overfitting(self, results: Dict[str, Any]) -> Dict[str, Any]:
    """检测过拟合"""
    analysis = {}

    if results.get("walk_forward_analysis") and results.get("base_backtest"):
        wf_summary = results["walk_forward_analysis"]["summary"]
        base_metrics = results["base_backtest"]["metrics"]

        # 比较训练期和测试期表现
        wf_avg_return = wf_summary["total_return"]["mean"]
        base_return = base_metrics["total_return"]

        # 过拟合指标
        overfitting_ratio = base_return / wf_avg_return if wf_avg_return != 0 else float("inf")

        analysis.update(
            {
                "overfitting_ratio": overfitting_ratio,
                "is_overfitted": overfitting_ratio > 2.0,  # 经验阈值
                "base_return": base_return,
                "walk_forward_avg_return": wf_avg_return,
                "performance_decay": wf_avg_return - base_return,
            }
        )

    # 稳定性分析
    if results.get("monte_carlo_analysis"):
        mc_analysis = results["monte_carlo_analysis"]["analysis"]
        return_std = mc_analysis["total_return_distribution"]["std"]
        return_mean = mc_analysis["total_return_distribution"]["mean"]

        # 变异系数 (CV)
        coefficient_of_variation = return_std / abs(return_mean) if return_mean != 0 else float("inf")

        analysis.update(
            {
                "coefficient_of_variation": coefficient_of_variation,
                "high_variability": coefficient_of_variation > 1.0,  # 经验阈值
                "return_stability_score": 1 / (1 + coefficient_of_variation),  # 0-1之间的稳定性得分
            }
        )

    return analysis


def _generate_comprehensive_report(self, results: Dict[str, Any]) -> str:
    """生成综合报告"""
    report_lines = [
        "=" * 80,
        "高级回测分析综合报告",
        "=" * 80,
        f"分析时间: {results['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}",
        "",
    ]

    # 基础回测结果
    if results.get("base_backtest"):
        base = results["base_backtest"]["metrics"]
        report_lines.extend(
            [
                "📊 基础回测结果:",
                f"  总收益率: {base['total_return']:.2%}",
                f"  年化收益率: {base['annualized_return']:.2%}",
                f"  夏普比率: {base['sharpe_ratio']:.3f}",
                f"  最大回撤: {base['max_drawdown']:.2%}",
                f"  胜率: {base['win_rate']:.2%}",
                "",
            ]
        )

    # Walk-forward分析结果
    if results.get("walk_forward_analysis"):
        wf = results["walk_forward_analysis"]["summary"]
        report_lines.extend(
            [
                "🔄 Walk-forward分析结果:",
                f"  分析窗口数: {wf['total_windows']}",
                f"  平均收益率: {wf['total_return']['mean']:.2%}",
                f"  鲁棒性得分: {wf['robustness_score']:.2%}",
                f"  一致性得分: {wf['consistency_score']:.3f}",
                "",
            ]
        )

    # Monte Carlo分析结果
    if results.get("monte_carlo_analysis"):
        mc = results["monte_carlo_analysis"]["analysis"]
        report_lines.extend(
            [
                "🎲 Monte Carlo模拟结果:",
                f"  模拟次数: {mc['successful_simulations']}/{mc['total_simulations']}",
                f"  平均收益率: {mc['total_return_distribution']['mean']:.2%}",
                f"  95% VaR: {mc['total_return_distribution']['var_95']:.2%}",
                f"  正收益概率: {mc['probability_analysis']['prob_positive_return']:.2%}",
                "",
            ]
        )

    # 统计检验结果
    if results.get("statistical_tests"):
        stat = results["statistical_tests"]
        report_lines.extend(
            [
                "📈 统计显著性检验:",
            ]
        )

        if "return_significance" in stat:
            sig = stat["return_significance"]
            report_lines.extend(
                [
                    "  收益率显著性 (t检验):",
                    f"    t统计量: {sig['t_statistic']:.3f}",
                    f"    p值: {sig['p_value']:.4f}",
                    f"    95%显著: {'是' if sig['significant_at_95pct'] else '否'}",
                    f"    99%显著: {'是' if sig['significant_at_99pct'] else '否'}",
                ]
            )

        if "monte_carlo_percentile" in stat:
            mc_pct = stat["monte_carlo_percentile"]
            report_lines.extend(
                [
                    "  Monte Carlo分位数分析:",
                    f"    基准收益率: {
                        mc_pct['base_return']:.2%}",
                    f"    90%置信区间: [{
                        mc_pct['percentile_5th']:.2%}, {
                        mc_pct['percentile_95th']:.2%}]",
                    f"    在置信区间内: {
                        '是' if mc_pct['within_90pct_confidence'] else '否'}",
                ]
            )

        report_lines.append("")

    # 过拟合检测结果
    if results.get("overfitting_analysis"):
        of = results["overfitting_analysis"]
        report_lines.extend(
            [
                "🎯 过拟合检测:",
                f"  过拟合比率: {of.get('overfitting_ratio', 'N/A')}",
                f"  是否过拟合: {'是' if of.get('is_overfitted', False) else '否'}",
                f"  变异系数: {of.get('coefficient_of_variation', 'N/A')}",
                f"  稳定性得分: {of.get('return_stability_score', 'N/A')}",
                "",
            ]
        )

    # 结论和建议
    report_lines.extend(
        [
            "📋 结论和建议:",
        ]
    )

    # 基于分析结果给出建议
    if results.get("statistical_tests"):
        stat = results["statistical_tests"]
        if stat.get("return_significance", {}).get("significant_at_95pct", False):
            report_lines.append("  ✅ 策略收益率在统计上显著，表现良好")
        else:
            report_lines.append("  ⚠️ 策略收益率统计显著性不足，需谨慎")

    if results.get("overfitting_analysis"):
        of = results["overfitting_analysis"]
        if of.get("is_overfitted", False):
            report_lines.append("  ⚠️ 检测到过拟合迹象，建议调整策略复杂度")
        else:
            report_lines.append("  ✅ 未检测到明显过拟合，策略稳定性良好")

    report_lines.extend(["", "=" * 80])

    return "\n".join(report_lines)


def _t_cdf(self, t: float, df: int) -> float:
    """计算t分布的累积分布函数（简化实现）"""
    # 使用正态分布近似（对于大样本）
    from scipy.stats import t as t_dist

    return t_dist.cdf(t, df)


# 便捷函数
def create_advanced_backtest_engine(
    enable_walk_forward: bool = True,
    enable_monte_carlo: bool = True,
    num_simulations: int = 1000,
    initial_train_window: int = 252,
    test_window: int = 63,
) -> AdvancedBacktestEngine:
    """
    创建高级回测引擎的便捷函数

    参数：
        enable_walk_forward: 是否启用Walk-forward分析
        enable_monte_carlo: 是否启用Monte Carlo模拟
        num_simulations: Monte Carlo模拟次数
        initial_train_window: 初始训练窗口
        test_window: 测试窗口

    返回：
        AdvancedBacktestEngine: 配置好的高级回测引擎
    """
    config = AdvancedBacktestConfig(
        walk_forward=WalkForwardConfig(initial_train_window=initial_train_window, test_window=test_window),
        monte_carlo=MonteCarloConfig(num_simulations=num_simulations),
        enable_walk_forward=enable_walk_forward,
        enable_monte_carlo=enable_monte_carlo,
    )

    return AdvancedBacktestEngine(config)


if __name__ == "__main__":
    # 测试代码
    print("高级回测引擎测试")
    print("=" * 80)

    # 生成测试数据
    np.random.seed(42)
    test_n = 500
    test_dates = pd.date_range("2023-01-01", periods=test_n, freq="D")

    # 价格数据
    test_close_prices = 100 + np.cumsum(np.random.randn(test_n) * 0.5 + 0.01)
    test_price_data = pd.DataFrame(
        {
            "open": test_close_prices + np.random.randn(test_n) * 0.3,
            "high": test_close_prices + np.abs(np.random.randn(test_n)) * 0.5,
            "low": test_close_prices - np.abs(np.random.randn(test_n)) * 0.5,
            "close": test_close_prices,
            "volume": np.random.uniform(1000000, 10000000, test_n),
        },
        index=test_dates,
    )

    # 简单信号函数（示例）
    def simple_signal_func(price_data, **kwargs):
        signals = pd.DataFrame(index=price_data.index)
        signals["signal"] = None
        signals["strength"] = 0.0

        close_prices = price_data["close"]
        sma_20 = close_prices.rolling(20).mean()
        sma_50 = close_prices.rolling(50).mean()

        # 简单的均线交叉策略
        for i in range(len(close_prices)):
            if i >= 50:
                if sma_20.iloc[i] > sma_50.iloc[i] and sma_20.iloc[i - 1] <= sma_50.iloc[i - 1]:
                    signals.iloc[i] = ["buy", 0.8]
                elif sma_20.iloc[i] < sma_50.iloc[i] and sma_20.iloc[i - 1] >= sma_50.iloc[i - 1]:
                    signals.iloc[i] = ["sell", 0.8]

        return signals

    # Create advanced backtest engine
    engine = create_advanced_backtest_engine(
        enable_walk_forward=True,
        enable_monte_carlo=True,
        num_simulations=100,
        initial_train_window=200,
        test_window=50,
    )

    # Run advanced backtest
    print("Running advanced backtest analysis...")
    results = engine.run_advanced_backtest(test_price_data, simple_signal_func)

    # Print comprehensive report
    if "comprehensive_report" in results and results["comprehensive_report"]:
        print(results["comprehensive_report"])
    else:
        print("Analysis failed or no report generated")

    print("\nTest completed!")
