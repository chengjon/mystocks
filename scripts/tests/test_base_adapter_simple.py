#!/usr/bin/env python3
"""
BaseDataSourceAdapter Phase 6 测试套件 - 简化有效版
专注于实际可测试的代码路径，避免复杂Mock问题
目标：将base_adapter.py的覆盖率从55%提升到95%+
"""

import sys
import os
import time
import pandas as pd
import numpy as np
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest
from datetime import datetime

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 导入被测试的模块
from src.adapters.base_adapter import BaseDataSourceAdapter, QualityMixin


class MockDataSourceAdapter(BaseDataSourceAdapter):
    """模拟数据源适配器用于测试"""

    def __init__(self, source_name="test_adapter"):
        super().__init__(source_name)


class MockDataSourceAdapterWithMixin(QualityMixin, BaseDataSourceAdapter):
    """模拟带QualityMixin的适配器用于测试"""

    def __init__(self, source_name="mixin_test"):
        BaseDataSourceAdapter.__init__(self, source_name)


class TestBaseDataSourceAdapterBasic:
    """BaseDataSourceAdapter基础功能测试"""

    def test_initialization(self):
        """测试适配器初始化"""
        adapter = MockDataSourceAdapter("test_source")
        assert adapter.source_name == "test_source"
        assert adapter.quality_validator is not None
        assert adapter.logger is not None

    def test_initialization_multiple_sources(self):
        """测试多个数据源的初始化"""
        sources = ["akshare", "tushare", "baostock", "financial", "custom"]
        for source in sources:
            adapter = MockDataSourceAdapter(source)
            assert adapter.source_name == source
            assert adapter.quality_validator is not None

    @patch("src.adapters.base_adapter.DataQualityValidator")
    def test_initialization_with_mock_validator(self, mock_validator_class):
        """测试使用Mock验证器的初始化"""
        mock_validator = Mock()
        mock_validator_class.return_value = mock_validator

        adapter = MockDataSourceAdapter("mocked_source")

        mock_validator_class.assert_called_once_with("mocked_source")
        assert adapter.quality_validator == mock_validator


class TestApplyQualityCheck:
    """测试_apply_quality_check方法"""

    def setup_method(self):
        """pytest setup方法"""
        self.adapter = MockDataSourceAdapter("quality_test")

    def test_apply_quality_check_empty_dataframe(self):
        """测试空DataFrame的质量检查"""
        empty_df = pd.DataFrame()

        # 使用patch来模拟validate_stock_data方法
        with patch.object(
            self.adapter.quality_validator, "validate_stock_data"
        ) as mock_validate:
            mock_validate.return_value = {
                "is_valid": True,
                "quality_score": 1.0,
                "issues": [],
            }

            result = self.adapter._apply_quality_check(empty_df, "600000", "daily")

            assert isinstance(result, pd.DataFrame)
            assert result.empty

    def test_apply_quality_check_valid_dataframe(self):
        """测试有效DataFrame的质量检查"""
        valid_df = pd.DataFrame(
            {
                "date": pd.date_range("2024-01-01", periods=5),
                "open": [10.0, 10.5, 11.0, 10.8, 11.2],
                "close": [10.3, 10.8, 11.1, 10.9, 11.3],
                "volume": [1000, 1200, 900, 1100, 1300],
            }
        )

        with patch.object(
            self.adapter.quality_validator, "validate_stock_data"
        ) as mock_validate:
            mock_validate.return_value = {
                "is_valid": True,
                "quality_score": 0.95,
                "issues": [],
            }

            result = self.adapter._apply_quality_check(valid_df, "000001", "daily")

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 5
            mock_validate.assert_called_once()

    def test_apply_quality_check_with_warning_issues(self):
        """测试有警告问题的DataFrame"""
        df = pd.DataFrame(
            {
                "date": pd.date_range("2024-01-01", periods=3),
                "close": [10.0, np.nan, 12.0],
            }
        )

        with patch.object(
            self.adapter.quality_validator, "validate_stock_data"
        ) as mock_validate:
            mock_validate.return_value = {
                "is_valid": False,
                "quality_score": 0.7,
                "issues": [
                    {
                        "type": "missing_values",
                        "message": "包含缺失值",
                        "severity": "warning",
                    }
                ],
            }

            result = self.adapter._apply_quality_check(df, "000001", "daily")

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 3
            mock_validate.assert_called_once()

    def test_apply_quality_check_with_critical_issues(self):
        """测试有严重问题的DataFrame"""
        df = pd.DataFrame({"test": [1, 2, 3]})

        with patch.object(
            self.adapter.quality_validator, "validate_stock_data"
        ) as mock_validate:
            mock_validate.return_value = {
                "is_valid": False,
                "quality_score": 0.3,
                "issues": [
                    {
                        "type": "missing_columns",
                        "message": "缺少必需列",
                        "severity": "critical",
                    }
                ],
            }

            result = self.adapter._apply_quality_check(df, "000001", "daily")

            assert isinstance(result, pd.DataFrame)
            mock_validate.assert_called_once()

    def test_apply_quality_check_exception_handling(self):
        """测试质量检查异常处理"""
        df = pd.DataFrame({"test": [1, 2, 3]})

        with patch.object(
            self.adapter.quality_validator, "validate_stock_data"
        ) as mock_validate:
            mock_validate.side_effect = Exception("Quality check failed")

            result = self.adapter._apply_quality_check(df, "000001", "daily")

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 3


