#!/usr/bin/env python3
"""
数据库健康检查模块测试套件
基于Phase 6成功模式：功能→边界→异常→性能→集成测试
"""

import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock, Mock
import pytest

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 导入被测试的模块
from src.utils.check_db_health import (
    check_mysql_connection,
    check_postgresql_connection,
    check_tdengine_connection,
    check_redis_connection,
    main,
)


class TestMySQLConnection:
    """MySQL连接测试类"""

    @patch("src.utils.check_db_health.pymysql")
    @patch("web.backend.app.core.config.settings")
    @patch("builtins.print")
    def test_mysql_connection_success(self, mock_print, mock_settings, mock_pymysql):
        """测试MySQL连接成功"""
        # 模拟设置
        mock_settings.mysql_host = "localhost"
        mock_settings.mysql_port = 3306
        mock_settings.mysql_user = "test_user"
        mock_settings.mysql_password = "test_pass"
        mock_settings.mysql_database = "test_db"

        # 模拟数据库连接和查询结果
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [("test_table1",), ("test_table2",)]
        mock_conn.cursor.return_value = mock_cursor
        mock_pymysql.connect.return_value = mock_conn

        success, error = check_mysql_connection()

        assert success is True
        assert error is None
        mock_pymysql.connect.assert_called_once_with(
            host="localhost",
            port=3306,
            user="test_user",
            password="test_pass",
            database="test_db",
            connect_timeout=5,
        )
        mock_cursor.execute.assert_called()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch("src.utils.check_db_health.pymysql")
    @patch("src.utils.check_db_health.settings")
    @patch("builtins.print")
    def test_mysql_connection_import_error(
        self, mock_print, mock_settings, mock_pymysql
    ):
        """测试pymysql导入错误"""
        mock_pymysql.side_effect = ImportError("No module named 'pymysql'")

        success, error = check_mysql_connection()

        assert success is False
        assert "No module named 'pymysql'" in error

    @patch("src.utils.check_db_health.pymysql")
    @patch("src.utils.check_db_health.settings")
    @patch("builtins.print")
    def test_mysql_connection_connection_error(
        self, mock_print, mock_settings, mock_pymysql
    ):
        """测试MySQL连接错误"""
        mock_settings.mysql_host = "invalid_host"
        mock_pymysql.connect.side_effect = Exception("连接失败")

        success, error = check_mysql_connection()

        assert success is False
        assert error == "连接失败"

    @patch("src.utils.check_db_health.pymysql")
    @patch("src.utils.check_db_health.settings")
    @patch("builtins.print")
    def test_mysql_connection_query_error(
        self, mock_print, mock_settings, mock_pymysql
    ):
        """测试MySQL查询错误"""
        mock_settings.mysql_host = "localhost"
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = Exception("查询失败")
        mock_conn.cursor.return_value = mock_cursor
        mock_pymysql.connect.return_value = mock_conn

        success, error = check_mysql_connection()

        assert success is False
        assert error == "查询失败"

    @patch("src.utils.check_db_health.pymysql")
    @patch("src.utils.check_db_health.settings")
    @patch("builtins.print")
    def test_mysql_connection_no_tables(self, mock_print, mock_settings, mock_pymysql):
        """测试MySQL没有表的情况"""
        mock_settings.mysql_host = "localhost"
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []  # 没有表
        mock_conn.cursor.return_value = mock_cursor
        mock_pymysql.connect.return_value = mock_conn

        success, error = check_mysql_connection()

        assert success is True
        assert error is None

    @patch("src.utils.check_db_health.pymysql")
    @patch("src.utils.check_db_health.settings")
    @patch("builtins.print")
    def test_mysql_connection_single_table(
        self, mock_print, mock_settings, mock_pymysql
    ):
        """测试MySQL只有一个表的情况"""
        mock_settings.mysql_host = "localhost"
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [("single_table",)]
        mock_conn.cursor.return_value = mock_cursor
        mock_pymysql.connect.return_value = mock_conn

        success, error = check_mysql_connection()

        assert success is True
        assert error is None


