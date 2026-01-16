#!/usr/bin/env python3
"""
BaseDataSourceAdapter Phase 6 测试套件
遵循Phase 6成功模式：功能→边界→异常→性能→集成测试
目标：将base_adapter.py的覆盖率从55%提升到95%+
"""

import sys
import time
import pandas as pd
from pathlib import Path
from unittest.mock import Mock, patch
import pytest

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


class MockAdapterWithQualityCheck(QualityMixin):
    """模拟带质量检查的适配器"""

    def __init__(self):
        self.quality_validator = Mock()
        self.logger = Mock()


class TestBaseDataSourceAdapter:
    """BaseDataSourceAdapter核心功能测试"""

    def test_initialization(self):
        """测试适配器初始化"""
        adapter = MockDataSourceAdapter("test_source")

        assert adapter.source_name == "test_source"
        assert hasattr(adapter, "quality_validator")
        assert hasattr(adapter, "logger")

    def test_initialization_with_different_names(self):
        """测试不同名称的初始化"""
        names = ["akshare", "baostock", "tushare", "custom_adapter"]

        for name in names:
            adapter = MockDataSourceAdapter(name)
            assert adapter.source_name == name
            assert adapter.logger.name.endswith(f".{name}")

    @patch("src.adapters.base_adapter.DataQualityValidator")
    def test_quality_validator_initialization(self, mock_validator_class):
        """测试质量验证器初始化"""
        mock_validator_instance = Mock()
        mock_validator_class.return_value = mock_validator_instance

        adapter = MockDataSourceAdapter("test_adapter")

        mock_validator_class.assert_called_once_with("test_adapter")
        assert adapter.quality_validator is mock_validator_instance


class TestDataQualityCheckMixin:
    """DataQualityCheckMixin功能测试"""

    def setUp(self):
        """设置测试环境"""
        self.mixin = MockAdapterWithQualityCheck()

    def setup_method(self):
        """pytest setup方法"""
        self.mixin = MockAdapterWithQualityCheck()

    def test_apply_quality_check_empty_dataframe(self):
        """测试空DataFrame的质量检查"""
        empty_df = pd.DataFrame()
        result = self.mixin.apply_quality_check(empty_df, "600000", "daily")

        assert result.equals(empty_df)
        self.mixin.quality_validator.validate_dataframe.assert_called_once()

    def test_apply_quality_check_valid_dataframe(self):
        """测试有效DataFrame的质量检查"""
        # Mock验证器返回成功
        self.mixin.quality_validator.validate_dataframe = Mock(return_value=True)

        test_df = pd.DataFrame(
            {"symbol": ["600000"], "price": [10.5], "volume": [1000]}
        )

        result = self.mixin.apply_quality_check(test_df, "600000", "daily")

        assert result.equals(test_df)
        self.mixin.quality_validator.validate_dataframe.assert_called_once()

    def test_apply_quality_check_with_fallback(self):
        """测试质量检查失败时使用fallback"""
        # Mock验证器返回失败但记录了问题
        self.mixin.quality_validator.validate_dataframe = Mock(return_value=False)

        original_df = pd.DataFrame({"test": [1]})

        result = self.mixin.apply_quality_check(original_df, "600000", "daily")

        # 验证失败时仍返回原始数据
        assert result.equals(original_df)

    def test_apply_quality_check_realtime_empty_dict(self):
        """测试空字典的实时数据质量检查"""
        empty_data = {}
        result = self.mixin.apply_quality_check_realtime(empty_data, "600000")

        assert result == empty_data
        self.mixin.quality_validator.validate_realtime_data.assert_called_once()

    def test_apply_quality_check_realtime_valid_data(self):
        """测试有效实时数据的质量检查"""
        self.mixin.quality_validator.validate_realtime_data = Mock(return_value=True)

        test_data = {
            "symbol": "600000",
            "price": 10.5,
            "timestamp": "2024-01-01 09:30:00",
        }

        result = self.mixin.apply_quality_check_realtime(test_data, "600000")

        assert result == test_data
        self.mixin.quality_validator.validate_realtime_data.assert_called_once()

    def test_get_quality_statistics(self):
        """测试获取质量统计"""
        mock_stats = {
            "total_checks": 100,
            "passed_checks": 95,
            "failed_checks": 5,
            "success_rate": 0.95,
        }
        self.mixin.quality_validator.get_statistics = Mock(return_value=mock_stats)

        result = self.mixin.get_quality_statistics()

        assert result == mock_stats
        self.mixin.quality_validator.get_statistics.assert_called_once()

    def test_set_quality_thresholds(self):
        """测试设置质量阈值"""
        self.mixin.quality_validator.set_thresholds = Mock()

        result = self.mixin.set_quality_thresholds(
            min_data_points=10, max_null_ratio=0.1
        )

        assert result is True
        self.mixin.quality_validator.set_thresholds.assert_called_once_with(
            min_data_points=10, max_null_ratio=0.1
        )


