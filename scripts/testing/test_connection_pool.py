"""
连接池测试脚本
测试数据库连接池的功能和性能
"""


import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

import asyncio
import time
import structlog
from src.core.database_pool import DatabaseConnectionPool
from src.core.connection_pool_config import get_config_for_environment
from src.core.config import DatabaseConfig

logger = structlog.get_logger()


async def test_connection_pool_initialization():
    """测试连接池初始化"""
    logger.info("开始测试连接池初始化")

    try:
        # 获取配置
        config = get_config_for_environment()
        config.validate_config()
        logger.info("配置验证通过", config=config.get_pool_config_dict())

        # 创建连接池
        database_config = DatabaseConfig()
        pool = DatabaseConnectionPool(database_config)
        await pool.initialize(
            min_connections=config.pool_min_connections,
            max_connections=config.pool_max_connections,
        )

        logger.info("连接池初始化成功")
        return pool

    except Exception as e:
        logger.error("连接池初始化失败", error=str(e))
        return None


async def test_connection_acquisition(pool: DatabaseConnectionPool):
    """测试连接获取"""
    logger.info("开始测试连接获取")

    try:
        # 测试连接获取
        async with pool.get_connection(timeout=10) as conn:
            logger.info("成功获取连接", connection_id=id(conn))

            # 测试简单查询
            result = await conn.fetch("SELECT 1 as test")
            logger.info("查询执行成功", result=result[0]["test"])

        logger.info("连接成功释放")
        return True

    except Exception as e:
        logger.error("连接获取失败", error=str(e))
        return False


async def test_connection_concurrent(
    pool: DatabaseConnectionPool, concurrent_connections: int = 10
):
    """测试并发连接"""
    logger.info("开始测试并发连接", concurrent_connections=concurrent_connections)

    async def execute_task(task_id: int):
        try:
            async with pool.get_connection(timeout=10) as conn:
                # 执行查询
                result = await conn.fetch("SELECT $1::text as value", f"task_{task_id}")
                time.sleep(0.1)  # 模拟工作
                return task_id, True, result[0]["value"]
        except Exception as e:
            return task_id, False, str(e)

    # 创建并发任务
    tasks = [execute_task(i) for i in range(concurrent_connections)]

    # 执行并发任务
    start_time = time.time()
    results = await asyncio.gather(*tasks, return_exceptions=True)
    end_time = time.time()

    # 分析结果
    successful = 0
    failed = 0
    for result in results:
        if isinstance(result, Exception):
            failed += 1
            logger.error("并发任务失败", error=str(result))
        else:
            task_id, success, value = result
            if success:
                successful += 1
                logger.debug("并发任务成功", task_id=task_id, value=value)
            else:
                failed += 1
                logger.error("并发任务失败", task_id=task_id, error=value)

    duration = end_time - start_time
    logger.info(
        "并发连接测试完成",
        successful=successful,
        failed=failed,
        duration=duration,
        rate=successful / duration if duration > 0 else 0,
    )

    return successful, failed, duration


async def test_query_performance(pool: DatabaseConnectionPool, num_queries: int = 100):
    """测试查询性能"""
    logger.info("开始测试查询性能", num_queries=num_queries)

    async def execute_query(query_num: int):
        try:
            async with pool.get_connection(timeout=5) as conn:
                start_time = time.time()

                # 执行简单查询
                result = await conn.fetch(
                    "SELECT $1::text as value", f"query_{query_num}"
                )

                end_time = time.time()
                return end_time - start_time, True, result[0]["value"]

        except Exception as e:
            return 0, False, str(e)

    # 创建查询任务
    tasks = [execute_query(i) for i in range(num_queries)]

    # 执行查询
    start_time = time.time()
    results = await asyncio.gather(*tasks, return_exceptions=True)
    end_time = time.time()

    # 分析结果
    total_time = 0
    successful = 0
    failed = 0
    query_times = []

    for result in results:
        if isinstance(result, Exception):
            failed += 1
            logger.error("查询失败", error=str(result))
        else:
            query_time, success, value = result
            if success:
                successful += 1
                total_time += query_time
                query_times.append(query_time)
            else:
                failed += 1
                logger.error("查询失败", error=value)

    # 计算统计信息
    avg_time = total_time / successful if successful > 0 else 0
    max_time = max(query_times) if query_times else 0
    min_time = min(query_times) if query_times else 0

    duration = end_time - start_time
    queries_per_second = successful / duration if duration > 0 else 0

    logger.info(
        "查询性能测试完成",
        successful=successful,
        failed=failed,
        total_duration=duration,
        avg_query_time=avg_time,
        max_query_time=max_time,
        min_query_time=min_time,
        queries_per_second=queries_per_second,
    )

    return {
        "successful": successful,
        "failed": failed,
        "total_duration": duration,
        "avg_query_time": avg_time,
        "max_query_time": max_time,
        "min_query_time": min_time,
        "queries_per_second": queries_per_second,
    }


