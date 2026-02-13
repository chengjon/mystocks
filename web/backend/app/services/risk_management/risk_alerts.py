"""
风险管理告警模块

提供告警规则管理、告警触发器、多渠道告警通知功能
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from .risk_base import RiskLevel

logger = __import__("logging").getLogger(__name__)


class AlertChannel(Enum):
    """告警渠道枚举"""

    EMAIL = "email"
    WEBHOOK = "webhook"
    SMS = "sms"
    IN_APP = "in_app"


class AlertRule:
    """告警规则类"""

    rule_id: str = ""
    rule_name: str = ""
    risk_level: RiskLevel = RiskLevel.LOW
    channel: AlertChannel = AlertChannel.EMAIL
    conditions: Dict[str, Any] = None
    is_enabled: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self) -> Dict:
        return {
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "risk_level": self.risk_level.value,
            "channel": self.channel.value,
            "conditions": self.conditions,
            "is_enabled": self.is_enabled,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


@dataclass
class AlertHistory:
    """告警历史记录"""

    alert_id: str = ""
    rule_id: str = ""
    triggered_at: datetime = datetime.now()
    risk_level: RiskLevel = RiskLevel.LOW
    message: str = ""
    is_sent: bool = False
    notification_sent: bool = False
    sent_channels: List[AlertChannel] = None

    def to_dict(self) -> Dict:
        return {
            "alert_id": self.alert_id,
            "rule_id": self.rule_id,
            "triggered_at": self.triggered_at.isoformat(),
            "risk_level": self.risk_level.value,
            "message": self.message,
            "is_sent": self.is_sent,
            "notification_sent": self.notification_sent,
            "sent_channels": [c.value for c in self.sent_channels] if self.sent_channels else [],
        }


class AlertManager:
    """告警管理器"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.rules: Dict[str, AlertRule] = {}
        self.alert_history: List[AlertHistory] = []
        self.notification_channels = {
            "email": self._init_email_channel(),
            "webhook": self._init_webhook_channel(),
            "sms": self._init_sms_channel(),
            "in_app": self._init_in_app_channel(),
        }

        logger.info("告警管理器初始化")

    def _init_email_channel(self):
        """初始化邮件告警渠道"""
        try:
            import os

            smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
            smtp_port = int(os.getenv("SMTP_PORT", "587"))
            smtp_username = os.getenv("SMTP_USERNAME", "")
            smtp_password = os.getenv("SMTP_PASSWORD", "")

            return {
                "type": AlertChannel.EMAIL,
                "config": {
                    "smtp_server": smtp_server,
                    "smtp_port": smtp_port,
                    "smtp_username": smtp_username,
                    "is_enabled": True,
                },
            }
        except Exception as e:
            logger.error(f"初始化邮件渠道失败: {e}")
            return {"type": AlertChannel.EMAIL, "config": {"is_enabled": False}}

    def _init_webhook_channel(self):
        """初始化Webhook告警渠道"""
        try:

            webhook_urls = {
                "low": os.getenv("WEBHOOK_LOW_URL", "https://api.example.com/webhook/low"),
                "medium": os.getenv("WEBHOOK_MEDIUM_URL", "https://api.example.com/webhook/medium"),
                "high": os.getenv("WEBHOOK_HIGH_URL", "https://api.example.com/webhook/high"),
                "critical": os.getenv("WEBHOOK_CRITICAL_URL", "https://api.example.com/webhook/critical"),
            }

            return {
                "type": AlertChannel.WEBHOOK,
                "config": {"webhook_urls": webhook_urls, "timeout": 30, "retry_count": 3, "is_enabled": True},
            }
        except Exception as e:
            logger.error(f"初始化Webhook渠道失败: {e}")
            return {"type": AlertChannel.WEBHOOK, "config": {"is_enabled": False}}

    def _init_sms_channel(self):
        """初始化短信告警渠道"""
        try:
            import os

            sms_api_url = os.getenv("SMS_API_URL", "")
            sms_api_key = os.getenv("SMS_API_KEY", "")

            return {
                "type": AlertChannel.SMS,
                "config": {
                    "api_url": sms_api_url,
                    "api_key": sms_api_key,
                    "template_id": "ALERT_TEMPLATE",
                    "is_enabled": False,
                },
            }
        except Exception as e:
            logger.error(f"初始化短信渠道失败: {e}")
            return {"type": AlertChannel.SMS, "config": {"is_enabled": False}}

    def _init_in_app_channel(self):
        """初始化应用内告警渠道"""
        try:
            import os

            in_app_push_service = os.getenv("IN_APP_PUSH_SERVICE", "")

            return {
                "type": AlertChannel.IN_APP,
                "config": {"push_service": in_app_push_service, "max_retries": 3, "is_enabled": False},
            }
        except Exception as e:
            logger.error(f"初始化应用内渠道失败: {e}")
            return {"type": AlertChannel.IN_APP, "config": {"is_enabled": False}}

    async def create_alert_rule(
        self, rule_name: str, risk_level: RiskLevel, conditions: Dict, channel: AlertChannel = AlertChannel.EMAIL
    ) -> AlertRule:
        """
        创建告警规则

        Args:
            rule_name: 规则名称
            risk_level: 风险等级
            conditions: 条件配置
            channel: 告警渠道

        Returns:
            AlertRule: 创建的规则
        """
        try:
            import uuid

            rule_id = f"rule_{uuid.uuid4()}"

            rule = AlertRule(
                rule_id=rule_id,
                rule_name=rule_name,
                risk_level=risk_level,
                channel=channel,
                conditions=conditions,
                is_enabled=True,
                created_at=datetime.now(),
            )

            self.rules[rule_id] = rule
            self.logger.info(f"创建告警规则: {rule_name} (风险等级{risk_level.value})")

            return rule

        except Exception as e:
            self.logger.error(f"创建告警规则失败: {e}")
            raise

    async def check_and_trigger_alerts(
        self, portfolio_id: str, current_metrics: Any, rule_id_filter: Optional[str] = None
    ) -> List[AlertHistory]:
        """
        检查并触发告警

        Args:
            portfolio_id: 投资组合ID
            current_metrics: 当前风险指标
            rule_id_filter: 规则ID过滤器

        Returns:
            List[AlertHistory]: 触发的告警列表
        """
        triggered_alerts = []

        try:
            for rule_id, rule in self.rules.items():
                if not rule.is_enabled:
                    continue

                if rule_id_filter and rule_id != rule_id_filter:
                    continue

                if self._check_rule_conditions(rule.conditions, current_metrics):
                    alert_history = AlertHistory(
                        alert_id=f"alert_{datetime.now().isoformat()}",
                        rule_id=rule_id,
                        triggered_at=datetime.now(),
                        risk_level=rule.risk_level,
                        message=rule.rule_name,
                        is_sent=False,
                        notification_sent=False,
                    )

                    await self._send_alert_notification(alert_history, rule.channel)
                    self.alert_history.append(alert_history)
                    triggered_alerts.append(alert_history)

                    self.logger.warning(f"触发告警: {rule.rule_name} (风险等级{rule.risk_level.value})")

        except Exception as e:
            self.logger.error(f"检查和触发告警失败: {e}")

        return triggered_alerts

    def _check_rule_conditions(self, conditions: Dict, current_metrics: Any) -> bool:
        """检查规则条件是否满足"""
        try:
            for key, value in conditions.items():
                if key == "var_95_threshold":
                    if current_metrics.get("var_95", 0) > value:
                        return True
                elif key == "var_99_threshold":
                    if current_metrics.get("var_99", 0) > value:
                        return True
                elif key == "max_drawdown_threshold":
                    if abs(current_metrics.get("max_drawdown", 0)) > abs(value):
                        return True
                elif key == "volatility_threshold":
                    if current_metrics.get("volatility", 0) > value:
                        return True

            return False

        except Exception as e:
            self.logger.error(f"检查规则条件失败: {e}")
            return False

    async def _send_alert_notification(self, alert: AlertHistory, channel: AlertChannel) -> None:
        """发送告警通知"""
        try:
            if not channel["config"]["is_enabled"]:
                self.logger.warning(f"渠道{channel.value}未启用")
                return

            if channel.value == AlertChannel.EMAIL:
                await self._send_email_alert(alert)
            elif channel.value == AlertChannel.WEBHOOK:
                await self._send_webhook_alert(alert)
            elif channel.value == AlertChannel.SMS:
                await self._send_sms_alert(alert)
            elif channel.value == AlertChannel.IN_APP:
                await self._send_in_app_alert(alert)

            alert.notification_sent = True

        except Exception as e:
            self.logger.error(f"发送告警通知失败: {e}")

    async def _send_email_alert(self, alert: AlertHistory) -> None:
        """发送邮件告警"""
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            import os

            smtp_server = self.notification_channels["email"]["config"]["smtp_server"]
            smtp_port = self.notification_channels["email"]["config"]["smtp_port"]
            smtp_username = self.notification_channels["email"]["config"]["smtp_username"]
            smtp_password = self.notification_channels["email"]["config"]["smtp_password"]

            to_email = os.getenv("ALERT_EMAIL", "")

            subject = f"[{alert.risk_level.value}] 风险告警 - {alert.message}"

            body = f"""
            告警详情：
            - 告警ID: {alert.alert_id}
            - 规则ID: {alert.rule_id}
            - 触发时间: {alert.triggered_at.isoformat()}
            - 风险等级: {alert.risk_level.value}
            - 消息: {alert.message}
            
            请及时处理此风险事件。
            """

            msg = MIMEMultipart()
            msg["From"] = smtp_username
            msg["To"] = to_email
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain"))

            with smtplib.SMTP(smtp_server, smtp_port, timeout=30) as server:
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.send_message(msg)
                server.quit()

            self.logger.info(f"邮件告警已发送: {alert.alert_id}")

        except Exception as e:
            self.logger.error(f"发送邮件告警失败: {e}")

    async def _send_webhook_alert(self, alert: AlertHistory) -> None:
        """发送Webhook告警"""
        try:
            import httpx

            risk_level = alert.risk_level.value
            webhook_url = self.notification_channels["webhook"]["config"]["webhook_urls"].get(risk_level, "")

            payload = {
                "alert_id": alert.alert_id,
                "rule_id": alert.rule_id,
                "risk_level": risk_level,
                "message": alert.message,
                "triggered_at": alert.triggered_at.isoformat(),
                "metadata": {
                    "portfolio_id": alert.metadata.get("portfolio_id"),
                    "stock_code": alert.metadata.get("stock_code"),
                },
            }

            timeout = self.notification_channels["webhook"]["config"]["timeout"]

            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(webhook_url, json=payload)

                if response.status_code == 200:
                    self.logger.info(f"Webhook告警已发送: {alert.alert_id}")
                else:
                    self.logger.error(f"Webhook告警发送失败: {response.status_code}")

        except Exception as e:
            self.logger.error(f"发送Webhook告警失败: {e}")

    async def get_alert_history(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """获取告警历史"""
        try:
            start_idx = offset
            end_idx = min(start_idx + limit, len(self.alert_history))

            history_slice = self.alert_history[start_idx:end_idx]

            return [alert.to_dict() for alert in history_slice]

        except Exception as e:
            self.logger.error(f"获取告警历史失败: {e}")
            return []

    async def enable_alert_rule(self, rule_id: str) -> bool:
        """启用告警规则"""
        try:
            if rule_id not in self.rules:
                return False

            rule = self.rules[rule_id]
            rule.is_enabled = True
            rule.updated_at = datetime.now()

            self.logger.info(f"启用告警规则: {rule.rule_name}")
            return True

        except Exception as e:
            self.logger.error(f"启用告警规则失败: {e}")
            return False

    async def disable_alert_rule(self, rule_id: str) -> bool:
        """禁用告警规则"""
        try:
            if rule_id not in self.rules:
                return False

            rule = self.rules[rule_id]
            rule.is_enabled = False
            rule.updated_at = datetime.now()

            self.logger.info(f"禁用告警规则: {rule.rule_name}")
            return True

        except Exception as e:
            self.logger.error(f"禁用告警规则失败: {e}")
            return False

    def get_rules_status(self) -> List[Dict]:
        """获取所有告警规则状态"""
        return [rule.to_dict() for rule in self.rules.values()]
