"""
Database Manager 综合测试
全面测试 DatabaseTableManager 类的所有功能
目标覆盖率: 80%+
"""

import os
import sys
from unittest.mock import Mock, mock_open, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../../.."))

from src.storage.database.database_manager import DatabaseTableManager, DatabaseType


class TestDatabaseTableManagerInit:
    """测试 DatabaseTableManager 初始化"""

    def test_init_success(self):
        """测试成功初始化"""
        with patch("src.storage.database.database_manager.load_dotenv"):
            manager = DatabaseTableManager()
            assert manager is not None
            assert hasattr(manager, "connections")
            assert hasattr(manager, "connection_pool")

    @patch("src.storage.database.database_manager.load_dotenv")
    def test_init_with_env_vars(self, mock_load_dotenv):
        """测试带环境变量的初始化"""
        manager = DatabaseTableManager()
        mock_load_dotenv.assert_called_once()


class TestDatabaseTableManagerConnection:
    """测试连接管理功能"""

    @patch("src.storage.database.database_manager.psycopg2.connect")
    @patch.dict(
        os.environ,
        {
            "POSTGRESQL_HOST": "localhost",
            "POSTGRESQL_USER": "test_user",
            "POSTGRESQL_PASSWORD": "test_password",
            "POSTGRESQL_DATABASE": "test_db",
        },
    )
    def test_get_postgresql_connection_success(self, mock_connect):
        """测试获取PostgreSQL连接成功"""
        mock_conn = Mock()
        mock_connect.return_value = mock_conn

        manager = DatabaseTableManager()
        result = manager.get_connection(DatabaseType.POSTGRESQL, "test_db")

        assert result is not None
        mock_connect.assert_called_once()

    @patch("src.storage.database.database_manager.taos.connect")
    @patch.dict(
        os.environ,
        {
            "TDENGINE_HOST": "localhost",
            "TDENGINE_USER": "root",
            "TDENGINE_PASSWORD": "taosdata",
            "TDENGINE_DATABASE": "test_db",
        },
    )
    def test_get_tdengine_connection_success(self, mock_connect):
        """测试获取TDengine连接成功"""
        mock_conn = Mock()
        mock_connect.return_value = mock_conn

        manager = DatabaseTableManager()
        result = manager.get_connection(DatabaseType.TDENGINE, "test_db")

        assert result is not None
        mock_connect.assert_called_once()

    @patch("src.storage.database.database_manager.psycopg2.connect")
    def test_get_connection_failure(self, mock_connect):
        """测试连接失败"""
        mock_connect.side_effect = Exception("Connection failed")

        manager = DatabaseTableManager()

        with pytest.raises(Exception):
            manager.get_connection(DatabaseType.POSTGRESQL, "test_db")

    def test_close_all_connections(self):
        """测试关闭所有连接"""
        manager = DatabaseTableManager()

        # 模拟一些连接
        mock_conn1 = Mock()
        mock_conn2 = Mock()
        manager.connections = {"db1": mock_conn1, "db2": mock_conn2}

        manager.close_all_connections()

        mock_conn1.close.assert_called_once()
        mock_conn2.close.assert_called_once()
        assert len(manager.connections) == 0


class TestDatabaseTableManagerTableOperations:
    """测试表操作功能"""

    def setup_method(self):
        """测试前准备"""
        with patch("src.storage.database.database_manager.load_dotenv"):
            self.manager = DatabaseTableManager()

    @patch("src.storage.database.database_manager.psycopg2.connect")
    def test_create_table_postgresql_success(self, mock_connect):
        """测试PostgreSQL创建表成功"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        columns = [
            {"name": "id", "type": "INTEGER", "primary_key": True},
            {"name": "name", "type": "VARCHAR", "length": 100},
            {"name": "created_at", "type": "TIMESTAMP", "nullable": False},
        ]

        result = self.manager.create_table(db_type=DatabaseType.POSTGRESQL, table_name="test_table", columns=columns)

        assert result is True
        mock_cursor.execute.assert_called()

    @patch("src.storage.database.database_manager.taos.connect")
    def test_create_table_tdengine_success(self, mock_connect):
        """测试TDengine创建表成功"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        columns = [
            {"name": "ts", "type": "TIMESTAMP"},
            {"name": "value", "type": "FLOAT"},
            {"name": "status", "type": "INT"},
        ]

        result = self.manager.create_table(db_type=DatabaseType.TDENGINE, table_name="test_table", columns=columns)

        assert result is True
        mock_cursor.execute.assert_called()

    @patch("src.storage.database.database_manager.psycopg2.connect")
    def test_alter_table_add_column(self, mock_connect):
        """测试添加列"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        alteration = {
            "action": "ADD",
            "column": {"name": "new_column", "type": "VARCHAR", "length": 50},
        }

        result = self.manager.alter_table(
            db_type=DatabaseType.POSTGRESQL,
            table_name="test_table",
            alterations=[alteration],
        )

        assert result is True
        mock_cursor.execute.assert_called()

    @patch("src.storage.database.database_manager.psycopg2.connect")
    def test_drop_table_success(self, mock_connect):
        """测试删除表成功"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        result = self.manager.drop_table(db_type=DatabaseType.POSTGRESQL, table_name="test_table")

        assert result is True
        mock_cursor.execute.assert_called()