async def test_connection_pool_stress(
    pool: DatabaseConnectionPool, iterations: int = 1000
):
    """测试连接池压力"""
    logger.info("开始测试连接池压力", iterations=iterations)

    async def stress_iteration(iteration: int):
        try:
            async with pool.get_connection(timeout=5) as conn:
                # 执行多个查询
                for i in range(5):
                    await conn.fetch(
                        "SELECT $1::text as value", f"stress_{iteration}_{i}"
                    )
                return iteration, True
        except Exception:
            return iteration, False

    # 执行压力测试
    start_time = time.time()
    results = await asyncio.gather(
        *[stress_iteration(i) for i in range(iterations)], return_exceptions=True
    )
    end_time = time.time()

    # 分析结果
    successful = 0
    failed = 0
    for result in results:
        if isinstance(result, Exception):
            failed += 1
        else:
            iteration, success = result
            if success:
                successful += 1
            else:
                failed += 1

    duration = end_time - start_time
    iterations_per_second = successful / duration if duration > 0 else 0

    logger.info(
        "连接池压力测试完成",
        successful=successful,
        failed=failed,
        duration=duration,
        iterations_per_second=iterations_per_second,
    )

    return successful, failed, duration, iterations_per_second


async def test_connection_health(pool: DatabaseConnectionPool):
    """测试连接健康检查"""
    logger.info("开始测试连接健康检查")

    try:
        # 执行健康检查
        is_healthy = await pool.health_check()
        logger.info("健康检查结果", healthy=is_healthy)

        if is_healthy:
            # 获取池统计信息
            stats = pool.get_stats()
            logger.info("连接池统计信息", stats=stats)
            return True
        else:
            logger.error("健康检查失败")
            return False

    except Exception as e:
        logger.error("健康检查异常", error=str(e))
        return False


async def test_connection_pool_monitoring(pool: DatabaseConnectionPool):
    """测试连接池监控"""
    logger.info("开始测试连接池监控")

    try:
        # 监控连接池
        for i in range(3):
            stats = pool.get_stats()
            logger.info("连接池状态", iteration=i, stats=stats)
            await asyncio.sleep(1)

        return True

    except Exception as e:
        logger.error("连接池监控失败", error=str(e))
        return False


async def cleanup_pool(pool: DatabaseConnectionPool):
    """清理连接池"""
    logger.info("开始清理连接池")

    try:
        await pool.close()
        logger.info("连接池清理完成")
        return True

    except Exception as e:
        logger.error("连接池清理失败", error=str(e))
        return False


async def main():
    """主测试函数"""
    logger.info("开始连接池测试")

    pool = None
    try:
        # 初始化连接池
        pool = await test_connection_pool_initialization()
        if not pool:
            logger.error("连接池初始化失败，测试终止")
            return

        # 测试基本功能
        await test_connection_acquisition(pool)

        # 测试并发连接
        await test_connection_concurrent(pool, concurrent_connections=20)

        # 测试查询性能
        await test_query_performance(pool, num_queries=200)

        # 测试压力
        await test_connection_pool_stress(pool, iterations=100)

        # 测试健康检查
        await test_connection_health(pool)

        # 测试监控
        await test_connection_pool_monitoring(pool)

    except Exception as e:
        logger.error("测试过程中发生错误", error=str(e))

    finally:
        # 清理连接池
        if pool:
            await cleanup_pool(pool)

        logger.info("连接池测试完成")


if __name__ == "__main__":
    # 设置日志
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # 运行测试
    asyncio.run(main())
