"""Unit tests for the current signal monitoring contracts."""

from types import SimpleNamespace
from unittest.mock import patch

from src.monitoring import signal_metrics
from src.monitoring.signal_decorator import (
    MonitoredStrategyExecutor,
    SignalMonitoringContext,
    monitored_strategy,
    record_signal_result,
)


class DummyExecutor:
    def __init__(self, execute_result=None, execute_symbol_result=None, gpu_used=False):
        self.name = "dummy-executor"
        self.strategy_version = "v1"
        self._gpu_used = gpu_used
        self._execute_result = execute_result if execute_result is not None else {"ok": True}
        self._execute_symbol_result = (
            execute_symbol_result if execute_symbol_result is not None else SimpleNamespace(signals=[])
        )
        self.execute_calls = []
        self.execute_symbol_calls = []

    def execute(self, symbols, start_date=None, end_date=None, **kwargs):
        self.execute_calls.append(
            {"symbols": symbols, "start_date": start_date, "end_date": end_date, "kwargs": kwargs}
        )
        return self._execute_result

    def execute_symbol(self, symbol, data=None, **kwargs):
        self.execute_symbol_calls.append({"symbol": symbol, "data": data, "kwargs": kwargs})
        return self._execute_symbol_result

    def helper(self):
        return "delegated-helper"


def make_signal(signal_type: str, symbol: str):
    return SimpleNamespace(side=SimpleNamespace(value=signal_type), symbol=symbol)


class TestSignalMetrics:
    def test_metrics_module_exports_current_metric_definitions(self):
        assert hasattr(signal_metrics, "SIGNAL_GENERATION_TOTAL")
        assert hasattr(signal_metrics, "SIGNAL_LATENCY_SECONDS")
        assert hasattr(signal_metrics, "SIGNAL_ACCURACY_PERCENTAGE")
        assert hasattr(signal_metrics, "SIGNAL_SUCCESS_RATE")
        assert hasattr(signal_metrics, "SIGNAL_PROFIT_RATIO")
        assert hasattr(signal_metrics, "ACTIVE_SIGNALS_COUNT")
        assert hasattr(signal_metrics, "SIGNAL_PUSH_TOTAL")
        assert hasattr(signal_metrics, "SIGNAL_PUSH_LATENCY_SECONDS")
        assert hasattr(signal_metrics, "STRATEGY_HEALTH_STATUS")

    def test_metric_helper_functions_accept_valid_payloads(self):
        signal_metrics.record_signal_generation(
            strategy_id="test_strategy", signal_type="BUY", symbol="600519", status="generated"
        )
        signal_metrics.record_signal_latency(strategy_id="test_strategy", latency_seconds=0.045, indicator_count=3)
        signal_metrics.update_signal_accuracy("test_strategy", "BUY", 75.5)
        signal_metrics.update_signal_success_rate("test_strategy", "BUY", 82.0)
        signal_metrics.update_profit_ratio("test_strategy", "1d", 65.0)
        signal_metrics.update_active_signals_count("test_strategy", "600519", "BUY", 5)
        signal_metrics.record_signal_push("websocket", "success")
        signal_metrics.record_push_latency("websocket", 0.12)
        signal_metrics.update_strategy_health("test_strategy", 1)


class TestSignalMonitoringContext:
    def test_context_initialization(self):
        context = SignalMonitoringContext("test_strategy")

        assert context.strategy_id == "test_strategy"
        assert context.signals_generated == {"BUY": 0, "SELL": 0, "HOLD": 0}
        assert context.signals_by_symbol == {}
        assert context.push_results == {}
        assert context.errors == []

    def test_record_signal_push_and_summary(self):
        context = SignalMonitoringContext("test_strategy")

        context.record_signal("BUY", "600519")
        context.record_signal("BUY", "600519")
        context.record_signal("SELL", "000001")
        context.record_push("websocket", True, 45.5)
        context.record_push("email", False, 120.0)
        context.record_gpu_usage(125.5)

        summary = context.get_summary()

        assert context.signals_generated["BUY"] == 2
        assert context.signals_generated["SELL"] == 1
        assert context.signals_by_symbol["600519"]["BUY"] == 2
        assert context.push_results["websocket"]["success"] == 1
        assert context.push_results["email"]["failed"] == 1
        assert summary["strategy_id"] == "test_strategy"
        assert summary["gpu_used"] is True
        assert summary["gpu_latency_ms"] == 125.5
        assert summary["total_signals"] == 3
        assert summary["unique_symbols"] == 2

    def test_update_gauges_updates_health_and_active_signal_counts(self):
        context = SignalMonitoringContext("test_strategy")
        context.record_signal("BUY", "600519")
        context.record_signal("SELL", "000001")

        with (
            patch("src.monitoring.signal_decorator.update_strategy_health") as health_mock,
            patch("src.monitoring.signal_decorator.update_active_signals_count") as active_mock,
        ):
            context.update_gauges()

        health_mock.assert_called_once_with("test_strategy", 1)
        active_mock.assert_any_call(strategy_id="test_strategy", symbol="600519", signal_type="BUY", count=1)
        active_mock.assert_any_call(strategy_id="test_strategy", symbol="000001", signal_type="SELL", count=1)

    def test_update_gauges_marks_strategy_degraded_when_errors_exist(self):
        context = SignalMonitoringContext("test_strategy")
        context.errors.append("push failed")

        with patch("src.monitoring.signal_decorator.update_strategy_health") as health_mock:
            context.update_gauges()

        health_mock.assert_called_once_with("test_strategy", 0)


