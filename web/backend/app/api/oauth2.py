"""
OAuth2 认证 API 端点

Task 2.1 Phase 2: OAuth2 Provider Integration
"""

from fastapi import APIRouter, HTTPException, Query, Depends, status
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import logging
from datetime import datetime, timedelta
import secrets

from app.core.oauth2_providers import (
    OAuth2ProviderFactory,
    create_oauth2_state,
    verify_oauth2_state,
)
from app.core.config import settings
from app.core.security import (
    create_access_token,
    Token,
    User,
    verify_password,
    get_password_hash,
)
from app.core.database import get_db
from app.models.user import User as UserModel, OAuth2Account as OAuth2AccountModel

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/oauth2/{provider}")
async def oauth2_login(
    provider: str, redirect_uri: Optional[str] = Query(None)
) -> RedirectResponse:
    """
    OAuth2 登录重定向端点

    将用户重定向到第三方 OAuth2 提供商的授权页面

    Args:
        provider: OAuth2 提供商名称 ('google', 'github')
        redirect_uri: 登录成功后的重定向 URI（可选）

    Returns:
        重定向到 OAuth2 提供商的授权 URL
    """
    # 获取 OAuth2 提供商
    oauth2_provider = OAuth2ProviderFactory.get_provider(provider)
    if not oauth2_provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"OAuth2 provider '{provider}' is not available",
        )

    # 创建 state 令牌用于 CSRF 防护
    state = create_oauth2_state()

    # 获取授权 URL
    auth_url = oauth2_provider.get_authorization_url(state)

    logger.info(f"OAuth2 login initiated for provider: {provider}")

    return RedirectResponse(url=auth_url)