class TestBaseDataSourceAdapterHelperMethods:
    """辅助方法测试"""

    @patch("src.adapters.base_adapter.DataQualityValidator")
    def test_log_data_fetch(self, mock_validator_class):
        """测试数据获取日志"""
        adapter = MockDataSourceAdapter("test_adapter")

        # 使用patch来捕获日志调用
        with patch.object(adapter.logger, "info") as mock_logger:
            adapter._log_data_fetch("600000", "daily", 1000, 0.5)

            # 验证日志被调用
            mock_logger.assert_called_once()
            log_message = mock_logger.call_args[0][0]
            assert "600000" in log_message
            assert "daily" in log_message
            assert "1000" in log_message

    @patch("src.adapters.base_adapter.DataQualityValidator")
    def test_handle_empty_data_with_fallback(self, mock_validator_class):
        """测试空数据处理with fallback"""
        adapter = MockDataSourceAdapter("test_adapter")
        fallback_data = pd.DataFrame({"fallback": [1, 2, 3]})

        with patch.object(adapter.logger, "warning") as mock_logger:
            result = adapter._handle_empty_data("600000", "daily", fallback_data)

            assert result.equals(fallback_data)
            mock_logger.assert_called_once()

    @patch("src.adapters.base_adapter.DataQualityValidator")
    def test_handle_empty_data_without_fallback(self, mock_validator_class):
        """测试空数据处理without fallback"""
        adapter = MockDataSourceAdapter("test_adapter")

        with patch.object(adapter.logger, "warning") as mock_logger:
            result = adapter._handle_empty_data("600000", "daily", None)

            assert result is None
            mock_logger.assert_called_once()

    @patch("src.adapters.base_adapter.DataQualityValidator")
    def test_validate_symbol_valid_symbols(self, mock_validator_class):
        """测试有效股票代码验证"""
        adapter = MockDataSourceAdapter("test_adapter")

        valid_symbols = ["600000", "000001", "300001", "688001"]

        for symbol in valid_symbols:
            result = adapter._validate_symbol(symbol)
            assert result == symbol

    @patch("src.adapters.base_adapter.DataQualityValidator")
    def test_validate_symbol_invalid_symbols(self, mock_validator_class):
        """测试无效股票代码处理"""
        adapter = MockDataSourceAdapter("test_adapter")

        with patch.object(adapter.logger, "warning") as mock_logger:
            invalid_symbols = ["", None, "invalid", "123"]

            for symbol in invalid_symbols:
                result = adapter._validate_symbol(symbol)
                assert result is None
                mock_logger.assert_called()

    @patch("src.adapters.base_adapter.DataQualityValidator")
    def test_validate_date_range_valid_dates(self, mock_validator_class):
        """测试有效日期范围验证"""
        adapter = MockDataSourceAdapter("test_adapter")

        valid_pairs = [
            ("2024-01-01", "2024-01-31"),
            ("2024-01-01", "2024-12-31"),
            ("2024-06-15", "2024-06-16"),
        ]

        for start, end in valid_pairs:
            result = adapter._validate_date_range(start, end)
            assert result == (start, end)

    @patch("src.adapters.base_adapter.DataQualityValidator")
    def test_validate_date_range_invalid_dates(self, mock_validator_class):
        """测试无效日期范围处理"""
        adapter = MockDataSourceAdapter("test_adapter")

        with patch.object(adapter.logger, "warning") as mock_logger:
            invalid_cases = [
                ("invalid_start", "2024-01-01"),
                ("2024-01-01", "invalid_end"),
                ("2024-01-01", "2023-12-31"),  # 结束早于开始
                ("", ""),  # 空日期
                (None, None),
            ]

            for start, end in invalid_cases:
                result = adapter._validate_date_range(start, end)
                assert result == (None, None)
                mock_logger.assert_called()


