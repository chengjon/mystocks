"""
File-level route aggregation tests for the active data API facade.

这里验证 `app.api.data` 是否正确聚合 7 个领域子路由，
替换掉原先与真实实现脱节的生成式占位断言。
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
def data_module(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("POSTGRESQL_HOST", "localhost")
    monkeypatch.setenv("POSTGRESQL_USER", "postgres")
    monkeypatch.setenv("POSTGRESQL_PASSWORD", "password")
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("BACKEND_PORT", "8020")
    monkeypatch.setenv("BACKEND_BACKUP_PORT", "8021")
    return importlib.import_module("app.api.data")


class TestDataAPIFile:
    @pytest.mark.file_test
    def test_router_exposes_data_service_tag_and_no_prefix(self, data_module):
        assert data_module.router.tags == ["Data Service"]
        assert data_module.router.prefix == ""

    @pytest.mark.file_test
    def test_router_aggregates_all_subrouter_paths(self, data_module):
        route_paths = {route.path for route in data_module.router.routes}

        assert "/stocks/basic" in route_paths
        assert "/stocks/industries" in route_paths
        assert "/stocks/concepts" in route_paths
        assert "/stocks/search" in route_paths
        assert "/stocks/{symbol}/detail" in route_paths
        assert "/markets/overview" in route_paths
        assert "/markets/price-distribution" in route_paths
        assert "/markets/hot-industries" in route_paths
        assert "/markets/hot-concepts" in route_paths
        assert "/stocks/daily" in route_paths
        assert "/kline" in route_paths
        assert "/stocks/kline" in route_paths
        assert "/stocks/intraday" in route_paths
        assert "/margin/account-info" in route_paths
        assert "/margin/detail/sse" in route_paths
        assert "/margin/detail/szse" in route_paths
        assert "/dragon-tiger/detail" in route_paths
        assert "/dragon-tiger/institution-stats" in route_paths
        assert "/futures/index/daily" in route_paths
        assert "/futures/index/realtime" in route_paths
        assert "/financial" in route_paths

    @pytest.mark.file_test
    def test_router_contains_expected_number_of_routes(self, data_module):
        assert len(data_module.router.routes) == 21

    @pytest.mark.file_test
    def test_all_aggregated_routes_are_get_only(self, data_module):
        for route in data_module.router.routes:
            assert tuple(sorted(route.methods or [])) == ("GET",)

    @pytest.mark.file_test
    def test_route_path_and_method_pairs_are_unique(self, data_module):
        route_pairs = [(route.path, tuple(sorted(route.methods or []))) for route in data_module.router.routes]

        assert len(route_pairs) == len(set(route_pairs))

    @pytest.mark.file_test
    def test_router_includes_all_imported_subrouters(self, data_module):
        subrouters = [
            data_module.stocks_router,
            data_module.market_router,
            data_module.kline_router,
            data_module.margin_router,
            data_module.lhb_router,
            data_module.futures_router,
            data_module.financial_router,
        ]

        assert sum(len(router.routes) for router in subrouters) == len(data_module.router.routes)

    @pytest.mark.file_test
    def test_representative_route_names_remain_stable(self, data_module):
        route_names = {route.path: route.name for route in data_module.router.routes}

        assert route_names["/stocks/basic"] == "get_stocks_basic"
        assert route_names["/markets/overview"] == "get_market_overview"
        assert route_names["/kline"] == "get_kline"
        assert route_names["/financial"] == "get_financial_data"

    @pytest.mark.file_test
    def test_package_exports_router_in___all__(self, data_module):
        assert data_module.__all__ == ["router"]

    @pytest.mark.file_test
    def test_router_does_not_expose_generated_placeholder_endpoints(self, data_module):
        route_paths = {route.path for route in data_module.router.routes}

        assert "/api/data/bulk" not in route_paths
        assert "/api/data/validate" not in route_paths
        assert "/api/data/export" not in route_paths

    @pytest.mark.file_test
    def test_futures_and_margin_domains_are_both_present(self, data_module):
        route_paths = {route.path for route in data_module.router.routes}

        assert any(path.startswith("/futures/") for path in route_paths)
        assert any(path.startswith("/margin/") for path in route_paths)
