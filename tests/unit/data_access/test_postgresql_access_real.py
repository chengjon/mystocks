"""
PostgreSQL数据访问层真实类单元测试
测试src/data_access/postgresql_access.py的PostgreSQLDataAccess类
使用Mock数据库连接来测试实际业务逻辑
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../'))


class TestPostgreSQLDataAccessReal:
    """PostgreSQLDataAccess真实类测试"""

    @pytest.fixture(autouse=True)
    def setup_with_mock(self):
        """使用Mock设置测试环境"""
        self.mock_conn_manager = MagicMock()
        self.mock_pool = MagicMock()
        self.mock_conn = MagicMock()
        self.mock_cursor = MagicMock()

        self.mock_conn_manager.get_postgresql_connection.return_value = self.mock_pool
        self.mock_pool.getconn.return_value = self.mock_conn
        self.mock_conn.cursor.return_value = self.mock_cursor
        # Add encoding attribute required by psycopg2.extras.execute_values
        # execute_values accesses cursor.connection.encoding
        self.mock_conn.encoding = 'UTF8'
        self.mock_cursor.connection = self.mock_conn

        with patch('src.data_access.postgresql_access.get_connection_manager') as mock_get_cm:
            mock_get_cm.return_value = self.mock_conn_manager
            from src.data_access.postgresql_access import PostgreSQLDataAccess
            self.db = PostgreSQLDataAccess()
            yield

    def test_init(self):
        """测试初始化"""
        assert self.db.conn_manager is not None
        assert self.db.pool is None

    def test_get_connection(self):
        """测试获取连接"""
        conn = self.db._get_connection()
        assert conn == self.mock_conn
        self.mock_pool.getconn.assert_called_once()

    def test_return_connection(self):
        """测试归还连接"""
        self.db._get_connection()
        self.db._return_connection(self.mock_conn)
        self.mock_pool.putconn.assert_called_once_with(self.mock_conn)

    def test_create_table(self):
        """测试创建表"""
        schema = {
            'symbol': 'VARCHAR(20)',
            'date': 'DATE',
            'close': 'DECIMAL(10,2)'
        }

        self.db.create_table('test_table', schema, primary_key='symbol, date')

        self.mock_cursor.execute.assert_called()
        call_args = self.mock_cursor.execute.call_args[0][0]
        assert 'CREATE TABLE' in call_args
        assert 'test_table' in call_args

    def test_create_hypertable(self):
        """测试创建时序表"""
        self.db.create_hypertable('kline_data', 'timestamp', '7 days')

        self.mock_cursor.execute.assert_called()

    def test_insert_dataframe(self):
        """测试插入DataFrame"""
        df = pd.DataFrame({
            'symbol': ['600519', '000001'],
            'price': [1750.50, 12.35],
            'date': ['2024-01-01', '2024-01-01']
        })

        # Mock execute_values as it requires complex psycopg2 internals
        with patch('src.data_access.postgresql_access.execute_values') as mock_execute_values:
            result = self.db.insert_dataframe('stocks', df)

            mock_execute_values.assert_called_once()
            # Verify the SQL pattern
            call_args = mock_execute_values.call_args
            assert 'INSERT INTO stocks' in call_args[0][1]

    def test_query(self):
        """测试查询"""
        self.mock_cursor.fetchall.return_value = [
            ('600519', 1750.50, '2024-01-01'),
            ('000001', 12.35, '2024-01-01')
        ]
        self.mock_cursor.description = [
            ('symbol',), ('price',), ('date',)
        ]

        result = self.db.query('stocks')

        assert isinstance(result, pd.DataFrame)
        self.mock_cursor.execute.assert_called()

    def test_query_by_time_range(self):
        """测试时间范围查询"""
        self.mock_cursor.fetchall.return_value = []
        self.mock_cursor.description = [('time',), ('value',)]

        start = datetime(2024, 1, 1)
        end = datetime(2024, 1, 31)

        result = self.db.query_by_time_range('kline', 'date', start, end)

        self.mock_cursor.execute.assert_called()

    def test_delete(self):
        """测试删除数据"""
        self.mock_cursor.rowcount = 5

        # delete() expects (table_name: str, where: str) - where is a SQL string condition
        self.db.delete('stocks', "symbol = '600519'")

        self.mock_cursor.execute.assert_called()
        call_args = self.mock_cursor.execute.call_args[0][0]
        assert 'DELETE' in call_args

    def test_upsert_dataframe(self):
        """测试upsert操作"""
        df = pd.DataFrame({
            'symbol': ['600519'],
            'price': [1800.00],
            'date': ['2024-01-01']
        })

        # Mock execute_values as it requires complex psycopg2 internals
        with patch('src.data_access.postgresql_access.execute_values') as mock_execute_values:
            self.db.upsert_dataframe('stocks', df, conflict_columns=['symbol', 'date'])

            mock_execute_values.assert_called_once()
            # Verify the SQL pattern includes ON CONFLICT
            call_args = mock_execute_values.call_args
            assert 'INSERT INTO stocks' in call_args[0][1]
            assert 'ON CONFLICT' in call_args[0][1]

    def test_execute_sql(self):
        """测试执行原始SQL"""
        self.mock_cursor.fetchall.return_value = [(1,)]
        self.mock_cursor.description = [('count',)]

        result = self.db.execute_sql('SELECT COUNT(*) FROM stocks')

        self.mock_cursor.execute.assert_called()

    def test_get_table_stats(self):
        """测试获取表统计"""
        self.mock_cursor.fetchone.return_value = (1000,)

        result = self.db.get_table_stats('stocks')

        self.mock_cursor.execute.assert_called()

    def test_save_data(self):
        """测试save_data方法"""
        df = pd.DataFrame({
            'symbol': ['600519'],
            'price': [1750.50]
        })

        # save_data signature: (data, classification, table_name, **kwargs)
        # Mock execute_values as it requires complex psycopg2 internals
        with patch('src.data_access.postgresql_access.execute_values') as mock_execute_values:
            result = self.db.save_data(df, None, 'stocks')

            mock_execute_values.assert_called_once()
            assert result is True

    def test_load_data(self):
        """测试load_data方法"""
        self.mock_cursor.fetchall.return_value = [('600519', 1750.50)]
        self.mock_cursor.description = [('symbol',), ('price',)]

        result = self.db.load_data('stocks')

        assert isinstance(result, pd.DataFrame)

    def test_close(self):
        """测试关闭连接"""
        self.db._get_connection()
        self.db.close()

        # 验证连接被关闭

    def test_close_all(self):
        """测试关闭所有连接"""
        self.db._get_connection()
        self.db.close_all()


class TestPostgreSQLDataAccessEdgeCases:
    """PostgreSQLDataAccess边界情况测试"""

    @pytest.fixture(autouse=True)
    def setup_with_mock(self):
        """使用Mock设置测试环境"""
        self.mock_conn_manager = MagicMock()
        self.mock_pool = MagicMock()
        self.mock_conn = MagicMock()
        self.mock_cursor = MagicMock()

        self.mock_conn_manager.get_postgresql_connection.return_value = self.mock_pool
        self.mock_pool.getconn.return_value = self.mock_conn
        self.mock_conn.cursor.return_value = self.mock_cursor
        # Add encoding attribute required by psycopg2.extras.execute_values
        # execute_values accesses cursor.connection.encoding
        self.mock_conn.encoding = 'UTF8'
        self.mock_cursor.connection = self.mock_conn

        with patch('src.data_access.postgresql_access.get_connection_manager') as mock_get_cm:
            mock_get_cm.return_value = self.mock_conn_manager
            from src.data_access.postgresql_access import PostgreSQLDataAccess
            self.db = PostgreSQLDataAccess()
            yield

    def test_empty_dataframe_insert(self):
        """测试插入空DataFrame"""
        df = pd.DataFrame()

        result = self.db.insert_dataframe('stocks', df)

        # 空DataFrame应该安全处理
        assert result is None or result == 0

    def test_query_empty_result(self):
        """测试空查询结果"""
        self.mock_cursor.fetchall.return_value = []
        self.mock_cursor.description = [('symbol',), ('price',)]

        result = self.db.query('empty_table')

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0

    def test_connection_error_handling(self):
        """测试连接错误处理"""
        self.mock_pool.getconn.side_effect = Exception("Connection failed")

        with pytest.raises(Exception):
            self.db._get_connection()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
