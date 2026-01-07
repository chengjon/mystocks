"""
Data Source Management Module

Provides unified management of multiple data sources including:
- DataSourceRegistry: Central registry for data source configurations
- DataSourceHealthMonitor: Health monitoring and metrics
- MultiSourceLoadBalancer: Load balancing and failover
"""

from .registry import (
    DataSourceRegistry,
    DataSourceConfig,
    DataSourceInfo,
    DataSourceType,
    HealthStatus,
    HealthReport,
)

from .health import (
    DataSourceHealthMonitor,
    HealthCheckMixin,
    DATASOURCE_REQUESTS_TOTAL,
    DATASOURCE_LATENCY_SECONDS,
    DATASOURCE_HEALTH_STATUS,
    DATASOURCE_LATENCY_MS,
)

from .loadbalancer import MultiSourceLoadBalancer, LoadBalancerConfig

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
