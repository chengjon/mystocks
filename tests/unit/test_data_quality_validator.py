"""
单元测试: DataQualityValidator
"""

import numpy as np
import pandas as pd
import pytest

from src.core.data_source.data_quality_validator import (
    DataQualityValidator,
    ValidationResult,
    ValidationSummary,
)


class TestDataQualityValidator:
    """DataQualityValidator 单元测试"""

    def test_ohlc_logic_validation_pass(self):
        """测试 OHLC 逻辑验证 (通过场景)"""
        validator = DataQualityValidator()

        # 创建有效的 OHLC 数据
        data = pd.DataFrame(
            {
                "open": [10.0, 11.0, 12.0],
                "high": [11.0, 12.0, 13.0],
                "low": [9.0, 10.0, 11.0],
                "close": [10.5, 11.5, 12.5],
                "volume": [1000, 2000, 3000],
            }
        )

        result = validator.validate(data, data_source="test")

        assert result.passed is True
        assert result.total_checks == 3  # logic, business, statistical
        assert result.quality_score == 100.0

    def test_ohlc_logic_validation_failure(self):
        """测试 OHLC 逻辑验证 (失败场景)"""
        validator = DataQualityValidator()

        # 创建无效的 OHLC 数据
        data = pd.DataFrame(
            {
                "open": [10.0, 11.0, 12.0],
                "high": [9.0, 10.0, 11.0],  # High < Open (无效)
                "low": [9.0, 10.0, 11.0],
                "close": [10.5, 11.5, 12.5],
            }
        )

        result = validator.validate(data, data_source="test")

        assert result.passed is False
        assert result.quality_score < 100.0

        # 找到逻辑检查失败的结果
        logic_result = next((r for r in result.results if r.check_type == "logic_check"), None)
        assert logic_result is not None
        assert logic_result.passed is False

    def test_business_rule_validation_extreme_price(self):
        """测试业务规则验证 (极端价格 > 20%)"""
        validator = DataQualityValidator()

        # 创建极端价格波动数据
        data = pd.DataFrame(
            {
                "open": [10.0, 10.0, 12.5],  # 25% 涨幅
                "high": [11.0, 11.0, 13.0],
                "low": [9.0, 9.0, 12.0],
                "close": [10.0, 10.0, 12.5],
                "volume": [1000, 1000, 5000],  # 异常成交量
            }
        )

        result = validator.validate(data, data_source="test")

        # 业务规则应该检测到极端价格
        business_result = next((r for r in result.results if r.check_type == "business_check"), None)
        assert business_result is not None
        assert "Extreme price change" in business_result.message

    def test_business_rule_validation_abnormal_volume(self):
        """测试业务规则验证 (异常成交量 > 10 倍均值)"""
        validator = DataQualityValidator()

        # 创建异常成交量数据
        data = pd.DataFrame(
            {
                "open": [10.0, 10.0, 10.0],
                "high": [11.0, 11.0, 11.0],
                "low": [9.0, 9.0, 9.0],
                "close": [10.0, 10.0, 10.0],
                "volume": [1000, 1000, 15000],  # 15 倍均值
            }
        )

        result = validator.validate(data, data_source="test")

        # 业务规则应该检测到异常成交量
        business_result = next((r for r in result.results if r.check_type == "business_check"), None)
        assert business_result is not None
        assert "Abnormal volume" in business_result.message

    def test_business_rule_validation_suspended_stock(self):
        """测试业务规则验证 (停牌数据)"""
        validator = DataQualityValidator()

        # 创建停牌数据 (价格不变)
        data = pd.DataFrame(
            {
                "open": [10.0, 10.0, 10.0],
                "high": [10.0, 10.0, 10.0],
                "low": [10.0, 10.0, 10.0],
                "close": [10.0, 10.0, 10.0],
                "volume": [0, 0, 0],
            }
        )

        result = validator.validate(data, data_source="test")

        # 业务规则应该检测到停牌
        business_result = next((r for r in result.results if r.check_type == "business_check"), None)
        assert business_result is not None
        assert "Suspended stock" in business_result.message

    def test_business_rule_validation_zero_price(self):
        """测试业务规则验证 (零或负价格)"""
        validator = DataQualityValidator()

        # 创建零价格数据
        data = pd.DataFrame(
            {
                "open": [10.0, 0.0, 10.0],  # 零价格
                "high": [11.0, 0.0, 11.0],
                "low": [9.0, 0.0, 9.0],
                "close": [10.0, 0.0, 10.0],
            }
        )

        result = validator.validate(data, data_source="test")

        # 业务规则应该检测到零价格
        business_result = next((r for r in result.results if r.check_type == "business_check"), None)
        assert business_result is not None
        assert business_result.passed is False
        assert "Zero or negative price" in business_result.message

    def test_statistical_outlier_detection(self):
        """测试统计异常检测 (3-sigma)"""
        validator = DataQualityValidator()

        # 创建包含离群值的数据
        data = pd.DataFrame(
            {
                "open": [10.0, 10.0, 10.0, 10.0, 10.0, 100.0],  # 最后一个是离群值
                "high": [11.0, 11.0, 11.0, 11.0, 11.0, 110.0],
                "low": [9.0, 9.0, 9.0, 9.0, 9.0, 90.0],
                "close": [10.0, 10.0, 10.0, 10.0, 10.0, 100.0],
                "volume": [1000, 1000, 1000, 1000, 1000, 1000],
            }
        )

        result = validator.validate(data, data_source="test")

        # 统计检查应该检测到离群值
        stat_result = next((r for r in result.results if r.check_type == "statistical_check"), None)
        assert stat_result is not None
        assert "outliers" in stat_result.message.lower()

    def test_cross_source_validation(self):
        """测试跨源验证 (一致性检查)"""
        validator = DataQualityValidator(enable_cross_source_check=True)

        # 创建两个数据集
        data1 = pd.DataFrame(
            {
                "open": [10.0, 11.0, 12.0],
                "high": [11.0, 12.0, 13.0],
                "low": [9.0, 10.0, 11.0],
                "close": [10.0, 11.0, 12.0],
                "volume": [1000, 2000, 3000],
            }
        )

        # 数据2: 价格稍有差异 (<1%)
        data2 = pd.DataFrame(
            {
                "open": [10.05, 11.05, 12.05],
                "high": [11.05, 12.05, 13.05],
                "low": [9.05, 10.05, 11.05],
                "close": [10.05, 11.05, 12.05],
                "volume": [1050, 2100, 3150],
            }
        )

        result = validator.validate(data1, data_source="source1", reference_data=data2)

        # 跨源验证应该通过 (差异 < 1%)
        cross_source_result = next((r for r in result.results if r.check_type == "cross_source_check"), None)
        assert cross_source_result is not None
        assert cross_source_result.passed is True

    def test_cross_source_validation_failure(self):
        """测试跨源验证 (失败场景)"""
        validator = DataQualityValidator(enable_cross_source_check=True)

        # 创建两个数据集
        data1 = pd.DataFrame(
            {
                "open": [10.0, 11.0, 12.0],
                "high": [11.0, 12.0, 13.0],
                "low": [9.0, 10.0, 11.0],
                "close": [10.0, 11.0, 12.0],
                "volume": [1000, 2000, 3000],
            }
        )

        # 数据2: 价格差异很大 (>1%)
        data2 = pd.DataFrame(
            {
                "open": [11.0, 12.1, 13.2],  # 10% 差异
                "high": [12.1, 13.2, 14.3],
                "low": [9.9, 11.0, 12.1],
                "close": [11.0, 12.1, 13.2],
                "volume": [1000, 2000, 3000],
            }
        )

        result = validator.validate(data1, data_source="source1", reference_data=data2)

        # 跨源验证应该失败
        cross_source_result = next((r for r in result.results if r.check_type == "cross_source_check"), None)
        assert cross_source_result is not None
        assert cross_source_result.passed is False

    def test_validation_summary(self):
        """测试验证汇总"""
        validator = DataQualityValidator()

        # 创建有效数据
        data = pd.DataFrame(
            {
                "open": [10.0, 11.0, 12.0],
                "high": [11.0, 12.0, 13.0],
                "low": [9.0, 10.0, 11.0],
                "close": [10.5, 11.5, 12.5],
                "volume": [1000, 2000, 3000],
            }
        )

        result = validator.validate(data, data_source="test")

        # 验证汇总信息
        assert isinstance(result, ValidationSummary)
        assert result.passed is True
        assert result.total_checks > 0
        assert result.passed_checks > 0
        assert result.failed_checks == 0
        assert result.quality_score >= 0.0
        assert result.quality_score <= 100.0

    def test_quality_score_calculation(self):
        """测试质量评分计算"""
        validator = DataQualityValidator()

        # 创建有问题的数据
        data = pd.DataFrame(
            {
                "open": [10.0, 11.0, 12.0],
                "high": [9.0, 10.0, 11.0],  # High < Open (逻辑错误)
                "low": [9.0, 10.0, 11.0],
                "close": [10.5, 11.5, 12.5],
            }
        )

        result = validator.validate(data, data_source="test")

        # 质量评分应该降低
        assert result.quality_score < 100.0
        assert result.passed is False

    def test_enable_disable_checks(self):
        """测试启用/禁用检查"""
        # 只启用逻辑检查
        validator = DataQualityValidator(
            enable_logic_check=True,
            enable_business_check=False,
            enable_statistical_check=False,
            enable_cross_source_check=False,
        )

        data = pd.DataFrame(
            {
                "open": [10.0, 11.0, 12.0],
                "high": [11.0, 12.0, 13.0],
                "low": [9.0, 10.0, 11.0],
                "close": [10.5, 11.5, 12.5],
            }
        )

        result = validator.validate(data, data_source="test")

        # 应该只执行 1 个检查
        assert result.total_checks == 1

    def test_gpu_accelerated_validation(self):
        """测试 GPU 加速验证 (100,000 行数据)"""
        validator = DataQualityValidator()

        # 创建大数据集
        data = pd.DataFrame(
            {
                "open": np.random.uniform(10, 20, 100000),
                "high": np.random.uniform(20, 30, 100000),
                "low": np.random.uniform(5, 10, 100000),
                "close": np.random.uniform(10, 20, 100000),
                "volume": np.random.randint(1000, 10000, 100000),
            }
        )

        # 验证应该在大数据集上快速完成
        import time

        start_time = time.time()
        result = validator.validate(data, data_source="test")
        elapsed_time = time.time() - start_time

        # 应该在合理时间内完成 (< 5 秒)
        assert elapsed_time < 5.0
        assert isinstance(result, ValidationSummary)

    def test_dict_to_dataframe_conversion(self):
        """测试 dict 到 DataFrame 的转换"""
        validator = DataQualityValidator()

        # 使用 dict 输入
        data = {
            "open": [10.0, 11.0, 12.0],
            "high": [11.0, 12.0, 13.0],
            "low": [9.0, 10.0, 11.0],
            "close": [10.5, 11.5, 12.5],
            "volume": [1000, 2000, 3000],
        }

        result = validator.validate(data, data_source="test")

        # 应该成功处理
        assert isinstance(result, ValidationSummary)
        assert result.total_checks > 0

    def test_missing_columns(self):
        """测试缺少必需列"""
        validator = DataQualityValidator()

        # 缺少 'low' 列
        data = pd.DataFrame(
            {
                "open": [10.0, 11.0, 12.0],
                "high": [11.0, 12.0, 13.0],
                "close": [10.5, 11.5, 12.5],
            }
        )

        result = validator.validate(data, data_source="test")

        # 应该检测到缺失列
        assert result.passed is False
        logic_result = next((r for r in result.results if r.check_type == "logic_check"), None)
        assert logic_result is not None
        assert "Missing required columns" in logic_result.message
