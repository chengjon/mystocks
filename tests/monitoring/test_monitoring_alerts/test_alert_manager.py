"""
测试监控告警系统

提供全面的测试监控、告警管理和通知功能。
"""

import json
import logging
import queue
import smtplib
import statistics
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

import psutil
import requests
from jinja2 import Template
from pydantic import BaseModel, Field
from prometheus_client import Counter, Gauge, Histogram, start_http_server

from ..ai.test_data_manager import DataManager as AIDataManager

class TestAlertManager:
    """测试告警管理器"""

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
        self.config = self._load_config()
        self.monitor = TestMonitor(self.config)
        self.data_manager = AIDataManager()
        self.alert_rules: Dict[str, AlertRule] = {}
        self.notification_channels: Dict[str, NotificationChannel] = {}

    def _load_config(self) -> Dict[str, Any]:
        """加载配置"""
        default_config = {
            "max_metric_history": 1000,
            "alert_retention_days": 30,
            "default_channels": ["email"],
            "auto_suppress_duration": 60,  # 分钟
        }

        if self.config_path and Path(self.config_path).exists():
            with open(self.config_path, "r", encoding="utf-8") as f:
                user_config = json.load(f)
                default_config.update(user_config)

        return default_config

    def initialize_default_rules(self):
        """初始化默认告警规则"""
        default_rules = [
            AlertRule(
                id="test_failure_rate",
                name="测试失败率告警",
                description="测试失败率超过阈值",
                severity=AlertSeverity.HIGH,
                condition="average_above",
                threshold=0.1,  # 10%
                duration=300,  # 5分钟
                enabled=True,
                tags=["test", "performance"],
                notification_channels=["email"],
            ),
            AlertRule(
                id="test_execution_time",
                name="测试执行时间告警",
                description="测试执行时间过长",
                severity=AlertSeverity.MEDIUM,
                condition="average_above",
                threshold=300,  # 5分钟
                duration=600,  # 10分钟
                enabled=True,
                tags=["test", "performance"],
                notification_channels=["email"],
            ),
            AlertRule(
                id="memory_usage",
                name="内存使用率告警",
                description="内存使用率过高",
                severity=AlertSeverity.CRITICAL,
                condition="above_threshold",
                threshold=90,  # 90%
                duration=60,  # 1分钟
                enabled=True,
                tags=["system", "memory"],
                notification_channels=["email", "slack"],
            ),
            AlertRule(
                id="cpu_usage",
                name="CPU使用率告警",
                description="CPU使用率过高",
                severity=AlertSeverity.HIGH,
                condition="average_above",
                threshold=80,  # 80%
                duration=300,  # 5分钟
                enabled=True,
                tags=["system", "cpu"],
                notification_channels=["email"],
            ),
            AlertRule(
                id="error_rate",
                name="错误率告警",
                description="系统错误率过高",
                severity=AlertSeverity.CRITICAL,
                condition="average_above",
                threshold=0.05,  # 5%
                duration=120,  # 2分钟
                enabled=True,
                tags=["system", "error"],
                notification_channels=["email", "slack"],
            ),
        ]

        for rule in default_rules:
            self.monitor.add_alert_rule(rule)
            self.alert_rules[rule.id] = rule

    def initialize_notification_channels(self):
        """初始化通知渠道"""
        # 邮件渠道
        email_config = self.config.get("email", {})
        if email_config:
            email_channel = EmailNotificationChannel(email_config)
            self.monitor.add_notification_channel("email", email_channel)
            self.notification_channels["email"] = email_channel

        # Webhook渠道
        webhook_config = self.config.get("webhook", {})
        if webhook_config:
            webhook_channel = WebhookNotificationChannel(webhook_config)
            self.monitor.add_notification_channel("webhook", webhook_channel)
            self.notification_channels["webhook"] = webhook_channel

        # Slack渠道
        slack_config = self.config.get("slack", {})
        if slack_config:
            slack_channel = SlackNotificationChannel(slack_config)
            self.monitor.add_notification_channel("slack", slack_channel)
            self.notification_channels["slack"] = slack_channel

    def record_test_metrics(
        self,
        test_name: str,
        execution_time: float,
        passed: bool,
        memory_mb: float,
        cpu_percent: float,
    ):
        """记录测试指标"""
        current_time = datetime.now()

        # 记录执行时间
        self.monitor.record_metric(
            MetricData(
                name=f"test_execution_time_{test_name}",
                value=execution_time,
                timestamp=current_time,
                tags={"test_name": test_name},
            )
        )

        # 记录内存使用
        self.monitor.record_metric(
            MetricData(
                name="memory_usage",
                value=memory_mb,
                timestamp=current_time,
                tags={"test_name": test_name},
            )
        )

        # 记录CPU使用
        self.monitor.record_metric(
            MetricData(
                name="cpu_usage",
                value=cpu_percent,
                timestamp=current_time,
                tags={"test_name": test_name},
            )
        )

        # 记录测试结果
        test_result = 1.0 if passed else 0.0
        self.monitor.record_metric(
            MetricData(
                name="test_result",
                value=test_result,
                timestamp=current_time,
                tags={"test_name": test_name},
            )
        )

    def start_monitoring(self):
        """开始监控"""
        self.initialize_default_rules()
        self.initialize_notification_channels()
        self.monitor.start_monitoring()
        logging.info("测试监控告警系统已启动")

    def stop_monitoring(self):
        """停止监控"""
        self.monitor.stop_monitoring()
        logging.info("测试监控告警系统已停止")

    def acknowledge_alert(self, alert_id: str, user: str):
        """确认告警"""
        self.monitor.acknowledge_alert(alert_id, user)

    def resolve_alert(self, alert_id: str):
        """解决告警"""
        self.monitor.resolve_alert(alert_id)

    def suppress_alert(self, alert_id: str, duration_minutes: int):
        """抑制告警"""
        self.monitor.suppress_alert(alert_id, duration_minutes)

    def get_dashboard_data(self) -> Dict[str, Any]:
        """获取仪表板数据"""
        return {
            "alerts": self.monitor.get_alert_summary(),
            "metrics": self.monitor.get_metrics_summary(),
            "rules": [
                {
                    "id": rule.id,
                    "name": rule.name,
                    "severity": rule.severity.value,
                    "status": "enabled" if rule.enabled else "disabled",
                    "last_evaluated": rule.last_evaluated.isoformat() if rule.last_evaluated else None,
                }
                for rule in self.monitor.alert_rules.values()
            ],
            "channels": [
                {
                    "id": channel_id,
                    "type": type(channel).__name__,
                    "config_valid": channel.validate_config(),
                }
                for channel_id, channel in self.monitor.notification_channels.items()
            ],
        }

    def export_alerts(self, output_path: str, format: str = "json"):
        """导出告警数据"""
        alerts_data = []
        for alert in self.monitor.alerts.values():
            alert_data = {
                "id": alert.id,
                "rule_id": alert.rule_id,
                "rule_name": alert.rule_name,
                "severity": alert.severity.value,
                "status": alert.status.value,
                "message": alert.message,
                "timestamp": alert.timestamp.isoformat(),
                "value": alert.value,
                "metadata": alert.metadata,
                "notification_history": alert.notification_history,
            }

            if alert.acknowledged_by:
                alert_data["acknowledged_by"] = alert.acknowledged_by
                alert_data["acknowledged_at"] = alert.acknowledged_at.isoformat() if alert.acknowledged_at else None

            if alert.resolved_at:
                alert_data["resolved_at"] = alert.resolved_at.isoformat()

            if alert.suppressed_until:
                alert_data["suppressed_until"] = alert.suppressed_until.isoformat()

            alerts_data.append(alert_data)

        output_path = Path(output_path)
        if format == "json":
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(alerts_data, f, indent=2, ensure_ascii=False)
        elif format == "csv":
            import csv

            if alerts_data:
                with open(output_path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=alerts_data[0].keys())
                    writer.writeheader()
                    writer.writerows(alerts_data)

        logging.info(f"告警数据已导出到: {output_path}")


