"""
IDataSource测试文件
用于测试数据源接口定义
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import unittest
from abc import ABC
import pandas as pd
from typing import Dict, List, Optional, Any

# 导入被测试的模块
from src.interfaces.data_source import IDataSource


class TestIDataSource(unittest.TestCase):
    """IDataSource接口测试类"""

    def test_interface_abstract_methods(self):
        """测试接口是否定义了所有必需的抽象方法"""
        # 获取接口的所有抽象方法
        abstract_methods = list(ABC.__subclasses__()[0].__abstractmethods__)

        # 检查IDataSource是否继承自ABC
        self.assertTrue(issubclass(IDataSource, ABC))

        # 检查是否定义了所有必需的方法
        required_methods = [
            "get_stock_daily",
            "get_index_daily",
            "get_stock_basic",
            "get_index_components",
            "get_real_time_data",
            "get_market_calendar",
            "get_financial_data",
            "get_news_data",
        ]

        # 验证每个必需的方法都存在于接口中
        for method_name in required_methods:
            self.assertTrue(hasattr(IDataSource, method_name), f"接口缺少必需的方法: {method_name}")

            # 验证方法是否为抽象方法
            method = getattr(IDataSource, method_name)
            self.assertTrue(
                hasattr(method, "__isabstractmethod__"),
                f"方法 {method_name} 不是抽象方法",
            )

    def test_method_signatures(self):
        """测试接口方法签名"""
        # 检查get_stock_daily方法签名
        import inspect

        get_stock_daily_sig = inspect.signature(IDataSource.get_stock_daily)
        params = list(get_stock_daily_sig.parameters.keys())
        self.assertEqual(params, ["self", "symbol", "start_date", "end_date"])

        # 检查返回类型注解
        self.assertEqual(get_stock_daily_sig.return_annotation, pd.DataFrame)

        # 检查get_stock_basic方法签名
        get_stock_basic_sig = inspect.signature(IDataSource.get_stock_basic)
        params = list(get_stock_basic_sig.parameters.keys())
        self.assertEqual(params, ["self", "symbol"])
        self.assertEqual(get_stock_basic_sig.return_annotation, Dict[str, Any])

        # 检查get_index_components方法签名
        get_index_components_sig = inspect.signature(IDataSource.get_index_components)
        params = list(get_index_components_sig.parameters.keys())
        self.assertEqual(params, ["self", "symbol"])
        self.assertEqual(get_index_components_sig.return_annotation, List[str])

        # 检查get_real_time_data方法签名
        get_real_time_data_sig = inspect.signature(IDataSource.get_real_time_data)
        params = list(get_real_time_data_sig.parameters.keys())
        self.assertEqual(params, ["self", "symbol"])
        self.assertEqual(get_real_time_data_sig.return_annotation, Optional[Dict[str, Any]])

        # 检查get_market_calendar方法签名
        get_market_calendar_sig = inspect.signature(IDataSource.get_market_calendar)
        params = list(get_market_calendar_sig.parameters.keys())
        self.assertEqual(params, ["self", "start_date", "end_date"])
        self.assertEqual(get_market_calendar_sig.return_annotation, pd.DataFrame)

        # 检查get_financial_data方法签名
        get_financial_data_sig = inspect.signature(IDataSource.get_financial_data)
        params = list(get_financial_data_sig.parameters.keys())
        self.assertEqual(params, ["self", "symbol", "period"])
        self.assertEqual(get_financial_data_sig.return_annotation, pd.DataFrame)

        # 检查get_news_data方法签名
        get_news_data_sig = inspect.signature(IDataSource.get_news_data)
        params = list(get_news_data_sig.parameters.keys())
        self.assertEqual(params, ["self", "symbol", "limit"])
        self.assertEqual(get_news_data_sig.return_annotation, List[Dict[str, Any]])


if __name__ == "__main__":
    unittest.main()
