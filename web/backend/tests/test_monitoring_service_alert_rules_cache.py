from __future__ import annotations

from datetime import datetime
from types import SimpleNamespace

from web.backend.app.services.monitoring_service import MonitoringService


class _FakeQuery:
    def __init__(self, rows):
        self._rows = rows

    def filter(self, *_args, **_kwargs):
        return self

    def order_by(self, *_args, **_kwargs):
        return self

    def all(self):
        return self._rows


class _FakeSession:
    def __init__(self, rows, call_counter):
        self._rows = rows
        self._call_counter = call_counter

    def query(self, *_args, **_kwargs):
        self._call_counter["query"] += 1
        return _FakeQuery(self._rows)

    def close(self):
        return None


def test_alert_rule_payloads_use_ttl_cache_and_invalidation(monkeypatch):
    service = MonitoringService()
    service._clear_alert_rules_cache()
    service._alert_rules_payload_cache_ttl_seconds = 60

    call_counter = {"query": 0}
    rows = [
        SimpleNamespace(
            id=1,
            rule_name="高优先级监控",
            rule_type="limit_up",
            description="desc",
            symbol="600519",
            stock_name="贵州茅台",
            parameters={"threshold": 9.8},
            trigger_conditions={"field": "change_percent"},
            notification_config={"channels": ["ui"]},
            is_active=True,
            priority=5,
            created_at=datetime(2026, 4, 20, 1, 0, 0),
            updated_at=datetime(2026, 4, 20, 1, 0, 0),
        )
    ]

    monkeypatch.setattr(service, "get_session", lambda: _FakeSession(rows, call_counter))

    first = service.get_alert_rule_payloads(rule_type="limit_up", is_active=True)
    second = service.get_alert_rule_payloads(rule_type="limit_up", is_active=True)

    assert call_counter["query"] == 1
    assert first == second
    assert first[0]["rule_name"] == "高优先级监控"

    service._clear_alert_rules_cache()
    third = service.get_alert_rule_payloads(rule_type="limit_up", is_active=True)

    assert call_counter["query"] == 2
    assert third[0]["notification_config"] == {"channels": ["ui"]}
