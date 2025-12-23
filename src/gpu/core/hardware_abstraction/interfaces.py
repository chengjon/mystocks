"""
GPU硬件抽象层接口定义
定义HAL组件的标准接口，确保组件间的松耦合
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import numpy as np


class StrategyPriority(Enum):
    """策略优先级"""

    HIGH = 1  # 实盘策略
    MEDIUM = 2  # 回测策略
    LOW = 3  # 分析任务


@dataclass
class GPUDeviceInfo:
    """GPU设备信息"""

    device_id: int
    name: str
    memory_total: int  # MB
    compute_capability: tuple
    is_available: bool
    current_memory_usage: int  # MB
    current_utilization: float  # 0.0-1.0


@dataclass
class PerformanceProfile:
    """性能配置"""

    max_memory_usage: float = 0.8  # 最大显存使用率
    max_compute_utilization: float = 0.9  # 最大算力使用率
    latency_target_ms: float = 1.0  # 延迟目标（毫秒）
    enable_preemption: bool = True  # 是否支持抢占


@dataclass
class AllocationRequest:
    """资源分配请求"""

    strategy_id: str
    priority: StrategyPriority
    required_memory: int  # MB
    required_compute_streams: int = 1
    performance_profile: Optional[PerformanceProfile] = None


@dataclass
class FailureResponse:
    """故障处理响应"""

    success: bool
    action_taken: str
    fallback_device: Optional[int] = None
    affected_strategies: List[str] = None
    recovery_time_ms: float = 0.0


class IGPUResourceProvider(ABC):
    """GPU资源提供者接口"""

    @abstractmethod
    async def initialize(self) -> bool:
        """初始化GPU资源提供者"""
        pass

    @abstractmethod
    def get_available_devices(self) -> List[GPUDeviceInfo]:
        """获取可用GPU设备列表"""
        pass

    @abstractmethod
    async def allocate_context(
        self, request: AllocationRequest
    ) -> Optional["IStrategyContext"]:
        """为策略分配GPU上下文"""
        pass

    @abstractmethod
    async def release_context(self, strategy_id: str) -> bool:
        """释放策略GPU上下文"""
        pass

    @abstractmethod
    def get_device_health(self, device_id: int) -> Dict[str, Any]:
        """获取GPU设备健康状态"""
        pass


class IStrategyContext(ABC):
    """策略上下文接口"""

    @abstractmethod
    def get_strategy_id(self) -> str:
        """获取策略ID"""
        pass

    @abstractmethod
    def get_device_id(self) -> int:
        """获取分配的GPU设备ID"""
        pass

    @abstractmethod
    def get_memory_pool(self) -> "MemoryPool":
        """获取策略内存池"""
        pass

    @abstractmethod
    def execute_compute(self, data: np.ndarray, kernel_name: str) -> np.ndarray:
        """执行GPU计算"""
        pass

    @abstractmethod
    def get_performance_metrics(self) -> Dict[str, float]:
        """获取性能指标"""
        pass

    @abstractmethod
    async def preempt_resources(self) -> bool:
        """被抢占资源时的处理"""
        pass


class IHealthMonitor(ABC):
    """健康监控接口"""

    @abstractmethod
    async def start_monitoring(self) -> None:
        """开始监控"""
        pass

    @abstractmethod
    async def handle_device_failure(self, device_id: int) -> FailureResponse:
        """处理设备故障"""
        pass

    @abstractmethod
    def check_performance_thresholds(self, device_id: int) -> List[str]:
        """检查性能阈值"""
        pass

    @abstractmethod
    def trigger_proactive_alert(
        self, device_id: int, alert_type: str, message: str
    ) -> None:
        """触发主动告警"""
        pass


class IRealTimeExecutor(ABC):
    """实时执行接口"""

    @abstractmethod
    async def prewarm_for_trading(
        self, strategy_contexts: List[IStrategyContext]
    ) -> bool:
        """为交易预热GPU资源"""
        pass

    @abstractmethod
    async def compile_common_kernels(self, kernel_names: List[str]) -> Dict[str, bool]:
        """编译常用核函数"""
        pass

    @abstractmethod
    async def allocate_and_lock_memory_pools(self, total_memory_mb: int) -> bool:
        """分配并锁定内存池"""
        pass

    @abstractmethod
    async def load_market_data_to_gpu(self, market_data: np.ndarray) -> bool:
        """加载行情数据到GPU"""
        pass

    @abstractmethod
    def get_prewarm_status(self) -> Dict[str, Any]:
        """获取预热状态"""
        pass


class IMemoryPool(ABC):
    """内存池接口"""

    @abstractmethod
    def allocate(self, size_bytes: int, strategy_id: str) -> Optional[int]:
        """分配内存"""
        pass

    @abstractmethod
    def deallocate(self, ptr: int, strategy_id: str) -> bool:
        """释放内存"""
        pass

    @abstractmethod
    def get_usage_statistics(self) -> Dict[str, Any]:
        """获取使用统计"""
        pass

    @abstractmethod
    def cleanup_fragmented_memory(self) -> int:
        """清理碎片内存"""
        pass

    @abstractmethod
    def enforce_strategy_limits(self) -> List[str]:
        """强制执行策略内存限制"""
        pass
