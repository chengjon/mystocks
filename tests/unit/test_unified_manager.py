"""
MyStocksUnifiedManager测试文件
用于测试统一管理器功能
"""

import sys
import os
# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import unittest
from unittest.mock import patch, MagicMock, mock_open
import pandas as pd
from datetime import datetime
import tempfile

# 导入被测试的模块
from src.core.unified_manager import MyStocksUnifiedManager
from src.core.data_classification import DataClassification


class TestMyStocksUnifiedManager(unittest.TestCase):
    """MyStocksUnifiedManager测试类"""
    
    def setUp(self):
        """测试前准备"""
        # 创建测试用的管理器实例
        self.manager = MyStocksUnifiedManager()
    
    def test_initialization(self):
        """测试初始化功能"""
        # 验证初始化结果
        self.assertIsNotNone(self.manager)
        self.assertTrue(self.manager._initialized)
    
    @patch('src.data_access.tdengine_access.TDengineDataAccess.save_data')
    def test_save_data_by_classification_tdengine(self, mock_save):
        """测试按分类保存数据到TDengine"""
        # 创建测试数据
        test_data = pd.DataFrame({
            'date': ['2023-01-01', '2023-01-02'],
            'open': [100.0, 101.0],
            'close': [102.0, 103.0],
            'high': [103.0, 104.0],
            'low': [99.0, 100.0],
            'volume': [1000, 1100]
        })
        
        # 调用保存方法
        result = self.manager.save_data_by_classification(
            DataClassification.TICK_DATA, 
            test_data, 
            'test_tick_table'
        )
        
        # 验证结果
        self.assertTrue(result)
        mock_save.assert_called_once()
    
    @patch('src.data_access.postgresql_access.PostgreSQLDataAccess.save_data')
    def test_save_data_by_classification_postgresql(self, mock_save):
        """测试按分类保存数据到PostgreSQL"""
        # 创建测试数据
        test_data = pd.DataFrame({
            'date': ['2023-01-01', '2023-01-02'],
            'symbol': ['AAPL', 'AAPL'],
            'open': [100.0, 101.0],
            'close': [102.0, 103.0],
            'high': [103.0, 104.0],
            'low': [99.0, 100.0],
            'volume': [1000, 1100]
        })
        
        # 调用保存方法
        result = self.manager.save_data_by_classification(
            DataClassification.DAILY_KLINE, 
            test_data, 
            'test_daily_table'
        )
        
        # 验证结果
        self.assertTrue(result)
        mock_save.assert_called_once()
    
    @patch('src.data_access.tdengine_access.TDengineDataAccess.load_data')
    def test_load_data_by_classification_tdengine(self, mock_load):
        """测试按分类从TDengine加载数据"""
        # 模拟返回数据
        mock_data = pd.DataFrame({
            'date': ['2023-01-01', '2023-01-02'],
            'open': [100.0, 101.0],
            'close': [102.0, 103.0]
        })
        mock_load.return_value = mock_data
        
        # 调用加载方法
        result = self.manager.load_data_by_classification(
            DataClassification.MINUTE_KLINE,
            'test_minute_table',
            filters={'date': '2023-01-01'}
        )
        
        # 验证结果
        self.assertEqual(len(result), 2)
        mock_load.assert_called_once()
    
    @patch('src.data_access.postgresql_access.PostgreSQLDataAccess.load_data')
    def test_load_data_by_classification_postgresql(self, mock_load):
        """测试按分类从PostgreSQL加载数据"""
        # 模拟返回数据
        mock_data = pd.DataFrame({
            'date': ['2023-01-01', '2023-01-02'],
            'symbol': ['AAPL', 'AAPL'],
            'open': [100.0, 101.0],
            'close': [102.0, 103.0]
        })
        mock_load.return_value = mock_data
        
        # 调用加载方法
        result = self.manager.load_data_by_classification(
            DataClassification.DAILY_KLINE,
            'test_daily_table',
            filters={'symbol': 'AAPL'}
        )
        
        # 验证结果
        self.assertEqual(len(result), 2)
        mock_load.assert_called_once()
    
    def test_data_classification_enum(self):
        """测试数据分类枚举"""
        # 验证枚举值
        self.assertEqual(DataClassification.TICK_DATA.value, "tick_data")
        self.assertEqual(DataClassification.MINUTE_KLINE.value, "minute_kline")
        self.assertEqual(DataClassification.DAILY_KLINE.value, "daily_kline")
        self.assertEqual(DataClassification.REFERENCE_DATA.value, "reference_data")
        self.assertEqual(DataClassification.DERIVED_DATA.value, "derived_data")
        self.assertEqual(DataClassification.TRANSACTION_DATA.value, "transaction_data")
        self.assertEqual(DataClassification.META_DATA.value, "meta_data")
        
        # 验证枚举数量
        all_classifications = list(DataClassification)
        self.assertEqual(len(all_classifications), 7)


if __name__ == '__main__':
    unittest.main()