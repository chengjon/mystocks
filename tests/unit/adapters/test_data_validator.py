"""
Data Validator Test Suite
数据验证器测试套件

创建日期: 2025-12-20
版本: 1.0.0
测试模块: src.adapters.data_validator (242行)
"""

import pytest
import pandas as pd
import numpy as np

# 添加src路径到导入路径
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../src"))

from src.adapters.data_validator import DataValidator


class TestDataValidator:
    """数据验证器测试"""

    def test_data_validator_initialization(self):
        """测试数据验证器初始化"""
        validator = DataValidator()
        assert isinstance(validator, DataValidator)

    def test_validate_stock_symbol_valid_symbols(self):
        """测试有效股票代码验证"""
        validator = DataValidator()

        valid_symbols = ["000001", "600000", "300001", "002001"]
        for symbol in valid_symbols:
            assert validator.validate_stock_symbol(symbol), f"Symbol {symbol} should be valid"

    def test_validate_stock_symbol_invalid_symbols(self):
        """测试无效股票代码验证"""
        validator = DataValidator()

        invalid_symbols = [
            "",  # 空字符串
            None,  # None值
            "ABC123",  # 包含字母
            "12345",  # 少于6位
            "1234567",  # 超过6位
            "000001A",  # 包含字母
            123456,  # 数字而非字符串
            [],  # 列表
            {},  # 字典
            "00 0001",  # 内部空格
        ]
        for symbol in invalid_symbols:
            assert not validator.validate_stock_symbol(symbol), f"Symbol {symbol} should be invalid"

    def test_validate_stock_symbol_whitespace_handling(self):
        """测试股票代码空格处理"""
        validator = DataValidator()

        # 前后空格应该被处理
        assert validator.validate_stock_symbol(" 000001 ")
        # 内部空格应该无效
        assert not validator.validate_stock_symbol("00 0001")

    def test_validate_date_format_valid_dates(self):
        """测试有效日期格式验证"""
        validator = DataValidator()

        valid_dates = [
            "2024-01-01",  # 标准格式
            "2024-12-31",  # 年末
            "2020-02-29",  # 闰年
            "2024-1-1",  # 单数月份日期
            "2024-01-5",  # 单数日期
        ]
        for date in valid_dates:
            assert validator.validate_date_format(date), f"Date {date} should be valid"

    def test_validate_date_format_invalid_dates(self):
        """测试无效日期格式验证"""
        validator = DataValidator()

        invalid_dates = [
            "",  # 空字符串
            None,  # None值
            "2024/01/01",  # 错误分隔符
            "2024.01.01",  # 错误分隔符
            "24-01-01",  # 短年份
            "2024-13-01",  # 无效月份
            "2024-01-32",  # 无效日
            "2024-02-30",  # 无效日期（非闰年）
            "2024-00-01",  # 无效月份
            "invalid_date",  # 完全无效
            "2024",  # 只有年份
            "01-01-2024",  # 日月年格式
        ]
        for date in invalid_dates:
            assert not validator.validate_date_format(date), f"Date {date} should be invalid"

    def test_validate_date_range_valid(self):
        """测试有效日期范围验证"""
        validator = DataValidator()

        # 开始日期早于结束日期
        assert validator.validate_date_range("2024-01-01", "2024-01-05")
        assert validator.validate_date_range("2024-01-01", "2024-12-31")
        assert validator.validate_date_range("2020-01-01", "2024-01-01")

    def test_validate_date_range_invalid(self):
        """测试无效日期范围验证"""
        validator = DataValidator()

        # 相同日期
        assert not validator.validate_date_range("2024-01-01", "2024-01-01")

        # 开始日期晚于结束日期
        assert not validator.validate_date_range("2024-01-05", "2024-01-01")

        # 无效日期格式
        assert not validator.validate_date_range("invalid", "2024-01-05")
        assert not validator.validate_date_range("2024-01-01", "invalid")

    def test_validate_price_data_valid(self):
        """测试有效价格数据验证"""
        validator = DataValidator()

        # 创建有效的价格数据
        data = pd.DataFrame(
            {
                "open": [10.0, 10.5, 11.0],
                "high": [10.5, 11.0, 11.5],
                "low": [9.5, 10.0, 10.5],
                "close": [10.2, 10.8, 11.2],
                "volume": [1000, 1500, 2000],
            }
        )

        assert validator.validate_price_data(data)

    def test_validate_price_data_missing_columns(self):
        """测试缺少必需列的价格数据"""
        validator = DataValidator()

        # 缺少volume列
        data = pd.DataFrame(
            {
                "open": [10.0, 10.5],
                "high": [10.5, 11.0],
                "low": [9.5, 10.0],
                "close": [10.2, 10.8],
            }
        )

        assert not validator.validate_price_data(data)

    def test_validate_price_data_empty(self):
        """测试空价格数据"""
        validator = DataValidator()

        # 空DataFrame
        data = pd.DataFrame(columns=["open", "high", "low", "close", "volume"])
        assert not validator.validate_price_data(data)

    def test_validate_price_data_invalid_price_logic(self):
        """测试无效价格逻辑"""
        validator = DataValidator()

        # High < Low
        data1 = pd.DataFrame(
            {
                "open": [10.0],
                "high": [9.5],  # High < Low
                "low": [10.5],
                "close": [10.2],
                "volume": [1000],
            }
        )
        assert not validator.validate_price_data(data1)

        # High < Open
        data2 = pd.DataFrame(
            {
                "open": [10.5],
                "high": [10.0],  # High < Open
                "low": [9.5],
                "close": [10.2],
                "volume": [1000],
            }
        )
        assert not validator.validate_price_data(data2)

        # Low > Close
        data3 = pd.DataFrame(
            {
                "open": [10.0],
                "high": [10.5],
                "low": [10.8],  # Low > Close
                "close": [10.2],
                "volume": [1000],
            }
        )
        assert not validator.validate_price_data(data3)

    def test_validate_price_data_negative_prices(self):
        """测试负价格"""
        validator = DataValidator()

        # 负价格
        data = pd.DataFrame(
            {
                "open": [-10.0],  # 负价格
                "high": [10.5],
                "low": [9.5],
                "close": [10.2],
                "volume": [1000],
            }
        )
        assert not validator.validate_price_data(data)

    def test_validate_price_data_negative_volume(self):
        """测试负成交量"""
        validator = DataValidator()

        # 负成交量
        data = pd.DataFrame(
            {
                "open": [10.0],
                "high": [10.5],
                "low": [9.5],
                "close": [10.2],
                "volume": [-1000],  # 负成交量
            }
        )
        assert not validator.validate_price_data(data)

    def test_validate_price_data_non_numeric_values(self):
        """测试非数值价格数据"""
        validator = DataValidator()

        # 完全非数值的价格（无法转换为float）
        data = pd.DataFrame(
            {
                "open": ["abc"],
                "high": [10.5],
                "low": [9.5],
                "close": [10.2],
                "volume": [1000],
            }
        )
        assert not validator.validate_price_data(data)

    def test_validate_volume_data_valid(self):
        """测试有效成交量数据"""
        validator = DataValidator()

        data = pd.DataFrame({"volume": [1000, 1500, 2000, 0]})

        assert validator.validate_volume_data(data)

    def test_validate_volume_data_missing_column(self):
        """测试缺少volume列"""
        validator = DataValidator()

        data = pd.DataFrame({"open": [10.0], "close": [10.2]})

        assert not validator.validate_volume_data(data)

    def test_validate_volume_data_empty(self):
        """测试空成交量数据"""
        validator = DataValidator()

        data = pd.DataFrame(columns=["volume"])
        assert not validator.validate_volume_data(data)

    def test_validate_volume_data_negative_values(self):
        """测试负成交量值"""
        validator = DataValidator()

        data = pd.DataFrame({"volume": [1000, -500, 2000]})  # 包含负值

        assert not validator.validate_volume_data(data)

    def test_validate_volume_data_nan_values(self):
        """测试NaN成交量值"""
        validator = DataValidator()

        data = pd.DataFrame({"volume": [1000, np.nan, 2000]})  # 包含NaN

        assert not validator.validate_volume_data(data)

    def test_validate_trading_day_valid_weekday(self):
        """测试有效工作日"""
        validator = DataValidator()

        # 周一到周五
        assert validator.validate_trading_day("2024-01-01")  # 周一
        assert validator.validate_trading_day("2024-01-05")  # 周五

    def test_validate_trading_day_weekend(self):
        """测试周末"""
        validator = DataValidator()

        # 周六和周日
        assert not validator.validate_trading_day("2024-01-06")  # 周六
        assert not validator.validate_trading_day("2024-01-07")  # 周日

    def test_validate_trading_day_invalid_date(self):
        """测试无效日期"""
        validator = DataValidator()

        assert not validator.validate_trading_day("invalid_date")

    def test_validate_price_range_valid(self):
        """测试有效价格范围"""
        validator = DataValidator()

        data = pd.DataFrame(
            {
                "open": [10.0, 50.0],
                "high": [10.5, 50.5],
                "low": [9.5, 49.5],
                "close": [10.2, 50.2],
            }
        )

        assert validator.validate_price_range(data, min_price=1.0, max_price=100.0)

    def test_validate_price_range_out_of_range(self):
        """测试超出范围价格"""
        validator = DataValidator()

        # 低于最小价格
        data1 = pd.DataFrame(
            {
                "open": [0.5],  # 低于min_price=1.0
                "high": [10.5],
                "low": [9.5],
                "close": [10.2],
            }
        )
        assert not validator.validate_price_range(data1, min_price=1.0, max_price=100.0)

        # 高于最大价格
        data2 = pd.DataFrame(
            {
                "open": [10.0],
                "high": [150.0],  # 高于max_price=100.0
                "low": [9.5],
                "close": [10.2],
            }
        )
        assert not validator.validate_price_range(data2, min_price=1.0, max_price=100.0)

    def test_validate_price_range_partial_columns(self):
        """测试部分价格列"""
        validator = DataValidator()

        # 只有部分价格列
        data = pd.DataFrame(
            {
                "open": [10.0],
                "close": [10.2],
                # 缺少high和low列
            }
        )

        # 应该返回True（只验证存在的列）
        assert validator.validate_price_range(data)

    def test_check_data_completeness_valid(self):
        """测试有效数据完整性检查"""
        validator = DataValidator()

        data = pd.DataFrame(
            {
                "open": [10.0, 10.5],
                "high": [10.5, 11.0],
                "low": [9.5, 10.0],
                "close": [10.2, 10.8],
                "volume": [1000, 1500],
            }
        )

        assert validator.check_data_completeness(data)

    def test_check_data_completeness_empty_data(self):
        """测试空数据完整性检查"""
        validator = DataValidator()

        data = pd.DataFrame(columns=["open", "high", "low", "close", "volume"])
        assert not validator.check_data_completeness(data)

    def test_check_data_completeness_missing_columns(self):
        """测试缺少列的完整性检查"""
        validator = DataValidator()

        data = pd.DataFrame(
            {
                "open": [10.0],
                "close": [10.2],
                # 缺少high, low, volume列
            }
        )

        assert not validator.check_data_completeness(data)

    def test_check_data_completeness_with_nulls(self):
        """测试包含空值的数据完整性检查"""
        validator = DataValidator()

        # 包含NaN值
        data = pd.DataFrame(
            {
                "open": [10.0, np.nan],  # 包含NaN
                "high": [10.5, 11.0],
                "low": [9.5, 10.0],
                "close": [10.2, 10.8],
                "volume": [1000, 1500],
            }
        )

        assert not validator.check_data_completeness(data)

    def test_check_data_completeness_custom_columns(self):
        """测试自定义列的完整性检查"""
        validator = DataValidator()

        data = pd.DataFrame({"symbol": ["000001", "000002"], "price": [10.0, 10.5]})

        # 使用自定义必需列
        assert validator.check_data_completeness(data, required_columns=["symbol", "price"])


