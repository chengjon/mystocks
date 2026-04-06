"""
File-level route contract tests for auth.py.

这里验证当前生效的鉴权路由面和关键元数据，
避免把文件级测试退化成只检查 fixture 的占位脚手架。
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import Any, Dict, get_origin

import pytest
from fastapi.security import HTTPBearer


ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = ROOT / "web" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


@pytest.fixture
def auth_module(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("POSTGRESQL_HOST", "localhost")
    monkeypatch.setenv("POSTGRESQL_USER", "postgres")
    monkeypatch.setenv("POSTGRESQL_PASSWORD", "password")
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("BACKEND_PORT", "8020")
    monkeypatch.setenv("BACKEND_BACKUP_PORT", "8021")
    return importlib.import_module("app.api.auth")


class TestAuthAPIFile:
    @pytest.mark.file_test
    @pytest.mark.contract_test
    def test_router_registers_expected_auth_routes(self, auth_module):
        route_methods = {(route.path, tuple(sorted(route.methods or []))) for route in auth_module.router.routes}

        assert ("/login", ("POST",)) in route_methods
        assert ("/logout", ("POST",)) in route_methods
        assert ("/me", ("GET",)) in route_methods
        assert ("/refresh", ("POST",)) in route_methods
        assert ("/users", ("GET",)) in route_methods
        assert ("/csrf/token", ("GET",)) in route_methods
        assert ("/register", ("POST",)) in route_methods
        assert ("/reset-password/request", ("POST",)) in route_methods
        assert ("/reset-password/confirm", ("POST",)) in route_methods

    @pytest.mark.file_test
    def test_register_route_keeps_created_status_code(self, auth_module):
        register_route = next(route for route in auth_module.router.routes if route.path == "/register")

        assert register_route.status_code == 201

    @pytest.mark.file_test
    def test_me_route_uses_user_response_model(self, auth_module):
        me_route = next(route for route in auth_module.router.routes if route.path == "/me")

        assert me_route.response_model is auth_module.User

    @pytest.mark.file_test
    def test_logout_refresh_and_users_routes_return_mapping_types(self, auth_module):
        logout_route = next(route for route in auth_module.router.routes if route.path == "/logout")
        refresh_route = next(route for route in auth_module.router.routes if route.path == "/refresh")
        users_route = next(route for route in auth_module.router.routes if route.path == "/users")

        assert get_origin(logout_route.response_model) is dict
        assert logout_route.response_model == Dict[str, Any]
        assert refresh_route.response_model == Dict[str, Any]
        assert users_route.response_model == Dict[str, Any]

    @pytest.mark.file_test
    def test_security_dependency_uses_http_bearer(self, auth_module):
        assert isinstance(auth_module.security, HTTPBearer)

    @pytest.mark.file_test
    def test_login_docstring_mentions_rate_limit_and_token_response(self, auth_module):
        doc = auth_module.login_for_access_token.__doc__ or ""

        assert "速率限制" in doc
        assert "访问令牌" in doc

    @pytest.mark.file_test
    def test_csrf_token_endpoint_docstring_mentions_csrf_contract(self, auth_module):
        doc = auth_module.get_csrf_token.__doc__ or ""

        assert "CSRF" in doc
        assert "token" in doc.lower()

    @pytest.mark.file_test
    def test_password_reset_endpoints_expose_stable_function_names(self, auth_module):
        reset_request_route = next(route for route in auth_module.router.routes if route.path == "/reset-password/request")
        reset_confirm_route = next(route for route in auth_module.router.routes if route.path == "/reset-password/confirm")

        assert reset_request_route.endpoint.__name__ == "request_password_reset"
        assert reset_confirm_route.endpoint.__name__ == "confirm_password_reset"

    @pytest.mark.file_test
    @pytest.mark.contract_test
    def test_route_paths_are_unique(self, auth_module):
        paths = [route.path for route in auth_module.router.routes]

        assert len(paths) == len(set(paths))
        assert len(paths) == 9

    @pytest.mark.file_test
    def test_auth_support_functions_are_callable(self, auth_module):
        assert callable(auth_module.get_current_user)
        assert callable(auth_module.get_current_active_user)
        assert callable(auth_module.check_permission)
