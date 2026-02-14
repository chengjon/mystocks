#!/usr/bin/env python3
"""
多渠道告警处理器

支持邮件、Webhook、日志等多种告警渠道的统一处理器。
提供配置化的告警路由、格式化模板、错误处理和重试机制。

作者: MyStocks AI开发团队
创建日期: 2025-11-16
版本: 1.0.0
依赖: smtplib, requests, asyncio
版权: MyStocks Project © 2025
"""

import asyncio
import json
import logging
import os
import smtplib
import ssl
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import aiohttp

# 监控组件导入
try:
    from .ai_alert_manager import Alert, AlertSeverity
except ImportError:
    Alert = Any
    AlertSeverity = Any

logger = logging.getLogger(__name__)

@dataclass
class AlertChannelConfig:
    """告警渠道配置"""

    name: str
    channel_type: str  # 'email', 'webhook', 'log', 'slack', 'teams', 'discord'
    enabled: bool = True
    priority: int = 1  # 1=highest, 5=lowest
    severity_filter: List[str] = None  # 过滤的严重级别
    rate_limit: int = 0  # 每小时最大告警数，0表示无限制
    retry_config: Dict[str, Any] = None

    def __post_init__(self):
        if self.severity_filter is None:
            self.severity_filter = ["critical", "warning", "info"]
        if self.retry_config is None:
            self.retry_config = {
                "max_retries": 3,
                "retry_delay": 5,  # 秒
                "backoff_factor": 2.0,
                "timeout": 30,
            }


@dataclass
class EmailConfig:
    """邮件配置"""

    smtp_server: str
    smtp_port: int = 587
    username: str
    password: str
    use_tls: bool = True
    use_ssl: bool = False
    from_email: str
    to_emails: List[str]
    subject_template: str = "MyStocks告警: {alert_type}"
    body_template: str = ""

    def __post_init__(self):
        if not self.body_template:
            self.body_template = """
告警详情:

严重程度: {severity}
规则名称: {rule_name}
触发时间: {timestamp}
当前值: {current_value}
阈值: {threshold}
消息: {message}

请及时处理此告警。

--
MyStocks AI监控系统
"""


@dataclass
class WebhookConfig:
    """Webhook配置"""

    url: str
    method: str = "POST"
    headers: Dict[str, str] = None
    payload_template: str = None
    timeout: int = 30
    verify_ssl: bool = True
    auth_config: Dict[str, str] = None

    def __post_init__(self):
        if self.headers is None:
            self.headers = {"Content-Type": "application/json"}
        if self.payload_template is None:
            self.payload_template = json.dumps(
                {
                    "alert_id": "{alert_id}",
                    "rule_name": "{rule_name}",
                    "severity": "{severity}",
                    "message": "{message}",
                    "timestamp": "{timestamp}",
                    "current_value": "{current_value}",
                    "threshold": "{threshold}",
                    "source": "MyStocks监控系统",
                },
                ensure_ascii=False,
            )


@dataclass
class LogConfig:
    """日志配置"""

    logger_name: str = "mystocks.alerts"
    level: str = "WARNING"
    format_template: str = None
    file_path: Optional[str] = None
    rotate_config: Dict[str, Any] = None

    def __post_init__(self):
        if self.format_template is None:
            self.format_template = (
                "{timestamp} | {severity:8} | {rule_name:20} | "
                "值: {current_value:8.2f} | 阈值: {threshold:8.2f} | {message}"
            )
        if self.rotate_config is None:
            self.rotate_config = {
                "max_size": 10 * 1024 * 1024,  # 10MB
                "backup_count": 5,
                "when": "midnight",
                "interval": 1,
            }


