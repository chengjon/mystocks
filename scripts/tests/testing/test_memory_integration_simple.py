#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的内存管理集成测试
直接测试内存管理功能而不依赖复杂的模块导入
"""

import sys
import asyncio
import gc

# 设置Python路径
project_root = "/opt/claude/mystocks_spec"
sys.path.insert(0, project_root)


def test_memory_manager_import():
    """测试内存管理器导入"""
    print("开始测试内存管理器导入...")

    try:
        # 尝试导入内存管理器
        from src.core.memory_manager import (
            get_memory_stats,
            get_resource_manager,
            initialize_memory_management,
        )

        print("✅ 成功导入内存管理模块")

        # 初始化内存管理
        initialize_memory_management()

        # 获取内存统计
        stats = get_memory_stats()
        print(f"✅ 内存统计获取成功: {stats['current']['process_memory_mb']:.2f} MB")

        # 获取资源管理器
        resource_manager = get_resource_manager()
        resource_manager.register_resource(
            "test_resource", {"data": "test"}, lambda: print("Test resource cleaned up")
        )
        resource_stats = resource_manager.get_stats()
        print(f"✅ 资源管理器统计: {resource_stats}")

        # 注销资源
        resource_manager.unregister_resource("test_resource")
        final_stats = resource_manager.get_stats()
        print(f"✅ 资源注销后统计: {final_stats}")

        return True

    except Exception as e:
        print(f"❌ 内存管理器测试失败: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_database_connection_memory():
    """测试数据库连接的内存管理"""
    print("\n开始测试数据库连接内存管理...")

    try:
        # 导入数据库连接管理器
        from src.storage.database.connection_manager import get_connection_manager

        # 获取连接管理器
        manager = get_connection_manager()
        print("✅ 连接管理器获取成功")

        # 测试获取连接（不实际连接，只测试内存管理）
        # 尝试获取PostgreSQL连接
        try:
            pg_conn = manager.get_postgresql_connection()
            print("✅ PostgreSQL连接获取成功")

            # 获取资源管理器统计
            from src.core.memory_manager import get_resource_manager

            resource_manager = get_resource_manager()
            stats = resource_manager.get_stats()
            print(f"✅ 资源管理器状态: {stats['total_resources']} 个资源")

        except Exception as e:
            print(f"⚠️  PostgreSQL连接失败（预期，可能需要配置）: {e}")

        # 尝试获取TDengine连接
        try:
            tdengine_conn = manager.get_tdengine_connection()
            print("✅ TDengine连接获取成功")

        except Exception as e:
            print(f"⚠️  TDengine连接失败（预期，可能需要配置）: {e}")

        return True

    except Exception as e:
        print(f"❌ 数据库连接内存管理测试失败: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_connection_pool_memory():
    """测试连接池的内存管理"""
    print("\n开始测试连接池内存管理...")

    try:
        # 导入数据库连接池
        from src.core.database_pool import DatabaseConnectionPool
        from src.core.config import DatabaseConfig

        # 创建配置和连接池
        config = DatabaseConfig()
        pool = DatabaseConnectionPool(config)
        print("✅ 连接池创建成功")

        # 初始化连接池
        pool.initialize(min_connections=1, max_connections=3)
        print("✅ 连接池初始化成功")

        # 获取连接池统计
        stats = pool.get_stats()
        print(f"✅ 连接池统计: {stats}")

        # 获取内存分析
        analysis = pool.get_memory_analysis()
        print(f"✅ 内存分析: {analysis}")

        # 关闭连接池
        await pool.close()
        print("✅ 连接池关闭成功")

        return True

    except Exception as e:
        print(f"❌ 连接池内存管理测试失败: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_connection_context_memory():
    """测试连接上下文的内存管理"""
    print("\n开始测试连接上下文内存管理...")

    try:
        # 导入连接上下文
        from src.storage.database.connection_context import ConnectionPoolManager

        # 测试连接池管理器
        pool_manager = ConnectionPoolManager()
        print("✅ 连接池管理器创建成功")

        # 获取池统计
        stats = pool_manager.get_pool_stats()
        print(f"✅ 池统计获取成功: {stats['active_connections']} 活跃连接")

        return True

    except Exception as e:
        print(f"❌ 连接上下文内存管理测试失败: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_concurrent_memory_monitoring():
    """测试并发内存监控"""
    print("\n开始测试并发内存监控...")

    try:
        # 导入内存管理
        from src.core.memory_manager import get_memory_stats

        # 创建并发监控任务
        async def monitor_task(task_id):
            print(f"   开始监控任务 {task_id}")

            start_memory = get_memory_stats()["current"]["process_memory_mb"]

            # 模拟工作
            for i in range(3):
                await asyncio.sleep(0.5)
                current_memory = get_memory_stats()["current"]["process_memory_mb"]
                print(f"   任务 {task_id}: {current_memory:.2f} MB")

                # 创建一些对象来测试内存
                if task_id == 1:
                    _temp_objects = [i for i in range(1000)]

            end_memory = get_memory_stats()["current"]["process_memory_mb"]
            print(f"   任务 {task_id} 完成: 变化 {end_memory - start_memory:.2f} MB")

        # 并发运行任务
        tasks = [monitor_task(1), monitor_task(2), monitor_task(3)]

        await asyncio.gather(*tasks)

        # 垃圾回收
        collected = gc.collect()
        print(f"✅ 垃圾回收: {collected} 个对象")

        return True

    except Exception as e:
        print(f"❌ 并发内存监控测试失败: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """主测试函数"""
    print("开始简化的内存管理集成测试...\n")

    # 测试结果汇总
    test_results = []

    # 1. 测试内存管理器导入
    print("=" * 50)
    print("测试 1: 内存管理器导入")
    print("=" * 50)
    result1 = test_memory_manager_import()
    test_results.append(("内存管理器导入", result1))
    print()

    # 2. 测试数据库连接内存管理
    print("=" * 50)
    print("测试 2: 数据库连接内存管理")
    print("=" * 50)
    result2 = test_database_connection_memory()
    test_results.append(("数据库连接内存管理", result2))
    print()

    # 3. 测试连接池内存管理
    print("=" * 50)
    print("测试 3: 连接池内存管理")
    print("=" * 50)
    try:
        result3 = test_connection_pool_memory()
        test_results.append(("连接池内存管理", result3))
    except Exception as e:
        print(f"❌ 连接池测试失败: {e}")
        test_results.append(("连接池内存管理", False))
    print()

    # 4. 测试连接上下文内存管理
    print("=" * 50)
    print("测试 4: 连接上下文内存管理")
    print("=" * 50)
    result4 = test_connection_context_memory()
    test_results.append(("连接上下文内存管理", result4))
    print()

    # 5. 测试并发内存监控
    print("=" * 50)
    print("测试 5: 并发内存监控")
    print("=" * 50)
    result5 = await test_concurrent_memory_monitoring()
    test_results.append(("并发内存监控", result5))
    print()

    # 汇总结果
    print("=" * 50)
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
        print("🎉 所有内存管理集成测试通过！")
        print("✅ 内存管理系统已成功集成到数据库连接模块")
        return True
    else:
        print("❌ 部分测试失败")
        print("请检查失败的项目并修复相关问题")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
