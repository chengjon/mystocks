"""
Trading signal analysis data models.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class TradingSignal:
    signal_id: str
    timestamp: datetime
    symbol: str
    signal_type: str
    strength: float
    confidence: float
    timeframe: str
    indicators: Dict[str, Any]
    price: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    description: str = ""
    risk_reward_ratio: Optional[float] = None
    validity_period: Optional[datetime] = None


@dataclass
class SignalConfluence:
    confluence_score: float
    timeframe_consensus: int
    indicator_consensus: int
    overall_signal: str
    supporting_signals: List[TradingSignal]
    conflicting_signals: List[TradingSignal]
