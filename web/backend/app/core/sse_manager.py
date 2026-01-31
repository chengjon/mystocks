"""
SSE (Server-Sent Events) Manager for Real-time Updates
Week 2 Day 3 - SSE Real-time Push Implementation

This module provides infrastructure for streaming real-time updates to frontend clients
using Server-Sent Events (SSE) protocol.

Features:
- Connection management for multiple concurrent SSE clients
- Event broadcasting to specific channels or all clients
- Automatic reconnection handling
- Memory-efficient event streaming
- Channel-based pub/sub pattern

Architecture:
- SSEConnectionManager: Manages all active SSE connections
- SSEBroadcaster: Broadcasts events to connected clients
- Channel-based routing: training, backtest, alerts, dashboard
"""

import asyncio
import logging
import uuid
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Any, AsyncGenerator, Dict, Optional, Set

from fastapi import Request

logger = logging.getLogger(__name__)


@dataclass
class SSEEvent:
    """SSE Event data structure"""

    event: str  # Event type (e.g., 'training_progress', 'backtest_update')
    data: Dict[str, Any]  # Event payload
    id: Optional[str] = None  # Event ID for client-side tracking
    retry: Optional[int] = None  # Retry interval in milliseconds

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        result = {
            "event": self.event,
            "data": self.data,
        }
        if self.id:
            result["id"] = self.id
        if self.retry:
            result["retry"] = self.retry
        return result


