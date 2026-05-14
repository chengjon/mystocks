from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = ROOT / "web" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.models.monitoring import MonitoringSummaryResponse
from app.services.monitoring_summary_service import MonitoringSummaryService


@dataclass
class StubMonitoringService:
    payload: dict[str, object]

    def get_monitoring_summary(self) -> dict[str, object]:
        return self.payload


def test_monitoring_summary_service_wraps_monitoring_service_result_when_mock_disabled() -> None:
    payload = {
        "total_stocks": 11,
        "limit_up_count": 4,
        "limit_down_count": 1,
        "strong_up_count": 3,
        "strong_down_count": 2,
        "avg_change_percent": 1.75,
        "total_amount": 998877.66,
        "active_alerts": 8,
        "unread_alerts": 3,
    }
    service = MonitoringSummaryService(
        monitoring_service=StubMonitoringService(payload),
        mock_enabled=lambda: False,
        mock_summary_loader=lambda: {"should": "not be used"},
    )

    result = service.get_summary()

    assert isinstance(result, MonitoringSummaryResponse)
    assert result.model_dump() == MonitoringSummaryResponse(**payload).model_dump()


def test_monitoring_summary_service_uses_mock_loader_when_mock_enabled() -> None:
    mock_payload = {
        "total_stocks": 2,
        "limit_up_count": 1,
        "limit_down_count": 0,
        "strong_up_count": 1,
        "strong_down_count": 0,
        "avg_change_percent": 5.5,
        "total_amount": 1234.5,
        "active_alerts": 1,
        "unread_alerts": 1,
    }
    service = MonitoringSummaryService(
        monitoring_service=StubMonitoringService({"total_stocks": 0}),
        mock_enabled=lambda: True,
        mock_summary_loader=lambda: mock_payload,
    )

    result = service.get_summary()

    assert result.model_dump() == MonitoringSummaryResponse(**mock_payload).model_dump()
