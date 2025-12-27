"""
Socket.IO Streaming Integration Tests

Test Socket.IO namespace event handlers integration with RealtimeStreamingService

Task 6.1: WebSocket event handlers for streaming

Author: Claude Code
Date: 2025-11-07
"""

import pytest
from unittest.mock import AsyncMock, patch

from app.core.socketio_manager import (
    MySocketIOManager,
    ConnectionManager,
    reset_socketio_manager,
)
from app.services.realtime_streaming_service import (
    get_streaming_service,
    reset_streaming_service,
)


class TestConnectionManagerIntegration:
    """Test ConnectionManager with streaming operations"""

    def test_connection_lifecycle_with_cleanup(self):
        """Test connection is properly cleaned up on disconnect"""
        cm = ConnectionManager()
        cm.add_connection("sid_001", "user_001")

        assert cm.is_connected("sid_001")

        user_id = cm.remove_connection("sid_001")

        assert user_id == "user_001"
        assert not cm.is_connected("sid_001")

    def test_connection_room_subscription_tracking(self):
        """Test room subscriptions are tracked correctly"""
        cm = ConnectionManager()
        cm.add_connection("sid_001", "user_001")

        # Subscribe to multiple rooms
        cm.subscribe_to_room("sid_001", "stream_600519")
        cm.subscribe_to_room("sid_001", "stream_000001")

        conn = cm.get_connection("sid_001")
        assert len(conn["rooms"]) == 2
        assert "stream_600519" in conn["rooms"]


class TestSocketIOStreamingEventHandlers:
    """Test Socket.IO streaming event handlers"""

    @pytest.fixture
    def socketio_namespace(self):
        """Create Socket.IO namespace for testing"""
        reset_socketio_manager()
        manager = MySocketIOManager()
        namespace = list(manager.sio.namespace_handlers.values())[0]
        return namespace

    @pytest.fixture
    def mock_sio_manager(self):
        """Create mock Socket.IO manager"""
        reset_socketio_manager()
        manager = MySocketIOManager()
        return manager

    def setup_method(self):
        """Reset services before each test"""
        reset_socketio_manager()
        reset_streaming_service()

    async def test_on_subscribe_market_stream(self, socketio_namespace):
        """Test market stream subscription event handler"""
        socketio_namespace.sio.connection_manager.add_connection("sid_001", "user_001")

        with patch.object(socketio_namespace, "emit", new_callable=AsyncMock) as mock_emit:
            await socketio_namespace.on_subscribe_market_stream("sid_001", {"symbol": "600519"})

            # Check that success response was emitted
            mock_emit.assert_called()
            calls = mock_emit.call_args_list
            assert any(call[1].get("to") == "sid_001" and "stream_subscribed" in str(call) for call in calls)

    async def test_on_subscribe_market_stream_with_fields(self, socketio_namespace):
        """Test market stream subscription with field filter"""
        socketio_namespace.sio.connection_manager.add_connection("sid_001", "user_001")

        with patch.object(socketio_namespace, "emit", new_callable=AsyncMock) as mock_emit:
            await socketio_namespace.on_subscribe_market_stream(
                "sid_001", {"symbol": "600519", "fields": ["price", "volume"]}
            )

            streaming_service = get_streaming_service()
            stream = streaming_service.get_stream("600519")
            assert stream is not None
            subscriber = stream.subscribers.get("sid_001")
            assert subscriber is not None
            assert "price" in subscriber.fields
            assert "volume" in subscriber.fields

    async def test_on_subscribe_market_stream_invalid_symbol(self, socketio_namespace):
        """Test market stream subscription with missing symbol"""
        socketio_namespace.sio.connection_manager.add_connection("sid_001", "user_001")

        with patch.object(socketio_namespace, "emit", new_callable=AsyncMock) as mock_emit:
            await socketio_namespace.on_subscribe_market_stream("sid_001", {})

            # Check that error response was emitted
            calls = mock_emit.call_args_list
            assert any("stream_error" in str(call) for call in calls)

    async def test_on_unsubscribe_market_stream(self, socketio_namespace):
        """Test market stream unsubscription event handler"""
        socketio_namespace.sio.connection_manager.add_connection("sid_001", "user_001")

        # First subscribe
        streaming_service = get_streaming_service()
        streaming_service.subscribe("sid_001", "600519", "user_001")

        with patch.object(socketio_namespace, "emit", new_callable=AsyncMock) as mock_emit:
            await socketio_namespace.on_unsubscribe_market_stream("sid_001", {"symbol": "600519"})

            # Check that success response was emitted
            calls = mock_emit.call_args_list
            assert any("stream_unsubscribed" in str(call) for call in calls)

            # Verify stream is no longer active
            stream = streaming_service.get_stream("600519")
            assert stream is None

    async def test_on_unsubscribe_market_stream_invalid_symbol(self, socketio_namespace):
        """Test market stream unsubscription with missing symbol"""
        socketio_namespace.sio.connection_manager.add_connection("sid_001", "user_001")

        with patch.object(socketio_namespace, "emit", new_callable=AsyncMock) as mock_emit:
            await socketio_namespace.on_unsubscribe_market_stream("sid_001", {})

            # Check that error response was emitted
            calls = mock_emit.call_args_list
            assert any("stream_error" in str(call) for call in calls)

    async def test_on_stream_filter_update(self, socketio_namespace):
        """Test stream filter update event handler"""
        socketio_namespace.sio.connection_manager.add_connection("sid_001", "user_001")

        # First subscribe
        streaming_service = get_streaming_service()
        streaming_service.subscribe("sid_001", "600519", "user_001")

        with patch.object(socketio_namespace, "emit", new_callable=AsyncMock) as mock_emit:
            await socketio_namespace.on_stream_filter_update(
                "sid_001", {"symbol": "600519", "fields": ["price", "bid", "ask"]}
            )

            # Check that success response was emitted
            calls = mock_emit.call_args_list
            assert any("stream_filter_updated" in str(call) for call in calls)

            # Verify fields were updated
            stream = streaming_service.get_stream("600519")
            subscriber = stream.subscribers.get("sid_001")
            assert subscriber.fields == {"price", "bid", "ask"}

    async def test_on_stream_filter_update_missing_stream(self, socketio_namespace):
        """Test stream filter update when stream not found"""
        socketio_namespace.sio.connection_manager.add_connection("sid_001", "user_001")

        with patch.object(socketio_namespace, "emit", new_callable=AsyncMock) as mock_emit:
            await socketio_namespace.on_stream_filter_update("sid_001", {"symbol": "600519", "fields": ["price"]})

            # Check that error response was emitted
            calls = mock_emit.call_args_list
            assert any("stream_error" in str(call) for call in calls)

    async def test_on_connect_initializes_streaming(self):
        """Test on_connect initializes streaming support"""
        reset_socketio_manager()
        manager = MySocketIOManager()
        namespace = list(manager.sio.namespace_handlers.values())[0]

        with patch.object(namespace, "emit", new_callable=AsyncMock) as mock_emit:
            await namespace.on_connect("sid_001", {"HTTP_X_USER_ID": "user_001"})

            # Verify connection was added
            assert manager.connection_manager.is_connected("sid_001")

            # Verify streaming service reference was obtained
            streaming_service = get_streaming_service()
            assert streaming_service is not None

    async def test_on_disconnect_cleans_up_subscriptions(self):
        """Test on_disconnect cleans up streaming subscriptions"""
        reset_socketio_manager()
        manager = MySocketIOManager()
        namespace = list(manager.sio.namespace_handlers.values())[0]

        # First connect and subscribe
        manager.connection_manager.add_connection("sid_001", "user_001")
        streaming_service = get_streaming_service()
        streaming_service.subscribe("sid_001", "600519")
        streaming_service.subscribe("sid_001", "000001")

        # Verify subscriptions exist
        assert len(streaming_service.get_active_symbols()) == 2

        # Disconnect
        await namespace.on_disconnect("sid_001")

        # Verify subscriptions were cleaned up
        assert "sid_001" not in streaming_service.subscriber_to_stream
        # Active symbols should be empty since no subscribers remain
        assert len(streaming_service.get_active_symbols()) == 0


