#!/usr/bin/env python3
"""
GPU硬件抽象层（HAL）实现测试
验证核心组件的功能和集成
"""

import asyncio
import sys
import logging
import time
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 导入HAL组件
from src.gpu.core.hardware_abstraction import (
    GPUResourceManager,
    StrategyPriority,
    PerformanceProfile,
    RealTimeGPUPath,
    DeviceHealthMonitor,
    PerformanceThreshold,
)
from src.gpu.core.hardware_abstraction.memory_pool import MemoryPoolConfig
import numpy as np

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class HALImplementationTest:
    """HAL实现测试类"""

    def __init__(self):
        self.resource_manager = None
        self.realtime_path = None
        self.health_monitor = None
        self.test_results = {}

    async def run_all_tests(self):
        """运行所有测试"""
        logger.info("=" * 60)
        logger.info("Starting GPU HAL Implementation Tests")
        logger.info("=" * 60)

        tests = [
            ("GPU资源管理器初始化", self.test_resource_manager_init),
            ("策略上下文分配", self.test_strategy_context_allocation),
            ("内存池管理", self.test_memory_pool_management),
            ("实时路径预热", self.test_realtime_path_prewarming),
            ("健康监控", self.test_health_monitoring),
            ("性能阈值检查", self.test_performance_thresholds),
            ("集成测试", self.test_integration),
        ]

        passed_tests = 0
        total_tests = len(tests)

        for test_name, test_func in tests:
            logger.info(f"\n--- Running Test: {test_name} ---")
            try:
                start_time = time.time()
                result = await test_func()
                duration = (time.time() - start_time) * 1000

                if result:
                    logger.info(f"✅ {test_name} PASSED ({duration:.1f}ms)")
                    passed_tests += 1
                    self.test_results[test_name] = {
                        "status": "PASSED",
                        "duration_ms": duration,
                    }
                else:
                    logger.error(f"❌ {test_name} FAILED")
                    self.test_results[test_name] = {
                        "status": "FAILED",
                        "duration_ms": duration,
                    }

            except Exception as e:
                logger.error(f"❌ {test_name} ERROR: {e}")
                self.test_results[test_name] = {"status": "ERROR", "error": str(e)}

        # 输出测试结果摘要
        logger.info("\n" + "=" * 60)
        logger.info("Test Results Summary")
        logger.info("=" * 60)
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {total_tests - passed_tests}")
        logger.info(f"Success Rate: {passed_tests / total_tests * 100:.1f}%")

        return passed_tests == total_tests

    async def test_resource_manager_init(self):
        """测试GPU资源管理器初始化"""
        self.resource_manager = GPUResourceManager()
        success = await self.resource_manager.initialize()

        if success:
            devices = self.resource_manager.get_available_devices()
            logger.info(f"Detected {len(devices)} GPU devices")
            for device in devices:
                logger.info(
                    f"  Device {device.device_id}: {device.name} ({device.memory_total}MB)"
                )
        else:
            logger.error("Failed to initialize GPU ResourceManager")

        return success

    async def test_strategy_context_allocation(self):
        """测试策略上下文分配"""
        if not self.resource_manager:
            return False

        # 创建分配请求
        from src.gpu.core.hardware_abstraction.interfaces import AllocationRequest

        request = AllocationRequest(
            strategy_id="test_strategy_001",
            priority=StrategyPriority.HIGH,
            required_memory=512,  # 512MB
            performance_profile=PerformanceProfile(
                max_memory_usage=0.8, latency_target_ms=1.0
            ),
        )

        # 分配策略上下文
        context = await self.resource_manager.allocate_context(request)

        if context:
            logger.info(f"Allocated context for strategy {context.get_strategy_id()}")
            logger.info(f"Device ID: {context.get_device_id()}")

            # 测试性能指标
            metrics = context.get_performance_metrics()
            logger.info(f"Strategy metrics: {metrics}")

            # 清理
            success = await self.resource_manager.release_context("test_strategy_001")
            return success
        else:
            logger.error("Failed to allocate strategy context")
            return False

    async def test_memory_pool_management(self):
        """测试内存池管理"""
        config = MemoryPoolConfig(
            pool_size_mb=1024,  # 1GB
            device_id=0,
            strategy_id="test_memory_strategy",
        )

        from src.gpu.core.hardware_abstraction.memory_pool import MemoryPool

        memory_pool = MemoryPool(config)

        # 测试内存分配
        ptr1 = memory_pool.allocate(1024 * 1024, "test_memory_strategy")  # 1MB
        ptr2 = memory_pool.allocate(512 * 1024, "test_memory_strategy")  # 512KB

        if ptr1 and ptr2:
            logger.info("Memory allocation successful")

            # 获取使用统计
            stats = memory_pool.get_usage_statistics()
            logger.info(f"Memory usage: {stats['usage']['utilization']:.2%}")

            # 测试内存释放
            success1 = memory_pool.deallocate(ptr1, "test_memory_strategy")
            success2 = memory_pool.deallocate(ptr2, "test_memory_strategy")

            if success1 and success2:
                logger.info("Memory deallocation successful")
                memory_pool.cleanup()
                return True

        return False

    async def test_realtime_path_prewarming(self):
        """测试实时路径预热"""
        self.realtime_path = RealTimeGPUPath()

        # 模拟策略上下文
        mock_contexts = []
        for i in range(2):
            # 这里需要创建一个模拟的策略上下文
            # 由于我们没有完整的实现，使用一个简单的模拟
            class MockStrategyContext:
                def get_strategy_id(self):
                    return f"mock_strategy_{i}"

                def get_device_id(self):
                    return 0

            mock_contexts.append(MockStrategyContext())

        # 测试核函数编译
        kernel_results = await self.realtime_path.compile_common_kernels(
            ["matrix_multiply", "feature_transform"]
        )

        if kernel_results.get("matrix_multiply", False):
            logger.info("Kernel compilation successful")

            # 测试内存池分配
            memory_success = await self.realtime_path.allocate_and_lock_memory_pools(
                512
            )
            if memory_success:
                logger.info("Memory pool allocation successful")

                # 测试行情数据加载
                market_data = np.random.random((1000, 10)).astype(np.float32)
                data_success = await self.realtime_path.load_market_data_to_gpu(
                    market_data
                )

                if data_success:
                    logger.info("Market data loading successful")

                    # 获取预热状态
                    status = self.realtime_path.get_prewarm_status()
                    logger.info(f"Prewarm status: {status}")

                    return True

        return False

    async def test_health_monitoring(self):
        """测试健康监控"""
        if not self.resource_manager:
            return False

        self.health_monitor = DeviceHealthMonitor(
            self.resource_manager,
            thresholds=PerformanceThreshold(
                memory_threshold=0.8, compute_threshold=0.85
            ),
        )

        # 获取初始设备健康状态
        summary = self.health_monitor.get_device_health_summary()
        logger.info(f"Health monitor status: {summary['monitoring_active']}")
        logger.info(f"Monitored devices: {summary['monitored_devices']}")

        # 检查性能阈值
        if self.resource_manager.get_available_devices():
            device_id = self.resource_manager.get_available_devices()[0].device_id
            issues = self.health_monitor.check_performance_thresholds(device_id)
            logger.info(f"Performance issues: {issues}")

            return True

        return False

    async def test_performance_thresholds(self):
        """测试性能阈值检查"""
        if not self.resource_manager or not self.health_monitor:
            return False

        # 更新设备指标
        await self.resource_manager.update_device_metrics()

        # 获取资源使用摘要
        summary = self.resource_manager.get_resource_usage_summary()
        logger.info(f"Resource usage summary: {summary}")

        return True

    async def test_integration(self):
        """集成测试"""
        try:
            # 创建完整的HAL组件集成
            if not self.resource_manager:
                return False

            # 分配多个策略上下文
            strategies = []
            for i in range(3):
                from src.gpu.core.hardware_abstraction.interfaces import (
                    AllocationRequest,
                )

                request = AllocationRequest(
                    strategy_id=f"integration_test_strategy_{i}",
                    priority=StrategyPriority.MEDIUM if i < 2 else StrategyPriority.LOW,
                    required_memory=256,
                )

                context = await self.resource_manager.allocate_context(request)
                if context:
                    strategies.append(context)

            if len(strategies) == 3:
                logger.info("Successfully allocated 3 strategy contexts")

                # 测试资源管理摘要
                summary = self.resource_manager.get_resource_usage_summary()
                logger.info(f"Active strategies: {summary['active_strategies']}")

                # 清理所有策略
                for context in strategies:
                    await self.resource_manager.release_context(
                        context.get_strategy_id()
                    )

                logger.info("Successfully cleaned up all strategies")
                return True

        except Exception as e:
            logger.error(f"Integration test error: {e}")
            return False

    async def cleanup(self):
        """清理资源"""
        if self.health_monitor:
            await self.health_monitor.stop_monitoring()

        if self.realtime_path:
            self.realtime_path.clear_prewarm()

        logger.info("HAL test cleanup completed")


async def main():
    """主测试函数"""
    test = HALImplementationTest()

    try:
        success = await test.run_all_tests()

        if success:
            print("\n🎉 All HAL implementation tests PASSED!")
            sys.exit(0)
        else:
            print("\n❌ Some HAL implementation tests FAILED!")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
        sys.exit(1)

    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)

    finally:
        await test.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
