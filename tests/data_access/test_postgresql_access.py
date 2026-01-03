"""
PostgreSQL数据访问层测试

测试PostgreSQLDataAccess类的所有功能：
- 连接池管理
- 表和超表创建
- 数据插入和upsert
- 复杂查询
- 数据删除
- 表统计信息

创建日期: 2026-01-03
Phase: 2 - Task 2.1.2
"""

import unittest
from unittest.mock import Mock, MagicMock, patch, call
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from src.data_access.postgresql_access import PostgreSQLDataAccess


class TestPostgreSQLDataAccessInit(unittest.TestCase):
    """测试PostgreSQLDataAccess初始化"""

    def test_init_with_db_manager(self):
        """测试使用db_manager初始化"""
        mock_db_manager = Mock()
        mock_monitoring_db = Mock()

        access = PostgreSQLDataAccess(db_manager=mock_db_manager, monitoring_db=mock_monitoring_db)

        self.assertIsNotNone(access)
        self.assertEqual(access.db_manager, mock_db_manager)
        self.assertEqual(access.monitoring_db, mock_monitoring_db)

    def test_init_without_db_manager(self):
        """测试不使用db_manager初始化"""
        access = PostgreSQLDataAccess()

        self.assertIsNotNone(access)
        self.assertIsNotNone(access.db_manager)


class TestPostgreSQLDataAccessConnection(unittest.TestCase):
    """测试连接管理功能"""

    def setUp(self):
        """测试前准备"""
        self.mock_db_manager = Mock()
        self.mock_pool = Mock()
        self.mock_connection = Mock()
        self.mock_db_manager.get_postgresql_pool.return_value = self.mock_pool
        self.mock_pool.connection.return_value.__enter__ = Mock(return_value=self.mock_connection)
        self.mock_pool.connection.return_value.__exit__ = Mock(return_value=False)
        self.access = PostgreSQLDataAccess(db_manager=self.mock_db_manager)

    def test_check_connection_success(self):
        """测试检查连接成功"""
        self.mock_connection.execute.return_value = Mock(rowcount=1)

        result = self.access.check_connection()

        self.assertTrue(result)

    def test_check_connection_failure(self):
        """测试检查连接失败"""
        self.mock_connection.execute.side_effect = Exception("Connection error")

        result = self.access.check_connection()

        self.assertFalse(result)

    def test_get_pool(self):
        """测试获取连接池"""
        pool = self.access._get_pool()

        self.assertEqual(pool, self.mock_pool)


class TestPostgreSQLDataAccessTableCreation(unittest.TestCase):
    """测试表创建功能"""

    def setUp(self):
        """测试前准备"""
        self.mock_db_manager = Mock()
        self.mock_connection = Mock()
        self.mock_pool = Mock()
        self.mock_pool.connection.return_value.__enter__ = Mock(return_value=self.mock_connection)
        self.mock_pool.connection.return_value.__exit__ = Mock(return_value=False)
        self.mock_db_manager.get_postgresql_pool.return_value = self.mock_pool
        self.access = PostgreSQLDataAccess(db_manager=self.mock_db_manager)

    def test_create_table_basic(self):
        """测试创建基本表"""
        table_name = "test_table"
        schema = {
            "id": "SERIAL PRIMARY KEY",
            "name": "VARCHAR(100)",
            "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
        }

        result = self.access.create_table(table_name, schema)

        self.assertTrue(result)
        self.mock_connection.execute.assert_called()

    def test_create_hypertable(self):
        """测试创建超表"""
        table_name = "test_table"
        time_column = "time"
        chunk_interval = "7 days"

        result = self.access.create_hypertable(table_name, time_column, chunk_interval)

        self.assertTrue(result)


class TestPostgreSQLDataAccessDataInsertion(unittest.TestCase):
    """测试数据插入功能"""

    def setUp(self):
        """测试前准备"""
        self.mock_db_manager = Mock()
        self.mock_connection = Mock()
        self.mock_pool = Mock()
        self.mock_pool.connection.return_value.__enter__ = Mock(return_value=self.mock_connection)
        self.mock_pool.connection.return_value.__exit__ = Mock(return_value=False)
        self.mock_db_manager.get_postgresql_pool.return_value = self.mock_pool
        self.mock_cursor = Mock()
        self.mock_connection.cursor.return_value = self.mock_cursor
        self.access = PostgreSQLDataAccess(db_manager=self.mock_db_manager)

        # 创建测试数据
        self.test_data = pd.DataFrame(
            {"id": range(1, 101), "name": [f"item_{i}" for i in range(100)], "value": np.random.randn(100) * 100}
        )

    def test_insert_dataframe_basic(self):
        """测试基本DataFrame插入"""
        table_name = "test_table"

        result = self.access.insert_dataframe(table_name, self.test_data)

        self.assertEqual(result, 100)
        self.mock_cursor.executemany.assert_called_once()

    def test_insert_dataframe_empty(self):
        """测试插入空DataFrame"""
        table_name = "test_table"
        empty_df = pd.DataFrame()

        result = self.access.insert_dataframe(table_name, empty_df)

        self.assertEqual(result, 0)

    @patch("src.data_access.postgresql_access.pd.read_sql")
    def test_upsert_dataframe(self, mock_read_sql):
        """测试upsert操作"""
        table_name = "test_table"
        conflict_columns = ["id"]

        result = self.access.upsert_dataframe(table_name, self.test_data, conflict_columns)

        self.assertTrue(result)
        self.mock_connection.execute.assert_called()


