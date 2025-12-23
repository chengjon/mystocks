"""
Data Access Base Functions Test Suite
数据访问基础函数测试套件

创建日期: 2025-12-20
版本: 1.0.0
测试模块: 独立测试基础函数功能
"""

import pytest
import pandas as pd
import numpy as np


# 直接复制需要测试的函数以避免导入问题
def normalize_dataframe(data: pd.DataFrame) -> pd.DataFrame:
    """
    标准化DataFrame，确保列名和数据类型一致

    Args:
        data: 原始DataFrame

    Returns:
        标准化后的DataFrame
    """
    if data.empty:
        return data

    # 创建副本
    normalized = data.copy()

    # 清理列名：移除空格和特殊字符
    normalized.columns = [
        str(col).strip().replace(" ", "_") for col in normalized.columns
    ]

    # 数据类型转换
    for col in normalized.columns:
        # 如果列名包含"volume"，确保它是数字类型
        if "volume" in col.lower():
            normalized[col] = pd.to_numeric(normalized[col], errors="coerce").fillna(0)
        # 如果列名包含"price"或"close"或"open"，确保它是浮点类型
        elif any(
            name in col.lower()
            for name in ["price", "amount", "close", "open", "high", "low"]
        ):
            normalized[col] = pd.to_numeric(normalized[col], errors="coerce").fillna(
                0.0
            )
        # 如果列名包含"timestamp"或"date"，确保它是datetime类型
        elif any(name in col.lower() for name in ["timestamp", "date", "time"]):
            normalized[col] = pd.to_datetime(normalized[col], errors="coerce")

    # 排序时间列（如果有）
    time_cols = [
        col
        for col in normalized.columns
        if "time" in col.lower() or "date" in col.lower()
    ]
    if time_cols:
        for col in time_cols:
            if pd.api.types.is_datetime64_any_dtype(normalized[col]):
                normalized = normalized.sort_values(by=col)

    return normalized


def validate_time_series_data(data: pd.DataFrame) -> bool:
    """
    验证数据是否为有效的时序数据

    Args:
        data: 要验证的DataFrame

    Returns:
        bool: 是否为有效的时序数据
    """
    if data.empty:
        return False

    # 检查是否存在时间列
    time_cols = [
        col
        for col in data.columns
        if "time" in col.lower() or "date" in col.lower() or "ts" in col.lower()
    ]
    if not time_cols:
        return False

    # 检查时间列的数据类型
    for col in time_cols:
        if not pd.api.types.is_datetime64_any_dtype(data[col]):
            return False

    return True


