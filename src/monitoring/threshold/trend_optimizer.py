#!/usr/bin/env python3
"""
# 功能：趋势优化器
# 作者：MyStocks AI开发团队
# 创建日期：2025-12-20
# 版本：1.0.0
# 说明：基于趋势分析的阈值优化器
"""

import logging
from datetime import datetime
from typing import List

import numpy as np

from .base_threshold_manager import OptimizationResult


class TrendOptimizer:
    """趋势分析优化器"""

    def __init__(self, min_data_points: int = 10):
        self.min_data_points = min_data_points
        self.logger = logging.getLogger(f"{__name__}.TrendOptimizer")

    def optimize_threshold_trend(
        self,
        values: List[float],
        timestamps: List[datetime],
        current_threshold: float,
        threshold_type: str = "upper",
    ) -> OptimizationResult:
        """基于趋势分析优化阈值"""

        if len(values) < self.min_data_points:
            return OptimizationResult(
                rule_name="trend_optimizer",
                optimization_type="trend_analysis",
                recommended_threshold=current_threshold,
                confidence_score=0.1,
                expected_improvement=0.0,
                reasoning="数据点不足，无法进行趋势分析",
                supporting_evidence=[f"需要至少{self.min_data_points}个数据点"],
                metadata={"insufficient_data": True},
            )

        try:
            # 转换时间戳为数值
            time_values = [(t - timestamps[0]).total_seconds() for t in timestamps]

            # 计算线性趋势
            slope, intercept = np.polyfit(time_values, values, 1)

            # 计算趋势强度
            correlation = np.corrcoef(time_values, values)[0, 1] if len(values) > 2 else 0

            # 预测未来值
            last_time = time_values[-1]
            future_time = last_time + 3600  # 预测1小时后
            predicted_value = slope * future_time + intercept

            # 根据趋势调整阈值
            if threshold_type == "upper":
                if slope > 0:  # 上升趋势
                    adjustment_factor = 1.1  # 增加10%
                else:  # 下降趋势
                    adjustment_factor = 0.95  # 减少5%
            else:  # lower
                if slope < 0:  # 下降趋势
                    adjustment_factor = 0.9  # 减少10%
                else:  # 上升趋势
                    adjustment_factor = 1.05  # 增加5%

            recommended_threshold = current_threshold * adjustment_factor

            # 计算置信度
            confidence = min(1.0, abs(correlation))

            # 估计改进
            improvement = abs(slope) * correlation if correlation > 0.5 else 0.0

            return OptimizationResult(
                rule_name="trend_optimizer",
                optimization_type="trend_analysis",
                recommended_threshold=recommended_threshold,
                confidence_score=confidence,
                expected_improvement=improvement,
                reasoning=f"基于趋势分析: {slope:.4f}/秒的变化率, 相关性: {correlation:.3f}",
                supporting_evidence=[
                    f"趋势斜率: {slope:.6f}",
                    f"相关系数: {correlation:.3f}",
                    f"预测值: {predicted_value:.2f}",
                    f"调整因子: {adjustment_factor:.2f}",
                ],
                metadata={
                    "slope": slope,
                    "correlation": correlation,
                    "predicted_value": predicted_value,
                    "adjustment_factor": adjustment_factor,
                    "data_points": len(values),
                },
            )
        except Exception as e:
            self.logger.error("趋势优化失败: %s", e)
            return OptimizationResult(
                rule_name="trend_optimizer",
                optimization_type="trend_analysis",
                recommended_threshold=current_threshold,
                confidence_score=0.0,
                expected_improvement=0.0,
                reasoning=f"趋势分析出错: {str(e)}",
                supporting_evidence=["处理过程中发生错误"],
                metadata={"error": True, "error_message": str(e)},
            )

    def detect_seasonal_patterns(self, values: List[float], timestamps: List[datetime]) -> dict:
        """检测季节性模式"""
        if len(values) < 24:  # 需要足够的数据点
            return {"has_seasonality": False, "period": None, "strength": 0}

        try:
            # 简单的季节性检测：基于自相关
            values_array = np.array(values)

            # 计算不同滞后期的自相关
            max_lag = min(len(values) // 2, 48)  # 最大滞后期
            autocorr = []

            for lag in range(1, max_lag + 1):
                if len(values_array) > lag:
                    corr = np.corrcoef(values_array[:-lag], values_array[lag:])[0, 1]
                    if not np.isnan(corr):
                        autocorr.append(abs(corr))
                    else:
                        autocorr.append(0)
                else:
                    autocorr.append(0)

            # 找到最强的周期性
            if autocorr:
                max_corr_idx = np.argmax(autocorr)
                max_corr = autocorr[max_corr_idx]

                # 周期性强度
                strength = max_corr

                # 如果自相关性足够强，认为存在季节性
                has_seasonality = strength > 0.3
                period = max_corr_idx + 1 if has_seasonality else None
            else:
                has_seasonality = False
                period = None
                strength = 0

            return {
                "has_seasonality": has_seasonality,
                "period": period,
                "strength": strength,
                "autocorr_max": max(autocorr) if autocorr else 0,
            }
        except Exception as e:
            self.logger.error("季节性检测失败: %s", e)
            return {"has_seasonality": False, "period": None, "strength": 0}

    def calculate_trend_strength(self, values: List[float]) -> float:
        """计算趋势强度"""
        if len(values) < 3:
            return 0.0

        try:
            values_array = np.array(values)
            x = np.arange(len(values_array))

            # 线性拟合
            slope, intercept = np.polyfit(x, values_array, 1)

            # 计算R²
            y_pred = slope * x + intercept
            ss_res = np.sum((values_array - y_pred) ** 2)
            ss_tot = np.sum((values_array - np.mean(values_array)) ** 2)

            if ss_tot == 0:
                return 0.0

            r_squared = 1 - (ss_res / ss_tot)

            # 趋势强度为R²的绝对值
            return abs(r_squared)
        except Exception as e:
            self.logger.error("趋势强度计算失败: %s", e)
            return 0.0

    def detect_change_points(self, values: List[float]) -> List[int]:
        """检测变化点"""
        if len(values) < 10:
            return []

        try:
            values_array = np.array(values)
            change_points = []

            # 使用简单的滑动窗口方法检测变化点
            window_size = min(10, len(values) // 4)

            for i in range(window_size, len(values) - window_size):
                # 前后窗口的均值
                before_window = values_array[i - window_size : i]
                after_window = values_array[i : i + window_size]

                before_mean = np.mean(before_window)
                after_mean = np.mean(after_window)

                # 检测显著的均值变化
                overall_std = np.std(values_array)
                if overall_std > 0:
                    change_magnitude = abs(after_mean - before_mean) / overall_std

                    # 如果变化幅度超过2个标准差，认为是变化点
                    if change_magnitude > 2.0:
                        change_points.append(i)

            return change_points
        except Exception as e:
            self.logger.error("变化点检测失败: %s", e)
            return []
