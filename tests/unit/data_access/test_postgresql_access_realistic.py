"""
PostgreSQL Access 现实测试
基于实际代码实现的综合测试
目标覆盖率: 67%+
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))

from src.data_access.postgresql_access import PostgreSQLDataAccess


class TestPostgreSQLDataAccessRealistic:
    """基于实际代码实现的现实测试"""

    @patch("src.data_access.postgresql_access.get_connection_manager")
    def test_initialization(self, mock_get_manager):
        """测试初始化"""
        mock_manager = Mock()
        mock_get_manager.return_value = mock_manager

        access = PostgreSQLDataAccess()

        assert access.conn_manager == mock_manager
        assert access.pool is None

    @patch("src.data_access.postgresql_access.get_connection_manager")
    def test_connection_management(self, mock_get_manager):
        """测试连接管理"""
        mock_manager = Mock()
        mock_pool = Mock()
        mock_conn = Mock()
        mock_pool.getconn.return_value = mock_conn
        mock_manager.get_postgresql_connection.return_value = mock_pool
        mock_get_manager.return_value = mock_manager

        access = PostgreSQLDataAccess()

        # 测试获取连接
        conn = access._get_connection()
        assert conn == mock_conn
        assert access.pool == mock_pool

        # 测试归还连接
        access._return_connection(conn)
        mock_pool.putconn.assert_called_once_with(conn)

    @patch("src.data_access.postgresql_access.get_connection_manager")
    def test_create_table_success(self, mock_get_manager):
        """测试创建表成功"""
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

        access.create_table("stock_basic", schema, primary_key="symbol")

        # 验证SQL执行
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()
        mock_cursor.close.assert_called_once()

        # 验证SQL内容
        executed_sql = mock_cursor.execute.call_args[0][0]
        assert "CREATE TABLE IF NOT EXISTS stock_basic" in executed_sql
        assert "symbol VARCHAR(20)" in executed_sql
        assert "PRIMARY KEY (symbol)" in executed_sql

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

        access.create_hypertable("stock_basic", "time", "7 days")

        # 应该执行两次：启用扩展和创建超表
        assert mock_cursor.execute.call_count == 2
        mock_conn.commit.assert_called()

        # 验证SQL内容
        calls = [call[0][0] for call in mock_cursor.execute.call_args_list]
        assert any(
            "CREATE EXTENSION IF NOT EXISTS timescaledb" in call for call in calls
        )
        assert any(
            "SELECT create_hypertable('stock_basic', 'time'" in call for call in calls
        )

    @patch("src.data_access.postgresql_access.get_connection_manager")
    @patch("src.data_access.postgresql_access.execute_values")
    def test_insert_dataframe_success(self, mock_execute_values, mock_get_manager):
        """测试成功插入DataFrame"""
        # 模拟连接
        mock_conn = Mock()
        mock_cursor = Mock()
        # 设置必要的连接属性
        mock_cursor.connection.encoding = "UTF8"
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

        result = access.insert_dataframe("stock_basic", df)

        assert result == len(df)
        mock_cursor.execute.assert_called()
        mock_execute_values.assert_called()
        mock_conn.commit.assert_called_once()
        mock_cursor.close.assert_called_once()

    @patch("src.data_access.postgresql_access.get_connection_manager")
    def test_insert_empty_dataframe(self, mock_get_manager):
        """测试插入空DataFrame"""
        mock_manager = Mock()
        mock_get_manager.return_value = mock_manager

        access = PostgreSQLDataAccess()

        empty_df = pd.DataFrame()
        result = access.insert_dataframe("stock_basic", empty_df)

        assert result == 0

    @patch("src.data_access.postgresql_access.get_connection_manager")
    def test_query_with_allowed_table(self, mock_get_manager):
        """测试允许的表查询"""
        # 模拟查询结果
        mock_records = [
            ("AAPL", "2024-01-01", 150.0, 1000000),
            ("GOOGL", "2024-01-01", 120.0, 500000),
        ]

        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = mock_records
        mock_cursor.description = [
            ("symbol", None, None, None, None, None, None),
            ("date", None, None, None, None, None, None),
            ("close", None, None, None, None, None, None),
            ("volume", None, None, None, None, None, None),
        ]
        mock_conn.cursor.return_value = mock_cursor

        mock_manager = Mock()
        mock_pool = Mock()
        mock_pool.getconn.return_value = mock_conn
        mock_manager.get_postgresql_connection.return_value = mock_pool
        mock_get_manager.return_value = mock_manager

        access = PostgreSQLDataAccess()

        result = access.query(
            table_name="stock_basic",  # 使用允许的表名
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
    def test_query_invalid_table(self, mock_get_manager):
        """测试无效表名"""
        mock_manager = Mock()
        mock_get_manager.return_value = mock_manager

        access = PostgreSQLDataAccess()

        with pytest.raises(ValueError, match="Invalid table name"):
            access.query("invalid_table", columns=["symbol"])

    @patch("src.data_access.postgresql_access.get_connection_manager")
    def test_query_by_time_range(self, mock_get_manager):
        """测试时间范围查询"""
        mock_records = [("AAPL", "2024-01-01", 150.0)]

        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = mock_records
        mock_cursor.description = [
            ("symbol", None, None, None, None, None, None),
            ("date", None, None, None, None, None, None),
            ("close", None, None, None, None, None, None),
        ]
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
            table_name="stock_basic",
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
        mock_cursor.description = [
            ("symbol", None, None, None, None, None, None),
            ("close", None, None, None, None, None, None),
        ]
        mock_conn.cursor.return_value = mock_cursor

        mock_manager = Mock()
        mock_pool = Mock()
        mock_pool.getconn.return_value = mock_conn
        mock_manager.get_postgresql_connection.return_value = mock_pool
        mock_get_manager.return_value = mock_manager

        access = PostgreSQLDataAccess()

        sql = "SELECT symbol, close FROM stock_basic WHERE symbol = %s"
        params = ("AAPL",)

        result = access.execute_sql(sql, params)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert result.iloc[0]["symbol"] == "AAPL"

        mock_cursor.execute.assert_called_with(sql, params)

    @patch("src.data_access.postgresql_access.get_connection_manager")
    def test_delete_operation(self, mock_get_manager):
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

        result = access.delete("stock_basic", "symbol = %s", ("AAPL",))

        assert result == 5
        mock_cursor.execute.assert_called()
        mock_conn.commit.assert_called()
        mock_cursor.close.assert_called()

    @patch("src.data_access.postgresql_access.get_connection_manager")
    def test_get_table_stats(self, mock_get_manager):
        """测试获取表统计信息"""
        # 模拟统计信息查询失败情况
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = []  # 返回空列表
        mock_conn.cursor.return_value = mock_cursor

        mock_manager = Mock()
        mock_pool = Mock()
        mock_pool.getconn.return_value = mock_conn
        mock_manager.get_postgresql_connection.return_value = mock_pool
        mock_get_manager.return_value = mock_manager

        access = PostgreSQLDataAccess()

        stats = access.get_table_stats("stock_basic")

        assert isinstance(stats, dict)
        assert "row_count" in stats
        assert stats["row_count"] == 0  # 由于查询返回空，行数为0

    @patch("src.data_access.postgresql_access.get_connection_manager")
    def test_upsert_dataframe(self, mock_get_manager):
        """测试更新插入DataFrame"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.connection.encoding = "UTF8"
        mock_conn.cursor.return_value = mock_cursor

        mock_manager = Mock()
        mock_pool = Mock()
        mock_pool.getconn.return_value = mock_conn
        mock_manager.get_postgresql_connection.return_value = mock_pool
        mock_get_manager.return_value = mock_manager

        access = PostgreSQLDataAccess()

        df = pd.DataFrame(
            {"symbol": ["AAPL"], "date": ["2024-01-01"], "close": [150.0]}
        )

        access.upsert_dataframe(
            df=df, table_name="stock_basic", conflict_columns=["symbol", "date"]
        )

        # 验证SQL执行
        mock_cursor.execute.assert_called()
        mock_conn.commit.assert_called()
        mock_cursor.close.assert_called()

        # 验证UPSERT语法
        executed_sql = mock_cursor.execute.call_args[0][0]
        assert "INSERT INTO stock_basic" in executed_sql
        assert "ON CONFLICT (symbol, date)" in executed_sql

    @patch("src.data_access.postgresql_access.get_connection_manager")
    def test_save_data_interface(self, mock_get_manager):
        """测试保存数据接口"""
        access = PostgreSQLDataAccess()

        df = pd.DataFrame({"symbol": ["AAPL"], "close": [150.0]})
        result = access.save_data(df, "DAILY_MARKET_DATA", "stock_basic")

        # 根据实现，这应该返回 True/False
        assert isinstance(result, bool)

    @patch("src.data_access.postgresql_access.get_connection_manager")
    def test_load_data_interface(self, mock_get_manager):
        """测试加载数据接口"""
        mock_records = [("AAPL", 150.0)]

        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = mock_records
        mock_cursor.description = [
            ("symbol", None, None, None, None, None, None),
            ("close", None, None, None, None, None, None),
        ]
        mock_conn.cursor.return_value = mock_cursor

        mock_manager = Mock()
        mock_pool = Mock()
        mock_pool.getconn.return_value = mock_conn
        mock_manager.get_postgresql_connection.return_value = mock_pool
        mock_get_manager.return_value = mock_manager

        access = PostgreSQLDataAccess()

        result = access.load_data("stock_basic", symbol="AAPL")

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1

    @patch("src.data_access.postgresql_access.get_connection_manager")
    def test_close_operations(self, mock_get_manager):
        """测试关闭操作"""
        mock_pool = Mock()
        mock_conn = Mock()

        mock_manager = Mock()
        mock_manager.get_postgresql_connection.return_value = mock_pool
        mock_pool.getconn.return_value = mock_conn
        mock_get_manager.return_value = mock_manager

        access = PostgreSQLDataAccess()

        # 测试单个关闭
        access.pool = mock_pool
        access.close()
        # close方法应该不会报错

        # 测试关闭所有
        access.close_all()
        mock_pool.closeall.assert_called_once()


