"""
MyStocksUnifiedManager测试文件
用于测试统一管理器功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import unittest
from unittest.mock import patch, MagicMock
import pandas as pd

# 导入被测试的模块
from src.core.unified_manager import MyStocksUnifiedManager
from src.core.data_classification import DataClassification


class TestMyStocksUnifiedManager(unittest.TestCase):
    """MyStocksUnifiedManager测试类"""

    @patch("src.core.unified_manager.TDengineDataAccess")
    @patch("src.core.unified_manager.PostgreSQLDataAccess")
    def setUp(self, mock_pg, mock_td):
        """测试前准备"""
        # Mock数据库访问层
        self.mock_td_instance = MagicMock()
        self.mock_pg_instance = MagicMock()
        mock_td.return_value = self.mock_td_instance
        mock_pg.return_value = self.mock_pg_instance

        # 创建测试用的管理器实例
        self.manager = MyStocksUnifiedManager()
        # 替换内部数据库访问对象
        self.manager.tdengine = self.mock_td_instance
        self.manager.postgresql = self.mock_pg_instance

    def test_initialization(self):
        """测试初始化功能"""
        # 验证初始化结果
        self.assertIsNotNone(self.manager)
        # 检查初始化状态(可能是属性或方法)
        self.assertTrue(hasattr(self.manager, "tdengine"))
        self.assertTrue(hasattr(self.manager, "postgresql"))

    def test_save_data_by_classification_tdengine(self):
        """测试按分类保存数据到TDengine"""
        # 配置mock返回成功
        self.mock_td_instance.insert_dataframe.return_value = 2

        # 创建测试数据
        test_data = pd.DataFrame(
            {
                "ts": pd.to_datetime(["2023-01-01", "2023-01-02"]),
                "open": [100.0, 101.0],
                "close": [102.0, 103.0],
                "high": [103.0, 104.0],
                "low": [99.0, 100.0],
                "volume": [1000, 1100],
            }
        )

        # 调用保存方法
        result = self.manager.save_data_by_classification(DataClassification.TICK_DATA, test_data, "test_tick_table")

        # 验证结果
        self.assertTrue(result)
        self.mock_td_instance.insert_dataframe.assert_called_once()

    def test_save_data_by_classification_postgresql(self):
        """测试按分类保存数据到PostgreSQL"""
        # 配置mock返回成功
        self.mock_pg_instance.insert_dataframe.return_value = 2

        # 创建测试数据
        test_data = pd.DataFrame(
            {
                "date": ["2023-01-01", "2023-01-02"],
                "symbol": ["AAPL", "AAPL"],
                "open": [100.0, 101.0],
                "close": [102.0, 103.0],
                "high": [103.0, 104.0],
                "low": [99.0, 100.0],
                "volume": [1000, 1100],
            }
        )

        # 调用保存方法 - SYMBOLS_INFO 路由到PostgreSQL
        result = self.manager.save_data_by_classification(
            DataClassification.SYMBOLS_INFO, test_data, "test_symbols_table"
        )

        # 验证结果
        self.assertTrue(result)
        self.mock_pg_instance.insert_dataframe.assert_called_once()

    def test_load_data_by_classification_tdengine(self):
        """测试按分类从TDengine加载数据"""
        # 模拟返回数据
        mock_data = pd.DataFrame(
            {
                "ts": pd.to_datetime(["2023-01-01", "2023-01-02"]),
                "open": [100.0, 101.0],
                "close": [102.0, 103.0],
            }
        )
        # TDengine使用query_latest方法
        self.mock_td_instance.query_latest.return_value = mock_data

        # 调用加载方法
        result = self.manager.load_data_by_classification(
            DataClassification.MINUTE_KLINE,
            "test_minute_table",
            filters={"date": "2023-01-01"},
        )

        # 验证结果
        self.assertEqual(len(result), 2)
        self.mock_td_instance.query_latest.assert_called_once()

    def test_load_data_by_classification_postgresql(self):
        """测试按分类从PostgreSQL加载数据"""
        # 模拟返回数据
        mock_data = pd.DataFrame(
            {
                "date": ["2023-01-01", "2023-01-02"],
                "symbol": ["AAPL", "AAPL"],
                "open": [100.0, 101.0],
                "close": [102.0, 103.0],
            }
        )
        # PostgreSQL使用query方法
        self.mock_pg_instance.query.return_value = mock_data

        # 调用加载方法 - SYMBOLS_INFO 路由到PostgreSQL
        result = self.manager.load_data_by_classification(
            DataClassification.SYMBOLS_INFO,
            "test_symbols_table",
            filters={"symbol": "AAPL"},
        )

        # 验证结果
        self.assertEqual(len(result), 2)
        self.mock_pg_instance.query.assert_called_once()

    def test_data_classification_enum(self):
        """测试数据分类枚举"""
        # 验证市场数据分类 (6项)
        self.assertEqual(DataClassification.TICK_DATA.value, "TICK_DATA")
        self.assertEqual(DataClassification.MINUTE_KLINE.value, "MINUTE_KLINE")
        self.assertEqual(DataClassification.DAILY_KLINE.value, "DAILY_KLINE")
        self.assertEqual(DataClassification.ORDER_BOOK_DEPTH.value, "ORDER_BOOK_DEPTH")
        self.assertEqual(DataClassification.LEVEL2_SNAPSHOT.value, "LEVEL2_SNAPSHOT")
        self.assertEqual(DataClassification.INDEX_QUOTES.value, "INDEX_QUOTES")

        # 验证参考数据分类存在
        self.assertIsNotNone(DataClassification.SYMBOLS_INFO)
        self.assertIsNotNone(DataClassification.INDUSTRY_CLASS)

        # 验证枚举数量 - 34个分类 (6+9+6+7+6)
        all_classifications = list(DataClassification)
        self.assertEqual(len(all_classifications), 34)


if __name__ == "__main__":
    unittest.main()
