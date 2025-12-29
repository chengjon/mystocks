import pytest
import asyncio
from src.gpu_monitoring.gpu_monitor_service import GPUMonitoringService
from src.gpu_monitoring.performance_collector import PerformanceCollector
from src.gpu_monitoring.history_service import HistoryDataService
from src.gpu_monitoring.optimization_advisor import OptimizationAdvisor
from datetime import datetime, timedelta


@pytest.fixture
def gpu_monitor():
    return GPUMonitoringService()


@pytest.fixture
def perf_collector():
    return PerformanceCollector()


@pytest.fixture
def history_service():
    return HistoryDataService()


@pytest.fixture
def advisor():
    return OptimizationAdvisor()


def test_gpu_monitor_init(gpu_monitor):
    assert gpu_monitor is not None
    assert gpu_monitor.device_count >= 0


def test_get_gpu_metrics(gpu_monitor):
    metrics = gpu_monitor.get_metrics(0)
    assert metrics.device_id == 0
    assert metrics.gpu_utilization >= 0
    assert metrics.gpu_utilization <= 100
    assert metrics.memory_used >= 0
    assert metrics.temperature >= 0


def test_get_all_metrics(gpu_monitor):
    all_metrics = gpu_monitor.get_all_metrics()
    assert len(all_metrics) >= 1


def test_get_process_info(gpu_monitor):
    processes = gpu_monitor.get_process_info(0)
    assert isinstance(processes, list)


@pytest.mark.asyncio
async def test_collect_performance_metrics(perf_collector):
    metrics = await perf_collector.collect_performance_metrics()
    assert metrics.timestamp is not None
    assert metrics.matrix_gflops >= 0
    assert metrics.matrix_speedup >= 0
    assert metrics.overall_speedup >= 0
    assert metrics.cache_hit_rate >= 0
    assert metrics.cache_hit_rate <= 100
    assert metrics.success_rate >= 0
    assert metrics.success_rate <= 100


def test_history_service_save_metrics(history_service, gpu_monitor):
    from src.gpu_monitoring.performance_collector import PerformanceCollector

    gpu_metrics = gpu_monitor.get_metrics(0)

    async def save_test():
        collector = PerformanceCollector()
        perf_metrics = await collector.collect_performance_metrics()
        history_service.save_metrics(gpu_metrics, perf_metrics)

    asyncio.run(save_test())


def test_history_service_query(history_service):
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=1)

    history = history_service.query_history(0, start_time, end_time)
    assert isinstance(history, list)


def test_history_service_aggregated_stats(history_service):
    stats = history_service.get_aggregated_stats(0, hours=24)
    assert "avg_utilization" in stats
    assert "max_utilization" in stats
    assert "avg_temperature" in stats
    assert "max_temperature" in stats
    assert "avg_gflops" in stats
    assert "peak_gflops" in stats


def test_optimization_advisor(advisor, gpu_monitor):
    from src.gpu_monitoring.performance_collector import PerformanceCollector
    from src.gpu_monitoring.history_service import HistoryDataService

    gpu_metrics = gpu_monitor.get_metrics(0)

    async def test_recommendations():
        collector = PerformanceCollector()
        perf_metrics = await collector.collect_performance_metrics()

        history_service = HistoryDataService()
        stats_24h = history_service.get_aggregated_stats(0, hours=24)

        recommendations = advisor.analyze_and_recommend(gpu_metrics, perf_metrics, stats_24h)

        assert isinstance(recommendations, list)

    asyncio.run(test_recommendations())


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
