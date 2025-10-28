"""
OAuth2 提供商实现 - 支持 Google、GitHub 等第三方认证

Task 2.1 Phase 2: OAuth2 Provider Integration
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import httpx
from datetime import datetime, timedelta
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class OAuth2Provider(ABC):
    """
    OAuth2 提供商基类

    定义所有 OAuth2 提供商必须实现的接口
    """

    def __init__(self):
        self.client_id = None
        self.client_secret = None
        self.redirect_uri = None
        self.authorization_url = None
        self.token_url = None
        self.userinfo_url = None

    @abstractmethod
    def get_authorization_url(self, state: str, scope: Optional[str] = None) -> str:
        """获取授权 URL"""
        pass

    @abstractmethod
    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """用授权码交换访问令牌"""
        pass

    @abstractmethod
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """获取用户信息"""
        pass

    async def refresh_access_token(
        self, refresh_token: str
    ) -> Optional[Dict[str, Any]]:
        """刷新访问令牌（可选）"""
        return None

    def validate_config(self) -> bool:
        """验证提供商配置是否完整"""
        return bool(self.client_id and self.client_secret and self.redirect_uri)


class GoogleOAuth2Provider(OAuth2Provider):
    """
    Google OAuth2 提供商实现

    支持 Google 账号登录
    """

    def __init__(self):
        super().__init__()
        self.client_id = settings.oauth2_google_client_id
        self.client_secret = settings.oauth2_google_client_secret
        self.redirect_uri = settings.oauth2_google_redirect_uri

        # Google OAuth2 固定端点
        self.authorization_url = "https://accounts.google.com/o/oauth2/v2/auth"
        self.token_url = "https://oauth2.googleapis.com/token"
        self.userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"

    def get_authorization_url(self, state: str, scope: Optional[str] = None) -> str:
        """
        获取 Google 授权 URL

        Args:
            state: CSRF 防护令牌
            scope: OAuth2 权限范围

        Returns:
            授权 URL
        """
        if not scope:
            scope = "openid email profile"

        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": scope,
            "state": state,
            "access_type": "offline",  # 获取刷新令牌
        }

        query_string = "&".join(f"{key}={value}" for key, value in params.items())
        return f"{self.authorization_url}?{query_string}"

    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """
        用授权码交换访问令牌

        Args:
            code: Google 返回的授权码

        Returns:
            包含 access_token、refresh_token 等信息的字典
        """
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                self.token_url,
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": self.redirect_uri,
                },
            )

            if response.status_code != 200:
                logger.error(f"Google token exchange failed: {response.text}")
                raise ValueError("Failed to exchange code for token")

            return response.json()

    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """
        获取用户信息

        Args:
            access_token: Google 访问令牌

        Returns:
            用户信息字典，包含 id、email、name、picture 等
        """
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                self.userinfo_url,
                headers={"Authorization": f"Bearer {access_token}"},
            )

            if response.status_code != 200:
                logger.error(f"Failed to get Google user info: {response.text}")
                raise ValueError("Failed to get user info")

            data = response.json()

            return {
                "provider_user_id": data.get("id"),
                "email": data.get("email"),
                "name": data.get("name"),
                "avatar": data.get("picture"),
                "verified_email": data.get("verified_email", False),
            }

    async def refresh_access_token(
        self, refresh_token: str
    ) -> Optional[Dict[str, Any]]:
        """
        刷新访问令牌

        Args:
            refresh_token: Google 刷新令牌

        Returns:
            包含新 access_token 的字典
        """
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                self.token_url,
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "refresh_token": refresh_token,
                    "grant_type": "refresh_token",
                },
            )

            if response.status_code != 200:
                logger.error(f"Failed to refresh Google token: {response.text}")
                return None

            return response.json()


class GitHubOAuth2Provider(OAuth2Provider):
    """
    GitHub OAuth2 提供商实现

    支持 GitHub 账号登录
    """

    def __init__(self):
        super().__init__()
        self.client_id = settings.oauth2_github_client_id
        self.client_secret = settings.oauth2_github_client_secret
        self.redirect_uri = settings.oauth2_github_redirect_uri

        # GitHub OAuth2 固定端点
        self.authorization_url = "https://github.com/login/oauth/authorize"
        self.token_url = "https://github.com/login/oauth/access_token"
        self.userinfo_url = "https://api.github.com/user"

    def get_authorization_url(self, state: str, scope: Optional[str] = None) -> str:
        """
        获取 GitHub 授权 URL

        Args:
            state: CSRF 防护令牌
            scope: OAuth2 权限范围

        Returns:
            授权 URL
        """
        if not scope:
            scope = "user:email"  # GitHub 权限范围

        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": scope,
            "state": state,
            "allow_signup": "true",
        }

        query_string = "&".join(f"{key}={value}" for key, value in params.items())
        return f"{self.authorization_url}?{query_string}"

    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """
        用授权码交换访问令牌

        Args:
            code: GitHub 返回的授权码

        Returns:
            包含 access_token 等信息的字典
        """
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                self.token_url,
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                    "redirect_uri": self.redirect_uri,
                },
                headers={"Accept": "application/json"},
            )

            if response.status_code != 200:
                logger.error(f"GitHub token exchange failed: {response.text}")
                raise ValueError("Failed to exchange code for token")

            return response.json()

    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """
        获取用户信息

        Args:
            access_token: GitHub 访问令牌

        Returns:
            用户信息字典，包含 id、login、email、avatar_url 等
        """
        async with httpx.AsyncClient(timeout=10) as client:
            # 获取基本用户信息
            response = await client.get(
                self.userinfo_url,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github.v3+json",
                },
            )

            if response.status_code != 200:
                logger.error(f"Failed to get GitHub user info: {response.text}")
                raise ValueError("Failed to get user info")

            data = response.json()

            # 如果用户未在个人资料中公开电子邮件，获取主电子邮件
            email = data.get("email")
            if not email:
                email = await self._get_primary_email(access_token)

            return {
                "provider_user_id": str(data.get("id")),
                "email": email,
                "name": data.get("name") or data.get("login"),
                "avatar": data.get("avatar_url"),
                "login": data.get("login"),
            }

    async def _get_primary_email(self, access_token: str) -> Optional[str]:
        """
        获取 GitHub 用户的主电子邮件地址

        GitHub 的主电子邮件在 /user/emails 端点中返回

        Args:
            access_token: GitHub 访问令牌

        Returns:
            主电子邮件地址或 None
        """
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(
                    "https://api.github.com/user/emails",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Accept": "application/vnd.github.v3+json",
                    },
                )

                if response.status_code == 200:
                    emails = response.json()
                    # 返回主电子邮件
                    for email_info in emails:
                        if email_info.get("primary"):
                            return email_info.get("email")

                    # 如果没有主电子邮件，返回已验证的第一个
                    for email_info in emails:
                        if email_info.get("verified"):
                            return email_info.get("email")

                return None
        except Exception as e:
            logger.warning(f"Failed to get GitHub emails: {e}")
            return None


class OAuth2ProviderFactory:
    """
    OAuth2 提供商工厂

    用于创建和管理 OAuth2 提供商实例
    """

    _providers = {
        "google": GoogleOAuth2Provider,
        "github": GitHubOAuth2Provider,
    }

    @classmethod
    def get_provider(cls, provider_name: str) -> Optional[OAuth2Provider]:
        """
        获取 OAuth2 提供商实例

        Args:
            provider_name: 提供商名称 ('google', 'github')

        Returns:
            提供商实例，或 None 如果提供商不存在或未配置
        """
        provider_class = cls._providers.get(provider_name.lower())
        if not provider_class:
            return None

        provider = provider_class()

        # 检查配置
        if not provider.validate_config():
            logger.warning(
                f"OAuth2 provider '{provider_name}' is not properly configured"
            )
            return None

        return provider

    @classmethod
    def register_provider(cls, name: str, provider_class: type) -> None:
        """
        注册新的 OAuth2 提供商

        Args:
            name: 提供商名称
            provider_class: 提供商类
        """
        cls._providers[name.lower()] = provider_class

    @classmethod
    def get_available_providers(cls) -> list:
        """获取所有可用的提供商列表"""
        available = []
        for name in cls._providers.keys():
            if cls.get_provider(name) is not None:
                available.append(name)

        return available


# 辅助函数
def create_oauth2_state(user_id: Optional[int] = None) -> str:
    """
    创建 OAuth2 状态令牌（CSRF 防护）

    Args:
        user_id: 可选的用户 ID

    Returns:
        状态令牌
    """
    import secrets
    import base64
    import json

    state_data = {
        "nonce": secrets.token_hex(16),
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": user_id,
    }

    state_json = json.dumps(state_data)
    state_bytes = state_json.encode("utf-8")
    state_b64 = base64.b64encode(state_bytes).decode("utf-8")

    return state_b64


def verify_oauth2_state(state: str, max_age_minutes: int = 10) -> Dict[str, Any]:
    """
    验证 OAuth2 状态令牌

    Args:
        state: 状态令牌
        max_age_minutes: 令牌最大有效期（分钟）

    Returns:
        解码后的状态数据

    Raises:
        ValueError: 如果状态令牌无效或已过期
    """
    import base64
    import json
    from datetime import datetime, timedelta

    try:
        state_bytes = base64.b64decode(state)
        state_json = state_bytes.decode("utf-8")
        state_data = json.loads(state_json)

        # 验证时间戳
        timestamp = datetime.fromisoformat(state_data.get("timestamp"))
        if datetime.utcnow() - timestamp > timedelta(minutes=max_age_minutes):
            raise ValueError("State token has expired")

        return state_data
    except Exception as e:
        logger.error(f"Failed to verify OAuth2 state: {e}")
        raise ValueError("Invalid state token")
