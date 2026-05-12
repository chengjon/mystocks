"""Compatibility auth routes extracted from `auth.py`."""

from __future__ import annotations

from datetime import timedelta

from fastapi import APIRouter, Form

from app.core.config import settings
from app.core.exceptions import UnauthorizedException
from app.core.responses import UnifiedResponse, create_unified_success_response
from app.core.security import authenticate_user, create_access_token
from app.openapi_config import COMMON_RESPONSES

compat_router = APIRouter()

AUTH_COMPAT_LOGIN_RESPONSES = {
    200: {
        "description": "兼容登录成功并返回访问令牌",
        "content": {
            "application/json": {
                "example": {
                    "success": True,
                    "data": {
                        "token": "eyJhbGciOiJIUzI1NiIs...",
                        "token_type": "bearer",
                        "expires_in": 7200,
                        "user": {"id": 1, "username": "trader_admin", "email": "admin@example.com", "role": "admin"},
                    },
                    "message": "登录成功",
                    "request_id": "req-auth-compat-login-001",
                }
            }
        },
    },
    401: COMMON_RESPONSES[401],
    422: COMMON_RESPONSES[422],
    500: COMMON_RESPONSES[500],
}


@compat_router.post(
    "/login",
    response_model=UnifiedResponse[dict],
    summary="兼容登录",
    description="兼容前端历史 `/api/auth/login` 表单登录请求，返回与主登录接口一致的统一令牌响应。",
    responses=AUTH_COMPAT_LOGIN_RESPONSES,
    openapi_extra={
        "requestBody": {
            "required": True,
            "content": {
                "application/x-www-form-urlencoded": {
                    "schema": {"$ref": "#/components/schemas/Body_compat_login_api_auth_login_post"},
                    "example": {
                        "username": "trader_admin",
                        "password": "SecurePass123",
                    },
                }
            },
        }
    },
)
async def compat_login(
    username: str = Form(..., description="用户名"),
    password: str = Form(..., description="密码"),
):
    """兼容登录端点 - 支持前端 `/api/auth/login` 请求。"""
    user = authenticate_user(username, password)
    if not user:
        raise UnauthorizedException(detail="用户名或密码错误")

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id, "role": user.role},
        expires_delta=access_token_expires,
    )

    return create_unified_success_response(
        data={
            "token": access_token,
            "token_type": "bearer",
            "expires_in": settings.access_token_expire_minutes * 60,
            "user": {"id": user.id, "username": user.username, "email": user.email, "role": user.role},
        },
        message="登录成功",
    )
