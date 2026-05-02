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


def _build_valid_ohlcv_frame(
    length: int = 5,
    *,
    base_price: float = 10.0,
    step: float = 0.05,
    volume: int = 1000,
) -> pd.DataFrame:
    close = [base_price + step * index for index in range(length)]
    return pd.DataFrame(
        {
            "open": [value - 0.05 for value in close],
            "high": [value + 0.20 for value in close],
            "low": [value - 0.20 for value in close],
            "close": close,
            "volume": [volume] * length,
        }
    )


def _build_abnormal_volume_frame(seed: int) -> pd.DataFrame:
    frame = _build_valid_ohlcv_frame(length=13, base_price=10.0 + seed * 0.01)
    frame["volume"] = [1000] * 12 + [200000 + seed * 1000]
    return frame


def _build_suspended_frame(seed: int) -> pd.DataFrame:
    price = 10.0 + seed * 0.01
    return pd.DataFrame(
        {
            "open": [price] * 5,
            "high": [price] * 5,
            "low": [price] * 5,
            "close": [price] * 5,
            "volume": [0] * 5,
        }
    )


def _build_anomaly_scenarios():
    scenarios = []

    for index in range(15):
        frame = _build_valid_ohlcv_frame(base_price=10.0 + index * 0.1)
        frame.loc[1, "high"] = frame.loc[1, "low"] - 0.05
        scenarios.append(
            pytest.param(
                frame,
                None,
                {},
                "logic_check",
                "High < Low detected",
                False,
                id=f"logic-high-below-low-{index:02d}",
            )
        )

    for index in range(15):
        frame = _build_valid_ohlcv_frame(base_price=12.0 + index * 0.1)
        frame.loc[2, "close"] = frame.loc[2, "high"] + 0.30
        scenarios.append(
            pytest.param(
                frame,
                None,
                {},
                "logic_check",
                "Close outside [Low, High] range",
                False,
                id=f"logic-close-out-of-range-{index:02d}",
            )
        )

    for index in range(10):
        frame = _build_valid_ohlcv_frame(base_price=14.0 + index * 0.1)
        frame.loc[0, "volume"] = -(index + 1)
        scenarios.append(
            pytest.param(
                frame,
                None,
                {},
                "logic_check",
                "Negative volume detected",
                False,
                id=f"logic-negative-volume-{index:02d}",
            )
        )

    for index in range(10):
        frame = _build_valid_ohlcv_frame(base_price=16.0 + index * 0.1)
        frame.loc[1, ["open", "high", "low", "close"]] = [0.05, 0.10, 0.0, 0.0]
        scenarios.append(
            pytest.param(
                frame,
                None,
                {},
                "business_check",
                "Zero or negative price detected",
                False,
                id=f"business-zero-price-{index:02d}",
            )
        )

    for index in range(15):
        frame = _build_valid_ohlcv_frame(length=4, base_price=18.0 + index * 0.1)
        frame.loc[3, "close"] = frame.loc[2, "close"] * 1.25
        frame.loc[3, "open"] = frame.loc[3, "close"] - 0.05
        frame.loc[3, "high"] = frame.loc[3, "close"] + 0.20
        frame.loc[3, "low"] = frame.loc[3, "close"] - 0.20
        scenarios.append(
            pytest.param(
                frame,
                None,
                {},
                "business_check",
                "Extreme price change detected",
                True,
                id=f"business-extreme-price-{index:02d}",
            )
        )

    for index in range(15):
        scenarios.append(
            pytest.param(
                _build_abnormal_volume_frame(index),
                None,
                {},
                "business_check",
                "Abnormal volume detected",
                True,
                id=f"business-abnormal-volume-{index:02d}",
            )
        )

    for index in range(10):
        scenarios.append(
            pytest.param(
                _build_suspended_frame(index),
                None,
                {},
                "business_check",
                "Suspended stock detected",
                True,
                id=f"business-suspended-stock-{index:02d}",
            )
        )

    for index in range(15):
        frame = _build_valid_ohlcv_frame(length=31, base_price=20.0 + index * 0.1)
        frame.loc[30, ["open", "high", "low", "close"]] = [1000.0, 1000.5, 999.5, 1000.0]
        scenarios.append(
            pytest.param(
                frame,
                None,
                {},
                "statistical_check",
                "Statistical outliers detected",
                True,
                id=f"statistical-outlier-{index:02d}",
            )
        )

    for index in range(15):
        data = _build_valid_ohlcv_frame(base_price=22.0 + index * 0.1)
        reference = data.copy()
        reference["close"] = reference["close"] * 1.03
        scenarios.append(
            pytest.param(
                data,
                reference,
                {"enable_cross_source_check": True},
                "cross_source_check",
                "Cross-source check failed",
                False,
                id=f"cross-source-price-drift-{index:02d}",
            )
        )

    return scenarios


ANOMALY_SCENARIOS = _build_anomaly_scenarios()


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

        # 创建异常成交量数据:
        # 使用多条正常成交量 + 一条极端放量，确保最后一条记录仍然 > 10 倍均值。
        normal_close = [10.0 + index * 0.01 for index in range(12)]
        abnormal_close = normal_close + [10.2]
        abnormal_volume = [1000] * 12 + [200000]

        data = pd.DataFrame(
            {
                "open": abnormal_close,
                "high": [value + 0.2 for value in abnormal_close],
                "low": [value - 0.2 for value in abnormal_close],
                "close": abnormal_close,
                "volume": abnormal_volume,
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

    def test_anomaly_scenario_matrix_has_100_plus_cases(self):
        """测试异常场景矩阵已覆盖 100+ 用例数据"""
        assert len(ANOMALY_SCENARIOS) >= 100


@pytest.mark.parametrize(
    "data, reference_data, validator_kwargs, expected_check_type, expected_message, expected_passed",
    ANOMALY_SCENARIOS,
)
def test_anomaly_scenario_matrix_covers_100_plus_cases(
    data,
    reference_data,
    validator_kwargs,
    expected_check_type,
    expected_message,
    expected_passed,
):
    """测试 100+ 异常场景矩阵的预期结果"""
    validator = DataQualityValidator(**validator_kwargs)

    result = validator.validate(data, data_source="matrix_case", reference_data=reference_data)

    matched_result = next((item for item in result.results if item.check_type == expected_check_type), None)
    assert matched_result is not None
    assert expected_message in matched_result.message
    assert matched_result.passed is expected_passed
