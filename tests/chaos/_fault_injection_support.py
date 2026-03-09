"""Support utilities extracted from ``tests.chaos.test_fault_injection``."""

from __future__ import annotations

import asyncio
import random
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List

import psutil

if TYPE_CHECKING:
    from tests.chaos.test_fault_injection import FaultInjectionConfig


class MetricsCollector:
    """指标收集器"""

    def __init__(self):
        self.process = psutil.Process()
        self.network_stats = psutil.net_io_counters()

    def collect_system_metrics(self) -> Dict[str, Any]:
        """收集系统指标"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")
            network = psutil.net_io_counters()
            process_memory = self.process.memory_info()
            process_cpu = self.process.cpu_percent()
            app_metrics = {
                "avg_response_time": random.uniform(50, 500),
                "error_rate": random.uniform(0, 0.05),
                "active_connections": random.randint(10, 100),
                "request_count": random.randint(100, 1000),
            }

            return {
                "timestamp": datetime.now().isoformat(),
                "cpu": {"percent": cpu_percent, "count": cpu_count, "process_percent": process_cpu},
                "memory": {
                    "total_mb": memory.total / 1024 / 1024,
                    "available_mb": memory.available / 1024 / 1024,
                    "percent": memory.percent,
                    "used_mb": memory.used / 1024 / 1024,
                    "process_rss_mb": process_memory.rss / 1024 / 1024,
                },
                "disk": {
                    "total_gb": disk.total / 1024 / 1024 / 1024,
                    "used_gb": disk.used / 1024 / 1024 / 1024,
                    "free_gb": disk.free / 1024 / 1024 / 1024,
                    "percent": disk.percent,
                },
                "network": {
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv,
                    "packets_sent": network.packets_sent,
                    "packets_recv": network.packets_recv,
                },
                "application": app_metrics,
            }
        except Exception as error:
            print(f"⚠️  指标收集失败: {str(error)}")
            return {}


class RecoveryMonitor:
    """恢复监控器"""

    def __init__(self):
        self.recovery_events = []
        self.health_checks = {}

    async def monitor_recovery(self, fault_id: str, recovery_start: datetime):
        """监控恢复过程"""
        start_time = datetime.now()

        while True:
            health_status = await self._check_system_health()
            self.recovery_events.append(
                {
                    "fault_id": fault_id,
                    "timestamp": datetime.now().isoformat(),
                    "health_status": health_status,
                    "recovery_duration": (datetime.now() - start_time).total_seconds(),
                }
            )

            if health_status == "healthy":
                print("    ✅ 系统已恢复正常")
                break

            await asyncio.sleep(2)

    async def _check_system_health(self) -> str:
        """检查系统健康状态"""
        try:
            await asyncio.sleep(0.1)
            return "healthy"
        except Exception:
            return "recovering"


class ControlPlane:
    """控制平面 - 用于协调故障注入和恢复"""

    def __init__(self):
        self.delay_handlers = []
        self.packet_loss_handlers = []
        self.fault_active = False

    async def inject_fault(self, config: "FaultInjectionConfig"):
        """通用故障注入方法"""
        print(f"    🎛️  控制平面注入故障: {config.fault_type.value}")
        self.fault_active = True

    async def recover_fault(self, config: "FaultInjectionConfig"):
        """通用故障恢复方法"""
        print(f"    🎛️  控制平面恢复故障: {config.fault_type.value}")
        self.fault_active = False

    async def simulate_network_partition(self, duration: int):
        """模拟网络分区"""
        print(f"    🔗 控制平面: 模拟网络分区 {duration} 秒")

    async def simulate_database_timeout(self, timeout: int):
        """模拟数据库超时"""
        print(f"    🗄️  控制平面: 模拟数据库超时 {timeout} 秒")

    async def simulate_api_error(self, error_code: int, error_rate: float):
        """模拟API错误"""
        print(f"    🚫 控制平面: 模拟API错误 {error_code} (错误率: {error_rate * 100}%)")

    async def simulate_memory_pressure(self, memory_mb: int):
        """模拟内存压力"""
        print(f"    💾 控制平面: 模拟内存压力 {memory_mb}MB")

    async def simulate_cpu_pressure(self, cpu_percent: int):
        """模拟CPU压力"""
        print(f"    ⚡ 控制平面: 模拟CPU压力 {cpu_percent}%")

    def register_delay_handler(self, handler):
        """注册延迟处理器"""
        self.delay_handlers.append(handler)

    def register_packet_loss_handler(self, handler):
        """注册丢包处理器"""
        self.packet_loss_handlers.append(handler)

    def unregister_delay_handler(self):
        """注销延迟处理器"""
        self.delay_handlers.clear()

    def unregister_packet_loss_handler(self):
        """注销丢包处理器"""
        self.packet_loss_handlers.clear()


class FaultGenerator:
    """故障生成器 - 用于生成随机故障场景"""

    def __init__(self):
        from tests.chaos.test_fault_injection import FaultSeverity, FaultType

        self.fault_templates = [
            {"type": FaultType.NETWORK_DELAY, "severity": FaultSeverity.MEDIUM, "parameters": {"delay_ms": 1000}},
            {"type": FaultType.NETWORK_PACKET_LOSS, "severity": FaultSeverity.MEDIUM, "parameters": {"loss_rate": 0.1}},
            {"type": FaultType.DATABASE_TIMEOUT, "severity": FaultSeverity.HIGH, "parameters": {"timeout_seconds": 5}},
            {
                "type": FaultType.API_ERROR,
                "severity": FaultSeverity.MEDIUM,
                "parameters": {"error_code": 500, "error_rate": 0.2},
            },
            {
                "type": FaultType.MEMORY_PRESSURE,
                "severity": FaultSeverity.HIGH,
                "parameters": {"memory_usage_mb": 2048},
            },
        ]

    def generate_random_fault(self) -> "FaultInjectionConfig":
        """生成随机故障配置"""
        from tests.chaos.test_fault_injection import FaultInjectionConfig

        template = random.choice(self.fault_templates)
        return FaultInjectionConfig(
            fault_type=template["type"],
            severity=template["severity"],
            parameters=template["parameters"],
            duration_seconds=random.randint(10, 60),
            recovery_time_seconds=random.randint(5, 20),
        )

    def generate_chaos_scenario(self, fault_count: int = 5) -> List["FaultInjectionConfig"]:
        """生成混沌工程测试场景"""
        configs = []
        for _index in range(fault_count):
            fault = self.generate_random_fault()
            fault.duration_seconds = random.randint(30, 120)
            configs.append(fault)
        return configs


def demo_fault_injection():
    """演示故障注入系统功能"""
    from tests.chaos.test_fault_injection import FaultInjectionConfig, FaultInjector, FaultSeverity, FaultType

    print("🎭 演示故障注入系统功能")
    injector = FaultInjector()
    configs = [
        FaultInjectionConfig(
            fault_type=FaultType.NETWORK_DELAY,
            severity=FaultSeverity.MEDIUM,
            parameters={"delay_ms": 500},
            duration_seconds=30,
        ),
        FaultInjectionConfig(
            fault_type=FaultType.DATABASE_TIMEOUT,
            severity=FaultSeverity.HIGH,
            parameters={"timeout_seconds": 3},
            duration_seconds=20,
        ),
        FaultInjectionConfig(
            fault_type=FaultType.API_ERROR,
            severity=FaultSeverity.MEDIUM,
            parameters={"error_code": 500, "error_rate": 0.3},
            duration_seconds=15,
        ),
        FaultInjectionConfig(
            fault_type=FaultType.MEMORY_PRESSURE,
            severity=FaultSeverity.HIGH,
            parameters={"memory_usage_mb": 1024},
            duration_seconds=25,
        ),
    ]

    for config in configs:
        injector.add_fault_config(config)

    asyncio.run(injector.run_comprehensive_fault_injection())


__all__ = [
    "MetricsCollector",
    "RecoveryMonitor",
    "ControlPlane",
    "FaultGenerator",
    "demo_fault_injection",
]
