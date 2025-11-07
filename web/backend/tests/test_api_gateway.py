"""
API Gateway Tests - Rate limiter, circuit breaker, router, transformer

Task 11: API Gateway and Request Routing
Author: Claude Code
Date: 2025-11-07
"""

import pytest
import time
from datetime import datetime

from app.gateway import (
    RateLimiter,
    RateLimitConfig,
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitBreakerState,
    RequestRouter,
    RouteConfig,
    RequestTransformer,
    ResponseTransformer,
)


class TestRateLimiter:
    """Test rate limiter with token bucket algorithm"""

    def test_rate_limiter_initialization(self):
        """Test rate limiter initialization"""
        config = RateLimitConfig(capacity=100, refill_rate=10.0)
        limiter = RateLimiter(config)

        assert limiter.config.capacity == 100
        assert limiter.config.refill_rate == 10.0

    def test_rate_limiter_allows_requests(self):
        """Test rate limiter allows requests within limit"""
        limiter = RateLimiter()

        # First request should be allowed
        allowed, stats = limiter.is_allowed("client1", 1)
        assert allowed is True
        assert stats["tokens_remaining"] > 0

    def test_rate_limiter_denies_after_limit(self):
        """Test rate limiter denies after tokens exhausted"""
        config = RateLimitConfig(capacity=5, refill_rate=0)  # No refill
        limiter = RateLimiter(config)

        # Consume all tokens
        for _ in range(5):
            allowed, _ = limiter.is_allowed("client1", 1)
            assert allowed is True

        # Next request should be denied
        allowed, stats = limiter.is_allowed("client1", 1)
        assert allowed is False
        assert stats["tokens_remaining"] == 0

    def test_rate_limiter_multiple_clients(self):
        """Test rate limiter handles multiple clients independently"""
        limiter = RateLimiter()

        allowed1, _ = limiter.is_allowed("client1", 1)
        allowed2, _ = limiter.is_allowed("client2", 1)

        assert allowed1 is True
        assert allowed2 is True

    def test_rate_limiter_reset_client(self):
        """Test resetting rate limit for a client"""
        config = RateLimitConfig(capacity=5, refill_rate=0)
        limiter = RateLimiter(config)

        # Consume all tokens
        for _ in range(5):
            limiter.is_allowed("client1", 1)

        # Verify limit exceeded
        allowed, _ = limiter.is_allowed("client1", 1)
        assert allowed is False

        # Reset client
        limiter.reset_client("client1")

        # Should be allowed again
        allowed, _ = limiter.is_allowed("client1", 1)
        assert allowed is True

    def test_rate_limiter_refill(self):
        """Test rate limiter refills tokens over time"""
        config = RateLimitConfig(capacity=10, refill_rate=1.0)
        limiter = RateLimiter(config)

        # Consume some tokens
        for _ in range(8):
            limiter.is_allowed("client1", 1)

        # Wait for refill
        time.sleep(1.1)

        # Should have more tokens
        _, stats = limiter.is_allowed("client1", 0)
        assert stats["tokens_remaining"] > 2

    def test_rate_limiter_stats(self):
        """Test getting rate limiter statistics"""
        limiter = RateLimiter()

        limiter.is_allowed("client1", 1)
        stats = limiter.get_stats("client1")

        assert stats["client_id"] == "client1"
        assert stats["capacity"] == 100
        assert stats["tokens_remaining"] > 0

    def test_rate_limiter_cleanup_stale(self):
        """Test cleaning up stale buckets"""
        config = RateLimitConfig()
        limiter = RateLimiter(config)

        limiter.is_allowed("client1", 1)
        limiter.is_allowed("client2", 1)

        # Cleanup (timeout is very high, so nothing should clean up)
        cleaned = limiter.cleanup_stale_buckets(timeout_seconds=0)
        assert cleaned >= 2


