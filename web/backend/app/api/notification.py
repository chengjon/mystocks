"""
通知管理 API
支持邮件发送、价格提醒等功能
"""

from typing import Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field

from app.api.auth import User, get_current_user
from app.services.email_service import get_email_service

router = APIRouter()


# ==================== 请求模型 ====================


class SendEmailRequest(BaseModel):
    """发送邮件请求"""

    to_addresses: List[EmailStr] = Field(..., description="收件人列表")
    subject: str = Field(..., description="邮件主题")
    content: str = Field(..., description="邮件内容")
    content_type: str = Field("plain", description="内容类型 (plain/html)")


class SendWelcomeEmailRequest(BaseModel):
    """发送欢迎邮件请求"""

    user_email: EmailStr = Field(..., description="用户邮箱")
    user_name: str = Field(..., description="用户姓名")


class SendNewsletterRequest(BaseModel):
    """发送新闻简报请求"""

    user_email: EmailStr = Field(..., description="用户邮箱")
    user_name: str = Field(..., description="用户姓名")
    watchlist_symbols: List[str] = Field(..., description="自选股列表")
    news_data: List[Dict] = Field(..., description="新闻数据")


class SendPriceAlertRequest(BaseModel):
    """发送价格提醒请求"""

    user_email: EmailStr = Field(..., description="用户邮箱")
    user_name: str = Field(..., description="用户姓名")
    symbol: str = Field(..., description="股票代码")
    stock_name: str = Field(..., description="股票名称")
    current_price: float = Field(..., description="当前价格")
    alert_condition: str = Field(..., description="提醒条件 (高于/低于)")
    alert_price: float = Field(..., description="提醒价格")


# ==================== API 端点 ====================


@router.get("/status")
async def get_email_service_status() -> Dict:
    """
    获取邮件服务状态
    """
    email_service = get_email_service()
    is_configured = email_service.is_configured()

    return {
        "configured": is_configured,
        "smtp_host": email_service.smtp_host if is_configured else "未配置",
        "smtp_port": email_service.smtp_port if is_configured else 0,
        "message": ("邮件服务已配置" if is_configured else "邮件服务未配置，请设置 SMTP 环境变量"),
    }


@router.post("/email/send")
async def send_email(
    request: SendEmailRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
) -> Dict:
    """
    发送邮件（需要管理员权限）
    """
    # 检查权限（仅管理员可发送）
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可以发送邮件")

    email_service = get_email_service()

    if not email_service.is_configured():
        raise HTTPException(status_code=503, detail="邮件服务未配置")

    # 在后台发送邮件
    def send_task():
        result = email_service.send_email(
            to_addresses=request.to_addresses,
            subject=request.subject,
            content=request.content,
            content_type=request.content_type,
        )
        if not result["success"]:
            print(f"❌ 邮件发送失败: {result['message']}")

    background_tasks.add_task(send_task)

    return {
        "success": True,
        "message": "邮件正在发送中",
        "recipients": request.to_addresses,
    }


@router.post("/email/welcome")
async def send_welcome_email(
    request: SendWelcomeEmailRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
) -> Dict:
    """
    发送欢迎邮件
    """
    email_service = get_email_service()

    if not email_service.is_configured():
        raise HTTPException(status_code=503, detail="邮件服务未配置")

    # 在后台发送欢迎邮件
    def send_task():
        result = email_service.send_welcome_email(user_email=request.user_email, user_name=request.user_name)
        if result["success"]:
            print(f"✅ 欢迎邮件已发送至 {request.user_email}")
        else:
            print(f"❌ 欢迎邮件发送失败: {result['message']}")

    background_tasks.add_task(send_task)

    return {
        "success": True,
        "message": "欢迎邮件正在发送中",
        "recipient": request.user_email,
    }


@router.post("/email/newsletter")
async def send_daily_newsletter(
    request: SendNewsletterRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
) -> Dict:
    """
    发送每日新闻简报
    """
    email_service = get_email_service()

    if not email_service.is_configured():
        raise HTTPException(status_code=503, detail="邮件服务未配置")

    # 在后台发送新闻简报
    def send_task():
        result = email_service.send_daily_newsletter(
            user_email=request.user_email,
            user_name=request.user_name,
            watchlist_symbols=request.watchlist_symbols,
            news_data=request.news_data,
        )
        if result["success"]:
            print(f"✅ 新闻简报已发送至 {request.user_email}")
        else:
            print(f"❌ 新闻简报发送失败: {result['message']}")

    background_tasks.add_task(send_task)

    return {
        "success": True,
        "message": "新闻简报正在发送中",
        "recipient": request.user_email,
        "symbols_count": len(request.watchlist_symbols),
    }


@router.post("/email/price-alert")
async def send_price_alert(
    request: SendPriceAlertRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
) -> Dict:
    """
    发送价格提醒邮件
    """
    email_service = get_email_service()

    if not email_service.is_configured():
        raise HTTPException(status_code=503, detail="邮件服务未配置")

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
            print(f"✅ 价格提醒已发送至 {request.user_email}")
        else:
            print(f"❌ 价格提醒发送失败: {result['message']}")

    background_tasks.add_task(send_task)

    return {
        "success": True,
        "message": "价格提醒正在发送中",
        "recipient": request.user_email,
        "symbol": request.symbol,
        "current_price": request.current_price,
    }


@router.post("/test-email")
async def send_test_email(current_user: User = Depends(get_current_user)) -> Dict:
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
    curl -X POST "http://localhost:8000/api/notification/test-email" \\
      -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
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
    email_service = get_email_service()

    if not email_service.is_configured():
        raise HTTPException(status_code=503, detail="邮件服务未配置")

    # 使用用户的 email 字段（如果有）
    user_email = getattr(current_user, "email", None)
    if not user_email:
        raise HTTPException(status_code=400, detail="用户未设置邮箱")

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
        raise HTTPException(status_code=500, detail=result["message"])
