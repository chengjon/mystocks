"""智能阈值管理器 - 趋势与聚类优化器"""

import logging
from typing import Any, Dict, List, Optional
import numpy as np

logger = logging.getLogger(__name__)
class TrendOptimizer:
    """趋势分析优化器"""

    def optimize_threshold_trend(
        self,
        values: List[float],
        timestamps: List[datetime],
        current_threshold: float,
        threshold_type: str = "upper",
    ) -> OptimizationResult:
        """基于趋势分析优化阈值"""

        if len(values) < 10:
            return OptimizationResult(
                rule_name="trend_optimizer",
                optimization_type="trend_analysis",
                recommended_threshold=current_threshold,
                confidence_score=0.1,
                expected_improvement=0.0,
                reasoning="数据点不足，无法进行趋势分析",
                supporting_evidence=["需要至少10个数据点"],
                metadata={"insufficient_data": True},
            )

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


class ClusteringOptimizer:
    """聚类分析优化器"""

    def __init__(self, min_cluster_size: int = 3):
        self.min_cluster_size = min_cluster_size

    def optimize_threshold_clustering(
        self,
        values: List[float],
        current_threshold: float,
        threshold_type: str = "upper",
    ) -> OptimizationResult:
        """基于聚类分析优化阈值"""

        if len(values) < 10:
            return OptimizationResult(
                rule_name="clustering_optimizer",
                optimization_type="clustering",
                recommended_threshold=current_threshold,
                confidence_score=0.1,
                expected_improvement=0.0,
                reasoning="数据点不足，无法进行聚类分析",
                supporting_evidence=["需要至少10个数据点"],
                metadata={"insufficient_data": True},
            )

        values_array = np.array(values).reshape(-1, 1)

        # 使用DBSCAN进行聚类
        clustering = DBSCAN(eps=0.5, min_samples=self.min_cluster_size)
        cluster_labels = clustering.fit_predict(values_array)

        # 分析聚类结果
        unique_labels = set(cluster_labels)
        cluster_sizes = {}

        for label in unique_labels:
            if label != -1:  # 忽略噪声点
                cluster_sizes[label] = np.sum(cluster_labels == label)

        if not cluster_sizes:
            return OptimizationResult(
                rule_name="clustering_optimizer",
                optimization_type="clustering",
                recommended_threshold=current_threshold,
                confidence_score=0.1,
                expected_improvement=0.0,
                reasoning="无法形成有效聚类",
                supporting_evidence=["所有点被标记为噪声"],
                metadata={"no_clusters": True},
            )

        # 找到最大聚类和次大聚类
        largest_cluster_label = max(cluster_sizes, key=cluster_sizes.get)
        largest_cluster_size = cluster_sizes[largest_cluster_label]

        # 获取最大聚类的边界
        largest_cluster_values = values_array[cluster_labels == largest_cluster_label]

        if threshold_type == "upper":
            # 上阈值设为最大聚类的上界
            boundary = np.percentile(largest_cluster_values, 95)
        else:
            # 下阈值设为最大聚类的下界
            boundary = np.percentile(largest_cluster_values, 5)

        recommended_threshold = float(boundary)

        # 计算置信度
        confidence = min(1.0, largest_cluster_size / len(values))

        # 估计改进效果
        improvement = confidence * 0.3  # 基于聚类质量的改进估计

        return OptimizationResult(
            rule_name="clustering_optimizer",
            optimization_type="clustering",
            recommended_threshold=recommended_threshold,
            confidence_score=confidence,
            expected_improvement=improvement,
            reasoning=f"基于聚类分析，最大聚类包含{largest_cluster_size}个点",
            supporting_evidence=[
                f"聚类数量: {len(unique_labels) - (1 if -1 in cluster_labels else 0)}",
                f"最大聚类大小: {largest_cluster_size}",
                f"噪声点数量: {np.sum(cluster_labels == -1)}",
                f"边界值: {boundary:.2f}",
            ],
            metadata={
                "num_clusters": len(unique_labels) - (1 if -1 in cluster_labels else 0),
                "largest_cluster_size": largest_cluster_size,
                "noise_points": np.sum(cluster_labels == -1),
                "boundary_value": boundary,
            },
        )


