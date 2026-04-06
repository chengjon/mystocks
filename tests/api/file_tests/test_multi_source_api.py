"""
File-level contract tests for the active multi_source API package.

仓库里同时存在包路由和遗留单文件定义，运行时实际导出的是
`app.api.multi_source.routes`。这里对齐当前生效的接口面。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import importlib


ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = ROOT / "web" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


@pytest.fixture
def multi_source_module(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("POSTGRESQL_HOST", "localhost")
    monkeypatch.setenv("POSTGRESQL_USER", "postgres")
    monkeypatch.setenv("POSTGRESQL_PASSWORD", "password")
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("BACKEND_PORT", "8020")
    monkeypatch.setenv("BACKEND_BACKUP_PORT", "8021")
    package = importlib.import_module("app.api.multi_source")
    routes = importlib.import_module("app.api.multi_source.routes")
    return package, routes


class TestMultiSourceAPIFile:
    @pytest.mark.file_test
    def test_router_registers_expected_paths(self, multi_source_module):
        package, routes = multi_source_module
        paths = {(route.path, tuple(sorted(route.methods or []))) for route in routes.router.routes}

        assert package.router is routes.router
        assert routes.router.prefix == ""
        assert ("/health", ("GET",)) in paths
        assert ("/status", ("GET",)) in paths
        assert ("/analyze", ("POST",)) in paths

    @pytest.mark.file_test
    @pytest.mark.asyncio
    async def test_health_check_returns_service_status(self, multi_source_module):
        _, routes = multi_source_module

        payload = await routes.health_check()

        assert payload == {"status": "ok", "service": "multi_source"}

    @pytest.mark.file_test
    @pytest.mark.asyncio
    async def test_status_endpoint_returns_active_service_marker(self, multi_source_module):
        _, routes = multi_source_module

        payload = await routes.get_status()

        assert payload == {"status": "active", "endpoint": "multi_source"}

    @pytest.mark.file_test
    @pytest.mark.asyncio
    async def test_analyze_endpoint_returns_placeholder_result_for_minimal_payload(self, multi_source_module):
        _, routes = multi_source_module

        payload = await routes.analyze_data({"symbol": "600519"})

        assert payload == {"result": "分析完成", "endpoint": "multi_source"}

    @pytest.mark.file_test
    @pytest.mark.asyncio
    async def test_analyze_endpoint_accepts_extended_request_shape(self, multi_source_module):
        _, routes = multi_source_module

        payload = await routes.analyze_data(
            {
                "symbol": "600519",
                "data_sources": ["technical", "fundamental", "sentiment"],
                "analysis_depth": "advanced",
                "weights": {"technical": 0.3, "fundamental": 0.5, "sentiment": 0.2},
                "time_range": "3m",
            }
        )

        assert payload["endpoint"] == "multi_source"
        assert payload["result"] == "分析完成"

    @pytest.mark.file_test
    def test_router_contains_unique_paths_only(self, multi_source_module):
        _, routes = multi_source_module
        route_paths = [route.path for route in routes.router.routes]

        assert route_paths == ["/health", "/status", "/analyze"]
        assert len(route_paths) == len(set(route_paths))

    @pytest.mark.file_test
    def test_router_methods_match_expected_contract(self, multi_source_module):
        _, routes = multi_source_module
        route_methods = {route.path: tuple(sorted(route.methods or [])) for route in routes.router.routes}

        assert route_methods["/health"] == ("GET",)
        assert route_methods["/status"] == ("GET",)
        assert route_methods["/analyze"] == ("POST",)

    @pytest.mark.file_test
    def test_package_exports_router_in___all__(self, multi_source_module):
        package, routes = multi_source_module

        assert package.__all__ == ["router"]
        assert package.router is routes.router

    @pytest.mark.file_test
    def test_analyze_endpoint_docstring_mentions_ai_analysis(self, multi_source_module):
        _, routes = multi_source_module

        assert "AI综合分析" in (routes.analyze_data.__doc__ or "")
        assert "多数据源" in (routes.analyze_data.__doc__ or "")

    @pytest.mark.file_test
    def test_health_and_status_handlers_have_stable_names(self, multi_source_module):
        _, routes = multi_source_module

        assert routes.health_check.__name__ == "health_check"
        assert routes.get_status.__name__ == "get_status"
