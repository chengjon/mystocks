"""
WebSocket Router for Real-Time Events
======================================

Provides WebSocket endpoints for real-time event streaming.

Features:
- Task progress subscription
- Market data updates
- Indicator calculation events
- Connection management

Version: 1.0.0
Author: MyStocks Project
"""

import logging
from typing import Optional

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.services.websocket_manager import manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["websocket"])


@router.websocket("/events")
async def websocket_events(
    websocket: WebSocket, token: Optional[str] = Query(None), channels: Optional[str] = Query(None)
):
    """
    WebSocket endpoint for real-time events

    Query Parameters:
    - token: Optional authentication token
    - channels: Comma-separated list of channels to subscribe (default: all events)

    Default channels if not specified:
    - events:tasks (task progress)
    - events:indicators (indicator calculations)

    Example:
    - ws://localhost:8000/ws/events?channels=events:tasks,events:indicators
    - ws://localhost:8000/ws/events?channels=events:task:calc_1234567890
    """
    # Generate connection ID
    import time

    connection_id = f"ws_{int(time.time() * 1000)}"

    # Parse channels
    default_channels = ["events:tasks", "events:indicators"]
    if channels:
        subscribe_channels = [ch.strip() for ch in channels.split(",")]
    else:
        subscribe_channels = default_channels

    # Accept connection
    await manager.connect(
        websocket=websocket,
        connection_id=connection_id,
        user_id=token,  # Use token as user_id for simplicity (should validate in production)
        subscribe_channels=subscribe_channels,
    )

    logger.info("WebSocket client connected: %(connection_id)s, channels: %(subscribe_channels)s")

    try:
        # Keep connection alive and handle incoming messages
        while True:
            # Receive message from client
            data = await websocket.receive_json()

            # Handle different message types
            message_type = data.get("type")

            if message_type == "heartbeat":
                # Update heartbeat
                await manager.update_heartbeat(connection_id)

            elif message_type == "subscribe":
                # Subscribe to additional channels
                new_channels = data.get("channels", [])
                for channel in new_channels:
                    manager.subscribe(connection_id, channel)

            elif message_type == "unsubscribe":
                # Unsubscribe from channels
                remove_channels = data.get("channels", [])
                for channel in remove_channels:
                    manager.unsubscribe(connection_id, channel)

            elif message_type == "ping":
                # Respond with pong
                await manager.send_personal_message({"type": "pong"}, connection_id)

            else:
                logger.warning("Unknown message type: %(message_type)s")

    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected: %(connection_id)s")
    except Exception:
        logger.error("WebSocket error for %(connection_id)s: %(e)s")
    finally:
        manager.disconnect(connection_id)


@router.get("/stats")
async def get_websocket_stats():
    """
    Get WebSocket connection statistics

    Returns:
    - Total active connections
    - Total unique users
    - Total channels
    - Per-channel subscriber counts
    """
    return manager.get_stats()


@router.get("/channels")
async def list_channels():
    """
    List available event channels

    Returns channel descriptions and recommended usage
    """

    return {
        "channels": {
            "events:tasks": {
                "description": "All task events (created, started, progress, completed, failed)",
                "example_use": "Monitor background calculation jobs",
                "event_types": ["task.created", "task.started", "task.progress", "task.completed", "task.failed"],
            },
            "events:task:{task_id}": {
                "description": "Specific task events (subscribe to individual task)",
                "example_use": "Monitor a specific calculation job",
                "event_types": ["task.progress", "task.completed", "task.failed"],
            },
            "events:market": {
                "description": "All market data events",
                "example_use": "Real-time price updates",
                "event_types": ["market.data.update", "market.price.update"],
            },
            "events:market:{stock_code}": {
                "description": "Specific stock market events",
                "example_use": "Monitor specific stock price",
                "event_types": ["market.price.update"],
            },
            "events:indicators": {
                "description": "All indicator calculation events",
                "example_use": "Track indicator calculations",
                "event_types": ["stock.indicators.completed"],
            },
            "events:system": {
                "description": "System events (heartbeat, status)",
                "example_use": "Health monitoring",
                "event_types": ["system.heartbeat"],
            },
        },
        "usage_examples": [
            "ws://localhost:8000/ws/events  # Subscribe to default channels",
            "ws://localhost:8000/ws/events?channels=events:tasks,events:indicators  # Custom channels",
            "ws://localhost:8000/ws/events?channels=events:task:calc_1234567890  # Specific task",
        ],
    }