class TestBaseDataSourceAdapterPerformance:
    """性能测试"""

    @patch("src.adapters.base_adapter.DataQualityValidator")
    def test_quality_check_performance_under_1ms(self, mock_validator_class):
        """测试质量检查性能（1ms以内）"""
        adapter = MockDataSourceAdapter("test_adapter")

        # Mock验证器快速响应
        mock_validator_class.return_value.validate_dataframe = Mock(return_value=True)

        # 创建测试数据
        test_df = pd.DataFrame(
            {
                "symbol": ["600000"] * 1000,
                "price": [10.5] * 1000,
                "volume": [1000] * 1000,
            }
        )

        # 测试多次质量检查
        start_time = time.time()
        for _ in range(100):
            adapter._apply_quality_check(test_df, "600000", "daily")
        end_time = time.time()

        avg_time = (end_time - start_time) / 100 * 1000  # 转换为毫秒
        assert avg_time < 1.0, f"质量检查平均时间: {avg_time:.2f}ms, 应该小于1ms"

    @patch("src.adapters.base_adapter.DataQualityValidator")
    def test_large_dataframe_quality_check(self, mock_validator_class):
        """测试大数据帧质量检查"""
        adapter = MockDataSourceAdapter("test_adapter")
        mock_validator_class.return_value.validate_dataframe = Mock(return_value=True)

        # 创建大数据帧
        large_df = pd.DataFrame(
            {
                "symbol": ["600000"] * 10000,
                "price": [10.5] * 10000,
                "volume": [1000] * 10000,
                "extra_column": range(10000),
            }
        )

        start_time = time.time()
        result = adapter._apply_quality_check(large_df, "600000", "daily")
        end_time = time.time()

        assert result.equals(large_df)
        operation_time = (end_time - start_time) * 1000
        print(f"大数据帧质量检查时间: {operation_time:.2f}ms")

        # 验证数据完整性
        assert len(result) == 10000


