#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据分类增强测试文件

增强对data_classification.py模块的测试覆盖率，重点测试边缘情况和高级功能。
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock


# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.core.data_classification import DataClassification


class TestDataClassificationEnhanced(unittest.TestCase):
    """增强数据分类测试类"""

    def test_all_classifications_exist(self):
        """测试所有分类都存在且正确"""
        # 测试市场数据分类
        market_data = [
            DataClassification.TICK_DATA,
            DataClassification.MINUTE_KLINE,
            DataClassification.DAILY_KLINE,
            DataClassification.ORDER_BOOK_DEPTH,
            DataClassification.LEVEL2_SNAPSHOT,
            DataClassification.INDEX_QUOTES
        ]
        
        for classification in market_data:
            self.assertIsInstance(classification, DataClassification)
            self.assertIsNotNone(classification.value)
            self.assertTrue(len(classification.value) > 0)

    def test_classification_comparison(self):
        """测试分类比较功能"""
        # 测试相等性
        self.assertEqual(DataClassification.TICK_DATA, DataClassification.TICK_DATA)
        self.assertNotEqual(DataClassification.TICK_DATA, DataClassification.MINUTE_KLINE)
        
        # 测试与字符串的比较（枚举可以与字符串比较，但值不同）
        # DataClassification.TICK_DATA == "TICK_DATA" 在某些情况下可能为True
        # 但它们的类型不同，所以我们检查类型
        self.assertNotIsInstance(DataClassification.TICK_DATA, str)
        self.assertIsInstance("TICK_DATA", str)

    def test_classification_string_representation(self):
        """测试分类的字符串表示"""
        # 测试value属性
        self.assertEqual(DataClassification.TICK_DATA.value, "TICK_DATA")
        self.assertEqual(DataClassification.MINUTE_KLINE.value, "MINUTE_KLINE")
        self.assertEqual(DataClassification.DAILY_KLINE.value, "DAILY_KLINE")
        
        # 测试__str__方法
        self.assertIn("TICK_DATA", str(DataClassification.TICK_DATA))
        self.assertIn("MINUTE_KLINE", str(DataClassification.MINUTE_KLINE))

    def test_classification_hash(self):
        """测试分类的哈希功能"""
        # 测试可以作为字典键使用
        test_dict = {}
        test_dict[DataClassification.TICK_DATA] = "tick_data_value"
        test_dict[DataClassification.MINUTE_KLINE] = "minute_kline_value"
        
        self.assertEqual(test_dict[DataClassification.TICK_DATA], "tick_data_value")
        self.assertEqual(test_dict[DataClassification.MINUTE_KLINE], "minute_kline_value")
        
        # 测试哈希值一致性
        self.assertEqual(hash(DataClassification.TICK_DATA), hash(DataClassification.TICK_DATA))

    def test_classification_in_collection(self):
        """测试分类在集合中的使用"""
        # 测试可以作为集合元素
        test_set = {DataClassification.TICK_DATA, DataClassification.MINUTE_KLINE}
        self.assertIn(DataClassification.TICK_DATA, test_set)
        self.assertIn(DataClassification.MINUTE_KLINE, test_set)
        self.assertNotIn(DataClassification.DAILY_KLINE, test_set)
        
        # 测试集合去重
        test_set.add(DataClassification.TICK_DATA)
        self.assertEqual(len(test_set), 2)  # 应该仍然只有2个元素

    def test_all_classifications_iteration(self):
        """测试所有分类的迭代"""
        all_classifications = list(DataClassification)
        
        # 验证分类数量
        self.assertGreater(len(all_classifications), 0)
        
        # 验证所有项目都是DataClassification类型
        for classification in all_classifications:
            self.assertIsInstance(classification, DataClassification)
            self.assertIsNotNone(classification.value)

    def test_classification_equality_with_none(self):
        """测试分类与None的比较"""
        self.assertNotEqual(DataClassification.TICK_DATA, None)
        self.assertIsNotNone(DataClassification.TICK_DATA)

    def test_classification_name_property(self):
        """测试分类的name属性"""
        # 测试name属性存在且正确
        self.assertEqual(DataClassification.TICK_DATA.name, "TICK_DATA")
        self.assertEqual(DataClassification.MINUTE_KLINE.name, "MINUTE_KLINE")
        
        # 确保name属性与value属性一致
        self.assertEqual(DataClassification.TICK_DATA.name, DataClassification.TICK_DATA.value)

    def test_market_data_classifications(self):
        """参数化测试：验证所有市场数据分类"""
        classifications = [
            DataClassification.TICK_DATA,
            DataClassification.MINUTE_KLINE,
            DataClassification.DAILY_KLINE,
            DataClassification.ORDER_BOOK_DEPTH,
            DataClassification.LEVEL2_SNAPSHOT,
            DataClassification.INDEX_QUOTES
        ]
        
        for classification in classifications:
            # 验证每个分类都有有效的值
            self.assertIsInstance(classification, DataClassification)
            self.assertIsNotNone(classification.value)
            self.assertIsInstance(classification.value, str)
            self.assertGreater(len(classification.value), 0)
            
            # 验证可以作为字典键
            test_dict = {classification: f"value_for_{classification.value}"}
            self.assertIn(classification, test_dict)


