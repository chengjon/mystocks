"""Monitoring today-statistics use-case service."""

from __future__ import annotations

from typing import Any, Protocol

from sqlalchemy import text


class MonitoringTodayStatisticsSource(Protocol):
    """Persistence-facing source for monitoring statistics views."""

    def get_session(self) -> Any:
        """Return a database session."""


class MonitoringTodayStatisticsService:
    """Application-level orchestration for today's monitoring statistics."""

    def __init__(self, statistics_source: MonitoringTodayStatisticsSource) -> None:
        self._statistics_source = statistics_source

    def get_today_statistics(self) -> dict[str, Any]:
        """Read today's monitoring statistics from the configured database views."""
        session = self._statistics_source.get_session()
        try:
            alerts_summary = session.execute(text("SELECT * FROM v_today_alerts_summary")).fetchall()
            active_rules = session.execute(text("SELECT * FROM v_active_alert_rules LIMIT 10")).fetchall()
            realtime_summary = session.execute(text("SELECT * FROM v_realtime_summary")).fetchone()

            return {
                "alerts_summary": [dict(row._mapping) for row in alerts_summary],
                "active_rules": [dict(row._mapping) for row in active_rules],
                "realtime_summary": dict(realtime_summary._mapping) if realtime_summary else {},
            }
        finally:
            session.close()
