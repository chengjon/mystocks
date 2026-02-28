"""
Sentiment Analysis Module for MyStocks Advanced Quantitative Analysis
A股量化分析平台舆情分析功能

This module provides comprehensive sentiment analysis including:
- News and research report sentiment extraction
- Social media sentiment monitoring
- Sentiment trend analysis and correlation
- Market sentiment impact assessment
- Multi-source sentiment aggregation
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np

from src.advanced_analysis import AnalysisResult, AnalysisType

def _generate_sentiment_signals(
    self, sentiment: SentimentScore, sentiment_trend: Dict[str, Any], alerts: List[SentimentAlert]
) -> List[Dict[str, Any]]:
    """生成舆情信号"""
    signals = []

    # 情感强度信号
    if sentiment.intensity > 0.6:
        direction = "正面" if sentiment.overall_sentiment > 0 else "负面"
        severity = "high" if sentiment.intensity > 0.8 else "medium"

        signals.append(
            {
                "type": f"sentiment_intensity_{direction.lower()}",
                "severity": severity,
                "message": f"市场情绪{direction}强度高 ({sentiment.overall_sentiment:.2f})",
                "details": {
                    "overall_sentiment": sentiment.overall_sentiment,
                    "intensity": sentiment.intensity,
                    "positivity": sentiment.positivity,
                    "negativity": sentiment.negativity,
                },
            }
        )

    # 情感趋势信号
    trend_direction = sentiment_trend.get("direction", "stable")
    trend_strength = sentiment_trend.get("strength", 0)

    if trend_strength > 0.4 and trend_direction != "stable":
        direction_text = {"improving": "改善", "declining": "恶化", "stable": "稳定"}.get(trend_direction, "未知")

        signals.append(
            {
                "type": f"sentiment_trend_{trend_direction}",
                "severity": "medium",
                "message": f"市场情绪趋势{direction_text} ({trend_strength:.2f})",
                "details": {
                    "trend_direction": trend_direction,
                    "trend_strength": trend_strength,
                    "change_rate": sentiment_trend.get("change_rate", 0),
                },
            }
        )

    # 告警信号
    for alert in alerts:
        signals.append(
            {
                "type": f"alert_{alert.alert_type}",
                "severity": alert.severity,
                "message": alert.description,
                "details": {
                    "alert_type": alert.alert_type,
                    "trigger_value": alert.trigger_value,
                    "threshold": alert.threshold,
                    "recommended_action": alert.recommended_action,
                },
            }
        )

    return signals


def _generate_sentiment_recommendations(
    self, sentiment: SentimentScore, sentiment_trend: Dict[str, Any], market_impact: Optional[MarketSentimentImpact]
) -> Dict[str, Any]:
    """生成舆情建议"""
    recommendations = {}

    try:
        # 基于情感的建议
        if sentiment.overall_sentiment > 0.3:
            primary_signal = "bullish"
            action = "市场情绪偏乐观，可适度关注投资机会"
            confidence = "medium"
        elif sentiment.overall_sentiment < -0.3:
            primary_signal = "bearish"
            action = "市场情绪偏悲观，建议谨慎观望"
            confidence = "medium"
        else:
            primary_signal = "neutral"
            action = "市场情绪相对中性，按常规策略操作"
            confidence = "low"

        # 考虑趋势
        trend_direction = sentiment_trend.get("direction", "stable")
        if trend_direction == "improving" and sentiment.overall_sentiment > 0:
            action += " (情绪趋势向好，可适当乐观)"
            confidence = "high" if confidence == "medium" else confidence
        elif trend_direction == "declining" and sentiment.overall_sentiment < 0:
            action += " (情绪趋势恶化，需谨慎应对)"
            confidence = "high" if confidence == "medium" else confidence

        # 考虑市场影响
        if market_impact and market_impact.predictive_power > 0.6:
            correlation = market_impact.sentiment_correlation
            if abs(correlation) > 0.5:
                direction = "正相关" if correlation > 0 else "负相关"
                action += f" (情绪与价格{direction}较强，影响显著)"

        recommendations.update(
            {
                "primary_signal": primary_signal,
                "recommended_action": action,
                "confidence_level": confidence,
                "sentiment_analysis": {
                    "overall_sentiment": sentiment.overall_sentiment,
                    "intensity": sentiment.intensity,
                    "confidence": sentiment.confidence,
                },
                "trend_analysis": sentiment_trend,
                "market_impact": (
                    {
                        "correlation": market_impact.sentiment_correlation if market_impact else 0,
                        "predictive_power": market_impact.predictive_power if market_impact else 0,
                        "sentiment_regime": market_impact.sentiment_regime if market_impact else "unknown",
                    }
                    if market_impact
                    else None
                ),
            }
        )

    except Exception as e:
        print(f"Error generating sentiment recommendations: {e}")
        recommendations = {
            "primary_signal": "neutral",
            "recommended_action": "分析过程中出现错误，建议观望",
            "confidence_level": "low",
        }

    return recommendations


def _assess_sentiment_risk(
    self, sentiment: SentimentScore, sentiment_trend: Dict[str, Any], alerts: List[SentimentAlert]
) -> Dict[str, Any]:
    """评估舆情风险"""
    risk_assessment = {}

    try:
        # 情感极端风险
        sentiment_extreme_risk = "low"
        if abs(sentiment.overall_sentiment) > 0.7:
            sentiment_extreme_risk = "high"
        elif abs(sentiment.overall_sentiment) > 0.5:
            sentiment_extreme_risk = "medium"

        # 情感波动风险
        sentiment_volatility = sentiment_trend.get("change_rate", 0)
        volatility_risk = "low"
        if abs(sentiment_volatility) > 0.1:
            volatility_risk = "high"
        elif abs(sentiment_volatility) > 0.05:
            volatility_risk = "medium"

        # 告警风险
        alert_risk = "low"
        if alerts:
            high_severity_alerts = [a for a in alerts if a.severity == "high"]
            if high_severity_alerts:
                alert_risk = "high"
            else:
                alert_risk = "medium"

        # 综合风险等级
        risk_scores = {"high": 3, "medium": 2, "low": 1}
        avg_risk_score = np.mean(
            [
                risk_scores.get(sentiment_extreme_risk, 1),
                risk_scores.get(volatility_risk, 1),
                risk_scores.get(alert_risk, 1),
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
                "sentiment_extreme_risk": sentiment_extreme_risk,
                "volatility_risk": volatility_risk,
                "alert_risk": alert_risk,
                "risk_factors": [
                    "市场情绪极端偏离" if sentiment_extreme_risk == "high" else None,
                    "情绪波动过于剧烈" if volatility_risk == "high" else None,
                    "存在严重情绪告警" if alert_risk == "high" else None,
                ],
                "risk_factors": [
                    f
                    for f in [
                        "市场情绪极端偏离" if sentiment_extreme_risk == "high" else None,
                        "情绪波动过于剧烈" if volatility_risk == "high" else None,
                        "存在严重情绪告警" if alert_risk == "high" else None,
                    ]
                    if f is not None
                ],
            }
        )

    except Exception as e:
        print(f"Error assessing sentiment risk: {e}")
        risk_assessment = {"overall_risk_level": "unknown", "error": str(e)}

    return risk_assessment


def _load_sentiment_lexicon(self) -> Dict[str, set]:
    """加载情感词典"""
    # 简化的中文情感词典
    return {
        "positive": {
            "上涨",
            "增长",
            "利好",
            "突破",
            "创新",
            "业绩",
            "盈利",
            "乐观",
            "看好",
            "机会",
            "发展",
            "进步",
            "成功",
            "优秀",
            "良好",
            "强势",
        },
        "negative": {
            "下跌",
            "亏损",
            "风险",
            "担忧",
            "回调",
            "压力",
            "减持",
            "悲观",
            "谨慎",
            "危机",
            "问题",
            "困难",
            "损失",
            "下跌",
            "暴跌",
            "恐慌",
        },
    }


def _load_stop_words(self) -> set:
    """加载停用词"""
    return {
        "的",
        "了",
        "和",
        "是",
        "在",
        "有",
        "这",
        "那",
        "一个",
        "公司",
        "股票",
        "市场",
        "投资",
        "资金",
        "价格",
        "交易",
        "投资者",
        "分析",
    }


def _initialize_sentiment_classifier(self):
    """初始化情感分类器"""
    # 这里可以初始化更复杂的分类器
    return None


def _create_error_result(self, stock_code: str, error_msg: str) -> AnalysisResult:
    """创建错误结果"""
    return AnalysisResult(
        analysis_type=AnalysisType.SENTIMENT_ANALYSIS,
        stock_code=stock_code,
        timestamp=datetime.now(),
        scores={"error": True},
        signals=[{"type": "analysis_error", "severity": "high", "message": f"舆情分析失败: {error_msg}"}],
        recommendations={"error": error_msg},
        risk_assessment={"error": True},
        metadata={"error": True, "error_message": error_msg},
    )


