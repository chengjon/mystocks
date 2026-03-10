"""
邮件通知服务模块
实现基于 SMTP 的邮件发送功能
迁移自 OpenStock 项目
"""

import logging
import os
import smtplib
from datetime import datetime
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, List

logger = logging.getLogger(__name__)


class EmailServiceError(Exception):
    """邮件服务错误"""


class EmailNotificationService:
    """邮件通知服务"""

    @staticmethod
    def _log_exception(action: str, error: Exception) -> None:
        logger.exception("%s: %s", action, error)

    @staticmethod
    def _log_warning(message: str, *args) -> None:
        logger.warning(message, *args)

    @staticmethod
    def _log_info(message: str, *args) -> None:
        logger.info(message, *args)

    def __init__(self, config: Dict[str, any] = None):
        """
        初始化邮件服务

        Args:
            config: 邮件服务配置，如果未提供则从环境变量读取
        """
        if config:
            self.smtp_host = config.get("smtp_host")
            self.smtp_port = config.get("smtp_port")
            self.username = config.get("username")
            self.password = config.get("password")
            self.use_tls = config.get("use_tls", True)
            self.from_name = config.get("from_name", "MyStocks")
        else:
            # 从环境变量读取配置
            self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
            self.smtp_port = int(os.getenv("SMTP_PORT", 587))
            self.username = os.getenv("SMTP_USERNAME", "")
            self.password = os.getenv("SMTP_PASSWORD", "")
            self.use_tls = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
            self.from_name = os.getenv("SMTP_FROM_NAME", "MyStocks")

        if not self.username or not self.password:
            self._log_warning("警告: SMTP 配置未完整，邮件发送功能将不可用")

    def send_email(
        self,
        to_addresses: List[str],
        subject: str,
        content: str,
        content_type: str = "html",
        from_name: str = None,
    ) -> bool:
        """
        发送邮件

        Args:
            to_addresses: 收件人地址列表
            subject: 邮件主题
            content: 邮件内容
            content_type: 内容类型 ("plain" 或 "html")
            from_name: 发件人名称（可选，覆盖默认值）

        Returns:
            bool: 发送是否成功
        """
        if not self.username or not self.password:
            self._log_warning("邮件发送失败: SMTP 配置未完整")
            return False

        try:
            # 创建邮件对象
            msg = MIMEMultipart()
            sender_name = from_name or self.from_name
            msg["From"] = f"{sender_name} <{self.username}>"
            msg["To"] = ", ".join(to_addresses)
            msg["Subject"] = Header(subject, "utf-8")

            # 添加邮件内容
            content_mime = MIMEText(content, content_type, "utf-8")
            msg.attach(content_mime)

            # 连接SMTP服务器并发送邮件
            server = smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=30)
            if self.use_tls:
                server.starttls()

            server.login(self.username, self.password)
            server.send_message(msg)
            server.quit()

            self._log_info("邮件已成功发送到: %s", ", ".join(to_addresses))
            return True
        except smtplib.SMTPException as e:
            self._log_exception("发送邮件时发生 SMTP 错误", e)
            return False
        except Exception as e:
            self._log_exception("发送邮件时发生错误", e)
            return False

    def send_welcome_email(self, user_email: str, user_name: str) -> bool:
        """
        发送欢迎邮件

        Args:
            user_email: 用户邮箱
            user_name: 用户姓名

        Returns:
            bool: 发送是否成功
        """
        subject = "欢迎使用 MyStocks 量化交易平台"
        content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #2563eb; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9fafb; }}
                .footer {{ padding: 20px; text-align: center; color: #6b7280; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>欢迎加入 MyStocks！</h1>
                </div>
                <div class="content">
                    <h2>你好，{user_name}！</h2>
                    <p>感谢您注册 MyStocks 量化交易数据管理平台。</p>
                    <p>我们为您提供以下功能：</p>
                    <ul>
                        <li>实时股价跟踪和市场数据</li>
                        <li>个性化自选股管理</li>
                        <li>技术指标分析和回测</li>
                        <li>量化策略开发和执行</li>
                        <li>详细的市场新闻和公司信息</li>
                    </ul>
                    <p>祝您投资顺利，收益满满！</p>
                </div>
                <div class="footer">
                    <p>MyStocks 量化交易平台 &copy; 2025</p>
                    <p>本邮件由系统自动发送，请勿直接回复</p>
                </div>
            </div>
        </body>
        </html>
        """

        return self.send_email([user_email], subject, content, "html")

    def send_daily_newsletter(
        self,
        user_email: str,
        user_name: str,
        watchlist_symbols: List[str],
        news_data: List[Dict],
    ) -> bool:
        """
        发送每日新闻简报

        Args:
            user_email: 用户邮箱
            user_name: 用户姓名
            watchlist_symbols: 用户自选股列表
            news_data: 新闻数据列表

        Returns:
            bool: 发送是否成功
        """
        subject = f"{datetime.now().strftime('%Y-%m-%d')} MyStocks 每日新闻简报"

        # 构建新闻内容
        news_content = ""
        for news in news_data[:10]:  # 限制最多10条新闻
            news_time = datetime.fromtimestamp(news.get("datetime", 0)).strftime("%Y-%m-%d %H:%M")
            news_content += f"""
            <div style="margin-bottom: 20px; padding: 15px; background-color: white; border-left: 4px solid #2563eb;">
                <h3 style="margin: 0 0 10px 0;">
                    <a href="{news.get("url", "#")}" style="color: #1f2937; text-decoration: none;">
                        {news.get("headline", "无标题")}
                    </a>
                </h3>
                <p style="margin: 0 0 10px 0; color: #4b5563;">{news.get("summary", "无摘要")}</p>
                <p style="margin: 0; color: #9ca3af; font-size: 12px;">
                    来源: {news.get("source", "未知")} | 时间: {news_time}
                </p>
            </div>
            """

        if not news_content:
            news_content = "<p>今日暂无相关新闻</p>"

        content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #2563eb; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9fafb; }}
                .watchlist {{ background-color: white; padding: 15px; margin-bottom: 20px; border-radius: 5px; }}
                .footer {{ padding: 20px; text-align: center; color: #6b7280; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📈 每日新闻简报</h1>
                </div>
                <div class="content">
                    <h2>你好，{user_name}！</h2>
                    <p>这是您的每日市场新闻简报。</p>

                    <div class="watchlist">
                        <h3>您的自选股：</h3>
                        <p style="color: #2563eb; font-weight: bold;">
                            {", ".join(watchlist_symbols) if watchlist_symbols else "暂无自选股"}
                        </p>
                    </div>

                    <h3>📰 最新新闻</h3>
                    {news_content}

                    <p style="margin-top: 30px;">
                        <a href="https://mystocks.com/dashboard"
                           style="background-color: #2563eb; color: white;
                                  padding: 10px 20px; text-decoration: none;
                                  border-radius: 5px;">
                            访问控制台
                        </a>
                    </p>
                </div>
                <div class="footer">
                    <p>MyStocks 量化交易平台 &copy; 2025</p>
                    <p>本邮件由系统自动发送，如需取消订阅请登录平台设置</p>
                </div>
            </div>
        </body>
        </html>
        """

        return self.send_email([user_email], subject, content, "html")

    def send_alert_email(self, user_email: str, alert_type: str, alert_message: str) -> bool:
        """
        发送告警邮件

        Args:
            user_email: 用户邮箱
            alert_type: 告警类型 (price_alert, news_alert, system_alert 等)
            alert_message: 告警消息

        Returns:
            bool: 发送是否成功
        """
        alert_types = {
            "price_alert": "价格提醒",
            "news_alert": "新闻提醒",
            "system_alert": "系统通知",
            "performance_alert": "性能告警",
        }

        subject = f"MyStocks 告警: {alert_types.get(alert_type, '通知')}"

        content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #dc2626; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #fef2f2; }}
                .alert-box {{ background-color: white; padding: 15px; border-left: 4px solid #dc2626; margin: 20px 0; }}
                .footer {{ padding: 20px; text-align: center; color: #6b7280; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>⚠️ 告警通知</h1>
                </div>
                <div class="content">
                    <h2>{alert_types.get(alert_type, "系统通知")}</h2>
                    <div class="alert-box">
                        <p>{alert_message}</p>
                    </div>
                    <p><strong>时间:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                </div>
                <div class="footer">
                    <p>MyStocks 量化交易平台 &copy; 2025</p>
                </div>
            </div>
        </body>
        </html>
        """

        return self.send_email([user_email], subject, content, "html")


# 创建全局实例
_email_service = None


def get_email_service() -> EmailNotificationService:
    """
    获取邮件服务实例（单例模式）

    Returns:
        EmailNotificationService: 邮件服务实例
    """
    global _email_service
    if _email_service is None:
        _email_service = EmailNotificationService()
    return _email_service
