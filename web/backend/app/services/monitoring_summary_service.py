"""Monitoring summary use-case service.

This module isolates monitoring summary assembly from the API layer so the
route stays thin and the summary behavior can be tested directly.
"""

from __future__ import annotations

from typing import Any, Callable, Mapping, Protocol

from app.core.config import settings
from app.models.monitoring import MonitoringSummaryResponse


class MonitoringSummarySource(Protocol):
    def get_monitoring_summary(self) -> Mapping[str, Any]:
        """Return a monitoring summary payload."""


def is_monitoring_summary_mock_enabled() -> bool:
    """Return whether the monitoring summary should use the mock payload."""

    return settings.use_mock_apis


def load_mock_monitoring_summary() -> dict[str, Any]:
    """Load the monitoring summary mock payload used by local and test runs."""

    from src.mock.mock_RealTimeMonitor import get_monitoring_summary as get_monitoring_summary_mock

    return get_monitoring_summary_mock()


class MonitoringSummaryService:
    """Build a validated monitoring summary response behind a small interface."""

    def __init__(
        self,
        monitoring_service: MonitoringSummarySource,
        mock_enabled: Callable[[], bool] = is_monitoring_summary_mock_enabled,
        mock_summary_loader: Callable[[], dict[str, Any]] = load_mock_monitoring_summary,
    ) -> None:
        self._monitoring_service = monitoring_service
        self._mock_enabled = mock_enabled
        self._mock_summary_loader = mock_summary_loader

    def get_summary(self) -> MonitoringSummaryResponse:
        if self._mock_enabled():
            return MonitoringSummaryResponse(**self._mock_summary_loader())

        summary = self._monitoring_service.get_monitoring_summary()
        return MonitoringSummaryResponse(**dict(summary))
