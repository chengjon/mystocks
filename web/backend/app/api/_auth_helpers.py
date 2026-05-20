"""Auth helper functions and shared objects."""

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.core.exceptions import UnauthorizedException
from app.core.security import User, verify_token

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    """
    获取当前用户 - 恢复认证验证
    验证 JWT token 并返回授权用户信息
    """
    if not credentials:
        raise UnauthorizedException(detail="Missing authentication credentials")

    try:
        # 验证 JWT token
        token_data = verify_token(credentials.credentials)
        if token_data is None:
            raise UnauthorizedException(detail="Invalid or expired token")

        username: str = token_data.username
        if username is None:
            raise UnauthorizedException(detail="Invalid token claims")
    except Exception as e:
        raise UnauthorizedException(detail=f"Invalid credentials: {str(e)}")

    # 从安全模块获取用户信息（数据库或模拟数据）
    from app.core.security import authenticate_user_by_id

    user_in_db = authenticate_user_by_id(token_data.user_id)
    if user_in_db is None:
        raise UnauthorizedException(detail="User not found")

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
        raise UnauthorizedException(detail="User account is inactive")
    return current_user


def check_permission(user_role: str, required_role: str) -> bool:
    role_hierarchy = {"user": 0, "admin": 1}
    return role_hierarchy.get(user_role, 0) >= role_hierarchy.get(required_role, 0)

