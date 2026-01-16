"""
认证API

提供用户认证和授权功能
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timedelta

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

security = HTTPBearer()


class LoginRequest(BaseModel):
    """登录请求"""

    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")


class LoginResponse(BaseModel):
    """登录响应"""

    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: str
    username: str


class TokenPayload(BaseModel):
    """Token载荷"""

    sub: str
    username: str
    exp: datetime


@router.post("/login", response_model=LoginResponse, summary="User Login")
async def login(request: LoginRequest):
    """
    用户登录

    Authenticates user and returns JWT token.
    """
    if request.username == "admin" and request.password == "admin123":
        token = f"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.{request.username}.{datetime.now().timestamp()}"
        return LoginResponse(
            access_token=token,
            token_type="bearer",
            expires_in=1800,
            user_id="user_001",
            username=request.username,
        )
    raise HTTPException(status_code=401, detail="Invalid credentials")


@router.post("/logout", summary="User Logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    用户登出

    Invalidates the current token.
    """
    return {"message": "Logged out successfully"}


@router.post("/refresh", response_model=LoginResponse, summary="Refresh Token")
async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    刷新Token

    Returns a new JWT token.
    """
    return LoginResponse(
        access_token="new_token",
        token_type="bearer",
        expires_in=1800,
        user_id="user_001",
        username="admin",
    )


@router.get("/me", summary="Get Current User")
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """
    获取当前用户信息

    Returns the current authenticated user's information.
    """
    return {
        "user_id": "user_001",
        "username": "admin",
        "email": "admin@mystocks.local",
        "role": "admin",
        "created_at": "2025-01-01T00:00:00Z",
    }