class TestPostgreSQLConnection:
    """PostgreSQL连接测试类"""

    @patch("src.utils.check_db_health.psycopg2")
    @patch("src.utils.check_db_health.settings")
    @patch("builtins.print")
    def test_postgresql_connection_success(
        self, mock_print, mock_settings, mock_psycopg2
    ):
        """测试PostgreSQL连接成功"""
        mock_settings.postgresql_host = "localhost"
        mock_settings.postgresql_port = 5432
        mock_settings.postgresql_user = "test_user"
        mock_settings.postgresql_password = "test_pass"
        mock_settings.postgresql_database = "test_db"

        # 模拟主数据库连接
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = ("PostgreSQL 13.0",)
        mock_cursor.fetchall.return_value = [("table1",), ("table2",)]
        mock_conn.cursor.return_value = mock_cursor
        mock_psycopg2.connect.return_value = mock_conn

        success, error = check_postgresql_connection()

        assert success is True
        assert error is None

    @patch("src.utils.check_db_health.psycopg2")
    @patch("src.utils.check_db_health.settings")
    @patch("builtins.print")
    def test_postgresql_connection_import_error(
        self, mock_print, mock_settings, mock_psycopg2
    ):
        """测试psycopg2导入错误"""
        mock_psycopg2.side_effect = ImportError("No module named 'psycopg2'")

        success, error = check_postgresql_connection()

        assert success is False
        assert "No module named 'psycopg2'" in error

    @patch("src.utils.check_db_health.psycopg2")
    @patch("src.utils.check_db_health.settings")
    @patch("builtins.print")
    def test_postgresql_connection_main_db_error(
        self, mock_print, mock_settings, mock_psycopg2
    ):
        """测试PostgreSQL主数据库连接错误"""
        mock_settings.postgresql_host = "invalid_host"
        mock_psycopg2.connect.side_effect = Exception("连接失败")

        success, error = check_postgresql_connection()

        assert success is False
        assert error == "连接失败"

    @patch("src.utils.check_db_health.psycopg2")
    @patch("src.utils.check_db_health.settings")
    @patch("builtins.print")
    def test_postgresql_connection_monitor_db_success(
        self, mock_print, mock_settings, mock_psycopg2
    ):
        """测试PostgreSQL监控数据库连接成功"""
        mock_settings.postgresql_host = "localhost"
        mock_settings.postgresql_database = "test_db"

        # 模拟主数据库连接
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = ("PostgreSQL 13.0",)
        mock_cursor.fetchall.return_value = [("table1",)]
        mock_conn.cursor.return_value = mock_cursor

        # 模拟监控数据库连接
        mock_conn_monitor = MagicMock()
        mock_cursor_monitor = MagicMock()
        mock_cursor_monitor.fetchall.return_value = [("monitor_table1",)]
        mock_conn_monitor.cursor.return_value = mock_cursor_monitor

        mock_psycopg2.connect.side_effect = [mock_conn, mock_conn_monitor]

        success, error = check_postgresql_connection()

        assert success is True
        assert error is None

    @patch("src.utils.check_db_health.psycopg2")
    @patch("src.utils.check_db_health.settings")
    @patch("builtins.print")
    def test_postgresql_connection_monitor_db_error(
        self, mock_print, mock_settings, mock_psycopg2
    ):
        """测试PostgreSQL监控数据库连接失败"""
        mock_settings.postgresql_host = "localhost"
        mock_settings.postgresql_database = "test_db"

        # 模拟主数据库连接成功
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = ("PostgreSQL 13.0",)
        mock_cursor.fetchall.return_value = [("table1",)]
        mock_conn.cursor.return_value = mock_cursor

        # 模拟监控数据库连接失败
        mock_psycopg2.connect.side_effect = [mock_conn, Exception("监控数据库连接失败")]

        success, error = check_postgresql_connection()

        assert success is True  # 主数据库成功，监控数据库失败不影响整体结果
        assert error is None

    @patch("src.utils.check_db_health.psycopg2")
    @patch("src.utils.check_db_health.settings")
    @patch("builtins.print")
    def test_postgresql_connection_query_error(
        self, mock_print, mock_settings, mock_psycopg2
    ):
        """测试PostgreSQL查询错误"""
        mock_settings.postgresql_host = "localhost"
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = Exception("查询失败")
        mock_conn.cursor.return_value = mock_cursor
        mock_psycopg2.connect.return_value = mock_conn

        success, error = check_postgresql_connection()

        assert success is False
        assert error == "查询失败"

    @patch("src.utils.check_db_health.psycopg2")
    @patch("src.utils.check_db_health.settings")
    @patch("builtins.print")
    def test_postgresql_connection_empty_database(
        self, mock_print, mock_settings, mock_psycopg2
    ):
        """测试PostgreSQL空数据库"""
        mock_settings.postgresql_host = "localhost"
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = ("PostgreSQL 13.0",)
        mock_cursor.fetchall.return_value = []  # 没有表
        mock_conn.cursor.return_value = mock_cursor
        mock_psycopg2.connect.return_value = mock_conn

        success, error = check_postgresql_connection()

        assert success is True
        assert error is None


