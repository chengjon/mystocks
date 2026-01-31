"""
ColumnMapper测试文件
用于测试列名映射器功能
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import unittest

import pandas as pd

from src.utils.column_mapper import ColumnMapper


class TestColumnMapper(unittest.TestCase):
    """ColumnMapper测试类"""

    def test_standardize_columns_to_english(self):
        """测试将列名标准化为英文"""
        # 创建包含中文列名的DataFrame
        df = pd.DataFrame(
            {
                "日期": ["2023-01-01", "2023-01-02"],
                "股票代码": ["000001", "000002"],
                "开盘": [10.0, 11.0],
                "收盘": [10.5, 11.5],
                "最高": [11.0, 12.0],
                "最低": [9.5, 10.5],
                "成交量": [1000000, 1200000],
            }
        )

        # 标准化为英文列名
        result_df = ColumnMapper.to_english(df)

        # 验证列名已转换为英文
        expected_columns = ["date", "symbol", "open", "close", "high", "low", "volume"]
        for col in expected_columns:
            self.assertIn(col, result_df.columns)

    def test_standardize_columns_to_chinese(self):
        """测试将列名标准化为中文"""
        # 创建包含英文列名的DataFrame
        df = pd.DataFrame(
            {
                "date": ["2023-01-01", "2023-01-02"],
                "symbol": ["000001", "000002"],
                "open": [10.0, 11.0],
                "close": [10.5, 11.5],
                "high": [11.0, 12.0],
                "low": [9.5, 10.5],
                "volume": [1000000, 1200000],
            }
        )

        # 标准化为中文列名
        result_df = ColumnMapper.to_chinese(df)

        # 验证列名已转换为中文
        expected_columns = [
            "日期",
            "股票代码",
            "开盘价",
            "收盘价",
            "最高价",
            "最低价",
            "成交量",
        ]
        for col in expected_columns:
            self.assertIn(col, result_df.columns)

    def test_standardize_columns_with_target_lang_param(self):
        """测试使用目标语言参数的标准化方法"""
        # 创建包含中文列名的DataFrame
        df = pd.DataFrame({"日期": ["2023-01-01", "2023-01-02"], "股票代码": ["000001", "000002"]})

        # 使用参数指定目标语言
        result_df = ColumnMapper.standardize_columns(df, target_lang="en")

        # 验证列名已转换为英文
        self.assertIn("date", result_df.columns)
        self.assertIn("symbol", result_df.columns)

        # 测试转换为中文
        result_df = ColumnMapper.standardize_columns(df, target_lang="cn")
        self.assertIn("日期", result_df.columns)
        self.assertIn("股票代码", result_df.columns)

    def test_get_standard_columns(self):
        """测试获取标准列名"""
        # 获取股票日线数据的标准列名（英文）
        standard_cols_en = ColumnMapper.get_standard_columns("stock_daily", "en")
        expected_en = [
            "date",
            "symbol",
            "open",
            "close",
            "high",
            "low",
            "volume",
            "amount",
            "pct_chg",
            "change",
        ]
        self.assertEqual(standard_cols_en, expected_en)

        # 获取股票日线数据的标准列名（中文）
        standard_cols_cn = ColumnMapper.get_standard_columns("stock_daily", "cn")
        expected_cn = [
            "日期",
            "股票代码",
            "开盘价",
            "收盘价",
            "最高价",
            "最低价",
            "成交量",
            "成交额",
            "涨跌幅",
            "涨跌额",
        ]
        self.assertEqual(standard_cols_cn, expected_cn)

    def test_validate_columns(self):
        """测试列名验证功能"""
        # 创建包含标准列名的DataFrame
        df = pd.DataFrame(
            {
                "date": ["2023-01-01", "2023-01-02"],
                "symbol": ["000001", "000002"],
                "open": [10.0, 11.0],
                "close": [10.5, 11.5],
            }
        )

        # 验证必需的列
        required_cols = ["date", "symbol", "open", "close"]
        is_valid, missing, extra = ColumnMapper.validate_columns(df, required_cols)

        self.assertTrue(is_valid)
        self.assertEqual(len(missing), 0)
        self.assertEqual(len(extra), 0)

        # 验证缺少列的情况
        required_cols_missing = ["date", "symbol", "open", "close", "volume"]
        is_valid, missing, extra = ColumnMapper.validate_columns(df, required_cols_missing)

        self.assertFalse(is_valid)
        self.assertIn("volume", missing)
        self.assertEqual(len(extra), 0)

    def test_custom_mapping(self):
        """测试自定义映射功能"""
        # 添加自定义映射
        custom_mapping = {"自定义列": "custom_col"}
        ColumnMapper.add_custom_mapping(custom_mapping, "en")

        # 创建包含自定义中文列名的DataFrame
        df = pd.DataFrame({"自定义列": [1, 2, 3], "日期": ["2023-01-01", "2023-01-02", "2023-01-03"]})

        # 转换为英文
        result_df = ColumnMapper.to_english(df)

        # 验证自定义映射已生效
        self.assertIn("custom_col", result_df.columns)
        self.assertIn("date", result_df.columns)


if __name__ == "__main__":
    unittest.main()
