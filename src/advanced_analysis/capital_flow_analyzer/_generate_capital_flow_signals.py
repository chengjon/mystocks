"""
Capital Flow Analysis Module for MyStocks Advanced Quantitative Analysis
A股量化分析平台资金流向与主力控盘分析功能

This module provides comprehensive capital flow analysis including:
- Capital flow clustering and pattern analysis
- Main force control detection and analysis
- Capital flow correlation and network analysis
- Institutional vs retail flow dynamics
- Smart money tracking and identification
"""

from datetime import datetime
from typing import Any, Dict, List

import numpy as np
import pandas as pd

from src.advanced_analysis import AnalysisResult, AnalysisType

def _generate_capital_flow_signals(
    self,
    data: pd.DataFrame,
    clusters: List[CapitalFlowCluster],
    control: MainForceControl,
    smart_money: SmartMoneyIndicator,
) -> List[Dict[str, Any]]:
    """生成资金流向信号"""
    signals = []

    # 主力控盘信号
    if control and control.control_degree > 0.6:
        severity = "high" if control.control_degree > 0.8 else "medium"
        signals.append(
            {
                "type": "main_force_control",
                "severity": severity,
                "message": f"主力控盘程度高 ({control.control_degree:.2f}) - {control.main_force_type}",
                "details": {
                    "control_degree": control.control_degree,
                    "concentration_ratio": control.concentration_ratio,
                    "sustained_period": control.sustained_period,
                    "control_signals": control.control_signals[:3],
                },
            }
        )

    # 聪明钱信号
    if smart_money and smart_money.smart_money_score > 0.7:
        signals.append(
            {
                "type": "smart_money_signal",
                "severity": "high",
                "message": f"聪明钱高度认可 ({smart_money.smart_money_score:.2f})",
                "details": {
                    "institutional_accumulation": smart_money.institutional_accumulation,
                    "timing_quality": smart_money.timing_quality,
                    "conviction_signals": smart_money.conviction_signals[:3],
                },
            }
        )

    # 聚类信号
    if clusters:
        dominant_cluster = max(clusters, key=lambda c: c.cluster_size)
        if dominant_cluster.confidence > 0.7:
            signals.append(
                {
                    "type": "flow_clustering",
                    "severity": "medium",
                    "message": f"资金流向聚类模式: {dominant_cluster.flow_pattern}",
                    "details": {
                        "cluster_size": dominant_cluster.cluster_size,
                        "flow_pattern": dominant_cluster.flow_pattern,
                        "confidence": dominant_cluster.confidence,
                    },
                }
            )

    # 资金流向强度信号
    if not data.empty:
        recent_flow = data["net_flow"].iloc[-1] if len(data) > 0 else 0
        avg_flow = data["net_flow"].mean() if len(data) > 0 else 0

        if abs(recent_flow) > abs(avg_flow) * 2:
            direction = "流入" if recent_flow > 0 else "流出"
            severity = "high" if abs(recent_flow) > abs(avg_flow) * 3 else "medium"
            signals.append(
                {
                    "type": "flow_intensity",
                    "severity": severity,
                    "message": f"资金大幅{direction} ({recent_flow:,.0f})",
                    "details": {
                        "recent_flow": recent_flow,
                        "avg_flow": avg_flow,
                        "intensity_ratio": abs(recent_flow) / abs(avg_flow),
                    },
                }
            )

    return signals


