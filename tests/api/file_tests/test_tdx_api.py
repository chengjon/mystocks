"""
File-level route contract tests for tdx.py.

这里对齐当前实际暴露的 TDX 路由和响应模型，
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
def tdx_module(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("POSTGRESQL_HOST", "localhost")
    monkeypatch.setenv("POSTGRESQL_USER", "postgres")
    monkeypatch.setenv("POSTGRESQL_PASSWORD", "password")
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("BACKEND_PORT", "8020")
    monkeypatch.setenv("BACKEND_BACKUP_PORT", "8021")
    return importlib.import_module("app.api.tdx")


class TestTdxAPIFile:
    @pytest.mark.file_test
    def test_router_registers_expected_tdx_routes(self, tdx_module):
        route_methods = {(route.path, tuple(sorted(route.methods or []))) for route in tdx_module.router.routes}

        assert ("/quote/{symbol}", ("GET",)) in route_methods
        assert ("/kline", ("GET",)) in route_methods
        assert ("/index/quote/{symbol}", ("GET",)) in route_methods
        assert ("/index/kline", ("GET",)) in route_methods
        assert ("/health", ("GET",)) in route_methods

    @pytest.mark.file_test
    def test_router_contains_expected_number_of_routes(self, tdx_module):
        route_pairs = [(route.path, tuple(sorted(route.methods or []))) for route in tdx_module.router.routes]

        assert len(route_pairs) == 5
        assert len(route_pairs) == len(set(route_pairs))

    @pytest.mark.file_test
    def test_response_models_remain_stable(self, tdx_module):
        response_models = {(route.path, tuple(sorted(route.methods or []))): route.response_model for route in tdx_module.router.routes}

        assert response_models[("/quote/{symbol}", ("GET",))] is tdx_module.RealTimeQuoteResponse
        assert response_models[("/kline", ("GET",))] is tdx_module.KlineResponse
        assert response_models[("/index/quote/{symbol}", ("GET",))] is tdx_module.IndexQuoteResponse
        assert response_models[("/index/kline", ("GET",))] is tdx_module.KlineResponse
        assert response_models[("/health", ("GET",))] is tdx_module.TdxHealthResponse

    @pytest.mark.file_test
    def test_route_names_remain_stable_for_core_operations(self, tdx_module):
        route_names = {(route.path, tuple(sorted(route.methods or []))): route.name for route in tdx_module.router.routes}

        assert route_names[("/quote/{symbol}", ("GET",))] == "get_stock_quote"
        assert route_names[("/kline", ("GET",))] == "get_stock_kline"
        assert route_names[("/index/quote/{symbol}", ("GET",))] == "get_index_quote"
        assert route_names[("/index/kline", ("GET",))] == "get_index_kline"
        assert route_names[("/health", ("GET",))] == "health_check"

    @pytest.mark.file_test
    def test_all_routes_are_get_only(self, tdx_module):
        for route in tdx_module.router.routes:
            assert tuple(sorted(route.methods or [])) == ("GET",)

    @pytest.mark.file_test
    def test_stock_and_index_docstrings_remain_descriptive(self, tdx_module):
        assert "获取股票实时行情" in (tdx_module.get_stock_quote.__doc__ or "")
        assert "获取股票K线数据" in (tdx_module.get_stock_kline.__doc__ or "")
        assert "获取指数实时行情" in (tdx_module.get_index_quote.__doc__ or "")
        assert "获取指数K线数据" in (tdx_module.get_index_kline.__doc__ or "")

    @pytest.mark.file_test
    def test_health_route_summary_and_description_are_present(self, tdx_module):
        health_route = next(route for route in tdx_module.router.routes if route.path == "/health")

        assert health_route.summary == "TDX服务健康检查"
        assert "检查TDX服务器连接状态" in (health_route.description or "")

    @pytest.mark.file_test
    def test_kline_route_description_mentions_supported_periods(self, tdx_module):
        kline_route = next(route for route in tdx_module.router.routes if route.path == "/kline")
        index_kline_route = next(route for route in tdx_module.router.routes if route.path == "/index/kline")

        assert "1m/5m/15m/30m/1h/1d" in (kline_route.description or "")
        assert "多种周期" in (index_kline_route.description or "")

    @pytest.mark.file_test
    def test_quote_routes_require_symbol_path_parameter(self, tdx_module):
        quote_paths = {route.path for route in tdx_module.router.routes if "quote" in route.path}

        assert "/quote/{symbol}" in quote_paths
        assert "/index/quote/{symbol}" in quote_paths

    @pytest.mark.file_test
    def test_module_docstring_describes_five_supported_endpoints(self, tdx_module):
        doc = tdx_module.__doc__ or ""

        assert "GET /api/tdx/quote/{symbol}" in doc
        assert "GET /api/tdx/kline" in doc
        assert "GET /api/tdx/index/quote/{symbol}" in doc
        assert "GET /api/tdx/index/kline" in doc
        assert "GET /api/tdx/health" in doc
