"""
通知管理 API 数据模型
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field, constr, validator


class SendEmailRequest(BaseModel):
    """发送邮件请求 - Phase 4C Enhanced"""

    to_addresses: List[EmailStr] = Field(..., min_items=1, max_items=100, description="收件人列表，最多100个邮箱地址")
    subject: constr(min_length=1, max_length=200, strip_whitespace=True) = Field(..., description="邮件主题，1-200字符")
    content: constr(min_length=1, max_length=100000, strip_whitespace=True) = Field(
        ..., description="邮件内容，1-100000字符"
    )
    content_type: str = Field("plain", pattern="^(plain|html)$", description="内容类型: plain 或 html")
    priority: str = Field("normal", pattern="^(low|normal|high|urgent)$", description="邮件优先级")
    scheduled_at: Optional[datetime] = Field(None, description="定时发送时间（UTC），为空则立即发送")

    @validator("to_addresses")
    def validate_recipients(cls, value):
        """验证收件人列表"""
        if not value:
            raise ValueError("收件人列表不能为空")

        if len(value) != len(set(value)):
            raise ValueError("收件人列表包含重复邮箱地址")

        return value

    @validator("scheduled_at")
    def validate_schedule_time(cls, value):
        """验证定时发送时间"""
        if value and value <= datetime.now(timezone.utc):
            raise ValueError("定时发送时间必须晚于当前时间")
        return value


class SendWelcomeEmailRequest(BaseModel):
    """发送欢迎邮件请求 - Phase 4C Enhanced"""

    user_email: EmailStr = Field(..., description="用户邮箱")
    user_name: constr(min_length=1, max_length=100, strip_whitespace=True) = Field(
        ..., description="用户姓名，1-100字符"
    )
    welcome_offer: Optional[str] = Field(None, max_length=500, description="欢迎优惠信息，最多500字符")
    language: str = Field("zh-CN", pattern="^(zh-CN|en-US)$", description="邮件语言")


class SendNewsletterRequest(BaseModel):
    """发送新闻简报请求 - Phase 4C Enhanced"""

    user_email: EmailStr = Field(..., description="用户邮箱")
    user_name: constr(min_length=1, max_length=100, strip_whitespace=True) = Field(..., description="用户姓名")
    watchlist_symbols: List[constr(min_length=1, max_length=20, strip_whitespace=True)] = Field(
        ..., min_items=1, max_items=50, description="自选股列表，1-50个股票代码"
    )
    news_data: List[Dict] = Field(..., min_items=1, max_items=100, description="新闻数据，1-100条新闻")
    newsletter_type: str = Field("daily", pattern="^(daily|weekly|monthly)$", description="简报类型")

    @validator("watchlist_symbols")
    def validate_symbols(cls, value):
        """验证股票代码列表"""
        if not value:
            raise ValueError("自选股列表不能为空")
        return list(set(value))


class SendPriceAlertRequest(BaseModel):
    """发送价格提醒请求 - Phase 4C Enhanced"""

    user_email: EmailStr = Field(..., description="用户邮箱")
    user_name: constr(min_length=1, max_length=100, strip_whitespace=True) = Field(..., description="用户姓名")
    symbol: constr(min_length=1, max_length=20, strip_whitespace=True, pattern=r"^[A-Za-z0-9\.]+$") = Field(
        ..., description="股票代码"
    )
    stock_name: constr(min_length=1, max_length=100, strip_whitespace=True) = Field(..., description="股票名称")
    current_price: float = Field(..., gt=0, description="当前价格，必须大于0")
    alert_condition: str = Field(..., pattern="^(高于|低于|突破|跌破)$", description="提醒条件")
    alert_price: float = Field(..., gt=0, description="提醒价格，必须大于0")
    percentage_change: Optional[float] = Field(None, ge=-100, le=1000, description="价格变化百分比，-100%到1000%")


class NotificationPreferences(BaseModel):
    """用户通知偏好设置"""

    email_enabled: bool = Field(True, description="是否启用邮件通知")
    websocket_enabled: bool = Field(True, description="是否启用WebSocket通知")
    price_alerts: bool = Field(True, description="是否接收价格提醒")
    news_alerts: bool = Field(True, description="是否接收新闻提醒")
    system_alerts: bool = Field(True, description="是否接收系统提醒")
    quiet_hours: Optional[Dict[str, str]] = Field(None, description="免打扰时间段 {'start': '22:00', 'end': '08:00'}")
    max_daily_emails: int = Field(50, ge=1, le=200, description="每日最大邮件数量")


class RealTimeNotification(BaseModel):
    """实时通知消息"""

    notification_id: str = Field(..., description="通知唯一ID")
    user_id: int = Field(..., description="用户ID")
    type: str = Field(..., pattern="^(price_alert|news|system|reminder)$", description="通知类型")
    title: constr(min_length=1, max_length=200) = Field(..., description="通知标题")
    message: constr(min_length=1, max_length=1000) = Field(..., description="通知内容")
    data: Optional[Dict] = Field(None, description="通知相关数据")
    priority: str = Field("normal", pattern="^(low|normal|high|urgent)$", description="优先级")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    expires_at: Optional[datetime] = Field(None, description="过期时间")
    action_required: bool = Field(False, description="是否需要用户操作")
    action_url: Optional[str] = Field(None, description="操作链接")
