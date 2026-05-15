from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = ROOT / "web" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.services.monitoring_runtime_fallbacks import (
    build_runtime_alert_records,
    build_runtime_alert_rules,
    resolve_query_int,
    runtime_fallback_enabled,
)


def test_runtime_fallback_enabled_reads_testing_or_development_mode(monkeypatch):
    monkeypatch.delenv("TESTING", raising=False)
    monkeypatch.delenv("DEVELOPMENT_MODE", raising=False)

    assert runtime_fallback_enabled() is False

    monkeypatch.setenv("TESTING", "true")
    assert runtime_fallback_enabled() is True

    monkeypatch.setenv("TESTING", "false")
    monkeypatch.setenv("DEVELOPMENT_MODE", "true")
    assert runtime_fallback_enabled() is True


def test_build_runtime_alert_rules_returns_two_rule_payloads():
    rules = build_runtime_alert_rules()

    assert len(rules) == 2
    assert rules[0].rule_name == "核心仓位跌破止损线"
    assert rules[1].rule_name == "北向资金快速回落"


def test_build_runtime_alert_records_returns_two_record_payloads():
    records = build_runtime_alert_records()

    assert len(records) == 2
    assert records[0].alert_title == "止损预警"
    assert records[1].alert_title == "资金波动提醒"


def test_resolve_query_int_preserves_int_or_default_value():
    assert resolve_query_int(8, 3) == 8
    assert resolve_query_int(object(), 3) == 3
