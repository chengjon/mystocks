"""
趋势分析器 - 从 intelligent_threshold_manager.py 拆分
职责：趋势分析、方向检测、趋势优化
遵循 TDD 原则：仅实现满足测试的最小功能
"""

import logging
from typing import Any, Dict, List

import numpy as np

# 设置日志
logger = logging.getLogger(__name__)


class TrendAnalyzer:
    """趋势分析器 - 专注于趋势分析和阈值优化"""

    def __init__(self, window_size: int = 50):
        """
        初始化趋势分析器

        Args:
            window_size: 分析窗口大小
        """
        self.window_size = window_size
        self.logger = logging.getLogger(__name__)

    def optimize_threshold_trend(
        self, data: List[float], current_threshold: float, threshold_type: str = "upper"
    ) -> Dict[str, Any]:
        """
        基于趋势优化阈值

        Args:
            data: 数据值列表
            current_threshold: 当前阈值
            threshold_type: 阈值类型

        Returns:
            Dict[str, Any]: 优化结果
        """
        if len(data) < 10:
            return {
                "recommended_threshold": current_threshold,
                "confidence_score": 0.0,
                "trend_direction": "insufficient_data",
                "reasoning": "Insufficient data for trend analysis",
            }

        try:
            # 检测趋势方向和强度
            trend_direction = self._detect_trend_direction(data)
            trend_strength = self._calculate_trend_strength(data)

            # 基于趋势计算推荐阈值
            recommended_threshold = self._calculate_trend_based_threshold(
                data, current_threshold, trend_direction, threshold_type
            )

            # 计算置信度
            confidence = self._calculate_trend_confidence(data, trend_direction, trend_strength)

            # 预测效果
            predicted_effectiveness = self._predict_trend_effectiveness(
                data, current_threshold, recommended_threshold, trend_direction
            )

            return {
                "recommended_threshold": recommended_threshold,
                "current_threshold": current_threshold,
                "confidence_score": confidence,
                "trend_direction": trend_direction,
                "trend_strength": trend_strength,
                "predicted_effectiveness": predicted_effectiveness,
                "reasoning": self._generate_trend_reasoning(data, trend_direction, recommended_threshold),
                "data_size": len(data),
                "method": "trend_analysis",
            }

        except Exception as e:
            logger.error("Error in trend optimization: %s", str(e))
            return {
                "recommended_threshold": current_threshold,
                "confidence_score": 0.0,
                "reasoning": f"Trend analysis failed: {str(e)}",
                "method": "trend_analysis",
                "error": str(e),
            }

    def _detect_trend_direction(self, data: List[float]) -> str:
        """
        检测趋势方向

        Args:
            data: 数据值列表

        Returns:
            str: 趋势方向 ("upward", "downward", "stable")
        """
        if len(data) < 3:
            return "stable"

        # 使用简单的线性回归检测趋势
        x = np.arange(len(data))
        y = np.array(data)

        # 计算斜率
        n = len(data)
        x_mean = n / 2
        y_mean = np.mean(y)

        numerator = np.sum((x - x_mean) * (y - y_mean))
        denominator = np.sum((x - x_mean) ** 2)

        if denominator == 0:
            return "stable"

        slope = numerator / denominator

        # 判断趋势方向
        if abs(slope) < 1e-6:
            return "stable"
        elif slope > 0:
            return "upward"
        else:
            return "downward"

    def _calculate_trend_strength(self, data: List[float]) -> float:
        """
        计算趋势强度

        Args:
            data: 数据值列表

        Returns:
            float: 趋势强度 (0-1)
        """
        if len(data) < 3:
            return 0.0

        try:
            x = np.arange(len(data))
            y = np.array(data)

            # 线性回归
            slope, intercept = np.polyfit(x, y, 1)
            y_pred = slope * x + intercept

            # 计算R²
            ss_res = np.sum((y - y_pred) ** 2)
            ss_tot = np.sum((y - np.mean(y)) ** 2)

            if ss_tot == 0:
                return 0.0

            r_squared = 1 - (ss_res / ss_tot)

            # 趋势强度基于斜率和R²
            data_range = np.max(data) - np.min(data)
            slope_strength = abs(slope) / (data_range / len(data)) if data_range > 0 else 0

            return float(min(1.0, r_squared * slope_strength))

        except Exception:
            return 0.0

    def _calculate_trend_based_threshold(
        self,
        data: List[float],
        current_threshold: float,
        trend_direction: str,
        threshold_type: str,
    ) -> float:
        """
        基于趋势计算阈值

        Args:
            data: 数据值列表
            current_threshold: 当前阈值
            trend_direction: 趋势方向
            threshold_type: 阈值类型

        Returns:
            float: 推荐阈值
        """
        if trend_direction == "upward":
            # 上升趋势：调整阈值向上
            trend_factor = 1.1
        elif trend_direction == "downward":
            # 下降趋势：调整阈值向下
            trend_factor = 0.9
        else:
            # 稳定趋势：保持当前阈值
            trend_factor = 1.0

        # 应用趋势因子，但要考虑趋势强度
        trend_strength = self._calculate_trend_strength(data)
        adjustment_factor = 1 + (trend_factor - 1) * trend_strength

        return current_threshold * adjustment_factor

    def _calculate_trend_confidence(self, data: List[float], trend_direction: str, trend_strength: float) -> float:
        """
        计算趋势分析置信度

        Args:
            data: 数据值列表
            trend_direction: 趋势方向
            trend_strength: 趋势强度

        Returns:
            float: 置信度分数 (0-1)
        """
        # 数据量影响置信度
        data_size_score = min(1.0, len(data) / 50)

        # 趋势强度影响置信度
        strength_score = trend_strength

        # 趋势稳定性（方向一致性）
        stability_score = self._calculate_trend_stability(data)

        # 综合置信度
        confidence = data_size_score * 0.3 + strength_score * 0.4 + stability_score * 0.3

        return float(min(1.0, max(0.0, confidence)))

    def _calculate_trend_stability(self, data: List[float]) -> float:
        """
        计算趋势稳定性

        Args:
            data: 数据值列表

        Returns:
            float: 稳定性分数 (0-1)
        """
        if len(data) < 10:
            return 0.0

        try:
            # 将数据分成两半，比较趋势方向
            mid = len(data) // 2
            first_half = data[:mid]
            second_half = data[mid:]

            first_trend = self._detect_trend_direction(first_half)
            second_trend = self._detect_trend_direction(second_half)

            # 趋势方向相同则稳定
            if first_trend == second_trend and first_trend != "stable":
                return 0.8
            elif first_trend == "stable" and second_trend != "stable":
                return 0.6
            else:
                return 0.3

        except Exception:
            return 0.0

    def _predict_trend_effectiveness(
        self,
        data: List[float],
        current_threshold: float,
        new_threshold: float,
        trend_direction: str,
    ) -> float:
        """
        预测趋势优化效果

        Args:
            data: 数据值列表
            current_threshold: 当前阈值
            new_threshold: 新阈值
            trend_direction: 趋势方向

        Returns:
            float: 预测效果 (0-1)
        """
        if len(data) == 0:
            return 0.0

        np.array(data)

        # 根据趋势方向评估调整的合理性
        if trend_direction == "upward" and new_threshold > current_threshold:
            return 0.8  # 向上趋势提高阈值是合理的
        elif trend_direction == "downward" and new_threshold < current_threshold:
            return 0.8  # 向下趋势降低阈值是合理的
        elif trend_direction == "stable":
            return 0.5  # 稳定趋势调整效果中等
        else:
            return 0.2  # 调整方向与趋势不符

    def _generate_trend_reasoning(self, data: List[float], trend_direction: str, recommended_threshold: float) -> str:
        """
        生成趋势推理说明

        Args:
            data: 数据值列表
            trend_direction: 趋势方向
            recommended_threshold: 推荐阈值

        Returns:
            str: 推理说明
        """
        np.array(data)
        trend_strength = self._calculate_trend_strength(data)

        if trend_direction == "upward":
            return (
                f"Upward trend detected (strength: {trend_strength:.2f}). "
                f"Adjusting threshold upward to {recommended_threshold:.2f} "
                f"to accommodate increasing values."
            )
        elif trend_direction == "downward":
            return (
                f"Downward trend detected (strength: {trend_strength:.2f}). "
                f"Adjusting threshold downward to {recommended_threshold:.2f} "
                f"to maintain sensitivity with decreasing values."
            )
        else:
            return (
                f"Stable trend detected (strength: {trend_strength:.2f}). "
                f"Maintaining threshold at {recommended_threshold:.2f} "
                f"as no significant directional change observed."
            )

    def forecast_trend(self, data: List[float], steps: int = 5) -> List[float]:
        """
        预测趋势

        Args:
            data: 历史数据
            steps: 预测步数

        Returns:
            List[float]: 预测值
        """
        if len(data) < 3:
            return [data[-1]] * steps if data else [0.0] * steps

        try:
            # 简单线性预测
            x = np.arange(len(data))
            y = np.array(data)

            # 计算斜率和截距
            slope, intercept = np.polyfit(x, y, 1)

            # 预测未来值
            future_x = np.arange(len(data), len(data) + steps)
            future_y = slope * future_x + intercept

            return [float(val) for val in future_y]

        except Exception:
            # 预测失败时返回最后一个值
            last_value = data[-1] if data else 0.0
            return [last_value] * steps

    def get_trend_summary(self, data: List[float]) -> Dict[str, Any]:
        """
        获取趋势摘要

        Args:
            data: 数据值列表

        Returns:
            Dict[str, Any]: 趋势摘要
        """
        if len(data) < 3:
            return {
                "direction": "insufficient_data",
                "strength": 0.0,
                "slope": 0.0,
                "mean": 0.0,
                "std": 0.0,
                "range": 0.0,
            }

        data_array = np.array(data)
        trend_direction = self._detect_trend_direction(data)
        trend_strength = self._calculate_trend_strength(data)

        # 计算斜率
        x = np.arange(len(data))
        slope, _ = np.polyfit(x, data_array, 1)

        return {
            "direction": trend_direction,
            "strength": trend_strength,
            "slope": float(slope),
            "mean": float(np.mean(data_array)),
            "std": float(np.std(data_array)),
            "range": float(np.max(data_array) - np.min(data_array)),
            "data_points": len(data),
        }
