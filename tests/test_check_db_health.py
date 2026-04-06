"""
Contract tests for the `check_db_health` utility script.

These tests validate the current script contract directly instead of using
dynamic imports, skip-heavy fallbacks, or the legacy `{"status": ...}` shape.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import MagicMock

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture
def check_db_health_module():
    return importlib.import_module("src.utils.check_db_health")


@pytest.fixture
def fake_config(monkeypatch: pytest.MonkeyPatch):
    config_module = ModuleType("web.backend.app.core.config")
    config_module.settings = SimpleNamespace(
        postgresql_host="localhost",
        postgresql_port=5432,
        postgresql_user="postgres",
        postgresql_password="postgres",
        postgresql_database="mystocks",
        tdengine_host="localhost",
        tdengine_port=6030,
        tdengine_user="root",
        tdengine_password="taosdata",
        tdengine_database="market_data",
    )
    monkeypatch.setitem(sys.modules, "web.backend.app.core.config", config_module)
    return config_module.settings


class TestDatabaseHealthCheck:
    def test_check_postgresql_connection_returns_success_tuple(
        self,
        monkeypatch: pytest.MonkeyPatch,
        check_db_health_module,
        fake_config,
    ) -> None:
        main_cursor = MagicMock()
        main_cursor.fetchone.return_value = ("PostgreSQL 17.6",)
        main_cursor.fetchall.return_value = [("prices",), ("signals",)]

        monitor_cursor = MagicMock()
        monitor_cursor.fetchall.return_value = [("alerts",)]

        main_connection = MagicMock()
        main_connection.cursor.return_value = main_cursor
        monitor_connection = MagicMock()
        monitor_connection.cursor.return_value = monitor_cursor

        psycopg2_module = ModuleType("psycopg2")
        psycopg2_module.connect = MagicMock(side_effect=[main_connection, monitor_connection])
        monkeypatch.setitem(sys.modules, "psycopg2", psycopg2_module)

        result = check_db_health_module.check_postgresql_connection()

        assert result == (True, None)
        assert psycopg2_module.connect.call_count == 2
        assert psycopg2_module.connect.call_args_list[0].kwargs["database"] == fake_config.postgresql_database
        assert psycopg2_module.connect.call_args_list[1].kwargs["database"] == "mystocks_monitoring"
        main_cursor.execute.assert_any_call("SELECT version()")
        main_connection.close.assert_called_once()
        monitor_connection.close.assert_called_once()

    def test_check_postgresql_connection_returns_failure_tuple(
        self,
        monkeypatch: pytest.MonkeyPatch,
        check_db_health_module,
        fake_config,
    ) -> None:
        psycopg2_module = ModuleType("psycopg2")
        psycopg2_module.connect = MagicMock(side_effect=Exception("Connection refused"))
        monkeypatch.setitem(sys.modules, "psycopg2", psycopg2_module)

        result = check_db_health_module.check_postgresql_connection()

        assert result == (False, "Connection refused")

    def test_check_tdengine_connection_returns_success_tuple(
        self,
        monkeypatch: pytest.MonkeyPatch,
        check_db_health_module,
        fake_config,
    ) -> None:
        cursor = MagicMock()
        cursor.fetchone.return_value = ("3.0.0",)
        cursor.fetchall.return_value = [("ts_tick_data",), ("ts_kline",)]

        connection = MagicMock()
        connection.cursor.return_value = cursor

        taos_module = ModuleType("taos")
        taos_module.connect = MagicMock(return_value=connection)
        monkeypatch.setitem(sys.modules, "taos", taos_module)

        result = check_db_health_module.check_tdengine_connection()

        assert result == (True, None)
        taos_module.connect.assert_called_once_with(
            host=fake_config.tdengine_host,
            port=fake_config.tdengine_port,
            user=fake_config.tdengine_user,
            password=fake_config.tdengine_password,
            timeout=5000,
        )
        cursor.execute.assert_any_call("SELECT CLIENT_VERSION()")
        cursor.execute.assert_any_call(f"USE {fake_config.tdengine_database}")
        cursor.execute.assert_any_call("SHOW STABLES")
        cursor.close.assert_called_once()
        connection.close.assert_called_once()

    def test_check_tdengine_connection_returns_failure_tuple(
        self,
        monkeypatch: pytest.MonkeyPatch,
        check_db_health_module,
        fake_config,
    ) -> None:
        taos_module = ModuleType("taos")
        taos_module.connect = MagicMock(side_effect=Exception("Connection refused"))
        monkeypatch.setitem(sys.modules, "taos", taos_module)

        result = check_db_health_module.check_tdengine_connection()

        assert result == (False, "Connection refused")

    def test_check_redis_connection_returns_success_tuple(
        self,
        monkeypatch: pytest.MonkeyPatch,
        check_db_health_module,
        fake_config,
    ) -> None:
        redis_client = MagicMock()
        redis_client.info.return_value = {"redis_version": "7.0.0", "used_memory_human": "1.00M"}
        redis_client.dbsize.return_value = 12

        redis_module = ModuleType("redis")
        redis_module.Redis = MagicMock(return_value=redis_client)
        monkeypatch.setitem(sys.modules, "redis", redis_module)
        monkeypatch.setattr(
            check_db_health_module,
            "get_redis_connection_kwargs",
            lambda *_args, **_kwargs: {
                "host": "localhost",
                "port": 6379,
                "password": None,
                "db": 1,
            },
        )

        result = check_db_health_module.check_redis_connection()

        assert result == (True, None)
        redis_module.Redis.assert_called_once()
        redis_client.ping.assert_called_once()
        redis_client.close.assert_called_once()


class TestHealthCheckMain:
    def test_main_summarizes_partial_failure_and_returns_non_zero(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
        check_db_health_module,
    ) -> None:
        monkeypatch.setattr(check_db_health_module, "check_postgresql_connection", lambda: (True, None))
        monkeypatch.setattr(check_db_health_module, "check_tdengine_connection", lambda: (False, "tdengine down"))
        monkeypatch.setattr(check_db_health_module, "check_redis_connection", lambda: (True, None))

        exit_code = check_db_health_module.main()
        output = capsys.readouterr().out

        assert exit_code == 1
        assert "MyStocks 数据库健康检查" in output
        assert "总计: 2/3 个数据库连接成功" in output
        assert "【TDengine修复】" in output
        assert "【Redis修复】" not in output
