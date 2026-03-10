"""
Time Series Analysis Module for MyStocks Advanced Quantitative Analysis
A股量化分析平台时间序列分析功能

This module provides advanced time series analysis capabilities including:
- Turning point detection and segmentation
- Pattern matching and prediction
- Time series decomposition and trend analysis
- Seasonal and cyclical pattern recognition
"""

from __future__ import annotations

from datetime import datetime

import numpy as np

from src.advanced_analysis import AnalysisResult, AnalysisType, BaseAnalyzer

from ._assess_ts_risk import _assess_pattern_risk, _assess_ts_risk, _assess_volatility_risk, _create_error_result
from ._turning_point_detection import (
    _analyze_segment,
    _detect_turning_points,
    _perform_segmentation,
    _simple_turning_point_detection,
)
from ._turning_point_models import PatternMatch, TimeSeriesSegment, TurningPoint
from ._turning_point_pattern_analysis import (
    _analyze_seasonal_patterns,
    _analyze_trend,
    _detect_cup_handle_pattern,
    _detect_double_bottom_pattern,
    _detect_double_top_pattern,
    _detect_head_shoulders_pattern,
    _detect_triangle_pattern,
    _detect_wedge_pattern,
    _generate_predictions,
    _perform_pattern_matching,
)
from ._turning_point_reporting import _calculate_ts_scores, _generate_ts_recommendations, _generate_ts_signals


class TimeSeriesAnalyzer(BaseAnalyzer):
    """
    时间序列分析器

    提供高级时间序列分析功能，包括：
    - 转折点检测和分段
    - 模式匹配和预测
    - 时间序列分解和趋势分析
    - 季节性和周期性模式识别
    """



def __init__(self, data_manager, gpu_manager=None):
    super().__init__(data_manager, gpu_manager)

    self.turning_point_params = {
        "min_prominence": 0.02,
        "min_distance": 5,
        "peak_width": 3,
        "valley_width": 3,
    }
    self.segmentation_params = {
        "min_segment_length": 10,
        "trend_threshold": 0.001,
        "volatility_window": 20,
    }
    self.pattern_params = {
        "min_pattern_length": 10,
        "max_pattern_length": 50,
        "similarity_threshold": 0.8,
        "dtw_window": 5,
    }
    self.pattern_library = {
        "head_shoulders": self._detect_head_shoulders_pattern,
        "double_top": self._detect_double_top_pattern,
        "double_bottom": self._detect_double_bottom_pattern,
        "triangle": self._detect_triangle_pattern,
        "wedge": self._detect_wedge_pattern,
        "cup_handle": self._detect_cup_handle_pattern,
    }



def analyze(self, stock_code: str, **kwargs) -> AnalysisResult:
    """执行时间序列分析。"""
    analysis_period = kwargs.get("analysis_period", 365)
    detect_turning_points = kwargs.get("detect_turning_points", True)
    perform_segmentation = kwargs.get("perform_segmentation", True)
    pattern_matching = kwargs.get("pattern_matching", True)
    include_predictions = kwargs.get("include_predictions", True)

    try:
        data = self._get_historical_data(stock_code, days=analysis_period, data_type="1d")
        if data.empty:
            return self._create_error_result(stock_code, "No historical data available for time series analysis")

        turning_points = self._detect_turning_points(data) if detect_turning_points else []
        segments = self._perform_segmentation(data, turning_points) if perform_segmentation else []
        patterns = self._perform_pattern_matching(data) if pattern_matching else []
        trend_analysis = self._analyze_trend(data)
        seasonal_analysis = self._analyze_seasonal_patterns(data)
        predictions = self._generate_predictions(data, patterns) if include_predictions else {}
        scores = self._calculate_ts_scores(data, turning_points, segments, patterns)
        signals = self._generate_ts_signals(turning_points, segments, patterns, predictions)
        recommendations = self._generate_ts_recommendations(trend_analysis, seasonal_analysis, predictions)
        risk_assessment = self._assess_ts_risk(turning_points, segments, patterns)

        metadata = {
            "analysis_period_days": analysis_period,
            "data_points": len(data),
            "turning_points_detected": len(turning_points),
            "segments_identified": len(segments),
            "patterns_found": len(patterns),
            "trend_direction": trend_analysis.get("direction"),
            "trend_strength": trend_analysis.get("strength"),
            "seasonal_patterns": bool(seasonal_analysis.get("has_seasonality")),
            "volatility_level": data["close"].pct_change().std() * np.sqrt(252) if len(data) > 1 else 0,
            "last_analysis_timestamp": datetime.now(),
        }

        return AnalysisResult(
            analysis_type=AnalysisType.TIME_SERIES,
            stock_code=stock_code,
            timestamp=datetime.now(),
            scores=scores,
            signals=signals,
            recommendations=recommendations,
            risk_assessment=risk_assessment,
            metadata=metadata,
            raw_data=data if kwargs.get("include_raw_data", False) else None,
        )
    except Exception as error:
        return self._create_error_result(stock_code, str(error))


__all__ = [
    "TurningPoint",
    "TimeSeriesSegment",
    "PatternMatch",
    "TimeSeriesAnalyzer",
    "__init__",
    "analyze",
    "_detect_turning_points",
    "_simple_turning_point_detection",
    "_perform_segmentation",
    "_analyze_segment",
    "_perform_pattern_matching",
    "_detect_head_shoulders_pattern",
    "_detect_double_top_pattern",
    "_detect_double_bottom_pattern",
    "_detect_triangle_pattern",
    "_detect_wedge_pattern",
    "_detect_cup_handle_pattern",
    "_analyze_trend",
    "_analyze_seasonal_patterns",
    "_generate_predictions",
    "_calculate_ts_scores",
    "_generate_ts_signals",
    "_generate_ts_recommendations",
    "_assess_ts_risk",
    "_assess_volatility_risk",
    "_assess_pattern_risk",
    "_create_error_result",
]
