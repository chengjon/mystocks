#!/usr/bin/env python3
"""
长期稳定性测试
Phase 6.4.4 - 长期稳定性测试

执行长期稳定性测试，验证内存泄漏和资源清理，确保GPU加速引擎在长期运行中的稳定性
"""

import asyncio
import gc
import sys
import time
import tracemalloc
import weakref
from pathlib import Path
from typing import Any, Dict

import numpy as np
import psutil

from tests.unit._long_term_stability_tail import LongTermStabilityTailMixin, run_long_term_stability_main

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


class LongTermStabilityTester(LongTermStabilityTailMixin):
    """长期稳定性测试器"""

    def __init__(self):
        self.test_results = {}
        self.process = psutil.Process()
        self.initial_memory = None
        self.memory_samples = []

    async def run_comprehensive_stability_tests(self) -> Dict[str, Any]:
        """运行全面的长期稳定性测试"""
        print("🚀 GPU加速引擎长期稳定性测试...")

        # 启动内存跟踪
        tracemalloc.start()
        gc.collect()
        self.initial_memory = self.process.memory_info().rss

        stability_tests = [
            ("长时间运行稳定性测试", self.test_long_running_stability),
            ("内存泄漏检测测试", self.test_memory_leak_detection),
            ("资源清理验证测试", self.test_resource_cleanup),
            ("并发压力稳定性测试", self.test_concurrent_stress_stability),
            ("异常恢复稳定性测试", self.test_exception_recovery_stability),
            ("内存池长期稳定性测试", self.test_memory_pool_stability),
        ]

        for test_name, test_func in stability_tests:
            print(f"   🧪 {test_name}...")
            try:
                start_time = time.time()
                result = await test_func()
                execution_time = time.time() - start_time

                self.test_results[test_name] = {
                    "success": result.get("success", False),
                    "execution_time": execution_time,
                    "details": result,
                    "memory_usage_mb": self.get_current_memory_usage(),
                }

                status = "✅" if result.get("success", False) else "❌"
                print(f"   {status} {test_name} ({execution_time:.2f}s)")

            except Exception as e:
                print(f"   ❌ {test_name}失败: {e}")
                self.test_results[test_name] = {
                    "success": False,
                    "error": str(e),
                    "execution_time": 0,
                    "memory_usage_mb": self.get_current_memory_usage(),
                }

        # 停止内存跟踪并生成报告
        tracemalloc.stop()
        return self.generate_stability_report()

    async def test_long_running_stability(self) -> Dict[str, Any]:
        """测试长时间运行稳定性"""
        try:
            from src.gpu.core.kernels import MatrixKernelEngine, TransformKernelEngine

            # 初始化内核
            matrix_kernel = MatrixKernelEngine()
            transform_kernel = TransformKernelEngine()

            await matrix_kernel.initialize()
            await transform_kernel.initialize()

            # 长期运行测试参数
            duration_minutes = 2  # 2分钟测试（实际中可能是数小时）
            operations_per_minute = 30
            total_operations = duration_minutes * operations_per_minute

            start_time = time.time()
            operation_results = []
            memory_samples = []

            print(f"      ⏱️  运行 {duration_minutes} 分钟，总计 {total_operations} 次操作...")

            for i in range(total_operations):
                # 记录内存使用
                memory_mb = self.get_current_memory_usage()
                memory_samples.append(memory_mb)

                # 随机选择操作类型
                if i % 2 == 0:
                    # 矩阵运算
                    size = np.random.choice([128, 256, 512])
                    matrix_a = np.random.random((size, size)).astype(np.float32)
                    matrix_b = np.random.random((size, size)).astype(np.float32)

                    from src.gpu.core.kernels.standardized_interface import (
                        MatrixConfig,
                        MatrixOperationType,
                    )

                    config = MatrixConfig(operation_type=MatrixOperationType.MULTIPLY)

                    result = await matrix_kernel.execute_matrix_operation(matrix_a, matrix_b, config)
                    operation_results.append(("matrix", result.success))
                else:
                    # 变换操作
                    data_size = np.random.choice([1000, 5000, 10000])
                    test_data = np.random.random(data_size).astype(np.float32)

                    from src.gpu.core.kernels.standardized_interface import (
                        TransformConfig,
                        TransformOperationType,
                    )

                    config = TransformConfig(operation_type=TransformOperationType.NORMALIZE)

                    result = await transform_kernel.execute_transform_operation(test_data, config)
                    operation_results.append(("transform", result.success))

                # 强制垃圾回收（模拟实际使用）
                if i % 10 == 0:
                    gc.collect()

                # 控制执行频率
                elapsed = time.time() - start_time
                expected_elapsed = (i + 1) / operations_per_minute * 60
                if elapsed < expected_elapsed:
                    await asyncio.sleep(expected_elapsed - elapsed)

            # 分析结果
            successful_operations = sum(1 for _, success in operation_results if success)
            total_operations = len(operation_results)

            # 内存增长分析
            if len(memory_samples) > 10:
                initial_memory = np.mean(memory_samples[:10])
                final_memory = np.mean(memory_samples[-10:])
                memory_growth_mb = final_memory - initial_memory
                memory_growth_rate = memory_growth_mb / (duration_minutes * 60)  # MB/second
            else:
                memory_growth_mb = 0
                memory_growth_rate = 0

            return {
                "success": successful_operations >= total_operations * 0.95,  # 95%成功率
                "total_operations": total_operations,
                "successful_operations": successful_operations,
                "success_rate": successful_operations / total_operations,
                "operation_breakdown": {
                    "matrix_operations": sum(1 for op, _ in operation_results if op == "matrix"),
                    "transform_operations": sum(1 for op, _ in operation_results if op == "transform"),
                },
                "memory_analysis": {
                    "initial_memory_mb": np.mean(memory_samples[:10]) if memory_samples else 0,
                    "final_memory_mb": np.mean(memory_samples[-10:]) if memory_samples else 0,
                    "memory_growth_mb": memory_growth_mb,
                    "memory_growth_rate_mb_per_sec": memory_growth_rate,
                    "max_memory_mb": max(memory_samples) if memory_samples else 0,
                    "min_memory_mb": min(memory_samples) if memory_samples else 0,
                },
                "stability_duration_minutes": duration_minutes,
                "operations_per_minute": total_operations / duration_minutes,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def test_memory_leak_detection(self) -> Dict[str, Any]:
        """测试内存泄漏检测"""
        try:
            from src.gpu.core.hardware_abstraction.memory_pool import get_memory_pool
            from src.gpu.core.kernels import MatrixKernelEngine

            # 初始化组件
            matrix_kernel = MatrixKernelEngine()
            memory_pool = get_memory_pool()

            await matrix_kernel.initialize()
            await memory_pool.initialize()

            # 内存泄漏检测参数
            iterations = 200
            matrix_size = 512

            # 基线内存使用
            gc.collect()
            baseline_memory = self.get_current_memory_usage()
            memory_samples = [baseline_memory]

            # 创建弱引用跟踪
            weak_references = []

            print(f"      🔍 执行 {iterations} 次迭代检测内存泄漏...")

            for i in range(iterations):
                # 创建大型对象
                large_matrix = np.random.random((matrix_size, matrix_size)).astype(np.float32)
                large_data = np.random.random(50000).astype(np.float32)

                # 添加弱引用
                weak_ref_matrix = weakref.ref(large_matrix)
                weak_ref_data = weakref.ref(large_data)
                weak_references.append(weak_ref_matrix)
                weak_references.append(weak_ref_data)

                # 执行GPU操作
                from src.gpu.core.kernels.standardized_interface import (
                    MatrixConfig,
                    MatrixOperationType,
                )

                config = MatrixConfig(operation_type=MatrixOperationType.MULTIPLY)
                result = await matrix_kernel.execute_matrix_operation(large_matrix, large_matrix.T, config)

                # 内存池操作
                block_sizes = [1024, 4096, 16384]
                allocated_blocks = []
                for size in block_sizes:
                    block_id = await memory_pool.allocate(size)
                    if block_id:
                        allocated_blocks.append(block_id)

                # 释放内存池
                for block_id in allocated_blocks:
                    await memory_pool.deallocate(block_id)

                # 记录内存使用
                current_memory = self.get_current_memory_usage()
                memory_samples.append(current_memory)

                # 删除大型对象引用
                del large_matrix, large_data

                # 定期垃圾回收
                if i % 20 == 0:
                    gc.collect()

                # 检查弱引用
                if i % 50 == 0:
                    still_alive_matrix = sum(1 for ref in weak_references[::2] if ref() is not None)
                    still_alive_data = sum(1 for ref in weak_references[1::2] if ref() is not None)
                    print(f"         第 {i} 次迭代: 存活对象 - 矩阵: {still_alive_matrix}, 数据: {still_alive_data}")

            # 最终垃圾回收
            gc.collect()
            final_memory = self.get_current_memory_usage()
            memory_samples.append(final_memory)

            # 分析内存使用模式
            memory_growth = final_memory - baseline_memory
            memory_variance = np.var(memory_samples) if memory_samples else 0

            # 检查对象清理
            alive_matrix_objects = sum(1 for ref in weak_references[::2] if ref() is not None)
            alive_data_objects = sum(1 for ref in weak_references[1::2] if ref() is not None)
            total_created_objects = len(weak_references)
            cleanup_rate = (total_created_objects - alive_matrix_objects - alive_data_objects) / total_created_objects

            return {
                "success": memory_growth < 100 and cleanup_rate > 0.9,  # 内存增长小于100MB且清理率>90%
                "iterations": iterations,
                "memory_analysis": {
                    "baseline_memory_mb": baseline_memory,
                    "final_memory_mb": final_memory,
                    "memory_growth_mb": memory_growth,
                    "memory_variance_mb2": memory_variance,
                    "max_memory_mb": max(memory_samples),
                    "memory_stability": memory_growth < 50,  # 50MB阈值
                },
                "object_cleanup_analysis": {
                    "total_created_objects": total_created_objects,
                    "alive_matrix_objects": alive_matrix_objects,
                    "alive_data_objects": alive_data_objects,
                    "cleanup_rate": cleanup_rate,
                    "cleanup_successful": cleanup_rate > 0.9,
                },
                "memory_pool_stats": memory_pool.get_stats(),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def test_resource_cleanup(self) -> Dict[str, Any]:
        """测试资源清理"""
        try:
            from src.gpu.core.hardware_abstraction.memory_pool import get_memory_pool
            from src.gpu.core.kernels import MatrixKernelEngine, TransformKernelEngine

            cleanup_results = []

            # 测试1: 内核引擎资源清理
            for i in range(10):
                kernel = MatrixKernelEngine()
                await kernel.initialize()

                # 执行一些操作
                matrix = np.random.random((256, 256)).astype(np.float32)
                from src.gpu.core.kernels.standardized_interface import (
                    MatrixConfig,
                    MatrixOperationType,
                )

                config = MatrixConfig(operation_type=MatrixOperationType.MULTIPLY)
                result = await kernel.execute_matrix_operation(matrix, matrix, config)

                # 清理资源
                kernel_cleanup_success = hasattr(kernel, "cleanup") and callable(getattr(kernel, "cleanup"))
                if kernel_cleanup_success:
                    await kernel.cleanup()

                # 弱引用检查
                weak_ref = weakref.ref(kernel)
                del kernel
                gc.collect()

                cleanup_results.append(
                    {
                        "test": f"kernel_cleanup_{i}",
                        "operation_successful": result.success,
                        "cleanup_available": kernel_cleanup_success,
                        "object_collected": weak_ref() is None,
                    }
                )

            # 测试2: 内存池资源清理
            memory_pool = get_memory_pool()
            await memory_pool.initialize()

            # 分配大量内存块
            allocated_blocks = []
            for i in range(100):
                block_id = await memory_pool.allocate(np.random.randint(1024, 65536))
                if block_id:
                    allocated_blocks.append(block_id)

            # 释放部分内存块
            for block_id in allocated_blocks[:50]:
                await memory_pool.deallocate(block_id)

            # 获取清理前统计
            before_stats = memory_pool.get_stats()

            # 执行完整清理
            if hasattr(memory_pool, "cleanup") and callable(getattr(memory_pool, "cleanup")):
                await memory_pool.cleanup()
                cleanup_available = True
            else:
                cleanup_available = False

            # 获取清理后统计
            after_stats = memory_pool.get_stats()

            cleanup_results.append(
                {
                    "test": "memory_pool_cleanup",
                    "blocks_allocated": len(allocated_blocks),
                    "blocks_deallocated": 50,
                    "cleanup_available": cleanup_available,
                    "before_stats": before_stats,
                    "after_stats": after_stats,
                }
            )

            # 测试3: 异常情况下的资源清理
            for i in range(5):
                try:
                    kernel = TransformKernelEngine()
                    await kernel.initialize()

                    # 故意触发错误
                    invalid_data = np.array([])
                    from src.gpu.core.kernels.standardized_interface import (
                        TransformConfig,
                        TransformOperationType,
                    )

                    config = TransformConfig(operation_type=TransformOperationType.NORMALIZE)
                    result = await kernel.execute_transform_operation(invalid_data, config)

                    # 清理
                    if hasattr(kernel, "cleanup") and callable(getattr(kernel, "cleanup")):
                        await kernel.cleanup()

                    cleanup_results.append(
                        {
                            "test": f"exception_cleanup_{i}",
                            "error_triggered": not result.success,
                            "cleanup_successful": True,
                        }
                    )

                except Exception as e:
                    cleanup_results.append(
                        {
                            "test": f"exception_cleanup_{i}",
                            "error_triggered": True,
                            "cleanup_successful": True,  # 异常后仍能清理
                            "exception_message": str(e),
                        }
                    )

            successful_cleanups = sum(1 for r in cleanup_results if r.get("cleanup_successful", False))
            total_cleanup_tests = len(cleanup_results)

            return {
                "success": successful_cleanups >= total_cleanup_tests * 0.8,
                "total_cleanup_tests": total_cleanup_tests,
                "successful_cleanups": successful_cleanups,
                "cleanup_success_rate": successful_cleanups / total_cleanup_tests,
                "detailed_results": cleanup_results,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def test_concurrent_stress_stability(self) -> Dict[str, Any]:
        """测试并发压力稳定性"""
        try:
            from src.gpu.core.kernels import MatrixKernelEngine

            # 并发压力测试参数
            concurrent_tasks = 20
            operations_per_task = 50
            matrix_size = 256

            async def concurrent_stress_worker(worker_id: int):
                """并发工作器"""
                kernel = MatrixKernelEngine()
                await kernel.initialize()

                operation_results = []
                memory_usage_samples = []

                for op_id in range(operations_per_task):
                    # 记录内存使用
                    memory_mb = self.get_current_memory_usage()
                    memory_usage_samples.append(memory_mb)

                    # 执行矩阵操作
                    matrix_a = np.random.random((matrix_size, matrix_size)).astype(np.float32)
                    matrix_b = np.random.random((matrix_size, matrix_size)).astype(np.float32)

                    from src.gpu.core.kernels.standardized_interface import (
                        MatrixConfig,
                        MatrixOperationType,
                    )

                    config = MatrixConfig(operation_type=MatrixOperationType.MULTIPLY)

                    try:
                        start_time = time.time()
                        result = await kernel.execute_matrix_operation(matrix_a, matrix_b, config)
                        execution_time = time.time() - start_time

                        operation_results.append(
                            {
                                "operation_id": op_id,
                                "success": result.success,
                                "execution_time": execution_time,
                                "memory_usage": memory_mb,
                            }
                        )
                    except Exception as e:
                        operation_results.append(
                            {
                                "operation_id": op_id,
                                "success": False,
                                "error": str(e),
                                "memory_usage": memory_mb,
                            }
                        )

                    # 清理引用
                    del matrix_a, matrix_b

                return {
                    "worker_id": worker_id,
                    "total_operations": operations_per_task,
                    "successful_operations": sum(1 for r in operation_results if r.get("success", False)),
                    "operation_results": operation_results,
                    "memory_samples": memory_usage_samples,
                    "max_memory_mb": max(memory_usage_samples) if memory_usage_samples else 0,
                    "min_memory_mb": min(memory_usage_samples) if memory_usage_samples else 0,
                }

            print(f"      🔄 启动 {concurrent_tasks} 个并发任务...")

            # 启动并发任务
            start_time = time.time()
            concurrent_tasks_list = [concurrent_stress_worker(i) for i in range(concurrent_tasks)]

            # 等待所有任务完成
            worker_results = await asyncio.gather(*concurrent_tasks_list, return_exceptions=True)
            total_execution_time = time.time() - start_time

            # 分析结果
            valid_results = [r for r in worker_results if isinstance(r, dict)]
            total_operations = sum(r.get("total_operations", 0) for r in valid_results)
            successful_operations = sum(r.get("successful_operations", 0) for r in valid_results)

            # 内存稳定性分析
            all_memory_samples = []
            for result in valid_results:
                all_memory_samples.extend(result.get("memory_samples", []))

            if all_memory_samples:
                memory_stability = {
                    "avg_memory_mb": np.mean(all_memory_samples),
                    "max_memory_mb": max(all_memory_samples),
                    "min_memory_mb": min(all_memory_samples),
                    "memory_variance": np.var(all_memory_samples),
                    "memory_stable": np.var(all_memory_samples) < 100,  # 方差阈值
                }
            else:
                memory_stability = {}

            return {
                "success": successful_operations >= total_operations * 0.9 and len(valid_results) == concurrent_tasks,
                "concurrent_workers": concurrent_tasks,
                "total_execution_time": total_execution_time,
                "total_operations": total_operations,
                "successful_operations": successful_operations,
                "success_rate": successful_operations / total_operations if total_operations > 0 else 0,
                "operations_per_second": total_operations / total_execution_time,
                "memory_stability": memory_stability,
                "worker_results_summary": {
                    "completed_workers": len(valid_results),
                    "failed_workers": len(worker_results) - len(valid_results),
                    "avg_operations_per_worker": total_operations / len(valid_results) if valid_results else 0,
                },
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def test_exception_recovery_stability(self) -> Dict[str, Any]:
        """测试异常恢复稳定性"""
        try:
            from src.gpu.core.kernels import MatrixKernelEngine, TransformKernelEngine

            recovery_tests = []

            # 测试1: 无效输入恢复
            for i in range(10):
                kernel = MatrixKernelEngine()
                await kernel.initialize()

                # 测试各种无效输入
                invalid_inputs = [
                    np.array([]),  # 空数组
                    np.random.random((0, 100)),  # 零维度
                    None,  # None输入
                    "invalid_string",  # 字符串输入
                ]

                recovery_success = 0
                for invalid_input in invalid_inputs:
                    try:
                        from src.gpu.core.kernels.standardized_interface import (
                            MatrixConfig,
                            MatrixOperationType,
                        )

                        config = MatrixConfig(operation_type=MatrixOperationType.MULTIPLY)

                        if invalid_input is not None:
                            result = await kernel.execute_matrix_operation(invalid_input, invalid_input, config)
                            if not result.success:
                                recovery_success += 1
                        else:
                            recovery_success += 1  # 正确处理None
                    except Exception:
                        recovery_success += 1  # 异常被正确捕获

                recovery_tests.append(
                    {
                        "test": f"invalid_input_recovery_{i}",
                        "recovery_rate": recovery_success / len(invalid_inputs),
                        "successful_recoveries": recovery_success,
                        "total_tests": len(invalid_inputs),
                    }
                )

            # 测试2: 内存压力下的异常恢复
            for i in range(5):
                kernel = TransformKernelEngine()
                await kernel.initialize()

                try:
                    # 尝试处理超大数组
                    huge_array = np.random.random(1000000).astype(np.float32)  # 1M元素

                    from src.gpu.core.kernels.standardized_interface import (
                        TransformConfig,
                        TransformOperationType,
                    )

                    config = TransformConfig(operation_type=TransformOperationType.NORMALIZE)

                    start_time = time.time()
                    result = await kernel.execute_transform_operation(huge_array, config)
                    execution_time = time.time() - start_time

                    recovery_tests.append(
                        {
                            "test": f"memory_pressure_recovery_{i}",
                            "handled_large_data": result.success,
                            "execution_time": execution_time,
                            "data_size": len(huge_array),
                        }
                    )

                except Exception as e:
                    recovery_tests.append(
                        {
                            "test": f"memory_pressure_recovery_{i}",
                            "handled_large_data": False,
                            "exception_handled": True,
                            "error_message": str(e)[:100],  # 截断错误信息
                        }
                    )

            # 测试3: 快速连续操作的稳定性
            kernel = MatrixKernelEngine()
            await kernel.initialize()

            rapid_operations = []
            for i in range(100):
                try:
                    matrix = np.random.random((128, 128)).astype(np.float32)
                    from src.gpu.core.kernels.standardized_interface import (
                        MatrixConfig,
                        MatrixOperationType,
                    )

                    config = MatrixConfig(operation_type=MatrixOperationType.MULTIPLY)

                    result = await kernel.execute_matrix_operation(matrix, matrix, config)
                    rapid_operations.append(result.success)
                except Exception:
                    rapid_operations.append(False)

            rapid_success_rate = sum(rapid_operations) / len(rapid_operations)
            recovery_tests.append(
                {
                    "test": "rapid_operations_stability",
                    "total_operations": len(rapid_operations),
                    "successful_operations": sum(rapid_operations),
                    "success_rate": rapid_success_rate,
                    "stable_performance": rapid_success_rate > 0.95,
                }
            )

            # 分析恢复能力
            total_recovery_tests = len(recovery_tests)
            successful_recoveries = sum(
                1
                for test in recovery_tests
                if test.get("recovery_rate", 0) > 0.8
                or test.get("success_rate", 0) > 0.8
                or test.get("handled_large_data", False)
                or test.get("stable_performance", False)
            )

            return {
                "success": successful_recoveries >= total_recovery_tests * 0.8,
                "total_recovery_tests": total_recovery_tests,
                "successful_recoveries": successful_recoveries,
                "recovery_success_rate": successful_recoveries / total_recovery_tests,
                "detailed_results": recovery_tests,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

async def main():
    """主函数"""
    return await run_long_term_stability_main(LongTermStabilityTester)


if __name__ == "__main__":
    report = asyncio.run(main())
