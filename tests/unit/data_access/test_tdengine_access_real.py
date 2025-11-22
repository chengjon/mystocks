"""
TDengine数据访问层真实类单元测试
测试src/data_access/tdengine_access.py的TDengineDataAccess类
使用Mock数据库连接来测试实际业务逻辑
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../'))


class TestTDengineDataAccessReal:
    """TDengineDataAccess真实类测试"""

    @pytest.fixture(autouse=True)
    def setup_with_mock(self):
        """使用Mock设置测试环境"""
        self.mock_conn_manager = MagicMock()
        self.mock_conn = MagicMock()
        self.mock_cursor = MagicMock()

        self.mock_conn_manager.get_tdengine_connection.return_value = self.mock_conn
        self.mock_conn.cursor.return_value = self.mock_cursor

        with patch('src.data_access.tdengine_access.get_connection_manager') as mock_get_cm:
            mock_get_cm.return_value = self.mock_conn_manager
            from src.data_access.tdengine_access import TDengineDataAccess
            self.db = TDengineDataAccess()
            yield

    def test_init(self):
        """测试初始化"""
        assert self.db.conn_manager is not None

    def test_create_stable(self):
        """测试创建超级表"""
        schema = {
            'ts': 'TIMESTAMP',
            'price': 'FLOAT',
            'volume': 'INT'
        }
        tags = {
            'symbol': 'BINARY(20)',
            'exchange': 'BINARY(10)'
        }

        self.db.create_stable('tick_data', schema, tags)

        self.mock_cursor.execute.assert_called()

    def test_create_table(self):
        """测试创建子表"""
        self.db.create_table(
            'tick_600519',
            stable_name='tick_data',
            tags={'symbol': '600519', 'exchange': 'SH'}
        )

        self.mock_cursor.execute.assert_called()

    def test_insert_dataframe(self):
        """测试插入DataFrame"""
        df = pd.DataFrame({
            'ts': pd.date_range('2024-01-01 09:30:00', periods=10, freq='1min'),
            'price': [1750.0 + i * 0.1 for i in range(10)],
            'volume': [1000 + i * 10 for i in range(10)]
        })

        self.db.insert_dataframe('tick_600519', df)

        assert self.mock_cursor.execute.called

    def test_query_by_time_range(self):
        """测试时间范围查询"""
        self.mock_cursor.fetchall.return_value = []
        self.mock_cursor.description = [('ts',), ('price',), ('volume',)]

        start = datetime(2024, 1, 1, 9, 30, 0)
        end = datetime(2024, 1, 1, 11, 30, 0)

        result = self.db.query_by_time_range('tick_data', start, end, symbol='600519')

        self.mock_cursor.execute.assert_called()

    def test_query_latest(self):
        """测试查询最新数据"""
        self.mock_cursor.fetchall.return_value = [
            (datetime(2024, 1, 1, 15, 0, 0), 1755.00, 5000),
        ]
        self.mock_cursor.description = [('ts',), ('price',), ('volume',)]

        result = self.db.query_latest('tick_600519', limit=1)

        self.mock_cursor.execute.assert_called()

    def test_aggregate_to_kline(self):
        """测试聚合K线"""
        self.mock_cursor.fetchall.return_value = [
            (datetime(2024, 1, 1, 9, 30, 0), 1750.00, 1755.00, 1748.00, 1752.00, 100000),
        ]
        self.mock_cursor.description = [
            ('ts',), ('open',), ('high',), ('low',), ('close',), ('volume',)
        ]

        result = self.db.aggregate_to_kline(
            'tick_600519',
            interval='1m',
            start_time=datetime(2024, 1, 1),
            end_time=datetime(2024, 1, 2)
        )

        self.mock_cursor.execute.assert_called()

    def test_delete_by_time_range(self):
        """测试按时间范围删除"""
        self.mock_cursor.rowcount = 100

        self.db.delete_by_time_range(
            'tick_600519',
            start_time=datetime(2024, 1, 1),
            end_time=datetime(2024, 1, 2)
        )

        self.mock_cursor.execute.assert_called()

    def test_get_table_info(self):
        """测试获取表信息"""
        self.mock_cursor.fetchall.return_value = [
            ('ts', 'TIMESTAMP'),
            ('price', 'FLOAT'),
            ('volume', 'INT'),
        ]

        result = self.db.get_table_info('tick_600519')

        self.mock_cursor.execute.assert_called()

    def test_save_data(self):
        """测试save_data方法"""
        df = pd.DataFrame({
            'ts': [datetime.now()],
            'price': [1750.50],
            'volume': [1000]
        })

        self.db.save_data('tick_600519', df)

        self.mock_cursor.execute.assert_called()

    def test_load_data(self):
        """测试load_data方法"""
        self.mock_cursor.fetchall.return_value = [
            (datetime(2024, 1, 1, 9, 30, 0), 1750.50, 1000)
        ]
        self.mock_cursor.description = [('ts',), ('price',), ('volume',)]

        result = self.db.load_data('tick_600519')

        assert isinstance(result, pd.DataFrame)

    def test_close(self):
        """测试关闭连接"""
        self.db.close()


class TestTDengineDataAccessEdgeCases:
    """TDengineDataAccess边界情况测试"""

    @pytest.fixture(autouse=True)
    def setup_with_mock(self):
        """使用Mock设置测试环境"""
        self.mock_conn_manager = MagicMock()
        self.mock_conn = MagicMock()
        self.mock_cursor = MagicMock()

        self.mock_conn_manager.get_tdengine_connection.return_value = self.mock_conn
        self.mock_conn.cursor.return_value = self.mock_cursor

        with patch('src.data_access.tdengine_access.get_connection_manager') as mock_get_cm:
            mock_get_cm.return_value = self.mock_conn_manager
            from src.data_access.tdengine_access import TDengineDataAccess
            self.db = TDengineDataAccess()
            yield

    def test_empty_dataframe(self):
        """测试空DataFrame"""
        df = pd.DataFrame()

        result = self.db.insert_dataframe('tick_600519', df)

        assert result is None or result == 0

    def test_connection_error(self):
        """测试连接错误"""
        self.mock_conn_manager.get_tdengine_connection.side_effect = Exception("Connection failed")

        with pytest.raises(Exception):
            self.db._get_connection()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
