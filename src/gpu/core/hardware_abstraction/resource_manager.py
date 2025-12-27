"""
GPU资源管理器
统一管理GPU设备检测、分配、策略隔离和优先级抢占
"""

import asyncio
import logging
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, field

try:
    import pynvml

    NVML_AVAILABLE = True
except ImportError:
    NVML_AVAILABLE = False
    print("Warning: pynvml not available, GPU detection will be simulated")

from .interfaces import (
    IGPUResourceProvider,
    IStrategyContext,
    StrategyPriority,
    GPUDeviceInfo,
    AllocationRequest,
    PerformanceProfile,
)
from .memory_pool import MemoryPool
from .strategy_context import StrategyGPUContext


logger = logging.getLogger(__name__)


@dataclass
class DeviceAllocation:
    """设备分配状态"""

    device_id: int
    allocated_strategies: Dict[str, IStrategyContext] = field(default_factory=dict)
    total_allocated_memory: int = 0
    peak_memory_usage: int = 0

    def add_strategy(self, strategy_id: str, context: IStrategyContext, memory_mb: int):
        self.allocated_strategies[strategy_id] = context
        self.total_allocated_memory += memory_mb
        self.peak_memory_usage = max(self.peak_memory_usage, self.total_allocated_memory)

    def remove_strategy(self, strategy_id: str, memory_mb: int):
        if strategy_id in self.allocated_strategies:
            del self.allocated_strategies[strategy_id]
            self.total_allocated_memory = max(0, self.total_allocated_memory - memory_mb)