class TestApplyQualityCheckRealtime:
    """测试_apply_quality_check_realtime方法"""

    def setup_method(self):
        """pytest setup方法"""
        self.adapter = MockDataSourceAdapter("realtime_test")

    def test_apply_quality_check_realtime_empty_dict(self):
        """测试实时空数据的质量检查"""
        empty_data = {}

        result = self.adapter._apply_quality_check_realtime(empty_data, "600000")

        assert isinstance(result, dict)
        assert len(result) == 0

    def test_apply_quality_check_realtime_valid_data(self):
        """测试实时有效数据的质量检查"""
        valid_data = {
            "price": 10.5,
            "volume": 1000,
            "timestamp": datetime.now().isoformat(),
        }

        with patch.object(
            self.adapter.quality_validator, "validate_stock_data"
        ) as mock_validate:
            mock_validate.return_value = {
                "is_valid": True,
                "quality_score": 0.9,
                "issues": [],
            }

            result = self.adapter._apply_quality_check_realtime(valid_data, "000001")

            assert isinstance(result, dict)
            assert result["price"] == 10.5
            mock_validate.assert_called_once()

    def test_apply_quality_check_realtime_add_timestamp(self):
        """测试实时数据自动添加时间戳"""
        data_without_timestamp = {"price": 10.5, "volume": 1000}

        with patch.object(
            self.adapter.quality_validator, "validate_stock_data"
        ) as mock_validate:

            def check_timestamp(df, symbol, data_type):
                assert "timestamp" in df.columns
                return {"is_valid": True, "quality_score": 0.9, "issues": []}

            mock_validate.side_effect = check_timestamp

            result = self.adapter._apply_quality_check_realtime(
                data_without_timestamp, "000001"
            )

            assert isinstance(result, dict)
            assert result["price"] == 10.5

    def test_apply_quality_check_realtime_exception(self):
        """测试实时质量检查异常处理"""
        valid_data = {"price": 10.5, "volume": 1000}

        with patch.object(
            self.adapter.quality_validator, "validate_stock_data"
        ) as mock_validate:
            mock_validate.side_effect = Exception("Realtime quality check failed")

            result = self.adapter._apply_quality_check_realtime(valid_data, "000001")

            assert isinstance(result, dict)
            assert result["price"] == 10.5


class TestLogDataFetch:
    """测试_log_data_fetch方法"""

    def setup_method(self):
        """pytest setup方法"""
        self.adapter = MockDataSourceAdapter("logging_test")

    def test_log_data_fetch_basic(self):
        """测试基本数据获取日志"""
        with patch.object(self.adapter.logger, "info") as mock_info:
            self.adapter._log_data_fetch("000001", "daily", 100)

            mock_info.assert_called_once()
            log_message = mock_info.call_args[0][0]
            assert "000001" in log_message
            assert "daily" in log_message
            assert "100" in log_message

    def test_log_data_fetch_with_columns(self):
        """测试带列名的数据获取日志"""
        columns = ["date", "open", "high", "low", "close", "volume"]

        with patch.object(self.adapter.logger, "info") as mock_info:
            with patch.object(self.adapter.logger, "debug") as mock_debug:
                self.adapter._log_data_fetch("000001", "daily", 100, columns)

                mock_info.assert_called_once()
                mock_debug.assert_called_once()
                debug_message = mock_debug.call_args[0][0]
                assert (
                    "['date', 'open', 'high', 'low', 'close', 'volume']"
                    in debug_message
                )


