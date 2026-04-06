"""
File-level route contract tests for data/market.py.

这里对齐当前真实的市场概览与热度路由，
替换掉生成式占位断言。
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import Any, Dict

import pytest


ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = ROOT / "web" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


@pytest.fixture
def market_module(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("POSTGRESQL_HOST", "localhost")
    monkeypatch.setenv("POSTGRESQL_USER", "postgres")
    monkeypatch.setenv("POSTGRESQL_PASSWORD", "password")
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("BACKEND_PORT", "8020")
    monkeypatch.setenv("BACKEND_BACKUP_PORT", "8021")
    return importlib.import_module("app.api.data.market")


class TestMarketAPIFile:
    @pytest.mark.file_test
    def test_router_registers_expected_market_routes(self, market_module):
        route_methods = {(route.path, tuple(sorted(route.methods or []))) for route in market_module.router.routes}

        assert ("/markets/overview", ("GET",)) in route_methods
        assert ("/markets/price-distribution", ("GET",)) in route_methods
        assert ("/markets/hot-industries", ("GET",)) in route_methods
        assert ("/markets/hot-concepts", ("GET",)) in route_methods

    @pytest.mark.file_test
    def test_router_contains_expected_number_of_routes(self, market_module):
        route_pairs = [(route.path, tuple(sorted(route.methods or []))) for route in market_module.router.routes]

        assert len(route_pairs) == 4
        assert len(route_pairs) == len(set(route_pairs))

    @pytest.mark.file_test
    def test_all_routes_use_plain_dict_response_model(self, market_module):
        for route in market_module.router.routes:
            assert route.response_model == Dict[str, Any]

    @pytest.mark.file_test
    def test_route_names_remain_stable_for_market_operations(self, market_module):
        route_names = {(route.path, tuple(sorted(route.methods or []))): route.name for route in market_module.router.routes}

        assert route_names[("/markets/overview", ("GET",))] == "get_market_overview"
        assert route_names[("/markets/price-distribution", ("GET",))] == "get_price_distribution"
        assert route_names[("/markets/hot-industries", ("GET",))] == "get_hot_industries"
        assert route_names[("/markets/hot-concepts", ("GET",))] == "get_hot_concepts"

    @pytest.mark.file_test
    def test_market_docstring_mentions_overview_and_heat(self, market_module):
        doc = market_module.__doc__ or ""

        assert "市场概览" in doc
        assert "热度" in doc

    @pytest.mark.file_test
    def test_route_docstrings_cover_overview_distribution_industries_and_concepts(self, market_module):
        assert "获取市场概览数据" in (market_module.get_market_overview.__doc__ or "")
        assert "获取全市场涨跌分布统计" in (market_module.get_price_distribution.__doc__ or "")
        assert "获取热门行业表现数据" in (market_module.get_hot_industries.__doc__ or "")
        assert "获取热门概念表现数据" in (market_module.get_hot_concepts.__doc__ or "")

    @pytest.mark.file_test
    def test_all_routes_are_get_only(self, market_module):
        for route in market_module.router.routes:
            assert tuple(sorted(route.methods or [])) == ("GET",)

    @pytest.mark.file_test
    @pytest.mark.contract_test
    def test_contract_fixture_still_covers_market_data_domain(self, contract_specs):
        spec = contract_specs["market-data"]

        assert spec["_meta"]["source_type"] == "historical_snapshot"
        assert spec["_meta"]["is_contract_truth"] is False
        assert "/api/market/overview" in spec["paths"]
        assert "/api/market/fund-flow" in spec["paths"]

    @pytest.mark.file_test
    def test_market_routes_share_single_namespace(self, market_module):
        assert all(route.path.startswith("/markets/") for route in market_module.router.routes)

    @pytest.mark.file_test
    def test_market_module_exports_db_service_and_business_exception_dependencies(self, market_module):
        assert market_module.db_service is not None
        assert market_module.BusinessException is not None
