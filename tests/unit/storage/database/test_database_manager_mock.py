"""
Database Manager Mock 测试
专注于模拟测试，避免实际数据库连接
目标覆盖率: 60%+
"""

import os
import sys
from unittest.mock import Mock, mock_open, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../../.."))

from src.storage.database.database_manager import DatabaseTableManager, DatabaseType


class TestDatabaseManagerMockOnly:
    """纯Mock测试DatabaseTableManager"""

    def test_init_mock_only(self):
        """测试仅模拟初始化"""
        with patch("src.storage.database.database_manager.load_dotenv"):
            manager = DatabaseTableManager()
            assert manager is not None
            assert hasattr(manager, "connections")
            assert hasattr(manager, "connection_pool")
            assert len(manager.connections) == 0

    @patch("src.storage.database.database_manager.psycopg2.connect")
    def test_get_postgresql_connection_mock_only(self, mock_connect):
        """测试PostgreSQL连接（仅模拟）"""
        mock_conn = Mock()
        mock_connect.return_value = mock_conn

        manager = DatabaseTableManager()

        with patch.dict(
            os.environ,
            {
                "POSTGRESQL_HOST": "localhost",
                "POSTGRESQL_USER": "test",
                "POSTGRESQL_PASSWORD": "test",
                "POSTGRESQL_PORT": "5432",
            },
        ):
            result = manager.get_connection(DatabaseType.POSTGRESQL, "test_db")
            assert result == mock_conn
            mock_connect.assert_called_once()

    @patch("src.storage.database.database_manager.taos.connect")
    def test_get_tdengine_connection_mock_only(self, mock_connect):
        """测试TDengine连接（仅模拟）"""
        mock_conn = Mock()
        mock_connect.return_value = mock_conn

        manager = DatabaseTableManager()

        with patch.dict(
            os.environ,
            {
                "TDENGINE_HOST": "localhost",
                "TDENGINE_USER": "root",
                "TDENGINE_PASSWORD": "taosdata",
            },
        ):
            result = manager.get_connection(DatabaseType.TDENGINE, "test_db")
            assert result == mock_conn
            mock_connect.assert_called_once()

    def test_get_connection_unsupported_db(self):
        """测试不支持的数据库类型"""
        manager = DatabaseTableManager()

        with pytest.raises(ValueError):
            manager.get_connection("UNSUPPORTED", "test_db")

    def test_close_all_connections_mock(self):
        """测试关闭所有连接（仅模拟）"""
        manager = DatabaseTableManager()

        # 模拟一些连接
        mock_conn1 = Mock()
        mock_conn2 = Mock()
        manager.connections = {"db1": mock_conn1, "db2": mock_conn2}

        manager.close_all_connections()

        mock_conn1.close.assert_called_once()
        mock_conn2.close.assert_called_once()
        assert len(manager.connections) == 0

    def test_log_operation_mock(self):
        """测试日志记录（仅模拟）"""
        manager = DatabaseTableManager()

        with patch("src.storage.database.database_manager.logging") as mock_logging:
            manager._log_operation(
                operation="CREATE_TABLE",
                table_name="test_table",
                db_type="postgresql",
                details={"columns": 3},
            )

            mock_logging.info.assert_called_once()

            # 检查日志内容
            call_args = mock_logging.info.call_args[0][0]
            assert "CREATE_TABLE" in call_args
            assert "test_table" in call_args

    def test_generate_postgresql_ddl_mock(self):
        """测试PostgreSQL DDL生成"""
        manager = DatabaseTableManager()

        col_def = {
            "name": "test_col",
            "type": "VARCHAR",
            "length": 100,
            "nullable": False,
        }

        result = manager._generate_postgresql_ddl(col_def)

        assert "test_col" in result
        assert "VARCHAR" in result
        assert "(100)" in result
        assert "NOT NULL" in result

    def test_generate_tdengine_ddl_mock(self):
        """测试TDengine DDL生成"""
        manager = DatabaseTableManager()

        col_def = {"name": "ts", "type": "TIMESTAMP"}

        result = manager._generate_tdengine_ddl(col_def)

        assert "ts" in result
        assert "TIMESTAMP" in result

    def test_generate_mysql_ddl_mock(self):
        """测试MySQL DDL生成"""
        manager = DatabaseTableManager()

        col_def = {"name": "test_col", "type": "DECIMAL", "precision": 10, "scale": 2}

        result = manager._generate_mysql_ddl(col_def)

        assert "test_col" in result
        assert "DECIMAL" in result
        assert "(10,2)" in result

    def test_generate_column_definition_mock(self):
        """测试列定义生成"""
        manager = DatabaseTableManager()

        col_def = {"name": "id", "type": "INTEGER", "primary_key": True}

        result = manager._generate_column_definition(col_def)

        assert isinstance(result, str)
        assert len(result) > 0

    @patch("src.storage.database.database_manager.psycopg2.connect")
    def test_create_table_mock_only(self, mock_connect):
        """测试创建表（仅模拟）"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.execute.return_value = None
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        manager = DatabaseTableManager()

        columns = [
            {"name": "id", "type": "INTEGER"},
            {"name": "name", "type": "VARCHAR", "length": 100},
        ]

        result = manager.create_table(db_type=DatabaseType.POSTGRESQL, table_name="test_table", columns=columns)

        assert result is True
        mock_cursor.execute.assert_called()

    @patch("src.storage.database.database_manager.psycopg2.connect")
    def test_alter_table_mock_only(self, mock_connect):
        """测试修改表（仅模拟）"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.execute.return_value = None
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        manager = DatabaseTableManager()

        alteration = {
            "action": "ADD",
            "column": {"name": "new_col", "type": "VARCHAR", "length": 50},
        }

        result = manager.alter_table(
            db_type=DatabaseType.POSTGRESQL,
            table_name="test_table",
            alterations=[alteration],
        )

        assert result is True
        mock_cursor.execute.assert_called()

    @patch("src.storage.database.database_manager.psycopg2.connect")
    def test_drop_table_mock_only(self, mock_connect):
        """测试删除表（仅模拟）"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.execute.return_value = None
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        manager = DatabaseTableManager()

        result = manager.drop_table(db_type=DatabaseType.POSTGRESQL, table_name="test_table")

        assert result is True
        mock_cursor.execute.assert_called()

    @patch("src.storage.database.database_manager.psycopg2.connect")
    def test_validate_table_structure_mock_only(self, mock_connect):
        """测试表结构验证（仅模拟）"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [
            ("id", "integer", "NO"),
            ("name", "character varying", "YES"),
        ]
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        manager = DatabaseTableManager()

        expected_schema = [
            {"name": "id", "type": "INTEGER"},
            {"name": "name", "type": "VARCHAR"},
        ]

        result = manager.validate_table_structure(
            db_type=DatabaseType.POSTGRESQL,
            table_name="test_table",
            expected_schema=expected_schema,
        )

        assert result is True
        mock_cursor.execute.assert_called()

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="""
tables:
  - name: test_table
    type: table
    database: postgresql
    columns:
      - name: id
        type: INTEGER
      - name: name
        type: VARCHAR(100)
""",
    )
    @patch("src.storage.database.database_manager.psycopg2.connect")
    def test_batch_create_tables_mock_only(self, mock_connect):
        """测试批量创建表（仅模拟）"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.execute.return_value = None
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        manager = DatabaseTableManager()

        result = manager.batch_create_tables("test_config.yaml")

        assert isinstance(result, dict)
        assert "test_table" in result

    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_batch_create_tables_file_not_found_mock(self):
        """测试配置文件不存在（仅模拟）"""
        manager = DatabaseTableManager()

        result = manager.batch_create_tables("nonexistent.yaml")

        assert isinstance(result, dict)
        assert "error" in result

    @patch("src.storage.database.database_manager.psycopg2.connect")
    def test_get_table_info_mock_only(self, mock_connect):
        """测试获取表信息（仅模拟）"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [("test_table", "public", "r", "test_user", False, None)]
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        manager = DatabaseTableManager()

        result = manager.get_table_info(DatabaseType.POSTGRESQL, "test_table")

        assert isinstance(result, dict)
        assert "table_name" in result
        assert result["table_name"] == "test_table"

    def test_context_manager_enter_mock(self):
        """测试上下文管理器进入（仅模拟）"""
        manager = DatabaseTableManager()

        result = manager.__enter__()
        assert result == manager

    def test_context_manager_exit_success_mock(self):
        """测试上下文管理器成功退出（仅模拟）"""
        manager = DatabaseTableManager()
        mock_conn = Mock()
        manager.connections = {"test_db": mock_conn}

        manager.__enter__()
        manager.__exit__(None, None, None)

        mock_conn.close.assert_called_once()

    def test_context_manager_exit_with_exception_mock(self):
        """测试上下文管理器异常退出（仅模拟）"""
        manager = DatabaseTableManager()
        mock_conn = Mock()
        manager.connections = {"test_db": mock_conn}

        manager.__enter__()
        manager.__exit__(Exception("Test"), None, None)

        mock_conn.close.assert_called_once()


class TestDatabaseManagerEdgeCases:
    """边界情况测试"""

    def setup_method(self):
        """测试前准备"""
        with patch("src.storage.database.database_manager.load_dotenv"):
            self.manager = DatabaseTableManager()

    def test_create_table_empty_columns(self):
        """测试空列列表"""
        with patch("src.storage.database.database_manager.psycopg2.connect") as mock_connect:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_cursor.execute.return_value = None
            mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
            mock_connect.return_value = mock_conn

            result = self.manager.create_table(db_type=DatabaseType.POSTGRESQL, table_name="test_table", columns=[])

            # 空列列表应该返回False
            assert result is False

    def test_validate_table_structure_mismatch(self):
        """测试表结构不匹配"""
        with patch("src.storage.database.database_manager.psycopg2.connect") as mock_connect:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_cursor.fetchall.return_value = [("id", "integer", "NO")]
            mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
            mock_connect.return_value = mock_conn

            expected_schema = [
                {"name": "id", "type": "INTEGER"},
                {"name": "missing_col", "type": "VARCHAR"},
            ]

            result = self.manager.validate_table_structure(
                db_type=DatabaseType.POSTGRESQL,
                table_name="test_table",
                expected_schema=expected_schema,
            )

            assert result is False


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])