class TestCircuitBreaker:
    """Test circuit breaker pattern"""

    def test_circuit_breaker_initialization(self):
        """Test circuit breaker initialization"""
        cb = CircuitBreaker("test_service")

        assert cb.name == "test_service"
        assert cb.state == CircuitBreakerState.CLOSED

    def test_circuit_breaker_success(self):
        """Test circuit breaker with successful call"""

        def success_func():
            return "success"

        cb = CircuitBreaker("test")
        result = cb.call(success_func)

        assert result["success"] is True
        assert result["result"] == "success"
        assert cb.state == CircuitBreakerState.CLOSED

    def test_circuit_breaker_failure(self):
        """Test circuit breaker with failed calls"""

        def failing_func():
            raise Exception("Service error")

        config = CircuitBreakerConfig(failure_threshold=2, timeout_seconds=1)
        cb = CircuitBreaker("test", config)

        # First failure
        result = cb.call(failing_func)
        assert result["success"] is False

        # Second failure - should open
        result = cb.call(failing_func)
        assert result["success"] is False
        assert cb.state == CircuitBreakerState.OPEN

    def test_circuit_breaker_open_rejects_requests(self):
        """Test circuit breaker in OPEN state rejects requests"""

        def func():
            return "success"

        def failing_func():
            raise Exception("Error")

        config = CircuitBreakerConfig(failure_threshold=1)
        cb = CircuitBreaker("test", config)

        # Trigger open
        cb.call(failing_func)

        # Circuit is now open, should reject
        result = cb.call(func)
        assert result["success"] is False

    def test_circuit_breaker_half_open(self):
        """Test circuit breaker transitions to HALF_OPEN"""

        def failing_func():
            raise Exception("Error")

        def success_func():
            return "success"

        config = CircuitBreakerConfig(
            failure_threshold=1, success_threshold=2, timeout_seconds=0
        )
        cb = CircuitBreaker("test", config)

        # Open the circuit
        cb.call(failing_func)
        assert cb.state == CircuitBreakerState.OPEN

        # Wait for timeout
        time.sleep(0.1)

        # Next call should transition to HALF_OPEN
        result = cb.call(success_func)
        assert cb.state == CircuitBreakerState.HALF_OPEN

        # One more successful call should close (meet threshold of 2)
        result = cb.call(success_func)
        assert cb.state == CircuitBreakerState.CLOSED

    def test_circuit_breaker_reset(self):
        """Test manually resetting circuit breaker"""

        def failing_func():
            raise Exception("Error")

        config = CircuitBreakerConfig(failure_threshold=1)
        cb = CircuitBreaker("test", config)

        # Open circuit
        cb.call(failing_func)
        assert cb.state == CircuitBreakerState.OPEN

        # Reset
        cb.reset()
        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.failure_count == 0

    def test_circuit_breaker_get_state(self):
        """Test getting circuit breaker state"""
        cb = CircuitBreaker("test")
        state = cb.get_state()

        assert state["name"] == "test"
        assert state["state"] == CircuitBreakerState.CLOSED


class TestRequestRouter:
    """Test request router with versioning"""

    def test_router_initialization(self):
        """Test router initialization"""
        router = RequestRouter("/api")

        assert router.base_path == "/api"
        assert len(router.routes) == 0

    def test_router_register_route(self):
        """Test registering a route"""
        router = RequestRouter()

        config = RouteConfig(
            path="/users/{id}",
            methods=["GET"],
            version="v1",
        )
        router.register_route(config)

        assert len(router.routes) > 0

    def test_router_find_route_exact_match(self):
        """Test finding route with exact path match"""
        router = RequestRouter()

        config = RouteConfig(
            path="/users",
            methods=["GET"],
            version="v1",
        )
        router.register_route(config)

        found = router.find_route("/users", "GET", "v1")
        assert found is not None
        assert found.path == "/users"

    def test_router_find_route_pattern_match(self):
        """Test finding route with pattern match"""
        router = RequestRouter()

        config = RouteConfig(
            path="/users/{id}",
            methods=["GET"],
            version="v1",
        )
        router.register_route(config)

        found = router.find_route("/users/123", "GET", "v1")
        assert found is not None

    def test_router_extract_path_params(self):
        """Test extracting path parameters"""
        router = RequestRouter()

        pattern = "/users/{id}/posts/{post_id}"
        path = "/users/123/posts/456"

        params = router.extract_path_params(pattern, path)

        assert params["id"] == "123"
        assert params["post_id"] == "456"

    def test_router_normalize_version(self):
        """Test version normalization"""
        router = RequestRouter()

        assert router.normalize_version("1") == "v1"
        assert router.normalize_version("v1") == "v1"
        assert router.normalize_version("V1") == "v1"
        assert router.normalize_version(None) == "v1"

    def test_router_routes_summary(self):
        """Test getting routes summary"""
        router = RequestRouter()

        router.register_route(RouteConfig(path="/users", methods=["GET"], version="v1"))
        router.register_route(
            RouteConfig(path="/posts", methods=["POST"], version="v2")
        )

        summary = router.get_routes_summary()

        assert summary["total_routes"] == 2
        assert "v1" in summary["versions"]
        assert "v2" in summary["versions"]


