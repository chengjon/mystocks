from types import SimpleNamespace

import pytest

from app.api import auth as auth_module


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