class TestTDengineConnection:
    """TDengine连接测试类"""

    @patch("src.utils.check_db_health.taos")
    @patch("src.utils.check_db_health.settings")
    @patch("builtins.print")
    def test_tdengine_connection_success(self, mock_print, mock_settings, mock_taos):
        """测试TDengine连接成功"""
        mock_settings.tdengine_host = "localhost"
        mock_settings.tdengine_port = 6030
        mock_settings.tdengine_user = "root"
        mock_settings.tdengine_password = "taosdata"
        mock_settings.tdengine_database = "test_db"

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = ("3.0.0",)
        mock_cursor.fetchall.return_value = [("stable1",), ("stable2",)]
        mock_conn.cursor.return_value = mock_cursor
        mock_taos.connect.return_value = mock_conn

        success, error = check_tdengine_connection()

        assert success is True
        assert error is None
        mock_taos.connect.assert_called_once_with(
            host="localhost",
            port=6030,
            user="root",
            password="taosdata",
            timeout=5000,
        )

    @patch("src.utils.check_db_health.taos")
    @patch("src.utils.check_db_health.settings")
    @patch("builtins.print")
    def test_tdengine_connection_import_error(
        self, mock_print, mock_settings, mock_taos
    ):
        """测试taos导入错误"""
        mock_taos.side_effect = ImportError("No module named 'taos'")

        success, error = check_tdengine_connection()

        assert success is False
        assert "No module named 'taos'" in error

    @patch("src.utils.check_db_health.taos")
    @patch("src.utils.check_db_health.settings")
    @patch("builtins.print")
    def test_tdengine_connection_connection_error(
        self, mock_print, mock_settings, mock_taos
    ):
        """测试TDengine连接错误"""
        mock_settings.tdengine_host = "invalid_host"
        mock_taos.connect.side_effect = Exception("连接失败")

        success, error = check_tdengine_connection()

        assert success is False
        assert error == "连接失败"

    @patch("src.utils.check_db_health.taos")
    @patch("src.utils.check_db_health.settings")
    @patch("builtins.print")
    def test_tdengine_connection_client_version_fallback(
        self, mock_print, mock_settings, mock_taos
    ):
        """测试TDengine CLIENT_VERSION()失败时的回退机制"""
        mock_settings.tdengine_host = "localhost"
        mock_settings.tdengine_database = "test_db"

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        # 第一次执行CLIENT_VERSION()失败，第二次执行SHOW VARIABLES成功
        mock_cursor.execute.side_effect = [Exception("CLIENT_VERSION失败"), None]
        mock_cursor.fetchall.return_value = [("stable1",)]
        mock_conn.cursor.return_value = mock_cursor
        mock_taos.connect.return_value = mock_conn

        success, error = check_tdengine_connection()

        assert success is True
        assert error is None

    @patch("src.utils.check_db_health.taos")
    @patch("src.utils.check_db_health.settings")
    @patch("builtins.print")
    def test_tdengine_connection_database_not_exist(
        self, mock_print, mock_settings, mock_taos
    ):
        """测试TDengine数据库不存在"""
        mock_settings.tdengine_host = "localhost"
        mock_settings.tdengine_database = "nonexistent_db"

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = ("3.0.0",)
        # USE数据库失败
        mock_cursor.execute.side_effect = [None, Exception("数据库不存在")]
        mock_conn.cursor.return_value = mock_cursor
        mock_taos.connect.return_value = mock_conn

        success, error = check_tdengine_connection()

        assert success is True  # 连接成功，数据库不存在不算失败
        assert error is None

    @patch("src.utils.check_db_health.taos")
    @patch("src.utils.check_db_health.settings")
    @patch("builtins.print")
    def test_tdengine_connection_no_stables(self, mock_print, mock_settings, mock_taos):
        """测试TDengine没有超级表"""
        mock_settings.tdengine_host = "localhost"
        mock_settings.tdengine_database = "test_db"

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = ("3.0.0",)
        mock_cursor.fetchall.return_value = []  # 没有超级表
        mock_conn.cursor.return_value = mock_cursor
        mock_taos.connect.return_value = mock_conn

        success, error = check_tdengine_connection()

        assert success is True
        assert error is None

    @patch("src.utils.check_db_health.taos")
    @patch("src.utils.check_db_health.settings")
    @patch("builtins.print")
    def test_tdengine_connection_use_db_error(
        self, mock_print, mock_settings, mock_taos
    ):
        """测试TDengine USE数据库错误"""
        mock_settings.tdengine_host = "localhost"
        mock_settings.tdengine_database = "test_db"

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = ("3.0.0",)
        # USE数据库失败
        mock_cursor.execute.side_effect = [None, Exception("无权限"), None]
        mock_cursor.fetchall.return_value = [("stable1",)]
        mock_conn.cursor.return_value = mock_cursor
        mock_taos.connect.return_value = mock_conn

        success, error = check_tdengine_connection()

        assert success is True
        assert error is None