class TestPostgreSQLDataAccessErrorHandling:
    """测试错误处理"""

    @patch("src.data_access.postgresql_access.get_connection_manager")
    def test_table_creation_failure(self, mock_get_manager):
        """测试表创建失败"""
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
            access.create_table("stock_basic", {"symbol": "VARCHAR(20)"})

        mock_conn.rollback.assert_called_once()
        mock_cursor.close.assert_called_once()

    @patch("src.data_access.postgresql_access.get_connection_manager")
    def test_query_no_results(self, mock_get_manager):
        """测试查询无结果"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = []
        mock_cursor.description = []
        mock_conn.cursor.return_value = mock_cursor

        mock_manager = Mock()
        mock_pool = Mock()
        mock_pool.getconn.return_value = mock_conn
        mock_manager.get_postgresql_connection.return_value = mock_pool
        mock_get_manager.return_value = mock_manager

        access = PostgreSQLDataAccess()

        result = access.query("stock_basic", columns=["symbol"])

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0

    @patch("src.data_access.postgresql_access.get_connection_manager")
    def test_invalid_columns(self, mock_get_manager):
        """测试无效列名"""
        mock_manager = Mock()
        mock_get_manager.return_value = mock_manager

        access = PostgreSQLDataAccess()

        with pytest.raises(ValueError, match="Invalid column"):
            access.query("stock_basic", columns=["invalid_column"])


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])
