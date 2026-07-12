"""数据库性能监控和慢查询检测
Database Performance Monitoring - Slow query detection and analysis

Task 14.3: 数据库性能优化 - Performance Monitoring

功能特性:
- 查询性能监控（时延、资源）
- 慢查询检测和告警
- 查询执行计划分析
- 时序性能数据存储
- 性能趋势分析
- 自动告警和通知

Author: Claude Code
Date: 2025-11-12
"""

import asyncio
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

import structlog


logger = structlog.get_logger()


class QuerySeverity(str, Enum):
    """查询严重级别"""

    NORMAL = "normal"  # 正常
    SLOW = "slow"  # 慢查询
    CRITICAL = "critical"  # 严重


@dataclass
class QueryMetric:
    """查询性能指标"""

    query_id: str
    sql: str
    table_name: str
    operation: str  # SELECT, INSERT, UPDATE, DELETE
    duration_ms: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    rows_affected: int = 0
    rows_scanned: int = 0
    severity: QuerySeverity = QuerySeverity.NORMAL
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "query_id": self.query_id,
            "sql": self.sql[:100],  # 截断长SQL
            "table_name": self.table_name,
            "operation": self.operation,
            "duration_ms": round(self.duration_ms, 2),
            "timestamp": self.timestamp.isoformat(),
            "rows_affected": self.rows_affected,
            "rows_scanned": self.rows_scanned,
            "severity": self.severity.value,
            "error": error[:100] if (error := self.error) else None,
        }


@dataclass
class SlowQueryAlert:
    """慢查询告警"""

    alert_id: str
    query_id: str
    threshold_ms: float
    actual_duration_ms: float
    excess_percent: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    sql: str = ""
    table_name: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "alert_id": self.alert_id,
            "query_id": self.query_id,
            "threshold_ms": round(self.threshold_ms, 2),
            "actual_duration_ms": round(self.actual_duration_ms, 2),
            "excess_percent": round(self.excess_percent, 2),
            "timestamp": self.timestamp.isoformat(),
            "table_name": self.table_name,
        }


