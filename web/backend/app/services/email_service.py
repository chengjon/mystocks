"""邮件发送服务模块
从 OpenStock 迁移，适配 FastAPI 架构
支持欢迎邮件、每日新闻简报等功能
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


class EmailService:
    """邮件发送服务"""

    def __init__(
        self,
        smtp_host: str = None,
        smtp_port: int = None,
        username: str = None,
        password: str = None,
        use_tls: bool = True,
    ):
        """初始化邮件服务

        Args:
            smtp_host: SMTP服务器地址（默认从环境变量读取）
            smtp_port: SMTP服务器端口（默认从环境变量读取）
            username: 邮箱用户名（默认从环境变量读取）
            password: 邮箱密码或应用密码（默认从环境变量读取）
            use_tls: 是否使用TLS加密

        """
        self.smtp_host = smtp_host or os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = smtp_port or int(os.getenv("SMTP_PORT", "587"))
        self.username = username or os.getenv("SMTP_USERNAME", "")
        self.password = password or os.getenv("SMTP_PASSWORD", "")
        self.use_tls = use_tls

        # 验证配置
        if not self.username or not self.password:
            logger.warning("邮件服务未配置：请设置 SMTP_USERNAME 和 SMTP_PASSWORD 环境变量")

    def is_configured(self) -> bool:
        """检查邮件服务是否已配置

        Returns:
            bool: 是否已配置

        """
        return bool(self.username and self.password)

    def send_email(
        self,
        to_addresses: List[str],
        subject: str,
        content: str,
        content_type: str = "plain",
        from_name: str = None,
    ) -> Dict[str, any]:
        """发送邮件

        Args:
            to_addresses: 收件人地址列表
            subject: 邮件主题
            content: 邮件内容
            content_type: 内容类型 ("plain" 或 "html")
            from_name: 发件人名称

        Returns:
            Dict: 发送结果 {"success": bool, "message": str}

        """
        if not self.is_configured():
            return {"success": False, "message": "邮件服务未配置，请设置 SMTP 环境变量"}

        try:
            # 创建邮件对象
            msg = MIMEMultipart()
            msg["From"] = f"{from_name} <{self.username}>" if from_name else self.username
            msg["To"] = ", ".join(to_addresses)
            msg["Subject"] = Header(subject, "utf-8")

            # 添加邮件内容
            content_mime = MIMEText(content, content_type, "utf-8")
            msg.attach(content_mime)

            # 连接SMTP服务器并发送邮件
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            if self.use_tls:
                server.starttls()

            server.login(self.username, self.password)
            server.send_message(msg)
            server.quit()

            return {
                "success": True,
                "message": f"邮件已发送至 {', '.join(to_addresses)}",
            }
        except Exception as e:
            error_msg = f"发送邮件失败: {e!s}"
            logger.exception(error_msg)
            return {"success": False, "message": error_msg}

    def send_welcome_email(self, user_email: str, user_name: str) -> Dict[str, any]:
        """发送欢迎邮件

        Args:
            user_email: 用户邮箱
            user_name: 用户姓名

        Returns:
            Dict: 发送结果

        """
        subject = "欢迎使用 MyStocks 量化交易平台"
        content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #409eff;">欢迎加入 MyStocks，{user_name}！</h2>
                <p>感谢您注册 MyStocks 量化交易平台。</p>
                <div style="background: #f5f7fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin-top: 0;">平台功能</h3>
                    <ul>
                        <li>📈 实时股价跟踪（A股 + H股）</li>
                        <li>⭐ 自选股分组管理</li>
                        <li>📰 股票新闻资讯</li>
                        <li>📊 专业K线图表分析</li>
                        <li>🔔 个性化提醒功能</li>
                    </ul>
                </div>
                <p>如有任何问题，请随时联系我们。</p>
                <p style="margin-top: 30px; color: #909399; font-size: 12px;">
                    此邮件由 MyStocks 系统自动发送，请勿直接回复。
                </p>
            </div>
        </body>
        </html>
        """

        return self.send_email(
            to_addresses=[user_email],
            subject=subject,
            content=content,
            content_type="html",
            from_name="MyStocks Team",
        )

    def send_daily_newsletter(
        self,
        user_email: str,
        user_name: str,
        watchlist_symbols: List[str],
        news_data: List[Dict],
    ) -> Dict[str, any]:
        """发送每日新闻简报

        Args:
            user_email: 用户邮箱
            user_name: 用户姓名
            watchlist_symbols: 用户自选股列表
            news_data: 新闻数据列表

        Returns:
            Dict: 发送结果

        """
        today = datetime.now().strftime("%Y年%m月%d日")
        subject = f"{today} MyStocks 每日新闻简报"

        # 构建新闻内容
        if news_data and len(news_data) > 0:
            news_content = ""
            for news in news_data[:10]:  # 最多10条新闻
                news_time = datetime.fromtimestamp(news.get("datetime", 0)).strftime("%Y-%m-%d %H:%M")
                news_content += f"""
                <div style="margin-bottom: 20px; padding-bottom: 15px; border-bottom: 1px solid #eee;">
                    <h3 style="margin: 0 0 10px 0;">
                        <a href="{news.get("url", "#")}" style="color: #409eff; text-decoration: none;">
                            {news.get("headline", "无标题")}
                        </a>
                    </h3>
                    <p style="margin: 5px 0; color: #666;">{news.get("summary", "暂无摘要")}</p>
                    <p style="margin: 5px 0; font-size: 12px; color: #999;">
                        来源: {news.get("source", "未知")} | 时间: {news_time}
                    </p>
                </div>
                """
        else:
            news_content = "<p style='color: #999;'>今日暂无新闻更新</p>"

        # 构建自选股列表
        watchlist_html = ", ".join(watchlist_symbols[:10]) if watchlist_symbols else "您还没有添加自选股"
        if len(watchlist_symbols) > 10:
            watchlist_html += f" 等 {len(watchlist_symbols)} 只"

        content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 700px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            padding: 20px; border-radius: 8px; color: white; margin-bottom: 20px;">
                    <h2 style="margin: 0;">您好，{user_name}！</h2>
                    <p style="margin: 10px 0 0 0; opacity: 0.9;">这是您的每日新闻简报</p>
                </div>

                <div style="background: #f5f7fa; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
                    <h3 style="margin-top: 0; color: #409eff;">📊 您关注的股票</h3>
                    <p style="margin: 0;">{watchlist_html}</p>
                </div>

                <h3 style="color: #409eff;">📰 今日新闻</h3>
                {news_content}

                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee;">
                    <p style="color: #909399; font-size: 12px; margin: 5px 0;">
                        此邮件由 MyStocks 系统自动发送，请勿直接回复。
                    </p>
                    <p style="color: #909399; font-size: 12px; margin: 5px 0;">
                        如不想接收此类邮件，请登录平台修改通知设置。
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

        return self.send_email(
            to_addresses=[user_email],
            subject=subject,
            content=content,
            content_type="html",
            from_name="MyStocks Daily",
        )

    def send_price_alert(
        self,
        user_email: str,
        user_name: str,
        symbol: str,
        stock_name: str,
        current_price: float,
        alert_condition: str,
        alert_price: float,
    ) -> Dict[str, any]:
        """发送价格提醒邮件

        Args:
            user_email: 用户邮箱
            user_name: 用户姓名
            symbol: 股票代码
            stock_name: 股票名称
            current_price: 当前价格
            alert_condition: 提醒条件 ("高于" 或 "低于")
            alert_price: 提醒价格

        Returns:
            Dict: 发送结果

        """
        subject = f"价格提醒：{stock_name}({symbol}) 已{alert_condition} {alert_price}"

        # 计算涨跌幅
        change_percent = ((current_price - alert_price) / alert_price) * 100
        change_color = "#f56c6c" if change_percent > 0 else "#67c23a"

        content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin-bottom: 20px;">
                    <h2 style="margin: 0 0 10px 0; color: #856404;">🔔 价格提醒</h2>
                    <p style="margin: 0;">您设置的价格提醒已触发</p>
                </div>

                <div style="background: #f5f7fa; padding: 20px; border-radius: 5px; margin-bottom: 20px;">
                    <h3 style="margin: 0 0 15px 0;">{stock_name} ({symbol})</h3>
                    <div style="font-size: 32px; font-weight: bold; color: {change_color}; margin: 10px 0;">
                        ¥ {current_price:.2f}
                    </div>
                    <p style="margin: 10px 0 0 0; color: #666;">
                        触发条件: {alert_condition} ¥{alert_price:.2f}
                    </p>
                    <p style="margin: 5px 0 0 0; color: {change_color};">
                        变化: {change_percent:+.2f}%
                    </p>
                </div>

                <p>尊敬的 {user_name}，请及时关注市场动态。</p>

                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee;">
                    <p style="color: #909399; font-size: 12px;">
                        提醒时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

        return self.send_email(
            to_addresses=[user_email],
            subject=subject,
            content=content,
            content_type="html",
            from_name="MyStocks Alert",
        )


# 全局邮件服务实例（单例模式）
_email_service = None


def get_email_service() -> EmailService:
    """获取邮件服务实例（单例）

    Returns:
        EmailService: 邮件服务实例

    """
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service
