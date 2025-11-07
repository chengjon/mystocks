"""
Circuit Breaker - Fail-Safe Pattern Implementation

Implements the circuit breaker pattern to protect against cascading failures.
States: CLOSED (normal) -> OPEN (failing) -> HALF_OPEN (testing) -> CLOSED

Task 11: API Gateway and Request Routing
Author: Claude Code
Date: 2025-11-07
"""

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Optional, Any, Dict
from datetime import datetime, timedelta
import time
import structlog

logger = structlog.get_logger()


class CircuitBreakerState(str, Enum):
    """Circuit breaker states"""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Rejecting requests
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration"""

    failure_threshold: int = 5  # Failures before opening
    success_threshold: int = 2  # Successes in half-open to close
    timeout_seconds: int = 60  # Time to wait before trying again


class CircuitBreaker:
    """Circuit breaker for protecting service endpoints"""

    def __init__(
        self,
        name: str,
        config: Optional[CircuitBreakerConfig] = None,
    ):
        """Initialize circuit breaker

        Args:
            name: Name/identifier for this breaker
            config: Circuit breaker configuration
        """
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[float] = None
        self.open_time: Optional[float] = None

        logger.info("✅ Circuit Breaker initialized", name=name, config=self.config)

    def call(self, func: Callable, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Execute function with circuit breaker protection

        Args:
            func: Function to execute
            *args: Positional arguments for function
            **kwargs: Keyword arguments for function

        Returns:
            Dictionary with result and metadata
        """
        if self.state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitBreakerState.HALF_OPEN
                self.success_count = 0
                logger.info(
                    "🔄 Circuit breaker transitioning to HALF_OPEN",
                    name=self.name,
                )
            else:
                return {
                    "success": False,
                    "state": self.state,
                    "error": "Circuit breaker is OPEN",
                }

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return {
                "success": True,
                "result": result,
                "state": self.state,
            }

        except Exception as e:
            self._on_failure()
            return {
                "success": False,
                "state": self.state,
                "error": str(e),
            }

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset

        Returns:
            True if ready to attempt reset
        """
        if self.open_time is None:
            return False

        elapsed = time.time() - self.open_time
        return elapsed >= self.config.timeout_seconds

    def _on_success(self) -> None:
        """Handle successful call"""
        self.failure_count = 0

        if self.state == CircuitBreakerState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                self.state = CircuitBreakerState.CLOSED
                self.open_time = None
                logger.info(
                    "✅ Circuit breaker CLOSED (recovered)",
                    name=self.name,
                )

    def _on_failure(self) -> None:
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.state == CircuitBreakerState.HALF_OPEN:
            # Immediately reopen if failing in half-open state
            self.state = CircuitBreakerState.OPEN
            self.open_time = time.time()
            self.success_count = 0
            logger.warning(
                "🔴 Circuit breaker OPEN (failed in HALF_OPEN)",
                name=self.name,
            )

        elif self.failure_count >= self.config.failure_threshold:
            self.state = CircuitBreakerState.OPEN
            self.open_time = time.time()
            logger.warning(
                "🔴 Circuit breaker OPEN (threshold exceeded)",
                name=self.name,
                failure_count=self.failure_count,
            )

    def reset(self) -> None:
        """Manually reset circuit breaker"""
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.open_time = None
        logger.info("🔄 Circuit breaker manually reset", name=self.name)

    def get_state(self) -> Dict[str, Any]:
        """Get current circuit breaker state

        Returns:
            State dictionary
        """
        return {
            "name": self.name,
            "state": self.state,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure_time": self.last_failure_time,
            "open_time": self.open_time,
        }


class CircuitBreakerManager:
    """Manager for multiple circuit breakers"""

    def __init__(self):
        """Initialize circuit breaker manager"""
        self.breakers: Dict[str, CircuitBreaker] = {}
        logger.info("✅ Circuit Breaker Manager initialized")

    def register(
        self,
        name: str,
        config: Optional[CircuitBreakerConfig] = None,
    ) -> CircuitBreaker:
        """Register a new circuit breaker

        Args:
            name: Unique name for the breaker
            config: Configuration for the breaker

        Returns:
            The created circuit breaker
        """
        if name in self.breakers:
            logger.warning("⚠️ Circuit breaker already exists", name=name)
            return self.breakers[name]

        breaker = CircuitBreaker(name, config)
        self.breakers[name] = breaker
        return breaker

    def get(self, name: str) -> Optional[CircuitBreaker]:
        """Get a circuit breaker by name

        Args:
            name: Name of the breaker

        Returns:
            Circuit breaker or None if not found
        """
        return self.breakers.get(name)

    def call(
        self, name: str, func: Callable, *args: Any, **kwargs: Any
    ) -> Dict[str, Any]:
        """Call a function through a registered circuit breaker

        Args:
            name: Name of the breaker
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Result dictionary
        """
        breaker = self.get(name)
        if breaker is None:
            logger.error("Circuit breaker not found", name=name)
            return {
                "success": False,
                "error": f"Circuit breaker '{name}' not found",
            }

        return breaker.call(func, *args, **kwargs)

    def get_all_states(self) -> Dict[str, Dict[str, Any]]:
        """Get states of all circuit breakers

        Returns:
            Dictionary with state for each breaker
        """
        return {name: breaker.get_state() for name, breaker in self.breakers.items()}

    def reset_all(self) -> None:
        """Reset all circuit breakers"""
        for breaker in self.breakers.values():
            breaker.reset()
        logger.info("✅ All circuit breakers reset")