class TestHandleEmptyData:
    """测试_handle_empty_data方法"""

    def setup_method(self):
        """pytest setup方法"""
        self.adapter = MockDataSourceAdapter("empty_data_test")

    def test_handle_empty_data_with_fallback(self):
        """测试带回退数据的空数据处理"""
        fallback_data = pd.DataFrame({"test": [1, 2, 3]})

        with patch.object(self.adapter.logger, "info") as mock_log:
            result = self.adapter._handle_empty_data("600000", "daily", fallback_data)

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 3
            assert result["test"].tolist() == [1, 2, 3]
            assert mock_log.call_count == 2  # 应该记录两次：空数据和回退数据

    def test_handle_empty_data_without_fallback(self):
        """测试无回退数据的空数据处理"""
        with patch.object(self.adapter.logger, "info") as mock_log:
            result = self.adapter._handle_empty_data("600000", "daily")

            assert isinstance(result, pd.DataFrame)
            assert result.empty
            mock_log.assert_called_once()


class TestValidateSymbol:
    """测试_validate_symbol方法"""

    def setup_method(self):
        """pytest setup方法"""
        self.adapter = MockDataSourceAdapter("symbol_test")

    def test_validate_symbol_valid_formats(self):
        """测试有效股票代码格式"""
        valid_symbols = ["000001", "600000", "300001", "002415"]

        for symbol in valid_symbols:
            result = self.adapter._validate_symbol(symbol)
            assert result == symbol.upper()

    def test_validate_symbol_with_spaces_and_lowercase(self):
        """测试带空格和小写的股票代码"""
        test_cases = [
            ("  000001  ", "000001"),
            ("600000", "600000"),
            ("  300001", "300001"),
        ]

        for input_symbol, expected in test_cases:
            result = self.adapter._validate_symbol(input_symbol)
            assert result == expected

    def test_validate_symbol_invalid_cases(self):
        """测试无效股票代码"""
        # None和空字符串会引发ValueError
        for symbol in [None, ""]:
            with pytest.raises(ValueError):
                self.adapter._validate_symbol(symbol)

        # 数字类型会引发ValueError
        with pytest.raises(ValueError):
            self.adapter._validate_symbol(123)

        # 太短的代码会引发ValueError
        for symbol in ["ABC", "123"]:
            with pytest.raises(ValueError, match="股票代码长度不足"):
                self.adapter._validate_symbol(symbol)

        # 长代码可以处理（会返回大写版本）
        result = self.adapter._validate_symbol("0000010")
        assert result == "0000010"

    def test_validate_symbol_short_length(self):
        """测试过短的股票代码"""
        short_symbols = ["123", "45", "6"]

        for symbol in short_symbols:
            with pytest.raises(ValueError, match="股票代码长度不足"):
                self.adapter._validate_symbol(symbol)


class TestValidateDateRange:
    """测试_validate_date_range方法"""

    def setup_method(self):
        """pytest setup方法"""
        self.adapter = MockDataSourceAdapter("date_test")

    def test_validate_date_range_valid_formats(self):
        """测试有效日期格式"""
        test_cases = [
            ("20240101", "20240131"),
            ("2024-01-01", "2024-01-31"),
            ("20241201", "20241231"),
        ]

        for start_date, end_date in test_cases:
            result = self.adapter._validate_date_range(start_date, end_date)
            assert result == (start_date, end_date)

    def test_validate_date_range_invalid_order(self):
        """测试日期顺序错误"""
        with pytest.raises(ValueError, match="开始日期不能大于结束日期"):
            self.adapter._validate_date_range("20240131", "20240101")

    def test_validate_date_range_invalid_format(self):
        """测试无效日期格式"""
        invalid_cases = [
            ("invalid-date", "20240101"),
            ("20240101", "invalid-date"),
            ("2024-13-01", "20240101"),  # 无效月份
            ("20240101", "2024-02-30"),  # 无效日期
        ]

        for start_date, end_date in invalid_cases:
            with pytest.raises(ValueError, match="无效的日期格式"):
                self.adapter._validate_date_range(start_date, end_date)


