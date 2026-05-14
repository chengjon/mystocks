"""Monitoring control use-case service.

The API layer owns HTTP concerns; this service owns the monitoring task
lifecycle and control-state semantics.
"""

from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any, Callable, Protocol


class MonitoringControlSource(Protocol):
    is_monitoring: bool
    monitored_symbols: list[str]

    async def start_monitoring(self, symbols: list[str] | None = None, interval: int = 60) -> None:
        """Start the underlying monitoring loop."""

    def stop_monitoring(self) -> None:
        """Stop the underlying monitoring loop."""


class MonitoringControlService:
    """Coordinate monitoring start, stop, and status behind a small interface."""

    def __init__(
        self,
        monitoring_service: MonitoringControlSource,
        now: Callable[[], datetime] = datetime.now,
    ) -> None:
        self._monitoring_service = monitoring_service
        self._now = now
        self._task: asyncio.Task[Any] | None = None
        self._interval: int | None = None
        self._last_started_at: datetime | None = None

    def get_task(self) -> asyncio.Task[Any] | None:
        task = self._task
        if task is not None and task.done() and not self._monitoring_service.is_monitoring:
            self._task = None
            return None
        return task

    def build_payload(self, *, include_interval_key: str | None = None) -> dict[str, Any]:
        symbols = list(self._monitoring_service.monitored_symbols or [])
        payload: dict[str, Any] = {
            "is_monitoring": bool(self._monitoring_service.is_monitoring),
            "monitored_symbols": symbols,
            "monitored_count": len(symbols),
        }
        if include_interval_key:
            payload[include_interval_key] = self._interval
        return payload

    async def start(self, *, symbols: list[str] | None, interval: int) -> dict[str, Any]:
        current_task = self.get_task()
        if not self._monitoring_service.is_monitoring or current_task is None:
            self._interval = interval
            self._last_started_at = self._now()
            self._task = asyncio.create_task(
                self._monitoring_service.start_monitoring(symbols=symbols, interval=interval)
            )
            await asyncio.sleep(0)
        return self.build_payload(include_interval_key="interval")

    async def stop(self) -> dict[str, Any]:
        self._monitoring_service.stop_monitoring()
        self._monitoring_service.monitored_symbols = []

        task = self.get_task()
        if task is not None:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        self._task = None
        self._interval = None
        self._last_started_at = None
        return self.build_payload()

    def get_status(self) -> dict[str, Any]:
        return self.build_payload(include_interval_key="update_interval")
