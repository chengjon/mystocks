"""
Event Models for Redis Pub/Sub
==============================

Standardized Pydantic models for all event messages published via Redis Pub/Sub.
Ensures type safety and makes frontend integration easier.

Version: 1.0.0
Author: MyStocks Project
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class EventType(str, Enum):
    """Event type enumeration"""
    # Task events
    TASK_CREATED = "task.created"
    TASK_STARTED = "task.started"
    TASK_PROGRESS = "task.progress"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"

    # Indicator events
    INDICATOR_CALCULATION_STARTED = "indicator.calculation.started"
    INDICATOR_CALCULATION_COMPLETED = "indicator.calculation.completed"
    INDICATOR_CALCULATION_FAILED = "indicator.calculation.failed"
    STOCK_INDICATORS_COMPLETED = "stock.indicators.completed"

    # Market events
    MARKET_DATA_UPDATE = "market.data.update"
    MARKET_PRICE_UPDATE = "market.price.update"

    # System events
    SYSTEM_HEARTBEAT = "system.heartbeat"
    SYSTEM_STATUS_CHANGED = "system.status_changed"


class TaskStatus(str, Enum):
    """Task status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class BaseEvent(BaseModel):
    """Base event model with common fields"""
    event_type: EventType = Field(..., description="Type of the event")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Event timestamp")
    version: str = Field(default="1.0", description="Event schema version")

    class Config:
        use_enum_values = True


class TaskProgressEvent(BaseEvent):
    """Task progress update event"""
    event_type: EventType = EventType.TASK_PROGRESS
    task_id: str = Field(..., description="Unique task identifier")
    task_type: str = Field(..., description="Task type (e.g., 'batch_daily')")
    status: TaskStatus = Field(..., description="Current task status")
    progress: float = Field(..., ge=0.0, le=100.0, description="Progress percentage (0-100)")
    message: str = Field(default="", description="Human-readable progress message")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional task metadata")

    # Batching optimization: processed counts
    processed: int = Field(default=0, description="Number of items processed")
    total: int = Field(default=0, description="Total number of items to process")
    failed: int = Field(default=0, description="Number of failed items")

    class Config:
        json_schema_extra = {
            "example": {
                "event_type": "task.progress",
                "task_id": "calc_1234567890",
                "task_type": "batch_daily",
                "status": "running",
                "progress": 45.5,
                "message": "Processing indicators for stock 000001",
                "processed": 2275,
                "total": 5000,
                "failed": 12
            }
        }


class TaskCompletedEvent(BaseEvent):
    """Task completed event"""
    event_type: EventType = EventType.TASK_COMPLETED
    task_id: str = Field(..., description="Unique task identifier")
    task_type: str = Field(..., description="Task type")
    status: TaskStatus = Field(..., description="Final task status")
    duration_seconds: float = Field(..., ge=0, description="Total execution time in seconds")
    result: Dict[str, Any] = Field(default_factory=dict, description="Task execution results")

    class Config:
        json_schema_extra = {
            "example": {
                "event_type": "task.completed",
                "task_id": "calc_1234567890",
                "task_type": "batch_daily",
                "status": "completed",
                "duration_seconds": 123.45,
                "result": {
                    "success": 4988,
                    "failed": 12
                }
            }
        }


class StockIndicatorsCompletedEvent(BaseEvent):
    """Stock indicators calculation completed event (Batching optimization)"""
    event_type: EventType = EventType.STOCK_INDICATORS_COMPLETED
    stock_code: str = Field(..., description="Stock symbol")
    indicators: List[str] = Field(..., description="List of calculated indicator abbreviations")
    success_count: int = Field(..., description="Number of successfully calculated indicators")
    failed_count: int = Field(default=0, description="Number of failed indicator calculations")
    calculation_time_ms: float = Field(..., ge=0, description="Total calculation time in milliseconds")
    from_cache_count: int = Field(default=0, description="Number of indicators served from cache")

    class Config:
        json_schema_extra = {
            "example": {
                "event_type": "stock.indicators.completed",
                "stock_code": "000001",
                "indicators": ["SMA", "MACD", "RSI", "BBANDS", "ATR"],
                "success_count": 5,
                "failed_count": 0,
                "calculation_time_ms": 123.45,
                "from_cache_count": 2
            }
        }


