"""
Data Source Management API

RESTful API endpoints for managing data sources,
including CRUD operations and health monitoring.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
import logging

from src.core.datasource import (
    DataSourceRegistry,
    DataSourceConfig,
    DataSourceType,
    DataSourceHealthMonitor,
    HealthStatus,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/datasources", tags=["Data Sources"])


class DataSourceCreateRequest(BaseModel):
    """Request model for creating a data source"""

    source_id: str = Field(..., description="Unique identifier for the data source")
    name: str = Field(..., description="Display name for the data source")
    source_type: str = Field(..., description="Type of data source (akshare, tushare, etc.)")
    api_key: Optional[str] = Field(None, description="API key for authentication")
    base_url: Optional[str] = Field(None, description="Base URL for API requests")
    timeout: int = Field(default=30, description="Request timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    retry_delay: float = Field(default=1.0, description="Delay between retries")
    weight: int = Field(default=100, ge=1, le=100, description="Load balancing weight")
    enabled: bool = Field(default=True, description="Whether the data source is enabled")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class DataSourceUpdateRequest(BaseModel):
    """Request model for updating a data source"""

    name: Optional[str] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    timeout: Optional[int] = None
    max_retries: Optional[int] = None
    retry_delay: Optional[float] = None
    weight: Optional[int] = None
    enabled: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class DataSourceResponse(BaseModel):
    """Response model for data source"""

    source_id: str
    name: str
    source_type: str
    health_status: str
    last_check: Optional[datetime] = None
    enabled: bool
    weight: int
    metrics: Dict[str, Any] = {}


class HealthStatusResponse(BaseModel):
    """Response model for health status"""

    source_id: str
    status: str
    latency_ms: float
    last_check: datetime
    error: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class MetricsSummaryResponse(BaseModel):
    """Response model for metrics summary"""

    source_id: str
    total_requests: int
    success_rate: float
    avg_latency_ms: float
    p99_latency_ms: float


async def get_registry() -> DataSourceRegistry:
    """Dependency to get data source registry"""
    # This should be injected from the main app
    from src.core.datasource.registry import DataSourceRegistry

    registry = DataSourceRegistry()
    await registry.connect()
    return registry


async def get_monitor() -> DataSourceHealthMonitor:
    """Dependency to get health monitor"""
    from src.core.datasource.registry import DataSourceRegistry
    from src.core.datasource.health import DataSourceHealthMonitor

    registry = DataSourceRegistry()
    await registry.connect()
    return DataSourceHealthMonitor(registry)


@router.get("", response_model=List[DataSourceResponse])
async def list_datasources(
    registry: DataSourceRegistry = Depends(get_registry),
) -> List[DataSourceResponse]:
    """List all registered data sources"""
    sources = await registry.list_sources()
    return [
        DataSourceResponse(
            source_id=s.source_id,
            name=s.name,
            source_type=s.source_type.value,
            health_status=s.health_status.value,
            last_check=s.last_check,
            enabled=s.config.enabled,
            weight=s.config.weight,
            metrics=s.metrics,
        )
        for s in sources
    ]


@router.get("/{source_id}", response_model=DataSourceResponse)
async def get_datasource(source_id: str, registry: DataSourceRegistry = Depends(get_registry)) -> DataSourceResponse:
    """Get details of a specific data source"""
    config = await registry.get_config(source_id)
    if not config:
        raise HTTPException(status_code=404, detail="Data source not found")

    health = await registry.get_health_status(source_id)

    return DataSourceResponse(
        source_id=source_id,
        name=config.name,
        source_type=config.source_type.value,
        health_status=health.status.value if health else HealthStatus.UNKNOWN.value,
        last_check=health.last_check if health else None,
        enabled=config.enabled,
        weight=config.weight,
        metrics={},
    )


@router.post("", response_model=DataSourceResponse, status_code=201)
async def create_datasource(
    request: DataSourceCreateRequest,
    registry: DataSourceRegistry = Depends(get_registry),
) -> DataSourceResponse:
    """Register a new data source"""
    # Check if already exists
    existing = await registry.get_config(request.source_id)
    if existing:
        raise HTTPException(status_code=409, detail="Data source already exists")

    try:
        config = DataSourceConfig(
            source_id=request.source_id,
            name=request.name,
            source_type=DataSourceType(request.source_type),
            api_key=request.api_key,
            base_url=request.base_url,
            timeout=request.timeout,
            max_retries=request.max_retries,
            retry_delay=request.retry_delay,
            weight=request.weight,
            enabled=request.enabled,
            metadata=request.metadata,
        )

        success = await registry.register(config)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to register data source")

        return DataSourceResponse(
            source_id=request.source_id,
            name=request.name,
            source_type=request.source_type,
            health_status=HealthStatus.UNKNOWN.value,
            enabled=request.enabled,
            weight=request.weight,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{source_id}", response_model=DataSourceResponse)
async def update_datasource(
    source_id: str,
    request: DataSourceUpdateRequest,
    registry: DataSourceRegistry = Depends(get_registry),
) -> DataSourceResponse:
    """Update a data source configuration"""
    config = await registry.get_config(source_id)
    if not config:
        raise HTTPException(status_code=404, detail="Data source not found")

    # Update fields
    update_data = request.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(config, key, value)

    success = await registry.register(config)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update data source")

    health = await registry.get_health_status(source_id)

    return DataSourceResponse(
        source_id=source_id,
        name=config.name,
        source_type=config.source_type.value,
        health_status=health.status.value if health else HealthStatus.UNKNOWN.value,
        last_check=health.last_check if health else None,
        enabled=config.enabled,
        weight=config.weight,
    )


@router.delete("/{source_id}", status_code=204)
async def delete_datasource(source_id: str, registry: DataSourceRegistry = Depends(get_registry)):
    """Unregister a data source"""
    config = await registry.get_config(source_id)
    if not config:
        raise HTTPException(status_code=404, detail="Data source not found")

    success = await registry.unregister(source_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete data source")


@router.get("/{source_id}/health", response_model=HealthStatusResponse)
async def get_health_status(
    source_id: str, registry: DataSourceRegistry = Depends(get_registry)
) -> HealthStatusResponse:
    """Get health status of a data source"""
    report = await registry.get_health_status(source_id)
    if not report:
        raise HTTPException(status_code=404, detail="Data source not found")

    return HealthStatusResponse(
        source_id=report.source_id,
        status=report.status.value,
        latency_ms=report.latency_ms,
        last_check=report.last_check,
        error=report.error,
        details=report.details,
    )


@router.post("/{source_id}/check", response_model=HealthStatusResponse)
async def trigger_health_check(
    source_id: str, monitor: DataSourceHealthMonitor = Depends(get_monitor)
) -> HealthStatusResponse:
    """Manually trigger a health check for a data source"""
    report = await monitor.check_health(source_id)
    return HealthStatusResponse(
        source_id=report.source_id,
        status=report.status.value,
        latency_ms=report.latency_ms,
        last_check=report.last_check,
        error=report.error,
        details=report.details,
    )


@router.post("/check-all")
async def trigger_all_health_checks(
    monitor: DataSourceHealthMonitor = Depends(get_monitor),
) -> Dict[str, Any]:
    """Trigger health checks for all data sources"""
    results = await monitor.check_all_sources()
    return {
        "checked": len(results),
        "results": {k: {"status": v.status.value, "latency_ms": v.latency_ms} for k, v in results.items()},
    }


@router.get("/{source_id}/metrics", response_model=MetricsSummaryResponse)
async def get_metrics(source_id: str, registry: DataSourceRegistry = Depends(get_registry)) -> MetricsSummaryResponse:
    """Get metrics summary for a data source"""
    config = await registry.get_config(source_id)
    if not config:
        raise HTTPException(status_code=404, detail="Data source not found")

    # In a real implementation, this would query Prometheus
    # For now, return placeholder data
    return MetricsSummaryResponse(
        source_id=source_id,
        total_requests=0,
        success_rate=100.0,
        avg_latency_ms=0.0,
        p99_latency_ms=0.0,
    )
