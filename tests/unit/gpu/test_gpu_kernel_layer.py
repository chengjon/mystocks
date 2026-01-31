#!/usr/bin/env python3
"""
Phase 6.2.3 计算内核层测试
验证标准化内核接口、矩阵内核、变换内核和推理内核的功能
"""

import asyncio
import logging
import sys
from pathlib import Path

import numpy as np

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 配置日志
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


async def test_kernel_registry():
    """测试内核注册中心"""
    print("🔧 测试内核注册中心...")

    try:
        from src.gpu.core.kernels.kernel_registry import get_kernel_registry

        registry = get_kernel_registry()

        # 获取注册中心统计
        stats = registry.get_registry_stats()
        print(f"   注册中心统计: {stats}")

        # 列出所有内核
        kernels = registry.list_kernels()
        print(f"   已注册内核数量: {len(kernels)}")

        for name, metadata in kernels.items():
            print(f"   - {name}: {metadata.status.value}, 支持 {len(metadata.supported_operations)} 个操作")

        # 测试查找内核
        matrix_kernels = registry.find_kernels_for_operation("matrix")
        print(f"   矩阵内核: {matrix_kernels}")

        transform_kernels = registry.find_kernels_for_operation("transform")
        print(f"   变换内核: {transform_kernels}")

        # 测试最佳内核选择
        best_matrix = registry.get_best_kernel_for_operation("matrix", "multiply", (1000, 1000))
        print(f"   最佳矩阵内核: {best_matrix}")

        return True, "内核注册中心测试通过"

    except Exception as e:
        return False, f"内核注册中心测试失败: {e}"


async def test_matrix_kernels():
    """测试矩阵内核"""
    print("🧮 测试矩阵内核...")

    try:
        from src.gpu.core.kernels.matrix_kernels import MatrixKernelEngine
        from src.gpu.core.kernels.standardized_interface import (
            MatrixOperationConfig,
            MatrixOperationType,
        )

        # 创建矩阵内核引擎
        kernel = MatrixKernelEngine()

        # 初始化
        success = await kernel.initialize()
        print(f"   矩阵内核初始化: {'成功' if success else '失败'}")

        # 创建测试数据
        left_matrix = np.random.random((100, 100)).astype(np.float32)
        right_matrix = np.random.random((100, 100)).astype(np.float32)

        # 测试矩阵乘法
        config = MatrixOperationConfig(operation_type=MatrixOperationType.MULTIPLY)
        result = await kernel.execute_matrix_operation(left_matrix, right_matrix, config)

        if result.success:
            print(f"   矩阵乘法成功: 执行时间 {result.execution_time_ms:.2f}ms")
            print(f"   结果形状: {result.result_data.shape if result.result_data is not None else 'None'}")
            print(f"   内存使用: {result.memory_used_bytes / 1024:.2f}KB")
        else:
            print(f"   矩阵乘法失败: {result.error_message}")

        # 测试转置操作
        config_transpose = MatrixOperationConfig(operation_type=MatrixOperationType.TRANSPOSE)
        result_transpose = await kernel.execute_matrix_operation(left_matrix, config=config_transpose)

        if result_transpose.success:
            print(f"   矩阵转置成功: 执行时间 {result_transpose.execution_time_ms:.2f}ms")

        # 测试批量执行
        operations = [
            (
                "multiply",
                left_matrix,
                right_matrix,
                MatrixOperationConfig(operation_type=MatrixOperationType.MULTIPLY),
            ),
            (
                "transpose",
                left_matrix,
                None,
                MatrixOperationConfig(operation_type=MatrixOperationType.TRANSPOSE),
            ),
        ]

        batch_results = await kernel.batch_execute(operations)
        print(f"   批量执行: {len(batch_results)} 个操作，成功 {sum(1 for r in batch_results if r.success)} 个")

        # 获取性能统计
        stats = kernel.get_performance_stats()
        print(f"   性能统计: {stats}")

        return result.success, f"矩阵内核测试: {'成功' if result.success else '失败'}"

    except Exception as e:
        return False, f"矩阵内核测试失败: {e}"


