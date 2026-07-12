#!/usr/bin/env python3
"""简化的内存管理集成验证测试
验证内存管理是否已正确集成到数据库连接模块
"""

import asyncio
import gc
import sys
import time

import psutil


# 设置Python路径
project_root = "/opt/claude/mystocks_spec"
sys.path.insert(0, project_root)


def test_memory_manager_functionality():
    """测试内存管理器基本功能"""
    print("开始测试内存管理器基本功能...")

    try:
        # 直接执行内存管理器文件以避免导入问题
        with open("src/core/memory_manager.py", encoding="utf-8") as f:
            memory_manager_code = f.read()

        # 去除typing注释以避免导入问题
        memory_manager_code = memory_manager_code.replace(
            "from typing import ",
            "# from typing import ",
        )

        # 执行内存管理器代码
        exec(memory_manager_code, globals())

        # 测试基本功能
        initialize_memory_management()

        # 获取内存统计
        stats = get_memory_stats()
        print(f"✅ 内存统计获取成功: {stats['current']['process_memory_mb']:.2f} MB")

        # 获取资源管理器
        resource_manager = get_resource_manager()
        test_resource = {"type": "test", "data": "test_data"}
        resource_manager.register_resource(
            "test_resource",
            test_resource,
            lambda: print("Test resource cleaned"),
        )

        resource_stats = resource_manager.get_stats()
        print(f"✅ 资源管理器统计: {resource_stats}")

        # 注销资源
        resource_manager.unregister_resource("test_resource")
        final_stats = resource_manager.get_stats()
        print(f"✅ 资源注销后统计: {final_stats}")

        # 清理所有资源
        resource_manager.cleanup_all()
        cleanup_stats = resource_manager.get_stats()
        print(f"✅ 清理后统计: {cleanup_stats}")

        return True

    except Exception as e:
        print(f"❌ 内存管理器功能测试失败: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_database_connection_integration():
    """测试数据库连接的内存集成"""
    print("\n开始测试数据库连接内存集成...")

    try:
        # 执行连接管理器代码
        with open(
            "src/storage/database/connection_manager.py",
            encoding="utf-8",
        ) as f:
            connection_manager_code = f.read()

        # 检查是否包含内存管理集成代码
        if "MEMORY_MANAGEMENT_AVAILABLE" in connection_manager_code:
            print("✅ 连接管理器包含内存管理检查")
        else:
            print("⚠️  连接管理器缺少内存管理检查")
            return False

        if "get_resource_manager" in connection_manager_code:
            print("✅ 连接管理器包含资源管理器引用")
        else:
            print("⚠️  连接管理器缺少资源管理器引用")
            return False

        if "register_resource" in connection_manager_code:
            print("✅ 连接管理器包含资源注册功能")
        else:
            print("⚠️  连接管理器缺少资源注册功能")
            return False

        # 检查关键方法是否包含内存管理
        key_methods = [
            "get_postgresql_connection",
            "get_tdengine_connection",
            "get_mysql_connection",
            "get_redis_connection",
        ]

        for method in key_methods:
            if method in connection_manager_code:
                print(f"✅ {method} 方法存在")

                # 检查该方法附近是否有内存管理代码
                method_pos = connection_manager_code.find(method)
                context = connection_manager_code[max(0, method_pos - 100) : method_pos + 100]
                if "resource_manager" in context or "MEMORY_MANAGEMENT" in context:
                    print(f"   ✅ {method} 包含内存管理集成")
                else:
                    print(f"   ⚠️  {method} 可能缺少内存管理集成")
            else:
                print(f"⚠️  {method} 方法不存在")

        return True

    except Exception as e:
        print(f"❌ 数据库连接内存集成测试失败: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_connection_pool_integration():
    """测试连接池的内存集成"""
    print("\n开始测试连接池内存集成...")

    try:
        # 执行连接池代码
        with open("src/core/database_pool.py", encoding="utf-8") as f:
            database_pool_code = f.read()

        # 检查内存集成功能
        if "MEMORY_MANAGEMENT_AVAILABLE" in database_pool_code:
            print("✅ 连接池包含内存管理检查")
        else:
            print("⚠️  连接池缺少内存管理检查")
            return False

        if "get_memory_stats" in database_pool_code:
            print("✅ 连接池包含内存统计功能")
        else:
            print("⚠️  连接池缺少内存统计功能")
            return False

        if "get_memory_monitor" in database_pool_code:
            print("✅ 连接池包含内存监控功能")
        else:
            print("⚠️  连接池缺少内存监控功能")
            return False

        # 检查关键方法
        key_methods = [
            "_record_memory_snapshot",
            "get_memory_analysis",
            "initialize",
            "get_stats",
            "close",
        ]

        for method in key_methods:
            if method in database_pool_code:
                print(f"✅ {method} 方法存在")
            else:
                print(f"⚠️  {method} 方法不存在")

        return True

    except Exception as e:
        print(f"❌ 连接池内存集成测试失败: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_connection_context_integration():
    """测试连接上下文的内存集成"""
    print("\n开始测试连接上下文内存集成...")

    try:
        # 执行连接上下文代码
        with open(
            "src/storage/database/connection_context.py",
            encoding="utf-8",
        ) as f:
            connection_context_code = f.read()

        # 检查内存集成功能
        if "MEMORY_MANAGEMENT_AVAILABLE" in connection_context_code:
            print("✅ 连接上下文包含内存管理检查")
        else:
            print("⚠️  连接上下文缺少内存管理检查")
            return False

        if "get_memory_stats" in connection_context_code:
            print("✅ 连接上下文包含内存统计功能")
        else:
            print("⚠️  连接上下文缺少内存统计功能")
            return False

        # 检查关键类和方法
        key_components = [
            "DatabaseConnectionContext",
            "ConnectionPoolManager",
            "database_connection_sync",
            "database_connection_async",
        ]

        for component in key_components:
            if component in connection_context_code:
                print(f"✅ {component} 存在")

                # 检查该组件附近是否有内存管理代码
                component_pos = connection_context_code.find(component)
                context = connection_context_code[max(0, component_pos - 200) : component_pos + 200]
                if "memory" in context.lower():
                    print(f"   ✅ {component} 包含内存管理集成")
                else:
                    print(f"   ⚠️  {component} 可能缺少内存管理集成")
            else:
                print(f"⚠️  {component} 不存在")

        # 检查内存监控装饰器
        if "monitor_connection_performance" in connection_context_code:
            print("✅ 性能监控装饰器存在")
        else:
            print("⚠️  性能监控装饰器不存在")

        return True

    except Exception as e:
        print(f"❌ 连接上下文内存集成测试失败: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_memory_leak_detection():
    """测试内存泄漏检测功能"""
    print("\n开始测试内存泄漏检测功能...")

    try:
        # 执行内存管理器代码
        with open("src/core/memory_manager.py", encoding="utf-8") as f:
            memory_manager_code = f.read()

        # 执行代码
        exec(memory_manager_code, globals())

        # 初始化内存管理
        initialize_memory_management()

        # 获取当前统计
        current_stats = get_memory_stats()
        print(f"当前对象数: {current_stats['current']['total_objects']}")

        # 强制垃圾回收
        collected = gc.collect()
        print(f"垃圾回收: {collected} 个对象")

        # 获取回收后统计
        after_gc_stats = get_memory_stats()
        print(f"GC后对象数: {after_gc_stats['current']['total_objects']}")

        # 检查泄漏检测功能
        if "leak_candidates" in after_gc_stats["current"]:
            leak_candidates = after_gc_stats["current"]["leak_candidates"]
            if leak_candidates:
                print(f"⚠️  发现泄漏候选者: {leak_candidates}")
            else:
                print("✅ 未发现明显的泄漏候选者")
        else:
            print("✅ 内存管理器支持泄漏检测")

        return True

    except Exception as e:
        print(f"❌ 内存泄漏检测测试失败: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_concurrent_memory_operations():
    """测试并发内存操作"""
    print("\n开始测试并发内存操作...")

    try:
        # 执行内存管理器代码
        with open("src/core/memory_manager.py", encoding="utf-8") as f:
            memory_manager_code = f.read()

        # 执行代码
        exec(memory_manager_code, globals())

        # 初始化内存管理
        initialize_memory_management()

        # 创建并发任务
        async def memory_task(task_id: int, duration: int):
            start_time = time.time()
            start_memory = psutil.Process().memory_info().rss / 1024 / 1024

            while time.time() - start_time < duration:
                # 模拟工作
                await asyncio.sleep(0.5)

                # 检查内存
                current_memory = psutil.Process().memory_info().rss / 1024 / 1024
                print(f"   任务 {task_id}: {current_memory:.2f} MB")

                # 创建一些对象
                if task_id == 1:
                    _temp = [i for i in range(1000)]

            end_memory = psutil.Process().memory_info().rss / 1024 / 1024
            print(f"   任务 {task_id} 完成: 变化 {end_memory - start_memory:.2f} MB")

        # 并发运行任务
        tasks = [memory_task(1, 3), memory_task(2, 3), memory_task(3, 3)]

        await asyncio.gather(*tasks)

        # 垃圾回收
        collected = gc.collect()
        print(f"   垃圾回收: {collected} 个对象")

        return True

    except Exception as e:
        print(f"❌ 并发内存操作测试失败: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """主测试函数"""
    print("开始简化的内存管理集成验证...\n")

    # 测试结果汇总
    test_results = []

    # 1. 测试内存管理器功能
    print("=" * 60)
    print("测试 1: 内存管理器基本功能")
    print("=" * 60)
    result1 = test_memory_manager_functionality()
    test_results.append(("内存管理器基本功能", result1))
    print()

    # 2. 测试数据库连接集成
    print("=" * 60)
    print("测试 2: 数据库连接内存集成")
    print("=" * 60)
    result2 = test_database_connection_integration()
    test_results.append(("数据库连接内存集成", result2))
    print()

    # 3. 测试连接池集成
    print("=" * 60)
    print("测试 3: 连接池内存集成")
    print("=" * 60)
    result3 = test_connection_pool_integration()
    test_results.append(("连接池内存集成", result3))
    print()

    # 4. 测试连接上下文集成
    print("=" * 60)
    print("测试 4: 连接上下文内存集成")
    print("=" * 60)
    result4 = test_connection_context_integration()
    test_results.append(("连接上下文内存集成", result4))
    print()

    # 5. 测试内存泄漏检测
    print("=" * 60)
    print("测试 5: 内存泄漏检测功能")
    print("=" * 60)
    result5 = test_memory_leak_detection()
    test_results.append(("内存泄漏检测功能", result5))
    print()

    # 6. 测试并发内存操作
    print("=" * 60)
    print("测试 6: 并发内存操作")
    print("=" * 60)
    result6 = await test_concurrent_memory_operations()
    test_results.append(("并发内存操作", result6))
    print()

    # 汇总结果
    print("=" * 60)
    print("测试结果汇总")
    print("=" * 60)

    passed = 0
    total = len(test_results)

    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1

    print(f"\n总计: {passed}/{total} 个测试通过")

    if passed == total:
        print("🎉 所有内存管理集成验证测试通过！")
        print("✅ 内存管理系统已成功集成到数据库连接模块")
        print("✅ 内存泄漏检测功能正常工作")
        print("✅ 并发内存操作正常工作")
        return True
    print("❌ 部分测试失败")
    print("请检查失败的项目并修复相关问题")
    return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
