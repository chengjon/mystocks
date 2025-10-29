"""
认证相关 API
"""

from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from datetime import timedelta
import structlog
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
from app.core.database import get_db
from app.models.user import User as UserModel, MFASecret as MFASecretModel

router = APIRouter()
security = HTTPBearer()
logger = structlog.get_logger()

# MFA 查询失败计数器 - 用于监控是否存在持续性故障
_mfa_query_failure_count = 0
_mfa_query_failure_threshold = 5  # 连续 5 次失败时触发警告

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
    获取当前用户
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # 验证 token
        token_data = verify_token(credentials.credentials)
        if token_data is None:
            raise credentials_exception

        username = token_data.username
        if username is None:
            raise credentials_exception

    except Exception:
        raise credentials_exception

    # 查找用户
    users_db = get_users_db()
    user = users_db.get(username)
    if user is None:
        raise credentials_exception

    return User(**user)


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    获取当前活跃用户
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@router.post("/login", response_model=Token)
async def login_for_access_token(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    用户登录获取访问令牌
    支持 OAuth2 标准的 form data 格式

    如果用户启用了 MFA，响应会包含 mfa_required 标志和临时令牌
    """
    try:
        # 验证用户身份
        user = authenticate_user(username, password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 尝试检查用户是否启用了 MFA（可选，如果数据库不可用则跳过）
        global _mfa_query_failure_count
        mfa_enabled = False
        verified_mfa = []
        try:
            db_user = db.execute(
                select(UserModel).where(UserModel.username == username)
            ).scalar_one_or_none()

            if db_user and db_user.mfa_enabled:
                # 检查用户是否有已验证的 MFA 方法
                verified_mfa = (
                    db.execute(
                        select(MFASecretModel).where(
                            (MFASecretModel.user_id == db_user.id)
                            and (MFASecretModel.is_verified == True)
                        )
                    )
                    .scalars()
                    .all()
                )
                mfa_enabled = bool(verified_mfa)
            # MFA 查询成功，重置失败计数
            _mfa_query_failure_count = 0
        except Exception as e:
            # 如果数据库查询失败，继续进行标准登录（优雅降级）
            # 但同时记录详细的错误信息用于监控和告警
            _mfa_query_failure_count += 1

            # 记录警告级别日志（可被监控系统捕获）
            logger.warning(
                "mfa_check_failed",
                username=username,
                error=str(e),
                failure_count=_mfa_query_failure_count,
                event_type="graceful_degradation_triggered",
            )

            # 当连续失败次数超过阈值时，记录为告警级别错误
            if _mfa_query_failure_count >= _mfa_query_failure_threshold:
                logger.error(
                    "mfa_persistent_failure_alert",
                    failure_count=_mfa_query_failure_count,
                    threshold=_mfa_query_failure_threshold,
                    message="MFA database checks have failed persistently. This may indicate a database corruption or connectivity issue.",
                    severity="HIGH",
                    action_required="Investigate database health and MFA tables immediately",
                )

        if mfa_enabled and verified_mfa:
            # 创建临时令牌用于 MFA 验证
            # 临时令牌有效期很短（5分钟）
            temp_token_expires = timedelta(minutes=5)
            temp_token = create_access_token(
                data={
                    "sub": user.username,
                    "user_id": user.id,
                    "role": user.role,
                    "mfa_pending": True,
                },
                expires_delta=temp_token_expires,
            )

            return {
                "access_token": temp_token,
                "token_type": "bearer",
                "expires_in": 5 * 60,  # 5 minutes
                "mfa_required": True,
                "mfa_methods": [mfa.method for mfa in verified_mfa],
                "user": {
                    "username": user.username,
                    "email": user.email,
                    "role": user.role,
                },
            }

        # 如果没有启用 MFA，直接返回完整的访问令牌
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": user.username, "user_id": user.id, "role": user.role},
            expires_delta=access_token_expires,
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.access_token_expire_minutes * 60,
            "mfa_required": False,
            "user": {
                "username": user.username,
                "email": user.email,
                "role": user.role,
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        # 捕获所有未预期的错误并返回 500 响应的友好版本
        import logging

        logging.error(f"Login endpoint error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登录服务暂时不可用，请稍后重试",
        )


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
