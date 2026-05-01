import time

import pandas as pd

from src.core.data_source.batch_processor import BatchProcessor
from src.governance.core.fetcher_bridge import RoutePolicy


class StubBatchFetcher:
    def __init__(self):
        self.resolve_calls = []
        self.fetch_calls = []

    def resolve_endpoint(self, data_category, policy, source_id=None, symbol=None):
        self.resolve_calls.append(
            {
                "symbol": symbol,
                "data_category": data_category,
                "policy": policy,
                "source_id": source_id,
            }
        )

        if symbol == "000003":
            return {"endpoint_name": "backup"}

        return {"endpoint_name": "primary"}

    def fetch_kline(
        self,
        symbol,
        start_date,
        end_date,
        adjust="qfq",
        data_category="DAILY_KLINE",
        policy=RoutePolicy.SMART_ROUTING,
        source_id=None,
    ):
        self.fetch_calls.append(
            {
                "symbol": symbol,
                "start_date": start_date,
                "end_date": end_date,
                "adjust": adjust,
                "data_category": data_category,
                "policy": policy,
                "source_id": source_id,
            }
        )

        if symbol == "000004":
            raise ValueError("boom")

        return pd.DataFrame({"close": [10, 11, 12]})


def test_batch_processor_propagates_request_context_and_isolates_failures():
    processor = BatchProcessor(max_workers=4, timeout=0.1)
    fetcher = StubBatchFetcher()

    result = processor.fetch_batch_kline(
        fetcher,
        symbols=["000001", "000002", "000003", "000004"],
        start_date="20240101",
        end_date="20240105",
        data_category="WEEKLY_KLINE",
        policy=RoutePolicy.SPECIFIC_SOURCE,
        source_id="tushare",
    )

    processor.shutdown(wait=False)

    assert set(result["data"]) == {"000001", "000002", "000003"}
    assert result["errors"] == {"000004": "boom"}
    assert {call["symbol"] for call in fetcher.resolve_calls} == {"000001", "000002", "000003", "000004"}
    assert all(call["data_category"] == "WEEKLY_KLINE" for call in fetcher.fetch_calls)
    assert all(call["policy"] == RoutePolicy.SPECIFIC_SOURCE for call in fetcher.fetch_calls)
    assert all(call["source_id"] == "tushare" for call in fetcher.fetch_calls)


def test_batch_processor_marks_timeout_without_blocking_fast_symbols():
    class SlowFetcher(StubBatchFetcher):
        def fetch_kline(
            self,
            symbol,
            start_date,
            end_date,
            adjust="qfq",
            data_category="DAILY_KLINE",
            policy=RoutePolicy.SMART_ROUTING,
            source_id=None,
        ):
            if symbol == "000002":
                time.sleep(0.15)

            return super().fetch_kline(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                adjust=adjust,
                data_category=data_category,
                policy=policy,
                source_id=source_id,
            )

    processor = BatchProcessor(max_workers=2, timeout=0.05)
    fetcher = SlowFetcher()

    start = time.perf_counter()
    result = processor.fetch_batch_kline(
        fetcher,
        symbols=["000001", "000002"],
        start_date="20240101",
        end_date="20240105",
    )
    elapsed = time.perf_counter() - start

    processor.shutdown(wait=False)

    assert "000001" in result["data"]
    assert result["errors"] == {"000002": "Timed out after 0.05s"}
    assert elapsed < 0.15


def test_batch_processor_shutdown_is_graceful():
    processor = BatchProcessor(max_workers=2, timeout=0.1)

    processor.shutdown(wait=False)

    assert processor.executor._shutdown is True
