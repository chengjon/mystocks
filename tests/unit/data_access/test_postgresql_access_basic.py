"""
PostgreSQL访问层基础测试 - 增强版
专注于提升PostgreSQL数据访问层覆盖率，目标 > 67%
"""

import os
import sys
from unittest.mock import Mock, patch
from datetime import datetime

import pandas as pd
import pytest

# 添加源码路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../src"))

# 测试目标模块
from src.data_access.postgresql_access import PostgreSQLDataAccess


class TestPostgreSQLDataAccessBasic:
    """PostgreSQLDataAccess基础测试 - 专注覆盖率"""

    @pytest.fixture
    def data_access(self):
        with patch("src.data_access.postgresql_access.get_connection_manager") as mock_cm:
            mock_conn_manager = Mock()
            mock_cm.return_value = mock_conn_manager
            access = PostgreSQLDataAccess()
            access.pool = Mock()
            return access

    def test_class_import_compatibility(self):
        """测试类导入兼容性"""
        from src.data_access.postgresql_access import PostgreSQLDataAccess

        assert PostgreSQLDataAccess is not None

    def test_initialization(self):
        """测试初始化"""
        with patch("src.data_access.postgresql_access.get_connection_manager") as mock_cm:
            mock_conn_manager = Mock()
            mock_cm.return_value = mock_conn_manager
            data_access = PostgreSQLDataAccess()
            assert data_access.conn_manager == mock_conn_manager
            assert data_access.pool is None

    def test_get_connection_method(self, data_access):
        """测试获取连接方法"""
        mock_conn = Mock()
        data_access.pool.getconn.return_value = mock_conn

        conn = data_access._get_connection()
        assert conn == mock_conn
        assert data_access.pool.getconn.call_count == 1

    def test_return_connection_method(self, data_access):
        """测试归还连接方法"""
        test_conn = Mock()
        data_access._return_connection(test_conn)
        data_access.pool.putconn.assert_called_once_with(test_conn)

    def test_create_table_method(self, data_access):
        """测试创建表方法"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        data_access.pool.getconn.return_value = mock_conn

        schema = {"id": "SERIAL PRIMARY KEY", "name": "VARCHAR(100)"}
        data_access.create_table("daily_kline", schema, "id")

        assert mock_cursor.execute.called
        sql_call = mock_cursor.execute.call_args[0][0]
        assert "CREATE TABLE IF NOT EXISTS daily_kline" in sql_call

    def test_create_table_error(self, data_access):
        """测试创建表异常"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.execute.side_effect = Exception("DB Error")
        mock_conn.cursor.return_value = mock_cursor
        data_access.pool.getconn.return_value = mock_conn

        with pytest.raises(Exception, match="DB Error"):
            data_access.create_table("daily_kline", {"a": "int"})
        assert mock_conn.rollback.called

    def test_create_hypertable_method(self, data_access):
        """测试创建超表方法"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        data_access.pool.getconn.return_value = mock_conn

        data_access.create_hypertable("daily_kline", "time_col")

        assert mock_cursor.execute.called
        assert "create_hypertable" in mock_cursor.execute.call_args[0][0]

    def test_create_hypertable_error(self, data_access):
        """测试创建超表异常"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.execute.side_effect = Exception("Hyper Error")
        mock_conn.cursor.return_value = mock_cursor
        data_access.pool.getconn.return_value = mock_conn

        with pytest.raises(Exception, match="Hyper Error"):
            data_access.create_hypertable("daily_kline")
        assert mock_conn.rollback.called

    def test_insert_dataframe_method(self, data_access):
        """测试插入DataFrame方法"""
        test_df = pd.DataFrame({"symbol": ["AAPL"], "close": [150.0]})

        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.connection.encoding = "UTF8"
        mock_cursor.rowcount = 1
        mock_conn.cursor.return_value = mock_cursor
        data_access.pool.getconn.return_value = mock_conn

        with patch("src.data_access.postgresql_access.execute_values") as mock_execute:
            result = data_access.insert_dataframe("daily_kline", test_df)
            assert result == 1
            assert mock_execute.called

    def test_insert_dataframe_empty(self, data_access):
        """测试插入空DataFrame"""
        assert data_access.insert_dataframe("table", pd.DataFrame()) == 0

    def test_insert_dataframe_error(self, data_access):
        """测试插入DataFrame异常"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.execute.side_effect = Exception("Insert Error")
        mock_conn.cursor.return_value = mock_cursor
        data_access.pool.getconn.return_value = mock_conn

        with patch(
            "src.data_access.postgresql_access.execute_values",
            side_effect=Exception("Insert Error"),
        ):
            with pytest.raises(Exception, match="Insert Error"):
                data_access.insert_dataframe("daily_kline", pd.DataFrame({"a": [1]}))
            assert mock_conn.rollback.called

    def test_upsert_dataframe_method(self, data_access):
        """测试upsert DataFrame方法"""
        test_df = pd.DataFrame({"symbol": ["AAPL"], "close": [150.0]})

        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.connection.encoding = "UTF8"
        mock_cursor.rowcount = 1
        mock_conn.cursor.return_value = mock_cursor
        data_access.pool.getconn.return_value = mock_conn

        with patch("src.data_access.postgresql_access.execute_values") as mock_execute:
            result = data_access.upsert_dataframe("daily_kline", test_df, conflict_columns=["symbol"])
            assert result == 1
            assert mock_execute.called

    def test_upsert_dataframe_empty(self, data_access):
        """测试Upsert空数据"""
        assert data_access.upsert_dataframe("table", pd.DataFrame(), ["id"]) == 0

    def test_upsert_dataframe_error(self, data_access):
        """测试Upsert异常"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        data_access.pool.getconn.return_value = mock_conn
        with patch(
            "src.data_access.postgresql_access.execute_values",
            side_effect=Exception("Upsert Error"),
        ):
            with pytest.raises(Exception, match="Upsert Error"):
                data_access.upsert_dataframe("daily_kline", pd.DataFrame({"a": [1]}), ["a"])
            assert mock_conn.rollback.called

    def test_query_method_full(self, data_access):
        """全面测试查询方法，包括列验证、排序、限制"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.description = [("symbol",), ("close",)]
        mock_cursor.fetchall.return_value = [("AAPL", 150.0)]
        mock_conn.cursor.return_value = mock_cursor
        data_access.pool.getconn.return_value = mock_conn

        # 测试带列验证和排序
        result = data_access.query(
            "daily_kline",
            columns=["symbol", "close"],
            where="symbol = %s",
            order_by="date DESC",
            limit=10,
        )
        assert isinstance(result, pd.DataFrame)

    def test_query_invalid_columns(self, data_access):
        """测试非法列名拦截"""
        with pytest.raises(ValueError, match="Invalid column name"):
            data_access.query("daily_kline", columns=["drop_table"])

    def test_query_invalid_order_by(self, data_access):
        """测试非法排序字段拦截"""
        with pytest.raises(ValueError, match="Invalid order field"):
            data_access.query("daily_kline", order_by="secret_col DESC")

    def test_query_invalid_limit(self, data_access):
        """测试非法Limit拦截"""
        with pytest.raises(ValueError, match="Invalid limit value"):
            data_access.query("daily_kline", limit=-1)
        with pytest.raises(ValueError, match="Invalid limit value"):
            data_access.query("daily_kline", limit=999999)

    def test_query_dangerous_where(self, data_access):
        """测试危险WHERE子句拦截"""
        with pytest.raises(ValueError, match="Potentially dangerous SQL"):
            data_access.query("daily_kline", where="symbol = 'AAPL'; DROP TABLE users")

    def test_query_invalid_table(self, data_access):
        """测试非法表名拦截"""
        with pytest.raises(ValueError, match="Invalid table name"):
            data_access.query("drop_everything")

    def test_query_by_time_range(self, data_access):
        """测试时间范围查询"""
        with patch.object(data_access, "query", return_value=pd.DataFrame()) as mock_q:
            data_access.query_by_time_range(
                "daily_kline",
                "date",
                datetime(2024, 1, 1),
                datetime(2024, 1, 2),
                filters="close > 100",
            )
            mock_q.assert_called_once()

    def test_execute_sql_method(self, data_access):
        """测试执行SQL方法"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.description = [("count",)]
        mock_cursor.fetchall.return_value = [(100,)]
        mock_conn.cursor.return_value = mock_cursor
        data_access.pool.getconn.return_value = mock_conn

        result = data_access.execute_sql("SELECT COUNT(*) FROM daily_kline")
        assert len(result) == 1
        assert result.iloc[0].iloc[0] == 100

    def test_execute_sql_error(self, data_access):
        """测试SQL执行错误"""
        mock_conn = Mock()
        data_access.pool.getconn.return_value = mock_conn
        with patch("pandas.read_sql", side_effect=Exception("SQL Error")):
            with pytest.raises(Exception, match="SQL Error"):
                data_access.execute_sql("SELECT 1")

    def test_delete_method(self, data_access):
        """测试删除方法"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.rowcount = 5
        mock_conn.cursor.return_value = mock_cursor
        data_access.pool.getconn.return_value = mock_conn

        # 带参数
        assert data_access.delete("daily_kline", "symbol = %s", ("AAPL",)) == 5

        # 不带参数（字面量验证）
        assert data_access.delete("daily_kline", "volume > 0") == 5

    def test_delete_invalid_table(self, data_access):
        """测试删除非法表名"""
        with pytest.raises(ValueError, match="Invalid table name"):
            data_access.delete("forbidden", "1=1")

    def test_delete_dangerous_where(self, data_access):
        """测试删除危险WHERE拦截"""
        with pytest.raises(ValueError, match="Potentially dangerous SQL"):
            data_access.delete("daily_kline", "1=1; DROP TABLE students")

    def test_delete_error(self, data_access):
        """测试删除异常"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.execute.side_effect = Exception("Delete Error")
        mock_conn.cursor.return_value = mock_cursor
        data_access.pool.getconn.return_value = mock_conn
        with pytest.raises(Exception, match="Delete Error"):
            data_access.delete("daily_kline", "1=1")
        assert mock_conn.rollback.called

    def test_get_table_stats_method(self, data_access):
        """测试获取表统计方法"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (1000, "50 MB")
        mock_conn.cursor.return_value = mock_cursor
        data_access.pool.getconn.return_value = mock_conn

        result = data_access.get_table_stats("daily_kline")
        assert result["row_count"] == 1000
        assert result["total_size"] == "50 MB"

    def test_get_table_stats_error(self, data_access):
        """测试获取统计错误"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.execute.side_effect = Exception("Stats Error")
        mock_conn.cursor.return_value = mock_cursor
        data_access.pool.getconn.return_value = mock_conn

        result = data_access.get_table_stats("daily_kline")
        assert result["row_count"] == 0

    def test_save_data_interface(self, data_access):
        """全面测试DataManager适配器接口 save_data"""
        # 普通模式
        with patch.object(data_access, "insert_dataframe", return_value=1) as m:
            assert data_access.save_data(pd.DataFrame({"a": [1]}), None, "daily_kline") is True
            m.assert_called_once()

        # Upsert模式
        with patch.object(data_access, "upsert_dataframe", return_value=1) as m:
            assert data_access.save_data(pd.DataFrame({"a": [1]}), None, "daily_kline", upsert=True) is True
            m.assert_called_once()

    def test_save_data_interface_error(self, data_access):
        """测试save_data接口错误"""
        with patch.object(data_access, "insert_dataframe", side_effect=Exception("Save Error")):
            assert data_access.save_data(pd.DataFrame({"a": [1]}), None, "daily_kline") is False

    def test_load_data_interface(self, data_access):
        """全面测试DataManager适配器接口 load_data"""
        mock_df = pd.DataFrame({"a": [1]})

        # 1. 时间范围分支
        with patch.object(data_access, "query_by_time_range", return_value=mock_df) as m:
            result = data_access.load_data("daily_kline", start_time="2024", end_time="2025")
            assert len(result) == 1
            m.assert_called_once()

        # 2. where 分支
        with patch.object(data_access, "query", return_value=mock_df) as m:
            result = data_access.load_data("daily_kline", where="id=1", limit=5)
            assert len(result) == 1
            m.assert_called_once()

        # 3. 全表分支
        with patch.object(data_access, "execute_sql", return_value=mock_df) as m:
            result = data_access.load_data("daily_kline", limit=10)
            assert len(result) == 1
            m.assert_called_once()

    def test_load_data_interface_error(self, data_access):
        """测试load_data接口错误"""
        with patch.object(data_access, "execute_sql", side_effect=Exception("Load Error")):
            assert data_access.load_data("daily_kline") is None

    def test_close_method(self, data_access):
        """测试关闭方法"""
        pool_ref = data_access.pool
        data_access.close()
        pool_ref.closeall.assert_called_once()
        assert data_access.pool is None


if __name__ == "__main__":
    pytest.main([__file__])
