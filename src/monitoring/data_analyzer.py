"""
数据分析器 - 从 intelligent_threshold_manager.py 拆分
职责：基础数据分析、统计计算、异常检测
遵循 TDD 原则：仅实现满足测试的最小功能
"""

import logging
from datetime import datetime
from typing import Dict, List, Any
from collections import deque
import numpy as np
from sklearn.ensemble import IsolationForest

# 设置日志
logger = logging.getLogger(__name__)


class DataAnalyzer:
    """数据分析器 - 专注于基础数据分析功能"""

    def __init__(self, window_size: int = 100):
        """
        初始化数据分析器

        Args:
            window_size: 数据窗口大小
        """
        self.window_size = window_size
        self.data_points = deque(maxlen=window_size)
        self.logger = logging.getLogger(__name__)

    def add_data_point(self, value: float, timestamp: datetime, rule_name: str):
        """
        添加数据点

        Args:
            value: 数据值
            timestamp: 时间戳
            rule_name: 规则名称
        """
        data_point = {"value": value, "timestamp": timestamp, "rule_name": rule_name}
        self.data_points.append(data_point)
        logger.debug(f"Added data point: {value} for rule {rule_name}")

    def calculate_statistics(self) -> Dict[str, float]:
        """
        计算统计数据

        Returns:
            Dict[str, float]: 统计结果
        """
        if not self.data_points:
            return {
                "mean": 0.0,
                "std_dev": 0.0,
                "min_value": 0.0,
                "max_value": 0.0,
                "median": 0.0,
                "count": 0,
            }

        values = [point["value"] for point in self.data_points]
        values_array = np.array(values)

        return {
            "mean": float(np.mean(values_array)),
            "std_dev": float(np.std(values_array)),
            "min_value": float(np.min(values_array)),
            "max_value": float(np.max(values_array)),
            "median": float(np.median(values_array)),
            "count": len(values),
        }

    def _calculate_skewness(self, values: List[float]) -> float:
        """
        计算偏度

        Args:
            values: 数值列表

        Returns:
            float: 偏度值
        """
        if len(values) < 3:
            return 0.0

        values_array = np.array(values)
        mean = np.mean(values_array)
        std = np.std(values_array)

        if std == 0:
            return 0.0

        skew = np.mean(((values_array - mean) / std) ** 3)
        return float(skew)

    def _calculate_kurtosis(self, values: List[float]) -> float:
        """
        计算峰度

        Args:
            values: 数值列表

        Returns:
            float: 峰度值
        """
        if len(values) < 4:
            return 0.0

        values_array = np.array(values)
        mean = np.mean(values_array)
        std = np.std(values_array)

        if std == 0:
            return 0.0

        kurt = np.mean(((values_array - mean) / std) ** 4) - 3
        return float(kurt)

    def detect_anomalies(self, contamination: float = 0.1) -> List[int]:
        """
        检测异常数据点

        Args:
            contamination: 异常值比例

        Returns:
            List[int]: 异常数据点索引
        """
        if len(self.data_points) < 10:
            return []

        try:
            values = np.array([[point["value"]] for point in self.data_points])

            # 使用IsolationForest检测异常
            clf = IsolationForest(contamination=contamination, random_state=42)
            predictions = clf.fit_predict(values)

            # 返回异常点索引（-1表示异常）
            anomaly_indices = [i for i, pred in enumerate(predictions) if pred == -1]

            logger.debug(
                f"Detected {len(anomaly_indices)} anomalies out of {len(self.data_points)} points"
            )
            return anomaly_indices

        except Exception as e:
            logger.error(f"Error in anomaly detection: {str(e)}")
            return []

    def analyze_trend(self) -> Dict[str, Any]:
        """
        分析数据趋势

        Returns:
            Dict[str, Any]: 趋势分析结果
        """
        if len(self.data_points) < 3:
            return {
                "direction": "insufficient_data",
                "strength": 0.0,
                "slope": 0.0,
                "r_squared": 0.0,
            }

        try:
            # 提取值和时间
            values = [point["value"] for point in self.data_points]
            timestamps = [point["timestamp"].timestamp() for point in self.data_points]

            # 简单线性回归分析趋势
            x = np.array(timestamps)
            y = np.array(values)

            # 计算斜率
            n = len(x)
            x_mean = np.mean(x)
            y_mean = np.mean(y)

            numerator = np.sum((x - x_mean) * (y - y_mean))
            denominator = np.sum((x - x_mean) ** 2)

            if denominator == 0:
                slope = 0.0
                r_squared = 0.0
            else:
                slope = numerator / denominator

                # 计算R²
                y_pred = y_mean + slope * (x - x_mean)
                ss_res = np.sum((y - y_pred) ** 2)
                ss_tot = np.sum((y - y_mean) ** 2)
                r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0

            # 判断趋势方向
            if abs(slope) < 1e-6:
                direction = "stable"
            elif slope > 0:
                direction = "upward"
            else:
                direction = "downward"

            # 趋势强度基于斜率和R²
            strength = abs(slope) * r_squared

            return {
                "direction": direction,
                "strength": float(strength),
                "slope": float(slope),
                "r_squared": float(r_squared),
            }

        except Exception as e:
            logger.error(f"Error in trend analysis: {str(e)}")
            return {
                "direction": "error",
                "strength": 0.0,
                "slope": 0.0,
                "r_squared": 0.0,
            }

    def get_recent_data(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        获取最近的数据点

        Args:
            count: 返回的数据点数量

        Returns:
            List[Dict[str, Any]]: 最近的数据点
        """
        return list(self.data_points)[-count:] if self.data_points else []

    def clear_data(self):
        """清空数据"""
        self.data_points.clear()
        logger.info("Data analyzer cleared")

    def get_data_summary(self) -> Dict[str, Any]:
        """
        获取数据摘要

        Returns:
            Dict[str, Any]: 数据摘要
        """
        if not self.data_points:
            return {
                "total_points": 0,
                "rules": set(),
                "time_range": None,
                "oldest_timestamp": None,
                "newest_timestamp": None,
            }

        timestamps = [point["timestamp"] for point in self.data_points]
        rules = {point["rule_name"] for point in self.data_points}

        return {
            "total_points": len(self.data_points),
            "rules": list(rules),
            "time_range": min(timestamps).isoformat()
            + " to "
            + max(timestamps).isoformat(),
            "oldest_timestamp": min(timestamps).isoformat(),
            "newest_timestamp": max(timestamps).isoformat(),
        }
