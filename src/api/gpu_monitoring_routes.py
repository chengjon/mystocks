from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from typing import List
from datetime import datetime, timedelta
import asyncio
import json
import logging
from ..gpu_monitoring.gpu_monitor_service import GPUMonitoringService, GPUMetrics
from ..gpu_monitoring.performance_collector import PerformanceCollector, PerformanceMetrics
from ..gpu_monitoring.history_service import HistoryDataService
from ..gpu_monitoring.optimization_advisor import OptimizationAdvisor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/gpu", tags=["GPU监控"])

gpu_monitor = GPUMonitoringService()
perf_collector = PerformanceCollector()
history_service = HistoryDataService()
advisor = OptimizationAdvisor()


@router.get("/metrics", response_model=List[GPUMetrics])
async def get_gpu_metrics():
    return gpu_monitor.get_all_metrics()


@router.get("/metrics/{device_id}", response_model=GPUMetrics)
async def get_gpu_metrics_by_id(device_id: int):
    return gpu_monitor.get_metrics(device_id)


@router.get("/processes/{device_id}")
async def get_gpu_processes(device_id: int):
    return gpu_monitor.get_process_info(device_id)


@router.get("/performance", response_model=PerformanceMetrics)
async def get_performance_metrics():
    return await perf_collector.collect_performance_metrics()


@router.get("/history/{device_id}")
async def get_gpu_history(device_id: int, hours: int = Query(24, ge=1, le=168)):
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=hours)
    history = history_service.query_history(device_id, start_time, end_time)
    return [
        {
            "timestamp": h.timestamp.isoformat(),
            "gpu_utilization": h.gpu_utilization,
            "memory_used": h.memory_used,
            "memory_total": h.memory_total,
            "temperature": h.temperature,
            "matrix_gflops": h.matrix_gflops,
            "overall_speedup": h.overall_speedup,
            "cache_hit_rate": h.cache_hit_rate,
            "memory_bandwidth_gbs": h.memory_bandwidth_gbs,
        }
        for h in history
    ]


@router.get("/stats/{device_id}")
async def get_aggregated_stats(device_id: int, hours: int = Query(24, ge=1, le=168)):
    return history_service.get_aggregated_stats(device_id, hours)


@router.get("/recommendations")
async def get_optimization_recommendations(device_id: int = Query(0, ge=0)):
    gpu_metrics = gpu_monitor.get_metrics(device_id)
    perf_metrics = await perf_collector.collect_performance_metrics()
    stats_24h = history_service.get_aggregated_stats(device_id, hours=24)

    recommendations = advisor.analyze_and_recommend(gpu_metrics, perf_metrics, stats_24h)
    return [rec.dict() for rec in recommendations]


@router.get("/stream/{device_id}")
async def gpu_metrics_stream(device_id: int):
    async def event_generator():
        try:
            while True:
                try:
                    gpu_metrics = gpu_monitor.get_metrics(device_id)
                    perf_metrics = await perf_collector.collect_performance_metrics()

                    data = {**gpu_metrics.dict(), **perf_metrics.dict()}

                    yield f"data: {json.dumps(data)}\n\n"

                    await asyncio.sleep(2)
                except Exception as e:
                    logger.error(f"Error in SSE stream: {e}")
                    await asyncio.sleep(2)
        except asyncio.CancelledError:
            logger.info("SSE stream cancelled")
            pass

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"},
    )