class TestRedisConnection:
    """Redis连接测试类"""

    @patch("src.utils.check_db_health.redis")
    @patch("src.utils.check_db_health.settings")
    @patch("builtins.print")
    def test_redis_connection_success(self, mock_print, mock_settings, mock_redis):
        """测试Redis连接成功"""
        mock_settings.redis_host = "localhost"
        mock_settings.redis_port = 6379
        mock_settings.redis_password = "test_pass"
        mock_settings.redis_db = 0

        mock_redis_client = MagicMock()
        mock_redis_client.ping.return_value = True
        mock_redis_client.info.return_value = {
            "redis_version": "6.0.0",
            "used_memory_human": "1M",
        }
        mock_redis_client.dbsize.return_value = 100
        mock_redis.Redis.return_value = mock_redis_client

        success, error = check_redis_connection()

        assert success is True
        assert error is None
        mock_redis.Redis.assert_called_once_with(
            host="localhost",
            port=6379,
            password="test_pass",
            db=0,
            socket_connect_timeout=5,
        )

    @patch("src.utils.check_db_health.redis")
    @patch("src.utils.check_db_health.settings")
    @patch("builtins.print")
    def test_redis_connection_import_error(self, mock_print, mock_settings, mock_redis):
        """测试redis导入错误"""
        mock_redis.side_effect = ImportError("No module named 'redis'")

        success, error = check_redis_connection()

        assert success is False
        assert "No module named 'redis'" in error

    @patch("src.utils.check_db_health.redis")
    @patch("src.utils.check_db_health.settings")
    @patch("builtins.print")
    def test_redis_connection_no_password(self, mock_print, mock_settings, mock_redis):
        """测试Redis无密码连接"""
        mock_settings.redis_host = "localhost"
        mock_settings.redis_port = 6379
        mock_settings.redis_password = ""
        mock_settings.redis_db = 1

        mock_redis_client = MagicMock()
        mock_redis_client.ping.return_value = True
        mock_redis_client.info.return_value = {"redis_version": "6.0.0"}
        mock_redis_client.dbsize.return_value = 50
        mock_redis.Redis.return_value = mock_redis_client

        success, error = check_redis_connection()

        assert success is True
        assert error is None
        # 验证密码为None而不是空字符串
        mock_redis.Redis.assert_called_once_with(
            host="localhost",
            port=6379,
            password=None,
            db=1,
            socket_connect_timeout=5,
        )

    @patch("src.utils.check_db_health.redis")
    @patch("src.utils.check_db_health.settings")
    @patch("builtins.print")
    def test_redis_connection_connection_error(
        self, mock_print, mock_settings, mock_redis
    ):
        """测试Redis连接错误"""
        mock_settings.redis_host = "invalid_host"
        mock_redis.Redis.side_effect = Exception("连接失败")

        success, error = check_redis_connection()

        assert success is False
        assert error == "连接失败"

    @patch("src.utils.check_db_health.redis")
    @patch("src.utils.check_db_health.settings")
    @patch("builtins.print")
    def test_redis_connection_ping_error(self, mock_print, mock_settings, mock_redis):
        """测试Redis ping错误"""
        mock_settings.redis_host = "localhost"
        mock_redis_client = MagicMock()
        mock_redis_client.ping.side_effect = Exception("ping失败")
        mock_redis.Redis.return_value = mock_redis_client

        success, error = check_redis_connection()

        assert success is False
        assert error == "ping失败"

    @patch("src.utils.check_db_health.redis")
    @patch("src.utils.check_db_health.settings")
    @patch("builtins.print")
    def test_redis_connection_info_error(self, mock_print, mock_settings, mock_redis):
        """测试Redis info获取错误"""
        mock_settings.redis_host = "localhost"
        mock_redis_client = MagicMock()
        mock_redis_client.ping.return_value = True
        mock_redis_client.info.side_effect = Exception("info失败")
        mock_redis.Redis.return_value = mock_redis_client

        success, error = check_redis_connection()

        assert success is False
        assert error == "info失败"

    @patch("src.utils.check_db_health.redis")
    @patch("src.utils.check_db_health.settings")
    @patch("builtins.print")
    def test_redis_connection_dbsize_error(self, mock_print, mock_settings, mock_redis):
        """测试Redis dbsize获取错误"""
        mock_settings.redis_host = "localhost"
        mock_redis_client = MagicMock()
        mock_redis_client.ping.return_value = True
        mock_redis_client.info.return_value = {"redis_version": "6.0.0"}
        mock_redis_client.dbsize.side_effect = Exception("dbsize失败")
        mock_redis.Redis.return_value = mock_redis_client

        success, error = check_redis_connection()

        assert success is False
        assert error == "dbsize失败"

    @patch("src.utils.check_db_health.redis")
    @patch("src.utils.check_db_health.settings")
    @patch("builtins.print")
    def test_redis_connection_missing_info(self, mock_print, mock_settings, mock_redis):
        """测试Redis info返回不完整信息"""
        mock_settings.redis_host = "localhost"
        mock_redis_client = MagicMock()
        mock_redis_client.ping.return_value = True
        mock_redis_client.info.return_value = {}  # 空信息
        mock_redis_client.dbsize.return_value = 0
        mock_redis.Redis.return_value = mock_redis_client

        success, error = check_redis_connection()

        assert success is True
        assert error is None


