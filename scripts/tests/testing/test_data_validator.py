#!/usr/bin/env python3
"""
DataValidator 测试套件
提供完整的数据验证器功能测试
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest
import pandas as pd
import numpy as np

# 导入被测试的模块
from src.adapters.data_validator import DataValidator


class TestDataValidator:
    """DataValidator 测试类"""

    @pytest.fixture
    def validator(self):
        """创建数据验证器实例"""
        return DataValidator()

    @pytest.fixture
    def valid_price_dataframe(self):
        """创建有效的价格数据DataFrame"""
        return pd.DataFrame(
            {
                "open": [100.0, 101.5, 102.0, 100.5, 103.0],
                "high": [
                    101.5,
                    103.0,
                    103.0,
                    101.5,
                    104.0,
                ],  # 确保high >= max(open, close)
                "low": [99.0, 100.5, 100.0, 99.5, 102.0],  # 确保low <= min(open, close)
                "close": [100.5, 102.0, 100.5, 101.0, 103.5],  # 调整第一行和第三行
                "volume": [1000000, 1200000, 900000, 1500000, 1100000],
            }
        )

    @pytest.fixture
    def invalid_price_dataframe(self):
        """创建无效的价格数据DataFrame"""
        return pd.DataFrame(
            {
                "open": [100.0, 101.5, 102.0],
                "high": [99.0, 102.5, 103.0],  # 第一行high < open，错误
                "low": [99.0, 100.5, 101.0],
                "close": [101.5, 102.0, 100.5],
                "volume": [1000000, 1200000, 900000],
            }
        )

    @pytest.fixture
    def mixed_dataframe(self):
        """创建混合数据DataFrame（包含有效和无效数据）"""
        return pd.DataFrame(
            {
                "open": [100.0, 101.5, -10.0],  # 第三行价格负数
                "high": [101.0, 102.5, 103.0],
                "low": [99.0, 100.5, 101.0],
                "close": [101.5, 102.0, 100.5],
                "volume": [1000000, 1200000, 900000],
            }
        )

    # === 初始化测试 ===
    def test_validator_initialization(self, validator):
        """测试验证器初始化"""
        assert validator is not None
        assert isinstance(validator, DataValidator)

    # === 股票代码验证测试 ===
    def test_validate_stock_symbol_valid(self, validator):
        """测试有效股票代码验证"""
        # A股代码（6位数字）
        assert validator.validate_stock_symbol("000001") is True
        assert validator.validate_stock_symbol("600000") is True
        assert validator.validate_stock_symbol("300001") is True
        assert validator.validate_stock_symbol("002001") is True

    def test_validate_stock_symbol_with_spaces(self, validator):
        """测试包含空格的股票代码"""
        assert validator.validate_stock_symbol(" 000001 ") is True
        assert validator.validate_stock_symbol("\t600000\n") is True

    def test_validate_stock_symbol_invalid(self, validator):
        """测试无效股票代码"""
        # 空值
        assert validator.validate_stock_symbol("") is False
        assert validator.validate_stock_symbol(None) is False

        # 非字符串
        assert validator.validate_stock_symbol(123456) is False
        assert validator.validate_stock_symbol([]) is False

        # 错误格式
        assert validator.validate_stock_symbol("00001") is False  # 5位
        assert validator.validate_stock_symbol("0000001") is False  # 7位
        assert validator.validate_stock_symbol("ABCDEF") is False  # 字母
        assert validator.validate_stock_symbol("000001.") is False  # 包含特殊字符

    # === 日期格式验证测试 ===
    def test_validate_date_format_valid(self, validator):
        """测试有效日期格式"""
        assert validator.validate_date_format("2024-01-01") is True
        assert validator.validate_date_format("2023-12-31") is True
        assert validator.validate_date_format("2024-02-29") is True  # 闰年

    def test_validate_date_format_invalid(self, validator):
        """测试无效日期格式"""
        # 空值
        assert validator.validate_date_format("") is False
        assert validator.validate_date_format(None) is False

        # 非字符串
        assert validator.validate_date_format(20240101) is False

        # 错误格式 - 注意Python的datetime.strptime比较宽容
        assert validator.validate_date_format("2024/01/01") is False
        assert validator.validate_date_format("01-01-2024") is False
        assert validator.validate_date_format("2024-13-01") is False  # 无效月份
        assert validator.validate_date_format("2024-01-32") is False  # 无效日期

    # === 日期范围验证测试 ===
    def test_validate_date_range_valid(self, validator):
        """测试有效日期范围"""
        assert validator.validate_date_range("2024-01-01", "2024-01-10") is True
        assert validator.validate_date_range("2023-12-31", "2024-01-01") is True

    def test_validate_date_range_invalid(self, validator):
        """测试无效日期范围"""
        # 开始日期晚于结束日期
        assert validator.validate_date_range("2024-01-10", "2024-01-01") is False

        # 无效日期格式
        assert validator.validate_date_range("2024-01-01", "invalid") is False
        assert validator.validate_date_range("invalid", "2024-01-10") is False

        # 相同日期
        assert validator.validate_date_range("2024-01-01", "2024-01-01") is False

    # === 价格数据验证测试 ===
    def test_validate_price_data_valid(self, validator, valid_price_dataframe):
        """测试有效价格数据验证"""
        assert validator.validate_price_data(valid_price_dataframe) is True

    def test_validate_price_data_missing_columns(self, validator):
        """测试缺少必需列的价格数据"""
        incomplete_df = pd.DataFrame(
            {
                "open": [100.0, 101.0],
                "high": [101.0, 102.0],
                "low": [99.0, 100.0],
                # 缺少close和volume
            }
        )
        assert validator.validate_price_data(incomplete_df) is False

    def test_validate_price_data_empty_dataframe(self, validator):
        """测试空DataFrame"""
        empty_df = pd.DataFrame()
        assert validator.validate_price_data(empty_df) is False

    def test_validate_price_data_invalid(self, validator, invalid_price_dataframe):
        """测试无效价格数据"""
        assert validator.validate_price_data(invalid_price_dataframe) is False

    def test_validate_price_data_negative_prices(self, validator, mixed_dataframe):
        """测试包含负数价格的数据"""
        assert validator.validate_price_data(mixed_dataframe) is False

    def test_validate_price_data_negative_volume(self, validator):
        """测试包含负数成交量的数据"""
        df_with_negative_volume = pd.DataFrame(
            {
                "open": [100.0, 101.5, 102.0],
                "high": [101.0, 102.5, 103.0],
                "low": [99.0, 100.5, 101.0],
                "close": [101.5, 102.0, 100.5],
                "volume": [1000000, -500000, 900000],  # 包含负成交量
            }
        )
        assert validator.validate_price_data(df_with_negative_volume) is False

    def test_validate_price_data_wrong_high_low_relationship(self, validator):
        """测试高低价关系错误的数据"""
        wrong_relationship_df = pd.DataFrame(
            {
                "open": [100.0, 101.5, 102.0],
                "high": [98.0, 102.5, 103.0],  # 第一行high < low
                "low": [99.0, 100.5, 101.0],
                "close": [101.5, 102.0, 100.5],
                "volume": [1000000, 1200000, 900000],
            }
        )
        assert validator.validate_price_data(wrong_relationship_df) is False

    def test_validate_price_data_type_conversion_errors(self, validator):
        """测试类型转换错误的数据"""
        df_with_strings = pd.DataFrame(
            {
                "open": ["100.0", "101.5", "invalid"],
                "high": [101.0, 102.5, 103.0],
                "low": [99.0, 100.5, 101.0],
                "close": [101.5, 102.0, 100.5],
                "volume": [1000000, 1200000, 900000],
            }
        )
        assert validator.validate_price_data(df_with_strings) is False

    # === 成交量数据验证测试 ===
    def test_validate_volume_data_valid(self, validator, valid_price_dataframe):
        """测试有效成交量数据"""
        assert validator.validate_volume_data(valid_price_dataframe) is True

    def test_validate_volume_data_missing_column(self, validator):
        """测试缺少volume列的数据"""
        df_without_volume = pd.DataFrame(
            {
                "open": [100.0, 101.0],
                "high": [101.0, 102.0],
                "low": [99.0, 100.0],
                "close": [100.5, 101.5],
            }
        )
        assert validator.validate_volume_data(df_without_volume) is False

    def test_validate_volume_data_empty_dataframe(self, validator):
        """测试空DataFrame"""
        empty_df = pd.DataFrame()
        assert validator.validate_volume_data(empty_df) is False

    def test_validate_volume_data_with_nan(self, validator):
        """测试包含NaN的成交量数据"""
        df_with_nan = pd.DataFrame(
            {
                "open": [100.0, 101.0],
                "high": [101.0, 102.0],
                "low": [99.0, 100.0],
                "close": [100.5, 101.5],
                "volume": [1000000, np.nan],
            }
        )
        assert validator.validate_volume_data(df_with_nan) is False

    def test_validate_volume_data_negative_values(self, validator):
        """测试包含负数的成交量数据"""
        df_with_negative = pd.DataFrame(
            {
                "open": [100.0, 101.0],
                "high": [101.0, 102.0],
                "low": [99.0, 100.0],
                "close": [100.5, 101.5],
                "volume": [1000000, -500000],
            }
        )
        assert validator.validate_volume_data(df_with_negative) is False

    # === 交易日验证测试 ===
    def test_validate_trading_day_weekdays(self, validator):
        """测试工作日验证"""
        # 周一到周五
        assert validator.validate_trading_day("2024-01-01") is True  # 周一
        assert validator.validate_trading_day("2024-01-02") is True  # 周二
        assert validator.validate_trading_day("2024-01-03") is True  # 周三
        assert validator.validate_trading_day("2024-01-04") is True  # 周四
        assert validator.validate_trading_day("2024-01-05") is True  # 周五

    def test_validate_trading_day_weekends(self, validator):
        """测试周末验证"""
        # 周六和周日
        assert validator.validate_trading_day("2024-01-06") is False  # 周六
        assert validator.validate_trading_day("2024-01-07") is False  # 周日

    def test_validate_trading_day_invalid_date(self, validator):
        """测试无效日期的交易日验证"""
        assert validator.validate_trading_day("invalid") is False
        assert validator.validate_trading_day("") is False

    # === 价格范围验证测试 ===
    def test_validate_price_range_valid(self, validator, valid_price_dataframe):
        """测试有效价格范围"""
        assert validator.validate_price_range(valid_price_dataframe) is True

    def test_validate_price_range_custom_limits(self, validator):
        """测试自定义价格范围限制"""
        # 价格在正常范围内
        normal_price_df = pd.DataFrame(
            {
                "open": [10.0, 20.0],
                "high": [15.0, 25.0],
                "low": [5.0, 15.0],
                "close": [12.0, 22.0],
                "volume": [1000, 2000],
            }
        )
        assert validator.validate_price_range(normal_price_df, 5.0, 30.0) is True

        # 价格超出范围
        out_of_range_df = pd.DataFrame(
            {
                "open": [1.0, 20.0],  # 第一行低于最小价格5.0
                "high": [15.0, 25.0],
                "low": [5.0, 15.0],
                "close": [12.0, 22.0],
                "volume": [1000, 2000],
            }
        )
        assert validator.validate_price_range(out_of_range_df, 5.0, 30.0) is False

    def test_validate_price_range_missing_columns(self, validator):
        """测试缺少价格列的数据"""
        df_with_partial_columns = pd.DataFrame(
            {
                "open": [100.0, 101.0],
                "volume": [1000, 2000],
                # 缺少high, low, close
            }
        )
        # 应该返回True，因为缺少的列被跳过
        assert validator.validate_price_range(df_with_partial_columns) is True

    def test_validate_price_range_with_negative_values(self, validator):
        """测试包含负数的范围验证"""
        df_with_negative = pd.DataFrame(
            {
                "open": [-10.0, 101.0],  # 包含负数
                "high": [102.0, 103.0],
                "low": [99.0, 100.0],
                "close": [100.5, 101.5],
                "volume": [1000, 2000],
            }
        )
        assert validator.validate_price_range(df_with_negative, 0.01, 10000.0) is False

    # === 数据完整性检查测试 ===
    def test_check_data_completeness_valid(self, validator, valid_price_dataframe):
        """测试完整数据检查"""
        assert validator.check_data_completeness(valid_price_dataframe) is True

    def test_check_data_completeness_custom_columns(self, validator):
        """测试自定义必需列的完整性检查"""
        df_with_extra_columns = pd.DataFrame(
            {
                "open": [100.0, 101.0],
                "high": [101.0, 102.0],
                "low": [99.0, 100.0],
                "close": [100.5, 101.5],
                "volume": [1000, 2000],
                "extra_column": [1, 2],
            }
        )

        custom_columns = ["open", "high", "low", "close"]
        assert (
            validator.check_data_completeness(df_with_extra_columns, custom_columns)
            is True
        )

    def test_check_data_completeness_missing_columns(self, validator):
        """测试缺少列的完整性检查"""
        df_missing_columns = pd.DataFrame(
            {
                "open": [100.0, 101.0],
                "high": [101.0, 102.0],
                "volume": [1000, 2000],
                # 缺少low, close
            }
        )
        assert validator.check_data_completeness(df_missing_columns) is False

    def test_check_data_completeness_empty_dataframe(self, validator):
        """测试空DataFrame的完整性检查"""
        empty_df = pd.DataFrame()
        assert validator.check_data_completeness(empty_df) is False

    def test_check_data_completeness_with_nan_values(self, validator):
        """测试包含NaN值的数据完整性检查"""
        df_with_nan = pd.DataFrame(
            {
                "open": [100.0, np.nan],
                "high": [101.0, 102.0],
                "low": [99.0, 100.0],
                "close": [100.5, 101.5],
                "volume": [1000, 2000],
            }
        )
        assert validator.check_data_completeness(df_with_nan) is False

    def test_check_data_completeness_with_none_values(self, validator):
        """测试包含None值的数据完整性检查"""
        df_with_none = pd.DataFrame(
            {
                "open": [100.0, None],
                "high": [101.0, 102.0],
                "low": [99.0, 100.0],
                "close": [100.5, 101.5],
                "volume": [1000, 2000],
            }
        )
        assert validator.check_data_completeness(df_with_none) is False


# 简化的边界条件测试 - 集成到主测试类中


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
