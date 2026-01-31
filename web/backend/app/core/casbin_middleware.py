"""
Casbin FastAPI 集成 - 简化版 (单用户系统)

Casbin FastAPI Integration - Simplified for Single-User System

Task 10: Casbin权限集成

功能特性:
- 简化的权限检查（无需复杂验证）
- 基于角色的权限控制
- 资源级别权限控制
- FastAPI依赖注入集成

Author: Claude Code
Date: 2025-11-07
"""

from typing import Callable

import structlog
from fastapi import HTTPException, status

from app.core.casbin_manager import CasbinManager, get_casbin_manager

logger = structlog.get_logger()


def get_current_role(role: str = "user") -> str:
    """获取当前用户角色

    对于单用户系统，返回配置的固定角色或参数角色

    Args:
        role: 用户角色 (默认: "user")

    Returns:
        用户角色
    """
    logger.debug("Getting current role", role=role)
    return role


def require_permission(resource: str, action: str, role: str = "user") -> Callable:
    """权限检查依赖

    Args:
        resource: 资源名称 (如 'indicator', 'dashboard')
        action: 操作 (如 'read', 'write', 'delete')
        role: 用户角色 (默认: 'user')

    Returns:
        异步依赖函数

    Example:
        @app.get("/api/indicators")
        async def get_indicators(
            _ = Depends(require_permission("indicator", "read"))
        ):
            return {"indicators": []}
    """

    async def check_permission() -> bool:
        """检查权限

        Raises:
            HTTPException: 权限不足
        """
        manager = get_casbin_manager()

        # 检查权限
        has_permission = manager.enforce(role, resource, action)

        if not has_permission:
            logger.warning(
                "⚠️ Permission denied",
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
            role=role,
            resource=resource,
            action=action,
        )

        return True

    return check_permission


def check_permission(resource: str, action: str, role: str = "user") -> bool:
    """直接检查权限（非依赖函数）

    用于在路由处理函数内部直接检查权限

    Args:
        resource: 资源名称
        action: 操作
        role: 用户角色 (默认: 'user')

    Returns:
        是否有权限

    Example:
        @app.get("/api/indicators")
        async def get_indicators():
            if not check_permission("indicator", "read"):
                raise HTTPException(status_code=403, detail="Permission denied")
            return {"indicators": []}
    """
    manager = get_casbin_manager()
    has_permission = manager.enforce(role, resource, action)

    if not has_permission:
        logger.warning(
            "⚠️ Permission check failed",
            role=role,
            resource=resource,
            action=action,
        )
    else:
        logger.debug(
            "✅ Permission check passed",
            role=role,
            resource=resource,
            action=action,
        )

    return has_permission


def get_manager() -> CasbinManager:
    """获取Casbin管理器实例

    Returns:
        CasbinManager实例
    """
    return get_casbin_manager()