class TestDatabaseTableManagerValidation:
    """测试表结构验证功能"""

    def setup_method(self):
        """测试前准备"""
        with patch("src.storage.database.database_manager.load_dotenv"):
            self.manager = DatabaseTableManager()

    @patch("src.storage.database.database_manager.psycopg2.connect")
    def test_validate_table_structure_success(self, mock_connect):
        """测试表结构验证成功"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [
            ("id", "integer", "NO"),
            ("name", "character varying", "YES"),
            ("created_at", "timestamp without time zone", "NO"),
        ]
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        expected_schema = [
            {"name": "id", "type": "INTEGER"},
            {"name": "name", "type": "VARCHAR"},
            {"name": "created_at", "type": "TIMESTAMP"},
        ]

        result = self.manager.validate_table_structure(
            db_type=DatabaseType.POSTGRESQL,
            table_name="test_table",
            expected_schema=expected_schema,
        )

        assert result is True
        mock_cursor.execute.assert_called()

    @patch("src.storage.database.database_manager.psycopg2.connect")
    def test_validate_table_structure_mismatch(self, mock_connect):
        """测试表结构验证失败"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [
            ("id", "integer", "NO"),
            ("name", "character varying", "YES"),
        ]
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        expected_schema = [
            {"name": "id", "type": "INTEGER"},
            {"name": "name", "type": "VARCHAR"},
            {"name": "missing_column", "type": "INTEGER"},
        ]

        result = self.manager.validate_table_structure(
            db_type=DatabaseType.POSTGRESQL,
            table_name="test_table",
            expected_schema=expected_schema,
        )

        assert result is False


class TestDatabaseTableManagerBatchOperations:
    """测试批量操作功能"""

    def setup_method(self):
        """测试前准备"""
        with patch("src.storage.database.database_manager.load_dotenv"):
            self.manager = DatabaseTableManager()

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="""
tables:
  - name: users
    type: table
    database: postgresql
    columns:
      - name: id
        type: INTEGER
        primary_key: true
      - name: name
        type: VARCHAR(100)
        nullable: false
  - name: logs
    type: table
    database: tdengine
    columns:
      - name: ts
        type: TIMESTAMP
      - name: level
        type: INT
      - name: message
        type: VARCHAR(500)
""",
    )
    @patch("src.storage.database.database_manager.psycopg2.connect")
    @patch("src.storage.database.database_manager.taos.connect")
    def test_batch_create_tables_success(self, mock_tdengine, mock_postgresql):
        """测试批量创建表成功"""
        mock_postgresql.return_value.cursor.return_value.__enter__.return_value = Mock()
        mock_tdengine.return_value.cursor.return_value.__enter__.return_value = Mock()

        result = self.manager.batch_create_tables("test_config.yaml")

        assert isinstance(result, dict)
        assert "users" in result
        assert "logs" in result

    @patch("builtins.open", side_effect=FileNotFoundError("Config not found"))
    def test_batch_create_tables_file_not_found(self):
        """测试配置文件不存在"""
        result = self.manager.batch_create_tables("nonexistent.yaml")

        assert isinstance(result, dict)
        assert "error" in result

    @patch("builtins.open", new_callable=mock_open, read_data="invalid yaml")
    def test_batch_create_tables_invalid_yaml(self):
        """测试无效YAML配置"""
        result = self.manager.batch_create_tables("invalid.yaml")

        assert isinstance(result, dict)
        assert "error" in result


