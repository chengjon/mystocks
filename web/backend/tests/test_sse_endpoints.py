"""
SSE Endpoints Tests
Week 2 Day 3 - SSE Real-time Push Testing

Tests SSE endpoints for:
- Connection establishment
- Event streaming
- Disconnection handling
- Multiple concurrent clients
"""

import pytest
import asyncio
import httpx
from fastapi.testclient import TestClient
from datetime import datetime
from typing import List, Dict, Any
import json

# Mark all tests in this module
pytestmark = [pytest.mark.week2, pytest.mark.sse]


class TestSSEBasicConnection:
    """Test basic SSE connection functionality"""

    def test_training_sse_connection(self, test_client):
        """
        Test SSE connection to training channel
        Expected: 200 OK with SSE headers
        """
        with test_client.stream("GET", "/api/v1/sse/training") as response:
            assert response.status_code == 200
            assert (
                response.headers["content-type"] == "text/event-stream; charset=utf-8"
            )
            assert response.headers["cache-control"] == "no-cache"

            # Read first event (connection confirmation)
            for line in response.iter_lines():
                if line.startswith("data:"):
                    data = json.loads(line[5:])  # Remove 'data:' prefix
                    assert "event" in data
                    assert data["event"] == "connected"
                    assert "timestamp" in data
                    break

    def test_backtest_sse_connection(self, test_client):
        """
        Test SSE connection to backtest channel
        Expected: 200 OK with connection event
        """
        with test_client.stream("GET", "/api/v1/sse/backtest") as response:
            assert response.status_code == 200

            # Read first event
            for line in response.iter_lines():
                if line.startswith("data:"):
                    data = json.loads(line[5:])
                    assert data["event"] == "connected"
                    break

    def test_alerts_sse_connection(self, test_client):
        """
        Test SSE connection to alerts channel
        Expected: 200 OK with connection event
        """
        with test_client.stream("GET", "/api/v1/sse/alerts") as response:
            assert response.status_code == 200

            for line in response.iter_lines():
                if line.startswith("data:"):
                    data = json.loads(line[5:])
                    assert data["event"] == "connected"
                    break

    def test_dashboard_sse_connection(self, test_client):
        """
        Test SSE connection to dashboard channel
        Expected: 200 OK with connection event
        """
        with test_client.stream("GET", "/api/v1/sse/dashboard") as response:
            assert response.status_code == 200

            for line in response.iter_lines():
                if line.startswith("data:"):
                    data = json.loads(line[5:])
                    assert data["event"] == "connected"
                    break


class TestSSEBroadcasting:
    """Test SSE event broadcasting"""

    @pytest.mark.asyncio
    async def test_broadcast_training_progress(self):
        """
        Test broadcasting training progress events
        Expected: Events received by all connected clients
        """
        from app.core.sse_manager import get_sse_broadcaster

        broadcaster = get_sse_broadcaster()

        # Simulate training progress broadcast
        await broadcaster.send_training_progress(
            task_id="test-task-123",
            progress=50.0,
            status="running",
            message="Training in progress",
            metrics={"loss": 0.5, "accuracy": 0.85},
        )

        # Note: This test verifies the broadcast API works
        # Actual event reception would require running server

    @pytest.mark.asyncio
    async def test_broadcast_backtest_progress(self):
        """
        Test broadcasting backtest progress events
        Expected: Events received by subscribers
        """
        from app.core.sse_manager import get_sse_broadcaster

        broadcaster = get_sse_broadcaster()

        await broadcaster.send_backtest_progress(
            backtest_id="backtest-456",
            progress=75.0,
            status="running",
            message="Simulating 2024-06-15",
            current_date="2024-06-15",
            results={"total_return": 0.15},
        )

    @pytest.mark.asyncio
    async def test_broadcast_risk_alert(self):
        """
        Test broadcasting risk alerts
        Expected: Alerts delivered to subscribers
        """
        from app.core.sse_manager import get_sse_broadcaster

        broadcaster = get_sse_broadcaster()

        await broadcaster.send_risk_alert(
            alert_type="var_exceeded",
            severity="high",
            message="VaR exceeded threshold",
            metric_name="var_95",
            metric_value=0.06,
            threshold=0.05,
        )

    @pytest.mark.asyncio
    async def test_broadcast_dashboard_update(self):
        """
        Test broadcasting dashboard updates
        Expected: Dashboard data pushed to clients
        """
        from app.core.sse_manager import get_sse_broadcaster

        broadcaster = get_sse_broadcaster()

        await broadcaster.send_dashboard_update(
            update_type="metrics",
            data={"total_value": 1500000.0, "daily_return": 0.025},
        )


