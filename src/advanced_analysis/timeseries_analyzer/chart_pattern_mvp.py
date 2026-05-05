"""Deterministic MVP chart-pattern detection helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

import pandas as pd


@dataclass
class DetectedAnchor:
    role: str
    timestamp: int
    value: float


@dataclass
class DetectedGapZone:
    start_timestamp: int
    end_timestamp: int
    upper_value: float
    lower_value: float
    filled_at: int | None


@dataclass
class DetectedPattern:
    pattern_name: Literal[
        "double_top",
        "double_bottom",
        "head_shoulders_top",
        "head_shoulders_bottom",
        "common_gap",
        "breakaway_gap",
        "runaway_gap",
        "exhaustion_gap",
    ]
    direction: Literal["bullish", "bearish"]
    confidence: float
    anchor_points: list[DetectedAnchor] = field(default_factory=list)
    gap_side: Literal["up", "down"] | None = None
    gap_fill_status: Literal["open", "partially_filled", "filled"] | None = None
    gap_zone: DetectedGapZone | None = None


@dataclass
class RawGapCandidate:
    previous_index: int
    gap_index: int
    gap_side: Literal["up", "down"]
    upper_value: float
    lower_value: float
    gap_ratio: float


MIN_GAP_RATIO = 0.005
BREAKAWAY_LOOKBACK_BARS = 10
BREAKAWAY_MAX_PRE_RANGE_RATIO = 0.08
BREAKAWAY_NO_FILL_WINDOW_BARS = 3
RUNAWAY_TREND_LOOKBACK_BARS = 5
RUNAWAY_MIN_TREND_RATIO = 0.04
RUNAWAY_NO_FULL_FILL_WINDOW_BARS = 5
EXHAUSTION_TREND_LOOKBACK_BARS = 5
EXHAUSTION_MIN_TREND_RATIO = 0.06
EXHAUSTION_FILL_CONFIRM_WINDOW_BARS = 3


def detect_patterns(frame: pd.DataFrame) -> list[DetectedPattern]:
    normalized = _prepare_frame(frame)
    if normalized is None:
        return []

    patterns: list[DetectedPattern] = []
    patterns.extend(_detect_double_top(normalized))
    patterns.extend(_detect_double_bottom(normalized))
    patterns.extend(_detect_head_shoulders_top(normalized))
    patterns.extend(_detect_head_shoulders_bottom(normalized))
    patterns.extend(_detect_gaps(normalized))
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
    candidates: list[DetectedPattern] = []

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
        candidates.append(
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
        )

    return _select_preferred_pattern(candidates)


def _detect_double_bottom(frame: pd.DataFrame) -> list[DetectedPattern]:
    bottoms = _local_extrema(frame["low"], kind="min")
    if len(bottoms) < 2:
        return []

    highs = frame["high"].tolist()
    lows = frame["low"].tolist()
    closes = frame["close"].tolist()
    candidates: list[DetectedPattern] = []

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
        candidates.append(
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
        )

    return _select_preferred_pattern(candidates)


def _detect_head_shoulders_top(frame: pd.DataFrame) -> list[DetectedPattern]:
    peaks = _local_extrema(frame["high"], kind="max")
    if len(peaks) < 3:
        return []

    highs = frame["high"].tolist()
    lows = frame["low"].tolist()
    closes = frame["close"].tolist()
    candidates: list[DetectedPattern] = []

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
        neckline_level = min(lows[left_neckline], lows[right_neckline])
        head_prominence_ratio = (head_value - shoulder_avg) / shoulder_avg
        neckline_depth_ratio = (shoulder_avg - neckline_level) / shoulder_avg
        trailing_closes = closes[right_shoulder + 1 :] or [closes[right_shoulder]]

        if head_prominence_ratio < 0.03 or neckline_depth_ratio < 0.03:
            continue

        if min(trailing_closes) > neckline_level * 1.02:
            continue

        confidence = round(
            max(0.55, min(0.92, 0.55 + head_prominence_ratio + neckline_depth_ratio - abs(left_value - right_value) / shoulder_avg)),
            4,
        )

        candidates.append(
            DetectedPattern(
                pattern_name="head_shoulders_top",
                direction="bearish",
                confidence=confidence,
                anchor_points=[
                    _anchor(frame, left_shoulder, "left_shoulder", "high"),
                    _anchor(frame, left_neckline, "left_neckline", "low"),
                    _anchor(frame, head, "head", "high"),
                    _anchor(frame, right_neckline, "right_neckline", "low"),
                    _anchor(frame, right_shoulder, "right_shoulder", "high"),
                ],
            )
        )

    return _select_preferred_pattern(candidates)


def _detect_head_shoulders_bottom(frame: pd.DataFrame) -> list[DetectedPattern]:
    bottoms = _local_extrema(frame["low"], kind="min")
    if len(bottoms) < 3:
        return []

    lows = frame["low"].tolist()
    highs = frame["high"].tolist()
    closes = frame["close"].tolist()
    candidates: list[DetectedPattern] = []

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
        neckline_level = max(highs[left_neckline], highs[right_neckline])
        head_prominence_ratio = (shoulder_avg - head_value) / shoulder_avg
        neckline_height_ratio = (neckline_level - shoulder_avg) / shoulder_avg
        trailing_closes = closes[right_shoulder + 1 :] or [closes[right_shoulder]]

        if head_prominence_ratio < 0.03 or neckline_height_ratio < 0.03:
            continue

        if max(trailing_closes) < neckline_level * 0.98:
            continue

        confidence = round(
            max(0.55, min(0.92, 0.55 + head_prominence_ratio + neckline_height_ratio - abs(left_value - right_value) / shoulder_avg)),
            4,
        )

        candidates.append(
            DetectedPattern(
                pattern_name="head_shoulders_bottom",
                direction="bullish",
                confidence=confidence,
                anchor_points=[
                    _anchor(frame, left_shoulder, "left_shoulder", "low"),
                    _anchor(frame, left_neckline, "left_neckline", "high"),
                    _anchor(frame, head, "head", "low"),
                    _anchor(frame, right_neckline, "right_neckline", "high"),
                    _anchor(frame, right_shoulder, "right_shoulder", "low"),
                ],
            )
        )

    return _select_preferred_pattern(candidates)


def _detect_gaps(frame: pd.DataFrame) -> list[DetectedPattern]:
    detections: list[DetectedPattern] = []

    for candidate in _find_raw_gaps(frame):
        gap_fill_status, filled_at, filled_index, partial_fill_index = _assess_gap_fill(frame, candidate)
        pattern_name = _classify_gap(frame, candidate, filled_index, partial_fill_index)
        confidence = _gap_confidence(pattern_name, candidate, frame)
        detections.append(
            _make_gap_pattern(
                frame=frame,
                candidate=candidate,
                pattern_name=pattern_name,
                gap_fill_status=gap_fill_status,
                filled_at=filled_at,
                confidence=confidence,
            )
        )

    return detections


def _find_raw_gaps(frame: pd.DataFrame) -> list[RawGapCandidate]:
    gaps: list[RawGapCandidate] = []

    for gap_index in range(1, len(frame)):
        previous_index = gap_index - 1
        previous_high = float(frame.iloc[previous_index]["high"])
        previous_low = float(frame.iloc[previous_index]["low"])
        current_high = float(frame.iloc[gap_index]["high"])
        current_low = float(frame.iloc[gap_index]["low"])

        if current_low > previous_high:
            gap_ratio = (current_low - previous_high) / previous_high if previous_high > 0 else 0.0
            if gap_ratio >= MIN_GAP_RATIO:
                gaps.append(
                    RawGapCandidate(
                        previous_index=previous_index,
                        gap_index=gap_index,
                        gap_side="up",
                        upper_value=current_low,
                        lower_value=previous_high,
                        gap_ratio=gap_ratio,
                    )
                )
            continue

        if current_high < previous_low:
            gap_ratio = (previous_low - current_high) / previous_low if previous_low > 0 else 0.0
            if gap_ratio >= MIN_GAP_RATIO:
                gaps.append(
                    RawGapCandidate(
                        previous_index=previous_index,
                        gap_index=gap_index,
                        gap_side="down",
                        upper_value=previous_low,
                        lower_value=current_high,
                        gap_ratio=gap_ratio,
                    )
                )

    return gaps


def _assess_gap_fill(
    frame: pd.DataFrame,
    candidate: RawGapCandidate,
) -> tuple[Literal["open", "partially_filled", "filled"], int | None, int | None, int | None]:
    partial_fill_index: int | None = None

    for index in range(candidate.gap_index + 1, len(frame)):
        low = float(frame.iloc[index]["low"])
        high = float(frame.iloc[index]["high"])

        if candidate.gap_side == "up":
            if low <= candidate.lower_value:
                return "filled", _timestamp_at(frame, index), index, partial_fill_index
            if low < candidate.upper_value and partial_fill_index is None:
                partial_fill_index = index
        else:
            if high >= candidate.upper_value:
                return "filled", _timestamp_at(frame, index), index, partial_fill_index
            if high > candidate.lower_value and partial_fill_index is None:
                partial_fill_index = index

    if partial_fill_index is not None:
        return "partially_filled", None, None, partial_fill_index
    return "open", None, None, None


def _classify_gap(
    frame: pd.DataFrame,
    candidate: RawGapCandidate,
    filled_index: int | None,
    partial_fill_index: int | None,
) -> Literal["common_gap", "breakaway_gap", "runaway_gap", "exhaustion_gap"]:
    trend_ratio = _trend_ratio(frame, candidate.gap_index, candidate.gap_side, EXHAUSTION_TREND_LOOKBACK_BARS)
    pre_range_ratio = _pre_gap_range_ratio(frame, candidate.gap_index, BREAKAWAY_LOOKBACK_BARS)

    if trend_ratio >= EXHAUSTION_MIN_TREND_RATIO and _filled_within_window(candidate.gap_index, filled_index, EXHAUSTION_FILL_CONFIRM_WINDOW_BARS):
        return "exhaustion_gap"

    if pre_range_ratio is not None and pre_range_ratio <= BREAKAWAY_MAX_PRE_RANGE_RATIO and _no_fill_within_window(
        candidate.gap_index,
        filled_index,
        partial_fill_index,
        BREAKAWAY_NO_FILL_WINDOW_BARS,
    ):
        return "breakaway_gap"

    if trend_ratio >= RUNAWAY_MIN_TREND_RATIO and _not_filled_within_window(candidate.gap_index, filled_index, RUNAWAY_NO_FULL_FILL_WINDOW_BARS):
        return "runaway_gap"

    return "common_gap"


def _gap_confidence(pattern_name: str, candidate: RawGapCandidate, frame: pd.DataFrame) -> float:
    trend_ratio = _trend_ratio(frame, candidate.gap_index, candidate.gap_side, EXHAUSTION_TREND_LOOKBACK_BARS)

    if pattern_name == "exhaustion_gap":
        raw_confidence = 0.72 + min(0.18, trend_ratio)
    elif pattern_name == "breakaway_gap":
        raw_confidence = 0.68 + min(0.2, candidate.gap_ratio * 4)
    elif pattern_name == "runaway_gap":
        raw_confidence = 0.64 + min(0.2, trend_ratio)
    else:
        raw_confidence = 0.55 + min(0.12, candidate.gap_ratio * 3)

    return round(max(0.55, min(0.95, raw_confidence)), 4)


def _make_gap_pattern(
    frame: pd.DataFrame,
    candidate: RawGapCandidate,
    pattern_name: Literal["common_gap", "breakaway_gap", "runaway_gap", "exhaustion_gap"],
    gap_fill_status: Literal["open", "partially_filled", "filled"],
    filled_at: int | None,
    confidence: float,
) -> DetectedPattern:
    return DetectedPattern(
        pattern_name=pattern_name,
        direction="bullish" if candidate.gap_side == "up" else "bearish",
        confidence=confidence,
        anchor_points=[],
        gap_side=candidate.gap_side,
        gap_fill_status=gap_fill_status,
        gap_zone=DetectedGapZone(
            start_timestamp=_timestamp_at(frame, candidate.previous_index),
            end_timestamp=_timestamp_at(frame, candidate.gap_index),
            upper_value=round(candidate.upper_value, 4),
            lower_value=round(candidate.lower_value, 4),
            filled_at=filled_at,
        ),
    )


def _trend_ratio(frame: pd.DataFrame, gap_index: int, gap_side: Literal["up", "down"], lookback_bars: int) -> float:
    start_index = max(0, gap_index - lookback_bars)
    history = frame.iloc[start_index:gap_index]
    if len(history) < 2:
        return 0.0

    first_close = float(history.iloc[0]["close"])
    last_close = float(history.iloc[-1]["close"])
    if first_close <= 0:
        return 0.0

    if gap_side == "up":
        return max(0.0, (last_close - first_close) / first_close)
    return max(0.0, (first_close - last_close) / first_close)


def _pre_gap_range_ratio(frame: pd.DataFrame, gap_index: int, lookback_bars: int) -> float | None:
    start_index = max(0, gap_index - lookback_bars)
    history = frame.iloc[start_index:gap_index]
    if len(history) < lookback_bars:
        return None

    base_close = float(history.iloc[0]["close"])
    if base_close <= 0:
        return None

    highest = float(history["high"].max())
    lowest = float(history["low"].min())
    return max(0.0, (highest - lowest) / base_close)


def _filled_within_window(gap_index: int, filled_index: int | None, window_bars: int) -> bool:
    return filled_index is not None and filled_index <= gap_index + window_bars


def _not_filled_within_window(gap_index: int, filled_index: int | None, window_bars: int) -> bool:
    return filled_index is None or filled_index > gap_index + window_bars


def _no_fill_within_window(
    gap_index: int,
    filled_index: int | None,
    partial_fill_index: int | None,
    window_bars: int,
) -> bool:
    return (
        (filled_index is None or filled_index > gap_index + window_bars)
        and (partial_fill_index is None or partial_fill_index > gap_index + window_bars)
    )


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
    value = float(frame.iloc[index][column])
    return DetectedAnchor(role=role, timestamp=_timestamp_at(frame, index), value=value)


def _timestamp_at(frame: pd.DataFrame, index: int) -> int:
    timestamp = pd.Timestamp(frame.iloc[index]["date"]).value // 1_000_000
    return int(timestamp)


def _adjacent_pairs(indices: list[int]) -> list[tuple[int, int]]:
    return list(zip(indices, indices[1:]))


def _sliding_triplets(indices: list[int]) -> list[tuple[int, int, int]]:
    return [(indices[idx], indices[idx + 1], indices[idx + 2]) for idx in range(len(indices) - 2)]


def _select_preferred_pattern(candidates: list[DetectedPattern]) -> list[DetectedPattern]:
    if not candidates:
        return []

    preferred = max(candidates, key=lambda candidate: (candidate.anchor_points[-1].timestamp, candidate.confidence))
    return [preferred]