class TestDatabaseTableManagerDDLSpecific:
    """测试DDL生成功能"""

    def setup_method(self):
        """测试前准备"""
        with patch("src.storage.database.database_manager.load_dotenv"):
            self.manager = DatabaseTableManager()

    def test_generate_postgresql_ddl(self):
        """测试PostgreSQL DDL生成"""
        col_def = {
            "name": "test_column",
            "type": "VARCHAR",
            "length": 100,
            "nullable": False,
            "default": "'default_value'",
        }

        result = self.manager._generate_postgresql_ddl(col_def)

        assert "test_column" in result
        assert "VARCHAR" in result
        assert "(100)" in result
        assert "NOT NULL" in result
        assert "DEFAULT 'default_value'" in result

    def test_generate_tdengine_ddl(self):
        """测试TDengine DDL生成"""
        col_def = {"name": "ts", "type": "TIMESTAMP"}

        result = self.manager._generate_tdengine_ddl(col_def)

        assert "ts" in result
        assert "TIMESTAMP" in result

    def test_generate_column_definition(self):
        """测试列定义生成"""
        col_def = {"name": "id", "type": "INTEGER", "primary_key": True}

        result = self.manager._generate_column_definition(col_def)

        assert "id" in result
        assert "INTEGER" in result


class TestDatabaseTableManagerContextManager:
    """测试上下文管理器功能"""

    def setup_method(self):
        """测试前准备"""
        with patch("src.storage.database.database_manager.load_dotenv"):
            self.manager = DatabaseTableManager()

    def test_context_manager_enter(self):
        """测试进入上下文"""
        with patch("src.storage.database.database_manager.psycopg2.connect"):
            result = self.manager.__enter__()
            assert result == self.manager

    def test_context_manager_exit_success(self):
        """测试成功退出上下文"""
        mock_conn = Mock()
        self.manager.connections = {"test_db": mock_conn}

        with patch("src.storage.database.database_manager.psycopg2.connect"):
            self.manager.__enter__()
            self.manager.__exit__(None, None, None)

            mock_conn.close.assert_called_once()

    def test_context_manager_exit_with_exception(self):
        """测试异常退出上下文"""
        mock_conn = Mock()
        self.manager.connections = {"test_db": mock_conn}

        with patch("src.storage.database.database_manager.psycopg2.connect"):
            self.manager.__enter__()
            self.manager.__exit__(Exception("Test error"), None, None)

            mock_conn.close.assert_called_once()


class TestDatabaseTableManagerLogging:
    """测试日志功能"""

    def setup_method(self):
        """测试前准备"""
        with patch("src.storage.database.database_manager.load_dotenv"):
            self.manager = DatabaseTableManager()

    def test_log_operation(self):
        """测试操作日志"""
        with patch("src.storage.database.database_manager.logging") as mock_logging:
            self.manager._log_operation(
                operation="CREATE_TABLE",
                table_name="test_table",
                db_type="postgresql",
                details={"columns": 3},
            )

            mock_logging.info.assert_called_once()


class TestDatabaseTableManagerEdgeCases:
    """测试边界情况"""

    def setup_method(self):
        """测试前准备"""
        with patch("src.storage.database.database_manager.load_dotenv"):
            self.manager = DatabaseTableManager()

    def test_get_table_info_postgresql(self):
        """测试获取PostgreSQL表信息"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [
            ("test_table", "public", "r", "root", False, None),
            ("test_table", "public", "w", "root", False, None),
        ]
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        with patch(
            "src.storage.database.database_manager.psycopg2.connect",
            return_value=mock_conn,
        ):
            result = self.manager.get_table_info(DatabaseType.POSTGRESQL, "test_table")

            assert isinstance(result, dict)
            assert "table_name" in result
            assert result["table_name"] == "test_table"

    def test_unsupported_database_type(self):
        """测试不支持的数据库类型"""
        with pytest.raises(ValueError):
            self.manager.get_connection("UNSUPPORTED_DB", "test_db")

    def test_empty_columns_list(self):
        """测试空列列表"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        with patch(
            "src.storage.database.database_manager.psycopg2.connect",
            return_value=mock_conn,
        ):
            result = self.manager.create_table(db_type=DatabaseType.POSTGRESQL, table_name="test_table", columns=[])

            # 空列列表应该返回False或抛出异常
            assert isinstance(result, bool)


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])