class TestRequestTransformer:
    """Test request transformer"""

    def test_transformer_initialization(self):
        """Test transformer initialization"""
        transformer = RequestTransformer()
        assert transformer is not None

    def test_transformer_transform(self):
        """Test transforming a request"""
        transformer = RequestTransformer()

        result = transformer.transform(
            path="/api/v1/users",
            method="GET",
            headers={"User-Agent": "TestClient"},
        )

        assert result["path"] == "/api/v1/users"
        assert result["method"] == "GET"
        assert result["metadata"]["version"] == "v1"

    def test_transformer_extract_version(self):
        """Test extracting version from path"""
        transformer = RequestTransformer()

        version = transformer._extract_version("/api/v2/users")
        assert version == "v2"

    def test_transformer_normalize_path(self):
        """Test path normalization"""
        transformer = RequestTransformer()

        assert transformer._normalize_path("/users/") == "/users"
        assert transformer._normalize_path("users") == "/users"


class TestResponseTransformer:
    """Test response transformer"""

    def test_response_transformer_initialization(self):
        """Test response transformer initialization"""
        transformer = ResponseTransformer()
        assert transformer is not None

    def test_response_transformer_success(self):
        """Test transforming successful response"""
        transformer = ResponseTransformer()

        result = transformer.transform(
            data={"user_id": 123},
            status_code=200,
            correlation_id="abc123",
        )

        assert result["success"] is True
        assert result["status_code"] == 200
        assert result["data"]["user_id"] == 123
        assert result["correlation_id"] == "abc123"

    def test_response_transformer_error(self):
        """Test transforming error response"""
        transformer = ResponseTransformer()

        result = transformer.transform_error(
            status_code=404,
            error_message="User not found",
            error_type="NotFound",
        )

        assert result["success"] is False
        assert result["status_code"] == 404
        assert result["error"] == "User not found"

    def test_response_transformer_list(self):
        """Test transforming paginated list response"""
        transformer = ResponseTransformer()

        result = transformer.transform_list(
            items=[{"id": 1}, {"id": 2}],
            total=10,
            page=1,
            page_size=2,
        )

        assert result["success"] is True
        assert len(result["data"]) == 2
        assert result["pagination"]["total"] == 10
        assert result["pagination"]["total_pages"] == 5


class TestGatewayIntegration:
    """Integration tests for gateway components"""

    def test_gateway_with_rate_limiting_and_routing(self):
        """Test gateway with rate limiting and routing"""
        limiter = RateLimiter()
        router = RequestRouter()

        # Register route
        router.register_route(
            RouteConfig(
                path="/api/v1/users",
                methods=["GET"],
                version="v1",
            )
        )

        # Check rate limit
        allowed, _ = limiter.is_allowed("client1")
        assert allowed is True

        # Find route
        route = router.find_route("/api/v1/users", "GET", "v1")
        assert route is not None

    def test_gateway_with_circuit_breaker(self):
        """Test gateway with circuit breaker"""

        def api_call():
            return {"data": "success"}

        cb = CircuitBreaker("api_service")
        result = cb.call(api_call)

        assert result["success"] is True
        assert cb.state == CircuitBreakerState.CLOSED

    def test_gateway_request_response_cycle(self):
        """Test complete request-response cycle"""
        req_transformer = RequestTransformer()
        resp_transformer = ResponseTransformer()

        # Transform request
        request = req_transformer.transform(
            path="/api/v1/users",
            method="GET",
            headers={"User-Agent": "Test"},
        )

        correlation_id = request["metadata"]["correlation_id"]

        # Transform response
        response = resp_transformer.transform(
            data=[{"id": 1, "name": "User 1"}],
            status_code=200,
            correlation_id=correlation_id,
        )

        assert request["metadata"]["correlation_id"] == response["correlation_id"]
        assert response["success"] is True
