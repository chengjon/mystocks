"""
PostgreSQL Access 综合测试
全面测试 PostgreSQLDataAccess 类的所有功能
目标覆盖率: 67%+
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch
from datetime import datetime

# 导入测试目标
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))

from src.data_access.postgresql_access import PostgreSQLDataAccess


class TestPostgreSQLDataAccessInit:
    """测试 PostgreSQLDataAccess 初始化"""

    @patch("src.data_access.postgresql_access.get_connection_manager")
    def test_init_success(self, mock_get_manager):
        """测试成功初始化"""
        mock_manager = Mock()
        mock_get_manager.return_value = mock_manager

        access = PostgreSQLDataAccess()

        assert access.conn_manager == mock_manager
        assert access.pool is None
        mock_get_manager.assert_called_once()

    def test_init_without_mock(self):
        """测试无依赖初始化"""
        # 实际初始化测试（不连接数据库）
        with patch("src.data_access.postgresql_access.get_connection_manager"):
            access = PostgreSQLDataAccess()
            assert hasattr(access, "conn_manager")
            assert hasattr(access, "pool")


class TestPostgreSQLDataAccessConnection:
    """测试连接管理功能"""

    @patch("src.data_access.postgresql_access.get_connection_manager")
    def test_get_connection(self, mock_get_manager):
        """测试获取连接"""
        # 模拟连接管理器和连接池
        mock_manager = Mock()
        mock_pool = Mock()
        mock_conn = Mock()

        mock_manager.get_postgresql_connection.return_value = mock_pool
        mock_pool.getconn.return_value = mock_conn
        mock_get_manager.return_value = mock_manager

        access = PostgreSQLDataAccess()
        conn = access._get_connection()

        assert conn == mock_conn
        assert access.pool == mock_pool
        mock_manager.get_postgresql_connection.assert_called_once()
        mock_pool.getconn.assert_called_once()

    @patch("src.data_access.postgresql_access.get_connection_manager")
    def test_return_connection(self, mock_get_manager):
        """测试归还连接"""
        mock_manager = Mock()
        mock_pool = Mock()
        mock_conn = Mock()

        mock_get_manager.return_value = mock_manager
        access = PostgreSQLDataAccess()
        access.pool = mock_pool

        access._return_connection(mock_conn)

        mock_pool.putconn.assert_called_once_with(mock_conn)

    @patch("src.data_access.postgresql_access.get_connection_manager")
    def test_return_connection_no_pool(self, mock_get_manager):
        """测试归还连接时没有池"""
        mock_manager = Mock()
        mock_get_manager.return_value = mock_manager

        access = PostgreSQLDataAccess()
        access.pool = None

        # 应该不会抛出异常
        access._return_connection(Mock())


class TestPostgreSQLDataAccessTable:
    """测试表管理功能"""

    @patch("src.data_access.postgresql_access.get_connection_manager")
    def test_create_table_success(self, mock_get_manager):
        """测试成功创建表"""
        # 模拟连接和游标
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor

        mock_manager = Mock()
        mock_pool = Mock()
        mock_pool.getconn.return_value = mock_conn
        mock_manager.get_postgresql_connection.return_value = mock_pool
        mock_get_manager.return_value = mock_manager

        access = PostgreSQLDataAccess()

        schema = {
            "symbol": "VARCHAR(20)",
            "date": "DATE",
            "open": "DECIMAL(10,2)",
            "high": "DECIMAL(10,2)",
            "low": "DECIMAL(10,2)",
            "close": "DECIMAL(10,2)",
            "volume": "BIGINT",
        }

        access.create_table("test_table", schema, primary_key="symbol, date")

        # 验证SQL执行
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()
        mock_cursor.close.assert_called_once()

        # 验证SQL内容
        executed_sql = mock_cursor.execute.call_args[0][0]
        assert "CREATE TABLE IF NOT EXISTS test_table" in executed_sql
        assert "symbol VARCHAR(20)" in executed_sql
        assert "PRIMARY KEY (symbol, date)" in executed_sql

    @patch("src.data_access.postgresql_access.get_connection_manager")
    def test_create_table_without_primary_key(self, mock_get_manager):
        """测试创建无主键表"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor

        mock_manager = Mock()
        mock_pool = Mock()
        mock_pool.getconn.return_value = mock_conn
        mock_manager.get_postgresql_connection.return_value = mock_pool
        mock_get_manager.return_value = mock_manager

        access = PostgreSQLDataAccess()

        schema = {"symbol": "VARCHAR(20)", "date": "DATE"}
        access.create_table("test_table", schema)

        executed_sql = mock_cursor.execute.call_args[0][0]
        assert "CREATE TABLE IF NOT EXISTS test_table" in executed_sql
        assert "PRIMARY KEY" not in executed_sql

    @patch("src.data_access.postgresql_access.get_connection_manager")
    def test_create_table_failure(self, mock_get_manager):
        """测试创建表失败"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.execute.side_effect = Exception("Database error")
        mock_conn.cursor.return_value = mock_cursor

        mock_manager = Mock()
        mock_pool = Mock()
        mock_pool.getconn.return_value = mock_conn
        mock_manager.get_postgresql_connection.return_value = mock_pool
        mock_get_manager.return_value = mock_manager

        access = PostgreSQLDataAccess()

        with pytest.raises(Exception, match="Database error"):
            access.create_table("test_table", {"symbol": "VARCHAR(20)"})

        mock_conn.rollback.assert_called_once()
        mock_cursor.close.assert_called_once()

    @patch("src.data_access.postgresql_access.get_connection_manager")
    def test_create_hypertable(self, mock_get_manager):
        """测试创建超表"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor

        mock_manager = Mock()
        mock_pool = Mock()
        mock_pool.getconn.return_value = mock_conn
        mock_manager.get_postgresql_connection.return_value = mock_pool
        mock_get_manager.return_value = mock_manager

        access = PostgreSQLDataAccess()

        access.create_hypertable("test_table", "time", "7 days")

        # 应该执行两次：启用扩展和创建超表
        assert mock_cursor.execute.call_count == 2
        mock_conn.commit.assert_called()

        # 验证SQL内容
        calls = [call[0][0] for call in mock_cursor.execute.call_args_list]
        assert any("CREATE EXTENSION IF NOT EXISTS timescaledb" in call for call in calls)
        assert any(
            "SELECT create_hypertable('test_table', 'time', chunk_time_interval => INTERVAL '7 days')" in call
            for call in calls
        )


