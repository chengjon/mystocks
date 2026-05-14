from __future__ import annotations

from datetime import datetime
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest


ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = ROOT / "web" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.models.monitoring import AlertLevel, AlertRecordResponse
from app.services.monitoring_alert_record_service import MonitoringAlertRecordService


def _record_payload(record_id: int, *, is_read: bool = False) -> dict[str, object]:
    return {
        "id": record_id,
        "rule_id": 10,
        "rule_name": "核心仓位风控",
        "symbol": "600519",
        "stock_name": "贵州茅台",
        "alert_time": datetime(2026, 3, 13, 10, record_id, 0),
        "alert_type": "price_change",
        "alert_level": "warning",
        "alert_title": "价格异动",
        "alert_message": "触发核心仓位风控提醒",
        "alert_details": {"record_id": record_id},
        "snapshot_data": {"price": 1800 + record_id},
        "is_read": is_read,
        "is_handled": False,
        "created_at": datetime(2026, 3, 13, 10, record_id, 1),
    }


def _record(record_id: int, *, is_read: bool = False) -> AlertRecordResponse:
    return AlertRecordResponse(**_record_payload(record_id, is_read=is_read))


class StubAlertRecordSource:
    def __init__(self) -> None:
        self.calls: list[tuple] = []
        self.fail_list = False
        self.records = [
            SimpleNamespace(**_record_payload(1, is_read=False)),
            SimpleNamespace(**_record_payload(2, is_read=False)),
            SimpleNamespace(**_record_payload(3, is_read=True)),
        ]
        self.read_success_by_id = {1: True, 2: False, 3: True}

    def get_alert_records(self, **filters):
        self.calls.append(("list", filters))
        if self.fail_list:
            raise RuntimeError("database unavailable")
        records = self.records
        if "is_read" in filters:
            records = [record for record in records if record.is_read is filters["is_read"]]
        return records, len(records)

    def mark_alert_read(self, alert_id: int) -> bool:
        self.calls.append(("mark", alert_id))
        return self.read_success_by_id.get(alert_id, False)


def test_alert_record_service_lists_records_and_uses_runtime_fallback_with_pagination() -> None:
    source = StubAlertRecordSource()
    source.fail_list = True
    fallback_records = [_record(1), _record(2), _record(3)]
    service = MonitoringAlertRecordService(
        alert_record_source=source,
        runtime_fallback_enabled=lambda: True,
        runtime_records_loader=lambda: fallback_records,
    )

    page = service.list_records(
        symbol="600519",
        alert_type="price_change",
        alert_level=AlertLevel.WARNING,
        is_read=False,
        start_date=None,
        end_date=None,
        limit=1,
        offset=1,
    )

    assert [record.id for record in page.records] == [2]
    assert page.total == 3
    assert page.limit == 1
    assert page.offset == 1
    assert source.calls == [
        (
            "list",
            {
                "symbol": "600519",
                "alert_type": "price_change",
                "alert_level": "warning",
                "is_read": False,
                "start_date": None,
                "end_date": None,
                "limit": 1,
                "offset": 1,
            },
        )
    ]


def test_alert_record_service_marks_single_and_all_unread_records() -> None:
    source = StubAlertRecordSource()
    service = MonitoringAlertRecordService(
        alert_record_source=source,
        runtime_fallback_enabled=lambda: False,
        runtime_records_loader=lambda: [],
    )

    read_result = service.mark_read(1)
    with pytest.raises(ValueError, match="查询条件"):
        service.mark_read(2)
    all_read_result = service.mark_all_read()

    assert read_result == {"success": True, "message": "已标记为已读"}
    assert all_read_result == {"status": "updated", "scope": "all_alerts", "updated_count": 1}
    assert source.calls == [
        ("mark", 1),
        ("mark", 2),
        ("list", {"is_read": False, "limit": 1000, "offset": 0}),
        ("mark", 1),
        ("mark", 2),
    ]


def test_alert_record_service_counts_runtime_fallback_unread_records() -> None:
    service = MonitoringAlertRecordService(
        alert_record_source=StubAlertRecordSource(),
        runtime_fallback_enabled=lambda: True,
        runtime_records_loader=lambda: [_record(1, is_read=False), _record(2, is_read=True)],
    )

    assert service.mark_all_read() == {"status": "updated", "scope": "all_alerts", "updated_count": 1}
