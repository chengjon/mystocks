import app.core.security as security_module


def test_authenticate_user_by_id_uses_mock_user_in_testing_mode(monkeypatch):
    monkeypatch.setattr(security_module.settings, "testing", True, raising=False)
    monkeypatch.setattr(security_module.settings, "mock_auth_enabled", True, raising=False)
    monkeypatch.setattr(
        security_module,
        "get_user_from_database_by_id",
        lambda _user_id: (_ for _ in ()).throw(RuntimeError("db unavailable")),
    )

    user = security_module.authenticate_user_by_id(1)

    assert user is not None
    assert user.username == "admin"
    assert user.id == 1
