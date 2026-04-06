"""
File-level route and helper contract tests for monitoring.py.

这里校验当前 18 个监控路由、fallback helper 和核心响应模型，
不触发真实数据库查询。
"""

from __future__ import annotations

import importlib
import sys
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
        assert response_models[("/alerts", ("GET",))] is monitoring_module.AlertRecordsResponse
        assert response_models[("/realtime/{symbol}", ("GET",))] is monitoring_module.RealtimeMonitoringResponse
        assert response_models[("/realtime", ("GET",))] == monitoring_module.List[
            monitoring_module.RealtimeMonitoringResponse
        ]
        assert response_models[("/dragon-tiger", ("GET",))] == monitoring_module.List[
            monitoring_module.DragonTigerListResponse
        ]
        assert response_models[("/summary", ("GET",))] is monitoring_module.MonitoringSummaryResponse

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

        assert response_models[("/analyze", ("GET",))] is monitoring_module.MonitoringSummaryResponse
        assert response_models[("/summary", ("GET",))] is monitoring_module.MonitoringSummaryResponse

    @pytest.mark.file_test
    def test_docstrings_cover_alerts_realtime_and_summary_operations(self, monitoring_module):
        assert "获取告警规则列表" in (monitoring_module.get_alert_rules.__doc__ or "")
        assert "获取实时监控数据列表" in (monitoring_module.get_realtime_monitoring_list.__doc__ or "")
        assert "获取监控系统摘要" in (monitoring_module.get_monitoring_summary.__doc__ or "")
