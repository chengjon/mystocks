"""
Unit tests for Signal Monitoring Module

信号监控模块单元测试

验证：
1. signal_metrics.py - 9个指标定义和辅助函数
2. signal_decorator.py - 装饰器和监控上下文
"""

import os
import sys
import time
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestSignalMetrics:
    """Test cases for signal_metrics.py"""

    def test_metrics_module_import(self):
        """Test that signal_metrics module can be imported"""
        try:
            from src.monitoring import signal_metrics

            assert hasattr(signal_metrics, "SIGNAL_GENERATION_TOTAL")
            assert hasattr(signal_metrics, "SIGNAL_LATENCY_SECONDS")
            assert hasattr(signal_metrics, "SIGNAL_ACCURACY_PERCENTAGE")
            assert hasattr(signal_metrics, "SIGNAL_SUCCESS_RATE")
            assert hasattr(signal_metrics, "SIGNAL_PROFIT_RATIO")
            assert hasattr(signal_metrics, "ACTIVE_SIGNALS_COUNT")
            assert hasattr(signal_metrics, "SIGNAL_PUSH_TOTAL")
            assert hasattr(signal_metrics, "SIGNAL_PUSH_LATENCY_SECONDS")
            assert hasattr(signal_metrics, "STRATEGY_HEALTH_STATUS")
        except ImportError:
            pytest.skip("signal_metrics module not available")

    def test_record_signal_generation_function(self):
        """Test record_signal_generation helper function"""
        try:
            from src.monitoring.signal_metrics import record_signal_generation

            # Should not raise exception (metrics are recorded internally)
            record_signal_generation(
                strategy_id="test_strategy", signal_type="BUY", symbol="600519", status="generated"
            )
        except ImportError:
            pytest.skip("signal_metrics module not available")

    def test_record_signal_latency_function(self):
        """Test record_signal_latency helper function"""
        try:
            from src.monitoring.signal_metrics import record_signal_latency

            record_signal_latency(strategy_id="test_strategy", latency_seconds=0.045, indicator_count=3)
        except ImportError:
            pytest.skip("signal_metrics module not available")

    def test_update_functions(self):
        """Test all update helper functions"""
        try:
            from src.monitoring.signal_metrics import (
                update_active_signals_count,
                update_profit_ratio,
                update_signal_accuracy,
                update_signal_success_rate,
                update_strategy_health,
            )

            # These should not raise exceptions
            update_signal_accuracy("test_strategy", "BUY", 75.5)
            update_signal_success_rate("test_strategy", "BUY", 82.0)
            update_profit_ratio("test_strategy", "1d", 65.0)
            update_active_signals_count("test_strategy", "600519", "BUY", 5)
            update_strategy_health("test_strategy", 1)
        except ImportError:
            pytest.skip("signal_metrics module not available")


class TestSignalMonitoringContext:
    """Test cases for SignalMonitoringContext"""

    def test_context_initialization(self):
        """Test context initialization"""
        from src.monitoring.signal_decorator import SignalMonitoringContext

        context = SignalMonitoringContext("test_strategy")

        assert context.strategy_id == "test_strategy"
        assert context.signals_generated["BUY"] == 0
        assert context.signals_generated["SELL"] == 0
        assert context.errors == []

    def test_record_signal(self):
        """Test signal recording"""
        from src.monitoring.signal_decorator import SignalMonitoringContext

        context = SignalMonitoringContext("test_strategy")

        context.record_signal("BUY", "600519")
        context.record_signal("BUY", "600519")
        context.record_signal("SELL", "000001")

        assert context.signals_generated["BUY"] == 2
        assert context.signals_generated["SELL"] == 1
        assert context.signals_by_symbol["600519"]["BUY"] == 2

    def test_record_push(self):
        """Test push result recording"""
        from src.monitoring.signal_decorator import SignalMonitoringContext

        context = SignalMonitoringContext("test_strategy")

        context.record_push("websocket", True, 45.5)
        context.record_push("websocket", True, 32.1)
        context.record_push("email", False, 120.0)

        assert context.push_results["websocket"]["success"] == 2
        assert context.push_results["email"]["failed"] == 1

    def test_record_gpu_usage(self):
        """Test GPU usage recording"""
        from src.monitoring.signal_decorator import SignalMonitoringContext

        context = SignalMonitoringContext("test_strategy")
        context.record_gpu_usage(125.5)

        assert context._gpu_used is True
        assert context._gpu_latency_ms > 0

    def test_get_summary(self):
        """Test summary generation"""
        from src.monitoring.signal_decorator import SignalMonitoringContext

        context = SignalMonitoringContext("test_strategy")
        context.record_signal("BUY", "600519")
        context.record_signal("SELL", "000001")
        context.record_push("websocket", True, 50.0)

        summary = context.get_summary()

        assert summary["strategy_id"] == "test_strategy"
        assert summary["total_signals"] == 2
        assert summary["signals_by_type"]["BUY"] == 1
        assert summary["unique_symbols"] == 2


