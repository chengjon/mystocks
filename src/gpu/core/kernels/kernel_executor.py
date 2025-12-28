"""
GPU计算内核执行器
提供统一的内核执行接口，支持批量执行、并行处理和性能监控
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from concurrent.futures import ThreadPoolExecutor

from .standardized_interface import (
    MatrixOperationConfig,
    TransformConfig,
    InferenceConfig,
    KernelExecutionResult,
)
from .kernel_registry import get_kernel_registry, KernelRegistry

logger = logging.getLogger(__name__)


class ExecutionMode(Enum):
    """执行模式"""

    SEQUENTIAL = "sequential"  # 顺序执行
    PARALLEL = "parallel"  # 并行执行
    BATCHED = "batched"  # 批量执行
    PIPELINED = "pipelined"  # 流水线执行


class ExecutionPriority(Enum):
    """执行优先级"""

    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


@dataclass
class ExecutionContext:
    """执行上下文"""

    kernel_name: str
    operation_type: str
    data: Any
    config: Optional[Any] = None
    priority: ExecutionPriority = ExecutionPriority.NORMAL
    timeout_ms: Optional[float] = None
    retry_count: int = 0
    max_retries: int = 3
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionResult:
    """执行结果"""

    success: bool
    kernel_name: str
    operation_type: str
    result_data: Optional[KernelExecutionResult] = None
    execution_time_ms: float = 0.0
    error_message: Optional[str] = None
    context: Optional[ExecutionContext] = None
    performance_metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BatchExecutionConfig:
    """批量执行配置"""

    max_parallel_jobs: int = 4
    enable_load_balancing: bool = True
    enable_fail_fast: bool = False
    timeout_ms: Optional[float] = None
    retry_failed_jobs: bool = True
    collect_performance_metrics: bool = True


class KernelExecutor:
    """GPU计算内核执行器"""

    def __init__(self, kernel_registry: Optional[KernelRegistry] = None):
        self.kernel_registry = kernel_registry or get_kernel_registry()
        self.executor = ThreadPoolExecutor(max_workers=8)

        # 执行统计
        self.stats = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "total_execution_time_ms": 0.0,
            "average_execution_time_ms": 0.0,
            "parallel_executions": 0,
            "batch_executions": 0,
        }

        # 执行队列
        self._execution_queue = asyncio.Queue()
        self._queue_processor_task = None
        self._is_running = False

    async def execute_matrix_operation(
        self,
        kernel_name: str,
        left_data: np.ndarray,
        right_data: Optional[np.ndarray] = None,
        config: Optional[MatrixOperationConfig] = None,
        timeout_ms: Optional[float] = None,
    ) -> ExecutionResult:
        """执行矩阵运算"""
        context = ExecutionContext(
            kernel_name=kernel_name,
            operation_type="matrix",
            data=(left_data, right_data),
            config=config,
            timeout_ms=timeout_ms,
        )

        return await self._execute_context(context)

    async def execute_transform_operation(
        self,
        kernel_name: str,
        data: np.ndarray,
        config: TransformConfig,
        timeout_ms: Optional[float] = None,
    ) -> ExecutionResult:
        """执行数据变换"""
        context = ExecutionContext(
            kernel_name=kernel_name,
            operation_type="transform",
            data=data,
            config=config,
            timeout_ms=timeout_ms,
        )

        return await self._execute_context(context)

    async def execute_inference_operation(
        self,
        kernel_name: str,
        data: np.ndarray,
        config: InferenceConfig,
        timeout_ms: Optional[float] = None,
    ) -> ExecutionResult:
        """执行机器学习推理"""
        context = ExecutionContext(
            kernel_name=kernel_name,
            operation_type="inference",
            data=data,
            config=config,
            timeout_ms=timeout_ms,
        )

        return await self._execute_context(context)

    async def execute_batch(
        self,
        contexts: List[ExecutionContext],
        config: Optional[BatchExecutionConfig] = None,
        mode: ExecutionMode = ExecutionMode.PARALLEL,
    ) -> List[ExecutionResult]:
        """批量执行"""
        if not contexts:
            return []

        batch_config = config or BatchExecutionConfig()
        start_time = time.time()

        try:
            if mode == ExecutionMode.SEQUENTIAL:
                results = await self._execute_sequential(contexts, batch_config)
            elif mode == ExecutionMode.PARALLEL:
                results = await self._execute_parallel(contexts, batch_config)
            elif mode == ExecutionMode.BATCHED:
                results = await self._execute_batched(contexts, batch_config)
            elif mode == ExecutionMode.PIPELINED:
                results = await self._execute_pipelined(contexts, batch_config)
            else:
                raise ValueError(f"Unsupported execution mode: {mode}")

            # 更新统计
            execution_time = (time.time() - start_time) * 1000
            self._update_batch_stats(len(contexts), len([r for r in results if r.success]), execution_time)

            return results

        except Exception as e:
            logger.error("Batch execution failed: %s", e)
            return self._create_error_results(contexts, str(e))

    async def execute_with_fallback(
        self,
        primary_kernel: str,
        fallback_kernels: List[str],
        context: ExecutionContext,
    ) -> ExecutionResult:
        """带回退机制的执行"""
        kernels_to_try = [primary_kernel] + fallback_kernels
        last_error = None

        for kernel_name in kernels_to_try:
            try:
                # 更新上下文中的内核名称
                context.kernel_name = kernel_name

                # 尝试执行
                result = await self._execute_context(context)

                if result.success:
                    if kernel_name != primary_kernel:
                        logger.info("Fallback kernel %s succeeded after primary %s failed", kernel_name, primary_kernel)
                    return result
                else:
                    last_error = result.error_message
                    logger.warning("Kernel %s failed: %s", kernel_name, result.error_message)

            except Exception as e:
                last_error = str(e)
                logger.warning("Kernel %s threw exception: %s", kernel_name, e)

        # 所有内核都失败了
        return ExecutionResult(
            success=False,
            kernel_name=primary_kernel,
            operation_type=context.operation_type,
            error_message=f"All kernels failed. Last error: {last_error}",
            context=context,
        )

    async def execute_with_auto_selection(
        self,
        operation_type: str,
        operation_name: Optional[str] = None,
        data: Optional[Any] = None,
        config: Optional[Any] = None,
        data_shape: Optional[tuple] = None,
    ) -> ExecutionResult:
        """自动选择内核执行"""
        # 选择最佳内核
        best_kernel = self.kernel_registry.get_best_kernel_for_operation(operation_type, operation_name, data_shape)

        if not best_kernel:
            return ExecutionResult(
                success=False,
                kernel_name="auto",
                operation_type=operation_type,
                error_message=f"No kernel found for operation: {operation_type}:{operation_name}",
            )

        # 创建执行上下文
        context = ExecutionContext(
            kernel_name=best_kernel,
            operation_type=operation_type,
            data=data,
            config=config,
        )

        # 执行
        return await self._execute_context(context)

    async def start_queue_processor(self) -> None:
        """启动队列处理器"""
        if self._is_running:
            logger.warning("Queue processor already running")
            return

        self._is_running = True
        self._queue_processor_task = asyncio.create_task(self._process_execution_queue())
        logger.info("Queue processor started")

    async def stop_queue_processor(self) -> None:
        """停止队列处理器"""
        if not self._is_running:
            return

        self._is_running = False

        if self._queue_processor_task:
            self._queue_processor_task.cancel()
            try:
                await self._queue_processor_task
            except asyncio.CancelledError:
                pass

        logger.info("Queue processor stopped")

    def submit_to_queue(self, context: ExecutionContext) -> bool:
        """提交执行任务到队列"""
        if not self._is_running:
            logger.warning("Queue processor not running, cannot submit task")
            return False

        try:
            self._execution_queue.put_nowait(context)
            return True
        except asyncio.QueueFull:
            logger.warning("Execution queue is full, cannot submit task")
            return False

    async def _execute_context(self, context: ExecutionContext) -> ExecutionResult:
        """执行单个上下文"""
        start_time = time.time()

        try:
            # 获取内核实例
            kernel = await self.kernel_registry.get_or_create_kernel(context.kernel_name)

            if kernel is None:
                return ExecutionResult(
                    success=False,
                    kernel_name=context.kernel_name,
                    operation_type=context.operation_type,
                    error_message=f"Failed to get kernel instance: {context.kernel_name}",
                    context=context,
                )

            # 根据操作类型执行
            if context.operation_type == "matrix":
                left_data, right_data = context.data
                result = await self._execute_with_timeout(
                    kernel.execute_matrix_operation(left_data, right_data, context.config),
                    context.timeout_ms,
                )
            elif context.operation_type == "transform":
                result = await self._execute_with_timeout(
                    kernel.execute_transform_operation(context.data, context.config),
                    context.timeout_ms,
                )
            elif context.operation_type == "inference":
                result = await self._execute_with_timeout(
                    kernel.execute_inference_operation(context.data, context.config),
                    context.timeout_ms,
                )
            else:
                raise ValueError(f"Unsupported operation type: {context.operation_type}")

            execution_time = (time.time() - start_time) * 1000

            # 更新内核性能统计
            self.kernel_registry.update_kernel_performance(context.kernel_name, execution_time, result.success)

            # 更新执行器统计
            self._update_single_stats(result.success, execution_time)

            return ExecutionResult(
                success=result.success,
                kernel_name=context.kernel_name,
                operation_type=context.operation_type,
                result_data=result,
                execution_time_ms=execution_time,
                error_message=result.error_message,
                context=context,
                performance_metrics={
                    "memory_used_bytes": result.memory_used_bytes,
                    "gpu_accelerated": result.performance_metrics.get("execution_backend") != "CPU",
                },
            )

        except asyncio.TimeoutError:
            execution_time = (time.time() - start_time) * 1000
            error_msg = f"Execution timeout after {context.timeout_ms}ms"

            self._update_single_stats(False, execution_time)

            return ExecutionResult(
                success=False,
                kernel_name=context.kernel_name,
                operation_type=context.operation_type,
                execution_time_ms=execution_time,
                error_message=error_msg,
                context=context,
            )

        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            error_msg = f"Execution failed: {str(e)}"

            self._update_single_stats(False, execution_time)

            return ExecutionResult(
                success=False,
                kernel_name=context.kernel_name,
                operation_type=context.operation_type,
                execution_time_ms=execution_time,
                error_message=error_msg,
                context=context,
            )

    async def _execute_with_timeout(self, coro, timeout_ms: Optional[float]) -> Any:
        """带超时的执行"""
        if timeout_ms is None:
            return await coro

        timeout_seconds = timeout_ms / 1000.0
        return await asyncio.wait_for(coro, timeout=timeout_seconds)

    async def _execute_sequential(
        self, contexts: List[ExecutionContext], config: BatchExecutionConfig
    ) -> List[ExecutionResult]:
        """顺序执行"""
        results = []

        for context in contexts:
            if config.enable_fail_fast and results and not results[-1].success:
                # 如果启用了快速失败且前一个失败了，跳过剩余的
                break

            result = await self._execute_context(context)
            results.append(result)

            # 重试失败的作业
            if config.retry_failed_jobs and not result.success and context.retry_count < context.max_retries:
                context.retry_count += 1
                logger.info("Retrying failed operation %s:%s", context.kernel_name, context.operation_type)

                retry_result = await self._execute_context(context)
                if retry_result.success:
                    results[-1] = retry_result

        return results

    async def _execute_parallel(
        self, contexts: List[ExecutionContext], config: BatchExecutionConfig
    ) -> List[ExecutionResult]:
        """并行执行"""
        self.stats["parallel_executions"] += 1

        # 限制并行作业数量
        semaphore = asyncio.Semaphore(config.max_parallel_jobs)

        async def execute_with_semaphore(context: ExecutionContext) -> ExecutionResult:
            async with semaphore:
                return await self._execute_context(context)

        # 创建任务
        tasks = [execute_with_semaphore(context) for context in contexts]

        # 等待所有任务完成
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 处理异常结果
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(
                    ExecutionResult(
                        success=False,
                        kernel_name=contexts[i].kernel_name,
                        operation_type=contexts[i].operation_type,
                        error_message=f"Task exception: {str(result)}",
                        context=contexts[i],
                    )
                )
            else:
                processed_results.append(result)

        return processed_results

    async def _execute_batched(
        self, contexts: List[ExecutionContext], config: BatchExecutionConfig
    ) -> List[ExecutionResult]:
        """批量执行（按内核分组）"""
        self.stats["batch_executions"] += 1

        # 按内核分组
        kernel_groups = {}
        for context in contexts:
            kernel_name = context.kernel_name
            if kernel_name not in kernel_groups:
                kernel_groups[kernel_name] = []
            kernel_groups[kernel_name].append(context)

        results = []

        # 按内核执行
        for kernel_name, group_contexts in kernel_groups.items():
            try:
                # 获取内核实例
                kernel = await self.kernel_registry.get_or_create_kernel(kernel_name)

                if kernel is None:
                    # 内核不可用，创建错误结果
                    for context in group_contexts:
                        results.append(
                            ExecutionResult(
                                success=False,
                                kernel_name=kernel_name,
                                operation_type=context.operation_type,
                                error_message=f"Kernel not available: {kernel_name}",
                                context=context,
                            )
                        )
                    continue

                # 准备批量数据
                batch_data = self._prepare_batch_data(group_contexts)

                # 执行批量操作
                batch_results = await kernel.batch_execute(batch_data)

                # 转换结果
                for i, context in enumerate(group_contexts):
                    if i < len(batch_results):
                        kernel_result = batch_results[i]
                        results.append(
                            ExecutionResult(
                                success=kernel_result.success,
                                kernel_name=kernel_name,
                                operation_type=context.operation_type,
                                result_data=kernel_result,
                                execution_time_ms=kernel_result.execution_time_ms,
                                error_message=kernel_result.error_message,
                                context=context,
                            )
                        )
                    else:
                        results.append(
                            ExecutionResult(
                                success=False,
                                kernel_name=kernel_name,
                                operation_type=context.operation_type,
                                error_message="No result returned from batch execution",
                                context=context,
                            )
                        )

            except Exception as e:
                # 批量执行失败，为每个上下文创建错误结果
                for context in group_contexts:
                    results.append(
                        ExecutionResult(
                            success=False,
                            kernel_name=kernel_name,
                            operation_type=context.operation_type,
                            error_message=f"Batch execution failed: {str(e)}",
                            context=context,
                        )
                    )

        return results

    async def _execute_pipelined(
        self, contexts: List[ExecutionContext], config: BatchExecutionConfig
    ) -> List[ExecutionResult]:
        """流水线执行"""
        # 流水线执行是高级功能，这里简化实现为并行执行
        logger.info("Pipelined execution not fully implemented, falling back to parallel")
        return await self._execute_parallel(contexts, config)

    def _prepare_batch_data(self, contexts: List[ExecutionContext]) -> List[Tuple]:
        """准备批量数据"""
        batch_data = []

        for context in contexts:
            if context.operation_type == "matrix":
                batch_data.append((context.operation_type, *context.data, context.config))
            else:
                batch_data.append((context.operation_type, context.data, context.config))

        return batch_data

    async def _process_execution_queue(self) -> None:
        """处理执行队列"""
        logger.info("Started processing execution queue")

        while self._is_running:
            try:
                # 获取任务（带超时）
                try:
                    context = await asyncio.wait_for(self._execution_queue.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    continue

                # 执行任务
                try:
                    await self._execute_context(context)
                except Exception as e:
                    logger.error("Error executing queued task: %s", e)

            except Exception as e:
                logger.error("Error in queue processor: %s", e)

        logger.info("Stopped processing execution queue")

    def _update_single_stats(self, success: bool, execution_time: float) -> None:
        """更新单个执行统计"""
        self.stats["total_executions"] += 1
        self.stats["total_execution_time_ms"] += execution_time

        if success:
            self.stats["successful_executions"] += 1
        else:
            self.stats["failed_executions"] += 1

        # 更新平均执行时间
        if self.stats["total_executions"] > 0:
            self.stats["average_execution_time_ms"] = (
                self.stats["total_execution_time_ms"] / self.stats["total_executions"]
            )

    def _update_batch_stats(self, total_contexts: int, successful_results: int, execution_time: float) -> None:
        """更新批量执行统计"""
        self.stats["total_executions"] += total_contexts
        self.stats["total_execution_time_ms"] += execution_time
        self.stats["successful_executions"] += successful_results
        self.stats["failed_executions"] += total_contexts - successful_results

        # 更新平均执行时间
        if self.stats["total_executions"] > 0:
            self.stats["average_execution_time_ms"] = (
                self.stats["total_execution_time_ms"] / self.stats["total_executions"]
            )

    def _create_error_results(self, contexts: List[ExecutionContext], error_message: str) -> List[ExecutionResult]:
        """创建错误结果列表"""
        return [
            ExecutionResult(
                success=False,
                kernel_name=context.kernel_name,
                operation_type=context.operation_type,
                error_message=error_message,
                context=context,
            )
            for context in contexts
        ]

    def get_execution_stats(self) -> Dict[str, Any]:
        """获取执行统计"""
        stats = self.stats.copy()

        # 计算成功率
        if stats["total_executions"] > 0:
            stats["success_rate"] = stats["successful_executions"] / stats["total_executions"]
            stats["failure_rate"] = stats["failed_executions"] / stats["total_executions"]
        else:
            stats["success_rate"] = 0.0
            stats["failure_rate"] = 0.0

        # 添加队列统计
        stats["queue_size"] = self._execution_queue.qsize() if self._execution_queue else 0
        stats["queue_processor_running"] = self._is_running

        return stats

    def reset_stats(self) -> None:
        """重置统计"""
        self.stats = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "total_execution_time_ms": 0.0,
            "average_execution_time_ms": 0.0,
            "parallel_executions": 0,
            "batch_executions": 0,
        }

    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.start_queue_processor()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.stop_queue_processor()
        self.executor.shutdown(wait=True)


# 全局内核执行器实例
_kernel_executor = None


def get_kernel_executor() -> KernelExecutor:
    """获取全局内核执行器"""
    global _kernel_executor
    if _kernel_executor is None:
        _kernel_executor = KernelExecutor()
    return _kernel_executor
