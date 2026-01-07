"""
数据质量监控框架 (Week 1 Day 1)
定义核心监控指标：数据源可用性、数据延迟、数据完整性、数据准确性
"""

import asyncio
import logging
import statistics
import time
from abc import ABC, abstractmethod
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


logger = logging.getLogger(__name__)


class DataQualityLevel(str, Enum):
    """数据质量等级"""

    EXCELLENT = "excellent"  # 95-100%
    GOOD = "good"  # 85-94%
    FAIR = "fair"  # 70-84%
    POOR = "poor"  # 50-69%
    CRITICAL = "critical"  # 0-49%


class AlertSeverity(str, Enum):
    """告警严重程度"""

    INFO = "info"  # 信息性告警
    WARNING = "warning"  # 警告
    ERROR = "error"  # 错误
    CRITICAL = "critical"  # 严重错误


@dataclass
class DataQualityMetric:
    """数据质量指标"""

    name: str
    value: float
    threshold_warning: float
    threshold_error: float
    threshold_critical: float
    unit: str
    description: str
    last_updated: datetime = field(default_factory=datetime.now)
    trend: List[float] = field(default_factory=list)  # 最近30个值用于趋势分析
    quality_level: DataQualityLevel = DataQualityLevel.EXCELLENT

    def update_value(self, new_value: float) -> None:
        """更新指标值并计算质量等级"""
        self.value = new_value
        self.last_updated = datetime.now()

        # 更新趋势数据（保留最近30个值）
        self.trend.append(new_value)
        if len(self.trend) > 30:
            self.trend.pop(0)

        # 计算质量等级
        if new_value >= 95:
            self.quality_level = DataQualityLevel.EXCELLENT
        elif new_value >= 85:
            self.quality_level = DataQualityLevel.GOOD
        elif new_value >= 70:
            self.quality_level = DataQualityLevel.FAIR
        elif new_value >= 50:
            self.quality_level = DataQualityLevel.POOR
        else:
            self.quality_level = DataQualityLevel.CRITICAL

    def get_severity(self) -> AlertSeverity:
        """获取告警严重程度"""
        if self.value >= self.threshold_critical:
            return AlertSeverity.CRITICAL
        elif self.value >= self.threshold_error:
            return AlertSeverity.ERROR
        elif self.value >= self.threshold_warning:
            return AlertSeverity.WARNING
        else:
            return AlertSeverity.INFO

    def get_trend_direction(self) -> str:
        """获取趋势方向"""
        if len(self.trend) < 2:
            return "stable"

        recent_values = self.trend[-5:]  # 最近5个值
        if len(recent_values) < 2:
            return "stable"

        avg_earlier = statistics.mean(recent_values[: len(recent_values) // 2])
        avg_later = statistics.mean(recent_values[len(recent_values) // 2 :])

        if avg_later > avg_earlier * 1.05:
            return "improving"
        elif avg_later < avg_earlier * 0.95:
            return "degrading"
        else:
            return "stable"


@dataclass
class DataQualityAlert:
    """数据质量告警"""

    id: str
    metric_name: str
    severity: AlertSeverity
    message: str
    source: str
    timestamp: datetime = field(default_factory=datetime.now)
    acknowledged: bool = False
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class DataSourceQualityMetrics:
    """数据源质量指标集合"""

    def __init__(self, source_name: str):
        self.source_name = source_name
        self.metrics: Dict[str, DataQualityMetric] = {}
        self.alerts: List[DataQualityAlert] = []

        # 初始化核心指标
        self._initialize_core_metrics()

    def _initialize_core_metrics(self):
        """初始化核心质量指标"""
        core_metrics = [
            ("availability", 100.0, 95.0, 90.0, 85.0, "%", "数据源可用性百分比"),
            ("response_time", 100.0, 500.0, 1000.0, 2000.0, "ms", "平均响应时间"),
            ("success_rate", 100.0, 95.0, 90.0, 85.0, "%", "请求成功率"),
            ("data_freshness", 100.0, 300.0, 600.0, 1800.0, "seconds", "数据延迟时间"),
            ("data_completeness", 100.0, 95.0, 90.0, 85.0, "%", "数据完整性百分比"),
            ("error_rate", 0.0, 1.0, 5.0, 10.0, "%", "错误率百分比"),
            ("data_consistency", 100.0, 95.0, 90.0, 85.0, "%", "数据一致性百分比"),
            ("cache_hit_rate", 100.0, 80.0, 60.0, 40.0, "%", "缓存命中率"),
        ]

        for name, default_val, warning, error, critical, unit, desc in core_metrics:
            self.metrics[name] = DataQualityMetric(
                name=name,
                value=default_val,
                threshold_warning=warning,
                threshold_error=error,
                threshold_critical=critical,
                unit=unit,
                description=desc,
            )

    def update_metric(self, metric_name: str, value: float) -> Optional[DataQualityAlert]:
        """更新指标并生成告警"""
        if metric_name not in self.metrics:
            logger.warning(f"Unknown metric: {metric_name}")
            return None

        metric = self.metrics[metric_name]
        metric.get_severity()
        metric.update_value(value)
        new_severity = metric.get_severity()

        # 生成告警
        alert = None
        if new_severity.value in ["error", "critical"]:
            alert = DataQualityAlert(
                id=f"{self.source_name}_{metric_name}_{int(time.time())}",
                metric_name=metric_name,
                severity=new_severity,
                message=(
                    f"{metric.description}: {value}{metric.unit} (threshold: {metric.threshold_critical}{metric.unit})"
                ),
                source=self.source_name,
                metadata={
                    "current_value": value,
                    "threshold": metric.threshold_critical,
                    "trend_direction": metric.get_trend_direction(),
                },
            )
            self.alerts.append(alert)

            # 保持最近100个告警
            if len(self.alerts) > 100:
                self.alerts = self.alerts[-100:]

        return alert

    def get_overall_quality_score(self) -> float:
        """计算整体质量评分"""
        if not self.metrics:
            return 0.0

        # 核心指标权重
        weights = {
            "availability": 0.25,
            "success_rate": 0.20,
            "response_time": 0.15,
            "data_freshness": 0.15,
            "data_completeness": 0.15,
            "error_rate": 0.10,
        }

        total_score = 0.0
        total_weight = 0.0

        for metric_name, weight in weights.items():
            if metric_name in self.metrics:
                metric = self.metrics[metric_name]

                # 对于响应时间和延迟等指标，值越小越好
                if metric_name in ["response_time", "data_freshness", "error_rate"]:
                    normalized_score = max(0, 100 - (metric.value / metric.threshold_critical) * 100)
                else:
                    normalized_score = min(100, metric.value)

                total_score += normalized_score * weight
                total_weight += weight

        return total_score / total_weight if total_weight > 0 else 0.0

    def get_active_alerts(self) -> List[DataQualityAlert]:
        """获取活跃告警"""
        return [alert for alert in self.alerts if not alert.resolved]

    def acknowledge_alert(self, alert_id: str) -> bool:
        """确认告警"""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.acknowledged = True
                return True
        return False

    def resolve_alert(self, alert_id: str) -> bool:
        """解决告警"""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.resolved = True
                alert.resolved_at = datetime.now()
                return True
        return False


class IDataQualityRule(ABC):
    """数据质量规则接口"""

    @abstractmethod
    async def evaluate(self, data: Any, source: str) -> Dict[str, Any]:
        """评估数据质量"""
        pass

    @abstractmethod
    def get_name(self) -> str:
        """获取规则名称"""
        pass

    @abstractmethod
    def get_description(self) -> str:
        """获取规则描述"""
        pass


class SchemaValidationRule(IDataQualityRule):
    """Schema验证规则"""

    def __init__(self, required_fields: List[str], field_types: Dict[str, type]):
        self.required_fields = required_fields
        self.field_types = field_types

    async def evaluate(self, data: Any, source: str) -> Dict[str, Any]:
        """验证数据schema"""
        if not isinstance(data, dict):
            return {
                "passed": False,
                "score": 0.0,
                "issues": ["Data is not a dictionary"],
                "details": {},
            }

        issues = []
        passed_fields = 0
        total_fields = len(self.required_fields)

        # 检查必需字段
        for field_name in self.required_fields:
            if field_name not in data:
                issues.append(f"Missing required field: {field_name}")
            else:
                value = data[field_name]
                expected_type = self.field_types.get(field_name, str)

                if not isinstance(value, expected_type):
                    issues.append(
                        f"Field {field} type mismatch: expected {expected_type.__name__}, got {type(value).__name__}"
                    )
                else:
                    passed_fields += 1

        score = (passed_fields / total_fields * 100) if total_fields > 0 else 0

        return {
            "passed": len(issues) == 0,
            "score": score,
            "issues": issues,
            "details": {
                "required_fields": len(self.required_fields),
                "passed_fields": passed_fields,
                "total_fields": total_fields,
            },
        }

    def get_name(self) -> str:
        return "schema_validation"

    def get_description(self) -> str:
        return "Validates data schema and required fields"


class DataFreshnessRule(IDataQualityRule):
    """数据新鲜度规则"""

    def __init__(self, timestamp_field: str = "timestamp", max_age_seconds: int = 300):
        self.timestamp_field = timestamp_field
        self.max_age_seconds = max_age_seconds

    async def evaluate(self, data: Any, source: str) -> Dict[str, Any]:
        """检查数据新鲜度"""
        if not isinstance(data, dict) or self.timestamp_field not in data:
            return {
                "passed": False,
                "score": 0.0,
                "issues": [f"Timestamp field '{self.timestamp_field}' not found"],
                "details": {},
            }

        try:
            timestamp_str = data[self.timestamp_field]
            if isinstance(timestamp_str, str):
                timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            else:
                timestamp = timestamp_str

            now = datetime.now()
            age_seconds = (now - timestamp).total_seconds()

            # 计算新鲜度分数（越新越好）
            if age_seconds <= 60:
                score = 100.0
            elif age_seconds <= self.max_age_seconds:
                score = 100.0 * (1 - (age_seconds / self.max_age_seconds))
            else:
                score = 0.0

            passed = age_seconds <= self.max_age_seconds
            issues = [] if passed else [f"Data is {age_seconds:.1f}s old, exceeds threshold of {self.max_age_seconds}s"]

            return {
                "passed": passed,
                "score": score,
                "issues": issues,
                "details": {
                    "age_seconds": age_seconds,
                    "max_age_seconds": self.max_age_seconds,
                    "timestamp": timestamp.isoformat(),
                },
            }

        except Exception as e:
            return {
                "passed": False,
                "score": 0.0,
                "issues": [f"Failed to parse timestamp: {str(e)}"],
                "details": {},
            }

    def get_name(self) -> str:
        return "data_freshness"

    def get_description(self) -> str:
        return "Checks if data is fresh enough based on timestamp"


class DataConsistencyRule(IDataQualityRule):
    """数据一致性规则"""

    def __init__(self, consistency_checks: List[Callable[[Dict[str, Any]], bool]]):
        self.consistency_checks = consistency_checks

    async def evaluate(self, data: Any, source: str) -> Dict[str, Any]:
        """检查数据一致性"""
        if not isinstance(data, dict):
            return {
                "passed": False,
                "score": 0.0,
                "issues": ["Data is not a dictionary"],
                "details": {},
            }

        issues = []
        passed_checks = 0

        for i, check_func in enumerate(self.consistency_checks):
            try:
                if check_func(data):
                    passed_checks += 1
                else:
                    issues.append(f"Consistency check {i + 1} failed")
            except Exception as e:
                issues.append(f"Consistency check {i + 1} error: {str(e)}")

        total_checks = len(self.consistency_checks)
        score = (passed_checks / total_checks * 100) if total_checks > 0 else 0

        return {
            "passed": len(issues) == 0,
            "score": score,
            "issues": issues,
            "details": {"total_checks": total_checks, "passed_checks": passed_checks},
        }

    def get_name(self) -> str:
        return "data_consistency"

    def get_description(self) -> str:
        return "Validates data consistency using custom checks"


class DataQualityMonitor:
    """数据质量监控器"""

    def __init__(self):
        self.source_metrics: Dict[str, DataSourceQualityMetrics] = {}
        self.rules: List[IDataQualityRule] = []
        self.evaluation_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.alert_callbacks: List[Callable[[DataQualityAlert], None]] = []
        self.monitoring_enabled = True

        # 初始化默认规则
        self._initialize_default_rules()

    def _initialize_default_rules(self):
        """初始化默认数据质量规则"""
        # Schema验证规则
        self.rules.append(
            SchemaValidationRule(
                required_fields=["timestamp", "status"],
                field_types={"timestamp": str, "status": str},
            )
        )

        # 数据新鲜度规则
        self.rules.append(DataFreshnessRule(timestamp_field="timestamp", max_age_seconds=300))

        # 数据一致性规则
        consistency_checks = [
            lambda data: "status" in data and data["status"] in ["success", "ok", "healthy"],
            lambda data: "timestamp" in data and len(data["timestamp"]) > 0,
        ]
        self.rules.append(DataConsistencyRule(consistency_checks))

    def get_or_create_source_metrics(self, source_name: str) -> DataSourceQualityMetrics:
        """获取或创建数据源指标"""
        if source_name not in self.source_metrics:
            self.source_metrics[source_name] = DataSourceQualityMetrics(source_name)
        return self.source_metrics[source_name]

    async def evaluate_data_quality(
        self,
        data: Any,
        source: str,
        response_time: Optional[float] = None,
        success: bool = True,
    ) -> Dict[str, Any]:
        """评估数据质量"""
        if not self.monitoring_enabled:
            return {"monitored": False}

        source_metrics = self.get_or_create_source_metrics(source)

        # 执行规则评估
        rule_results = []
        total_score = 0.0
        total_rules = 0

        for rule in self.rules:
            try:
                result = await rule.evaluate(data, source)
                rule_results.append(
                    {
                        "rule": rule.get_name(),
                        "description": rule.get_description(),
                        **result,
                    }
                )

                total_score += result["score"]
                total_rules += 1

            except Exception as e:
                logger.error(f"Rule {rule.get_name()} evaluation failed: {e}")
                rule_results.append(
                    {
                        "rule": rule.get_name(),
                        "description": rule.get_description(),
                        "passed": False,
                        "score": 0.0,
                        "issues": [f"Evaluation error: {str(e)}"],
                        "details": {},
                    }
                )
                total_rules += 1

        # 计算平均质量分数
        avg_quality_score = total_score / total_rules if total_rules > 0 else 0.0

        # 更新数据源指标
        if response_time is not None:
            alert = source_metrics.update_metric("response_time", response_time)
            if alert:
                await self._trigger_alert(alert)

        success_rate = 100.0 if success else 0.0
        alert = source_metrics.update_metric("success_rate", success_rate)
        if alert:
            await self._trigger_alert(alert)

        # 更新数据完整性分数
        alert = source_metrics.update_metric("data_completeness", avg_quality_score)
        if alert:
            await self._trigger_alert(alert)

        # 保存评估历史
        evaluation_record = {
            "timestamp": datetime.now().isoformat(),
            "quality_score": avg_quality_score,
            "rule_results": rule_results,
            "response_time": response_time,
            "success": success,
        }
        self.evaluation_history[source].append(evaluation_record)

        return {
            "monitored": True,
            "source": source,
            "quality_score": avg_quality_score,
            "rule_results": rule_results,
            "response_time": response_time,
            "success": success,
        }

    async def update_source_availability(self, source: str, available: bool) -> None:
        """更新数据源可用性"""
        source_metrics = self.get_or_create_source_metrics(source)
        availability = 100.0 if available else 0.0

        alert = source_metrics.update_metric("availability", availability)
        if alert:
            await self._trigger_alert(alert)

    async def update_source_error_rate(self, source: str, error_rate: float) -> None:
        """更新数据源错误率"""
        source_metrics = self.get_or_create_source_metrics(source)

        alert = source_metrics.update_metric("error_rate", error_rate)
        if alert:
            await self._trigger_alert(alert)

    async def update_data_freshness(self, source: str, age_seconds: float) -> None:
        """更新数据新鲜度"""
        source_metrics = self.get_or_create_source_metrics(source)

        # 新鲜度分数：越新越好
        if age_seconds <= 60:
            freshness_score = 100.0
        elif age_seconds <= 300:  # 5分钟
            freshness_score = 100.0 * (1 - (age_seconds - 60) / 240)
        elif age_seconds <= 1800:  # 30分钟
            freshness_score = 40.0 * (1 - (age_seconds - 300) / 1500)
        else:
            freshness_score = 0.0

        alert = source_metrics.update_metric("data_freshness", freshness_score)
        if alert:
            await self._trigger_alert(alert)

    async def _trigger_alert(self, alert: DataQualityAlert) -> None:
        """触发告警"""
        logger.warning(f"Data quality alert triggered: {alert.message}")

        # 通知所有注册的回调
        for callback in self.alert_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(alert)
                else:
                    callback(alert)
            except Exception as e:
                logger.error(f"Alert callback failed: {e}")

    def add_alert_callback(self, callback: Callable[[DataQualityAlert], None]) -> None:
        """添加告警回调"""
        self.alert_callbacks.append(callback)

    def get_source_metrics(self, source: str) -> Optional[DataSourceQualityMetrics]:
        """获取数据源指标"""
        return self.source_metrics.get(source)

    def get_all_source_metrics(self) -> Dict[str, DataSourceQualityMetrics]:
        """获取所有数据源指标"""
        return self.source_metrics.copy()

    def get_source_alerts(self, source: str) -> List[DataQualityAlert]:
        """获取数据源告警"""
        source_metrics = self.source_metrics.get(source)
        return source_metrics.get_active_alerts() if source_metrics else []

    def get_all_alerts(self) -> List[DataQualityAlert]:
        """获取所有活跃告警"""
        all_alerts = []
        for source_metrics in self.source_metrics.values():
            all_alerts.extend(source_metrics.get_active_alerts())

        # 按严重程度和时间排序
        severity_order = {"critical": 4, "error": 3, "warning": 2, "info": 1}
        all_alerts.sort(
            key=lambda a: (severity_order.get(a.severity.value, 0), a.timestamp),
            reverse=True,
        )

        return all_alerts

    def get_overall_health_summary(self) -> Dict[str, Any]:
        """获取整体健康状态摘要"""
        total_sources = len(self.source_metrics)
        healthy_sources = 0
        total_alerts = 0
        critical_alerts = 0

        quality_scores = []

        for source, metrics in self.source_metrics.items():
            overall_score = metrics.get_overall_quality_score()
            quality_scores.append(overall_score)

            if overall_score >= 90:
                healthy_sources += 1

            active_alerts = metrics.get_active_alerts()
            total_alerts += len(active_alerts)
            critical_alerts += sum(1 for a in active_alerts if a.severity == AlertSeverity.CRITICAL)

        avg_quality_score = statistics.mean(quality_scores) if quality_scores else 0.0

        return {
            "total_sources": total_sources,
            "healthy_sources": healthy_sources,
            "health_percentage": (healthy_sources / total_sources * 100) if total_sources > 0 else 0,
            "average_quality_score": avg_quality_score,
            "total_active_alerts": total_alerts,
            "critical_alerts": critical_alerts,
            "overall_health": (
                "healthy" if avg_quality_score >= 90 else "degraded" if avg_quality_score >= 70 else "unhealthy"
            ),
        }

    def add_quality_rule(self, rule: IDataQualityRule) -> None:
        """添加数据质量规则"""
        self.rules.append(rule)

    def remove_quality_rule(self, rule_name: str) -> bool:
        """移除数据质量规则"""
        for i, rule in enumerate(self.rules):
            if rule.get_name() == rule_name:
                self.rules.pop(i)
                return True
        return False

    def enable_monitoring(self) -> None:
        """启用监控"""
        self.monitoring_enabled = True

    def disable_monitoring(self) -> None:
        """禁用监控"""
        self.monitoring_enabled = False

    def is_monitoring_enabled(self) -> bool:
        """检查监控是否启用"""
        return self.monitoring_enabled


# 全局监控实例
_global_monitor: Optional[DataQualityMonitor] = None


def get_data_quality_monitor() -> DataQualityMonitor:
    """获取全局数据质量监控实例"""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = DataQualityMonitor()
    return _global_monitor


async def monitor_data_quality(
    data: Any, source: str, response_time: Optional[float] = None, success: bool = True
) -> Dict[str, Any]:
    """便捷函数：监控数据质量"""
    monitor = get_data_quality_monitor()
    return await monitor.evaluate_data_quality(data, source, response_time, success)


# 导出的主要接口
__all__ = [
    "DataQualityLevel",
    "AlertSeverity",
    "DataQualityMetric",
    "DataQualityAlert",
    "DataSourceQualityMetrics",
    "IDataQualityRule",
    "SchemaValidationRule",
    "DataFreshnessRule",
    "DataConsistencyRule",
    "DataQualityMonitor",
    "get_data_quality_monitor",
    "monitor_data_quality",
]
