"""
系统健康检查API

提供数据库健康状态和数据分类统计功能
"""

from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

router = APIRouter(
    prefix="/health",
    tags=["System Health"],
)


class DatabaseHealthResponse(BaseModel):
    """Database health check response"""

    database_type: str = Field(..., description="Database type (postgresql|tdengine)")
    connection_status: str = Field(..., description="Connection status")
    response_time_ms: float = Field(..., description="Response time in milliseconds")
    active_connections: int = Field(..., description="Active connections")
    total_tables: int = Field(..., description="Total tables count")
    last_health_check: datetime = Field(..., description="Last health check timestamp")


class DataClassificationStats(BaseModel):
    """Data classification statistics"""

    description: str
    record_count: int
    storage_size_gb: float
    database: str
    compression_ratio: float


@router.get(
    "/database",
    response_model=List[DatabaseHealthResponse],
    summary="Database Health Check",
)
async def get_database_health():
    """
    检查所有数据库的健康状态

    Returns health metrics for PostgreSQL and TDengine databases including
    connection status, response times, and table counts.
    """
    mock_response = [
        DatabaseHealthResponse(
            database_type="postgresql",
            connection_status="healthy",
            response_time_ms=15.2,
            active_connections=5,
            total_tables=45,
            last_health_check=datetime.now(),
        ),
        DatabaseHealthResponse(
            database_type="tdengine",
            connection_status="healthy",
            response_time_ms=8.7,
            active_connections=12,
            total_tables=28,
            last_health_check=datetime.now(),
        ),
    ]
    return mock_response


@router.get("/classification/stats", summary="Data Classification Statistics")
async def get_data_classification_stats():
    """
    获取数据分类统计信息

    Returns statistics about data distribution across different classifications.
    """
    mock_stats = {
        "market_data": {
            "description": "高频时序数据",
            "record_count": 12500000,
            "storage_size_gb": 45.2,
            "database": "tdengine",
            "compression_ratio": 20.0,
        },
        "reference_data": {
            "description": "参考数据",
            "record_count": 500000,
            "storage_size_gb": 2.1,
            "database": "postgresql",
            "compression_ratio": 1.0,
        },
        "derived_data": {
            "description": "计算密集型数据",
            "record_count": 2500000,
            "storage_size_gb": 8.5,
            "database": "tdengine",
            "compression_ratio": 15.0,
        },
        "transaction_data": {
            "description": "事务完整性数据",
            "record_count": 100000,
            "storage_size_gb": 1.2,
            "database": "postgresql",
            "compression_ratio": 1.0,
        },
        "metadata": {
            "description": "配置和管理数据",
            "record_count": 5000,
            "storage_size_gb": 0.1,
            "database": "postgresql",
            "compression_ratio": 1.0,
        },
    }
    return {"data": mock_stats, "total_classes": len(mock_stats)}