class TestPostgreSQLDataAccessDataframe:
    """测试DataFrame操作"""

    @patch("src.data_access.postgresql_access.get_connection_manager")
    @patch("src.data_access.postgresql_access.execute_values")
    def test_insert_dataframe_success(self, mock_execute_values, mock_get_manager):
        """测试成功插入DataFrame"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor

        mock_manager = Mock()
        mock_pool = Mock()
        mock_pool.getconn.return_value = mock_conn
        mock_manager.get_postgresql_connection.return_value = mock_pool
        mock_get_manager.return_value = mock_manager

        access = PostgreSQLDataAccess()

        # 创建测试数据
        df = pd.DataFrame(
            {
                "symbol": ["AAPL", "GOOGL"],
                "date": ["2024-01-01", "2024-01-01"],
                "close": [150.0, 120.0],
                "volume": [1000000, 500000],
            }
        )

        result = access.insert_dataframe("test_table", df)

        assert result == len(df)
        mock_cursor.execute.assert_called()
        mock_execute_values.assert_called()
        mock_conn.commit.assert_called_once()
        mock_cursor.close.assert_called_once()

    @patch("src.data_access.postgresql_access.get_connection_manager")
    def test_insert_empty_dataframe(self, mock_get_manager):
        """测试插入空DataFrame"""
        access = PostgreSQLDataAccess()

        empty_df = pd.DataFrame()
        result = access.insert_dataframe("test_table", empty_df)

        assert result == 0

    @patch("src.data_access.postgresql_access.get_connection_manager")
    def test_upsert_dataframe(self, mock_get_manager):
        """测试更新插入DataFrame"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor

        mock_manager = Mock()
        mock_pool = Mock()
        mock_pool.getconn.return_value = mock_conn
        mock_manager.get_postgresql_connection.return_value = mock_pool
        mock_get_manager.return_value = mock_manager

        access = PostgreSQLDataAccess()

        df = pd.DataFrame({"symbol": ["AAPL"], "date": ["2024-01-01"], "close": [150.0]})

        access.upsert_dataframe(df=df, table_name="test_table", conflict_columns=["symbol", "date"])

        # 验证SQL执行
        mock_cursor.execute.assert_called()
        mock_conn.commit.assert_called()
        mock_cursor.close.assert_called()

        # 验证UPSERT语法
        executed_sql = mock_cursor.execute.call_args[0][0]
        assert "INSERT INTO test_table" in executed_sql
        assert "ON CONFLICT (symbol, date)" in executed_sql


