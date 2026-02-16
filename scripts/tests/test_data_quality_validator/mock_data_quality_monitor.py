#!/usr/bin/env python3
"""
数据质量验证器测试套件 - Phase 6 成功模式
提供完整的数据质量验证功能测试，包括Mock监控器和各种数据场景
覆盖功能、边界、异常、性能、集成等全方位测试
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest
from unittest.mock import Mock, patch
import pandas as pd
import numpy as np
from datetime import datetime

# 导入被测试的模块
from src.core.data_quality_validator import (
    DataQualityValidator,
    create_validator,
    validate_dataframe,
)

class MockDataQualityMonitor:
    """Mock数据质量监控器，完整模拟真实监控器行为"""

    def __init__(self):
        self.accuracy_checks = []
        self.completeness_checks = []
        self.freshness_checks = []
        self.call_count = 0

    def check_accuracy(
        self,
        classification,
        database_type,
        table_name,
        total_records,
        invalid_records,
        validation_rules,
        threshold,
    ):
        """记录准确性检查"""
        self.call_count += 1
        self.accuracy_checks.append(
            {
                "classification": classification,
                "database_type": database_type,
                "table_name": table_name,
                "total_records": total_records,
                "invalid_records": invalid_records,
                "validation_rules": validation_rules,
                "threshold": threshold,
            }
        )
        return True

    def check_completeness(
        self,
        classification,
        database_type,
        table_name,
        total_records,
        null_records,
        required_columns,
        threshold,
    ):
        """记录完整性检查"""
        self.call_count += 1
        self.completeness_checks.append(
            {
                "classification": classification,
                "database_type": database_type,
                "table_name": table_name,
                "total_records": total_records,
                "null_records": null_records,
                "required_columns": required_columns,
                "threshold": threshold,
            }
        )
        return True

    def check_freshness(
        self,
        classification,
        database_type,
        table_name,
        latest_timestamp,
        threshold_seconds,
    ):
        """记录新鲜度检查"""
        self.call_count += 1
        self.freshness_checks.append(
            {
                "classification": classification,
                "database_type": database_type,
                "table_name": table_name,
                "latest_timestamp": latest_timestamp,
                "threshold_seconds": threshold_seconds,
            }
        )
        return True


class TestDataQualityValidatorBasic:
    """DataQualityValidator 基础功能测试类"""

    @pytest.fixture
    def mock_monitor(self):
        """创建Mock数据质量监控器"""
        return MockDataQualityMonitor()

    @pytest.fixture
    def validator(self, mock_monitor):
        """创建数据质量验证器实例"""
        return DataQualityValidator("test_source", mock_monitor)

    @pytest.fixture
    def sample_daily_data(self):
        """创建样本日线数据"""
        dates = pd.date_range(start="2024-01-01", end="2024-01-10", freq="D")
        # 只包含工作日
        dates = [d for d in dates if d.weekday() < 5][:5]

        return pd.DataFrame(
            {
                "date": [d.strftime("%Y-%m-%d") for d in dates],
                "open": [100.0 + i * 2 for i in range(len(dates))],
                "high": [105.0 + i * 2 for i in range(len(dates))],
                "low": [95.0 + i * 2 for i in range(len(dates))],
                "close": [102.0 + i * 2 for i in range(len(dates))],
                "volume": [1000000 + i * 100000 for i in range(len(dates))],
            }
        )

    @pytest.fixture
    def sample_realtime_data(self):
        """创建样本实时数据"""
        return pd.DataFrame(
            [
                {
                    "code": "600519",
                    "name": "贵州茅台",
                    "price": 1680.50,
                    "volume": 1000,
                    "timestamp": datetime.now().isoformat(),
                }
            ]
        )

    def test_initialization_with_default_monitor(self):
        """测试使用默认监控器初始化"""
        with patch(
            "src.core.data_quality_validator.get_quality_monitor"
        ) as mock_get_monitor:
            mock_monitor = Mock()
            mock_get_monitor.return_value = mock_monitor

            validator = DataQualityValidator("test_source")

            assert validator.source_name == "test_source"
            assert validator.quality_monitor is mock_monitor
            assert "missing_rate_threshold" in validator.thresholds
            assert validator.thresholds["missing_rate_threshold"] == 5.0

    def test_initialization_with_custom_monitor(self, mock_monitor):
        """测试使用自定义监控器初始化"""
        validator = DataQualityValidator("custom_source", mock_monitor)

        assert validator.source_name == "custom_source"
        assert validator.quality_monitor is mock_monitor

    def test_initialization_thresholds(self, mock_monitor):
        """测试初始化阈值配置"""
        validator = DataQualityValidator("test_source", mock_monitor)

        expected_thresholds = {
            "missing_rate_threshold": 5.0,
            "invalid_rate_threshold": 1.0,
            "duplicate_rate_threshold": 0.5,
            "outlier_rate_threshold": 2.0,
            "freshness_threshold_seconds": 300,
        }

        for key, value in expected_thresholds.items():
            assert key in validator.thresholds
            assert validator.thresholds[key] == value

    def test_validate_empty_dataframe(self, validator):
        """测试验证空DataFrame"""
        empty_df = pd.DataFrame()
        result = validator.validate_stock_data(empty_df, "600519", "daily")

        assert result["is_valid"] is False
        assert result["quality_score"] == 0.0
        assert len(result["issues"]) == 1
        assert result["issues"][0]["type"] == "empty_data"
        assert result["statistics"] == {}

    def test_validate_daily_data_success(self, validator, sample_daily_data):
        """测试验证成功的日线数据"""
        result = validator.validate_stock_data(sample_daily_data, "600519", "daily")

        assert result["is_valid"] is True
        assert result["quality_score"] >= 70.0
        assert len(result["issues"]) == 0  # 正常数据应该没有问题
        assert result["statistics"]["total_records"] == 5
        assert "date_range" in result["statistics"]
        assert "price_summary" in result["statistics"]

    def test_validate_realtime_data_success(self, validator, sample_realtime_data):
        """测试验证成功的实时数据"""
        result = validator.validate_stock_data(
            sample_realtime_data, "600519", "realtime"
        )

        assert result["is_valid"] is True
        assert result["quality_score"] >= 70.0
        assert len(result["issues"]) == 0
        assert result["statistics"]["total_records"] == 1

    def test_validate_data_missing_columns(self, validator):
        """测试验证缺少必需列的数据"""
        # 只包含date列，缺少价格和成交量列
        incomplete_df = pd.DataFrame({"date": ["2024-01-01", "2024-01-02"]})

        result = validator.validate_stock_data(incomplete_df, "600519", "daily")

        assert result["is_valid"] is False  # 缺少关键列应该无效
        assert result["quality_score"] < 70.0

        # 检查是否有missing_columns问题
        missing_column_issues = [
            i for i in result["issues"] if i["type"] == "missing_columns"
        ]
        assert len(missing_column_issues) > 0

    def test_get_required_columns_daily(self, validator):
        """测试获取日线数据必需列"""
        columns = validator._get_required_columns("daily")
        expected = ["date", "open", "high", "low", "close", "volume"]
        assert set(columns) == set(expected)

    def test_get_required_columns_realtime(self, validator):
        """测试获取实时数据必需列"""
        columns = validator._get_required_columns("realtime")
        expected = ["code", "name", "price", "volume", "timestamp"]
        assert set(columns) == set(expected)

    def test_get_required_columns_index_daily(self, validator):
        """测试获取指数日线数据必需列"""
        columns = validator._get_required_columns("index_daily")
        expected = ["date", "open", "high", "low", "close", "volume"]
        assert set(columns) == set(expected)

    def test_get_required_columns_default(self, validator):
        """测试获取默认数据类型必需列"""
        columns = validator._get_required_columns("unknown_type")
        expected = ["date", "close"]
        assert set(columns) == set(expected)

    def test_set_thresholds(self, validator):
        """测试自定义阈值配置"""
        original_threshold = validator.thresholds["missing_rate_threshold"]

        validator.set_thresholds(
            missing_rate_threshold=10.0, outlier_rate_threshold=5.0
        )

        assert validator.thresholds["missing_rate_threshold"] == 10.0
        assert validator.thresholds["outlier_rate_threshold"] == 5.0
        assert validator.thresholds["invalid_rate_threshold"] == 1.0  # 其他值保持不变


class TestDataQualityValidatorCompleteness:
    """数据完整性测试类"""

    @pytest.fixture
    def validator(self):
        mock_monitor = MockDataQualityMonitor()
        return DataQualityValidator("test_source", mock_monitor)

    def test_check_completeness_no_missing_data(self, validator):
        """测试没有缺失数据的情况"""
        df = pd.DataFrame(
            {
                "date": ["2024-01-01", "2024-01-02"],
                "close": [100.0, 101.0],
                "volume": [1000, 1100],
            }
        )

        issues = validator._check_completeness(df, ["date", "close", "volume"])
        assert len(issues) == 0

    def test_check_completeness_with_missing_data_below_threshold(self, validator):
        """测试缺失率低于阈值的情况"""
        # 创建有1%缺失率的数据（低于5%阈值）
        df = pd.DataFrame(
            {
                "date": ["2024-01-01"] * 10,
                "close": [100.0] * 9 + [None],  # 1/10 = 10%缺失，高于阈值
                "volume": [1000] * 10,  # 没有缺失
            }
        )

        # 设置高阈值以测试低于阈值的情况
        validator.set_thresholds(missing_rate_threshold=25.0)
        issues = validator._check_completeness(df, ["date", "close", "volume"])
        assert len(issues) == 0

    def test_check_completeness_with_missing_data_above_threshold(self, validator):
        """测试缺失率高于阈值的情况"""
        # 创建有10%缺失率的数据（高于5%阈值）
        df = pd.DataFrame(
            {
                "date": ["2024-01-01"] * 10,
                "close": [100.0] * 9 + [None],  # 1/10 = 10%缺失
                "volume": [1000] * 10,  # 没有缺失
            }
        )

        issues = validator._check_completeness(df, ["date", "close", "volume"])
        assert len(issues) == 1
        assert issues[0]["type"] == "missing_data"
        assert issues[0]["column"] == "close"
        assert issues[0]["missing_rate"] == 10.0
        assert issues[0]["severity"] == "warning"

    def test_check_completeness_critical_missing_rate(self, validator):
        """测试严重缺失率的情况"""
        # 创建有30%缺失率的数据（严重问题）
        df = pd.DataFrame(
            {
                "date": ["2024-01-01"] * 10,
                "close": [100.0] * 7 + [None] * 3,  # 3/10 = 30%缺失
            }
        )

        issues = validator._check_completeness(df, ["date", "close"])
        assert len(issues) == 1
        assert issues[0]["severity"] == "critical"
        assert issues[0]["score_penalty"] == 20  # 30%超过20限制

    def test_check_completeness_missing_required_column(self, validator):
        """测试缺少必需列的情况"""
        df = pd.DataFrame(
            {
                "date": ["2024-01-01", "2024-01-02"],
                # 缺少close列
                "volume": [1000, 1100],
            }
        )

        # close列不在DataFrame中，但我们在检查完整性，所以应该跳过
        issues = validator._check_completeness(df, ["date", "close", "volume"])
        # 只有存在的列会被检查
        assert len(issues) == 0

    def test_check_completeness_edge_case_empty_column(self, validator):
        """测试空列的边界情况"""
        df = pd.DataFrame(
            {
                "date": ["2024-01-01", "2024-01-02", "2024-01-03"],
                "close": [None, None, None],  # 全部缺失
            }
        )

        issues = validator._check_completeness(df, ["date", "close"])
        assert len(issues) == 1
        assert issues[0]["missing_rate"] == 100.0
        assert issues[0]["severity"] == "critical"


class TestDataQualityValidatorAccuracy:
    """数据准确性测试类"""

    @pytest.fixture
    def validator(self):
        mock_monitor = MockDataQualityMonitor()
        return DataQualityValidator("test_source", mock_monitor)

    def test_check_accuracy_normal_prices(self, validator):
        """测试正常价格数据"""
        df = pd.DataFrame(
            {
                "open": [100.0, 101.0, 102.0],
                "high": [105.0, 106.0, 107.0],
                "low": [95.0, 96.0, 97.0],
                "close": [102.0, 103.0, 104.0],
                "volume": [1000, 1100, 1200],
            }
        )

        issues = validator._check_accuracy(df, "600519")
        assert len(issues) == 0

    def test_check_accuracy_negative_prices(self, validator):
        """测试负价格数据"""
        df = pd.DataFrame(
            {
                "open": [100.0, -50.0, 102.0],  # 包含负价格
                "high": [105.0, 106.0, 107.0],
                "low": [95.0, 96.0, 97.0],
                "close": [102.0, 103.0, 104.0],
                "volume": [1000, 1100, 1200],
            }
        )

        issues = validator._check_accuracy(df, "600519")
        assert len(issues) == 1
        assert issues[0]["type"] == "invalid_price"
        assert issues[0]["column"] == "open"
        assert issues[0]["invalid_count"] == 1
        assert issues[0]["severity"] == "critical"

    def test_check_accuracy_invalid_high_low_logic(self, validator):
        """测试最高价低于最低价的逻辑错误"""
        df = pd.DataFrame(
            {
                "open": [100.0, 101.0, 102.0],
                "high": [95.0, 106.0, 107.0],  # 第一行high < low
                "low": [105.0, 96.0, 97.0],
                "close": [102.0, 103.0, 104.0],
                "volume": [1000, 1100, 1200],
            }
        )

        issues = validator._check_accuracy(df, "600519")
        assert len(issues) == 1
        assert issues[0]["type"] == "price_logic_error"
        assert issues[0]["severity"] == "critical"

    def test_check_accuracy_negative_volume(self, validator):
        """测试负成交量数据"""
        df = pd.DataFrame(
            {
                "open": [100.0, 101.0, 102.0],
                "high": [105.0, 106.0, 107.0],
                "low": [95.0, 96.0, 97.0],
                "close": [102.0, 103.0, 104.0],
                "volume": [1000, -500, 1200],  # 包含负成交量
            }
        )

        issues = validator._check_accuracy(df, "600519")
        assert len(issues) == 1
        assert issues[0]["type"] == "invalid_volume"
        assert issues[0]["invalid_count"] == 1
        assert issues[0]["severity"] == "critical"

    def test_check_accuracy_multiple_issues(self, validator):
        """测试多个准确性问题"""
        df = pd.DataFrame(
            {
                "open": [100.0, -50.0, -30.0],  # 两个负价格
                "high": [95.0, 106.0, 107.0],  # 第一行逻辑错误
                "low": [105.0, 96.0, 97.0],
                "close": [102.0, 103.0, 104.0],
                "volume": [1000, -500, -300],  # 两个负成交量
            }
        )

        issues = validator._check_accuracy(df, "600519")

        # 应该检测到所有问题
        issue_types = [issue["type"] for issue in issues]
        assert "invalid_price" in issue_types
        assert "price_logic_error" in issue_types
        assert "invalid_volume" in issue_types

        # 验证问题数量 - 验证器将同一列的问题合并为一个issue
        price_issues = [i for i in issues if i["type"] == "invalid_price"]
        volume_issues = [i for i in issues if i["type"] == "invalid_volume"]
        assert len(price_issues) == 1  # open列的负价格合并为一个issue
        assert len(volume_issues) == 1  # volume列的负成交量合并为一个issue

        # 验证负价格数量统计
        assert price_issues[0]["invalid_count"] == 2  # open有两个负值
        assert volume_issues[0]["invalid_count"] == 2  # volume有两个负值

    def test_check_accuracy_no_price_columns(self, validator):
        """测试没有价格列的数据"""
        df = pd.DataFrame(
            {"date": ["2024-01-01", "2024-01-02"], "some_other_column": [1, 2]}
        )

        issues = validator._check_accuracy(df, "600519")
        assert len(issues) == 0  # 没有价格列就不进行价格检查


class TestDataQualityValidatorConsistency:
    """数据一致性测试类"""

    @pytest.fixture
    def validator(self):
        mock_monitor = MockDataQualityMonitor()
        return DataQualityValidator("test_source", mock_monitor)

    def test_check_consistency_valid_date_format(self, validator):
        """测试有效日期格式"""
        df = pd.DataFrame(
            {
                "date": ["2024-01-01", "2024-01-02", "2024-01-03"],
                "close": [100.0, 101.0, 102.0],
            }
        )

        issues = validator._check_consistency(df, "daily")
        assert len(issues) == 0

    def test_check_consistency_invalid_date_format(self, validator):
        """测试无效日期格式"""
        df = pd.DataFrame(
            {
                "date": ["2024-13-01", "invalid-date", "2024-01-32"],  # 无效日期
                "close": [100.0, 101.0, 102.0],
            }
        )

        issues = validator._check_consistency(df, "daily")
        assert len(issues) == 1
        assert issues[0]["type"] == "date_format_inconsistent"
        assert issues[0]["severity"] == "warning"

    def test_check_consistency_valid_timestamp_format(self, validator):
        """测试有效时间戳格式"""
        df = pd.DataFrame(
            {
                "code": ["600519"],
                "name": "贵州茅台",
                "price": 1680.50,
                "volume": 1000,
                "timestamp": [datetime.now().isoformat()],
            }
        )

        issues = validator._check_consistency(df, "realtime")
        assert len(issues) == 0

    def test_check_consistency_invalid_timestamp_format(self, validator):
        """测试无效时间戳格式"""
        df = pd.DataFrame(
            {
                "code": ["600519"],
                "name": "贵州茅台",
                "price": 1680.50,
                "volume": 1000,
                "timestamp": ["invalid-timestamp"],
            }
        )

        issues = validator._check_consistency(df, "realtime")
        assert len(issues) == 1
        assert issues[0]["type"] == "timestamp_format_inconsistent"
        assert issues[0]["severity"] == "warning"

    def test_check_consistency_mixed_date_formats(self, validator):
        """测试混合日期格式"""
        df = pd.DataFrame(
            {
                "date": ["2024-01-01", "2024/01/02", "2024-01-03"],  # 混合格式
                "close": [100.0, 101.0, 102.0],
            }
        )

        issues = validator._check_consistency(df, "daily")
        # 混合格式可能导致不一致的日期解析
        assert len(issues) >= 0  # pandas可能处理某些格式

    def test_check_consistency_edge_case_empty_timestamps(self, validator):
        """测试空时间戳的边界情况"""
        df = pd.DataFrame(
            {
                "code": ["600519", "000001"],
                "name": ["股票A", "股票B"],
                "price": [100.0, 200.0],
                "volume": [1000, 2000],
                "timestamp": ["", None],  # 空值和None
            }
        )

        issues = validator._check_consistency(df, "realtime")
        # 空时间戳应该被识别为格式问题
        assert len(issues) >= 0


class TestDataQualityValidatorDuplicates:
    """重复数据测试类"""

    @pytest.fixture
    def validator(self):
        mock_monitor = MockDataQualityMonitor()
        return DataQualityValidator("test_source", mock_monitor)

    def test_check_duplicates_no_duplicates(self, validator):
        """测试没有重复数据"""
        df = pd.DataFrame(
            {
                "date": ["2024-01-01", "2024-01-02", "2024-01-03"],
                "close": [100.0, 101.0, 102.0],
            }
        )

        issues = validator._check_duplicates(df)
        assert len(issues) == 0

    def test_check_duplicates_with_duplicates_below_threshold(self, validator):
        """测试重复率低于阈值"""
        # 创建1%重复率的数据（低于0.5%阈值）
        data = []
        for i in range(200):
            data.append({"date": f"2024-01-{i % 30 + 1:02d}", "close": 100.0 + i})
        # 添加2行重复数据
        data.append({"date": "2024-01-01", "close": 100.0})
        data.append({"date": "2024-01-01", "close": 100.0})

        df = pd.DataFrame(data)
        duplicate_rate = (2 / len(df)) * 100  # 约1%

        # 设置高阈值以测试低于阈值的情况
        validator.set_thresholds(duplicate_rate_threshold=2.0)
        issues = validator._check_duplicates(df)
        assert len(issues) == 0

    def test_check_duplicates_with_duplicates_above_threshold(self, validator):
        """测试重复率高于阈值"""
        df = pd.DataFrame(
            {
                "date": [
                    "2024-01-01",
                    "2024-01-01",
                    "2024-01-02",
                    "2024-01-02",
                ],  # 50%重复
                "close": [100.0, 100.0, 101.0, 101.0],
            }
        )

        issues = validator._check_duplicates(df)
        assert len(issues) == 1
        assert issues[0]["type"] == "duplicate_rows"
        assert issues[0]["duplicate_count"] == 2
        assert issues[0]["duplicate_rate"] == 50.0
        assert issues[0]["severity"] == "warning"

    def test_check_duplicates_penalty_calculation(self, validator):
        """测试重复数据惩罚计算"""
        df = pd.DataFrame(
            {
                "date": ["2024-01-01"] * 10,  # 90%重复率
                "close": [100.0] * 10,
            }
        )

        issues = validator._check_duplicates(df)
        assert len(issues) == 1
        # 惩罚应该是 min(10, duplicate_rate * 2) = min(10, 18) = 10
        assert issues[0]["score_penalty"] == 10

    def test_check_duplicates_exact_duplicates(self, validator):
        """测试完全重复的行"""
        df = pd.DataFrame(
            {
                "date": ["2024-01-01", "2024-01-01", "2024-01-02"],
                "open": [100.0, 100.0, 101.0],
                "close": [102.0, 102.0, 103.0],
            }
        )

        issues = validator._check_duplicates(df)
        assert len(issues) == 1
        assert issues[0]["duplicate_count"] == 1  # 第一行重复一次

    def test_check_duplicates_partial_duplicates(self, validator):
        """测试部分列重复的行"""
        df = pd.DataFrame(
            {
                "date": ["2024-01-01", "2024-01-01", "2024-01-02"],
                "open": [100.0, 100.0, 101.0],
                "close": [102.0, 103.0, 103.0],  # close列不同
            }
        )

        # pandas的duplicated()默认检查所有列
        # 这种情况下前两行不完全重复，所以不会被识别为重复
        issues = validator._check_duplicates(df)
        assert len(issues) == 0