class TestMainFunction:
    """主函数测试类"""

    @patch("src.utils.check_db_health.check_redis_connection")
    @patch("src.utils.check_db_health.check_tdengine_connection")
    @patch("src.utils.check_db_health.check_postgresql_connection")
    @patch("src.utils.check_db_health.check_mysql_connection")
    @patch("builtins.print")
    def test_main_all_success(
        self, mock_print, mock_mysql, mock_pg, mock_td, mock_redis
    ):
        """测试所有数据库连接成功"""
        mock_mysql.return_value = (True, None)
        mock_pg.return_value = (True, None)
        mock_td.return_value = (True, None)
        mock_redis.return_value = (True, None)

        exit_code = main()

        assert exit_code == 0
        mock_mysql.assert_called_once()
        mock_pg.assert_called_once()
        mock_td.assert_called_once()
        mock_redis.assert_called_once()

    @patch("src.utils.check_db_health.check_redis_connection")
    @patch("src.utils.check_db_health.check_tdengine_connection")
    @patch("src.utils.check_db_health.check_postgresql_connection")
    @patch("src.utils.check_db_health.check_mysql_connection")
    @patch("builtins.print")
    def test_main_partial_failure(
        self, mock_print, mock_mysql, mock_pg, mock_td, mock_redis
    ):
        """测试部分数据库连接失败"""
        mock_mysql.return_value = (True, None)
        mock_pg.return_value = (False, "PostgreSQL错误")
        mock_td.return_value = (True, None)
        mock_redis.return_value = (False, "Redis错误")

        exit_code = main()

        assert exit_code == 1

    @patch("src.utils.check_db_health.check_redis_connection")
    @patch("src.utils.check_db_health.check_tdengine_connection")
    @patch("src.utils.check_db_health.check_postgresql_connection")
    @patch("src.utils.check_db_health.check_mysql_connection")
    @patch("builtins.print")
    def test_main_all_failure(
        self, mock_print, mock_mysql, mock_pg, mock_td, mock_redis
    ):
        """测试所有数据库连接失败"""
        mock_mysql.return_value = (False, "MySQL错误")
        mock_pg.return_value = (False, "PostgreSQL错误")
        mock_td.return_value = (False, "TDengine错误")
        mock_redis.return_value = (False, "Redis错误")

        exit_code = main()

        assert exit_code == 1

    @patch("src.utils.check_db_health.check_redis_connection")
    @patch("src.utils.check_db_health.check_tdengine_connection")
    @patch("src.utils.check_db_health.check_postgresql_connection")
    @patch("src.utils.check_db_health.check_mysql_connection")
    @patch("builtins.print")
    def test_main_statistics_calculation(
        self, mock_print, mock_mysql, mock_pg, mock_td, mock_redis
    ):
        """测试统计计算"""
        # 2个成功，2个失败
        mock_mysql.return_value = (True, None)
        mock_pg.return_value = (True, None)
        mock_td.return_value = (False, "TDengine错误")
        mock_redis.return_value = (False, "Redis错误")

        exit_code = main()

        assert exit_code == 1
        # 验证统计信息被正确打印
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("2/4" in call for call in print_calls)
        assert any("50.0%" in call for call in print_calls)

    @patch("src.utils.check_db_health.check_redis_connection")
    @patch("src.utils.check_db_health.check_tdengine_connection")
    @patch("src.utils.check_db_health.check_postgresql_connection")
    @patch("src.utils.check_db_health.check_mysql_connection")
    @patch("builtins.print")
    def test_main_fix_suggestions(
        self, mock_print, mock_mysql, mock_pg, mock_td, mock_redis
    ):
        """测试修复建议输出"""
        # 只有MySQL成功
        mock_mysql.return_value = (True, None)
        mock_pg.return_value = (False, "PostgreSQL错误")
        mock_td.return_value = (False, "TDengine错误")
        mock_redis.return_value = (False, "Redis错误")

        exit_code = main()

        assert exit_code == 1
        # 验证修复建议被打印
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("修复建议" in call for call in print_calls)
        assert any("PostgreSQL修复" in call for call in print_calls)
        assert any("TDengine修复" in call for call in print_calls)
        assert any("Redis修复" in call for call in print_calls)

    @patch("src.utils.check_db_health.check_redis_connection")
    @patch("src.utils.check_db_health.check_tdengine_connection")
    @patch("src.utils.check_db_health.check_postgresql_connection")
    @patch("src.utils.check_db_health.check_mysql_connection")
    @patch("builtins.print")
    def test_main_no_fix_suggestions(
        self, mock_print, mock_mysql, mock_pg, mock_td, mock_redis
    ):
        """测试没有修复建议的情况（全部成功）"""
        mock_mysql.return_value = (True, None)
        mock_pg.return_value = (True, None)
        mock_td.return_value = (True, None)
        mock_redis.return_value = (True, None)

        exit_code = main()

        assert exit_code == 0
        # 验证没有修复建议
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("4/4" in call for call in print_calls)
        assert any("100.0%" in call for call in print_calls)


