"""
Tests for Rate Limiting Module

Tests the rate limiting middleware and rate limiter functionality.
"""

import pytest
from unittest.mock import MagicMock, patch
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from app.core.rate_limit import (
    InMemoryRateLimiter,
    RateLimitConfig,
    RateLimitMiddleware,
    get_rate_limiter,
    setup_rate_limiting,
)
from app.core.exceptions import RateLimitException


class TestInMemoryRateLimiter:
    """Tests for InMemoryRateLimiter class"""

    def test_init_default_config(self):
        """Test default configuration initialization"""
        limiter = InMemoryRateLimiter()
        assert limiter.config.requests_per_minute == 10
        assert limiter.config.requests_per_hour == 100
        assert limiter.config.block_duration_seconds == 300

    def test_init_custom_config(self):
        """Test custom configuration initialization"""
        config = RateLimitConfig(
            requests_per_minute=5,
            requests_per_hour=50,
            block_duration_seconds=60,
        )
        limiter = InMemoryRateLimiter(config)
        assert limiter.config.requests_per_minute == 5
        assert limiter.config.requests_per_hour == 50
        assert limiter.config.block_duration_seconds == 60

    def test_get_client_ip_direct(self):
        """Test getting client IP from direct connection"""
        limiter = InMemoryRateLimiter()
        request = MagicMock(spec=Request)
        request.headers = {}
        request.client = MagicMock()
        request.client.host = "192.168.1.1"

        ip = limiter._get_client_ip(request)
        assert ip == "192.168.1.1"

    def test_get_client_ip_forwarded(self):
        """Test getting client IP from X-Forwarded-For header"""
        limiter = InMemoryRateLimiter()
        request = MagicMock(spec=Request)
        request.headers = {"X-Forwarded-For": "10.0.0.1, 192.168.1.1"}
        request.client = MagicMock()
        request.client.host = "192.168.1.1"

        ip = limiter._get_client_ip(request)
        assert ip == "10.0.0.1"

    def test_check_rate_limit_allows_requests(self):
        """Test that requests under limit are allowed"""
        limiter = InMemoryRateLimiter()
        allowed, error = limiter._check_rate_limit("192.168.1.1")
        assert allowed is True
        assert error is None

    def test_check_rate_limit_blocks_excessive_requests(self):
        """Test that excessive requests are blocked"""
        config = RateLimitConfig(requests_per_minute=2)
        limiter = InMemoryRateLimiter(config)

        # First two requests should be allowed
        limiter._check_rate_limit("192.168.1.1")
        limiter._check_rate_limit("192.168.1.1")

        # Third request should be blocked
        allowed, error = limiter._check_rate_limit("192.168.1.1")
        assert allowed is False
        assert "too many requests per minute" in error.lower()

    def test_record_failed_auth_triggers_block(self):
        """Test that failed auth attempts trigger block after threshold"""
        limiter = InMemoryRateLimiter()

        # Record 5 failed attempts
        for _ in range(5):
            limiter.record_failed_auth("192.168.1.1")

        # Next request should be blocked
        allowed, error = limiter._check_rate_limit("192.168.1.1")
        assert allowed is False
        assert "blocked" in error.lower() or "too many" in error.lower()

    def test_reset_failed_auth(self):
        """Test that successful auth resets failed counter"""
        limiter = InMemoryRateLimiter()

        # Record some failed attempts
        limiter.record_failed_auth("192.168.1.1")
        limiter.record_failed_auth("192.168.1.1")

        # Reset on successful auth
        limiter.reset_failed_auth("192.168.1.1")

        # Should still have remaining attempts
        allowed, _ = limiter._check_rate_limit("192.168.1.1")
        assert allowed is True

    def test_different_clients_tracked_separately(self):
        """Test that different clients are tracked independently"""
        config = RateLimitConfig(requests_per_minute=2)
        limiter = InMemoryRateLimiter(config)

        # Client 1 uses up their limit
        limiter._check_rate_limit("192.168.1.1")
        limiter._check_rate_limit("192.168.1.1")

        # Client 2 should still be allowed
        allowed, _ = limiter._check_rate_limit("192.168.1.2")
        assert allowed is True

        # Client 1 should be blocked
        allowed, _ = limiter._check_rate_limit("192.168.1.1")
        assert allowed is False