class DatabasePerformanceMonitor:
    """数据库性能监控器"""

    def __init__(
        self,
        slow_query_threshold_ms: float = 1000,
        critical_query_threshold_ms: float = 5000,
        metrics_retention_hours: int = 24,
        alert_retention_hours: int = 7,
    ):
        """初始化性能监控器

        Args:
            slow_query_threshold_ms: 慢查询阈值（毫秒）
            critical_query_threshold_ms: 严重查询阈值（毫秒）
            metrics_retention_hours: 指标保留时间（小时）
            alert_retention_hours: 告警保留时间（小时）

        """
        self.slow_query_threshold_ms = slow_query_threshold_ms
        self.critical_query_threshold_ms = critical_query_threshold_ms
        self.metrics_retention_hours = metrics_retention_hours
        self.alert_retention_hours = alert_retention_hours

        # 性能指标
        self.query_metrics: List[QueryMetric] = []
        self.slow_query_alerts: List[SlowQueryAlert] = []

        # 统计
        self.total_queries = 0
        self.total_slow_queries = 0
        self.total_critical_queries = 0
        self.total_errors = 0

        # 按表统计
        self.table_stats: Dict[str, Dict[str, Any]] = {}

        # 监控任务
        self.cleanup_task: Optional[asyncio.Task] = None

        logger.info(
            "✅ Database Performance Monitor initialized",
            slow_threshold_ms=slow_query_threshold_ms,
            critical_threshold_ms=critical_query_threshold_ms,
        )

    async def start_monitoring(self) -> None:
        """启动监控"""
        if not self.cleanup_task or self.cleanup_task.done():
            self.cleanup_task = asyncio.create_task(self._cleanup_loop())

        logger.info("✅ Performance monitoring started")

    async def stop_monitoring(self) -> None:
        """停止监控"""
        if self.cleanup_task and not self.cleanup_task.done():
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass

        logger.info("✅ Performance monitoring stopped")

    async def _cleanup_loop(self) -> None:
        """定期清理循环"""
        while True:
            try:
                # 每小时清理一次
                await asyncio.sleep(3600)
                await self._cleanup_old_metrics()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("❌ Error in cleanup loop", error=str(e))

    async def _cleanup_old_metrics(self) -> None:
        """清理过期指标"""
        try:
            now = datetime.now(timezone.utc)
            cutoff_metrics = now - timedelta(hours=self.metrics_retention_hours)
            cutoff_alerts = now - timedelta(hours=self.alert_retention_hours)

            # 清理指标
            initial_count = len(self.query_metrics)
            self.query_metrics = [m for m in self.query_metrics if m.timestamp > cutoff_metrics]
            removed_metrics = initial_count - len(self.query_metrics)

            # 清理告警
            alert_count = len(self.slow_query_alerts)
            self.slow_query_alerts = [a for a in self.slow_query_alerts if a.timestamp > cutoff_alerts]
            removed_alerts = alert_count - len(self.slow_query_alerts)

            if removed_metrics > 0 or removed_alerts > 0:
                logger.info(
                    "🧹 Cleaned up metrics and alerts",
                    removed_metrics=removed_metrics,
                    removed_alerts=removed_alerts,
                )

        except Exception as e:
            logger.error("❌ Error cleaning up metrics", error=str(e))

    def record_query(
        self,
        sql: str,
        table_name: str,
        operation: str,
        duration_ms: float,
        rows_affected: int = 0,
        rows_scanned: int = 0,
        error: Optional[str] = None,
    ) -> Optional[SlowQueryAlert]:
        """记录查询性能

        Args:
            sql: SQL语句
            table_name: 表名
            operation: 操作类型（SELECT/INSERT/UPDATE/DELETE）
            duration_ms: 执行时间（毫秒）
            rows_affected: 影响行数
            rows_scanned: 扫描行数
            error: 错误信息

        Returns:
            如果是慢查询，返回SlowQueryAlert对象

        """
        try:
            query_id = f"query_{int(time.time() * 1000000)}"

            # 判断查询严重级别
            if duration_ms >= self.critical_query_threshold_ms:
                severity = QuerySeverity.CRITICAL
            elif duration_ms >= self.slow_query_threshold_ms:
                severity = QuerySeverity.SLOW
            else:
                severity = QuerySeverity.NORMAL

            # 创建指标对象
            metric = QueryMetric(
                query_id=query_id,
                sql=sql,
                table_name=table_name,
                operation=operation,
                duration_ms=duration_ms,
                rows_affected=rows_affected,
                rows_scanned=rows_scanned,
                severity=severity,
                error=error,
            )

            self.query_metrics.append(metric)
            self.total_queries += 1

            # 更新表统计
            if table_name not in self.table_stats:
                self.table_stats[table_name] = {
                    "total_queries": 0,
                    "total_duration_ms": 0,
                    "avg_duration_ms": 0,
                    "slow_queries": 0,
                    "critical_queries": 0,
                }

            stats = self.table_stats[table_name]
            stats["total_queries"] += 1
            stats["total_duration_ms"] += duration_ms
            stats["avg_duration_ms"] = stats["total_duration_ms"] / stats["total_queries"]

            # 如果是慢查询或错误，生成告警
            alert = None
            if severity == QuerySeverity.SLOW:
                self.total_slow_queries += 1
                stats["slow_queries"] += 1

                excess_percent = (duration_ms - self.slow_query_threshold_ms) / self.slow_query_threshold_ms * 100

                alert = SlowQueryAlert(
                    alert_id=f"alert_{query_id}",
                    query_id=query_id,
                    threshold_ms=self.slow_query_threshold_ms,
                    actual_duration_ms=duration_ms,
                    excess_percent=excess_percent,
                    sql=sql[:200],
                    table_name=table_name,
                )

                self.slow_query_alerts.append(alert)

                logger.warning(
                    "⚠️ Slow query detected",
                    table=table_name,
                    operation=operation,
                    duration_ms=round(duration_ms, 2),
                    threshold_ms=self.slow_query_threshold_ms,
                    excess_percent=round(excess_percent, 1),
                )

            elif severity == QuerySeverity.CRITICAL:
                self.total_critical_queries += 1
                stats["critical_queries"] += 1

                excess_percent = (
                    (duration_ms - self.critical_query_threshold_ms) / self.critical_query_threshold_ms * 100
                )

                alert = SlowQueryAlert(
                    alert_id=f"alert_{query_id}",
                    query_id=query_id,
                    threshold_ms=self.critical_query_threshold_ms,
                    actual_duration_ms=duration_ms,
                    excess_percent=excess_percent,
                    sql=sql[:200],
                    table_name=table_name,
                )

                self.slow_query_alerts.append(alert)

                logger.critical(
                    "❌ CRITICAL slow query detected",
                    table=table_name,
                    operation=operation,
                    duration_ms=round(duration_ms, 2),
                    threshold_ms=self.critical_query_threshold_ms,
                    excess_percent=round(excess_percent, 1),
                )

            if error:
                self.total_errors += 1
                logger.error(
                    "❌ Query error",
                    table=table_name,
                    operation=operation,
                    error=error[:100],
                )

            return alert

        except Exception as e:
            logger.error("❌ Error recording query metric", error=str(e))
            return None

    def get_slow_queries(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取慢查询列表"""
        slow_queries = [m for m in self.query_metrics if m.severity != QuerySeverity.NORMAL]
        # 按时间倒序排列
        slow_queries.sort(key=lambda x: x.timestamp, reverse=True)
        return [q.to_dict() for q in slow_queries[:limit]]

    def get_recent_alerts(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取最近告警"""
        recent = sorted(self.slow_query_alerts, key=lambda x: x.timestamp, reverse=True)
        return [a.to_dict() for a in recent[:limit]]

    def get_table_performance(self) -> Dict[str, Dict[str, Any]]:
        """获取表级性能统计"""
        return {
            table: {
                **stats,
                "avg_duration_ms": round(stats["avg_duration_ms"], 2),
            }
            for table, stats in self.table_stats.items()
        }

    def get_monitoring_stats(self) -> Dict[str, Any]:
        """获取监控统计"""
        return {
            "total_queries": self.total_queries,
            "total_slow_queries": self.total_slow_queries,
            "total_critical_queries": self.total_critical_queries,
            "total_errors": self.total_errors,
            "slow_query_rate": ((self.total_slow_queries / max(1, self.total_queries)) * 100),
            "error_rate": (self.total_errors / max(1, self.total_queries)) * 100,
            "metrics_count": len(self.query_metrics),
            "alerts_count": len(self.slow_query_alerts),
            "tables_monitored": len(self.table_stats),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def get_comprehensive_report(self) -> Dict[str, Any]:
        """获取综合报告"""
        return {
            "summary": self.get_monitoring_stats(),
            "table_performance": self.get_table_performance(),
            "recent_slow_queries": self.get_slow_queries(10),
            "recent_alerts": self.get_recent_alerts(10),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# 全局单例
_performance_monitor: Optional[DatabasePerformanceMonitor] = None


def get_performance_monitor(
    slow_query_threshold_ms: float = 1000,
    critical_query_threshold_ms: float = 5000,
    metrics_retention_hours: int = 24,
    alert_retention_hours: int = 7,
) -> DatabasePerformanceMonitor:
    """获取性能监控器单例"""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = DatabasePerformanceMonitor(
            slow_query_threshold_ms=slow_query_threshold_ms,
            critical_query_threshold_ms=critical_query_threshold_ms,
            metrics_retention_hours=metrics_retention_hours,
            alert_retention_hours=alert_retention_hours,
        )
    return _performance_monitor


def reset_performance_monitor() -> None:
    """重置性能监控器（仅用于测试）"""
    global _performance_monitor
    _performance_monitor = None
