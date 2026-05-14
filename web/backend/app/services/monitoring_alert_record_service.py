"""Monitoring alert-record use-case service."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from typing import Any, Protocol

from app.models.monitoring import AlertLevel, AlertRecordResponse


@dataclass(frozen=True)
class AlertRecordsPage:
    """Normalized alert-record page returned to the route layer."""

    records: list[AlertRecordResponse]
    total: int
    limit: int
    offset: int


class MonitoringAlertRecordSource(Protocol):
    """Persistence-facing alert-record operations used by the API service."""

    def get_alert_records(self, **filters: Any) -> tuple[list[Any], int]:
        """Return alert records and total count for a filter set."""

    def mark_alert_read(self, alert_id: int) -> bool:
        """Mark one alert record as read."""


class MonitoringAlertRecordService:
    """Application-level alert-record orchestration for monitoring routes."""

    def __init__(
        self,
        alert_record_source: MonitoringAlertRecordSource,
        *,
        runtime_fallback_enabled: Callable[[], bool],
        runtime_records_loader: Callable[[], list[AlertRecordResponse]],
    ) -> None:
        self._alert_record_source = alert_record_source
        self._runtime_fallback_enabled = runtime_fallback_enabled
        self._runtime_records_loader = runtime_records_loader

    def list_records(
        self,
        *,
        symbol: str | None = None,
        alert_type: str | None = None,
        alert_level: AlertLevel | str | None = None,
        is_read: bool | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> AlertRecordsPage:
        """List alert records and normalize ORM/domain objects into response models."""
        normalized_alert_level = alert_level.value if isinstance(alert_level, AlertLevel) else alert_level

        try:
            records, total = self._alert_record_source.get_alert_records(
                symbol=symbol,
                alert_type=alert_type,
                alert_level=normalized_alert_level,
                is_read=is_read,
                start_date=start_date,
                end_date=end_date,
                limit=limit,
                offset=offset,
            )
            return AlertRecordsPage(
                records=[AlertRecordResponse.model_validate(record) for record in records],
                total=total,
                limit=limit,
                offset=offset,
            )
        except Exception:
            if self._runtime_fallback_enabled():
                fallback_records = self._runtime_records_loader()
                return AlertRecordsPage(
                    records=fallback_records[offset : offset + limit],
                    total=len(fallback_records),
                    limit=limit,
                    offset=offset,
                )
            raise

    def mark_read(self, alert_id: int) -> dict[str, Any]:
        """Mark a single alert record as read."""
        success = self._alert_record_source.mark_alert_read(alert_id)
        if not success:
            raise ValueError("查询条件")
        return {"success": True, "message": "已标记为已读"}

    def mark_all_read(self) -> dict[str, Any]:
        """Mark currently unread alert records as read and return the update count."""
        if self._runtime_fallback_enabled():
            fallback_records = self._runtime_records_loader()
            updated_count = sum(1 for record in fallback_records if not record.is_read)
            return {"status": "updated", "scope": "all_alerts", "updated_count": updated_count}

        records, _ = self._alert_record_source.get_alert_records(is_read=False, limit=1000, offset=0)
        updated_count = 0
        for record in records:
            if self._alert_record_source.mark_alert_read(record.id):
                updated_count += 1

        return {"status": "updated", "scope": "all_alerts", "updated_count": updated_count}
