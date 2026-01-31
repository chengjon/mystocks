"""
SSE Performance Optimization Test Script

测试SSE性能优化功能的简单脚本
"""

import asyncio
import time
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 模拟导入
try:
    from app.core.sse_manager import get_sse_manager, get_sse_broadcaster, SSEEvent
    from app.core.sse_performance_optimizer import get_performance_optimizer
except ImportError as e:
    logger.error("无法导入SSE模块: %(e)s"")
    print("请确保在正确的目录中运行此脚本")
    exit(1)


async def test_basic_sse_functionality():
    """测试基础SSE功能"""
    logger.info("🧪 开始测试基础SSE功能...")

    try:
        manager = get_sse_manager()
        broadcaster = get_sse_broadcaster()

        # 测试连接
        client_id, queue = await manager.connect("test_channel", "test_client_001")
        logger.info("✅ 客户端连接成功: %(client_id)s"")

        # 测试事件发送
        test_event = SSEEvent(
            event="test_message",
            data={"message": "Hello SSE!", "timestamp": datetime.now().isoformat()},
        )

        await manager.send_to_client("test_channel", client_id, test_event)
        logger.info("✅ 事件发送成功")

        # 测试广播
        await broadcaster.send_dashboard_update("test", {"key": "value"})
        logger.info("✅ 广播发送成功")

        # 清理
        await manager.disconnect("test_channel", client_id)
        logger.info("✅ 客户端断开连接")

        return True

    except Exception as e:
        logger.error("❌ 基础SSE功能测试失败: %(e)s"")
        return False


async def test_performance_optimizer():
    """测试性能优化器功能"""
    logger.info("🚀 开始测试性能优化器功能...")

    try:
        optimizer = get_performance_optimizer()

        # 测试事件优化
        test_event = {
            "event": "test_optimization",
            "data": {"message": "test data", "value": 123},
            "channel": "test",
        }

        optimized = await optimizer.optimize_event(test_event)
        logger.info("✅ 事件优化成功: {type(optimized)}"")

        # 测试批量优化
        batch_events = [test_event] * 10
        optimized_batch = await optimizer.optimize_batch(batch_events)
        logger.info("✅ 批量优化成功: {len(optimized_batch)} 个事件"")

        return True

    except Exception as e:
        logger.error("❌ 性能优化器测试失败: %(e)s"")
        return False


async def test_performance_stats():
    """测试性能统计功能"""
    logger.info("📊 开始测试性能统计功能...")

    try:
        manager = get_sse_manager()

        # 创建一些测试连接
        client_ids = []
        for i in range(3):
            client_id, _ = await manager.connect("stats_test", f"test_client_{i}")
            client_ids.append(client_id)

        # 发送一些测试事件
        broadcaster = get_sse_broadcaster()
        await broadcaster.send_dashboard_update("stats_test", {"test": "data"})

        # 获取性能统计
        stats = manager.get_performance_stats()
        logger.info("✅ 性能统计获取成功: {len(str(stats))} 字符"")

        # 获取连接指标
        metrics = manager.get_connection_metrics()
        logger.info("✅ 连接指标获取成功: {metrics['total_connections']} 个连接"")

        # 获取系统健康状态
        health = manager.get_system_health()
        logger.info("✅ 系统健康状态: {health['status']}"")

        # 清理连接
        for client_id in client_ids:
            await manager.disconnect("stats_test", client_id)

        return True

    except Exception as e:
        logger.error("❌ 性能统计测试失败: %(e)s"")
        return False


async def test_broadcast_optimization():
    """测试优化广播功能"""
    logger.info("📡 开始测试优化广播功能...")

    try:
        manager = get_sse_manager()

        # 创建测试连接
        client_ids = []
        for i in range(5):
            client_id, _ = await manager.connect("broadcast_test", f"client_{i}")
            client_ids.append(client_id)

        # 测试优化广播
        test_data = {
            "event": "optimized_broadcast",
            "data": {"message": "test optimized broadcast", "batch_id": "test_001"},
        }

        sent_count = await manager.broadcast_optimized("broadcast_test", test_data)
        logger.info("✅ 优化广播成功: 发送到 %(sent_count)s 个客户端"")

        # 测试批量广播
        batch_data = [
            {"event": "batch_1", "data": {"value": 1}},
            {"event": "batch_2", "data": {"value": 2}},
            {"event": "batch_3", "data": {"value": 3}},
        ]

        batch_count = await manager.broadcast_batch("broadcast_test", batch_data)
        logger.info("✅ 批量广播成功: 发送 %(batch_count)s 个事件"")

        # 清理连接
        for client_id in client_ids:
            await manager.disconnect("broadcast_test", client_id)

        return True

    except Exception as e:
        logger.error("❌ 优化广播测试失败: %(e)s"")
        return False


async def test_error_handling():
    """测试错误处理"""
    logger.info("🛡️ 开始测试错误处理...")

    try:
        manager = get_sse_manager()

        # 测试无效频道
        health = manager.get_channel_health("invalid_channel")
        logger.info("✅ 无效频道处理: {health['status']}"")

        # 测试无效客户端
        metrics = manager.get_connection_metrics("invalid_client")
        logger.info("✅ 无效客户端处理: {metrics['total_connections']} 个连接"")

        # 测试性能统计错误处理
        # 这里我们直接调用方法，因为它应该有错误处理
        stats = manager.get_performance_stats()
        logger.info("✅ 性能统计错误处理正常")

        return True

    except Exception as e:
        logger.error("❌ 错误处理测试失败: %(e)s"")
        return False


async def main():
    """主测试函数"""
    logger.info("🎯 开始SSE性能优化功能测试")
    logger.info("=" * 50)

    test_results = {}

    # 运行所有测试
    tests = [
        ("基础SSE功能", test_basic_sse_functionality),
        ("性能优化器", test_performance_optimizer),
        ("性能统计", test_performance_stats),
        ("优化广播", test_broadcast_optimization),
        ("错误处理", test_error_handling),
    ]

    for test_name, test_func in tests:
        logger.info("\n🔍 测试: %(test_name)s"")
        start_time = time.time()

        try:
            result = await test_func()
            test_results[test_name] = result

            if result:
                logger.info("✅ %(test_name)s 测试通过 (耗时: {time.time() - start_time:.2f}s)"")
            else:
                logger.error("❌ %(test_name)s 测试失败"")

        except Exception as e:
            logger.error("💥 %(test_name)s 测试异常: %(e)s"")
            test_results[test_name] = False

    # 测试总结
    logger.info("\n" + "=" * 50)
    logger.info("📋 测试总结:")

    passed = 0
    total = len(test_results)

    for test_name, result in test_results.items():
        status = "✅ 通过" if result else "❌ 失败"
        logger.info("  %(test_name)s: %(status)s"")
        if result:
            passed += 1

    success_rate = (passed / total) * 100 if total > 0 else 0
    logger.info("\n📊 总体结果: %(passed)s/%(total)s 测试通过 ({success_rate:.1f}%)"")

    if success_rate >= 80:
        logger.info("🎉 SSE性能优化功能测试基本通过！")
    else:
        logger.warning("⚠️ SSE性能优化功能存在问题，需要进一步检查")


if __name__ == "__main__":
    print("🚀 MyStocks SSE Performance Optimization Test")
    print("=" * 50)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ 测试被用户中断")
    except Exception as e:
        print(f"\n💥 测试运行失败: {e}")
        import traceback

        traceback.print_exc()
