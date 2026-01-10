#!/usr/bin/env python3
"""
GPU性能优化管理器测试套件
测试GPU集成到MyStocks主系统的完整功能

作者: MyStocks AI开发团队
创建日期: 2025-11-16
版本: 1.0.0
依赖: pytest, src.monitoring.gpu_performance_optimizer
注意事项: 这是MyStocks v3.0 GPU系统测试模块
版权: MyStocks Project © 2025
"""

import asyncio
import pytest
import logging
from datetime import datetime
import os
import sys

# Add project root to path
sys.path.insert(0, os.getcwd())

# 导入待测试的模块
from src.monitoring.gpu_performance_optimizer import (
    GPUPerformanceOptimizer,
    GPUOptimizationConfig,
    GPUMetrics,
    OptimizationResult,
    initialize_gpu_optimizer,
)

from src.monitoring.gpu_integration_manager import (
    GPUOptimizationConfig as IntegrationGPUConfig,
    initialize_gpu_integration,
    get_gpu_integration_status,
    run_gpu_optimization,
    get_gpu_performance_report,
    get_gpu_health,
    optimize_gpu_memory,
)


# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestGPUPerformanceOptimizer:
    """GPU性能优化管理器测试"""

    @pytest.fixture
    def gpu_config(self):
        """创建测试配置"""
        return GPUOptimizationConfig(
            auto_optimize=True,
            optimization_interval=30,  # 30秒用于测试
            performance_threshold=0.5,
            memory_optimization=True,
            adaptive_batch_size=True,
            cpu_gpu_balance=False,  # 测试时禁用CPU-GPU平衡
            enable_performance_alerts=False,  # 测试时禁用告警
        )

    @pytest.fixture
    async def gpu_optimizer(self, gpu_config):
        """创建GPU优化管理器实例"""
        optimizer = await initialize_gpu_optimizer(gpu_config)
        yield optimizer
        # 清理资源
        if hasattr(optimizer, "_monitoring_task"):
            optimizer._monitoring_task.cancel()

    @pytest.mark.asyncio
    async def test_gpu_optimizer_initialization(self, gpu_optimizer):
        """测试GPU优化器初始化"""
        assert gpu_optimizer is not None
        assert gpu_optimizer.config is not None
        assert gpu_optimizer.gpu_available is not None  # 可能是False（无GPU硬件）
        assert gpu_optimizer.metrics_history == []
        assert gpu_optimizer.optimization_history == []

    @pytest.mark.asyncio
    async def test_gpu_metrics_collection(self, gpu_optimizer):
        """测试GPU指标收集"""
        metrics = await gpu_optimizer._collect_gpu_metrics()

        assert isinstance(metrics, GPUMetrics)
        assert isinstance(metrics.timestamp, datetime)
        assert 0 <= metrics.gpu_utilization <= 100
        assert 0 <= metrics.gpu_memory_utilization <= 100
        assert 0 <= metrics.gpu_temperature
        assert 0 <= metrics.efficiency_score <= 1

    @pytest.mark.asyncio
    async def test_performance_optimization(self, gpu_optimizer):
        """测试性能优化"""
        result = await gpu_optimizer.optimize_performance()

        assert isinstance(result, OptimizationResult)
        assert result.timestamp is not None
        assert isinstance(result.before_metrics, GPUMetrics)
        assert isinstance(result.after_metrics, GPUMetrics)
        assert isinstance(result.applied_actions, list)
        assert isinstance(result.success, bool)
        assert isinstance(result.improvement_score, float)

    @pytest.mark.asyncio
    async def test_memory_optimization(self, gpu_optimizer):
        """测试内存优化"""
        # 测试内存优化操作
        action = await gpu_optimizer._optimize_memory()

        # action可能是None（无需优化）或字符串（执行的操作）
        assert action is None or isinstance(action, str)

    @pytest.mark.asyncio
    async def test_batch_size_optimization(self, gpu_optimizer):
        """测试批次大小优化"""
        # 创建测试指标
        test_metrics = GPUMetrics(
            timestamp=datetime.now(),
            gpu_utilization=40.0,  # 低利用率
            gpu_memory_used=4000.0,
            gpu_memory_total=8192.0,
            gpu_memory_utilization=50.0,
            gpu_temperature=65.0,
            gpu_power_usage=120.0,
            gpu_fan_speed=2500.0,
            cuda_memory_pool_used=1000.0,
            cuda_memory_pool_total=2000.0,
            processing_time=0.0,
            throughput=1000.0,
            efficiency_score=0.8,
        )

        # 测试批次优化
        action = await gpu_optimizer._optimize_batch_size(test_metrics)

        # 验证自适应参数被更新
        original_batch = gpu_optimizer.adaptive_params["current_batch_size"]
        assert isinstance(original_batch, int)
        assert original_batch >= gpu_optimizer.config.min_batch_size
        assert original_batch <= gpu_optimizer.config.max_batch_size

    @pytest.mark.asyncio
    async def test_performance_report_generation(self, gpu_optimizer):
        """测试性能报告生成"""
        # 先生成一些测试数据
        await gpu_optimizer.optimize_performance()

        report = await gpu_optimizer.get_performance_report()

        assert isinstance(report, dict)
        assert "timestamp" in report
        assert "gpu_available" in report
        assert "current_metrics" in report
        assert "optimization_stats" in report
        assert "adaptive_params" in report
        assert "recommendations" in report

    @pytest.mark.asyncio
    async def test_efficiency_score_calculation(self, gpu_optimizer):
        """测试效率评分计算"""
        # 测试不同场景下的效率评分
        test_cases = [
            (80, 70, 1000, 2000, 0.8),  # 正常情况
            (95, 95, 1500, 2000, 0.6),  # 高利用率
            (20, 30, 500, 2000, 0.5),  # 低利用率
        ]

        for gpu_util, memory_util, pool_used, pool_total, expected_range in test_cases:
            score = gpu_optimizer._calculate_efficiency_score(gpu_util, memory_util, pool_used, pool_total)
            assert 0 <= score <= 1, f"效率评分应在0-1范围内，得到: {score}"

    @pytest.mark.asyncio
    async def test_state_save_and_load(self, gpu_optimizer, tmp_path):
        """测试状态保存和加载"""
        # 创建临时文件
        state_file = tmp_path / "test_gpu_state.json"

        # 执行一些操作
        await gpu_optimizer.optimize_performance()

        # 保存状态
        gpu_optimizer.save_optimization_state(str(state_file))
        assert state_file.exists()

        # 创建新的优化器实例
        new_optimizer = GPUPerformanceOptimizer()

        # 加载状态
        new_optimizer.load_optimization_state(str(state_file))

        # 验证状态已恢复
        assert new_optimizer.config.auto_optimize == gpu_optimizer.config.auto_optimize
        assert len(new_optimizer.metrics_history) > 0

    @pytest.mark.asyncio
    async def test_continuous_optimization(self, gpu_optimizer):
        """测试连续优化"""
        # 启动连续优化，但只运行很短时间
        optimization_task = asyncio.create_task(
            gpu_optimizer.start_continuous_optimization(duration_minutes=0.5)  # 30秒
        )

        # 等待一段时间
        await asyncio.sleep(5)

        # 取消任务
        optimization_task.cancel()

        try:
            await optimization_task
        except asyncio.CancelledError:
            pass  # 预期的取消异常

        # 验证应该有历史记录
        assert len(gpu_optimizer.metrics_history) > 0

    @pytest.mark.asyncio
    async def test_gpu_health_recommendations(self, gpu_optimizer):
        """测试GPU健康建议生成"""
        # 测试不同健康状况的建议
        test_metrics = [
            GPUMetrics(  # 健康状态
                timestamp=datetime.now(),
                gpu_utilization=70.0,
                gpu_memory_used=5000.0,
                gpu_memory_total=8192.0,
                gpu_memory_utilization=60.0,
                gpu_temperature=70.0,
                gpu_power_usage=150.0,
                gpu_fan_speed=2500.0,
                cuda_memory_pool_used=1000.0,
                cuda_memory_pool_total=2000.0,
                processing_time=1.0,
                throughput=1000.0,
                efficiency_score=0.85,
            ),
            GPUMetrics(  # 问题状态
                timestamp=datetime.now(),
                gpu_utilization=95.0,
                gpu_memory_used=7800.0,
                gpu_memory_total=8192.0,
                gpu_memory_utilization=95.0,
                gpu_temperature=90.0,
                gpu_power_usage=250.0,
                gpu_fan_speed=4000.0,
                cuda_memory_pool_used=1900.0,
                cuda_memory_pool_total=2000.0,
                processing_time=2.0,
                throughput=500.0,
                efficiency_score=0.3,
            ),
        ]

        for metrics in test_metrics:
            recommendations = await gpu_optimizer._generate_performance_recommendations(metrics)
            assert isinstance(recommendations, list)
            assert len(recommendations) > 0

            # 健康状况应该有相应的建议
            if metrics.gpu_utilization > 90:
                assert any("满载" in rec or "高" in rec for rec in recommendations)
            if metrics.gpu_temperature > 85:
                assert any("温度" in rec for rec in recommendations)


