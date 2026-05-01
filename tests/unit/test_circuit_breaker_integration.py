import time

import pandas as pd
import pytest

from src.core.data_source.circuit_breaker import CircuitBreaker, CircuitBreakerOpenError
from src.core.data_source.handler import _call_endpoint


class FailingHandler:
    def __init__(self):
        self.fetch_calls = 0

    def fetch(self, **kwargs):
        self.fetch_calls += 1
        raise ValueError("boom")


class FlakyHandler:
    def __init__(self):
        self.fetch_calls = 0

    def fetch(self, **kwargs):
        self.fetch_calls += 1
        if self.fetch_calls == 1:
            raise ValueError("boom")
        return pd.DataFrame([{"symbol": kwargs.get("symbol", "000001"), "close": 10.0}])


class DummyManager:
    def __init__(self, handler):
        self._handler = handler
        self.registry = {
            "demo.endpoint": {
                "handler": None,
                "config": {},
            }
        }
        self.circuit_breakers = {
            "demo.endpoint": CircuitBreaker(
                failure_threshold=1,
                recovery_timeout=60,
                name="demo.endpoint",
            )
        }
        self.failure_records = []
        self.success_records = []

    def _create_handler(self, endpoint_info):
        return self._handler

    def _identify_caller(self):
        return {"service": "unit-test"}

    def _record_success(self, *args):
        self.success_records.append(args)

    def _record_failure(self, *args):
        self.failure_records.append(args)


def test_call_endpoint_uses_circuit_breaker_after_first_failure():
    handler = FailingHandler()
    manager = DummyManager(handler)
    endpoint = {
        "endpoint_name": "demo.endpoint",
        "source_type": "akshare",
        "config": {"source_type": "akshare"},
    }

    with pytest.raises(ValueError, match="boom"):
        _call_endpoint(manager, endpoint, symbol="000001")

    with pytest.raises(CircuitBreakerOpenError):
        _call_endpoint(manager, endpoint, symbol="000001")

    assert handler.fetch_calls == 1
    assert len(manager.failure_records) == 2
    assert manager.success_records == []


def test_call_endpoint_recovers_after_circuit_breaker_timeout():
    handler = FlakyHandler()
    manager = DummyManager(handler)
    manager.circuit_breakers["demo.endpoint"] = CircuitBreaker(
        failure_threshold=1,
        recovery_timeout=0.01,
        name="demo.endpoint",
    )
    endpoint = {
        "endpoint_name": "demo.endpoint",
        "source_type": "akshare",
        "config": {"source_type": "akshare"},
    }

    with pytest.raises(ValueError, match="boom"):
        _call_endpoint(manager, endpoint, symbol="000001")

    with pytest.raises(CircuitBreakerOpenError):
        _call_endpoint(manager, endpoint, symbol="000001")

    time.sleep(0.02)
    data = _call_endpoint(manager, endpoint, symbol="000001")

    assert not data.empty
    assert handler.fetch_calls == 2
    assert len(manager.failure_records) == 2
    assert len(manager.success_records) == 1