async def test_transform_kernels():
    """测试变换内核"""
    print("🔄 测试变换内核...")

    try:
        from src.gpu.core.kernels.standardized_interface import (
            TransformConfig,
            TransformOperationType,
        )
        from src.gpu.core.kernels.transform_kernels import TransformKernelEngine

        # 创建变换内核引擎
        kernel = TransformKernelEngine()

        # 初始化
        success = await kernel.initialize()
        print(f"   变换内核初始化: {'成功' if success else '失败'}")

        # 创建测试数据 (模拟股价序列)
        price_data = np.random.random(1000).astype(np.float32) * 100 + 50

        # 测试标准化
        config_normalize = TransformConfig(operation_type=TransformOperationType.NORMALIZE)
        result = await kernel.execute_transform_operation(price_data, config_normalize)

        if result.success:
            print(f"   数据标准化成功: 执行时间 {result.execution_time_ms:.2f}ms")
            if result.result_data is not None:
                normalized_data = result.result_data
                print(f"   标准化后数据范围: [{normalized_data.min():.4f}, {normalized_data.max():.4f}]")
        else:
            print(f"   数据标准化失败: {result.error_message}")

        # 测试滚动平均
        config_ma = TransformConfig(operation_type=TransformOperationType.ROLLING_MEAN, window_size=20)
        result_ma = await kernel.execute_transform_operation(price_data, config_ma)

        if result_ma.success:
            print(f"   滚动平均成功: 执行时间 {result_ma.execution_time_ms:.2f}ms")
            if result_ma.result_data is not None:
                ma_data = result_ma.result_data
                print(f"   滚动平均数据长度: {len(ma_data)}")

        # 测试收益率计算
        config_return = TransformConfig(operation_type=TransformOperationType.RETURN)
        result_return = await kernel.execute_transform_operation(price_data, config_return)

        if result_return.success:
            print(f"   收益率计算成功: 执行时间 {result_return.execution_time_ms:.2f}ms")

        # 获取支持的变换操作
        supported_ops = kernel.get_supported_operations()
        print(f"   支持的变换操作: {supported_ops}")

        return result.success, f"变换内核测试: {'成功' if result.success else '失败'}"

    except Exception as e:
        return False, f"变换内核测试失败: {e}"


async def test_inference_kernels():
    """测试推理内核"""
    print("🤖 测试推理内核...")

    try:
        from src.gpu.core.kernels.inference_kernels import InferenceKernelEngine
        from src.gpu.core.kernels.standardized_interface import (
            InferenceConfig,
            InferenceOperationType,
        )

        # 创建推理内核引擎
        kernel = InferenceKernelEngine()

        # 初始化
        success = await kernel.initialize()
        print(f"   推理内核初始化: {'成功' if success else '失败'}")

        # 创建测试数据 (特征矩阵)
        features = np.random.random((100, 10)).astype(np.float32)  # 100个样本，10个特征
        targets = np.random.random(100).astype(np.float32)  # 100个目标值

        # 测试线性回归
        config_lr = InferenceConfig(
            operation_type=InferenceOperationType.LINEAR_REGRESSION,
            model_params={"regularization": 0.01},
            input_shape=(100, 10),
            batch_size=32,
        )

        # 简化的线性回归测试 (仅验证接口)
        result = await kernel.execute_inference_operation(features, config_lr)

        if result.success:
            print(f"   线性回归接口调用成功: 执行时间 {result.execution_time_ms:.2f}ms")
            if result.result_data is not None:
                predictions = result.result_data
                print(f"   预测结果形状: {predictions.shape}")
        else:
            print(f"   线性回归接口调用失败: {result.error_message}")

        # 测试PCA降维
        config_pca = InferenceConfig(
            operation_type=InferenceOperationType.PCA,
            model_params={"n_components": 5},
            input_shape=(100, 10),
            batch_size=32,
        )

        result_pca = await kernel.execute_inference_operation(features, config_pca)

        if result_pca.success:
            print(f"   PCA降维接口调用成功: 执行时间 {result_pca.execution_time_ms:.2f}ms")
            if result_pca.result_data is not None:
                reduced_data = result_pca.result_data
                print(f"   降维后数据形状: {reduced_data.shape}")

        # 获取支持的推理操作
        supported_ops = kernel.get_supported_operations()
        print(f"   支持的推理操作: {supported_ops}")

        return result.success, f"推理内核测试: {'成功' if result.success else '失败'}"

    except Exception as e:
        return False, f"推理内核测试失败: {e}"