class TestDataValidatorAdvanced:
    """数据验证器高级测试"""

    def test_validate_price_data_edge_cases(self):
        """测试价格数据边界情况"""
        validator = DataValidator()

        # 极小价格值
        data1 = pd.DataFrame(
            {
                "open": [0.01],
                "high": [0.02],
                "low": [0.005],
                "close": [0.015],
                "volume": [1],
            }
        )
        assert validator.validate_price_data(data1)

        # 零成交量
        data2 = pd.DataFrame(
            {
                "open": [10.0],
                "high": [10.5],
                "low": [9.5],
                "close": [10.2],
                "volume": [0],
            }
        )
        assert validator.validate_price_data(data2)

    def test_validate_price_data_large_dataset(self):
        """测试大数据集验证性能"""
        validator = DataValidator()

        # 创建1000行数据
        np.random.seed(42)
        data = pd.DataFrame(
            {
                "open": np.random.uniform(1, 100, 1000),
                "high": np.random.uniform(1, 100, 1000),
                "low": np.random.uniform(1, 100, 1000),
                "close": np.random.uniform(1, 100, 1000),
                "volume": np.random.randint(1000, 100000, 1000),
            }
        )

        # 修正价格逻辑关系
        for i in range(len(data)):
            open_price = data.loc[i, "open"]
            data.loc[i, "high"] = max(data.loc[i, "high"], open_price)
            data.loc[i, "low"] = min(data.loc[i, "low"], open_price)
            data.loc[i, "close"] = np.random.uniform(data.loc[i, "low"], data.loc[i, "high"])

        assert validator.validate_price_data(data)

    def test_validate_price_data_exact_equal_prices(self):
        """测试相等价格的特殊情况"""
        validator = DataValidator()

        # 所有价格相等（开盘=最高=最低=收盘）
        data = pd.DataFrame(
            {
                "open": [10.0, 10.0],
                "high": [10.0, 10.0],
                "low": [10.0, 10.0],
                "close": [10.0, 10.0],
                "volume": [1000, 2000],
            }
        )

        assert validator.validate_price_data(data)

    def test_validate_volume_data_large_numbers(self):
        """测试大数值成交量"""
        validator = DataValidator()

        # 非常大的成交量数值
        data = pd.DataFrame({"volume": [1000000000, 5000000000, 9999999999]})

        assert validator.validate_volume_data(data)

    def test_validate_trading_day_leap_year(self):
        """测试闰年交易日"""
        validator = DataValidator()

        # 2024年是闰年，2月29日存在，检查是否为工作日
        # 2024-02-29是周四，应该是交易日
        assert validator.validate_trading_day("2024-02-29")
        # 2020年是闰年，但2月29日是周六，不是交易日
        assert not validator.validate_trading_day("2020-02-29")
        # 2023年不是闰年，2月29日不存在
        assert not validator.validate_date_format("2023-02-29")

    def test_validate_price_range_default_parameters(self):
        """测试价格范围默认参数"""
        validator = DataValidator()

        # 使用默认参数
        data = pd.DataFrame(
            {
                "open": [10.0, 10000.0],
                "high": [10.5, 10050.0],
                "low": [9.5, 9950.0],
                "close": [10.0, 10000.0],
            }
        )

        # 默认范围是0.01到10000.0
        assert not validator.validate_price_range(data)  # 10050.0超出默认最大值

    def test_validate_date_range_edge_cases(self):
        """测试日期范围边界情况"""
        validator = DataValidator()

        # 相差一秒的时间差异
        assert validator.validate_date_range("2024-01-01", "2024-01-02")

        # 跨年范围
        assert validator.validate_date_range("2023-12-31", "2024-01-01")

    def test_validator_error_handling(self):
        """测试验证器错误处理"""
        validator = DataValidator()

        # 测试各种错误输入
        test_cases = [
            ("validate_stock_symbol", ["", None, {}, []]),
            ("validate_date_format", ["", None, "invalid"]),
            ("validate_date_range", ["invalid", "2024-01-01"]),
            ("validate_price_data", ["not_dataframe", 123, None]),
            ("validate_volume_data", ["not_dataframe", 123, None]),
            ("validate_trading_day", ["invalid", None]),
            ("validate_price_range", ["not_dataframe", 123, None]),
            ("check_data_completeness", ["not_dataframe", 123, None]),
        ]

        for method_name, invalid_inputs in test_cases:
            method = getattr(validator, method_name)
            for invalid_input in invalid_inputs:
                # 大多数方法应该优雅地处理无效输入
                try:
                    result = method(invalid_input)
                    # 对于某些方法，某些无效输入可能返回False而不是抛出异常
                    assert isinstance(result, bool)
                except (TypeError, AttributeError, ValueError):
                    # 预期的异常
                    pass

    def test_comprehensive_validation_integration(self):
        """测试综合验证集成"""
        validator = DataValidator()

        # 创建一个完整的金融数据集
        data = pd.DataFrame(
            {
                "date": pd.date_range("2024-01-01", periods=5, freq="D"),
                "symbol": ["000001"] * 5,
                "open": [10.0, 10.2, 10.1, 10.3, 10.4],
                "high": [10.5, 10.7, 10.6, 10.8, 10.9],
                "low": [9.5, 9.8, 9.7, 9.9, 10.0],
                "close": [10.2, 10.5, 10.3, 10.6, 10.7],
                "volume": [1000, 1200, 1100, 1300, 1400],
            }
        )

        # 验证各个方面
        assert validator.validate_stock_symbol(data["symbol"][0])
        assert validator.validate_date_format("2024-01-01")
        assert validator.validate_date_range("2024-01-01", "2024-01-05")
        assert validator.validate_price_data(data[["open", "high", "low", "close", "volume"]])
        assert validator.validate_volume_data(data[["volume"]])
        assert validator.validate_trading_day("2024-01-01")  # 假设是工作日
        assert validator.validate_price_range(data[["open", "high", "low", "close"]])
        assert validator.check_data_completeness(data[["open", "high", "low", "close", "volume"]])


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])