class TestGPUIntegrationManager:
    """GPU集成管理器测试"""

    @pytest.fixture
    def integration_config(self):
        """创建集成测试配置"""
        return IntegrationGPUConfig(
            auto_optimize=True,
            optimization_interval=30,
            memory_optimization=True,
            adaptive_batch_size=True,
        )

    @pytest.fixture
    async def gpu_integration(self, integration_config):
        """创建GPU集成管理器实例"""
        integration = await initialize_gpu_integration(gpu_config=integration_config)
        yield integration
        # 清理资源
        await integration.shutdown_integration()

    @pytest.mark.asyncio
    async def test_integration_initialization(self, gpu_integration):
        """测试集成初始化"""
        assert gpu_integration is not None
        assert gpu_integration.gpu_config is not None
        assert gpu_integration.integration_status is not None

    @pytest.mark.asyncio
    async def test_manual_optimization(self, gpu_integration):
        """测试手动优化"""
        result = await gpu_integration.run_manual_optimization()

        assert isinstance(result, dict)
        assert "success" in result
        assert "improvement_score" in result
        assert "recommendation" in result
        assert "applied_actions" in result

    @pytest.mark.asyncio
    async def test_performance_report(self, gpu_integration):
        """测试性能报告"""
        report = await gpu_integration.get_performance_report()

        assert isinstance(report, dict)
        if "error" not in report:
            assert "integration_status" in report
            assert "gpu_usage_stats" in report
            assert "current_metrics" in report

    @pytest.mark.asyncio
    async def test_gpu_health_status(self, gpu_integration):
        """测试GPU健康状态"""
        health = await gpu_integration.get_gpu_health_status()

        assert isinstance(health, dict)
        assert "available" in health
        assert "healthy" in health
        assert "health_score" in health
        assert "issues" in health
        assert "metrics" in health

    @pytest.mark.asyncio
    async def test_memory_optimization(self, gpu_integration):
        """测试内存优化"""
        result = await gpu_integration.optimize_gpu_memory()

        assert isinstance(result, dict)
        assert "success" in result
        assert "action" in result or "message" in result

    @pytest.mark.asyncio
    async def test_integration_status(self, gpu_integration):
        """测试集成状态"""
        status = gpu_integration.get_integration_status()

        assert isinstance(status, dict)
        assert "integration_timestamp" in status
        assert "gpu_optimizer_initialized" in status
        assert "unified_manager_enhanced" in status
        assert "monitoring_integrated" in status

    @pytest.mark.asyncio
    async def test_convenience_functions(self):
        """测试便捷函数"""
        # 测试便捷函数
        status = await get_gpu_integration_status()
        assert isinstance(status, dict)

        optimization_result = await run_gpu_optimization()
        assert isinstance(optimization_result, dict)

        report = await get_gpu_performance_report()
        assert isinstance(report, dict)

        health = await get_gpu_health()
        assert isinstance(health, dict)

        memory_result = await optimize_gpu_memory()
        assert isinstance(memory_result, dict)


