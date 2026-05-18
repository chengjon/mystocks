"""Notification route response examples and OpenAPI response specs."""

from typing import Dict


NOTIFICATION_INTERNAL_ERROR_RESPONSE = {
    500: {
        "description": "Notification service request failed while reading configuration or sending a message.",
        "content": {
            "application/json": {
                "example": {
                    "detail": "获取邮件服务状态失败: SMTP timeout",
                }
            }
        },
    }
}


def _success_response_spec(
    description: str,
    example: Dict,
    extra_responses: Dict[int, Dict] | None = None,
) -> Dict[int, Dict]:
    return {
        200: {
            "description": description,
            "content": {"application/json": {"example": example}},
        },
        **(extra_responses or {}),
        **NOTIFICATION_INTERNAL_ERROR_RESPONSE,
    }


NOTIFICATION_STATUS_RESPONSES = {
    **NOTIFICATION_INTERNAL_ERROR_RESPONSE,
    200: {
        "description": "邮件服务状态查询成功。",
        "content": {
            "application/json": {
                "example": {
                    "success": True,
                    "data": {
                        "configured": True,
                        "smtp_host": "smtp.example.com",
                        "smtp_port": 587,
                        "smtp_tls_enabled": True,
                        "service_type": "smtp",
                        "supported_content_types": ["plain", "html"],
                        "max_recipients_per_email": 100,
                        "rate_limits": {
                            "user_per_minute": 5,
                            "user_per_hour": 50,
                            "global_per_minute": 100,
                        },
                        "status": "healthy",
                        "message": "邮件服务已配置并可用",
                    },
                    "message": "邮件服务状态查询成功",
                    "timestamp": "2026-04-07T02:20:00Z",
                    "request_id": "req-notification-status-001",
                }
            }
        },
    },
}

NOTIFICATION_TEST_EMAIL_RESPONSES = {
    400: {
        "description": "当前用户未配置邮箱地址。",
        "content": {
            "application/json": {
                "example": {
                    "detail": "用户未设置邮箱",
                }
            }
        },
    },
    500: {
        "description": "Test email delivery failed because the mail provider rejected or timed out the request.",
        "content": {
            "application/json": {
                "example": {
                    "detail": "测试邮件发送失败: SMTP timeout",
                }
            }
        },
    },
    503: {
        "description": "邮件服务未配置，无法发送测试邮件。",
        "content": {
            "application/json": {
                "example": {
                    "detail": "邮件服务未配置",
                }
            }
        },
    },
    200: {
        "description": "测试邮件发送成功。",
        "content": {
            "application/json": {
                "example": {
                    "success": True,
                    "message": "测试邮件已发送至 trader@example.com",
                    "recipient": "trader@example.com",
                }
            }
        },
    },
}

NOTIFICATION_PREFERENCES_RESPONSES = {
    **NOTIFICATION_INTERNAL_ERROR_RESPONSE,
    200: {
        "description": "通知偏好设置查询成功。",
        "content": {
            "application/json": {
                "example": {
                    "success": True,
                    "data": {
                        "email_enabled": True,
                        "websocket_enabled": True,
                        "price_alerts": True,
                        "news_alerts": True,
                        "system_alerts": True,
                        "quiet_hours": {"start": "22:30", "end": "07:30"},
                        "max_daily_emails": 25,
                        "notification_types": {
                            "price_alert": {"enabled": True, "priority": "normal"},
                            "news_alert": {"enabled": True, "priority": "low"},
                            "system_alert": {"enabled": False, "priority": "high"},
                        },
                    },
                    "message": "通知偏好设置获取成功",
                    "timestamp": "2026-04-07T02:20:00Z",
                    "request_id": "req-notification-preferences-001",
                }
            }
        },
    },
}

NOTIFICATION_SEND_EMAIL_RESPONSES = _success_response_spec(
    "邮件发送请求已受理，后台任务将按优先级和预约时间调度发送。",
    {
        "success": True,
        "data": {
            "success": True,
            "message": "邮件已安排在 2026-04-08 09:30:00+00:00 发送",
            "recipients_count": 2,
            "priority": "high",
            "scheduled_at": "2026-04-08T09:30:00+00:00",
            "content_type": "html",
        },
        "message": "邮件发送请求已受理",
        "timestamp": "2026-04-07T02:20:00Z",
        "request_id": "req-notification-send-001",
    },
    extra_responses={
        400: {
            "description": "预约发送时间早于当前时间。",
            "content": {"application/json": {"example": {"detail": "定时发送时间必须晚于当前时间"}}},
        },
        403: {
            "description": "非管理员无权发起群发邮件任务。",
            "content": {"application/json": {"example": {"detail": "仅管理员可以发送邮件"}}},
        },
        503: {
            "description": "邮件服务未配置，无法创建发送任务。",
            "content": {"application/json": {"example": {"detail": "邮件服务未配置，无法发送邮件"}}},
        },
    },
)

