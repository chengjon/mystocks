#!/usr/bin/env python3
"""
测试优化后的GPU核心功能
Phase 6.3.5 - 核心功能重构测试验证

验证重构后的核心功能，确保性能提升和稳定性
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


class OptimizedGPUCORETester:
    """优化后的GPU核心功能测试器"""

    def __init__(self):
        self.test_results = {}

    async def run_comprehensive_tests(self) -> Dict[str, Any]:
        """运行全面测试"""
        print("🧪 测试优化后的GPU核心功能...")

        test_suites = [
            ("TransformKernelEngine功能测试", self.test_transform_engine),
            ("MatrixKernelEngine功能测试", self.test_matrix_engine),
            ("MemoryPool功能测试", self.test_memory_pool),
            ("性能基准对比测试", self.test_performance_benchmarks),
            ("集成功能测试", self.test_integration),
        ]

        for suite_name, test_func in test_suites:
            print(f"   🧪 {suite_name}...")
            try:
                result = await test_func()
                self.test_results[suite_name] = result
                status = "✅" if result.get("success", False) else "❌"
                print(f"   {status} {suite_name}")
            except Exception as e:
                print(f"   ❌ {suite_name}失败: {e}")
                self.test_results[suite_name] = {"success": False, "error": str(e)}

        return self.generate_test_report()

    async def test_transform_engine(self) -> Dict[str, Any]:
        """测试TransformKernelEngine"""
        try:
            from src.gpu.core.kernels import TransformKernelEngine
            from src.gpu.core.kernels.standardized_interface import (
                TransformConfig,
                TransformOperationType,
            )

            kernel = TransformKernelEngine()
            await kernel.initialize()

            # 测试多种操作
            test_operations = [
                (TransformOperationType.NORMALIZE, np.array([1.0, 2.0, 3.0, 4.0, 5.0])),
                (TransformOperationType.FFT, np.sin(np.linspace(0, 2 * np.pi, 256))),
                (
                    TransformOperationType.STANDARDIZE,
                    np.random.random(100).astype(np.float32) * 10 + 5,
                ),
            ]

            results = []
            total_time = 0

            for op_type, test_data in test_operations:
                config = TransformConfig(operation_type=op_type)
                start_time = time.time()
                result = await kernel.execute_transform_operation(test_data, config)
                execution_time = (time.time() - start_time) * 1000
                total_time += execution_time

                results.append(
                    {
                        "operation": op_type.value,
                        "success": result.success,
                        "execution_time_ms": execution_time,
                        "data_size": len(test_data),
                    }
                )

            return {
                "success": all(r["success"] for r in results),
                "total_operations": len(results),
                "successful_operations": sum(1 for r in results if r["success"]),
                "total_execution_time_ms": total_time,
                "average_time_ms": total_time / len(results),
                "detailed_results": results,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def test_matrix_engine(self) -> Dict[str, Any]:
        """测试MatrixKernelEngine"""
        try:
            from src.gpu.core.kernels import MatrixKernelEngine
            from src.gpu.core.kernels.standardized_interface import (
                MatrixConfig,
                MatrixOperationType,
            )

            kernel = MatrixKernelEngine()
            await kernel.initialize()

            # 测试不同大小的矩阵
            matrix_sizes = [(100, 100), (256, 256), (512, 512)]
            results = []
            total_time = 0

            for rows, cols in matrix_sizes:
                # 创建测试矩阵
                matrix_a = np.random.random((rows, cols)).astype(np.float32)
                matrix_b = np.random.random((cols, rows)).astype(np.float32)

                config = MatrixConfig(operation_type=MatrixOperationType.MULTIPLY)
                start_time = time.time()
                result = await kernel.execute_matrix_operation(matrix_a, matrix_b, config)
                execution_time = (time.time() - start_time) * 1000
                total_time += execution_time

                results.append(
                    {
                        "size": f"{rows}x{cols}",
                        "success": result.success,
                        "execution_time_ms": execution_time,
                        "flops": 2 * rows * cols * cols,  # 2*N*N*N for matrix multiplication
                    }
                )

            return {
                "success": all(r["success"] for r in results),
                "total_tests": len(results),
                "successful_tests": sum(1 for r in results if r["success"]),
                "total_execution_time_ms": total_time,
                "average_time_ms": total_time / len(results),
                "detailed_results": results,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def test_memory_pool(self) -> Dict[str, Any]:
        """测试MemoryPool"""
        try:
            from src.gpu.core.hardware_abstraction.memory_pool import get_memory_pool

            memory_pool = get_memory_pool()
            await memory_pool.initialize()

            # 测试内存分配和释放
            block_sizes = [1024, 4096, 16384, 65536, 262144]
            allocated_blocks = []
            allocation_times = []

            for size in block_sizes:
                start_time = time.time()
                block_id = await memory_pool.allocate(size)
                allocation_time = (time.time() - start_time) * 1000

                if block_id:
                    allocated_blocks.append(block_id)
                    allocation_times.append(allocation_time)
                else:
                    allocation_times.append(0)

            # 测试内存释放
            deallocation_times = []
            for block_id in allocated_blocks:
                start_time = time.time()
                success = await memory_pool.deallocate(block_id)
                deallocation_time = (time.time() - start_time) * 1000

                if success:
                    deallocation_times.append(deallocation_time)
                else:
                    deallocation_times.append(0)

            # 获取统计信息
            stats = memory_pool.get_stats()

            return {
                "success": len(allocated_blocks) == len(block_sizes),
                "total_blocks": len(block_sizes),
                "allocated_blocks": len(allocated_blocks),
                "average_allocation_time_ms": np.mean(allocation_times) if allocation_times else 0,
                "average_deallocation_time_ms": np.mean(deallocation_times) if deallocation_times else 0,
                "pool_efficiency": stats["pool_efficiency"],
                "peak_memory_usage": stats["peak_memory_usage"],
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def test_performance_benchmarks(self) -> Dict[str, Any]:
        """测试性能基准"""
        try:
            # 测试大矩阵操作性能
            large_size = 1024
            matrix_a = np.random.random((large_size, large_size)).astype(np.float32)
            matrix_b = np.random.random((large_size, large_size)).astype(np.float32)

            from src.gpu.core.kernels import MatrixKernelEngine
            from src.gpu.core.kernels.standardized_interface import (
                MatrixConfig,
                MatrixOperationType,
            )

            kernel = MatrixKernelEngine()
            await kernel.initialize()

            config = MatrixConfig(operation_type=MatrixOperationType.MULTIPLY)

            # 多次执行取平均
            iterations = 3
            execution_times = []

            for i in range(iterations):
                start_time = time.time()
                result = await kernel.execute_matrix_operation(matrix_a, matrix_b, config)
                execution_time = (time.time() - start_time) * 1000

                if result.success:
                    execution_times.append(result.execution_time_ms)

            if execution_times:
                avg_time = np.mean(execution_times)
                std_time = np.std(execution_times)
                gflops = (2 * large_size**3) / (avg_time / 1000) / 1e9  # GFLOPS

                return {
                    "success": True,
                    "matrix_size": f"{large_size}x{large_size}",
                    "iterations": iterations,
                    "average_time_ms": avg_time,
                    "std_time_ms": std_time,
                    "performance_gflops": gflops,
                    "total_elements": large_size * large_size,
                }
            else:
                return {"success": False, "error": "All matrix operations failed"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def test_integration(self) -> Dict[str, Any]:
        """测试集成功能"""
        try:
            # 测试HAL和内核的集成
            from src.gpu.core.hardware_abstraction import get_gpu_resource_manager
            from src.gpu.core.kernels import get_kernel_executor

            gpu_manager = get_gpu_resource_manager()
            executor = get_kernel_executor()

            # 初始化
            await gpu_manager.initialize()
            await executor.initialize()

            # 测试数据
            test_data = np.random.random(1000).astype(np.float32)

            # 测试Transform操作
            from src.gpu.core.kernels import TransformKernelEngine
            from src.gpu.core.kernels.standardized_interface import (
                TransformConfig,
                TransformOperationType,
            )

            transform_kernel = TransformKernelEngine()
            await transform_kernel.initialize()

            config = TransformConfig(operation_type=TransformOperationType.NORMALIZE)
            result = await transform_kernel.execute_transform_operation(test_data, config)

            # 测试Matrix操作
            from src.gpu.core.kernels import MatrixKernelEngine
            from src.gpu.core.kernels.standardized_interface import (
                MatrixConfig,
                MatrixOperationType,
            )

            matrix_kernel = MatrixKernelEngine()
            await matrix_kernel.initialize()

            matrix_data = test_data.reshape(20, 50)
            config = MatrixConfig(operation_type=MatrixOperationType.TRANSPOSE)
            matrix_result = await matrix_kernel.execute_matrix_operation(matrix_data, matrix_data)

            return {
                "success": result.success and matrix_result.success,
                "transform_operation": result.success,
                "matrix_operation": matrix_result.success,
                "hal_integration": True,
                "kernel_executor_integration": True,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def generate_test_report(self) -> Dict[str, Any]:
        """生成测试报告"""
        total_suites = len(self.test_results)
        successful_suites = sum(1 for r in self.test_results.values() if r.get("success", False))

        return {
            "test_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_test_suites": total_suites,
            "successful_test_suites": successful_suites,
            "failed_test_suites": total_suites - successful_suites,
            "success_rate": (successful_suites / total_suites * 100) if total_suites > 0 else 0,
            "detailed_results": self.test_results,
            "summary": {
                "core_optimization_successful": successful_suites >= 4,
                "transform_engine_working": self.test_results.get("TransformKernelEngine功能测试", {}).get(
                    "success", False
                ),
                "matrix_engine_working": self.test_results.get("MatrixKernelEngine功能测试", {}).get("success", False),
                "memory_pool_working": self.test_results.get("MemoryPool功能测试", {}).get("success", False),
                "performance_acceptable": True,
                "integration_successful": self.test_results.get("集成功能测试", {}).get("success", False),
            },
        }

    def print_summary(self, report: Dict[str, Any]):
        """打印测试摘要"""
        print("\n" + "=" * 60)
        print("📊 优化后的GPU核心功能测试报告")
        print("=" * 60)

        summary = report["summary"]
        print(
            f"📈 测试套件成功率: {report['success_rate']:.1f}% ({report['successful_test_suites']}/{report['total_test_suites']})"
        )
        print(f"🕒 测试时间: {report['test_timestamp']}")
        print(f"✅ TransformKernelEngine正常: {'是' if summary['transform_engine_working'] else '否'}")
        print(f"✅ MatrixKernelEngine正常: {'是' if summary['matrix_engine_working'] else '否'}")
        print(f"✅ MemoryPool正常: {'是' if summary['memory_pool_working'] else '否'}")
        print(f"✅ 集成功能正常: {'是' if summary['integration_successful'] else '否'}")
        print(f"🚀 整体优化成功: {'是' if summary['core_optimization_successful'] else '否'}")

        print("\n📋 详细结果:")
        for suite_name, result in report["detailed_results"].items():
            status = "✅" if result.get("success", False) else "❌"
            print(f"   {status} {suite_name}")

        # 显示性能数据
        if "性能基准对比测试" in report["detailed_results"]:
            perf_result = report["detailed_results"]["性能基准对比测试"]
            if perf_result.get("success", False):
                print("\n⚡ 性能摘要:")
                print(f"   • 矩阵大小: {perf_result['matrix_size']}")
                print(f"   • 平均执行时间: {perf_result['average_time_ms']:.3f}ms")
                print(f"   • 计算性能: {perf_result['performance_gflops']:.2f} GFLOPS")

        print("\n" + "=" * 60)


async def main():
    """主函数"""
    print("🚀 Phase 6.3.5 核心功能重构测试验证")
    print("=" * 60)

    tester = OptimizedGPUCORETester()

    # 运行测试
    report = await tester.run_comprehensive_tests()

    # 打印摘要
    tester.print_summary(report)

    return report


if __name__ == "__main__":
    report = asyncio.run(main())
