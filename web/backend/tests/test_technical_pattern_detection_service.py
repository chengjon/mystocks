from __future__ import annotations

import pandas as pd

from app.services.technical_pattern_detection_service import TechnicalPatternDetectionService


def _build_double_top_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": pd.date_range("2026-01-01", periods=7, freq="D"),
            "open": [10.0, 10.6, 11.1, 10.4, 11.0, 10.2, 9.9],
            "high": [10.3, 11.0, 11.5, 10.7, 11.4, 10.5, 10.0],
            "low": [9.8, 10.4, 10.8, 10.0, 10.8, 9.8, 9.6],
            "close": [10.1, 10.9, 11.3, 10.2, 11.2, 10.0, 9.7],
            "volume": [100, 120, 140, 110, 135, 150, 160],
        }
    )


def _build_double_bottom_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": pd.date_range("2026-02-01", periods=7, freq="D"),
            "open": [11.1, 10.7, 10.2, 11.0, 10.3, 11.3, 11.6],
            "high": [11.3, 10.9, 10.5, 11.4, 10.6, 11.5, 11.8],
            "low": [10.9, 10.4, 10.0, 10.7, 10.1, 10.8, 11.0],
            "close": [11.1, 10.6, 10.1, 11.3, 10.2, 11.4, 11.7],
            "volume": [130, 120, 160, 170, 150, 180, 190],
        }
    )


def _build_head_shoulders_top_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": pd.date_range("2026-03-01", periods=7, freq="D"),
            "open": [10.2, 11.6, 10.9, 12.6, 10.8, 11.4, 10.0],
            "high": [10.5, 12.0, 11.0, 13.0, 11.1, 11.9, 10.2],
            "low": [10.0, 11.3, 10.7, 12.2, 10.8, 11.2, 9.8],
            "close": [10.3, 11.8, 10.9, 12.7, 10.9, 11.5, 9.9],
            "volume": [100, 140, 120, 180, 130, 150, 170],
        }
    )


def _build_head_shoulders_bottom_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": pd.date_range("2026-04-01", periods=7, freq="D"),
            "open": [12.2, 11.0, 11.8, 10.0, 11.7, 11.1, 12.3],
            "high": [12.5, 11.2, 12.0, 10.5, 12.1, 11.3, 12.6],
            "low": [12.0, 10.8, 11.5, 9.8, 11.4, 10.9, 12.1],
            "close": [12.3, 11.0, 11.9, 10.1, 11.8, 11.2, 12.4],
            "volume": [110, 150, 125, 185, 135, 145, 175],
        }
    )


def _build_multiple_double_top_candidates_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": pd.date_range("2026-05-01", periods=11, freq="D"),
            "open": [10.0, 10.8, 11.1, 10.5, 11.0, 10.7, 10.8, 11.8, 10.3, 11.7, 9.8],
            "high": [10.2, 10.9, 11.2, 10.7, 11.1, 10.8, 10.9, 12.0, 10.8, 11.9, 10.1],
            "low": [9.9, 10.5, 10.8, 10.4, 10.9, 10.6, 10.7, 11.4, 10.1, 11.3, 9.6],
            "close": [10.0, 10.8, 11.1, 10.5, 11.0, 10.7, 10.8, 11.8, 10.3, 11.7, 9.7],
            "volume": [100, 120, 140, 130, 150, 145, 155, 180, 165, 175, 190],
        }
    )


def _build_head_shoulders_top_near_miss_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": pd.date_range("2026-06-01", periods=7, freq="D"),
            "open": [10.2, 11.6, 11.0, 11.9, 11.1, 11.6, 11.3],
            "high": [10.5, 12.0, 11.0, 12.1, 11.1, 11.9, 11.5],
            "low": [10.0, 11.3, 10.9, 11.4, 10.95, 11.2, 11.0],
            "close": [10.3, 11.8, 11.0, 12.0, 11.1, 11.7, 11.2],
            "volume": [100, 140, 120, 180, 130, 150, 155],
        }
    )


def _build_head_shoulders_bottom_near_miss_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": pd.date_range("2026-07-01", periods=7, freq="D"),
            "open": [12.2, 11.0, 11.8, 10.9, 11.7, 11.1, 11.2],
            "high": [12.5, 11.2, 12.0, 11.1, 12.1, 11.3, 11.6],
            "low": [12.0, 10.8, 11.5, 10.7, 11.4, 10.9, 11.2],
            "close": [12.3, 11.0, 11.9, 10.9, 11.8, 11.2, 11.1],
            "volume": [110, 150, 125, 185, 135, 145, 150],
        }
    )


def test_detect_patterns_returns_double_top_with_ordered_anchor_roles():
    service = TechnicalPatternDetectionService()

    detections = service.detect_from_history_frame(_build_double_top_frame())

    assert detections
    assert detections[0].pattern_name == "double_top"
    assert [point.role for point in detections[0].anchor_points] == ["left_peak", "neckline", "right_peak"]
    assert 0.0 <= detections[0].confidence <= 1.0


def test_detect_patterns_returns_double_bottom_with_ordered_anchor_roles():
    service = TechnicalPatternDetectionService()

    detections = service.detect_from_history_frame(_build_double_bottom_frame())

    assert detections
    assert detections[0].pattern_name == "double_bottom"
    assert [point.role for point in detections[0].anchor_points] == ["left_bottom", "neckline", "right_bottom"]
    assert 0.0 <= detections[0].confidence <= 1.0


def test_detect_patterns_returns_head_shoulders_top_with_ordered_anchor_roles():
    service = TechnicalPatternDetectionService()

    detections = service.detect_from_history_frame(_build_head_shoulders_top_frame())

    assert detections
    assert detections[0].pattern_name == "head_shoulders_top"
    assert [point.role for point in detections[0].anchor_points] == [
        "left_shoulder",
        "left_neckline",
        "head",
        "right_neckline",
        "right_shoulder",
    ]
    assert 0.0 <= detections[0].confidence <= 1.0


def test_detect_patterns_prefers_the_more_recent_double_top_candidate():
    service = TechnicalPatternDetectionService()

    detections = service.detect_from_history_frame(_build_multiple_double_top_candidates_frame())

    assert detections
    assert detections[0].pattern_name == "double_top"
    assert detections[0].anchor_points[0].timestamp == int(pd.Timestamp("2026-05-08").value // 1_000_000)
    assert detections[0].anchor_points[2].timestamp == int(pd.Timestamp("2026-05-10").value // 1_000_000)


def test_detect_patterns_does_not_emit_head_shoulders_top_without_break_confirmation():
    service = TechnicalPatternDetectionService()

    detections = service.detect_from_history_frame(_build_head_shoulders_top_near_miss_frame())

    assert "head_shoulders_top" not in {detection.pattern_name for detection in detections}


def test_detect_patterns_does_not_emit_head_shoulders_bottom_without_break_confirmation():
    service = TechnicalPatternDetectionService()

    detections = service.detect_from_history_frame(_build_head_shoulders_bottom_near_miss_frame())

    assert "head_shoulders_bottom" not in {detection.pattern_name for detection in detections}


def test_detect_patterns_returns_head_shoulders_bottom_with_ordered_anchor_roles():
    service = TechnicalPatternDetectionService()

    detections = service.detect_from_history_frame(_build_head_shoulders_bottom_frame())

    assert detections
    assert detections[0].pattern_name == "head_shoulders_bottom"
    assert [point.role for point in detections[0].anchor_points] == [
        "left_shoulder",
        "left_neckline",
        "head",
        "right_neckline",
        "right_shoulder",
    ]
    assert 0.0 <= detections[0].confidence <= 1.0
