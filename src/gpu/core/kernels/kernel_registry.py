"""
GPU计算内核注册中心
提供内核的注册、发现和管理功能，支持动态内核加载和版本管理
"""

import asyncio
import importlib
import inspect
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Type

from .standardized_interface import KernelConfig, StandardizedKernelInterface

logger = logging.getLogger(__name__)


class KernelStatus(Enum):
    """内核状态"""

    REGISTERED = "registered"  # 已注册
    ACTIVE = "active"  # 活跃状态
    DISABLED = "disabled"  # 禁用状态
    ERROR = "error"  # 错误状态
    LOADING = "loading"  # 加载中


@dataclass
class KernelMetadata:
    """内核元数据"""

    name: str
    version: str
    description: str
    author: str
    created_at: float = field(default_factory=time.time)
    last_updated: float = field(default_factory=time.time)
    status: KernelStatus = KernelStatus.REGISTERED
    dependencies: List[str] = field(default_factory=list)
    supported_operations: List[str] = field(default_factory=list)
    gpu_required: bool = False
    memory_usage_mb: int = 0
    performance_score: float = 0.0
    error_count: int = 0
    success_count: int = 0
    average_execution_time_ms: float = 0.0


@dataclass
class KernelRegistration:
    """内核注册信息"""

    kernel_class: Type[StandardizedKernelInterface]
    metadata: KernelMetadata
    instance: Optional[StandardizedKernelInterface] = None
    is_initialized: bool = False
    load_error: Optional[str] = None