class TestDataClassificationEdgeCases(unittest.TestCase):
    """测试数据分类的边缘情况"""

    def test_classification_immutability(self):
        """测试分类的不可变性"""
        classification = DataClassification.TICK_DATA
        
        # 尝试修改value属性应该失败
        try:
            classification.value = "NEW_VALUE"
            self.fail("Expected AttributeError when modifying value")
        except AttributeError:
            pass  # 预期的异常
        
        # 尝试修改name属性应该失败
        try:
            classification.name = "NEW_NAME"
            self.fail("Expected AttributeError when modifying name")
        except AttributeError:
            pass  # 预期的异常

    def test_classification_ordering(self):
        """测试分类的排序功能"""
        classifications = [
            DataClassification.DAILY_KLINE,
            DataClassification.TICK_DATA,
            DataClassification.MINUTE_KLINE
        ]
        
        # 测试排序
        sorted_classifications = sorted(classifications, key=lambda x: x.value)
        
        # 验证排序结果
        expected_order = [
            DataClassification.DAILY_KLINE,  # DAILY_KLINE
            DataClassification.MINUTE_KLINE,  # MINUTE_KLINE  
            DataClassification.TICK_DATA  # TICK_DATA
        ]
        
        self.assertEqual(sorted_classifications, expected_order)

    def test_classification_membership_in_complex_structures(self):
        """测试分类在复杂结构中的成员关系"""
        # 在嵌套字典中使用
        nested_dict = {
            'market': {
                DataClassification.TICK_DATA: ['stock1', 'stock2'],
                DataClassification.MINUTE_KLINE: ['stock3', 'stock4']
            },
            'reference': {
                DataClassification.SYMBOLS_INFO: ['symbol1', 'symbol2']
            }
        }
        
        # 验证访问
        self.assertIn(DataClassification.TICK_DATA, nested_dict['market'])
        self.assertEqual(len(nested_dict['market'][DataClassification.TICK_DATA]), 2)
        
        # 在嵌套列表中使用
        nested_list = [
            [DataClassification.TICK_DATA, DataClassification.MINUTE_KLINE],
            [DataClassification.DAILY_KLINE]
        ]
        
        # 验证成员关系
        self.assertIn(DataClassification.TICK_DATA, nested_list[0])
        self.assertIn(DataClassification.DAILY_KLINE, nested_list[1])
        self.assertNotIn(DataClassification.ORDER_BOOK_DEPTH, nested_list[0])


if __name__ == '__main__':
    unittest.main()