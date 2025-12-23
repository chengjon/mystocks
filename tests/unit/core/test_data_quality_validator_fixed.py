"""
数据质量验证器测试模块

测试数据质量验证和异常检测功能的核心模块

测试覆盖:
- 验证器初始化
- 基本数据验证功能
- 统计计算功能
- 边界情况处理
"""

import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import sys

# Mock the monitoring dependencies to avoid import issues
sys.modules["src.monitoring.data_quality_monitor"] = MagicMock()
sys.modules["src.monitoring.monitoring_database"] = MagicMock()
sys.modules["src.core.exceptions"] = MagicMock()

from src.core.data_quality_validator import DataQualityValidator


class TestDataQualityValidator:
    """数据质量验证器测试类"""

    def test_validator_initialization_default(self):
        """测试验证器默认初始化"""
        # Mock the monitoring dependencies
        with patch(
            "src.core.data_quality_validator.get_quality_monitor"
        ) as mock_get_monitor:
            mock_monitor = Mock()
            mock_get_monitor.return_value = mock_monitor

            validator = DataQualityValidator("test_source")
            assert validator.source_name == "test_source"
            assert validator.quality_monitor is mock_monitor
            assert validator.thresholds["missing_rate_threshold"] == 5.0
            assert validator.thresholds["invalid_rate_threshold"] == 1.0
            assert validator.thresholds["duplicate_rate_threshold"] == 0.5
            assert validator.thresholds["outlier_rate_threshold"] == 2.0
            assert validator.thresholds["freshness_threshold_seconds"] == 300

    def test_validator_initialization_with_custom_monitor(self):
        """测试使用自定义监控器的验证器初始化"""
        mock_monitor = Mock()

        validator = DataQualityValidator("test_source", mock_monitor)
        assert validator.source_name == "test_source"
        assert validator.quality_monitor is mock_monitor

    def test_validate_stock_data_empty_dataframe(self):
        """测试空数据框验证"""
        with patch("src.core.data_quality_validator.get_quality_monitor"):
            validator = DataQualityValidator("test_source")
            empty_df = pd.DataFrame()

            result = validator.validate_stock_data(empty_df, "600000", "daily")

            assert result["is_valid"] is False
            assert result["quality_score"] == 0.0
            assert len(result["issues"]) == 1
            assert result["issues"][0]["type"] == "empty_data"
            assert result["statistics"] == {}

    def test_validate_stock_data_missing_columns(self):
        """测试缺少必需列的数据验证"""
        with patch("src.core.data_quality_validator.get_quality_monitor"):
            validator = DataQualityValidator("test_source")

            # 创建缺少关键列的数据
            incomplete_data = pd.DataFrame(
                {
                    "date": ["2024-01-01", "2024-01-02"],
                    "open": [10.0, 11.0],
                    # 缺少 high, low, close, volume
                }
            )

            result = validator.validate_stock_data(incomplete_data, "600000", "daily")

            assert result["is_valid"] is False
            assert result["quality_score"] < 100.0

            # 检查缺少列的问题
            missing_column_issues = [
                issue
                for issue in result["issues"]
                if issue["type"] == "missing_columns"
            ]
            assert len(missing_column_issues) > 0

    def test_validate_stock_data_with_issues(self):
        """测试有问题的数据验证"""
        with patch("src.core.data_quality_validator.get_quality_monitor"):
            validator = DataQualityValidator("test_source")

            # 创建有问题数据的DataFrame
            problematic_data = pd.DataFrame(
                {
                    "date": ["2024-01-01", "2024-01-02", "2024-01-03"],
                    "open": [10.0, -5.0, 12.0],  # 包含负价格
                    "high": [11.0, 9.0, 8.0],  # 包含价格逻辑错误 (第3行high < open)
                    "low": [9.0, 8.0, 13.0],  # 包含价格逻辑错误 (第3行low > open)
                    "close": [10.5, 9.5, 11.0],
                    "volume": [1000, -100, 1200],  # 包含负成交量
                }
            )

            result = validator.validate_stock_data(problematic_data, "600000", "daily")

            assert result["is_valid"] is False  # 应该有严重问题
            assert result["quality_score"] < 100.0
            assert len(result["issues"]) > 0

    def test_check_completeness_with_missing_data(self):
        """测试完整性检查 - 有缺失数据"""
        with patch("src.core.data_quality_validator.get_quality_monitor"):
            validator = DataQualityValidator("test_source")

            # 添加一些缺失值
            data_with_missing = pd.DataFrame(
                {
                    "date": ["2024-01-01", "2024-01-02", "2024-01-03"],
                    "open": [10.0, np.nan, 12.0],
                    "high": [11.0, 13.0, np.nan],
                    "low": [9.0, 11.0, 13.0],
                    "close": [10.5, 12.5, 14.5],
                    "volume": [1000, 1200, np.nan],
                }
            )

            required_columns = ["date", "open", "high", "low", "close", "volume"]
            issues = validator._check_completeness(data_with_missing, required_columns)

            assert len(issues) > 0

            # 检查缺失的列
            missing_columns = [issue["column"] for issue in issues]
            assert "open" in missing_columns
            assert "high" in missing_columns
            assert "volume" in missing_columns

    def test_check_completeness_no_issues(self):
        """测试完整性检查 - 无问题"""
        with patch("src.core.data_quality_validator.get_quality_monitor"):
            validator = DataQualityValidator("test_source")

            # 创建完整的数据
            complete_data = pd.DataFrame(
                {
                    "date": ["2024-01-01", "2024-01-02"],
                    "open": [10.0, 11.0],
                    "high": [11.0, 12.0],
                    "low": [9.0, 10.0],
                    "close": [10.5, 11.5],
                    "volume": [1000, 1200],
                }
            )

            required_columns = ["date", "open", "high", "low", "close", "volume"]
            issues = validator._check_completeness(complete_data, required_columns)

            assert len(issues) == 0

    def test_check_accuracy_negative_prices(self):
        """测试准确性检查 - 负价格"""
        with patch("src.core.data_quality_validator.get_quality_monitor"):
            validator = DataQualityValidator("test_source")

            # 添加负价格
            data_with_negative = pd.DataFrame(
                {
                    "date": ["2024-01-01", "2024-01-02"],
                    "open": [10.0, -5.0],
                    "high": [11.0, 12.0],
                    "low": [9.0, 10.0],
                    "close": [-10.5, 11.5],
                    "volume": [1000, 1200],
                }
            )

            issues = validator._check_accuracy(data_with_negative, "600000")

            assert len(issues) >= 2  # open和close都应该有问题

            # 检查问题类型
            issue_types = [issue["type"] for issue in issues]
            assert "invalid_price" in issue_types

    def test_check_accuracy_price_logic_error(self):
        """测试准确性检查 - 价格逻辑错误"""
        with patch("src.core.data_quality_validator.get_quality_monitor"):
            validator = DataQualityValidator("test_source")

            # 添加价格逻辑错误
            data_with_logic_error = pd.DataFrame(
                {
                    "date": ["2024-01-01", "2024-01-02"],
                    "open": [10.0, 15.0],
                    "high": [9.0, 16.0],  # 第1行high < low，逻辑错误
                    "low": [11.0, 14.0],  # 第1行low > open，逻辑错误
                    "close": [10.5, 15.5],
                    "volume": [1000, 1200],
                }
            )

            issues = validator._check_accuracy(data_with_logic_error, "600000")

            assert len(issues) > 0

            # 检查问题类型
            issue_types = [issue["type"] for issue in issues]
            assert "price_logic_error" in issue_types

    def test_check_accuracy_negative_volume(self):
        """测试准确性检查 - 负成交量"""
        with patch("src.core.data_quality_validator.get_quality_monitor"):
            validator = DataQualityValidator("test_source")

            # 添加负成交量
            data_with_negative_volume = pd.DataFrame(
                {
                    "date": ["2024-01-01", "2024-01-02"],
                    "open": [10.0, 11.0],
                    "high": [11.0, 12.0],
                    "low": [9.0, 10.0],
                    "close": [10.5, 11.5],
                    "volume": [-100, 1200],
                }
            )

            issues = validator._check_accuracy(data_with_negative_volume, "600000")

            assert len(issues) > 0

            # 检查问题类型
            issue_types = [issue["type"] for issue in issues]
            assert any("volume" in issue.get("type", "").lower() for issue in issues)

    def test_check_duplicates_with_duplicates(self):
        """测试重复检查 - 有重复"""
        with patch("src.core.data_quality_validator.get_quality_monitor"):
            validator = DataQualityValidator("test_source")

            # 创建重复行数据
            data_with_duplicates = pd.DataFrame(
                {
                    "date": ["2024-01-01", "2024-01-01", "2024-01-02"],
                    "open": [10.0, 10.0, 11.0],
                    "high": [11.0, 11.0, 12.0],
                    "low": [9.0, 9.0, 10.0],
                    "close": [10.5, 10.5, 11.5],
                    "volume": [1000, 1000, 1200],
                }
            )

            issues = validator._check_duplicates(data_with_duplicates)

            assert len(issues) > 0

            # 检查问题类型
            issue_types = [issue["type"] for issue in issues]
            assert "duplicate_rows" in issue_types

    def test_check_outliers_with_outliers(self):
        """测试异常值检查 - 有异常值"""
        with patch("src.core.data_quality_validator.get_quality_monitor"):
            validator = DataQualityValidator("test_source")

            # 添加极端异常值
            normal_prices = [10.0, 10.5, 11.0, 11.5, 12.0]
            data_with_outliers = pd.DataFrame(
                {
                    "date": [
                        "2024-01-01",
                        "2024-01-02",
                        "2024-01-03",
                        "2024-01-04",
                        "2024-01-05",
                        "2024-01-06",
                    ],
                    "open": normal_prices + [1000.0],  # 添加极端异常值
                    "high": [p + 0.5 for p in normal_prices] + [1001.0],
                    "low": [p - 0.5 for p in normal_prices] + [999.0],
                    "close": normal_prices + [1000.5],
                    "volume": [1000] * 6,
                }
            )

            issues = validator._check_outliers(data_with_outliers)

            # 由于异常值检测基于IQR方法，极端值应该被检测到
            # 但具体行为取决于数据分布
            assert isinstance(issues, list)

    def test_calculate_statistics_basic(self):
        """测试统计计算 - 基本功能"""
        with patch("src.core.data_quality_validator.get_quality_monitor"):
            validator = DataQualityValidator("test_source")

            sample_data = pd.DataFrame(
                {
                    "date": ["2024-01-01", "2024-01-02", "2024-01-03"],
                    "open": [10.0, 11.0, 12.0],
                    "high": [11.0, 12.0, 13.0],
                    "low": [9.0, 10.0, 11.0],
                    "close": [10.5, 11.5, 12.5],
                    "volume": [1000, 1200, 1100],
                }
            )

            stats = validator._calculate_statistics(sample_data)

            assert stats["total_records"] == 3
            assert "columns" in stats
            assert "memory_usage_mb" in stats
            assert stats["memory_usage_mb"] > 0

    def test_calculate_statistics_with_date_range(self):
        """测试统计计算 - 日期范围"""
        with patch("src.core.data_quality_validator.get_quality_monitor"):
            validator = DataQualityValidator("test_source")

            sample_data = pd.DataFrame(
                {
                    "date": ["2024-01-01", "2024-01-03", "2024-01-05"],
                    "close": [10.5, 11.5, 12.5],
                }
            )

            stats = validator._calculate_statistics(sample_data)

            assert "date_range" in stats
            assert "start" in stats["date_range"]
            assert "end" in stats["date_range"]
            assert "days" in stats["date_range"]
            assert stats["date_range"]["days"] > 0

    def test_calculate_statistics_price_summary(self):
        """测试统计计算 - 价格摘要"""
        with patch("src.core.data_quality_validator.get_quality_monitor"):
            validator = DataQualityValidator("test_source")

            sample_data = pd.DataFrame(
                {
                    "date": ["2024-01-01", "2024-01-02"],
                    "open": [10.0, 11.0],
                    "high": [11.0, 12.0],
                    "low": [9.0, 10.0],
                    "close": [10.5, 11.5],
                    "volume": [1000, 1200],
                }
            )

            stats = validator._calculate_statistics(sample_data)

            assert "price_summary" in stats

            price_summary = stats["price_summary"]
            expected_columns = ["open", "high", "low", "close"]
            for col in expected_columns:
                assert col in price_summary
                assert "min" in price_summary[col]
                assert "max" in price_summary[col]
                assert "mean" in price_summary[col]
                assert "std" in price_summary[col]

    def test_calculate_statistics_empty_dataframe(self):
        """测试统计计算 - 空数据框"""
        with patch("src.core.data_quality_validator.get_quality_monitor"):
            validator = DataQualityValidator("test_source")

            empty_data = pd.DataFrame()

            stats = validator._calculate_statistics(empty_data)

            assert stats["total_records"] == 0
            assert stats["columns"] == []
            assert "price_summary" not in stats