class AlertType(Enum):
    """告警类型"""

    TEST_FAILURE = "test_failure"
    PERFORMANCE_THRESHOLD = "performance_threshold"
    RESOURCE_USAGE = "resource_usage"
    INFRASTRUCTURE_ISSUE = "infrastructure_issue"
    SECURITY_VIOLATION = "security_violation"
    DATA_INTEGRITY = "data_integrity"
    SYSTEM_HEALTH = "system_health"
    BUSINESS_LOGIC = "business_logic"


class TestExecutionResult(BaseModel):
    """测试执行结果"""

    test_id: str
    test_name: str
    test_type: str
    execution_time: float
    status: str  # passed, failed, skipped, error
    error_message: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    network_io: Dict[str, float] = Field(default_factory=dict)
    disk_io: Dict[str, float] = Field(default_factory=dict)
    custom_metrics: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RealTimeMonitor:
    """实时监控器"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.is_monitoring = False
        self.monitoring_thread = None
        self.check_interval = config.get("check_interval", 1.0)
        self.prometheus_port = config.get("prometheus_port", 8001)

        # 指标历史
        self.metrics_history: Dict[str, List[Tuple[float, datetime]]] = defaultdict(list)
        self.alerts: List[Dict[str, Any]] = []
        self.alert_thresholds = config.get("alert_thresholds", {})

        # Prometheus指标
        self._initialize_prometheus_metrics()

        # 启动Prometheus服务器
        try:
            start_http_server(self.prometheus_port)
            logging.info(f"Prometheus服务器已启动，端口: {self.prometheus_port}")
        except Exception as e:
            logging.error(f"启动Prometheus服务器失败: {e}")

    def _initialize_prometheus_metrics(self):
        """初始化Prometheus指标"""
        self.prometheus_metrics = {
            "test_executions_total": Counter(
                "test_executions_total",
                "Total test executions",
                ["status", "test_type"],
            ),
            "test_execution_duration": Histogram(
                "test_execution_duration_seconds",
                "Test execution duration",
                ["test_type"],
            ),
            "alert_count": Gauge("test_alert_count", "Active alert count", ["severity"]),
            "system_cpu_usage": Gauge("test_system_cpu_usage", "CPU usage"),
            "system_memory_usage": Gauge("test_system_memory_usage", "Memory usage"),
            "test_throughput": Gauge("test_throughput", "Tests per second"),
        }

    def start_monitoring(self):
        """启动监控"""
        if self.is_monitoring:
            return

        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        logging.info("实时监控已启动")

    def stop_monitoring(self):
        """停止监控"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join()
        logging.info("实时监控已停止")

    def _monitoring_loop(self):
        """监控循环"""
        while self.is_monitoring:
            try:
                # 采集系统指标
                system_metrics = self._collect_system_metrics()

                # 记录指标
                for name, value in system_metrics.items():
                    timestamp = datetime.now()
                    self.metrics_history[name].append((value, timestamp))

                    # 限制历史记录大小
                    max_history = self.config.get("max_history", 1000)
                    if len(self.metrics_history[name]) > max_history:
                        self.metrics_history[name] = self.metrics_history[name][-max_history:]

                    # 更新Prometheus指标
                    self._update_prometheus_metric(name, value)

                # 检查告警
                self._check_alerts(system_metrics)

                # 计算测试吞吐量
                self._calculate_test_throughput()

            except Exception as e:
                logging.error(f"监控循环错误: {e}")

            time.sleep(self.check_interval)

    def _collect_system_metrics(self) -> Dict[str, Any]:
        """收集系统指标"""
        try:
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            return {
                "cpu_usage": cpu_usage / 100.0,
                "memory_usage": memory.percent / 100.0,
                "disk_usage": (disk.total - disk.free) / disk.total,
                "disk_free": disk.free / disk.total,
                "timestamp": datetime.now(),
            }
        except Exception as e:
            logging.error(f"收集系统指标失败: {e}")
            return {}

    def _update_prometheus_metric(self, name: str, value: float):
        """更新Prometheus指标"""
        try:
            metric_name = name.replace(" ", "_").lower()

            if metric_name in self.prometheus_metrics:
                prom_metric = self.prometheus_metrics[metric_name]

                if hasattr(prom_metric, "_value"):  # Gauge
                    prom_metric.set(value)
                elif hasattr(prom_metric, "_count"):  # Counter
                    prom_metric.inc(value)

        except Exception as e:
            logging.warning(f"更新Prometheus指标失败: {e}")

    def _check_alerts(self, metrics: Dict[str, Any]):
        """检查告警条件"""
        for metric_name, threshold in self.alert_thresholds.items():
            if metric_name in metrics:
                value = metrics[metric_name]
                if value > threshold:
                    self._trigger_alert(metric_name, value, threshold)

    def _trigger_alert(self, metric_name: str, value: float, threshold: float):
        """触发告警"""
        alert = {
            "id": f"alert_{int(time.time())}",
            "metric_name": metric_name,
            "current_value": value,
            "threshold": threshold,
            "timestamp": datetime.now(),
            "severity": "high" if value > threshold * 1.5 else "medium",
            "status": "active",
        }

        self.alerts.append(alert)

        # 限制告警历史
        max_alerts = self.config.get("max_alerts", 100)
        if len(self.alerts) > max_alerts:
            self.alerts = self.alerts[-max_alerts:]

        # 更新Prometheus指标
        self.prometheus_metrics["alert_count"].labels(severity=alert["severity"]).inc()

        logging.warning(f"告警触发: {metric_name} = {value} > {threshold}")

    def _calculate_test_throughput(self):
        """计算测试吞吐量"""
        now = datetime.now()
        recent_tests = []

        # 查找最近的测试指标
        for metric_name, history in self.metrics_history.items():
            if "test" in metric_name:
                recent_tests.extend([t for t in history if (now - t[1]).total_seconds() < 60])

        throughput = len(recent_tests) / 60.0 if recent_tests else 0
        self._update_prometheus_metric("test_throughput", throughput)

    def get_dashboard_data(self) -> Dict[str, Any]:
        """获取仪表板数据"""
        # 计算最新指标
        latest_metrics = {}
        for name, history in self.metrics_history.items():
            if history:
                latest_metrics[name] = history[-1][0]

        # 按严重级别统计告警
        alert_counts = defaultdict(int)
        for alert in self.alerts:
            alert_counts[alert["severity"]] += 1

        return {
            "latest_metrics": latest_metrics,
            "alert_counts": dict(alert_counts),
            "total_alerts": len(self.alerts),
            "metrics_history": {
                name: [(value, ts.isoformat()) for value, ts in history[-100:]]
                for name, history in self.metrics_history.items()
            },
        }


