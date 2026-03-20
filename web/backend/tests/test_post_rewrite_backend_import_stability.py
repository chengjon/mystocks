from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def test_app_main_imports_on_origin_main_recovery_path() -> None:
    env = os.environ.copy()
    env.update(
        {
            "POSTGRESQL_HOST": "localhost",
            "POSTGRESQL_PORT": "5432",
            "POSTGRESQL_USER": "tester",
            "POSTGRESQL_PASSWORD": "tester",
            "POSTGRESQL_DATABASE": "tester",
            "JWT_SECRET_KEY": "test-secret-key",
            "BACKEND_PORT": "8134",
            "BACKEND_BACKUP_PORT": "8135",
            "TESTING": "true",
            "PYTHONPATH": ".:web/backend",
        }
    )

    completed = subprocess.run(
        [sys.executable, "-c", "import app.main"],
        capture_output=True,
        text=True,
        check=False,
        cwd=PROJECT_ROOT,
        env=env,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr


def test_tdx_adapter_import_avoids_legacy_loguru_chain() -> None:
    env = os.environ.copy()
    env["PYTHONPATH"] = ".:web/backend"

    completed = subprocess.run(
        [
            sys.executable,
            "-c",
            """
import builtins

_real_import = builtins.__import__

def _guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
    if name == "loguru" or name.startswith("loguru."):
        raise ModuleNotFoundError("No module named 'loguru'")
    return _real_import(name, globals, locals, fromlist, level)

builtins.__import__ = _guarded_import
from src.adapters.tdx.tdx_adapter import TdxDataSource
assert TdxDataSource.__name__ == "TdxDataSource"
""",
        ],
        capture_output=True,
        text=True,
        check=False,
        cwd=PROJECT_ROOT,
        env=env,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr


def test_app_main_imports_when_loguru_is_unavailable() -> None:
    env = os.environ.copy()
    env.update(
        {
            "POSTGRESQL_HOST": "localhost",
            "POSTGRESQL_PORT": "5438",
            "POSTGRESQL_USER": "postgres",
            "POSTGRESQL_PASSWORD": "password",
            "POSTGRESQL_DATABASE": "mystocks",
            "JWT_SECRET_KEY": "test-secret-key",
            "BACKEND_PORT": "8000",
            "BACKEND_BACKUP_PORT": "8001",
            "TESTING": "true",
            "PYTHONPATH": ".:web/backend",
        }
    )

    completed = subprocess.run(
        [
            sys.executable,
            "-c",
            """
import builtins

_real_import = builtins.__import__

def _guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
    if name == "loguru" or name.startswith("loguru."):
        raise ModuleNotFoundError("No module named 'loguru'")
    return _real_import(name, globals, locals, fromlist, level)

builtins.__import__ = _guarded_import
import app.main
""",
        ],
        capture_output=True,
        text=True,
        check=False,
        cwd=PROJECT_ROOT,
        env=env,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr


def test_app_main_imports_when_talib_is_unavailable() -> None:
    env = os.environ.copy()
    env.update(
        {
            "POSTGRESQL_HOST": "localhost",
            "POSTGRESQL_PORT": "5438",
            "POSTGRESQL_USER": "postgres",
            "POSTGRESQL_PASSWORD": "password",
            "POSTGRESQL_DATABASE": "mystocks",
            "JWT_SECRET_KEY": "test-secret-key",
            "BACKEND_PORT": "8000",
            "BACKEND_BACKUP_PORT": "8001",
            "TESTING": "true",
            "PYTHONPATH": ".:web/backend",
        }
    )

    completed = subprocess.run(
        [
            sys.executable,
            "-c",
            """
import builtins

_real_import = builtins.__import__

def _guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
    if name == "talib" or name.startswith("talib."):
        raise ModuleNotFoundError("No module named 'talib'")
    return _real_import(name, globals, locals, fromlist, level)

builtins.__import__ = _guarded_import
import app.main
""",
        ],
        capture_output=True,
        text=True,
        check=False,
        cwd=PROJECT_ROOT,
        env=env,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
