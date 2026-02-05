from contextlib import contextmanager
from types import SimpleNamespace

import pandas as pd

from src.core.transaction import saga_coordinator


class FakePG:
    @contextmanager
    def transaction_scope(self):
        yield object()

    def execute_sql(self, sql_str, params=None):
        return None


class FakeTD:
    def save_data(self, data, classification, table_name):
        return True

    def invalidate_data_by_txn_id(self, table_name, txn_id):
        return None


def _counter_value(counter, **labels):
    return counter.labels(**labels)._value.get()


def _gauge_value(gauge, **labels):
    return gauge.labels(**labels)._value.get()


def _hist_count(histogram, **labels):
    for metric in histogram.collect():
        for sample in metric.samples:
            if sample.name.endswith("_count") and sample.labels == labels:
                return sample.value
    return 0


def _sample_kline():
    return pd.DataFrame(
        {
            "ts": [pd.Timestamp("2026-02-06 09:30:00")],
            "open": [10.0],
            "high": [10.5],
            "low": [9.8],
            "close": [10.2],
            "volume": [1000],
            "amount": [10200.0],
            "symbol": ["SAGA_METRIC"],
            "frequency": ["1m"],
        }
    )


def test_saga_metrics_increment_on_commit():
    coordinator = saga_coordinator.SagaCoordinator(FakePG(), FakeTD())
    classification = SimpleNamespace(value="SAGA_METRIC")

    committed_before = _counter_value(
        saga_coordinator.SAGA_TXN_TOTAL, business_type="SAGA_METRIC", result="committed"
    )
    in_flight_before = _gauge_value(saga_coordinator.SAGA_TXN_IN_FLIGHT, business_type="SAGA_METRIC")
    duration_before = _hist_count(
        saga_coordinator.SAGA_TXN_DURATION, business_type="SAGA_METRIC", result="committed"
    )

    result = coordinator.execute_kline_sync(
        business_id="SAGA_METRIC_1",
        kline_data=_sample_kline(),
        classification=classification,
        table_name="market_data.minute_kline",
        metadata_update_func=lambda _session: None,
    )

    assert result is True
    assert (
        _counter_value(saga_coordinator.SAGA_TXN_TOTAL, business_type="SAGA_METRIC", result="committed")
        == committed_before + 1
    )
    assert _gauge_value(saga_coordinator.SAGA_TXN_IN_FLIGHT, business_type="SAGA_METRIC") == in_flight_before
    assert (
        _hist_count(saga_coordinator.SAGA_TXN_DURATION, business_type="SAGA_METRIC", result="committed")
        == duration_before + 1
    )


def test_saga_metrics_increment_on_rollback():
    coordinator = saga_coordinator.SagaCoordinator(FakePG(), FakeTD())
    classification = SimpleNamespace(value="SAGA_METRIC")

    rolled_before = _counter_value(
        saga_coordinator.SAGA_TXN_TOTAL, business_type="SAGA_METRIC", result="rolled_back"
    )

    def failing_metadata(_session):
        raise RuntimeError("fail metadata")

    result = coordinator.execute_kline_sync(
        business_id="SAGA_METRIC_2",
        kline_data=_sample_kline(),
        classification=classification,
        table_name="market_data.minute_kline",
        metadata_update_func=failing_metadata,
    )

    assert result is False
    assert (
        _counter_value(saga_coordinator.SAGA_TXN_TOTAL, business_type="SAGA_METRIC", result="rolled_back")
        == rolled_before + 1
    )
