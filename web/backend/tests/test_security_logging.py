from __future__ import annotations

import importlib
import logging
from pathlib import Path


def test_security_source_contains_no_print_statements():
    module = importlib.import_module("app.core.security")
    source = Path(module.__file__).read_text(encoding="utf-8")

    assert "print(" not in source


def test_authenticate_user_logs_test_mode(monkeypatch, caplog):
    module = importlib.import_module("app.core.security")
    monkeypatch.setattr(module.settings, "testing", True, raising=False)
    monkeypatch.setattr(module, "_authenticate_with_mock", lambda username, _password: {"username": username})

    with caplog.at_level(logging.INFO, logger=module.__name__):
        result = module.authenticate_user("tester", "secret")

    assert result == {"username": "tester"}
    assert any("[Test Mode] Using mock authentication" in record.getMessage() for record in caplog.records)


def test_get_user_from_database_logs_errors(monkeypatch, caplog):
    module = importlib.import_module("app.core.security")
    database_module = importlib.import_module("app.core.database")

    def raise_error():
        raise RuntimeError("db down")

    monkeypatch.setattr(database_module, "get_postgresql_session", raise_error)

    with caplog.at_level(logging.ERROR, logger=module.__name__):
        try:
            module.get_user_from_database("tester")
        except RuntimeError as exc:
            result = str(exc)
        else:
            result = None

    assert result == "db down"


def test_authenticate_user_logs_db_failure_without_mock_fallback(monkeypatch, caplog):
    module = importlib.import_module("app.core.security")
    monkeypatch.setattr(module.settings, "testing", False, raising=False)
    monkeypatch.setattr(module, "get_user_from_database", lambda _username: (_ for _ in ()).throw(RuntimeError("db down")))
    mock_called = False

    def fake_mock_auth(_username, _password):
        nonlocal mock_called
        mock_called = True
        return {"username": "mock-user"}

    monkeypatch.setattr(module, "_authenticate_with_mock", fake_mock_auth)

    with caplog.at_level(logging.WARNING, logger=module.__name__):
        result = module.authenticate_user("tester", "secret")

    assert result is None
    assert mock_called is False
    assert any("without mock fallback" in record.getMessage() for record in caplog.records)


def test_mock_auth_disabled_logs_warning(monkeypatch, caplog):
    module = importlib.import_module("app.core.security")
    monkeypatch.setattr(module.settings, "mock_auth_enabled", False, raising=False)

    with caplog.at_level(logging.WARNING, logger=module.__name__):
        result = module._authenticate_with_mock("admin", "admin123")

    assert result is None
    assert any("Mock authentication attempt blocked" in record.getMessage() for record in caplog.records)


def test_mock_auth_requires_configured_credentials(monkeypatch, caplog):
    module = importlib.import_module("app.core.security")
    monkeypatch.setattr(module.settings, "mock_auth_enabled", True, raising=False)
    monkeypatch.setattr(module.settings, "mock_auth_admin_password", "", raising=False)
    monkeypatch.setattr(module.settings, "mock_auth_user_password", "", raising=False)
    monkeypatch.setattr(module.settings, "admin_initial_password", "", raising=False)

    with caplog.at_level(logging.WARNING, logger=module.__name__):
        result = module._authenticate_with_mock("admin", "admin123")

    assert result is None
    assert any("missing mock credentials configuration" in record.getMessage() for record in caplog.records)