class TestMonitoredStrategyExecutor:
    def test_monitored_strategy_wraps_executor_and_preserves_attrs(self):
        executor = DummyExecutor()

        monitored = monitored_strategy(executor)

        assert isinstance(monitored, MonitoredStrategyExecutor)
        assert monitored._executor is executor
        assert monitored._strategy_id == "default"
        assert monitored.name == "dummy-executor"
        assert monitored.strategy_version == "v1"
        assert monitored.helper() == "delegated-helper"

    def test_execute_adds_monitoring_summary_to_dict_results(self):
        executor = DummyExecutor(execute_result={"payload": "ok"})
        monitored = MonitoredStrategyExecutor(executor, strategy_id="test_strategy")

        result = monitored.execute(["600519"], start_date="2026-01-01", end_date="2026-01-31", dry_run=True)

        assert result["payload"] == "ok"
        assert result["_monitoring"]["strategy_id"] == "test_strategy"
        assert result["_monitoring"]["total_signals"] == 0
        assert result["_monitoring"]["gpu_used"] is False
        assert executor.execute_calls == [
            {
                "symbols": ["600519"],
                "start_date": "2026-01-01",
                "end_date": "2026-01-31",
                "kwargs": {"dry_run": True},
            }
        ]

    def test_execute_tracks_object_signals_and_gpu_usage(self):
        result = SimpleNamespace(
            signals=[make_signal("BUY", "600519"), make_signal("SELL", "000001")],
            _monitoring=None,
        )
        executor = DummyExecutor(execute_result=result, gpu_used=True)
        monitored = MonitoredStrategyExecutor(executor, strategy_id="test_strategy")

        monitored_result = monitored.execute(["600519", "000001"])

        assert monitored_result._monitoring["strategy_id"] == "test_strategy"
        assert monitored_result._monitoring["total_signals"] == 2
        assert monitored_result._monitoring["signals_by_type"]["BUY"] == 1
        assert monitored_result._monitoring["signals_by_type"]["SELL"] == 1
        assert monitored_result._monitoring["unique_symbols"] == 2
        assert monitored_result._monitoring["gpu_used"] is True

    def test_execute_symbol_records_latency_and_updates_gauges(self):
        result = SimpleNamespace(signals=[make_signal("BUY", "600519")])
        executor = DummyExecutor(execute_symbol_result=result)
        monitored = MonitoredStrategyExecutor(executor, strategy_id="test_strategy")

        with (
            patch("src.monitoring.signal_decorator.record_signal_latency") as latency_mock,
            patch.object(SignalMonitoringContext, "update_gauges") as update_mock,
        ):
            monitored_result = monitored.execute_symbol("600519", data={"close": [1, 2, 3]}, dry_run=True)

        assert monitored_result is result
        assert executor.execute_symbol_calls == [
            {"symbol": "600519", "data": {"close": [1, 2, 3]}, "kwargs": {"dry_run": True}}
        ]
        latency_mock.assert_called_once()
        assert latency_mock.call_args.kwargs["strategy_id"] == "test_strategy"
        assert latency_mock.call_args.kwargs["indicator_count"] == 1
        assert latency_mock.call_args.kwargs["latency_seconds"] >= 0
        update_mock.assert_called_once()

    def test_get_monitoring_summary_before_execution_returns_no_execution(self):
        monitored = MonitoredStrategyExecutor(DummyExecutor(), strategy_id="test_strategy")

        assert monitored.get_monitoring_summary() == {"status": "no_execution", "strategy_id": "test_strategy"}

    def test_record_push_result_updates_active_context(self):
        executor = DummyExecutor(execute_result={"payload": "ok"})
        monitored = MonitoredStrategyExecutor(executor, strategy_id="test_strategy")
        monitored.execute(["600519"])

        monitored.record_push_result("websocket", True, 12.5)
        summary = monitored.get_monitoring_summary()

        assert summary["push_results"]["websocket"]["success"] == 1
        assert summary["push_results"]["websocket"]["failed"] == 0
        assert summary["push_results"]["websocket"]["total_latency_ms"] == 12.5


class TestRecordSignalResult:
    def test_record_signal_result_updates_success_and_profit_metrics_for_profitable_execution(self):
        with (
            patch("src.monitoring.signal_decorator.update_signal_success_rate") as success_mock,
            patch("src.monitoring.signal_decorator.update_profit_ratio") as profit_mock,
        ):
            record_signal_result(
                strategy_id="test",
                signal_id="sig_001",
                executed=True,
                profit_loss=100.5,
                execution_time_ms=45.2,
            )

        success_mock.assert_called_once_with("test", "BUY", 100.0)
        profit_mock.assert_called_once_with("test", "1d", 100.0)

    def test_record_signal_result_updates_failed_execution_without_profit_metric(self):
        with (
            patch("src.monitoring.signal_decorator.update_signal_success_rate") as success_mock,
            patch("src.monitoring.signal_decorator.update_profit_ratio") as profit_mock,
        ):
            record_signal_result(
                strategy_id="test",
                signal_id="sig_002",
                executed=False,
                profit_loss=None,
                execution_time_ms=10.0,
            )

        success_mock.assert_called_once_with("test", "BUY", 0.0)
        profit_mock.assert_not_called()
