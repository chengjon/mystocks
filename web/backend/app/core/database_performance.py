"""
数据库性能优化集成管理
Database Performance Optimization Integration - Unified performance management

Task 14.3: 数据库性能优化 - Performance Optimization Integration

整合以下优化模块:
- 连接池优化 (Connection Pool Optimization)
- 查询批处理 (Query Batch Processing)
- 性能监控 (Performance Monitoring)

Author: Claude Code
Date: 2025-11-12
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import structlog

from app.core.database_connection_pool import (
    get_pool_optimizer,
)
from app.core.database_query_batch import (
    get_query_batcher,
)
from app.core.database_performance_monitor import (
    get_performance_monitor,
)

logger = structlog.get_logger()


@dataclass
class DatabasePerformanceMetrics:
    """数据库性能指标"""

    timestamp: datetime
    pool_size_total: int
    pool_size_idle: int
    pool_size_in_use: int
    connection_reuse_rate: float
    avg_latency_ms: float
    total_queries: int
    slow_queries: int
    critical_queries: int
    error_rate: float
    batch_count: int
    total_rows_batched: int
    avg_batch_execution_ms: float


class DatabasePerformanceManager:
    """数据库性能管理器 - 整合所有优化模块"""

    def __init__(
        self,
        # 连接池配置
        pool_min_size: int = 20,
        pool_max_size: int = 100,
        pool_max_overflow: int = 40,
        pool_timeout: int = 30,
        pool_recycle: int = 3600,
        pool_stale_timeout: int = 3600,
        health_check_interval: int = 60,
        # 查询批处理配置
        batch_size: int = 1000,
        batch_timeout_ms: int = 100,
        # 性能监控配置
        slow_query_threshold_ms: float = 1000,
        critical_query_threshold_ms: float = 5000,
    ):
        """
        初始化数据库性能管理器

        Args:
            pool_min_size: 连接池最小大小
            pool_max_size: 连接池最大大小
            pool_max_overflow: 最大溢出连接
            pool_timeout: 连接获取超时
            pool_recycle: 连接回收时间
            pool_stale_timeout: 连接过期超时
            health_check_interval: 健康检查间隔
            batch_size: 批处理大小
            batch_timeout_ms: 批处理超时
            slow_query_threshold_ms: 慢查询阈值
            critical_query_threshold_ms: 严重查询阈值
        """
        # 初始化所有优化模块
        self.pool_optimizer = get_pool_optimizer(
            min_size=pool_min_size,
            max_size=pool_max_size,
            max_overflow=pool_max_overflow,
            pool_timeout=pool_timeout,
            pool_recycle=pool_recycle,
            stale_timeout=pool_stale_timeout,
            health_check_interval=health_check_interval,
        )

        self.query_batcher = get_query_batcher(
            batch_size=batch_size,
            batch_timeout_ms=batch_timeout_ms,
        )

        self.performance_monitor = get_performance_monitor(
            slow_query_threshold_ms=slow_query_threshold_ms,
            critical_query_threshold_ms=critical_query_threshold_ms,
        )

        # 性能指标历史
        self.metrics_history: List[DatabasePerformanceMetrics] = []
        self.max_metrics = 1440  # 24小时（分钟级）

        logger.info(
            "✅ Database Performance Manager initialized",
            pool_min=pool_min_size,
            pool_max=pool_max_size,
            batch_size=batch_size,
            slow_threshold_ms=slow_query_threshold_ms,
        )

    async def initialize(self) -> None:
        """初始化性能管理器"""
        try:
            await self.pool_optimizer.start_monitoring()
            await self.performance_monitor.start_monitoring()
            logger.info("✅ Database Performance Manager initialized and monitoring started")
        except Exception as e:
            logger.error("❌ Error initializing performance manager", error=str(e))
            raise

    async def shutdown(self) -> None:
        """关闭性能管理器"""
        try:
            await self.pool_optimizer.stop_monitoring()
            await self.performance_monitor.stop_monitoring()
            await self.query_batcher.flush_all()
            logger.info("✅ Database Performance Manager shut down")
        except Exception as e:
            logger.error("❌ Error shutting down performance manager", error=str(e))

    def get_connection(self, conn_obj: Any = None):
        """获取数据库连接"""
        return self.pool_optimizer.get_connection(conn_obj)

    def return_connection(self, conn_id: str, error: bool = False, latency_ms: float = 0.0) -> None:
        """归还数据库连接"""
        self.pool_optimizer.return_connection(conn_id, error, latency_ms)

    async def queue_insert(
        self,
        table_name: str,
        rows: List[Dict[str, Any]],
        execute_immediately: bool = False,
    ):
        """排队批量INSERT"""
        return await self.query_batcher.queue_insert(table_name, rows, execute_immediately)

    async def queue_update(
        self,
        table_name: str,
        updates: List[Dict[str, Any]],
        execute_immediately: bool = False,
    ):
        """排队批量UPDATE"""
        return await self.query_batcher.queue_update(table_name, updates, execute_immediately)

    async def queue_delete(
        self,
        table_name: str,
        delete_rows: List[Dict[str, Any]],
        execute_immediately: bool = False,
    ):
        """排队批量DELETE"""
        return await self.query_batcher.queue_delete(table_name, delete_rows, execute_immediately)

    async def flush_batches(self) -> None:
        """刷新所有批处理缓冲"""
        await self.query_batcher.flush_all()

    def record_query(
        self,
        sql: str,
        table_name: str,
        operation: str,
        duration_ms: float,
        rows_affected: int = 0,
        rows_scanned: int = 0,
        error: Optional[str] = None,
    ):
        """记录查询性能"""
        return self.performance_monitor.record_query(
            sql, table_name, operation, duration_ms, rows_affected, rows_scanned, error
        )

    async def collect_metrics(self) -> DatabasePerformanceMetrics:
        """收集性能指标"""
        pool_stats = self.pool_optimizer.get_pool_stats()
        batch_stats = self.query_batcher.get_stats()
        monitor_stats = self.performance_monitor.get_monitoring_stats()

        metrics = DatabasePerformanceMetrics(
            timestamp=datetime.utcnow(),
            pool_size_total=pool_stats["pool_size"]["total"],
            pool_size_idle=pool_stats["pool_size"]["idle"],
            pool_size_in_use=pool_stats["pool_size"]["in_use"],
            connection_reuse_rate=pool_stats["performance"]["connection_reuse_rate"],
            avg_latency_ms=pool_stats["performance"]["avg_latency_ms"],
            total_queries=monitor_stats["total_queries"],
            slow_queries=monitor_stats["total_slow_queries"],
            critical_queries=monitor_stats["total_critical_queries"],
            error_rate=monitor_stats["error_rate"],
            batch_count=batch_stats["total_batches"],
            total_rows_batched=batch_stats["total_rows_batched"],
            avg_batch_execution_ms=batch_stats["performance"]["avg_execution_time_ms"],
        )

        # 保持指标历史
        self.metrics_history.append(metrics)
        if len(self.metrics_history) > self.max_metrics:
            self.metrics_history.pop(0)

        return metrics

    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """获取综合统计信息"""
        return {
            "connection_pool": self.pool_optimizer.get_pool_stats(),
            "query_batcher": self.query_batcher.get_stats(),
            "performance_monitor": self.performance_monitor.get_monitoring_stats(),
            "timestamp": datetime.utcnow().isoformat(),
        }

    def get_comprehensive_report(self) -> Dict[str, Any]:
        """获取综合性能报告"""
        return {
            "connection_pool": self.pool_optimizer.get_pool_stats(),
            "query_batcher": self.query_batcher.get_stats(),
            "performance": self.performance_monitor.get_comprehensive_report(),
            "timestamp": datetime.utcnow().isoformat(),
        }

    def get_performance_summary(self) -> Dict[str, Any]:
        """获取性能总结"""
        if not self.metrics_history:
            return {
                "status": "no_data",
                "message": "No metrics collected yet",
            }

        recent_metrics = self.metrics_history[-60:]  # 最近60个数据点

        avg_pool_idle = sum(m.pool_size_idle for m in recent_metrics) / len(recent_metrics)
        avg_pool_in_use = sum(m.pool_size_in_use for m in recent_metrics) / len(recent_metrics)
        avg_slow_queries = sum(m.slow_queries for m in recent_metrics) / len(recent_metrics)
        avg_error_rate = sum(m.error_rate for m in recent_metrics) / len(recent_metrics)

        return {
            "period": "last_60_measurements",
            "average_pool_idle_connections": round(avg_pool_idle, 2),
            "average_pool_in_use_connections": round(avg_pool_in_use, 2),
            "average_slow_queries": round(avg_slow_queries, 2),
            "average_error_rate": round(avg_error_rate, 2),
            "peak_in_use_connections": max(m.pool_size_in_use for m in recent_metrics),
            "connection_reuse_rate": self.pool_optimizer.get_pool_stats()["performance"]["connection_reuse_rate"],
            "timestamp": datetime.utcnow().isoformat(),
        }

    def export_metrics_history(self) -> List[Dict[str, Any]]:
        """导出指标历史"""
        return [
            {
                "timestamp": m.timestamp.isoformat(),
                "pool_size_total": m.pool_size_total,
                "pool_size_idle": m.pool_size_idle,
                "pool_size_in_use": m.pool_size_in_use,
                "connection_reuse_rate": round(m.connection_reuse_rate, 4),
                "avg_latency_ms": round(m.avg_latency_ms, 2),
                "total_queries": m.total_queries,
                "slow_queries": m.slow_queries,
                "critical_queries": m.critical_queries,
                "error_rate": round(m.error_rate, 2),
                "batch_count": m.batch_count,
                "total_rows_batched": m.total_rows_batched,
                "avg_batch_execution_ms": round(m.avg_batch_execution_ms, 2),
            }
            for m in self.metrics_history
        ]


# 全局单例
_performance_manager: Optional[DatabasePerformanceManager] = None


def get_database_performance_manager(
    pool_min_size: int = 20,
    pool_max_size: int = 100,
    pool_max_overflow: int = 40,
    pool_timeout: int = 30,
    pool_recycle: int = 3600,
    pool_stale_timeout: int = 3600,
    health_check_interval: int = 60,
    batch_size: int = 1000,
    batch_timeout_ms: int = 100,
    slow_query_threshold_ms: float = 1000,
    critical_query_threshold_ms: float = 5000,
) -> DatabasePerformanceManager:
    """获取数据库性能管理器单例"""
    global _performance_manager
    if _performance_manager is None:
        _performance_manager = DatabasePerformanceManager(
            pool_min_size=pool_min_size,
            pool_max_size=pool_max_size,
            pool_max_overflow=pool_max_overflow,
            pool_timeout=pool_timeout,
            pool_recycle=pool_recycle,
            pool_stale_timeout=pool_stale_timeout,
            health_check_interval=health_check_interval,
            batch_size=batch_size,
            batch_timeout_ms=batch_timeout_ms,
            slow_query_threshold_ms=slow_query_threshold_ms,
            critical_query_threshold_ms=critical_query_threshold_ms,
        )
    return _performance_manager


def reset_database_performance_manager() -> None:
    """重置数据库性能管理器（仅用于测试）"""
    global _performance_manager
    _performance_manager = None
