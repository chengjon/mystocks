"""
认证相关 API
"""

from datetime import timedelta
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2PasswordRequestForm

from app.core.config import settings
from app.core.responses import create_success_response
from app.core.security import (
    Token,
    User,
    authenticate_user,
    create_access_token,
    verify_token,
)

router = APIRouter()
security = HTTPBearer()

# User database now backed by PostgreSQL via security.py
# The authenticate_user() and get_user_from_database() functions
# handle database queries with automatic fallback to mock data
# if the database is unavailable.


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    """
    获取当前用户 - 恢复认证验证
    验证 JWT token 并返回授权用户信息
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        # 验证 JWT token
        token_data = verify_token(credentials.credentials)
        if token_data is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        username: str = token_data.username
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token claims",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 从安全模块获取用户信息（数据库或模拟数据）
    from app.core.security import authenticate_user_by_id

    user_in_db = authenticate_user_by_id(token_data.user_id)
    if user_in_db is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = User(
        id=user_in_db.id,
        username=user_in_db.username,
        email=user_in_db.email,
        role=user_in_db.role,
        is_active=user_in_db.is_active,
    )
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    获取当前活跃用户 - 验证用户活跃状态
    检查用户是否处于活跃状态
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
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
    从PostgreSQL数据库获取所有活跃用户
    """
    if not check_permission(current_user.role, "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")

    try:
        from app.core.database import get_postgresql_session
        from app.db import UserRepository
        from src.core.exceptions import DatabaseConnectionError, DatabaseOperationError

        session = get_postgresql_session()
        try:
            repository = UserRepository(session)
            users_list = repository.get_all_users()

            users = []
            for user in users_list:
                user_info = {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "role": user.role,
                    "is_active": user.is_active,
                    # 不返回密码哈希
                }
                users.append(user_info)

            return {"users": users, "total": len(users)}

        finally:
            session.close()

    except (DatabaseConnectionError, DatabaseOperationError) as e:
        # 数据库查询失败时返回错误响应
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to retrieve users: {str(e)}",
        )
    except Exception as e:
        # 捕获其他异常
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving users: {str(e)}",
        )


def check_permission(user_role: str, required_role: str) -> bool:
    """
    检查用户权限
    """
    role_hierarchy = {"user": 0, "admin": 1}

    return role_hierarchy.get(user_role, 0) >= role_hierarchy.get(required_role, 0)


# SECURITY FIX 1.2: CSRF Token获取端点
@router.get("/csrf/token")
async def get_csrf_token():
    """
    获取CSRF保护令牌 - v1版本 (标准化端点)

    用于防止跨站请求伪造（CSRF）攻击。
    前端应该在发送修改请求（POST/PUT/PATCH/DELETE）时，
    在X-CSRF-Token请求头中包含此令牌。

    **响应示例**:
    ```json
    {
        "code": "SUCCESS",
        "message": "CSRF token generated successfully",
        "data": {
            "token": "...base64-encoded-token...",
            "token_type": "csrf",
            "expires_in": 3600
        },
        "timestamp": 1733318400.123
    }
    ```

    **使用示例**:
    ```javascript
    // 获取CSRF token
    const response = await fetch('/api/v1/auth/csrf/token');
    const { data } = await response.json();
    const csrfToken = data.token;

    // 发送受保护的请求
    fetch('/api/v1/data', {
        method: 'POST',
        headers: {
            'X-CSRF-Token': csrfToken,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ ... })
    });
    ```

    **错误码**:
    - SUCCESS: Token生成成功
    - INTERNAL_SERVER_ERROR: Token生成失败

    **HTTP状态码**:
    - 200: 成功获取token
    - 500: 服务器错误

    **Rate Limit**: 无限制（CSRF token获取不计入速率限制）
    """
    from app.main import csrf_manager

    try:
        # 生成新的CSRF token
        token = csrf_manager.generate_token()

        return create_success_response(
            data={
                "token": token,
                "token_type": "csrf",
                "expires_in": csrf_manager.token_timeout,
            },
            message="CSRF token generated successfully",
        )
    except Exception as e:
        return create_success_response(
            data=None,
            message=f"Failed to generate CSRF token: {str(e)}",
            code="INTERNAL_SERVER_ERROR",
        )
