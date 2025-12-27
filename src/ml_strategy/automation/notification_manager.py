"""
通知管理器 (Notification Manager)

功能说明:
- 多渠道通知发送（邮件、Webhook、日志）
- 通知模板管理
- 通知历史记录
- 通知过滤和频率限制

支持的通知渠道:
- Email: SMTP邮件通知
- Webhook: HTTP POST到指定URL
- Log: 记录到日志文件
- Console: 控制台输出（开发调试）

作者: MyStocks量化交易团队
创建时间: 2025-10-18
版本: 1.0.0
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import logging

# Email支持（可选）
try:
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    EMAIL_AVAILABLE = True
except ImportError:
    EMAIL_AVAILABLE = False

# HTTP请求支持（可选）
try:
    import requests

    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class NotificationChannel(Enum):
    """通知渠道"""

    EMAIL = "email"
    WEBHOOK = "webhook"
    LOG = "log"
    CONSOLE = "console"


class NotificationLevel(Enum):
    """通知级别"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class NotificationConfig:
    """通知配置"""

    channels: List[NotificationChannel]  # 启用的渠道

    # Email配置
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    email_from: str = ""
    email_to: List[str] = field(default_factory=list)

    # Webhook配置
    webhook_url: str = ""
    webhook_headers: Dict[str, str] = field(default_factory=dict)

    # 频率限制（相同通知的最小间隔，秒）
    rate_limit: int = 300  # 5分钟

    # 启用HTML格式邮件
    html_email: bool = True


@dataclass
class Notification:
    """通知记录"""

    notification_id: str
    level: NotificationLevel
    title: str
    message: str
    channels: List[NotificationChannel]
    timestamp: datetime
    context: Dict[str, Any] = field(default_factory=dict)
    sent: bool = False
    error: Optional[str] = None


