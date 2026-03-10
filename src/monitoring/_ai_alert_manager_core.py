from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from ._ai_alert_handlers import LogAlertHandler
from ._ai_alert_models import Alert, AlertRule, AlertSeverity, AlertType, IAlertHandler, SystemMetrics



def _load_default_alert_rules(self) -> List[AlertRule]:
    return [
        AlertRule(
            name="CPU使用率过高",
            alert_type=AlertType.SYSTEM_RESOURCE_HIGH,
            severity=AlertSeverity.WARNING,
            threshold=80.0,
            duration_seconds=60,
            enabled=True,
            description="CPU使用率持续超过80%",
        ),
        AlertRule(
            name="GPU内存使用率过高",
            alert_type=AlertType.GPU_MEMORY_HIGH,
            severity=AlertSeverity.WARNING,
            threshold=85.0,
            duration_seconds=30,
            enabled=True,
            description="GPU内存使用率持续超过85%",
        ),
        AlertRule(
            name="AI策略胜率异常",
            alert_type=AlertType.STRATEGY_ANOMALY,
            severity=AlertSeverity.CRITICAL,
            threshold=0.3,
            duration_seconds=300,
            enabled=True,
            description="AI策略胜率持续低于30%",
        ),
        AlertRule(
            name="AI策略回撤过大",
            alert_type=AlertType.STRATEGY_ANOMALY,
            severity=AlertSeverity.CRITICAL,
            threshold=5.0,
            duration_seconds=180,
            enabled=True,
            description="AI策略最大回撤持续超过5%",
        ),
        AlertRule(
            name="数据质量异常",
            alert_type=AlertType.DATA_QUALITY_ISSUE,
            severity=AlertSeverity.WARNING,
            threshold=0.8,
            duration_seconds=120,
            enabled=True,
            description="数据质量评分持续低于80%",
        ),
        AlertRule(
            name="慢查询检测",
            alert_type=AlertType.SLOW_QUERY,
            severity=AlertSeverity.WARNING,
            threshold=5000.0,
            duration_seconds=30,
            enabled=True,
            description="查询执行时间超过5秒",
        ),
    ]



def add_alert_handler(self, handler: IAlertHandler):
    self.alert_handlers.append(handler)
    self._logger.info("✅ 添加告警处理器: %s", handler.__class__.__name__)



def add_alert_rule(self, rule: AlertRule):
    self.alert_rules.append(rule)
    self._logger.info("✅ 添加自定义告警规则: %s", rule.name)



def remove_alert_rule(self, rule_name: str):
    self.alert_rules = [rule for rule in self.alert_rules if rule.name != rule_name]
    if rule_name in self.active_alerts:
        del self.active_alerts[rule_name]
    self._logger.info("🗑️ 移除告警规则: %s", rule_name)


async def check_alert_conditions(self, metrics: SystemMetrics):
    for rule in self.alert_rules:
        if not rule.enabled:
            continue

        try:
            metric_value = self._get_metric_value(metrics, rule.alert_type)
            if metric_value is None:
                continue

            if self._check_threshold(metric_value, rule):
                await self._trigger_alert(rule, metrics, metric_value)
            else:
                await self._resolve_alert(rule)
        except Exception as error:
            self._logger.error("❌ 告警规则 %s 检查失败: %s", rule.name, error)



def _get_metric_value(self, metrics: SystemMetrics, alert_type: AlertType) -> Optional[float]:
    if alert_type == AlertType.SYSTEM_RESOURCE_HIGH:
        return metrics.cpu_usage
    if alert_type == AlertType.GPU_MEMORY_HIGH:
        return (metrics.gpu_memory_used / metrics.gpu_memory_total * 100) if metrics.gpu_memory_total > 0 else 0
    if alert_type == AlertType.STRATEGY_ANOMALY:
        return metrics.ai_strategy_metrics.get("win_rate", 0)
    if alert_type == AlertType.DATA_QUALITY_ISSUE:
        return metrics.trading_metrics.get("data_quality_score", 0)
    if alert_type == AlertType.PERFORMANCE_DEGRADATION:
        return metrics.trading_metrics.get("sharpe_ratio", 0)
    if alert_type == AlertType.SLOW_QUERY:
        return metrics.trading_metrics.get("last_query_time", 0)
    return None



def _check_threshold(self, metric_value: float, rule: AlertRule) -> bool:
    if rule.alert_type in {AlertType.GPU_MEMORY_HIGH, AlertType.SYSTEM_RESOURCE_HIGH, AlertType.SLOW_QUERY}:
        return metric_value > rule.threshold
    if rule.alert_type in {
        AlertType.STRATEGY_ANOMALY,
        AlertType.DATA_QUALITY_ISSUE,
        AlertType.PERFORMANCE_DEGRADATION,
    }:
        return metric_value < rule.threshold
    return False


async def _trigger_alert(self, rule: AlertRule, metrics: SystemMetrics, metric_value: float):
    alert_id = f"{rule.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    if rule.name in self.active_alerts:
        return

    alert = Alert(
        id=alert_id,
        rule_name=rule.name,
        alert_type=rule.alert_type,
        severity=rule.severity,
        message=self._generate_alert_message(rule, metric_value),
        timestamp=datetime.now(),
        metrics={
            "current_value": metric_value,
            "threshold": rule.threshold,
            "duration_seconds": rule.duration_seconds,
            "system_metrics": self._serialize_metrics(metrics),
        },
    )

    self.active_alerts[rule.name] = alert
    self._save_alert_history(alert)
    self._update_alert_stats(alert)
    await self._handle_alert(alert)
    self._logger.warning("🚨 告警触发: %s", alert.message)