class TestMonitoredStrategyExecutor:
    """Test cases for monitored strategy decorator"""

    def test_create_monitored_executor(self):
        """Test creating a monitored executor"""
        from src.monitoring.signal_decorator import create_monitored_executor

        # Create mock executor
        mock_executor = MagicMock()
        mock_executor.execute = MagicMock(return_value={"signals": []})

        monitored = create_monitored_executor(mock_executor, "test_strategy")

        assert monitored._strategy_id == "test_strategy"
        assert monitored._executor is mock_executor

    def test_execute_with_signals(self):
        """Test execute method with signal results"""
        from src.monitoring.signal_decorator import create_monitored_executor

        mock_signal = MagicMock()
        mock_signal.side = MagicMock()
        mock_signal.side.value = "BUY"
        mock_signal.symbol = "600519"

        mock_executor = MagicMock()
        mock_executor.execute = MagicMock(return_value={"signals": [mock_signal]})

        monitored = create_monitored_executor(mock_executor, "test_strategy")
        result = monitored.execute(["600519"])

        assert "signals" in result
        mock_executor.execute.assert_called_once()

    def test_get_monitoring_summary(self):
        """Test getting monitoring summary"""
        from src.monitoring.signal_decorator import create_monitored_executor

        mock_executor = MagicMock()
        mock_executor.execute = MagicMock(return_value={"signals": []})

        monitored = create_monitored_executor(mock_executor, "test_strategy")
        summary = monitored.get_monitoring_summary()

        assert summary["status"] == "no_execution"


class TestRecordSignalResult:
    """Test cases for record_signal_result function"""

    def test_record_executed_signal(self):
        """Test recording an executed signal"""
        try:
            from src.monitoring.signal_decorator import record_signal_result

            # Should not raise
            record_signal_result(
                strategy_id="test", signal_id="sig_001", executed=True, profit_loss=100.5, execution_time_ms=45.2
            )
        except ImportError:
            pytest.skip("signal_decorator module not available")


class TestSignalMetricsCollector:
    """Test cases for SignalMetricsCollector"""

    def test_collector_initialization(self):
        """Test collector initialization"""
        from src.monitoring.signal_decorator import SignalMetricsCollector

        collector = SignalMetricsCollector("test_strategy")

        assert collector.strategy_id == "test_strategy"
        assert collector._pending_signals == []
        assert collector._push_results == []

    def test_add_signal(self):
        """Test adding signals to collector"""
        from src.monitoring.signal_decorator import SignalMetricsCollector

        collector = SignalMetricsCollector("test")
        collector.add_signal({"signal_type": "BUY", "symbol": "600519"})
        collector.add_signal({"signal_type": "SELL", "symbol": "000001"})

        assert len(collector._pending_signals) == 2

    def test_add_push_result(self):
        """Test adding push results to collector"""
        from src.monitoring.signal_decorator import SignalMetricsCollector

        collector = SignalMetricsCollector("test")
        collector.add_push_result({"channel": "websocket", "success": True})
        collector.add_push_result({"channel": "email", "success": False})

        assert len(collector._push_results) == 2


class TestMonitorSignalPushDecorator:
    """Test cases for monitor_signal_push decorator"""

    @pytest.mark.asyncio
    async def test_push_decorator_success(self):
        """Test push decorator with successful push"""
        try:
            from src.monitoring.signal_decorator import monitor_signal_push

            @monitor_signal_push("websocket")
            async def fake_push(signal):
                return {"status": "sent"}

            result = await fake_push({"id": "test"})
            assert result["status"] == "sent"
        except ImportError:
            pytest.skip("signal_decorator module not available")

    @pytest.mark.asyncio
    async def test_push_decorator_failure(self):
        """Test push decorator with failed push"""
        try:
            from src.monitoring.signal_decorator import monitor_signal_push

            @monitor_signal_push("email")
            async def failing_push(signal):
                raise Exception("Connection failed")

            with pytest.raises(Exception):
                await failing_push({"id": "test"})
        except ImportError:
            pytest.skip("signal_decorator module not available")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