class TestPostgreSQLDataAccessQuery:
    """测试查询功能"""

    @patch("src.data_access.postgresql_access.get_connection_manager")
    def test_query_basic(self, mock_get_manager):
        """测试基本查询"""
        # 模拟查询结果
        mock_records = [
            ("AAPL", "2024-01-01", 150.0, 1000000),
            ("GOOGL", "2024-01-01", 120.0, 500000),
        ]

        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = mock_records
        mock_cursor.description = [("symbol",), ("date",), ("close",), ("volume",)]
        mock_conn.cursor.return_value = mock_cursor

        mock_manager = Mock()
        mock_pool = Mock()
        mock_pool.getconn.return_value = mock_conn
        mock_manager.get_postgresql_connection.return_value = mock_pool
        mock_get_manager.return_value = mock_manager

        access = PostgreSQLDataAccess()

        result = access.query(
            table_name="test_table",
            columns=["symbol", "date", "close", "volume"],
            filters={"symbol": "AAPL"},
            order_by="date DESC",
            limit=10,
        )

        # 验证结果
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert list(result.columns) == ["symbol", "date", "close", "volume"]
        assert result.iloc[0]["symbol"] == "AAPL"

        # 验证SQL执行
        mock_cursor.execute.assert_called()
        mock_cursor.close.assert_called_once()

    @patch("src.data_access.postgresql_access.get_connection_manager")
    def test_query_by_time_range(self, mock_get_manager):
        """测试时间范围查询"""
        mock_records = [("AAPL", "2024-01-01", 150.0)]

        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = mock_records
        mock_cursor.description = [("symbol",), ("date",), ("close",)]
        mock_conn.cursor.return_value = mock_cursor

        mock_manager = Mock()
        mock_pool = Mock()
        mock_pool.getconn.return_value = mock_conn
        mock_manager.get_postgresql_connection.return_value = mock_pool
        mock_get_manager.return_value = mock_manager

        access = PostgreSQLDataAccess()

        start_time = datetime(2024, 1, 1)
        end_time = datetime(2024, 1, 2)

        result = access.query_by_time_range(
            table_name="test_table",
            time_column="date",
            start_time=start_time,
            end_time=end_time,
            filters={"symbol": "AAPL"},
        )

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1

        # 验证时间条件
        executed_sql = mock_cursor.execute.call_args[0][0]
        assert "date >= %s" in executed_sql
        assert "date <= %s" in executed_sql

    @patch("src.data_access.postgresql_access.get_connection_manager")
    def test_execute_sql(self, mock_get_manager):
        """测试执行原始SQL"""
        mock_records = [("AAPL", 150.0)]

        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = mock_records
        mock_cursor.description = [("symbol",), ("close",)]
        mock_conn.cursor.return_value = mock_cursor

        mock_manager = Mock()
        mock_pool = Mock()
        mock_pool.getconn.return_value = mock_conn
        mock_manager.get_postgresql_connection.return_value = mock_pool
        mock_get_manager.return_value = mock_manager

        access = PostgreSQLDataAccess()

        sql = "SELECT symbol, close FROM test_table WHERE symbol = %s"
        params = ("AAPL",)

        result = access.execute_sql(sql, params)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert result.iloc[0]["symbol"] == "AAPL"

        mock_cursor.execute.assert_called_with(sql, params)


