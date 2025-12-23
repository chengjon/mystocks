#!/usr/bin/env python3
"""
数据质量验证器模块单元测试 - 源代码覆盖率测试

测试MyStocks系统中数据质量验证器的完整功能，包括质量检查、异常检测和监控集成
"""

import pytest
import sys
import os
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.core.data_quality_validator import (
    DataQualityValidator,
    create_validator,
    validate_dataframe,
)


class TestDataQualityValidator:
    """测试数据质量验证器类"""

    @pytest.fixture
    def sample_daily_data(self):
        """创建示例日线数据"""
        return pd.DataFrame(
            {
                "date": pd.date_range("2025-01-01", periods=5, freq="D"),
                "open": [10.0, 10.5, 10.3, 10.8, 11.0],
                "high": [10.5, 10.8, 10.6, 11.0, 11.2],
                "low": [9.8, 10.2, 10.1, 10.5, 10.8],
                "close": [10.2, 10.6, 10.4, 10.9, 11.1],
                "volume": [1000, 1200, 800, 1500, 2000],
            }
        )

    @pytest.fixture
    def sample_realtime_data(self):
        """创建示例实时数据"""
        return pd.DataFrame(
            {
                "code": ["000001", "000002", "600000", "600036"],
                "name": ["平安银行", "万科A", "浦发银行", "招商银行"],
                "price": [10.5, 12.3, 8.9, 15.6],
                "volume": [5000, 3000, 8000, 4000],
                "timestamp": pd.date_range(
                    "2025-01-01 09:30:00", periods=4, freq="1min"
                ),
            }
        )

    @pytest.fixture
    def empty_data(self):
        """创建空数据"""
        return pd.DataFrame()

    @pytest.fixture
    def data_with_issues(self):
        """创建有问题的数据"""
        return pd.DataFrame(
            {
                "date": pd.date_range("2025-01-01", periods=5, freq="D"),
                "open": [10.0, -5.0, 10.3, 10.8, 11.0],  # 负价格
                "high": [10.2, 9.8, 10.6, 11.0, 11.2],  # 最高价低于最低价
                "low": [10.5, 12.0, 10.1, 10.5, 10.8],
                "close": [10.2, 10.6, 10.4, 10.9, 11.1],
                "volume": [1000, -200, 800, 1500, 2000],  # 负成交量
            }
        )

    @patch("src.core.data_quality_validator.get_quality_monitor")
    def test_initialization_with_default_monitor(self, mock_get_quality_monitor):
        """测试初始化 - 使用默认监控器"""
        mock_monitor = Mock()
        mock_get_quality_monitor.return_value = mock_monitor

        validator = DataQualityValidator("test_source")

        assert validator.source_name == "test_source"
        assert validator.quality_monitor is mock_monitor
        mock_get_quality_monitor.assert_called_once()

        # 验证默认阈值
        assert validator.thresholds["missing_rate_threshold"] == 5.0
        assert validator.thresholds["invalid_rate_threshold"] == 1.0
        assert validator.thresholds["duplicate_rate_threshold"] == 0.5
        assert validator.thresholds["outlier_rate_threshold"] == 2.0
        assert validator.thresholds["freshness_threshold_seconds"] == 300

    @patch("src.core.data_quality_validator.get_quality_monitor")
    def test_initialization_with_custom_monitor(self, mock_get_quality_monitor):
        """测试初始化 - 使用自定义监控器"""
        custom_monitor = Mock()
        validator = DataQualityValidator("test_source", quality_monitor=custom_monitor)

        assert validator.source_name == "test_source"
        assert validator.quality_monitor is custom_monitor
        mock_get_quality_monitor.assert_not_called()

    def test_validate_stock_data_empty_data(self, empty_data):
        """测试验证股票数据 - 空数据"""
        validator = DataQualityValidator("test_source")

        result = validator.validate_stock_data(empty_data, "600000", "daily")

        assert result["is_valid"] is False
        assert result["quality_score"] == 0.0
        assert len(result["issues"]) == 1
        assert result["issues"][0]["type"] == "empty_data"
        assert result["statistics"] == {}

    def test_validate_stock_data_perfect_data(self, sample_daily_data):
        """测试验证股票数据 - 完美数据"""
        validator = DataQualityValidator("test_source")

        result = validator.validate_stock_data(sample_daily_data, "600000", "daily")

        assert result["is_valid"] is True
        assert result["quality_score"] == 100.0
        assert len(result["issues"]) == 0
        assert result["statistics"]["total_records"] == 5

    def test_validate_stock_data_with_issues(self, data_with_issues):
        """测试验证股票数据 - 有问题的数据"""
        validator = DataQualityValidator("test_source")

        result = validator.validate_stock_data(data_with_issues, "600000", "daily")

        assert result["is_valid"] is False  # 负价格导致严重问题
        assert result["quality_score"] < 70.0
        assert len(result["issues"]) > 0

        # 检查是否包含负价格问题
        invalid_price_issues = [
            i for i in result["issues"] if i["type"] == "invalid_price"
        ]
        assert len(invalid_price_issues) > 0

        # 检查是否包含价格逻辑错误
        price_logic_issues = [
            i for i in result["issues"] if i["type"] == "price_logic_error"
        ]
        assert len(price_logic_issues) > 0

    @patch("src.core.data_quality_validator.get_quality_monitor")
    def test_validate_stock_data_realtime_data(
        self, mock_get_quality_monitor, sample_realtime_data
    ):
        """测试验证股票数据 - 实时数据"""
        mock_monitor = Mock()
        mock_get_quality_monitor.return_value = mock_monitor

        validator = DataQualityValidator("test_source")

        result = validator.validate_stock_data(
            sample_realtime_data, "000001", "realtime"
        )

        assert result["is_valid"] is True
        assert result["quality_score"] == 100.0
        assert result["statistics"]["total_records"] == 4

    def test_get_required_columns_realtime(self):
        """测试获取必需列 - 实时数据"""
        validator = DataQualityValidator("test_source")

        columns = validator._get_required_columns("realtime")
        expected = ["code", "name", "price", "volume", "timestamp"]
        assert columns == expected

    def test_get_required_columns_daily(self):
        """测试获取必需列 - 日线数据"""
        validator = DataQualityValidator("test_source")

        columns = validator._get_required_columns("daily")
        expected = ["date", "open", "high", "low", "close", "volume"]
        assert columns == expected

    def test_get_required_columns_index_daily(self):
        """测试获取必需列 - 指数日线数据"""
        validator = DataQualityValidator("test_source")

        columns = validator._get_required_columns("index_daily")
        expected = ["date", "open", "high", "low", "close", "volume"]
        assert columns == expected

    def test_get_required_columns_default(self):
        """测试获取必需列 - 默认类型"""
        validator = DataQualityValidator("test_source")

        columns = validator._get_required_columns("unknown")
        expected = ["date", "close"]
        assert columns == expected

    def test_check_completeness_no_issues(self, sample_daily_data):
        """测试检查完整性 - 无问题"""
        validator = DataQualityValidator("test_source")

        issues = validator._check_completeness(
            sample_daily_data, ["date", "open", "high", "low", "close", "volume"]
        )

        assert len(issues) == 0

    def test_check_completeness_with_missing_data(self):
        """测试检查完整性 - 有缺失数据"""
        # 创建有缺失值的数据
        data_with_nulls = pd.DataFrame(
            {
                "date": pd.date_range("2025-01-01", periods=5, freq="D"),
                "open": [10.0, None, 10.3, None, 11.0],  # 40%缺失
                "high": [10.5, 10.8, 10.6, 11.0, 11.2],
                "low": [9.8, 10.2, 10.1, 10.5, 10.8],
                "close": [10.2, 10.6, 10.4, 10.9, 11.1],
                "volume": [1000, 1200, 800, 1500, None],  # 20%缺失
            }
        )

        validator = DataQualityValidator("test_source")

        issues = validator._check_completeness(
            data_with_nulls, ["date", "open", "high", "low", "close", "volume"]
        )

        assert len(issues) == 2  # open列40%缺失(严重), volume列20%缺失

        # 检查open列问题
        open_issue = next(i for i in issues if i["column"] == "open")
        assert open_issue["missing_rate"] == 40.0
        assert open_issue["severity"] == "critical"
        assert open_issue["score_penalty"] == 20.0

    def test_check_completeness_critical_threshold(self):
        """测试检查完整性 - 严重阈值"""
        # 创建严重缺失的数据
        data_severe_missing = pd.DataFrame(
            {
                "date": pd.date_range("2025-01-01", periods=5, freq="D"),
                "open": [None, None, None, None, None],  # 100%缺失
                "high": [10.5, 10.8, 10.6, 11.0, 11.2],
            }
        )

        validator = DataQualityValidator("test_source")

        issues = validator._check_completeness(
            data_severe_missing, ["date", "open", "high"]
        )

        assert len(issues) == 1
        open_issue = issues[0]
        assert open_issue["severity"] == "critical"
        assert open_issue["score_penalty"] == 20.0

    def test_check_accuracy_no_issues(self, sample_daily_data):
        """测试检查准确性 - 无问题"""
        validator = DataQualityValidator("test_source")

        issues = validator._check_accuracy(sample_daily_data, "600000")

        assert len(issues) == 0

    def test_check_accuracy_negative_prices(self, data_with_issues):
        """测试检查准确性 - 负价格"""
        validator = DataQualityValidator("test_source")

        issues = validator._check_accuracy(data_with_issues, "600000")

        # 检查负价格
        negative_price_issues = [i for i in issues if i["type"] == "invalid_price"]
        assert len(negative_price_issues) == 2  # open和volume列有负值

    def test_check_accuracy_price_logic_error(self, data_with_issues):
        """测试检查准确性 - 价格逻辑错误"""
        validator = DataQualityValidator("test_source")

        issues = validator._check_accuracy(data_with_issues, "600000")

        # 检查价格逻辑错误
        price_logic_issues = [i for i in issues if i["type"] == "price_logic_error"]
        assert len(price_logic_issues) == 1

    def test_check_accuracy_negative_volume(self, data_with_issues):
        """测试检查准确性 - 负成交量"""
        validator = DataQualityValidator("test_source")

        issues = validator._check_accuracy(data_with_issues, "600000")

        # 检查负成交量
        negative_volume_issues = [i for i in issues if i["type"] == "invalid_volume"]
        assert len(negative_volume_issues) == 1

    def test_check_consistency_no_issues(self, sample_daily_data):
        """测试检查一致性 - 无问题"""
        validator = DataQualityValidator("test_source")

        issues = validator._check_consistency(sample_daily_data, "daily")

        assert len(issues) == 0

    def test_check_consistency_invalid_date(self):
        """测试检查一致性 - 无效日期格式"""
        data_invalid_date = pd.DataFrame(
            {
                "date": ["2025-01-01", "invalid-date", "2025-01-03"],
                "close": [10.0, 10.5, 11.0],
            }
        )

        validator = DataQualityValidator("test_source")

        issues = validator._check_consistency(data_invalid_date, "daily")

        assert len(issues) == 1
        assert issues[0]["type"] == "date_format_inconsistent"
        assert issues[0]["severity"] == "warning"

    def test_check_consistency_invalid_timestamp(self):
        """测试检查一致性 - 无效时间戳格式"""
        data_invalid_timestamp = pd.DataFrame(
            {
                "timestamp": [
                    "2025-01-01 09:30:00",
                    "invalid-timestamp",
                    "2025-01-01 09:32:00",
                ],
                "code": ["000001", "000002", "000003"],
                "price": [10.0, 10.5, 11.0],
            }
        )

        validator = DataQualityValidator("test_source")

        issues = validator._check_consistency(data_invalid_timestamp, "realtime")

        assert len(issues) == 1
        assert issues[0]["type"] == "timestamp_format_inconsistent"

    def test_check_duplicates_no_duplicates(self, sample_daily_data):
        """测试检查重复 - 无重复"""
        validator = DataQualityValidator("test_source")

        issues = validator._check_duplicates(sample_daily_data)

        assert len(issues) == 0

    def test_check_duplicates_with_duplicates(self):
        """测试检查重复 - 有重复"""
        # 创建有重复的数据
        data_with_duplicates = sample_daily_data.copy()
        data_with_duplicates = pd.concat(
            [data_with_duplicates, data_with_duplicates.iloc[:2]], ignore_index=True
        )

        validator = DataQualityValidator("test_source")

        issues = validator._check_duplicates(data_with_duplicates)

        assert len(issues) == 1
        assert issues[0]["type"] == "duplicate_rows"
        assert issues[0]["duplicate_count"] == 2
        assert issues[0]["duplicate_rate"] == (2 / 7) * 100  # 7条记录中有2条重复

    def test_check_duplicates_below_threshold(self):
        """测试检查重复 - 低于阈值"""
        # 创建少量重复的数据
        data_few_duplicates = sample_daily_data.copy()
        data_few_duplicates = pd.concat(
            [data_few_duplicates, data_few_duplicates.iloc[:1]], ignore_index=True
        )

        validator = DataQualityValidator("test_source")

        issues = validator._check_duplicates(data_few_duplicates)

        assert len(issues) == 0  # 低于0.5%阈值

    def test_check_outliers_no_outliers(self, sample_daily_data):
        """测试检查异常值 - 无异常值"""
        validator = DataQualityValidator("test_source")

        issues = validator._check_outliers(sample_daily_data)

        assert len(issues) == 0

    def test_check_outliers_with_outliers(self):
        """测试检查异常值 - 有异常值"""
        # 创建包含极端异常值的数据
        data_with_outliers = pd.DataFrame(
            {
                "date": pd.date_range("2025-01-01", periods=5, freq="D"),
                "open": [10.0, 10.5, 10.3, 100.0, 11.0],  # 极端高值
                "high": [10.5, 10.8, 10.6, 11.0, 11.2],
                "low": [9.8, 10.2, 10.1, 10.5, 10.8],
                "close": [10.2, 10.6, 10.4, 10.9, 11.1],
                "volume": [1000, 1200, 800, 1500, 2000],
            }
        )

        validator = DataQualityValidator("test_source")

        issues = validator._check_outliers(data_with_outliers)

        assert len(issues) == 1
        assert issues[0]["type"] == "price_outliers"
        assert issues[0]["column"] == "open"

    def test_calculate_statistics_basic(self, sample_daily_data):
        """测试计算统计信息 - 基本信息"""
        validator = DataQualityValidator("test_source")

        stats = validator._calculate_statistics(sample_daily_data)

        assert stats["total_records"] == 5
        assert "date" in stats["columns"]
        assert "open" in stats["columns"]
        assert "close" in stats["columns"]
        assert stats["memory_usage_mb"] > 0

    def test_calculate_statistics_with_date_range(self, sample_daily_data):
        """测试计算统计信息 - 包含日期范围"""
        validator = DataQualityValidator("test_source")

        stats = validator._calculate_statistics(sample_daily_data)

        assert "date_range" in stats
        assert stats["date_range"]["start"] == "2025-01-01"
        assert stats["date_range"]["end"] == "2025-01-05"
        assert stats["date_range"]["days"] == 4

    def test_calculate_statistics_price_summary(self, sample_daily_data):
        """测试计算统计信息 - 价格汇总"""
        validator = DataQualityValidator("test_source")

        stats = validator._calculate_statistics(sample_daily_data)

        assert "price_summary" in stats
        price_summary = stats["price_summary"]

        assert "open" in price_summary
        assert "close" in price_summary
        assert "high" in price_summary
        assert "low" in price_summary

        # 验证统计值
        assert price_summary["open"]["min"] == 10.0
        assert price_summary["open"]["max"] == 10.8
        assert price_summary["close"]["mean"] == 10.64

    def test_calculate_statistics_invalid_date(self):
        """测试计算统计信息 - 无效日期"""
        data_invalid_date = pd.DataFrame(
            {"date": ["invalid-date", "also-invalid"], "close": [10.0, 10.5]}
        )

        validator = DataQualityValidator("test_source")

        stats = validator._calculate_statistics(data_invalid_date)

        assert stats["total_records"] == 2
        assert "date_range" not in stats  # 日期解析失败

    @patch("src.core.data_quality_validator.get_quality_monitor")
    def test_log_quality_check_with_monitor(self, mock_get_quality_monitor):
        """测试记录质量检查 - 有监控器"""
        mock_monitor = Mock()
        mock_get_quality_monitor.return_value = mock_monitor

        validator = DataQualityValidator("test_source")
        validator.quality_monitor = mock_monitor

        result = {
            "is_valid": False,
            "quality_score": 65.0,
            "issues": [{"severity": "critical"}, {"severity": "warning"}],
            "statistics": {"total_records": 100},
        }

        validator._log_quality_check(
            "600000", "daily", False, 65.0, result["issues"], result["statistics"]
        )

        # 验证监控器被调用
        mock_monitor.check_accuracy.assert_called_once()
        mock_monitor.check_completeness.assert_called_once()

    @patch("src.core.data_quality_validator.get_quality_monitor")
    def test_log_quality_check_without_monitor(self, mock_get_quality_monitor):
        """测试记录质量检查 - 无监控器"""
        mock_get_quality_monitor.return_value = None

        validator = DataQualityValidator("test_source")
        validator.quality_monitor = None

        # 应该不抛出异常
        validator._log_quality_check("600000", "daily", False, 65.0, [], {})

    @patch("src.core.data_quality_validator.get_quality_monitor")
    def test_log_quality_check_exception_handling(self, mock_get_quality_monitor):
        """测试记录质量检查 - 异常处理"""
        mock_monitor = Mock()
        mock_monitor.check_accuracy.side_effect = Exception("监控异常")
        mock_get_quality_monitor.return_value = mock_monitor

        validator = DataQualityValidator("test_source")
        validator.quality_monitor = mock_monitor

        # 应该不抛出异常
        validator._log_quality_check("600000", "daily", False, 65.0, [], {})

    def test_set_thresholds(self):
        """测试自定义阈值配置"""
        validator = DataQualityValidator("test_source")

        original_thresholds = validator.thresholds.copy()
        validator.set_thresholds(
            missing_rate_threshold=10.0, invalid_rate_threshold=2.0
        )

        # 验证阈值被更新
        assert validator.thresholds["missing_rate_threshold"] == 10.0
        assert validator.thresholds["invalid_rate_threshold"] == 2.0
        assert (
            validator.thresholds["duplicate_rate_threshold"]
            == original_thresholds["duplicate_rate_threshold"]
        )
        assert (
            validator.thresholds["outlier_rate_threshold"]
            == original_thresholds["outlier_rate_threshold"]
        )

    def test_set_thresholds_empty_kwargs(self):
        """测试自定义阈值配置 - 空参数"""
        validator = DataQualityValidator("test_source")

        original_thresholds = validator.thresholds.copy()
        validator.set_thresholds()

        # 验证阈值保持不变
        assert validator.thresholds == original_thresholds


