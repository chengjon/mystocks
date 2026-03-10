from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List

import numpy as np

from src.advanced_analysis import AnalysisResult, AnalysisType

from ._turning_point_models import PatternMatch, TimeSeriesSegment, TurningPoint

logger = logging.getLogger(__name__)



def _assess_ts_risk(
    self,
    turning_points: List[TurningPoint],
    segments: List[TimeSeriesSegment],
    patterns: List[PatternMatch],
) -> Dict[str, Any]:
    """评估时间序列风险"""
    risk_assessment = {}

    try:
        if turning_points:
            high_significance_points = [turning_point for turning_point in turning_points if turning_point.significance > 0.7]
            turning_point_risk = len(high_significance_points) / max(len(turning_points), 1)

            if turning_point_risk > 0.5:
                risk_level = "high"
            elif turning_point_risk > 0.3:
                risk_level = "medium"
            else:
                risk_level = "low"
        else:
            turning_point_risk = 0
            risk_level = "medium"

        risk_assessment.update(
            {
                "turning_point_risk": turning_point_risk,
                "overall_risk_level": risk_level,
                "volatility_risk": self._assess_volatility_risk(segments),
                "pattern_risk": self._assess_pattern_risk(patterns),
            }
        )
    except Exception as error:
        logger.exception("Error assessing TS risk")
        risk_assessment = {"overall_risk_level": "unknown", "error": str(error)}

    return risk_assessment



def _assess_volatility_risk(self, segments: List[TimeSeriesSegment]) -> str:
    """评估波动率风险"""
    if not segments:
        return "medium"

    avg_volatility = np.mean([segment.volatility for segment in segments])
    volatile_segments = sum(1 for segment in segments if segment.segment_type == "volatile")
    volatility_ratio = volatile_segments / len(segments)

    if avg_volatility > 0.05 or volatility_ratio > 0.4:
        return "high"
    if avg_volatility > 0.03 or volatility_ratio > 0.2:
        return "medium"
    return "low"



def _assess_pattern_risk(self, patterns: List[PatternMatch]) -> str:
    """评估模式风险"""
    if not patterns:
        return "medium"

    bearish_patterns = sum(1 for pattern in patterns if pattern.predicted_direction in ["down", "bearish"])
    bearish_ratio = bearish_patterns / len(patterns)

    if bearish_ratio > 0.6:
        return "high"
    if bearish_ratio > 0.4:
        return "medium"
    return "low"



def _create_error_result(self, stock_code: str, error_msg: str) -> AnalysisResult:
    """创建错误结果"""
    return AnalysisResult(
        analysis_type=AnalysisType.TIME_SERIES,
        stock_code=stock_code,
        timestamp=datetime.now(),
        scores={"error": True},
        signals=[{"type": "analysis_error", "severity": "high", "message": f"时间序列分析失败: {error_msg}"}],
        recommendations={"error": error_msg},
        risk_assessment={"error": True},
        metadata={"error": True, "error_message": error_msg},
    )