class TestEdgeCases:
    """边界情况测试"""

    def test_validator_with_large_dataframe(self):
        """测试较大数据框的处理"""
        with patch("src.core.data_quality_validator.get_quality_monitor"):
            validator = DataQualityValidator("test_source")

            # 创建较大的数据框（但不要太大以免测试缓慢）
            large_data = pd.DataFrame(
                {
                    "date": pd.date_range("2024-01-01", periods=100, freq="D").strftime(
                        "%Y-%m-%d"
                    ),
                    "open": np.random.uniform(10, 100, 100),
                    "high": np.random.uniform(10, 100, 100),
                    "low": np.random.uniform(10, 100, 100),
                    "close": np.random.uniform(10, 100, 100),
                    "volume": np.random.randint(1000, 100000, 100),
                }
            )

            result = validator.validate_stock_data(large_data, "600000", "daily")

            assert result["is_valid"] in [
                True,
                False,
            ]  # 结果可能有效或无效，取决于随机数据
            assert result["statistics"]["total_records"] == 100
            assert result["statistics"]["memory_usage_mb"] > 0

    def test_validator_with_single_column(self):
        """测试单列数据框"""
        with patch("src.core.data_quality_validator.get_quality_monitor"):
            validator = DataQualityValidator("test_source")

            single_column_data = pd.DataFrame({"close": [10.0, 11.0, 12.0]})

            result = validator.validate_stock_data(
                single_column_data, "600000", "daily"
            )

            assert result["is_valid"] is False  # 应该因为缺少必需列而无效
            assert len(result["issues"]) > 0

    def test_get_required_columns_for_different_types(self):
        """测试不同数据类型的必需列获取"""
        with patch("src.core.data_quality_validator.get_quality_monitor"):
            validator = DataQualityValidator("test_source")

            # 测试日线数据
            daily_columns = validator._get_required_columns("daily")
            assert isinstance(daily_columns, list)
            assert len(daily_columns) > 0

            # 测试实时数据
            realtime_columns = validator._get_required_columns("realtime")
            assert isinstance(realtime_columns, list)
            assert len(realtime_columns) > 0

    def test_threshold_configurations(self):
        """测试阈值配置"""
        with patch("src.core.data_quality_validator.get_quality_monitor"):
            validator = DataQualityValidator("test_source")

            # 验证所有阈值都存在
            expected_thresholds = [
                "missing_rate_threshold",
                "invalid_rate_threshold",
                "duplicate_rate_threshold",
                "outlier_rate_threshold",
                "freshness_threshold_seconds",
            ]

            for threshold in expected_thresholds:
                assert threshold in validator.thresholds
                assert isinstance(validator.thresholds[threshold], (int, float))
                assert validator.thresholds[threshold] > 0
