from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class TurningPoint:
    """转折点数据结构"""

    index: int
    timestamp: datetime
    price: float
    point_type: str
    significance: float
    confidence: float
    duration: Optional[int] = None


@dataclass
class TimeSeriesSegment:
    """时间序列分段"""

    start_index: int
    end_index: int
    start_timestamp: datetime
    end_timestamp: datetime
    segment_type: str
    duration: int
    magnitude: float
    trend_strength: float
    volatility: float
    pattern_match: Optional[str] = None


@dataclass
class PatternMatch:
    """模式匹配结果"""

    pattern_name: str
    start_index: int
    end_index: int
    similarity_score: float
    predicted_direction: str
    confidence: float
    expected_return: Optional[float] = None