class TestPostgreSQLDataAccessManagement:
    """测试管理功能"""

    @patch("src.data_access.postgresql_access.get_connection_manager")
    def test_delete(self, mock_get_manager):
        """测试删除操作"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.rowcount = 5
        mock_conn.cursor.return_value = mock_cursor

        mock_manager = Mock()
        mock_pool = Mock()
        mock_pool.getconn.return_value = mock_conn
        mock_manager.get_postgresql_connection.return_value = mock_pool
        mock_get_manager.return_value = mock_manager

        access = PostgreSQLDataAccess()

        result = access.delete("test_table", "symbol = %s", ("AAPL",))

        assert result == 5
        mock_cursor.execute.assert_called()
        mock_conn.commit.assert_called()
        mock_cursor.close.assert_called()

    @patch("src.data_access.postgresql_access.get_connection_manager")
    def test_get_table_stats(self, mock_get_manager):
        """测试获取表统计信息"""
        # 模拟统计信息
        mock_records = [(1000, "2024-01-01", "2024-12-31", 1024)]

        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = mock_records
        mock_conn.cursor.return_value = mock_cursor

        mock_manager = Mock()
        mock_pool = Mock()
        mock_pool.getconn.return_value = mock_conn
        mock_manager.get_postgresql_connection.return_value = mock_pool
        mock_get_manager.return_value = mock_manager

        access = PostgreSQLDataAccess()

        stats = access.get_table_stats("test_table")

        assert isinstance(stats, dict)
        assert "row_count" in stats
        assert stats["row_count"] == 1000
        assert "size_estimate" in stats

    @patch("src.data_access.postgresql_access.get_connection_manager")
    def test_save_data(self, mock_get_manager):
        """测试保存数据接口"""
        access = PostgreSQLDataAccess()

        df = pd.DataFrame({"test": [1, 2, 3]})
        result = access.save_data(df, "DAILY_MARKET_DATA", "test_table")

        # 根据实现，这应该调用 upsert_dataframe
        assert isinstance(result, bool)

    @patch("src.data_access.postgresql_access.get_connection_manager")
    def test_load_data(self, mock_get_manager):
        """测试加载数据接口"""
        mock_records = [("AAPL", 150.0)]

        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = mock_records
        mock_cursor.description = [("symbol",), ("close",)]
        mock_conn.cursor.return_value = mock_cursor

        mock_manager = Mock()
        mock_pool = Mock()
        mock_pool.getconn.return_value = mock_conn
        mock_manager.get_postgresql_connection.return_value = mock_pool
        mock_get_manager.return_value = mock_manager

        access = PostgreSQLDataAccess()

        result = access.load_data("test_table", symbol="AAPL")

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1

    @patch("src.data_access.postgresql_access.get_connection_manager")
    def test_close(self, mock_get_manager):
        """测试关闭连接"""
        mock_pool = Mock()
        mock_conn = Mock()

        mock_manager = Mock()
        mock_manager.get_postgresql_connection.return_value = mock_pool
        mock_pool.getconn.return_value = mock_conn
        mock_get_manager.return_value = mock_manager

        access = PostgreSQLDataAccess()
        access.pool = mock_pool
        access._get_connection()  # 获取一个连接

        access.close()

        mock_pool.putconn.assert_called_with(mock_conn)

    @patch("src.data_access.postgresql_access.get_connection_manager")
    def test_close_all(self, mock_get_manager):
        """测试关闭所有连接"""
        mock_pool = Mock()

        mock_manager = Mock()
        mock_manager.get_postgresql_connection.return_value = mock_pool
        mock_get_manager.return_value = mock_manager

        access = PostgreSQLDataAccess()
        access.pool = mock_pool

        access.close_all()

        mock_pool.closeall.assert_called_once()


class TestPostgreSQLDataAccessEdgeCases:
    """测试边界情况和错误处理"""

    @patch("src.data_access.postgresql_access.get_connection_manager")
    def test_query_no_results(self, mock_get_manager):
        """测试查询无结果"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = []
        mock_conn.cursor.return_value = mock_cursor

        mock_manager = Mock()
        mock_pool = Mock()
        mock_pool.getconn.return_value = mock_conn
        mock_manager.get_postgresql_connection.return_value = mock_pool
        mock_get_manager.return_value = mock_manager

        access = PostgreSQLDataAccess()

        result = access.query("test_table", columns=["symbol"])

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0

    @patch("src.data_access.postgresql_access.get_connection_manager")
    def test_insert_dataframe_with_missing_columns(self, mock_get_manager):
        """测试插入缺少列的DataFrame"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor

        mock_manager = Mock()
        mock_pool = Mock()
        mock_pool.getconn.return_value = mock_conn
        mock_manager.get_postgresql_connection.return_value = mock_pool
        mock_get_manager.return_value = mock_manager

        access = PostgreSQLDataAccess()

        # 创建只有一部分列的DataFrame
        df = pd.DataFrame({"symbol": ["AAPL"], "close": [150.0]})

        result = access.insert_dataframe("test_table", df)

        # 应该能够处理缺少列的情况
        assert isinstance(result, int)


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])
