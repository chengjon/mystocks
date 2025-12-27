"""
聚合流媒体桥接服务测试

Tests for AggregationStreamingBridge service

Task 7: 实现实时OHLCV柱线聚合与多时间周期支持

Author: Claude Code
Date: 2025-11-07
"""

from unittest.mock import MagicMock, patch
from decimal import Decimal

from app.services.data_aggregation_service import (
    OHLCV,
    Timeframe,
    reset_aggregation_engine,
)
from app.services.realtime_streaming_service import (
    reset_streaming_service,
)
from app.services.aggregation_streaming_bridge import (
    AggregationStreamingBridge,
    BarPublishMode,
    get_aggregation_streaming_bridge,
    reset_aggregation_streaming_bridge,
)


class TestBridgeInitialization:
    """Test bridge initialization"""

    def setup_method(self):
        """Reset services before each test"""
        reset_aggregation_engine()
        reset_streaming_service()
        reset_aggregation_streaming_bridge()

    def test_bridge_creation(self):
        """Test bridge object creation"""
        bridge = AggregationStreamingBridge()

        assert bridge.engine is not None
        assert bridge.streaming is not None
        assert bridge.publish_mode == BarPublishMode.COMPLETED
        assert bridge.bars_published == 0
        assert bridge.bars_persisted == 0

    def test_bridge_with_custom_mode(self):
        """Test bridge with custom publish mode"""
        bridge = AggregationStreamingBridge(publish_mode=BarPublishMode.REAL_TIME)
        assert bridge.publish_mode == BarPublishMode.REAL_TIME

    def test_bridge_singleton(self):
        """Test singleton pattern"""
        reset_aggregation_streaming_bridge()
        bridge1 = get_aggregation_streaming_bridge()
        bridge2 = get_aggregation_streaming_bridge()
        assert bridge1 is bridge2

    def test_bridge_persistence_disabled(self):
        """Test bridge with persistence disabled"""
        bridge = AggregationStreamingBridge(enable_persistence=False)
        assert bridge.storage is None
        assert bridge.enable_persistence is False


class TestBridgePublishing:
    """Test bar publishing"""

    def setup_method(self):
        """Reset services before each test"""
        reset_aggregation_engine()
        reset_streaming_service()
        reset_aggregation_streaming_bridge()

    def test_publish_single_bar(self):
        """Test publishing a single bar"""
        bridge = AggregationStreamingBridge(enable_persistence=False)
        bridge.streaming.subscribe("sid_001", "600519")

        bar = OHLCV(
            symbol="600519",
            timeframe=Timeframe.ONE_MINUTE,
            timestamp=1699000000000,
            open=Decimal("100.00"),
            high=Decimal("100.50"),
            low=Decimal("99.50"),
            close=Decimal("100.25"),
            volume=10000,
            completed=True,
        )

        bridge.process_completed_bars([bar])

        assert bridge.bars_published == 1
        assert bridge.publish_errors == 0

    def test_publish_multiple_bars(self):
        """Test publishing multiple bars"""
        bridge = AggregationStreamingBridge(enable_persistence=False)
        bridge.streaming.subscribe("sid_001", "600519")

        bars = [
            OHLCV(
                symbol="600519",
                timeframe=Timeframe.ONE_MINUTE,
                timestamp=1699000000000 + i * 60000,
                open=Decimal("100.00"),
                high=Decimal("100.50"),
                low=Decimal("99.50"),
                close=Decimal("100.25"),
                volume=10000,
                completed=True,
            )
            for i in range(5)
        ]

        bridge.process_completed_bars(bars)

        assert bridge.bars_published == 5
        assert bridge.publish_errors == 0

    def test_publish_empty_list(self):
        """Test publishing empty list"""
        bridge = AggregationStreamingBridge(enable_persistence=False)

        bridge.process_completed_bars([])

        assert bridge.bars_published == 0

    def test_publish_with_callback(self):
        """Test publishing with callback"""
        bridge = AggregationStreamingBridge(enable_persistence=False)
        bridge.streaming.subscribe("sid_001", "600519")

        callback_called = []

        def on_bar_published(bar):
            callback_called.append(bar)

        bridge.on_bar_published = on_bar_published

        bar = OHLCV(
            symbol="600519",
            timeframe=Timeframe.ONE_MINUTE,
            timestamp=1699000000000,
            open=Decimal("100.00"),
            high=Decimal("100.50"),
            low=Decimal("99.50"),
            close=Decimal("100.25"),
            volume=10000,
            completed=True,
        )

        bridge.process_completed_bars([bar])

        assert len(callback_called) == 1
        assert callback_called[0].symbol == "600519"


class TestBridgePersistence:
    """Test bar persistence"""

    def setup_method(self):
        """Reset services before each test"""
        reset_aggregation_engine()
        reset_streaming_service()
        reset_aggregation_streaming_bridge()

    def test_persistence_enabled(self):
        """Test bar persistence when enabled"""
        with patch("app.services.aggregation_streaming_bridge.OHLCVStorage") as mock_storage:
            mock_instance = MagicMock()
            mock_instance.insert_bars_batch.return_value = 1
            mock_storage.return_value = mock_instance

            bridge = AggregationStreamingBridge(enable_persistence=True)
            bridge.storage = mock_instance

            bar = OHLCV(
                symbol="600519",
                timeframe=Timeframe.ONE_MINUTE,
                timestamp=1699000000000,
                open=Decimal("100.00"),
                high=Decimal("100.50"),
                low=Decimal("99.50"),
                close=Decimal("100.25"),
                volume=10000,
                completed=True,
            )

            bridge.process_completed_bars([bar])

            assert bridge.bars_persisted == 1
            mock_instance.insert_bars_batch.assert_called_once()

    def test_persistence_disabled(self):
        """Test no persistence when disabled"""
        bridge = AggregationStreamingBridge(enable_persistence=False)

        bar = OHLCV(
            symbol="600519",
            timeframe=Timeframe.ONE_MINUTE,
            timestamp=1699000000000,
            open=Decimal("100.00"),
            high=Decimal("100.50"),
            low=Decimal("99.50"),
            close=Decimal("100.25"),
            volume=10000,
            completed=True,
        )

        bridge.process_completed_bars([bar])

        assert bridge.bars_persisted == 0


