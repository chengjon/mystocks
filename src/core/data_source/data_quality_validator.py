"""
数据质量验证器模块 (DataQualityValidator)

实现多层次的数据质量验证，包括基础逻辑、业务规则、统计异常和跨源验证。
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """验证结果"""

    passed: bool
    message: str
    check_type: str
    details: Optional[Dict[str, Any]] = None


@dataclass
class ValidationSummary:
    """验证汇总"""

    passed: bool
    total_checks: int
    passed_checks: int
    failed_checks: int
    results: List[ValidationResult]
    quality_score: float  # 0-100


class DataQualityValidator:
    """
    数据质量验证器

    特性:
    - 基础逻辑验证 (OHLC 逻辑)
    - 业务规则验证 (极端价格、异常成交量)
    - 统计异常检测 (3-sigma)
    - 跨源验证 (一致性检查)
    """

    def __init__(
        self,
        enable_logic_check: bool = True,
        enable_business_check: bool = True,
        enable_statistical_check: bool = True,
        enable_cross_source_check: bool = False,  # 默认禁用 (需要多个数据源)
    ):
        """
        初始化数据质量验证器

        Args:
            enable_logic_check: 启用基础逻辑验证
            enable_business_check: 启用业务规则验证
            enable_statistical_check: 启用统计异常检测
            enable_cross_source_check: 启用跨源验证
        """
        self.enable_logic_check = enable_logic_check
        self.enable_business_check = enable_business_check
        self.enable_statistical_check = enable_statistical_check
        self.enable_cross_source_check = enable_cross_source_check

        logger.info(
            f"DataQualityValidator initialized: "
            f"logic={enable_logic_check}, business={enable_business_check}, "
            f"statistical={enable_statistical_check}, cross_source={enable_cross_source_check}"
        )

    def validate(
        self,
        data: Any,
        data_source: str = "unknown",
        reference_data: Optional[Any] = None,
    ) -> ValidationSummary:
        """
        执行完整的数据质量验证

        Args:
            data: 待验证的数据 (DataFrame 或 dict)
            data_source: 数据源名称
            reference_data: 参考数据 (用于跨源验证)

        Returns:
            验证汇总结果
        """
        results = []

        # 1. 基础逻辑验证
        if self.enable_logic_check:
            result = self._logic_check(data)
            results.append(result)

        # 2. 业务规则验证
        if self.enable_business_check:
            result = self._business_check(data)
            results.append(result)

        # 3. 统计异常检测
        if self.enable_statistical_check:
            result = self._statistical_check(data)
            results.append(result)

        # 4. 跨源验证
        if self.enable_cross_source_check and reference_data is not None:
            result = self._cross_source_check(data, reference_data)
            results.append(result)

        # 计算汇总
        passed_checks = sum(1 for r in results if r.passed)
        total_checks = len(results)
        failed_checks = total_checks - passed_checks
        all_passed = all(r.passed for r in results)

        # 计算质量评分 (0-100)
        quality_score = self._calculate_quality_score(results)

        summary = ValidationSummary(
            passed=all_passed,
            total_checks=total_checks,
            passed_checks=passed_checks,
            failed_checks=failed_checks,
            results=results,
            quality_score=quality_score,
        )

        log_message = (
            f"Data validation summary for '{data_source}': "
            f"{passed_checks}/{total_checks} checks passed, "
            f"quality_score={quality_score:.1f}"
        )

        if all_passed:
            logger.info(log_message)
        else:
            logger.warning(log_message)

        return summary

    def _logic_check(self, data: Any) -> ValidationResult:
        """
        基础逻辑验证 (OHLC)

        检查:
        - High >= Low
        - Close 在 [Low, High] 范围内
        - Open 在 [Low, High] 范围内
        - Volume >= 0

        Args:
            data: 待验证的数据

        Returns:
            验证结果
        """
        issues = []

        try:
            # 尝试转换为 DataFrame
            if not hasattr(data, "shape"):
                # 如果是 dict 或其他格式，尝试转换
                import pandas as pd

                data = pd.DataFrame(data)

            # 检查必需列
            required_cols = ["open", "high", "low", "close"]
            missing_cols = [col for col in required_cols if col not in data.columns]
            if missing_cols:
                return ValidationResult(
                    passed=False,
                    message=f"Missing required columns: {missing_cols}",
                    check_type="logic_check",
                )

            # OHLC 逻辑检查
            high_low_valid = (data["high"] >= data["low"]).all()
            close_valid = ((data["close"] >= data["low"]) & (data["close"] <= data["high"])).all()
            open_valid = ((data["open"] >= data["low"]) & (data["open"] <= data["high"])).all()

            # 成交量检查 (如果存在)
            volume_valid = True
            if "volume" in data.columns:
                volume_valid = (data["volume"] >= 0).all()

            # 收集问题
            if not high_low_valid:
                issues.append("High < Low detected")
            if not close_valid:
                issues.append("Close outside [Low, High] range")
            if not open_valid:
                issues.append("Open outside [Low, High] range")
            if not volume_valid:
                issues.append("Negative volume detected")

            if issues:
                return ValidationResult(
                    passed=False,
                    message=f"OHLC logic check failed: {', '.join(issues)}",
                    check_type="logic_check",
                    details={"issues": issues},
                )
            else:
                return ValidationResult(
                    passed=True,
                    message="OHLC logic check passed",
                    check_type="logic_check",
                )

        except Exception as e:
            return ValidationResult(
                passed=False,
                message=f"Logic check error: {str(e)}",
                check_type="logic_check",
            )

    def _business_check(self, data: Any) -> ValidationResult:
        """
        业务规则验证

        检查:
        - 极端价格波动 (>20%)
        - 异常成交量 (>10 倍均值)
        - 停牌数据 (价格不变)
        - 零或负价格

        Args:
            data: 待验证的数据

        Returns:
            验证结果
        """
        issues = []
        warnings = []

        try:
            import pandas as pd

            if not hasattr(data, "shape"):
                data = pd.DataFrame(data)

            # 1. 零或负价格检查
            if "close" in data.columns:
                zero_price = (data["close"] <= 0).sum()
                if zero_price > 0:
                    issues.append(f"Zero or negative price detected ({zero_price} rows)")

            # 2. 极端价格波动检查 (>20%)
            if "close" in data.columns and len(data) > 1:
                data_sorted = data.sort_index()
                price_change = data_sorted["close"].pct_change().abs()
                extreme_change = price_change > 0.20  # 20% 阈值
                extreme_count = extreme_change.sum()

                if extreme_count > 0:
                    warnings.append(f"Extreme price change detected ({extreme_count} rows > 20%)")

            # 3. 异常成交量检查 (>10 倍均值)
            if "volume" in data.columns:
                mean_volume = data["volume"].mean()
                if mean_volume > 0:
                    abnormal_volume = data["volume"] > (10 * mean_volume)
                    abnormal_count = abnormal_volume.sum()

                    if abnormal_count > 0:
                        warnings.append(f"Abnormal volume detected ({abnormal_count} rows > 10x mean)")

            # 4. 停牌数据检查 (价格完全不变)
            if "close" in data.columns and len(data) > 1:
                data_sorted = data.sort_index()
                price_std = data_sorted["close"].std()

                if price_std == 0:
                    warnings.append("Suspended stock detected (zero price variation)")

            # 判断结果
            if issues:
                return ValidationResult(
                    passed=False,
                    message=f"Business rule check failed: {', '.join(issues)}",
                    check_type="business_check",
                    details={"issues": issues, "warnings": warnings},
                )
            elif warnings:
                return ValidationResult(
                    passed=True,
                    message=f"Business rule check passed with warnings: {', '.join(warnings)}",
                    check_type="business_check",
                    details={"warnings": warnings},
                )
            else:
                return ValidationResult(
                    passed=True,
                    message="Business rule check passed",
                    check_type="business_check",
                )

        except Exception as e:
            return ValidationResult(
                passed=False,
                message=f"Business check error: {str(e)}",
                check_type="business_check",
            )

    def _statistical_check(self, data: Any) -> ValidationResult:
        """
        统计异常检测 (3-sigma)

        检查:
        - 价格离群值 (3-sigma 规则)
        - 成交量离群值

        Args:
            data: 待验证的数据

        Returns:
            验证结果
        """
        outliers = []

        try:
            import pandas as pd

            if not hasattr(data, "shape"):
                data = pd.DataFrame(data)

            # 检查价格离群值
            price_cols = ["open", "high", "low", "close"]
            for col in price_cols:
                if col in data.columns:
                    mean = data[col].mean()
                    std = data[col].std()

                    if std > 0:
                        # 3-sigma 规则
                        lower_bound = mean - 3 * std
                        upper_bound = mean + 3 * std

                        outlier_mask = (data[col] < lower_bound) | (data[col] > upper_bound)
                        outlier_count = outlier_mask.sum()

                        if outlier_count > 0:
                            outliers.append(f"{col}: {outlier_count} outliers")

            # 检查成交量离群值
            if "volume" in data.columns:
                mean_volume = data["volume"].mean()
                std_volume = data["volume"].std()

                if std_volume > 0:
                    lower_bound = mean_volume - 3 * std_volume
                    upper_bound = mean_volume + 3 * std_volume

                    outlier_mask = (data["volume"] < lower_bound) | (data["volume"] > upper_bound)
                    outlier_count = outlier_mask.sum()

                    if outlier_count > 0:
                        outliers.append(f"volume: {outlier_count} outliers")

            if outliers:
                return ValidationResult(
                    passed=True,  # 统计异常不算失败，只是警告
                    message=f"Statistical outliers detected: {', '.join(outliers)}",
                    check_type="statistical_check",
                    details={"outliers": outliers},
                )
            else:
                return ValidationResult(
                    passed=True,
                    message="Statistical check passed (no outliers)",
                    check_type="statistical_check",
                )

        except Exception as e:
            return ValidationResult(
                passed=False,
                message=f"Statistical check error: {str(e)}",
                check_type="statistical_check",
            )

    def _cross_source_check(self, data: Any, reference_data: Any) -> ValidationResult:
        """
        跨源验证 (一致性检查)

        检查:
        - 价格差异 (<1%)
        - 成交量差异 (<5%)

        Args:
            data: 待验证的数据
            reference_data: 参考数据

        Returns:
            验证结果
        """
        try:
            import pandas as pd

            if not hasattr(data, "shape"):
                data = pd.DataFrame(data)

            if not hasattr(reference_data, "shape"):
                reference_data = pd.DataFrame(reference_data)

            # 对齐数据
            data_sorted = data.sort_index()
            reference_sorted = reference_data.sort_index()

            # 找到共同的索引
            common_index = data_sorted.index.intersection(reference_sorted.index)

            if len(common_index) == 0:
                return ValidationResult(
                    passed=False,
                    message="No common data points for cross-source validation",
                    check_type="cross_source_check",
                )

            # 检查收盘价差异
            if "close" in data.columns and "close" in reference_data.columns:
                data_close = data_sorted.loc[common_index, "close"]
                ref_close = reference_sorted.loc[common_index, "close"]

                # 计算相对差异
                price_diff = ((data_close - ref_close).abs() / ref_close).mean()

                # 检查成交量差异
                if "volume" in data.columns and "volume" in reference_data.columns:
                    data_volume = data_sorted.loc[common_index, "volume"]
                    ref_volume = reference_sorted.loc[common_index, "volume"]

                    # 避免除零
                    nonzero_volume = ref_volume > 0
                    if nonzero_volume.any():
                        volume_diff = (
                            (data_volume[nonzero_volume] - ref_volume[nonzero_volume]).abs()
                            / ref_volume[nonzero_volume]
                        ).mean()
                    else:
                        volume_diff = 0.0
                else:
                    volume_diff = 0.0

                # 判断结果
                if price_diff > 0.01:  # 1% 阈值
                    return ValidationResult(
                        passed=False,
                        message=f"Cross-source check failed: price diff {price_diff:.2%}",
                        check_type="cross_source_check",
                        details={"price_diff": price_diff, "volume_diff": volume_diff},
                    )
                elif volume_diff > 0.05:  # 5% 阈值
                    return ValidationResult(
                        passed=True,
                        message=f"Cross-source check passed with warnings: volume diff {volume_diff:.2%}",
                        check_type="cross_source_check",
                        details={"price_diff": price_diff, "volume_diff": volume_diff},
                    )
                else:
                    return ValidationResult(
                        passed=True,
                        message=f"Cross-source check passed: price diff {price_diff:.2%}, volume diff {volume_diff:.2%}",
                        check_type="cross_source_check",
                        details={"price_diff": price_diff, "volume_diff": volume_diff},
                    )
            else:
                return ValidationResult(
                    passed=False,
                    message="Missing 'close' column for cross-source validation",
                    check_type="cross_source_check",
                )

        except Exception as e:
            return ValidationResult(
                passed=False,
                message=f"Cross-source check error: {str(e)}",
                check_type="cross_source_check",
            )

    def _calculate_quality_score(self, results: List[ValidationResult]) -> float:
        """
        计算质量评分 (0-100)

        Args:
            results: 验证结果列表

        Returns:
            质量评分
        """
        if not results:
            return 0.0

        # 基础分数
        base_score = 100.0

        # 每个失败的检查扣分
        for result in results:
            if not result.passed:
                if result.check_type == "logic_check":
                    base_score -= 40.0  # 逻辑问题最严重
                elif result.check_type == "business_check":
                    base_score -= 30.0  # 业务规则次之
                elif result.check_type == "statistical_check":
                    base_score -= 10.0  # 统计异常较轻
                elif result.check_type == "cross_source_check":
                    base_score -= 20.0  # 跨源不一致中等

        return max(0.0, min(100.0, base_score))
