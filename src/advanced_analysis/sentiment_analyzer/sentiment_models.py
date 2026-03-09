"""
Sentiment analysis data models.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List


@dataclass
class SentimentScore:
    overall_sentiment: float
    positivity: float
    negativity: float
    neutrality: float
    confidence: float
    intensity: float


@dataclass
class SentimentSource:
    source_type: str
    source_name: str
    content_count: int
    avg_sentiment: float
    sentiment_trend: str
    last_updated: datetime


@dataclass
class MarketSentimentImpact:
    sentiment_correlation: float
    sentiment_lead_lag: int
    impact_strength: float
    predictive_power: float
    sentiment_regime: str


@dataclass
class SentimentKeywords:
    positive_keywords: List[str]
    negative_keywords: List[str]
    neutral_keywords: List[str]
    emerging_topics: List[str]
    keyword_weights: Dict[str, float]


@dataclass
class SentimentAlert:
    alert_type: str
    severity: str
    trigger_value: float
    threshold: float
    description: str
    recommended_action: str