async def _resolve_alert(self, rule: AlertRule):
    if rule.name in self.active_alerts:
        alert = self.active_alerts[rule.name]
        alert.resolved = True
        alert.resolved_at = datetime.now()
        del self.active_alerts[rule.name]
        self._save_alert_history(alert)
        self.alert_stats["resolved_alerts"] += 1
        self._logger.info("✅ 告警解决: %s", rule.name)



def _generate_alert_message(self, rule: AlertRule, metric_value: float) -> str:
    if rule.alert_type == AlertType.GPU_MEMORY_HIGH:
        return f"GPU内存使用率过高: {metric_value:.1f}% (阈值: {rule.threshold}%)"
    if rule.alert_type == AlertType.SYSTEM_RESOURCE_HIGH:
        return f"CPU使用率过高: {metric_value:.1f}% (阈值: {rule.threshold}%)"
    if rule.alert_type == AlertType.STRATEGY_ANOMALY:
        return f"AI策略胜率异常: {metric_value:.1%} (阈值: {rule.threshold}%)"
    if rule.alert_type == AlertType.DATA_QUALITY_ISSUE:
        return f"数据质量异常: {metric_value:.1%} (阈值: {rule.threshold}%)"
    if rule.alert_type == AlertType.SLOW_QUERY:
        return f"慢查询检测: {metric_value:.0f}ms (阈值: {rule.threshold:.0f}ms)"
    return f"{rule.name}: {metric_value:.2f} (阈值: {rule.threshold})"



def _serialize_metrics(self, metrics: SystemMetrics) -> Dict[str, Any]:
    return {
        "timestamp": metrics.timestamp.isoformat(),
        "cpu_usage": metrics.cpu_usage,
        "memory_usage": metrics.memory_usage,
        "gpu_utilization": metrics.gpu_utilization,
        "ai_strategies_count": len(metrics.ai_strategy_metrics),
        "trading_metrics": metrics.trading_metrics,
    }



def _save_alert_history(self, alert: Alert):
    self.alert_history.append(alert)
    if len(self.alert_history) > self.max_history_size:
        self.alert_history = self.alert_history[-self.max_history_size :]

    if self.monitoring_db:
        try:
            self.monitoring_db.record_alert(
                alert_id=alert.id,
                alert_type=alert.alert_type.value,
                severity=alert.severity.value,
                message=alert.message,
                source="AIAlertManager",
                additional_data=alert.to_dict(),
            )
        except Exception as error:
            self._logger.error("❌ 保存告警到数据库失败: %s", error)



def _update_alert_stats(self, alert: Alert):
    self.alert_stats["total_alerts"] += 1
    if alert.severity == AlertSeverity.CRITICAL:
        self.alert_stats["critical_alerts"] += 1
    elif alert.severity == AlertSeverity.WARNING:
        self.alert_stats["warning_alerts"] += 1
    else:
        self.alert_stats["info_alerts"] += 1


async def _handle_alert(self, alert: Alert):
    for handler in self.alert_handlers:
        try:
            success = await handler.handle_alert(alert)
            if not success:
                self._logger.error("❌ 告警处理器 %s 处理失败", handler.__class__.__name__)
        except Exception as error:
            self._logger.error("❌ 告警处理器异常: %s", error)



def get_active_alerts(self) -> List[Alert]:
    return list(self.active_alerts.values())



def acknowledge_alert(self, alert_id: str, acknowledged_by: str = "system") -> bool:
    for alert in self.alert_history:
        if alert.id == alert_id:
            alert.acknowledged = True
            alert.acknowledged_at = datetime.now()
            alert.acknowledged_by = acknowledged_by
            self._logger.info("✅ 告警已确认: %s by %s", alert_id, acknowledged_by)
            return True
    return False



def get_alert_summary(self) -> Dict[str, Any]:
    return {
        "active_alerts_count": len(self.active_alerts),
        "total_alerts": self.alert_stats["total_alerts"],
        "critical_alerts": self.alert_stats["critical_alerts"],
        "warning_alerts": self.alert_stats["warning_alerts"],
        "info_alerts": self.alert_stats["info_alerts"],
        "resolved_alerts": self.alert_stats["resolved_alerts"],
        "alert_rules_count": len(self.alert_rules),
        "enabled_rules_count": len([rule for rule in self.alert_rules if rule.enabled]),
        "active_alert_types": list(self.active_alerts.keys()),
    }


async def test_all_handlers(self) -> Dict[str, bool]:
    results = {}
    for handler in self.alert_handlers:
        try:
            results[handler.__class__.__name__] = await handler.test_connection()
        except Exception as error:
            self._logger.error("❌ 处理器 %s 测试失败: %s", handler.__class__.__name__, error)
            results[handler.__class__.__name__] = False
    return results



def get_alert_rules(self) -> List[AlertRule]:
    return self.alert_rules.copy()



def update_alert_rule(self, rule_name: str, updates: Dict[str, Any]) -> bool:
    for rule in self.alert_rules:
        if rule.name == rule_name:
            for key, value in updates.items():
                if hasattr(rule, key):
                    setattr(rule, key, value)
            self._logger.info("✅ 更新告警规则: %s", rule_name)
            return True
    return False



def initialize_manager_state(self):
    self.alert_rules = self._load_default_alert_rules()
    self.active_alerts = {}
    self.alert_handlers = []
    self.alert_history = []
    self.max_history_size = 10000
    self.alert_stats = {
        "total_alerts": 0,
        "critical_alerts": 0,
        "warning_alerts": 0,
        "info_alerts": 0,
        "resolved_alerts": 0,
    }
    self.add_alert_handler(LogAlertHandler())
    self._logger.info("✅ AIAlertManager initialized")