class TestRateLimitMiddleware:
    """Tests for RateLimitMiddleware class"""

    @pytest.fixture
    def app(self):
        """Create a test FastAPI app"""
        app = FastAPI()

        @app.get("/api/auth/login")
        async def login():
            return {"message": "login"}

        @app.get("/health")
        async def health():
            return {"status": "ok"}

        @app.get("/api/data")
        async def data():
            return {"data": "test"}

        return app

    def test_whitelist_paths_pass_through(self, app):
        """Test that whitelist paths bypass rate limiting"""
        config = RateLimitConfig(enabled=True)  # 需要显式启用
        app.add_middleware(RateLimitMiddleware, config=config)
        client = TestClient(app)

        # Health endpoint should always be accessible
        for _ in range(15):
            response = client.get("/health")
            assert response.status_code == 200

    def test_auth_paths_rate_limited(self, app):
        """Test that auth paths are rate limited when enabled"""
        config = RateLimitConfig(enabled=True, requests_per_minute=5)  # 需要显式启用
        app.add_middleware(RateLimitMiddleware, config=config)
        client = TestClient(app)

        # Make requests up to the limit
        for _ in range(5):
            response = client.get("/api/auth/login")
            assert response.status_code == 200

        # Next request should be rate limited
        response = client.get("/api/auth/login")
        assert response.status_code == 429
        assert response.json()["code"] == "RATE_LIMIT_EXCEEDED"

    def test_non_auth_paths_not_limited(self, app):
        """Test that non-auth paths are not rate limited"""
        config = RateLimitConfig(enabled=True, requests_per_minute=2)  # 需要显式启用
        app.add_middleware(RateLimitMiddleware, config=config)
        client = TestClient(app)

        # Make many requests to non-auth endpoint
        for _ in range(10):
            response = client.get("/api/data")
            assert response.status_code == 200


class TestRateLimitException:
    """Tests for RateLimitException class"""

    def test_exception_default_values(self):
        """Test default exception values"""
        exc = RateLimitException()
        assert exc.status_code == 429
        assert exc.error_code == "RATE_LIMIT_EXCEEDED"
        assert "频繁" in exc.detail

    def test_exception_custom_message(self):
        """Test custom exception message"""
        exc = RateLimitException(detail="Too many requests")
        assert exc.detail == "Too many requests"

    def test_exception_retry_after_header(self):
        """Test Retry-After header is set"""
        exc = RateLimitException(retry_after=60)
        assert exc.headers is not None
        assert exc.headers["Retry-After"] == "60"


class TestGlobalRateLimiter:
    """Tests for global rate limiter functions"""

    def test_get_rate_limiter_singleton(self):
        """Test that get_rate_limiter returns singleton"""
        import app.core.rate_limit as rl

        # Reset global state
        rl._rate_limiter = None

        limiter1 = get_rate_limiter()
        limiter2 = get_rate_limiter()

        assert limiter1 is limiter2

    def test_setup_rate_limiting(self):
        """Test setup_rate_limiting function"""
        app = FastAPI()
        config = RateLimitConfig(enabled=True, requests_per_minute=3)

        limiter = setup_rate_limiting(app, config)

        assert limiter is not None
        assert limiter.config.requests_per_minute == 3
        assert limiter.config.enabled is True

    def test_rate_limiting_disabled_by_default(self):
        """Test that rate limiting is disabled by default"""
        app = FastAPI()
        config = RateLimitConfig()  # 默认配置

        limiter = setup_rate_limiting(app, config)

        assert limiter is not None
        assert limiter.config.enabled is False
