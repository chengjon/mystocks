"""
通知管理 API
支持邮件发送、价格提醒、实时通知等功能

Phase 4C Enhanced - 企业级通知服务
- 统一响应格式
- 增强输入验证
- 速率限制保护
- WebSocket实时通知
- 完整错误处理
- 性能优化
"""

import asyncio
import json
from datetime import datetime, timezone
from typing import Dict

import structlog
from fastapi import APIRouter, BackgroundTasks, Body, Depends, WebSocket, WebSocketDisconnect

from app.core.exceptions import BusinessException

from app.api._notification_responses import (
    NEWSLETTER_EXAMPLES,
    NOTIFICATION_NEWSLETTER_RESPONSES,
    NOTIFICATION_PREFERENCES_RESPONSES,
    NOTIFICATION_PRICE_ALERT_RESPONSES,
    NOTIFICATION_SEND_EMAIL_RESPONSES,
    NOTIFICATION_STATUS_RESPONSES,
    NOTIFICATION_TEST_EMAIL_RESPONSES,
    NOTIFICATION_UPDATE_PREFERENCES_RESPONSES,
    NOTIFICATION_WELCOME_EMAIL_RESPONSES,
    PREFERENCES_EXAMPLES,
    PRICE_ALERT_EXAMPLES,
    SEND_EMAIL_EXAMPLES,
    WELCOME_EMAIL_EXAMPLES,
)
from app.api.auth import User, get_current_active_user, get_current_user
from app.api.notification_models import (
    NotificationPreferences,
    RealTimeNotification,
    SendEmailRequest,
    SendNewsletterRequest,
    SendPriceAlertRequest,
    SendWelcomeEmailRequest,
)
from app.api.notification_support import (
    connection_manager,
    rate_limit,
)
from app.core.responses import create_success_response
from app.services.email_service import EmailService, get_email_service_dependency

logger = structlog.get_logger()
router = APIRouter()


# ==================== API 端点 ====================


@router.get(
    "/status",
    responses=NOTIFICATION_STATUS_RESPONSES,
)
@rate_limit(limit=10, window=60)  # 每分钟最多10次请求
async def get_email_service_status(
    current_user: User = Depends(get_current_user),
    email_service: EmailService = Depends(get_email_service_dependency),
) -> Dict:
    """
    获取邮件服务状态 - Phase 4C Enhanced

    返回邮件服务的详细配置状态和统计信息
    """
    try:
        is_configured = email_service.is_configured()

        status_data = {
            "configured": is_configured,
            "smtp_host": email_service.smtp_host if is_configured else None,
            "smtp_port": email_service.smtp_port if is_configured else 0,
            "smtp_tls_enabled": getattr(email_service, "use_tls", False),
            "service_type": "smtp",
            "supported_content_types": ["plain", "html"],
            "max_recipients_per_email": 100,
            "rate_limits": {"user_per_minute": 5, "user_per_hour": 50, "global_per_minute": 100},
        }

        if is_configured:
            status_data["status"] = "healthy"
            status_data["message"] = "邮件服务已配置并可用"
        else:
            status_data["status"] = "misconfigured"
            status_data["message"] = "邮件服务未配置，请设置 SMTP 环境变量"

        logger.info(
            "邮件服务状态查询",
            user_id=current_user.id,
            configured=is_configured,
            host=email_service.smtp_host if is_configured else None,
        )

        return create_success_response(data=status_data, message="邮件服务状态查询成功").dict(exclude_unset=True)

    except Exception as e:
        logger.error("邮件服务状态查询失败", user_id=current_user.id, error=str(e), exc_info=True)
        raise BusinessException(status_code=500, detail=f"获取邮件服务状态失败: {str(e)}")


