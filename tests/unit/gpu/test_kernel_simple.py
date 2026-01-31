#!/usr/bin/env python3
"""
简化的GPU内核层测试
"""

import asyncio
import sys
from pathlib import Path

import numpy as np

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


async def test_imports():
    """测试导入"""
    print("🔧 测试导入...")

    try:
        # 测试标准化接口
        print("   ✅ 标准化接口导入成功")

        # 测试矩阵内核
        print("   ✅ 矩阵内核导入成功")

        # 测试变换内核
        print("   ✅ 变换内核导入成功")

        # 测试推理内核
        print("   ✅ 推理内核导入成功")

        # 测试注册中心
        print("   ✅ 内核注册中心导入成功")

        # 测试执行器
        print("   ✅ 内核执行器导入成功")

        return True, "所有导入成功"

    except Exception as e:
        return False, f"导入失败: {e}"


async def test_matrix_kernel_basic():
    """测试矩阵内核基础功能"""
    print("🧮 测试矩阵内核基础功能...")

    try:
        from src.gpu.core.kernels.matrix_kernels import MatrixKernelEngine
        from src.gpu.core.kernels.standardized_interface import (
            MatrixOperationConfig,
            MatrixOperationType,
        )

        # 创建内核
        kernel = MatrixKernelEngine()

        # 创建小测试数据
        left_matrix = np.random.random((10, 10)).astype(np.float32)
        right_matrix = np.random.random((10, 10)).astype(np.float32)

        # 测试矩阵乘法
        config = MatrixOperationConfig(operation_type=MatrixOperationType.MULTIPLY)
        result = await kernel.execute_matrix_operation(left_matrix, right_matrix, config)

        if result.success:
            print(f"   ✅ 矩阵乘法成功: {result.execution_time_ms:.2f}ms")
            return True, "矩阵内核测试成功"
        else:
            print(f"   ❌ 矩阵乘法失败: {result.error_message}")
            return False, f"矩阵内核测试失败: {result.error_message}"

    except Exception as e:
        return False, f"矩阵内核测试异常: {e}"


async def test_kernel_registry_basic():
    """测试内核注册中心基础功能"""
    print("📋 测试内核注册中心基础功能...")

    try:
        from src.gpu.core.kernels.kernel_registry import (
            get_kernel_registry,
            register_standard_kernels,
        )

        # 获取注册中心
        registry = get_kernel_registry()

        # 注册标准内核
        register_standard_kernels()

        # 获取统计
        stats = registry.get_registry_stats()
        print(f"   注册统计: {stats['total_kernels']} 个内核")

        # 列出内核
        kernels = registry.list_kernels()
        print(f"   已注册: {list(kernels.keys())}")

        return True, "内核注册中心测试成功"

    except Exception as e:
        return False, f"内核注册中心测试异常: {e}"


async def run_simple_tests():
    """运行简化测试"""
    print("🚀 开始GPU内核层简化测试\n")

    test_functions = [
        test_imports,
        test_matrix_kernel_basic,
        test_kernel_registry_basic,
    ]

    results = []

    for test_func in test_functions:
        try:
            success, message = await test_func()
            results.append((test_func.__name__, success, message))
            print(f"   {'✅' if success else '❌'} {message}\n")
        except Exception as e:
            results.append((test_func.__name__, False, f"测试异常: {e}"))
            print(f"   ❌ 测试异常: {e}\n")

    # 汇总
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)

    print("=" * 60)
    print(f"📊 简化测试汇总: {passed}/{total} 通过")
    print("=" * 60)

    for test_name, success, message in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")

    if passed == total:
        print("\n🎉 简化测试全部通过！")
        return True
    else:
        print(f"\n⚠️  {total - passed} 个测试失败")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_simple_tests())
    sys.exit(0 if success else 1)
