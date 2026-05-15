"""
File-level route and helper contract tests for monitoring.py.

这里校验当前 18 个监控路由、fallback helper 和核心响应模型，
不触发真实数据库查询。
"""

from __future__ import annotations

import asyncio
import importlib
import sys
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

import dotenv
import pytest


ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = ROOT / "web" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


@pytest.fixture
def monitoring_module(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("POSTGRESQL_HOST", "localhost")
    monkeypatch.setenv("POSTGRESQL_USER", "postgres")
    monkeypatch.setenv("POSTGRESQL_PASSWORD", "password")
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("BACKEND_PORT", "8020")
    monkeypatch.setenv("BACKEND_BACKUP_PORT", "8021")
    monkeypatch.setattr(dotenv, "load_dotenv", lambda *args, **kwargs: False)
    return importlib.import_module("app.api.monitoring")


class TestMonitoringAPIFile:
    @pytest.mark.file_test
    def test_router_registers_expected_monitoring_routes(self, monitoring_module):
        route_methods = {(route.path, tuple(sorted(route.methods or []))) for route in monitoring_module.router.routes}

        assert ("/alert-rules", ("GET",)) in route_methods
        assert ("/alert-rules", ("POST",)) in route_methods
        assert ("/alert-rules/{rule_id}", ("PUT",)) in route_methods
        assert ("/alert-rules/{rule_id}", ("DELETE",)) in route_methods
        assert ("/alerts", ("GET",)) in route_methods
        assert ("/alerts/{alert_id}/mark-read", ("POST",)) in route_methods
        assert ("/alerts/mark-all-read", ("POST",)) in route_methods
        assert ("/realtime/{symbol}", ("GET",)) in route_methods
        assert ("/realtime", ("GET",)) in route_methods
        assert ("/realtime/fetch", ("POST",)) in route_methods
        assert ("/dragon-tiger", ("GET",)) in route_methods
        assert ("/dragon-tiger/fetch", ("POST",)) in route_methods
        assert ("/analyze", ("GET",)) in route_methods
        assert ("/summary", ("GET",)) in route_methods
        assert ("/stats/today", ("GET",)) in route_methods
        assert ("/control/start", ("POST",)) in route_methods
        assert ("/control/stop", ("POST",)) in route_methods
        assert ("/control/status", ("GET",)) in route_methods

    @pytest.mark.file_test
    def test_router_contains_expected_number_of_route_method_pairs(self, monitoring_module):
        route_pairs = [(route.path, tuple(sorted(route.methods or []))) for route in monitoring_module.router.routes]

        assert len(route_pairs) == 18
        assert len(route_pairs) == len(set(route_pairs))

    @pytest.mark.file_test
    def test_response_models_remain_stable_for_key_routes(self, monitoring_module):
        response_models = {(route.path, tuple(sorted(route.methods or []))): route.response_model for route in monitoring_module.router.routes}

        assert response_models[("/alert-rules", ("GET",))] == monitoring_module.UnifiedResponse[
            monitoring_module.List[monitoring_module.AlertRuleResponse]
        ]
        assert response_models[("/alerts", ("GET",))] == monitoring_module.UnifiedResponse[
            monitoring_module.AlertRecordsResponse
        ]
        assert response_models[("/realtime/{symbol}", ("GET",))] == monitoring_module.UnifiedResponse[
            monitoring_module.RealtimeMonitoringResponse
        ]
        assert response_models[("/realtime", ("GET",))] == monitoring_module.UnifiedResponse[
            monitoring_module.List[monitoring_module.RealtimeMonitoringResponse]
        ]
        assert response_models[("/dragon-tiger", ("GET",))] == monitoring_module.UnifiedResponse[
            monitoring_module.List[monitoring_module.DragonTigerListResponse]
        ]
        assert response_models[("/summary", ("GET",))] == monitoring_module.UnifiedResponse[
            monitoring_module.MonitoringSummaryResponse
        ]

    @pytest.mark.file_test
    def test_route_names_remain_stable_for_core_operations(self, monitoring_module):
        route_names = {(route.path, tuple(sorted(route.methods or []))): route.name for route in monitoring_module.router.routes}

        assert route_names[("/alert-rules", ("GET",))] == "get_alert_rules"
        assert route_names[("/alerts", ("GET",))] == "get_alert_records"
        assert route_names[("/summary", ("GET",))] == "get_monitoring_summary"
        assert route_names[("/control/status", ("GET",))] == "get_monitoring_status"

    @pytest.mark.file_test
    def test_runtime_fallback_flag_reads_testing_or_development_env(self, monitoring_module, monkeypatch):
        monkeypatch.setenv("TESTING", "false")
        monkeypatch.setenv("DEVELOPMENT_MODE", "false")
        assert monitoring_module._runtime_fallback_enabled() is False

        monkeypatch.setenv("TESTING", "true")
        assert monitoring_module._runtime_fallback_enabled() is True

        monkeypatch.setenv("TESTING", "false")
        monkeypatch.setenv("DEVELOPMENT_MODE", "true")
        assert monitoring_module._runtime_fallback_enabled() is True

    @pytest.mark.file_test
    def test_runtime_fallback_builders_return_consistent_fixture_objects(self, monitoring_module):
        rules = monitoring_module._build_runtime_alert_rules()
        records = monitoring_module._build_runtime_alert_records()

        assert len(rules) == 2
        assert len(records) == 2
        assert rules[0].id == 9001
        assert records[0].rule_id == 9001
        assert rules[1].symbol == "000001"
        assert records[1].alert_level == "warning"

    @pytest.mark.file_test
    def test_resolve_query_int_uses_default_when_query_like_object_is_passed(self, monitoring_module):
        query_like = SimpleNamespace(default=25)

        assert monitoring_module._resolve_query_int(12, 99) == 12
        assert monitoring_module._resolve_query_int(query_like, 99) == 25

    @pytest.mark.file_test
    def test_alert_records_response_model_fields_remain_stable(self, monitoring_module):
        fields = set(monitoring_module.AlertRecordsResponse.model_fields)

        assert fields == {"success", "data", "total", "limit", "offset"}

    @pytest.mark.file_test
    def test_summary_and_analyze_routes_share_same_response_model(self, monitoring_module):
        response_models = {(route.path, tuple(sorted(route.methods or []))): route.response_model for route in monitoring_module.router.routes}
        expected_model = monitoring_module.UnifiedResponse[monitoring_module.MonitoringSummaryResponse]

        assert response_models[("/analyze", ("GET",))] == expected_model
        assert response_models[("/summary", ("GET",))] == expected_model

    @pytest.mark.file_test
    def test_monitoring_summary_route_delegates_to_summary_service(self, monitoring_module, monkeypatch):
        expected = monitoring_module.MonitoringSummaryResponse(
            total_stocks=7,
            limit_up_count=2,
            limit_down_count=1,
            strong_up_count=3,
            strong_down_count=0,
            avg_change_percent=4.25,
            total_amount=123456.78,
            active_alerts=5,
            unread_alerts=2,
        )

        class FakeSummaryService:
            def __init__(self):
                self.calls = 0

            def get_summary(self):
                self.calls += 1
                return expected

        fake_service = FakeSummaryService()
        monkeypatch.setattr(monitoring_module, "_monitoring_summary_service", fake_service, raising=False)

        result = asyncio.run(monitoring_module.get_monitoring_summary(SimpleNamespace()))

        assert result.data.model_dump() == expected.model_dump()
        assert fake_service.calls == 1

    @pytest.mark.file_test
    def test_today_statistics_route_delegates_to_today_statistics_service(self, monitoring_module, monkeypatch):
        class FakeTodayStatisticsService:
            def __init__(self):
                self.calls = 0

            def get_today_statistics(self):
                self.calls += 1
                return {"alerts_summary": [{"alert_type": "limit_up", "count": 2}]}

        fake_service = FakeTodayStatisticsService()
        monkeypatch.setattr(monitoring_module, "_monitoring_today_statistics_service", fake_service, raising=False)

        result = asyncio.run(monitoring_module.get_today_statistics(SimpleNamespace()))

        assert result.data == {"alerts_summary": [{"alert_type": "limit_up", "count": 2}]}
        assert fake_service.calls == 1

    @pytest.mark.file_test
    def test_monitoring_control_routes_delegate_to_control_service(self, monitoring_module, monkeypatch):
        class LegacySafeMonitoringService:
            def __init__(self):
                self.is_monitoring = False
                self.monitored_symbols = []

            async def start_monitoring(self, symbols=None, interval=60):
                self.is_monitoring = True
                self.monitored_symbols = list(symbols or [])
                try:
                    while True:
                        await asyncio.sleep(3600)
                except asyncio.CancelledError:
                    raise

            def stop_monitoring(self):
                self.is_monitoring = False

        class FakeControlService:
            def __init__(self):
                self.calls = []

            async def start(self, *, symbols, interval):
                self.calls.append(("start", symbols, interval))
                return {
                    "is_monitoring": True,
                    "monitored_symbols": list(symbols or []),
                    "monitored_count": len(symbols or []),
                    "interval": interval,
                }

            async def stop(self):
                self.calls.append(("stop",))
                return {
                    "is_monitoring": False,
                    "monitored_symbols": [],
                    "monitored_count": 0,
                }

            def get_status(self):
                self.calls.append(("status",))
                return {
                    "is_monitoring": True,
                    "monitored_symbols": ["600519"],
                    "monitored_count": 1,
                    "update_interval": 15,
                }

        fake_service = FakeControlService()
        monkeypatch.setattr(monitoring_module, "monitoring_service", LegacySafeMonitoringService())
        monkeypatch.setattr(monitoring_module, "_monitoring_control_service", fake_service, raising=False)

        start_response = asyncio.run(
            monitoring_module.start_monitoring(
                monitoring_module.MonitoringControlRequest(symbols=["600519"], interval=15),
                SimpleNamespace(),
            )
        )
        stop_response = asyncio.run(monitoring_module.stop_monitoring(SimpleNamespace()))
        status_response = asyncio.run(monitoring_module.get_monitoring_status())

        assert fake_service.calls == [
            ("start", ["600519"], 15),
            ("stop",),
            ("status",),
        ]
        assert start_response.data["interval"] == 15
        assert stop_response["data"]["is_monitoring"] is False
        assert status_response["data"]["update_interval"] == 15

    @pytest.mark.file_test
    def test_alert_rule_routes_delegate_to_alert_rule_service(self, monitoring_module, monkeypatch):
        class FakeAlertRuleService:
            def __init__(self):
                self.calls = []

            def list_rules(self, *, rule_type, is_active):
                self.calls.append(("list", rule_type, is_active))
                return [{"id": 1, "rule_name": "核心仓位跌破止损线"}]

            def create_rule(self, rule):
                self.calls.append(("create", rule.rule_name))
                return "created-rule"

            def update_rule(self, rule_id, updates):
                self.calls.append(("update", rule_id, updates.description))
                return "updated-rule"

            def delete_rule(self, rule_id):
                self.calls.append(("delete", rule_id))
                return {"success": True, "message": "告警规则已删除"}

        fake_service = FakeAlertRuleService()
        monkeypatch.setattr(monitoring_module, "_monitoring_alert_rule_service", fake_service, raising=False)

        list_response = asyncio.run(
            monitoring_module.get_alert_rules(monitoring_module.AlertRuleType.LIMIT_UP, True, SimpleNamespace())
        )
        created = asyncio.run(
            monitoring_module.create_alert_rule(
                monitoring_module.AlertRuleCreate(
                    rule_name="茅台涨停监控",
                    rule_type=monitoring_module.AlertRuleType.LIMIT_UP,
                ),
                SimpleNamespace(),
            )
        )
        updated = asyncio.run(
            monitoring_module.update_alert_rule(
                42,
                monitoring_module.AlertRuleUpdate(description="更新后的涨停提醒规则"),
                SimpleNamespace(),
            )
        )
        deleted = asyncio.run(monitoring_module.delete_alert_rule(42, SimpleNamespace()))

        assert fake_service.calls == [
            ("list", "limit_up", True),
            ("create", "茅台涨停监控"),
            ("update", 42, "更新后的涨停提醒规则"),
            ("delete", 42),
        ]
        assert list_response.data == [{"id": 1, "rule_name": "核心仓位跌破止损线"}]
        assert created.data == "created-rule"
        assert updated.data == "updated-rule"
        assert deleted.data == {"success": True, "message": "告警规则已删除"}

    @pytest.mark.file_test
    def test_alert_record_routes_delegate_to_alert_record_service(self, monitoring_module, monkeypatch):
        class FakeAlertRecordService:
            def __init__(self):
                self.calls = []

            def list_records(
                self,
                *,
                symbol,
                alert_type,
                alert_level,
                is_read,
                start_date,
                end_date,
                limit,
                offset,
            ):
                self.calls.append(
                    ("list", symbol, alert_type, alert_level, is_read, start_date, end_date, limit, offset)
                )
                return SimpleNamespace(
                    records=[
                        monitoring_module.AlertRecordResponse(
                            id=101,
                            rule_id=10,
                            rule_name="核心仓位风控",
                            symbol="600519",
                            stock_name="贵州茅台",
                            alert_time=datetime(2026, 3, 13, 10, 0, 0),
                            alert_type="price_change",
                            alert_level="warning",
                            alert_title="价格异动",
                            alert_message="触发核心仓位风控提醒",
                            alert_details={},
                            snapshot_data={},
                            is_read=False,
                            is_handled=False,
                            created_at=datetime(2026, 3, 13, 10, 0, 1),
                        )
                    ],
                    total=3,
                    limit=limit,
                    offset=offset,
                )

            def mark_read(self, alert_id):
                self.calls.append(("mark", alert_id))
                return {"success": True, "message": "已标记为已读"}

            def mark_all_read(self):
                self.calls.append(("mark_all",))
                return {"status": "updated", "scope": "all_alerts", "updated_count": 2}

        fake_service = FakeAlertRecordService()
        monkeypatch.setattr(monitoring_module, "_monitoring_alert_record_service", fake_service, raising=False)

        list_response = asyncio.run(
            monitoring_module.get_alert_records(
                "600519",
                "price_change",
                monitoring_module.AlertLevel.WARNING,
                False,
                None,
                None,
                25,
                5,
                SimpleNamespace(),
            )
        )
        marked = asyncio.run(monitoring_module.mark_alert_read(101, SimpleNamespace()))
        marked_all = asyncio.run(monitoring_module.mark_all_alerts_read(SimpleNamespace()))

        assert fake_service.calls == [
            ("list", "600519", "price_change", "warning", False, None, None, 25, 5),
            ("mark", 101),
            ("mark_all",),
        ]
        assert [record.id for record in list_response.data.data] == [101]
        assert list_response.data.total == 3
        assert list_response.data.limit == 25
        assert list_response.data.offset == 5
        assert marked.data == {"success": True, "message": "已标记为已读"}
        assert marked_all.data == {"status": "updated", "scope": "all_alerts", "updated_count": 2}

    @pytest.mark.file_test
    def test_docstrings_cover_alerts_realtime_and_summary_operations(self, monitoring_module):
        assert "获取告警规则列表" in (monitoring_module.get_alert_rules.__doc__ or "")
        assert "获取实时监控数据列表" in (monitoring_module.get_realtime_monitoring_list.__doc__ or "")
        assert "获取监控系统摘要" in (monitoring_module.get_monitoring_summary.__doc__ or "")
