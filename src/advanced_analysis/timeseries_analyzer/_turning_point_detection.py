from __future__ import annotations

import logging
from typing import List, Optional

import numpy as np
import pandas as pd

from ._turning_point_models import TimeSeriesSegment, TurningPoint

logger = logging.getLogger(__name__)

try:
    from scipy.signal import find_peaks

    SCIPY_AVAILABLE = True
except Exception:
    find_peaks = None
    SCIPY_AVAILABLE = False



def _detect_turning_points(self, data: pd.DataFrame) -> List[TurningPoint]:
    """检测转折点"""
    if data.empty or "close" not in data.columns:
        return []

    try:
        prices = data["close"].values

        if SCIPY_AVAILABLE and find_peaks is not None:
            peaks, peak_properties = find_peaks(
                prices,
                prominence=np.std(prices) * self.turning_point_params["min_prominence"],
                distance=self.turning_point_params["min_distance"],
                width=self.turning_point_params["peak_width"],
            )
            valleys, valley_properties = find_peaks(
                -prices,
                prominence=np.std(prices) * self.turning_point_params["min_prominence"],
                distance=self.turning_point_params["min_distance"],
                width=self.turning_point_params["valley_width"],
            )

            turning_points = []

            for index, peak_idx in enumerate(peaks):
                prominence = peak_properties["prominences"][index] if index < len(peak_properties["prominences"]) else 0
                significance = min(prominence / np.std(prices), 1.0)
                turning_points.append(
                    TurningPoint(
                        index=int(peak_idx),
                        timestamp=data.index[peak_idx].to_pydatetime(),
                        price=prices[peak_idx],
                        point_type="peak",
                        significance=significance,
                        confidence=0.8,
                    )
                )

            for index, valley_idx in enumerate(valleys):
                prominence = (
                    valley_properties["prominences"][index] if index < len(valley_properties["prominences"]) else 0
                )
                significance = min(prominence / np.std(prices), 1.0)
                turning_points.append(
                    TurningPoint(
                        index=int(valley_idx),
                        timestamp=data.index[valley_idx].to_pydatetime(),
                        price=prices[valley_idx],
                        point_type="valley",
                        significance=significance,
                        confidence=0.8,
                    )
                )

            turning_points.sort(key=lambda point: point.index)
            return turning_points

        return self._simple_turning_point_detection(data)
    except Exception:
        logger.exception("Error detecting turning points")
        return []



def _simple_turning_point_detection(self, data: pd.DataFrame) -> List[TurningPoint]:
    """简化的转折点检测"""
    prices = data["close"].values
    turning_points = []

    ma_short = pd.Series(prices).rolling(window=5).mean()
    ma_long = pd.Series(prices).rolling(window=20).mean()
    trend_change = np.sign(ma_short - ma_long).diff()
    change_points = np.where(trend_change != 0)[0]

    for idx in change_points:
        if idx < len(prices):
            point_type = "peak" if trend_change.iloc[idx] < 0 else "valley"
            turning_points.append(
                TurningPoint(
                    index=int(idx),
                    timestamp=data.index[idx].to_pydatetime(),
                    price=prices[idx],
                    point_type=point_type,
                    significance=0.5,
                    confidence=0.6,
                )
            )

    return turning_points



def _perform_segmentation(self, data: pd.DataFrame, turning_points: List[TurningPoint]) -> List[TimeSeriesSegment]:
    """执行时间序列分段"""
    if data.empty:
        return []

    try:
        segments = []

        if turning_points:
            segment_boundaries = [0] + [turning_point.index for turning_point in turning_points] + [len(data) - 1]

            for index in range(len(segment_boundaries) - 1):
                start_idx = segment_boundaries[index]
                end_idx = segment_boundaries[index + 1]

                if end_idx - start_idx >= self.segmentation_params["min_segment_length"]:
                    segment = self._analyze_segment(data, start_idx, end_idx)
                    if segment:
                        segments.append(segment)
        else:
            segment = self._analyze_segment(data, 0, len(data) - 1)
            if segment:
                segments.append(segment)

        return segments
    except Exception:
        logger.exception("Error performing segmentation")
        return []



def _analyze_segment(self, data: pd.DataFrame, start_idx: int, end_idx: int) -> Optional[TimeSeriesSegment]:
    """分析单个分段"""
    try:
        segment_data = data.iloc[start_idx : end_idx + 1]
        prices = segment_data["close"].values

        if len(prices) < 2:
            return None

        start_price = prices[0]
        end_price = prices[-1]
        price_change = (end_price - start_price) / start_price

        returns = np.diff(prices) / prices[:-1]
        volatility = np.std(returns) if len(returns) > 0 else 0

        if abs(price_change) < self.segmentation_params["trend_threshold"]:
            segment_type = "sideways"
            trend_strength = 0.0
        elif price_change > 0:
            segment_type = "uptrend"
            trend_strength = min(abs(price_change) * 10, 1.0)
        else:
            segment_type = "downtrend"
            trend_strength = min(abs(price_change) * 10, 1.0)

        if volatility > np.mean(np.abs(returns)) * 2:
            segment_type = "volatile"

        return TimeSeriesSegment(
            start_index=start_idx,
            end_index=end_idx,
            start_timestamp=data.index[start_idx].to_pydatetime(),
            end_timestamp=data.index[end_idx].to_pydatetime(),
            segment_type=segment_type,
            duration=end_idx - start_idx + 1,
            magnitude=abs(price_change),
            trend_strength=trend_strength,
            volatility=volatility,
        )
    except Exception:
        logger.exception("Error analyzing segment %s-%s", start_idx, end_idx)
        return None