class NotificationManager:
    """
    通知管理器

    功能:
    - 多渠道通知发送
    - 通知模板
    - 频率限制
    - 发送历史
    """

    def __init__(self, config: Optional[NotificationConfig] = None):
        """
        初始化通知管理器

        参数:
            config: 通知配置
        """
        self.logger = logging.getLogger(f"{__name__}.NotificationManager")
        self.logger.setLevel(logging.INFO)

        self.config = config or NotificationConfig(channels=[NotificationChannel.LOG])

        # 通知历史
        self.notifications: List[Notification] = []

        # 频率限制追踪
        self._last_sent: Dict[str, datetime] = {}

        # 统计
        self.stats = {
            "total_sent": 0,
            "email_sent": 0,
            "webhook_sent": 0,
            "log_sent": 0,
            "console_sent": 0,
            "failed": 0,
            "rate_limited": 0,
        }

    def send_notification(
        self,
        title: str,
        message: str,
        level: NotificationLevel = NotificationLevel.INFO,
        context: Optional[Dict] = None,
        channels: Optional[List[NotificationChannel]] = None,
    ) -> bool:
        """
        发送通知

        参数:
            title: 通知标题
            message: 通知内容
            level: 通知级别
            context: 上下文数据
            channels: 发送渠道（可选，默认使用配置的渠道）

        返回:
            bool: 是否成功发送
        """
        # 使用配置的渠道或指定渠道
        if channels is None:
            channels = self.config.channels

        # 检查频率限制
        if self._is_rate_limited(title, message):
            self.logger.debug(f"通知被频率限制: {title}")
            self.stats["rate_limited"] += 1
            return False

        # 创建通知记录
        notification = Notification(
            notification_id=f"notif_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            level=level,
            title=title,
            message=message,
            channels=channels,
            timestamp=datetime.now(),
            context=context or {},
        )

        # 发送到各个渠道
        all_success = True
        for channel in channels:
            try:
                if channel == NotificationChannel.EMAIL:
                    self._send_email(notification)
                    self.stats["email_sent"] += 1

                elif channel == NotificationChannel.WEBHOOK:
                    self._send_webhook(notification)
                    self.stats["webhook_sent"] += 1

                elif channel == NotificationChannel.LOG:
                    self._send_log(notification)
                    self.stats["log_sent"] += 1

                elif channel == NotificationChannel.CONSOLE:
                    self._send_console(notification)
                    self.stats["console_sent"] += 1

            except Exception as e:
                all_success = False
                notification.error = str(e)
                self.stats["failed"] += 1
                self.logger.error(f"发送通知失败 ({channel.value}): {e}")

        notification.sent = all_success
        self.notifications.append(notification)

        if all_success:
            self.stats["total_sent"] += 1
            self._update_rate_limit(title, message)

        return all_success

    def send_success_notification(self, task_name: str, execution_time: float, result: Any = None):
        """发送任务成功通知"""
        title = f"✓ 任务成功: {task_name}"
        message = f"任务 '{task_name}' 执行成功\n执行时间: {execution_time:.2f} 秒"

        if result:
            message += f"\n结果: {result}"

        self.send_notification(
            title=title,
            message=message,
            level=NotificationLevel.INFO,
            context={"task_name": task_name, "execution_time": execution_time},
        )

    def send_failure_notification(self, task_name: str, error_message: str, retry_count: int = 0):
        """发送任务失败通知"""
        title = f"✗ 任务失败: {task_name}"
        message = f"任务 '{task_name}' 执行失败\n"
        message += f"错误信息: {error_message}\n"

        if retry_count > 0:
            message += f"重试次数: {retry_count}"

        self.send_notification(
            title=title,
            message=message,
            level=NotificationLevel.ERROR,
            context={
                "task_name": task_name,
                "error_message": error_message,
                "retry_count": retry_count,
            },
        )

    def send_signal_notification(
        self,
        strategy_name: str,
        symbol: str,
        signal: str,
        price: float,
        context: Optional[Dict] = None,
    ):
        """发送交易信号通知"""
        emoji = "🔔"
        if signal.lower() == "buy":
            emoji = "📈"
        elif signal.lower() == "sell":
            emoji = "📉"

        title = f"{emoji} 交易信号: {symbol} - {signal.upper()}"
        message = f"策略: {strategy_name}\n"
        message += f"标的: {symbol}\n"
        message += f"信号: {signal.upper()}\n"
        message += f"价格: {price:.2f}"

        if context:
            message += "\n\n附加信息:\n"
            for key, value in context.items():
                message += f"  {key}: {value}\n"

        self.send_notification(
            title=title,
            message=message,
            level=NotificationLevel.WARNING,
            context={
                "strategy_name": strategy_name,
                "symbol": symbol,
                "signal": signal,
                "price": price,
                **(context or {}),
            },
        )

    def _send_email(self, notification: Notification):
        """发送邮件通知"""
        if not EMAIL_AVAILABLE:
            raise ImportError("Email功能需要安装smtplib")

        if not self.config.email_to:
            self.logger.warning("未配置邮件接收者，跳过邮件发送")
            return

        # 创建邮件
        msg = MIMEMultipart("alternative")
        msg["Subject"] = notification.title
        msg["From"] = self.config.email_from
        msg["To"] = ", ".join(self.config.email_to)

        # 创建纯文本和HTML版本
        text_content = notification.message

        if self.config.html_email:
            html_content = self._format_html_email(notification)
            msg.attach(MIMEText(text_content, "plain"))
            msg.attach(MIMEText(html_content, "html"))
        else:
            msg.attach(MIMEText(text_content, "plain"))

        # 发送
        with smtplib.SMTP(self.config.smtp_host, self.config.smtp_port) as server:
            server.starttls()
            server.login(self.config.smtp_user, self.config.smtp_password)
            server.send_message(msg)

        self.logger.info(f"✓ 邮件已发送: {notification.title}")

    def _send_webhook(self, notification: Notification):
        """发送Webhook通知"""
        if not REQUESTS_AVAILABLE:
            raise ImportError("Webhook功能需要安装requests")

        if not self.config.webhook_url:
            self.logger.warning("未配置Webhook URL，跳过Webhook发送")
            return

        # 准备payload
        payload = {
            "title": notification.title,
            "message": notification.message,
            "level": notification.level.value,
            "timestamp": notification.timestamp.isoformat(),
            "context": notification.context,
        }

        # 发送POST请求
        response = requests.post(
            self.config.webhook_url,
            json=payload,
            headers=self.config.webhook_headers,
            timeout=10,
        )

        response.raise_for_status()
        self.logger.info(f"✓ Webhook已发送: {notification.title}")

    def _send_log(self, notification: Notification):
        """发送日志通知"""
        level_map = {
            NotificationLevel.INFO: logging.INFO,
            NotificationLevel.WARNING: logging.WARNING,
            NotificationLevel.ERROR: logging.ERROR,
            NotificationLevel.CRITICAL: logging.CRITICAL,
        }

        log_level = level_map.get(notification.level, logging.INFO)
        log_msg = f"[NOTIFICATION] {notification.title}: {notification.message}"

        self.logger.log(log_level, log_msg)

    def _send_console(self, notification: Notification):
        """发送控制台通知"""
        level_symbols = {
            NotificationLevel.INFO: "ℹ️",
            NotificationLevel.WARNING: "⚠️",
            NotificationLevel.ERROR: "❌",
            NotificationLevel.CRITICAL: "🔴",
        }

        symbol = level_symbols.get(notification.level, "•")
        print(f"\n{symbol} {notification.title}")
        print(f"  {notification.message}")
        print(f"  时间: {notification.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n")

    def _format_html_email(self, notification: Notification) -> str:
        """格式化HTML邮件"""
        level_colors = {
            NotificationLevel.INFO: "#2196F3",
            NotificationLevel.WARNING: "#FF9800",
            NotificationLevel.ERROR: "#F44336",
            NotificationLevel.CRITICAL: "#D32F2F",
        }

        color = level_colors.get(notification.level, "#000000")

        html = f"""
        <html>
          <head></head>
          <body style="font-family: Arial, sans-serif;">
            <div style="padding: 20px; background-color: #f5f5f5;">
              <div style="background-color: white; padding: 20px; border-radius: 5px;">
                <h2 style="color: {color}; margin-top: 0;">
                  {notification.title}
                </h2>
                <div style="line-height: 1.6;">
                  {notification.message.replace(chr(10), "<br>")}
                </div>
                <hr style="margin: 20px 0; border: none; border-top: 1px solid #e0e0e0;">
                <div style="font-size: 12px; color: #757575;">
                  <p>通知时间: {notification.timestamp.strftime("%Y-%m-%d %H:%M:%S")}</p>
                  <p>通知级别: {notification.level.value.upper()}</p>
                </div>
              </div>
            </div>
          </body>
        </html>
        """

        return html

    def _is_rate_limited(self, title: str, message: str) -> bool:
        """检查是否达到频率限制"""
        key = f"{title}:{message}"

        if key in self._last_sent:
            elapsed = (datetime.now() - self._last_sent[key]).total_seconds()
            if elapsed < self.config.rate_limit:
                return True

        return False

    def _update_rate_limit(self, title: str, message: str):
        """更新频率限制追踪"""
        key = f"{title}:{message}"
        self._last_sent[key] = datetime.now()

    def get_notification_history(
        self, level: Optional[NotificationLevel] = None, limit: int = 100
    ) -> List[Notification]:
        """
        获取通知历史

        参数:
            level: 通知级别过滤
            limit: 返回数量

        返回:
            List[Notification]: 通知列表
        """
        if level:
            history = [n for n in self.notifications if n.level == level]
        else:
            history = self.notifications

        return sorted(history, key=lambda x: x.timestamp, reverse=True)[:limit]

    def get_statistics(self) -> Dict:
        """获取统计信息"""
        return {
            **self.stats,
            "total_notifications": len(self.notifications),
            "success_rate": (self.stats["total_sent"] / max(len(self.notifications), 1)) * 100,
        }

    def clear_history(self, days: int = 30):
        """清除旧通知历史"""
        cutoff = datetime.now() - timedelta(days=days)
        self.notifications = [n for n in self.notifications if n.timestamp > cutoff]
        self.logger.info(f"已清除 {days} 天前的通知历史")


