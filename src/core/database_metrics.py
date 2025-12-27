"""
Database Performance Metrics and Monitoring
Provides Prometheus metrics for database operations and query performance
"""

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from prometheus_client import Counter, Gauge, Histogram, Summary

logger = logging.getLogger(__name__)

DB_POOL_SIZE = Gauge(
    "db_pool_size",
    "Database connection pool size",
    ["database", "pool_type"],
)

DB_POOL_CONNECTIONS_IN_USE = Gauge(
    "db_pool_connections_in_use",
    "Database connections currently in use",
    ["database", "pool_type"],
)

DB_POOL_CONNECTIONS_IDLE = Gauge(
    "db_pool_connections_idle",
    "Idle database connections",
    ["database", "pool_type"],
)

DB_QUERY_DURATION = Histogram(
    "db_query_duration_seconds",
    "Database query duration in seconds",
    ["database", "query_type"],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

DB_QUERY_COUNT = Counter(
    "db_query_total",
    "Total number of database queries",
    ["database", "query_type", "status"],
)

DB_QUERY_ROWS = Summary(
    "db_query_rows",
    "Number of rows returned by queries",
    ["database", "query_type"],
)

DB_CONNECTION_ACQUIRE_DURATION = Histogram(
    "db_connection_acquire_duration_seconds",
    "Time to acquire database connection",
    ["database", "pool_type"],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5],
)

