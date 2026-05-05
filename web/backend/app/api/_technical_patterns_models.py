"""Structured API models for reviewed technical-pattern detections."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

PatternName = Literal["double_top", "double_bottom", "head_shoulders_top", "head_shoulders_bottom"]
PatternDirection = Literal["bullish", "bearish"]
PatternPeriod = Literal["daily", "weekly", "monthly"]
PatternStatus = Literal["available", "empty"]


class PatternAnchorPoint(BaseModel):
    """A chart-renderable anchor emitted by the backend detector."""

    role: str = Field(..., description="Pattern-defined anchor role.")
    timestamp: int = Field(..., description="Millisecond epoch timestamp for the anchor.")
    value: float = Field(..., description="Price value at the anchor.")


class PatternDetection(BaseModel):
    """A reviewed automatic chart-pattern detection."""

    pattern_name: PatternName = Field(..., description="Reviewed MVP pattern identifier.")
    direction: PatternDirection = Field(..., description="Pattern bias inferred from the reviewed detector.")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Detector confidence in the inclusive range 0.0-1.0.")
    anchor_points: list[PatternAnchorPoint] = Field(
        default_factory=list,
        description="Ordered anchor points that can be rendered directly on the chart.",
    )


class PatternDetectionData(BaseModel):
    """Envelope for the reviewed technical-pattern route payload."""

    status: PatternStatus = Field(..., description="Route result status: available when detections exist, empty otherwise.")
    symbol: str = Field(..., description="Normalized symbol requested from the pattern endpoint.")
    period: PatternPeriod = Field(..., description="Reviewed analysis period.")
    patterns: list[PatternDetection] = Field(
        default_factory=list,
        description="Reviewed automatic pattern detections for the requested symbol and period.",
    )
