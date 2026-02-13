"""
Data Source Health Monitor

Provides real-time monitoring of data source availability, latency,
and success rate with Prometheus metrics integration.
"""

import asyncio
import logging
import time
from datetime import datetime, timezone
from typing import Callable, Dict, Optional

from prometheus_client import Counter, Gauge, Histogram

from .registry import DataSourceRegistry, HealthReport, HealthStatus

logger = logging.getLogger(__name__)

# Prometheus metrics
DATASOURCE_REQUESTS_TOTAL = Counter(
    "datasource_requests_total",
    "Total number of data source requests",
    ["source_id", "status", "operation"],
)

DATASOURCE_LATENCY_SECONDS = Histogram(
    "datasource_latency_seconds",
    "Latency of data source requests in seconds",
    ["source_id", "operation"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

DATASOURCE_HEALTH_STATUS = Gauge(
    "datasource_health_status",
    "Health status of data source (1=HEALTHY, 0=UNHEALTHY/ERROR)",
    ["source_id"],
)

DATASOURCE_LATENCY_MS = Gauge("datasource_latency_ms", "Last measured latency in milliseconds", ["source_id"])


class DataSourceHealthMonitor:
    """
    Health monitor for data sources that performs active health checks
    and tracks metrics.
    """

    def __init__(self, registry: DataSourceRegistry):
        self._registry = registry
        self._health_checks: Dict[str, Callable] = {}
        self._running = False
        self._check_interval = 30  # seconds
        self._tasks: Dict[str, asyncio.Task] = {}

    def register_health_check(self, source_type: str, check_func: Callable) -> None:
        """
        Register a health check function for a specific data source type.

        Args:
            source_type: Type of data source (e.g., 'akshare', 'tushare')
            check_func: Async function that returns True if healthy
        """
        self._health_checks[source_type] = check_func
        logger.info("Registered health check for %(source_type)s")

    async def check_health(self, source_id: str) -> HealthReport:
        """
        Perform a health check on a specific data source.

        Args:
            source_id: Unique identifier of the data source

        Returns:
            HealthReport with health status
        """
        config = await self._registry.get_config(source_id)
        if not config:
            return HealthReport(
                source_id=source_id,
                status=HealthStatus.UNKNOWN,
                error="Data source not found",
            )

        if not config.enabled:
            return HealthReport(
                source_id=source_id,
                status=HealthStatus.UNKNOWN,
                error="Data source is disabled",
            )

        start_time = time.time()
        try:
            check_func = self._health_checks.get(config.source_type.value)
            if check_func:
                result = await asyncio.wait_for(check_func(config), timeout=5.0)
            else:
                result = True

            latency = time.time() - start_time
            status = HealthStatus.HEALTHY if result else HealthStatus.UNHEALTHY

            report = HealthReport(
                source_id=source_id,
                status=status,
                latency_ms=latency * 1000,
                last_check=datetime.now(timezone.utc),
                details={"success": result},
            )

            # Update metrics
            DATASOURCE_REQUESTS_TOTAL.labels(
                source_id=source_id,
                status="success" if result else "failed",
                operation="health_check",
            ).inc()

            await self._registry.update_health_status(source_id, report)
            self._update_gauges(source_id, report)

            return report

        except asyncio.TimeoutError:
            latency = time.time() - start_time
            report = HealthReport(
                source_id=source_id,
                status=HealthStatus.UNHEALTHY,
                latency_ms=latency * 1000,
                last_check=datetime.now(timezone.utc),
                error="Health check timed out",
            )

            DATASOURCE_REQUESTS_TOTAL.labels(source_id=source_id, status="timeout", operation="health_check").inc()

            await self._registry.update_health_status(source_id, report)
            self._update_gauges(source_id, report)

            return report

        except Exception as e:
            latency = time.time() - start_time
            report = HealthReport(
                source_id=source_id,
                status=HealthStatus.ERROR,
                latency_ms=latency * 1000,
                last_check=datetime.now(timezone.utc),
                error=str(e),
            )

            DATASOURCE_REQUESTS_TOTAL.labels(source_id=source_id, status="error", operation="health_check").inc()

            await self._registry.update_health_status(source_id, report)
            self._update_gauges(source_id, report)

            return report

    def _update_gauges(self, source_id: str, report: HealthReport) -> None:
        """Update Prometheus gauge metrics"""
        status_value = 1.0 if report.status == HealthStatus.HEALTHY else 0.0
        DATASOURCE_HEALTH_STATUS.labels(source_id=source_id).set(status_value)
        DATASOURCE_LATENCY_MS.labels(source_id=source_id).set(report.latency_ms)

    async def check_all_sources(self) -> Dict[str, HealthReport]:
        """
        Perform health checks on all registered data sources.

        Returns:
            Dictionary mapping source_id to HealthReport
        """
        sources = await self._registry.list_sources()
        results = {}

        for source in sources:
            if source.config.enabled:
                report = await self.check_health(source.source_id)
                results[source.source_id] = report

        return results

    async def start_monitoring(self, interval: int = 30) -> None:
        """
        Start continuous health monitoring for all data sources.

        Args:
            interval: Health check interval in seconds
        """
        self._running = True
        self._check_interval = interval

        while self._running:
            try:
                await self.check_all_sources()
            except Exception:
                logger.error("Error during health check cycle: %(e)s")

            await asyncio.sleep(self._check_interval)

    def stop_monitoring(self) -> None:
        """Stop health monitoring"""
        self._running = False
        for task in self._tasks.values():
            task.cancel()
        self._tasks.clear()

    async def record_request(
        self,
        source_id: str,
        operation: str,
        success: bool,
        latency: float,
        error: Optional[str] = None,
    ) -> None:
        """
        Record metrics for a data source request.

        Args:
            source_id: Data source identifier
            operation: Operation performed
            success: Whether the request was successful
            latency: Request latency in seconds
            error: Error message if request failed
        """
        status = "success" if success else "failed"

        # Update counters
        DATASOURCE_REQUESTS_TOTAL.labels(source_id=source_id, status=status, operation=operation).inc()

        # Update histogram
        DATASOURCE_LATENCY_SECONDS.labels(source_id=source_id, operation=operation).observe(latency)

        # Update gauges
        status_value = 1.0 if success else 0.0
        DATASOURCE_HEALTH_STATUS.labels(source_id=source_id).set(status_value)
        DATASOURCE_LATENCY_MS.labels(source_id=source_id).set(latency * 1000)


class HealthCheckMixin:
    """
    Mixin class that provides health check functionality for data source adapters.
    """

    async def health_check(self) -> bool:
        """
        Default health check implementation.
        Override this in subclasses for specific data source checks.

        Returns:
            True if the data source is healthy
        """
        return True

    async def perform_health_check(self) -> bool:
        """
        Perform health check with proper error handling.

        Returns:
            True if healthy, False otherwise
        """
        try:
            return await self.health_check()
        except Exception:
            return False
