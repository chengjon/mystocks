"""
WebSocket Connection Manager
============================

Manages WebSocket connections for real-time event broadcasting.

Features:
- Connection tracking by user/session
- Heartbeat detection
- Automatic cleanup on disconnect
- Channel-based broadcasting

Version: 1.0.0
Author: MyStocks Project
"""

import logging
import asyncio
from typing import Dict, Set, Optional, List
from datetime import datetime, timedelta
from fastapi import WebSocket
from json import dumps as json_dumps

from app.models.event_models import BaseEvent, EventChannels


logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    WebSocket connection manager

    Manages active WebSocket connections and provides broadcasting capabilities.
    """

    def __init__(self):
        # Active connections: {connection_id: WebSocket}
        self.active_connections: Dict[str, WebSocket] = {}

        # Connection metadata: {connection_id: metadata}
        self.connection_metadata: Dict[str, Dict] = {}

        # Channel subscriptions: {channel: Set[connection_id]}
        self.channel_subscriptions: Dict[str, Set[str]] = {}

        # User connections: {user_id: Set[connection_id]}
        self.user_connections: Dict[str, Set[str]] = {}

        # Heartbeat tracking: {connection_id: last_heartbeat}
        self.last_heartbeat: Dict[str, datetime] = {}

        # Heartbeat check interval (seconds)
        self.heartbeat_interval = 30

        # Heartbeat timeout (seconds)
        self.heartbeat_timeout = 60

        # Background task for heartbeat checking
        self._heartbeat_task: Optional[asyncio.Task] = None

    async def connect(
        self,
        websocket: WebSocket,
        connection_id: str,
        user_id: Optional[str] = None,
        subscribe_channels: Optional[List[str]] = None
    ):
        """
        Accept a new WebSocket connection

        Args:
            websocket: WebSocket connection
            connection_id: Unique connection identifier
            user_id: Optional user ID
            subscribe_channels: Optional list of channels to auto-subscribe
        """
        await websocket.accept()

        # Store connection
        self.active_connections[connection_id] = websocket
        self.last_heartbeat[connection_id] = datetime.utcnow()

        # Store metadata
        self.connection_metadata[connection_id] = {
            "connected_at": datetime.utcnow(),
            "user_id": user_id,
            "remote_addr": websocket.client.host if websocket.client else None
        }

        # Track user connection
        if user_id:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = set()
            self.user_connections[user_id].add(connection_id)

        # Auto-subscribe to channels
        if subscribe_channels:
            for channel in subscribe_channels:
                self.subscribe(connection_id, channel)

        logger.info(f"WebSocket connected: {connection_id} (user: {user_id})")

        # Send welcome message
        await self.send_personal_message({
            "type": "connected",
            "connection_id": connection_id,
            "timestamp": datetime.utcnow().isoformat()
        }, connection_id)

        # Start heartbeat checker if not running
        if self._heartbeat_task is None:
            self._heartbeat_task = asyncio.create_task(self._heartbeat_checker())

    def disconnect(self, connection_id: str):
        """
        Remove a WebSocket connection

        Args:
            connection_id: Connection identifier
        """
        # Remove from active connections
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]

        # Remove from heartbeat tracking
        if connection_id in self.last_heartbeat:
            del self.last_heartbeat[connection_id]

        # Remove from user connections
        metadata = self.connection_metadata.get(connection_id, {})
        user_id = metadata.get("user_id")
        if user_id and user_id in self.user_connections:
            self.user_connections[user_id].discard(connection_id)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]

        # Remove from all channel subscriptions
        for channel in list(self.channel_subscriptions.keys()):
            self.unsubscribe(connection_id, channel)

        # Remove metadata
        if connection_id in self.connection_metadata:
            del self.connection_metadata[connection_id]

        logger.info(f"WebSocket disconnected: {connection_id} (user: {user_id})")

    def subscribe(self, connection_id: str, channel: str):
        """
        Subscribe a connection to a channel

        Args:
            connection_id: Connection identifier
            channel: Channel name
        """
        if connection_id not in self.active_connections:
            logger.warning(f"Cannot subscribe {connection_id} to {channel}: connection not found")
            return

        if channel not in self.channel_subscriptions:
            self.channel_subscriptions[channel] = set()

        self.channel_subscriptions[channel].add(connection_id)
        logger.debug(f"Connection {connection_id} subscribed to {channel}")

    def unsubscribe(self, connection_id: str, channel: str):
        """
        Unsubscribe a connection from a channel

        Args:
            connection_id: Connection identifier
            channel: Channel name
        """
        if channel in self.channel_subscriptions:
            self.channel_subscriptions[channel].discard(connection_id)
            if not self.channel_subscriptions[channel]:
                del self.channel_subscriptions[channel]
            logger.debug(f"Connection {connection_id} unsubscribed from {channel}")

    async def send_personal_message(self, message: dict, connection_id: str):
        """
        Send a message to a specific connection

        Args:
            message: Message to send (will be JSON serialized)
            connection_id: Connection identifier
        """
        if connection_id in self.active_connections:
            try:
                websocket = self.active_connections[connection_id]
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send message to {connection_id}: {e}")
                self.disconnect(connection_id)
        else:
            logger.warning(f"Cannot send message to {connection_id}: connection not found")

    async def broadcast(self, message: dict, channel: str):
        """
        Broadcast a message to all subscribers of a channel

        Args:
            message: Message to broadcast (will be JSON serialized)
            channel: Channel name
        """
        if channel not in self.channel_subscriptions:
            logger.debug(f"No subscribers for channel {channel}")
            return

        # Get subscribers
        subscribers = self.channel_subscriptions[channel].copy()
        if not subscribers:
            return

        # Broadcast to all subscribers
        failed_connections = []
        for connection_id in subscribers:
            if connection_id not in self.active_connections:
                failed_connections.append(connection_id)
                continue

            try:
                websocket = self.active_connections[connection_id]
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Failed to broadcast to {connection_id}: {e}")
                failed_connections.append(connection_id)

        # Clean up failed connections
        for connection_id in failed_connections:
            self.disconnect(connection_id)

    async def broadcast_to_user(self, message: dict, user_id: str):
        """
        Broadcast a message to all connections of a specific user

        Args:
            message: Message to broadcast
            user_id: User identifier
        """
        if user_id not in self.user_connections:
            logger.debug(f"No connections for user {user_id}")
            return

        connections = self.user_connections[user_id].copy()
        for connection_id in connections:
            await self.send_personal_message(message, connection_id)

    async def broadcast_event(self, event: BaseEvent, channel: str):
        """
        Broadcast a typed event to a channel

        Args:
            event: Event model (will be converted to dict)
            channel: Channel name
        """
        message = event.model_dump()
        await self.broadcast(message, channel)

    async def update_heartbeat(self, connection_id: str):
        """
        Update heartbeat timestamp for a connection

        Args:
            connection_id: Connection identifier
        """
        if connection_id in self.active_connections:
            self.last_heartbeat[connection_id] = datetime.utcnow()

    async def _heartbeat_checker(self):
        """
        Background task to check for stale connections
        """
        while self.active_connections:
            try:
                now = datetime.utcnow()
                stale_connections = []

                for connection_id, last_heartbeat in self.last_heartbeat.items():
                    # Check if connection is stale
                    if (now - last_heartbeat).total_seconds() > self.heartbeat_timeout:
                        stale_connections.append(connection_id)

                # Disconnect stale connections
                for connection_id in stale_connections:
                    logger.warning(f"Disconnecting stale connection: {connection_id}")
                    self.disconnect(connection_id)

                # Sleep until next check
                await asyncio.sleep(self.heartbeat_interval)

            except asyncio.CancelledError:
                logger.info("Heartbeat checker task cancelled")
                break
            except Exception as e:
                logger.error(f"Error in heartbeat checker: {e}")
                await asyncio.sleep(self.heartbeat_interval)

        # Task completed (no active connections)
        self._heartbeat_task = None

    def get_connection_count(self) -> int:
        """Get total number of active connections"""
        return len(self.active_connections)

    def get_user_connection_count(self, user_id: str) -> int:
        """Get number of active connections for a user"""
        return len(self.user_connections.get(user_id, set()))

    def get_channel_subscriber_count(self, channel: str) -> int:
        """Get number of subscribers for a channel"""
        return len(self.channel_subscriptions.get(channel, set()))

    def get_stats(self) -> dict:
        """Get connection manager statistics"""
        return {
            "total_connections": len(self.active_connections),
            "total_users": len(self.user_connections),
            "total_channels": len(self.channel_subscriptions),
            "channels": {
                channel: len(subscribers)
                for channel, subscribers in self.channel_subscriptions.items()
            }
        }


# Global connection manager instance
manager = ConnectionManager()