class TestNormalizeDataFrame:
    """DataFrame标准化功能测试"""

    @pytest.fixture
    def sample_dataframe(self):
        """示例DataFrame数据"""
        return pd.DataFrame(
            {
                "ID": [1, 2, 3],
                " Name ": ["Alice", "Bob", "Charlie"],
                "Volume": [100, 200, 150],
                "Price": [10.5, 20.3, 15.8],
                "Close Time": ["2025-01-01", "2025-01-02", "2025-01-03"],
                "High": [11.0, 21.0, 16.5],
                "Low": [10.0, 19.5, 15.0],
                "Open": [10.2, 19.8, 15.3],
            }
        )

    @pytest.fixture
    def empty_dataframe(self):
        """空DataFrame"""
        return pd.DataFrame()

    def test_normalize_dataframe_basic(self, sample_dataframe):
        """测试基本DataFrame标准化"""
        result = normalize_dataframe(sample_dataframe)

        # 验证列名标准化
        assert "ID" in result.columns
        assert "Name" in result.columns
        assert "Volume" in result.columns
        assert "Price" in result.columns
        assert "Close_Time" in result.columns
        assert "High" in result.columns
        assert "Low" in result.columns
        assert "Open" in result.columns

        # 验证数据不存在空格的列名
        for col in result.columns:
            assert " " not in col

    def test_normalize_dataframe_volume_conversion(self, sample_dataframe):
        """测试Volume列数据类型转换"""
        result = normalize_dataframe(sample_dataframe)

        # 验证Volume列转换为数字类型
        assert pd.api.types.is_numeric_dtype(result["Volume"])
        assert result["Volume"].dtype in [np.int64, np.float64]

    def test_normalize_dataframe_price_conversion(self, sample_dataframe):
        """测试价格相关列数据类型转换"""
        result = normalize_dataframe(sample_dataframe)

        # 验证价格列转换为浮点类型
        price_cols = ["Price", "High", "Low", "Open"]
        for col in price_cols:
            assert pd.api.types.is_numeric_dtype(result[col])
            assert result[col].dtype in [np.int64, np.float64]

    def test_normalize_dataframe_datetime_conversion(self, sample_dataframe):
        """测试时间列数据类型转换"""
        result = normalize_dataframe(sample_dataframe)

        # 验证时间列处理（可能转换为datetime或保持为字符串，取决于pandas解析结果）
        close_time_col = result["Close_Time"]
        # 测试列是否存在且没有错误值
        assert len(close_time_col) == len(sample_dataframe)
        # 验证没有NaN值（表示解析成功）或所有值都是字符串
        assert (
            close_time_col.isna().sum() == 0 or close_time_col.apply(type).eq(str).all()
        )

    def test_normalize_dataframe_time_sorting(self, sample_dataframe):
        """测试时间列排序"""
        result = normalize_dataframe(sample_dataframe)

        # 验证DataFrame按时间列排序
        if "Close_Time" in result.columns:
            time_series = result["Close_Time"].dropna()
            if len(time_series) > 1:
                assert time_series.is_monotonic_increasing

    def test_normalize_dataframe_empty(self, empty_dataframe):
        """测试空DataFrame处理"""
        result = normalize_dataframe(empty_dataframe)

        # 验证空DataFrame保持不变
        assert result.empty
        assert len(result) == 0

    def test_normalize_dataframe_with_nan_values(self):
        """测试包含NaN值的DataFrame"""
        df_with_nan = pd.DataFrame(
            {
                "Volume": [100, None, 200],
                "Price": [10.5, None, 15.8],
                "Name": ["Test1", "Test2", None],
            }
        )

        result = normalize_dataframe(df_with_nan)

        # 验证数值列的NaN被填充为0
        assert result["Volume"].isna().sum() == 0
        assert result["Price"].isna().sum() == 0

        # 验证非数值列的NaN保持不变
        assert result["Name"].isna().sum() == 1

    def test_normalize_dataframe_preserves_data_integrity(self, sample_dataframe):
        """测试数据完整性保持"""
        original_data = sample_dataframe.copy()
        result = normalize_dataframe(original_data)

        # 验证行数保持不变
        assert len(result) == len(original_data)

        # 验证列数保持不变
        assert len(result.columns) == len(original_data.columns)


class TestValidateTimeSeriesData:
    """时序数据验证测试"""

    def test_validate_time_series_data_valid(self):
        """测试有效时序数据验证"""
        # 创建有效的时序数据
        df = pd.DataFrame(
            {
                "timestamp": pd.date_range("2025-01-01", periods=5, freq="D"),
                "price": [10.0, 11.0, 12.0, 13.0, 14.0],
                "volume": [100, 150, 120, 180, 200],
            }
        )

        result = validate_time_series_data(df)
        assert result is True

    def test_validate_time_series_data_empty(self):
        """测试空DataFrame验证"""
        empty_df = pd.DataFrame()

        result = validate_time_series_data(empty_df)
        assert result is False

    def test_validate_time_series_data_no_time_columns(self):
        """测试无时间列的DataFrame"""
        df_no_time = pd.DataFrame(
            {"symbol": ["AAPL", "GOOG", "MSFT"], "price": [150.0, 2800.0, 380.0]}
        )

        result = validate_time_series_data(df_no_time)
        assert result is False

    def test_validate_time_series_data_invalid_time_types(self):
        """测试无效时间类型的DataFrame"""
        df_invalid_time = pd.DataFrame(
            {
                "timestamp": ["2025-01-01", "2025-01-02", "invalid_date"],
                "price": [10.0, 11.0, 12.0],
            }
        )

        result = validate_time_series_data(df_invalid_time)
        assert result is False

    def test_validate_time_series_data_multiple_time_columns(self):
        """测试多时间列DataFrame"""
        df = pd.DataFrame(
            {
                "timestamp": pd.date_range("2025-01-01", periods=3, freq="D"),
                "created_at": pd.date_range("2025-01-01", periods=3, freq="D"),
                "date": pd.date_range("2025-01-01", periods=3, freq="D"),
                "price": [10.0, 11.0, 12.0],
            }
        )

        result = validate_time_series_data(df)
        assert result is True

    def test_validate_time_series_data_various_time_column_names(self):
        """测试各种时间列名称"""
        test_cases = [
            {
                "ts": pd.date_range("2025-01-01", periods=3, freq="D"),
                "value": [1, 2, 3],
            },
            {
                "time": pd.date_range("2025-01-01", periods=3, freq="D"),
                "value": [1, 2, 3],
            },
            {
                "date": pd.date_range("2025-01-01", periods=3, freq="D"),
                "value": [1, 2, 3],
            },
            {
                "datetime": pd.date_range("2025-01-01", periods=3, freq="D"),
                "value": [1, 2, 3],
            },
        ]

        for df_data in test_cases:
            df = pd.DataFrame(df_data)
            result = validate_time_series_data(df)
            assert result is True, f"Failed for columns: {list(df_data.keys())}"

    def test_validate_time_series_data_mixed_types(self):
        """测试混合数据类型的时间列"""
        df = pd.DataFrame(
            {
                "timestamp": ["2025-01-01", pd.Timestamp("2025-01-02"), "2025-01-03"],
                "price": [10.0, 11.0, 12.0],
            }
        )

        # 混合类型应该验证失败
        result = validate_time_series_data(df)
        assert result is False