NOTIFICATION_WELCOME_EMAIL_RESPONSES = _success_response_spec(
    "欢迎邮件发送任务已受理，后台会继续完成模板渲染和发送。",
    {
        "success": True,
        "data": {
            "success": True,
            "message": "欢迎邮件正在发送中",
            "recipient": "new.user@example.com",
            "language": "zh-CN",
            "estimated_delivery": "2-5分钟",
        },
        "message": "欢迎邮件发送请求已受理",
        "timestamp": "2026-04-07T02:20:00Z",
        "request_id": "req-notification-welcome-001",
    },
    extra_responses={
        403: {
            "description": "非管理员只能给自己的邮箱发送欢迎邮件。",
            "content": {"application/json": {"example": {"detail": "只能为自己的邮箱发送欢迎邮件"}}},
        },
        503: {
            "description": "邮件服务未配置，无法发送欢迎邮件。",
            "content": {"application/json": {"example": {"detail": "邮件服务未配置，无法发送欢迎邮件"}}},
        },
    },
)

NOTIFICATION_NEWSLETTER_RESPONSES = _success_response_spec(
    "新闻简报发送任务已创建，后台将按传入股票列表组装邮件内容。",
    {
        "success": True,
        "message": "新闻简报正在发送中",
        "recipient": "investor@example.com",
        "symbols_count": 2,
    },
    extra_responses={
        503: {
            "description": "邮件服务未配置，无法发送新闻简报。",
            "content": {"application/json": {"example": {"detail": "邮件服务未配置"}}},
        }
    },
)

NOTIFICATION_PRICE_ALERT_RESPONSES = _success_response_spec(
    "价格提醒邮件发送任务已创建，后台将使用当前行情和触发阈值生成通知。",
    {
        "success": True,
        "message": "价格提醒正在发送中",
        "recipient": "alert@example.com",
        "symbol": "600519.SH",
        "current_price": 1688.5,
    },
    extra_responses={
        503: {
            "description": "邮件服务未配置，无法发送价格提醒。",
            "content": {"application/json": {"example": {"detail": "邮件服务未配置"}}},
        }
    },
)

NOTIFICATION_UPDATE_PREFERENCES_RESPONSES = _success_response_spec(
    "通知偏好设置已保存，后续消息分发会使用新的渠道和限额配置。",
    {
        "success": True,
        "data": {"updated": True},
        "message": "通知偏好设置更新成功",
        "timestamp": "2026-04-07T02:20:00Z",
        "request_id": "req-notification-preferences-update-001",
    },
)

SEND_EMAIL_EXAMPLES = {
    "bulk_html_email": {
        "summary": "Bulk HTML email",
        "value": {
            "to_addresses": ["trader@example.com", "ops@example.com"],
            "subject": "MyStocks morning market briefing",
            "content": "<h2>Market Open</h2><p>Futures are trending higher before the bell.</p>",
            "content_type": "html",
            "priority": "high",
        },
    }
}

WELCOME_EMAIL_EXAMPLES = {
    "localized_welcome": {
        "summary": "Localized welcome email",
        "value": {
            "user_email": "new.user@example.com",
            "user_name": "New User",
            "welcome_offer": "限时 7 天高级功能试用",
            "language": "zh-CN",
        },
    }
}

NEWSLETTER_EXAMPLES = {
    "daily_watchlist_newsletter": {
        "summary": "Daily watchlist newsletter",
        "value": {
            "user_email": "investor@example.com",
            "user_name": "Investor",
            "watchlist_symbols": ["600519.SH", "000001.SZ"],
            "news_data": [
                {"title": "白酒板块早盘走强", "summary": "贵州茅台领涨消费板块", "source": "mock"},
                {"title": "银行股成交活跃", "summary": "资金回流高股息方向", "source": "mock"},
            ],
            "newsletter_type": "daily",
        },
    }
}

PRICE_ALERT_EXAMPLES = {
    "breakout_alert": {
        "summary": "Breakout price alert",
        "value": {
            "user_email": "alert@example.com",
            "user_name": "Alert User",
            "symbol": "600519.SH",
            "stock_name": "贵州茅台",
            "current_price": 1688.5,
            "alert_condition": "突破",
            "alert_price": 1700.0,
            "percentage_change": 2.5,
        },
    }
}

PREFERENCES_EXAMPLES = {
    "active_trader_preferences": {
        "summary": "Active trader notification preferences",
        "value": {
            "email_enabled": True,
            "websocket_enabled": True,
            "price_alerts": True,
            "news_alerts": True,
            "system_alerts": False,
            "quiet_hours": {"start": "22:30", "end": "07:30"},
            "max_daily_emails": 25,
        },
    }
}
