"""Time-series analyzer compatibility exports."""

from ._turning_point_models import PatternMatch, TimeSeriesSegment, TurningPoint
from .turning_point import TimeSeriesAnalyzer

__all__ = [
    "PatternMatch",
    "TimeSeriesAnalyzer",
    "TimeSeriesSegment",
    "TurningPoint",
]