def _generate_capital_flow_recommendations(
    self, control: MainForceControl, smart_money: SmartMoneyIndicator, market_context: Dict[str, Any]
) -> Dict[str, Any]:
    """生成资金流向投资建议"""
    recommendations = {}

    try:
        # 基于控盘情况的建议
        if control:
            if control.control_degree > 0.8:
                primary_signal = "hold"
                action = "主力高度控盘，观望为主"
                confidence = "high"
            elif control.control_degree > 0.6:
                primary_signal = "follow"
                action = "主力控盘明显，跟随主力操作"
                confidence = "medium"
            else:
                primary_signal = "normal"
                action = "控盘程度正常，可按常规策略操作"
                confidence = "medium"
        else:
            primary_signal = "unknown"
            action = "控盘情况不明，谨慎操作"
            confidence = "low"

        # 考虑聪明钱因素
        if smart_money and smart_money.smart_money_score > 0.8:
            action += " (聪明钱高度认可，可适当乐观)"
            confidence = "high"
        elif smart_money and smart_money.smart_money_score < 0.3:
            action += " (聪明钱认可度低，需谨慎)"
            confidence = "low"

        # 考虑市场背景
        market_sentiment = market_context.get("market_sentiment", "neutral")
        if market_sentiment == "bullish":
            action += " (市场情绪乐观)"
        elif market_sentiment == "bearish":
            action += " (市场情绪谨慎)"

        recommendations.update(
            {
                "primary_signal": primary_signal,
                "recommended_action": action,
                "confidence_level": confidence,
                "control_analysis": {
                    "control_degree": control.control_degree if control else 0,
                    "main_force_type": control.main_force_type if control else "unknown",
                },
                "smart_money_analysis": {
                    "smart_money_score": smart_money.smart_money_score if smart_money else 0,
                    "timing_quality": smart_money.timing_quality if smart_money else 0,
                },
                "market_context": market_context,
            }
        )

    except Exception as e:
        print(f"Error generating capital flow recommendations: {e}")
        recommendations = {
            "primary_signal": "hold",
            "recommended_action": "分析过程中出现错误，建议观望",
            "confidence_level": "low",
        }

    return recommendations


def _assess_capital_flow_risk(
    self, data: pd.DataFrame, control: MainForceControl, smart_money: SmartMoneyIndicator
) -> Dict[str, Any]:
    """评估资金流向风险"""
    risk_assessment = {}

    try:
        # 流向波动风险
        if not data.empty:
            flow_volatility = data["net_flow"].std() / (abs(data["net_flow"].mean()) + 1e-8)
            if flow_volatility > 1.0:
                flow_volatility_risk = "high"
            elif flow_volatility > 0.5:
                flow_volatility_risk = "medium"
            else:
                flow_volatility_risk = "low"
        else:
            flow_volatility_risk = "unknown"

        # 控盘风险
        if control:
            if control.control_degree > 0.8:
                control_risk = "high"  # 过度控盘可能存在风险
            elif control.control_stability < 0.4:
                control_risk = "high"  # 控盘不稳定
            else:
                control_risk = "low"
        else:
            control_risk = "medium"

        # 聪明钱风险
        if smart_money:
            if smart_money.smart_money_score < 0.3:
                smart_money_risk = "high"  # 聪明钱不认可
            elif smart_money.flow_divergence > 0.7:
                smart_money_risk = "medium"  # 存在背离
            else:
                smart_money_risk = "low"
        else:
            smart_money_risk = "medium"

        # 综合风险等级
        risk_scores = {"high": 3, "medium": 2, "low": 1, "unknown": 2}
        avg_risk_score = np.mean(
            [
                risk_scores.get(flow_volatility_risk, 2),
                risk_scores.get(control_risk, 2),
                risk_scores.get(smart_money_risk, 2),
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
                "flow_volatility_risk": flow_volatility_risk,
                "control_risk": control_risk,
                "smart_money_risk": smart_money_risk,
                "risk_factors": [
                    "资金流向波动大" if flow_volatility_risk == "high" else None,
                    "主力过度控盘" if control_risk == "high" else None,
                    "聪明钱认可度低" if smart_money_risk == "high" else None,
                ],
                "risk_factors": [
                    f
                    for f in [
                        "资金流向波动大" if flow_volatility_risk == "high" else None,
                        "主力过度控盘" if control_risk == "high" else None,
                        "聪明钱认可度低" if smart_money_risk == "high" else None,
                    ]
                    if f is not None
                ],
            }
        )

    except Exception as e:
        print(f"Error assessing capital flow risk: {e}")
        risk_assessment = {"overall_risk_level": "unknown", "error": str(e)}

    return risk_assessment


def _create_error_result(self, stock_code: str, error_msg: str) -> AnalysisResult:
    """创建错误结果"""
    return AnalysisResult(
        analysis_type=AnalysisType.CAPITAL_FLOW,
        stock_code=stock_code,
        timestamp=datetime.now(),
        scores={"error": True},
        signals=[{"type": "analysis_error", "severity": "high", "message": f"资金流向分析失败: {error_msg}"}],
        recommendations={"error": error_msg},
        risk_assessment={"error": True},
        metadata={"error": True, "error_message": error_msg},
    )


