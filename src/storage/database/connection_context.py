#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库连接上下文管理器

提供安全的数据库连接管理，确保连接在使用后正确关闭，
并与内存管理系统集成，防止内存泄漏。

创建日期: 2025-12-11
版本: 1.0.0 - 内存管理集成版本
"""

import asyncio
from contextlib import contextmanager
from typing import Any, Dict, Generator, Optional

from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 导入内存管理
try:
    from src.core.memory_manager import get_memory_stats

    MEMORY_MANAGEMENT_AVAILABLE = True
except ImportError:
    MEMORY_MANAGEMENT_AVAILABLE = False

# 导入连接管理器
try:
    from .connection_manager import get_connection_manager

    CONNECTION_MANAGER_AVAILABLE = True
except ImportError:
    CONNECTION_MANAGER_AVAILABLE = False
    get_connection_manager = None


def _normalize_db_type(db_type: str) -> str:
    normalized = db_type.lower()
    if normalized in {"mysql", "mariadb"}:
        raise ValueError("MySQL/MariaDB已移除，请使用PostgreSQL")
    return normalized


class DatabaseConnectionContext:
    """数据库连接上下文管理器"""

    def __init__(self, db_type: str):
        """
        初始化连接上下文

        Args:
            db_type: 数据库类型 (tdengine, postgresql, redis)
        """
        self.db_type = _normalize_db_type(db_type)
        self.connection: Optional[Any] = None
        self.manager = None

    async def __aenter__(self):
        """异步进入上下文"""
        if not CONNECTION_MANAGER_AVAILABLE or get_connection_manager is None:
            raise RuntimeError("连接管理器不可用")

        self.manager = get_connection_manager()

        # 获取连接前的内存统计
        if MEMORY_MANAGEMENT_AVAILABLE:
            memory_before = get_memory_stats()
            print(f"获取{self.db_type}连接前内存使用: {memory_before['current']['process_memory_mb']:.2f} MB")

        # 根据数据库类型获取连接
        if self.db_type == "tdengine":
            self.connection = self.manager.get_tdengine_connection()
        elif self.db_type == "postgresql":
            self.connection = self.manager.get_postgresql_connection()
        elif self.db_type == "redis":
            self.connection = self.manager.get_redis_connection()
        else:
            raise ValueError(f"不支持的数据库类型: {self.db_type}")

        return self.connection

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步退出上下文"""
        # 获取连接后的内存统计
        if MEMORY_MANAGEMENT_AVAILABLE and self.connection:
            memory_after = get_memory_stats()
            print(f"释放{self.db_type}连接后内存使用: {memory_after['current']['process_memory_mb']:.2f} MB")

        # 清理连接
        self._cleanup_connection()

    def _cleanup_connection(self):
        """清理连接"""
        try:
            if self.connection:
                if self.db_type == "tdengine":
                    if hasattr(self.connection, "close"):
                        self.connection.close()
                elif self.db_type == "postgresql":
                    # PostgreSQL连接池不需要手动关闭单个连接
                    pass
                elif self.db_type == "redis":
                    if hasattr(self.connection, "close"):
                        self.connection.close()

                self.connection = None
                print(f"✓ {self.db_type}连接已清理")
        except Exception as e:
            print(f"清理{self.db_type}连接时出错: {e}")

    def get_connection(self):
        """获取连接"""
        return self.connection


@contextmanager
def database_connection_sync(db_type: str) -> Generator[Any, None, None]:
    """
    同步数据库连接上下文管理器

    Args:
        db_type: 数据库类型

    Yields:
        数据库连接对象
    """
    db_type = _normalize_db_type(db_type)
    connection = None
    try:
        if not CONNECTION_MANAGER_AVAILABLE or get_connection_manager is None:
            raise RuntimeError("连接管理器不可用")

        manager = get_connection_manager()

        # 记录内存使用
        if MEMORY_MANAGEMENT_AVAILABLE:
            memory_before = get_memory_stats()
            print(f"同步获取{db_type}连接前内存使用: {memory_before['current']['process_memory_mb']:.2f} MB")

        # 获取连接
        if db_type == "tdengine":
            connection = manager.get_tdengine_connection()
        elif db_type == "postgresql":
            connection = manager.get_postgresql_connection()
        elif db_type == "redis":
            connection = manager.get_redis_connection()
        else:
            raise ValueError(f"不支持的数据库类型: {db_type}")

        yield connection

    finally:
        # 记录内存使用
        if MEMORY_MANAGEMENT_AVAILABLE and connection:
            memory_after = get_memory_stats()
            print(f"同步释放{db_type}连接后内存使用: {memory_after['current']['process_memory_mb']:.2f} MB")

        # 清理连接
        try:
            if connection:
                if db_type == "tdengine" and hasattr(connection, "close"):
                    connection.close()
                elif db_type == "redis" and hasattr(connection, "close"):
                    connection.close()
                print(f"✓ 同步{db_type}连接已清理")
        except Exception as e:
            print(f"清理同步{db_type}连接时出错: {e}")


async def database_connection_async(db_type: str) -> Any:
    """
    异步数据库连接获取函数

    Args:
        db_type: 数据库类型

    Returns:
        数据库连接对象
    """
    if not CONNECTION_MANAGER_AVAILABLE or get_connection_manager is None:
        raise RuntimeError("连接管理器不可用")

    db_type = _normalize_db_type(db_type)
    manager = get_connection_manager()

    # 记录内存使用
    if MEMORY_MANAGEMENT_AVAILABLE:
        memory_before = get_memory_stats()
        print(f"异步获取{db_type}连接前内存使用: {memory_before['current']['process_memory_mb']:.2f} MB")

    # 根据数据库类型获取连接
    if db_type == "tdengine":
        connection = manager.get_tdengine_connection()
    elif db_type == "postgresql":
        connection = manager.get_postgresql_connection()
    elif db_type == "redis":
        connection = manager.get_redis_connection()
    else:
        raise ValueError(f"不支持的数据库类型: {db_type}")

    return connection


