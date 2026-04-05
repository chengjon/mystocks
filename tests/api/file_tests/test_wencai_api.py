"""
File-level route and model contract tests for wencai.py.

这里对齐当前真实的问财查询路由与响应模型，
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
def wencai_module(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("POSTGRESQL_HOST", "localhost")
    monkeypatch.setenv("POSTGRESQL_USER", "postgres")
    monkeypatch.setenv("POSTGRESQL_PASSWORD", "password")
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("BACKEND_PORT", "8020")
    monkeypatch.setenv("BACKEND_BACKUP_PORT", "8021")
    return importlib.import_module("app.api.wencai")


class TestWencaiAPIFile:
    @pytest.mark.file_test
    def test_router_registers_expected_wencai_routes(self, wencai_module):
        route_methods = {(route.path, tuple(sorted(route.methods or []))) for route in wencai_module.router.routes}

        assert wencai_module.router.prefix == "/api/market/wencai"
        assert wencai_module.router.tags == ["wencai"]
        assert ("/api/market/wencai/queries", ("GET",)) in route_methods
        assert ("/api/market/wencai/queries/{query_name}", ("GET",)) in route_methods
        assert ("/api/market/wencai/query", ("POST",)) in route_methods
        assert ("/api/market/wencai/results/{query_name}", ("GET",)) in route_methods
        assert ("/api/market/wencai/refresh/{query_name}", ("POST",)) in route_methods
        assert ("/api/market/wencai/history/{query_name}", ("GET",)) in route_methods
        assert ("/api/market/wencai/custom-query", ("POST",)) in route_methods
        assert ("/api/market/wencai/health", ("GET",)) in route_methods

    @pytest.mark.file_test
    def test_router_contains_expected_number_of_routes(self, wencai_module):
        route_pairs = [(route.path, tuple(sorted(route.methods or []))) for route in wencai_module.router.routes]

        assert len(route_pairs) == 8
        assert len(route_pairs) == len(set(route_pairs))

    @pytest.mark.file_test
    def test_response_models_remain_stable(self, wencai_module):
        response_models = {(route.path, tuple(sorted(route.methods or []))): route.response_model for route in wencai_module.router.routes}

        assert response_models[("/api/market/wencai/queries", ("GET",))] is wencai_module.WencaiQueryListResponse
        assert response_models[("/api/market/wencai/queries/{query_name}", ("GET",))] is wencai_module.WencaiQueryInfo
        assert response_models[("/api/market/wencai/query", ("POST",))] is wencai_module.WencaiQueryResponse
        assert response_models[("/api/market/wencai/results/{query_name}", ("GET",))] is wencai_module.WencaiResultsResponse
        assert response_models[("/api/market/wencai/refresh/{query_name}", ("POST",))] is wencai_module.WencaiRefreshResponse
        assert response_models[("/api/market/wencai/history/{query_name}", ("GET",))] is wencai_module.WencaiHistoryResponse
        assert response_models[("/api/market/wencai/custom-query", ("POST",))] is wencai_module.WencaiCustomQueryResponse
        assert response_models[("/api/market/wencai/health", ("GET",))] is None

    @pytest.mark.file_test
    def test_route_names_remain_stable(self, wencai_module):
        route_names = {(route.path, tuple(sorted(route.methods or []))): route.name for route in wencai_module.router.routes}

        assert route_names[("/api/market/wencai/queries", ("GET",))] == "get_all_queries"
        assert route_names[("/api/market/wencai/query", ("POST",))] == "execute_query"
        assert route_names[("/api/market/wencai/custom-query", ("POST",))] == "execute_custom_query"
        assert route_names[("/api/market/wencai/health", ("GET",))] == "health_check"

    @pytest.mark.file_test
    @pytest.mark.asyncio
    async def test_health_check_returns_expected_static_payload(self, wencai_module):
        payload = await wencai_module.health_check()

        assert payload == {"status": "healthy", "service": "wencai", "version": "1.0.0"}

    @pytest.mark.file_test
    def test_router_exposes_four_get_and_three_post_business_routes_plus_health(self, wencai_module):
        methods = [tuple(sorted(route.methods or [])) for route in wencai_module.router.routes]

        assert methods.count(("GET",)) == 5
        assert methods.count(("POST",)) == 3

    @pytest.mark.file_test
    def test_module_docstring_mentions_restful_stock_screening_api(self, wencai_module):
        doc = wencai_module.__doc__ or ""

        assert "问财API路由" in doc
        assert "RESTful API端点" in doc

    @pytest.mark.file_test
    def test_docstrings_cover_queries_results_and_custom_query(self, wencai_module):
        assert "获取所有查询列表" in (wencai_module.get_all_queries.__doc__ or "")
        assert "获取查询结果" in (wencai_module.get_query_results.__doc__ or "")
        assert "执行自定义查询" in (wencai_module.execute_custom_query.__doc__ or "")

    @pytest.mark.file_test
    def test_background_refresh_task_helper_is_exported_and_callable(self, wencai_module):
        assert callable(wencai_module._refresh_query_task)

    @pytest.mark.file_test
    def test_all_routes_share_same_wencai_namespace(self, wencai_module):
        assert all(route.path.startswith("/api/market/wencai") for route in wencai_module.router.routes)