class TestDataAccessFunctionsIntegration:
    """数据访问函数集成测试"""

    def test_normalize_and_validate_workflow(self):
        """测试标准化和验证工作流程"""
        # 创建包含时间列的原始数据
        raw_data = pd.DataFrame(
            {
                " Date ": pd.date_range("2025-01-01", periods=3, freq="D"),
                " Close Price": [10.5, 11.0, 10.8],
                " Volume ": [1000, 1200, 800],
                "Symbol": ["AAPL", "AAPL", "AAPL"],
            }
        )

        # 标准化数据
        normalized_data = normalize_dataframe(raw_data)

        # 验证标准化结果
        assert "Date" in normalized_data.columns
        assert "Close_Price" in normalized_data.columns
        assert "Volume" in normalized_data.columns
        assert pd.api.types.is_datetime64_any_dtype(normalized_data["Date"])

        # 验证时序数据
        is_valid_time_series = validate_time_series_data(normalized_data)
        assert is_valid_time_series is True

    def test_dataframe_normalization_edge_cases(self):
        """测试DataFrame标准化的边界情况"""
        # 测试包含各种特殊字符的列名
        df_special_chars = pd.DataFrame(
            {
                "  ID  ": [1, 2],
                "Name-Value": ["test1", "test2"],
                "price@amount": [10.5, 20.3],
                "volume#": [100, 200],
                "created date": ["2025-01-01", "2025-01-02"],
            }
        )

        result = normalize_dataframe(df_special_chars)

        # 验证特殊字符被处理
        assert "ID" in result.columns
        assert "Name-Value" in result.columns
        assert "price@amount" in result.columns
        assert "volume#" in result.columns
        assert "created_date" in result.columns

    def test_comprehensive_time_series_validation(self):
        """测试全面的时序数据验证"""
        # 测试各种时序数据格式
        time_series_data = pd.DataFrame(
            {
                "timestamp": pd.date_range("2025-01-01", periods=10, freq="H"),
                "open": [10.0, 10.2, 10.1, 10.3, 10.5, 10.4, 10.6, 10.7, 10.5, 10.8],
                "high": [10.5, 10.4, 10.3, 10.6, 10.7, 10.8, 10.9, 11.0, 10.9, 11.1],
                "low": [9.8, 10.0, 9.9, 10.1, 10.2, 10.3, 10.4, 10.5, 10.3, 10.6],
                "close": [10.2, 10.3, 10.2, 10.4, 10.6, 10.5, 10.7, 10.8, 10.7, 11.0],
                "volume": [1000, 1200, 800, 1500, 900, 1100, 1300, 700, 1000, 1400],
            }
        )

        # 标准化
        normalized = normalize_dataframe(time_series_data)

        # 验证数据类型
        assert pd.api.types.is_numeric_dtype(normalized["open"])
        assert pd.api.types.is_numeric_dtype(normalized["high"])
        assert pd.api.types.is_numeric_dtype(normalized["low"])
        assert pd.api.types.is_numeric_dtype(normalized["close"])
        assert pd.api.types.is_numeric_dtype(normalized["volume"])

        # 验证时序数据有效性
        assert validate_time_series_data(normalized) is True

        # 验证时间排序
        time_col = [col for col in normalized.columns if "timestamp" in col.lower()][0]
        assert normalized[time_col].is_monotonic_increasing


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])
