"""
File-level route and helper contract tests for data_source_config.py.

这里对齐当前真实的 CRUD、版本历史、回滚和热重载路由，
替换掉生成式占位断言。
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest


ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = ROOT / "web" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


@pytest.fixture
def data_source_config_module(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("POSTGRESQL_HOST", "localhost")
    monkeypatch.setenv("POSTGRESQL_USER", "postgres")
    monkeypatch.setenv("POSTGRESQL_PASSWORD", "password")
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("BACKEND_PORT", "8020")
    monkeypatch.setenv("BACKEND_BACKUP_PORT", "8021")
    return importlib.import_module("app.api.data_source_config")


class TestDataSourceConfigAPIFile:
    @pytest.mark.file_test
    def test_router_registers_expected_config_routes(self, data_source_config_module):
        route_methods = {(route.path, tuple(sorted(route.methods or []))) for route in data_source_config_module.router.routes}

        assert data_source_config_module.router.prefix == "/api/v1/data-sources/config"
        assert data_source_config_module.router.tags == ["数据源配置管理"]
        assert ("/api/v1/data-sources/config/", ("POST",)) in route_methods
        assert ("/api/v1/data-sources/config/", ("GET",)) in route_methods
        assert ("/api/v1/data-sources/config/{endpoint_name}", ("PUT",)) in route_methods
        assert ("/api/v1/data-sources/config/{endpoint_name}", ("DELETE",)) in route_methods
        assert ("/api/v1/data-sources/config/{endpoint_name}", ("GET",)) in route_methods
        assert ("/api/v1/data-sources/config/batch", ("POST",)) in route_methods
        assert ("/api/v1/data-sources/config/{endpoint_name}/versions", ("GET",)) in route_methods
        assert ("/api/v1/data-sources/config/{endpoint_name}/rollback/{version}", ("POST",)) in route_methods
        assert ("/api/v1/data-sources/config/reload", ("POST",)) in route_methods

    @pytest.mark.file_test
    def test_router_contains_expected_number_of_route_method_pairs(self, data_source_config_module):
        route_pairs = [(route.path, tuple(sorted(route.methods or []))) for route in data_source_config_module.router.routes]

        assert len(route_pairs) == 9
        assert len(route_pairs) == len(set(route_pairs))

    @pytest.mark.file_test
    def test_all_routes_use_unified_response_model(self, data_source_config_module):
        for route in data_source_config_module.router.routes:
            assert route.response_model is data_source_config_module.UnifiedResponse

    @pytest.mark.file_test
    def test_create_route_keeps_created_status_code(self, data_source_config_module):
        create_route = next(route for route in data_source_config_module.router.routes if route.path == "/api/v1/data-sources/config/" and "POST" in route.methods)

        assert create_route.status_code == 201

    @pytest.mark.file_test
    def test_route_names_remain_stable_for_core_operations(self, data_source_config_module):
        route_names = {(route.path, tuple(sorted(route.methods or []))): route.name for route in data_source_config_module.router.routes}

        assert route_names[("/api/v1/data-sources/config/", ("POST",))] == "create_data_source"
        assert route_names[("/api/v1/data-sources/config/{endpoint_name}", ("PUT",))] == "update_data_source"
        assert route_names[("/api/v1/data-sources/config/batch", ("POST",))] == "batch_operations"
        assert route_names[("/api/v1/data-sources/config/reload", ("POST",))] == "reload_config"

    @pytest.mark.file_test
    def test_get_current_user_returns_system_in_testing_mode(self, data_source_config_module, monkeypatch):
        monkeypatch.setattr(data_source_config_module.settings, "testing", True)

        assert data_source_config_module.get_current_user() == "system"

    @pytest.mark.file_test
    def test_get_current_user_rejects_missing_authorization_outside_testing(self, data_source_config_module, monkeypatch):
        monkeypatch.setattr(data_source_config_module.settings, "testing", False)

        with pytest.raises(data_source_config_module.HTTPException) as excinfo:
            data_source_config_module.get_current_user(None)

        assert excinfo.value.status_code == 401

    @pytest.mark.file_test
    def test_handle_config_error_maps_duplicate_and_not_found(self, data_source_config_module):
        duplicate = data_source_config_module.handle_config_error("endpoint already exists", "req-1")
        not_found = data_source_config_module.handle_config_error("record not found", "req-2")
        generic = data_source_config_module.handle_config_error("boom", "req-3")

        assert duplicate.code == data_source_config_module.BusinessCode.CONFLICT
        assert duplicate.message == "数据源配置已存在"
        assert not_found.code == data_source_config_module.BusinessCode.NOT_FOUND
        assert not_found.message == "数据源配置不存在"
        assert generic.code == data_source_config_module.BusinessCode.INTERNAL_ERROR
        assert generic.message == "boom"

    @pytest.mark.file_test
    def test_module_docstring_mentions_crud_versioning_and_hot_reload(self, data_source_config_module):
        doc = data_source_config_module.__doc__ or ""

        assert "CRUD" in doc
        assert "版本管理" in doc
        assert "热重载" in doc

    @pytest.mark.file_test
    def test_router_response_descriptions_include_success_and_conflict(self, data_source_config_module):
        responses = data_source_config_module.router.responses

        assert responses[200]["description"] == "成功"
        assert responses[201]["description"] == "创建成功"
        assert responses[409]["description"] == "资源冲突"
