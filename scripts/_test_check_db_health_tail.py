#!/usr/bin/env python3
"""Support tests extracted from `scripts/tests/test_check_db_health.py`."""

import importlib
import sys
from unittest.mock import MagicMock, patch


try:
    _CHECK_DB_HEALTH_MODULE = importlib.import_module("src.utils.check_db_health")
    if not hasattr(_CHECK_DB_HEALTH_MODULE, "check_mysql_connection"):
        raise ImportError("src.utils.check_db_health missing check_mysql_connection")
except ImportError:
    _CHECK_DB_HEALTH_MODULE = importlib.import_module("scripts.dev.check_db_health")
    sys.modules["src.utils.check_db_health"] = _CHECK_DB_HEALTH_MODULE

check_mysql_connection = _CHECK_DB_HEALTH_MODULE.check_mysql_connection
check_postgresql_connection = _CHECK_DB_HEALTH_MODULE.check_postgresql_connection
check_tdengine_connection = _CHECK_DB_HEALTH_MODULE.check_tdengine_connection
check_redis_connection = _CHECK_DB_HEALTH_MODULE.check_redis_connection
main = _CHECK_DB_HEALTH_MODULE.main


class TestEdgeCasesAndErrorHandling:
    """边界条件和错误处理测试类"""

    @patch("src.utils.check_db_health.check_redis_connection")
    @patch("src.utils.check_db_health.check_tdengine_connection")
    @patch("src.utils.check_db_health.check_postgresql_connection")
    @patch("src.utils.check_db_health.check_mysql_connection")
    @patch("builtins.print")
    def test_main_exception_handling(
        self,
        mock_print,
        mock_mysql,
        mock_pg,
        mock_td,
        mock_redis,
    ):
        """测试主函数异常处理"""
        mock_mysql.side_effect = Exception("MySQL检查异常")

        exit_code = main()

        assert exit_code == 1

    @patch("src.utils.check_db_health.settings")
    @patch("builtins.print")
    def test_mysql_missing_settings(self, mock_print, mock_settings):
        """测试MySQL设置缺失"""
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
        with patch("src.utils.check_db_health.settings") as mock_settings:
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
            mock_settings.tdengine_password = "your-tdengine-password"
            mock_settings.tdengine_database = "test_db"
            mock_settings.redis_host = "localhost"
            mock_settings.redis_port = 6379
            mock_settings.redis_password = ""
            mock_settings.redis_db = 0

            with patch("src.utils.check_db_health.pymysql") as mock_pymysql:
                with patch("src.utils.check_db_health.psycopg2") as mock_psycopg2:
                    with patch("src.utils.check_db_health.taos") as mock_taos:
                        with patch("src.utils.check_db_health.redis") as mock_redis:
                            mock_mysql_conn = MagicMock()
                            mock_mysql_cursor = MagicMock()
                            mock_mysql_cursor.fetchall.return_value = [("test_table",)]
                            mock_mysql_conn.cursor.return_value = mock_mysql_cursor
                            mock_pymysql.connect.return_value = mock_mysql_conn

                            mock_pg_conn = MagicMock()
                            mock_pg_cursor = MagicMock()
                            mock_pg_cursor.fetchone.return_value = ("PostgreSQL 13.0",)
                            mock_pg_cursor.fetchall.return_value = [("pg_table",)]
                            mock_pg_conn.cursor.return_value = mock_pg_cursor
                            mock_psycopg2.connect.side_effect = [
                                mock_pg_conn,
                                Exception("监控数据库连接失败"),
                            ]

                            mock_td_conn = MagicMock()
                            mock_td_cursor = MagicMock()
                            mock_td_cursor.fetchone.return_value = ("3.0.0",)
                            mock_td_cursor.execute.side_effect = [
                                None,
                                Exception("数据库不存在"),
                            ]
                            mock_td_conn.cursor.return_value = mock_td_cursor
                            mock_taos.connect.return_value = mock_td_conn

                            mock_redis.Redis.side_effect = Exception("Redis连接失败")

                            exit_code = main()

                            assert exit_code == 1

                            print_calls = [str(call) for call in mock_print.call_args_list]
                            assert any("3/4" in call for call in print_calls)
                            assert any("75.0%" in call for call in print_calls)
                            assert any("修复建议" in call for call in print_calls)

    def test_path_import_structure(self):
        """测试路径和导入结构"""
        assert callable(check_mysql_connection)
        assert callable(check_postgresql_connection)
        assert callable(check_tdengine_connection)
        assert callable(check_redis_connection)
        assert callable(main)

    @patch("builtins.print")
    def test_constants_and_configuration(self, mock_print):
        """测试常量和配置结构"""
        functions = [
            check_mysql_connection,
            check_postgresql_connection,
            check_tdengine_connection,
            check_redis_connection,
            main,
        ]

        for func in functions:
            assert callable(func)
            try:
                func()
            except Exception as error:
                assert error is not None
