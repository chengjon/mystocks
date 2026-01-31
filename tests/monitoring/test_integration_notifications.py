"""
测试集成通知模块

提供测试监控告警的集成管理、通知推送和状态同步功能。
"""

import asyncio
import json
import logging
import queue
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import aiohttp
import requests
from jinja2 import Environment, FileSystemLoader, select_autoescape

from ..ai.test_data_manager import DataManager as AIDataManager


class NotificationLevel(Enum):
    """通知级别"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class NotificationType(Enum):
    """通知类型"""

    EMAIL = "email"
    WEBHOOK = "webhook"
    SLACK = "slack"
    TEAMS = "teams"
    SMS = "sms"
    PUSH = "push"


@dataclass
class NotificationTemplate:
    """通知模板"""

    id: str
    name: str
    subject_template: str
    body_template: str
    html_template: Optional[str] = None
    type: NotificationType = NotificationType.EMAIL
    category: str = "alert"  # alert, report, summary
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class NotificationMessage:
    """通知消息"""

    id: str
    level: NotificationLevel
    type: NotificationType
    title: str
    message: str
    html_body: Optional[str] = None
    recipients: List[str] = field(default_factory=list)
    channels: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    scheduled_at: Optional[datetime] = None
    status: str = "pending"  # pending, sent, failed
    retry_count: int = 0
    max_retries: int = 3
    retry_delay: int = 300  # 秒


@dataclass
class IntegrationConfig:
    """集成配置"""

    id: str
    name: str
    type: str  # webhook, api, database
    endpoint: str
    method: str = "POST"
    headers: Dict[str, str] = field(default_factory=dict)
    auth: Dict[str, str] = field(default_factory=dict)
    timeout: int = 30
    retry_policy: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    last_sync: Optional[datetime] = None


class NotificationChannel:
    """通知渠道基类"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = config.get("name", "unknown")
        self.enabled = config.get("enabled", True)

    async def send(self, message: NotificationMessage) -> bool:
        """发送通知"""
        raise NotImplementedError

    def validate_config(self) -> bool:
        """验证配置"""
        return True


class EmailNotificationChannel(NotificationChannel):
    """邮件通知渠道"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.smtp_server = config.get("smtp_server")
        self.smtp_port = config.get("smtp_port", 587)
        self.username = config.get("username")
        self.password = config.get("password")
        self.from_email = config.get("from_email")
        self.use_tls = config.get("use_tls", True)

    def validate_config(self) -> bool:
        required = ["smtp_server", "username", "password", "from_email"]
        return all(req in self.config for req in required)

    async def send(self, message: NotificationMessage) -> bool:
        if not self.enabled:
            return False

        try:
            import smtplib
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText

            # 创建邮件
            msg = MIMEMultipart()
            msg["From"] = self.from_email
            msg["To"] = ", ".join(message.recipients)
            msg["Subject"] = message.title

            # HTML内容
            if message.html_body:
                msg.attach(MIMEText(message.html_body, "html"))
            else:
                msg.attach(MIMEText(message.message, "plain"))

            # 发送邮件
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)

            logging.info(f"邮件发送成功: {message.id}")
            return True

        except Exception as e:
            logging.error(f"邮件发送失败: {e}")
            return False


class WebhookNotificationChannel(NotificationChannel):
    """Webhook通知渠道"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.url = config.get("url")
        self.headers = config.get("headers", {})
        self.timeout = config.get("timeout", 30)

    def validate_config(self) -> bool:
        return bool(self.url)

    async def send(self, message: NotificationMessage) -> bool:
        if not self.enabled:
            return False

        try:
            payload = {
                "id": message.id,
                "level": message.level.value,
                "type": message.type.value,
                "title": message.title,
                "message": message.message,
                "created_at": message.created_at.isoformat(),
                "metadata": message.metadata,
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.url,
                    json=payload,
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=self.timeout),
                ) as response:
                    if response.status == 200:
                        logging.info(f"Webhook发送成功: {message.id}")
                        return True
                    else:
                        logging.error(f"Webhook发送失败: {response.status}")
                        return False

        except Exception as e:
            logging.error(f"Webhook发送异常: {e}")
            return False


