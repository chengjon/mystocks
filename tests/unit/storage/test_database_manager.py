"""
Storage Database Manager Test Suite (Mock-based)
存储数据库管理器测试套件

测试模块: src.storage.database.database_manager
创建日期: 2025-12-28
版本: 2.0.0
"""

import os
import sys
from unittest.mock import MagicMock, patch

import pytest

# 确保 src 目录在 path 中
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from src.storage.database.database_manager import DatabaseTableManager, DatabaseType, TableOperationLog


class TestDatabaseTableManager:
    """测试数据库表管理器"""

    @pytest.fixture
    def db_manager(self):
        """创建数据库管理器实例，Mock 掉监控引擎初始化"""
        with (
            patch("src.storage.database.database_manager.create_engine"),
            patch("src.storage.database.database_manager.sessionmaker"),
        ):
            return DatabaseTableManager()

    def test_initialization(self, db_manager):
        """测试初始化"""
        assert db_manager is not None
        assert hasattr(db_manager, "get_tdengine_connection")
        assert hasattr(db_manager, "get_postgresql_connection")

    def test_get_connection(self, db_manager):
        """测试获取连接"""
        mock_connection = MagicMock()
        db_manager.db_connections["TDengine_test_db"] = mock_connection

        result = db_manager.get_connection(DatabaseType.TDENGINE, "test_db")
        assert result == mock_connection

    def test_database_type_enum(self):
        """测试数据库类型枚举"""
        assert DatabaseType.POSTGRESQL.value == "PostgreSQL"
        assert DatabaseType.TDENGINE.value == "TDengine"

    def test_monitoring_log_enum_uses_non_native_type(self):
        """监控日志枚举不应触发 PostgreSQL 原生 Enum"""
        operation_type = TableOperationLog.__table__.c.operation_type.type
        operation_status = TableOperationLog.__table__.c.operation_status.type
        assert operation_type.native_enum is False
        assert operation_status.native_enum is False


class TestDatabaseManagerQueryOperations:
    """测试数据库管理器查询操作"""

    @pytest.fixture
    def db_manager(self):
        """创建数据库管理器实例"""
        with (
            patch("src.storage.database.database_manager.create_engine"),
            patch("src.storage.database.database_manager.sessionmaker"),
        ):
            return DatabaseTableManager()

    def test_validate_table_structure(self, db_manager):
        """测试表结构验证"""
        schema = [
            {"name": "ts", "type": "TIMESTAMP"},
            {"name": "symbol", "type": "BINARY", "length": 20},
            {"name": "price", "type": "FLOAT"},
        ]

        # Mock get_table_info to return matching structure
        with patch.object(db_manager, "get_table_info") as mock_get_info:
            mock_get_info.return_value = {
                "table_name": "test_table",
                "columns": [
                    {"name": "ts", "type": "TIMESTAMP", "nullable": True},
                    {"name": "symbol", "type": "BINARY", "length": 20, "nullable": True},
                    {"name": "price", "type": "FLOAT", "nullable": True},
                ],
            }
            # Mock monitor session
            db_manager.monitor_session = MagicMock()

            result = db_manager.validate_table_structure(DatabaseType.TDENGINE, "test_db", "test_table", schema)
            assert isinstance(result, dict)
            assert result["matches"] is True

    def test_get_table_info(self, db_manager):
        """测试获取表信息"""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        # Mock TDengine DESCRIBE result
        mock_cursor.fetchall.return_value = [
            ("ts", "TIMESTAMP", 8, "PRESET", "YES"),
            ("symbol", "BINARY", 20, "PRESET", "YES"),
            ("price", "FLOAT", 4, "PRESET", "YES"),
        ]
        mock_connection.cursor.return_value = mock_cursor

        with patch.object(db_manager, "get_connection", return_value=mock_connection):
            info = db_manager.get_table_info(DatabaseType.TDENGINE, "test_db", "test_table")
            assert info is not None
            assert info["table_name"] == "test_table"
            assert len(info["columns"]) == 3


class TestDatabaseManagerDDL:
    """测试数据库管理器DDL操作"""

    @pytest.fixture
    def db_manager(self):
        """创建数据库管理器实例"""
        with (
            patch("src.storage.database.database_manager.create_engine"),
            patch("src.storage.database.database_manager.sessionmaker"),
        ):
            return DatabaseTableManager()

    def test_generate_postgresql_ddl(self, db_manager):
        """测试生成PostgreSQL DDL"""
        schema = [
            {"name": "symbol", "type": "VARCHAR", "length": 20},
            {"name": "date", "type": "DATE"},
            {"name": "close", "type": "DECIMAL", "precision": 10, "scale": 2},
        ]

        ddl = db_manager._generate_postgresql_ddl("test_table", schema)
        assert "CREATE TABLE IF NOT EXISTS test_table" in ddl
        assert "symbol VARCHAR(20)" in ddl
        assert "date DATE" in ddl
        assert "close DECIMAL(10, 2)" in ddl

    def test_generate_tdengine_ddl(self, db_manager):
        """测试生成TDengine DDL"""
        schema = [{"name": "ts", "type": "TIMESTAMP"}, {"name": "price", "type": "FLOAT"}]
        tags = [{"name": "symbol", "type": "BINARY", "length": 20}]

        ddl = db_manager._generate_tdengine_ddl("test_stable", schema, tags, is_super_table=True)
        assert "CREATE STABLE IF NOT EXISTS test_stable" in ddl
        assert "TAGS (symbol BINARY(20))" in ddl



class TestDatabaseManagerUtilities:
    """测试数据库管理器工具方法"""

    @pytest.fixture
    def db_manager(self):
        """创建数据库管理器实例"""
        with (
            patch("src.storage.database.database_manager.create_engine"),
            patch("src.storage.database.database_manager.sessionmaker"),
        ):
            return DatabaseTableManager()

    def test_close_connections(self, db_manager):
        """测试关闭连接"""
        mock_conn = MagicMock()
        db_manager.db_connections["test_conn"] = mock_conn
        db_manager.monitor_session = MagicMock()

        db_manager.close()

        assert mock_conn.close.called
        assert db_manager.monitor_session.close.called
