"""
Chip Distribution Analysis Module for MyStocks Advanced Quantitative Analysis
A股量化分析平台筹码分布分析功能

This module provides comprehensive chip distribution analysis including:
- Cost distribution analysis based on cost transformation principles
- Chip concentration and peak analysis
- Winning probability calculation based on chip distribution
- Chip flow dynamics and cost area identification
- Long-term vs short-term chip distribution analysis
"""

from datetime import datetime
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd

from src.advanced_analysis import AnalysisResult, AnalysisType

def _generate_chip_recommendations(
    self,
    winning_probability: Optional[WinningProbability],
    cost_analysis: Optional[CostAreaAnalysis],
    concentration: Optional[ChipConcentration],
) -> Dict[str, Any]:
    """生成筹码分析建议"""
    recommendations = {}

    try:
        # 基于获胜概率的建议
        if winning_probability:
            max_prob = max(
                winning_probability.break_up_prob,
                winning_probability.break_down_prob,
                winning_probability.hold_prob,
            )

            if winning_probability.break_up_prob == max_prob and winning_probability.break_up_prob > 0.6:
                primary_signal = "bullish"
                action = f"建议买入，向上突破概率较高 ({winning_probability.break_up_prob:.1%})"
                confidence = "high" if winning_probability.break_up_prob > 0.7 else "medium"
            elif winning_probability.break_down_prob == max_prob and winning_probability.break_down_prob > 0.6:
                primary_signal = "bearish"
                action = f"建议卖出，向下突破概率较高 ({winning_probability.break_down_prob:.1%})"
                confidence = "high" if winning_probability.break_down_prob > 0.7 else "medium"
            else:
                primary_signal = "neutral"
                action = "建议观望，市场震荡概率较高"
                confidence = "low"
        else:
            primary_signal = "unknown"
            action = "筹码分布分析不足，建议结合其他指标判断"
            confidence = "low"

        # 考虑成本区压力
        if cost_analysis:
            if cost_analysis.cost_pressure == "bearish" and cost_analysis.pressure_strength > 0.5:
                action += " (成本压力向下，需谨慎)"
            elif cost_analysis.cost_pressure == "bullish" and cost_analysis.pressure_strength > 0.5:
                action += " (成本压力向上，可积极)"

        # 考虑筹码集中度
        if concentration and concentration.concentration_index > 0.8:
            action += " (筹码高度集中，突破可能性大)"

        recommendations.update(
            {
                "primary_signal": primary_signal,
                "recommended_action": action,
                "confidence_level": confidence,
                "optimal_entry_exit": (
                    {
                        "entry_price": winning_probability.optimal_entry if winning_probability else None,
                        "exit_price": winning_probability.optimal_exit if winning_probability else None,
                        "risk_reward_ratio": winning_probability.risk_reward_ratio if winning_probability else None,
                    }
                    if winning_probability
                    else None
                ),
                "key_levels": {
                    "equilibrium_price": cost_analysis.equilibrium_price if cost_analysis else None,
                    "peak_price": concentration.peak_price if concentration else None,
                    "main_cost_area": concentration.main_cost_area if concentration else None,
                },
            }
        )

    except Exception as e:
        print(f"Error generating chip recommendations: {e}")
        recommendations = {
            "primary_signal": "unknown",
            "recommended_action": "分析过程中出现错误，建议观望",
            "confidence_level": "low",
        }

    return recommendations


def _assess_chip_risk(
    self,
    chip_distribution: pd.Series,
    flow_dynamics: Optional[ChipFlowDynamics],
    winning_probability: Optional[WinningProbability],
) -> Dict[str, Any]:
    """评估筹码风险"""
    risk_assessment = {}

    try:
        # 筹码分布风险
        if chip_distribution is not None:
            # 计算分布偏度风险
            skewness = chip_distribution.skew()
            if abs(skewness) > 1:
                distribution_risk = "high"  # 分布严重偏斜
            elif abs(skewness) > 0.5:
                distribution_risk = "medium"
            else:
                distribution_risk = "low"
        else:
            distribution_risk = "unknown"

        # 流动风险
        if flow_dynamics and flow_dynamics.distribution_change > 0.7:
            flow_risk = "high"  # 筹码分布变化剧烈
        elif flow_dynamics and flow_dynamics.distribution_change > 0.4:
            flow_risk = "medium"
        else:
            flow_risk = "low"

        # 概率风险
        if winning_probability:
            prob_uncertainty = 1 - max(
                winning_probability.break_up_prob,
                winning_probability.break_down_prob,
                winning_probability.hold_prob,
            )
            if prob_uncertainty > 0.6:
                probability_risk = "high"  # 概率不确定性高
            elif prob_uncertainty > 0.4:
                probability_risk = "medium"
            else:
                probability_risk = "low"
        else:
            probability_risk = "medium"

        # 综合风险等级
        risk_scores = {"high": 3, "medium": 2, "low": 1, "unknown": 2}
        avg_risk_score = np.mean(
            [
                risk_scores.get(distribution_risk, 2),
                risk_scores.get(flow_risk, 2),
                risk_scores.get(probability_risk, 2),
            ]
        )

        if avg_risk_score > 2.5:
            overall_risk = "high"
        elif avg_risk_score > 1.5:
            overall_risk = "medium"
        else:
            overall_risk = "low"

        risk_assessment.update(
            {
                "overall_risk_level": overall_risk,
                "distribution_risk": distribution_risk,
                "flow_risk": flow_risk,
                "probability_risk": probability_risk,
                "risk_factors": [
                    "筹码分布偏斜严重" if distribution_risk == "high" else None,
                    "筹码流动过于剧烈" if flow_risk == "high" else None,
                    "概率判断不确定性高" if probability_risk == "high" else None,
                ],
                "risk_factors": [
                    f
                    for f in [
                        "筹码分布偏斜严重" if distribution_risk == "high" else None,
                        "筹码流动过于剧烈" if flow_risk == "high" else None,
                        "概率判断不确定性高" if probability_risk == "high" else None,
                    ]
                    if f is not None
                ],
            }
        )

    except Exception as e:
        print(f"Error assessing chip risk: {e}")
        risk_assessment = {"overall_risk_level": "unknown", "error": str(e)}

    return risk_assessment


def _create_error_result(self, stock_code: str, error_msg: str) -> AnalysisResult:
    """创建错误结果"""
    return AnalysisResult(
        analysis_type=AnalysisType.CHIP_DISTRIBUTION,
        stock_code=stock_code,
        timestamp=datetime.now(),
        scores={"error": True},
        signals=[{"type": "analysis_error", "severity": "high", "message": f"筹码分布分析失败: {error_msg}"}],
        recommendations={"error": error_msg},
        risk_assessment={"error": True},
        metadata={"error": True, "error_message": error_msg},
    )


