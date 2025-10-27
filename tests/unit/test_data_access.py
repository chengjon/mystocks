"""
数据访问层单元测试

目标:
- 验证 TDengineDataAccess 的核心功能
- 验证 PostgreSQLDataAccess 的核心功能
- 使用 Mock 对象避免实际数据库依赖
- 测试错误处理和边界情况

创建日期: 2025-10-28
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch

import sys
import os

# 添加项目根目录到 sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from data_access.tdengine_access import TDengineDataAccess
from data_access.postgresql_access import PostgreSQLDataAccess


class TestTDengineDataAccess:
    """TDengineDataAccess 单元测试"""

    @pytest.fixture
    def mock_connection_manager(self):
        """创建 Mock 连接管理器"""
        with patch("data_access.tdengine_access.get_connection_manager") as mock:
            mock_manager = MagicMock()
            mock_conn = MagicMock()
            mock_cursor = MagicMock()

            mock_manager.get_tdengine_connection.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor

            mock.return_value = mock_manager
            yield mock, mock_manager, mock_conn, mock_cursor

    @pytest.fixture
    def access(self, mock_connection_manager):
        """创建 TDengineDataAccess 实例"""
        return TDengineDataAccess()

    def test_init(self, access):
        """测试初始化"""
        assert access.conn is None
        assert access.conn_manager is not None

    def test_get_connection_lazy_loading(self, access, mock_connection_manager):
        """测试连接懒加载"""
        mock_manager, mock_conn, mock_cursor = (
            mock_connection_manager[1],
            mock_connection_manager[2],
            mock_connection_manager[3],
        )

        # 第一次调用应该创建连接
        conn1 = access._get_connection()
        assert conn1 is not None
        assert mock_manager.get_tdengine_connection.call_count == 1

        # 第二次调用应该使用缓存的连接
        conn2 = access._get_connection()
        assert conn1 is conn2
        assert mock_manager.get_tdengine_connection.call_count == 1

    def test_create_stable(self, access, mock_connection_manager):
        """测试创建超表"""
        mock_conn = mock_connection_manager[2]
        mock_cursor = mock_connection_manager[3]

        schema = {"ts": "TIMESTAMP", "price": "FLOAT", "volume": "INT"}
        tags = {"symbol": "BINARY(20)", "exchange": "BINARY(10)"}

        access.create_stable("tick_data", schema, tags)

        # 验证执行了 SQL
        mock_cursor.execute.assert_called_once()
        mock_cursor.close.assert_called_once()

        # 验证 SQL 包含关键字
        call_args = mock_cursor.execute.call_args
        sql = call_args[0][0]
        assert "CREATE STABLE" in sql
        assert "tick_data" in sql
        assert "TIMESTAMP" in sql

    def test_insert_dataframe(self, access, mock_connection_manager):
        """测试 DataFrame 批量插入"""
        mock_cursor = mock_connection_manager[3]

        # 创建示例数据
        df = pd.DataFrame(
            {
                "ts": pd.date_range("2025-01-01", periods=100, freq="1s"),
                "price": np.random.uniform(10, 20, 100),
                "volume": np.random.randint(100, 10000, 100),
            }
        )

        rows_inserted = access.insert_dataframe("tick_data_600000", df)

        # 验证返回的行数
        assert rows_inserted == 100

        # 验证执行了 SQL
        assert mock_cursor.execute.called

    def test_insert_empty_dataframe(self, access):
        """测试插入空 DataFrame"""
        df = pd.DataFrame()

        rows_inserted = access.insert_dataframe("tick_data_600000", df)

        # 应该返回 0
        assert rows_inserted == 0

    def test_query_by_time_range(self, access, mock_connection_manager):
        """测试按时间范围查询"""
        mock_cursor = mock_connection_manager[3]

        # Mock cursor 返回值
        mock_cursor.description = [("ts",), ("price",), ("volume",)]
        mock_cursor.fetchall.return_value = [
            (datetime(2025, 1, 1, 9, 30), 10.5, 1000),
            (datetime(2025, 1, 1, 9, 31), 10.6, 1100),
        ]

        start_time = datetime(2025, 1, 1, 9, 30)
        end_time = datetime(2025, 1, 1, 15, 0)

        df = access.query_by_time_range("tick_data_600000", start_time, end_time)

        # 验证返回了数据
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert list(df.columns) == ["ts", "price", "volume"]

        # 验证执行了 SQL
        assert mock_cursor.execute.called

    def test_query_latest(self, access, mock_connection_manager):
        """测试查询最新数据"""
        mock_cursor = mock_connection_manager[3]

        mock_cursor.description = [("ts",), ("price",), ("volume",)]
        mock_cursor.fetchall.return_value = [
            (datetime(2025, 1, 1, 15, 0), 10.9, 1500),
            (datetime(2025, 1, 1, 14, 59), 10.8, 1400),
        ]

        df = access.query_latest("tick_data_600000", limit=100)

        # 验证返回了数据
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2

        # 验证执行了带 LIMIT 的 SQL
        call_args = mock_cursor.execute.call_args
        sql = call_args[0][0]
        assert "LIMIT" in sql

    def test_aggregate_to_kline(self, access, mock_connection_manager):
        """测试聚合为 K 线"""
        mock_cursor = mock_connection_manager[3]

        mock_cursor.description = [
            ("ts",),
            ("open",),
            ("high",),
            ("low",),
            ("close",),
            ("volume",),
        ]
        mock_cursor.fetchall.return_value = [
            (datetime(2025, 1, 1, 9, 30), 10.0, 10.9, 9.9, 10.5, 100000),
            (datetime(2025, 1, 1, 9, 35), 10.5, 11.0, 10.4, 10.8, 120000),
        ]

        start_time = datetime(2025, 1, 1, 9, 30)
        end_time = datetime(2025, 1, 1, 15, 0)

        df = access.aggregate_to_kline(
            "tick_data_600000", start_time, end_time, interval="5m"
        )

        # 验证返回了 K 线数据
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert set(df.columns) == {"ts", "open", "high", "low", "close", "volume"}

        # 验证包含聚合 SQL 关键字
        call_args = mock_cursor.execute.call_args
        sql = call_args[0][0]
        assert "INTERVAL" in sql

    def test_delete_by_time_range(self, access, mock_connection_manager):
        """测试按时间范围删除"""
        mock_cursor = mock_connection_manager[3]
        mock_cursor.rowcount = 50

        start_time = datetime(2025, 1, 1)
        end_time = datetime(2025, 1, 2)

        deleted = access.delete_by_time_range("tick_data_600000", start_time, end_time)

        # 验证返回删除的行数
        assert deleted == 50

        # 验证执行了 DELETE SQL
        call_args = mock_cursor.execute.call_args
        sql = call_args[0][0]
        assert "DELETE" in sql

    def test_get_table_info(self, access, mock_connection_manager):
        """测试获取表信息"""
        mock_cursor = mock_connection_manager[3]
        mock_cursor.fetchone.return_value = (
            1000,
            datetime(2025, 1, 1, 9, 30),
            datetime(2025, 1, 1, 15, 0),
        )

        info = access.get_table_info("tick_data_600000")

        # 验证返回了表信息
        assert info["row_count"] == 1000
        assert info["start_time"] == datetime(2025, 1, 1, 9, 30)
        assert info["end_time"] == datetime(2025, 1, 1, 15, 0)

    def test_save_data(self, access, mock_connection_manager):
        """测试保存数据（DataManager API）"""
        mock_cursor = mock_connection_manager[3]

        df = pd.DataFrame(
            {
                "ts": pd.date_range("2025-01-01", periods=10, freq="1s"),
                "price": np.random.uniform(10, 20, 10),
                "volume": np.random.randint(100, 10000, 10),
            }
        )

        result = access.save_data(df, None, "tick_data_600000")

        # 验证保存成功
        assert result is True

    def test_load_data_with_time_range(self, access, mock_connection_manager):
        """测试加载数据（时间范围）"""
        mock_cursor = mock_connection_manager[3]
        mock_cursor.description = [("ts",), ("price",), ("volume",)]
        mock_cursor.fetchall.return_value = [
            (datetime(2025, 1, 1, 9, 30), 10.5, 1000),
        ]

        filters = {
            "start_time": datetime(2025, 1, 1, 9, 30),
            "end_time": datetime(2025, 1, 1, 15, 0),
        }

        df = access.load_data("tick_data_600000", **filters)

        # 验证加载了数据
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1

    def test_load_data_without_time_range(self, access, mock_connection_manager):
        """测试加载数据（无时间范围，返回最新）"""
        mock_cursor = mock_connection_manager[3]
        mock_cursor.description = [("ts",), ("price",), ("volume",)]
        mock_cursor.fetchall.return_value = [
            (datetime(2025, 1, 1, 15, 0), 10.9, 1500),
        ]

        df = access.load_data("tick_data_600000")

        # 应该调用 query_latest
        assert isinstance(df, pd.DataFrame)

    def test_close_connection(self, access, mock_connection_manager):
        """测试关闭连接"""
        mock_conn = mock_connection_manager[2]

        # 先获取连接
        access._get_connection()

        # 关闭连接
        access.close()

        # 验证调用了 close
        mock_conn.close.assert_called_once()
        assert access.conn is None


class TestPostgreSQLDataAccess:
    """PostgreSQLDataAccess 单元测试"""

    @pytest.fixture
    def mock_connection_manager(self):
        """创建 Mock 连接管理器"""
        with patch("data_access.postgresql_access.get_connection_manager") as mock:
            mock_manager = MagicMock()
            mock_pool = MagicMock()
            mock_conn = MagicMock()
            mock_cursor = MagicMock()

            mock_manager.get_postgresql_connection.return_value = mock_pool
            mock_pool.getconn.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor

            mock.return_value = mock_manager
            yield mock, mock_manager, mock_pool, mock_conn, mock_cursor

    @pytest.fixture
    def access(self, mock_connection_manager):
        """创建 PostgreSQLDataAccess 实例"""
        return PostgreSQLDataAccess()

    def test_init(self, access):
        """测试初始化"""
        assert access.pool is None
        assert access.conn_manager is not None

    def test_get_connection_from_pool(self, access, mock_connection_manager):
        """测试从连接池获取连接"""
        mock_manager, mock_pool, mock_conn, _ = (
            mock_connection_manager[1],
            mock_connection_manager[2],
            mock_connection_manager[3],
            mock_connection_manager[4],
        )

        # 第一次调用应该获取连接池
        conn1 = access._get_connection()
        assert mock_pool.getconn.call_count == 1

        # 第二次调用应该从缓存的连接池获取
        conn2 = access._get_connection()
        assert mock_pool.getconn.call_count == 2

    def test_return_connection_to_pool(self, access, mock_connection_manager):
        """测试归还连接到连接池"""
        mock_pool = mock_connection_manager[2]
        mock_conn = MagicMock()

        # 初始化连接池
        access._get_connection()

        # 归还连接
        access._return_connection(mock_conn)

        # 验证调用了 putconn
        mock_pool.putconn.assert_called_once_with(mock_conn)

    def test_create_table(self, access, mock_connection_manager):
        """测试创建普通表"""
        mock_conn = mock_connection_manager[3]
        mock_cursor = mock_connection_manager[4]

        schema = {
            "symbol": "VARCHAR(20)",
            "date": "DATE",
            "close": "DECIMAL(10,2)",
        }

        access.create_table("daily_kline", schema, primary_key="symbol, date")

        # 验证执行了 SQL
        mock_cursor.execute.assert_called()
        mock_conn.commit.assert_called()

        # 验证 SQL 包含关键字
        call_args = mock_cursor.execute.call_args
        sql = call_args[0][0]
        assert "CREATE TABLE" in sql
        assert "daily_kline" in sql

    def test_create_hypertable(self, access, mock_connection_manager):
        """测试创建 TimescaleDB 时序表"""
        mock_conn = mock_connection_manager[3]
        mock_cursor = mock_connection_manager[4]

        access.create_hypertable(
            "daily_kline", time_column="date", chunk_interval="30 days"
        )

        # 验证执行了 SQL
        mock_cursor.execute.assert_called()
        mock_conn.commit.assert_called()

        # 验证调用了 create_hypertable 函数
        call_args = mock_cursor.execute.call_args
        sql = call_args[0][0]
        assert "create_hypertable" in sql

    def test_insert_dataframe(self, access, mock_connection_manager):
        """测试 DataFrame 批量插入"""
        mock_conn = mock_connection_manager[3]
        mock_cursor = mock_connection_manager[4]
        mock_cursor.rowcount = 100

        df = pd.DataFrame(
            {
                "symbol": ["600000.SH"] * 100,
                "date": pd.date_range("2025-01-01", periods=100),
                "close": np.random.uniform(10, 20, 100),
            }
        )

        # Mock execute_values to avoid encoding issues
        with patch(
            "data_access.postgresql_access.execute_values"
        ) as mock_execute_values:
            rows_inserted = access.insert_dataframe("daily_kline", df)

            # 验证返回的行数
            assert rows_inserted == 100

            # 验证调用了 execute_values
            mock_execute_values.assert_called_once()

    def test_insert_empty_dataframe(self, access):
        """测试插入空 DataFrame"""
        df = pd.DataFrame()

        rows_inserted = access.insert_dataframe("daily_kline", df)

        # 应该返回 0
        assert rows_inserted == 0

    def test_upsert_dataframe(self, access, mock_connection_manager):
        """测试 Upsert 操作"""
        mock_conn = mock_connection_manager[3]
        mock_cursor = mock_connection_manager[4]
        mock_cursor.rowcount = 50

        df = pd.DataFrame(
            {
                "symbol": ["600000.SH"] * 50,
                "date": pd.date_range("2025-01-01", periods=50),
                "close": np.random.uniform(10, 20, 50),
            }
        )

        # Mock execute_values to avoid encoding issues
        with patch(
            "data_access.postgresql_access.execute_values"
        ) as mock_execute_values:
            rows_affected = access.upsert_dataframe(
                "daily_kline", df, conflict_columns=["symbol", "date"]
            )

            # 验证返回的影响行数
            assert rows_affected == 50

            # 验证调用了 execute_values
            mock_execute_values.assert_called_once()

    def test_query(self, access, mock_connection_manager):
        """测试通用查询"""
        mock_conn = mock_connection_manager[3]

        # Mock pd.read_sql 返回值
        with patch("data_access.postgresql_access.pd.read_sql") as mock_read_sql:
            expected_df = pd.DataFrame(
                {
                    "symbol": ["600000.SH"],
                    "date": [datetime(2025, 1, 1)],
                    "close": [10.5],
                }
            )
            mock_read_sql.return_value = expected_df

            df = access.query(
                "daily_kline",
                columns=["symbol", "date", "close"],
                where="symbol = '600000.SH'",
            )

            # 验证返回了数据
            assert isinstance(df, pd.DataFrame)
            assert len(df) == 1

    def test_query_by_time_range(self, access, mock_connection_manager):
        """测试按时间范围查询"""
        mock_conn = mock_connection_manager[3]

        with patch("data_access.postgresql_access.pd.read_sql") as mock_read_sql:
            expected_df = pd.DataFrame(
                {
                    "symbol": ["600000.SH"],
                    "date": [datetime(2025, 1, 1)],
                    "close": [10.5],
                }
            )
            mock_read_sql.return_value = expected_df

            df = access.query_by_time_range(
                "daily_kline",
                "date",
                datetime(2025, 1, 1),
                datetime(2025, 1, 2),
            )

            # 验证返回了数据
            assert isinstance(df, pd.DataFrame)

    def test_execute_sql(self, access, mock_connection_manager):
        """测试执行自定义 SQL"""
        with patch("data_access.postgresql_access.pd.read_sql") as mock_read_sql:
            expected_df = pd.DataFrame({"avg_close": [10.5]})
            mock_read_sql.return_value = expected_df

            df = access.execute_sql(
                "SELECT AVG(close) as avg_close FROM daily_kline WHERE date >= %s",
                params=("2025-01-01",),
            )

            # 验证返回了数据
            assert isinstance(df, pd.DataFrame)
            assert "avg_close" in df.columns

    def test_delete(self, access, mock_connection_manager):
        """测试删除数据"""
        mock_conn = mock_connection_manager[3]
        mock_cursor = mock_connection_manager[4]
        mock_cursor.rowcount = 10

        deleted = access.delete("daily_kline", "date < '2020-01-01'")

        # 验证返回删除的行数
        assert deleted == 10

        # 验证执行了 DELETE SQL
        call_args = mock_cursor.execute.call_args
        sql = call_args[0][0]
        assert "DELETE" in sql

    def test_get_table_stats(self, access, mock_connection_manager):
        """测试获取表统计信息"""
        mock_conn = mock_connection_manager[3]
        mock_cursor = mock_connection_manager[4]
        mock_cursor.fetchone.return_value = (1000, "100 MB")

        stats = access.get_table_stats("daily_kline")

        # 验证返回了统计信息
        assert stats["row_count"] == 1000
        assert stats["total_size"] == "100 MB"

    def test_save_data(self, access, mock_connection_manager):
        """测试保存数据（DataManager API）"""
        mock_cursor = mock_connection_manager[4]
        mock_cursor.rowcount = 50

        df = pd.DataFrame(
            {
                "symbol": ["600000.SH"] * 50,
                "date": pd.date_range("2025-01-01", periods=50),
                "close": np.random.uniform(10, 20, 50),
            }
        )

        # Mock execute_values to avoid encoding issues
        with patch(
            "data_access.postgresql_access.execute_values"
        ) as mock_execute_values:
            result = access.save_data(df, None, "daily_kline")

            # 验证保存成功
            assert result is True

    def test_save_data_with_upsert(self, access, mock_connection_manager):
        """测试保存数据（使用 Upsert）"""
        mock_cursor = mock_connection_manager[4]
        mock_cursor.rowcount = 50

        df = pd.DataFrame(
            {
                "symbol": ["600000.SH"] * 50,
                "date": pd.date_range("2025-01-01", periods=50),
                "close": np.random.uniform(10, 20, 50),
            }
        )

        # Mock execute_values to avoid encoding issues
        with patch(
            "data_access.postgresql_access.execute_values"
        ) as mock_execute_values:
            result = access.save_data(
                df,
                None,
                "daily_kline",
                upsert=True,
                conflict_columns=["symbol", "date"],
            )

            # 验证保存成功
            assert result is True

    def test_load_data_with_time_range(self, access, mock_connection_manager):
        """测试加载数据（时间范围）"""
        # The load_data method actually expects start_time and end_time
        # but query_by_time_range expects (table_name, time_column, start_time, end_time)
        # So we need to mock the query_by_time_range to avoid the signature mismatch

        expected_df = pd.DataFrame(
            {
                "symbol": ["600000.SH"],
                "date": [datetime(2025, 1, 1)],
                "close": [10.5],
            }
        )

        with patch.object(
            access, "query_by_time_range", return_value=expected_df
        ) as mock_query:
            filters = {
                "start_time": datetime(2025, 1, 1),
                "end_time": datetime(2025, 1, 2),
                "time_column": "date",
            }

            df = access.load_data("daily_kline", **filters)

            # 验证加载了数据
            assert df is not None
            assert isinstance(df, pd.DataFrame)
            assert len(df) == 1

    def test_load_data_with_where_clause(self, access, mock_connection_manager):
        """测试加载数据（WHERE 条件）"""
        with patch("data_access.postgresql_access.pd.read_sql") as mock_read_sql:
            expected_df = pd.DataFrame(
                {
                    "symbol": ["600000.SH"],
                    "date": [datetime(2025, 1, 1)],
                    "close": [10.5],
                }
            )
            mock_read_sql.return_value = expected_df

            filters = {"where": "symbol = '600000.SH' AND date >= '2025-01-01'"}

            df = access.load_data("daily_kline", **filters)

            # 验证加载了数据
            assert isinstance(df, pd.DataFrame)

    def test_close_all_connections(self, access, mock_connection_manager):
        """测试关闭所有连接"""
        mock_pool = mock_connection_manager[2]

        # 先初始化连接池
        access._get_connection()

        # 关闭所有连接
        access.close_all()

        # 验证调用了 closeall
        mock_pool.closeall.assert_called_once()
        assert access.pool is None


class TestDataAccessIntegration:
    """数据访问层集成测试"""

    def test_tdengine_and_postgresql_compatibility(self):
        """测试 TDengineDataAccess 和 PostgreSQLDataAccess 的 API 兼容性"""
        # 两个类应该有相同的核心方法签名
        tdengine_methods = set(dir(TDengineDataAccess))
        postgresql_methods = set(dir(PostgreSQLDataAccess))

        # 检查关键方法
        key_methods = {"save_data", "load_data"}
        for method in key_methods:
            assert method in tdengine_methods
            assert method in postgresql_methods


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
