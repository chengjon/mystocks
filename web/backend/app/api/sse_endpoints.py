"""
SSE API Endpoints for Real-time Updates
Week 2 Day 3 - SSE Real-time Push Implementation

Provides Server-Sent Events endpoints for streaming real-time updates to frontend:
- /api/v1/sse/training - Model training progress
- /api/v1/sse/backtest - Backtest execution progress
- /api/v1/sse/alerts - Risk alert notifications
- /api/v1/sse/dashboard - Dashboard data updates

Usage (JavaScript):
    const eventSource = new EventSource('/api/v1/sse/training');
    eventSource.addEventListener('training_progress', (event) => {
        const data = JSON.parse(event.data);
        console.log('Training progress:', data.progress);
    });
"""

from fastapi import APIRouter, Request, Query
from sse_starlette.sse import EventSourceResponse
from typing import Optional
import logging

from app.core.sse_manager import sse_event_generator, get_sse_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/sse", tags=["SSE实时推送"])


@router.get("/training")
async def sse_training_stream(
    request: Request,
    client_id: Optional[str] = Query(None, description="客户端ID（可选，自动生成）"),
):
    """
    SSE endpoint for model training progress updates

    **Event Types:**
    - `connected`: Initial connection confirmation
    - `training_progress`: Training progress update
    - `ping`: Keepalive heartbeat (every 30s)

    **Event Data Structure:**
    ```json
    {
        "event": "training_progress",
        "data": {
            "task_id": "training-uuid",
            "progress": 45.5,
            "status": "running",
            "message": "Training epoch 10/100",
            "metrics": {
                "loss": 0.023,
                "accuracy": 0.95
            }
        },
        "timestamp": "2025-10-24T14:30:00Z"
    }
    ```

    **Example (JavaScript):**
    ```javascript
    const eventSource = new EventSource('/api/v1/sse/training');

    eventSource.addEventListener('training_progress', (event) => {
        const data = JSON.parse(event.data);
        updateProgressBar(data.data.progress);
        updateMetrics(data.data.metrics);
    });

    eventSource.addEventListener('error', () => {
        console.error('SSE connection error');
        eventSource.close();
    });
    ```
    """
    return EventSourceResponse(
        sse_event_generator(request, channel="training", client_id=client_id),
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )


@router.get("/backtest")
async def sse_backtest_stream(
    request: Request,
    client_id: Optional[str] = Query(None, description="客户端ID（可选，自动生成）"),
):
    """
    SSE endpoint for backtest execution progress updates

    **Event Types:**
    - `connected`: Initial connection confirmation
    - `backtest_progress`: Backtest progress update
    - `ping`: Keepalive heartbeat (every 30s)

    **Event Data Structure:**
    ```json
    {
        "event": "backtest_progress",
        "data": {
            "backtest_id": "backtest-uuid",
            "progress": 67.8,
            "status": "running",
            "message": "Simulating 2024-06-15",
            "current_date": "2024-06-15",
            "results": {
                "total_return": 0.15,
                "sharpe_ratio": 1.8,
                "max_drawdown": -0.08
            }
        },
        "timestamp": "2025-10-24T14:30:00Z"
    }
    ```

    **Example (JavaScript):**
    ```javascript
    const eventSource = new EventSource('/api/v1/sse/backtest');

    eventSource.addEventListener('backtest_progress', (event) => {
        const data = JSON.parse(event.data);
        updateBacktestProgress(data.data.progress);
        updateCurrentDate(data.data.current_date);
        if (data.data.results) {
            updateResultsChart(data.data.results);
        }
    });
    ```
    """
    return EventSourceResponse(
        sse_event_generator(request, channel="backtest", client_id=client_id),
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/alerts")
async def sse_alerts_stream(
    request: Request,
    client_id: Optional[str] = Query(None, description="客户端ID（可选，自动生成）"),
):
    """
    SSE endpoint for risk alert notifications

    **Event Types:**
    - `connected`: Initial connection confirmation
    - `risk_alert`: Risk alert notification
    - `ping`: Keepalive heartbeat (every 30s)

    **Event Data Structure:**
    ```json
    {
        "event": "risk_alert",
        "data": {
            "alert_type": "var_exceeded",
            "severity": "high",
            "message": "VaR exceeded threshold",
            "metric_name": "var_95",
            "metric_value": 0.06,
            "threshold": 0.05,
            "entity_type": "portfolio",
            "entity_id": "portfolio-123"
        },
        "timestamp": "2025-10-24T14:30:00Z"
    }
    ```

    **Severity Levels:**
    - `low`: Informational alerts
    - `medium`: Warning alerts
    - `high`: Important alerts requiring attention
    - `critical`: Critical alerts requiring immediate action

    **Example (JavaScript):**
    ```javascript
    const eventSource = new EventSource('/api/v1/sse/alerts');

    eventSource.addEventListener('risk_alert', (event) => {
        const data = JSON.parse(event.data);
        showNotification({
            title: data.data.message,
            severity: data.data.severity,
            details: `${data.data.metric_name}: ${data.data.metric_value}`
        });
    });
    ```
    """
    return EventSourceResponse(
        sse_event_generator(request, channel="alerts", client_id=client_id),
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/dashboard")
async def sse_dashboard_stream(
    request: Request,
    client_id: Optional[str] = Query(None, description="客户端ID（可选，自动生成）"),
):
    """
    SSE endpoint for real-time dashboard updates

    **Event Types:**
    - `connected`: Initial connection confirmation
    - `dashboard_update`: Dashboard data update
    - `ping`: Keepalive heartbeat (every 30s)

    **Event Data Structure:**
    ```json
    {
        "event": "dashboard_update",
        "data": {
            "update_type": "metrics",
            "data": {
                "total_value": 1500000.0,
                "daily_return": 0.025,
                "positions_count": 15
            }
        },
        "timestamp": "2025-10-24T14:30:00Z"
    }
    ```

    **Update Types:**
    - `metrics`: Portfolio metrics update
    - `positions`: Positions update
    - `orders`: Orders update
    - `market`: Market data update

    **Example (JavaScript):**
    ```javascript
    const eventSource = new EventSource('/api/v1/sse/dashboard');

    eventSource.addEventListener('dashboard_update', (event) => {
        const data = JSON.parse(event.data);

        switch (data.data.update_type) {
            case 'metrics':
                updatePortfolioMetrics(data.data.data);
                break;
            case 'positions':
                updatePositionsTable(data.data.data);
                break;
            case 'orders':
                updateOrdersTable(data.data.data);
                break;
        }
    });
    ```
    """
    return EventSourceResponse(
        sse_event_generator(request, channel="dashboard", client_id=client_id),
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/status")
async def sse_status():
    """
    Get SSE server status

    Returns:
        Connection statistics for all channels
    """
    manager = get_sse_manager()

    return {
        "status": "active",
        "total_connections": manager.get_connection_count(),
        "channels": {
            channel: {
                "connection_count": manager.get_connection_count(channel),
                "clients": manager.get_clients(channel),
            }
            for channel in manager.get_channels()
        },
    }


# Export router
__all__ = ["router"]
