"""Compatibility auth routes extracted from `auth.py`."""

from __future__ import annotations

from datetime import timedelta

from fastapi import APIRouter, Form

from app.core.config import settings
from app.core.exceptions import UnauthorizedException
from app.core.responses import create_success_response
from app.core.security import authenticate_user, create_access_token


compat_router = APIRouter()


@compat_router.post("/login")
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

    return create_success_response(
        data={
            "token": access_token,
            "token_type": "bearer",
            "expires_in": settings.access_token_expire_minutes * 60,
            "user": {"username": user.username, "email": user.email, "role": user.role},
        },
        message="登录成功",
    )