class KernelRegistry:
    """GPU计算内核注册中心"""

    def __init__(self):
        self._kernels: Dict[str, KernelRegistration] = {}
        self._operation_mappings: Dict[str, List[str]] = {}
        self._performance_cache: Dict[str, Dict[str, float]] = {}

        # 内核统计
        self.stats = {
            "total_kernels": 0,
            "active_kernels": 0,
            "error_kernels": 0,
            "total_executions": 0,
            "cache_hits": 0,
        }

    def register_kernel(
        self,
        kernel_class: Type[StandardizedKernelInterface],
        metadata: Optional[KernelMetadata] = None,
        auto_initialize: bool = False,
    ) -> bool:
        """注册内核"""
        try:
            # 创建元数据
            if metadata is None:
                metadata = self._create_default_metadata(kernel_class)

            name = metadata.name

            # 检查是否已存在
            if name in self._kernels:
                logger.warning("Kernel %s already exists, updating...", name)
                self._update_existing_kernel(name, kernel_class, metadata)
            else:
                # 创建新的注册
                registration = KernelRegistration(kernel_class=kernel_class, metadata=metadata)
                self._kernels[name] = registration

                logger.info("Registered kernel: %s v%s", name, metadata.version)

            # 自动初始化
            if auto_initialize:
                asyncio.create_task(self._initialize_kernel_async(name))

            # 更新操作映射
            self._update_operation_mappings(name, metadata.supported_operations)

            # 更新统计
            self._update_stats()

            return True

        except Exception as e:
            logger.error("Failed to register kernel %s: %s", kernel_class.__name__, e)
            return False

    async def unregister_kernel(self, name: str) -> bool:
        """注销内核"""
        if name not in self._kernels:
            logger.warning("Kernel %s not found for unregistration", name)
            return False

        try:
            registration = self._kernels[name]

            # 清理实例
            if registration.instance:
                # 如果有清理方法，调用它
                if hasattr(registration.instance, "cleanup"):
                    try:
                        await registration.instance.cleanup()
                    except Exception as e:
                        logger.warning("Error cleaning up kernel %s: %s", name, e)

            # 删除注册
            del self._kernels[name]

            # 清理操作映射
            self._remove_operation_mappings(name)

            # 清理性能缓存
            if name in self._performance_cache:
                del self._performance_cache[name]

            # 更新统计
            self._update_stats()

            logger.info("Unregistered kernel: %s", name)
            return True

        except Exception as e:
            logger.error("Failed to unregister kernel %s: %s", name, e)
            return False

    def get_kernel(self, name: str) -> Optional[StandardizedKernelInterface]:
        """获取内核实例"""
        if name not in self._kernels:
            return None

        registration = self._kernels[name]

        if registration.instance is None:
            logger.warning("Kernel %s not initialized", name)
            return None

        if registration.metadata.status != KernelStatus.ACTIVE:
            logger.warning("Kernel %s not active (status: %s)", name, registration.metadata.status.value)
            return None

        return registration.instance

    async def get_or_create_kernel(
        self, name: str, config: Optional[KernelConfig] = None
    ) -> Optional[StandardizedKernelInterface]:
        """获取或创建内核实例"""
        if name not in self._kernels:
            return None

        registration = self._kernels[name]

        # 如果实例已存在且活跃，直接返回
        if registration.instance is not None and registration.metadata.status == KernelStatus.ACTIVE:
            self.stats["cache_hits"] += 1
            return registration.instance

        # 创建新实例
        try:
            registration.metadata.status = KernelStatus.LOADING

            # 创建实例
            instance = registration.kernel_class(config)

            # 初始化
            if hasattr(instance, "initialize"):
                await instance.initialize()

            registration.instance = instance
            registration.is_initialized = True
            registration.metadata.status = KernelStatus.ACTIVE
            registration.metadata.last_updated = time.time()

            logger.info("Created and initialized kernel: %s", name)
            return instance

        except Exception as e:
            registration.metadata.status = KernelStatus.ERROR
            registration.load_error = str(e)
            registration.metadata.error_count += 1

            logger.error("Failed to create kernel %s: %s", name, e)
            return None

    def find_kernels_for_operation(self, operation_type: str, operation_name: Optional[str] = None) -> List[str]:
        """查找支持特定操作的内核"""
        matching_kernels = []

        for name, registration in self._kernels.items():
            if registration.metadata.status not in [
                KernelStatus.ACTIVE,
                KernelStatus.REGISTERED,
            ]:
                continue

            supported_ops = registration.metadata.supported_operations

            # 精确匹配
            if operation_name and operation_name in supported_ops:
                matching_kernels.append(name)
                continue

            # 类型匹配
            if any(op.startswith(operation_type) for op in supported_ops):
                matching_kernels.append(name)

        # 按性能评分排序
        matching_kernels.sort(key=lambda k: self._kernels[k].metadata.performance_score, reverse=True)

        return matching_kernels

    def get_best_kernel_for_operation(
        self,
        operation_type: str,
        operation_name: Optional[str] = None,
        data_shape: Optional[tuple] = None,
    ) -> Optional[str]:
        """获取执行特定操作的最佳内核"""
        candidates = self.find_kernels_for_operation(operation_type, operation_name)

        if not candidates:
            return None

        if len(candidates) == 1:
            return candidates[0]

        # 根据数据大小选择最优内核
        if data_shape:
            best_kernel = self._select_kernel_by_data_size(candidates, data_shape)
            if best_kernel:
                return best_kernel

        # 根据性能统计选择
        best_kernel = self._select_kernel_by_performance(candidates)
        return best_kernel

    def list_kernels(self, status_filter: Optional[KernelStatus] = None) -> Dict[str, KernelMetadata]:
        """列出所有内核"""
        result = {}

        for name, registration in self._kernels.items():
            if status_filter and registration.metadata.status != status_filter:
                continue

            result[name] = registration.metadata

        return result

    def get_kernel_info(self, name: str) -> Optional[Dict[str, Any]]:
        """获取内核详细信息"""
        if name not in self._kernels:
            return None

        registration = self._kernels[name]

        info = {
            "name": registration.metadata.name,
            "version": registration.metadata.version,
            "description": registration.metadata.description,
            "author": registration.metadata.author,
            "status": registration.metadata.status.value,
            "supported_operations": registration.metadata.supported_operations,
            "gpu_required": registration.metadata.gpu_required,
            "memory_usage_mb": registration.metadata.memory_usage_mb,
            "performance_score": registration.metadata.performance_score,
            "success_count": registration.metadata.success_count,
            "error_count": registration.metadata.error_count,
            "average_execution_time_ms": registration.metadata.average_execution_time_ms,
            "is_initialized": registration.is_initialized,
            "has_instance": registration.instance is not None,
            "load_error": registration.load_error,
        }

        # 添加性能缓存信息
        if name in self._performance_cache:
            info["performance_history"] = self._performance_cache[name]

        return info

    def update_kernel_performance(self, kernel_name: str, execution_time_ms: float, success: bool) -> None:
        """更新内核性能统计"""
        if kernel_name not in self._kernels:
            return

        registration = self._kernels[kernel_name]

        # 更新元数据
        if success:
            registration.metadata.success_count += 1
        else:
            registration.metadata.error_count += 1

        # 更新平均执行时间
        total_executions = registration.metadata.success_count + registration.metadata.error_count
        if total_executions > 0:
            current_avg = registration.metadata.average_execution_time_ms
            registration.metadata.average_execution_time_ms = (
                current_avg * (total_executions - 1) + execution_time_ms
            ) / total_executions

        # 更新性能评分
        registration.metadata.performance_score = self._calculate_performance_score(registration.metadata)

        # 更新性能缓存
        if kernel_name not in self._performance_cache:
            self._performance_cache[kernel_name] = {}

        timestamp = int(time.time() * 1000)
        self._performance_cache[kernel_name][str(timestamp)] = execution_time_ms

        # 限制缓存大小
        if len(self._performance_cache[kernel_name]) > 100:
            oldest_key = min(self._performance_cache[kernel_name].keys())
            del self._performance_cache[kernel_name][oldest_key]

        # 更新总执行次数
        self.stats["total_executions"] += 1

    async def enable_kernel(self, name: str) -> bool:
        """启用内核"""
        if name not in self._kernels:
            return False

        registration = self._kernels[name]

        if registration.metadata.status == KernelStatus.DISABLED:
            registration.metadata.status = KernelStatus.REGISTERED
            registration.metadata.last_updated = time.time()
            await self.get_or_create_kernel(name)
            return True

        return False

    async def disable_kernel(self, name: str) -> bool:
        """禁用内核"""
        if name not in self._kernels:
            return False

        registration = self._kernels[name]

        if registration.metadata.status in [
            KernelStatus.ACTIVE,
            KernelStatus.REGISTERED,
        ]:
            registration.metadata.status = KernelStatus.DISABLED
            registration.metadata.last_updated = time.time()

            # 清理实例
            if registration.instance:
                if hasattr(registration.instance, "cleanup"):
                    try:
                        await registration.instance.cleanup()
                    except Exception as e:
                        logger.warning("Error cleaning up kernel %s: %s", name, e)

                registration.instance = None
                registration.is_initialized = False

            return True

        return False

    def get_registry_stats(self) -> Dict[str, Any]:
        """获取注册中心统计信息"""
        stats = self.stats.copy()

        # 添加内核分类统计
        kernel_counts = {"matrix": 0, "transform": 0, "inference": 0, "other": 0}

        total_memory_mb = 0

        for registration in self._kernels.values():
            metadata = registration.metadata

            # 统计内核类型
            if "matrix" in metadata.supported_operations[0] if metadata.supported_operations else False:
                kernel_counts["matrix"] += 1
            elif "transform" in metadata.supported_operations[0] if metadata.supported_operations else False:
                kernel_counts["transform"] += 1
            elif "inference" in metadata.supported_operations[0] if metadata.supported_operations else False:
                kernel_counts["inference"] += 1
            else:
                kernel_counts["other"] += 1

            total_memory_mb += metadata.memory_usage_mb

        stats.update(
            {
                "kernel_type_counts": kernel_counts,
                "total_memory_usage_mb": total_memory_mb,
                "cache_hit_rate": (stats["cache_hits"] / max(1, stats["total_executions"]) * 100),
            }
        )

        return stats

    async def auto_discover_kernels(self, module_paths: List[str]) -> int:
        """自动发现并注册内核"""
        discovered_count = 0

        for module_path in module_paths:
            try:
                # 动态导入模块
                module = importlib.import_module(module_path)

                # 查找内核类
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, StandardizedKernelInterface) and obj != StandardizedKernelInterface:
                        # 自动注册
                        success = self.register_kernel(obj)
                        if success:
                            discovered_count += 1
                            logger.info("Auto-discovered kernel: %s", obj.__name__)

            except Exception as e:
                logger.error("Failed to auto-discover kernels in %s: %s", module_path, e)

        logger.info("Auto-discovered %s kernels", discovered_count)
        return discovered_count

    def _create_default_metadata(self, kernel_class: Type[StandardizedKernelInterface]) -> KernelMetadata:
        """创建默认元数据"""
        doc = kernel_class.__doc__ or f"{kernel_class.__name__} kernel"

        # 尝试从类属性获取操作支持
        supported_ops = []
        if hasattr(kernel_class, "get_supported_operations"):
            try:
                # 创建临时实例获取支持的操作
                temp_instance = kernel_class()
                ops_dict = temp_instance.get_supported_operations()
                for category, operations in ops_dict.items():
                    supported_ops.extend(operations)
            except Exception:
                # 如果失败，使用默认操作
                pass

        return KernelMetadata(
            name=kernel_class.__name__.replace("KernelEngine", "").replace("Kernel", ""),
            version="1.0.0",
            description=doc.split("\n")[0] if doc else f"{kernel_class.__name__} kernel",
            author="Auto-generated",
            supported_operations=supported_ops or ["unknown"],
            gpu_required="gpu" in kernel_class.__name__.lower() or "GPU" in kernel_class.__name__,
        )

    def _update_existing_kernel(self, name: str, kernel_class: Type, metadata: KernelMetadata) -> None:
        """更新现有内核"""
        registration = self._kernels[name]

        # 检查版本是否更新
        if metadata.version != registration.metadata.version:
            logger.info("Updating kernel %s from v%s to v%s", name, registration.metadata.version, metadata.version)

        registration.kernel_class = kernel_class
        registration.metadata = metadata
        registration.is_initialized = False

        # 清理旧实例
        if registration.instance:
            registration.instance = None

    def _update_operation_mappings(self, kernel_name: str, operations: List[str]) -> None:
        """更新操作映射"""
        for operation in operations:
            if operation not in self._operation_mappings:
                self._operation_mappings[operation] = []

            if kernel_name not in self._operation_mappings[operation]:
                self._operation_mappings[operation].append(kernel_name)

    def _remove_operation_mappings(self, kernel_name: str) -> None:
        """移除操作映射"""
        operations_to_remove = []

        for operation, kernels in self._operation_mappings.items():
            if kernel_name in kernels:
                kernels.remove(kernel_name)
                if not kernels:
                    operations_to_remove.append(operation)

        for operation in operations_to_remove:
            del self._operation_mappings[operation]

    def _update_stats(self) -> None:
        """更新统计信息"""
        self.stats["total_kernels"] = len(self._kernels)
        self.stats["active_kernels"] = sum(
            1 for reg in self._kernels.values() if reg.metadata.status == KernelStatus.ACTIVE
        )
        self.stats["error_kernels"] = sum(
            1 for reg in self._kernels.values() if reg.metadata.status == KernelStatus.ERROR
        )

    def _select_kernel_by_data_size(self, candidates: List[str], data_shape: tuple) -> Optional[str]:
        """根据数据大小选择内核"""
        data_size = data_shape[0] if data_shape else 1

        # 根据数据大小偏好选择
        if data_size < 1000:
            # 小数据：选择轻量级内核
            lightweight_kernels = [k for k in candidates if "lightweight" in k.lower() or "simple" in k.lower()]
            if lightweight_kernels:
                return lightweight_kernels[0]

        elif data_size > 100000:
            # 大数据：选择高性能内核
            high_perf_kernels = [k for k in candidates if "high" in k.lower() or "optimized" in k.lower()]
            if high_perf_kernels:
                return high_perf_kernels[0]

        return None

    def _select_kernel_by_performance(self, candidates: List[str]) -> Optional[str]:
        """根据性能统计选择内核"""
        if not candidates:
            return None

        # 按成功率和平均执行时间排序
        best_kernel = None
        best_score = -1

        for kernel_name in candidates:
            registration = self._kernels[kernel_name]
            metadata = registration.metadata

            total_executions = metadata.success_count + metadata.error_count
            if total_executions == 0:
                success_rate = 0
            else:
                success_rate = metadata.success_count / total_executions

            # 计算综合评分：成功率权重70%，速度权重30%
            avg_time = metadata.average_execution_time_ms
            speed_score = max(0, 100 - avg_time / 10)  # 假设10ms为满分

            composite_score = success_rate * 70 + speed_score * 30

            if composite_score > best_score:
                best_score = composite_score
                best_kernel = kernel_name

        return best_kernel

    def _calculate_performance_score(self, metadata: KernelMetadata) -> float:
        """计算性能评分"""
        total_executions = metadata.success_count + metadata.error_count

        if total_executions == 0:
            return 0.0

        # 成功率
        success_rate = metadata.success_count / total_executions

        # 速度评分 (假设理想执行时间为1ms)
        avg_time = metadata.average_execution_time_ms
        speed_score = max(0, 100 - avg_time * 10)

        # 综合评分
        performance_score = success_rate * 0.7 + speed_score * 0.3

        return min(100.0, performance_score * 100)

    async def _initialize_kernel_async(self, name: str) -> None:
        """异步初始化内核"""
        await self.get_or_create_kernel(name)


# 全局内核注册中心实例
_kernel_registry = KernelRegistry()


def get_kernel_registry() -> KernelRegistry:
    """获取全局内核注册中心"""
    return _kernel_registry


def register_standard_kernels():
    """注册标准内核"""
    try:
        # 注册矩阵内核
        from .matrix_kernels import MatrixKernelEngine

        get_kernel_registry().register_kernel(MatrixKernelEngine)

        # 注册变换内核
        from .transform_kernels import TransformKernelEngine

        get_kernel_registry().register_kernel(TransformKernelEngine)

        # 注册推理内核
        from .inference_kernels import InferenceKernelEngine

        get_kernel_registry().register_kernel(InferenceKernelEngine)

        logger.info("Standard kernels registered successfully")

    except ImportError as e:
        logger.warning("Failed to register some standard kernels: %s", e)
    except Exception as e:
        logger.error("Error registering standard kernels: %s", e)
