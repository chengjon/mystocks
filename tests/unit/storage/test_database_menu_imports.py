import builtins
import subprocess
from types import SimpleNamespace

import pytest

import src.storage.database.test_database_menu as database_menu_module


def test_check_database_drivers_uses_importlib_and_never_exec(monkeypatch: pytest.MonkeyPatch) -> None:
    imported_modules = []

    def fake_import_module(module_name: str) -> object:
        imported_modules.append(module_name)
        if module_name in {"psycopg2", "redis", "sqlalchemy", "taosws"}:
            return object()
        raise ImportError(module_name)

    def fail_exec(*args, **kwargs):  # type: ignore[no-untyped-def]
        raise AssertionError(f"exec should not be used: {args!r}")

    def fake_pip_show(*args, **kwargs):  # type: ignore[no-untyped-def]
        return SimpleNamespace(returncode=1, stdout="")

    monkeypatch.setattr(database_menu_module.importlib, "import_module", fake_import_module)
    monkeypatch.setattr(builtins, "exec", fail_exec)
    monkeypatch.setattr(subprocess, "run", fake_pip_show)

    tool = database_menu_module.DatabaseTestTool()

    result = tool.check_database_drivers()

    assert result is True
    assert tool.db_libs["psycopg2"] is True
    assert tool.db_libs["redis"] is True
    assert tool.db_libs["sqlalchemy"] is True
    assert tool.db_libs["tdengine"] == ["WebSocket(taos-ws-py)"]
    assert imported_modules == ["psycopg2", "redis", "taosws", "taosrest", "taos", "sqlalchemy"]


def test_check_tdengine_drivers_handles_import_failures_without_raising(monkeypatch: pytest.MonkeyPatch) -> None:
    imported_modules = []

    def fake_import_module(module_name: str) -> object:
        imported_modules.append(module_name)
        if module_name == "taosws":
            raise RuntimeError("native client load failed")
        raise ImportError(module_name)

    def fail_exec(*args, **kwargs):  # type: ignore[no-untyped-def]
        raise AssertionError(f"exec should not be used: {args!r}")

    def fake_pip_show(*args, **kwargs):  # type: ignore[no-untyped-def]
        return SimpleNamespace(returncode=1, stdout="")

    monkeypatch.setattr(database_menu_module.importlib, "import_module", fake_import_module)
    monkeypatch.setattr(builtins, "exec", fail_exec)
    monkeypatch.setattr(subprocess, "run", fake_pip_show)

    tool = database_menu_module.DatabaseTestTool()

    assert tool._check_tdengine_drivers() == []
    assert imported_modules == ["taosws", "taosrest", "taos"]
