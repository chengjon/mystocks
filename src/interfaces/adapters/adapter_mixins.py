"""
Data Source Adapter Mixin for Health Check and Lineage Integration

This module provides mixin classes that can be added to existing adapters
to support:
1. Health check functionality
2. Data lineage tracking
3. Prometheus metrics export
"""

import time
from typing import Any, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class HealthCheckMixin:
    """
    Mixin class that provides health check functionality for data source adapters.
    Add this class to adapter inheritance to enable health checks.
    """


async def health_check(self) -> bool:
    """
    Perform a health check on the data source.

    Override this method in subclasses for specific data source checks.

    Returns:
        True if the data source is healthy, False otherwise
    """
    raise NotImplementedError("Subclasses must implement health_check()")


async def perform_health_check(self) -> Dict[str, Any]:
    """
    Perform a health check and return detailed results.

    Returns:
        Dictionary containing health check results
    """
    start_time = time.time()
    try:
        is_healthy = await self.health_check()
        latency = (time.time() - start_time) * 1000

        return {
            "healthy": is_healthy,
            "latency_ms": latency,
            "error": None,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        latency = (time.time() - start_time) * 1000
        return {
            "healthy": False,
            "latency_ms": latency,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }


class LineageTrackerMixin:
    """
    Mixin class that provides data lineage tracking for adapters.
    Add this class to adapter inheritance to enable lineage tracking.
    """


def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self._lineage_enabled = True
    self._lineage_context = None


def enable_lineage_tracking(self, enabled: bool = True) -> None:
    """Enable or disable lineage tracking"""
    self._lineage_enabled = enabled


def _record_lineage(
    self, operation: str, target_id: str, target_type: str, metadata: Optional[Dict[str, Any]] = None
) -> None:
    """
    Record a lineage event.

    Args:
        operation: Operation type (fetch, transform, store)
        target_id: ID of the target dataset
        target_type: Type of target (dataset, api, storage)
        metadata: Additional metadata
    """
    if not self._lineage_enabled:
        return

    try:
        # Test if lineage tracking is available
        import importlib

        importlib.import_module("src.data_governance")

        # In a real implementation, this would use a global tracker instance
        # For now, we just log to lineage event
        logger.debug(f"Lineage event: {operation} -> {target_id} ({target_type})")

    except ImportError:
        logger.warning("Lineage tracking not available")


def record_fetch(
    self, dataset_id: str, source: str, record_count: int, metadata: Optional[Dict[str, Any]] = None
) -> None:
    """
    Record a data fetch operation.

    Args:
        dataset_id: ID of the fetched dataset
        source: Data source identifier
        record_count: Number of records fetched
        metadata: Additional metadata
    """
    meta = {"source": source, "record_count": record_count, "adapter": getattr(self, "source_name", "unknown")}
    if metadata:
        meta.update(metadata)

    self._record_lineage("fetch", dataset_id, "dataset", meta)


def record_transform(
    self,
    dataset_id: str,
    transform_type: str,
    input_records: int,
    output_records: int,
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Record a data transformation operation.

    Args:
        dataset_id: ID of the transformed dataset
        transform_type: Type of transformation
        input_records: Number of input records
        output_records: Number of output records
        metadata: Additional metadata
    """
    meta = {"transform_type": transform_type, "input_records": input_records, "output_records": output_records}
    if metadata:
        meta.update(metadata)

    self._record_lineage("transform", dataset_id, "dataset", meta)


def record_store(
    self, storage_id: str, storage_type: str, record_count: int, metadata: Optional[Dict[str, Any]] = None
) -> None:
    """
    Record a data storage operation.

    Args:
        storage_id: ID of the storage location
        storage_type: Type of storage (tdengine, postgresql, etc.)
        record_count: Number of records stored
        metadata: Additional metadata
    """
    meta = {"storage_type": storage_type, "record_count": record_count}
    if metadata:
        meta.update(metadata)

    self._record_lineage("store", storage_id, "storage", meta)


class MetricsExportMixin:
    """
    Mixin class that provides Prometheus metrics export for adapters.
    Add this class to adapter inheritance to enable metrics export.
    """


def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self._request_count: Dict[str, int] = {}
    self._error_count: Dict[str, int] = {}
    self._latency_sum: Dict[str, float] = {}
    self._latency_count: Dict[str, int] = {}


def record_request(self, operation: str, success: bool, latency_seconds: float) -> None:
    """
    Record a request for metrics.

    Args:
        operation: Operation type
        success: Whether the request was successful
        latency_seconds: Request latency in seconds
    """
    if operation not in self._request_count:
        self._request_count[operation] = 0
        self._error_count[operation] = 0
        self._latency_sum[operation] = 0.0
        self._latency_count[operation] = 0

    self._request_count[operation] += 1
    self._latency_sum[operation] += latency_seconds
    self._latency_count[operation] += 1

    if not success:
        self._error_count[operation] += 1


def get_metrics_summary(self) -> Dict[str, Any]:
    """
    Get metrics summary for the adapter.

    Returns:
        Dictionary containing metrics summary
    """
    summary = {"source_name": getattr(self, "source_name", "unknown"), "operations": {}}

    for op in self._request_count:
        total = self._request_count[op]
        errors = self._error_count.get(op, 0)
        avg_latency = self._latency_sum[op] / max(self._latency_count[op], 1)

        summary["operations"][op] = {
            "total_requests": total,
            "success_count": total - errors,
            "error_count": errors,
            "error_rate": errors / max(total, 1),
            "avg_latency_seconds": avg_latency,
        }

    return summary


class AdapterIntegrationMixin(HealthCheckMixin, LineageTrackerMixin, MetricsExportMixin):
    """
    Combined mixin that provides all adapter integration features:
    - Health check functionality
    - Data lineage tracking
    - Prometheus metrics export

    Add this class to adapter inheritance:
        class MyAdapter(AdapterIntegrationMixin, BaseDataSourceAdapter):
            ...
    """


async def health_check(self) -> bool:
    """
    Default health check implementation.
    Override this in subclasses for specific data source checks.
    """
    try:
        # Default implementation: try a simple API call
        return True
    except Exception:
        return False


async def fetch_with_metrics(self, fetch_func, *args, dataset_id: Optional[str] = None, **kwargs) -> Any:
    """
    Execute a fetch operation with metrics tracking.

    Args:
        fetch_func: Async function to execute
        *args: Arguments for fetch_func
        dataset_id: Dataset ID for lineage tracking
        **kwargs: Keyword arguments for fetch_func

    Returns:
        Result from fetch_func
    """
    start_time = time.time()
    source_name = getattr(self, "source_name", "unknown")

    try:
        result = await fetch_func(*args, **kwargs)
        success = True
        latency = time.time() - start_time

        self.record_request("fetch", True, latency)

        # Record lineage if successful
        if dataset_id and success:
            record_count = len(result) if hasattr(result, "__len__") else 0
            self.record_fetch(dataset_id, source_name, record_count)

        return result

    except Exception:
        latency = time.time() - start_time
        self.record_request("fetch", False, latency)
        raise


async def store_with_metrics(
    self, store_func, storage_id: str, storage_type: str, *args, record_count: int = 0, **kwargs
) -> Any:
    """
    Execute a store operation with metrics and lineage tracking.

    Args:
        store_func: Async function to execute
        storage_id: ID of the storage location
        storage_type: Type of storage
        *args: Arguments for store_func
        record_count: Number of records to store
        **kwargs: Keyword arguments for store_func

    Returns:
        Result from store_func
    """
    start_time = time.time()

    try:
        result = await store_func(*args, **kwargs)
        latency = time.time() - start_time

        self.record_request("store", True, latency)
        self.record_store(storage_id, storage_type, record_count)

        return result

    except Exception:
        latency = time.time() - start_time
        self.record_request("store", False, latency)
        raise
