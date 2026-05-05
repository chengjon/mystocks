"""Backend service for reviewed chart-pattern detections."""

from __future__ import annotations

from functools import lru_cache
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
from typing import Any

import pandas as pd

from app.api._technical_patterns_models import PatternAnchorPoint, PatternDetection
from app.services.data_source_factory import DataSourceFactory


@lru_cache(maxsize=1)
def _load_chart_pattern_detector():
    """Load the isolated MVP detector without triggering unrelated advanced-analysis package side effects."""
    module_path = Path(__file__).resolve().parents[4] / "src/advanced_analysis/timeseries_analyzer/chart_pattern_mvp.py"
    spec = spec_from_file_location("chart_pattern_mvp_runtime", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load chart pattern detector from {module_path}")

    module = module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.detect_patterns


class TechnicalPatternDetectionService:
    """Fetch price history and map analyzer findings to API models."""

    async def detect_for_symbol(self, symbol: str, period: str) -> list[PatternDetection]:
        factory = DataSourceFactory()
        adapter = await factory.get_data_source("technical_analysis")
        if adapter is None:
            raise RuntimeError("technical_analysis data source unavailable")

        result = await adapter.get_data("history", {"symbol": symbol, "period": period, "limit": 240})
        rows = result.get("data", [])
        return self.detect_from_history_rows(rows)

    def detect_from_history_rows(self, rows: list[dict[str, Any]]) -> list[PatternDetection]:
        frame = pd.DataFrame(rows)
        if frame.empty:
            return []
        if "date" in frame.columns:
            frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
        return self.detect_from_history_frame(frame)

    def detect_from_history_frame(self, frame: pd.DataFrame) -> list[PatternDetection]:
        detect_patterns = _load_chart_pattern_detector()
        findings = detect_patterns(frame)
        return [
            PatternDetection(
                pattern_name=finding.pattern_name,
                direction=finding.direction,
                confidence=finding.confidence,
                anchor_points=[
                    PatternAnchorPoint(role=point.role, timestamp=point.timestamp, value=point.value)
                    for point in finding.anchor_points
                ],
            )
            for finding in findings
        ]