class SlackNotificationChannel(NotificationChannel):
    """Slack通知渠道"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.webhook_url = config.get("webhook_url")
        self.channel = config.get("channel", "#alerts")

    def validate_config(self) -> bool:
        return bool(self.webhook_url)

    async def send(self, message: NotificationMessage) -> bool:
        if not self.enabled:
            return False

        try:
            # 颜色映射
            color_map = {
                NotificationLevel.INFO: "#36a64f",
                NotificationLevel.WARNING: "#ff9500",
                NotificationLevel.ERROR: "#ff0000",
                NotificationLevel.CRITICAL: "#cc0000",
            }

            payload = {
                "channel": self.channel,
                "username": "MyStocks Alert Bot",
                "attachments": [
                    {
                        "color": color_map.get(message.level, "#808080"),
                        "title": message.title,
                        "text": message.message,
                        "fields": [
                            {"title": "ID", "value": message.id, "short": True},
                            {
                                "title": "Level",
                                "value": message.level.value,
                                "short": True,
                            },
                            {
                                "title": "Type",
                                "value": message.type.value,
                                "short": True,
                            },
                            {
                                "title": "Created",
                                "value": message.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                                "short": True,
                            },
                        ],
                        "footer": "MyStocks Test Monitoring",
                        "ts": int(message.created_at.timestamp()),
                    }
                ],
            }

            if message.html_body:
                payload["attachments"][0]["text"] = f"查看详情: {message.metadata.get('dashboard_url', '#')}"

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.webhook_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as response:
                    if response.status == 200:
                        logging.info(f"Slack发送成功: {message.id}")
                        return True
                    else:
                        logging.error(f"Slack发送失败: {response.status}")
                        return False

        except Exception as e:
            logging.error(f"Slack发送异常: {e}")
            return False


class TemplateEngine:
    """模板引擎"""

    def __init__(self, template_dir: Optional[str] = None):
        self.env = Environment(
            loader=FileSystemLoader(template_dir or str(Path(__file__).parent / "templates")),
            autoescape=select_autoescape(["html", "xml"]),
        )

    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """渲染模板"""
        try:
            template = self.env.get_template(template_name)
            return template.render(**context)
        except Exception as e:
            logging.error(f"模板渲染失败: {e}")
            return str(context)

    def render_subject(self, subject_template: str, context: Dict[str, Any]) -> str:
        """渲染主题"""
        try:
            template = self.env.from_string(subject_template)
            return template.render(**context)
        except Exception as e:
            logging.error(f"主题渲染失败: {e}")
            return subject_template


class NotificationManager:
    """通知管理器"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.channels: Dict[str, NotificationChannel] = {}
        self.templates: Dict[str, NotificationTemplate] = {}
        self.message_queue = queue.Queue()
        self.scheduled_messages: Dict[str, NotificationMessage] = {}
        self.send_thread: Optional[threading.Thread] = None
        self.is_running = False
        self.template_engine = TemplateEngine()

    def add_channel(self, channel: NotificationChannel):
        """添加通知渠道"""
        if channel.validate_config():
            self.channels[channel.name] = channel
            logging.info(f"添加通知渠道: {channel.name}")
        else:
            logging.error(f"通知渠道配置无效: {channel.name}")

    def add_template(self, template: NotificationTemplate):
        """添加通知模板"""
        self.templates[template.id] = template
        logging.info(f"添加通知模板: {template.name}")

    async def send_notification(self, message: NotificationMessage) -> bool:
        """发送通知"""
        success_count = 0

        for channel_name in message.channels:
            channel = self.channels.get(channel_name)
            if channel:
                try:
                    result = await channel.send(message)
                    if result:
                        success_count += 1
                        logging.info(f"通知发送成功: {message.id} via {channel_name}")
                    else:
                        logging.error(f"通知发送失败: {message.id} via {channel_name}")
                except Exception as e:
                    logging.error(f"通知发送异常: {message.id} via {channel_name}: {e}")

        # 更新消息状态
        message.status = "sent" if success_count > 0 else "failed"

        return success_count > 0

    def schedule_notification(self, message: NotificationMessage):
        """定时发送通知"""
        message.scheduled_at = datetime.now() + timedelta(seconds=message.retry_delay)
        self.scheduled_messages[message.id] = message

    async def process_scheduled_messages(self):
        """处理定时消息"""
        current_time = datetime.now()
        messages_to_send = []

        for msg_id, message in self.scheduled_messages.items():
            if message.scheduled_at and message.scheduled_at <= current_time:
                messages_to_send.append(message)
                del self.scheduled_messages[msg_id]

        for message in messages_to_send:
            await self.send_notification(message)

    async def notification_worker(self):
        """通知工作线程"""
        while self.is_running:
            try:
                # 处理队列中的消息
                if not self.message_queue.empty():
                    message = self.message_queue.get_nowait()
                    await self.send_notification(message)
                else:
                    # 处理定时消息
                    await self.process_scheduled_messages()
                    await asyncio.sleep(1)  # 避免CPU占用过高

            except Exception as e:
                logging.error(f"通知工作线程异常: {e}")
                await asyncio.sleep(5)

    def start(self):
        """启动通知管理器"""
        if not self.is_running:
            self.is_running = True
            self.send_thread = threading.Thread(target=self._run_notification_loop)
            self.send_thread.daemon = True
            self.send_thread.start()
            logging.info("通知管理器已启动")

    def stop(self):
        """停止通知管理器"""
        self.is_running = False
        if self.send_thread:
            self.send_thread.join()
        logging.info("通知管理器已停止")

    def _run_notification_loop(self):
        """运行通知循环"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.notification_worker())

    def queue_message(self, message: NotificationMessage):
        """队列消息"""
        self.message_queue.put(message)
        logging.info(f"消息已入队: {message.id}")

    def create_alert_message(
        self,
        level: NotificationLevel,
        title: str,
        message: str,
        recipients: List[str],
        channels: List[str],
        metadata: Dict[str, Any] = None,
    ) -> NotificationMessage:
        """创建告警消息"""
        return NotificationMessage(
            id=str(uuid.uuid4()),
            level=level,
            type=NotificationType.EMAIL,
            title=title,
            message=message,
            recipients=recipients,
            channels=channels,
            metadata=metadata or {},
        )

    def create_report_message(
        self, report_data: Dict[str, Any], recipients: List[str], channels: List[str]
    ) -> NotificationMessage:
        """创建报告消息"""
        return NotificationMessage(
            id=str(uuid.uuid4()),
            level=NotificationLevel.INFO,
            type=NotificationType.EMAIL,
            title=f"测试监控报告 - {datetime.now().strftime('%Y-%m-%d')}",
            message="测试监控报告已生成",
            recipients=recipients,
            channels=channels,
            metadata={"report_data": report_data},
        )


class TestIntegrationManager:
    """测试集成管理器"""

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
        self.config = self._load_config()
        self.notification_manager = NotificationManager(self.config)
        self.data_manager = AIDataManager()
        self.integrations: Dict[str, IntegrationConfig] = {}
        self.webhook_handlers: Dict[str, Callable] = {}
        self.status_sync_enabled = False

    def _load_config(self) -> Dict[str, Any]:
        """加载配置"""
        default_config = {
            "notification_channels": [],
            "templates": [],
            "integrations": [],
            "webhook_port": 8081,
            "sync_interval": 60,  # 同步间隔（秒）
        }

        if self.config_path and Path(self.config_path).exists():
            with open(self.config_path, "r", encoding="utf-8") as f:
                user_config = json.load(f)
                default_config.update(user_config)

        return default_config

    def initialize_channels(self):
        """初始化通知渠道"""
        channel_configs = self.config.get("notification_channels", [])

        for channel_config in channel_configs:
            channel_type = channel_config.get("type")

            if channel_type == "email":
                channel = EmailNotificationChannel(channel_config)
            elif channel_type == "webhook":
                channel = WebhookNotificationChannel(channel_config)
            elif channel_type == "slack":
                channel = SlackNotificationChannel(channel_config)
            else:
                logging.warning(f"未知渠道类型: {channel_type}")
                continue

            self.notification_manager.add_channel(channel)

    def initialize_templates(self):
        """初始化通知模板"""
        template_configs = self.config.get("templates", [])

        for template_config in template_configs:
            template = NotificationTemplate(
                id=template_config.get("id", str(uuid.uuid4())),
                name=template_config.get("name", "unnamed"),
                subject_template=template_config.get("subject_template", ""),
                body_template=template_config.get("body_template", ""),
                html_template=template_config.get("html_template"),
                type=NotificationType(template_config.get("type", "email")),
                category=template_config.get("category", "alert"),
            )
            self.notification_manager.add_template(template)

    def add_webhook_handler(self, endpoint: str, handler: Callable):
        """添加Webhook处理器"""
        self.webhook_handlers[endpoint] = handler
        logging.info(f"添加Webhook处理器: {endpoint}")

    async def handle_webhook(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """处理Webhook请求"""
        handler = self.webhook_handlers.get(endpoint)
        if handler:
            try:
                if asyncio.iscoroutinefunction(handler):
                    return await handler(data)
                else:
                    return handler(data)
            except Exception as e:
                logging.error(f"Webhook处理异常: {e}")
                return {"status": "error", "message": str(e)}
        else:
            return {"status": "error", "message": "Handler not found"}

    def create_alert_notification(self, alert_data: Dict[str, Any]) -> NotificationMessage:
        """创建告警通知"""
        level = NotificationLevel(alert_data.get("severity", "info"))
        title = f"测试告警: {alert_data.get('rule_name', 'Unknown Rule')}"
        message = alert_data.get("message", "")

        # 渲染HTML模板
        html_context = {
            "alert": alert_data,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        html_body = (
            self.notification_manager.template_engine.render_template(
                "alert.html" if Path("templates/alert.html").exists() else None,
                html_context,
            )
            or message
        )

        return NotificationMessage(
            id=alert_data.get("id", str(uuid.uuid4())),
            level=level,
            type=NotificationType.EMAIL,
            title=title,
            message=message,
            html_body=html_body,
            recipients=alert_data.get("recipients", []),
            channels=alert_data.get("channels", ["email"]),
            metadata=alert_data,
        )

    async def send_alert_notification(self, alert_data: Dict[str, Any]) -> bool:
        """发送告警通知"""
        message = self.create_alert_notification(alert_data)
        return await self.notification_manager.send_notification(message)

    def create_test_summary_notification(self, summary_data: Dict[str, Any]) -> NotificationMessage:
        """创建测试摘要通知"""
        title = f"测试执行摘要 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        message = f"测试执行完成，共执行 {summary_data.get('total_tests', 0)} 个测试"

        # 渲染报告HTML
        html_context = {
            "summary": summary_data,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        html_body = (
            self.notification_manager.template_engine.render_template(
                "summary.html" if Path("templates/summary.html").exists() else None,
                html_context,
            )
            or message
        )

        return NotificationMessage(
            id=str(uuid.uuid4()),
            level=NotificationLevel.INFO,
            type=NotificationType.EMAIL,
            title=title,
            message=message,
            html_body=html_body,
            recipients=summary_data.get("recipients", []),
            channels=summary_data.get("channels", ["email"]),
            metadata=summary_data,
        )

    async def send_test_summary(self, summary_data: Dict[str, Any]) -> bool:
        """发送测试摘要"""
        message = self.create_test_summary_notification(summary_data)
        return await self.notification_manager.send_notification(message)

    def sync_with_external_systems(self):
        """同步外部系统"""
        if not self.status_sync_enabled:
            return

        for integration_id, integration in self.integrations.items():
            if not integration.enabled:
                continue

            try:
                # 构建同步数据
                sync_data = {
                    "timestamp": datetime.now().isoformat(),
                    "system": "mystocks_test_monitoring",
                    "integrations": [integration_id],
                    "alerts": self._get_pending_alerts(),
                    "metrics": self._get_latest_metrics(),
                }

                # 发送同步请求
                self._sync_to_system(integration, sync_data)

            except Exception as e:
                logging.error(f"系统同步失败 {integration_id}: {e}")

    def _sync_to_system(self, integration: IntegrationConfig, data: Dict[str, Any]):
        """同步到特定系统"""
        try:
            response = requests.request(
                method=integration.method,
                url=integration.endpoint,
                json=data,
                headers=integration.headers,
                timeout=integration.timeout,
            )

            if response.status_code == 200:
                integration.last_sync = datetime.now()
                logging.info(f"系统同步成功: {integration.name}")
            else:
                logging.error(f"系统同步失败: {response.status_code}")

        except Exception as e:
            logging.error(f"系统同步异常: {e}")

    def _get_pending_alerts(self) -> List[Dict[str, Any]]:
        """获取待处理告警"""
        # 这里应该从告警系统获取
        return []

    def _get_latest_metrics(self) -> Dict[str, Any]:
        """获取最新指标"""
        # 这里应该从指标系统获取
        return {}

    def start(self):
        """启动集成管理器"""
        self.initialize_channels()
        self.initialize_templates()
        self.notification_manager.start()
        self.status_sync_enabled = True
        logging.info("测试集成管理器已启动")

    def stop(self):
        """停止集成管理器"""
        self.notification_manager.stop()
        self.status_sync_enabled = False
        logging.info("测试集成管理器已停止")

    def get_notification_status(self) -> Dict[str, Any]:
        """获取通知状态"""
        return {
            "channels": [
                {
                    "name": name,
                    "type": type(channel).__name__,
                    "enabled": channel.enabled,
                    "valid": channel.validate_config(),
                }
                for name, channel in self.notification_manager.channels.items()
            ],
            "templates": [
                {"id": t.id, "name": t.name, "type": t.type.value, "enabled": t.enabled}
                for t in self.notification_manager.templates.values()
            ],
        }

    def export_notification_logs(self, output_path: str, days: int = 7):
        """导出通知日志"""
        # 这里应该从日志系统获取通知相关日志
        from datetime import datetime, timedelta

        logs = []
        start_time = datetime.now() - timedelta(days=days)

        # 模拟日志数据
        for i in range(100):
            log_entry = {
                "timestamp": (start_time + timedelta(minutes=i * 10)).isoformat(),
                "level": "INFO",
                "message": f"通知发送示例 {i + 1}",
                "channel": "email",
                "status": "sent",
            }
            logs.append(log_entry)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)

        logging.info(f"通知日志已导出: {output_path}")


# 使用示例
def demo_integration_notifications():
    """演示集成通知功能"""
    print("🚀 演示测试集成通知系统")

    # 创建集成管理器
    manager = TestIntegrationManager()

    # 启动管理器
    manager.start()

    # 模拟告警数据
    alert_data = {
        "id": "alert_001",
        "severity": "high",
        "rule_name": "测试失败率告警",
        "message": "测试失败率超过10%",
        "recipients": ["admin@example.com"],
        "channels": ["email"],
        "timestamp": datetime.now().isoformat(),
    }

    # 发送告警通知
    async def send_alert():
        success = await manager.send_alert_notification(alert_data)
        print(f"告警通知发送结果: {'成功' if success else '失败'}")

    # 模拟摘要数据
    summary_data = {
        "total_tests": 100,
        "passed": 85,
        "failed": 15,
        "success_rate": 0.85,
        "recipients": ["team@example.com"],
        "channels": ["email"],
    }

    # 发送测试摘要
    async def send_summary():
        success = await manager.send_test_summary(summary_data)
        print(f"测试摘要发送结果: {'成功' if success else '失败'}")

    # 运行示例
    import asyncio

    asyncio.run(send_alert())
    asyncio.run(send_summary())

    # 导出通知日志
    manager.export_notification_logs("notification_logs.json")

    # 获取状态
    status = manager.get_notification_status()
    print(f"\n📊 通知状态: {status}")

    # 停止管理器
    manager.stop()


if __name__ == "__main__":
    demo_integration_notifications()
