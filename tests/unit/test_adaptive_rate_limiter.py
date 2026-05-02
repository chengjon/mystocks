from __future__ import annotations

import pytest

from src.core.data_source.adaptive_rate_limiter import AdaptiveRateLimiter


def test_initial_configuration_is_exposed():
    limiter = AdaptiveRateLimiter(initial_rate=12, min_rate=3, max_rate=24, adjustment_factor=0.2)

    assert limiter.current_rate == 12
    assert limiter.min_rate == 3
    assert limiter.max_rate == 24
    assert limiter.adjustment_factor == 0.2
    assert limiter.error_rate == 0.0


def test_high_error_rate_reduces_rate_down_to_minimum():
    limiter = AdaptiveRateLimiter(initial_rate=10, min_rate=4, max_rate=20, adjustment_factor=0.5)

    limiter.record_error(0.2)
    limiter.acquire()
    assert limiter.current_rate == 5

    limiter.record_error(0.2)
    limiter.acquire()
    assert limiter.current_rate == 4


def test_low_error_rate_increases_rate_up_to_maximum():
    limiter = AdaptiveRateLimiter(initial_rate=10, min_rate=4, max_rate=12, adjustment_factor=0.25)
    limiter.current_rate = 8

    limiter.acquire()
    assert limiter.current_rate == 10

    limiter.acquire()
    assert limiter.current_rate == 12


def test_acquire_uses_current_rate_to_throttle_permits():
    sleep_calls: list[float] = []
    now = {"value": 0.0}

    def fake_time() -> float:
        return now["value"]

    def fake_sleep(seconds: float) -> None:
        sleep_calls.append(seconds)
        now["value"] += seconds

    limiter = AdaptiveRateLimiter(initial_rate=10, time_fn=fake_time, sleep_fn=fake_sleep)
    limiter.error_rate = 0.05

    limiter.acquire()
    now["value"] = 0.05
    limiter.acquire()
    now["value"] = 0.10
    limiter.acquire(permits=2)

    assert sleep_calls == [0.05, 0.2]


def test_error_rate_is_clamped_between_zero_and_one():
    limiter = AdaptiveRateLimiter(initial_rate=10)

    limiter.record_error(2.0)
    assert limiter.error_rate == 1.0

    limiter.record_success(0.7)
    assert limiter.error_rate == pytest.approx(0.3)

    limiter.record_success(1.0)
    assert limiter.error_rate == 0.0