class TestGPUIntegrationScenarios:
    """GPU集成场景测试"""

    @pytest.mark.asyncio
    async def test_full_integration_workflow(self):
        """测试完整集成工作流"""
        # 1. 创建配置
        config = GPUOptimizationConfig(
            auto_optimize=True,
            optimization_interval=60,
            memory_optimization=True,
            adaptive_batch_size=True,
        )

        # 2. 初始化集成
        integration = await initialize_gpu_integration(gpu_config=config)

        # 3. 检查初始状态
        initial_status = await get_gpu_integration_status()
        assert initial_status["gpu_optimizer_initialized"] in [True, False]

        # 4. 运行优化
        optimization_result = await run_gpu_optimization()
        assert "success" in optimization_result

        # 5. 获取健康状态
        health = await get_gpu_health()
        assert "available" in health

        # 6. 生成报告
        report = await get_gpu_performance_report()
        assert isinstance(report, dict)

        # 7. 关闭集成
        await integration.shutdown_integration()

        # 8. 验证最终状态
        final_status = await get_gpu_integration_status()
        assert final_status["total_optimizations"] >= 1

    @pytest.mark.asyncio
    async def test_error_handling(self):
        """测试错误处理"""
        # 测试在GPU不可用情况下的处理
        config = GPUOptimizationConfig(auto_optimize=False)

        integration = await initialize_gpu_integration(gpu_config=config)

        # 各种操作应该在GPU不可用时仍然正常工作
        try:
            result = await run_gpu_optimization()
            assert isinstance(result, dict)

            health = await get_gpu_health()
            assert isinstance(health, dict)

            await integration.shutdown_integration()

        except Exception as e:
            pytest.fail(f"GPU不可用时的错误处理失败: {e}")

    @pytest.mark.asyncio
    async def test_performance_under_load(self):
        """测试高负载性能"""
        config = GPUOptimizationConfig(
            auto_optimize=True,
            optimization_interval=10,  # 快速优化
            memory_optimization=True,
        )

        integration = await initialize_gpu_integration(gpu_config=config)

        # 连续运行多个优化操作
        optimization_results = []
        for i in range(3):
            result = await run_gpu_optimization()
            optimization_results.append(result)
            await asyncio.sleep(1)  # 短暂间隔

        # 验证所有操作都成功执行
        assert len(optimization_results) == 3
        for result in optimization_results:
            assert "success" in result

        await integration.shutdown_integration()