async def test_kernel_executor():
    """测试内核执行器"""
    print("⚡ 测试内核执行器...")

    try:
        from src.gpu.core.kernels.kernel_executor import (
            BatchExecutionConfig,
            ExecutionMode,
            KernelExecutor,
        )
        from src.gpu.core.kernels.standardized_interface import (
            MatrixOperationConfig,
            TransformConfig,
        )

        # 创建内核执行器
        executor = KernelExecutor()

        # 启动队列处理器
        await executor.start_queue_processor()

        # 测试单个执行
        left_matrix = np.random.random((50, 50)).astype(np.float32)
        right_matrix = np.random.random((50, 50)).astype(np.float32)

        result = await executor.execute_matrix_operation(
            "Matrix",
            left_matrix,
            right_matrix,
            MatrixOperationConfig(operation_type=MatrixOperationType.MULTIPLY),
        )

        print(f"   单个矩阵执行: {'成功' if result.success else '失败'}")

        # 测试自动选择内核
        price_data = np.random.random(200).astype(np.float32)
        auto_result = await executor.execute_with_auto_selection(
            operation_type="transform",
            operation_name="normalize",
            data=price_data,
            config=TransformConfig(operation_type=TransformOperationType.NORMALIZE),
        )

        print(f"   自动内核选择: {'成功' if auto_result.success else '失败'}")

        # 测试批量执行
        from src.gpu.core.kernels.standardized_interface import (
            ExecutionContext,
            ExecutionPriority,
        )

        contexts = [
            ExecutionContext(
                kernel_name="Matrix",
                operation_type="matrix",
                data=(
                    np.random.random((20, 20)).astype(np.float32),
                    np.random.random((20, 20)).astype(np.float32),
                ),
                config=MatrixOperationConfig(operation_type=MatrixOperationType.MULTIPLY),
                priority=ExecutionPriority.NORMAL,
            ),
            ExecutionContext(
                kernel_name="Transform",
                operation_type="transform",
                data=np.random.random(100).astype(np.float32),
                config=TransformConfig(operation_type=TransformOperationType.NORMALIZE),
                priority=ExecutionPriority.HIGH,
            ),
        ]

        batch_config = BatchExecutionConfig(max_parallel_jobs=2, enable_fail_fast=False, retry_failed_jobs=True)

        batch_results = await executor.execute_batch(contexts, batch_config, ExecutionMode.PARALLEL)

        success_count = sum(1 for r in batch_results if r.success)
        print(f"   批量执行: {success_count}/{len(batch_results)} 成功")

        # 获取执行统计
        stats = executor.get_execution_stats()
        print(f"   执行器统计: {stats}")

        # 停止队列处理器
        await executor.stop_queue_processor()

        return (
            success_count > 0,
            f"内核执行器测试: {success_count}/{len(batch_results)} 成功",
        )

    except Exception as e:
        return False, f"内核执行器测试失败: {e}"


async def test_integration_workflow():
    """测试集成工作流"""
    print("🔗 测试集成工作流...")

    try:
        from src.gpu.core.kernels.kernel_executor import get_kernel_executor
        from src.gpu.core.kernels.kernel_registry import get_kernel_registry
        from src.gpu.core.kernels.standardized_interface import TransformOperationType

        # 获取注册中心和执行器
        registry = get_kernel_registry()
        executor = get_kernel_executor()

        # 启动执行器
        await executor.start_queue_processor()

        # 创建金融数据处理工作流
        # 1. 生成模拟市场数据
        price_data = np.random.random(500).astype(np.float32) * 50 + 100
        volume_data = np.random.random(500).astype(np.float32) * 1000000

        # 2. 计算价格收益率
        return_result = await executor.execute_with_auto_selection(
            operation_type="transform",
            operation_name="return",
            data=price_data,
            config=TransformConfig(operation_type=TransformOperationType.RETURN),
        )

        # 3. 计算相关性矩阵
        price_volume_matrix = np.column_stack([price_data, volume_data])
        correlation_result = await executor.execute_with_auto_selection(
            operation_type="transform",
            operation_name="correlation",
            data=price_volume_matrix,
            config=TransformConfig(operation_type=TransformOperationType.CORRELATION),
        )

        # 4. 执行矩阵运算
        if correlation_result.success and correlation_result.result_data is not None:
            matrix_result = await executor.execute_with_auto_selection(
                operation_type="matrix",
                operation_name="multiply",
                data=correlation_result.result_data,
                data_shape=correlation_result.result_data.shape,
            )

        # 验证工作流完成
        workflow_success = (
            return_result.success and correlation_result.success and (correlation_result.result_data is not None)
        )

        print(f"   工作流状态: {'成功' if workflow_success else '失败'}")
        print(f"   收益率计算: {'成功' if return_result.success else '失败'}")
        print(f"   相关性计算: {'成功' if correlation_result.success else '失败'}")

        # 获取最终统计
        final_stats = executor.get_execution_stats()
        registry_stats = registry.get_registry_stats()

        print(
            f"   最终执行统计: 总执行 {final_stats['total_executions']} 次，成功率 {final_stats.get('success_rate', 0):.2%}"
        )
        print(f"   注册中心统计: {registry_stats['total_kernels']} 个内核，{registry_stats['active_kernels']} 个活跃")

        # 停止执行器
        await executor.stop_queue_processor()

        return workflow_success, f"集成工作流: {'成功' if workflow_success else '失败'}"

    except Exception as e:
        return False, f"集成工作流测试失败: {e}"


async def run_all_tests():
    """运行所有测试"""
    print("🚀 开始Phase 6.2.3计算内核层测试\n")

    test_functions = [
        test_kernel_registry,
        test_matrix_kernels,
        test_transform_kernels,
        test_inference_kernels,
        test_kernel_executor,
        test_integration_workflow,
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

    # 汇总结果
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)

    print("=" * 60)
    print(f"📊 测试汇总: {passed}/{total} 通过")
    print("=" * 60)

    for test_name, success, message in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")

    if passed == total:
        print("\n🎉 所有测试通过！Phase 6.2.3计算内核层实现完成")
        return True
    else:
        print(f"\n⚠️  {total - passed} 个测试失败，需要检查实现")
        return False


if __name__ == "__main__":
    # 运行测试
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