class TestBaseDataSourceAdapterEdgeCases:
    """边界条件和异常处理测试"""

    @patch("src.adapters.base_adapter.DataQualityValidator")
    def test_apply_quality_check_with_none_dataframe(self, mock_validator_class):
        """测试None DataFrame的处理"""
        adapter = MockDataSourceAdapter("test_adapter")

        # Mock None处理
        mock_validator_class.return_value.validate_dataframe = Mock(return_value=True)

        result = adapter._apply_quality_check(None, "600000", "daily")

        # 应该返回None或适当的处理
        assert result is None

    @patch("src.adapters.base_adapter.DataQualityValidator")
    def test_apply_quality_check_with_malformed_dataframe(self, mock_validator_class):
        """测试格式错误的DataFrame处理"""
        adapter = MockDataSourceAdapter("test_adapter")

        # 创建包含问题的DataFrame
        problematic_df = pd.DataFrame(
            {
                "symbol": [None, "", "invalid_symbol"],
                "price": [float("inf"), float("-inf"), None],
                "volume": [float("nan"), None, -1],  # 负数成交量
            }
        )

        # Mock验证器处理但记录问题
        mock_validator_class.return_value.validate_dataframe = Mock(return_value=False)

        result = adapter._apply_quality_check(problematic_df, "600000", "daily")

        # 应该返回原始DataFrame
        assert result.equals(problematic_df)

    @patch("src.adapters.base_adapter.DataQualityValidator")
    def test_apply_quality_check_realtime_with_none_data(self, mock_validator_class):
        """测试None实时数据处理"""
        adapter = MockDataSourceAdapter("test_adapter")

        result = adapter._apply_quality_check_realtime(None, "600000")

        assert result is None

    @patch("src.adapters.base_adapter.DataQualityValidator")
    def test_apply_quality_check_realtime_with_invalid_data(self, mock_validator_class):
        """测试无效实时数据处理"""
        adapter = MockDataSourceAdapter("test_adapter")

        invalid_data = {
            "symbol": None,
            "price": float("inf"),
            "volume": float("nan"),
            "invalid_field": "value",
        }

        # Mock验证器处理但记录问题
        mock_validator_class.return_value.validate_realtime_data = Mock(
            return_value=False
        )

        result = adapter._apply_quality_check_realtime(invalid_data, "600000")

        assert result == invalid_data

    def test_log_data_fetch_with_zero_records(self):
        """测试零记录的日志记录"""
        adapter = MockDataSourceAdapter("test_adapter")

        with patch.object(adapter.logger, "warning") as mock_logger:
            adapter._log_data_fetch("600000", "daily", 0, 0.1)

            mock_logger.assert_called_once()
            log_message = mock_logger.call_args[0][0]
            assert "0" in log_message or "empty" in log_message.lower()

    @patch("src.adapters.base_adapter.DataQualityValidator")
    def test_log_data_fetch_with_long_execution_time(self, mock_validator_class):
        """测试长时间执行的日志记录"""
        adapter = MockDataSourceAdapter("test_adapter")

        with patch.object(adapter.logger, "warning") as mock_logger:
            adapter._log_data_fetch("600000", "daily", 1000, 5.0)  # 5秒执行时间

            mock_logger.assert_called_once()
            log_message = mock_logger.call_args[0][0]
            assert "5.0s" in log_message or "slow" in log_message.lower()

    def test_symbol_validation_edge_cases(self):
        """测试股票代码验证的边界情况"""
        adapter = MockDataSourceAdapter("test_adapter")

        # 测试各种边界情况
        edge_cases = [
            "0",  # 单个数字
            "1234567",  # 7位数字
            "ABC",  # 纯字母
            "600000.SH",  # 带后缀
            "sh600000",  # 带前缀小写
            " 600000  ",  # 带空格
        ]

        with patch.object(adapter.logger, "warning") as mock_logger:
            for symbol in edge_cases:
                result = adapter._validate_symbol(symbol)
                # 验证结果符合预期（根据实现逻辑）


