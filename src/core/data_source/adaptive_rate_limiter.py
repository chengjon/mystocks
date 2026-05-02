from __future__ import annotations

import threading
import time
from typing import Callable


class AdaptiveRateLimiter:
    """Adaptive request throttling driven by recent error-rate signals."""

    def __init__(
        self,
        initial_rate: int = 10,
        min_rate: int = 1,
        max_rate: int = 100,
        adjustment_factor: float = 0.1,
        time_fn: Callable[[], float] | None = None,
        sleep_fn: Callable[[float], None] | None = None,
    ) -> None:
        if min_rate <= 0:
            raise ValueError("min_rate must be positive")
        if max_rate < min_rate:
            raise ValueError("max_rate must be greater than or equal to min_rate")
        if adjustment_factor <= 0:
            raise ValueError("adjustment_factor must be positive")

        self.min_rate = min_rate
        self.max_rate = max_rate
        self.current_rate = max(min(initial_rate, max_rate), min_rate)
        self.adjustment_factor = adjustment_factor
        self.error_rate = 0.0
        self.last_call_time: float | None = None
        self._time_fn = time_fn or time.time
        self._sleep_fn = sleep_fn or time.sleep
        self._lock = threading.RLock()

    def acquire(self, permits: int = 1) -> None:
        if permits <= 0:
            raise ValueError("permits must be positive")

        with self._lock:
            self._adjust_rate_locked()

            now = self._time_fn()
            if self.last_call_time is not None:
                elapsed = now - self.last_call_time
                min_interval = permits / float(self.current_rate)
                if elapsed < min_interval:
                    self._sleep_fn(min_interval - elapsed)
                    now = self._time_fn()

            self.last_call_time = now

    def record_error(self, delta: float = 0.05) -> None:
        with self._lock:
            self.error_rate = min(1.0, self.error_rate + max(delta, 0.0))

    def record_success(self, delta: float = 0.01) -> None:
        with self._lock:
            self.error_rate = max(0.0, self.error_rate - max(delta, 0.0))

    def _adjust_rate_locked(self) -> None:
        if self.error_rate > 0.1:
            adjusted_rate = int(self.current_rate * (1 - self.adjustment_factor))
            self.current_rate = max(self.min_rate, adjusted_rate)
        elif self.error_rate < 0.01:
            adjusted_rate = int(self.current_rate * (1 + self.adjustment_factor))
            self.current_rate = min(self.max_rate, max(self.min_rate, adjusted_rate))
