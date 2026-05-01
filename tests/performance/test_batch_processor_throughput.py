import time

import pandas as pd

from src.core.data_source.batch_processor import BatchProcessor
from src.governance.core.fetcher_bridge import RoutePolicy


class ThroughputFetcher:
    def __init__(self):
        self.fetch_calls = []

    def resolve_endpoint(self, data_category, policy, source_id=None, symbol=None):
        return {"endpoint_name": "throughput-endpoint"}

    def fetch_kline(
        self,
        symbol,
        start_date,
        end_date,
        adjust="qfq",
        data_category="DAILY_KLINE",
        policy=RoutePolicy.SMART_ROUTING,
        source_id=None,
        endpoint_info=None,
    ):
        self.fetch_calls.append(symbol)
        time.sleep(0.02)
        return pd.DataFrame({"symbol": [symbol], "close": [10.0]})


def test_batch_processor_improves_throughput_over_serial_stub_workload():
    symbols = [f"{index:06d}" for index in range(60)]
    fetcher = ThroughputFetcher()
    processor = BatchProcessor(max_workers=10, timeout=1.0)

    batch_started = time.perf_counter()
    batch_result = processor.fetch_batch_kline(
        fetcher,
        symbols=symbols,
        start_date="20240101",
        end_date="20240105",
    )
    batch_elapsed = time.perf_counter() - batch_started

    serial_started = time.perf_counter()
    serial_results = {}
    for symbol in symbols:
        serial_results[symbol] = fetcher.fetch_kline(
            symbol=symbol,
            start_date="20240101",
            end_date="20240105",
        )
    serial_elapsed = time.perf_counter() - serial_started

    processor.shutdown(wait=False)

    assert batch_result["errors"] == {}
    assert len(batch_result["data"]) == 60
    assert len(serial_results) == 60
    assert batch_elapsed * 2 < serial_elapsed
