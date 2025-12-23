"""
测试监控告警系统

提供全面的测试监控、告警管理和通知功能。
"""

import json
import logging
import smtplib
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from enum import Enum
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable, Tuple
import threading
import queue
import statistics

from jinja2 import Template
import requests
import psutil
from prometheus_client import Counter, Gauge, Histogram, start_http_server
from ..ai.test_data_manager import DataManager as AIDataManager


class AlertSeverity(Enum):
    """告警严重级别"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AlertStatus(Enum):
    """告警状态"""

    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"


@dataclass
class AlertRule:
    """告警规则"""

    id: str
    name: str
    description: str
    severity: AlertSeverity
    condition: str  # 表达式条件
    threshold: float
    duration: int  # 持续时间（秒）
    enabled: bool = True
    tags: List[str] = field(default_factory=list)
    notification_channels: List[str] = field(default_factory=list)
    evaluation_interval: int = 60  # 评估间隔（秒）
    last_evaluated: Optional[datetime] = None


@dataclass
class Alert:
    """告警实例"""

    id: str
    rule_id: str
    rule_name: str
    severity: AlertSeverity
    status: AlertStatus
    message: str
    timestamp: datetime
    value: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    suppressed_until: Optional[datetime] = None
    notification_history: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class MetricData:
    """指标数据"""

    name: str
    value: float
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    labels: Dict[str, str] = field(default_factory=dict)


class NotificationChannel(ABC):
    """通知渠道抽象基类"""

    @abstractmethod
    async def send_notification(self, alert: Alert) -> bool:
        """发送通知"""
        pass

    @abstractmethod
    def validate_config(self) -> bool:
        """验证配置"""
        pass


class EmailNotificationChannel(NotificationChannel):
    """邮件通知渠道"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.smtp_server = config.get("smtp_server")
        self.smtp_port = config.get("smtp_port", 587)
        self.username = config.get("username")
        self.password = config.get("password")
        self.from_email = config.get("from_email")
        self.to_emails = config.get("to_emails", [])
        self.use_tls = config.get("use_tls", True)

    def validate_config(self) -> bool:
        """验证邮件配置"""
        required_fields = [
            "smtp_server",
            "username",
            "password",
            "from_email",
            "to_emails",
        ]
        return all(field in self.config for field in required_fields)

    async def send_notification(self, alert: Alert) -> bool:
        """发送邮件通知"""
        try:
            # 创建邮件内容
            template = Template("""
            <html>
            <body>
                <h2>测试监控告警</h2>
                <table border="1" cellpadding="5" cellspacing="0">
                    <tr><td><strong>告警ID:</strong></td><td>{{ alert.id }}</td></tr>
                    <tr><td><strong>规则名称:</strong></td><td>{{ alert.rule_name }}</td></tr>
                    <tr><td><strong>严重级别:</strong></td><td>{{ alert.severity.value }}</td></tr>
                    <tr><td><strong>状态:</strong></td><td>{{ alert.status.value }}</td></tr>
                    <tr><td><strong>时间:</strong></td><td>{{ alert.timestamp }}</td></tr>
                    <tr><td><strong>消息:</strong></td><td>{{ alert.message }}</td></tr>
                    <tr><td><strong>当前值:</strong></td><td>{{ alert.value }}</td></tr>
                </table>
                {% if alert.metadata %}
                <h3>详细信息</h3>
                <table border="1" cellpadding="5" cellspacing="0">
                    {% for key, value in alert.metadata.items() %}
                    <tr><td><strong>{{ key }}:</strong></td><td>{{ value }}</td></tr>
                    {% endfor %}
                </table>
                {% endif %}
                <p><em>此邮件由 MyStocks 测试监控系统自动发送</em></p>
            </body>
            </html>
            """)

            html_content = template.render(alert=alert)

            # 创建邮件
            msg = MIMEMultipart("alternative")
            msg["From"] = self.from_email
            msg["To"] = ", ".join(self.to_emails)
            msg["Subject"] = (
                f"[{alert.severity.value.upper()}] 测试监控告警: {alert.rule_name}"
            )

            # 添加HTML内容
            part = MIMEText(html_content, "html")
            msg.attach(part)

            # 发送邮件
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)

            logging.info(f"邮件通知已发送: {alert.id}")
            return True

        except Exception as e:
            logging.error(f"发送邮件通知失败: {e}")
            return False