class TestPostgreSQLDataAccessQuery(unittest.TestCase):
    """测试查询功能"""

    def setUp(self):
        """测试前准备"""
        self.mock_db_manager = Mock()
        self.mock_connection = Mock()
        self.mock_pool = Mock()
        self.mock_pool.connection.return_value.__enter__ = Mock(return_value=self.mock_connection)
        self.mock_pool.connection.return_value.__exit__ = Mock(return_value=False)
        self.mock_db_manager.get_postgresql_pool.return_value = self.mock_pool

        # 模拟查询结果
        self.mock_result = pd.DataFrame(
            {"id": [1, 2, 3], "name": ["item_1", "item_2", "item_3"], "value": [100.0, 200.0, 300.0]}
        )

        self.access = PostgreSQLDataAccess(db_manager=self.mock_db_manager)

    @patch("src.data_access.postgresql_access.pd.read_sql")
    def test_query_basic(self, mock_read_sql):
        """测试基本查询"""
        mock_read_sql.return_value = self.mock_result

        table_name = "test_table"
        columns = ["id", "name", "value"]

        result = self.access.query(table_name, columns=columns)

        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 3)

    @patch("src.data_access.postgresql_access.pd.read_sql")
    def test_query_by_time_range(self, mock_read_sql):
        """测试时间范围查询"""
        mock_read_sql.return_value = self.mock_result

        table_name = "test_table"
        start_time = datetime(2025, 1, 1)
        end_time = datetime(2025, 1, 31)

        result = self.access.query_by_time_range(table_name, start_time, end_time, time_column="created_at")

        self.assertIsInstance(result, pd.DataFrame)


class TestPostgreSQLDataAccessDelete(unittest.TestCase):
    """测试数据删除功能"""

    def setUp(self):
        """测试前准备"""
        self.mock_db_manager = Mock()
        self.mock_connection = Mock()
        self.mock_pool = Mock()
        self.mock_pool.connection.return_value.__enter__ = Mock(return_value=self.mock_connection)
        self.mock_pool.connection.return_value.__exit__ = Mock(return_value=False)
        self.mock_db_manager.get_postgresql_pool.return_value = self.mock_pool
        self.mock_cursor = Mock()
        self.mock_connection.cursor.return_value = self.mock_cursor
        self.mock_cursor.rowcount = 50
        self.access = PostgreSQLDataAccess(db_manager=self.mock_db_manager)

    def test_delete(self):
        """测试删除操作"""
        table_name = "test_table"
        where = "value < 0"

        result = self.access.delete(table_name, where)

        self.assertEqual(result, 50)
        self.mock_cursor.execute.assert_called_once()


class TestPostgreSQLDataAccessStats(unittest.TestCase):
    """测试统计信息功能"""

    def setUp(self):
        """测试前准备"""
        self.mock_db_manager = Mock()
        self.mock_connection = Mock()
        self.mock_pool = Mock()
        self.mock_pool.connection.return_value.__enter__ = Mock(return_value=self.mock_connection)
        self.mock_pool.connection.return_value.__exit__ = Mock(return_value=False)
        self.mock_db_manager.get_postgresql_pool.return_value = self.mock_pool

        # 模拟统计查询结果
        self.mock_connection.execute.return_value = Mock(fetchone=lambda: (10000, 1024, "2025-01-01"))

        self.access = PostgreSQLDataAccess(db_manager=self.mock_db_manager)

    def test_get_table_stats(self):
        """测试获取表统计信息"""
        table_name = "test_table"

        stats = self.access.get_table_stats(table_name)

        self.assertIsInstance(stats, dict)
        self.assertIn("row_count", stats)


class TestPostgreSQLDataAccessSaveLoad(unittest.TestCase):
    """测试save_data和load_data接口"""

    def setUp(self):
        """测试前准备"""
        from src.core.data_classification import DataClassification

        self.mock_db_manager = Mock()
        self.mock_connection = Mock()
        self.mock_pool = Mock()
        self.mock_pool.connection.return_value.__enter__ = Mock(return_value=self.mock_connection)
        self.mock_pool.connection.return_value.__exit__ = Mock(return_value=False)
        self.mock_db_manager.get_postgresql_pool.return_value = self.mock_pool

        self.test_data = pd.DataFrame(
            {"id": range(1, 11), "symbol": ["600000.SH"] * 10, "date": pd.date_range("2025-01-01", periods=10)}
        )

        self.access = PostgreSQLDataAccess(db_manager=self.mock_db_manager)
        self.classification = DataClassification.DAILY_KLINE

    def test_save_data(self):
        """测试保存数据"""
        table_name = "test_table"

        result = self.access.save_data(self.test_data, self.classification, table_name)

        self.assertTrue(result)

    @patch("src.data_access.postgresql_access.pd.read_sql")
    def test_load_data(self, mock_read_sql):
        """测试加载数据"""
        mock_read_sql.return_value = self.test_data

        table_name = "test_table"

        result = self.access.load_data(table_name)

        self.assertIsInstance(result, pd.DataFrame)


class TestPostgreSQLDataAccessClose(unittest.TestCase):
    """测试关闭连接功能"""

    def test_close(self):
        """测试关闭连接"""
        mock_db_manager = Mock()
        access = PostgreSQLDataAccess(db_manager=mock_db_manager)

        access.close()

        # 验证没有异常
        self.assertTrue(True)

    def test_close_all(self):
        """测试关闭所有连接"""
        mock_db_manager = Mock()
        access = PostgreSQLDataAccess(db_manager=mock_db_manager)

        access.close_all()

        self.assertTrue(True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
