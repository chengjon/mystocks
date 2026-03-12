from __future__ import annotations

import importlib
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _set_required_database_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for key, value in {
        "TDENGINE_HOST": "localhost",
        "TDENGINE_PORT": "6030",
        "TDENGINE_USER": "root",
        "TDENGINE_PASSWORD": "taosdata",
        "TDENGINE_DATABASE": "market_data",
        "POSTGRESQL_HOST": "localhost",
        "POSTGRESQL_PORT": "5438",
        "POSTGRESQL_USER": "postgres",
        "POSTGRESQL_PASSWORD": "password",
        "POSTGRESQL_DATABASE": "mystocks",
    }.items():
        monkeypatch.setenv(key, value)


def test_postgresql_default_port_falls_back_to_5432(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_required_database_env(monkeypatch)

    from src.storage.database.connection_manager import DatabaseConnectionManager

    manager = DatabaseConnectionManager()
    monkeypatch.delenv("POSTGRESQL_PORT", raising=False)

    with patch("psycopg2.pool.SimpleConnectionPool") as mock_pool:
        manager.get_postgresql_connection()

    assert mock_pool.call_args.kwargs["port"] == 5432


@pytest.mark.parametrize(
    "module_name",
    [
        "src.data_access_pkg.postgresql_access",
        "src.data_access_pkg.tdengine_access",
    ],
)
def test_data_access_pkg_modules_import_cleanly(module_name: str) -> None:
    for loaded_name in list(sys.modules):
        if loaded_name.startswith("src.data_access_pkg"):
            sys.modules.pop(loaded_name, None)

    module = importlib.import_module(module_name)

    assert module is not None