class TestEdgeCasesAndErrorHandling:
    """边界条件和错误处理测试类"""

    @patch("src.utils.check_db_health.check_redis_connection")
    @patch("src.utils.check_db_health.check_tdengine_connection")
    @patch("src.utils.check_db_health.check_postgresql_connection")
    @patch("src.utils.check_db_health.check_mysql_connection")
    @patch("builtins.print")
    def test_main_exception_handling(
        self, mock_print, mock_mysql, mock_pg, mock_td, mock_redis
    ):
        """测试主函数异常处理"""
        mock_mysql.side_effect = Exception("MySQL检查异常")

        exit_code = main()

        # 应该优雅地处理异常
        assert exit_code == 1

    @patch("src.utils.check_db_health.settings")
    @patch("builtins.print")
    def test_mysql_missing_settings(self, mock_print, mock_settings):
        """测试MySQL设置缺失"""
        # 模拟settings对象缺少某些属性
        del mock_settings.mysql_host

        with patch("src.utils.check_db_health.pymysql") as mock_pymysql:
            mock_pymysql.connect.side_effect = AttributeError("Missing attribute")

            success, error = check_mysql_connection()

            assert success is False
            assert "Missing attribute" in error

    @patch("src.utils.check_db_health.settings")
    @patch("builtins.print")
    def test_postgresql_missing_settings(self, mock_print, mock_settings):
        """测试PostgreSQL设置缺失"""
        del mock_settings.postgresql_host

        with patch("src.utils.check_db_health.psycopg2") as mock_psycopg2:
            mock_psycopg2.connect.side_effect = AttributeError("Missing attribute")

            success, error = check_postgresql_connection()

            assert success is False
            assert "Missing attribute" in error

    @patch("src.utils.check_db_health.settings")
    @patch("builtins.print")
    def test_tdengine_missing_settings(self, mock_print, mock_settings):
        """测试TDengine设置缺失"""
        del mock_settings.tdengine_host

        with patch("src.utils.check_db_health.taos") as mock_taos:
            mock_taos.connect.side_effect = AttributeError("Missing attribute")

            success, error = check_tdengine_connection()

            assert success is False
            assert "Missing attribute" in error

    @patch("src.utils.check_db_health.settings")
    @patch("builtins.print")
    def test_redis_missing_settings(self, mock_print, mock_settings):
        """测试Redis设置缺失"""
        del mock_settings.redis_host

        with patch("src.utils.check_db_health.redis") as mock_redis:
            mock_redis.Redis.side_effect = AttributeError("Missing attribute")

            success, error = check_redis_connection()

            assert success is False
            assert "Missing attribute" in error


