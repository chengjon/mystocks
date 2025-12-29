"""
GPU监控 - Prometheus Exporter
GPU Metrics Prometheus Exporter

将GPU监控指标暴露为Prometheus格式
"""

from prometheus_client import start_http_server, Gauge, Counter, Summary
import logging
from .gpu_monitor_service import GPUMonitoringService
from .performance_collector import PerformanceCollector
import asyncio

logger = logging.getLogger(__name__)


class GPUMetricsExporter:
    """GPU指标Prometheus导出器"""

    def __init__(self):
        self.gpu_monitor = GPUMonitoringService()
        self.perf_collector = PerformanceCollector()

        # GPU硬件指标
        self.gpu_utilization = Gauge(
            "gpu_utilization_percent", "GPU utilization percentage", ["device_id", "device_name"]
        )
        self.memory_used = Gauge("gpu_memory_used_bytes", "GPU memory used in bytes", ["device_id"])
        self.memory_total = Gauge("gpu_memory_total_bytes", "GPU total memory in bytes", ["device_id"])
        self.memory_utilization = Gauge(
            "gpu_memory_utilization_percent", "GPU memory utilization percentage", ["device_id"]
        )
        self.temperature = Gauge("gpu_temperature_celsius", "GPU temperature in Celsius", ["device_id"])
        self.power_usage = Gauge("gpu_power_usage_watts", "GPU power usage in watts", ["device_id"])
        self.power_limit = Gauge("gpu_power_limit_watts", "GPU power limit in watts", ["device_id"])
        self.sm_clock = Gauge("gpu_sm_clock_mhz", "GPU SM clock frequency in MHz", ["device_id"])
        self.memory_clock = Gauge("gpu_memory_clock_mhz", "GPU memory clock frequency in MHz", ["device_id"])
        self.pcie_throughput_tx = Gauge(
            "gpu_pcie_throughput_tx_mbps", "GPU PCIe throughput transmit in MB/s", ["device_id"]
        )
        self.pcie_throughput_rx = Gauge(
            "gpu_pcie_throughput_rx_mbps", "GPU PCIe throughput receive in MB/s", ["device_id"]
        )

        # 性能指标
        self.matrix_gflops = Gauge(
            "gpu_matrix_gflops", "GPU matrix multiplication performance in GFLOPS", ["device_id"]
        )
        self.matrix_speedup = Gauge(
            "gpu_matrix_speedup_ratio", "GPU matrix multiplication speedup ratio", ["device_id"]
        )
        self.matrix_throughput = Gauge(
            "gpu_matrix_throughput_ops_per_sec", "GPU matrix throughput in operations per second", ["device_id"]
        )
        self.memory_bandwidth = Gauge("gpu_memory_bandwidth_gbps", "GPU memory bandwidth in GB/s", ["device_id"])
        self.memory_speedup = Gauge("gpu_memory_speedup_ratio", "GPU memory operation speedup ratio", ["device_id"])
        self.memory_throughput = Gauge(
            "gpu_memory_throughput_ops_per_sec", "GPU memory throughput in operations per second", ["device_id"]
        )
        self.overall_speedup = Gauge("gpu_overall_speedup_ratio", "GPU overall speedup ratio", ["device_id"])
        self.cache_hit_rate = Gauge("gpu_cache_hit_rate_percent", "GPU cache hit rate percentage", ["device_id"])
        self.success_rate = Gauge("gpu_task_success_rate_percent", "GPU task success rate percentage", ["device_id"])

        # 计数器
        self.benchmark_runs = Counter("gpu_benchmark_runs_total", "Total number of benchmark runs", ["device_id"])

        # 汇总统计
        self.benchmark_duration = Summary(
            "gpu_benchmark_duration_seconds", "GPU benchmark duration in seconds", ["device_id", "benchmark_type"]
        )

        self.running = False

    async def collect_metrics(self):
        """采集并更新指标"""
        try:
            # 获取所有GPU指标
            gpu_metrics = self.gpu_monitor.get_all_metrics()

            for metrics in gpu_metrics:
                device_id = metrics.device_id
                device_name = metrics.device_name

                # 更新硬件指标
                self.gpu_utilization.labels(device_id=device_id, device_name=device_name).set(metrics.gpu_utilization)

                self.memory_used.labels(device_id=device_id).set(metrics.memory_used * 1024 * 1024)  # 转换为bytes

                self.memory_total.labels(device_id=device_id).set(metrics.memory_total * 1024 * 1024)  # 转换为bytes

                self.memory_utilization.labels(device_id=device_id).set(metrics.memory_utilization)

                self.temperature.labels(device_id=device_id).set(metrics.temperature)

                self.power_usage.labels(device_id=device_id).set(metrics.power_usage)

                self.power_limit.labels(device_id=device_id).set(metrics.power_limit)

                self.sm_clock.labels(device_id=device_id).set(metrics.sm_clock)

                self.memory_clock.labels(device_id=device_id).set(metrics.memory_clock)

                self.pcie_throughput_tx.labels(device_id=device_id).set(metrics.pcie_throughput_tx)

                self.pcie_throughput_rx.labels(device_id=device_id).set(metrics.pcie_throughput_rx)

            # 获取性能指标
            perf_metrics = await self.perf_collector.collect_performance_metrics()

            # 更新性能指标（使用device 0）
            self.matrix_gflops.labels(device_id=0).set(perf_metrics.matrix_gflops)
            self.matrix_speedup.labels(device_id=0).set(perf_metrics.matrix_speedup)
            self.matrix_throughput.labels(device_id=0).set(perf_metrics.matrix_throughput)
            self.memory_bandwidth.labels(device_id=0).set(perf_metrics.memory_bandwidth_gbs)
            self.memory_speedup.labels(device_id=0).set(perf_metrics.memory_speedup)
            self.memory_throughput.labels(device_id=0).set(perf_metrics.memory_throughput)
            self.overall_speedup.labels(device_id=0).set(perf_metrics.overall_speedup)
            self.cache_hit_rate.labels(device_id=0).set(perf_metrics.cache_hit_rate)
            self.success_rate.labels(device_id=0).set(perf_metrics.success_rate)

            # 记录基准测试
            self.benchmark_runs.labels(device_id=0).inc()

            logger.info("GPU metrics collected and updated")
            return True

        except Exception as e:
            logger.error(f"Failed to collect GPU metrics: {e}")
            return False

    async def update_loop(self, interval: int = 10):
        """定期更新指标"""
        logger.info(f"Starting GPU metrics update loop (interval: {interval}s)")

        while self.running:
            await self.collect_metrics()
            await asyncio.sleep(interval)

    def start(self, port: int = 9100, interval: int = 10):
        """启动Prometheus exporter"""
        logger.info(f"Starting GPU metrics exporter on port {port}")

        # 启动Prometheus HTTP服务器
        start_http_server(port)
        logger.info(f"✅ Prometheus metrics available at http://localhost:{port}/metrics")

        # 标记为运行中
        self.running = True

        # 启动更新循环
        try:
            asyncio.run(self.update_loop(interval))
        except KeyboardInterrupt:
            logger.info("Shutting down GPU metrics exporter")
            self.running = False


def main():
    """主函数"""
    import sys

    # 解析参数
    port = 9100
    interval = 10

    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    if len(sys.argv) > 2:
        interval = int(sys.argv[2])

    print(
        f"""
╔══════════════════════════════════════════════════════════╗
║         GPU Metrics Prometheus Exporter                ║
╚══════════════════════════════════════════════════════════╝

Configuration:
  Port: {port}
  Update Interval: {interval}s

Metrics URL: http://localhost:{port}/metrics

Press Ctrl+C to stop...
"""
    )

    # 创建并启动exporter
    exporter = GPUMetricsExporter()
    exporter.start(port=port, interval=interval)


if __name__ == "__main__":
    main()