class IndicatorCalculationEvent(BaseEvent):
    """Individual indicator calculation event (for debugging)"""
    event_type: EventType = EventType.INDICATOR_CALCULATION_COMPLETED
    stock_code: str = Field(..., description="Stock symbol")
    indicator_code: str = Field(..., description="Indicator abbreviation")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Calculation parameters")
    success: bool = Field(..., description="Whether calculation succeeded")
    calculation_time_ms: float = Field(..., ge=0, description="Calculation time in milliseconds")
    from_cache: bool = Field(default=False, description="Whether result came from cache")
    error_message: Optional[str] = Field(None, description="Error message if failed")

    class Config:
        json_schema_extra = {
            "example": {
                "event_type": "indicator.calculation.completed",
                "stock_code": "000001",
                "indicator_code": "MACD",
                "parameters": {"fastperiod": 12, "slowperiod": 26},
                "success": True,
                "calculation_time_ms": 45.67,
                "from_cache": False
            }
        }


class MarketDataUpdateEvent(BaseEvent):
    """Market data update event"""
    event_type: EventType = EventType.MARKET_DATA_UPDATE
    stock_code: str = Field(..., description="Stock symbol")
    data_type: str = Field(..., description="Data type (e.g., 'quote', 'kline')")
    data: Dict[str, Any] = Field(..., description="Market data payload")

    class Config:
        json_schema_extra = {
            "example": {
                "event_type": "market.data.update",
                "stock_code": "000001",
                "data_type": "quote",
                "data": {
                    "price": 10.50,
                    "change": 0.25,
                    "change_percent": 2.44,
                    "volume": 1234567,
                    "timestamp": "2026-01-10T09:30:00Z"
                }
            }
        }


class SystemHeartbeatEvent(BaseEvent):
    """System heartbeat event"""
    event_type: EventType = EventType.SYSTEM_HEARTBEAT
    service: str = Field(..., description="Service name")
    status: str = Field(..., description="Service status (e.g., 'healthy', 'degraded')")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Service metrics")

    class Config:
        json_schema_extra = {
            "example": {
                "event_type": "system.heartbeat",
                "service": "indicator_calculator",
                "status": "healthy",
                "metrics": {
                    "cpu_usage": 45.2,
                    "memory_usage": 67.8,
                    "active_tasks": 3
                }
            }
        }


# ========== Channel Naming Constants ==========

class EventChannels:
    """
    Hierarchical channel naming convention

    Channel Structure:
    - events:tasks              - All task events (global broadcast)
    - events:task:{task_id}     - Specific task events
    - events:market             - All market data events
    - events:market:{code}      - Specific stock market events
    - events:indicators         - All indicator events
    - events:system             - System events (heartbeat, status)
    """

    TASKS_ALL = "events:tasks"
    TASK_SPECIFIC = "events:task:{task_id}"

    MARKET_ALL = "events:market"
    MARKET_SPECIFIC = "events:market:{stock_code}"

    INDICATORS_ALL = "events:indicators"

    SYSTEM = "events:system"

    @classmethod
    def task_channel(cls, task_id: str) -> str:
        """Get channel for specific task"""
        return cls.TASK_SPECIFIC.format(task_id=task_id)

    @classmethod
    def market_channel(cls, stock_code: str) -> str:
        """Get channel for specific stock"""
        return cls.MARKET_SPECIFIC.format(stock_code=stock_code)


# ========== Event Publishing Utilities ==========

def create_task_progress_event(
    task_id: str,
    task_type: str,
    status: TaskStatus,
    progress: float,
    message: str = "",
    processed: int = 0,
    total: int = 0,
    failed: int = 0,
    **metadata
) -> TaskProgressEvent:
    """Helper to create task progress event"""
    return TaskProgressEvent(
        task_id=task_id,
        task_type=task_type,
        status=status,
        progress=progress,
        message=message,
        processed=processed,
        total=total,
        failed=failed,
        metadata=metadata
    )


def create_stock_indicators_completed_event(
    stock_code: str,
    indicators: List[str],
    success_count: int,
    failed_count: int = 0,
    calculation_time_ms: float = 0,
    from_cache_count: int = 0
) -> StockIndicatorsCompletedEvent:
    """Helper to create stock indicators completed event"""
    return StockIndicatorsCompletedEvent(
        stock_code=stock_code,
        indicators=indicators,
        success_count=success_count,
        failed_count=failed_count,
        calculation_time_ms=calculation_time_ms,
        from_cache_count=from_cache_count
    )


def create_task_completed_event(
    task_id: str,
    task_type: str,
    status: TaskStatus,
    duration_seconds: float,
    **result
) -> TaskCompletedEvent:
    """Helper to create task completed event"""
    return TaskCompletedEvent(
        task_id=task_id,
        task_type=task_type,
        status=status,
        duration_seconds=duration_seconds,
        result=result
    )