class WebhookNotificationChannel(NotificationChannel):
    """Webhook通知渠道"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.url = config.get("url")
        self.method = config.get("method", "POST").upper()
        self.headers = config.get("headers", {})
        self.timeout = config.get("timeout", 30)

    def validate_config(self) -> bool:
        """验证Webhook配置"""
        return bool(self.url)

    async def send_notification(self, alert: Alert) -> bool:
        """发送Webhook通知"""
        try:
            payload = {
                "alert_id": alert.id,
                "rule_id": alert.rule_id,
                "rule_name": alert.rule_name,
                "severity": alert.severity.value,
                "status": alert.status.value,
                "message": alert.message,
                "timestamp": alert.timestamp.isoformat(),
                "value": alert.value,
                "metadata": alert.metadata,
            }

            response = requests.request(
                method=self.method,
                url=self.url,
                json=payload,
                headers=self.headers,
                timeout=self.timeout,
            )

            if response.status_code == 200:
                logging.info(f"Webhook通知已发送: {alert.id}")
                return True
            else:
                logging.error(f"Webhook通知失败: {response.status_code}")
                return False

        except Exception as e:
            logging.error(f"发送Webhook通知失败: {e}")
            return False


class SlackNotificationChannel(NotificationChannel):
    """Slack通知渠道"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.webhook_url = config.get("webhook_url")
        self.channel = config.get("channel", "#alerts")
        self.username = config.get("username", "MyStocks Alert Bot")
        self.timeout = config.get("timeout", 30)

    def validate_config(self) -> bool:
        """验证Slack配置"""
        return bool(self.webhook_url)

    async def send_notification(self, alert: Alert) -> bool:
        """发送Slack通知"""
        try:
            # 根据严重级别选择颜色
            color_map = {
                AlertSeverity.CRITICAL: "danger",
                AlertSeverity.HIGH: "warning",
                AlertSeverity.MEDIUM: "warning",
                AlertSeverity.LOW: "good",
                AlertSeverity.INFO: "#808080",
            }
            color = color_map.get(alert.severity, "good")

            payload = {
                "channel": self.channel,
                "username": self.username,
                "attachments": [
                    {
                        "color": color,
                        "title": f"[{alert.severity.value.upper()}] {alert.rule_name}",
                        "text": alert.message,
                        "fields": [
                            {"title": "告警ID", "value": alert.id, "short": True},
                            {
                                "title": "时间",
                                "value": alert.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                                "short": True,
                            },
                            {
                                "title": "当前值",
                                "value": str(alert.value),
                                "short": True,
                            },
                            {
                                "title": "状态",
                                "value": alert.status.value,
                                "short": True,
                            },
                        ],
                        "footer": "MyStocks 测试监控系统",
                        "ts": int(alert.timestamp.timestamp()),
                    }
                ],
            }

            if alert.metadata:
                payload["attachments"][0]["fields"].append(
                    {
                        "title": "详细信息",
                        "value": json.dumps(alert.metadata, indent=2),
                        "short": False,
                    }
                )

            response = requests.post(
                self.webhook_url, json=payload, timeout=self.timeout
            )

            if response.status_code == 200:
                logging.info(f"Slack通知已发送: {alert.id}")
                return True
            else:
                logging.error(f"Slack通知失败: {response.status_code}")
                return False

        except Exception as e:
            logging.error(f"发送Slack通知失败: {e}")
            return False


