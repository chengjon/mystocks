"""
File-level route and export contract tests for strategy_management package.

这里对齐 `app.api.strategy_management` 当前真实导出面，
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
def strategy_module(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("POSTGRESQL_HOST", "localhost")
    monkeypatch.setenv("POSTGRESQL_USER", "postgres")
    monkeypatch.setenv("POSTGRESQL_PASSWORD", "password")
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("BACKEND_PORT", "8020")
    monkeypatch.setenv("BACKEND_BACKUP_PORT", "8021")
    return importlib.import_module("app.api.strategy_management")


class TestStrategyManagementAPIFile:
    @pytest.mark.file_test
    @pytest.mark.contract_test
    def test_router_registers_expected_strategy_routes(self, strategy_module):
        route_methods = {(route.path, tuple(sorted(route.methods or []))) for route in strategy_module.router.routes}

        assert strategy_module.router.prefix == "/api/v1/strategy"
        assert ("/api/v1/strategy/strategies", ("GET",)) in route_methods
        assert ("/api/v1/strategy/strategies", ("POST",)) in route_methods
        assert ("/api/v1/strategy/strategies/{strategy_id}", ("GET",)) in route_methods
        assert ("/api/v1/strategy/strategies/{strategy_id}", ("PUT",)) in route_methods
        assert ("/api/v1/strategy/strategies/{strategy_id}", ("DELETE",)) in route_methods
        assert ("/api/v1/strategy/{strategy_id}/start", ("POST",)) in route_methods
        assert ("/api/v1/strategy/{strategy_id}/pause", ("POST",)) in route_methods
        assert ("/api/v1/strategy/{strategy_id}/resume", ("POST",)) in route_methods
        assert ("/api/v1/strategy/{strategy_id}/stop", ("POST",)) in route_methods
        assert ("/api/v1/strategy/models/train", ("POST",)) in route_methods
        assert ("/api/v1/strategy/models/training/{task_id}/status", ("GET",)) in route_methods
        assert ("/api/v1/strategy/models", ("GET",)) in route_methods
        assert ("/api/v1/strategy/backtest/run", ("POST",)) in route_methods
        assert ("/api/v1/strategy/backtest/results", ("GET",)) in route_methods
        assert ("/api/v1/strategy/backtest/results/{backtest_id}", ("GET",)) in route_methods
        assert ("/api/v1/strategy/backtest/status/{backtest_id}", ("GET",)) in route_methods

    @pytest.mark.file_test
    def test_router_contains_expected_number_of_route_method_pairs(self, strategy_module):
        route_pairs = [(route.path, tuple(sorted(route.methods or []))) for route in strategy_module.router.routes]

        assert len(route_pairs) == 16
        assert len(route_pairs) == len(set(route_pairs))

    @pytest.mark.file_test
    def test_package_exports_key_functions_and_router(self, strategy_module):
        assert "router" in strategy_module.__all__
        assert "get_backtest_result" in strategy_module.__all__
        assert callable(strategy_module.list_strategies)
        assert callable(strategy_module.create_strategy)
        assert callable(strategy_module.train_model)
        assert callable(strategy_module.get_backtest_result)
        assert callable(strategy_module.router)

    @pytest.mark.file_test
    def test_route_names_remain_stable_for_core_operations(self, strategy_module):
        route_names = {(route.path, tuple(sorted(route.methods or []))): route.name for route in strategy_module.router.routes}

        assert route_names[("/api/v1/strategy/strategies", ("GET",))] == "list_strategies"
        assert route_names[("/api/v1/strategy/models/train", ("POST",))] == "train_model"
        assert route_names[("/api/v1/strategy/backtest/run", ("POST",))] == "run_backtest"
        assert route_names[("/api/v1/strategy/backtest/results/{backtest_id}", ("GET",))] == "get_backtest_result"

    @pytest.mark.file_test
    def test_chart_data_function_is_exported_but_not_wired_into_package_router(self, strategy_module):
        route_paths = {route.path for route in strategy_module.router.routes}

        assert callable(strategy_module.get_backtest_chart_data)
        assert "/api/v1/strategy/backtest/results/{backtest_id}/chart-data" not in route_paths

    @pytest.mark.file_test
    @pytest.mark.contract_test
    def test_contract_fixture_still_matches_strategy_management_surface(self, contract_specs):
        spec = contract_specs["strategy-management"]

        assert spec["_meta"]["source_type"] == "historical_snapshot"
        assert spec["_meta"]["is_contract_truth"] is False
        assert "/api/strategies" in spec["paths"]
        assert "/api/models/train" in spec["paths"]

    @pytest.mark.file_test
    def test_strategy_router_prefix_is_shared_by_all_paths(self, strategy_module):
        assert all(route.path.startswith("/api/v1/strategy") for route in strategy_module.router.routes)

    @pytest.mark.file_test
    def test_strategy_package_docstring_and_exports_indicate_split_package(self, strategy_module):
        assert "拆分包" in (strategy_module.__doc__ or "")
        assert "router" in strategy_module.__all__

    @pytest.mark.file_test
    def test_backtest_related_routes_cover_run_status_and_results(self, strategy_module):
        backtest_paths = {route.path for route in strategy_module.router.routes if "/backtest/" in route.path}

        assert "/api/v1/strategy/backtest/run" in backtest_paths
        assert "/api/v1/strategy/backtest/results" in backtest_paths
        assert "/api/v1/strategy/backtest/results/{backtest_id}" in backtest_paths
        assert "/api/v1/strategy/backtest/status/{backtest_id}" in backtest_paths

    @pytest.mark.file_test
    def test_model_routes_cover_train_status_and_listing(self, strategy_module):
        model_paths = {route.path for route in strategy_module.router.routes if "/models" in route.path}

        assert "/api/v1/strategy/models/train" in model_paths
        assert "/api/v1/strategy/models/training/{task_id}/status" in model_paths
        assert "/api/v1/strategy/models" in model_paths
