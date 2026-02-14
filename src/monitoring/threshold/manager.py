"""智能阈值管理器 - 主管理器"""

import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

from .dataclasses import ThresholdConfig, ThresholdResult, OptimizationHistory
from .data_analyzer import DataAnalyzer
from .statistical_optimizer import StatisticalOptimizer
from .advanced_optimizers import TrendOptimizer, ClusteringOptimizer

logger = logging.getLogger(__name__)
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


