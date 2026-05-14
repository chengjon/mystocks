from __future__ import annotations

from datetime import datetime
from pathlib import Path
import sys
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = ROOT / "web" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.models.monitoring import AlertRuleCreate, AlertRuleResponse, AlertRuleType, AlertRuleUpdate
from app.services.monitoring_alert_rule_service import MonitoringAlertRuleService


def _rule_payload(**overrides):
    payload = {
        "id": 101,
        "rule_name": "核心仓位跌破止损线",
        "rule_type": "technical_break",
        "description": "关键持仓跌破止损价时触发",
        "symbol": "600519",
        "stock_name": "贵州茅台",
        "parameters": {"stop_loss_price": 1750},
        "trigger_conditions": {"operator": "<=", "field": "current_price"},
        "notification_config": {"channels": ["ui"], "level": "critical"},
        "is_active": True,
        "priority": 5,
        "created_at": datetime(2026, 5, 14, 9, 30, 0),
        "updated_at": datetime(2026, 5, 14, 9, 30, 0),
    }
    payload.update(overrides)
    return payload


class StubAlertRuleSource:
    def __init__(self) -> None:
        self.calls: list[tuple] = []
        self.fail_list = False

    def get_alert_rule_payloads(self, *, rule_type=None, is_active=None):
        self.calls.append(("list", rule_type, is_active))
        if self.fail_list:
            raise RuntimeError("database unavailable")
        return [_rule_payload(id=201)]

    def create_alert_rule(self, rule_data):
        self.calls.append(("create", rule_data))
        return SimpleNamespace(**_rule_payload(id=202, rule_name=rule_data["rule_name"]))

    def update_alert_rule(self, rule_id, updates):
        self.calls.append(("update", rule_id, updates))
        return SimpleNamespace(**_rule_payload(id=rule_id, description=updates["description"]))

    def delete_alert_rule(self, rule_id):
        self.calls.append(("delete", rule_id))
        return True


def test_alert_rule_service_lists_payloads_and_uses_runtime_fallback_when_enabled() -> None:
    source = StubAlertRuleSource()
    source.fail_list = True
    fallback_rules = [AlertRuleResponse(**_rule_payload(id=301))]
    service = MonitoringAlertRuleService(
        alert_rule_source=source,
        runtime_fallback_enabled=lambda: True,
        runtime_rules_loader=lambda: fallback_rules,
    )

    result = service.list_rules(rule_type=AlertRuleType.LIMIT_UP, is_active=True)

    assert result == fallback_rules
    assert source.calls == [("list", "limit_up", True)]


def test_alert_rule_service_delegates_mutations_and_returns_response_models() -> None:
    source = StubAlertRuleSource()
    service = MonitoringAlertRuleService(
        alert_rule_source=source,
        runtime_fallback_enabled=lambda: False,
        runtime_rules_loader=lambda: [],
    )

    created = service.create_rule(
        AlertRuleCreate(
            rule_name="茅台涨停监控",
            rule_type=AlertRuleType.LIMIT_UP,
            symbol="600519",
            stock_name="贵州茅台",
        )
    )
    updated = service.update_rule(202, AlertRuleUpdate(description="更新后的涨停提醒规则"))
    deleted = service.delete_rule(202)

    assert created.rule_name == "茅台涨停监控"
    assert updated.description == "更新后的涨停提醒规则"
    assert deleted == {"success": True, "message": "告警规则已删除"}
    create_call, update_call, delete_call = source.calls
    assert create_call[0] == "create"
    assert create_call[1]["rule_name"] == "茅台涨停监控"
    assert create_call[1]["rule_type"] == AlertRuleType.LIMIT_UP
    assert create_call[1]["symbol"] == "600519"
    assert update_call == ("update", 202, {"description": "更新后的涨停提醒规则"})
    assert delete_call == ("delete", 202)