class TestConvenienceFunctions:
    """测试便捷函数"""

    @patch("src.core.data_quality_validator.DataQualityValidator")
    def test_create_validator(self, mock_validator_class):
        """测试创建验证器"""
        mock_instance = Mock()
        mock_validator_class.return_value = mock_instance

        result = create_validator("test_source")

        mock_validator_class.assert_called_once_with("test_source")
        assert result is mock_instance

    @patch("src.core.data_quality_validator.create_validator")
    def test_validate_dataframe_convenience(self, mock_create_validator):
        """测试便捷数据验证函数"""
        mock_validator = Mock()
        mock_result = {
            "is_valid": True,
            "quality_score": 95.0,
            "issues": [],
            "statistics": {},
        }
        mock_validator.validate_stock_data.return_value = mock_result
        mock_create_validator.return_value = mock_validator

        sample_df = pd.DataFrame({"test": [1, 2, 3]})

        result = validate_dataframe(sample_df, "test_source", "600000", "daily")

        mock_create_validator.assert_called_once_with("test_source")
        mock_validator.validate_stock_data.assert_called_once_with(
            sample_df, "600000", "daily"
        )
        assert result == mock_result


class TestEdgeCases:
    """测试边界情况"""

    def test_validator_with_very_large_dataframe(self):
        """测试大数据集验证"""
        # 创建1000行数据
        large_df = pd.DataFrame(
            {
                "date": pd.date_range("2020-01-01", periods=1000, freq="D"),
                "open": np.random.uniform(10, 20, 1000),
                "high": np.random.uniform(10, 20, 1000),
                "low": np.random.uniform(10, 20, 1000),
                "close": np.random.uniform(10, 20, 1000),
                "volume": np.random.randint(1000, 10000, 1000),
            }
        )

        validator = DataQualityValidator("test_source")

        result = validator.validate_stock_data(large_df, "TEST", "daily")

        assert result["is_valid"] is True  # 随机数据通常通过验证
        assert result["statistics"]["total_records"] == 1000

    def test_validator_with_missing_required_columns(self):
        """测试缺少必需列的数据"""
        data_missing_cols = pd.DataFrame(
            {
                "date": pd.date_range("2025-01-01", periods=3, freq="D"),
                "open": [10.0, 10.5, 10.3],
                # 缺少 'high', 'low', 'close', 'volume'
            }
        )

        validator = DataQualityValidator("test_source")

        result = validator.validate_stock_data(data_missing_cols, "TEST", "daily")

        assert result["is_valid"] is False
        assert result["quality_score"] < 30.0  # 缺失3个重要列

        missing_cols_issues = [
            i for i in result["issues"] if i["type"] == "missing_columns"
        ]
        assert len(missing_cols_issues) == 1
        assert "high" in missing_cols_issues[0]["message"]
        assert "low" in missing_cols_issues[0]["message"]
        assert "close" in missing_cols_issues[0]["message"]
        assert "volume" in missing_cols_issues[0]["message"]

    def test_validator_with_single_column(self):
        """测试单列数据"""
        data_single_col = pd.DataFrame({"close": [10.0, 10.5, 11.0]})

        validator = DataQualityValidator("test_source")

        result = validator.validate_stock_data(data_single_col, "TEST", "default")

        # 默认类型只需要date和close，但缺少date
        assert result["is_valid"] is False

    def test_validate_all_data_types(self, sample_daily_data, sample_realtime_data):
        """测试所有数据类型的验证"""
        validator = DataQualityValidator("test_source")

        data_types = ["daily", "index_daily", "realtime", "default"]
        data_samples = [
            sample_daily_data,
            sample_daily_data,
            sample_realtime_data,
            sample_daily_data,
        ]
        symbols = ["600000", "000001", "000002", "600036"]

        for data_type, data, symbol in zip(data_types, data_samples, symbols):
            result = validator.validate_stock_data(data, symbol, data_type)
            assert isinstance(result, dict)
            assert "is_valid" in result
            assert "quality_score" in result
            assert "issues" in result
            assert "statistics" in result

    def test_calculate_statistics_no_columns(self):
        """测试计算统计信息 - 无列数据"""
        empty_df = pd.DataFrame()

        validator = DataQualityValidator("test_source")

        stats = validator._calculate_statistics(empty_df)

        assert stats["total_records"] == 0
        assert stats["columns"] == []
        assert stats["memory_usage_mb"] == 0.0

    def test_check_outliers_no_price_columns(self):
        """测试检查异常值 - 无价格列"""
        data_no_price = pd.DataFrame(
            {
                "date": pd.date_range("2025-01-01", periods=3, freq="D"),
                "volume": [1000, 1200, 800],
            }
        )

        validator = DataQualityValidator("test_source")

        issues = validator._check_outliers(data_no_price)

        assert len(issues) == 0  # 没有价格列可以检查


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
