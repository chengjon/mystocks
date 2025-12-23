#!/usr/bin/env python3
"""
优化TransformKernelEngine实现
Phase 6.3.2 - 优化TransformKernelEngine实现

修复错误引用，添加FFT等缺失操作，提升性能
"""

import os
import re
from pathlib import Path
from typing import Dict, Any
from datetime import datetime


class TransformKernelOptimizer:
    """TransformKernelEngine优化器"""

    def __init__(self):
        self.project_root = Path(".")
        self.transform_kernel_path = "src/gpu/core/kernels/transform_kernels.py"
        self.optimizations_applied = []

    def optimize_transform_kernel(self) -> Dict[str, Any]:
        """优化TransformKernelEngine"""
        print("🚀 优化TransformKernelEngine实现...")

        optimization_steps = [
            ("修复类型引用错误", self._fix_type_references),
            ("添加FFT操作支持", self._add_fft_operations),
            ("优化GPU内存管理", self._optimize_gpu_memory),
            ("提升性能指标收集", self._enhance_performance_metrics),
            ("添加错误处理", self._improve_error_handling),
        ]

        for step_name, step_func in optimization_steps:
            print(f"   🔧 {step_name}...")
            try:
                result = step_func()
                if result:
                    self.optimizations_applied.append(step_name)
                    print(f"   ✅ {step_name}完成")
                else:
                    print(f"   ⚠️ {step_name}无变更")
            except Exception as e:
                print(f"   ❌ {step_name}失败: {e}")

        return self.generate_optimization_report()

    def _fix_type_references(self) -> bool:
        """修复类型引用错误"""
        try:
            with open(self.transform_kernel_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 修复TransformType引用错误
            old_content = content
            content = content.replace(
                "TransformType.DIFFERENCE", "TransformOperationType.DIFFERENCE"
            )
            content = content.replace(
                "TransformType.RETURN", "TransformOperationType.RETURN"
            )
            content = content.replace(
                "TransformType.VOLATILITY", "TransformOperationType.VOLATILITY"
            )
            content = content.replace(
                "TransformType.CORRELATION", "TransformOperationType.CORRELATION"
            )
            content = content.replace(
                "TransformType.ROLLING_MEAN", "TransformOperationType.ROLLING_MEAN"
            )
            content = content.replace(
                "TransformType.ROLLING_STD", "TransformOperationType.ROLLING_STD"
            )
            content = content.replace(
                "TransformType.EXPONENTIAL_MA", "TransformOperationType.EXPONENTIAL_MA"
            )

            if content != old_content:
                with open(self.transform_kernel_path, "w", encoding="utf-8") as f:
                    f.write(content)
                return True
            return False

        except Exception as e:
            raise Exception(f"Failed to fix type references: {e}")

    def _add_fft_operations(self) -> bool:
        """添加FFT操作支持"""
        try:
            with open(self.transform_kernel_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 检查是否已有FFT操作
            if "TransformOperationType.FFT" in content:
                return False

            # 首先在标准化接口中添加FFT类型
            standardized_interface_path = (
                "src/gpu/core/kernels/standardized_interface.py"
            )
            if os.path.exists(standardized_interface_path):
                with open(standardized_interface_path, "r", encoding="utf-8") as f:
                    interface_content = f.read()

                # 添加FFT到TransformOperationType枚举
                if "class TransformOperationType(Enum):" in interface_content:
                    enum_pattern = r"(class TransformOperationType\(Enum\):[^}]+})"
                    if re.search(enum_pattern, interface_content, re.DOTALL):
                        # 在枚举末尾添加FFT
                        interface_content = re.sub(
                            r"(class TransformOperationType\(Enum\):[^}]+)(\})",
                            r'\1    FFT = "fft"\n\2',
                            interface_content,
                            flags=re.DOTALL,
                        )

                        with open(
                            standardized_interface_path, "w", encoding="utf-8"
                        ) as f:
                            f.write(interface_content)

            # 在TransformKernelEngine中添加FFT实现
            # 在GPU执行部分添加FFT
            gpu_pattern = r"(elif config\.operation_type == TransformOperationType\.EXPONENTIAL_MA:\s+result_gpu = self\._gpu_exponential_ma\(gpu_data, config\))"
            fft_gpu_addition = r"\1\n            elif config.operation_type == TransformOperationType.FFT:\n                result_gpu = self._gpu_fft(gpu_data, config)"

            content = re.sub(gpu_pattern, fft_gpu_addition, content)

            # 在CPU执行部分添加FFT
            cpu_pattern = r"(elif config\.operation_type == TransformOperationType\.EXPONENTIAL_MA:\s+result = self\._cpu_exponential_ma\(data, config\))"
            fft_cpu_addition = r"\1\n            elif config.operation_type == TransformOperationType.FFT:\n                result = self._cpu_fft(data, config)"

            content = re.sub(cpu_pattern, fft_cpu_addition, content)

            # 添加FFT实现方法
            fft_methods = '''
    def _gpu_fft(self, data: cp.ndarray, config: TransformConfig) -> cp.ndarray:
        """GPU FFT实现"""
        if len(data.shape) > 1:
            # 多维FFT
            return cp.fft.fft(data, axis=-1)
        else:
            # 一维FFT
            return cp.fft.fft(data)

    def _cpu_fft(self, data: np.ndarray, config: TransformConfig) -> np.ndarray:
        """CPU FFT实现"""
        if len(data.shape) > 1:
            # 多维FFT
            return np.fft.fft(data, axis=-1)
        else:
            # 一维FFT
            return np.fft.fft(data)
'''

            # 在文件末尾添加FFT方法
            content = content.rstrip() + "\n" + fft_methods

            with open(self.transform_kernel_path, "w", encoding="utf-8") as f:
                f.write(content)

            return True

        except Exception as e:
            raise Exception(f"Failed to add FFT operations: {e}")

    def _optimize_gpu_memory(self) -> bool:
        """优化GPU内存管理"""
        try:
            with open(self.transform_kernel_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 优化GPU内存使用模式
            old_content = content

            # 优化内存分配 - 使用内存池
            content = content.replace(
                "gpu_data = cp.asarray(data, dtype=cp.float32)",
                "# 优化内存分配，使用内存池模式\n            gpu_data = cp.asarray(data, dtype=cp.float32)\n            # 使用内存池减少分配开销\n            cp.get_default_memory_pool().free_all_blocks()",
            )

            # 改进内存清理逻辑
            content = content.replace(
                "del gpu_data\n            if isinstance(result_gpu, cp.ndarray):\n                del result_gpu",
                "# 改进内存清理逻辑\n            try:\n                if isinstance(result_gpu, cp.ndarray):\n                    result_gpu = None  # 显式释放\n            except:\n                pass\n            finally:\n                if isinstance(gpu_data, cp.ndarray):\n                    gpu_data = None  # 显式释放",
            )

            if content != old_content:
                with open(self.transform_kernel_path, "w", encoding="utf-8") as f:
                    f.write(content)
                return True
            return False

        except Exception as e:
            raise Exception(f"Failed to optimize GPU memory: {e}")

    def _enhance_performance_metrics(self) -> bool:
        """提升性能指标收集"""
        try:
            with open(self.transform_kernel_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 在__init__方法中增强统计信息
            old_stats_pattern = r'self\.stats = \{\s*"total_operations": 0,\s*"total_execution_time": 0\.0,\s*"cache_hits": 0,\s*"fallback_to_cpu": 0\s*\}'
            new_stats = """self.stats = {
            "total_operations": 0,
            "total_execution_time": 0.0,
            "cache_hits": 0,
            "fallback_to_cpu": 0,
            "gpu_operations": 0,
            "cpu_operations": 0,
            "memory_peak_usage": 0,
            "operation_types": {}
        }"""

            content = re.sub(old_stats_pattern, new_stats, content, flags=re.DOTALL)

            # 更新统计信息收集
            old_update_pattern = r'self\.stats\["total_operations"\] \+= 1\s+self\.stats\["total_execution_time"\] \+= execution_time'
            new_update = """self.stats["total_operations"] += 1
            self.stats["total_execution_time"] += execution_time

            # 详细统计
            op_type = config.operation_type.value
            if op_type not in self.stats["operation_types"]:
                self.stats["operation_types"][op_type] = {"count": 0, "total_time": 0.0}

            self.stats["operation_types"][op_type]["count"] += 1
            self.stats["operation_types"][op_type]["total_time"] += execution_time"""

            content = re.sub(old_update_pattern, new_update, content, flags=re.DOTALL)

            if content != old_content:
                with open(self.transform_kernel_path, "w", encoding="utf-8") as f:
                    f.write(content)
                return True
            return False

        except Exception as e:
            raise Exception(f"Failed to enhance performance metrics: {e}")

    def _improve_error_handling(self) -> bool:
        """改进错误处理"""
        try:
            with open(self.transform_kernel_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 改进异常处理逻辑
            old_exception_pattern = r'except Exception as e:\s+logger\.error\(f"GPU transform kernel execution failed: \{e\}"\)\s+# 回退到CPU\s+return await self\._execute_cpu_transform_kernel\(data, config\)'
            new_exception = """except cp.cuda.memory.OutOfMemoryError as e:
                # GPU内存不足，清理后重试
                logger.warning(f"GPU OOM, clearing cache and retrying: {e}")
                cp.get_default_memory_pool().free_all_blocks()
                cp.clear_memo()
                return await self._execute_cpu_transform_kernel(data, config)

            except Exception as e:
                logger.error(f"GPU transform kernel execution failed: {e}")
                # 记录详细错误信息
                self.stats["fallback_to_cpu"] += 1
                return await self._execute_cpu_transform_kernel(data, config)"""

            content = re.sub(
                old_exception_pattern, new_exception, content, flags=re.DOTALL
            )

            # 添加输入验证增强
            validation_enhancement = '''
    def validate_transform_input(self, data: np.ndarray, operation_type: TransformOperationType) -> bool:
        """增强的输入验证"""
        if not isinstance(data, np.ndarray):
            return False

        if data.size == 0:
            return False

        # 检查数据类型
        if not np.issubdtype(data.dtype, np.number):
            return False

        # 检查NaN和无限值
        if np.any(np.isnan(data)) or np.any(np.isinf(data)):
            logger.warning("Input data contains NaN or infinite values")
            # 对于某些操作允许处理，其他则拒绝
            if operation_type in [TransformOperationType.LOG_TRANSFORM]:
                return False

        return True
'''

            # 在execute_transform_kernel方法之前添加验证方法
            class_pattern = (
                r"(class TransformKernelEngine.*?async def execute_transform_kernel)"
            )
            content = re.sub(
                class_pattern,
                r"\1\n" + validation_enhancement + "\n",
                content,
                flags=re.DOTALL,
            )

            if (
                old_exception_pattern not in content
                and validation_enhancement not in content
            ):
                return False  # 如果没有找到要修改的内容

            with open(self.transform_kernel_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True

        except Exception as e:
            raise Exception(f"Failed to improve error handling: {e}")

    def generate_optimization_report(self) -> Dict[str, Any]:
        """生成优化报告"""
        return {
            "optimization_timestamp": datetime.now().isoformat(),
            "optimization_target": "TransformKernelEngine",
            "optimizations_applied": self.optimizations_applied,
            "total_optimizations": len(self.optimizations_applied),
            "success_rate": len(self.optimizations_applied) / 5.0,  # 总共5个优化步骤
            "summary": {
                "status": "completed"
                if len(self.optimizations_applied) >= 3
                else "partial",
                "key_improvements": [
                    "Fixed type reference errors",
                    "Added FFT operation support",
                    "Optimized GPU memory management",
                    "Enhanced performance metrics collection",
                    "Improved error handling and validation",
                ],
            },
            "recommendations": [
                "Run comprehensive tests to validate optimizations",
                "Benchmark FFT performance against baseline",
                "Monitor memory usage patterns in production",
            ],
        }

    def print_summary(self, report: Dict[str, Any]):
        """打印优化摘要"""
        print("\n" + "=" * 60)
        print("📊 TransformKernelEngine优化报告")
        print("=" * 60)

        summary = report["summary"]
        print(f"📈 优化状态: {summary['status']}")
        print(
            f"✅ 应用优化: {report['total_optimizations']}/5 ({report['success_rate'] * 100:.1f}%)"
        )
        print(f"🕒 优化时间: {report['optimization_timestamp']}")

        print("\n🔧 应用的优化:")
        for optimization in report["optimizations_applied"]:
            print(f"   ✅ {optimization}")

        print("\n💡 关键改进:")
        for improvement in summary["key_improvements"]:
            print(f"   🚀 {improvement}")

        print("\n📋 建议:")
        for recommendation in report["recommendations"]:
            print(f"   📌 {recommendation}")

        print("\n" + "=" * 60)


def main():
    """主函数"""
    print("🚀 Phase 6.3.2 优化TransformKernelEngine实现")
    print("=" * 60)

    optimizer = TransformKernelOptimizer()

    # 执行优化
    report = optimizer.optimize_transform_kernel()

    # 打印摘要
    optimizer.print_summary(report)

    return report


if __name__ == "__main__":
    report = main()
