#!/usr/bin/env python3
"""
测试优化后的MemoryPool
验证内存分配、释放和性能
"""

import asyncio
import sys
import time
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


async def test_memory_pool():
    """测试MemoryPool"""
    try:
        print("🧪 测试MemoryPool...")

        from src.gpu.core.hardware_abstraction.memory_pool import get_memory_pool

        # 获取内存池
        memory_pool = get_memory_pool()
        await memory_pool.initialize()
        print("   ✅ 内存池初始化成功")

        # 测试内存分配
        block_sizes = [1024, 4096, 16384, 65536]  # 1KB, 4KB, 16KB, 64KB
        allocated_blocks = []

        for i, size in enumerate(block_sizes):
            block_id = await memory_pool.allocate(size)
            if block_id:
                allocated_blocks.append(block_id)
                print(f"   ✅ 分配内存块 {i + 1}: {size} bytes -> {block_id}")
            else:
                print(f"   ❌ 分配内存块 {i + 1} 失败")

        # 测试内存指针获取
        for i, block_id in enumerate(allocated_blocks):
            ptr = memory_pool.get_memory_ptr(block_id)
            if ptr is not None:
                print(f"   ✅ 获取内存指针 {i + 1}: 成功")
            else:
                print(f"   ❌ 获取内存指针 {i + 1}: 失败")

        # 测试内存释放
        for i, block_id in enumerate(allocated_blocks):
            success = await memory_pool.deallocate(block_id)
            if success:
                print(f"   ✅ 释放内存块 {i + 1}: 成功")
            else:
                print(f"   ❌ 释放内存块 {i + 1}: 失败")

        # 获取统计信息
        stats = memory_pool.get_stats()
        print("   📊 内存池统计:")
        print(f"      • 总分配次数: {stats['total_allocations']}")
        print(f"      • 总释放次数: {stats['total_deallocations']}")
        print(f"      • 当前内存使用: {stats['current_memory_usage']} bytes")
        print(f"      • 峰值内存使用: {stats['peak_memory_usage']} bytes")
        print(f"      • 池命中率: {stats['pool_efficiency']:.2%}")

        # 测试并发分配
        print("   🔄 测试并发分配...")
        concurrent_tasks = []
        start_time = time.time()

        for i in range(10):
            task = memory_pool.allocate(4096)
            concurrent_tasks.append(task)

        concurrent_block_ids = await asyncio.gather(*concurrent_tasks)
        concurrent_time = (time.time() - start_time) * 1000

        successful_concurrent = sum(1 for bid in concurrent_block_ids if bid is not None)
        print(f"   ✅ 并发分配: {successful_concurrent}/10 成功 (耗时: {concurrent_time:.3f}ms)")

        # 清理并发分配的块
        for block_id in concurrent_block_ids:
            if block_id:
                await memory_pool.deallocate(block_id)

        print("   🎉 MemoryPool测试完成!")
        return True

    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_memory_pool())
    sys.exit(0 if success else 1)