class SSEConnectionManager:
    """
    Manages SSE connections and event broadcasting

    Features:
    - Channel-based subscriptions (training, backtest, alerts, dashboard)
    - Automatic connection cleanup on disconnect
    - Memory-efficient queue management
    - Concurrent client support
    """

    def __init__(self, max_queue_size: int = 100):
        """
        Initialize SSE Connection Manager

        Args:
            max_queue_size: Maximum events to queue per connection
        """
        # {channel: {client_id: asyncio.Queue}}
        self._connections: Dict[str, Dict[str, asyncio.Queue]] = defaultdict(dict)

        # Track all client IDs across channels
        self._client_channels: Dict[str, Set[str]] = defaultdict(set)

        self.max_queue_size = max_queue_size

        logger.info("✅ SSEConnectionManager initialized (max_queue_size=%(max_queue_size)s)"")

    async def connect(self, channel: str, client_id: Optional[str] = None) -> tuple[str, asyncio.Queue]:
        """
        Register a new SSE connection

        Args:
            channel: Channel name (e.g., 'training', 'backtest', 'alerts', 'dashboard')
            client_id: Optional client identifier (auto-generated if not provided)

        Returns:
            Tuple of (client_id, event_queue)
        """
        if client_id is None:
            client_id = str(uuid.uuid4())

        # Create event queue for this client
        queue = asyncio.Queue(maxsize=self.max_queue_size)

        # Register connection
        self._connections[channel][client_id] = queue
        self._client_channels[client_id].add(channel)

        logger.info(
            f"🔗 SSE client connected: client_id={client_id}, channel={channel}, "
            f"total_clients={self.get_connection_count(channel)}"
        )

        # Send initial connection event
        await self.send_to_client(
            channel=channel,
            client_id=client_id,
            event=SSEEvent(
                event="connected",
                data={
                    "client_id": client_id,
                    "channel": channel,
                    "message": f"Connected to {channel} channel",
                },
                id=str(uuid.uuid4()),
            ),
        )

        return client_id, queue

    async def disconnect(self, channel: str, client_id: str):
        """
        Unregister an SSE connection

        Args:
            channel: Channel name
            client_id: Client identifier
        """
        if channel in self._connections and client_id in self._connections[channel]:
            # Remove from connections
            del self._connections[channel][client_id]

            # Remove from client channels tracking
            if client_id in self._client_channels:
                self._client_channels[client_id].discard(channel)
                if not self._client_channels[client_id]:
                    del self._client_channels[client_id]

            # Clean up empty channel
            if not self._connections[channel]:
                del self._connections[channel]

            logger.info(
                f"🔌 SSE client disconnected: client_id={client_id}, "
                f"channel={channel}, remaining_clients={self.get_connection_count(channel)}"
            )

    async def broadcast(self, channel: str, event: SSEEvent):
        """
        Broadcast event to all clients on a channel

        Args:
            channel: Channel name
            event: SSE event to broadcast
        """
        if channel not in self._connections:
            logger.debug("No clients connected to channel: %(channel)s"")
            return

        client_count = 0
        failed_clients = []

        for client_id, queue in list(self._connections[channel].items()):
            try:
                # Non-blocking put with timeout
                await asyncio.wait_for(queue.put(event), timeout=1.0)
                client_count += 1
            except asyncio.TimeoutError:
                logger.warning("Client queue full: %(client_id)s"")
                failed_clients.append(client_id)
            except Exception as e:
                logger.error("Failed to queue event for client %(client_id)s: %(e)s"")
                failed_clients.append(client_id)

        # Clean up failed clients
        for client_id in failed_clients:
            await self.disconnect(channel, client_id)

        if client_count > 0:
            logger.debug("📡 Broadcasted {event.event} to %(client_count)s clients on %(channel)s channel"")

    async def send_to_client(self, channel: str, client_id: str, event: SSEEvent):
        """
        Send event to specific client

        Args:
            channel: Channel name
            client_id: Client identifier
            event: SSE event to send
        """
        if channel in self._connections and client_id in self._connections[channel]:
            queue = self._connections[channel][client_id]
            try:
                await asyncio.wait_for(queue.put(event), timeout=1.0)
                logger.debug("📤 Sent {event.event} to client %(client_id)s"")
            except asyncio.TimeoutError:
                logger.warning("Client queue full: %(client_id)s"")
                await self.disconnect(channel, client_id)
            except Exception as e:
                logger.error("Failed to send event to client %(client_id)s: %(e)s"")

    def get_connection_count(self, channel: Optional[str] = None) -> int:
        """
        Get number of active connections

        Args:
            channel: Optional channel name (all channels if None)

        Returns:
            Number of active connections
        """
        if channel:
            return len(self._connections.get(channel, {}))
        else:
            return sum(len(clients) for clients in self._connections.values())

    def get_channels(self) -> list[str]:
        """Get list of active channels"""
        return list(self._connections.keys())

    def get_clients(self, channel: str) -> list[str]:
        """Get list of client IDs on a channel"""
        return list(self._connections.get(channel, {}).keys())


class SSEBroadcaster:
    """
    High-level SSE broadcasting interface

    Provides convenient methods for broadcasting different event types
    """

    def __init__(self, manager: SSEConnectionManager):
        """
        Initialize SSE Broadcaster

        Args:
            manager: SSE connection manager instance
        """
        self.manager = manager

    async def send_training_progress(
        self,
        task_id: str,
        progress: float,
        status: str,
        message: str,
        metrics: Optional[Dict[str, Any]] = None,
    ):
        """
        Broadcast model training progress

        Args:
            task_id: Training task identifier
            progress: Progress percentage (0-100)
            status: Status (running, completed, failed)
            message: Human-readable message
            metrics: Optional training metrics (loss, accuracy, etc.)
        """
        event = SSEEvent(
            event="training_progress",
            data={
                "task_id": task_id,
                "progress": progress,
                "status": status,
                "message": message,
                "metrics": metrics or {},
            },
            id=str(uuid.uuid4()),
        )
        await self.manager.broadcast("training", event)

    async def send_backtest_progress(
        self,
        backtest_id: str,
        progress: float,
        status: str,
        message: str,
        current_date: Optional[str] = None,
        results: Optional[Dict[str, Any]] = None,
    ):
        """
        Broadcast backtest execution progress

        Args:
            backtest_id: Backtest identifier
            progress: Progress percentage (0-100)
            status: Status (running, completed, failed)
            message: Human-readable message
            current_date: Current simulation date
            results: Optional partial results
        """
        event = SSEEvent(
            event="backtest_progress",
            data={
                "backtest_id": backtest_id,
                "progress": progress,
                "status": status,
                "message": message,
                "current_date": current_date,
                "results": results or {},
            },
            id=str(uuid.uuid4()),
        )
        await self.manager.broadcast("backtest", event)

    async def send_risk_alert(
        self,
        alert_type: str,
        severity: str,
        message: str,
        metric_name: str,
        metric_value: float,
        threshold: float,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
    ):
        """
        Broadcast risk alert notification

        Args:
            alert_type: Alert type (var_exceeded, drawdown_limit, etc.)
            severity: Severity level (low, medium, high, critical)
            message: Alert message
            metric_name: Risk metric name
            metric_value: Current metric value
            threshold: Alert threshold
            entity_type: Optional entity type (portfolio, strategy, etc.)
            entity_id: Optional entity identifier
        """
        event = SSEEvent(
            event="risk_alert",
            data={
                "alert_type": alert_type,
                "severity": severity,
                "message": message,
                "metric_name": metric_name,
                "metric_value": metric_value,
                "threshold": threshold,
                "entity_type": entity_type,
                "entity_id": entity_id,
            },
            id=str(uuid.uuid4()),
        )
        await self.manager.broadcast("alerts", event)

    async def send_dashboard_update(self, update_type: str, data: Dict[str, Any]):
        """
        Broadcast dashboard data update

        Args:
            update_type: Update type (metrics, positions, orders, etc.)
            data: Update data
        """
        event = SSEEvent(
            event="dashboard_update",
            data={"update_type": update_type, "data": data},
            id=str(uuid.uuid4()),
        )
        await self.manager.broadcast("dashboard", event)


# Global SSE manager instance (singleton)
_sse_manager: Optional[SSEConnectionManager] = None
_sse_broadcaster: Optional[SSEBroadcaster] = None


def get_sse_manager() -> SSEConnectionManager:
    """Get global SSE manager instance (lazy initialization)"""
    global _sse_manager
    if _sse_manager is None:
        _sse_manager = SSEConnectionManager()
    return _sse_manager


def get_sse_broadcaster() -> SSEBroadcaster:
    """Get global SSE broadcaster instance (lazy initialization)"""
    global _sse_broadcaster
    if _sse_broadcaster is None:
        manager = get_sse_manager()
        _sse_broadcaster = SSEBroadcaster(manager)
    return _sse_broadcaster


async def sse_event_generator(
    request: Request, channel: str, client_id: Optional[str] = None
) -> AsyncGenerator[Dict[str, Any], None]:
    """
    SSE event generator for FastAPI endpoint

    Args:
        request: FastAPI request object
        channel: Channel name
        client_id: Optional client identifier

    Yields:
        SSE events as dictionaries
    """
    manager = get_sse_manager()
    client_id, queue = await manager.connect(channel, client_id)

    try:
        while True:
            # Check if client disconnected
            if await request.is_disconnected():
                break

            try:
                # Wait for event with timeout
                event = await asyncio.wait_for(queue.get(), timeout=30.0)

                # Add timestamp to event data
                event_data = event.data.copy() if event.data else {}
                event_data["timestamp"] = datetime.now().isoformat()

                # Yield event data with timestamp included (filter None values)
                event_dict = {
                    "event": event.event,
                    "data": event_data,
                }
                if event.id:
                    event_dict["id"] = event.id
                if event.retry:
                    event_dict["retry"] = event.retry

                yield event_dict

            except asyncio.TimeoutError:
                # Send keepalive ping every 30 seconds
                yield {
                    "event": "ping",
                    "data": {"timestamp": datetime.now().isoformat()},
                }

    finally:
        # Cleanup on disconnect
        await manager.disconnect(channel, client_id)


# Export public API
__all__ = [
    "SSEEvent",
    "SSEConnectionManager",
    "SSEBroadcaster",
    "get_sse_manager",
    "get_sse_broadcaster",
    "sse_event_generator",
]