class TestSocketIOManagerStreamingMethods:
    """Test Socket.IO manager streaming-specific methods"""

    def setup_method(self):
        """Reset services before each test"""
        reset_socketio_manager()
        reset_streaming_service()

    async def test_emit_stream_data(self):
        """Test emitting stream data to subscribers"""
        reset_socketio_manager()
        manager = MySocketIOManager()

        # Create a stream subscription
        streaming_service = get_streaming_service()
        streaming_service.subscribe("sid_001", "600519")

        with patch.object(manager.sio, "emit", new_callable=AsyncMock) as mock_emit:
            await manager.emit_stream_data("600519", {"price": 100.5, "volume": 1000})

            # Verify emit was called with correct parameters
            mock_emit.assert_called_once()
            call_args = mock_emit.call_args
            assert call_args[0][0] == "stream_data"
            assert call_args[1]["to"] == "stream_600519"

    async def test_emit_stream_data_nonexistent_stream(self):
        """Test emitting stream data for non-existent stream"""
        reset_socketio_manager()
        manager = MySocketIOManager()

        with patch.object(manager.sio, "emit", new_callable=AsyncMock) as mock_emit:
            await manager.emit_stream_data("nonexistent", {"price": 100})

            # Should not emit if stream doesn't exist
            mock_emit.assert_not_called()

    def test_get_streaming_stats(self):
        """Test getting streaming statistics"""
        reset_socketio_manager()
        manager = MySocketIOManager()

        streaming_service = get_streaming_service()
        streaming_service.subscribe("sid_001", "600519")
        streaming_service.subscribe("sid_002", "600519")

        stats = manager.get_streaming_stats()

        assert stats["active_streams"] == 1
        assert stats["total_subscribers"] == 2

    def test_get_stats_includes_streaming(self):
        """Test get_stats includes streaming information"""
        reset_socketio_manager()
        manager = MySocketIOManager()

        streaming_service = get_streaming_service()
        streaming_service.subscribe("sid_001", "600519")

        manager.connection_manager.add_connection("sid_001", "user_001")

        stats = manager.get_stats()

        assert "streaming" in stats
        assert stats["streaming"]["active_streams"] == 1
        assert "reconnection" in stats


