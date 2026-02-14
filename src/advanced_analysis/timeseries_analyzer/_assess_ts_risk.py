"""
Time Series Analysis Module for MyStocks Advanced Quantitative Analysis
A股量化分析平台时间序列分析功能

This module provides advanced time series analysis capabilities including:
- Turning point detection and segmentation
- Pattern matching and prediction
- Time series decomposition and trend analysis
- Seasonal and cyclical pattern recognition
"""

import warnings
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from src.advanced_analysis import AnalysisResult, AnalysisType, BaseAnalyzer

def _assess_ts_risk(
    self, turning_points: List[TurningPoint], segments: List[TimeSeriesSegment], patterns: List[PatternMatch]
) -> Dict[str, Any]:
    """评估时间序列风险"""
    risk_assessment = {}

    try:
        # 转折点风险
        if turning_points:
            high_significance_points = [tp for tp in turning_points if tp.significance > 0.7]
            turning_point_risk = len(high_significance_points) / max(len(turning_points), 1)

            if turning_point_risk > 0.5:
                risk_level = "high"  # 太多重要转折点，风险高
            elif turning_point_risk > 0.3:
                risk_level = "medium"
            else:
                risk_level = "low"
        else:
            risk_level = "medium"  # 没有检测到转折点，可能数据不足

        risk_assessment.update(
            {
                "turning_point_risk": turning_point_risk if "turning_point_risk" in locals() else 0,
                "overall_risk_level": risk_level,
                "volatility_risk": self._assess_volatility_risk(segments),
                "pattern_risk": self._assess_pattern_risk(patterns),
            }
        )

    except Exception as e:
        print(f"Error assessing TS risk: {e}")
        risk_assessment = {"overall_risk_level": "unknown", "error": str(e)}

    return risk_assessment


def _assess_volatility_risk(self, segments: List[TimeSeriesSegment]) -> str:
    """评估波动率风险"""
    if not segments:
        return "medium"

    avg_volatility = np.mean([seg.volatility for seg in segments])
    volatile_segments = sum(1 for seg in segments if seg.segment_type == "volatile")

    volatility_ratio = volatile_segments / len(segments)

    if avg_volatility > 0.05 or volatility_ratio > 0.4:  # 5%日波动率或40%波动分段
        return "high"
    elif avg_volatility > 0.03 or volatility_ratio > 0.2:
        return "medium"
    else:
        return "low"


def _assess_pattern_risk(self, patterns: List[PatternMatch]) -> str:
    """评估模式风险"""
    if not patterns:
        return "medium"

    # 计算看跌模式的比例
    bearish_patterns = sum(1 for p in patterns if p.predicted_direction in ["down", "bearish"])
    bearish_ratio = bearish_patterns / len(patterns)

    if bearish_ratio > 0.6:
        return "high"  # 大多模式看跌，风险高
    elif bearish_ratio > 0.4:
        return "medium"
    else:
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


