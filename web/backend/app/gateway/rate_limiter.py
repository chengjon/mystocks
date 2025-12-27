"""
Rate Limiter - Token Bucket Algorithm Implementation

Provides rate limiting using the token bucket algorithm.
Each client/endpoint has a bucket that refills at a specified rate.
Requests are allowed only if sufficient tokens are available.

Task 11: API Gateway and Request Routing
Author: Claude Code
Date: 2025-11-07
"""

from dataclasses import dataclass
from typing import Dict, Optional, Tuple
import time
import structlog

logger = structlog.get_logger()


@dataclass
class RateLimitConfig:
    """Rate limiting configuration"""

    capacity: int = 100  # Maximum tokens in bucket
    refill_rate: float = 10.0  # Tokens per second
    window_size: int = 60  # Time window in seconds


class RateLimiter:
    """Token bucket rate limiter"""

    def __init__(self, config: Optional[RateLimitConfig] = None):
        """Initialize rate limiter

        Args:
            config: Rate limit configuration
        """
        self.config = config or RateLimitConfig()
        self.buckets: Dict[str, Dict] = {}
        logger.info("✅ Rate Limiter initialized", config=self.config)

    def _get_bucket(self, client_id: str) -> Dict:
        """Get or create bucket for client

        Args:
            client_id: Unique client identifier

        Returns:
            Bucket state dictionary
        """
        if client_id not in self.buckets:
            self.buckets[client_id] = {
                "tokens": self.config.capacity,
                "last_refill": time.time(),
            }
        return self.buckets[client_id]

    def _refill_bucket(self, bucket: Dict) -> None:
        """Refill bucket tokens based on elapsed time

        Args:
            bucket: Bucket state dictionary
        """
        now = time.time()
        elapsed = now - bucket["last_refill"]

        # Calculate tokens to add
        tokens_to_add = elapsed * self.config.refill_rate

        # Update bucket
        bucket["tokens"] = min(self.config.capacity, bucket["tokens"] + tokens_to_add)
        bucket["last_refill"] = now

    def is_allowed(self, client_id: str, tokens_required: int = 1) -> Tuple[bool, Dict]:
        """Check if request is allowed and consume tokens if allowed

        Args:
            client_id: Unique client identifier
            tokens_required: Number of tokens required for this request

        Returns:
            Tuple of (allowed, stats) where stats contains remaining tokens and reset time
        """
        bucket = self._get_bucket(client_id)
        self._refill_bucket(bucket)

        allowed = bucket["tokens"] >= tokens_required

        if allowed:
            bucket["tokens"] -= tokens_required
            logger.debug(
                "✅ Rate limit check passed",
                client_id=client_id,
                tokens_remaining=int(bucket["tokens"]),
            )
        else:
            logger.warning(
                "⚠️ Rate limit exceeded",
                client_id=client_id,
                tokens_needed=tokens_required,
                tokens_available=int(bucket["tokens"]),
            )

        # Calculate reset time (when bucket will be full again)
        tokens_to_full = max(0, self.config.capacity - bucket["tokens"])
        if self.config.refill_rate > 0:
            reset_time = bucket["last_refill"] + (tokens_to_full / self.config.refill_rate)
        else:
            reset_time = float("inf")  # Never refill if rate is 0

        # Calculate retry_after, handling infinity case
        if reset_time == float("inf"):
            retry_after = None  # Never refills
        else:
            retry_after = max(0, int(reset_time - time.time()) + 1)

        stats = {
            "allowed": allowed,
            "tokens_remaining": int(bucket["tokens"]),
            "tokens_required": tokens_required,
            "reset_time": reset_time,
            "retry_after": retry_after,
        }

        return allowed, stats

    def reset_client(self, client_id: str) -> None:
        """Reset rate limit for a client

        Args:
            client_id: Unique client identifier
        """
        if client_id in self.buckets:
            self.buckets[client_id] = {
                "tokens": self.config.capacity,
                "last_refill": time.time(),
            }
            logger.info("✅ Client rate limit reset", client_id=client_id)

    def get_stats(self, client_id: str) -> Dict:
        """Get rate limit statistics for a client

        Args:
            client_id: Unique client identifier

        Returns:
            Statistics dictionary
        """
        bucket = self._get_bucket(client_id)
        self._refill_bucket(bucket)

        return {
            "client_id": client_id,
            "capacity": self.config.capacity,
            "refill_rate": self.config.refill_rate,
            "tokens_remaining": int(bucket["tokens"]),
            "last_refill": bucket["last_refill"],
        }

    def cleanup_stale_buckets(self, timeout_seconds: int = 3600) -> int:
        """Clean up buckets that haven't been used recently

        Args:
            timeout_seconds: Timeout for stale buckets (default: 1 hour)

        Returns:
            Number of buckets cleaned up
        """
        now = time.time()
        stale_clients = [
            client_id for client_id, bucket in self.buckets.items() if now - bucket["last_refill"] > timeout_seconds
        ]

        for client_id in stale_clients:
            del self.buckets[client_id]

        if stale_clients:
            logger.info(
                "✅ Cleaned up stale buckets",
                count=len(stale_clients),
                timeout_seconds=timeout_seconds,
            )

        return len(stale_clients)

    def get_all_stats(self) -> Dict:
        """Get statistics for all active clients

        Returns:
            Dictionary with stats for each client
        """
        stats = {}
        for client_id in self.buckets:
            stats[client_id] = self.get_stats(client_id)
        return stats
