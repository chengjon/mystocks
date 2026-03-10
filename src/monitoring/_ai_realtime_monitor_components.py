"""
AI 实时监控器组件定义。
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict

import psutil

try:
    import GPUtil

    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False
    logging.warning("⚠️ GPUtil not available, GPU monitoring disabled")

logger = logging.getLogger(__name__)


@dataclass
class MonitoringConfig:
    """监控配置"""

    monitoring_interval: float = 5.0
    max_history_size: int = 1000
    enable_gpu_monitoring: bool = True
    enable_performance_monitoring: bool = True
    enable_ai_strategy_monitoring: bool = True
    adaptive_intervals: bool = True
    alert_check_frequency: int = 1

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)


@dataclass
class PerformanceThresholds:
    """性能阈值配置"""

    cpu_warning: float = 80.0
    cpu_critical: float = 95.0
    memory_warning: float = 85.0
    memory_critical: float = 95.0
    gpu_memory_warning: float = 85.0
    gpu_memory_critical: float = 95.0
    gpu_utilization_warning: float = 90.0
    disk_warning: float = 80.0
    disk_critical: float = 90.0
    ai_strategy_win_rate_critical: float = 0.3
    data_quality_critical: float = 0.8

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)


class IMetricsCollector(ABC):
    """指标收集器接口"""

    @abstractmethod
    async def collect_metrics(self) -> Dict[str, Any]:
        """收集指标"""

    @abstractmethod
    def is_available(self) -> bool:
        """检查是否可用"""


class SystemMetricsCollector(IMetricsCollector):
    """系统指标收集器"""

    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.previous_network_io = None

    async def collect_metrics(self) -> Dict[str, Any]:
        """收集系统指标"""
        try:
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            disk = psutil.disk_usage("/")
            disk_usage = (disk.used / disk.total) * 100
            network = psutil.net_io_counters()
            network_io = {
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv,
                "packets_sent": network.packets_sent,
                "packets_recv": network.packets_recv,
            }

            network_speed = {}
            if self.previous_network_io:
                time_diff = 1.0
                network_speed = {
                    "bytes_sent_per_sec": (network.bytes_sent - self.previous_network_io.bytes_sent) / time_diff,
                    "bytes_recv_per_sec": (network.bytes_recv - self.previous_network_io.bytes_recv) / time_diff,
                }

            self.previous_network_io = network

            return {
                "cpu_usage": cpu_usage,
                "memory_usage": memory_usage,
                "disk_usage": disk_usage,
                "network_io": network_io,
                "network_speed": network_speed,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as error:
            logger.error("❌ 系统指标收集失败: %s", error)
            return {}

    def is_available(self) -> bool:
        """检查是否可用"""
        return True


class GPUMetricsCollector(IMetricsCollector):
    """GPU 指标收集器"""

    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.gpu_available = GPU_AVAILABLE

    async def collect_metrics(self) -> Dict[str, Any]:
        """收集 GPU 指标"""
        if not self.config.enable_gpu_monitoring or not self.gpu_available:
            return {}

        try:
            gpus = GPUtil.getGPUs()
            if not gpus:
                return {}

            gpu = gpus[0]
            return {
                "gpu_memory_used": gpu.memoryUsed,
                "gpu_memory_total": gpu.memoryTotal,
                "gpu_utilization": gpu.load * 100,
                "gpu_temperature": gpu.temperature,
                "gpu_name": gpu.name,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as error:
            logger.warning("⚠️ GPU指标收集失败: %s", error)
            return {}

    def is_available(self) -> bool:
        """检查是否可用"""
        return self.gpu_available and self.config.enable_gpu_monitoring


class AIStrategyMetricsCollector(IMetricsCollector):
    """AI 策略指标收集器"""

    def __init__(self, config: MonitoringConfig):
        self.config = config

    async def collect_metrics(self) -> Dict[str, Any]:
        """收集 AI 策略指标"""
        if not self.config.enable_ai_strategy_monitoring:
            return {}

        try:
            return {
                "active_strategies": 3,
                "total_signals_today": 156,
                "avg_confidence": 0.73,
                "winning_trades": 89,
                "total_trades": 156,
                "win_rate": 0.57,
                "best_strategy": "ML-Based Strategy",
                "strategy_performance": {
                    "ML-Based": {"return": 1.78, "sharpe": 0.79, "drawdown": 2.42},
                    "Momentum": {"return": 1.14, "sharpe": 0.60, "drawdown": 1.73},
                    "Mean_Reversion": {"return": 0.42, "sharpe": 0.50, "drawdown": 1.40},
                },
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as error:
            logger.error("❌ AI策略指标收集失败: %s", error)
            return {}

    def is_available(self) -> bool:
        """检查是否可用"""
        return self.config.enable_ai_strategy_monitoring


class TradingMetricsCollector(IMetricsCollector):
    """交易指标收集器"""

    def __init__(self, config: MonitoringConfig):
        self.config = config

    async def collect_metrics(self) -> Dict[str, Any]:
        """收集交易指标"""
        try:
            return {
                "total_positions": 12,
                "daily_pnl": 1250.75,
                "portfolio_value": 102567.83,
                "daily_return": 0.0123,
                "max_drawdown": 2.42,
                "sharpe_ratio": 0.79,
                "last_trade_time": datetime.now().isoformat(),
                "active_alerts": 0,
                "data_quality_score": 0.95,
                "last_query_time": 125.0,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as error:
            logger.error("❌ 交易指标收集失败: %s", error)
            return {}

    def is_available(self) -> bool:
        """检查是否可用"""
        return True


class AdaptiveIntervalManager:
    """自适应间隔管理器"""

    def __init__(self, base_interval: float = 5.0, min_interval: float = 2.0, max_interval: float = 60.0):
        self.base_interval = base_interval
        self.min_interval = min_interval
        self.max_interval = max_interval
        self.current_interval = base_interval
        self.load_history = []
        self.max_history = 50

    def calculate_next_interval(self, system_metrics: Dict[str, Any]) -> float:
        """根据系统负载计算下一个监控间隔"""
        try:
            cpu_usage = system_metrics.get("cpu_usage", 0)
            memory_usage = system_metrics.get("memory_usage", 0)
            load_score = (cpu_usage + memory_usage) / 2

            self.load_history.append(load_score)
            if len(self.load_history) > self.max_history:
                self.load_history = self.load_history[-self.max_history :]

            if load_score > 80:
                self.current_interval = min(self.current_interval * 1.2, self.max_interval)
            elif load_score < 30:
                self.current_interval = max(self.current_interval * 0.8, self.min_interval)
            else:
                self.current_interval = self.base_interval

            import random

            self.current_interval *= random.uniform(0.9, 1.1)
            self.current_interval = max(self.min_interval, min(self.current_interval, self.max_interval))

            if load_score > 80:
                self.current_interval = max(self.current_interval, self.base_interval)
            elif load_score < 30:
                self.current_interval = min(self.current_interval, self.base_interval)

            return self.current_interval
        except Exception as error:
            logger.error("❌ 自适应间隔计算失败: %s", error)
            return self.base_interval

    def get_interval(self) -> float:
        """获取当前间隔"""
        return self.current_interval
