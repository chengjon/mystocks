import inspect
from types import SimpleNamespace

import pytest

from app.api import auth as auth_module
from app.api import auth_compat as auth_compat_module
from app.core.security import oauth2_scheme


class _FakeRateLimiter:
    def get_client_ip(self, request):
        return "127.0.0.1"

    def record_failed_auth(self, client_ip):
        raise AssertionError("successful login should not record failed auth")

    def reset_failed_auth(self, client_ip):
        self.reset_client_ip = client_ip


@pytest.mark.asyncio
async def test_login_response_includes_numeric_user_id(monkeypatch):
    rate_limiter = _FakeRateLimiter()
    fake_user = SimpleNamespace(id=7, username="contractuser", email="contract@example.com", role="admin")

    monkeypatch.setattr(auth_module, "get_rate_limiter", lambda: rate_limiter)
    monkeypatch.setattr(auth_module, "authenticate_user", lambda username, password: fake_user)
    monkeypatch.setattr(auth_module, "create_access_token", lambda data, expires_delta: "jwt-token")
    monkeypatch.setattr(auth_module.settings, "access_token_expire_minutes", 120)

    response = await auth_module.login_for_access_token(
        request=SimpleNamespace(),
        form_data=SimpleNamespace(username="contractuser", password="secret"),
    )

    assert response.data["user"]["id"] == 7
    assert isinstance(response.data["user"]["id"], int)


@pytest.mark.asyncio
async def test_compat_login_response_includes_numeric_user_id(monkeypatch):
    fake_user = SimpleNamespace(id=9, username="compatuser", email="compat@example.com", role="user")

    monkeypatch.setattr(auth_compat_module, "authenticate_user", lambda username, password: fake_user)
    monkeypatch.setattr(auth_compat_module, "create_access_token", lambda data, expires_delta: "compat-jwt-token")
    monkeypatch.setattr(auth_compat_module.settings, "access_token_expire_minutes", 120)

    response = await auth_compat_module.compat_login(username="compatuser", password="secret")

    assert response.data["user"]["id"] == 9
    assert isinstance(response.data["user"]["id"], int)


def test_oauth2_password_flow_uses_canonical_v1_login_path():
    assert oauth2_scheme.model.flows.password.tokenUrl == "/api/v1/auth/login"


def test_auth_db_handlers_use_route_local_session_factory_dependency():
    expected_provider = auth_module.get_auth_postgresql_session_factory

    for handler_name in (
        "get_users",
        "register_user",
        "request_password_reset",
        "confirm_password_reset",
    ):
        signature = inspect.signature(getattr(auth_module, handler_name))
        session_factory = signature.parameters["session_factory"]

        assert session_factory.default.dependency is expected_provider
