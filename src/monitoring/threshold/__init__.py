"""
# 智能阈值管理模块
# 作者：MyStocks AI开发团队
# 创建日期：2025-12-20
# 版本：1.0.0
# 说明：模块化的智能阈值管理系统
"""

from .base_threshold_manager import (
    ThresholdRule,
    ThresholdAdjustment,
    OptimizationResult,
    DataAnalyzer,
)
from .statistical_optimizer import StatisticalOptimizer
from .trend_optimizer import TrendOptimizer
from .clustering_optimizer import ClusteringOptimizer

__all__ = [
    "ThresholdRule",
    "ThresholdAdjustment",
    "OptimizationResult",
    "DataAnalyzer",
    "StatisticalOptimizer",
    "TrendOptimizer",
    "ClusteringOptimizer",
]

# 版本信息
__version__ = "1.0.0"
__author__ = "MyStocks AI开发团队"


# 模块级别的便捷函数
def create_data_analyzer(window_size: int = 100) -> DataAnalyzer:
    """创建数据分析器的便捷函数"""
    return DataAnalyzer(window_size)


def create_statistical_optimizer(min_data_points: int = 30) -> StatisticalOptimizer:
    """创建统计优化器的便捷函数"""
    return StatisticalOptimizer(min_data_points)


def create_trend_optimizer(min_data_points: int = 10) -> TrendOptimizer:
    """创建趋势优化器的便捷函数"""
    return TrendOptimizer(min_data_points)


def create_clustering_optimizer(min_cluster_size: int = 3) -> ClusteringOptimizer:
    """创建聚类优化器的便捷函数"""
    return ClusteringOptimizer(min_cluster_size)
