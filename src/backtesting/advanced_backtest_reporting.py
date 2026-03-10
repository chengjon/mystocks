"""
高级回测引擎的统计与报告辅助函数。
"""

from __future__ import annotations

import math
from datetime import datetime
from typing import Any, Dict, Iterable

import numpy as np


def distribution_stats(values: Iterable[float]) -> Dict[str, Any]:
    """构建常用分布统计摘要。"""
    data = np.asarray(list(values), dtype=float)
    if data.size == 0:
        return {
            "mean": 0.0,
            "std": 0.0,
            "min": 0.0,
            "max": 0.0,
            "median": 0.0,
            "percentiles": {"5th": 0.0, "95th": 0.0},
            "var_95": 0.0,
        }

    return {
        "mean": float(np.mean(data)),
        "std": float(np.std(data)),
        "min": float(np.min(data)),
        "max": float(np.max(data)),
        "median": float(np.median(data)),
        "percentiles": {
            "5th": float(np.percentile(data, 5)),
            "95th": float(np.percentile(data, 95)),
        },
        "var_95": float(np.percentile(data, 5)),
    }


def t_cdf(value: float, degrees_of_freedom: int) -> float:
    """计算 t 分布 CDF，缺少 scipy 时退化到正态近似。"""
    try:
        from scipy.stats import t as t_dist

        return float(t_dist.cdf(value, degrees_of_freedom))
    except Exception:
        return 0.5 * (1 + math.erf(value / math.sqrt(2)))


def generate_comprehensive_report(results: Dict[str, Any]) -> str:
    """生成高级回测综合报告。"""
    timestamp = results.get("timestamp") or datetime.now()
    report_lines = [
        "高级回测分析综合报告",
        "=" * 80,
        f"分析时间: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
    ]

    if results.get("base_backtest"):
        base_metrics = results["base_backtest"]["metrics"]
        report_lines.extend(
            [
                "基础回测结果",
                f"  总收益率: {base_metrics.get('total_return', 0):.2%}",
                f"  年化收益率: {base_metrics.get('annualized_return', 0):.2%}",
                f"  夏普比率: {base_metrics.get('sharpe_ratio', 0):.3f}",
                f"  最大回撤: {base_metrics.get('max_drawdown', 0):.2%}",
                f"  胜率: {base_metrics.get('win_rate', 0):.2%}",
                "",
            ]
        )

    if results.get("walk_forward_analysis"):
        summary = results["walk_forward_analysis"]["summary"]
        report_lines.extend(
            [
                "Walk-forward分析结果",
                f"  分析窗口数: {summary.get('total_windows', 0)}",
                f"  平均收益率: {summary.get('total_return', {}).get('mean', 0):.2%}",
                f"  鲁棒性得分: {summary.get('robustness_score', 0):.2%}",
                f"  一致性得分: {summary.get('consistency_score', 0):.3f}",
                "",
            ]
        )

    if results.get("monte_carlo_analysis"):
        analysis = results["monte_carlo_analysis"]["analysis"]
        total_return_distribution = analysis.get("total_return_distribution", {})
        probability_analysis = analysis.get("probability_analysis", {})
        report_lines.extend(
            [
                "Monte Carlo模拟结果",
                f"  模拟次数: {analysis.get('successful_simulations', 0)}/{analysis.get('total_simulations', 0)}",
                f"  平均收益率: {total_return_distribution.get('mean', 0):.2%}",
                f"  95% VaR: {total_return_distribution.get('var_95', 0):.2%}",
                f"  正收益概率: {probability_analysis.get('prob_positive_return', 0):.2%}",
                "",
            ]
        )

    if results.get("statistical_tests"):
        stat_tests = results["statistical_tests"]
        report_lines.append("统计显著性检验")

        if "return_significance" in stat_tests:
            significance = stat_tests["return_significance"]
            report_lines.extend(
                [
                    f"  t统计量: {significance.get('t_statistic', 0):.3f}",
                    f"  p值: {significance.get('p_value', 1):.4f}",
                    f"  95%显著: {'是' if significance.get('significant_at_95pct', False) else '否'}",
                    f"  99%显著: {'是' if significance.get('significant_at_99pct', False) else '否'}",
                ]
            )

        if "monte_carlo_percentile" in stat_tests:
            percentile = stat_tests["monte_carlo_percentile"]
            report_lines.extend(
                [
                    f"  基准收益率: {percentile.get('base_return', 0):.2%}",
                    f"  90%置信区间: [{percentile.get('percentile_5th', 0):.2%}, {percentile.get('percentile_95th', 0):.2%}]",
                    f"  在置信区间内: {'是' if percentile.get('within_90pct_confidence', False) else '否'}",
                ]
            )

        report_lines.append("")

    if results.get("overfitting_analysis"):
        overfitting = results["overfitting_analysis"]
        report_lines.extend(
            [
                "过拟合检测",
                f"  过拟合比率: {overfitting.get('overfitting_ratio', 0):.3f}",
                f"  是否过拟合: {'是' if overfitting.get('is_overfitted', False) else '否'}",
                f"  变异系数: {overfitting.get('coefficient_of_variation', 0):.3f}",
                f"  稳定性得分: {overfitting.get('return_stability_score', 0):.3f}",
                "",
            ]
        )

    report_lines.append("结论和建议")
    if results.get("statistical_tests", {}).get("return_significance", {}).get("significant_at_95pct", False):
        report_lines.append("  ✅ 策略收益率在统计上显著，表现良好")
    else:
        report_lines.append("  ⚠️ 策略收益率统计显著性不足，需谨慎")

    if results.get("overfitting_analysis", {}).get("is_overfitted", False):
        report_lines.append("  ⚠️ 检测到过拟合迹象，建议调整策略复杂度")
    else:
        report_lines.append("  ✅ 未检测到明显过拟合，策略稳定性良好")

    report_lines.extend(["", "=" * 80])
    return "\n".join(report_lines)
