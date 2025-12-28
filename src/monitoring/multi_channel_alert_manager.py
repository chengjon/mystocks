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
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import aiohttp
from urllib.parse import urlparse

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


class MultiChannelAlertManager:
    """多渠道告警管理器"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._get_default_config()
        self.handlers: Dict[str, AlertHandler] = {}
        self.alert_history: List[Dict[str, Any]] = []

        # 初始化默认处理器
        self._initialize_default_handlers()

        logger.info("✅ 多渠道告警管理器初始化完成")

    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "max_history_size": 1000,
            "enable_history": True,
            "template_dir": Path(__file__).parent / "templates",
            "default_retry_delay": 5,
            "enable_statistics": True,
        }

    def _initialize_default_handlers(self):
        """初始化默认处理器"""

        # 添加基础日志处理器
        log_config = AlertChannelConfig(
            name="default_log",
            channel_type="log",
            severity_filter=["critical", "warning", "info"],
        )

        log_handler = LogAlertHandler(log_config, LogConfig())
        self.add_handler(log_handler)

    def add_handler(self, handler: AlertHandler) -> bool:
        """添加告警处理器"""

        try:
            self.handlers[handler.config.name] = handler
            logger.info("✅ 已添加告警处理器: %s", handler.config.name)
            return True
        except Exception as e:
            logger.error("添加告警处理器失败: %s", e)
            return False

    def remove_handler(self, handler_name: str) -> bool:
        """移除告警处理器"""

        if handler_name in self.handlers:
            del self.handlers[handler_name]
            logger.info("✅ 已移除告警处理器: %s", handler_name)
            return True
        return False

    async def send_alert(self, alert: Alert) -> Dict[str, bool]:
        """发送告警到所有启用的处理器"""

        results = {}

        # 按优先级排序处理器
        sorted_handlers = sorted(self.handlers.values(), key=lambda h: h.config.priority)

        # 并发发送到所有处理器
        tasks = []
        for handler in sorted_handlers:
            if handler.config.enabled:
                task = asyncio.create_task(self._send_with_retry(handler, alert))
                tasks.append((handler.config.name, task))

        # 收集结果
        for handler_name, task in tasks:
            try:
                success = await task
                results[handler_name] = success
            except Exception as e:
                logger.error("告警发送到%s时发生异常: %s", handler_name, e)
                results[handler_name] = False

        # 记录告警历史
        if self.config["enable_history"]:
            self._record_alert_history(alert, results)

        # 统计发送结果
        success_count = sum(1 for success in results.values() if success)
        logger.info("告警已发送到%s个渠道，成功%s个", len(results), success_count)

        return results

    async def _send_with_retry(self, handler: AlertHandler, alert: Alert) -> bool:
        """带重试的发送"""

        max_retries = handler.config.retry_config.get("max_retries", 3)
        retry_delay = handler.config.retry_config.get("retry_delay", 5)
        backoff_factor = handler.config.retry_config.get("backoff_factor", 2.0)

        for attempt in range(max_retries + 1):
            try:
                success = await handler.handle_alert(alert)
                if success:
                    return True

                # 如果不是最后一次尝试，等待后重试
                if attempt < max_retries:
                    wait_time = retry_delay * (backoff_factor**attempt)
                    await asyncio.sleep(wait_time)

            except Exception as e:
                logger.warning("告警发送尝试%s失败: %s", attempt + 1, e)
                if attempt < max_retries:
                    wait_time = retry_delay * (backoff_factor**attempt)
                    await asyncio.sleep(wait_time)

        return False

    def _record_alert_history(self, alert: Alert, results: Dict[str, bool]):
        """记录告警历史"""

        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "alert_id": alert.id,
            "rule_name": alert.rule_name,
            "severity": alert.severity.value,
            "message": alert.message,
            "channels_results": results,
            "total_channels": len(results),
            "success_count": sum(1 for success in results.values() if success),
            "failure_count": sum(1 for success in results.values() if not success),
        }

        self.alert_history.append(history_entry)

        # 限制历史大小
        if len(self.alert_history) > self.config["max_history_size"]:
            self.alert_history = self.alert_history[-self.config["max_history_size"] :]

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""

        if not self.config["enable_statistics"]:
            return {"statistics_disabled": True}

        # 整体统计
        total_alerts = len(self.alert_history)
        successful_alerts = sum(1 for entry in self.alert_history if entry["success_count"] > 0)
        failed_alerts = sum(1 for entry in self.alert_history if entry["success_count"] == 0)

        # 处理器统计
        handler_stats = {}
        for handler_name, handler in self.handlers.items():
            handler_stats[handler_name] = handler.get_statistics()

        # 严重级别统计
        severity_stats = {}
        for entry in self.alert_history:
            severity = entry["severity"]
            if severity not in severity_stats:
                severity_stats[severity] = 0
            severity_stats[severity] += 1

        # 最近告警
        recent_alerts = self.alert_history[-10:] if self.alert_history else []

        return {
            "total_alerts": total_alerts,
            "successful_alerts": successful_alerts,
            "failed_alerts": failed_alerts,
            "success_rate": f"{(successful_alerts / max(1, total_alerts) * 100):.1f}%",
            "handler_statistics": handler_stats,
            "severity_distribution": severity_stats,
            "recent_alerts": recent_alerts,
            "active_handlers": len([h for h in self.handlers.values() if h.config.enabled]),
            "total_handlers": len(self.handlers),
        }

    def add_email_handler(
        self,
        handler_name: str,
        email_config: EmailConfig,
        priority: int = 1,
        severity_filter: Optional[List[str]] = None,
    ) -> bool:
        """添加邮件处理器"""

        try:
            channel_config = AlertChannelConfig(
                name=handler_name,
                channel_type="email",
                priority=priority,
                severity_filter=severity_filter or ["critical", "warning"],
            )

            handler = EmailAlertHandler(channel_config, email_config)
            return self.add_handler(handler)

        except Exception as e:
            logger.error("添加邮件处理器失败: %s", e)
            return False

    def add_webhook_handler(
        self,
        handler_name: str,
        webhook_config: WebhookConfig,
        priority: int = 1,
        severity_filter: Optional[List[str]] = None,
    ) -> bool:
        """添加Webhook处理器"""

        try:
            channel_config = AlertChannelConfig(
                name=handler_name,
                channel_type="webhook",
                priority=priority,
                severity_filter=severity_filter or ["critical", "warning", "info"],
            )

            handler = WebhookAlertHandler(channel_config, webhook_config)
            return self.add_handler(handler)

        except Exception as e:
            logger.error("添加Webhook处理器失败: %s", e)
            return False

    def add_log_handler(
        self,
        handler_name: str,
        log_config: LogConfig,
        priority: int = 5,
        severity_filter: Optional[List[str]] = None,
    ) -> bool:
        """添加日志处理器"""

        try:
            channel_config = AlertChannelConfig(
                name=handler_name,
                channel_type="log",
                priority=priority,
                severity_filter=severity_filter or ["critical", "warning", "info"],
            )

            handler = LogAlertHandler(channel_config, log_config)
            return self.add_handler(handler)

        except Exception as e:
            logger.error("添加日志处理器失败: %s", e)
            return False

    def export_configuration(self) -> str:
        """导出配置"""

        config_data = {
            "timestamp": datetime.now().isoformat(),
            "config": self.config,
            "handlers": {},
            "alert_history": self.alert_history[-100:],  # 最近100条
        }

        # 导出处理器配置
        for name, handler in self.handlers.items():
            handler_data = {
                "config": asdict(handler.config),
                "statistics": handler.get_statistics(),
            }

            if isinstance(handler, EmailAlertHandler):
                handler_data["email_config"] = asdict(handler.email_config)
            elif isinstance(handler, WebhookAlertHandler):
                handler_data["webhook_config"] = asdict(handler.webhook_config)
            elif isinstance(handler, LogAlertHandler):
                handler_data["log_config"] = asdict(handler.log_config)

            config_data["handlers"][name] = handler_data

        return json.dumps(config_data, indent=2, default=str, ensure_ascii=False)

    async def import_configuration(self, config_json: str) -> bool:
        """导入配置"""

        try:
            config_data = json.loads(config_json)

            # 清空现有处理器
            self.handlers.clear()

            # 恢复配置
            self.config.update(config_data.get("config", {}))

            # 恢复处理器
            for name, handler_data in config_data.get("handlers", {}).items():
                try:
                    config = AlertChannelConfig(**handler_data["config"])

                    if config.channel_type == "email":
                        email_config = EmailConfig(**handler_data["email_config"])
                        handler = EmailAlertHandler(config, email_config)
                    elif config.channel_type == "webhook":
                        webhook_config = WebhookConfig(**handler_data["webhook_config"])
                        handler = WebhookAlertHandler(config, webhook_config)
                    elif config.channel_type == "log":
                        log_config = LogConfig(**handler_data["log_config"])
                        handler = LogAlertHandler(config, log_config)
                    else:
                        logger.warning("未知的处理器类型: %s", config.channel_type)
                        continue

                    self.add_handler(handler)

                except Exception as e:
                    logger.error("恢复处理器%s失败: %s", name, e)
                    continue

            # 恢复告警历史
            self.alert_history = config_data.get("alert_history", [])

            logger.info("✅ 配置导入成功: %s个处理器", len(self.handlers))
            return True

        except Exception as e:
            logger.error("配置导入失败: %s", e)
            return False


# 全局单例管理器
_multi_channel_manager = None


def get_multi_channel_alert_manager() -> MultiChannelAlertManager:
    """获取多渠道告警管理器单例"""
    global _multi_channel_manager

    if _multi_channel_manager is None:
        _multi_channel_manager = MultiChannelAlertManager()

    return _multi_channel_manager


# 便捷函数
async def send_alert_to_all_channels(alert: Alert) -> Dict[str, bool]:
    """发送告警到所有渠道"""
    manager = get_multi_channel_alert_manager()
    return await manager.send_alert(alert)


def add_email_alert_handler(name: str, email_config: EmailConfig) -> bool:
    """添加邮件告警处理器"""
    manager = get_multi_channel_alert_manager()
    return manager.add_email_handler(name, email_config)


def add_webhook_alert_handler(name: str, webhook_config: WebhookConfig) -> bool:
    """添加Webhook告警处理器"""
    manager = get_multi_channel_alert_manager()
    return manager.add_webhook_handler(name, webhook_config)


def add_log_alert_handler(name: str, log_config: LogConfig) -> bool:
    """添加日志告警处理器"""
    manager = get_multi_channel_alert_manager()
    return manager.add_log_handler(name, log_config)


if __name__ == "__main__":
    """示例用法"""

    async def main():
        print("📢 多渠道告警处理器演示")
        print("=" * 50)

        # 创建管理器
        manager = MultiChannelAlertManager()

        # 添加邮件处理器
        email_config = EmailConfig(
            smtp_server="smtp.gmail.com",
            smtp_port=587,
            username="your_email@gmail.com",
            password=os.getenv("SMTP_PASSWORD"),  # Should be set via environment variable
            from_email="mystocks@system.com",
            to_emails=["admin@company.com", "ops@company.com"],
        )

        manager.add_email_handler("email_alerts", email_config, priority=1)

        # 添加Webhook处理器
        webhook_config = WebhookConfig(url="https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK", method="POST")

        manager.add_webhook_handler("slack_alerts", webhook_config, priority=2)

        # 添加日志处理器
        log_config = LogConfig(
            logger_name="mystocks.alerts",
            level="INFO",
            file_path="/tmp/mystocks_alerts.log",
        )

        manager.add_log_handler("file_alerts", log_config, priority=3)

        # 模拟告警
        from src.monitoring.ai_alert_manager import Alert, AlertSeverity, AlertType

        test_alert = Alert(
            id="test_alert_001",
            rule_name="cpu_usage_high",
            alert_type=AlertType.SYSTEM_RESOURCE_HIGH,
            severity=AlertSeverity.CRITICAL,
            message="CPU使用率过高: 95% (阈值: 80%)",
            timestamp=datetime.now(),
            metrics={"current_value": 95.0, "threshold": 80.0, "duration_seconds": 120},
        )

        print("\n🔔 发送测试告警...")
        results = await manager.send_alert(test_alert)

        print("发送结果:")
        for channel, success in results.items():
            status = "✅ 成功" if success else "❌ 失败"
            print(f"  {channel}: {status}")

        # 获取统计信息
        print("\n📊 统计信息:")
        stats = manager.get_statistics()
        print(f"  总告警数: {stats['total_alerts']}")
        print(f"  成功率: {stats['success_rate']}")
        print(f"  活跃处理器: {stats['active_handlers']}/{stats['total_handlers']}")

        print("\n💾 导出配置...")
        config = manager.export_configuration()
        print(f"配置已导出 ({len(config)}字符)")

        print("\n🎉 演示完成!")

    # 运行演示
    asyncio.run(main())
