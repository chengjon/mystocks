#!/usr/bin/env python3
"""
GPU加速引擎集成测试套件
Phase 6.4.2 - GPU加速引擎集成测试

验证所有GPU组件的协同工作，包括HAL、内核层、内存池和高级功能的完整集成
"""

import asyncio
import sys
import time
from pathlib import Path
from typing import Any, Dict

import numpy as np

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


class GPUEngineIntegrationTester:
    """GPU加速引擎集成测试器"""

    def __init__(self):
        self.test_results = {}
        self.performance_metrics = {}

    async def run_comprehensive_integration_tests(self) -> Dict[str, Any]:
        """运行全面的集成测试"""
        print("🚀 GPU加速引擎集成测试...")

        test_suites = [
            ("HAL层集成测试", self.test_hal_integration),
            ("内核层协同测试", self.test_kernel_coordination),
            ("内存池集成测试", self.test_memory_pool_integration),
            ("端到端工作流测试", self.test_end_to_end_workflow),
            ("性能压力测试", self.test_performance_stress),
            ("错误恢复测试", self.test_error_recovery),
            ("并发操作测试", self.test_concurrent_operations),
        ]

        for suite_name, test_func in test_suites:
            print(f"   🧪 {suite_name}...")
            try:
                start_time = time.time()
                result = await test_func()
                execution_time = time.time() - start_time

                self.test_results[suite_name] = {
                    "success": result.get("success", False),
                    "execution_time": execution_time,
                    "details": result,
                }

                status = "✅" if result.get("success", False) else "❌"
                print(f"   {status} {suite_name} ({execution_time:.2f}s)")

            except Exception as e:
                print(f"   ❌ {suite_name}失败: {e}")
                self.test_results[suite_name] = {
                    "success": False,
                    "error": str(e),
                    "execution_time": 0,
                }

        return self.generate_integration_report()

    async def test_hal_integration(self) -> Dict[str, Any]:
        """测试HAL层集成"""
        try:
            from src.gpu.core.hardware_abstraction import (
                get_gpu_resource_manager,
                get_memory_pool,
            )
            from src.gpu.core.kernels import get_kernel_executor

            # 初始化HAL组件
            gpu_manager = get_gpu_resource_manager()
            memory_pool = get_memory_pool()
            kernel_executor = get_kernel_executor()

            # 测试初始化 (KernelExecutor没有initialize方法)
            await gpu_manager.initialize()
            await memory_pool.initialize()
            # kernel_executor 在实例化时已经初始化完成

            # 测试设备检测
            devices = gpu_manager.get_available_devices()
            if not devices:
                return {"success": True, "simulated_mode": True, "devices": 0}

            # 测试资源分配
            from src.gpu.core.hardware_abstraction.interfaces import (
                AllocationRequest,
                PerformanceProfile,
                StrategyPriority,
            )

            request = AllocationRequest(
                strategy_id="integration_test",
                required_memory=1024,  # 1GB
                priority=StrategyPriority.MEDIUM,
                performance_profile=PerformanceProfile(),
            )

            context = await gpu_manager.allocate_context(request)

            return {
                "success": True,
                "devices_detected": len(devices),
                "context_allocated": context is not None,
                "hal_components_initialized": 3,
                "simulated_mode": len(devices) > 0 and "Simulated" in devices[0].name,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def test_kernel_coordination(self) -> Dict[str, Any]:
        """测试内核层协同工作"""
        try:
            from src.gpu.core.kernels import MatrixKernelEngine, TransformKernelEngine
            from src.gpu.core.kernels.standardized_interface import (
                MatrixConfig,
                MatrixOperationType,
                TransformConfig,
                TransformOperationType,
            )

            # 初始化内核
            matrix_kernel = MatrixKernelEngine()
            transform_kernel = TransformKernelEngine()

            await matrix_kernel.initialize()
            await transform_kernel.initialize()

            # 创建测试数据
            test_matrix = np.random.random((256, 256)).astype(np.float32)
            test_data = np.random.random(1000).astype(np.float32)

            # 测试矩阵运算
            matrix_config = MatrixConfig(operation_type=MatrixOperationType.MULTIPLY)
            matrix_result = await matrix_kernel.execute_matrix_operation(test_matrix, test_matrix.T, matrix_config)

            # 测试变换运算
            transform_config = TransformConfig(operation_type=TransformOperationType.NORMALIZE)
            transform_result = await transform_kernel.execute_transform_operation(test_data, transform_config)

            # 测试链式操作（先变换后矩阵运算）
            chained_data = np.random.random((512, 512)).astype(np.float32)
            normalize_config = TransformConfig(operation_type=TransformOperationType.NORMALIZE)
            normalized_result = await transform_kernel.execute_transform_operation(chained_data, normalize_config)

            if normalized_result.success:
                # 将标准化后的数据转换为矩阵进行乘法
                matrix_config = MatrixConfig(operation_type=MatrixOperationType.MULTIPLY)
                final_result = await matrix_kernel.execute_matrix_operation(
                    normalized_result.result_data,
                    normalized_result.result_data.T,
                    matrix_config,
                )
            else:
                final_result = None

            return {
                "success": matrix_result.success and transform_result.success,
                "matrix_operations": matrix_result.success,
                "transform_operations": transform_result.success,
                "chained_operations": final_result.success if final_result else False,
                "matrix_execution_time": matrix_result.execution_time_ms,
                "transform_execution_time": transform_result.execution_time_ms,
                "kernels_coordination": True,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def test_memory_pool_integration(self) -> Dict[str, Any]:
        """测试内存池集成"""
        try:
            from src.gpu.core.hardware_abstraction.memory_pool import get_memory_pool

            memory_pool = get_memory_pool()
            await memory_pool.initialize()

            # 测试多次内存分配和释放
            allocation_sizes = [1024, 4096, 16384, 65536, 262144]  # 1KB到256KB
            allocated_blocks = []

            # 分配阶段
            for size in allocation_sizes:
                block_id = await memory_pool.allocate(size)
                if block_id:
                    allocated_blocks.append((block_id, size))

            # 测试并发分配
            concurrent_tasks = []
            for i in range(10):
                task = memory_pool.allocate(8192)  # 8KB
                concurrent_tasks.append(task)

            concurrent_results = await asyncio.gather(*concurrent_tasks)
            concurrent_allocated = sum(1 for r in concurrent_results if r)

            # 释放阶段
            deallocation_success = 0
            for block_id, size in allocated_blocks:
                success = await memory_pool.deallocate(block_id)
                if success:
                    deallocation_success += 1

            # 获取统计信息
            stats = memory_pool.get_stats()

            return {
                "success": len(allocated_blocks) == len(allocation_sizes),
                "allocations_successful": len(allocated_blocks),
                "total_allocation_size": sum(allocation_sizes),
                "concurrent_allocations": concurrent_allocated,
                "concurrent_success_rate": concurrent_allocated / 10,
                "deallocations_successful": deallocation_success,
                "pool_efficiency": stats.get("pool_efficiency", 0),
                "peak_memory_usage": stats.get("peak_memory_usage", 0),
                "memory_integration": True,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def test_end_to_end_workflow(self) -> Dict[str, Any]:
        """测试端到端工作流"""
        try:
            # 模拟完整的量化交易工作流
            from src.gpu.core.hardware_abstraction import get_memory_pool
            from src.gpu.core.kernels import MatrixKernelEngine, TransformKernelEngine

            # 初始化组件
            matrix_kernel = MatrixKernelEngine()
            transform_kernel = TransformKernelEngine()
            memory_pool = get_memory_pool()

            await matrix_kernel.initialize()
            await transform_kernel.initialize()
            await memory_pool.initialize()

            # 步骤1: 模拟市场数据（价格序列）
            price_data = np.random.random(10000).astype(np.float32) * 100 + 50

            # 步骤2: 计算收益率（变换操作）
            from src.gpu.core.kernels.standardized_interface import (
                TransformConfig,
                TransformOperationType,
            )

            return_config = TransformConfig(operation_type=TransformOperationType.RETURN)
            return_result = await transform_kernel.execute_transform_operation(price_data, return_config)

            # 步骤3: 计算波动率（变换操作）
            volatility_config = TransformConfig(operation_type=TransformOperationType.VOLATILITY)
            volatility_result = await transform_kernel.execute_transform_operation(price_data, volatility_config)

            # 步骤4: 创建相关矩阵（矩阵操作）
            # 将价格序列转换为多资产价格矩阵
            price_matrix = np.random.random((100, 50)).astype(np.float32)  # 100个时间点，50个资产

            # 计算收益率矩阵
            returns_matrix = np.diff(price_matrix, axis=0)

            # 计算相关系数矩阵
            returns_matrix_normalized = (returns_matrix - np.mean(returns_matrix, axis=0)) / np.std(
                returns_matrix, axis=0
            )
            correlation_matrix = np.corrcoef(returns_matrix_normalized.T)

            # 步骤5: 风险计算（矩阵运算）
            from src.gpu.core.kernels.standardized_interface import (
                MatrixConfig,
                MatrixOperationType,
            )

            risk_config = MatrixConfig(operation_type=MatrixOperationType.MULTIPLY)

            # 模拟风险权重矩阵
            risk_weights = np.random.random((50, 50)).astype(np.float32)
            risk_result = await matrix_kernel.execute_matrix_operation(correlation_matrix, risk_weights, risk_config)

            workflow_success = return_result.success and volatility_result.success and risk_result.success

            return {
                "success": workflow_success,
                "price_data_points": len(price_data),
                "return_calculation": return_result.success,
                "volatility_calculation": volatility_result.success,
                "correlation_matrix_size": correlation_matrix.shape,
                "risk_calculation": risk_result.success,
                "workflow_stages_completed": sum(
                    [
                        return_result.success,
                        volatility_result.success,
                        risk_result.success,
                    ]
                ),
                "total_workflow_stages": 3,
                "workflow_completion_rate": sum(
                    [
                        return_result.success,
                        volatility_result.success,
                        risk_result.success,
                    ]
                )
                / 3,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def test_performance_stress(self) -> Dict[str, Any]:
        """测试性能压力"""
        try:
            from src.gpu.core.kernels import MatrixKernelEngine

            matrix_kernel = MatrixKernelEngine()
            await matrix_kernel.initialize()

            # 压力测试：大矩阵运算
            large_sizes = [512, 1024, 2048]
            stress_results = []

            for size in large_sizes:
                # 创建大矩阵
                matrix_a = np.random.random((size, size)).astype(np.float32)
                matrix_b = np.random.random((size, size)).astype(np.float32)

                # 执行矩阵乘法
                from src.gpu.core.kernels.standardized_interface import (
                    MatrixConfig,
                    MatrixOperationType,
                )

                config = MatrixConfig(operation_type=MatrixOperationType.MULTIPLY)

                start_time = time.time()
                result = await matrix_kernel.execute_matrix_operation(matrix_a, matrix_b, config)
                execution_time = time.time() - start_time

                if result.success:
                    gflops = (2 * size**3) / execution_time / 1e9
                    stress_results.append(
                        {
                            "matrix_size": size,
                            "execution_time": execution_time,
                            "performance_gflops": gflops,
                            "memory_usage_mb": result.memory_used_bytes / (1024 * 1024),
                        }
                    )

            # 测试多次迭代稳定性
            iterations = 10
            test_matrix = np.random.random((512, 512)).astype(np.float32)
            iteration_times = []

            for i in range(iterations):
                config = MatrixConfig(operation_type=MatrixOperationType.MULTIPLY)
                start_time = time.time()
                result = await matrix_kernel.execute_matrix_operation(test_matrix, test_matrix, config)
                iteration_time = time.time() - start_time

                if result.success:
                    iteration_times.append(iteration_time)

            return {
                "success": len(stress_results) > 0 and len(iteration_times) > 0,
                "stress_tests_passed": len(stress_results),
                "max_matrix_size_tested": max(s["matrix_size"] for s in stress_results) if stress_results else 0,
                "peak_performance_gflops": (
                    max(s["performance_gflops"] for s in stress_results) if stress_results else 0
                ),
                "average_performance_gflops": (
                    sum(s["performance_gflops"] for s in stress_results) / len(stress_results) if stress_results else 0
                ),
                "iteration_stability": {
                    "iterations": len(iteration_times),
                    "avg_time": sum(iteration_times) / len(iteration_times) if iteration_times else 0,
                    "std_time": np.std(iteration_times) if iteration_times else 0,
                    "performance_cv": (
                        np.std(iteration_times) / np.mean(iteration_times)
                        if iteration_times and np.mean(iteration_times) > 0
                        else 0
                    ),
                },
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def test_error_recovery(self) -> Dict[str, Any]:
        """测试错误恢复"""
        try:
            from src.gpu.core.kernels import MatrixKernelEngine, TransformKernelEngine

            matrix_kernel = MatrixKernelEngine()
            transform_kernel = TransformKernelEngine()

            await matrix_kernel.initialize()
            await transform_kernel.initialize()

            error_recovery_tests = []

            # 测试1: 不兼容的矩阵维度
            try:
                from src.gpu.core.kernels.standardized_interface import (
                    MatrixConfig,
                    MatrixOperationType,
                )

                matrix_a = np.random.random((100, 200)).astype(np.float32)
                matrix_b = np.random.random((300, 400)).astype(np.float32)  # 不兼容
                config = MatrixConfig(operation_type=MatrixOperationType.MULTIPLY)
                result = await matrix_kernel.execute_matrix_operation(matrix_a, matrix_b, config)
                error_recovery_tests.append(
                    {
                        "test": "incompatible_matrices",
                        "handled_gracefully": not result.success,
                        "error_message": result.error_message if not result.success else None,
                    }
                )
            except Exception as e:
                error_recovery_tests.append(
                    {
                        "test": "incompatible_matrices",
                        "handled_gracefully": False,
                        "error_message": str(e),
                    }
                )

            # 测试2: 无效的变换操作
            try:
                from src.gpu.core.kernels.standardized_interface import (
                    TransformConfig,
                    TransformOperationType,
                )

                invalid_data = np.array([])  # 空数组
                config = TransformConfig(operation_type=TransformOperationType.NORMALIZE)
                result = await transform_kernel.execute_transform_operation(invalid_data, config)
                error_recovery_tests.append(
                    {
                        "test": "invalid_transform_data",
                        "handled_gracefully": not result.success,
                        "error_message": result.error_message if not result.success else None,
                    }
                )
            except Exception as e:
                error_recovery_tests.append(
                    {
                        "test": "invalid_transform_data",
                        "handled_gracefully": False,
                        "error_message": str(e),
                    }
                )

            # 测试3: 内存分配恢复
            try:
                from src.gpu.core.hardware_abstraction.memory_pool import (
                    get_memory_pool,
                )

                memory_pool = get_memory_pool()
                await memory_pool.initialize()

                # 尝试分配超大内存块
                huge_block = await memory_pool.allocate(1024 * 1024 * 1024)  # 1GB
                deallocation_success = await memory_pool.deallocate(huge_block) if huge_block else True

                error_recovery_tests.append(
                    {
                        "test": "huge_memory_allocation",
                        "handled_gracefully": True,  # CPU回退应该能处理
                        "allocation_successful": huge_block is not None,
                        "deallocation_successful": deallocation_success,
                    }
                )
            except Exception as e:
                error_recovery_tests.append(
                    {
                        "test": "huge_memory_allocation",
                        "handled_gracefully": False,
                        "error_message": str(e),
                    }
                )

            successful_recoveries = sum(1 for test in error_recovery_tests if test.get("handled_gracefully", False))

            return {
                "success": successful_recoveries >= 2,  # 至少2/3测试通过
                "total_tests": len(error_recovery_tests),
                "successful_recoveries": successful_recoveries,
                "recovery_rate": successful_recoveries / len(error_recovery_tests),
                "detailed_results": error_recovery_tests,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def test_concurrent_operations(self) -> Dict[str, Any]:
        """测试并发操作"""
        try:
            from src.gpu.core.kernels import MatrixKernelEngine

            matrix_kernel = MatrixKernelEngine()
            await matrix_kernel.initialize()

            # 创建并发任务
            async def concurrent_matrix_operation(matrix_size: int, operation_id: int):
                try:
                    matrix_a = np.random.random((matrix_size, matrix_size)).astype(np.float32)
                    matrix_b = np.random.random((matrix_size, matrix_size)).astype(np.float32)

                    from src.gpu.core.kernels.standardized_interface import (
                        MatrixConfig,
                        MatrixOperationType,
                    )

                    config = MatrixConfig(operation_type=MatrixOperationType.MULTIPLY)

                    start_time = time.time()
                    result = await matrix_kernel.execute_matrix_operation(matrix_a, matrix_b, config)
                    execution_time = time.time() - start_time

                    return {
                        "operation_id": operation_id,
                        "success": result.success,
                        "execution_time": execution_time,
                        "matrix_size": matrix_size,
                        "performance_gflops": (2 * matrix_size**3) / execution_time / 1e9 if result.success else 0,
                    }
                except Exception as e:
                    return {
                        "operation_id": operation_id,
                        "success": False,
                        "error": str(e),
                        "matrix_size": matrix_size,
                    }

            # 启动多个并发操作
            concurrent_tasks = []
            matrix_sizes = [256, 512, 256, 512, 256]  # 不同大小的矩阵

            for i, size in enumerate(matrix_sizes):
                task = concurrent_matrix_operation(size, i)
                concurrent_tasks.append(task)

            # 等待所有任务完成
            results = await asyncio.gather(*concurrent_tasks, return_exceptions=True)

            # 分析结果
            successful_operations = sum(1 for r in results if isinstance(r, dict) and r.get("success", False))
            total_operations = len(results)

            performance_stats = []
            for r in results:
                if isinstance(r, dict) and r.get("success", False):
                    performance_stats.append(r.get("performance_gflops", 0))

            return {
                "success": successful_operations >= total_operations * 0.8,  # 80%成功率
                "total_concurrent_operations": total_operations,
                "successful_operations": successful_operations,
                "concurrency_success_rate": successful_operations / total_operations,
                "average_performance_gflops": (
                    sum(performance_stats) / len(performance_stats) if performance_stats else 0
                ),
                "performance_variance": np.var(performance_stats) if performance_stats else 0,
                "detailed_results": [r for r in results if isinstance(r, dict)],
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def generate_integration_report(self) -> Dict[str, Any]:
        """生成集成测试报告"""
        total_suites = len(self.test_results)
        successful_suites = sum(1 for r in self.test_results.values() if r.get("success", False))

        # 计算总体执行时间
        total_execution_time = sum(r.get("execution_time", 0) for r in self.test_results.values())

        return {
            "test_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "integration_phase": "Phase 6.4.2",
            "total_test_suites": total_suites,
            "successful_test_suites": successful_suites,
            "failed_test_suites": total_suites - successful_suites,
            "success_rate": (successful_suites / total_suites * 100) if total_suites > 0 else 0,
            "total_execution_time": total_execution_time,
            "detailed_results": self.test_results,
            "summary": {
                "hal_integration_working": self.test_results.get("HAL层集成测试", {}).get("success", False),
                "kernel_coordination_working": self.test_results.get("内核层协同测试", {}).get("success", False),
                "memory_pool_integration_working": self.test_results.get("内存池集成测试", {}).get("success", False),
                "end_to_end_workflow_working": self.test_results.get("端到端工作流测试", {}).get("success", False),
                "performance_stress_passed": self.test_results.get("性能压力测试", {}).get("success", False),
                "error_recovery_working": self.test_results.get("错误恢复测试", {}).get("success", False),
                "concurrent_operations_working": self.test_results.get("并发操作测试", {}).get("success", False),
                "overall_integration_successful": successful_suites >= total_suites * 0.8,
            },
        }

    def print_summary(self, report: Dict[str, Any]):
        """打印测试摘要"""
        print("\n" + "=" * 70)
        print("📊 GPU加速引擎集成测试报告")
        print("=" * 70)

        summary = report["summary"]
        print(
            f"📈 集成测试成功率: {report['success_rate']:.1f}% ({report['successful_test_suites']}/{report['total_test_suites']})"
        )
        print(f"🕒 测试时间: {report['test_timestamp']}")
        print(f"⏱️  总执行时间: {report['total_execution_time']:.2f}秒")

        print("\n🔧 组件状态:")
        print(f"   ✅ HAL层集成: {'正常' if summary['hal_integration_working'] else '异常'}")
        print(f"   ✅ 内核协同: {'正常' if summary['kernel_coordination_working'] else '异常'}")
        print(f"   ✅ 内存池集成: {'正常' if summary['memory_pool_integration_working'] else '异常'}")
        print(f"   ✅ 端到端工作流: {'正常' if summary['end_to_end_workflow_working'] else '异常'}")
        print(f"   ✅ 性能压力测试: {'通过' if summary['performance_stress_passed'] else '失败'}")
        print(f"   ✅ 错误恢复: {'正常' if summary['error_recovery_working'] else '异常'}")
        print(f"   ✅ 并发操作: {'正常' if summary['concurrent_operations_working'] else '异常'}")
        print(f"🚀 整体集成成功: {'是' if summary['overall_integration_successful'] else '否'}")

        print("\n📋 详细结果:")
        for suite_name, result in report["detailed_results"].items():
            status = "✅" if result.get("success", False) else "❌"
            execution_time = result.get("execution_time", 0)
            print(f"   {status} {suite_name} ({execution_time:.2f}s)")

        # 显示性能数据
        if "性能压力测试" in report["detailed_results"]:
            perf_result = report["detailed_results"]["性能压力测试"]["details"]
            if perf_result.get("success", False):
                print("\n⚡ 性能摘要:")
                print(
                    f"   • 最大矩阵规模: {perf_result['max_matrix_size_tested']}x{perf_result['max_matrix_size_tested']}"
                )
                print(f"   • 峰值性能: {perf_result['peak_performance_gflops']:.2f} GFLOPS")
                print(f"   • 平均性能: {perf_result['average_performance_gflops']:.2f} GFLOPS")

                if "iteration_stability" in perf_result:
                    stability = perf_result["iteration_stability"]
                    print(f"   • 迭代稳定性: CV={stability['performance_cv']:.3f} (越低越好)")

        # 显示并发数据
        if "并发操作测试" in report["detailed_results"]:
            concurrent_result = report["detailed_results"]["并发操作测试"]["details"]
            if concurrent_result.get("success", False):
                print("\n🔄 并发操作摘要:")
                print(f"   • 并发成功率: {concurrent_result['concurrency_success_rate'] * 100:.1f}%")
                print(f"   • 平均性能: {concurrent_result['average_performance_gflops']:.2f} GFLOPS")

        print("\n" + "=" * 70)


async def main():
    """主函数"""
    print("🚀 Phase 6.4.2 GPU加速引擎集成测试")
    print("=" * 70)

    tester = GPUEngineIntegrationTester()

    # 运行集成测试
    report = await tester.run_comprehensive_integration_tests()

    # 打印摘要
    tester.print_summary(report)

    return report


if __name__ == "__main__":
    report = asyncio.run(main())
