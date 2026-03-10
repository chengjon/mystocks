"""Runtime tail extracted from `test_stress_test.py`."""

from __future__ import annotations

import asyncio
import time
from datetime import datetime
from typing import Any, Dict, List

import psutil


class SystemMonitor:
    """系统监控器"""

    def __init__(self, monitor_interval: int = 5):
        self.monitor_interval = monitor_interval
        self.metrics_history = []

    async def monitor(self, duration_minutes: int) -> List[Dict[str, Any]]:
        """监控系统性能"""
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)

        while time.time() < end_time:
            metrics = self._collect_metrics()
            self.metrics_history.append(metrics)
            await asyncio.sleep(self.monitor_interval)

        return self.metrics_history

    def _collect_metrics(self) -> Dict[str, Any]:
        """收集当前性能指标"""
        return {
            "timestamp": datetime.now().isoformat(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_io_read": psutil.disk_io_counters().read_bytes if psutil.disk_io_counters() else 0,
            "disk_io_write": psutil.disk_io_counters().write_bytes if psutil.disk_io_counters() else 0,
            "network_io": psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv,
        }


async def test_gradual_stress():
    """逐步增加压力测试"""
    from tests.performance.test_stress_test import StressTestConfig, StressTestSuite, StressTestType

    config = StressTestConfig(
        test_type=StressTestType.GRADUAL,
        initial_users=10,
        max_users=200,
        increment_rate=20,
        increment_interval=15,
        max_duration_minutes=5,
    )

    suite = StressTestSuite(config)
    report = await suite.run_stress_test()

    assert suite.result.total_requests > 0
    assert report


async def test_burst_stress():
    """突发压力测试"""
    from tests.performance.test_stress_test import StressTestConfig, StressTestSuite, StressTestType

    config = StressTestConfig(test_type=StressTestType.BURST, max_users=300, max_duration_minutes=5)
    suite = StressTestSuite(config)
    report = await suite.run_stress_test()

    assert suite.result.total_requests > 0
    assert report


async def test_extreme_stress():
    """极限压力测试"""
    from tests.performance.test_stress_test import StressTestConfig, StressTestSuite, StressTestType

    config = StressTestConfig(test_type=StressTestType.EXTREME, max_users=500, max_duration_minutes=3)
    suite = StressTestSuite(config)
    report = await suite.run_stress_test()

    assert suite.result.total_requests > 0
    assert report


async def run_stress_test_example() -> str:
    """运行压力测试示例并返回报告路径。"""
    from tests.performance.test_stress_test import StressTestConfig, StressTestSuite, StressTestType

    config = StressTestConfig(
        test_type=StressTestType.GRADUAL,
        initial_users=10,
        max_users=200,
        increment_rate=20,
        increment_interval=15,
        max_duration_minutes=5,
    )
    suite = StressTestSuite(config)
    return await suite.run_stress_test()


__all__ = [
    "SystemMonitor",
    "run_stress_test_example",
    "test_burst_stress",
    "test_extreme_stress",
    "test_gradual_stress",
]
