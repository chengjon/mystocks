"""
统计优化器 - 从 intelligent_threshold_manager.py 拆分
职责：统计阈值优化、置信度计算、数据分析
遵循 TDD 原则：仅实现满足测试的最小功能
"""

import logging
import numpy as np
from typing import Dict, List, Any

# 设置日志
logger = logging.getLogger(__name__)


class StatisticalOptimizer:
    """统计优化器 - 专注于统计方法阈值优化"""

    def __init__(self, min_data_points: int = 30):
        """
        初始化统计优化器

        Args:
            min_data_points: 最小数据点数量
        """
        self.min_data_points = min_data_points
        self.logger = logging.getLogger(__name__)

    def optimize_threshold_statistical(
        self, data: List[float], current_threshold: float, threshold_type: str = "upper"
    ) -> Dict[str, Any]:
        """
        统计阈值优化

        Args:
            data: 数据值列表
            current_threshold: 当前阈值
            threshold_type: 阈值类型 ("upper", "lower")

        Returns:
            Dict[str, Any]: 优化结果
        """
        if len(data) < self.min_data_points:
            return self._create_insufficient_data_result(
                data, current_threshold, threshold_type
            )

        try:
            # 基于统计数据计算建议阈值
            recommended_threshold = self._calculate_statistical_threshold(
                data, threshold_type
            )

            # 计算置信度
            confidence = self._calculate_confidence(
                data, recommended_threshold, threshold_type
            )

            # 估算改善效果
            improvement = self._estimate_improvement(
                data, current_threshold, recommended_threshold, threshold_type
            )

            # 生成推理说明
            reasoning = self._generate_statistical_reasoning(
                data, recommended_threshold, threshold_type
            )

            return {
                "recommended_threshold": recommended_threshold,
                "current_threshold": current_threshold,
                "confidence_score": confidence,
                "expected_improvement": improvement,
                "reasoning": reasoning,
                "data_size": len(data),
                "method": "statistical",
                "optimization_type": "statistical",
            }

        except Exception as e:
            logger.error(f"Error in statistical optimization: {str(e)}")
            return {
                "recommended_threshold": current_threshold,
                "confidence_score": 0.0,
                "reasoning": f"Optimization failed: {str(e)}",
                "method": "statistical",
                "error": str(e),
            }

    def _calculate_statistical_threshold(
        self, data: List[float], threshold_type: str
    ) -> float:
        """
        计算统计阈值

        Args:
            data: 数据值列表
            threshold_type: 阈值类型

        Returns:
            float: 推荐的阈值
        """
        data_array = np.array(data)

        if threshold_type == "upper":
            # 上阈值：使用均值 + 3倍标准差
            mean = np.mean(data_array)
            std = np.std(data_array)
            return float(mean + 3 * std)
        elif threshold_type == "lower":
            # 下阈值：使用均值 - 3倍标准差
            mean = np.mean(data_array)
            std = np.std(data_array)
            return float(max(0, mean - 3 * std))
        else:
            # 默认使用中位数和IQR
            median = np.median(data_array)
            q75 = np.percentile(data_array, 75)
            q25 = np.percentile(data_array, 25)
            iqr = q75 - q25
            return float(median + 1.5 * iqr)

    def _calculate_confidence(
        self, data: List[float], threshold: float, threshold_type: str
    ) -> float:
        """
        计算置信度

        Args:
            data: 数据值列表
            threshold: 计算的阈值
            threshold_type: 阈值类型

        Returns:
            float: 置信度分数 (0-1)
        """
        if len(data) < self.min_data_points:
            return 0.0

        try:
            data_array = np.array(data)

            # 数据分布的稳定性影响置信度
            cv = (
                np.std(data_array) / np.mean(data_array)
                if np.mean(data_array) > 0
                else 1.0
            )

            # 变异系数越小，置信度越高
            stability_score = max(0, 1 - cv / 2)

            # 数据量影响置信度
            data_size_score = min(1, len(data) / 100)

            # 阈值合理性检查
            threshold_reasonableness = self._check_threshold_reasonableness(
                data_array, threshold, threshold_type
            )

            # 综合置信度
            confidence = (
                stability_score * 0.3
                + data_size_score * 0.3
                + threshold_reasonableness * 0.4
            )

            return float(min(1.0, max(0.0, confidence)))

        except Exception:
            return 0.0

    def _check_threshold_reasonableness(
        self, data: np.ndarray, threshold: float, threshold_type: str
    ) -> float:
        """
        检查阈值合理性

        Args:
            data: 数据数组
            threshold: 阈值
            threshold_type: 阈值类型

        Returns:
            float: 合理性分数
        """
        if threshold_type == "upper":
            # 上阈值应该大于大部分数据
            data_above_threshold = np.sum(data > threshold)
            ratio = data_above_threshold / len(data)
            return 1.0 - ratio  # 超过阈值的数据越少越好
        elif threshold_type == "lower":
            # 下阈值应该小于大部分数据
            data_below_threshold = np.sum(data < threshold)
            ratio = data_below_threshold / len(data)
            return 1.0 - ratio  # 低于阈值的数据越少越好
        else:
            return 0.5  # 默认中性分数

    def _estimate_improvement(
        self,
        data: List[float],
        current_threshold: float,
        new_threshold: float,
        threshold_type: str,
    ) -> float:
        """
        估算改善效果

        Args:
            data: 数据值列表
            current_threshold: 当前阈值
            new_threshold: 新阈值
            threshold_type: 阈值类型

        Returns:
            float: 预期改善效果 (0-1)
        """
        if len(data) == 0:
            return 0.0

        data_array = np.array(data)

        # 计算当前阈值下的异常率
        current_anomalies = self._count_anomalies(
            data_array, current_threshold, threshold_type
        )
        current_rate = current_anomalies / len(data_array)

        # 计算新阈值下的异常率
        new_anomalies = self._count_anomalies(data_array, new_threshold, threshold_type)
        new_rate = new_anomalies / len(data_array)

        # 计算改善效果
        if current_rate > 0:
            improvement = (current_rate - new_rate) / current_rate
        else:
            improvement = 0.0

        return float(min(1.0, max(0.0, improvement)))

    def _count_anomalies(
        self, data: np.ndarray, threshold: float, threshold_type: str
    ) -> int:
        """
        计算异常数据点数量

        Args:
            data: 数据数组
            threshold: 阈值
            threshold_type: 阈值类型

        Returns:
            int: 异常数据点数量
        """
        if threshold_type == "upper":
            return int(np.sum(data > threshold))
        elif threshold_type == "lower":
            return int(np.sum(data < threshold))
        else:
            return 0

    def _generate_statistical_reasoning(
        self, data: List[float], threshold: float, threshold_type: str
    ) -> str:
        """
        生成统计推理说明

        Args:
            data: 数据值列表
            threshold: 阈值
            threshold_type: 阈值类型

        Returns:
            str: 推理说明
        """
        data_array = np.array(data)
        mean = np.mean(data_array)
        std = np.std(data_array)

        if threshold_type == "upper":
            return (
                f"Statistical analysis (mean={mean:.2f}, std={std:.2f}) "
                f"suggests upper threshold at {threshold:.2f} "
                f"({(threshold - mean) / std:.1f} standard deviations from mean)"
            )
        elif threshold_type == "lower":
            return (
                f"Statistical analysis (mean={mean:.2f}, std={std:.2f}) "
                f"suggests lower threshold at {threshold:.2f} "
                f"({(mean - threshold) / std:.1f} standard deviations below mean)"
            )
        else:
            return f"Statistical analysis suggests threshold at {threshold:.2f}"

    def _is_anomaly(self, value: float, threshold: float, threshold_type: str) -> bool:
        """
        判断是否为异常值

        Args:
            value: 数据值
            threshold: 阈值
            threshold_type: 阈值类型

        Returns:
            bool: 是否为异常
        """
        if threshold_type == "upper":
            return value > threshold
        elif threshold_type == "lower":
            return value < threshold
        else:
            return False

    def _create_insufficient_data_result(
        self, data: List[float], current_threshold: float, threshold_type: str
    ) -> Dict[str, Any]:
        """
        创建数据不足结果

        Args:
            data: 数据值列表
            current_threshold: 当前阈值
            threshold_type: 阈值类型

        Returns:
            Dict[str, Any]: 数据不足的结果
        """
        return {
            "recommended_threshold": current_threshold,
            "current_threshold": current_threshold,
            "confidence_score": 0.0,
            "expected_improvement": 0.0,
            "reasoning": f"Insufficient data: {len(data)} points (minimum {self.min_data_points} required)",
            "data_size": len(data),
            "method": "statistical",
            "optimization_type": "statistical",
            "insufficient_data": True,
        }
