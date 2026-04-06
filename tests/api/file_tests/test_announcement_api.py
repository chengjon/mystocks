"""
File-level route contract tests for the active announcement API package.

这里对齐 `app.api.announcement.routes` 当前真实导出的路由集合，
替换掉生成式占位断言。
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = ROOT / "web" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


@pytest.fixture
def announcement_module(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("POSTGRESQL_HOST", "localhost")
    monkeypatch.setenv("POSTGRESQL_USER", "postgres")
    monkeypatch.setenv("POSTGRESQL_PASSWORD", "password")
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("BACKEND_PORT", "8020")
    monkeypatch.setenv("BACKEND_BACKUP_PORT", "8021")
    package = importlib.import_module("app.api.announcement")
    routes = importlib.import_module("app.api.announcement.routes")
    return package, routes


class TestAnnouncementAPIFile:
    @pytest.mark.file_test
    @pytest.mark.contract_test
    def test_router_registers_base_announcement_routes(self, announcement_module):
        package, routes = announcement_module
        route_methods = {(route.path, tuple(sorted(route.methods or []))) for route in routes.router.routes}

        assert package.router is routes.router
        assert routes.router.prefix == "/announcement"
        assert ("/announcement/health", ("GET",)) in route_methods
        assert ("/announcement/status", ("GET",)) in route_methods
        assert ("/announcement/analyze", ("POST",)) in route_methods

    @pytest.mark.file_test
    def test_router_registers_service_routes_when_service_is_available(self, announcement_module):
        _, routes = announcement_module
        route_methods = {(route.path, tuple(sorted(route.methods or []))) for route in routes.router.routes}

        if routes.HAS_ANNOUNCEMENT_SERVICE:
            assert ("/announcement/fetch", ("POST",)) in route_methods
            assert ("/announcement/list", ("GET",)) in route_methods
            assert ("/announcement/today", ("GET",)) in route_methods
            assert ("/announcement/important", ("GET",)) in route_methods
            assert ("/announcement/stats", ("GET",)) in route_methods
            assert ("/announcement/monitor-rules", ("GET",)) in route_methods
            assert ("/announcement/monitor-rules", ("POST",)) in route_methods
            assert ("/announcement/monitor-rules/{rule_id}", ("PUT",)) in route_methods
            assert ("/announcement/monitor-rules/{rule_id}", ("DELETE",)) in route_methods
            assert ("/announcement/triggered-records", ("GET",)) in route_methods
            assert ("/announcement/monitor/evaluate", ("POST",)) in route_methods
        else:
            assert len(route_methods) == 3

    @pytest.mark.file_test
    @pytest.mark.asyncio
    async def test_health_check_returns_service_status(self, announcement_module):
        _, routes = announcement_module

        payload = await routes.health_check()

        assert payload == {"status": "ok", "service": "announcement"}

    @pytest.mark.file_test
    @pytest.mark.asyncio
    async def test_status_endpoint_returns_active_service_marker(self, announcement_module):
        _, routes = announcement_module

        payload = await routes.get_status()

        assert payload == {"status": "active", "endpoint": "announcement"}

    @pytest.mark.file_test
    @pytest.mark.asyncio
    async def test_analyze_endpoint_returns_placeholder_result_for_minimal_payload(self, announcement_module):
        _, routes = announcement_module

        payload = await routes.analyze_data({"symbol": "600519"})

        assert payload == {"result": "分析完成", "endpoint": "announcement"}

    @pytest.mark.file_test
    @pytest.mark.asyncio
    async def test_analyze_endpoint_accepts_extended_request_shape(self, announcement_module):
        _, routes = announcement_module

        payload = await routes.analyze_data(
            {
                "symbol": "600519",
                "keywords": ["回购", "增持"],
                "categories": ["important", "finance"],
                "analysis_depth": "advanced",
            }
        )

        assert payload["endpoint"] == "announcement"
        assert payload["result"] == "分析完成"

    @pytest.mark.file_test
    def test_package_exports_router_in___all__(self, announcement_module):
        package, routes = announcement_module

        assert package.__all__ == ["router"]
        assert package.router is routes.router

    @pytest.mark.file_test
    def test_analyze_docstring_mentions_ai_analysis(self, announcement_module):
        _, routes = announcement_module

        assert "AI分析" in (routes.analyze_data.__doc__ or "")

    @pytest.mark.file_test
    def test_health_and_status_handlers_have_stable_names(self, announcement_module):
        _, routes = announcement_module

        assert routes.health_check.__name__ == "health_check"
        assert routes.get_status.__name__ == "get_status"

    @pytest.mark.file_test
    def test_monitor_rules_path_exposes_two_methods_when_service_enabled(self, announcement_module):
        _, routes = announcement_module
        methods = [tuple(sorted(route.methods or [])) for route in routes.router.routes if route.path == "/announcement/monitor-rules"]

        if routes.HAS_ANNOUNCEMENT_SERVICE:
            assert sorted(methods) == [("GET",), ("POST",)]
        else:
            assert methods == []

    @pytest.mark.file_test
    def test_route_paths_remain_unique_per_path_method_pair(self, announcement_module):
        _, routes = announcement_module
        route_methods = [(route.path, tuple(sorted(route.methods or []))) for route in routes.router.routes]

        assert len(route_methods) == len(set(route_methods))
