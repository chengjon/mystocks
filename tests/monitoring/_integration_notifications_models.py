"""
集成通知模块的共享模型与基础组件。
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape


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
    category: str = "alert"
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
    status: str = "pending"
    retry_count: int = 0
    max_retries: int = 3
    retry_delay: int = 300


@dataclass
class IntegrationConfig:
    """集成配置"""

    id: str
    name: str
    type: str
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
        except Exception as error:
            logging.error(f"模板渲染失败: {error}")
            return str(context)

    def render_subject(self, subject_template: str, context: Dict[str, Any]) -> str:
        """渲染主题"""
        try:
            template = self.env.from_string(subject_template)
            return template.render(**context)
        except Exception as error:
            logging.error(f"主题渲染失败: {error}")
            return subject_template