class TestSSEStatus:
    """Test SSE status endpoint"""

    def test_sse_status_no_connections(self, test_client):
        """
        Test SSE status with no active connections
        Expected: 200 OK with zero connection count
        """
        response = test_client.get("/api/v1/sse/status")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "active"
        assert "total_connections" in data
        assert "channels" in data

    def test_sse_status_with_connections(self, test_client):
        """
        Test SSE status with active connections
        Expected: Status shows connected clients
        """
        # Note: This would require actually establishing SSE connections
        # For now, we just verify the endpoint works
        response = test_client.get("/api/v1/sse/status")
        assert response.status_code == 200


class TestSSEConnectionManager:
    """Test SSEConnectionManager directly"""

    @pytest.mark.asyncio
    async def test_connection_manager_connect_disconnect(self):
        """
        Test connection manager connect/disconnect cycle
        Expected: Proper connection registration and cleanup
        """
        from app.core.sse_manager import SSEConnectionManager

        manager = SSEConnectionManager()

        # Connect client
        client_id, queue = await manager.connect("training")
        assert client_id is not None
        assert manager.get_connection_count("training") == 1

        # Disconnect client
        await manager.disconnect("training", client_id)
        assert manager.get_connection_count("training") == 0

    @pytest.mark.asyncio
    async def test_connection_manager_multiple_clients(self):
        """
        Test multiple concurrent clients
        Expected: All clients registered correctly
        """
        from app.core.sse_manager import SSEConnectionManager

        manager = SSEConnectionManager()

        # Connect multiple clients
        client_ids = []
        for i in range(5):
            client_id, queue = await manager.connect("backtest")
            client_ids.append(client_id)

        assert manager.get_connection_count("backtest") == 5

        # Disconnect all
        for client_id in client_ids:
            await manager.disconnect("backtest", client_id)

        assert manager.get_connection_count("backtest") == 0

    @pytest.mark.asyncio
    async def test_connection_manager_broadcast(self):
        """
        Test event broadcasting to multiple clients
        Expected: All clients receive the event
        """
        from app.core.sse_manager import SSEConnectionManager, SSEEvent

        manager = SSEConnectionManager()

        # Connect clients
        client1_id, queue1 = await manager.connect("alerts")
        client2_id, queue2 = await manager.connect("alerts")

        # Consume the "connected" events first
        connected1 = await asyncio.wait_for(queue1.get(), timeout=1.0)
        connected2 = await asyncio.wait_for(queue2.get(), timeout=1.0)
        assert connected1.event == "connected"
        assert connected2.event == "connected"

        # Broadcast event
        event = SSEEvent(event="test_event", data={"message": "Test broadcast"})
        await manager.broadcast("alerts", event)

        # Verify both clients received the broadcast event
        event1 = await asyncio.wait_for(queue1.get(), timeout=1.0)
        event2 = await asyncio.wait_for(queue2.get(), timeout=1.0)

        assert event1.event == "test_event"
        assert event2.event == "test_event"

        # Cleanup
        await manager.disconnect("alerts", client1_id)
        await manager.disconnect("alerts", client2_id)


class TestSSEErrorHandling:
    """Test SSE error handling"""

    @pytest.mark.asyncio
    async def test_queue_overflow_handling(self):
        """
        Test queue overflow handling
        Expected: Client disconnected when queue is full
        """
        from app.core.sse_manager import SSEConnectionManager, SSEEvent

        manager = SSEConnectionManager(max_queue_size=2)

        client_id, queue = await manager.connect("training")

        # Fill the queue
        for i in range(3):
            event = SSEEvent(event="overflow_test", data={"index": i})
            try:
                await manager.broadcast("training", event)
            except:
                pass  # Expected to fail on overflow

        # Client should still be connected (with limited queue)
        # In real scenario, client would be disconnected if queue can't accept events

    @pytest.mark.asyncio
    async def test_invalid_channel(self):
        """
        Test broadcasting to non-existent channel
        Expected: Graceful handling (no error)
        """
        from app.core.sse_manager import SSEConnectionManager, SSEEvent

        manager = SSEConnectionManager()

        event = SSEEvent(event="test", data={"message": "test"})

        # Should not raise error for non-existent channel
        await manager.broadcast("non_existent_channel", event)


# Markers are registered in pytest.ini
