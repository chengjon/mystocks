"""Tail helpers for `multidimensional_radar.py`."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

from src.advanced_analysis import AnalysisResult, AnalysisType


def _assess_overall_risk_from_dimensions(self, dimensions: List[Any]) -> Dict[str, Any]:
    """基于维度列表评估整体风险"""
    risk_counts = {"low": 0, "medium": 0, "high": 0, "extreme": 0}
    for dim in dimensions:
        risk_counts[dim.risk_level] += 1

    if risk_counts["extreme"] > 0:
        overall_risk = "extreme"
    elif risk_counts["high"] >= len(dimensions) * 0.3:
        overall_risk = "high"
    elif risk_counts["medium"] >= len(dimensions) * 0.5:
        overall_risk = "medium"
    else:
        overall_risk = "low"

    return {
        "overall_risk_level": overall_risk,
        "risk_distribution": risk_counts,
        "risk_description": self.risk_levels[overall_risk]["description"],
        "high_risk_dimensions": [dim.name for dim in dimensions if dim.risk_level in ["high", "extreme"]],
    }


def _assess_overall_risk(self, radar_result: Any) -> Dict[str, Any]:
    """评估整体风险"""
    dimensions = radar_result.dimensions
    return _assess_overall_risk_from_dimensions(self, dimensions)


def _assess_risk(self, radar_result: Any) -> Dict[str, Any]:
    """风险评估（兼容现有接口）"""
    return self._assess_overall_risk(radar_result)


def _aggregate_signals(self, dimensions: List[Any]) -> List[Dict[str, Any]]:
    """聚合所有维度的信号"""
    all_signals = []
    for dim in dimensions:
        all_signals.extend(dim.signals)

    all_signals.sort(key=lambda x: x.get("score", 0), reverse=True)
    return all_signals[:10]


def _generate_recommendation(self, overall_score: float, risk_assessment: Dict[str, Any]) -> str:
    """生成投资建议"""
    risk_level = risk_assessment.get("overall_risk_level", "medium")

    if overall_score >= 80 and risk_level == "low":
        return "强烈推荐买入"
    if overall_score >= 70 and risk_level in ["low", "medium"]:
        return "推荐买入"
    if overall_score >= 60 and risk_level != "extreme":
        return "谨慎买入"
    if overall_score >= 40:
        return "观望"
    if overall_score >= 20:
        return "谨慎卖出"
    return "建议卖出"


def _create_error_result(self, stock_code: str, error_msg: str) -> AnalysisResult:
    """创建错误结果"""
    return AnalysisResult(
        analysis_type=AnalysisType.MULTIDIMENSIONAL_RADAR,
        stock_code=stock_code,
        timestamp=datetime.now(),
        scores={"error": 0.0},
        signals=[],
        recommendations={"error": error_msg},
        risk_assessment={"error": "Analysis failed"},
        metadata={"error": True},
        raw_data=None,
    )