class TestStreamingEventIntegration:
    """Test end-to-end streaming event integration"""

    def setup_method(self):
        """Reset services before each test"""
        reset_socketio_manager()
        reset_streaming_service()

    async def test_multiple_subscribers_same_symbol(self):
        """Test multiple subscribers can subscribe to same symbol"""
        reset_socketio_manager()
        manager = MySocketIOManager()
        namespace = list(manager.sio.namespace_handlers.values())[0]

        # Add connections
        manager.connection_manager.add_connection("sid_001", "user_001")
        manager.connection_manager.add_connection("sid_002", "user_002")

        streaming_service = get_streaming_service()

        with patch.object(namespace, "emit", new_callable=AsyncMock) as mock_emit:
            # Both subscribe to same symbol
            await namespace.on_subscribe_market_stream("sid_001", {"symbol": "600519"})
            await namespace.on_subscribe_market_stream("sid_002", {"symbol": "600519"})

            stream = streaming_service.get_stream("600519")
            assert len(stream.subscribers) == 2

    async def test_single_subscriber_multiple_symbols(self):
        """Test single subscriber can subscribe to multiple symbols"""
        reset_socketio_manager()
        manager = MySocketIOManager()
        namespace = list(manager.sio.namespace_handlers.values())[0]

        manager.connection_manager.add_connection("sid_001", "user_001")
        streaming_service = get_streaming_service()

        with patch.object(namespace, "emit", new_callable=AsyncMock) as mock_emit:
            # Subscribe to multiple symbols
            symbols = ["600519", "000001", "600000"]
            for symbol in symbols:
                await namespace.on_subscribe_market_stream("sid_001", {"symbol": symbol})

            active_symbols = streaming_service.get_active_symbols()
            assert len(active_symbols) == 3
            for symbol in symbols:
                assert symbol in active_symbols

    async def test_subscriber_cleanup_on_last_unsubscribe(self):
        """Test stream is cleaned up when last subscriber unsubscribes"""
        reset_socketio_manager()
        manager = MySocketIOManager()
        namespace = list(manager.sio.namespace_handlers.values())[0]

        manager.connection_manager.add_connection("sid_001", "user_001")
        streaming_service = get_streaming_service()

        with patch.object(namespace, "emit", new_callable=AsyncMock) as mock_emit:
            # Subscribe and then unsubscribe
            await namespace.on_subscribe_market_stream("sid_001", {"symbol": "600519"})
            assert "600519" in streaming_service.get_active_symbols()

            await namespace.on_unsubscribe_market_stream("sid_001", {"symbol": "600519"})
            assert "600519" not in streaming_service.get_active_symbols()


class TestStreamingErrorHandling:
    """Test error handling in streaming operations"""

    def setup_method(self):
        """Reset services before each test"""
        reset_socketio_manager()
        reset_streaming_service()

    async def test_subscribe_with_missing_connection(self):
        """Test subscription with non-existent connection"""
        reset_socketio_manager()
        manager = MySocketIOManager()
        namespace = list(manager.sio.namespace_handlers.values())[0]

        with patch.object(namespace, "emit", new_callable=AsyncMock) as mock_emit:
            # Don't add connection, just try to subscribe
            await namespace.on_subscribe_market_stream("nonexistent_sid", {"symbol": "600519"})

            # Should still work (get_connection returns None gracefully)
            streaming_service = get_streaming_service()
            stream = streaming_service.get_stream("600519")
            assert stream is not None

    async def test_exception_during_subscription(self):
        """Test exception handling during subscription"""
        reset_socketio_manager()
        manager = MySocketIOManager()
        namespace = list(manager.sio.namespace_handlers.values())[0]

        manager.connection_manager.add_connection("sid_001", "user_001")

        with patch.object(namespace, "emit", new_callable=AsyncMock) as mock_emit:
            # Force an exception in streaming service
            with patch(
                "app.core.socketio_manager.get_streaming_service",
                side_effect=Exception("Service error"),
            ):
                await namespace.on_subscribe_market_stream("sid_001", {"symbol": "600519"})

                # Should emit error response
                calls = mock_emit.call_args_list
                assert any("stream_error" in str(call) for call in calls)