class IntelligentPerformanceAnalyzer:
    """智能性能分析器"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.analysis_window = config.get("analysis_window", 3600)  # 1小时
        self.pattern_history: List[Dict[str, Any]] = []
        self.anomaly_threshold = config.get("anomaly_threshold", 2.0)

    def analyze_performance_patterns(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """分析性能模式"""
        analysis_result = {
            "timestamp": datetime.now(),
            "patterns": [],
            "anomalies": [],
            "recommendations": [],
        }

        # 分析CPU使用模式
        if "cpu_usage" in metrics:
            cpu_pattern = self._analyze_cpu_pattern(metrics["cpu_usage"])
            analysis_result["patterns"].append(cpu_pattern)

            if cpu_pattern["anomaly"]:
                analysis_result["anomalies"].append(cpu_pattern)

        # 分析内存使用模式
        if "memory_usage" in metrics:
            memory_pattern = self._analyze_memory_pattern(metrics["memory_usage"])
            analysis_result["patterns"].append(memory_pattern)

            if memory_pattern["anomaly"]:
                analysis_result["anomalies"].append(memory_pattern)

        # 生成建议
        if analysis_result["anomalies"]:
            analysis_result["recommendations"] = self._generate_recommendations(analysis_result["anomalies"])

        # 保存历史
        self.pattern_history.append(analysis_result)

        # 限制历史大小
        max_history = self.config.get("max_pattern_history", 100)
        if len(self.pattern_history) > max_history:
            self.pattern_history = self.pattern_history[-max_history:]

        return analysis_result

    def _analyze_cpu_pattern(self, cpu_usage: float) -> Dict[str, Any]:
        """分析CPU使用模式"""
        pattern = {
            "metric": "cpu_usage",
            "current_value": cpu_usage,
            "pattern_type": "normal",
            "anomaly": False,
            "details": {},
        }

        # 基于阈值的检测
        if cpu_usage > 0.8:
            pattern["pattern_type"] = "high_usage"
            pattern["anomaly"] = True
            pattern["details"]["threshold_exceeded"] = cpu_usage - 0.8

        # 基于历史的检测
        recent_values = [m.get("cpu_usage", 0) for m in self.pattern_history[-10:]]
        if len(recent_values) >= 5:
            avg_usage = statistics.mean(recent_values)
            if abs(cpu_usage - avg_usage) > self.anomaly_threshold * statistics.stdev(recent_values):
                pattern["pattern_type"] = "anomaly"
                pattern["anomaly"] = True
                pattern["details"]["deviation"] = abs(cpu_usage - avg_usage)

        return pattern

    def _analyze_memory_pattern(self, memory_usage: float) -> Dict[str, Any]:
        """分析内存使用模式"""
        pattern = {
            "metric": "memory_usage",
            "current_value": memory_usage,
            "pattern_type": "normal",
            "anomaly": False,
            "details": {},
        }

        # 基于阈值的检测
        if memory_usage > 0.85:
            pattern["pattern_type"] = "high_usage"
            pattern["anomaly"] = True
            pattern["details"]["threshold_exceeded"] = memory_usage - 0.85

        return pattern

    def _generate_recommendations(self, anomalies: List[Dict[str, Any]]) -> List[str]:
        """生成优化建议"""
        recommendations = []

        for anomaly in anomalies:
            if anomaly["metric"] == "cpu_usage":
                if anomaly["pattern_type"] == "high_usage":
                    recommendations.append("考虑增加CPU资源或优化CPU密集型任务")
                elif anomaly["pattern_type"] == "anomaly":
                    recommendations.append("检查是否存在异常的CPU使用模式")

            elif anomaly["metric"] == "memory_usage":
                if anomaly["pattern_type"] == "high_usage":
                    recommendations.append("考虑增加内存或优化内存使用")

        return recommendations


class DynamicPerformanceOptimizer:
    """动态性能优化器"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.optimization_strategies = config.get("optimization_strategies", {})
        self.optimization_history: List[Dict[str, Any]] = []
        self.optimization_thresholds = config.get("optimization_thresholds", {})

    def optimize_performance(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """优化性能"""
        optimization_result = {
            "timestamp": datetime.now(),
            "applied_optimizations": [],
            "performance_improvement": 0.0,
            "next_steps": [],
        }

        # 基于分析结果应用优化策略
        for pattern in analysis_result["patterns"]:
            strategy = self._get_optimization_strategy(pattern)
            if strategy:
                optimization = self._apply_optimization(strategy, pattern)
                if optimization["success"]:
                    optimization_result["applied_optimizations"].append(optimization)
                    optimization_result["performance_improvement"] += optimization["improvement"]

        # 更新历史
        self.optimization_history.append(optimization_result)

        # 生成下一步建议
        optimization_result["next_steps"] = self._generate_next_steps(optimization_result)

        return optimization_result

    def _get_optimization_strategy(self, pattern: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """获取优化策略"""
        metric = pattern["metric"]
        pattern_type = pattern["pattern_type"]

        # 查找匹配的策略
        for strategy_key, strategy in self.optimization_strategies.items():
            if strategy.get("metric") == metric and strategy.get("pattern_type") == pattern_type:
                return strategy

        return None

    def _apply_optimization(self, strategy: Dict[str, Any], pattern: Dict[str, Any]) -> Dict[str, Any]:
        """应用优化"""
        optimization = {
            "strategy_id": strategy["id"],
            "strategy_name": strategy["name"],
            "applied": True,
            "success": False,
            "improvement": 0.0,
            "details": {},
        }

        try:
            # 执行优化操作
            if strategy["type"] == "resource_allocation":
                improvement = self._optimize_resource_allocation(strategy, pattern)
            elif strategy["type"] == "code_optimization":
                improvement = self._optimize_code_performance(strategy, pattern)
            elif strategy["type"] == "cache_optimization":
                improvement = self._optimize_cache_strategy(strategy, pattern)
            else:
                improvement = 0.0

            optimization["success"] = True
            optimization["improvement"] = improvement

        except Exception as e:
            logging.error(f"应用优化失败: {strategy['name']}, 错误: {e}")
            optimization["success"] = False
            optimization["error"] = str(e)

        return optimization

    def _optimize_resource_allocation(self, strategy: Dict[str, Any], pattern: Dict[str, Any]) -> float:
        """优化资源分配"""
        # 模拟资源优化
        current_value = pattern["current_value"]
        target_value = strategy.get("target_value", 0.7)

        # 计算改进（模拟）
        improvement = (current_value - target_value) * 0.1
        return max(0, improvement)

    def _optimize_code_performance(self, strategy: Dict[str, Any], pattern: Dict[str, Any]) -> float:
        """优化代码性能"""
        # 模拟代码优化
        return 0.05  # 5%改进

    def _optimize_cache_strategy(self, strategy: Dict[str, Any], pattern: Dict[str, Any]) -> float:
        """优化缓存策略"""
        # 模拟缓存优化
        return 0.03  # 3%改进

    def _generate_next_steps(self, optimization_result: Dict[str, Any]) -> List[str]:
        """生成下一步建议"""
        next_steps = []

        if optimization_result["performance_improvement"] < 0.1:
            next_steps.append("考虑进行更深入的代码优化")

        if optimization_result["applied_optimizations"]:
            next_steps.append("监控优化效果，持续调整")

        next_steps.append("定期进行性能分析")

        return next_steps


