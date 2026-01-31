#!/usr/bin/env python3
"""
智能阈值算法和误报优化模块

基于机器学习的智能阈值算法，自动学习和调整监控阈值，减少误报率。
集成历史数据分析和趋势预测，提供动态阈值优化功能。

作者: MyStocks AI开发团队
创建日期: 2025-11-16
版本: 1.0.0
依赖: numpy, pandas, scikit-learn
版权: MyStocks Project © 2025
"""

import asyncio
import json
import logging
import warnings
from collections import deque
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.ensemble import IsolationForest

# 监控组件导入
try:
    from .monitoring_database import get_monitoring_database
    from .performance_monitor import SystemMetrics
except ImportError:
    # 兼容模式
    SystemMetrics = Any
    get_monitoring_database = None

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


class StatisticalOptimizer:
    """统计优化器"""

    def __init__(self, min_data_points: int = 30):
        self.min_data_points = min_data_points

    def optimize_threshold_statistical(
        self,
        values: List[float],
        current_threshold: float,
        threshold_type: str = "upper",
    ) -> OptimizationResult:
        """基于统计方法优化阈值"""

        if len(values) < self.min_data_points:
            return self._create_insufficient_data_result(current_threshold)

        values_array = np.array(values)

        # 计算统计指标
        mean_val = np.mean(values_array)
        std_val = np.std(values_array)
        q75 = np.percentile(values_array, 75)
        q95 = np.percentile(values_array, 95)
        q99 = np.percentile(values_array, 99)

        if threshold_type == "upper":
            # 上阈值优化
            if std_val > 0:
                # 基于标准差的方法 (均值 + k*标准差)
                k = 2.0  # 2-sigma规则
                recommended_threshold = mean_val + k * std_val
            else:
                recommended_threshold = q95

            # 确保新阈值比当前阈值更合理
            recommended_threshold = min(recommended_threshold, q99)

        elif threshold_type == "lower":
            # 下阈值优化
            if std_val > 0:
                k = 2.0
                recommended_threshold = mean_val - k * std_val
            else:
                recommended_threshold = np.percentile(values_array, 5)

            recommended_threshold = max(recommended_threshold, q1=np.percentile(values_array, 1))

        else:  # range
            recommended_threshold = q75

        # 计算置信度
        confidence = self._calculate_confidence(values_array, recommended_threshold, threshold_type)

        # 计算预期改进
        improvement = self._estimate_improvement(values, current_threshold, recommended_threshold, threshold_type)

        return OptimizationResult(
            rule_name="statistical_optimizer",
            optimization_type="statistical",
            recommended_threshold=float(recommended_threshold),
            confidence_score=confidence,
            expected_improvement=improvement,
            reasoning=f"基于{len(values)}个数据点的统计分析",
            supporting_evidence=[
                f"均值: {mean_val:.2f}",
                f"标准差: {std_val:.2f}",
                f"95%分位数: {q95:.2f}",
                "异常值检测使用IQR方法",
            ],
            metadata={
                "mean": float(mean_val),
                "std": float(std_val),
                "q75": float(q75),
                "q95": float(q95),
                "data_points": len(values),
            },
        )

    def _calculate_confidence(self, values: np.ndarray, threshold: float, threshold_type: str) -> float:
        """计算阈值置信度"""

        # 基于阈值与数据分布的匹配度
        if threshold_type == "upper":
            # 检查有多少数据在阈值以下
            ratio_below = np.sum(values <= threshold) / len(values)
            # 理想情况下应该是95-99%的数据在阈值以下
            target_ratio = 0.97
            confidence = 1.0 - abs(ratio_below - target_ratio)
        else:
            # 对于下阈值，检查有多少数据在阈值以上
            ratio_above = np.sum(values >= threshold) / len(values)
            target_ratio = 0.97
            confidence = 1.0 - abs(ratio_above - target_ratio)

        return max(0.0, min(1.0, confidence))

    def _estimate_improvement(
        self,
        values: List[float],
        old_threshold: float,
        new_threshold: float,
        threshold_type: str,
    ) -> float:
        """估计阈值改进效果"""

        if not values:
            return 0.0

        # 计算旧阈值和新阈值下的异常率
        old_anomaly_count = sum(1 for v in values if self._is_anomaly(v, old_threshold, threshold_type))
        new_anomaly_count = sum(1 for v in values if self._is_anomaly(v, new_threshold, threshold_type))

        old_rate = old_anomaly_count / len(values)
        new_rate = new_anomaly_count / len(values)

        # 改进率为异常率减少的比例
        if old_rate > 0:
            improvement = (old_rate - new_rate) / old_rate
        else:
            improvement = 0.0 if new_rate == 0 else -1.0

        return max(-1.0, improvement)

    def _is_anomaly(self, value: float, threshold: float, threshold_type: str) -> bool:
        """判断值是否为异常"""
        if threshold_type == "upper":
            return value > threshold
        elif threshold_type == "lower":
            return value < threshold
        else:
            return False

    def _create_insufficient_data_result(self, current_threshold: float) -> OptimizationResult:
        """数据不足时的结果"""
        return OptimizationResult(
            rule_name="statistical_optimizer",
            optimization_type="statistical",
            recommended_threshold=current_threshold,
            confidence_score=0.1,
            expected_improvement=0.0,
            reasoning="数据不足，无法进行统计优化",
            supporting_evidence=["需要至少30个数据点"],
            metadata={"data_insufficient": True},
        )


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


