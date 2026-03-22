from __future__ import annotations

import os
import json
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def test_backend_pm2_config_includes_project_root_in_pythonpath() -> None:
    env = os.environ.copy()
    env.update(
        {
            "BACKEND_PORT": "8888",
            "BACKEND_BACKUP_PORT": "8889",
        }
    )

    completed = subprocess.run(
        [
            "node",
            "-e",
            """
const config = require('./web/backend/ecosystem.config.js');
const backend = config.apps.find((app) => app.name === 'mystocks-backend');
process.stdout.write(JSON.stringify(backend.env));
""",
        ],
        capture_output=True,
        text=True,
        check=False,
        cwd=PROJECT_ROOT,
        env=env,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    backend_env = json.loads(completed.stdout)
    pythonpath_entries = backend_env["PYTHONPATH"].split(":")

    assert str(PROJECT_ROOT) in pythonpath_entries
    assert str(PROJECT_ROOT / "web" / "backend") in pythonpath_entries


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


def test_app_main_imports_when_akshare_is_unavailable() -> None:
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
    if name == "akshare" or name.startswith("akshare."):
        raise ModuleNotFoundError("No module named 'akshare'")
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


def test_app_main_imports_when_joblib_is_unavailable() -> None:
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
    if name == "joblib" or name.startswith("joblib."):
        raise ModuleNotFoundError("No module named 'joblib'")
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


def test_akshare_extension_returns_empty_results_when_akshare_is_unavailable() -> None:
    env = os.environ.copy()
    env.update(
        {
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
    if name == "akshare" or name.startswith("akshare."):
        raise ModuleNotFoundError("No module named 'akshare'")
    return _real_import(name, globals, locals, fromlist, level)

builtins.__import__ = _guarded_import

from app.adapters.akshare_extension import get_akshare_extension

extension = get_akshare_extension()
assert extension.get_etf_spot().empty
assert extension.get_stock_fund_flow("600519.SH") == {}
assert extension.get_stock_lhb_detail("2025-03-21").empty
assert extension.get_dividend_data("600519.SH").empty
assert extension.get_sector_fund_flow().empty
""",
        ],
        capture_output=True,
        text=True,
        check=False,
        cwd=PROJECT_ROOT,
        env=env,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr


def test_app_main_imports_when_taos_runtime_is_unavailable() -> None:
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
    if name == "taos" or name.startswith("taos."):
        raise ModuleNotFoundError("No module named 'taos'")
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
