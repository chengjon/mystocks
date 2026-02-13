"""
Rate Limiting Module - 认证端点速率限制

【设计边界说明】
本模块为可选功能，默认禁用。仅当系统暴露到公网时建议启用。
对于本地部署场景，通常不需要此功能。

使用场景：
- 公网暴露：启用，防止暴力破解
- 本地部署：禁用（默认），减少复杂度
"""

import time
from collections import defaultdict
from dataclasses import dataclass, field
from threading import Lock
from typing import Callable, Dict, Optional, Tuple

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


@dataclass
class RateLimitConfig:
    """速率限制配置"""

    enabled: bool = False  # 默认禁用，本地部署不需要
    requests_per_minute: int = 10
    requests_per_hour: int = 100
    block_duration_seconds: int = 300  # 5 minutes
    whitelist_paths: set = field(
        default_factory=lambda: {
            "/health",
            "/api/health",
            "/docs",
            "/openapi.json",
            "/redoc",
        }
    )
    auth_paths: set = field(
        default_factory=lambda: {
            "/api/auth/login",
            "/api/auth/register",
            "/api/auth/password-reset",
            "/api/auth/password-reset/confirm",
        }
    )


@dataclass
class ClientState:
    """客户端状态"""

    minute_requests: list = field(default_factory=list)
    hour_requests: list = field(default_factory=list)
    blocked_until: float = 0
    failed_attempts: int = 0


class InMemoryRateLimiter:
    """
    内存速率限制器

    使用滑动窗口算法实现精确的速率限制。
    线程安全，支持并发访问。
    """

    def __init__(self, config: Optional[RateLimitConfig] = None):
        self.config = config or RateLimitConfig()
        self._clients: Dict[str, ClientState] = defaultdict(ClientState)
        self._lock = Lock()
        self._cleanup_interval = 3600  # 每小时清理一次过期数据
        self._last_cleanup = time.time()

    def _get_client_ip(self, request: Request) -> str:
        """获取客户端真实IP"""
        # 检查代理头
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # 直接连接
        if request.client:
            return request.client.host

        return "unknown"

    def _cleanup_expired(self) -> None:
        """清理过期数据"""
        current_time = time.time()
        if current_time - self._last_cleanup < self._cleanup_interval:
            return

        with self._lock:
            self._last_cleanup = current_time
            expired_clients = []

            for ip, state in self._clients.items():
                # 清理过期请求记录
                state.minute_requests = [t for t in state.minute_requests if current_time - t < 60]
                state.hour_requests = [t for t in state.hour_requests if current_time - t < 3600]

                # 如果客户端已被解封且没有请求记录，标记删除
                if state.blocked_until < current_time and not state.minute_requests and not state.hour_requests:
                    expired_clients.append(ip)

            for ip in expired_clients:
                del self._clients[ip]

    def _check_rate_limit(self, client_ip: str) -> Tuple[bool, Optional[str]]:
        """
        检查是否超过速率限制

        Returns:
            Tuple[bool, Optional[str]]: (是否允许, 错误消息)
        """
        current_time = time.time()

        with self._lock:
            state = self._clients[client_ip]

            # 检查是否被封禁
            if state.blocked_until > current_time:
                remaining = int(state.blocked_until - current_time)
                return False, f"Too many requests. Please try again in {remaining} seconds."

            # 清理过期记录
            state.minute_requests = [t for t in state.minute_requests if current_time - t < 60]
            state.hour_requests = [t for t in state.hour_requests if current_time - t < 3600]

            # 检查每分钟限制
            if len(state.minute_requests) >= self.config.requests_per_minute:
                return False, "Rate limit exceeded: too many requests per minute."

            # 检查每小时限制
            if len(state.hour_requests) >= self.config.requests_per_hour:
                return False, "Rate limit exceeded: too many requests per hour."

            # 记录请求
            state.minute_requests.append(current_time)
            state.hour_requests.append(current_time)

            return True, None

    def record_failed_auth(self, client_ip: str) -> None:
        """记录认证失败，连续失败多次将触发临时封禁"""
        current_time = time.time()

        with self._lock:
            state = self._clients[client_ip]
            state.failed_attempts += 1

            # 5次失败后封禁
            if state.failed_attempts >= 5:
                state.blocked_until = current_time + self.config.block_duration_seconds
                state.failed_attempts = 0

    def reset_failed_auth(self, client_ip: str) -> None:
        """认证成功后重置失败计数"""
        with self._lock:
            state = self._clients[client_ip]
            state.failed_attempts = 0

    def is_rate_limited(self, request: Request) -> Tuple[bool, Optional[str]]:
        """检查请求是否被限流"""
        self._cleanup_expired()
        client_ip = self._get_client_ip(request)
        return self._check_rate_limit(client_ip)

    def get_client_ip(self, request: Request) -> str:
        """公开方法：获取客户端IP"""
        return self._get_client_ip(request)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    速率限制中间件

    对认证端点实施严格的速率限制，防止暴力破解。
    默认禁用，仅通过环境变量 RATE_LIMIT_ENABLED=true 启用。
    """

    def __init__(self, app, config: Optional[RateLimitConfig] = None):
        super().__init__(app)
        self.config = config or RateLimitConfig()
        self.limiter = InMemoryRateLimiter(self.config) if self.config.enabled else None

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求"""
        # 如果未启用，直接放行
        if not self.config.enabled or self.limiter is None:
            return await call_next(request)

        path = request.url.path

        # 白名单路径直接通过
        if path in self.config.whitelist_paths:
            return await call_next(request)

        # 只对认证路径进行速率限制
        if path not in self.config.auth_paths:
            return await call_next(request)

        # 检查速率限制
        allowed, error_message = self.limiter.is_rate_limited(request)

        if not allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "code": "RATE_LIMIT_EXCEEDED",
                    "message": error_message or "Too many requests",
                    "data": None,
                    "path": path,
                },
                headers={"Retry-After": str(self.config.block_duration_seconds)},
            )

        # 继续处理请求
        response = await call_next(request)

        return response


# 全局速率限制器实例
_rate_limiter: Optional[InMemoryRateLimiter] = None


def get_rate_limiter() -> InMemoryRateLimiter:
    """获取全局速率限制器实例"""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = InMemoryRateLimiter()
    return _rate_limiter


def setup_rate_limiting(app, config: Optional[RateLimitConfig] = None) -> InMemoryRateLimiter:
    """
    配置应用的速率限制

    Args:
        app: FastAPI 应用实例
        config: 速率限制配置

    Returns:
        InMemoryRateLimiter: 速率限制器实例
    """
    global _rate_limiter

    config = config or RateLimitConfig()
    _rate_limiter = InMemoryRateLimiter(config)

    # 添加中间件
    app.add_middleware(RateLimitMiddleware, config=config)

    return _rate_limiter
