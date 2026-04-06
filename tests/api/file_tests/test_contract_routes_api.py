"""
File-level route contract tests for `app.api.contract.routes`.

这份测试只验证当前实际导出的契约管理路由面和响应模型元数据，
不触发数据库访问。
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import List

import pytest


ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = ROOT / "web" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


@pytest.fixture
def contract_module(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("POSTGRESQL_HOST", "localhost")
    monkeypatch.setenv("POSTGRESQL_USER", "postgres")
    monkeypatch.setenv("POSTGRESQL_PASSWORD", "password")
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("BACKEND_PORT", "8020")
    monkeypatch.setenv("BACKEND_BACKUP_PORT", "8021")
    package = importlib.import_module("app.api.contract")
    routes = importlib.import_module("app.api.contract.routes")
    return package, routes


class TestContractRoutesAPIFile:
    @pytest.mark.file_test
    @pytest.mark.contract_test
    def test_router_registers_expected_contract_routes(self, contract_module):
        package, routes = contract_module
        route_methods = {(route.path, tuple(sorted(route.methods or []))) for route in routes.router.routes}

        assert package.router is routes.router
        assert routes.router.prefix == "/api/contracts"
        assert routes.router.tags == ["contract-management"]
        assert ("/api/contracts/versions", ("POST",)) in route_methods
        assert ("/api/contracts/versions", ("GET",)) in route_methods
        assert ("/api/contracts/versions/{version_id}", ("GET",)) in route_methods
        assert ("/api/contracts/versions/{version_id}", ("PUT",)) in route_methods
        assert ("/api/contracts/versions/{version_id}", ("DELETE",)) in route_methods
        assert ("/api/contracts/versions/{name}/active", ("GET",)) in route_methods
        assert ("/api/contracts/versions/{version_id}/activate", ("POST",)) in route_methods
        assert ("/api/contracts/contracts", ("GET",)) in route_methods
        assert ("/api/contracts/diff", ("POST",)) in route_methods
        assert ("/api/contracts/validate", ("POST",)) in route_methods
        assert ("/api/contracts/sync", ("POST",)) in route_methods
        assert ("/api/contracts/sync/report", ("GET",)) in route_methods

    @pytest.mark.file_test
    def test_router_contains_expected_number_of_route_method_pairs(self, contract_module):
        _, routes = contract_module
        route_pairs = [(route.path, tuple(sorted(route.methods or []))) for route in routes.router.routes]

        assert len(route_pairs) == 12
        assert len(route_pairs) == len(set(route_pairs))

    @pytest.mark.file_test
    def test_version_management_routes_keep_response_models(self, contract_module):
        _, routes = contract_module
        create_route = next(route for route in routes.router.routes if route.path == "/api/contracts/versions" and "POST" in route.methods)
        get_route = next(route for route in routes.router.routes if route.path == "/api/contracts/versions/{version_id}" and "GET" in route.methods)
        list_route = next(route for route in routes.router.routes if route.path == "/api/contracts/versions" and "GET" in route.methods)

        assert create_route.response_model is routes.ContractVersionResponse
        assert get_route.response_model is routes.ContractVersionResponse
        assert list_route.response_model == List[routes.ContractVersionResponse]

    @pytest.mark.file_test
    def test_contract_list_diff_and_validate_routes_keep_response_models(self, contract_module):
        _, routes = contract_module
        contracts_route = next(route for route in routes.router.routes if route.path == "/api/contracts/contracts")
        diff_route = next(route for route in routes.router.routes if route.path == "/api/contracts/diff")
        validate_route = next(route for route in routes.router.routes if route.path == "/api/contracts/validate")

        assert contracts_route.response_model is routes.ContractListResponse
        assert diff_route.response_model is routes.ContractDiffResponse
        assert validate_route.response_model is routes.ContractValidateResponse

    @pytest.mark.file_test
    def test_package_exports_router_in___all__(self, contract_module):
        package, routes = contract_module

        assert package.__all__ == ["router"]
        assert package.router is routes.router

    @pytest.mark.file_test
    def test_route_names_remain_stable_for_key_operations(self, contract_module):
        _, routes = contract_module
        route_names = {(route.path, tuple(sorted(route.methods or []))): route.name for route in routes.router.routes}

        assert route_names[("/api/contracts/versions", ("POST",))] == "create_version"
        assert route_names[("/api/contracts/diff", ("POST",))] == "compare_versions"
        assert route_names[("/api/contracts/validate", ("POST",))] == "validate_contract"
        assert route_names[("/api/contracts/sync", ("POST",))] == "sync_contract"

    @pytest.mark.file_test
    def test_docstrings_cover_version_diff_validate_and_sync_operations(self, contract_module):
        _, routes = contract_module

        assert "创建新的契约版本" in (routes.create_version.__doc__ or "")
        assert "对比两个契约版本的差异" in (routes.compare_versions.__doc__ or "")
        assert "验证OpenAPI规范" in (routes.validate_contract.__doc__ or "")
        assert "同步契约" in (routes.sync_contract.__doc__ or "")

    @pytest.mark.file_test
    def test_http_methods_match_route_semantics(self, contract_module):
        _, routes = contract_module
        method_map = {route.path: sorted(route.methods or []) for route in routes.router.routes if route.path in {"/api/contracts/sync/report", "/api/contracts/diff", "/api/contracts/contracts"}}

        assert method_map["/api/contracts/sync/report"] == ["GET"]
        assert method_map["/api/contracts/diff"] == ["POST"]
        assert method_map["/api/contracts/contracts"] == ["GET"]

    @pytest.mark.file_test
    @pytest.mark.contract_test
    def test_route_paths_are_unique_even_when_shared_by_different_methods(self, contract_module):
        _, routes = contract_module
        version_routes = [tuple(sorted(route.methods or [])) for route in routes.router.routes if route.path == "/api/contracts/versions"]
        version_id_routes = [tuple(sorted(route.methods or [])) for route in routes.router.routes if route.path == "/api/contracts/versions/{version_id}"]

        assert sorted(version_routes) == [("GET",), ("POST",)]
        assert sorted(version_id_routes) == [("DELETE",), ("GET",), ("PUT",)]

    @pytest.mark.file_test
    def test_support_functions_and_dependencies_are_callable(self, contract_module):
        _, routes = contract_module

        assert callable(routes.get_db)
        assert callable(routes.VersionManager.create_version)
        assert callable(routes.DiffEngine.compare_versions)
        assert callable(routes.ContractValidator.validate)
