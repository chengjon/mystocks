"""Tail helpers for `sentiment_score.py`."""

import logging
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd

from src.advanced_analysis.sentiment_analyzer.sentiment_models import (
    MarketSentimentImpact,
    SentimentAlert,
    SentimentKeywords,
    SentimentScore,
)

logger = logging.getLogger(__name__)


class SentimentAnalyzerTailMixin:
    def _analyze_market_sentiment_impact(
        self, sentiment_data: pd.DataFrame, stock_code: str
    ) -> Optional[MarketSentimentImpact]:
        """分析市场情绪影响"""
        try:
            # 获取价格数据
            price_data = self._get_historical_data(stock_code, days=30, data_type="1d")

            if price_data.empty or sentiment_data.empty:
                return None

            # 计算每日平均情感
            daily_sentiment = sentiment_data.groupby("date")["sentiment"].mean()

            # 对齐价格和情感数据
            combined_data = pd.DataFrame(
                {"price": price_data.set_index("date")["close"], "sentiment": daily_sentiment}
            ).dropna()

            if len(combined_data) < 5:
                return MarketSentimentImpact(0, 0, 0, 0, "unknown")

            # 计算相关性和领先滞后关系
            max_lag = min(self.sentiment_params["correlation_lag_max"], len(combined_data) - 1)

            correlations = []
            for lag in range(-max_lag, max_lag + 1):
                if lag < 0:
                    corr = combined_data["sentiment"].corr(combined_data["price"].shift(-lag))
                else:
                    corr = combined_data["sentiment"].corr(combined_data["price"].shift(lag))

                if not pd.isna(corr):
                    correlations.append((lag, corr))

            if not correlations:
                return MarketSentimentImpact(0, 0, 0, 0, "unknown")

            # 找到最佳相关性
            best_corr = max(correlations, key=lambda x: abs(x[1]))
            sentiment_correlation = best_corr[1]
            sentiment_lead_lag = best_corr[0]

            # 计算影响强度
            impact_strength = abs(sentiment_correlation)

            # 计算预测能力
            predictive_power = max(0, sentiment_correlation * (1 - abs(sentiment_lead_lag) / max_lag))

            # 判断情绪状态
            avg_sentiment = combined_data["sentiment"].mean()
            if avg_sentiment > 0.2:
                sentiment_regime = "bullish"
            elif avg_sentiment < -0.2:
                sentiment_regime = "bearish"
            else:
                sentiment_regime = "neutral"

            return MarketSentimentImpact(
                sentiment_correlation=sentiment_correlation,
                sentiment_lead_lag=sentiment_lead_lag,
                impact_strength=impact_strength,
                predictive_power=predictive_power,
                sentiment_regime=sentiment_regime,
            )

        except Exception as e:
            logger.error("Error analyzing market sentiment impact: %s", e)
            return None


    def _generate_sentiment_alerts(
        self, sentiment: SentimentScore, sentiment_trend: Dict[str, Any]
    ) -> List[SentimentAlert]:
        """生成情感告警"""
        alerts = []

        try:
            # 极端情感告警
            if abs(sentiment.overall_sentiment) > 0.7:
                alert_type = "extreme_positive" if sentiment.overall_sentiment > 0 else "extreme_negative"
                severity = "high"

                alert = SentimentAlert(
                    alert_type=alert_type,
                    severity=severity,
                    trigger_value=sentiment.overall_sentiment,
                    threshold=0.7,
                    description=f"市场情绪{sentiment.overall_sentiment:.2f}，{'极度乐观' if sentiment.overall_sentiment > 0 else '极度悲观'}",
                    recommended_action="密切关注市场动向，谨慎决策",
                )
                alerts.append(alert)

            # 情感突变告警
            trend_direction = sentiment_trend.get("direction", "stable")
            trend_strength = sentiment_trend.get("strength", 0)

            if trend_strength > 0.5 and trend_direction in ["improving", "declining"]:
                alert = SentimentAlert(
                    alert_type="sentiment_trend_change",
                    severity="medium",
                    trigger_value=trend_strength,
                    threshold=0.5,
                    description=f"市场情绪{trend_direction}趋势明显，强度{trend_strength:.2f}",
                    recommended_action="关注情绪趋势变化对市场的影响",
                )
                alerts.append(alert)

        except Exception as e:
            logger.error("Error generating sentiment alerts: %s", e)

        return alerts


    def _calculate_sentiment_scores(
        self, sentiment: SentimentScore, sentiment_trend: Dict[str, Any], market_impact: Optional[MarketSentimentImpact]
    ) -> Dict[str, float]:
        """计算舆情分析得分"""
        scores = {}

        try:
            # 情感强度得分
            sentiment_intensity_score = min(sentiment.intensity * 2, 1.0)
            scores["sentiment_intensity"] = sentiment_intensity_score

            # 情感一致性得分
            sentiment_consistency = 1 - abs(sentiment.positivity + sentiment.negativity - 1)
            scores["sentiment_consistency"] = sentiment_consistency

            # 情感置信度得分
            confidence_score = sentiment.confidence
            scores["sentiment_confidence"] = confidence_score

            # 趋势稳定性得分
            trend_stability = 1 - sentiment_trend.get("change_rate", 0) * 10
            trend_stability = max(0, min(trend_stability, 1))
            scores["trend_stability"] = trend_stability

            # 市场影响得分
            if market_impact:
                market_influence_score = market_impact.impact_strength * market_impact.predictive_power
                scores["market_influence"] = market_influence_score
            else:
                scores["market_influence"] = 0.5

            # 综合得分
            weights = {
                "sentiment_intensity": 0.2,
                "sentiment_consistency": 0.2,
                "sentiment_confidence": 0.25,
                "trend_stability": 0.15,
                "market_influence": 0.2,
            }

            overall_score = sum(scores.get(key, 0) * weight for key, weight in weights.items())
            scores["overall_score"] = overall_score

        except Exception as e:
            logger.error("Error calculating sentiment scores: %s", e)
            scores = {"overall_score": 0.5, "error": True}

        return scores
