#!/usr/bin/env python3
"""
# 功能：基础阈值管理器
# 作者：MyStocks AI开发团队
# 创建日期：2025-12-20
# 版本：1.0.0
# 说明：智能阈值管理的基础类和数据分析器
"""

import logging
import warnings
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

warnings.filterwarnings("ignore", category=UserWarning)

logger = logging.getLogger(__name__)


@dataclass
class ThresholdRule:
    """阈值规则定义"""

    name: str
    metric_name: str
    current_threshold: float
    optimal_threshold: Optional[float] = None
    threshold_type: str = "upper"  # 'upper', 'lower', 'range'
    confidence_score: float = 0.5
    learning_rate: float = 0.1
    adaptation_speed: float = 0.05
    false_positive_rate: float = 0.0
    false_negative_rate: float = 0.0
    adjustment_count: int = 0
    last_adjustment: Optional[datetime] = None
    history: List[Dict[str, Any]] = None

    def __post_init__(self):
        if self.history is None:
            self.history = []


@dataclass
class ThresholdAdjustment:
    """阈值调整记录"""

    timestamp: datetime
    rule_name: str
    old_threshold: float
    new_threshold: float
    reason: str
    confidence: float
    metrics_snapshot: Dict[str, Any]
    predicted_effectiveness: float = 0.0
    actual_effectiveness: Optional[float] = None


@dataclass
class OptimizationResult:
    """优化结果"""

    rule_name: str
    optimization_type: str  # 'anomaly_detection', 'trend_analysis', 'clustering', 'statistical'
    recommended_threshold: float
    confidence_score: float
    expected_improvement: float
    reasoning: str
    supporting_evidence: List[str]
    metadata: Dict[str, Any]