class AlertHandler:
    """告警处理器基类"""

    def __init__(self, config: AlertChannelConfig):
        self.config = config
        self.sent_count = 0
        self.success_count = 0
        self.failure_count = 0
        self.last_sent_time: Optional[datetime] = None
        self.rate_limiter = RateLimiter(config.rate_limit) if config.rate_limit > 0 else None

    async def handle_alert(self, alert: Alert) -> bool:
        """处理告警"""
        try:
            # 检查严重级别过滤
            if alert.severity.value.lower() not in [s.lower() for s in self.config.severity_filter]:
                return False

            # 检查启用状态
            if not self.config.enabled:
                return False

            # 检查速率限制
            if self.rate_limiter and not self.rate_limiter.allow_request():
                logger.warning("告警%s触发速率限制", self.config.name)
                return False

            # 执行发送
            success = await self._send_alert(alert)

            # 更新统计
            self._update_statistics(success)

            return success

        except Exception as e:
            logger.error("告警处理器%s执行失败: %s", self.config.name, e)
            self.failure_count += 1
            return False

    def _update_statistics(self, success: bool):
        """更新统计信息"""
        self.sent_count += 1
        if success:
            self.success_count += 1
        else:
            self.failure_count += 1
        self.last_sent_time = datetime.now()

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        success_rate = (self.success_count / max(1, self.sent_count)) * 100

        return {
            "name": self.config.name,
            "channel_type": self.config.channel_type,
            "enabled": self.config.enabled,
            "total_sent": self.sent_count,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "success_rate": f"{success_rate:.1f}%",
            "last_sent": self.last_sent_time.isoformat() if self.last_sent_time else None,
            "rate_limited": self.rate_limiter.is_limited() if self.rate_limiter else False,
        }

    async def _send_alert(self, alert: Alert) -> bool:
        """发送告警 - 子类实现"""
        raise NotImplementedError("子类必须实现_send_alert方法")


