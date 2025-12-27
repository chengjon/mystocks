"""
策略GPU上下文
为每个量化策略提供独立的GPU执行环境
"""

import asyncio
import logging
import time
from typing import Dict
import numpy as np

from .interfaces import (
    IStrategyContext,
    IGPUResourceProvider,
    StrategyPriority,
    PerformanceProfile,
    IMemoryPool,
)
from .memory_pool import MemoryPool


logger = logging.getLogger(__name__)


class StrategyGPUContext(IStrategyContext):
    """策略GPU上下文实现"""

    def __init__(
        self,
        strategy_id: str,
        device_id: int,
        priority: StrategyPriority,
        memory_pool: MemoryPool,
        performance_profile: PerformanceProfile,
        resource_manager: IGPUResourceProvider,
    ):
        self.strategy_id = strategy_id
        self.device_id = device_id
        self.priority = priority
        self.memory_pool = memory_pool
        self.performance_profile = performance_profile
        self.resource_manager = resource_manager

        # 执行状态
        self.is_active = True
        self.is_preempted = False
        self.allocated_memory = 0

        # 性能指标
        self.execution_count = 0
        self.total_execution_time = 0.0
        self.peak_memory_usage = 0
        self.error_count = 0

        # 计算流管理
        self.compute_streams = {}
        self.current_stream = None

        # 预编译核函数缓存
        self.compiled_kernels = {}

        # 时间戳
        self.created_time = time.time()
        self.last_activity_time = time.time()

        logger.info(f"StrategyGPUContext created for strategy {strategy_id} on device {device_id}")

    def get_strategy_id(self) -> str:
        """获取策略ID"""
        return self.strategy_id

    def get_device_id(self) -> int:
        """获取分配的GPU设备ID"""
        return self.device_id

    def get_memory_pool(self) -> IMemoryPool:
        """获取策略内存池"""
        return self.memory_pool

    async def execute_compute(self, data: np.ndarray, kernel_name: str) -> np.ndarray:
        """执行GPU计算"""
        if not self.is_active or self.is_preempted:
            raise RuntimeError(f"Strategy context {self.strategy_id} is not active or is preempted")

        start_time = time.time()

        try:
            # 检查性能阈值
            if not await self._check_performance_thresholds():
                logger.warning(f"Performance thresholds exceeded for strategy {self.strategy_id}")

            # 执行计算
            result = await self._execute_kernel(data, kernel_name)

            # 更新性能指标
            execution_time = time.time() - start_time
            self._update_performance_metrics(execution_time, data.nbytes)

            self.last_activity_time = time.time()
            self.execution_count += 1

            logger.debug(f"Executed kernel {kernel_name} for strategy {self.strategy_id} " f"in {execution_time:.3f}s")

            return result

        except Exception as e:
            self.error_count += 1
            logger.error(f"Error executing kernel {kernel_name} for strategy {self.strategy_id}: {e}")
            raise

    async def _execute_kernel(self, data: np.ndarray, kernel_name: str) -> np.ndarray:
        """执行核函数"""
        # 模拟GPU计算 - 实际实现需要调用具体的GPU计算库
        # 这里提供一个框架，具体的核函数实现在其他地方

        # 分配GPU内存
        data_size = data.nbytes
        gpu_ptr = self.memory_pool.allocate(data_size, self.strategy_id)
        if gpu_ptr is None:
            raise RuntimeError(f"Failed to allocate GPU memory for kernel {kernel_name}")

        try:
            # 模拟数据传输到GPU
            await asyncio.sleep(0.001)  # 模拟传输延迟

            # 模拟GPU计算
            compute_time = self._estimate_compute_time(data, kernel_name)
            await asyncio.sleep(compute_time)

            # 模拟结果处理
            result = self._process_kernel_result(data, kernel_name)

            return result

        finally:
            # 释放GPU内存
            self.memory_pool.deallocate(gpu_ptr, self.strategy_id)

    def _estimate_compute_time(self, data: np.ndarray, kernel_name: str) -> float:
        """估算计算时间"""
        # 基于数据大小和核函数类型估算
        base_time = 0.001  # 基础延迟

        if kernel_name == "matrix_multiply":
            size_factor = (data.size / 10000) ** 0.33  # 矩阵乘法复杂度 O(n^3)
        elif kernel_name == "feature_transform":
            size_factor = data.size / 10000  # 特征变换复杂度 O(n)
        elif kernel_name == "ml_inference":
            size_factor = (data.size / 10000) ** 0.5  # 机器学习推理复杂度
        else:
            size_factor = data.size / 10000  # 默认线性复杂度

        # 考虑设备性能
        device_factor = 1.0  # 可以根据设备性能调整

        return base_time * (1 + size_factor) * device_factor

    def _process_kernel_result(self, data: np.ndarray, kernel_name: str) -> np.ndarray:
        """处理核函数结果"""
        # 模拟不同核函数的结果处理
        if kernel_name == "matrix_multiply":
            # 矩阵乘法结果
            return np.dot(data, data.T) if len(data.shape) == 2 else data
        elif kernel_name == "feature_transform":
            # 特征变换结果
            return np.log1p(np.abs(data))
        elif kernel_name == "ml_inference":
            # 机器学习推理结果
            return np.random.random(data.shape[0])  # 模拟预测结果
        else:
            # 默认处理
            return data.copy()

    async def _check_performance_thresholds(self) -> bool:
        """检查性能阈值"""
        # 检查内存使用率
        memory_stats = self.memory_pool.get_usage_statistics()
        current_usage_ratio = memory_stats["usage"]["utilization"]

        if current_usage_ratio > self.performance_profile.max_memory_usage:
            logger.warning(
                f"Memory usage {current_usage_ratio:.2%} exceeds threshold "
                f"{self.performance_profile.max_memory_usage:.2%}"
            )
            return False

        # 检查错误率
        if self.execution_count > 100:  # 至少执行100次后才检查错误率
            error_rate = self.error_count / self.execution_count
            if error_rate > 0.05:  # 5%错误率阈值
                logger.warning(f"Error rate {error_rate:.2%} exceeds acceptable threshold")
                return False

        return True

    def _update_performance_metrics(self, execution_time: float, data_size: int):
        """更新性能指标"""
        self.total_execution_time += execution_time

        # 更新内存使用峰值
        memory_stats = self.memory_pool.get_usage_statistics()
        current_memory_usage = memory_stats["usage"]["total_allocated_bytes"]
        self.peak_memory_usage = max(self.peak_memory_usage, current_memory_usage)

        # 检查延迟目标
        if execution_time > self.performance_profile.latency_target_ms / 1000:
            logger.debug(
                f"Execution time {execution_time:.3f}s exceeds target "
                f"{self.performance_profile.latency_target_ms}ms"
            )

    def get_performance_metrics(self) -> Dict[str, float]:
        """获取性能指标"""
        if self.execution_count == 0:
            return {
                "strategy_id": self.strategy_id,
                "device_id": self.device_id,
                "execution_count": 0,
                "average_execution_time": 0.0,
                "total_execution_time": 0.0,
                "peak_memory_usage": 0,
                "error_count": 0,
                "error_rate": 0.0,
                "uptime": time.time() - self.created_time,
                "is_active": self.is_active,
                "is_preempted": self.is_preempted,
            }

        return {
            "strategy_id": self.strategy_id,
            "device_id": self.device_id,
            "execution_count": self.execution_count,
            "average_execution_time": self.total_execution_time / self.execution_count,
            "total_execution_time": self.total_execution_time,
            "peak_memory_usage": self.peak_memory_usage,
            "error_count": self.error_count,
            "error_rate": self.error_count / self.execution_count,
            "uptime": time.time() - self.created_time,
            "is_active": self.is_active,
            "is_preempted": self.is_preempted,
        }

    async def preempt_resources(self) -> bool:
        """被抢占资源时的处理"""
        logger.info(f"Strategy {self.strategy_id} being preempted")

        # 标记为被抢占
        self.is_preempted = True

        try:
            # 保存当前状态
            await self._save_strategy_state()

            # 释放计算资源
            await self._release_compute_resources()

            # 清理内存（保留关键数据）
            await self._cleanup_non_critical_memory()

            logger.info(f"Strategy {self.strategy_id} successfully preempted")
            return True

        except Exception as e:
            logger.error(f"Error during preemption of strategy {self.strategy_id}: {e}")
            return False

    async def _save_strategy_state(self):
        """保存策略状态"""
        # 保存策略执行状态，以便后续恢复
        # 这里需要根据具体策略实现状态保存逻辑
        await asyncio.sleep(0.001)  # 模拟状态保存时间

    async def _release_compute_resources(self):
        """释放计算资源"""
        # 释放计算流
        self.compute_streams.clear()
        self.current_stream = None

        # 清理编译的核函数缓存
        self.compiled_kernels.clear()

        await asyncio.sleep(0.001)  # 模拟资源释放时间

    async def _cleanup_non_critical_memory(self):
        """清理非关键内存"""
        # 释放非关键的内存分配，保留策略状态所需的最小内存
        memory_stats = self.memory_pool.get_usage_statistics()
        current_usage = memory_stats["usage"]["total_allocated_bytes"]

        # 保留策略状态所需的最小内存（例如，保留10%的当前使用量）
        int(current_usage * 0.1)

        # 这里需要实现具体的内存清理逻辑
        # 暂时只记录日志
        logger.debug(f"Cleaning up non-critical memory for strategy {self.strategy_id}")

    async def restore_from_preemption(self) -> bool:
        """从抢占中恢复"""
        if not self.is_preempted:
            return True

        logger.info(f"Restoring strategy {self.strategy_id} from preemption")

        try:
            # 恢复计算资源
            await self._restore_compute_resources()

            # 恢复内存状态
            await self._restore_memory_state()

            # 恢复策略状态
            await self._restore_strategy_state()

            # 标记为活跃
            self.is_preempted = False
            self.is_active = True
            self.last_activity_time = time.time()

            logger.info(f"Strategy {self.strategy_id} successfully restored")
            return True

        except Exception as e:
            logger.error(f"Error restoring strategy {self.strategy_id}: {e}")
            return False

    async def _restore_compute_resources(self):
        """恢复计算资源"""
        # 重新初始化计算流和核函数缓存
        self.compute_streams = {}
        self.current_stream = None
        self.compiled_kernels = {}

        await asyncio.sleep(0.001)  # 模拟资源初始化时间

    async def _restore_memory_state(self):
        """恢复内存状态"""
        # 重新分配之前占用的内存
        # 这里需要根据之前保存的状态恢复内存分配
        await asyncio.sleep(0.001)  # 模拟内存分配时间

    async def _restore_strategy_state(self):
        """恢复策略状态"""
        # 恢复策略的执行状态
        await asyncio.sleep(0.001)  # 模拟状态恢复时间

    def shutdown(self):
        """关闭策略上下文"""
        logger.info(f"Shutting down StrategyGPUContext for strategy {self.strategy_id}")

        # 标记为非活跃
        self.is_active = False

        # 清理内存池
        try:
            self.memory_pool.cleanup()
        except Exception as e:
            logger.error(f"Error cleaning up memory pool for strategy {self.strategy_id}: {e}")

        # 清理其他资源
        self.compute_streams.clear()
        self.compiled_kernels.clear()

        logger.info(f"StrategyGPUContext for strategy {self.strategy_id} shutdown complete")
