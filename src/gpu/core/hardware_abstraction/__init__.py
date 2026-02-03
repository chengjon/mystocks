"""
GPU硬件抽象层 (Hardware Abstraction Layer)
统一GPU资源管理，策略隔离，低延迟优化，故障容灾

Phase 6.2 GPU加速引擎架构重构
"""

from .health_monitor import DeviceHealthMonitor, PerformanceThreshold
from .interfaces import (
    AllocationRequest,
    IGPUResourceProvider,
    IStrategyContext,
    PerformanceProfile,
    StrategyPriority,
)
from .memory_pool import MemoryPool
from .realtime_path import RealTimeGPUPath
from .resource_manager import GPUResourceManager
from .strategy_context import StrategyGPUContext


def get_gpu_resource_manager():
    """获取GPU资源管理器实例"""
    return GPUResourceManager()


def get_strategy_context():
    """获取策略GPU上下文实例"""
    return StrategyGPUContext()


def get_realtime_path():
    """获取实时GPU路径实例"""
    return RealTimeGPUPath()


def get_health_monitor():
    """获取设备健康监控实例"""
    return DeviceHealthMonitor()


def get_memory_pool():
    """获取内存池实例"""
    return MemoryPool()


__all__ = [
    # 核心资源管理
    "GPUResourceManager",
    "StrategyGPUContext",
    "StrategyPriority",
    # 低延迟执行路径
    "RealTimeGPUPath",
    # 健康监控
    "DeviceHealthMonitor",
    "PerformanceThreshold",
    # 内存管理
    "MemoryPool",
    # 接口定义
    "AllocationRequest",
    "IGPUResourceProvider",
    "IStrategyContext",
    "PerformanceProfile",
    # 便捷函数
    "get_gpu_resource_manager",
    "get_strategy_context",
    "get_realtime_path",
    "get_health_monitor",
    "get_memory_pool",
]