class EmailAlertHandler(AlertHandler):
    """邮件告警处理器"""

    def __init__(self, config: AlertChannelConfig, email_config: EmailConfig):
        super().__init__(config)
        self.email_config = email_config

        # 初始化SMTP连接
        self.smtp_connection = None

    async def _send_alert(self, alert: Alert) -> bool:
        """发送邮件告警"""

        try:
            # 准备邮件内容
            subject = self._format_template(self.email_config.subject_template, alert)
            body = self._format_template(self.email_config.body_template, alert)

            # 创建邮件
            msg = MIMEMultipart()
            msg["From"] = self.email_config.from_email
            msg["To"] = ", ".join(self.email_config.to_emails)
            msg["Subject"] = subject

            # 添加HTML版本（可选）
            html_body = self._create_html_body(alert)
            msg.attach(MIMEText(body, "plain", "utf-8"))
            if html_body:
                msg.attach(MIMEText(html_body, "html", "utf-8"))

            # 发送邮件
            await self._send_email_async(msg)

            logger.info("邮件告警已发送到: %s", self.email_config.to_emails)
            return True

        except Exception as e:
            logger.error("发送邮件告警失败: %s", e)
            return False

    def _format_template(self, template: str, alert: Alert) -> str:
        """格式化模板"""

        format_dict = {
            "alert_id": alert.id,
            "rule_name": alert.rule_name,
            "severity": alert.severity.value,
            "message": alert.message,
            "timestamp": alert.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "current_value": alert.metrics.get("current_value", "N/A"),
            "threshold": alert.metrics.get("threshold", "N/A"),
            "duration": alert.metrics.get("duration_seconds", 0),
        }

        try:
            return template.format(**format_dict)
        except KeyError as e:
            logger.warning("邮件模板格式化失败，缺少键: %s", e)
            return template

    def _create_html_body(self, alert: Alert) -> str:
        """创建HTML邮件内容"""

        severity_colors = {
            "critical": "#ff4444",
            "warning": "#ff8800",
            "info": "#0088ff",
        }

        color = severity_colors.get(alert.severity.value.lower(), "#666666")

        html = f"""
        <html>
        <head>
            <style>
                .alert-container {{
                    font-family: Arial, sans-serif;
                    max-width: 600px;
                    margin: 0 auto;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                }}
                .header {{
                    background-color: {color};
                    color: white;
                    padding: 20px;
                    border-radius: 5px 5px 0 0;
                }}
                .content {{
                    padding: 20px;
                    background-color: #f9f9f9;
                }}
                .metric {{
                    background-color: white;
                    padding: 10px;
                    margin: 10px 0;
                    border-radius: 3px;
                    border-left: 4px solid {color};
                }}
            </style>
        </head>
        <body>
            <div class="alert-container">
                <div class="header">
                    <h2>MyStocks AI监控告警</h2>
                    <p>严重程度: {alert.severity.value.upper()}</p>
                </div>
                <div class="content">
                    <div class="metric">
                        <strong>规则名称:</strong> {alert.rule_name}<br>
                        <strong>触发时间:</strong> {alert.timestamp.strftime("%Y-%m-%d %H:%M:%S")}<br>
                        <strong>告警消息:</strong> {alert.message}
                    </div>
                    <div class="metric">
                        <strong>当前值:</strong> {alert.metrics.get("current_value", "N/A")}<br>
                        <strong>阈值:</strong> {alert.metrics.get("threshold", "N/A")}<br>
                        <strong>持续时间:</strong> {alert.metrics.get("duration_seconds", 0)}秒
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

        return html

    async def _send_email_async(self, msg: MIMEMultipart):
        """异步发送邮件"""

        def _send():
            try:
                if self.email_config.use_ssl:
                    server = smtplib.SMTP_SSL(self.email_config.smtp_server, self.email_config.smtp_port)
                else:
                    server = smtplib.SMTP(self.email_config.smtp_server, self.email_config.smtp_port)
                    if self.email_config.use_tls:
                        context = ssl.create_default_context()
                        server.starttls(context=context)

                server.login(self.email_config.username, self.email_config.password)
                server.send_message(msg)
                server.quit()

            except Exception as e:
                logger.error("SMTP发送失败: %s", e)
                raise e

        # 在线程池中执行同步的SMTP操作
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _send)


class WebhookAlertHandler(AlertHandler):
    """Webhook告警处理器"""

    def __init__(self, config: AlertChannelConfig, webhook_config: WebhookConfig):
        super().__init__(config)
        self.webhook_config = webhook_config

        # 验证URL
        parsed = urlparse(webhook_config.url)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError(f"无效的Webhook URL: {webhook_config.url}")

    async def _send_alert(self, alert: Alert) -> bool:
        """发送Webhook告警"""

        try:
            # 准备请求数据
            payload_data = self._prepare_payload(alert)

            # 发送请求
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.webhook_config.timeout),
                connector=aiohttp.TCPConnector(verify_ssl=self.webhook_config.verify_ssl),
            ) as session:
                headers = self.webhook_config.headers.copy()

                # 添加认证头
                if self.webhook_config.auth_config:
                    if "bearer" in self.webhook_config.auth_config:
                        headers["Authorization"] = f"Bearer {self.webhook_config.auth_config['bearer']}"
                    elif "api_key" in self.webhook_config.auth_config:
                        headers["X-API-Key"] = self.webhook_config.auth_config["api_key"]

                async with session.request(
                    method=self.webhook_config.method,
                    url=self.webhook_config.url,
                    headers=headers,
                    json=payload_data if self.webhook_config.method.upper() == "POST" else None,
                    data=payload_data if self.webhook_config.method.upper() != "POST" else None,
                ) as response:
                    if response.status < 400:
                        logger.info("Webhook告警发送成功: %s", self.webhook_config.url)
                        return True
                    else:
                        error_text = await response.text()
                        logger.error("Webhook请求失败: HTTP %s - %s", response.status, error_text)
                        return False

        except asyncio.TimeoutError:
            logger.error("Webhook请求超时: %s", self.webhook_config.url)
            return False
        except Exception as e:
            logger.error("Webhook发送失败: %s", e)
            return False

    def _prepare_payload(self, alert: Alert) -> Dict[str, Any]:
        """准备载荷数据"""

        if self.webhook_config.payload_template:
            try:
                # 尝试解析JSON模板
                payload_str = self.webhook_config.payload_template.format(
                    alert_id=alert.id,
                    rule_name=alert.rule_name,
                    severity=alert.severity.value,
                    message=alert.message,
                    timestamp=alert.timestamp.isoformat(),
                    current_value=alert.metrics.get("current_value", "N/A"),
                    threshold=alert.metrics.get("threshold", "N/A"),
                )
                return json.loads(payload_str)
            except (KeyError, json.JSONDecodeError) as e:
                logger.warning("Webhook模板解析失败: %s", e)

        # 默认载荷格式
        return {
            "alert_id": alert.id,
            "rule_name": alert.rule_name,
            "severity": alert.severity.value,
            "message": alert.message,
            "timestamp": alert.timestamp.isoformat(),
            "current_value": alert.metrics.get("current_value"),
            "threshold": alert.metrics.get("threshold"),
            "duration_seconds": alert.metrics.get("duration_seconds", 0),
            "source": "MyStocks监控系统",
        }


class LogAlertHandler(AlertHandler):
    """日志告警处理器"""

    def __init__(self, config: AlertChannelConfig, log_config: LogConfig):
        super().__init__(config)
        self.log_config = log_config

        # 设置日志记录器
        self.logger = logging.getLogger(self.log_config.logger_name)

        # 配置文件日志（如果指定）
        if self.log_config.file_path:
            self._setup_file_handler()

    def _setup_file_handler(self):
        """设置文件处理器"""

        try:
            from logging.handlers import RotatingFileHandler

            file_handler = RotatingFileHandler(
                filename=self.log_config.file_path,
                maxBytes=self.log_config.rotate_config["max_size"],
                backupCount=self.log_config.rotate_config["backup_count"],
                encoding="utf-8",
            )

            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

        except ImportError:
            # 简单的文件处理器（无轮转）
            file_handler = logging.FileHandler(self.log_config.file_path, encoding="utf-8")
            self.logger.addHandler(file_handler)

        # 设置日志级别
        log_level = getattr(logging, self.log_config.level.upper(), logging.WARNING)
        self.logger.setLevel(log_level)

    async def _send_alert(self, alert: Alert) -> bool:
        """记录日志告警"""

        try:
            # 格式化日志消息
            log_message = self._format_log_message(alert)

            # 根据严重级别选择日志级别
            if alert.severity.value.lower() == "critical":
                self.logger.critical(log_message)
            elif alert.severity.value.lower() == "warning":
                self.logger.warning(log_message)
            else:
                self.logger.info(log_message)

            return True

        except Exception as e:
            logger.error("日志记录失败: %s", e)
            return False

    def _format_log_message(self, alert: Alert) -> str:
        """格式化日志消息"""

        format_dict = {
            "timestamp": alert.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "severity": alert.severity.value.upper(),
            "rule_name": alert.rule_name,
            "current_value": alert.metrics.get("current_value", "N/A"),
            "threshold": alert.metrics.get("threshold", "N/A"),
            "message": alert.message,
        }

        try:
            return self.log_config.format_template.format(**format_dict)
        except KeyError as e:
            logger.warning("日志格式模板缺少键: %s", e)
            return str(alert)


class RateLimiter:
    """速率限制器"""

    def __init__(self, max_requests: int):
        self.max_requests = max_requests
        self.requests = []

    def allow_request(self) -> bool:
        """检查是否允许请求"""
        now = datetime.now()

        # 清理1小时前的请求记录
        hour_ago = now - timedelta(hours=1)
        self.requests = [req_time for req_time in self.requests if req_time > hour_ago]

        # 检查是否超限
        if len(self.requests) >= self.max_requests:
            return False

        # 记录当前请求
        self.requests.append(now)
        return True

    def is_limited(self) -> bool:
        """检查是否被限制"""
        now = datetime.now()
        hour_ago = now - timedelta(hours=1)
        recent_requests = [req_time for req_time in self.requests if req_time > hour_ago]
        return len(recent_requests) >= self.max_requests