# 辅助测试函数
def create_test_gpu_metrics(utilization: float = 50.0, memory_util: float = 50.0) -> GPUMetrics:
    """创建测试用的GPU指标"""
    return GPUMetrics(
        timestamp=datetime.now(),
        gpu_utilization=utilization,
        gpu_memory_used=memory_util * 81.92,  # 8192MB * percentage
        gpu_memory_total=8192.0,
        gpu_memory_utilization=memory_util,
        gpu_temperature=70.0 + (utilization - 50) * 0.3,
        gpu_power_usage=120.0 + utilization * 1.0,
        gpu_fan_speed=2500.0 + utilization * 20.0,
        cuda_memory_pool_used=memory_util * 20.0,
        cuda_memory_pool_total=2000.0,
        processing_time=1.0,
        throughput=1000.0,
        efficiency_score=0.8,
    )


# 性能测试
class TestGPUPerformanceBenchmarks:
    """GPU性能基准测试"""

    @pytest.mark.asyncio
    async def test_optimization_performance(self):
        """测试优化性能"""
        config = GPUOptimizationConfig(auto_optimize=False)  # 禁用自动优化
        optimizer = await initialize_gpu_optimizer(config)

        start_time = asyncio.get_event_loop().time()
        result = await optimizer.optimize_performance()
        end_time = asyncio.get_event_loop().time()

        optimization_time = end_time - start_time

        # 优化应该在合理时间内完成（这里设置为10秒阈值）
        assert optimization_time < 10.0, f"优化时间过长: {optimization_time:.2f}秒"
        assert isinstance(result, OptimizationResult)

    @pytest.mark.asyncio
    async def test_metrics_collection_performance(self):
        """测试指标收集性能"""
        config = GPUOptimizationConfig(auto_optimize=False)
        optimizer = await initialize_gpu_optimizer(config)

        # 测试多次指标收集的性能
        collection_times = []
        for _ in range(10):
            start_time = asyncio.get_event_loop().time()
            await optimizer._collect_gpu_metrics()
            end_time = asyncio.get_event_loop().time()
            collection_times.append(end_time - start_time)

        avg_time = sum(collection_times) / len(collection_times)
        max_time = max(collection_times)

        # 平均收集时间应该少于1秒
        assert avg_time < 1.0, f"平均指标收集时间过长: {avg_time:.3f}秒"
        assert max_time < 5.0, f"最大指标收集时间过长: {max_time:.3f}秒"


if __name__ == "__main__":
    # 运行基本测试
    print("🚀 运行GPU性能优化器测试...")

    # 异步测试示例
    async def run_basic_tests():
        # 测试GPU优化器
        config = GPUOptimizationConfig(auto_optimize=False)
        optimizer = await initialize_gpu_optimizer(config)

        print("1. 测试GPU指标收集...")
        metrics = await optimizer._collect_gpu_metrics()
        print(f"   GPU利用率: {metrics.gpu_utilization:.1f}%")
        print(f"   效率评分: {metrics.efficiency_score:.3f}")

        print("2. 测试性能优化...")
        result = await optimizer.optimize_performance()
        print(f"   优化成功: {result.success}")
        print(f"   改进评分: {result.improvement_score:.3f}")

        print("3. 测试集成功能...")
        integration = await initialize_gpu_integration(gpu_config=config)
        status = await get_gpu_integration_status()
        print(f"   集成状态: {status['gpu_optimizer_initialized']}")

        print("4. 测试便捷函数...")
        health = await get_gpu_health()
        print(f"   GPU可用: {health.get('available', False)}")

        await integration.shutdown_integration()
        print("✅ 测试完成")

    # 运行基本测试
    asyncio.run(run_basic_tests())

    print("\n💡 运行pytest获取完整测试套件:")
    print("   pytest tests/test_gpu_performance_optimizer.py -v")
