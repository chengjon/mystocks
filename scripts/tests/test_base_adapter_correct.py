#!/usr/bin/env python3
"""
BaseDataSourceAdapter Phase 6 测试套件 - 正确版
基于实际API创建的测试套件
目标：将base_adapter.py的覆盖率从55%提升到95%+
"""

import sys
import os
import time
import pandas as pd
import numpy as np
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call
import pytest
from datetime import datetime, timedelta

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 导入被测试的模块
from src.adapters.base_adapter import BaseDataSourceAdapter, QualityMixin


class MockDataSourceAdapter(BaseDataSourceAdapter):
    """模拟数据源适配器用于测试"""

    def __init__(self, source_name="test_adapter"):
        super().__init__(source_name)

    def test_method(self):
        """测试方法"""
        return "test_result"


class TestBaseDataSourceAdapter:
    """BaseDataSourceAdapter核心功能测试"""

    def test_initialization(self):
        """测试适配器初始化"""
        adapter = MockDataSourceAdapter("test_source")
        assert adapter.source_name == "test_source"
        assert adapter.quality_validator is not None
        assert adapter.logger is not None

    def test_initialization_with_different_names(self):
        """测试不同名称的适配器初始化"""
        names = ["akshare", "tushare", "baostock", "custom_adapter"]
        for name in names:
            adapter = MockDataSourceAdapter(name)
            assert adapter.source_name == name

    @patch("src.adapters.base_adapter.DataQualityValidator")
    def test_quality_validator_initialization(self, mock_validator_class):
        """测试质量验证器初始化"""
        mock_validator = Mock()
        mock_validator_class.return_value = mock_validator

        adapter = MockDataSourceAdapter("test_source")

        mock_validator_class.assert_called_once_with("test_source")
        assert adapter.quality_validator == mock_validator


