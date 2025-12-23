#!/usr/bin/env python3
"""
快速测试优化后的TransformKernelEngine
"""

import asyncio
import numpy as np
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


async def quick_test():
    """快速测试"""
    try:
        print("🧪 快速测试TransformKernelEngine...")

        from src.gpu.core.kernels import TransformKernelEngine
        from src.gpu.core.kernels.standardized_interface import (
            TransformOperationType,
            TransformConfig,
        )

        # 创建引擎
        kernel = TransformKernelEngine()
        await kernel.initialize()
        print("   ✅ 引擎初始化成功")

        # 测试数据
        test_data = np.array([1.0, 2.0, 3.0, 4.0, 5.0], dtype=np.float32)
        print(f"   📊 测试数据: {test_data}")

        # 测试归一化
        config = TransformConfig(operation_type=TransformOperationType.NORMALIZE)
        result = await kernel.execute_transform_operation(test_data, config)

        if result.success:
            print(
                f"   ✅ 归一化成功: {result.result_data} (耗时: {result.execution_time_ms:.3f}ms)"
            )
        else:
            print(f"   ❌ 归一化失败: {result.error_message}")

        # 测试FFT
        fft_config = TransformConfig(operation_type=TransformOperationType.FFT)
        fft_result = await kernel.execute_transform_operation(test_data, fft_config)

        if fft_result.success:
            print(
                f"   ✅ FFT成功: 复数结果长度 {len(fft_result.result_data)} (耗时: {fft_result.execution_time_ms:.3f}ms)"
            )
            print(f"   📈 FFT结果前3个值: {fft_result.result_data[:3]}")
        else:
            print(f"   ❌ FFT失败: {fft_result.error_message}")

        print("   🎉 TransformKernelEngine测试完成!")
        return True

    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(quick_test())
    sys.exit(0 if success else 1)
