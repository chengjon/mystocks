"""智能阈值管理器 - 数据分析器"""

import logging
from typing import Any, Dict, List, Optional
import numpy as np
from .dataclasses import ThresholdConfig, ThresholdResult, OptimizationHistory

logger = logging.getLogger(__name__)
class DataAnalyzer:
    """数据分析器 - 基础阈值分析功能"""

    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.data_buffer = deque(maxlen=window_size)
        self.statistics_cache = {}

    def add_data_point(self, value: float, timestamp: datetime, rule_name: str):
        """添加数据点"""
        self.data_buffer.append({"value": value, "timestamp": timestamp, "rule_name": rule_name})

    def calculate_statistics(self) -> Dict[str, float]:
        """计算基本统计信息"""
        if len(self.data_buffer) < 10:
            return {}

        values = [point["value"] for point in self.data_buffer]

        stats = {
            "mean": np.mean(values),
            "std": np.std(values),
            "min": np.min(values),
            "max": np.max(values),
            "median": np.median(values),
            "q25": np.percentile(values, 25),
            "q75": np.percentile(values, 75),
            "iqr": np.percentile(values, 75) - np.percentile(values, 25),
            "skewness": self._calculate_skewness(values),
            "kurtosis": self._calculate_kurtosis(values),
        }

        self.statistics_cache = stats
        return stats

    def _calculate_skewness(self, values: List[float]) -> float:
        """计算偏度"""
        if len(values) < 3:
            return 0.0

        mean_val = np.mean(values)
        std_val = np.std(values)
        if std_val == 0:
            return 0.0

        return np.mean([((x - mean_val) / std_val) ** 3 for x in values])

    def _calculate_kurtosis(self, values: List[float]) -> float:
        """计算峰度"""
        if len(values) < 4:
            return 0.0

        mean_val = np.mean(values)
        std_val = np.std(values)
        if std_val == 0:
            return 0.0

        return np.mean([((x - mean_val) / std_val) ** 4 for x in values]) - 3

    def detect_anomalies(self, contamination: float = 0.1) -> List[int]:
        """检测异常值"""
        if len(self.data_buffer) < 20:
            return []

        values = np.array([point["value"] for point in self.data_buffer]).reshape(-1, 1)

        # 使用Isolation Forest检测异常
        iso_forest = IsolationForest(contamination=contamination, random_state=42)
        anomaly_labels = iso_forest.fit_predict(values)

        # 返回异常点的索引
        return [i for i, label in enumerate(anomaly_labels) if label == -1]

    def analyze_trend(self) -> Dict[str, Any]:
        """分析趋势"""
        if len(self.data_buffer) < 5:
            return {"trend": "insufficient_data"}

        values = [point["value"] for point in self.data_buffer]
        [point["timestamp"] for point in self.data_buffer]

        # 简单线性趋势
        x = np.arange(len(values))
        coeffs = np.polyfit(x, values, 1)
        slope = coeffs[0]

        # 计算趋势强度
        correlation = np.corrcoef(x, values)[0, 1] if len(values) > 2 else 0

        # 确定趋势方向
        if abs(slope) < 0.01:
            trend_direction = "stable"
        elif slope > 0:
            trend_direction = "increasing"
        else:
            trend_direction = "decreasing"

        return {
            "trend": trend_direction,
            "slope": slope,
            "strength": abs(correlation),
            "correlation": correlation,
            "current_value": values[-1],
            "previous_value": values[-2] if len(values) > 1 else values[-1],
        }


