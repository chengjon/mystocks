"""
Technical analysis data models.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TechnicalSignal:
    signal_type: str
    strength: float
    confidence: float
    timeframe: str
    indicator: str
    value: float
    threshold: float
    description: str


@dataclass
class PatternResult:
    pattern_name: str
    confidence: float
    direction: str
    strength: float
    start_idx: int
    end_idx: int
    description: str


@dataclass
class MarketRegime:
    primary_regime: str
    volatility_regime: str
    trend_strength: float
    volatility_level: float
    adx_value: float
    recommended_strategy: str
