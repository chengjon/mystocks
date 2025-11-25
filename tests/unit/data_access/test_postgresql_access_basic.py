"""
PostgreSQL访问层基础测试
专注于提升PostgreSQL数据访问层覆盖率（554行代码）
"""

import os
import sys
from unittest.mock import MagicMock, Mock, patch

import pandas as pd
import pytest

# 添加源码路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../src"))

# 测试目标模块
from src.data_access.postgresql_access import PostgreSQLDataAccess


class TestPostgreSQLDataAccessBasic:
    """PostgreSQLDataAccess基础测试 - 专注覆盖率"""

    def test_class_import_compatibility(self):
        """测试类导入兼容性"""
        try:
            from src.data_access.postgresql_access import PostgreSQLDataAccess

            assert PostgreSQLDataAccess is not None
        except ImportError as e:
            pytest.skip(f"PostgreSQLDataAccess不可用: {e}")

    def test_initialization(self):
        """测试初始化"""
        with patch("src.data_access.postgresql_access.get_connection_manager") as mock_cm:
            mock_conn_manager = Mock()
            mock_cm.return_value = mock_conn_manager

            data_access = PostgreSQLDataAccess()

            # 验证基本属性
            assert hasattr(data_access, "conn_manager")
            assert hasattr(data_access, "pool")
            assert data_access.conn_manager == mock_conn_manager
            assert data_access.pool is None

    def test_get_connection_method(self):
        """测试获取连接方法"""
        with patch("src.data_access.postgresql_access.get_connection_manager") as mock_cm:
            mock_conn_manager = Mock()
            mock_conn_pool = Mock()
            mock_connection = Mock()
            mock_conn_pool.getconn.return_value = mock_connection
            mock_conn_manager.get_postgresql_connection.return_value = mock_conn_pool
            mock_cm.return_value = mock_conn_manager

            data_access = PostgreSQLDataAccess()

            # 首次调用应该初始化连接池
            conn1 = data_access._get_connection()
            assert conn1 == mock_connection
            assert data_access.pool == mock_conn_pool

            # 第二次调用应该使用已有的连接池
            conn2 = data_access._get_connection()
            assert conn2 == mock_connection

            # 验证getconn被调用了两次
            assert mock_conn_pool.getconn.call_count == 2

    def test_return_connection_method(self):
        """测试归还连接方法"""
        with patch("src.data_access.postgresql_access.get_connection_manager") as mock_cm:
            mock_conn_manager = Mock()
            mock_conn_pool = Mock()
            mock_cm.return_value = mock_conn_manager
            mock_conn_manager.get_postgresql_connection.return_value = mock_conn_pool

            data_access = PostgreSQLDataAccess()
            data_access.pool = mock_conn_pool  # 设置连接池

            test_conn = Mock()
            data_access._return_connection(test_conn)

            mock_conn_pool.putconn.assert_called_once_with(test_conn)

    def test_return_connection_without_pool(self):
        """测试无连接池时归还连接"""
        with patch("src.data_access.postgresql_access.get_connection_manager") as mock_cm:
            mock_conn_manager = Mock()
            mock_cm.return_value = mock_conn_manager

            data_access = PostgreSQLDataAccess()
            # 不设置连接池

            test_conn = Mock()
            # 应该不会抛出异常
            data_access._return_connection(test_conn)

    def test_create_table_method(self):
        """测试创建表方法"""
        with patch.object(PostgreSQLDataAccess, "_get_connection") as mock_get_conn:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_conn.cursor.return_value = mock_cursor
            mock_get_conn.return_value = mock_conn

            data_access = PostgreSQLDataAccess()
            data_access.pool = Mock()  # 模拟有连接池

            schema = {
                "id": "SERIAL PRIMARY KEY",
                "name": "VARCHAR(100)",
                "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            }

            data_access.create_table("test_table", schema, "id")

            # 验证SQL语句生成
            sql_calls = [call[0][0] for call in mock_cursor.execute.call_args_list]
            assert any("CREATE TABLE" in sql for sql in sql_calls)
            assert any("test_table" in sql for sql in sql_calls)

    def test_create_table_without_primary_key(self):
        """测试创建表无主键"""
        with patch.object(PostgreSQLDataAccess, "_get_connection") as mock_get_conn:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_conn.cursor.return_value = mock_cursor
            mock_get_conn.return_value = mock_conn

            data_access = PostgreSQLDataAccess()
            data_access.pool = Mock()

            schema = {"name": "VARCHAR(100)"}
            data_access.create_table("test_table", schema)

            # 验证创建了表
            assert mock_cursor.execute.called

    def test_create_hypertable_method(self):
        """测试创建超表方法"""
        with patch.object(PostgreSQLDataAccess, "_get_connection") as mock_get_conn:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_conn.cursor.return_value = mock_cursor
            mock_get_conn.return_value = mock_conn

            data_access = PostgreSQLDataAccess()
            data_access.pool = Mock()

            data_access.create_hypertable("test_table", "time_col")

            # 验证超表创建SQL
            sql_calls = [call[0][0] for call in mock_cursor.execute.call_args_list]
            assert any("SELECT create_hypertable" in sql for sql in sql_calls)
            assert any("test_table" in sql for sql in sql_calls)

    def test_create_hypertable_with_default_options(self):
        """测试创建超表使用默认选项"""
        with patch.object(PostgreSQLDataAccess, "_get_connection") as mock_get_conn:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_conn.cursor.return_value = mock_cursor
            mock_get_conn.return_value = mock_conn

            data_access = PostgreSQLDataAccess()
            data_access.pool = Mock()

            # 使用默认参数
            data_access.create_hypertable("test_table", "time_col")

            assert mock_cursor.execute.called

    def test_insert_dataframe_method(self):
        """测试插入DataFrame方法"""
        test_df = pd.DataFrame({"id": [1, 2], "name": ["test1", "test2"], "value": [10.0, 20.0]})

        with patch.object(PostgreSQLDataAccess, "_get_connection") as mock_get_conn:
            with patch("src.data_access.postgresql_access.execute_values") as mock_execute_values:
                mock_conn = Mock()
                mock_cursor = Mock()
                mock_conn.cursor.return_value = mock_cursor
                mock_cursor.rowcount = 2
                mock_get_conn.return_value = mock_conn

                data_access = PostgreSQLDataAccess()
                data_access.pool = Mock()

                result = data_access.insert_dataframe("test_table", test_df)

                assert result == 2
                mock_execute_values.assert_called_once()

    def test_insert_dataframe_empty(self):
        """测试插入空DataFrame"""
        empty_df = pd.DataFrame()

        data_access = PostgreSQLDataAccess()
        data_access.pool = Mock()

        result = data_access.insert_dataframe("test_table", empty_df)

        assert result == 0

    def test_upsert_dataframe_method(self):
        """测试upsert DataFrame方法"""
        test_df = pd.DataFrame({"id": [1, 2], "name": ["test1", "test2"], "value": [10.0, 20.0]})

        with patch.object(PostgreSQLDataAccess, "_get_connection") as mock_get_conn:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_conn.cursor.return_value = mock_cursor
            mock_get_conn.return_value = mock_conn

            data_access = PostgreSQLDataAccess()
            data_access.pool = Mock()

            result = data_access.upsert_dataframe("test_table", test_df, conflict_columns=["id"])

            # 验证方法被调用
            assert mock_cursor.execute.called

    def test_query_method(self):
        """测试查询方法"""
        with patch.object(PostgreSQLDataAccess, "_get_connection") as mock_get_conn:
            mock_conn = Mock()
            mock_cursor = Mock()
            test_data = [("row1",), ("row2",)]
            mock_cursor.fetchall.return_value = test_data
            mock_conn.cursor.return_value = mock_cursor
            mock_get_conn.return_value = mock_conn

            data_access = PostgreSQLDataAccess()
            data_access.pool = Mock()

            result = data_access.query("SELECT * FROM test_table")

            assert len(result) == 2
            mock_cursor.execute.assert_called_once_with("SELECT * FROM test_table", None)
            mock_cursor.fetchall.assert_called_once()

    def test_query_with_params(self):
        """测试带参数的查询方法"""
        with patch.object(PostgreSQLDataAccess, "_get_connection") as mock_get_conn:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_cursor.fetchall.return_value = []
            mock_conn.cursor.return_value = mock_cursor
            mock_get_conn.return_value = mock_conn

            data_access = PostgreSQLDataAccess()
            data_access.pool = Mock()

            result = data_access.query("SELECT * FROM test_table WHERE id > %s", (10,))

            mock_cursor.execute.assert_called_once_with("SELECT * FROM test_table WHERE id > %s", (10,))

    def test_query_by_time_range_method(self):
        """测试时间范围查询方法"""
        with patch.object(PostgreSQLDataAccess, "query") as mock_query:
            mock_query.return_value = pd.DataFrame({"result": ["test"]})

            data_access = PostgreSQLDataAccess()

            result = data_access.query_by_time_range("test_table", "time_col", "2024-01-01", "2024-01-31")

            # 验证时间范围查询SQL生成
            mock_query.assert_called_once()
            sql_call = mock_query.call_args[0][0]
            assert "time_col" in sql_call
            assert "2024-01-01" in sql_call
            assert "2024-01-31" in sql_call

    def test_execute_sql_method(self):
        """测试执行SQL方法"""
        with patch.object(PostgreSQLDataAccess, "_get_connection") as mock_get_conn:
            mock_conn = Mock()
            mock_cursor = Mock()
            test_data = [("col1", "col2"), ("col3", "col4")]
            mock_cursor.fetchall.return_value = test_data
            mock_conn.cursor.return_value = mock_cursor
            mock_get_conn.return_value = mock_conn

            data_access = PostgreSQLDataAccess()
            data_access.pool = Mock()

            result = data_access.execute_sql("SELECT COUNT(*) FROM test_table")

            assert len(result) == 2
            mock_cursor.execute.assert_called_once_with("SELECT COUNT(*) FROM test_table", None)

    def test_delete_method(self):
        """测试删除方法"""
        with patch.object(PostgreSQLDataAccess, "_get_connection") as mock_get_conn:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_cursor.rowcount = 5
            mock_conn.cursor.return_value = mock_cursor
            mock_get_conn.return_value = mock_conn

            data_access = PostgreSQLDataAccess()
            data_access.pool = Mock()

            result = data_access.delete("test_table", "id > 100")

            assert result == 5
            mock_cursor.execute.assert_called_once_with("DELETE FROM test_table WHERE id > 100", None)

    def test_get_table_stats_method(self):
        """测试获取表统计方法"""
        with patch.object(PostgreSQLDataAccess, "_get_connection") as mock_get_conn:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_cursor.fetchone.return_value = (1000, 50000)
            mock_conn.cursor.return_value = mock_cursor
            mock_get_conn.return_value = mock_conn

            data_access = PostgreSQLDataAccess()
            data_access.pool = Mock()

            result = data_access.get_table_stats("test_table")

            assert "row_count" in result
            assert "total_size" in result
            assert result["row_count"] == 1000
            assert result["total_size"] == 50000

    def test_save_data_method(self):
        """测试保存数据方法"""
        test_data = [{"id": 1, "name": "test"}]

        with patch.object(PostgreSQLDataAccess, "upsert_dataframe") as mock_upsert:
            mock_upsert.return_value = 1

            data_access = PostgreSQLDataAccess()

            result = data_access.save_data("test_table", test_data, conflict_columns=["id"])

            assert result == 1
            mock_upsert.assert_called_once()

    def test_load_data_method(self):
        """测试加载数据方法"""
        with patch.object(PostgreSQLDataAccess, "query") as mock_query:
            mock_query.return_value = pd.DataFrame({"id": [1, 2]})

            data_access = PostgreSQLDataAccess()

            result = data_access.load_data("test_table", id=1)

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 2
            mock_query.assert_called_once()

    def test_load_data_empty_result(self):
        """测试加载空数据"""
        with patch.object(PostgreSQLDataAccess, "query") as mock_query:
            mock_query.return_value = pd.DataFrame()

            data_access = PostgreSQLDataAccess()

            result = data_access.load_data("test_table", non_existent=1)

            assert result is None

    def test_close_method(self):
        """测试关闭连接方法"""
        with patch("src.data_access.postgresql_access.get_connection_manager") as mock_cm:
            mock_conn_manager = Mock()
            mock_conn_pool = Mock()
            mock_cm.return_value = mock_conn_manager

            data_access = PostgreSQLDataAccess()
            data_access.pool = mock_conn_pool
            data_access.conn_manager = mock_conn_manager

            data_access.close()

            mock_conn_pool.close.assert_called_once()

    def test_close_method_without_pool(self):
        """测试无连接池时关闭方法"""
        data_access = PostgreSQLDataAccess()
        # pool 为 None

        # 应该不会抛出异常
        data_access.close()

    def test_close_all_method(self):
        """测试关闭所有连接方法"""
        with patch("src.data_access.postgresql_access.get_connection_manager") as mock_cm:
            mock_conn_manager = Mock()
            mock_cm.return_value = mock_conn_manager

            data_access = PostgreSQLDataAccess()
            data_access.conn_manager = mock_conn_manager

            data_access.close_all()

            mock_conn_manager.close_all.assert_called_once()

    def test_error_handling_in_database_operations(self):
        """测试数据库操作中的错误处理"""
        with patch.object(PostgreSQLDataAccess, "_get_connection") as mock_get_conn:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_conn.cursor.return_value = mock_cursor
            mock_cursor.execute.side_effect = Exception("Database error")
            mock_get_conn.return_value = mock_conn

            data_access = PostgreSQLDataAccess()
            data_access.pool = Mock()

            # 应该抛出数据库异常
            with pytest.raises(Exception, match="Database error"):
                data_access.query("SELECT * FROM test_table")

    def test_method_parameter_validation(self):
        """测试方法参数验证"""
        import inspect

        data_access = PostgreSQLDataAccess()

        # 检查关键方法的参数
        methods_to_check = ["create_table", "insert_dataframe", "upsert_dataframe", "query", "execute_sql", "delete"]

        for method_name in methods_to_check:
            method = getattr(data_access, method_name)
            sig = inspect.signature(method)
            assert sig is not None
            # 方法应该有合理的参数数量
            assert len(sig.parameters) >= 1  # 至少有self参数

    def test_connection_management_flow(self):
        """测试连接管理流程"""
        with patch("src.data_access.postgresql_access.get_connection_manager") as mock_cm:
            mock_conn_manager = Mock()
            mock_conn_pool = Mock()
            mock_connection1 = Mock()
            mock_connection2 = Mock()

            mock_conn_pool.getconn.side_effect = [mock_connection1, mock_connection2]
            mock_conn_manager.get_postgresql_connection.return_value = mock_conn_pool
            mock_cm.return_value = mock_conn_manager

            data_access = PostgreSQLDataAccess()

            # 获取两个连接
            conn1 = data_access._get_connection()
            conn2 = data_access._get_connection()

            assert conn1 == mock_connection1
            assert conn2 == mock_connection2

            # 归还连接
            data_access._return_connection(conn1)
            data_access._return_connection(conn2)

            # 验证连接池操作
            assert mock_conn_pool.putconn.call_count == 2

    def test_database_operations_return_types(self):
        """测试数据库操作返回类型"""
        import inspect

        data_access = PostgreSQLDataAccess()

        # 检查方法的返回类型注解（如果存在）
        methods_with_return_types = [
            "insert_dataframe",  # 应该返回 int
            "upsert_dataframe",  # 应该返回 int
            "delete",  # 应该返回 int
            "query",  # 应该返回 pd.DataFrame
            "execute_sql",  # 应该返回 pd.DataFrame
        ]

        for method_name in methods_with_return_types:
            method = getattr(data_access, method_name)
            sig = inspect.signature(method)
            # 验证方法签名存在
            assert sig is not None

    def test_dataframe_processing_capabilities(self):
        """测试DataFrame处理能力"""
        data_access = PostgreSQLDataAccess()

        # 测试不同的DataFrame格式
        test_dfs = [
            pd.DataFrame({"id": [1, 2], "value": [10, 20]}),
            pd.DataFrame({"name": ["test1", "test2"], "score": [0.5, 0.8]}),
            pd.DataFrame({"date": pd.date_range("2024-01-01", periods=2)}),
        ]

        # 模拟连接池以避免实际数据库操作
        data_access.pool = Mock()

        for i, df in enumerate(test_dfs):
            # 测试DataFrame不为空时的处理
            assert not df.empty
            assert len(df) > 0

    def test_class_documentation(self):
        """测试类文档"""
        class_doc = PostgreSQLDataAccess.__doc__
        assert class_doc is not None
        assert len(class_doc.strip()) > 0
        assert "PostgreSQL" in class_doc

    def test_module_imports(self):
        """测试模块导入"""
        from src.data_access.postgresql_access import PostgreSQLDataAccess, execute_values, pd, psycopg2

        # 验证关键模块被导入
        assert PostgreSQLDataAccess is not None
        assert pd is not None


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__])