@router.get("/oauth2/{provider}/callback")
async def oauth2_callback(
    provider: str,
    code: str = Query(...),
    state: str = Query(...),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    OAuth2 回调端点

    处理来自 OAuth2 提供商的回调，交换授权码获取令牌

    Args:
        provider: OAuth2 提供商名称
        code: OAuth2 授权码
        state: CSRF 防护令牌
        db: 数据库会话

    Returns:
        JWT 访问令牌和用户信息
    """
    # 验证 state 令牌
    try:
        state_data = verify_oauth2_state(state)
    except ValueError as e:
        logger.warning(f"OAuth2 state verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired state token",
        )

    # 获取 OAuth2 提供商
    oauth2_provider = OAuth2ProviderFactory.get_provider(provider)
    if not oauth2_provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"OAuth2 provider '{provider}' is not available",
        )

    # 交换授权码获取令牌
    try:
        token_response = await oauth2_provider.exchange_code_for_token(code)
    except ValueError as e:
        logger.error(f"Token exchange failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Failed to exchange authorization code for token",
        )

    # 获取用户信息
    try:
        access_token = token_response.get("access_token")
        user_info = await oauth2_provider.get_user_info(access_token)
    except ValueError as e:
        logger.error(f"Failed to get user info: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Failed to retrieve user information from OAuth2 provider",
        )

    # 查找或创建用户
    provider_user_id = user_info.get("provider_user_id")

    # 首先查找现有的 OAuth2 账户
    stmt = select(OAuth2AccountModel).where(
        (OAuth2AccountModel.provider == provider)
        and (OAuth2AccountModel.provider_user_id == provider_user_id)
    )
    oauth2_account = db.execute(stmt).scalar_one_or_none()

    if oauth2_account:
        # 更新现有 OAuth2 账户
        oauth2_account.access_token = access_token
        oauth2_account.refresh_token = token_response.get("refresh_token")
        oauth2_account.token_expires_at = datetime.utcnow() + timedelta(
            seconds=token_response.get("expires_in", 3600)
        )
        oauth2_account.provider_email = user_info.get("email")
        oauth2_account.provider_name = user_info.get("name")
        oauth2_account.provider_avatar = user_info.get("avatar")
        oauth2_account.last_used_at = datetime.utcnow()

        user = db.execute(
            select(UserModel).where(UserModel.id == oauth2_account.user_id)
        ).scalar_one_or_none()

        logger.info(f"OAuth2 account updated: {provider}:{provider_user_id}")
    else:
        # 查找或创建用户
        email = user_info.get("email")
        stmt = select(UserModel).where(UserModel.email == email)
        user = db.execute(stmt).scalar_one_or_none()

        if not user:
            # 创建新用户
            username = (
                user_info.get("login") or user_info.get("email", "").split("@")[0]
            )

            # 确保用户名唯一
            base_username = username
            counter = 1
            while (
                db.execute(
                    select(UserModel).where(UserModel.username == username)
                ).scalar_one_or_none()
                is not None
            ):
                username = f"{base_username}{counter}"
                counter += 1

            user = UserModel(
                username=username,
                email=email,
                full_name=user_info.get("name"),
                avatar_url=user_info.get("avatar"),
                role="user",
                is_active=True,
                email_verified=user_info.get("verified_email", False),
            )

            db.add(user)
            db.flush()  # 获取生成的 user.id

            logger.info(f"New user created from OAuth2: {username} ({provider})")

        # 创建 OAuth2 账户关联
        oauth2_account = OAuth2AccountModel(
            user_id=user.id,
            provider=provider,
            provider_user_id=provider_user_id,
            access_token=access_token,
            refresh_token=token_response.get("refresh_token"),
            token_type=token_response.get("token_type", "Bearer"),
            token_expires_at=(
                datetime.utcnow()
                + timedelta(seconds=token_response.get("expires_in", 3600))
            ),
            provider_email=email,
            provider_name=user_info.get("name"),
            provider_avatar=user_info.get("avatar"),
            last_used_at=datetime.utcnow(),
        )

        db.add(oauth2_account)

        logger.info(f"New OAuth2 account created: {provider}:{provider_user_id}")

    # 更新用户最后登录时间
    user.last_login = datetime.utcnow()

    # 提交事务
    db.commit()

    # 创建 JWT 访问令牌
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    jwt_token = create_access_token(
        data={
            "sub": user.username,
            "user_id": user.id,
            "role": user.role,
        },
        expires_delta=access_token_expires,
    )

    # 返回令牌和用户信息
    response = {
        "access_token": jwt_token,
        "token_type": "bearer",
        "expires_in": settings.access_token_expire_minutes * 60,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "full_name": user.full_name,
            "avatar_url": user.avatar_url,
        },
    }

    logger.info(f"OAuth2 login successful for user: {user.username}")

    return response


@router.post("/oauth2/link/{provider}")
async def link_oauth2_account(
    provider: str,
    code: str,
    state: str,
    current_user: User = Depends(),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    关联 OAuth2 账户到现有用户

    允许已登录的用户将其账户与 OAuth2 提供商关联

    Args:
        provider: OAuth2 提供商名称
        code: OAuth2 授权码
        state: CSRF 防护令牌
        current_user: 当前登录的用户
        db: 数据库会话

    Returns:
        成功消息
    """
    # 验证 state 令牌
    try:
        verify_oauth2_state(state)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired state token",
        )

    # 获取 OAuth2 提供商
    oauth2_provider = OAuth2ProviderFactory.get_provider(provider)
    if not oauth2_provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"OAuth2 provider '{provider}' is not available",
        )

    # 交换授权码获取令牌
    try:
        token_response = await oauth2_provider.exchange_code_for_token(code)
        access_token = token_response.get("access_token")
        user_info = await oauth2_provider.get_user_info(access_token)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Failed to authenticate with OAuth2 provider",
        )

    # 检查 OAuth2 账户是否已经被其他用户关联
    provider_user_id = user_info.get("provider_user_id")
    existing_account = db.execute(
        select(OAuth2AccountModel).where(
            (OAuth2AccountModel.provider == provider)
            and (OAuth2AccountModel.provider_user_id == provider_user_id)
        )
    ).scalar_one_or_none()

    if existing_account and existing_account.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This OAuth2 account is already linked to another user",
        )

    # 获取当前用户数据库对象
    user = db.execute(
        select(UserModel).where(UserModel.id == current_user.id)
    ).scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if existing_account:
        # 更新现有关联
        existing_account.access_token = access_token
        existing_account.refresh_token = token_response.get("refresh_token")
        existing_account.token_expires_at = datetime.utcnow() + timedelta(
            seconds=token_response.get("expires_in", 3600)
        )
        existing_account.last_used_at = datetime.utcnow()
    else:
        # 创建新的关联
        oauth2_account = OAuth2AccountModel(
            user_id=user.id,
            provider=provider,
            provider_user_id=provider_user_id,
            access_token=access_token,
            refresh_token=token_response.get("refresh_token"),
            token_type=token_response.get("token_type", "Bearer"),
            token_expires_at=(
                datetime.utcnow()
                + timedelta(seconds=token_response.get("expires_in", 3600))
            ),
            provider_email=user_info.get("email"),
            provider_name=user_info.get("name"),
            provider_avatar=user_info.get("avatar"),
            last_used_at=datetime.utcnow(),
        )

        db.add(oauth2_account)

    db.commit()

    logger.info(f"OAuth2 account linked for user {user.username}: {provider}")

    return {
        "success": True,
        "message": f"Successfully linked {provider} account",
        "provider": provider,
        "email": user_info.get("email"),
    }


@router.get("/oauth2/available-providers")
async def get_available_providers() -> Dict[str, Any]:
    """
    获取可用的 OAuth2 提供商列表

    Returns:
        可用提供商列表
    """
    providers = OAuth2ProviderFactory.get_available_providers()

    return {
        "available_providers": providers,
        "count": len(providers),
    }
