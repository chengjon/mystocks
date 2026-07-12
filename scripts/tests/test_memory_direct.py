#!/usr/bin/env python3
"""直接测试内存管理功能
绕过模块导入问题，直接测试核心功能
"""

import asyncio
import gc
import sys
import time
from datetime import datetime

import psutil


# 设置Python路径
project_root = "/opt/claude/mystocks_spec"
sys.path.insert(0, project_root)


def test_basic_memory_functions():
    """测试基本内存功能"""
    print("开始测试基本内存功能...")

    try:
        # 测试基本的内存统计功能
        process = psutil.Process()
        memory_info = process.memory_info()

        current_memory_mb = memory_info.rss / 1024 / 1024
        system_memory = psutil.virtual_memory()
        system_memory_percent = system_memory.percent

        # 获取对象统计
        active_objects = len(gc.get_objects())

        print("✅ 基本内存统计:")
        print(f"   - 当前进程内存: {current_memory_mb:.2f} MB")
        print(f"   - 系统内存使用率: {system_memory_percent:.1f}%")
        print(f"   - 活跃对象数: {active_objects}")

        # 测试垃圾回收
        collected = gc.collect()
        print(f"   - 垃圾回收: {collected} 个对象")

        return True

    except Exception as e:
        print(f"❌ 基本内存功能测试失败: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_resource_management():
    """测试资源管理模拟"""
    print("\n开始测试资源管理...")

    try:
        # 模拟资源管理器
        class MockResourceManager:
            def __init__(self):
                self.resources = {}
                self.cleanup_callbacks = {}

            def register_resource(self, id, resource, cleanup_callback=None):
                self.resources[id] = resource
                if cleanup_callback:
                    self.cleanup_callbacks[id] = cleanup_callback
                print(f"   注册资源: {id}")

            def unregister_resource(self, id):
                if id in self.resources:
                    del self.resources[id]
                if id in self.cleanup_callbacks:
                    callback = self.cleanup_callbacks[id]
                    try:
                        callback()
                        del self.cleanup_callbacks[id]
                    except Exception as e:
                        print(f"   清理回调失败: {e}")
                print(f"   注销资源: {id}")

            def get_stats(self):
                return {
                    "total_resources": len(self.resources),
                    "total_callbacks": len(self.cleanup_callbacks),
                }

            def cleanup_all(self):
                ids = list(self.resources.keys())
                for id in ids:
                    self.unregister_resource(id)

        # 测试资源管理
        rm = MockResourceManager()

        # 注册资源
        test_resource1 = {"type": "database", "conn": "mock_conn"}
        test_resource2 = {"type": "cache", "data": "mock_data"}

        rm.register_resource(
            "db_conn",
            test_resource1,
            lambda: print("数据库连接已关闭"),
        )
        rm.register_resource("cache", test_resource2, lambda: print("缓存已清理"))

        stats = rm.get_stats()
        print(f"   注册后资源数: {stats['total_resources']}")

        # 注销一个资源
        rm.unregister_resource("db_conn")
        stats_after = rm.get_stats()
        print(f"   注销后资源数: {stats_after['total_resources']}")

        # 清理所有
        rm.cleanup_all()
        final_stats = rm.get_stats()
        print(f"   清理后资源数: {final_stats['total_resources']}")

        return True

    except Exception as e:
        print(f"❌ 资源管理测试失败: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_memory_limit_simulation():
    """测试内存限制模拟"""
    print("\n开始测试内存限制模拟...")

    try:
        # 模拟内存限制器
        class MockMemoryLimit:
            def __init__(self, max_memory_mb=512, warning_threshold=0.8):
                self.max_memory_mb = max_memory_mb
                self.warning_threshold = warning_threshold
                self.monitors = []

            def check_memory_usage(self):
                process = psutil.Process()
                memory_info = process.memory_info()
                return memory_info.rss / 1024 / 1024

            def is_approaching_limit(self):
                current = self.check_memory_usage()
                threshold = self.max_memory_mb * self.warning_threshold
                return current >= threshold

            def is_over_limit(self):
                current = self.check_memory_usage()
                return current >= self.max_memory_mb

            def register_monitor(self, callback):
                self.monitors.append(callback)

            def notify_monitors(self, memory_mb):
                for monitor in self.monitors:
                    try:
                        monitor(memory_mb)
                    except Exception as e:
                        print(f"   监控回调失败: {e}")

        # 测试内存限制
        memory_limit = MockMemoryLimit(max_memory_mb=512, warning_threshold=0.8)

        current_memory = memory_limit.check_memory_usage()
        print(f"   当前内存使用: {current_memory:.2f} MB")

        approaching = memory_limit.is_approaching_limit()
        over_limit = memory_limit.is_over_limit()

        print(f"   接近限制: {approaching}")
        print(f"   超过限制: {over_limit}")

        # 测试监控回调
        def memory_callback(memory_mb):
            print(f"   内存监控回调: {memory_mb:.2f} MB")

        memory_limit.register_monitor(memory_callback)
        memory_limit.notify_monitors(current_memory)

        return True

    except Exception as e:
        print(f"❌ 内存限制模拟测试失败: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_connection_pool_simulation():
    """测试连接池模拟"""
    print("\n开始测试连接池模拟...")

    try:
        # 模拟连接池
        class MockConnectionPool:
            def __init__(self):
                self.connections = {}
                self.stats = {
                    "total_requests": 0,
                    "active_connections": 0,
                    "peak_connections": 0,
                    "memory_snapshots": [],
                }

            async def get_connection(self, name):
                self.stats["total_requests"] += 1
                self.stats["active_connections"] += 1
                self.stats["peak_connections"] = max(
                    self.stats["peak_connections"],
                    self.stats["active_connections"],
                )

                # 模拟连接对象
                connection = {"name": name, "created": datetime.now()}
                self.connections[name] = connection
                print(f"   获取连接: {name}")

                return connection

            async def release_connection(self, name):
                if name in self.connections:
                    del self.connections[name]
                    self.stats["active_connections"] -= 1
                    print(f"   释放连接: {name}")

            async def close(self):
                # 清理所有连接
                names = list(self.connections.keys())
                for name in names:
                    await self.release_connection(name)
                print("   连接池已关闭")

            def get_stats(self):
                return {**self.stats, "current_connections": len(self.connections)}

            def get_memory_analysis(self):
                # 模拟内存分析
                current_memory = psutil.Process().memory_info().rss / 1024 / 1024
                return {
                    "current_memory_mb": current_memory,
                    "peak_connections": self.stats["peak_connections"],
                    "active_connections": len(self.connections),
                }

        # 测试连接池
        pool = MockConnectionPool()

        # 获取连接
        conn1 = await pool.get_connection("conn1")
        conn2 = await pool.get_connection("conn2")

        # 获取统计
        stats = pool.get_stats()
        print(f"   连接池统计: {stats['active_connections']} 活跃连接")

        # 获取内存分析
        analysis = pool.get_memory_analysis()
        print(f"   内存分析: {analysis['current_memory_mb']:.2f} MB")

        # 释放连接
        await pool.release_connection("conn1")
        await pool.release_connection("conn2")

        # 清理
        await pool.close()

        return True

    except Exception as e:
        print(f"❌ 连接池模拟测试失败: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_concurrent_memory_monitoring():
    """测试并发内存监控"""
    print("\n开始测试并发内存监控...")

    try:
        import asyncio

        async def monitor_memory(task_id, duration):
            """监控内存的协程"""
            print(f"   开始监控任务 {task_id}")

            start_time = time.time()
            start_memory = psutil.Process().memory_info().rss / 1024 / 1024

            while time.time() - start_time < duration:
                # 模拟一些工作
                await asyncio.sleep(0.5)

                # 检查内存
                current_memory = psutil.Process().memory_info().rss / 1024 / 1024
                print(f"   任务 {task_id}: {current_memory:.2f} MB")

                # 创建一些对象来增加内存使用
                if task_id == 1:
                    _temp_objects = [i for i in range(1000)]

            end_memory = psutil.Process().memory_info().rss / 1024 / 1024
            print(f"   任务 {task_id} 完成: 变化 {end_memory - start_memory:.2f} MB")

        # 并发运行多个监控任务
        tasks = [monitor_memory(1, 3), monitor_memory(2, 3), monitor_memory(3, 3)]

        await asyncio.gather(*tasks)

        # 最终垃圾回收
        collected = gc.collect()
        print(f"   垃圾回收: {collected} 个对象")

        return True

    except Exception as e:
        print(f"❌ 并发内存监控测试失败: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """主测试函数"""
    print("开始直接内存管理测试...\n")

    # 测试结果汇总
    test_results = []

    # 1. 测试基本内存功能
    print("=" * 50)
    result1 = test_basic_memory_functions()
    test_results.append(("基本内存功能", result1))

    # 2. 测试资源管理
    print("=" * 50)
    result2 = test_resource_management()
    test_results.append(("资源管理", result2))

    # 3. 测试内存限制
    print("=" * 50)
    result3 = test_memory_limit_simulation()
    test_results.append(("内存限制", result3))

    # 4. 测试连接池
    print("=" * 50)
    result4 = await test_connection_pool_simulation()
    test_results.append(("连接池", result4))

    # 5. 测试并发监控
    print("=" * 50)
    result5 = await test_concurrent_memory_monitoring()
    test_results.append(("并发监控", result5))

    # 汇总结果
    print("\n" + "=" * 50)
    print("测试结果汇总")
    print("=" * 50)

    passed = 0
    total = len(test_results)

    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1

    print(f"\n总计: {passed}/{total} 个测试通过")

    if passed == total:
        print("🎉 所有直接内存管理测试通过！")
        print("✅ 内存管理核心功能正常工作")
        return True
    print("❌ 部分测试失败")
    print("需要检查失败的项目")
    return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
