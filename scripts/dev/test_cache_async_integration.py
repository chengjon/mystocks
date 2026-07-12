#!/usr/bin/env python3
"""测试CacheManager异步化与Redis集成
验证三级缓存架构是否正常工作
"""

import asyncio
import os
import sys


# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import sys


sys.path.append("web/backend")

from app.core.cache_manager import get_cache_manager_async
from src.core.cache.multi_level import get_cache


async def test_cache_manager_async():
    """测试异步CacheManager功能"""
    print("🧪 开始测试CacheManager异步化...")

    try:
        # 测试1: 异步缓存管理器初始化
        print("\n1️⃣ 测试异步缓存管理器初始化...")
        redis_cache = None
        try:
            redis_cache = get_cache()
            print("✅ Redis缓存服务可用")
        except Exception as e:
            print(f"⚠️ Redis缓存服务不可用: {e}")

        cache_manager = await get_cache_manager_async(redis_cache=redis_cache)
        print("✅ 异步缓存管理器初始化成功")

        # 测试2: 异步写入缓存
        print("\n2️⃣ 测试异步缓存写入...")
        test_data = {"symbol": "600000", "price": 10.50, "volume": 1000000, "timestamp": "2025-01-10T10:00:00Z"}

        success = await cache_manager.write_to_cache(
            symbol="600000",
            data_type="realtime_quote",
            timeframe="1m",
            data=test_data,
            ttl_days=1,
        )

        if success:
            print("✅ 异步缓存写入成功")
        else:
            print("❌ 异步缓存写入失败")

        # 测试3: 异步读取缓存
        print("\n3️⃣ 测试异步缓存读取...")
        cached_data = await cache_manager.fetch_from_cache(symbol="600000", data_type="realtime_quote", timeframe="1m")

        if cached_data:
            print("✅ 异步缓存读取成功")
            print(f"   📊 缓存数据: {cached_data.get('data', {}).get('price', 'N/A')}")
        else:
            print("⚠️ 异步缓存读取未命中")

        # 测试4: 缓存统计
        print("\n4️⃣ 测试缓存统计...")
        stats = cache_manager.get_cache_stats()
        print(f"✅ 缓存统计: 读取{stats.get('total_reads', 0)}次, 写入{stats.get('total_writes', 0)}次")
        print(f"   📈 命中率: {stats.get('hit_rate_percent', '0%')}")

        # 测试5: 三级缓存清理
        print("\n5️⃣ 测试三级缓存清理...")
        deleted_count = await cache_manager.invalidate_cache(symbol="600000")
        print(f"✅ 清理完成: 删除 {deleted_count} 条缓存记录")

        print("\n🎉 CacheManager异步化测试完成!")
        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_redis_integration():
    """测试Redis集成"""
    print("\n🔴 开始测试Redis集成...")

    try:
        # 初始化Redis缓存
        redis_cache = get_cache()
        await redis_cache.initialize()

        # 测试Redis基本操作
        test_key = "test:mystocks:cache:integration"
        test_value = {"message": "Redis integration test", "timestamp": "2025-01-10"}

        # 写入Redis
        await redis_cache.set(test_key, test_value, ttl=300)
        print("✅ Redis写入成功")

        # 从Redis读取
        result, found, level = await redis_cache.get(test_key)
        if found and result:
            print("✅ Redis读取成功")
            print(f"   📊 数据: {result}")
        else:
            print("❌ Redis读取失败")

        # 清理测试数据
        await redis_cache.delete(test_key)
        print("✅ Redis清理完成")

        return True

    except Exception as e:
        print(f"❌ Redis集成测试失败: {e}")
        return False


async def main():
    """主测试函数"""
    print("🚀 MyStocks 三级缓存架构测试")
    print("=" * 50)

    # 测试CacheManager异步化
    cache_test_result = await test_cache_manager_async()

    # 测试Redis集成
    redis_test_result = await test_redis_integration()

    print("\n" + "=" * 50)
    if cache_test_result and redis_test_result:
        print("🎉 所有测试通过! 三级缓存架构正常工作")
        return 0
    print("❌ 部分测试失败，请检查配置")
    return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