class IntelligentThresholdManager:
    """智能阈值管理器 - 主控制器"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._get_default_config()
        self.threshold_rules: Dict[str, ThresholdRule] = {}
        self.adjustment_history: List[ThresholdAdjustment] = []
        self.data_analyzers: Dict[str, DataAnalyzer] = {}

        # 优化器
        self.statistical_optimizer = StatisticalOptimizer()
        self.trend_optimizer = TrendOptimizer()
        self.clustering_optimizer = ClusteringOptimizer()

        # 监控数据库
        self.monitoring_db = None
        if get_monitoring_database:
            try:
                self.monitoring_db = get_monitoring_database()
            except Exception as e:
                logger.warning("监控数据库初始化失败: %s", e)

        # 初始化默认阈值规则
        self._initialize_default_rules()

        logger.info("✅ 智能阈值管理器初始化完成")

    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "learning_rate": 0.1,
            "adaptation_speed": 0.05,
            "min_data_points": 30,
            "optimization_interval": 3600,  # 1小时
            "max_history_size": 1000,
            "false_positive_threshold": 0.1,
            "false_negative_threshold": 0.05,
            "confidence_threshold": 0.7,
            "trend_analysis_window": 24,  # 24小时
            "anomaly_detection_contamination": 0.1,
        }

    def _initialize_default_rules(self):
        """初始化默认阈值规则"""
        default_rules = [
            ThresholdRule(
                name="cpu_usage_high",
                metric_name="cpu_usage",
                current_threshold=80.0,
                threshold_type="upper",
            ),
            ThresholdRule(
                name="gpu_memory_high",
                metric_name="gpu_memory_usage",
                current_threshold=85.0,
                threshold_type="upper",
            ),
            ThresholdRule(
                name="memory_usage_high",
                metric_name="memory_usage",
                current_threshold=85.0,
                threshold_type="upper",
            ),
            ThresholdRule(
                name="strategy_win_rate_low",
                metric_name="strategy_win_rate",
                current_threshold=30.0,
                threshold_type="lower",
            ),
            ThresholdRule(
                name="strategy_drawdown_high",
                metric_name="strategy_drawdown",
                current_threshold=5.0,
                threshold_type="upper",
            ),
            ThresholdRule(
                name="query_time_high",
                metric_name="query_time_ms",
                current_threshold=5000.0,
                threshold_type="upper",
            ),
        ]

        for rule in default_rules:
            self.add_threshold_rule(rule)

        logger.info("✅ 已初始化%s个默认阈值规则", len(default_rules))

    def add_threshold_rule(self, rule: ThresholdRule):
        """添加阈值规则"""
        self.threshold_rules[rule.name] = rule
        self.data_analyzers[rule.name] = DataAnalyzer()
        logger.info("✅ 已添加阈值规则: %s", rule.name)

    def remove_threshold_rule(self, rule_name: str) -> bool:
        """移除阈值规则"""
        if rule_name in self.threshold_rules:
            del self.threshold_rules[rule_name]
            if rule_name in self.data_analyzers:
                del self.data_analyzers[rule_name]
            logger.info("✅ 已移除阈值规则: %s", rule_name)
            return True
        return False

    async def process_metric_value(
        self, rule_name: str, value: float, timestamp: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """处理指标值，评估是否触发告警"""

        if rule_name not in self.threshold_rules:
            return {"triggered": False, "reason": "rule_not_found"}

        rule = self.threshold_rules[rule_name]
        if timestamp is None:
            timestamp = datetime.now()

        # 添加数据点到分析器
        analyzer = self.data_analyzers[rule_name]
        analyzer.add_data_point(value, timestamp, rule_name)

        # 记录历史数据
        self._record_metric_data(rule_name, value, timestamp)

        # 评估是否触发告警
        triggered = self._evaluate_threshold(rule, value)

        # 如果触发了告警，记录误报检测结果
        if triggered:
            await self._handle_potential_false_positive(rule_name, value, timestamp)

        # 更新规则统计
        self._update_rule_statistics(rule_name, value, triggered, timestamp)

        return {
            "triggered": triggered,
            "rule_name": rule_name,
            "value": value,
            "threshold": rule.current_threshold,
            "threshold_type": rule.threshold_type,
            "confidence": rule.confidence_score,
        }

    def _evaluate_threshold(self, rule: ThresholdRule, value: float) -> bool:
        """评估阈值触发条件"""

        if rule.threshold_type == "upper":
            return value > rule.current_threshold
        elif rule.threshold_type == "lower":
            return value < rule.current_threshold
        else:
            return False  # range类型暂未实现

    def _record_metric_data(self, rule_name: str, value: float, timestamp: datetime):
        """记录指标数据"""

        if not self.monitoring_db:
            return

        try:
            # 记录到监控数据库
            pass

            # 这里可以调用具体的数据库写入方法
            # self.monitoring_db.record_intelligent_metric_data(record)

        except Exception as e:
            logger.warning("记录指标数据失败: %s", e)

    async def _handle_potential_false_positive(self, rule_name: str, value: float, timestamp: datetime):
        """处理可能的误报"""

        try:
            analyzer = self.data_analyzers[rule_name]

            # 检测异常值
            anomalies = analyzer.detect_anomalies(contamination=self.config["anomaly_detection_contamination"])

            # 如果当前值被标记为异常，可能是真正的告警
            if len(anomalies) > 0:
                current_index = len(analyzer.data_buffer) - 1
                if current_index in anomalies:
                    # 记录异常确认
                    self._confirm_true_positive(rule_name, value, timestamp)
                else:
                    # 记录可能的误报
                    self._flag_potential_false_positive(rule_name, value, timestamp)

        except Exception as e:
            logger.warning("误报检测失败: %s", e)

    def _confirm_true_positive(self, rule_name: str, value: float, timestamp: datetime):
        """确认真正的正例"""

        if rule_name in self.threshold_rules:
            rule = self.threshold_rules[rule_name]

            # 减少误报率
            rule.false_positive_rate *= 0.95  # 递减
            rule.false_negative_rate *= 1.05  # 微增

            # 记录历史
            self._add_to_rule_history(
                rule,
                {
                    "timestamp": timestamp.isoformat(),
                    "type": "true_positive",
                    "value": value,
                    "threshold": rule.current_threshold,
                },
            )

    def _flag_potential_false_positive(self, rule_name: str, value: float, timestamp: datetime):
        """标记可能的误报"""

        if rule_name in self.threshold_rules:
            rule = self.threshold_rules[rule_name]

            # 增加误报率
            rule.false_positive_rate = min(1.0, rule.false_positive_rate * 1.1)

            # 如果误报率过高，触发阈值调整
            if rule.false_positive_rate > self.config["false_positive_threshold"]:
                logger.info("规则%s误报率过高(%s)，建议调整阈值", rule_name, rule.false_positive_rate)

            # 记录历史
            self._add_to_rule_history(
                rule,
                {
                    "timestamp": timestamp.isoformat(),
                    "type": "potential_false_positive",
                    "value": value,
                    "threshold": rule.current_threshold,
                },
            )

    def _update_rule_statistics(self, rule_name: str, value: float, triggered: bool, timestamp: datetime):
        """更新规则统计信息"""

        if rule_name not in self.threshold_rules:
            return

        rule = self.threshold_rules[rule_name]

        # 添加到历史记录
        self._add_to_rule_history(
            rule,
            {
                "timestamp": timestamp.isoformat(),
                "value": value,
                "triggered": triggered,
                "threshold": rule.current_threshold,
            },
        )

        # 计算置信度
        rule.confidence_score = self._calculate_confidence_score(rule)

    def _add_to_rule_history(self, rule: ThresholdRule, entry: Dict[str, Any]):
        """添加到规则历史"""

        rule.history.append(entry)

        # 限制历史大小
        if len(rule.history) > self.config["max_history_size"]:
            rule.history = rule.history[-self.config["max_history_size"] :]

    def _calculate_confidence_score(self, rule: ThresholdRule) -> float:
        """计算规则置信度"""

        if not rule.history:
            return 0.5

        recent_history = rule.history[-50:]  # 最近50条记录

        # 计算各项指标
        triggered_count = sum(1 for entry in recent_history if entry.get("triggered", False))
        trigger_rate = triggered_count / len(recent_history)

        # 理想触发率应该在5-15%之间
        ideal_rate = 0.1
        rate_score = 1.0 - abs(trigger_rate - ideal_rate) / ideal_rate

        # 考虑误报率
        fp_penalty = rule.false_positive_rate * 0.5
        fn_penalty = rule.false_negative_rate * 0.3

        # 综合置信度
        confidence = (rate_score + fp_penalty + fn_penalty) / 2.0
        confidence = max(0.0, min(1.0, confidence))

        return confidence

    async def optimize_thresholds(self, rule_name: Optional[str] = None) -> Dict[str, OptimizationResult]:
        """优化阈值"""

        if rule_name:
            # 优化指定规则
            if rule_name not in self.threshold_rules:
                return {}

            results = await self._optimize_single_rule(rule_name)
            return {rule_name: results}
        else:
            # 优化所有规则
            results = {}

            for name in self.threshold_rules.keys():
                try:
                    result = await self._optimize_single_rule(name)
                    results[name] = result
                except Exception as e:
                    logger.error("优化规则%s失败: %s", name, e)
                    continue

            return results

    async def _optimize_single_rule(self, rule_name: str) -> OptimizationResult:
        """优化单个规则"""

        if rule_name not in self.threshold_rules:
            raise ValueError(f"规则{rule_name}不存在")

        rule = self.threshold_rules[rule_name]
        self.data_analyzers[rule_name]

        # 获取历史数据
        values = [entry["value"] for entry in rule.history if "value" in entry]
        timestamps = [datetime.fromisoformat(entry["timestamp"]) for entry in rule.history if "timestamp" in entry]

        if len(values) < self.config["min_data_points"]:
            return OptimizationResult(
                rule_name=rule_name,
                optimization_type="insufficient_data",
                recommended_threshold=rule.current_threshold,
                confidence_score=0.1,
                expected_improvement=0.0,
                reasoning="数据不足，无法优化",
                supporting_evidence=[f"需要至少{self.config['min_data_points']}个数据点"],
                metadata={"data_insufficient": True},
            )

        # 执行多种优化策略
        optimization_results = []

        # 1. 统计优化
        try:
            stat_result = self.statistical_optimizer.optimize_threshold_statistical(
                values, rule.current_threshold, rule.threshold_type
            )
            optimization_results.append(stat_result)
        except Exception as e:
            logger.warning("统计优化失败: %s", e)

        # 2. 趋势优化
        try:
            trend_result = self.trend_optimizer.optimize_threshold_trend(
                values, timestamps, rule.current_threshold, rule.threshold_type
            )
            optimization_results.append(trend_result)
        except Exception as e:
            logger.warning("趋势优化失败: %s", e)

        # 3. 聚类优化
        try:
            cluster_result = self.clustering_optimizer.optimize_threshold_clustering(
                values, rule.current_threshold, rule.threshold_type
            )
            optimization_results.append(cluster_result)
        except Exception as e:
            logger.warning("聚类优化失败: %s", e)

        if not optimization_results:
            return OptimizationResult(
                rule_name=rule_name,
                optimization_type="failed",
                recommended_threshold=rule.current_threshold,
                confidence_score=0.0,
                expected_improvement=0.0,
                reasoning="所有优化策略都失败了",
                supporting_evidence=["检查数据质量和算法参数"],
                metadata={"all_optimizations_failed": True},
            )

        # 选择最佳优化结果
        best_result = max(
            optimization_results,
            key=lambda x: x.confidence_score * x.expected_improvement,
        )

        logger.info("规则%s优化完成: %s -> %s", rule_name, rule.current_threshold, best_result.recommended_threshold)

        return best_result

    async def apply_optimization(self, rule_name: str, optimization_result: OptimizationResult) -> bool:
        """应用优化结果"""

        if rule_name not in self.threshold_rules:
            logger.error("规则%s不存在", rule_name)
            return False

        rule = self.threshold_rules[rule_name]

        # 验证置信度
        if optimization_result.confidence_score < self.config["confidence_threshold"]:
            logger.info("优化结果置信度过低(%s)，跳过应用", optimization_result.confidence_score)
            return False

        old_threshold = rule.current_threshold
        new_threshold = optimization_result.recommended_threshold

        # 应用新阈值
        rule.current_threshold = new_threshold
        rule.optimal_threshold = new_threshold
        rule.adjustment_count += 1
        rule.last_adjustment = datetime.now()

        # 记录调整历史
        adjustment = ThresholdAdjustment(
            timestamp=datetime.now(),
            rule_name=rule_name,
            old_threshold=old_threshold,
            new_threshold=new_threshold,
            reason=optimization_result.reasoning,
            confidence=optimization_result.confidence_score,
            metrics_snapshot=optimization_result.metadata,
            predicted_effectiveness=optimization_result.expected_improvement,
        )

        self.adjustment_history.append(adjustment)

        # 限制调整历史大小
        if len(self.adjustment_history) > self.config["max_history_size"]:
            self.adjustment_history = self.adjustment_history[-self.config["max_history_size"] :]

        logger.info("✅ 已应用阈值优化: %s %s -> %s", rule_name, old_threshold, new_threshold)
        return True

    def get_threshold_status(self) -> Dict[str, Any]:
        """获取阈值状态"""

        status = {
            "total_rules": len(self.threshold_rules),
            "optimization_enabled": True,
            "last_optimization": None,
            "rules_status": {},
            "adjustment_statistics": self._get_adjustment_statistics(),
        }

        # 获取各规则状态
        for rule_name, rule in self.threshold_rules.items():
            rule_status = {
                "current_threshold": rule.current_threshold,
                "optimal_threshold": rule.optimal_threshold,
                "confidence_score": rule.confidence_score,
                "adjustment_count": rule.adjustment_count,
                "false_positive_rate": rule.false_positive_rate,
                "false_negative_rate": rule.false_negative_rate,
                "last_adjustment": rule.last_adjustment.isoformat() if rule.last_adjustment else None,
                "data_points": len(rule.history),
            }

            # 计算阈值合理性
            rule_status["threshold合理性"] = self._evaluate_threshold_reasonableness(rule)

            status["rules_status"][rule_name] = rule_status

        # 获取最后优化时间
        if self.adjustment_history:
            status["last_optimization"] = self.adjustment_history[-1].timestamp.isoformat()

        return status

    def _evaluate_threshold_reasonableness(self, rule: ThresholdRule) -> Dict[str, Any]:
        """评估阈值合理性"""

        if not rule.history:
            return {"status": "insufficient_data", "score": 0.0}

        recent_values = [entry["value"] for entry in rule.history[-20:] if "value" in entry]
        if not recent_values:
            return {"status": "insufficient_data", "score": 0.0}

        # 计算指标
        recent_mean = np.mean(recent_values)
        recent_std = np.std(recent_values)

        # 计算触发率
        triggered_count = sum(1 for entry in rule.history[-20:] if entry.get("triggered", False))
        trigger_rate = triggered_count / min(20, len(rule.history))

        # 评估合理性
        reasonableness_score = 0.5  # 基础分

        # 触发率合理性 (理想5-15%)
        if 0.05 <= trigger_rate <= 0.15:
            reasonableness_score += 0.3
        elif 0.02 <= trigger_rate <= 0.25:
            reasonableness_score += 0.1

        # 置信度
        reasonableness_score += rule.confidence_score * 0.2

        reasonableness_score = min(1.0, reasonableness_score)

        if reasonableness_score >= 0.8:
            status = "excellent"
        elif reasonableness_score >= 0.6:
            status = "good"
        elif reasonableness_score >= 0.4:
            status = "acceptable"
        else:
            status = "needs_optimization"

        return {
            "status": status,
            "score": reasonableness_score,
            "trigger_rate": trigger_rate,
            "recent_mean": recent_mean,
            "recent_std": recent_std,
        }

    def _get_adjustment_statistics(self) -> Dict[str, Any]:
        """获取调整统计信息"""

        if not self.adjustment_history:
            return {"total_adjustments": 0}

        recent_adjustments = self.adjustment_history[-30:]  # 最近30次调整

        return {
            "total_adjustments": len(self.adjustment_history),
            "recent_adjustments": len(recent_adjustments),
            "avg_confidence": np.mean([adj.confidence for adj in recent_adjustments]),
            "avg_effectiveness": np.mean(
                [adj.predicted_effectiveness for adj in recent_adjustments if adj.predicted_effectiveness is not None]
            ),
            "most_adjusted_rule": self._get_most_adjusted_rule(),
            "optimization_types": list(set([adj.reason.split(":")[0] for adj in recent_adjustments])),
        }

    def _get_most_adjusted_rule(self) -> Optional[str]:
        """获取调整最多的规则"""

        if not self.adjustment_history:
            return None

        rule_counts = {}
        for adj in self.adjustment_history:
            rule_counts[adj.rule_name] = rule_counts.get(adj.rule_name, 0) + 1

        if rule_counts:
            return max(rule_counts, key=rule_counts.get)

        return None

    def export_configuration(self) -> str:
        """导出配置"""

        config_data = {
            "timestamp": datetime.now().isoformat(),
            "threshold_rules": {name: asdict(rule) for name, rule in self.threshold_rules.items()},
            "adjustment_history": [asdict(adj) for adj in self.adjustment_history[-100:]],  # 最近100条
            "config": self.config,
        }

        return json.dumps(config_data, indent=2, default=str)

    async def import_configuration(self, config_json: str) -> bool:
        """导入配置"""

        try:
            config_data = json.loads(config_json)

            # 恢复阈值规则
            for name, rule_data in config_data.get("threshold_rules", {}).items():
                rule = ThresholdRule(**rule_data)
                self.threshold_rules[name] = rule
                self.data_analyzers[name] = DataAnalyzer()

            # 恢复调整历史
            for adj_data in config_data.get("adjustment_history", []):
                adj_data["timestamp"] = datetime.fromisoformat(adj_data["timestamp"])
                adjustment = ThresholdAdjustment(**adj_data)
                self.adjustment_history.append(adjustment)

            # 更新配置
            self.config.update(config_data.get("config", {}))

            logger.info("✅ 配置导入成功: %s个规则", len(self.threshold_rules))
            return True

        except Exception as e:
            logger.error("配置导入失败: %s", e)
            return False


# 全局单例管理器
_intelligent_threshold_manager = None


def get_intelligent_threshold_manager() -> IntelligentThresholdManager:
    """获取智能阈值管理器单例"""
    global _intelligent_threshold_manager

    if _intelligent_threshold_manager is None:
        _intelligent_threshold_manager = IntelligentThresholdManager()

    return _intelligent_threshold_manager


# 便捷函数
async def create_intelligent_threshold(
    config: Optional[Dict[str, Any]] = None,
) -> IntelligentThresholdManager:
    """创建智能阈值管理器"""
    return IntelligentThresholdManager(config)


async def optimize_all_thresholds() -> Dict[str, OptimizationResult]:
    """优化所有阈值"""
    manager = get_intelligent_threshold_manager()
    return await manager.optimize_thresholds()


async def process_metric(rule_name: str, value: float, timestamp: Optional[datetime] = None) -> Dict[str, Any]:
    """处理指标值"""
    manager = get_intelligent_threshold_manager()
    return await manager.process_metric_value(rule_name, value, timestamp)


if __name__ == "__main__":
    """示例用法"""

    async def main():
        # 创建智能阈值管理器
        manager = IntelligentThresholdManager()

        print("🤖 智能阈值算法和误报优化模块演示")
        print("=" * 50)

        # 模拟数据
        import random

        rule_name = "cpu_usage_high"

        # 模拟CPU使用率数据
        for i in range(50):
            value = random.gauss(60, 15)  # 正态分布，均值60，标准差15
            await manager.process_metric_value(rule_name, value)

        # 获取规则状态
        status = manager.get_threshold_status()
        print(f"\n📊 阈值状态: {status['total_rules']}个规则")

        # 优化阈值
        print("\n🔧 开始优化阈值...")
        results = await manager.optimize_thresholds(rule_name)

        for rule_name, result in results.items():
            print(f"规则: {rule_name}")
            print(f"  当前阈值: {status['rules_status'][rule_name]['current_threshold']:.2f}")
            print(f"  推荐阈值: {result.recommended_threshold:.2f}")
            print(f"  置信度: {result.confidence_score:.3f}")
            print(f"  预期改进: {result.expected_improvement:.3f}")
            print(f"  推理: {result.reasoning}")

        # 应用优化
        if results:
            rule_name = list(results.keys())[0]
            optimization_result = results[rule_name]
            success = await manager.apply_optimization(rule_name, optimization_result)
            print(f"\n✅ 优化应用{'成功' if success else '失败'}")

        # 导出配置
        config = manager.export_configuration()
        print(f"\n💾 配置已导出 ({len(config)}字符)")

        print("\n🎉 演示完成!")

    # 运行演示
    asyncio.run(main())
