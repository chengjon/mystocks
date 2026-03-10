from __future__ import annotations

import importlib
import importlib.util
import logging
import sys
from pathlib import Path
from types import ModuleType

import pytest


def install_app_namespace(monkeypatch):
    app_root = Path("web/backend/app").resolve()
    core_root = app_root / "core"

    fake_app = ModuleType("app")
    fake_core = ModuleType("app.core")
    fake_app.__path__ = [str(app_root)]
    fake_core.__path__ = [str(core_root)]
    fake_app.core = fake_core

    monkeypatch.setitem(sys.modules, "app", fake_app)
    monkeypatch.setitem(sys.modules, "app.core", fake_core)


def load_auth_module():
    api_root = Path("web/backend/app/api").resolve()
    app_root = Path("web/backend/app").resolve()
    module_name = "app.api.auth"
    module_paths = {
        "app.api.auth_compat": api_root / "auth_compat.py",
        "app.api.auth_schemas": api_root / "auth_schemas.py",
    }

    fake_app = ModuleType("app")
    fake_api = ModuleType("app.api")
    fake_app.__path__ = [str(app_root)]
    fake_api.__path__ = [str(api_root)]
    fake_app.api = fake_api

    previous = {
        "app": sys.modules.get("app"),
        "app.api": sys.modules.get("app.api"),
        module_name: sys.modules.get(module_name),
    }

    for dotted_name in module_paths:
        previous[dotted_name] = sys.modules.get(dotted_name)

    sys.modules["app"] = fake_app
    sys.modules["app.api"] = fake_api

    for dotted_name, module_path in module_paths.items():
        spec = importlib.util.spec_from_file_location(dotted_name, module_path)
        module = importlib.util.module_from_spec(spec)
        assert spec is not None and spec.loader is not None
        sys.modules[dotted_name] = module
        spec.loader.exec_module(module)

    spec = importlib.util.spec_from_file_location(module_name, api_root / "auth.py")
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    for name, previous_module in previous.items():
        if previous_module is None:
            sys.modules.pop(name, None)
        else:
            sys.modules[name] = previous_module

    return module


def test_auth_source_contains_no_print_statements():
    source = Path("web/backend/app/api/auth.py").read_text(encoding="utf-8")

    assert "print(" not in source


@pytest.mark.asyncio
async def test_request_password_reset_logs_database_errors(monkeypatch, caplog):
    module = load_auth_module()
    install_app_namespace(monkeypatch)
    database_module = importlib.import_module("app.core.database")
    exceptions_module = importlib.import_module("src.core.exceptions")

    class DummyDatabaseConnectionError(Exception):
        pass

    def raise_db_error():
        raise DummyDatabaseConnectionError("db temporarily unavailable")

    monkeypatch.setattr(exceptions_module, "DatabaseConnectionError", DummyDatabaseConnectionError)
    monkeypatch.setattr(database_module, "get_postgresql_session", raise_db_error)

    with caplog.at_level(logging.ERROR, logger=module.__name__):
        response = await module.request_password_reset(module.PasswordResetRequest(email="user@example.com"))

    assert response.success is True
    assert any("Database error during password reset request" in record.getMessage() for record in caplog.records)
    assert any(record.exc_info is not None for record in caplog.records)


@pytest.mark.asyncio
async def test_request_password_reset_logs_unexpected_errors(monkeypatch, caplog):
    module = load_auth_module()
    install_app_namespace(monkeypatch)
    database_module = importlib.import_module("app.core.database")

    def raise_unexpected_error():
        raise RuntimeError("boom")

    monkeypatch.setattr(database_module, "get_postgresql_session", raise_unexpected_error)

    with caplog.at_level(logging.ERROR, logger=module.__name__):
        response = await module.request_password_reset(module.PasswordResetRequest(email="user@example.com"))

    assert response.success is True
    assert any("Unexpected error during password reset request" in record.getMessage() for record in caplog.records)
    assert any(record.exc_info is not None for record in caplog.records)