class TestQualityStatisticsAndThresholds:
    """测试质量统计和阈值设置方法"""

    def setup_method(self):
        """pytest setup方法"""
        self.adapter = MockDataSourceAdapter("stats_test")

    def test_get_quality_statistics(self):
        """测试获取质量统计信息"""
        # 设置一个假的thresholds属性
        self.adapter.quality_validator.thresholds = {"min_score": 0.8}

        result = self.adapter.get_quality_statistics()

        assert isinstance(result, dict)
        assert result["source_name"] == "stats_test"
        assert result["validator_initialized"] is True
        assert "quality_thresholds" in result

    def test_get_quality_statistics_with_exception(self):
        """测试获取质量统计信息异常处理"""
        # 模拟thresholds属性访问异常
        original_getattribute = object.__getattribute__

        def failing_getattribute(obj, name):
            if name == "thresholds":
                raise Exception("Threshold access failed")
            return original_getattribute(obj, name)

        with patch.object(
            type(self.adapter.quality_validator),
            "__getattribute__",
            side_effect=failing_getattribute,
        ):
            with patch.object(self.adapter.logger, "error") as mock_error:
                result = self.adapter.get_quality_statistics()

                assert isinstance(result, dict)
                assert result["source_name"] == "stats_test"
                assert "error" in result
                mock_error.assert_called_once()

    def test_set_quality_thresholds(self):
        """测试设置质量阈值"""
        thresholds = {"min_completeness": 0.9, "max_missing_ratio": 0.1}

        with patch.object(self.adapter.quality_validator, "set_thresholds") as mock_set:
            with patch.object(self.adapter.logger, "info") as mock_log:
                self.adapter.set_quality_thresholds(**thresholds)

                mock_set.assert_called_once_with(**thresholds)
                mock_log.assert_called_once()


class TestQualityMixin:
    """测试QualityMixin类"""

    def test_quality_mixin_integration(self):
        """测试QualityMixin集成"""
        adapter = MockDataSourceAdapterWithMixin("mixin_test")

        # 测试基本方法存在
        assert hasattr(adapter, "apply_quality_check")
        assert hasattr(adapter, "apply_quality_check_realtime")

        # 测试apply_quality_check方法
        test_df = pd.DataFrame({"test": [1, 2, 3]})
        result = adapter.apply_quality_check(test_df, "000001", "daily")
        assert isinstance(result, pd.DataFrame)

        # 测试apply_quality_check_realtime方法
        test_data = {"price": 10.5}
        result = adapter.apply_quality_check_realtime(test_data, "000001")
        assert isinstance(result, dict)


class TestPerformanceAndEdgeCases:
    """性能测试和边界情况"""

    def setup_method(self):
        """pytest setup方法"""
        self.adapter = MockDataSourceAdapter("performance_test")

    def test_large_dataframe_processing(self):
        """测试大型DataFrame处理"""
        # 创建大型DataFrame
        large_df = pd.DataFrame(
            {
                "date": pd.date_range("2020-01-01", periods=5000),
                "close": np.random.random(5000) * 100,
                "volume": np.random.randint(1000, 10000, 5000),
            }
        )

        with patch.object(
            self.adapter.quality_validator, "validate_stock_data"
        ) as mock_validate:
            mock_validate.return_value = {
                "is_valid": True,
                "quality_score": 0.95,
                "issues": [],
            }

            start_time = time.time()
            result = self.adapter._apply_quality_check(large_df, "000001", "daily")
            execution_time = time.time() - start_time

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 5000
            assert execution_time < 5.0  # 应该在5秒内完成

    def test_realtime_data_processing_performance(self):
        """测试实时数据处理性能"""
        realtime_data = {
            "price": 10.5,
            "volume": 1000,
            "timestamp": datetime.now().isoformat(),
            "bid": 10.4,
            "ask": 10.6,
            "high": 10.8,
            "low": 10.2,
        }

        with patch.object(
            self.adapter.quality_validator, "validate_stock_data"
        ) as mock_validate:
            mock_validate.return_value = {
                "is_valid": True,
                "quality_score": 0.9,
                "issues": [],
            }

            start_time = time.time()
            result = self.adapter._apply_quality_check_realtime(realtime_data, "000001")
            execution_time = time.time() - start_time

            assert isinstance(result, dict)
            assert result["price"] == 10.5
            assert execution_time < 0.1  # 应该在100ms内完成

    def test_none_dataframe_handling(self):
        """测试None DataFrame处理"""
        with patch.object(
            self.adapter.quality_validator, "validate_stock_data"
        ) as mock_validate:
            mock_validate.return_value = {
                "is_valid": True,
                "quality_score": 1.0,
                "issues": [],
            }

            # 测试空DataFrame处理
            empty_df = pd.DataFrame()
            result = self.adapter._apply_quality_check(empty_df, "000001", "daily")

            assert isinstance(result, pd.DataFrame)
            assert result.empty


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])
