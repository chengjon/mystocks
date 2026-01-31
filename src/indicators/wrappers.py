import time
from typing import Any, Dict

from src.indicators.base import StreamingIndicator
from src.monitoring.indicator_metrics import CALCULATION_REQUESTS, STREAMING_LATENCY


class MonitoredStreamingIndicator(StreamingIndicator):
    """
    Proxy class that adds monitoring to any StreamingIndicator.
    """

    def __init__(self, inner: StreamingIndicator, indicator_id: str):
        self._inner = inner
        self._id = indicator_id

    def update(self, bar: Dict[str, float]) -> float:
        start = time.perf_counter()
        try:
            result = self._inner.update(bar)

            # Record metrics
            duration = time.perf_counter() - start
            STREAMING_LATENCY.labels(indicator_id=self._id).observe(duration)

            # Use 1/100 sampling for counters to avoid high cardinality overhead on high frequency?
            # For now, record all.
            # CALCULATION_REQUESTS.labels(indicator_id=self._id, mode='streaming', status='success').inc()

            return result
        except Exception as e:
            CALCULATION_REQUESTS.labels(indicator_id=self._id, mode="streaming", status="error").inc()
            raise e

    def snapshot(self) -> Dict[str, Any]:
        return self._inner.snapshot()

    def load_snapshot(self, state: Dict[str, Any]):
        self._inner.load_snapshot(state)

    @property
    def name(self) -> str:
        return self._inner.name