class GPUResourceManager(IGPUResourceProvider):
    """GPU资源管理器 - HAL层的核心组件"""

    def __init__(self):
        self.devices: Dict[int, GPUDeviceInfo] = {}
        self.device_allocations: Dict[int, DeviceAllocation] = {}
        self.strategy_contexts: Dict[str, IStrategyContext] = {}
        self.available_devices: Set[int] = set()
        self._initialized = False
        self._lock = asyncio.Lock()

        # 性能阈值配置
        self.memory_threshold = 0.85  # 85%显存使用率阈值
        self.compute_threshold = 0.9  # 90%算力使用率阈值

        logger.info("GPUResourceManager initialized")

    async def initialize(self) -> bool:
        """初始化GPU资源管理器"""
        try:
            logger.info("Initializing GPU resource manager...")

            # 检测GPU设备
            await self._detect_gpu_devices()

            if not self.devices:
                logger.warning("No GPU devices detected")
                return False

            # 初始化设备分配状态
            for device_id in self.devices:
                self.device_allocations[device_id] = DeviceAllocation(device_id=device_id)
                self.available_devices.add(device_id)

            self._initialized = True
            logger.info(f"GPU ResourceManager initialized with {len(self.devices)} devices")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize GPU ResourceManager: {e}")
            return False

    async def _detect_gpu_devices(self) -> None:
        """检测GPU设备"""
        if NVML_AVAILABLE:
            await self._detect_nvidia_devices()
        else:
            # 模拟设备用于开发环境
            await self._simulate_gpu_devices()

    async def _detect_nvidia_devices(self) -> None:
        """检测NVIDIA GPU设备"""
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()

            for i in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                # 兼容不同版本的pynvml库
                name_raw = pynvml.nvmlDeviceGetName(handle)
                if isinstance(name_raw, bytes):
                    name = name_raw.decode("utf-8")
                else:
                    name = str(name_raw)

                # 获取内存信息
                mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                memory_total = mem_info.total // (1024 * 1024)  # Convert to MB

                # 获取计算能力
                try:
                    major, minor = pynvml.nvmlDeviceGetCudaComputeCapability(handle)
                    compute_capability = (major, minor)
                except Exception:
                    compute_capability = (0, 0)

                device = GPUDeviceInfo(
                    device_id=i,
                    name=name,
                    memory_total=memory_total,
                    compute_capability=compute_capability,
                    is_available=True,
                    current_memory_usage=0,
                    current_utilization=0.0,
                )

                self.devices[i] = device
                logger.info(f"Detected GPU {i}: {name} ({memory_total}MB)")

            pynvml.nvmlShutdown()

        except Exception as e:
            logger.error(f"Failed to detect NVIDIA devices: {e}")
            await self._simulate_gpu_devices()

    async def _simulate_gpu_devices(self) -> None:
        """模拟GPU设备（开发环境使用）"""
        simulated_devices = [
            GPUDeviceInfo(
                device_id=0,
                name="NVIDIA RTX 4090 (Simulated)",
                memory_total=24576,  # 24GB
                compute_capability=(8, 9),
                is_available=True,
                current_memory_usage=0,
                current_utilization=0.0,
            ),
            GPUDeviceInfo(
                device_id=1,
                name="NVIDIA A100 (Simulated)",
                memory_total=40960,  # 40GB
                compute_capability=(8, 0),
                is_available=True,
                current_memory_usage=0,
                current_utilization=0.0,
            ),
        ]

        for device in simulated_devices:
            self.devices[device.device_id] = device
            logger.info(f"Simulated GPU {device.device_id}: {device.name} ({device.memory_total}MB)")

    def get_available_devices(self) -> List[GPUDeviceInfo]:
        """获取可用GPU设备列表"""
        if not self._initialized:
            return []

        return [device for device in self.devices.values() if device.is_available]

    async def allocate_context(self, request: AllocationRequest) -> Optional[IStrategyContext]:
        """为策略分配GPU上下文"""
        async with self._lock:
            if not self._initialized:
                logger.error("GPU ResourceManager not initialized")
                return None

            # 检查策略是否已存在
            if request.strategy_id in self.strategy_contexts:
                logger.warning(f"Strategy {request.strategy_id} already has context")
                return self.strategy_contexts[request.strategy_id]

            # 选择最佳GPU设备
            device_id = await self._select_best_device(request)
            if device_id is None:
                # 尝试抢占低优先级策略
                device_id = await self._try_preempt_low_priority_strategies(request)
                if device_id is None:
                    logger.error(f"No available GPU for strategy {request.strategy_id}")
                    return None

            # 创建策略上下文
            context = await self._create_strategy_context(device_id, request)
            if context is None:
                return None

            # 记录分配
            device_allocation = self.device_allocations[device_id]
            device_allocation.add_strategy(request.strategy_id, context, request.required_memory)
            self.strategy_contexts[request.strategy_id] = context

            logger.info(f"Allocated GPU context for strategy {request.strategy_id} on device {device_id}")
            return context

    async def _select_best_device(self, request: AllocationRequest) -> Optional[int]:
        """选择最佳GPU设备"""
        suitable_devices = []

        for device_id, device in self.devices.items():
            if not device.is_available:
                continue

            device_allocation = self.device_allocations[device_id]

            # 检查内存是否足够
            available_memory = device.memory_total - device_allocation.total_allocated_memory
            if available_memory < request.required_memory:
                continue

            # 检查设备利用率
            if device.current_utilization > 0.9:  # 90%以上设备不考虑
                continue

            suitable_devices.append((device_id, available_memory, device.current_utilization))

        if not suitable_devices:
            return None

        # 选择可用内存最多且利用率最低的设备
        suitable_devices.sort(key=lambda x: (x[2], -x[1]))  # 先按利用率升序，再按可用内存降序
        return suitable_devices[0][0]

    async def _try_preempt_low_priority_strategies(self, request: AllocationRequest) -> Optional[int]:
        """尝试抢占低优先级策略资源"""
        if request.priority == StrategyPriority.LOW:
            return None  # 低优先级策略不能抢占其他策略

        # 收集可抢占的策略
        preemptible_strategies = []

        for device_id, device_allocation in self.device_allocations.items():
            for strategy_id, context in device_allocation.allocated_strategies.items():
                strategy_priority = getattr(context, "priority", StrategyPriority.MEDIUM)

                # 只有高优先级策略可以抢占中低优先级策略
                if request.priority.value < strategy_priority.value:
                    available_memory = self.devices[device_id].memory_total - (
                        device_allocation.total_allocated_memory - getattr(context, "allocated_memory", 0)
                    )

                    if available_memory >= request.required_memory:
                        preemptible_strategies.append(
                            (
                                device_id,
                                strategy_id,
                                strategy_priority,
                                available_memory,
                            )
                        )

        if not preemptible_strategies:
            return None

        # 选择最佳抢占目标（最低优先级，最大可用内存）
        preemptible_strategies.sort(key=lambda x: (x[2].value, -x[3]))
        device_id, strategy_id, _, _ = preemptible_strategies[0]

        # 执行抢占
        logger.info(f"Preempting low priority strategy {strategy_id} on device {device_id}")
        success = await self._execute_preemption(device_id, strategy_id)

        if success:
            return device_id
        else:
            logger.error(f"Failed to preempt strategy {strategy_id}")
            return None

    async def _execute_preemption(self, device_id: int, strategy_id: str) -> bool:
        """执行策略抢占"""
        try:
            context = self.strategy_contexts.get(strategy_id)
            if context:
                # 优雅抢占：先通知策略，然后释放资源
                success = await context.preempt_resources()
                if success:
                    await self.release_context(strategy_id)
                    return True
            return False
        except Exception as e:
            logger.error(f"Error during preemption of strategy {strategy_id}: {e}")
            return False

    async def _create_strategy_context(self, device_id: int, request: AllocationRequest) -> Optional[IStrategyContext]:
        """创建策略上下文"""
        try:
            # 创建内存池配置
            memory_config = {
                "pool_size_mb": request.required_memory,
                "device_id": device_id,
                "strategy_id": request.strategy_id,
            }
            memory_pool = MemoryPool(memory_config)

            # 使用默认性能配置
            performance_profile = request.performance_profile or PerformanceProfile()

            # 创建策略上下文
            context = StrategyGPUContext(
                strategy_id=request.strategy_id,
                device_id=device_id,
                priority=request.priority,
                memory_pool=memory_pool,
                performance_profile=performance_profile,
                resource_manager=self,
            )

            return context

        except Exception as e:
            logger.error(f"Failed to create strategy context: {e}")
            return None

    async def release_context(self, strategy_id: str) -> bool:
        """释放策略GPU上下文"""
        async with self._lock:
            if strategy_id not in self.strategy_contexts:
                logger.warning(f"Strategy {strategy_id} context not found")
                return False

            context = self.strategy_contexts[strategy_id]
            device_id = context.get_device_id()

            # 清理内存池
            try:
                memory_pool = context.get_memory_pool()
                memory_pool.cleanup()
            except Exception as e:
                logger.error(f"Error cleaning up memory pool for strategy {strategy_id}: {e}")

            # 从设备分配中移除
            if device_id in self.device_allocations:
                device_allocation = self.device_allocations[device_id]
                allocated_memory = getattr(context, "allocated_memory", 0)
                device_allocation.remove_strategy(strategy_id, allocated_memory)

            # 移除策略上下文
            del self.strategy_contexts[strategy_id]

            logger.info(f"Released GPU context for strategy {strategy_id}")
            return True

    def get_device_health(self, device_id: int) -> Dict[str, Any]:
        """获取GPU设备健康状态"""
        if device_id not in self.devices:
            return {"error": f"Device {device_id} not found"}

        device = self.devices[device_id]
        allocation = self.device_allocations.get(device_id)

        health = {
            "device_id": device_id,
            "name": device.name,
            "is_available": device.is_available,
            "memory_total_mb": device.memory_total,
            "memory_used_mb": device.current_memory_usage,
            "memory_utilization": device.current_memory_usage / device.memory_total,
            "compute_utilization": device.current_utilization,
            "allocated_strategies": len(allocation.allocated_strategies) if allocation else 0,
            "allocated_memory_mb": allocation.total_allocated_memory if allocation else 0,
            "peak_memory_usage_mb": allocation.peak_memory_usage if allocation else 0,
            "health_status": self._calculate_health_status(device),
        }

        return health

    def _calculate_health_status(self, device: GPUDeviceInfo) -> str:
        """计算设备健康状态"""
        if not device.is_available:
            return "unavailable"

        memory_utilization = device.current_memory_usage / device.memory_total

        if device.current_utilization > 0.95 or memory_utilization > 0.95:
            return "critical"
        elif device.current_utilization > 0.85 or memory_utilization > 0.85:
            return "warning"
        else:
            return "healthy"

    async def get_strategy_context(self, strategy_id: str) -> Optional[IStrategyContext]:
        """获取策略上下文"""
        return self.strategy_contexts.get(strategy_id)

    async def update_device_metrics(self) -> None:
        """更新设备指标（定期调用）"""
        if NVML_AVAILABLE and self._initialized:
            try:
                pynvml.nvmlInit()

                for device_id, device in self.devices.items():
                    try:
                        handle = pynvml.nvmlDeviceGetHandleByIndex(device_id)

                        # 更新内存使用情况
                        mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                        device.current_memory_usage = mem_info.used // (1024 * 1024)

                        # 更新GPU利用率
                        try:
                            utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
                            device.current_utilization = utilization.gpu / 100.0
                        except Exception:
                            device.current_utilization = 0.0

                    except Exception as e:
                        logger.warning(f"Failed to update metrics for device {device_id}: {e}")
                        device.current_utilization = 0.0
                        device.current_memory_usage = 0

                pynvml.nvmlShutdown()

            except Exception as e:
                logger.warning(f"Failed to update device metrics: {e}")

    def get_resource_usage_summary(self) -> Dict[str, Any]:
        """获取资源使用摘要"""
        total_devices = len(self.devices)
        active_strategies = len(self.strategy_contexts)

        total_memory = sum(device.memory_total for device in self.devices.values())
        used_memory = sum(device.current_memory_usage for device in self.devices.values())
        allocated_memory = sum(allocation.total_allocated_memory for allocation in self.device_allocations.values())

        summary = {
            "total_devices": total_devices,
            "available_devices": len(self.available_devices),
            "active_strategies": active_strategies,
            "total_memory_mb": total_memory,
            "used_memory_mb": used_memory,
            "allocated_memory_mb": allocated_memory,
            "memory_utilization": used_memory / total_memory if total_memory > 0 else 0,
            "devices": [self.get_device_health(device_id) for device_id in self.devices.keys()],
        }

        return summary
