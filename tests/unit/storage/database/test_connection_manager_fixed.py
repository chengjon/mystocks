"""
DatabaseConnectionManager 模块契约测试

这份测试关注模块级导入、副作用初始化和较细的边界语义。
前两份 connection_manager 测试覆盖核心行为，这里补足剩余分支。
"""

from __future__ import annotations

import importlib
from types import SimpleNamespace
from unittest.mock import Mock

import dotenv
import pytest

from src.storage.database import connection_manager as cm


DEFAULT_ENV = {
    "TDENGINE_HOST": "localhost",
    "TDENGINE_PORT": "6030",
    "TDENGINE_REST_PORT": None,
    "TDENGINE_USER": "root",
    "TDENGINE_PASSWORD": "td-secret",
    "TDENGINE_DATABASE": "market_data",
    "POSTGRESQL_HOST": "localhost",
    "POSTGRESQL_PORT": "5432",
    "POSTGRESQL_USER": "postgres",
    "POSTGRESQL_PASSWORD": "pg-secret",
    "POSTGRESQL_DATABASE": "mystocks",
}


def patch_env(monkeypatch: pytest.MonkeyPatch, **overrides: str | None) -> dict[str, str | None]:
    values = {**DEFAULT_ENV, **overrides}
    monkeypatch.setattr(cm.os, "getenv", lambda key, default=None: values.get(key, default))
    return values


@pytest.fixture(autouse=True)
def reset_singleton(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cm, "_connection_manager", None)


def test_module_structure_exposes_expected_methods() -> None:
    expected_methods = {
        "__init__",
        "_validate_env_variables",
        "get_tdengine_connection",
        "get_postgresql_connection",
        "_return_postgresql_connection",
        "get_redis_connection",
        "close_all_connections",
        "test_all_connections",
    }

    assert callable(cm.DatabaseConnectionManager)
    assert callable(cm.get_connection_manager)
    assert expected_methods.issubset(set(dir(cm.DatabaseConnectionManager)))


def test_validate_env_variables_reports_partial_missing_set(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_env(
        monkeypatch,
        TDENGINE_USER=None,
        TDENGINE_PASSWORD=None,
        POSTGRESQL_DATABASE=None,
    )

    with pytest.raises(EnvironmentError) as excinfo:
        cm.DatabaseConnectionManager()

    message = str(excinfo.value)
    assert "TDENGINE_USER" in message
    assert "TDENGINE_PASSWORD" in message
    assert "POSTGRESQL_DATABASE" in message


def test_connections_dict_accepts_runtime_entries_after_init(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_env(monkeypatch)
    manager = cm.DatabaseConnectionManager()
    marker = Mock()

    manager._connections["custom"] = marker

    assert manager._connections == {"custom": marker}


def test_close_all_connections_supports_plain_redis_client(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_env(monkeypatch)
    manager = cm.DatabaseConnectionManager()
    redis_client = Mock()
    manager._connections = {"redis": redis_client}

    manager.close_all_connections()

    redis_client.close.assert_called_once_with()
    assert manager._connections == {}


def test_close_all_connections_continues_after_tdengine_close_error(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_env(monkeypatch)
    manager = cm.DatabaseConnectionManager()
    broken_tdengine = Mock()
    broken_tdengine.close.side_effect = RuntimeError("close failed")
    postgresql_pool = Mock()
    manager._connections = {"tdengine": broken_tdengine, "postgresql": postgresql_pool}

    manager.close_all_connections()

    postgresql_pool.closeall.assert_called_once_with()
    assert manager._connections == {}


def test_return_postgresql_connection_does_not_raise_without_pool(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_env(monkeypatch)
    manager = cm.DatabaseConnectionManager()

    manager._return_postgresql_connection(Mock())

    assert manager._connections == {}


def test_get_connection_manager_creates_new_singleton_after_manual_reset(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_env(monkeypatch)
    first_manager = Mock()
    second_manager = Mock()
    manager_class = Mock(side_effect=[first_manager, second_manager])
    monkeypatch.setattr(cm, "DatabaseConnectionManager", manager_class)

    one = cm.get_connection_manager()
    cm._connection_manager = None
    two = cm.get_connection_manager()

    assert one is first_manager
    assert two is second_manager
    assert manager_class.call_count == 2


def test_module_reload_invokes_load_dotenv(monkeypatch: pytest.MonkeyPatch) -> None:
    load_dotenv = Mock()
    monkeypatch.setattr(dotenv, "load_dotenv", load_dotenv)

    reloaded = importlib.reload(cm)

    try:
        load_dotenv.assert_called_once_with()
        assert reloaded is cm
    finally:
        importlib.reload(cm)


def test_get_tdengine_connection_falls_back_to_tdengine_port(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_env(monkeypatch, TDENGINE_REST_PORT=None, TDENGINE_PORT="6035")
    connect = Mock(return_value=Mock())
    monkeypatch.setattr(cm, "taosws", SimpleNamespace(connect=connect))
    manager = cm.DatabaseConnectionManager()

    manager.get_tdengine_connection()

    assert connect.call_args.kwargs["port"] == 6035


def test_get_postgresql_connection_wraps_pool_factory_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_env(monkeypatch, POSTGRESQL_HOST="db.internal", POSTGRESQL_PORT="5439")
    pool_factory = Mock(side_effect=RuntimeError("factory failed"))
    monkeypatch.setattr(cm, "pool", SimpleNamespace(SimpleConnectionPool=pool_factory))
    manager = cm.DatabaseConnectionManager()

    with pytest.raises(ConnectionError) as excinfo:
        manager.get_postgresql_connection()

    message = str(excinfo.value)
    assert "PostgreSQL连接失败" in message
    assert "db.internal:5439" in message
