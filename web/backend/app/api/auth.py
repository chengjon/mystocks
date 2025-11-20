"""
认证相关 API
"""

from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials,
    OAuth2PasswordRequestForm,
)
from typing import Dict, Any
from datetime import timedelta

from app.core.security import (
    User,
    UserInDB,
    Token,
    TokenData,
    authenticate_user,
    create_access_token,
    verify_token,
    verify_password,
    get_password_hash,
)
from app.core.config import settings

router = APIRouter()
security = HTTPBearer()

# 模拟用户数据库 - 使用预先计算的密码哈希
# TODO: 替换为真实的数据库存储
USERS_DB = {
    "admin": {
        "id": 1,
        "username": "admin",
        "email": "admin@mystocks.com",
        "hashed_password": "$2b$12$JzXL46bSlDVnMJlDvkV7q.u5gY6pVEYNV18otWdH8FwHD3uRcV1ia",  # admin123
        "role": "admin",
        "is_active": True,
    },
    "user": {
        "id": 2,
        "username": "user",
        "email": "user@mystocks.com",
        "hashed_password": "$2b$12$8aBh8ytBXEX0B0okxvYqPO428xzvnJlnA6c.q/ua6BS6z33ZP3WnK",  # user123
        "role": "user",
        "is_active": True,
    },
}


def get_users_db():
    """获取用户数据库"""
    return USERS_DB


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    """
    获取当前用户 - 已禁用认证
    返回默认用户，不再验证token
    """
    # 返回默认用户，绕过认证
    return User(
        id=1,
        username="guest",
        email="guest@mystocks.com",
        role="admin",  # 给予管理员权限
        is_active=True
    )


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    获取当前活跃用户 - 已禁用认证检查
    始终返回用户，不再检查活跃状态
    """
    # 始终返回用户，不再检查活跃状态
    return current_user


@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Dict[str, Any]:
    """
    用户登录获取访问令牌
    支持 OAuth2 标准的 form data 格式
    """
    # 验证用户身份
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id, "role": user.role},
        expires_delta=access_token_expires,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.access_token_expire_minutes * 60,
        "user": {"username": user.username, "email": user.email, "role": user.role},
    }


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)) -> Dict[str, Any]:
    """
    用户登出
    """
    # 在实际应用中，可以将 token 加入黑名单
    return {"message": "登出成功", "success": True}


@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)) -> User:
    """
    获取当前用户信息
    """
    return current_user


@router.post("/refresh")
async def refresh_token(
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    刷新访问令牌
    """
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={
            "sub": current_user.username,
            "user_id": current_user.id,
            "role": current_user.role,
        },
        expires_delta=access_token_expires,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.access_token_expire_minutes * 60,
    }


@router.get("/users")
async def get_users(current_user: User = Depends(get_current_user)) -> Dict[str, Any]:
    """
    获取用户列表（仅管理员）
    """
    if not check_permission(current_user.role, "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")

    users_db = get_users_db()
    users = []
    for username, user_data in users_db.items():
        user_info = user_data.copy()
        # 不返回密码哈希
        user_info.pop("hashed_password", None)
        users.append(user_info)

    return {"users": users, "total": len(users)}


def check_permission(user_role: str, required_role: str) -> bool:
    """
    检查用户权限
    """
    role_hierarchy = {"user": 0, "admin": 1}

    return role_hierarchy.get(user_role, 0) >= role_hierarchy.get(required_role, 0)