DB_CONNECTION_CREATE_DURATION = Histogram(
    "db_connection_create_duration_seconds",
    "Time to create new database connection",
    ["database"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
)

DB_SLOW_QUERY = Counter(
    "db_slow_query_total",
    "Count of slow queries (>100ms)",
    ["database", "query_type"],
)

DB_TRANSACTION_DURATION = Histogram(
    "db_transaction_duration_seconds",
    "Database transaction duration",
    ["database", "transaction_type"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

DB_DEADLOCK_COUNT = Counter(
    "db_deadlock_total",
    "Number of deadlocks",
    ["database"],
)

DB_RECONNECT_COUNT = Counter(
    "db_reconnect_total",
    "Number of connection reconnections",
    ["database"],
)


@dataclass
class QueryMetrics:
    """Query performance metrics"""

    query_count: int = 0
    total_duration: float = 0.0
    avg_duration: float = 0.0
    min_duration: float = float("inf")
    max_duration: float = 0.0
    p95_duration: float = 0.0
    slow_queries: int = 0
    failed_queries: int = 0
    last_query_time: Optional[datetime] = None


@dataclass
class PoolMetrics:
    """Connection pool metrics"""

    pool_size: int = 0
    connections_in_use: int = 0
    connections_idle: int = 0
    wait_time_avg: float = 0.0
    acquire_time_avg: float = 0.0
    total_queries: int = 0
    total_slow_queries: int = 0
    last_update: datetime = field(default_factory=datetime.now)


class DatabaseMetricsCollector:
    """Database metrics collector"""

    def __init__(self, database: str = "mystocks"):
        self.database = database
        self._query_metrics: Dict[str, QueryMetrics] = {}
        self._pool_metrics = PoolMetrics()
        self._lock = asyncio.Lock()
        self._slow_query_threshold = 0.1

    def record_query(
        self,
        query_type: str,
        duration: float,
        rows: int = 0,
        success: bool = True,
    ) -> None:
        """Record a query execution"""
        if query_type not in self._query_metrics:
            self._query_metrics[query_type] = QueryMetrics()

        metrics = self._query_metrics[query_type]
        metrics.query_count += 1
        metrics.total_duration += duration
        metrics.avg_duration = metrics.total_duration / metrics.query_count
        metrics.min_duration = min(metrics.min_duration, duration)
        metrics.max_duration = max(metrics.max_duration, duration)
        metrics.last_query_time = datetime.now()

        DB_QUERY_DURATION.labels(database=self.database, query_type=query_type).observe(duration)

        DB_QUERY_COUNT.labels(
            database=self.database, query_type=query_type, status="success" if success else "error"
        ).inc()

        if rows >= 0:
            DB_QUERY_ROWS.labels(database=self.database, query_type=query_type).observe(rows)

        if duration > self._slow_query_threshold:
            metrics.slow_queries += 1
            self._pool_metrics.total_slow_queries += 1
            DB_SLOW_QUERY.labels(database=self.database, query_type=query_type).inc()

        if not success:
            metrics.failed_queries += 1

    def record_connection_acquire(self, duration: float) -> None:
        """Record connection acquire time"""
        DB_CONNECTION_ACQUIRE_DURATION.labels(database=self.database, pool_type="default").observe(duration)

        self._pool_metrics.acquire_time_avg = self._pool_metrics.acquire_time_avg * 0.9 + duration * 0.1

    def record_connection_create(self, duration: float) -> None:
        """Record new connection creation time"""
        DB_CONNECTION_CREATE_DURATION.labels(database=self.database).observe(duration)

    def record_pool_stats(
        self,
        pool_size: int,
        in_use: int,
        idle: int,
        wait_time: float = 0.0,
    ) -> None:
        """Record pool statistics"""
        self._pool_metrics.pool_size = pool_size
        self._pool_metrics.connections_in_use = in_use
        self._pool_metrics.connections_idle = idle
        self._pool_metrics.wait_time_avg = wait_time
        self._pool_metrics.last_update = datetime.now()

        DB_POOL_SIZE.labels(database=self.database, pool_type="default").set(pool_size)

        DB_POOL_CONNECTIONS_IN_USE.labels(database=self.database, pool_type="default").set(in_use)

        DB_POOL_CONNECTIONS_IDLE.labels(database=self.database, pool_type="default").set(idle)

    def record_transaction(self, tx_type: str, duration: float) -> None:
        """Record transaction duration"""
        DB_TRANSACTION_DURATION.labels(database=self.database, transaction_type=tx_type).observe(duration)

    def record_deadlock(self) -> None:
        """Record deadlock occurrence"""
        DB_DEADLOCK_COUNT.labels(database=self.database).inc()

    def record_reconnect(self) -> None:
        """Record connection reconnection"""
        DB_RECONNECT_COUNT.labels(database=self.database).inc()

    def get_query_metrics(self, query_type: str) -> QueryMetrics:
        """Get metrics for a specific query type"""
        return self._query_metrics.get(query_type, QueryMetrics())

    def get_all_query_metrics(self) -> Dict[str, QueryMetrics]:
        """Get all query metrics"""
        return dict(self._query_metrics)

    def get_pool_metrics(self) -> PoolMetrics:
        """Get pool metrics"""
        return self._pool_metrics

    def get_slow_queries(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get slowest queries"""
        slow_queries = []
        for query_type, metrics in self._query_metrics.items():
            if metrics.slow_queries > 0:
                slow_queries.append(
                    {
                        "query_type": query_type,
                        "count": metrics.slow_queries,
                        "avg_duration": metrics.avg_duration,
                        "max_duration": metrics.max_duration,
                        "p95_duration": metrics.p95_duration,
                    }
                )

        return sorted(slow_queries, key=lambda x: x["avg_duration"], reverse=True)[:limit]

    def get_summary(self) -> Dict[str, Any]:
        """Get metrics summary"""
        total_queries = sum(m.q for m in self._query_metrics.values())
        total_slow = sum(m.slow_queries for m in self._query_metrics.values())
        total_failed = sum(m.failed_queries for m in self._query_metrics.values())

        return {
            "database": self.database,
            "timestamp": datetime.now().isoformat(),
            "pool": {
                "size": self._pool_metrics.pool_size,
                "in_use": self._pool_metrics.connections_in_use,
                "idle": self._pool_metrics.connections_idle,
                "wait_time_avg_ms": self._pool_metrics.wait_time_avg * 1000,
            },
            "queries": {
                "total": total_queries,
                "slow": total_slow,
                "failed": total_failed,
                "slow_rate": (total_slow / total_queries * 100) if total_queries > 0 else 0,
            },
            "by_type": {
                qt: {
                    "count": m.query_count,
                    "avg_duration_ms": m.avg_duration * 1000,
                    "max_duration_ms": m.max_duration * 1000,
                    "slow_count": m.slow_queries,
                }
                for qt, m in self._query_metrics.items()
            },
        }


class QueryPerformanceLogger:
    """Query performance logger for slow query detection"""

    def __init__(self, slow_threshold: float = 0.1, max_queries: int = 1000):
        self.slow_threshold = slow_threshold
        self._slow_queries: List[Dict[str, Any]] = []
        self._lock = asyncio.Lock()
        self._max_queries = max_queries

    async def log_query(
        self,
        query: str,
        duration: float,
        query_type: str = "general",
        params: Optional[tuple] = None,
    ) -> None:
        """Log a query with performance info"""
        if duration >= self.slow_threshold:
            async with self._lock:
                self._slow_queries.append(
                    {
                        "query": self._truncate_query(query),
                        "duration": duration,
                        "type": query_type,
                        "timestamp": datetime.now().isoformat(),
                        "params": str(params) if params else None,
                    }
                )

                if len(self._slow_queries) > self._max_queries:
                    self._slow_queries = self._slow_queries[-self._max_queries :]

                logger.warning(f"Slow query detected ({duration * 1000:.2f}ms): {self._truncate_query(query)}")

    def _truncate_query(self, query: str, max_length: int = 500) -> str:
        """Truncate long queries"""
        if len(query) <= max_length:
            return query
        return query[:max_length] + "..."

    def get_slow_queries(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get slow query log"""
        return sorted(
            self._slow_queries,
            key=lambda x: x["duration"],
            reverse=True,
        )[:limit]

    def clear(self) -> None:
        """Clear slow query log"""
        self._slow_queries.clear()


_global_metrics_collectors: Dict[str, DatabaseMetricsCollector] = {}
_global_performance_loggers: Dict[str, QueryPerformanceLogger] = {}


def get_metrics_collector(database: str = "mystocks") -> DatabaseMetricsCollector:
    """Get metrics collector for database"""
    global _global_metrics_collectors
    if database not in _global_metrics_collectors:
        _global_metrics_collectors[database] = DatabaseMetricsCollector(database)
    return _global_metrics_collectors[database]


def get_performance_logger(database: str = "mystocks") -> QueryPerformanceLogger:
    """Get performance logger for database"""
    global _global_performance_loggers
    if database not in _global_performance_loggers:
        _global_performance_loggers[database] = QueryPerformanceLogger()
    return _global_performance_loggers[database]


@asynccontextmanager
async def track_query(
    database: str,
    query_type: str,
    query: str = "",
    params: Optional[tuple] = None,
):
    """Context manager for tracking query performance"""
    start_time = time.perf_counter()
    metrics = get_metrics_collector(database)
    logger = get_performance_logger(database)

    try:
        yield
        success = True
        rows = 0
    except Exception:
        success = False
        raise
    finally:
        duration = time.perf_counter() - start_time
        metrics.record_query(query_type, duration, rows, success)
        if query:
            await logger.log_query(query, duration, query_type, params)


async def track_connection_acquire(database: str, duration: float):
    """Track connection acquire time"""
    metrics = get_metrics_collector(database)
    metrics.record_connection_acquire(duration)


async def track_pool_stats(
    database: str,
    pool_size: int,
    in_use: int,
    idle: int,
    wait_time: float = 0.0,
):
    """Track pool statistics"""
    metrics = get_metrics_collector(database)
    metrics.record_pool_stats(pool_size, in_use, idle, wait_time)