class DataAnalyzer:
    """数据分析器 - 基础阈值分析功能"""

    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.logger = logging.getLogger(f"{__name__}.DataAnalyzer")

    def analyze_basic_statistics(self, data: List[float]) -> Dict[str, float]:
        """基础统计分析"""
        if not data:
            return {}

        try:
            data_array = np.array(data)
            return {
                "mean": float(np.mean(data_array)),
                "median": float(np.median(data_array)),
                "std": float(np.std(data_array)),
                "min": float(np.min(data_array)),
                "max": float(np.max(data_array)),
                "q25": float(np.percentile(data_array, 25)),
                "q75": float(np.percentile(data_array, 75)),
                "iqr": float(np.percentile(data_array, 75) - np.percentile(data_array, 25)),
                "skewness": float(self._calculate_skewness(data_array)),
                "kurtosis": float(self._calculate_kurtosis(data_array)),
                "cv": float(np.std(data_array) / np.mean(data_array)) if np.mean(data_array) != 0 else 0,
            }
        except Exception as e:
            self.logger.error(f"统计分析失败: {e}")
            return {}

    def _calculate_skewness(self, data: np.ndarray) -> float:
        """计算偏度"""
        try:
            if len(data) < 3:
                return 0
            mean = np.mean(data)
            std = np.std(data)
            if std == 0:
                return 0
            return float(np.mean(((data - mean) / std) ** 3))
        except Exception:
            return 0

    def _calculate_kurtosis(self, data: np.ndarray) -> float:
        """计算峰度"""
        try:
            if len(data) < 4:
                return 0
            mean = np.mean(data)
            std = np.std(data)
            if std == 0:
                return 0
            return float(np.mean(((data - mean) / std) ** 4) - 3)
        except Exception:
            return 0

    def detect_outliers_iqr(self, data: List[float], factor: float = 1.5) -> Dict[str, Any]:
        """基于IQR的异常值检测"""
        if not data:
            return {"outliers": [], "outlier_indices": [], "outlier_count": 0}

        try:
            data_array = np.array(data)
            q1, q3 = np.percentile(data_array, [25, 75])
            iqr = q3 - q1
            lower_bound = q1 - factor * iqr
            upper_bound = q3 + factor * iqr

            outlier_mask = (data_array < lower_bound) | (data_array > upper_bound)
            outlier_indices = np.where(outlier_mask)[0].tolist()
            outliers = data_array[outlier_mask].tolist()

            return {
                "outliers": outliers,
                "outlier_indices": outlier_indices,
                "outlier_count": len(outliers),
                "lower_bound": float(lower_bound),
                "upper_bound": float(upper_bound),
                "iqr": float(iqr),
            }
        except Exception as e:
            self.logger.error(f"IQR异常值检测失败: {e}")
            return {"outliers": [], "outlier_indices": [], "outlier_count": 0}

    def calculate_moving_statistics(self, data: List[float], window: Optional[int] = None) -> Dict[str, List[float]]:
        """计算移动统计量"""
        if not data:
            return {"moving_mean": [], "moving_std": [], "moving_median": []}

        window = window or min(self.window_size, len(data))
        if window <= 1:
            return {
                "moving_mean": data,
                "moving_std": [0] * len(data),
                "moving_median": data,
            }

        try:
            data_array = np.array(data)
            moving_mean = []
            moving_std = []
            moving_median = []

            for i in range(len(data)):
                start_idx = max(0, i - window + 1)
                window_data = data_array[start_idx : i + 1]

                moving_mean.append(float(np.mean(window_data)))
                moving_std.append(float(np.std(window_data)))
                moving_median.append(float(np.median(window_data)))

            return {
                "moving_mean": moving_mean,
                "moving_std": moving_std,
                "moving_median": moving_median,
            }
        except Exception as e:
            self.logger.error(f"移动统计计算失败: {e}")
            return {"moving_mean": [], "moving_std": [], "moving_median": []}

    def analyze_volatility(self, data: List[float]) -> Dict[str, float]:
        """分析数据波动性"""
        if len(data) < 2:
            return {"volatility": 0, "max_drawdown": 0, "up_down_ratio": 0}

        try:
            data_array = np.array(data)
            returns = np.diff(data_array) / data_array[:-1]

            # 过滤无效值
            valid_returns = returns[np.isfinite(returns)]

            if len(valid_returns) == 0:
                return {"volatility": 0, "max_drawdown": 0, "up_down_ratio": 0}

            volatility = float(np.std(valid_returns))

            # 最大回撤
            peak = np.maximum.accumulate(data_array)
            drawdown = (peak - data_array) / peak
            max_drawdown = float(np.max(drawdown))

            # 上涨下跌比例
            up_moves = np.sum(valid_returns > 0)
            down_moves = np.sum(valid_returns < 0)
            up_down_ratio = float(up_moves / down_moves) if down_moves > 0 else float("inf")

            return {
                "volatility": volatility,
                "max_drawdown": max_drawdown,
                "up_down_ratio": up_down_ratio,
                "positive_moves": int(up_moves),
                "negative_moves": int(down_moves),
                "total_moves": len(valid_returns),
            }
        except Exception as e:
            self.logger.error(f"波动性分析失败: {e}")
            return {"volatility": 0, "max_drawdown": 0, "up_down_ratio": 0}

    def calculate_z_scores(self, data: List[float]) -> List[float]:
        """计算Z分数"""
        if not data:
            return []

        try:
            data_array = np.array(data)
            mean = np.mean(data_array)
            std = np.std(data_array)

            if std == 0:
                return [0.0] * len(data)

            z_scores = (data_array - mean) / std
            return [float(z) for z in z_scores]
        except Exception as e:
            self.logger.error(f"Z分数计算失败: {e}")
            return [0.0] * len(data)

    def detect_trend_changes(self, data: List[float], min_window: int = 5) -> List[int]:
        """检测趋势变化点"""
        if len(data) < min_window * 2:
            return []

        try:
            data_array = np.array(data)
            trend_changes = []

            # 使用简单移动平均斜率检测趋势变化
            for i in range(min_window, len(data) - min_window):
                before_window = data_array[i - min_window : i]
                after_window = data_array[i : i + min_window]

                before_slope = np.polyfit(range(min_window), before_window, 1)[0]
                after_slope = np.polyfit(range(min_window), after_window, 1)[0]

                # 检测斜率符号变化
                if before_slope * after_slope < 0:
                    trend_changes.append(i)

            return trend_changes
        except Exception as e:
            self.logger.error(f"趋势变化检测失败: {e}")
            return []

    def get_data_quality_metrics(self, data: List[float]) -> Dict[str, Any]:
        """获取数据质量指标"""
        if not data:
            return {
                "total_count": 0,
                "valid_count": 0,
                "missing_count": 0,
                "missing_ratio": 0,
                "duplicate_count": 0,
                "quality_score": 0,
            }

        try:
            total_count = len(data)

            # 检测有效值（非NaN、非None、有限数值）
            valid_data = [x for x in data if x is not None and np.isfinite(x)]
            valid_count = len(valid_data)
            missing_count = total_count - valid_count
            missing_ratio = missing_count / total_count if total_count > 0 else 0

            # 检测重复值
            unique_count = len(set(valid_data))
            duplicate_count = valid_count - unique_count

            # 计算质量分数（考虑完整性、唯一性）
            completeness_score = (valid_count / total_count) if total_count > 0 else 0
            uniqueness_score = (unique_count / valid_count) if valid_count > 0 else 0
            quality_score = (completeness_score + uniqueness_score) / 2

            return {
                "total_count": total_count,
                "valid_count": valid_count,
                "missing_count": missing_count,
                "missing_ratio": missing_ratio,
                "unique_count": unique_count,
                "duplicate_count": duplicate_count,
                "completeness_score": completeness_score,
                "uniqueness_score": uniqueness_score,
                "quality_score": quality_score,
            }
        except Exception as e:
            self.logger.error(f"数据质量分析失败: {e}")
            return {
                "total_count": len(data),
                "valid_count": 0,
                "missing_count": len(data),
                "missing_ratio": 1.0,
                "duplicate_count": 0,
                "quality_score": 0,
            }
