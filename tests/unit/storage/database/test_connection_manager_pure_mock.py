"""
DatabaseConnectionManager 纯 Mock 测试

这份测试不依赖真实数据库驱动或连接，只验证控制流与错误处理。
"""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from src.storage.database import connection_manager as cm


DEFAULT_ENV = {
    "TDENGINE_HOST": "localhost",
    "TDENGINE_PORT": "6030",
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


def test_import_surface_exposes_manager_and_factory() -> None:
    assert callable(cm.DatabaseConnectionManager)
    assert callable(cm.get_connection_manager)


def test_manager_initialization_creates_empty_connection_cache(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_env(monkeypatch)

    manager = cm.DatabaseConnectionManager()

    assert manager._connections == {}


def test_manager_initialization_fails_when_required_env_is_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_env(monkeypatch, TDENGINE_PASSWORD=None)

    with pytest.raises(EnvironmentError, match="缺少必需的环境变量"):
        cm.DatabaseConnectionManager()


def test_get_tdengine_connection_raises_import_error_when_driver_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_env(monkeypatch)
    monkeypatch.setattr(cm, "taosws", None)
    manager = cm.DatabaseConnectionManager()

    with pytest.raises(ImportError, match="TDengine驱动未安装"):
        manager.get_tdengine_connection()


def test_get_postgresql_connection_raises_import_error_when_driver_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_env(monkeypatch)
    monkeypatch.setattr(cm, "pool", None)
    manager = cm.DatabaseConnectionManager()

    with pytest.raises(ImportError, match="PostgreSQL驱动未安装"):
        manager.get_postgresql_connection()


def test_return_postgresql_connection_puts_connection_back_when_pool_is_cached(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    patch_env(monkeypatch)
    manager = cm.DatabaseConnectionManager()
    pg_pool = Mock()
    pg_conn = Mock()
    manager._connections["postgresql"] = pg_pool

    manager._return_postgresql_connection(pg_conn)

    pg_pool.putconn.assert_called_once_with(pg_conn)


def test_return_postgresql_connection_is_noop_without_cached_pool(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_env(monkeypatch)
    manager = cm.DatabaseConnectionManager()

    manager._return_postgresql_connection(Mock())

    assert manager._connections == {}


def test_close_all_connections_swallows_close_errors_and_clears_cache(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_env(monkeypatch)
    manager = cm.DatabaseConnectionManager()
    failing_tdengine = Mock()
    failing_tdengine.close.side_effect = RuntimeError("close failed")
    postgresql_pool = Mock()
    redis_conn = Mock()
    redis_pool = Mock()
    manager._connections = {
        "tdengine": failing_tdengine,
        "postgresql": postgresql_pool,
        "redis": (redis_conn, redis_pool),
    }

    manager.close_all_connections()

    postgresql_pool.closeall.assert_called_once_with()
    redis_conn.close.assert_called_once_with()
    redis_pool.disconnect.assert_called_once_with()
    assert manager._connections == {}


def test_test_all_connections_reports_failures_without_raising(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_env(monkeypatch)
    manager = cm.DatabaseConnectionManager()
    pg_pool = Mock()
    pg_pool.getconn.side_effect = RuntimeError("pg down")
    monkeypatch.setattr(manager, "get_tdengine_connection", Mock(side_effect=RuntimeError("td down")))
    monkeypatch.setattr(manager, "get_postgresql_connection", Mock(return_value=pg_pool))

    results = manager.test_all_connections()

    assert results == {"tdengine": False, "postgresql": False}


def test_get_connection_manager_returns_singleton_instance(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_env(monkeypatch)
    fake_manager = Mock()
    manager_class = Mock(return_value=fake_manager)
    monkeypatch.setattr(cm, "DatabaseConnectionManager", manager_class)

    first = cm.get_connection_manager()
    second = cm.get_connection_manager()

    assert first is fake_manager
    assert second is fake_manager
    manager_class.assert_called_once_with()


def test_get_redis_connection_raises_import_error_when_driver_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_env(monkeypatch)
    monkeypatch.setattr(cm, "redis", None)
    manager = cm.DatabaseConnectionManager()

    with pytest.raises(ImportError, match="Redis驱动未安装"):
        manager.get_redis_connection()


def test_get_redis_connection_builds_connection_pool_from_runtime_config(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_env(monkeypatch)
    redis_pool = Mock()
    redis_client = Mock()
    redis_client.ping.return_value = True
    redis_module = SimpleNamespace(
        ConnectionPool=Mock(return_value=redis_pool),
        Redis=Mock(return_value=redis_client),
    )
    config_loader = Mock(return_value={"host": "redis.local", "port": 6380, "db": 1})
    monkeypatch.setattr(cm, "redis", redis_module)
    monkeypatch.setattr(cm, "get_redis_connection_kwargs", config_loader)
    manager = cm.DatabaseConnectionManager()

    assert manager.get_redis_connection() is redis_client
    assert manager.get_redis_connection() is redis_client
    config_loader.assert_called_once_with("app_cache", decode_responses=True)
    redis_module.ConnectionPool.assert_called_once()
    redis_module.Redis.assert_called_once_with(connection_pool=redis_pool)
