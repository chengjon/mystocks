#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的内存管理测试
测试核心内存管理功能而不涉及复杂的依赖
"""

import sys
import asyncio

# 设置Python路径
project_root = "/opt/claude/mystocks_spec"
sys.path.insert(0, project_root)


def test_basic_memory_monitoring():
    """测试基本内存监控功能"""
    try:
        # 直接执行内存管理器代码
        exec(open("src/core/memory_manager.py").read())

        print("✅ 基本内存监控测试:")

        # 获取内存统计
        stats = get_memory_stats()
        print(f"   - 当前进程内存: {stats['current']['process_memory_mb']:.2f} MB")
        print(f"   - 系统内存使用率: {stats['current']['system_memory_percent']:.1f}%")
        print(f"   - 活跃对象数: {stats['current']['active_objects']}")
        print(f"   - 总对象数: {stats['current']['total_objects']}")

        # 获取资源管理器统计
        resource_stats = get_resource_manager().get_stats()
        print(f"   - 资源管理器: {resource_stats['total_resources']} 个资源")

        return True

    except Exception as e:
        print(f"❌ 基本内存监控测试失败: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_database_pool_memory():
    """测试数据库池内存管理"""
    try:
        # 先执行内存管理器
        exec(open("src/core/memory_manager.py").read())

        # 执行数据库池配置
        exec(open("src/core/connection_pool_config.py").read())

        print("\n✅ 数据库池内存管理测试:")

        # 获取配置
        config = get_config_for_environment()
        print(f"   - 最小连接数: {config.pool_min_connections}")
        print(f"   - 最大连接数: {config.pool_max_connections}")
        print(f"   - 连接超时: {config.pool_timeout}")

        return True

    except Exception as e:
        print(f"❌ 数据库池内存管理测试失败: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_connection_pool_memory():
    """测试连接池内存功能"""
    try:
        # 先执行内存管理器
        exec(open("src/core/memory_manager.py").read())

        # 执行数据库池
        exec(open("src/core/database_pool.py").read())

        print("\n✅ 连接池内存功能测试:")

        # 创建配置
        from src.core.config import DatabaseConfig

        config = DatabaseConfig()

        # 创建连接池
        pool = DatabaseConnectionPool(config)
        print(f"   - 连接池创建成功: {type(pool)}")

        # 获取初始统计
        stats = pool.get_stats()
        print(f"   - 连接池统计: {stats['active_connections']} 活跃连接")

        # 测试内存分析（如果可用）
        if MEMORY_MANAGEMENT_AVAILABLE:
            analysis = pool.get_memory_analysis()
            if "error" not in analysis:
                print(f"   - 内存分析: {analysis['current_memory_mb']:.2f} MB")
            else:
                print(f"   - 内存分析不可用: {analysis['error']}")

        # 清理
        await pool.close()
        print("   - 连接池已关闭")

        return True

    except Exception as e:
        print(f"❌ 连接池内存功能测试失败: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_resource_manager():
    """测试资源管理器"""
    try:
        # 执行内存管理器
        exec(open("src/core/memory_manager.py").read())

        print("\n✅ 资源管理器测试:")

        # 获取资源管理器
        resource_manager = get_resource_manager()
        print("   - 资源管理器初始化成功")

        # 测试资源注册
        test_resource = {"type": "test", "id": "test_001"}
        resource_manager.register_resource(
            id="test_resource",
            resource=test_resource,
            cleanup_callback=lambda: print("Test resource cleaned up"),
        )

        # 检查资源是否注册
        stats = resource_manager.get_stats()
        print(f"   - 注册资源数: {stats['total_resources']}")

        # 注销资源
        resource_manager.unregister_resource("test_resource")
        stats_after = resource_manager.get_stats()
        print(f"   - 注销后资源数: {stats_after['total_resources']}")

        # 清理所有资源
        resource_manager.cleanup_all()
        final_stats = resource_manager.get_stats()
        print(f"   - 清理后资源数: {final_stats['total_resources']}")

        return True

    except Exception as e:
        print(f"❌ 资源管理器测试失败: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_memory_limits():
    """测试内存限制功能"""
    try:
        # 执行内存管理器
        exec(open("src/core/memory_manager.py").read())

        print("\n✅ 内存限制功能测试:")

        # 创建内存限制
        memory_limit = MemoryLimit(max_memory_mb=512, warning_threshold=0.8)

        # 检查当前内存使用
        current_memory = memory_limit.check_memory_usage()
        print(f"   - 当前内存使用: {current_memory:.2f} MB")

        # 检查是否接近限制
        approaching = memory_limit.is_approaching_limit()
        print(f"   - 接近限制: {approaching}")

        over_limit = memory_limit.is_over_limit()
        print(f"   - 超过限制: {over_limit}")

        # 注册监控回调
        def memory_callback(memory_mb):
            print(f"   - 内存监控回调: {memory_mb:.2f} MB")

        memory_limit.register_monitor(memory_callback)
        memory_limit.notify_monitors(current_memory)

        return True

    except Exception as e:
        print(f"❌ 内存限制功能测试失败: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_concurrent_memory_monitoring():
    """测试并发内存监控"""
    try:
        # 执行内存管理器
        exec(open("src/core/memory_manager.py").read())

        print("\n✅ 并发内存监控测试:")

        # 获取内存监控器
        monitor = get_memory_monitor()
        print(f"   - 内存监控器: {type(monitor)}")

        # 获取当前统计
        current_stats = get_memory_stats()
        print(f"   - 当前统计: {current_stats['current']['process_memory_mb']:.2f} MB")

        # 测试垃圾回收
        import gc

        collected = gc.collect()
        print(f"   - 垃圾回收: {collected} 个对象")

        # 获取回收后统计
        after_gc_stats = get_memory_stats()
        print(f"   - GC后统计: {after_gc_stats['current']['process_memory_mb']:.2f} MB")

        return True

    except Exception as e:
        print(f"❌ 并发内存监控测试失败: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """主测试函数"""
    print("开始简化的内存管理测试...\n")

    # 测试结果汇总
    test_results = []

    # 1. 测试基本内存监控
    print("=" * 50)
    result1 = test_basic_memory_monitoring()
    test_results.append(("基本内存监控", result1))

    # 2. 测试数据库池内存管理
    print("=" * 50)
    result2 = test_database_pool_memory()
    test_results.append(("数据库池内存管理", result2))

    # 3. 测试资源管理器
    print("=" * 50)
    result3 = test_resource_manager()
    test_results.append(("资源管理器", result3))

    # 4. 测试内存限制功能
    print("=" * 50)
    result4 = test_memory_limits()
    test_results.append(("内存限制功能", result4))

    # 5. 测试连接池内存功能
    print("=" * 50)
    result5 = await test_connection_pool_memory()
    test_results.append(("连接池内存功能", result5))

    # 6. 测试并发内存监控
    print("=" * 50)
    result6 = await test_concurrent_memory_monitoring()
    test_results.append(("并发内存监控", result6))

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
        print("🎉 所有简化内存管理测试通过！")
        print("✅ 内存管理核心功能正常工作")
        return True
    else:
        print("❌ 部分测试失败")
        print("需要检查失败的项目")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
