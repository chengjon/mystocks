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
from typing import Any, Callable, Dict, List, Optional

import requests
from jinja2 import Template


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
            template = Template(
                """
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
            """
            )

            html_content = template.render(alert=alert)

            # 创建邮件
            msg = MIMEMultipart("alternative")
            msg["From"] = self.from_email
            msg["To"] = ", ".join(self.to_emails)
            msg["Subject"] = f"[{alert.severity.value.upper()}] 测试监控告警: {alert.rule_name}"

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

            response = requests.post(self.webhook_url, json=payload, timeout=self.timeout)

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
            self.metrics_history[metric.name] = self.metrics_history[metric.name][-max_history:]

    def evaluate_alert_rules(self):
        """评估告警规则"""
        current_time = datetime.now()

        for rule in self.alert_rules.values():
            if not rule.enabled:
                continue

            # 检查是否需要评估
            if rule.last_evaluated and (current_time - rule.last_evaluated).total_seconds() < rule.evaluation_interval:
                continue

            rule.last_evaluated = current_time

            # 获取相关指标数据
            metrics = self.metrics_history.get(rule.name, [])
            if not metrics:
                continue

            # 计算指标值
            recent_metrics = [m for m in metrics if (current_time - m.timestamp).total_seconds() <= rule.duration]

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
                    (a for a in self.alerts.values() if a.rule_id == rule.id and a.status == AlertStatus.OPEN),
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
                    opposite_triggered = self._check_opposite_condition(rule, recent_metrics, rule.threshold)
                    if opposite_triggered:
                        alert.status = AlertStatus.RESOLVED
                        alert.resolved_at = current_time
                        self.send_alert_notifications(alert)

    def _check_opposite_condition(self, rule: AlertRule, metrics: List[MetricData], threshold: float) -> bool:
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
            alert.suppressed_until = datetime.now() + timedelta(minutes=duration_minutes)
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
        open_alerts = len([a for a in self.alerts.values() if a.status == AlertStatus.OPEN])
        acknowledged_alerts = len([a for a in self.alerts.values() if a.status == AlertStatus.ACKNOWLEDGED])
        resolved_alerts = len([a for a in self.alerts.values() if a.status == AlertStatus.RESOLVED])

        by_severity = {}
        for severity in AlertSeverity:
            by_severity[severity.value] = len(
                [a for a in self.alerts.values() if a.severity == severity and a.status == AlertStatus.OPEN]
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


