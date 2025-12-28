#!/usr/bin/env python3
"""
# 功能：聚类优化器
# 作者：MyStocks AI开发团队
# 创建日期：2025-12-20
# 版本：1.0.0
# 说明：基于聚类分析的阈值优化器
"""

import logging
import numpy as np
from typing import List
from sklearn.cluster import DBSCAN

from .base_threshold_manager import OptimizationResult


class ClusteringOptimizer:
    """聚类分析优化器"""

    def __init__(self, min_cluster_size: int = 3):
        self.min_cluster_size = min_cluster_size
        self.logger = logging.getLogger(f"{__name__}.ClusteringOptimizer")

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

        try:
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
        except Exception as e:
            self.logger.error("聚类优化失败: %s", e)
            return OptimizationResult(
                rule_name="clustering_optimizer",
                optimization_type="clustering",
                recommended_threshold=current_threshold,
                confidence_score=0.0,
                expected_improvement=0.0,
                reasoning=f"聚类分析出错: {str(e)}",
                supporting_evidence=["处理过程中发生错误"],
                metadata={"error": True, "error_message": str(e)},
            )

    def analyze_cluster_quality(self, values: List[float], cluster_labels: np.ndarray) -> dict:
        """分析聚类质量"""
        try:
            if not values or len(cluster_labels) != len(values):
                return {"quality_score": 0, "silhouette_score": 0, "num_clusters": 0}

            from sklearn.metrics import silhouette_score

            values_array = np.array(values).reshape(-1, 1)

            # 过滤噪声点
            valid_mask = cluster_labels != -1
            if np.sum(valid_mask) < 2:
                return {"quality_score": 0, "silhouette_score": 0, "num_clusters": 0}

            valid_values = values_array[valid_mask]
            valid_labels = cluster_labels[valid_mask]

            # 计算轮廓系数
            silhouette_avg = silhouette_score(valid_values, valid_labels)

            # 计算聚类质量分数
            unique_labels = set(valid_labels)
            num_clusters = len(unique_labels)

            # 质量分数综合考虑轮廓系数和聚类数量
            if num_clusters > 1:
                quality_score = silhouette_avg * (1 - abs(num_clusters - 3) / 10)
            else:
                quality_score = 0.5

            return {
                "quality_score": max(0, quality_score),
                "silhouette_score": silhouette_avg,
                "num_clusters": num_clusters,
                "noise_ratio": np.sum(cluster_labels == -1) / len(cluster_labels),
            }
        except Exception as e:
            self.logger.error("聚类质量分析失败: %s", e)
            return {"quality_score": 0, "silhouette_score": 0, "num_clusters": 0}

    def detect_anomalies_with_clustering(
        self, values: List[float], eps: float = 0.5, min_samples: int = 3
    ) -> List[int]:
        """使用聚类检测异常值"""
        try:
            if len(values) < min_samples:
                return []

            values_array = np.array(values).reshape(-1, 1)

            # 使用DBSCAN聚类
            clustering = DBSCAN(eps=eps, min_samples=min_samples)
            cluster_labels = clustering.fit_predict(values_array)

            # 噪声点被认为是异常值
            anomaly_indices = [i for i, label in enumerate(cluster_labels) if label == -1]

            return anomaly_indices
        except Exception as e:
            self.logger.error("聚类异常检测失败: %s", e)
            return []

    def optimize_dbscan_parameters(self, values: List[float]) -> dict:
        """优化DBSCAN参数"""
        try:
            if len(values) < 10:
                return {"eps": 0.5, "min_samples": 3, "score": 0}

            values_array = np.array(values).reshape(-1, 1)

            # 尝试不同的参数组合
            best_params = {"eps": 0.5, "min_samples": 3, "score": 0}

            eps_values = np.linspace(0.1, 2.0, 10)
            min_samples_values = [2, 3, 4, 5]

            for eps in eps_values:
                for min_samples in min_samples_values:
                    try:
                        clustering = DBSCAN(eps=eps, min_samples=min_samples)
                        cluster_labels = clustering.fit_predict(values_array)

                        # 计算聚类质量
                        quality = self.analyze_cluster_quality(values, cluster_labels)

                        if quality["quality_score"] > best_params["score"]:
                            best_params = {
                                "eps": eps,
                                "min_samples": min_samples,
                                "score": quality["quality_score"],
                                "num_clusters": quality["num_clusters"],
                                "silhouette_score": quality["silhouette_score"],
                            }
                    except Exception:
                        continue

            return best_params
        except Exception as e:
            self.logger.error("DBSCAN参数优化失败: %s", e)
            return {"eps": 0.5, "min_samples": 3, "score": 0}
