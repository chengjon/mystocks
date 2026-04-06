from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List

from src.monitoring.monitoring_service._operation_metric_models import OperationMetrics

logger = logging.getLogger("MyStocksMonitoring")


class PerformanceMonitor:
    """性能监控器"""

    def __init__(self):
        """初始化性能监控器"""
        self.metrics_history: List[OperationMetrics] = []
        self.max_history_size = 5000
        self.slow_query_threshold = 5.0

    def record_operation_metrics(self, metrics: OperationMetrics):
        """
        记录操作指标

        Args:
            metrics: 操作指标
        """
        try:
            self.metrics_history.append(metrics)

            if len(self.metrics_history) > self.max_history_size:
                del self.metrics_history[: -self.max_history_size]

            if metrics.duration and metrics.duration > self.slow_query_threshold:
                self._alert_slow_operation(metrics)
        except Exception as e:
            logger.error("记录操作指标失败: %s", e)

    def _alert_slow_operation(self, metrics: OperationMetrics) -> None:
        """告警慢操作"""
        logger.warning(
            "慢操作告警: %s on %s 耗时 %.2f秒",
            metrics.operation_type,
            metrics.table_name,
            metrics.duration,
        )

    def get_performance_summary(self, hours: int = 24) -> Dict[str, Any]:
        """
        获取性能摘要

        Args:
            hours: 统计时间范围（小时）

        Returns:
            Dict: 性能摘要
        """
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            recent_metrics = [m for m in self.metrics_history if m.start_time >= cutoff_time and m.duration is not None]

            if not recent_metrics:
                return {"message": "没有性能数据"}

            durations = [m.duration for m in recent_metrics]
            summary = {
                "time_range_hours": hours,
                "total_operations": len(recent_metrics),
                "avg_duration": sum(durations) / len(durations),
                "min_duration": min(durations),
                "max_duration": max(durations),
                "slow_operations": len([d for d in durations if d > self.slow_query_threshold]),
                "success_rate": len([m for m in recent_metrics if m.status == "success"]) / len(recent_metrics),
                "operation_breakdown": {},
                "database_breakdown": {},
            }

            for metrics in recent_metrics:
                op_type = metrics.operation_type
                if op_type not in summary["operation_breakdown"]:
                    summary["operation_breakdown"][op_type] = {
                        "count": 0,
                        "avg_duration": 0,
                    }
                summary["operation_breakdown"][op_type]["count"] += 1

            for op_type in summary["operation_breakdown"]:
                op_metrics = [m for m in recent_metrics if m.operation_type == op_type]
                op_durations = [m.duration for m in op_metrics]
                summary["operation_breakdown"][op_type]["avg_duration"] = sum(op_durations) / len(op_durations)

            logger.info("性能摘要生成完成: 最近%s小时，%s个操作", hours, len(recent_metrics))
            return summary
        except Exception as e:
            logger.error("获取性能摘要失败: %s", e)
            return {"error": str(e)}

    def get_slow_operations(self, hours: int = 24, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取慢操作列表

        Args:
            hours: 时间范围（小时）
            limit: 返回数量限制

        Returns:
            List[Dict]: 慢操作列表
        """
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            slow_operations = [
                {
                    "operation_id": m.operation_id,
                    "table_name": m.table_name,
                    "operation_type": m.operation_type,
                    "duration": m.duration,
                    "start_time": m.start_time.isoformat(),
                    "data_count": m.data_count,
                }
                for m in self.metrics_history
                if m.start_time >= cutoff_time and m.duration is not None and m.duration > self.slow_query_threshold
            ]

            slow_operations.sort(key=lambda x: x["duration"], reverse=True)

            logger.info("获取慢操作列表: %s 个操作", len(slow_operations))
            return slow_operations[:limit]
        except Exception as e:
            logger.error("获取慢操作列表失败: %s", e)
            return []


__all__ = ["PerformanceMonitor"]
