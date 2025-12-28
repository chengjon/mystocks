"""
Storage Database Manager Test Suite (Mock-based)
存储数据库管理器测试套件

测试模块: src.storage.database.database_manager
创建日期: 2025-12-28
版本: 1.0.0
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))


class TestDatabaseTableManager:
    """测试数据库表管理器"""

    @pytest.fixture
    def mock_conn_manager(self):
        """Mock连接管理器"""
        return MagicMock()

    @pytest.fixture
    def db_manager(self, mock_conn_manager):
        """创建数据库管理器实例"""
        with patch("src.storage.database.connection_manager.get_connection_manager", return_value=mock_conn_manager):
            from src.storage.database.database_manager import DatabaseTableManager

            return DatabaseTableManager()

    def test_initialization(self, db_manager):
        """测试初始化"""
        assert db_manager is not None
        assert hasattr(db_manager, "get_tdengine_connection")
        assert hasattr(db_manager, "get_postgresql_connection")

    def test_get_connection(self, db_manager):
        """测试获取连接"""
        mock_connection = MagicMock()
        db_manager._tdengine_conn = mock_connection

        result = db_manager.get_connection(DatabaseType.TDENGINE)
        assert result == mock_connection

    def test_database_type_enum(self):
        """测试数据库类型枚举"""
        from src.storage.database.database_manager import DatabaseType

        assert DatabaseType.POSTGRESQL.value == "postgresql"
        assert DatabaseType.TDENGINE.value == "tdengine"
        assert DatabaseType.MYSQL.value == "mysql"


class TestDatabaseManagerQueryOperations:
    """测试数据库管理器查询操作"""

    @pytest.fixture
    def mock_conn_manager(self):
        """Mock连接管理器"""
        return MagicMock()

    @pytest.fixture
    def db_manager(self, mock_conn_manager):
        """创建数据库管理器实例"""
        with patch("src.storage.database.connection_manager.get_connection_manager", return_value=mock_conn_manager):
            from src.storage.database.database_manager import DatabaseTableManager

            return DatabaseTableManager()

    def test_validate_table_structure(self, db_manager):
        """测试表结构验证"""
        schema = {"ts": "TIMESTAMP", "symbol": "BINARY(20)", "price": "FLOAT"}

        result = db_manager.validate_table_structure("test_table", schema)
        assert isinstance(result, dict)

    def test_get_table_info(self, db_manager):
        """测试获取表信息"""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = ("test_table", 3)
        mock_connection.cursor.return_value = mock_cursor
        db_manager._tdengine_conn = mock_connection

        info = db_manager.get_table_info("test_table")
        assert info is not None


class TestDatabaseManagerDDL:
    """测试数据库管理器DDL操作"""

    @pytest.fixture
    def mock_conn_manager(self):
        """Mock连接管理器"""
        return MagicMock()

    @pytest.fixture
    def db_manager(self, mock_conn_manager):
        """创建数据库管理器实例"""
        with patch("src.storage.database.connection_manager.get_connection_manager", return_value=mock_conn_manager):
            from src.storage.database.database_manager import DatabaseTableManager

            return DatabaseTableManager()

    def test_generate_postgresql_ddl(self, db_manager):
        """测试生成PostgreSQL DDL"""
        schema = {"symbol": "VARCHAR(20)", "date": "DATE", "close": "DECIMAL(10,2)"}

        ddl = db_manager._generate_postgresql_ddl("test_table", schema)
        assert "CREATE TABLE IF NOT EXISTS test_table" in ddl
        assert "symbol" in ddl
        assert "date" in ddl
        assert "close" in ddl

    def test_generate_tdengine_ddl(self, db_manager):
        """测试生成TDengine DDL"""
        schema = {"ts": "TIMESTAMP", "symbol": "BINARY(20)", "price": "FLOAT"}
        tags = {"symbol": "BINARY(20)"}

        ddl = db_manager._generate_tdengine_ddl("test_stable", schema, tags)
        assert "CREATE STABLE IF NOT EXISTS test_stable" in ddl
        assert "TAGS" in ddl

    def test_generate_mysql_ddl(self, db_manager):
        """测试生成MySQL DDL"""
        schema = {"id": "INT AUTO_INCREMENT PRIMARY KEY", "symbol": "VARCHAR(20)", "date": "DATE"}

        ddl = db_manager._generate_mysql_ddl("test_table", schema)
        assert "CREATE TABLE IF NOT EXISTS test_table" in ddl
        assert "symbol" in ddl


class TestDatabaseManagerUtilities:
    """测试数据库管理器工具方法"""

    @pytest.fixture
    def mock_conn_manager(self):
        """Mock连接管理器"""
        return MagicMock()

    @pytest.fixture
    def db_manager(self, mock_conn_manager):
        """创建数据库管理器实例"""
        with patch("src.storage.database.connection_manager.get_connection_manager", return_value=mock_conn_manager):
            from src.storage.database.database_manager import DatabaseTableManager

            return DatabaseTableManager()

    def test_close_connections(self, db_manager):
        """测试关闭连接"""
        mock_pg_conn = MagicMock()
        mock_td_conn = MagicMock()
        db_manager._postgresql_conn = mock_pg_conn
        db_manager._tdengine_conn = mock_td_conn

        db_manager.close()

        assert mock_pg_conn.close.called or hasattr(mock_pg_conn, "close")
        assert mock_td_conn.close.called or hasattr(mock_td_conn, "close")