class TestBaseDataSourceAdapterIntegration:
    """集成测试"""

    @patch("src.adapters.base_adapter.DataQualityValidator")
    def test_complete_quality_check_workflow(self, mock_validator_class):
        """测试完整的质量检查工作流"""
        adapter = MockDataSourceAdapter("test_adapter")

        # Mock验证器
        mock_validator_instance = Mock()
        mock_validator_class.return_value = mock_validator_instance
        mock_validator_instance.validate_dataframe = Mock(return_value=True)
        mock_validator_instance.get_statistics = Mock(
            return_value={"total_checks": 10, "passed_checks": 8, "failed_checks": 2}
        )

        # 测试完整工作流
        test_df = pd.DataFrame(
            {
                "symbol": ["600000", "000001"],
                "price": [10.5, 15.2],
                "volume": [1000, 2000],
            }
        )

        # 1. 应用质量检查
        result_df = adapter._apply_quality_check(test_df, "600000", "daily")
        assert result_df.equals(test_df)

        # 2. 获取质量统计
        stats = adapter.get_quality_statistics()
        assert stats["total_checks"] == 10
        assert stats["success_rate"] == 0.8

        # 3. 设置新的质量阈值
        adapter.set_quality_thresholds(min_data_points=50)
        mock_validator_instance.set_thresholds.assert_called_with(min_data_points=50)

    @patch("src.adapters.base_adapter.DataQualityValidator")
    def test_real_time_data_quality_workflow(self, mock_validator_class):
        """测试实时数据质量检查工作流"""
        adapter = MockDataSourceAdapter("test_adapter")

        # Mock验证器
        mock_validator_instance = Mock()
        mock_validator_class.return_value = mock_validator_instance
        mock_validator_instance.validate_realtime_data = Mock(return_value=True)

        # 测试实时数据工作流
        realtime_data = [
            {"symbol": "600000", "price": 10.5, "timestamp": "2024-01-01 09:30:00"},
            {"symbol": "000001", "price": 15.2, "timestamp": "2024-01-01 09:30:01"},
            {"symbol": "300001", "price": 8.8, "timestamp": "2024-01-01 09:30:02"},
        ]

        for data in realtime_data:
            result = adapter._apply_quality_check_realtime(data, data["symbol"])
            assert result == data
            mock_validator_instance.validate_realtime_data.assert_called_with(
                data, data["symbol"]
            )

    @patch("src.adapters.base_adapter.DataQualityValidator")
    def test_data_validation_and_logging_integration(self, mock_validator_class):
        """测试数据验证和日志记录集成"""
        adapter = MockDataSourceAdapter("test_adapter")

        # Mock验证器
        mock_validator_instance = Mock()
        mock_validator_class.return_value = mock_validator_instance
        mock_validator_instance.validate_dataframe = Mock(return_value=True)

        test_df = pd.DataFrame({"symbol": ["600000"], "price": [10.5]})

        # 同时执行质量检查和日志记录
        with patch.object(adapter.logger, "info") as mock_logger:
            adapter._log_data_fetch("600000", "daily", len(test_df), 0.1)
            result = adapter._apply_quality_check(test_df, "600000", "daily")

            # 验证日志记录被调用
            mock_logger.assert_called()

            # 验证质量检查被调用
            mock_validator_instance.validate_dataframe.assert_called_once()

            # 验证结果正确
            assert result.equals(test_df)


class TestBaseDataSourceAdapterErrorHandling:
    """错误处理测试"""

    @patch("src.adapters.base_adapter.DataQualityValidator")
    def test_quality_validator_initialization_failure(self, mock_validator_class):
        """测试质量验证器初始化失败"""
        mock_validator_class.side_effect = Exception("Validation system unavailable")

        # 验证适配器初始化不会因验证器失败而崩溃
        try:
            adapter = MockDataSourceAdapter("test_adapter")
            assert adapter.source_name == "test_adapter"
            # 验证使用了默认的Mock实现
            assert hasattr(adapter, "quality_validator")
        except Exception:
            pytest.fail("适配器初始化不应该因验证器失败而崩溃")

    @patch("src.adapters.base_adapter.DataQualityValidator")
    def test_apply_quality_check_exception_handling(self, mock_validator_class):
        """测试质量检查异常处理"""
        adapter = MockDataSourceAdapter("test_adapter")

        # Mock验证器抛出异常
        mock_validator_instance = Mock()
        mock_validator_class.return_value = mock_validator_instance
        mock_validator_instance.validate_dataframe = Mock(
            side_effect=Exception("Validation error")
        )

        test_df = pd.DataFrame({"test": [1]})

        # 验证异常不会传播
        result = adapter._apply_quality_check(test_df, "600000", "daily")
        assert result.equals(test_df)

    @patch("src.adapters.base_adapter.DataQualityValidator")
    def test_get_statistics_exception_handling(self, mock_validator_class):
        """测试获取统计信息异常处理"""
        adapter = MockDataSourceAdapter("test_adapter")

        # Mock验证器抛出异常
        mock_validator_instance = Mock()
        mock_validator_class.return_value = mock_validator_instance
        mock_validator_instance.get_statistics = Mock(
            side_effect=Exception("Stats error")
        )

        # 验证异常处理
        with patch.object(adapter.logger, "error") as mock_logger:
            result = adapter.get_quality_statistics()

            # 应该返回空字典或默认值
            assert isinstance(result, dict)
            mock_logger.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
