"""
TDengine数据访问层测试

测试TDengineDataAccess类的所有功能：
- 连接管理
- 表和超表创建
- 数据插入
- 时间范围查询
- 数据聚合
- 数据删除
- 表信息获取

创建日期: 2026-01-03
Phase: 2 - Task 2.1.1
"""

import unittest
from datetime import datetime
from unittest.mock import Mock, patch

import numpy as np
import pandas as pd

from src.data_access.tdengine_access import TDengineDataAccess


class TestTDengineDataAccessInit(unittest.TestCase):
    """测试TDengineDataAccess初始化"""

    def test_init_with_db_manager(self):
        """测试使用db_manager初始化"""
        mock_db_manager = Mock()
        mock_monitoring_db = Mock()

        access = TDengineDataAccess(db_manager=mock_db_manager, monitoring_db=mock_monitoring_db)

        self.assertIsNotNone(access)
        self.assertEqual(access.db_manager, mock_db_manager)
        self.assertEqual(access.monitoring_db, mock_monitoring_db)

    def test_init_without_db_manager(self):
        """测试不使用db_manager初始化"""
        access = TDengineDataAccess()

        self.assertIsNotNone(access)
        self.assertIsNotNone(access.db_manager)


class TestTDengineDataAccessConnection(unittest.TestCase):
    """测试连接管理功能"""

    def setUp(self):
        """测试前准备"""
        self.mock_db_manager = Mock()
        self.mock_connection = Mock()
        self.mock_db_manager.get_tdx_connection.return_value = self.mock_connection
        self.access = TDengineDataAccess(db_manager=self.mock_db_manager)

    def test_check_connection_success(self):
        """测试检查连接成功"""
        self.mock_connection.execute_sql.return_value = Mock()
        self.mock_connection.execute_sql.return_value.fetchall.return_value = [["1"]]

        result = self.access.check_connection()

        self.assertTrue(result)
        self.mock_connection.execute_sql.assert_called_once()

    def test_check_connection_failure(self):
        """测试检查连接失败"""
        self.mock_connection.execute_sql.side_effect = Exception("Connection lost")

        result = self.access.check_connection()

        self.assertFalse(result)

    def test_get_connection(self):
        """测试获取连接"""
        conn = self.access._get_connection()

        self.assertEqual(conn, self.mock_connection)
        self.mock_db_manager.get_tdx_connection.assert_called_once()


class TestTDengineDataAccessTableCreation(unittest.TestCase):
    """测试表创建功能"""

    def setUp(self):
        """测试前准备"""
        self.mock_db_manager = Mock()
        self.mock_connection = Mock()
        self.mock_db_manager.get_tdx_connection.return_value = self.mock_connection
        self.access = TDengineDataAccess(db_manager=self.mock_db_manager)

    def test_create_stable_basic(self):
        """测试创建基本超表"""
        stable_name = "test_stable"
        schema = {"ts": "TIMESTAMP", "symbol": "NCHAR(10)", "price": "DOUBLE", "volume": "BIGINT"}
        tags = {"symbol": "NCHAR(10)"}

        result = self.access.create_stable(stable_name, schema, tags)

        self.assertTrue(result)
        self.mock_connection.execute_sql.assert_called_once()

    def test_create_table_basic(self):
        """测试创建基本表"""
        table_name = "test_table"
        stable_name = "test_stable"
        tag_values = {"symbol": "600000.SH"}

        result = self.access.create_table(table_name, stable_name, tag_values)

        self.assertTrue(result)
        self.mock_connection.execute_sql.assert_called_once()


class TestTDengineDataAccessDataInsertion(unittest.TestCase):
    """测试数据插入功能"""

    def setUp(self):
        """测试前准备"""
        self.mock_db_manager = Mock()
        self.mock_connection = Mock()
        self.mock_db_manager.get_tdx_connection.return_value = self.mock_connection

        # 创建测试数据
        self.test_data = pd.DataFrame(
            {
                "ts": pd.date_range("2025-01-01", periods=100, freq="T"),
                "symbol": ["600000.SH"] * 100,
                "price": np.random.randn(100) * 10 + 100,
                "volume": np.random.randint(1000, 10000, 100),
            }
        )

        self.access = TDengineDataAccess(db_manager=self.mock_db_manager)

    def test_insert_dataframe_basic(self):
        """测试基本DataFrame插入"""
        table_name = "test_table"
        timestamp_col = "ts"

        result = self.access.insert_dataframe(table_name, self.test_data, timestamp_col)

        self.assertTrue(result)
        self.mock_connection.execute_sql.assert_called()

    def test_insert_dataframe_empty(self):
        """测试插入空DataFrame"""
        table_name = "test_table"
        empty_df = pd.DataFrame()

        result = self.access.insert_dataframe(table_name, empty_df)

        self.assertFalse(result)

    def test_insert_dataframe_invalid_timestamp_col(self):
        """测试使用不存在的时间戳列"""
        table_name = "test_table"
        invalid_col = "nonexistent_col"

        result = self.access.insert_dataframe(table_name, self.test_data, invalid_col)

        self.assertFalse(result)