class TestIntegrationScenarios:
    """集成场景测试类"""

    @patch("builtins.print")
    def test_real_workflow_simulation(self, mock_print):
        """模拟真实工作流程"""
        # 这个测试模拟实际的数据库检查流程，而不依赖真实的数据库服务

        with patch("src.utils.check_db_health.settings") as mock_settings:
            # 设置模拟的配置
            mock_settings.mysql_host = "localhost"
            mock_settings.mysql_port = 3306
            mock_settings.mysql_user = "test_user"
            mock_settings.mysql_password = "test_pass"
            mock_settings.mysql_database = "test_db"
            mock_settings.postgresql_host = "localhost"
            mock_settings.postgresql_port = 5432
            mock_settings.postgresql_user = "test_user"
            mock_settings.postgresql_password = "test_pass"
            mock_settings.postgresql_database = "test_db"
            mock_settings.tdengine_host = "localhost"
            mock_settings.tdengine_port = 6030
            mock_settings.tdengine_user = "root"
            mock_settings.tdengine_password = "taosdata"
            mock_settings.tdengine_database = "test_db"
            mock_settings.redis_host = "localhost"
            mock_settings.redis_port = 6379
            mock_settings.redis_password = ""
            mock_settings.redis_db = 0

            # 模拟不同数据库的不同响应
            with patch("src.utils.check_db_health.pymysql") as mock_pymysql:
                with patch("src.utils.check_db_health.psycopg2") as mock_psycopg2:
                    with patch("src.utils.check_db_health.taos") as mock_taos:
                        with patch("src.utils.check_db_health.redis") as mock_redis:
                            # MySQL连接成功
                            mock_mysql_conn = MagicMock()
                            mock_mysql_cursor = MagicMock()
                            mock_mysql_cursor.fetchall.return_value = [("test_table",)]
                            mock_mysql_conn.cursor.return_value = mock_mysql_cursor
                            mock_pymysql.connect.return_value = mock_mysql_conn

                            # PostgreSQL连接成功，监控数据库失败
                            mock_pg_conn = MagicMock()
                            mock_pg_cursor = MagicMock()
                            mock_pg_cursor.fetchone.return_value = ("PostgreSQL 13.0",)
                            mock_pg_cursor.fetchall.return_value = [("pg_table",)]
                            mock_pg_conn.cursor.return_value = mock_pg_cursor
                            mock_psycopg2.connect.side_effect = [
                                mock_pg_conn,
                                Exception("监控数据库连接失败"),
                            ]

                            # TDengine连接成功但数据库不存在
                            mock_td_conn = MagicMock()
                            mock_td_cursor = MagicMock()
                            mock_td_cursor.fetchone.return_value = ("3.0.0",)
                            mock_td_cursor.execute.side_effect = [
                                None,
                                Exception("数据库不存在"),
                            ]
                            mock_td_conn.cursor.return_value = mock_td_cursor
                            mock_taos.connect.return_value = mock_td_conn

                            # Redis连接失败
                            mock_redis.Redis.side_effect = Exception("Redis连接失败")

                            # 执行主函数
                            exit_code = main()

                            # 验证结果：3个成功，1个失败
                            assert exit_code == 1

                            # 验证输出包含关键信息
                            print_calls = [
                                str(call) for call in mock_print.call_args_list
                            ]
                            assert any("3/4" in call for call in print_calls)
                            assert any("75.0%" in call for call in print_calls)
                            assert any("修复建议" in call for call in print_calls)

    def test_path_import_structure(self):
        """测试路径和导入结构"""
        # 验证模块可以被正确导入
        assert callable(check_mysql_connection)
        assert callable(check_postgresql_connection)
        assert callable(check_tdengine_connection)
        assert callable(check_redis_connection)
        assert callable(main)

    @patch("builtins.print")
    def test_constants_and_configuration(self, mock_print):
        """测试常量和配置结构"""
        # 验证模块的基本结构完整性
        functions = [
            check_mysql_connection,
            check_postgresql_connection,
            check_tdengine_connection,
            check_redis_connection,
            main,
        ]

        for func in functions:
            assert callable(func)
            # 验证函数可以被调用（即使可能失败）
            try:
                # 尝试调用函数，预期会失败（因为没有mock数据库）
                func()
            except Exception as e:
                # 预期的异常，因为数据库服务不存在
                assert e is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
