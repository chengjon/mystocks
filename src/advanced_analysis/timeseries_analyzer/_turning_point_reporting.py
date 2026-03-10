from __future__ import annotations

import logging
from typing import Any, Dict, List

import numpy as np
import pandas as pd

from ._turning_point_models import PatternMatch, TimeSeriesSegment, TurningPoint

logger = logging.getLogger(__name__)



def _calculate_ts_scores(
    self,
    data: pd.DataFrame,
    turning_points: List[TurningPoint],
    segments: List[TimeSeriesSegment],
    patterns: List[PatternMatch],
) -> Dict[str, float]:
    """计算时间序列分析得分"""
    scores = {}

    try:
        scores["turning_point_significance"] = (
            np.mean([turning_point.significance for turning_point in turning_points]) if turning_points else 0.0
        )
        scores["segment_trend_strength"] = (
            np.mean([segment.trend_strength for segment in segments]) if segments else 0.0
        )
        scores["pattern_similarity"] = (
            np.mean([pattern.similarity_score for pattern in patterns]) if patterns else 0.0
        )

        if len(data) > 10:
            returns = data["close"].pct_change().dropna()
            volatility = returns.std()
            scores["stability_score"] = max(0, 1 - volatility * 10)
        else:
            scores["stability_score"] = 0.5

        weights = {
            "turning_point_significance": 0.25,
            "segment_trend_strength": 0.30,
            "pattern_similarity": 0.25,
            "stability_score": 0.20,
        }
        scores["overall_score"] = sum(scores.get(key, 0) * weight for key, weight in weights.items())
    except Exception:
        logger.exception("Error calculating TS scores")
        scores = {"overall_score": 0.0, "error": True}

    return scores



def _generate_ts_signals(
    self,
    turning_points: List[TurningPoint],
    segments: List[TimeSeriesSegment],
    patterns: List[PatternMatch],
    predictions: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """生成时间序列信号"""
    signals = []

    for turning_point in turning_points[-5:]:
        severity = "high" if turning_point.significance > 0.7 else "medium" if turning_point.significance > 0.5 else "low"
        signals.append(
            {
                "type": "turning_point",
                "severity": severity,
                "message": f"{turning_point.point_type.upper()}转折点检测 - 重要性: {turning_point.significance:.2f}",
                "details": {
                    "point_type": turning_point.point_type,
                    "significance": turning_point.significance,
                    "confidence": turning_point.confidence,
                    "timestamp": turning_point.timestamp.isoformat(),
                },
            }
        )

    if segments:
        latest_segment = segments[-1]
        signals.append(
            {
                "type": f"segment_{latest_segment.segment_type}",
                "severity": "high" if latest_segment.trend_strength > 0.7 else "medium",
                "message": f"当前分段: {latest_segment.segment_type} - 趋势强度: {latest_segment.trend_strength:.2f}",
                "details": {
                    "segment_type": latest_segment.segment_type,
                    "trend_strength": latest_segment.trend_strength,
                    "volatility": latest_segment.volatility,
                    "duration": latest_segment.duration,
                },
            }
        )

    for pattern in patterns[:3]:
        signals.append(
            {
                "type": f"pattern_{pattern.pattern_name}",
                "severity": "high" if pattern.similarity_score > 0.85 else "medium",
                "message": f"模式匹配: {pattern.pattern_name} - 相似度: {pattern.similarity_score:.2f}",
                "details": {
                    "pattern_name": pattern.pattern_name,
                    "similarity_score": pattern.similarity_score,
                    "predicted_direction": pattern.predicted_direction,
                    "confidence": pattern.confidence,
                },
            }
        )

    if "combined" in predictions:
        prediction = predictions["combined"]
        signals.append(
            {
                "type": f"prediction_{prediction['predicted_direction']}",
                "severity": "medium",
                "message": f"预测方向: {prediction['predicted_direction']} - 置信度: {prediction['confidence']:.2f}",
                "details": {
                    "predicted_direction": prediction["predicted_direction"],
                    "confidence": prediction["confidence"],
                    "method": prediction.get("method", "unknown"),
                },
            }
        )

    return signals



def _generate_ts_recommendations(
    self, trend_analysis: Dict[str, Any], seasonal_analysis: Dict[str, Any], predictions: Dict[str, Any]
) -> Dict[str, Any]:
    """生成时间序列建议"""
    recommendations = {}

    try:
        trend_direction = trend_analysis.get("direction", "unknown")
        trend_strength = trend_analysis.get("strength", 0.0)

        if trend_direction == "uptrend" and trend_strength > 0.6:
            primary_signal = "buy"
            action = "趋势向上，可考虑买入"
            confidence = "high"
        elif trend_direction == "downtrend" and trend_strength > 0.6:
            primary_signal = "sell"
            action = "趋势向下，建议观望或卖出"
            confidence = "high"
        else:
            primary_signal = "hold"
            action = "趋势不明，建议观望"
            confidence = "medium"

        if seasonal_analysis.get("has_seasonality", False):
            seasonal_strength = seasonal_analysis.get("seasonal_strength", 0)
            if seasonal_strength > 0.5:
                action += f" (季节性因素显著: {seasonal_strength:.2f})"

        if "combined" in predictions:
            pred_direction = predictions["combined"].get("predicted_direction")
            pred_confidence = predictions["combined"].get("confidence", 0)

            if pred_confidence > 0.7:
                if pred_direction == primary_signal:
                    action += f" (预测确认{primary_signal}信号)"
                    confidence = "high"
                else:
                    action += " (预测与趋势存在分歧，需谨慎)"

        recommendations.update(
            {
                "primary_signal": primary_signal,
                "recommended_action": action,
                "confidence_level": confidence,
                "trend_analysis": trend_analysis,
                "seasonal_factors": seasonal_analysis.get("has_seasonality", False),
                "prediction_available": bool(predictions),
            }
        )
    except Exception:
        logger.exception("Error generating TS recommendations")
        recommendations = {
            "primary_signal": "hold",
            "recommended_action": "分析过程中出现错误，建议观望",
            "confidence_level": "low",
        }

    return recommendations