class TestMonitor:
    """测试监控器"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.alert_rules: Dict[str, AlertRule] = {}
        self.alerts: Dict[str, Alert] = {}
        self.metrics_history: Dict[str, List[MetricData]] = {}
        self.notification_channels: Dict[str, NotificationChannel] = {}
        self.is_monitoring = False
        self.monitoring_thread: Optional[threading.Thread] = None
        self.metric_queue = queue.Queue()
        self.alert_callback: Optional[Callable[[Alert], None]] = None

    def add_alert_rule(self, rule: AlertRule):
        """添加告警规则"""
        self.alert_rules[rule.id] = rule
        logging.info(f"添加告警规则: {rule.name} (ID: {rule.id})")

    def remove_alert_rule(self, rule_id: str):
        """移除告警规则"""
        if rule_id in self.alert_rules:
            del self.alert_rules[rule_id]
            # 关闭相关的告警
            alerts_to_close = [a for a in self.alerts.values() if a.rule_id == rule_id]
            for alert in alerts_to_close:
                alert.status = AlertStatus.RESOLVED
                alert.resolved_at = datetime.now()
            logging.info(f"移除告警规则: {rule_id}")

    def add_notification_channel(self, channel_id: str, channel: NotificationChannel):
        """添加通知渠道"""
        if channel.validate_config():
            self.notification_channels[channel_id] = channel
            logging.info(f"添加通知渠道: {channel_id}")
        else:
            logging.error(f"通知渠道配置无效: {channel_id}")

    def record_metric(self, metric: MetricData):
        """记录指标数据"""
        if metric.name not in self.metrics_history:
            self.metrics_history[metric.name] = []

        self.metrics_history[metric.name].append(metric)

        # 保持历史数据在合理范围内
        max_history = self.config.get("max_metric_history", 1000)
        if len(self.metrics_history[metric.name]) > max_history:
            self.metrics_history[metric.name] = self.metrics_history[metric.name][
                -max_history:
            ]

    def evaluate_alert_rules(self):
        """评估告警规则"""
        current_time = datetime.now()

        for rule in self.alert_rules.values():
            if not rule.enabled:
                continue

            # 检查是否需要评估
            if (
                rule.last_evaluated
                and (current_time - rule.last_evaluated).total_seconds()
                < rule.evaluation_interval
            ):
                continue

            rule.last_evaluated = current_time

            # 获取相关指标数据
            metrics = self.metrics_history.get(rule.name, [])
            if not metrics:
                continue

            # 计算指标值
            recent_metrics = [
                m
                for m in metrics
                if (current_time - m.timestamp).total_seconds() <= rule.duration
            ]

            if not recent_metrics:
                continue

            # 根据规则类型评估
            if rule.condition == "above_threshold":
                value = max(m.value for m in recent_metrics)
                triggered = value > rule.threshold
            elif rule.condition == "below_threshold":
                value = min(m.value for m in recent_metrics)
                triggered = value < rule.threshold
            elif rule.condition == "average_above":
                value = statistics.mean(m.value for m in recent_metrics)
                triggered = value > rule.threshold
            elif rule.condition == "average_below":
                value = statistics.mean(m.value for m in recent_metrics)
                triggered = value < rule.threshold
            elif rule.condition == "variance_high":
                values = [m.value for m in recent_metrics]
                value = statistics.variance(values)
                triggered = value > rule.threshold
            else:
                continue

            # 处理告警触发
            if triggered:
                existing_alert = next(
                    (
                        a
                        for a in self.alerts.values()
                        if a.rule_id == rule.id and a.status == AlertStatus.OPEN
                    ),
                    None,
                )

                if existing_alert:
                    # 更新现有告警
                    existing_alert.value = value
                    existing_alert.metadata["last_updated"] = current_time.isoformat()
                else:
                    # 创建新告警
                    alert = Alert(
                        id=f"alert_{rule.id}_{int(time.time())}",
                        rule_id=rule.id,
                        rule_name=rule.name,
                        severity=rule.severity,
                        status=AlertStatus.OPEN,
                        message=f"{rule.description} - 当前值: {value}",
                        timestamp=current_time,
                        value=value,
                        metadata={
                            "condition": rule.condition,
                            "threshold": rule.threshold,
                        },
                    )
                    self.alerts[alert.id] = alert
                    self.send_alert_notifications(alert)

            # 检查告警解决
            for alert in self.alerts.values():
                if alert.rule_id == rule.id and alert.status == AlertStatus.OPEN:
                    opposite_triggered = self._check_opposite_condition(
                        rule, recent_metrics, rule.threshold
                    )
                    if opposite_triggered:
                        alert.status = AlertStatus.RESOLVED
                        alert.resolved_at = current_time
                        self.send_alert_notifications(alert)

    def _check_opposite_condition(
        self, rule: AlertRule, metrics: List[MetricData], threshold: float
    ) -> bool:
        """检查相反条件是否满足（用于告警解决）"""
        if rule.condition in ["above_threshold", "average_above"]:
            return all(m.value <= threshold for m in metrics)
        elif rule.condition in ["below_threshold", "average_below"]:
            return all(m.value >= threshold for m in metrics)
        return False

    async def send_alert_notifications(self, alert: Alert):
        """发送告警通知"""
        rule = self.alert_rules.get(alert.rule_id)
        if not rule:
            return

        # 发送到所有配置的通知渠道
        for channel_id in rule.notification_channels:
            channel = self.notification_channels.get(channel_id)
            if channel:
                try:
                    success = await channel.send_notification(alert)
                    if success:
                        alert.notification_history.append(
                            {
                                "channel": channel_id,
                                "timestamp": datetime.now().isoformat(),
                                "status": "success",
                            }
                        )
                except Exception as e:
                    logging.error(f"发送通知失败: {channel_id}, 错误: {e}")
                    alert.notification_history.append(
                        {
                            "channel": channel_id,
                            "timestamp": datetime.now().isoformat(),
                            "status": "failed",
                            "error": str(e),
                        }
                    )

        # 调用回调函数
        if self.alert_callback:
            try:
                self.alert_callback(alert)
            except Exception as e:
                logging.error(f"告警回调函数执行失败: {e}")

    def acknowledge_alert(self, alert_id: str, acknowledged_by: str):
        """确认告警"""
        if alert_id in self.alerts:
            alert = self.alerts[alert_id]
            alert.status = AlertStatus.ACKNOWLEDGED
            alert.acknowledged_by = acknowledged_by
            alert.acknowledged_at = datetime.now()
            logging.info(f"告警已确认: {alert_id} by {acknowledged_by}")

    def resolve_alert(self, alert_id: str):
        """解决告警"""
        if alert_id in self.alerts:
            alert = self.alerts[alert_id]
            alert.status = AlertStatus.RESOLVED
            alert.resolved_at = datetime.now()
            logging.info(f"告警已解决: {alert_id}")

    def suppress_alert(self, alert_id: str, duration_minutes: int):
        """抑制告警"""
        if alert_id in self.alerts:
            alert = self.alerts[alert_id]
            alert.suppressed_until = datetime.now() + timedelta(
                minutes=duration_minutes
            )
            alert.status = AlertStatus.SUPPRESSED
            logging.info(f"告警已抑制: {alert_id} until {alert.suppressed_until}")

    def start_monitoring(self):
        """开始监控"""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
            self.monitoring_thread.daemon = True
            self.monitoring_thread.start()
            logging.info("测试监控已启动")

    def stop_monitoring(self):
        """停止监控"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join()
        logging.info("测试监控已停止")

    def _monitoring_loop(self):
        """监控循环"""
        while self.is_monitoring:
            try:
                # 评估告警规则
                self.evaluate_alert_rules()
                time.sleep(1)  # 1秒检查间隔
            except Exception as e:
                logging.error(f"监控循环错误: {e}")
                time.sleep(5)  # 错误时等待5秒

    def get_alert_summary(self) -> Dict[str, Any]:
        """获取告警摘要"""
        total_alerts = len(self.alerts)
        open_alerts = len(
            [a for a in self.alerts.values() if a.status == AlertStatus.OPEN]
        )
        acknowledged_alerts = len(
            [a for a in self.alerts.values() if a.status == AlertStatus.ACKNOWLEDGED]
        )
        resolved_alerts = len(
            [a for a in self.alerts.values() if a.status == AlertStatus.RESOLVED]
        )

        by_severity = {}
        for severity in AlertSeverity:
            by_severity[severity.value] = len(
                [
                    a
                    for a in self.alerts.values()
                    if a.severity == severity and a.status == AlertStatus.OPEN
                ]
            )

        return {
            "total_alerts": total_alerts,
            "open_alerts": open_alerts,
            "acknowledged_alerts": acknowledged_alerts,
            "resolved_alerts": resolved_alerts,
            "by_severity": by_severity,
        }

    def get_metrics_summary(self) -> Dict[str, Any]:
        """获取指标摘要"""
        summary = {}
        for name, metrics in self.metrics_history.items():
            if metrics:
                latest = metrics[-1]
                values = [m.value for m in metrics[-100:]]  # 最近100个值
                summary[name] = {
                    "latest_value": latest.value,
                    "latest_timestamp": latest.timestamp.isoformat(),
                    "min": min(values),
                    "max": max(values),
                    "average": statistics.mean(values),
                    "count": len(values),
                }
        return summary


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
                    "last_evaluated": rule.last_evaluated.isoformat()
                    if rule.last_evaluated
                    else None,
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
                alert_data["acknowledged_at"] = (
                    alert.acknowledged_at.isoformat() if alert.acknowledged_at else None
                )

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