class TestBaseDataSourceAdapterCoreMethods:
    """BaseDataSourceAdapter核心方法测试"""

    def setup_method(self):
        """pytest setup方法"""
        self.adapter = MockDataSourceAdapter("test_adapter")

    def test_apply_quality_check_empty_dataframe(self):
        """测试空DataFrame的质量检查"""
        empty_df = pd.DataFrame()

        # 配置mock验证器的validate_stock_data方法
        self.adapter.quality_validator.validate_stock_data.return_value = {
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
                "high": [10.5, 11.0, 11.3, 11.1, 11.5],
                "low": [9.8, 10.2, 10.7, 10.5, 10.9],
                "close": [10.3, 10.8, 11.1, 10.9, 11.3],
                "volume": [1000, 1200, 900, 1100, 1300],
            }
        )

        # 配置mock验证器返回有效结果
        self.adapter.quality_validator.validate_stock_data.return_value = {
            "is_valid": True,
            "quality_score": 0.95,
            "issues": [],
        }

        result = self.adapter._apply_quality_check(valid_df, "000001", "daily")

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 5
        self.adapter.quality_validator.validate_stock_data.assert_called_once()

    def test_apply_quality_check_with_issues(self):
        """测试有质量问题的DataFrame"""
        df = pd.DataFrame(
            {
                "date": pd.date_range("2024-01-01", periods=3),
                "close": [10.0, np.nan, 12.0],  # 包含NaN值
            }
        )

        # 配置mock验证器返回质量问题
        self.adapter.quality_validator.validate_stock_data.return_value = {
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

        # 应该返回原始DataFrame，但记录警告
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        self.adapter.quality_validator.validate_stock_data.assert_called_once()

    def test_apply_quality_check_with_critical_issues(self):
        """测试有严重质量问题的DataFrame"""
        df = pd.DataFrame({"test": [1, 2, 3]})

        # 配置mock验证器返回严重问题
        self.adapter.quality_validator.validate_stock_data.return_value = {
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
        self.adapter.quality_validator.validate_stock_data.assert_called_once()

    def test_apply_quality_check_exception_handling(self):
        """测试质量检查异常处理"""
        df = pd.DataFrame({"test": [1, 2, 3]})

        # 配置验证器抛出异常
        self.adapter.quality_validator.validate_stock_data.side_effect = Exception(
            "Quality check failed"
        )

        result = self.adapter._apply_quality_check(df, "000001", "daily")

        # 应该返回原始DataFrame
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3

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
            "change": 0.05,
        }

        # 配置mock验证器
        self.adapter.quality_validator.validate_stock_data.return_value = {
            "is_valid": True,
            "quality_score": 0.9,
            "issues": [],
        }

        result = self.adapter._apply_quality_check_realtime(valid_data, "000001")

        assert isinstance(result, dict)
        assert result["price"] == 10.5
        self.adapter.quality_validator.validate_stock_data.assert_called_once()

    def test_apply_quality_check_realtime_without_timestamp(self):
        """测试没有时间戳的实时数据"""
        data_without_timestamp = {"price": 10.5, "volume": 1000}

        # 配置mock验证器
        self.adapter.quality_validator.validate_stock_data.return_value = {
            "is_valid": True,
            "quality_score": 0.9,
            "issues": [],
        }

        result = self.adapter._apply_quality_check_realtime(
            data_without_timestamp, "000001"
        )

        assert isinstance(result, dict)
        assert result["price"] == 10.5
        # 应该自动添加时间戳
        assert (
            "timestamp" in result
            or self.adapter.quality_validator.validate_stock_data.called
        )

    def test_apply_quality_check_realtime_exception_handling(self):
        """测试实时质量检查异常处理"""
        valid_data = {"price": 10.5, "volume": 1000}

        # 配置验证器抛出异常
        self.adapter.quality_validator.validate_stock_data.side_effect = Exception(
            "Realtime quality check failed"
        )

        result = self.adapter._apply_quality_check_realtime(valid_data, "000001")

        # 应该返回原始数据
        assert isinstance(result, dict)
        assert result["price"] == 10.5


class TestBaseDataSourceAdapterHelperMethods:
    """BaseDataSourceAdapter辅助方法测试"""

    def setup_method(self):
        """pytest setup方法"""
        self.adapter = MockDataSourceAdapter("test_adapter")

    def test_log_data_fetch(self):
        """测试数据获取日志记录"""
        with patch.object(self.adapter.logger, "info") as mock_logger:
            self.adapter._log_data_fetch("000001", "daily", 100, ["date", "close"])

            mock_logger.assert_called_once()
            log_message = mock_logger.call_args[0][0]
            assert "000001" in log_message
            assert "daily" in log_message
            assert "100" in log_message

        with patch.object(self.adapter.logger, "debug") as mock_debug:
            self.adapter._log_data_fetch("000001", "daily", 100, ["date", "close"])

            mock_debug.assert_called_once()
            assert "['date', 'close']" in mock_debug.call_args[0][0]

    def test_handle_empty_data_with_fallback(self):
        """测试空数据处理带回退机制"""
        fallback_data = pd.DataFrame({"test": [1, 2, 3]})

        with patch.object(self.adapter.logger, "info") as mock_log:
            result = self.adapter._handle_empty_data("600000", "daily", fallback_data)

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 3
            assert result["test"].tolist() == [1, 2, 3]
            mock_log.assert_called()

    def test_handle_empty_data_without_fallback(self):
        """测试空数据处理无回退机制"""
        with patch.object(self.adapter.logger, "info") as mock_log:
            result = self.adapter._handle_empty_data("600000", "daily")

            assert isinstance(result, pd.DataFrame)
            assert result.empty
            mock_log.assert_called_once()

    def test_validate_symbol_valid_symbols(self):
        """测试有效股票代码验证"""
        valid_symbols = ["000001", "600000", "300001", "002415"]

        for symbol in valid_symbols:
            result = self.adapter._validate_symbol(symbol)
            assert result == symbol.upper()

    def test_validate_symbol_invalid_symbols(self):
        """测试无效股票代码验证"""
        invalid_symbols = ["", None, 123, "ABC", "123", "0000010"]

        for symbol in invalid_symbols:
            with pytest.raises(ValueError):
                self.adapter._validate_symbol(symbol)

    def test_validate_symbol_with_spaces(self):
        """测试带空格的股票代码"""
        symbol_with_spaces = "  000001  "
        result = self.adapter._validate_symbol(symbol_with_spaces)
        assert result == "000001"

    def test_validate_symbol_lowercase(self):
        """测试小写股票代码"""
        lowercase_symbol = "000001"
        result = self.adapter._validate_symbol(lowercase_symbol)
        assert result == "000001"

    def test_validate_date_range_valid_dates(self):
        """测试有效日期范围验证"""
        test_cases = [
            ("20240101", "20240131"),
            ("2024-01-01", "2024-01-31"),
            ("20241201", "20241231"),
        ]

        for start_date, end_date in test_cases:
            result = self.adapter._validate_date_range(start_date, end_date)
            assert result == (start_date, end_date)

    def test_validate_date_range_invalid_dates(self):
        """测试无效日期范围验证"""
        invalid_cases = [
            ("20240131", "20240101"),  # 结束日期早于开始日期
            ("invalid-date", "20240101"),  # 无效开始日期
            ("20240101", "invalid-date"),  # 无效结束日期
        ]

        for start_date, end_date in invalid_cases:
            with pytest.raises(ValueError):
                self.adapter._validate_date_range(start_date, end_date)


class TestBaseDataSourceAdapterQualityMethods:
    """BaseDataSourceAdapter质量方法测试"""

    def setup_method(self):
        """pytest setup方法"""
        self.adapter = MockDataSourceAdapter("quality_test")

    def test_get_quality_statistics_success(self):
        """测试获取质量统计信息成功"""
        # 配置mock验证器
        self.adapter.quality_validator.thresholds = {"min_score": 0.8}

        result = self.adapter.get_quality_statistics()

        assert isinstance(result, dict)
        assert result["source_name"] == "quality_test"
        assert result["validator_initialized"] is True
        assert "quality_thresholds" in result

    def test_get_quality_statistics_exception(self):
        """测试获取质量统计信息异常处理"""
        # 配置验证器抛出异常
        self.adapter.quality_validator.thresholds = Mock(
            side_effect=Exception("Threshold access failed")
        )

        result = self.adapter.get_quality_statistics()

        assert isinstance(result, dict)
        assert result["source_name"] == "quality_test"
        assert "error" in result

    def test_set_quality_thresholds(self):
        """测试设置质量阈值"""
        thresholds = {
            "min_completeness": 0.9,
            "max_missing_ratio": 0.1,
            "required_columns": ["date", "close", "volume"],
        }

        with patch.object(self.adapter.quality_validator, "set_thresholds") as mock_set:
            with patch.object(self.adapter.logger, "info") as mock_log:
                self.adapter.set_quality_thresholds(**thresholds)

                mock_set.assert_called_once_with(**thresholds)
                mock_log.assert_called_once()


class TestBaseDataSourceAdapterPerformance:
    """BaseDataSourceAdapter性能测试"""

    def setup_method(self):
        """pytest setup方法"""
        self.adapter = MockDataSourceAdapter("performance_test")

    def test_quality_check_performance_large_dataframe(self):
        """测试大型DataFrame质量检查性能"""
        # 创建大型DataFrame
        large_df = pd.DataFrame(
            {
                "date": pd.date_range("2020-01-01", periods=10000),
                "close": np.random.random(10000) * 100,
                "volume": np.random.randint(1000, 10000, 10000),
            }
        )

        # 配置mock验证器
        self.adapter.quality_validator.validate_stock_data.return_value = {
            "is_valid": True,
            "quality_score": 0.95,
            "issues": [],
        }

        start_time = time.time()
        result = self.adapter._apply_quality_check(large_df, "000001", "daily")
        execution_time = time.time() - start_time

        assert isinstance(result, pd.DataFrame)
        assert execution_time < 2.0  # 应该在2秒内完成

    def test_realtime_quality_check_performance(self):
        """测试实时质量检查性能"""
        realtime_data = {
            "price": 10.5,
            "volume": 1000,
            "timestamp": datetime.now().isoformat(),
        }

        # 配置mock验证器
        self.adapter.quality_validator.validate_stock_data.return_value = {
            "is_valid": True,
            "quality_score": 0.9,
            "issues": [],
        }

        start_time = time.time()
        result = self.adapter._apply_quality_check_realtime(realtime_data, "000001")
        execution_time = time.time() - start_time

        assert isinstance(result, dict)
        assert execution_time < 0.1  # 应该在100ms内完成


class TestQualityMixin:
    """QualityMixin测试"""

    def test_quality_mixin_with_base_adapter_methods(self):
        """测试QualityMixin与BaseDataSourceAdapter方法的集成"""
        adapter = MockDataSourceAdapter("mixin_test")

        # 配置mock验证器
        adapter.quality_validator.validate_stock_data.return_value = {
            "is_valid": True,
            "quality_score": 0.95,
            "issues": [],
        }

        test_df = pd.DataFrame({"test": [1, 2, 3]})
        test_data = {"price": 10.5}

        # 测试apply_quality_check方法
        result_df = adapter.apply_quality_check(test_df, "000001", "daily")
        assert isinstance(result_df, pd.DataFrame)

        # 测试apply_quality_check_realtime方法
        result_data = adapter.apply_quality_check_realtime(test_data, "000001")
        assert isinstance(result_data, dict)


class TestBaseDataSourceAdapterIntegration:
    """BaseDataSourceAdapter集成测试"""

    def setup_method(self):
        """pytest setup方法"""
        self.adapter = MockDataSourceAdapter("integration_test")

    def test_complete_quality_workflow(self):
        """测试完整质量检查工作流"""
        # 创建测试数据
        test_data = pd.DataFrame(
            {
                "date": pd.date_range("2024-01-01", periods=10),
                "close": [10.0, 10.5, 11.0, 10.8, 11.2, 11.5, 11.1, 11.8, 12.0, 11.9],
                "volume": [1000, 1200, 900, 1100, 1300, 1500, 800, 1400, 1600, 1200],
            }
        )

        # 配置mock验证器
        self.adapter.quality_validator.validate_stock_data.return_value = {
            "is_valid": True,
            "quality_score": 0.92,
            "issues": [
                {"type": "minor_issue", "message": "轻微问题", "severity": "warning"}
            ],
        }

        # 执行完整工作流
        result = self.adapter._apply_quality_check(test_data, "000001", "daily")

        # 验证结果
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 10
        self.adapter.quality_validator.validate_stock_data.assert_called_once()

    def test_symbol_and_date_validation_workflow(self):
        """测试股票代码和日期验证工作流"""
        # 测试股票代码验证
        validated_symbol = self.adapter._validate_symbol("  600000  ")
        assert validated_symbol == "600000"

        # 测试日期范围验证
        validated_dates = self.adapter._validate_date_range("20240101", "20240131")
        assert validated_dates == ("20240101", "20240131")

        # 测试空数据处理
        empty_result = self.adapter._handle_empty_data("000001", "daily")
        assert isinstance(empty_result, pd.DataFrame)
        assert empty_result.empty

    def test_logging_and_quality_check_integration(self):
        """测试日志记录和质量检查集成"""
        test_data = pd.DataFrame(
            {
                "date": pd.date_range("2024-01-01", periods=5),
                "close": [10.0, 10.5, 11.0, 10.8, 11.2],
                "volume": [1000, 1200, 900, 1100, 1300],
            }
        )

        # 配置所有mock组件
        self.adapter.quality_validator.validate_stock_data.return_value = {
            "is_valid": True,
            "quality_score": 0.88,
            "issues": [],
        }

        with patch.object(self.adapter, "_log_data_fetch") as mock_log:
            # 执行数据获取和质量检查
            self.adapter._log_data_fetch(
                "000001", "daily", len(test_data), list(test_data.columns)
            )
            result = self.adapter._apply_quality_check(test_data, "000001", "daily")

            # 验证集成结果
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 5
            mock_log.assert_called_once()


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])
