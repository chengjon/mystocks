"""
Data Access Module Test Suite (Mock-based)
数据访问模块测试套件 - 基于Mock

测试模块: src.data_access (500行)
创建日期: 2025-12-28
版本: 1.0.0
"""

import pytest
import pandas as pd
from unittest.mock import Mock, MagicMock, patch
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))


class TestDataAccessModuleStructure:
    """测试data_access模块结构"""

    @patch("src.storage.database.connection_manager.get_connection_manager")
    @patch("src.core.data_manager.DataManager")
    def test_module_imports(self, mock_data_manager, mock_conn_manager):
        """测试模块可以正常导入"""
        mock_conn_manager.return_value = MagicMock()
        from src.data_access import TDengineDataAccess, PostgreSQLDataAccess

        assert TDengineDataAccess is not None
        assert PostgreSQLDataAccess is not None


class TestTDengineDataAccessWithMock:
    """测试TDengine数据访问层（使用Mock）"""

    @pytest.fixture
    def mock_conn_manager(self):
        """Mock连接管理器"""
        return MagicMock()

    @pytest.fixture
    def tdengine_access(self, mock_conn_manager):
        """创建TDengine访问层实例（Mock版本）"""
        with patch("src.storage.database.connection_manager.get_connection_manager", return_value=mock_conn_manager):
            from src.data_access import TDengineDataAccess

            return TDengineDataAccess()

    def test_initialization(self, tdengine_access):
        """测试初始化"""
        assert tdengine_access is not None
        assert hasattr(tdengine_access, "_get_connection")

    def test_create_stable(self, tdengine_access, mock_conn_manager):
        """测试创建超表"""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_conn_manager.get_tdengine_connection.return_value = mock_connection

        tdengine_access.create_stable("test_stable", {"ts": "TIMESTAMP", "price": "FLOAT"}, {"symbol": "BINARY(20)"})

        mock_cursor.execute.assert_called_once()

    def test_insert_dataframe(self, tdengine_access, mock_conn_manager):
        """测试插入DataFrame"""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_conn_manager.get_tdengine_connection.return_value = mock_connection

        data = pd.DataFrame(
            {
                "ts": pd.date_range("2024-01-01", periods=3, freq="min"),
                "symbol": ["600000.SH", "600000.SH", "600000.SH"],
                "price": [10.0, 10.1, 10.2],
                "volume": [1000, 1100, 1200],
            }
        )

        tdengine_access.insert_dataframe("test_table", data)

        assert mock_cursor.execute.called


class TestPostgreSQLDataAccessWithMock:
    """测试PostgreSQL数据访问层（使用Mock）"""

    @pytest.fixture
    def mock_conn_manager(self):
        """Mock连接管理器"""
        return MagicMock()

    @pytest.fixture
    def postgresql_access(self, mock_conn_manager):
        """创建PostgreSQL访问层实例（Mock版本）"""
        with patch("src.storage.database.connection_manager.get_connection_manager", return_value=mock_conn_manager):
            from src.data_access import PostgreSQLDataAccess

            return PostgreSQLDataAccess()

    def test_initialization(self, postgresql_access):
        """测试初始化"""
        assert postgresql_access is not None
        assert hasattr(postgresql_access, "_get_connection")

    def test_create_table(self, postgresql_access, mock_conn_manager):
        """测试创建表"""
        mock_pool = MagicMock()
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_pool.getconn.return_value = mock_connection
        mock_conn_manager.get_postgresql_connection.return_value = mock_pool

        postgresql_access.create_table(
            "test_table",
            {"symbol": "VARCHAR(20)", "date": "DATE", "close": "DECIMAL(10,2)"},
            primary_key="symbol, date",
        )

        mock_cursor.execute.assert_called_once()

    def test_insert_dataframe(self, postgresql_access, mock_conn_manager):
        """测试插入DataFrame"""
        mock_pool = MagicMock()
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_pool.getconn.return_value = mock_connection
        mock_conn_manager.get_postgresql_connection.return_value = mock_pool

        data = pd.DataFrame(
            {
                "symbol": ["600000.SH", "600001.SH"],
                "date": pd.date_range("2024-01-01", periods=2),
                "close": [10.0, 20.0],
            }
        )

        postgresql_access.insert_dataframe("test_table", data)

        assert mock_cursor.execute.called


class TestDataClassificationRouting:
    """测试数据分类路由"""

    @patch("src.storage.database.connection_manager.get_connection_manager")
    @patch("src.core.data_manager.DataManager")
    def test_timeseries_data_routes_to_tdengine(self, mock_data_manager, mock_conn_manager):
        """测试时序数据路由到TDengine"""
        mock_conn_manager.return_value = MagicMock()
        from src.core import DataClassification, DatabaseTarget

        from src.core.data_manager import DataManager

        dm = DataManager(enable_monitoring=False)

        target = dm.get_target_database(DataClassification.TICK_DATA)
        assert target == DatabaseTarget.TDENGINE

        target = dm.get_target_database(DataClassification.MINUTE_KLINE)
        assert target == DatabaseTarget.TDENGINE

    @patch("src.storage.database.connection_manager.get_connection_manager")
    @patch("src.core.data_manager.DataManager")
    def test_relational_data_routes_to_postgresql(self, mock_data_manager, mock_conn_manager):
        """测试关系数据路由到PostgreSQL"""
        mock_conn_manager.return_value = MagicMock()
        from src.core import DataClassification, DatabaseTarget

        from src.core.data_manager import DataManager

        dm = DataManager(enable_monitoring=False)

        target = dm.get_target_database(DataClassification.DAILY_KLINE)
        assert target == DatabaseTarget.POSTGRESQL

        target = dm.get_target_database(DataClassification.STOCK_BASIC_INFO)
        assert target == DatabaseTarget.POSTGRESQL


class TestDataAccessIntegration:
    """测试数据访问集成"""

    @patch("src.storage.database.connection_manager.get_connection_manager")
    @patch("src.core.data_manager.DataManager")
    def test_tdengine_and_postgresql_access(self, mock_data_manager, mock_conn_manager):
        """测试同时访问TDengine和PostgreSQL"""
        mock_conn_manager.return_value = MagicMock()

        from src.data_access import TDengineDataAccess, PostgreSQLDataAccess

        td_access = TDengineDataAccess()
        pg_access = PostgreSQLDataAccess()

        assert td_access is not None
        assert pg_access is not None

        # 验证它们是不同的实例
        assert td_access is not pg_access
