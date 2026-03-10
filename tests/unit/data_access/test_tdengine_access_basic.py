"""
TDengine访问层基础测试
专注于提升TDengine数据访问层覆盖率（494行代码）
"""

import os
import sys
from datetime import datetime
from unittest.mock import Mock, patch

import pandas as pd
import pytest

# 添加源码路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../src"))

# 测试目标模块
from src.data_access.tdengine_access import TDengineDataAccess
from tests.unit.data_access._tdengine_access_basic_tail import (
    TestTDengineDataAccessBasicTailMixin,
)


class TestTDengineDataAccessBasic(TestTDengineDataAccessBasicTailMixin):
    """TDengineDataAccess基础测试 - 专注覆盖率"""

    def test_class_import_compatibility(self):
        """测试类导入兼容性"""
        try:
            from src.data_access.tdengine_access import TDengineDataAccess

            assert TDengineDataAccess is not None
        except ImportError as e:
            pytest.skip(f"TDengineDataAccess不可用: {e}")

    def test_initialization(self):
        """测试初始化"""
        with patch("src.data_access.tdengine_access.get_connection_manager") as mock_cm:
            mock_conn_manager = Mock()
            mock_cm.return_value = mock_conn_manager

            data_access = TDengineDataAccess()

            # 验证基本属性
            assert hasattr(data_access, "conn_manager")
            assert hasattr(data_access, "conn")
            assert data_access.conn_manager == mock_conn_manager
            assert data_access.conn is None

    def test_get_connection_method(self):
        """测试获取连接方法"""
        with patch("src.data_access.tdengine_access.get_connection_manager") as mock_cm:
            mock_conn_manager = Mock()
            mock_connection = Mock()
            mock_conn_manager.get_tdengine_connection.return_value = mock_connection
            mock_cm.return_value = mock_conn_manager

            data_access = TDengineDataAccess()

            # 首次调用应该初始化连接
            conn1 = data_access._get_connection()
            assert conn1 == mock_connection
            assert data_access.conn == mock_connection

            # 第二次调用应该使用已有的连接
            conn2 = data_access._get_connection()
            assert conn2 == mock_connection

            # 验证get_tdengine_connection被调用了一次（懒加载）
            mock_conn_manager.get_tdengine_connection.assert_called_once()

    def test_create_stable_method(self):
        """测试创建超表方法"""
        with patch.object(TDengineDataAccess, "_get_connection") as mock_get_conn:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_conn.cursor.return_value = mock_cursor
            mock_get_conn.return_value = mock_conn

            data_access = TDengineDataAccess()

            schema = {"ts": "TIMESTAMP", "price": "FLOAT", "volume": "INT"}
            tags = {"symbol": "BINARY(20)", "exchange": "BINARY(10)"}

            data_access.create_stable("test_stable", schema, tags)

            # 验证SQL语句生成
            mock_cursor.execute.assert_called_once()
            sql_call = mock_cursor.execute.call_args[0][0]
            assert "CREATE STABLE IF NOT EXISTS test_stable" in sql_call
            assert "ts TIMESTAMP" in sql_call
            assert "price FLOAT" in sql_call
            assert "volume INT" in sql_call
            assert "symbol BINARY(20)" in sql_call
            assert "exchange BINARY(10)" in sql_call
            assert "TAGS" in sql_call

    def test_create_table_method(self):
        """测试创建子表方法"""
        with patch.object(TDengineDataAccess, "_get_connection") as mock_get_conn:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_conn.cursor.return_value = mock_cursor
            mock_get_conn.return_value = mock_conn

            data_access = TDengineDataAccess()

            tag_values = {"symbol": "600000.SH", "exchange": "SSE"}

            data_access.create_table("test_table", "test_stable", tag_values)

            # 验证SQL语句生成
            mock_cursor.execute.assert_called_once()
            sql_call = mock_cursor.execute.call_args[0][0]
            assert "CREATE TABLE IF NOT EXISTS test_table" in sql_call
            assert "USING test_stable" in sql_call
            assert "TAGS" in sql_call
            assert "'600000.SH'" in sql_call
            assert "'SSE'" in sql_call

    def test_create_table_with_numeric_tags(self):
        """测试创建子表方法（数值标签）"""
        with patch.object(TDengineDataAccess, "_get_connection") as mock_get_conn:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_conn.cursor.return_value = mock_cursor
            mock_get_conn.return_value = mock_conn

            data_access = TDengineDataAccess()

            tag_values = {
                "symbol": "600000.SH",
                "exchange": 1,
                "active": True,
            }  # 数值标签  # 布尔标签

            data_access.create_table("test_table", "test_stable", tag_values)

            # 验证SQL语句生成
            sql_call = mock_cursor.execute.call_args[0][0]
            assert "'600000.SH'" in sql_call
            assert "1" in sql_call
            assert "True" in sql_call

    def test_insert_dataframe_method(self):
        """测试插入DataFrame方法"""
        test_df = pd.DataFrame(
            {
                "ts": pd.date_range("2025-01-01 09:30:00", periods=3, freq="1s"),
                "price": [10.5, 10.6, 10.7],
                "volume": [1000, 1500, 1200],
            }
        )

        with patch.object(TDengineDataAccess, "_get_connection") as mock_get_conn:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_conn.cursor.return_value = mock_cursor
            mock_get_conn.return_value = mock_conn

            data_access = TDengineDataAccess()

            result = data_access.insert_dataframe("test_table", test_df)

            assert result == 3
            assert mock_cursor.execute.call_count == 1  # 一个批次

    def test_insert_dataframe_empty(self):
        """测试插入空DataFrame"""
        empty_df = pd.DataFrame()

        data_access = TDengineDataAccess()

        result = data_access.insert_dataframe("test_table", empty_df)

        assert result == 0

    def test_insert_dataframe_large_dataset(self):
        """测试插入大数据集DataFrame（分批处理）"""
        # 创建超过10000行的数据
        large_df = pd.DataFrame(
            {
                "ts": pd.date_range("2025-01-01 09:30:00", periods=25000, freq="1s"),
                "price": [10.5] * 25000,
                "volume": [1000] * 25000,
            }
        )

        with patch.object(TDengineDataAccess, "_get_connection") as mock_get_conn:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_conn.cursor.return_value = mock_cursor
            mock_get_conn.return_value = mock_conn

            data_access = TDengineDataAccess()

            result = data_access.insert_dataframe("test_table", large_df)

            assert result == 25000
            # 应该分3批：10000 + 10000 + 5000
            assert mock_cursor.execute.call_count == 3

    def test_insert_dataframe_with_nulls(self):
        """测试插入包含空值的DataFrame"""
        test_df = pd.DataFrame(
            {
                "ts": pd.date_range("2025-01-01 09:30:00", periods=3, freq="1s"),
                "price": [10.5, None, 10.7],
                "volume": [1000, 1500, None],
            }
        )

        with patch.object(TDengineDataAccess, "_get_connection") as mock_get_conn:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_conn.cursor.return_value = mock_cursor
            mock_get_conn.return_value = mock_conn

            data_access = TDengineDataAccess()

            result = data_access.insert_dataframe("test_table", test_df)

            assert result == 3
            # 验证SQL包含NULL值
            sql_call = mock_cursor.execute.call_args[0][0]
            assert "NULL" in sql_call

    def test_insert_dataframe_string_timestamp_conversion(self):
        """测试插入DataFrame字符串时间戳转换"""
        test_df = pd.DataFrame(
            {
                "ts": ["2025-01-01 09:30:00", "2025-01-01 09:30:01"],
                "price": [10.5, 10.6],
                "volume": [1000, 1500],
            }
        )

        with patch.object(TDengineDataAccess, "_get_connection") as mock_get_conn:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_conn.cursor.return_value = mock_cursor
            mock_get_conn.return_value = mock_conn

            data_access = TDengineDataAccess()

            result = data_access.insert_dataframe("test_table", test_df)

            assert result == 2

    def test_query_by_time_range_method(self):
        """测试时间范围查询方法"""
        start_time = datetime(2025, 1, 1, 9, 30)
        end_time = datetime(2025, 1, 1, 15, 0)

        with patch.object(TDengineDataAccess, "_get_connection") as mock_get_conn:
            mock_conn = Mock()
            mock_cursor = Mock()
            test_data = [
                (datetime(2025, 1, 1, 9, 30), 10.5, 1000),
                (datetime(2025, 1, 1, 9, 31), 10.6, 1500),
            ]
            mock_cursor.fetchall.return_value = test_data
            mock_cursor.description = [("ts",), ("price",), ("volume",)]
            mock_conn.cursor.return_value = mock_cursor
            mock_get_conn.return_value = mock_conn

            data_access = TDengineDataAccess()

            result = data_access.query_by_time_range("test_table", start_time, end_time)

            assert len(result) == 2
            assert list(result.columns) == ["ts", "price", "volume"]
            mock_cursor.execute.assert_called_once()

            # 验证SQL语句
            sql_call = mock_cursor.execute.call_args[0][0]
            assert "SELECT * FROM test_table" in sql_call
            assert "ts >= '2025-01-01 09:30:00'" in sql_call
            assert "ts < '2025-01-01 15:00:00'" in sql_call
            assert "ORDER BY ts ASC" in sql_call

    def test_query_by_time_range_with_columns(self):
        """测试时间范围查询方法（指定列）"""
        start_time = datetime(2025, 1, 1, 9, 30)
        end_time = datetime(2025, 1, 1, 15, 0)

        with patch.object(TDengineDataAccess, "_get_connection") as mock_get_conn:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_cursor.fetchall.return_value = []
            mock_cursor.description = [("ts",), ("price",)]
            mock_conn.cursor.return_value = mock_cursor
            mock_get_conn.return_value = mock_conn

            data_access = TDengineDataAccess()

            data_access.query_by_time_range("test_table", start_time, end_time, columns=["ts", "price"])

            # 验证SQL语句包含指定列
            sql_call = mock_cursor.execute.call_args[0][0]
            assert "SELECT ts, price FROM test_table" in sql_call

    def test_query_by_time_range_with_limit(self):
        """测试时间范围查询方法（带限制）"""
        start_time = datetime(2025, 1, 1, 9, 30)
        end_time = datetime(2025, 1, 1, 15, 0)

        with patch.object(TDengineDataAccess, "_get_connection") as mock_get_conn:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_cursor.fetchall.return_value = []
            mock_cursor.description = []
            mock_conn.cursor.return_value = mock_cursor
            mock_get_conn.return_value = mock_conn

            data_access = TDengineDataAccess()

            data_access.query_by_time_range("test_table", start_time, end_time, limit=1000)

            # 验证SQL语句包含LIMIT
            sql_call = mock_cursor.execute.call_args[0][0]
            assert "LIMIT 1000" in sql_call

    def test_query_latest_method(self):
        """测试查询最新数据方法"""
        with patch.object(TDengineDataAccess, "_get_connection") as mock_get_conn:
            mock_conn = Mock()
            mock_cursor = Mock()
            test_data = [
                (datetime(2025, 1, 1, 15, 0), 10.8, 2000),
                (datetime(2025, 1, 1, 14, 59), 10.7, 1800),
            ]
            mock_cursor.fetchall.return_value = test_data
            mock_cursor.description = [("ts",), ("price",), ("volume",)]
            mock_conn.cursor.return_value = mock_cursor
            mock_get_conn.return_value = mock_conn

            data_access = TDengineDataAccess()

            result = data_access.query_latest("test_table", limit=100)

            assert len(result) == 2
            assert list(result.columns) == ["ts", "price", "volume"]

            # 验证SQL语句
            sql_call = mock_cursor.execute.call_args[0][0]
            assert "SELECT * FROM test_table" in sql_call
            assert "ORDER BY ts DESC" in sql_call
            assert "LIMIT 100" in sql_call

    def test_query_latest_default_limit(self):
        """测试查询最新数据方法（默认限制）"""
        with patch.object(TDengineDataAccess, "_get_connection") as mock_get_conn:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_cursor.fetchall.return_value = []
            mock_cursor.description = []
            mock_conn.cursor.return_value = mock_cursor
            mock_get_conn.return_value = mock_conn

            data_access = TDengineDataAccess()

            data_access.query_latest("test_table")

            # 验证默认限制
            sql_call = mock_cursor.execute.call_args[0][0]
            assert "LIMIT 100" in sql_call

    def test_aggregate_to_kline_method(self):
        """测试聚合为K线方法"""
        start_time = datetime(2025, 1, 1, 9, 30)
        end_time = datetime(2025, 1, 1, 15, 0)

        with patch.object(TDengineDataAccess, "_get_connection") as mock_get_conn:
            mock_conn = Mock()
            mock_cursor = Mock()
            test_data = [
                (datetime(2025, 1, 1, 9, 30), 10.5, 10.8, 10.4, 10.7, 10000),
                (datetime(2025, 1, 1, 9, 31), 10.7, 10.9, 10.6, 10.8, 12000),
            ]
            mock_cursor.fetchall.return_value = test_data
            mock_cursor.description = [
                ("ts",),
                ("open",),
                ("high",),
                ("low",),
                ("close",),
                ("volume",),
            ]
            mock_conn.cursor.return_value = mock_cursor
            mock_get_conn.return_value = mock_conn

            data_access = TDengineDataAccess()

            result = data_access.aggregate_to_kline("test_table", start_time, end_time)

            assert len(result) == 2
            assert list(result.columns) == [
                "ts",
                "open",
                "high",
                "low",
                "close",
                "volume",
            ]

            # 验证SQL语句
            sql_call = mock_cursor.execute.call_args[0][0]
            assert "FIRST(price)" in sql_call
            assert "MAX(price)" in sql_call
            assert "MIN(price)" in sql_call
            assert "LAST(price)" in sql_call
            assert "SUM(volume)" in sql_call
            assert "INTERVAL(1m)" in sql_call

    def test_aggregate_to_kline_custom_interval(self):
        """测试聚合为K线方法（自定义间隔）"""
        start_time = datetime(2025, 1, 1, 9, 30)
        end_time = datetime(2025, 1, 1, 15, 0)

        with patch.object(TDengineDataAccess, "_get_connection") as mock_get_conn:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_cursor.fetchall.return_value = []
            mock_cursor.description = []
            mock_conn.cursor.return_value = mock_cursor
            mock_get_conn.return_value = mock_conn

            data_access = TDengineDataAccess()

            data_access.aggregate_to_kline(
                "test_table",
                start_time,
                end_time,
                interval="5m",
                price_col="bid_price",
                volume_col="bid_volume",
            )

            # 验证SQL语句包含自定义参数
            sql_call = mock_cursor.execute.call_args[0][0]
            assert "FIRST(bid_price)" in sql_call
            assert "MAX(bid_price)" in sql_call
            assert "MIN(bid_price)" in sql_call
            assert "LAST(bid_price)" in sql_call
            assert "SUM(bid_volume)" in sql_call
            assert "INTERVAL(5m)" in sql_call

    def test_delete_by_time_range_method(self):
        """测试按时间范围删除方法"""
        start_time = datetime(2025, 1, 1, 9, 30)
        end_time = datetime(2025, 1, 1, 15, 0)

        with patch.object(TDengineDataAccess, "_get_connection") as mock_get_conn:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_cursor.rowcount = 1500
            mock_conn.cursor.return_value = mock_cursor
            mock_get_conn.return_value = mock_conn

            data_access = TDengineDataAccess()

            result = data_access.delete_by_time_range("test_table", start_time, end_time)

            assert result == 1500

            # 验证SQL语句
            sql_call = mock_cursor.execute.call_args[0][0]
            assert "DELETE FROM test_table" in sql_call
            assert "ts >= '2025-01-01 09:30:00'" in sql_call
            assert "ts < '2025-01-01 15:00:00'" in sql_call

    def test_delete_by_time_range_no_affected_rows(self):
        """测试按时间范围删除方法（无影响行）"""
        start_time = datetime(2025, 1, 1, 9, 30)
        end_time = datetime(2025, 1, 1, 15, 0)

        with patch.object(TDengineDataAccess, "_get_connection") as mock_get_conn:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_cursor.rowcount = None  # 模拟无影响行
            mock_conn.cursor.return_value = mock_cursor
            mock_get_conn.return_value = mock_conn

            data_access = TDengineDataAccess()

            result = data_access.delete_by_time_range("test_table", start_time, end_time)

            assert result == 0

    def test_get_table_info_method(self):
        """测试获取表信息方法"""
        with patch.object(TDengineDataAccess, "_get_connection") as mock_get_conn:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_cursor.fetchone.return_value = (
                10000,
                datetime(2025, 1, 1),
                datetime(2025, 1, 2),
            )
            mock_conn.cursor.return_value = mock_cursor
            mock_get_conn.return_value = mock_conn

            data_access = TDengineDataAccess()

            result = data_access.get_table_info("test_table")

            assert result["row_count"] == 10000
            assert result["start_time"] == datetime(2025, 1, 1)
            assert result["end_time"] == datetime(2025, 1, 2)

            # 验证SQL语句
            sql_call = mock_cursor.execute.call_args[0][0]
            assert "SELECT COUNT(*) as row_count" in sql_call
            assert "MIN(ts) as start_time" in sql_call
            assert "MAX(ts) as end_time" in sql_call
            assert "FROM test_table" in sql_call

    def test_get_table_info_empty_table(self):
        """测试获取表信息方法（空表）"""
        with patch.object(TDengineDataAccess, "_get_connection") as mock_get_conn:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_cursor.fetchone.return_value = None
            mock_conn.cursor.return_value = mock_cursor
            mock_get_conn.return_value = mock_conn

            data_access = TDengineDataAccess()

            result = data_access.get_table_info("test_table")

            assert result["row_count"] == 0
            assert result["start_time"] is None
            assert result["end_time"] is None

    def test_save_data_method(self):
        """测试保存数据方法"""
        test_df = pd.DataFrame(
            {
                "ts": pd.date_range("2025-01-01 09:30:00", periods=2, freq="1s"),
                "price": [10.5, 10.6],
                "volume": [1000, 1500],
            }
        )

        with patch.object(TDengineDataAccess, "insert_dataframe") as mock_insert:
            mock_insert.return_value = 2

            data_access = TDengineDataAccess()

            result = data_access.save_data(test_df, "test_classification", "test_table", timestamp_col="ts")

            assert result == True
            mock_insert.assert_called_once_with("test_table", test_df, timestamp_col="ts")

    def test_save_data_method_failure(self):
        """测试保存数据方法（失败情况）"""
        test_df = pd.DataFrame({"price": [10.5]})

        with patch.object(TDengineDataAccess, "insert_dataframe") as mock_insert:
            mock_insert.side_effect = Exception("Database error")

            data_access = TDengineDataAccess()

            result = data_access.save_data(test_df, "test_classification", "test_table")

            assert result == False

    def test_load_data_method_with_time_range(self):
        """测试加载数据方法（有时间范围）"""
        start_time = datetime(2025, 1, 1, 9, 30)
        end_time = datetime(2025, 1, 1, 15, 0)

        with patch.object(TDengineDataAccess, "query_by_time_range") as mock_query:
            mock_query.return_value = pd.DataFrame({"test": [1, 2]})

            data_access = TDengineDataAccess()

            result = data_access.load_data(
                "test_table",
                start_time=start_time,
                end_time=end_time,
                columns=["ts", "price"],
            )

            assert result is not None
            assert len(result) == 2
            mock_query.assert_called_once_with("test_table", start_time, end_time, columns=["ts", "price"])

    def test_load_data_method_without_time_range(self):
        """测试加载数据方法（无时间范围）"""
        with patch.object(TDengineDataAccess, "query_latest") as mock_query:
            mock_query.return_value = pd.DataFrame({"test": [1]})

            data_access = TDengineDataAccess()

            result = data_access.load_data("test_table", limit=50)

            assert result is not None
            assert len(result) == 1
            mock_query.assert_called_once_with("test_table", limit=50)

    def test_load_data_method_failure(self):
        """测试加载数据方法（失败情况）"""
        with patch.object(TDengineDataAccess, "query_latest") as mock_query:
            mock_query.side_effect = Exception("Query error")

            data_access = TDengineDataAccess()

            result = data_access.load_data("test_table")

            assert result is None

    def test_close_method(self):
        """测试关闭连接方法"""
        with patch("src.data_access.tdengine_access.get_connection_manager") as mock_cm:
            mock_conn_manager = Mock()
            mock_cm.return_value = mock_conn_manager

            data_access = TDengineDataAccess()
            mock_connection = Mock()
            data_access.conn = mock_connection

            data_access.close()

            mock_connection.close.assert_called_once()
            assert data_access.conn is None

    def test_close_method_without_connection(self):
        """测试关闭连接方法（无连接）"""
        data_access = TDengineDataAccess()
        # conn 为 None

        # 应该不会抛出异常
        data_access.close()

    def test_error_handling_in_database_operations(self):
        """测试数据库操作中的错误处理"""
        with patch.object(TDengineDataAccess, "_get_connection") as mock_get_conn:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_cursor.execute.side_effect = Exception("Database error")
            mock_conn.cursor.return_value = mock_cursor
            mock_get_conn.return_value = mock_conn

            data_access = TDengineDataAccess()

            # 应该抛出数据库异常
            with pytest.raises(Exception, match="Database error"):
                data_access.create_stable("test", {}, {})

if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__])