class TestBridgeIntegration:
    """Test end-to-end integration"""

    def setup_method(self):
        """Reset services before each test"""
        reset_aggregation_engine()
        reset_streaming_service()
        reset_aggregation_streaming_bridge()

    def test_complete_flow(self):
        """Test complete aggregation to streaming flow"""
        bridge = AggregationStreamingBridge(enable_persistence=False)
        engine = bridge.engine
        streaming = bridge.streaming

        # Subscribe to stream
        streaming.subscribe("sid_001", "600519")

        # Create bars
        bars = [
            OHLCV(
                symbol="600519",
                timeframe=Timeframe.ONE_MINUTE,
                timestamp=1699000000000,
                open=Decimal("100.00"),
                high=Decimal("100.50"),
                low=Decimal("99.50"),
                close=Decimal("100.25"),
                volume=10000,
                completed=True,
            )
        ]

        # Process through bridge
        bridge.process_completed_bars(bars)

        # Verify results
        assert bridge.bars_published == 1
        assert bridge.publish_errors == 0

        # Verify stream still exists
        stream = streaming.get_stream("600519")
        assert stream is not None
        assert len(stream.subscribers) == 1

    def test_multiple_symbols_and_timeframes(self):
        """Test with multiple symbols and timeframes"""
        bridge = AggregationStreamingBridge(enable_persistence=False)
        streaming = bridge.streaming

        # Subscribe to multiple symbols
        streaming.subscribe("sid_001", "600519")
        streaming.subscribe("sid_002", "000001")

        bars = [
            OHLCV(
                symbol="600519",
                timeframe=Timeframe.ONE_MINUTE,
                timestamp=1699000000000,
                open=Decimal("100.00"),
                high=Decimal("100.50"),
                low=Decimal("99.50"),
                close=Decimal("100.25"),
                volume=10000,
                completed=True,
            ),
            OHLCV(
                symbol="600519",
                timeframe=Timeframe.FIVE_MINUTES,
                timestamp=1699000000000,
                open=Decimal("100.00"),
                high=Decimal("100.50"),
                low=Decimal("99.50"),
                close=Decimal("100.25"),
                volume=50000,
                completed=True,
            ),
            OHLCV(
                symbol="000001",
                timeframe=Timeframe.ONE_MINUTE,
                timestamp=1699000000000,
                open=Decimal("200.00"),
                high=Decimal("200.50"),
                low=Decimal("199.50"),
                close=Decimal("200.25"),
                volume=20000,
                completed=True,
            ),
        ]

        bridge.process_completed_bars(bars)

        assert bridge.bars_published == 3
        assert len(streaming.get_active_symbols()) == 2


class TestBridgeStats:
    """Test statistics"""

    def setup_method(self):
        """Reset services before each test"""
        reset_aggregation_engine()
        reset_streaming_service()
        reset_aggregation_streaming_bridge()

    def test_get_stats(self):
        """Test getting bridge statistics"""
        bridge = AggregationStreamingBridge(enable_persistence=False)

        bar = OHLCV(
            symbol="600519",
            timeframe=Timeframe.ONE_MINUTE,
            timestamp=1699000000000,
            open=Decimal("100.00"),
            high=Decimal("100.50"),
            low=Decimal("99.50"),
            close=Decimal("100.25"),
            volume=10000,
            completed=True,
        )

        bridge.process_completed_bars([bar])

        stats = bridge.get_stats()

        assert stats["bars_published"] == 1
        assert stats["bars_persisted"] == 0
        assert stats["publish_errors"] == 0
        assert stats["publish_mode"] == "completed"
        assert "aggregation_stats" in stats
        assert "streaming_stats" in stats

    def test_stats_with_errors(self):
        """Test stats when errors occur"""
        bridge = AggregationStreamingBridge(enable_persistence=False)

        # Mock error scenario
        bridge.publish_errors = 5
        bridge.last_error = "Test error"

        stats = bridge.get_stats()

        assert stats["publish_errors"] == 5
        assert stats["last_error"] == "Test error"


class TestBridgeErrorHandling:
    """Test error handling"""

    def setup_method(self):
        """Reset services before each test"""
        reset_aggregation_engine()
        reset_streaming_service()
        reset_aggregation_streaming_bridge()

    def test_handle_persistence_error(self):
        """Test handling persistence errors"""
        with patch("app.services.aggregation_streaming_bridge.OHLCVStorage") as mock_storage:
            mock_instance = MagicMock()
            mock_instance.insert_bars_batch.side_effect = Exception("DB error")
            mock_storage.return_value = mock_instance

            bridge = AggregationStreamingBridge(enable_persistence=True)
            bridge.storage = mock_instance

            bar = OHLCV(
                symbol="600519",
                timeframe=Timeframe.ONE_MINUTE,
                timestamp=1699000000000,
                open=Decimal("100.00"),
                high=Decimal("100.50"),
                low=Decimal("99.50"),
                close=Decimal("100.25"),
                volume=10000,
                completed=True,
            )

            bridge.process_completed_bars([bar])

            # Bar should still be published despite persistence error
            assert bridge.bars_published == 1
            assert bridge.last_error is not None
