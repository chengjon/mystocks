from __future__ import annotations

import asyncio
import json
import logging
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, List, Optional

import aiohttp

from ._ai_alert_models import Alert, AlertSeverity, IAlertHandler

logger = logging.getLogger(__name__)


class EmailAlertHandler(IAlertHandler):
    """邮件告警处理器。"""

    def __init__(
        self,
        smtp_server: str,
        smtp_port: int,
        username: str,
        password: str,
        recipients: List[str],
    ):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.recipients = recipients

    async def handle_alert(self, alert: Alert) -> bool:
        try:
            msg = MIMEMultipart()
            msg["From"] = self.username
            msg["To"] = ", ".join(self.recipients)
            msg["Subject"] = f"[{alert.severity.value.upper()}] MyStocks AI告警: {alert.rule_name}"

            body = f"""
            <html>
            <body>
                <h2>MyStocks AI系统告警</h2>
                <p><strong>告警ID:</strong> {alert.id}</p>
                <p><strong>规则名称:</strong> {alert.rule_name}</p>
                <p><strong>严重性:</strong> {alert.severity.value}</p>
                <p><strong>告警类型:</strong> {alert.alert_type.value}</p>
                <p><strong>发生时间:</strong> {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>告警消息:</strong> {alert.message}</p>

                <h3>详细指标:</h3>
                <pre>{json.dumps(alert.metrics, indent=2, ensure_ascii=False)}</pre>

                <p>请及时处理此告警。</p>
                <p><small>此邮件由MyStocks AI监控系统自动发送</small></p>
            </body>
            </html>
            """

            msg.attach(MIMEText(body, "html", "utf-8"))
            await self._send_email(msg)
            logger.info("✅ 邮件告警发送成功: %s", alert.rule_name)
            return True
        except Exception as error:
            logger.error("❌ 邮件告警发送失败: %s", error)
            return False

    async def _send_email(self, msg: MIMEMultipart):
        def _send():
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _send)

    async def test_connection(self) -> bool:
        try:
            def _test():
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    server.starttls()
                    server.login(self.username, self.password)
                    return True

            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, _test)
        except Exception as error:
            logger.error("❌ 邮件连接测试失败: %s", error)
            return False


class WebhookAlertHandler(IAlertHandler):
    """Webhook 告警处理器。"""

    def __init__(
        self,
        webhook_url: str,
        headers: Dict[str, str] = None,
        auth_token: Optional[str] = None,
    ):
        self.webhook_url = webhook_url
        self.headers = headers or {"Content-Type": "application/json"}
        if auth_token:
            self.headers["Authorization"] = f"Bearer {auth_token}"

    async def handle_alert(self, alert: Alert) -> bool:
        try:
            payload = {
                "alert_id": alert.id,
                "rule_name": alert.rule_name,
                "severity": alert.severity.value,
                "alert_type": alert.alert_type.value,
                "message": alert.message,
                "timestamp": alert.timestamp.isoformat(),
                "metrics": alert.metrics,
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.webhook_url,
                    json=payload,
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as response:
                    if response.status == 200:
                        logger.info("✅ Webhook告警发送成功: %s", alert.rule_name)
                        return True
                    logger.error("❌ Webhook告警发送失败: HTTP %s", response.status)
                    return False
        except Exception as error:
            logger.error("❌ Webhook告警发送失败: %s", error)
            return False

    async def test_connection(self) -> bool:
        try:
            test_payload = {
                "test": True,
                "message": "MyStocks AI监控连接测试",
                "timestamp": datetime.now().isoformat(),
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.webhook_url,
                    json=test_payload,
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as response:
                    return response.status == 200
        except Exception as error:
            logger.error("❌ Webhook连接测试失败: %s", error)
            return False


class LogAlertHandler(IAlertHandler):
    """本地日志告警处理器。"""

    def __init__(self, log_file: str = "ai_alerts.log"):
        self.log_file = log_file
        self.logger = logging.getLogger("AIAlertHandler")

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))

        if not any(isinstance(handler, logging.FileHandler) for handler in self.logger.handlers):
            self.logger.addHandler(file_handler)
            self.logger.setLevel(logging.INFO)

    async def handle_alert(self, alert: Alert) -> bool:
        try:
            log_message = f"""
========================================
AI系统告警通知
========================================
告警ID: {alert.id}
规则名称: {alert.rule_name}
严重性: {alert.severity.value.upper()}
告警类型: {alert.alert_type.value}
发生时间: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
告警消息: {alert.message}

详细指标:
{json.dumps(alert.metrics, indent=2, ensure_ascii=False)}
========================================
            """

            if alert.severity == AlertSeverity.CRITICAL:
                self.logger.critical(log_message)
            elif alert.severity == AlertSeverity.WARNING:
                self.logger.warning(log_message)
            else:
                self.logger.info(log_message)
            return True
        except Exception as error:
            logger.exception("❌ 日志告警处理失败: %s", error)
            return False

    async def test_connection(self) -> bool:
        try:
            self.logger.info("MyStocks AI监控日志处理器连接测试")
            return True
        except Exception as error:
            logger.exception("❌ 日志处理器测试失败: %s", error)
            return False
