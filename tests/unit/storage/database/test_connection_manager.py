"""
DatabaseConnectionManager 公共契约测试

这份测试替换自动生成的占位断言，专注于公共行为契约。
更细粒度的 mock 组合测试留给同目录下的 *_fixed.py 和 *_pure_mock.py。
"""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from src.storage.database import connection_manager as cm


DEFAULT_ENV = {
    "TDENGINE_HOST": "tdengine.local",
    "TDENGINE_PORT": "6030",
    "TDENGINE_REST_PORT": None,
    "TDENGINE_USER": "root",
    "TDENGINE_PASSWORD": "td-secret",
    "TDENGINE_DATABASE": "market_data",
    "POSTGRESQL_HOST": "postgres.local",
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
def reset_connection_manager_singleton(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cm, "_connection_manager", None)


def test_initialization_raises_when_required_env_vars_are_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_env(monkeypatch, TDENGINE_HOST=None, POSTGRESQL_PASSWORD=None)

    with pytest.raises(EnvironmentError) as excinfo:
        cm.DatabaseConnectionManager()

    message = str(excinfo.value)
    assert "TDENGINE_HOST" in message
    assert "POSTGRESQL_PASSWORD" in message
    assert "MySQL已从US3架构中移除" in message


def test_get_tdengine_connection_prefers_rest_port_and_caches_connection(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_env(monkeypatch, TDENGINE_REST_PORT="6041")
    mock_connection = Mock()
    connect = Mock(return_value=mock_connection)
    monkeypatch.setattr(cm, "taosws", SimpleNamespace(connect=connect))

    manager = cm.DatabaseConnectionManager()

    assert manager.get_tdengine_connection() is mock_connection
    assert manager.get_tdengine_connection() is mock_connection
    connect.assert_called_once_with(
        host="tdengine.local",
        port=6041,
        user="root",
        password="td-secret",
        database="market_data",
    )


def test_get_postgresql_connection_builds_pool_once_with_expected_settings(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    patch_env(monkeypatch, POSTGRESQL_PORT="5544")
    mock_pool = Mock()
    pool_factory = Mock(return_value=mock_pool)
    monkeypatch.setattr(cm, "pool", SimpleNamespace(SimpleConnectionPool=pool_factory))

    manager = cm.DatabaseConnectionManager()

    assert manager.get_postgresql_connection() is mock_pool
    assert manager.get_postgresql_connection() is mock_pool
    pool_factory.assert_called_once_with(
        minconn=1,
        maxconn=20,
        host="postgres.local",
        port=5544,
        user="postgres",
        password="pg-secret",
        database="mystocks",
        connect_timeout=10,
    )


def test_get_redis_connection_uses_runtime_config_and_caches_client(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_env(monkeypatch)
    mock_pool = Mock()
    mock_client = Mock()
    mock_client.ping.return_value = True
    redis_module = SimpleNamespace(
        ConnectionPool=Mock(return_value=mock_pool),
        Redis=Mock(return_value=mock_client),
    )
    config_loader = Mock(return_value={"host": "redis.local", "port": 6380, "db": 1})
    monkeypatch.setattr(cm, "redis", redis_module)
    monkeypatch.setattr(cm, "get_redis_connection_kwargs", config_loader)

    manager = cm.DatabaseConnectionManager()

    assert manager.get_redis_connection() is mock_client
    assert manager.get_redis_connection() is mock_client
    config_loader.assert_called_once_with("app_cache", decode_responses=True)
    redis_module.ConnectionPool.assert_called_once_with(
        host="redis.local",
        port=6380,
        db=1,
        socket_connect_timeout=5,
        socket_timeout=5,
        max_connections=10,
    )
    redis_module.Redis.assert_called_once_with(connection_pool=mock_pool)
    mock_client.ping.assert_called_once_with()


def test_close_all_connections_closes_supported_connection_types(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_env(monkeypatch)
    manager = cm.DatabaseConnectionManager()
    tdengine_conn = Mock()
    postgresql_pool = Mock()
    redis_conn = Mock()
    redis_pool = Mock()
    manager._connections = {
        "tdengine": tdengine_conn,
        "postgresql": postgresql_pool,
        "redis": (redis_conn, redis_pool),
    }

    manager.close_all_connections()

    tdengine_conn.close.assert_called_once_with()
    postgresql_pool.closeall.assert_called_once_with()
    redis_conn.close.assert_called_once_with()
    redis_pool.disconnect.assert_called_once_with()
    assert manager._connections == {}


def test_test_all_connections_returns_statuses_without_closing_pg_connection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    patch_env(monkeypatch)
    manager = cm.DatabaseConnectionManager()
    pg_conn = Mock()
    pg_pool = Mock()
    pg_pool.getconn.return_value = pg_conn
    monkeypatch.setattr(manager, "get_tdengine_connection", Mock(return_value=Mock()))
    monkeypatch.setattr(manager, "get_postgresql_connection", Mock(return_value=pg_pool))

    results = manager.test_all_connections()

    assert results == {"tdengine": True, "postgresql": True}
    pg_pool.getconn.assert_called_once_with()
    pg_pool.putconn.assert_called_once_with(pg_conn)
    pg_conn.close.assert_not_called()


def test_test_all_connections_records_failures_per_backend(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_env(monkeypatch)
    manager = cm.DatabaseConnectionManager()
    pg_pool = Mock()
    pg_pool.getconn.side_effect = RuntimeError("pg down")
    monkeypatch.setattr(manager, "get_tdengine_connection", Mock(side_effect=RuntimeError("td down")))
    monkeypatch.setattr(manager, "get_postgresql_connection", Mock(return_value=pg_pool))

    results = manager.test_all_connections()

    assert results == {"tdengine": False, "postgresql": False}


def test_get_connection_manager_reuses_singleton_instance(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_env(monkeypatch)
    fake_manager = Mock()
    manager_class = Mock(return_value=fake_manager)
    monkeypatch.setattr(cm, "DatabaseConnectionManager", manager_class)

    first = cm.get_connection_manager()
    second = cm.get_connection_manager()

    assert first is fake_manager
    assert second is fake_manager
    manager_class.assert_called_once_with()
