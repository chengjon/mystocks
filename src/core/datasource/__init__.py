"""
Data Source Management Module

Provides unified management of multiple data sources including:
- DataSourceRegistry: Central registry for data source configurations
- DataSourceHealthMonitor: Health monitoring and metrics
- MultiSourceLoadBalancer: Load balancing and failover
"""

from .health import (
    DATASOURCE_HEALTH_STATUS,
    DATASOURCE_LATENCY_MS,
    DATASOURCE_LATENCY_SECONDS,
    DATASOURCE_REQUESTS_TOTAL,
    DataSourceHealthMonitor,
    HealthCheckMixin,
)
from .loadbalancer import LoadBalancerConfig, MultiSourceLoadBalancer
from .registry import (
    DataSourceConfig,
    DataSourceInfo,
    DataSourceRegistry,
    DataSourceType,
    HealthReport,
    HealthStatus,
)

__all__ = [
    "DataSourceRegistry",
    "DataSourceConfig",
    "DataSourceInfo",
    "DataSourceType",
    "HealthStatus",
    "HealthReport",
    "DataSourceHealthMonitor",
    "HealthCheckMixin",
    "MultiSourceLoadBalancer",
    "LoadBalancerConfig",
    "DATASOURCE_REQUESTS_TOTAL",
    "DATASOURCE_LATENCY_SECONDS",
    "DATASOURCE_HEALTH_STATUS",
    "DATASOURCE_LATENCY_MS",
]