class TestTDengineDataAccessQuery(unittest.TestCase):
    """测试查询功能"""

    def setUp(self):
        """测试前准备"""
        self.mock_db_manager = Mock()
        self.mock_connection = Mock()
        self.mock_db_manager.get_tdx_connection.return_value = self.mock_connection

        # 模拟查询结果
        self.mock_result = Mock()
        self.mock_result.fetchall.return_value = [
            ["2025-01-01 09:30:00", "600000.SH", 100.5, 5000],
            ["2025-01-01 09:31:00", "600000.SH", 101.0, 6000],
        ]
        self.mock_result.data = (("ts", "symbol", "price", "volume"),)
        self.mock_connection.execute_sql.return_value = self.mock_result

        self.access = TDengineDataAccess(db_manager=self.mock_db_manager)

    def test_query_by_time_range_basic(self):
        """测试基本时间范围查询"""
        table_name = "test_table"
        start_time = datetime(2025, 1, 1, 9, 30)
        end_time = datetime(2025, 1, 1, 10, 0)

        result = self.access.query_by_time_range(table_name, start_time, end_time)

        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)

    def test_query_latest(self):
        """测试查询最新数据"""
        table_name = "test_table"
        limit = 10

        result = self.access.query_latest(table_name, limit)

        self.assertIsInstance(result, pd.DataFrame)


class TestTDengineDataAccessDeletion(unittest.TestCase):
    """测试数据删除功能"""

    def setUp(self):
        """测试前准备"""
        self.mock_db_manager = Mock()
        self.mock_connection = Mock()
        self.mock_db_manager.get_tdx_connection.return_value = self.mock_connection
        self.mock_connection.execute_sql.return_value = Mock(rowcount=100)
        self.access = TDengineDataAccess(db_manager=self.mock_db_manager)

    def test_delete_by_time_range(self):
        """测试按时间范围删除"""
        table_name = "test_table"
        start_time = datetime(2025, 1, 1, 9, 30)
        end_time = datetime(2025, 1, 1, 10, 0)

        result = self.access.delete_by_time_range(table_name, start_time, end_time)

        self.assertEqual(result, 100)
        self.mock_connection.execute_sql.assert_called_once()


class TestTDengineDataAccessAggregation(unittest.TestCase):
    """测试数据聚合功能"""

    def setUp(self):
        """测试前准备"""
        self.mock_db_manager = Mock()
        self.mock_connection = Mock()
        self.mock_db_manager.get_tdx_connection.return_value = self.mock_connection
        self.access = TDengineDataAccess(db_manager=self.mock_db_manager)

    @patch("src.data_access.tdengine_access.pd.read_sql")
    def test_aggregate_to_kline(self, mock_read_sql):
        """测试聚合为K线"""
        mock_read_sql.return_value = pd.DataFrame(
            {
                "ts": pd.date_range("2025-01-01", periods=5, freq="D"),
                "open": [100.0] * 5,
                "high": [105.0] * 5,
                "low": [98.0] * 5,
                "close": [103.0] * 5,
                "volume": [10000] * 5,
            }
        )

        table_name = "tick_data"
        target_table = "daily_kline"

        result = self.access.aggregate_to_kline(table_name=table_name, target_table=target_table, window_size="1d")

        self.assertIsInstance(result, pd.DataFrame)


class TestTDengineDataAccessTableInfo(unittest.TestCase):
    """测试表信息获取功能"""

    def setUp(self):
        """测试前准备"""
        self.mock_db_manager = Mock()
        self.mock_connection = Mock()
        self.mock_db_manager.get_tdx_connection.return_value = self.mock_connection
        self.access = TDengineDataAccess(db_manager=self.mock_db_manager)

    def test_get_table_info(self):
        """测试获取表信息"""
        self.mock_connection.execute_sql.return_value = Mock(
            fetchall=lambda: [["test_table", "test_stable", "created"]]
        )

        table_name = "test_table"

        info = self.access.get_table_info(table_name)

        self.assertIsInstance(info, dict)
        self.assertIn("table_name", info)


class TestTDengineDataAccessSaveLoad(unittest.TestCase):
    """测试save_data和load_data接口"""

    def setUp(self):
        """测试前准备"""
        from src.core.data_classification import DataClassification

        self.mock_db_manager = Mock()
        self.mock_connection = Mock()
        self.mock_db_manager.get_tdx_connection.return_value = self.mock_connection

        self.test_data = pd.DataFrame(
            {
                "ts": pd.date_range("2025-01-01", periods=10, freq="T"),
                "symbol": ["600000.SH"] * 10,
                "price": [100.0 + i * 0.1 for i in range(10)],
            }
        )

        self.access = TDengineDataAccess(db_manager=self.mock_db_manager)
        self.classification = DataClassification.MINUTE_KLINE

    def test_save_data(self):
        """测试保存数据"""
        table_name = "test_table"

        result = self.access.save_data(self.test_data, self.classification, table_name)

        self.assertTrue(result)

    def test_load_data(self):
        """测试加载数据"""
        table_name = "test_table"
        self.mock_connection.execute_sql.return_value = Mock(
            fetchall=lambda: [["2025-01-01 09:30:00", "600000.SH", 100.0]]
        )

        result = self.access.load_data(table_name)

        self.assertIsInstance(result, pd.DataFrame)


class TestTDengineDataAccessClose(unittest.TestCase):
    """测试关闭连接功能"""

    def test_close(self):
        """测试关闭连接"""
        mock_db_manager = Mock()
        access = TDengineDataAccess(db_manager=mock_db_manager)

        access.close()

        # 验证没有异常
        self.assertTrue(True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