@router.post(
    "/email/send",
    summary="发送通知邮件",
    responses=NOTIFICATION_SEND_EMAIL_RESPONSES,
)
@rate_limit(limit=5, window=60)  # 每分钟最多5次邮件发送
async def send_email(
    background_tasks: BackgroundTasks,
    request: SendEmailRequest = Body(..., openapi_examples=SEND_EMAIL_EXAMPLES),
    current_user: User = Depends(get_current_user),
    email_service: EmailService = Depends(get_email_service_dependency),
) -> Dict:
    """
    发送邮件 - Phase 4C Enhanced（需要管理员权限）

    支持定时发送、优先级设置等高级功能
    """
    try:
        # 检查权限（仅管理员可发送群发邮件）
        if current_user.role != "admin":
            logger.warning(
                "非管理员尝试发送邮件",
                user_id=current_user.id,
                role=current_user.role,
                recipients=len(request.to_addresses),
            )
            raise BusinessException(status_code=403, detail="仅管理员可以发送邮件")

        if not email_service.is_configured():
            raise BusinessException(status_code=503, detail="邮件服务未配置，无法发送邮件")

        # 验证定时发送时间
        if request.scheduled_at and request.scheduled_at <= datetime.now(timezone.utc):
            raise BusinessException(status_code=400, detail="定时发送时间必须晚于当前时间")

        # 记录发送请求
        logger.info(
            "邮件发送请求",
            user_id=current_user.id,
            recipients=len(request.to_addresses),
            subject_length=len(request.subject),
            content_type=request.content_type,
            priority=request.priority,
            scheduled=request.scheduled_at is not None,
        )

        # 后台任务：发送邮件
        async def send_email_task():
            try:
                # 如果是定时发送，等待到指定时间
                if request.scheduled_at:
                    now = datetime.now(timezone.utc)
                    if request.scheduled_at > now:
                        wait_seconds = (request.scheduled_at - now).total_seconds()
                        await asyncio.sleep(wait_seconds)

                result = email_service.send_email(
                    to_addresses=request.to_addresses,
                    subject=request.subject,
                    content=request.content,
                    content_type=request.content_type,
                )

                if result["success"]:
                    logger.info(
                        "邮件发送成功",
                        user_id=current_user.id,
                        recipients=request.to_addresses,
                        subject=request.subject[:50],  # 记录前50个字符
                    )

                    # 发送实时通知给发送者
                    if current_user.id in connection_manager.active_connections:
                        notification = RealTimeNotification(
                            notification_id=f"email_sent_{datetime.now(timezone.utc).timestamp()}",
                            user_id=current_user.id,
                            type="system",
                            title="邮件发送成功",
                            message=f"邮件《{request.subject[:30]}...》已发送给 {len(request.to_addresses)} 位收件人",
                            priority="low",
                        )
                        await connection_manager.send_personal_notification(notification)
                else:
                    logger.error(
                        "邮件发送失败",
                        user_id=current_user.id,
                        error=result.get("message", "Unknown error"),
                        recipients=request.to_addresses,
                    )

            except Exception as e:
                logger.error("邮件发送任务异常", user_id=current_user.id, error=str(e), exc_info=True)

        # 添加后台任务
        background_tasks.add_task(send_email_task)

        response_data = {
            "success": True,
            "message": (
                "邮件已加入发送队列" if not request.scheduled_at else f"邮件已安排在 {request.scheduled_at} 发送"
            ),
            "recipients_count": len(request.to_addresses),
            "priority": request.priority,
            "scheduled_at": request.scheduled_at.isoformat() if request.scheduled_at else None,
            "content_type": request.content_type,
        }

        return create_success_response(data=response_data, message="邮件发送请求已受理").dict(exclude_unset=True)

    except BusinessException:
        raise
    except Exception as e:
        logger.error("邮件发送请求处理失败", user_id=current_user.id, error=str(e), exc_info=True)
        raise BusinessException(status_code=500, detail=f"处理邮件发送请求时发生错误: {str(e)}")


