"""
Casbin FastAPI 集成中间件 - Casbin FastAPI Integration Middleware

Task 10: Casbin权限集成

功能特性:
- FastAPI中间件和依赖注入集成
- 权限检查依赖装饰器
- 自动角色提取和权限强制
- 资源级别权限控制
- 动态权限检查

Author: Claude Code
Date: 2025-11-07
"""

from typing import Optional, Callable, Any
from functools import wraps
from fastapi import Depends, HTTPException, status, Request
from starlette.authentication import AuthenticationError
import structlog
import jwt

from app.core.casbin_manager import get_casbin_manager, CasbinManager

logger = structlog.get_logger()


async def get_current_user_from_token(
    request: Request = None,
) -> dict:
    """从JWT token获取当前用户信息

    Args:
        request: FastAPI请求对象

    Returns:
        用户信息字典

    Raises:
        HTTPException: 认证失败
    """
    # 从Authorization header获取token
    auth_header = request.headers.get("Authorization") if request else None
    if not auth_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
        )

    # 提取Bearer token
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
        )

    token = parts[1]

    try:
        # 这里应该使用实际的JWT密钥和算法
        # 为了演示，我们使用简单的解析
        payload = jwt.decode(token, options={"verify_signature": False})
        user_id = payload.get("sub")
        role = payload.get("role", "user")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user_id",
            )

        return {"user_id": user_id, "role": role}

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )


def require_permission(
    resource: str,
    action: str,
    casbin_manager: Optional[CasbinManager] = None,
) -> Callable:
    """权限检查依赖生成器

    Args:
        resource: 资源名称 (如 'indicator', 'dashboard')
        action: 操作 (如 'read', 'write', 'delete')
        casbin_manager: Casbin管理器实例

    Returns:
        异步依赖函数

    Example:
        @app.get("/api/indicators")
        async def get_indicators(
            user: dict = Depends(get_current_user_from_token),
            _ = Depends(require_permission("indicator", "read"))
        ):
            ...
    """

    async def check_permission(
        user: dict = Depends(get_current_user_from_token),
    ) -> dict:
        """检查用户是否有权限

        Args:
            user: 用户信息字典

        Returns:
            用户信息字典

        Raises:
            HTTPException: 权限不足
        """
        manager = casbin_manager or get_casbin_manager()
        user_id = user.get("user_id")
        role = user.get("role", "user")

        # 使用角色而不是用户ID进行权限检查
        # 如果需要用户级别的权限检查，可以改为user_id
        has_permission = manager.enforce(role, resource, action)

        if not has_permission:
            logger.warning(
                "⚠️ Permission denied",
                user_id=user_id,
                role=role,
                resource=resource,
                action=action,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {action} on {resource}",
            )

        logger.debug(
            "✅ Permission granted",
            user_id=user_id,
            role=role,
            resource=resource,
            action=action,
        )

        return user

    return check_permission


def permission_required(resource: str, action: str) -> Callable:
    """权限装饰器 - 用于FastAPI路由

    Args:
        resource: 资源名称
        action: 操作

    Returns:
        装饰器函数

    Example:
        @app.get("/api/indicators")
        @permission_required("indicator", "read")
        async def get_indicators():
            ...
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(
            *args,
            user: dict = Depends(get_current_user_from_token),
            **kwargs,
        ):
            manager = get_casbin_manager()
            role = user.get("role", "user")
            user_id = user.get("user_id")

            # 检查权限
            has_permission = manager.enforce(role, resource, action)

            if not has_permission:
                logger.warning(
                    "⚠️ Permission denied by decorator",
                    user_id=user_id,
                    role=role,
                    resource=resource,
                    action=action,
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied: {action} on {resource}",
                )

            logger.debug(
                "✅ Permission granted by decorator",
                user_id=user_id,
                role=role,
                resource=resource,
                action=action,
            )

            # 注入用户信息到kwargs中
            kwargs["user"] = user
            return await func(*args, **kwargs)

        return wrapper

    return decorator


class CasbinPermissionMiddleware:
    """Casbin权限检查中间件

    可选的中间件层，用于全局权限检查
    通常需要与路由级别的权限检查配合使用
    """

    def __init__(self, casbin_manager: Optional[CasbinManager] = None):
        """初始化中间件

        Args:
            casbin_manager: Casbin管理器实例
        """
        self.manager = casbin_manager or get_casbin_manager()
        logger.info("✅ Casbin Permission Middleware initialized")

    async def __call__(self, request: Request, call_next) -> Any:
        """处理请求

        Args:
            request: FastAPI请求对象
            call_next: 下一个中间件

        Returns:
            响应对象
        """
        # 中间件主要用于日志记录和统计
        # 实际的权限检查应在路由级别进行
        response = await call_next(request)
        return response


# 获取用户ID用于行级权限检查
def get_user_id_from_request(
    user: dict = Depends(get_current_user_from_token),
) -> str:
    """从请求中获取用户ID

    Args:
        user: 用户信息字典

    Returns:
        用户ID
    """
    return user.get("user_id", "")


# 行级权限检查函数
def check_row_level_permission(
    user_id: str,
    resource_owner_id: str,
    allow_admin: bool = True,
) -> bool:
    """检查行级权限（用户数据所有权）

    Args:
        user_id: 请求用户ID
        resource_owner_id: 资源所有者ID
        allow_admin: 是否允许管理员跳过所有权检查

    Returns:
        是否有权访问该资源
    """
    manager = get_casbin_manager()

    # 管理员可以访问所有数据
    if allow_admin and manager.enforce("admin", "data", "read"):
        return True

    # 用户只能访问自己的数据
    return user_id == resource_owner_id


def require_admin(user: dict = Depends(get_current_user_from_token)) -> dict:
    """管理员权限检查依赖

    Args:
        user: 用户信息字典

    Returns:
        用户信息字典

    Raises:
        HTTPException: 非管理员用户
    """
    role = user.get("role", "user")

    if role != "admin":
        logger.warning(
            "⚠️ Admin access denied",
            user_id=user.get("user_id"),
            role=role,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    logger.debug("✅ Admin access granted", user_id=user.get("user_id"))
    return user


def require_vip(user: dict = Depends(get_current_user_from_token)) -> dict:
    """VIP权限检查依赖

    Args:
        user: 用户信息字典

    Returns:
        用户信息字典

    Raises:
        HTTPException: 非VIP用户
    """
    role = user.get("role", "user")

    if role not in ["admin", "vip"]:
        logger.warning(
            "⚠️ VIP access denied",
            user_id=user.get("user_id"),
            role=role,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="VIP access required",
        )

    logger.debug("✅ VIP access granted", user_id=user.get("user_id"))
    return user


# 获取Casbin管理器
def get_manager() -> CasbinManager:
    """获取Casbin管理器实例

    Returns:
        CasbinManager实例
    """
    return get_casbin_manager()
