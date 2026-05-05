"""Deterministic MVP chart-pattern detection helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import pandas as pd


@dataclass
class DetectedAnchor:
    role: str
    timestamp: int
    value: float


@dataclass
class DetectedPattern:
    pattern_name: Literal["double_top", "double_bottom", "head_shoulders_top", "head_shoulders_bottom"]
    direction: Literal["bullish", "bearish"]
    confidence: float
    anchor_points: list[DetectedAnchor]


def detect_patterns(frame: pd.DataFrame) -> list[DetectedPattern]:
    normalized = _prepare_frame(frame)
    if normalized is None:
        return []

    patterns: list[DetectedPattern] = []
    patterns.extend(_detect_double_top(normalized))
    patterns.extend(_detect_double_bottom(normalized))
    patterns.extend(_detect_head_shoulders_top(normalized))
    patterns.extend(_detect_head_shoulders_bottom(normalized))
    return patterns


def _prepare_frame(frame: pd.DataFrame) -> pd.DataFrame | None:
    required_columns = {"date", "high", "low", "close"}
    if frame.empty or not required_columns.issubset(frame.columns):
        return None

    normalized = frame.copy()
    normalized["date"] = pd.to_datetime(normalized["date"], errors="coerce")
    normalized = normalized.dropna(subset=["date", "high", "low", "close"]).sort_values("date").reset_index(drop=True)

    if normalized.empty:
        return None

    for column in ["high", "low", "close"]:
        normalized[column] = pd.to_numeric(normalized[column], errors="coerce")

    normalized = normalized.dropna(subset=["high", "low", "close"]).reset_index(drop=True)
    if len(normalized) < 5:
        return None

    return normalized


def _detect_double_top(frame: pd.DataFrame) -> list[DetectedPattern]:
    peaks = _local_extrema(frame["high"], kind="max")
    if len(peaks) < 2:
        return []

    highs = frame["high"].tolist()
    lows = frame["low"].tolist()
    closes = frame["close"].tolist()

    for left_peak, right_peak in _adjacent_pairs(peaks):
        if right_peak - left_peak < 2:
            continue

        left_value = highs[left_peak]
        right_value = highs[right_peak]
        average_peak = (left_value + right_value) / 2
        if average_peak <= 0:
            continue

        peak_gap_ratio = abs(left_value - right_value) / average_peak
        if peak_gap_ratio > 0.03:
            continue

        neckline_index = min(range(left_peak + 1, right_peak), key=lambda idx: lows[idx])
        neckline_value = lows[neckline_index]
        retracement_ratio = (average_peak - neckline_value) / average_peak
        if retracement_ratio < 0.05:
            continue

        trailing_closes = closes[right_peak + 1 :] or [closes[right_peak]]
        if min(trailing_closes) > neckline_value * 1.02:
            continue

        confidence = round(max(0.55, min(0.95, 1.0 - peak_gap_ratio - max(0.0, 0.08 - retracement_ratio))), 4)
        return [
            DetectedPattern(
                pattern_name="double_top",
                direction="bearish",
                confidence=confidence,
                anchor_points=[
                    _anchor(frame, left_peak, "left_peak", "high"),
                    _anchor(frame, neckline_index, "neckline", "low"),
                    _anchor(frame, right_peak, "right_peak", "high"),
                ],
            )
        ]

    return []


def _detect_double_bottom(frame: pd.DataFrame) -> list[DetectedPattern]:
    bottoms = _local_extrema(frame["low"], kind="min")
    if len(bottoms) < 2:
        return []

    highs = frame["high"].tolist()
    lows = frame["low"].tolist()
    closes = frame["close"].tolist()

    for left_bottom, right_bottom in _adjacent_pairs(bottoms):
        if right_bottom - left_bottom < 2:
            continue

        left_value = lows[left_bottom]
        right_value = lows[right_bottom]
        average_bottom = (left_value + right_value) / 2
        if average_bottom <= 0:
            continue

        bottom_gap_ratio = abs(left_value - right_value) / average_bottom
        if bottom_gap_ratio > 0.03:
            continue

        neckline_index = max(range(left_bottom + 1, right_bottom), key=lambda idx: highs[idx])
        neckline_value = highs[neckline_index]
        rebound_ratio = (neckline_value - average_bottom) / average_bottom
        if rebound_ratio < 0.05:
            continue

        trailing_closes = closes[right_bottom + 1 :] or [closes[right_bottom]]
        if max(trailing_closes) < neckline_value * 0.98:
            continue

        confidence = round(max(0.55, min(0.95, 1.0 - bottom_gap_ratio - max(0.0, 0.08 - rebound_ratio))), 4)
        return [
            DetectedPattern(
                pattern_name="double_bottom",
                direction="bullish",
                confidence=confidence,
                anchor_points=[
                    _anchor(frame, left_bottom, "left_bottom", "low"),
                    _anchor(frame, neckline_index, "neckline", "high"),
                    _anchor(frame, right_bottom, "right_bottom", "low"),
                ],
            )
        ]

    return []


def _detect_head_shoulders_top(frame: pd.DataFrame) -> list[DetectedPattern]:
    peaks = _local_extrema(frame["high"], kind="max")
    if len(peaks) < 3:
        return []

    highs = frame["high"].tolist()
    lows = frame["low"].tolist()

    for left_shoulder, head, right_shoulder in _sliding_triplets(peaks):
        if head - left_shoulder < 2 or right_shoulder - head < 2:
            continue

        left_value = highs[left_shoulder]
        head_value = highs[head]
        right_value = highs[right_shoulder]
        shoulder_avg = (left_value + right_value) / 2
        if head_value <= max(left_value, right_value) or shoulder_avg <= 0:
            continue

        if abs(left_value - right_value) / shoulder_avg > 0.05:
            continue

        left_neckline = min(range(left_shoulder + 1, head), key=lambda idx: lows[idx])
        right_neckline = min(range(head + 1, right_shoulder), key=lambda idx: lows[idx])

        return [
            DetectedPattern(
                pattern_name="head_shoulders_top",
                direction="bearish",
                confidence=0.7,
                anchor_points=[
                    _anchor(frame, left_shoulder, "left_shoulder", "high"),
                    _anchor(frame, left_neckline, "left_neckline", "low"),
                    _anchor(frame, head, "head", "high"),
                    _anchor(frame, right_neckline, "right_neckline", "low"),
                    _anchor(frame, right_shoulder, "right_shoulder", "high"),
                ],
            )
        ]

    return []


def _detect_head_shoulders_bottom(frame: pd.DataFrame) -> list[DetectedPattern]:
    bottoms = _local_extrema(frame["low"], kind="min")
    if len(bottoms) < 3:
        return []

    lows = frame["low"].tolist()
    highs = frame["high"].tolist()

    for left_shoulder, head, right_shoulder in _sliding_triplets(bottoms):
        if head - left_shoulder < 2 or right_shoulder - head < 2:
            continue

        left_value = lows[left_shoulder]
        head_value = lows[head]
        right_value = lows[right_shoulder]
        shoulder_avg = (left_value + right_value) / 2
        if head_value >= min(left_value, right_value) or shoulder_avg <= 0:
            continue

        if abs(left_value - right_value) / shoulder_avg > 0.05:
            continue

        left_neckline = max(range(left_shoulder + 1, head), key=lambda idx: highs[idx])
        right_neckline = max(range(head + 1, right_shoulder), key=lambda idx: highs[idx])

        return [
            DetectedPattern(
                pattern_name="head_shoulders_bottom",
                direction="bullish",
                confidence=0.7,
                anchor_points=[
                    _anchor(frame, left_shoulder, "left_shoulder", "low"),
                    _anchor(frame, left_neckline, "left_neckline", "high"),
                    _anchor(frame, head, "head", "low"),
                    _anchor(frame, right_neckline, "right_neckline", "high"),
                    _anchor(frame, right_shoulder, "right_shoulder", "low"),
                ],
            )
        ]

    return []


def _local_extrema(series: pd.Series, kind: Literal["max", "min"]) -> list[int]:
    values = [float(value) for value in series.tolist()]
    extrema: list[int] = []

    for index in range(1, len(values) - 1):
        previous_value = values[index - 1]
        current_value = values[index]
        next_value = values[index + 1]

        if kind == "max" and current_value > previous_value and current_value >= next_value:
            extrema.append(index)
        if kind == "min" and current_value < previous_value and current_value <= next_value:
            extrema.append(index)

    return extrema


def _anchor(frame: pd.DataFrame, index: int, role: str, column: Literal["high", "low"]) -> DetectedAnchor:
    timestamp = pd.Timestamp(frame.iloc[index]["date"]).value // 1_000_000
    value = float(frame.iloc[index][column])
    return DetectedAnchor(role=role, timestamp=int(timestamp), value=value)


def _adjacent_pairs(indices: list[int]) -> list[tuple[int, int]]:
    return list(zip(indices, indices[1:]))


def _sliding_triplets(indices: list[int]) -> list[tuple[int, int, int]]:
    return [(indices[idx], indices[idx + 1], indices[idx + 2]) for idx in range(len(indices) - 2)]
