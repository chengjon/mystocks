from typing import List
from datetime import datetime
import logging
import asyncio
from .history_service import HistoryDataService, GPUPerformanceEvent
from .gpu_monitor_service import GPUMetrics
from .performance_collector import PerformanceMetrics

logger = logging.getLogger(__name__)


class GPUAlertRule:
    @staticmethod
    def check_alerts(
        gpu_metrics: GPUMetrics, perf_metrics: PerformanceMetrics, history_service: HistoryDataService
    ) -> List[GPUPerformanceEvent]:
        events = []

        if gpu_metrics.temperature > 85:
            events.append(
                GPUPerformanceEvent(
                    device_id=gpu_metrics.device_id,
                    timestamp=datetime.now(),
                    event_type="high_temp",
                    severity="critical",
                    message=f"GPU温度过高: {gpu_metrics.temperature:.1f}°C (阈值: 85°C)",
                    metadata='{"temperature": %.1f}' % gpu_metrics.temperature,
                )
            )

        if gpu_metrics.memory_utilization > 95:
            events.append(
                GPUPerformanceEvent(
                    device_id=gpu_metrics.device_id,
                    timestamp=datetime.now(),
                    event_type="memory_leak",
                    severity="warning",
                    message=f"显存使用率过高: {gpu_metrics.memory_utilization:.1f}% (阈值: 95%)",
                    metadata='{"memory_utilization": %.1f}' % gpu_metrics.memory_utilization,
                )
            )

        if perf_metrics.overall_speedup < 30:
            events.append(
                GPUPerformanceEvent(
                    device_id=gpu_metrics.device_id,
                    timestamp=datetime.now(),
                    event_type="performance_drop",
                    severity="warning",
                    message=f"加速比异常下降: {perf_metrics.overall_speedup:.2f}x (预期: >50x)",
                    metadata='{"speedup": %.2f}' % perf_metrics.overall_speedup,
                )
            )

        return events


async def alert_checker_loop(gpu_monitor, perf_collector, history_service: HistoryDataService, interval: int = 30):
    while True:
        try:
            gpu_metrics = gpu_monitor.get_metrics(0)
            perf_metrics = await perf_collector.collect_performance_metrics()

            events = GPUAlertRule.check_alerts(gpu_metrics, perf_metrics, history_service)

            for event in events:
                history_service.log_event(event)
                logger.warning(f"GPU Alert: {event.message}")

        except Exception as e:
            logger.error(f"告警检查失败: {e}")

        await asyncio.sleep(interval)
