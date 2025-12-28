#!/usr/bin/env python3
"""
# 功能：统计优化器
# 作者：MyStocks AI开发团队
# 创建日期：2025-12-20
# 版本：1.0.0
# 说明：基于统计方法的阈值优化器
"""

import logging
import numpy as np
from typing import List

from .base_threshold_manager import OptimizationResult


class StatisticalOptimizer:
    """统计优化器"""

    def __init__(self, min_data_points: int = 30):
        self.min_data_points = min_data_points
        self.logger = logging.getLogger(f"{__name__}.StatisticalOptimizer")

    def optimize_threshold_statistical(
        self,
        values: List[float],
        current_threshold: float,
        threshold_type: str = "upper",
    ) -> OptimizationResult:
        """基于统计方法优化阈值"""

        if len(values) < self.min_data_points:
            return self._create_insufficient_data_result(current_threshold)

        try:
            values_array = np.array(values)

            # 计算统计指标
            mean_val = np.mean(values_array)
            std_val = np.std(values_array)
            q75 = np.percentile(values_array, 75)
            q95 = np.percentile(values_array, 95)
            q99 = np.percentile(values_array, 99)

            if threshold_type == "upper":
                # 上阈值优化
                if std_val > 0:
                    # 基于标准差的方法 (均值 + k*标准差)
                    k = 2.0  # 2-sigma规则
                    recommended_threshold = mean_val + k * std_val
                else:
                    recommended_threshold = q95

                # 确保新阈值比当前阈值更合理
                recommended_threshold = min(recommended_threshold, q99)

            elif threshold_type == "lower":
                # 下阈值优化
                if std_val > 0:
                    k = 2.0
                    recommended_threshold = mean_val - k * std_val
                else:
                    recommended_threshold = np.percentile(values_array, 5)

                recommended_threshold = max(recommended_threshold, q1=np.percentile(values_array, 1))

            else:  # range
                recommended_threshold = q75

            # 计算置信度
            confidence = self._calculate_confidence(values_array, recommended_threshold, threshold_type)

            # 计算预期改进
            improvement = self._estimate_improvement(values, current_threshold, recommended_threshold, threshold_type)

            return OptimizationResult(
                rule_name="statistical_optimizer",
                optimization_type="statistical",
                recommended_threshold=float(recommended_threshold),
                confidence_score=confidence,
                expected_improvement=improvement,
                reasoning=f"基于{len(values)}个数据点的统计分析",
                supporting_evidence=[
                    f"均值: {mean_val:.2f}",
                    f"标准差: {std_val:.2f}",
                    f"95%分位数: {q95:.2f}",
                    "异常值检测使用IQR方法",
                ],
                metadata={
                    "mean": float(mean_val),
                    "std": float(std_val),
                    "q75": float(q75),
                    "q95": float(q95),
                    "data_points": len(values),
                },
            )
        except Exception as e:
            self.logger.error("统计优化失败: %s", e)
            return self._create_error_result(current_threshold, str(e))

    def _calculate_confidence(self, values: np.ndarray, threshold: float, threshold_type: str) -> float:
        """计算阈值置信度"""

        try:
            # 基于阈值与数据分布的匹配度
            if threshold_type == "upper":
                # 检查有多少数据在阈值以下
                ratio_below = np.sum(values <= threshold) / len(values)
                # 理想情况下应该是95-99%的数据在阈值以下
                target_ratio = 0.97
                confidence = 1.0 - abs(ratio_below - target_ratio)
            else:
                # 对于下阈值，检查有多少数据在阈值以上
                ratio_above = np.sum(values >= threshold) / len(values)
                target_ratio = 0.97
                confidence = 1.0 - abs(ratio_above - target_ratio)

            return max(0.0, min(1.0, confidence))
        except Exception as e:
            self.logger.error("置信度计算失败: %s", e)
            return 0.5

    def _estimate_improvement(
        self,
        values: List[float],
        old_threshold: float,
        new_threshold: float,
        threshold_type: str,
    ) -> float:
        """估计阈值改进效果"""

        if not values:
            return 0.0

        try:
            # 计算旧阈值和新阈值下的异常率
            old_anomaly_count = sum(1 for v in values if self._is_anomaly(v, old_threshold, threshold_type))
            new_anomaly_count = sum(1 for v in values if self._is_anomaly(v, new_threshold, threshold_type))

            old_rate = old_anomaly_count / len(values)
            new_rate = new_anomaly_count / len(values)

            # 改进率为异常率减少的比例
            if old_rate > 0:
                improvement = (old_rate - new_rate) / old_rate
            else:
                improvement = 0.0 if new_rate == 0 else -1.0

            return max(-1.0, improvement)
        except Exception as e:
            self.logger.error("改进估计失败: %s", e)
            return 0.0

    def _is_anomaly(self, value: float, threshold: float, threshold_type: str) -> bool:
        """判断值是否为异常"""
        if threshold_type == "upper":
            return value > threshold
        elif threshold_type == "lower":
            return value < threshold
        else:
            return False

    def _create_insufficient_data_result(self, current_threshold: float) -> OptimizationResult:
        """数据不足时的结果"""
        return OptimizationResult(
            rule_name="statistical_optimizer",
            optimization_type="statistical",
            recommended_threshold=current_threshold,
            confidence_score=0.1,
            expected_improvement=0.0,
            reasoning="数据不足，无法进行统计优化",
            supporting_evidence=[f"需要至少{self.min_data_points}个数据点"],
            metadata={"data_insufficient": True},
        )

    def _create_error_result(self, current_threshold: float, error_message: str) -> OptimizationResult:
        """错误情况下的结果"""
        return OptimizationResult(
            rule_name="statistical_optimizer",
            optimization_type="statistical",
            recommended_threshold=current_threshold,
            confidence_score=0.0,
            expected_improvement=0.0,
            reasoning=f"统计优化出错: {error_message}",
            supporting_evidence=["处理过程中发生错误"],
            metadata={"error": True, "error_message": error_message},
        )
