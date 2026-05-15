from __future__ import annotations

from pathlib import Path
import sys
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = ROOT / "web" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.services.monitoring_today_statistics_service import MonitoringTodayStatisticsService


class FakeSession:
    def __init__(self) -> None:
        self.executed_sql: list[str] = []
        self.closed = False

    def execute(self, statement):
        sql = str(statement)
        self.executed_sql.append(sql)
        if "v_today_alerts_summary" in sql:
            return SimpleNamespace(fetchall=lambda: [_row({"alert_type": "limit_up", "count": 2})])
        if "v_active_alert_rules" in sql:
            return SimpleNamespace(fetchall=lambda: [_row({"id": 7, "rule_name": "涨停监控"})])
        if "v_realtime_summary" in sql:
            return SimpleNamespace(fetchone=lambda: _row({"total_stocks": 320, "limit_up_count": 12}))
        raise AssertionError(f"unexpected SQL: {sql}")

    def close(self) -> None:
        self.closed = True


class FakeMonitoringSource:
    def __init__(self) -> None:
        self.session = FakeSession()
        self.calls = 0

    def get_session(self):
        self.calls += 1
        return self.session


def _row(mapping: dict[str, object]) -> SimpleNamespace:
    return SimpleNamespace(_mapping=mapping)


def test_today_statistics_service_queries_expected_views_and_closes_session() -> None:
    source = FakeMonitoringSource()
    service = MonitoringTodayStatisticsService(source)

    result = service.get_today_statistics()

    assert result == {
        "alerts_summary": [{"alert_type": "limit_up", "count": 2}],
        "active_rules": [{"id": 7, "rule_name": "涨停监控"}],
        "realtime_summary": {"total_stocks": 320, "limit_up_count": 12},
    }
    assert source.calls == 1
    assert source.session.closed is True
    assert source.session.executed_sql == [
        "SELECT * FROM v_today_alerts_summary",
        "SELECT * FROM v_active_alert_rules LIMIT 10",
        "SELECT * FROM v_realtime_summary",
    ]


def test_today_statistics_service_returns_empty_realtime_summary_when_view_is_empty() -> None:
    source = FakeMonitoringSource()
    source.session.execute = lambda statement: SimpleNamespace(fetchall=lambda: [], fetchone=lambda: None)
    service = MonitoringTodayStatisticsService(source)

    result = service.get_today_statistics()

    assert result["realtime_summary"] == {}
    assert source.session.closed is True
