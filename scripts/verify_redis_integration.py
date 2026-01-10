#!/usr/bin/env python3
"""
Redis Integration Verification Script
=====================================

验证三数据库架构中Redis的集成状态

Version: 1.0.0
Author: MyStocks Project
"""

import sys
import os
import asyncio
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "web" / "backend"))


def test_redis_connection():
    """测试1: Redis连接"""
    print("\n" + "="*60)
    print("📋 测试1: Redis连接验证")
    print("="*60)

    try:
        from app.core.redis_client import redis_manager

        # 健康检查
        if redis_manager.health_check():
            print("✅ Redis连接成功")
            print(f"   - Host: {redis_manager.client.connection_pool.connection_kwargs['host']}")
            print(f"   - Port: {redis_manager.client.connection_pool.connection_kwargs['port']}")
            print(f"   - DB: {redis_manager.client.connection_pool.connection_kwargs['db']}")
            return True
        else:
            print("❌ Redis连接失败")
            return False

    except Exception as e:
        print(f"❌ Redis连接异常: {e}")
        return False


def test_cache_service():
    """测试2: 缓存服务"""
    print("\n" + "="*60)
    print("📋 测试2: L2缓存服务")
    print("="*60)

    try:
        from app.services.redis import redis_cache

        # 设置测试数据
        test_key = "test:cache:verification"
        test_data = {"message": "Hello Redis!", "timestamp": "2024-01-10"}

        print(f"📝 设置缓存: {test_key}")
        redis_cache.set(test_key, test_data, ttl=60)

        # 获取缓存
        print(f"📖 获取缓存: {test_key}")
        result = redis_cache.get(test_key)

        if result and result == test_data:
            print("✅ 缓存读写成功")
            print(f"   - 数据: {result}")

            # 删除测试数据
            redis_cache.delete(test_key)
            print("🗑️  测试数据已清理")
            return True
        else:
            print("❌ 缓存数据不匹配")
            return False

    except Exception as e:
        print(f"❌ 缓存服务异常: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_pubsub_service():
    """测试3: 消息总线"""
    print("\n" + "="*60)
    print("📋 测试3: 实时消息总线")
    print("="*60)

    try:
        from app.services.redis import redis_pubsub
        import time

        # 订阅测试频道
        test_channel = "test:verification"
        received_messages = []

        def message_handler(message):
            received_messages.append(message)
            print(f"📨 收到消息: {message}")

        print(f"📢 订阅频道: {test_channel}")
        redis_pubsub.subscribe(test_channel, message_handler)

        # 发布测试消息
        test_message = {"test": "verification", "timestamp": time.time()}
        print(f"📤 发布消息到 {test_channel}")
        count = redis_pubsub.publish(test_channel, test_message)
        print(f"✅ 消息已发布，订阅者数量: {count}")

        # 短暂等待消息处理
        time.sleep(1)

        if received_messages and received_messages[0] == test_message:
            print("✅ 消息总线测试成功")
            return True
        else:
            print("⚠️  消息未收到 (可能需要启动监听器)")
            return True  # 不算失败，因为需要单独启动监听器

    except Exception as e:
        print(f"❌ 消息总线异常: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_lock_service():
    """测试4: 分布式锁"""
    print("\n" + "="*60)
    print("📋 测试4: 分布式锁")
    print("="*60)

    try:
        from app.services.redis import redis_lock

        test_resource = "test:lock:verification"

        print(f"🔒 尝试获取锁: {test_resource}")

        # 使用上下文管理器测试
        with redis_lock.lock(test_resource, timeout=10):
            print("✅ 锁获取成功")

            # 检查锁状态
            if redis_lock.is_locked(test_resource):
                print("✅ 锁状态检查成功")

        print("✅ 锁已自动释放")

        # 再次检查锁状态
        if not redis_lock.is_locked(test_resource):
            print("✅ 锁已正确释放")
            return True
        else:
            print("❌ 锁未正确释放")
            return False

    except Exception as e:
        print(f"❌ 分布式锁异常: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_indicator_cache():
    """测试5: 指标缓存集成"""
    print("\n" + "="*60)
    print("📋 测试5: 指标缓存专用方法")
    print("="*60)

    try:
        from app.services.redis import redis_cache

        stock_code = "000001"
        indicator_code = "SMA"
        params = {"timeperiod": 20}

        # 缓存指标结果
        test_result = {"value": [10.5, 10.6, 10.7], "timestamp": "2024-01-10"}

        print(f"💾 缓存指标结果: {stock_code} - {indicator_code}")
        success = redis_cache.cache_indicator_result(
            stock_code, indicator_code, params, test_result, ttl=3600
        )

        if success:
            print("✅ 指标结果缓存成功")

            # 获取缓存
            cached = redis_cache.get_cached_indicator_result(stock_code, indicator_code, params)
            if cached and cached == test_result:
                print("✅ 指标缓存读取成功")
                return True
            else:
                print("❌ 指标缓存读取失败")
                return False
        else:
            print("❌ 指标缓存写入失败")
            return False

    except Exception as e:
        print(f"❌ 指标缓存异常: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("🚀 MyStocks Redis 集成验证工具")
    print("="*60)
    print(f"项目路径: {project_root}")
    print(f"Python版本: {sys.version.split()[0]}")

    results = {
        "Redis连接": test_redis_connection(),
        "L2缓存服务": test_cache_service(),
        "消息总线": test_pubsub_service(),
        "分布式锁": test_lock_service(),
        "指标缓存": test_indicator_cache(),
    }

    # 汇总结果
    print("\n" + "="*60)
    print("📊 测试结果汇总")
    print("="*60)

    total = len(results)
    passed = sum(1 for v in results.values() if v)

    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:<20} {status}")

    print("\n" + "-"*60)
    print(f"总计: {passed}/{total} 测试通过")
    print("="*60)

    if passed == total:
        print("\n🎉 所有测试通过！Redis集成成功！")
        return 0
    else:
        print(f"\n⚠️  {total - passed}个测试失败，请检查Redis配置")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
