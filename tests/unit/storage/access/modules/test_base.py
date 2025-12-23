"""
Data Access Base Module Test Suite
数据访问基础模块测试套件

创建日期: 2025-12-20
版本: 1.0.0
测试模块: src.storage.access.modules.base (167行)
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch

# Test target imports
from src.storage.access.modules.base import (
    IDataAccessLayer,
    normalize_dataframe,
    validate_time_series_data,
    get_database_name_from_classification,
)
from src.core import DataClassification


class TestIDataAccessLayer:
    """数据访问层接口测试"""

    def test_interface_is_abstract(self):
        """测试接口是抽象类"""
        assert hasattr(IDataAccessLayer, "__abstractmethods__")

        # 验证所有抽象方法
        abstract_methods = IDataAccessLayer.__abstractmethods__
        assert "save_data" in abstract_methods
        assert "load_data" in abstract_methods
        assert "update_data" in abstract_methods
        assert "delete_data" in abstract_methods

    def test_cannot_instantiate_abstract_class(self):
        """测试不能实例化抽象类"""
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IDataAccessLayer()

    def test_concrete_implementation(self):
        """测试具体实现可以正常工作"""

        class TestDataAccess(IDataAccessLayer):
            def save_data(self, data, classification, table_name=None, **kwargs):
                return True

            def load_data(
                self, classification, table_name=None, filters=None, **kwargs
            ):
                return pd.DataFrame()

            def update_data(
                self, data, classification, table_name=None, key_columns=None, **kwargs
            ):
                return True

            def delete_data(
                self, classification, table_name=None, filters=None, **kwargs
            ):
                return True

        # 测试可以实例化具体实现
        data_access = TestDataAccess()
        assert isinstance(data_access, IDataAccessLayer)

        # 测试所有方法都能正常调用
        test_df = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})
        assert data_access.save_data(test_df, DataClassification.MARKET_DATA)
        assert isinstance(
            data_access.load_data(DataClassification.REFERENCE_DATA), pd.DataFrame
        )
        assert data_access.update_data(test_df, DataClassification.TRANSACTION_DATA)
        assert data_access.delete_data(DataClassification.DERIVED_DATA)


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

        # 验证时间列转换为datetime类型
        assert pd.api.types.is_datetime64_any_dtype(result["Close_Time"])

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


class TestGetDatabaseNameFromClassification:
    """数据库名称获取测试"""

    @pytest.fixture
    def mock_data_manager(self):
        """模拟DataManager"""
        with patch("src.storage.access.modules.base.DataManager") as mock_dm:
            mock_instance = Mock()
            mock_dm.return_value = mock_instance
            yield mock_instance

    def test_get_database_name_market_data(self, mock_data_manager):
        """测试市场数据分类获取数据库名"""
        mock_data_manager.get_database_name.return_value = "mystocks_market"

        result = get_database_name_from_classification(DataClassification.MARKET_DATA)

        assert result == "mystocks_market"
        mock_data_manager.get_database_name.assert_called_once_with(
            DataClassification.MARKET_DATA
        )

    def test_get_database_name_reference_data(self, mock_data_manager):
        """测试参考数据分类获取数据库名"""
        mock_data_manager.get_database_name.return_value = "mystocks_reference"

        result = get_database_name_from_classification(
            DataClassification.REFERENCE_DATA
        )

        assert result == "mystocks_reference"
        mock_data_manager.get_database_name.assert_called_once_with(
            DataClassification.REFERENCE_DATA
        )

    def test_get_database_name_transaction_data(self, mock_data_manager):
        """测试交易数据分类获取数据库名"""
        mock_data_manager.get_database_name.return_value = "mystocks_transaction"

        result = get_database_name_from_classification(
            DataClassification.TRANSACTION_DATA
        )

        assert result == "mystocks_transaction"
        mock_data_manager.get_database_name.assert_called_once_with(
            DataClassification.TRANSACTION_DATA
        )

    def test_get_database_name_derived_data(self, mock_data_manager):
        """测试衍生数据分类获取数据库名"""
        mock_data_manager.get_database_name.return_value = "mystocks_derived"

        result = get_database_name_from_classification(DataClassification.DERIVED_DATA)

        assert result == "mystocks_derived"
        mock_data_manager.get_database_name.assert_called_once_with(
            DataClassification.DERIVED_DATA
        )

    def test_get_database_name_metadata(self, mock_data_manager):
        """测试元数据分类获取数据库名"""
        mock_data_manager.get_database_name.return_value = "mystocks_metadata"

        result = get_database_name_from_classification(DataClassification.METADATA)

        assert result == "mystocks_metadata"
        mock_data_manager.get_database_name.assert_called_once_with(
            DataClassification.METADATA
        )


class TestDataAccessModuleIntegration:
    """数据访问模块集成测试"""

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