class ConnectionPoolManager:
    """连接池管理器 - 优化连接使用"""

    def __init__(self):
        """初始化连接池管理器"""
        self._active_connections = 0
        self._connection_stats = {}

    async def get_connection_with_stats(self, db_type: str) -> Dict[str, Any]:
        """
        获取连接并返回统计信息

        Args:
            db_type: 数据库类型

        Returns:
            包含连接和统计信息的字典
        """
        # 记录获取前的统计
        self._active_connections += 1

        if db_type not in self._connection_stats:
            self._connection_stats[db_type] = {
                "total_requests": 0,
                "active_connections": 0,
                "peak_connections": 0,
                "total_allocated": 0,
            }

        stats = self._connection_stats[db_type]
        stats["total_requests"] += 1
        stats["active_connections"] += 1
        stats["peak_connections"] = max(stats["peak_connections"], stats["active_connections"])

        # 获取连接
        connection = await database_connection_async(db_type)

        # 记录内存使用
        if MEMORY_MANAGEMENT_AVAILABLE:
            memory_stats = get_memory_stats()
            stats["current_memory_mb"] = memory_stats["current"]["process_memory_mb"]
            stats["resource_count"] = memory_stats["resource_manager"]["total_resources"]
        else:
            stats["current_memory_mb"] = 0
            stats["resource_count"] = 0

        stats["total_allocated"] += 1

        return {"connection": connection, "stats": stats, "db_type": db_type}

    async def release_connection(self, db_type: str):
        """释放连接资源"""
        if db_type in self._connection_stats:
            stats = self._connection_stats[db_type]
            stats["active_connections"] = max(0, stats["active_connections"] - 1)

        self._active_connections = max(0, self._active_connections - 1)

        # 记录释放后的内存使用
        if MEMORY_MANAGEMENT_AVAILABLE:
            memory_after = get_memory_stats()
            print(f"释放{db_type}连接后总内存使用: {memory_after['current']['process_memory_mb']:.2f} MB")

    def get_pool_stats(self) -> Dict[str, Any]:
        """获取连接池统计信息"""
        return {
            "active_connections": self._active_connections,
            "db_stats": self._connection_stats.copy(),
        }


# 全局连接池管理器实例
_pool_manager = ConnectionPoolManager()


def get_pool_manager() -> ConnectionPoolManager:
    """获取全局连接池管理器"""
    return _pool_manager


# 性能监控装饰器
def monitor_connection_performance(func):
    """监控连接性能的装饰器"""

    async def wrapper(*args, **kwargs):
        import time

        start_time = time.time()

        try:
            result = await func(*args, **kwargs)

            # 计算执行时间
            execution_time = time.time() - start_time

            # 记录性能指标
            if MEMORY_MANAGEMENT_AVAILABLE:
                memory_stats = get_memory_stats()
                print(
                    f"连接操作性能: 执行时间={execution_time:.3f}s, "
                    f"内存使用={memory_stats['current']['process_memory_mb']:.2f}MB"
                )

            return result

        except Exception as e:
            execution_time = time.time() - start_time
            print(f"连接操作失败: 执行时间={execution_time:.3f}s, 错误={str(e)}")
            raise

    return wrapper


# 使用示例和测试函数
async def test_connection_contexts():
    """测试连接上下文管理器"""
    print("开始测试连接上下文管理器...")

    try:
        # 测试TDengine连接
        async with DatabaseConnectionContext("tdengine") as conn:
            print(f"✓ 获取TDengine连接成功: {type(conn)}")

        # 测试PostgreSQL连接
        async with DatabaseConnectionContext("postgresql") as conn:
            print(f"✓ 获取PostgreSQL连接成功: {type(conn)}")

        # 测试Redis连接
        async with DatabaseConnectionContext("redis") as conn:
            print(f"✓ 获取Redis连接成功: {type(conn)}")

        print("✓ 所有连接上下文测试通过")

    except Exception as e:
        print(f"❌ 连接上下文测试失败: {e}")


def test_sync_connection_context():
    """测试同步连接上下文管理器"""
    print("开始测试同步连接上下文管理器...")

    try:
        # 测试同步PostgreSQL连接
        with database_connection_sync("postgresql") as conn:
            print(f"✓ 同步获取PostgreSQL连接成功: {type(conn)}")

        print("✓ 同步连接上下文测试通过")

    except Exception as e:
        print(f"❌ 同步连接上下文测试失败: {e}")


if __name__ == "__main__":
    """测试连接上下文管理器"""
    import asyncio

    print("开始连接上下文管理器测试...\n")

    # 测试同步上下文
    test_sync_connection_context()
    print()

    # 测试异步上下文
    asyncio.run(test_connection_contexts())
    print()

    # 测试连接池统计
    pool_manager = get_pool_manager()
    stats = pool_manager.get_pool_stats()
    print("连接池统计信息:")
    print(f"  活跃连接数: {stats['active_connections']}")
    for db_type, db_stats in stats["db_stats"].items():
        print(f"  {db_type}: 请求次数={db_stats['total_requests']}, 峰值连接={db_stats['peak_connections']}")

    print("\n✓ 所有测试完成")
