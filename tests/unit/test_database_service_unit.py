"""
单元测试：Mock函数单元测试（快速验证）
测试文件：tests/unit/test_database_service_unit.py
"""

import pytest
from unittest.mock import Mock, patch
import pandas as pd
from src.database.database_service import DatabaseService


class TestDatabaseServiceUnit:
    """数据库服务单元测试类"""
    
    def setup_method(self):
        """设置测试环境"""
        self.mock_postgresql_access = Mock()
        with patch('src.database.database_service.PostgreSQLDataAccess') as MockPostgreSQLAccess:
            MockPostgreSQLAccess.return_value = self.mock_postgresql_access
            self.db_service = DatabaseService()
    
    def test_get_stock_list_empty_params(self):
        """测试获取股票列表 - 空参数"""
        # 模拟数据库返回空DataFrame
        mock_df_empty = pd.DataFrame(columns=['symbol', 'name', 'industry', 'area', 'market', 'list_date'])
        self.mock_postgresql_access.query.return_value = mock_df_empty
        
        result = self.db_service.get_stock_list()
        assert result == []
    
    def test_get_stock_list_with_data(self):
        """测试获取股票列表 - 有数据"""
        # 模拟数据库返回
        mock_df = pd.DataFrame({
            'symbol': ['000001', '600000'],
            'name': ['平安银行', '浦发银行'],
            'industry': ['银行', '银行'],
            'area': ['深圳', '上海'],
            'market': ['深交所', '上交所'],
            'list_date': [pd.Timestamp('2020-01-01'), pd.Timestamp('2020-01-02')]
        })
        
        # 模拟总数量查询
        mock_total_df = pd.DataFrame({'total': [2]})
        
        # 修复两次调用query方法
        def side_effect(table_name, **kwargs):
            if 'columns' in kwargs and kwargs['columns'] and 'COUNT(*)' in kwargs['columns'][0]:
                return mock_total_df
            else:
                return mock_df
        
        self.mock_postgresql_access.query.side_effect = side_effect
        
        result = self.db_service.get_stock_list({'limit': 20, 'offset': 0})
        
        assert len(result) == 2
        assert result[0]['symbol'] == '000001'
        assert result[0]['name'] == '平安银行'
        assert result[0]['market'] == '深交所'
        assert result[0]['total'] == 2  # 每个结果都应该包含总数
    
    def test_get_stock_detail_empty_code(self):
        """测试获取股票详情 - 空股票代码"""
        result = self.db_service.get_stock_detail('')
        assert result == {}
    
    def test_get_technical_indicators_empty_symbol(self):
        """测试获取技术指标 - 空股票代码"""
        result = self.db_service.get_technical_indicators('')
        assert result == {}