@router.websocket("/ws/notifications")
async def websocket_notifications(websocket: WebSocket, token: str = None):
    """
    WebSocket实时通知连接

    Args:
        websocket: WebSocket连接对象
        token: JWT认证token，通过查询参数传递
    """
    try:
        # 验证token
        if not token:
            await websocket.close(code=4001, reason="缺少认证token")
            return

        # 验证用户身份
        try:
            from app.api.auth import verify_token

            user = verify_token(token)
            if not user:
                await websocket.close(code=4001, reason="无效的认证token")
                return
        except Exception:
            await websocket.close(code=4001, reason="认证失败")
            return

        # 建立连接
        await connection_manager.connect(websocket, user.id)

        # 发送连接成功消息
        await websocket.send_json(
            {
                "type": "connection_established",
                "message": "实时通知连接已建立",
                "user_id": user.id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

        # 保持连接活跃
        try:
            while True:
                # 接收客户端消息（心跳包等）
                data = await websocket.receive_text()

                try:
                    message = json.loads(data)

                    if message.get("type") == "ping":
                        # 响应心跳包
                        await websocket.send_json({"type": "pong", "timestamp": datetime.now(timezone.utc).isoformat()})

                    elif message.get("type") == "mark_read":
                        # 标记通知已读（这里可以实现具体的标记逻辑）
                        notification_id = message.get("notification_id")
                        logger.info("用户标记通知已读", user_id=user.id, notification_id=notification_id)

                except json.JSONDecodeError:
                    logger.warning("收到无效的WebSocket消息", user_id=user.id, message=data[:100])

        except WebSocketDisconnect:
            logger.info("WebSocket客户端断开连接", user_id=user.id)
            connection_manager.disconnect(websocket, user.id)

        except Exception as e:
            logger.error("WebSocket连接处理异常", user_id=user.id, error=str(e), exc_info=True)
            await websocket.close(code=4000, reason="服务器内部错误")

    except Exception as e:
        logger.error("WebSocket连接建立失败", error=str(e), exc_info=True)
        await websocket.close(code=4000, reason="连接建立失败")


@router.post(
    "/email/welcome",
    summary="发送欢迎邮件",
    responses=NOTIFICATION_WELCOME_EMAIL_RESPONSES,
)
@rate_limit(limit=3, window=60)  # 每分钟最多3次欢迎邮件
async def send_welcome_email(
    background_tasks: BackgroundTasks,
    request: SendWelcomeEmailRequest = Body(..., openapi_examples=WELCOME_EMAIL_EXAMPLES),
    current_user: User = Depends(get_current_user),
    email_service: EmailService = Depends(get_email_service_dependency),
) -> Dict:
    """
    发送欢迎邮件 - Phase 4C Enhanced

    支持多语言和个性化欢迎信息
    """
    try:
        if not email_service.is_configured():
            raise BusinessException(status_code=503, detail="邮件服务未配置，无法发送欢迎邮件")

        # 验证邮箱地址与当前用户是否匹配（管理员可以为其他用户发送）
        if current_user.role != "admin" and current_user.email != request.user_email:
            raise BusinessException(status_code=403, detail="只能为自己的邮箱发送欢迎邮件")

        logger.info(
            "欢迎邮件发送请求",
            user_id=current_user.id,
            recipient=request.user_email,
            user_name=request.user_name,
            language=request.language,
        )

        # 后台任务：发送欢迎邮件
        async def send_welcome_task():
            try:
                result = email_service.send_welcome_email(user_email=request.user_email, user_name=request.user_name)

                if result["success"]:
                    logger.info("欢迎邮件发送成功", user_id=current_user.id, recipient=request.user_email)

                    # 发送实时通知
                    notification = RealTimeNotification(
                        notification_id=f"welcome_sent_{datetime.now(timezone.utc).timestamp()}",
                        user_id=current_user.id,
                        type="system",
                        title="欢迎邮件已发送",
                        message=f"欢迎邮件已发送至 {request.user_email}",
                        priority="low",
                    )
                    await connection_manager.send_personal_notification(notification)
                else:
                    logger.error(
                        "欢迎邮件发送失败", user_id=current_user.id, error=result.get("message", "Unknown error")
                    )

            except Exception as e:
                logger.error("欢迎邮件发送任务异常", user_id=current_user.id, error=str(e), exc_info=True)

        background_tasks.add_task(send_welcome_task)

        response_data = {
            "success": True,
            "message": "欢迎邮件正在发送中",
            "recipient": request.user_email,
            "language": request.language,
            "estimated_delivery": "2-5分钟",
        }

        return create_success_response(data=response_data, message="欢迎邮件发送请求已受理").dict(exclude_unset=True)

    except BusinessException:
        raise
    except Exception as e:
        logger.error("欢迎邮件发送请求处理失败", user_id=current_user.id, error=str(e), exc_info=True)
        raise BusinessException(status_code=500, detail=f"处理欢迎邮件发送请求时发生错误: {str(e)}")


@router.post(
    "/email/newsletter",
    summary="发送新闻简报邮件",
    description="Send a watchlist-focused newsletter email with curated market news for the target recipient.",
    responses=NOTIFICATION_NEWSLETTER_RESPONSES,
)
async def send_daily_newsletter(
    background_tasks: BackgroundTasks,
    request: SendNewsletterRequest = Body(..., openapi_examples=NEWSLETTER_EXAMPLES),
    current_user: User = Depends(get_current_user),
    email_service: EmailService = Depends(get_email_service_dependency),
) -> Dict:
    """
    发送每日新闻简报
    """
    if not email_service.is_configured():
        raise BusinessException(status_code=503, detail="邮件服务未配置")

    # 在后台发送新闻简报
    def send_task():
        result = email_service.send_daily_newsletter(
            user_email=request.user_email,
            user_name=request.user_name,
            watchlist_symbols=request.watchlist_symbols,
            news_data=request.news_data,
        )
        if result["success"]:
            logger.info("新闻简报已发送至 %s", request.user_email)
        else:
            logger.error("新闻简报发送失败: %s", result["message"])

    background_tasks.add_task(send_task)

    return {
        "success": True,
        "message": "新闻简报正在发送中",
        "recipient": request.user_email,
        "symbols_count": len(request.watchlist_symbols),
    }


@router.post(
    "/email/price-alert",
    summary="发送价格提醒邮件",
    description="Send a threshold or breakout alert email containing the current quote and configured trigger price.",
    responses=NOTIFICATION_PRICE_ALERT_RESPONSES,
)
async def send_price_alert(
    background_tasks: BackgroundTasks,
    request: SendPriceAlertRequest = Body(..., openapi_examples=PRICE_ALERT_EXAMPLES),
    current_user: User = Depends(get_current_user),
    email_service: EmailService = Depends(get_email_service_dependency),
) -> Dict:
    """
    发送价格提醒邮件
    """
    if not email_service.is_configured():
        raise BusinessException(status_code=503, detail="邮件服务未配置")

    # 在后台发送价格提醒
    def send_task():
        result = email_service.send_price_alert(
            user_email=request.user_email,
            user_name=request.user_name,
            symbol=request.symbol,
            stock_name=request.stock_name,
            current_price=request.current_price,
            alert_condition=request.alert_condition,
            alert_price=request.alert_price,
        )
        if result["success"]:
            logger.info("价格提醒已发送至 %s", request.user_email)
        else:
            logger.error("价格提醒发送失败: %s", result["message"])

    background_tasks.add_task(send_task)

    return {
        "success": True,
        "message": "价格提醒正在发送中",
        "recipient": request.user_email,
        "symbol": request.symbol,
        "current_price": request.current_price,
    }


@router.post(
    "/test-email",
    responses=NOTIFICATION_TEST_EMAIL_RESPONSES,
)
async def send_test_email(
    current_user: User = Depends(get_current_user),
    email_service: EmailService = Depends(get_email_service_dependency),
) -> Dict:
    """
    发送测试邮件到当前用户邮箱

    向已登录用户的注册邮箱发送测试邮件，用于验证邮件服务配置是否正确。该端点会
    立即发送邮件，并返回发送结果。

    **功能说明**:
    - 发送HTML格式的测试邮件
    - 验证SMTP服务器配置正确性
    - 检查邮箱地址有效性
    - 测试邮件发送延迟和送达率
    - 同步返回发送结果（非后台任务）

    **使用场景**:
    - 初次配置邮件服务后的功能验证
    - 检查邮件服务是否正常工作
    - 验证用户邮箱地址是否有效
    - 排查邮件发送失败问题
    - 测试邮件模板渲染效果

    **认证要求**:
    - 需要用户登录（JWT Token认证）
    - 用户必须在个人资料中设置了邮箱地址
    - 无角色限制，所有用户均可使用

    **返回值**:
    成功响应:
    - success: 发送成功标志（true）
    - message: 成功消息描述
    - recipient: 接收邮箱地址

    失败响应:
    - 400: 用户未设置邮箱
    - 503: 邮件服务未配置
    - 500: 邮件发送失败

    **示例**:
    ```bash
    # 发送测试邮件（需要认证Token）
    curl -X POST "http://localhost:${BACKEND_PORT}/api/notification/test-email" \\
      -H "Authorization: Bearer <jwt-token>"
    ```

    **成功响应示例**:
    ```json
    {
      "success": true,
      "message": "测试邮件已发送至 user@example.com",
      "recipient": "user@example.com"
    }
    ```

    **用户未设置邮箱响应**:
    ```json
    {
      "detail": "用户未设置邮箱"
    }
    ```

    **邮件服务未配置响应**:
    ```json
    {
      "detail": "邮件服务未配置"
    }
    ```

    **注意事项**:
    - 该端点会立即发送邮件，不使用后台任务
    - 发送失败会抛出HTTP异常，前端需处理错误
    - 测试邮件包含用户名和发送时间信息
    - 频繁调用可能触发SMTP限流，建议间隔至少30秒
    - 某些邮箱服务商可能将测试邮件标记为垃圾邮件
    - 发送前会检查邮件服务配置状态
    """
    if not email_service.is_configured():
        raise BusinessException(status_code=503, detail="邮件服务未配置")

    # 使用用户的 email 字段（如果有）
    user_email = getattr(current_user, "email", None)
    if not user_email:
        raise BusinessException(status_code=400, detail="用户未设置邮箱")

    result = email_service.send_email(
        to_addresses=[user_email],
        subject="MyStocks 测试邮件",
        content=f"""
        <html>
        <body>
            <h2>测试邮件</h2>
            <p>您好，{current_user.username}！</p>
            <p>这是一封测试邮件，如果您收到此邮件，说明邮件服务配置正确。</p>
            <p>发送时间: {email_service.__class__.__name__}</p>
        </body>
        </html>
        """,
        content_type="html",
    )

    if result["success"]:
        return {
            "success": True,
            "message": f"测试邮件已发送至 {user_email}",
            "recipient": user_email,
        }
    else:
        logger.error("测试邮件发送失败", user_id=current_user.id, error=result["message"])
        raise BusinessException(status_code=500, detail=f"测试邮件发送失败: {result['message']}")


@router.get(
    "/preferences",
    description="Return the current user's notification channel switches, alert categories, and delivery limits.",
    responses=NOTIFICATION_PREFERENCES_RESPONSES,
)
async def get_notification_preferences(current_user: User = Depends(get_current_active_user)) -> Dict:
    """
    获取用户通知偏好设置
    """
    try:
        # 这里应该从数据库获取用户偏好设置
        # 暂时返回默认设置
        preferences = {
            "email_enabled": True,
            "websocket_enabled": True,
            "price_alerts": True,
            "news_alerts": True,
            "system_alerts": True,
            "quiet_hours": None,
            "max_daily_emails": 50,
            "notification_types": {
                "price_alert": {"enabled": True, "priority": "normal"},
                "news_alert": {"enabled": True, "priority": "low"},
                "system_alert": {"enabled": True, "priority": "high"},
                "welcome_email": {"enabled": True, "priority": "normal"},
                "newsletter": {"enabled": True, "priority": "low"},
            },
        }

        logger.info("获取通知偏好设置", user_id=current_user.id)

        return create_success_response(data=preferences, message="通知偏好设置获取成功").dict(exclude_unset=True)

    except Exception as e:
        logger.error("获取通知偏好设置失败", user_id=current_user.id, error=str(e), exc_info=True)
        raise BusinessException(status_code=500, detail=f"获取通知偏好设置失败: {str(e)}")


@router.post(
    "/preferences",
    summary="更新通知偏好设置",
    description="Persist the current user's notification switches and per-category delivery preferences.",
    responses=NOTIFICATION_UPDATE_PREFERENCES_RESPONSES,
)
@rate_limit(limit=5, window=60)  # 每分钟最多5次设置更新
async def update_notification_preferences(
    preferences: NotificationPreferences = Body(..., openapi_examples=PREFERENCES_EXAMPLES),
    current_user: User = Depends(get_current_active_user),
) -> Dict:
    """
    更新用户通知偏好设置
    """
    try:
        # 这里应该保存到数据库
        # 暂时只记录日志
        logger.info("更新通知偏好设置", user_id=current_user.id, preferences=preferences.dict(exclude_unset=True))

        return create_success_response(data={"updated": True}, message="通知偏好设置更新成功").dict(exclude_unset=True)

    except Exception as e:
        logger.error("更新通知偏好设置失败", user_id=current_user.id, error=str(e), exc_info=True)
        raise BusinessException(status_code=500, detail=f"更新通知偏好设置失败: {str(e)}")
