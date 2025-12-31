"""
聚类分析器 - 从 intelligent_threshold_manager.py 拆分
职责：聚类分析、异常检测、阈值优化
遵循 TDD 原则：仅实现满足测试的最小功能
"""

import logging
from typing import Any, Dict, List

import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler

# 设置日志
logger = logging.getLogger(__name__)


class ClusteringAnalyzer:
    """聚类分析器 - 专注于聚类方法阈值优化"""

    def __init__(self, min_cluster_size: int = 3):
        """
        初始化聚类分析器

        Args:
            min_cluster_size: 最小聚类大小
        """
        self.min_cluster_size = min_cluster_size
        self.logger = logging.getLogger(__name__)

    def optimize_threshold_clustering(
        self, data: List[float], current_threshold: float, threshold_type: str = "upper"
    ) -> Dict[str, Any]:
        """
        基于聚类分析优化阈值

        Args:
            data: 数据值列表
            current_threshold: 当前阈值
            threshold_type: 阈值类型

        Returns:
            Dict[str, Any]: 优化结果
        """
        if len(data) < self.min_cluster_size * 2:
            return self._create_insufficient_data_result(data, current_threshold, threshold_type)

        try:
            # 执行聚类分析
            clusters = self._identify_clusters(data)

            if clusters["num_clusters"] < 2:
                return self._create_single_cluster_result(data, current_threshold, threshold_type)

            # 分析聚类特征
            cluster_analysis = self._analyze_clusters(data, clusters)

            # 基于聚类结果计算推荐阈值
            recommended_threshold = self._calculate_cluster_based_threshold(cluster_analysis, threshold_type)

            # 计算置信度
            confidence = self._calculate_cluster_confidence(cluster_analysis, clusters)

            # 生成推理说明
            reasoning = self._generate_clustering_reasoning(cluster_analysis, recommended_threshold)

            return {
                "recommended_threshold": recommended_threshold,
                "current_threshold": current_threshold,
                "confidence_score": confidence,
                "num_clusters": clusters["num_clusters"],
                "cluster_analysis": cluster_analysis,
                "reasoning": reasoning,
                "data_size": len(data),
                "method": "clustering",
                "optimization_type": "clustering",
            }

        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("Error in clustering optimization: %s", e)
            return {
                "recommended_threshold": current_threshold,
                "confidence_score": 0.0,
                "reasoning": f"Clustering analysis failed: {str(e)}",
                "method": "clustering",
                "error": str(e),
            }

    def _identify_clusters(self, data: List[float]) -> Dict[str, Any]:
        """
        识别聚类

        Args:
            data: 数据值列表

        Returns:
            Dict[str, Any]: 聚类结果
        """
        try:
            # 将数据转换为2D数组（DBSCAN需要2D）
            data_array = np.array(data).reshape(-1, 1)

            # 数据标准化
            scaler = StandardScaler()
            data_scaled = scaler.fit_transform(data_array)

            # DBSCAN聚类
            eps = 0.5  # 邻域半径
            min_samples = max(2, len(data) // 10)  # 最小样本数

            clustering = DBSCAN(eps=eps, min_samples=min_samples)
            cluster_labels = clustering.fit_predict(data_scaled)

            unique_labels = set(cluster_labels)
            n_clusters = len(unique_labels) - (1 if -1 in unique_labels else 0)

            return {
                "cluster_labels": cluster_labels.tolist(),
                "num_clusters": n_clusters,
                "noise_points": int(np.sum(cluster_labels == -1)),
                "eps": eps,
                "min_samples": min_samples,
            }

        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("Error in cluster identification: %s", e)
            return {
                "cluster_labels": [],
                "num_clusters": 0,
                "noise_points": len(data),
                "error": str(e),
            }

    def _analyze_clusters(self, data: List[float], clusters: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析聚类特征

        Args:
            data: 数据值列表
            clusters: 聚类结果

        Returns:
            Dict[str, Any]: 聚类分析结果
        """
        if clusters["num_clusters"] == 0:
            return {}

        cluster_labels = clusters["cluster_labels"]
        data_array = np.array(data)

        cluster_info = {}

        for label in set(cluster_labels):
            if label == -1:  # 噪声点
                continue

            cluster_mask = np.array(cluster_labels) == label
            cluster_data = data_array[cluster_mask]

            if len(cluster_data) == 0:
                continue

            cluster_info[label] = {
                "size": int(len(cluster_data)),
                "mean": float(np.mean(cluster_data)),
                "std": float(np.std(cluster_data)),
                "min": float(np.min(cluster_data)),
                "max": float(np.max(cluster_data)),
                "range": float(np.max(cluster_data) - np.min(cluster_data)),
                "variance": float(np.var(cluster_data)),
                "points": cluster_data.tolist(),
            }

        # 识别主要聚类（最大的）
        if cluster_info:
            main_cluster = max(cluster_info.keys(), key=lambda k: cluster_info[k]["size"])
            main_stats = cluster_info[main_cluster]

            # 计算与其他聚类的分离度
            separation_analysis = self._calculate_cluster_separation(cluster_info, main_cluster)

            return {
                "clusters": cluster_info,
                "main_cluster": main_cluster,
                "main_cluster_stats": main_stats,
                "separation_analysis": separation_analysis,
            }

        return {"clusters": cluster_info}

    def _calculate_cluster_separation(self, cluster_info: Dict[str, Dict], main_cluster: int) -> Dict[str, Any]:
        """
        计算聚类分离度

        Args:
            cluster_info: 聚类信息
            main_cluster: 主聚类标签

        Returns:
            Dict[str, Any]: 分离度分析
        """
        if main_cluster not in cluster_info:
            return {"separation_score": 0.0}

        main_stats = cluster_info[main_cluster]
        separations = {}

        for label, stats in cluster_info.items():
            if label == main_cluster:
                continue

            # 计算聚类中心的距离
            center_distance = abs(main_stats["mean"] - stats["mean"])

            # 计算聚类范围的重叠
            main_upper = main_stats["mean"] + main_stats["std"]
            main_lower = main_stats["mean"] - main_stats["std"]
            other_upper = stats["mean"] + stats["std"]
            other_lower = stats["mean"] - stats["std"]

            # 计算重叠程度
            overlap = max(0, min(main_upper, other_upper) - max(main_lower, other_lower))
            total_range = max(main_upper, other_upper) - min(main_lower, other_lower)
            overlap_ratio = overlap / total_range if total_range > 0 else 0

            separations[label] = {
                "center_distance": center_distance,
                "overlap_ratio": overlap_ratio,
                "separation_score": max(0, 1 - overlap_ratio),
            }

        # 计算整体分离度
        if separations:
            avg_separation = np.mean([s["separation_score"] for s in separations.values()])
        else:
            avg_separation = 1.0  # 只有一个聚类，认为是完全分离的

        return {
            "separations": separations,
            "avg_separation": float(avg_separation),
            "separation_score": float(avg_separation),
        }

    def _calculate_cluster_based_threshold(self, cluster_analysis: Dict[str, Any], threshold_type: str) -> float:
        """
        基于聚类结果计算阈值

        Args:
            cluster_analysis: 聚类分析结果
            threshold_type: 阈值类型

        Returns:
            float: 推荐阈值
        """
        if not cluster_analysis or "main_cluster_stats" not in cluster_analysis:
            return 0.0

        main_stats = cluster_analysis["main_cluster_stats"]

        if threshold_type == "upper":
            # 上阈值：基于主聚类上限和分离度
            if "separation_analysis" in cluster_analysis:
                separation = cluster_analysis["separation_analysis"]["separation_score"]
                # 分离度越高，可以设置更严格的阈值
                buffer_factor = 1.0 + (1.0 - separation) * 0.5
            else:
                buffer_factor = 1.5

            return main_stats["mean"] + main_stats["std"] * buffer_factor

        if threshold_type == "lower":
            # 下阈值：基于主聚类下限
            if "separation_analysis" in cluster_analysis:
                separation = cluster_analysis["separation_analysis"]["separation_score"]
                buffer_factor = 1.0 + (1.0 - separation) * 0.5
            else:
                buffer_factor = 1.5

            return max(0, main_stats["mean"] - main_stats["std"] * buffer_factor)

        # 默认使用主聚类均值
        return main_stats["mean"]

    def _calculate_cluster_confidence(self, cluster_analysis: Dict[str, Any], clusters: Dict[str, Any]) -> float:
        """
        计算聚类分析置信度

        Args:
            cluster_analysis: 聚类分析结果
            clusters: 聚类结果

        Returns:
            float: 置信度分数 (0-1)
        """
        if not cluster_analysis or clusters["num_clusters"] == 0:
            return 0.0

        confidence_factors = []

        # 聚类数量影响置信度
        n_clusters = clusters["num_clusters"]
        cluster_count_score = min(1.0, n_clusters / 5)  # 2-5个聚类较为理想
        confidence_factors.append(cluster_count_score)

        # 噪声点比例影响置信度
        total_cluster_points = (
            sum(
                len(cluster_analysis.get("clusters", {}).get(label, {}).get("points", []))
                for label in cluster_analysis.get("clusters", {}).keys()
            )
            if cluster_analysis.get("clusters")
            else 0
        )

        total_points = total_cluster_points + clusters["noise_points"]
        noise_ratio = clusters["noise_points"] / total_points if total_points > 0 else 0.0
        noise_score = max(0, 1.0 - noise_ratio)
        confidence_factors.append(noise_score)

        # 分离度影响置信度
        if "separation_analysis" in cluster_analysis:
            separation_score = cluster_analysis["separation_analysis"]["separation_score"]
            confidence_factors.append(separation_score)

        # 综合置信度
        return float(np.mean(confidence_factors))

    def _generate_clustering_reasoning(self, cluster_analysis: Dict[str, Any], recommended_threshold: float) -> str:
        """
        生成聚类推理说明

        Args:
            cluster_analysis: 聚类分析结果
            recommended_threshold: 推荐阈值

        Returns:
            str: 推理说明
        """
        if not cluster_analysis or "main_cluster_stats" not in cluster_analysis:
            return "Clustering analysis failed to identify meaningful clusters."

        main_stats = cluster_analysis["main_cluster_stats"]
        n_clusters = len(cluster_analysis.get("clusters", {}))

        reasoning = (
            f"Clustering analysis identified {n_clusters} distinct data groups. "
            f"The main cluster (size: {main_stats.get('size', 0)}) "
            f"has mean={main_stats.get('mean', 0):.2f} and std={main_stats.get('std', 0):.2f}. "
        )

        if "separation_analysis" in cluster_analysis:
            separation = cluster_analysis["separation_analysis"]["separation_score"]
            reasoning += f"Cluster separation score: {separation:.2f}. "

        reasoning += f"Recommended threshold: {recommended_threshold:.2f} based on cluster characteristics."

        return reasoning

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
            "num_clusters": 0,
            "reasoning": (
                f"Insufficient data for clustering: {len(data)} points "
                f"(minimum {self.min_cluster_size * 2} required)"
            ),
            "data_size": len(data),
            "method": "clustering",
            "optimization_type": "clustering",
            "insufficient_data": True,
        }

    def _create_single_cluster_result(
        self, data: List[float], current_threshold: float, threshold_type: str
    ) -> Dict[str, Any]:
        """
        创建单聚类结果

        Args:
            data: 数据值列表
            current_threshold: 当前阈值
            threshold_type: 阈值类型

        Returns:
            Dict[str, Any]: 单聚类结果
        """
        data_array = np.array(data)

        return {
            "recommended_threshold": current_threshold,
            "current_threshold": current_threshold,
            "confidence_score": 0.3,  # 低置信度
            "num_clusters": 1,
            "cluster_analysis": {
                "clusters": {
                    0: {
                        "size": len(data),
                        "mean": float(np.mean(data_array)),
                        "std": float(np.std(data_array)),
                        "min": float(np.min(data_array)),
                        "max": float(np.max(data_array)),
                    }
                },
                "main_cluster": 0,
                "main_cluster_stats": {
                    "size": len(data),
                    "mean": float(np.mean(data_array)),
                    "std": float(np.std(data_array)),
                },
            },
            "reasoning": "Only one cluster identified, insufficient separation for threshold optimization.",
            "data_size": len(data),
            "method": "clustering",
        }

    def get_cluster_summary(self, data: List[float]) -> Dict[str, Any]:
        """
        获取聚类摘要

        Args:
            data: 数据值列表

        Returns:
            Dict[str, Any]: 聚类摘要
        """
        if len(data) < self.min_cluster_size:
            return {"num_clusters": 0, "recommended_action": "insufficient_data"}

        clusters = self._identify_clusters(data)

        summary = {
            "num_clusters": clusters["num_clusters"],
            "noise_points": clusters["noise_points"],
            "data_points": len(data),
            "cluster_quality": "unknown",
        }

        if clusters["num_clusters"] > 0:
            # 分析聚类质量
            cluster_labels = clusters["cluster_labels"]
            unique_labels = set(cluster_labels) - {-1}  # 排除噪声点

            if len(unique_labels) > 1:
                summary["cluster_quality"] = "good"
            elif len(unique_labels) == 1:
                summary["cluster_quality"] = "single"

            summary["cluster_sizes"] = [int(np.sum(np.array(cluster_labels) == label)) for label in unique_labels]

        return summary