# 高级监控组件


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
        self.metrics_history: Dict[str, List[Tuple[float, datetime]]] = defaultdict(
            list
        )
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
            "alert_count": Gauge(
                "test_alert_count", "Active alert count", ["severity"]
            ),
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
                        self.metrics_history[name] = self.metrics_history[name][
                            -max_history:
                        ]

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
                recent_tests.extend(
                    [t for t in history if (now - t[1]).total_seconds() < 60]
                )

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
            analysis_result["recommendations"] = self._generate_recommendations(
                analysis_result["anomalies"]
            )

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
            if abs(cpu_usage - avg_usage) > self.anomaly_threshold * statistics.stdev(
                recent_values
            ):
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
                    optimization_result["performance_improvement"] += optimization[
                        "improvement"
                    ]

        # 更新历史
        self.optimization_history.append(optimization_result)

        # 生成下一步建议
        optimization_result["next_steps"] = self._generate_next_steps(
            optimization_result
        )

        return optimization_result

    def _get_optimization_strategy(
        self, pattern: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """获取优化策略"""
        metric = pattern["metric"]
        pattern_type = pattern["pattern_type"]

        # 查找匹配的策略
        for strategy_key, strategy in self.optimization_strategies.items():
            if (
                strategy.get("metric") == metric
                and strategy.get("pattern_type") == pattern_type
            ):
                return strategy

        return None

    def _apply_optimization(
        self, strategy: Dict[str, Any], pattern: Dict[str, Any]
    ) -> Dict[str, Any]:
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

    def _optimize_resource_allocation(
        self, strategy: Dict[str, Any], pattern: Dict[str, Any]
    ) -> float:
        """优化资源分配"""
        # 模拟资源优化
        current_value = pattern["current_value"]
        target_value = strategy.get("target_value", 0.7)

        # 计算改进（模拟）
        improvement = (current_value - target_value) * 0.1
        return max(0, improvement)

    def _optimize_code_performance(
        self, strategy: Dict[str, Any], pattern: Dict[str, Any]
    ) -> float:
        """优化代码性能"""
        # 模拟代码优化
        return 0.05  # 5%改进

    def _optimize_cache_strategy(
        self, strategy: Dict[str, Any], pattern: Dict[str, Any]
    ) -> float:
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


class EnhancedTestMonitor:
    """增强的测试监控器"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.real_time_monitor = RealTimeMonitor(config.get("real_time_monitor", {}))
        self.performance_analyzer = IntelligentPerformanceAnalyzer(
            config.get("performance_analyzer", {})
        )
        self.performance_optimizer = DynamicPerformanceOptimizer(
            config.get("performance_optimizer", {})
        )

        # 测试结果历史
        self.test_results: List[TestExecutionResult] = []
        self.test_stats = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "error": 0,
        }

    def start_monitoring(self):
        """启动监控"""
        self.real_time_monitor.start_monitoring()
        logging.info("增强的测试监控已启动")

    def stop_monitoring(self):
        """停止监控"""
        self.real_time_monitor.stop_monitoring()
        logging.info("增强的测试监控已停止")

    def record_test_result(self, result: TestExecutionResult):
        """记录测试结果"""
        # 添加到历史
        self.test_results.append(result)

        # 更新统计
        self.test_stats["total"] += 1
        if result.status == "passed":
            self.test_stats["passed"] += 1
        elif result.status == "failed":
            self.test_stats["failed"] += 1
        elif result.status == "skipped":
            self.test_stats["skipped"] += 1
        elif result.status == "error":
            self.test_stats["error"] += 1

        # 更新Prometheus指标
        self._update_test_metrics(result)

        # 分析性能
        metrics = self._build_metrics_from_result(result)
        analysis_result = self.performance_analyzer.analyze_performance_patterns(
            metrics
        )

        # 优化性能
        if analysis_result["anomalies"]:
            optimization_result = self.performance_optimizer.optimize_performance(
                analysis_result
            )
            logging.info(
                f"性能优化完成，改进: {optimization_result['performance_improvement']:.2%}"
            )

        # 限制历史大小
        max_history = self.config.get("max_test_history", 1000)
        if len(self.test_results) > max_history:
            self.test_results = self.test_results[-max_history:]

    def _update_test_metrics(self, result: TestExecutionResult):
        """更新测试指标"""
        try:
            # 更新测试执行计数
            self.real_time_monitor.prometheus_metrics["test_executions_total"].labels(
                status=result.status, test_type=result.test_type
            ).inc()

            # 更新执行时间直方图
            self.real_time_monitor.prometheus_metrics["test_execution_duration"].labels(
                test_type=result.test_type
            ).observe(result.execution_time)

        except Exception as e:
            logging.error(f"更新测试指标失败: {e}")

    def _build_metrics_from_result(self, result: TestExecutionResult) -> Dict[str, Any]:
        """从测试结果构建指标"""
        return {
            "cpu_usage": result.cpu_usage / 100.0,
            "memory_usage": result.memory_usage / 100.0,
            "test_execution_time": result.execution_time,
            "test_result": 1.0 if result.status == "passed" else 0.0,
            "timestamp": result.timestamp,
        }

    def get_comprehensive_dashboard_data(self) -> Dict[str, Any]:
        """获取综合仪表板数据"""
        dashboard_data = self.real_time_monitor.get_dashboard_data()

        # 添加测试统计
        dashboard_data["test_statistics"] = self.test_stats.copy()
        dashboard_data["test_statistics"]["pass_rate"] = (
            self.test_stats["passed"] / self.test_stats["total"]
            if self.test_stats["total"] > 0
            else 0
        )

        # 添加最近的测试结果
        recent_tests = self.test_results[-10:]
        dashboard_data["recent_tests"] = [
            {
                "name": test.test_name,
                "status": test.status,
                "execution_time": test.execution_time,
                "timestamp": test.timestamp.isoformat(),
            }
            for test in recent_tests
        ]

        # 添加性能分析结果
        if self.performance_analyzer.pattern_history:
            latest_analysis = self.performance_analyzer.pattern_history[-1]
            dashboard_data["performance_analysis"] = {
                "anomalies_count": len(latest_analysis["anomalies"]),
                "recommendations": latest_analysis["recommendations"],
            }

        # 添加优化历史
        dashboard_data["optimization_history"] = (
            self.performance_optimizer.optimization_history[-5:]
        )

        return dashboard_data


# 使用示例
def demo_test_monitoring():
    """演示测试监控告警功能"""
    print("🚀 演示测试监控告警系统")

    # 创建告警管理器
    alert_manager = TestAlertManager()

    # 启动监控
    alert_manager.start_monitoring()

    # 模拟测试执行
    for i in range(10):
        import random

        test_name = f"test_{i + 1}"
        execution_time = random.uniform(10, 300)
        passed = random.choice([True, True, False])  # 66.7% 通过率
        memory_mb = random.uniform(100, 2000)
        cpu_percent = random.uniform(20, 90)

        alert_manager.record_test_metrics(
            test_name=test_name,
            execution_time=execution_time,
            passed=passed,
            memory_mb=memory_mb,
            cpu_percent=cpu_percent,
        )

        time.sleep(2)

    # 获取仪表板数据
    dashboard_data = alert_manager.get_dashboard_data()
    print("\n📊 仪表板数据:")
    print(f"告警摘要: {dashboard_data['alerts']}")
    print(f"指标摘要: {list(dashboard_data['metrics'].keys())}")

    # 导出告警数据
    alert_manager.export_alerts("test_alerts.json", "json")

    # 停止监控
    alert_manager.stop_monitoring()


if __name__ == "__main__":
    demo_test_monitoring()