if __name__ == "__main__":
    # 测试代码
    print("通知管理器测试")
    print("=" * 70)

    # 设置日志
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    # 创建通知管理器（仅使用日志和控制台）
    config = NotificationConfig(channels=[NotificationChannel.LOG, NotificationChannel.CONSOLE])

    manager = NotificationManager(config)

    # 测试1: 基本通知
    print("\n测试1: 发送基本通知")
    manager.send_notification(title="测试通知", message="这是一条测试通知", level=NotificationLevel.INFO)

    # 测试2: 任务成功通知
    print("\n测试2: 任务成功通知")
    manager.send_success_notification(task_name="数据更新", execution_time=12.5, result="导入1000条记录")

    # 测试3: 任务失败通知
    print("\n测试3: 任务失败通知")
    manager.send_failure_notification(task_name="策略执行", error_message="数据库连接失败", retry_count=2)

    # 测试4: 交易信号通知
    print("\n测试4: 交易信号通知")
    manager.send_signal_notification(
        strategy_name="动量策略",
        symbol="sh600000",
        signal="buy",
        price=10.52,
        context={"ma_5": 10.45, "ma_20": 10.38, "rsi": 65},
    )

    # 测试5: 频率限制
    print("\n测试5: 频率限制测试")
    for i in range(3):
        success = manager.send_notification(title="重复通知", message="测试频率限制", level=NotificationLevel.INFO)
        print(f"  第{i + 1}次发送: {'成功' if success else '被限制'}")

    # 获取统计
    print("\n测试6: 通知统计")
    stats = manager.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    # 获取历史
    print("\n测试7: 通知历史")
    history = manager.get_notification_history(limit=5)
    for notification in history:
        print(f"  [{notification.level.value}] {notification.title} - {notification.timestamp}")

    print("\n" + "=" * 70)
    print("测试完成")
