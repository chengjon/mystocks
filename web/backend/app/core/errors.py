"""
错误处理模块 - Week 3 简化版
提供用户友好的错误信息，隐藏技术细节
"""

import structlog
from typing import Optional
from fastapi import HTTPException

logger = structlog.get_logger()


class UserFriendlyError(Exception):
    """
    用户友好错误类

    将技术错误转换为用户可理解的消息
    技术细节记录到日志，用户只看到友好提示

    属性:
        user_message: 显示给用户的友好消息
        technical_details: 记录到日志的技术细节
        status_code: HTTP状态码（可选）
    """

    def __init__(
        self, user_message: str, technical_details: str, status_code: int = 500
    ):
        """
        初始化用户友好错误

        参数:
            user_message: 显示给用户的消息（中文，简洁明了）
            technical_details: 技术错误详情（用于日志和调试）
            status_code: HTTP状态码，默认500
        """
        self.user_message = user_message
        self.technical_details = technical_details
        self.status_code = status_code
        super().__init__(user_message)

        # 记录技术细节到日志
        logger.error(
            "UserFriendlyError raised",
            user_message=user_message,
            technical_details=technical_details,
            status_code=status_code,
        )


class DatabaseError(UserFriendlyError):
    """数据库相关错误"""

    def __init__(self, technical_details: str):
        super().__init__(
            user_message="数据加载失败，请稍后重试",
            technical_details=technical_details,
            status_code=500,
        )


class AuthenticationError(UserFriendlyError):
    """认证相关错误"""

    def __init__(self, technical_details: str):
        super().__init__(
            user_message="登录已过期，请重新登录",
            technical_details=technical_details,
            status_code=401,
        )


class ValidationError(UserFriendlyError):
    """输入验证错误"""

    def __init__(self, technical_details: str, field_name: Optional[str] = None):
        user_msg = "输入数据有误，请检查后重试"
        if field_name:
            user_msg = f"「{field_name}」输入有误，请检查"

        super().__init__(
            user_message=user_msg, technical_details=technical_details, status_code=400
        )


class ResourceNotFoundError(UserFriendlyError):
    """资源未找到错误"""

    def __init__(self, technical_details: str, resource_type: Optional[str] = None):
        user_msg = "请求的数据不存在"
        if resource_type:
            user_msg = f"{resource_type}不存在"

        super().__init__(
            user_message=user_msg, technical_details=technical_details, status_code=404
        )


def to_http_exception(error: Exception) -> HTTPException:
    """
    将异常转换为FastAPI HTTPException

    参数:
        error: 任意异常对象

    返回:
        HTTPException: FastAPI可识别的HTTP异常
    """
    if isinstance(error, UserFriendlyError):
        return HTTPException(
            status_code=error.status_code,
            detail={"error": error.user_message, "type": error.__class__.__name__},
        )

    # 未知错误 - 返回通用消息
    logger.error("Unhandled exception", exception=str(error), exc_info=True)
    return HTTPException(
        status_code=500,
        detail={
            "error": "系统错误，我们已记录此问题，请稍后重试",
            "type": "InternalServerError",
        },
    )
