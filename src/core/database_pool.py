"""
数据库连接池管理模块
实现高效的数据库连接管理，提高系统性能
"""

import asyncio
import time
from contextlib import asynccontextmanager
from typing import Dict, Any
import asyncpg
import structlog
from .config import DatabaseConfig
from .exceptions import DatabaseConnectionError, DatabaseOperationError

# 导入内存管理
try:
    from .memory_manager import get_memory_stats

    MEMORY_MANAGEMENT_AVAILABLE = True
except ImportError:
    MEMORY_MANAGEMENT_AVAILABLE = False

logger = structlog.get_logger()


class DatabaseConnectionPool:
    """PostgreSQL连接池管理器"""

    def __init__(self, config: DatabaseConfig):
        """
        初始化连接池

        Args:
            config: 数据库配置
        """
        self.config = config
        self.pool = None
        self._lock = asyncio.Lock()
        self._stats = {
            "total_connections": 0,
            "active_connections": 0,
            "pool_hits": 0,
            "pool_misses": 0,
            "connection_timeouts": 0,
            "total_queries": 0,
            "query_errors": 0,
            "memory_snapshots": [],  # 内存快照记录
        }
        self._connection_times = {}  # 连接时间跟踪

    async def initialize(self, min_connections: int = 5, max_connections: int = 20):
        """
        初始化连接池

        Args:
            min_connections: 最小连接数
            max_connections: 最大连接数
        """
        async with self._lock:
            if self.pool is not None:
                logger.warning("连接池已经初始化")
                return

            try:
                connection_string = self.config.get_postgresql_url()

                # 创建连接池配置
                pool_config = {
                    "min_size": min_connections,
                    "max_size": max_connections,
                    "command_timeout": 60,
                    "server_settings": {
                        "application_name": "MyStocks-API",
                        "timezone": "UTC",
                    },
                }

                # 创建连接池
                self.pool = await asyncpg.create_pool(connection_string, **pool_config)

                self._stats["total_connections"] = max_connections

                # 记录初始化后的内存使用情况
                await self._record_memory_snapshot(
                    "pool_initialized",
                    min_connections=min_connections,
                    max_connections=max_connections,
                )

                logger.info(
                    "数据库连接池初始化成功",
                    min_connections=min_connections,
                    max_connections=max_connections,
                    total_connections=max_connections,
                )

            except Exception as e:
                logger.error("数据库连接池初始化失败", error=str(e))
                raise DatabaseConnectionError(
                    message=f"Failed to initialize connection pool: {str(e)}",
                    code="CONNECTION_POOL_INIT_FAILED",
                    severity="CRITICAL",
                    original_exception=e,
                )

    async def close(self):
        """关闭连接池"""
        async with self._lock:
            if self.pool is not None:
                await self.pool.close()
                self.pool = None

                # 记录关闭后的内存使用情况
                await self._record_memory_snapshot("pool_closed")

                logger.info("数据库连接池已关闭")

    @asynccontextmanager
    async def get_connection(self, timeout: int = 30):
        """
        获取数据库连接

        Args:
            timeout: 连接超时时间（秒）

        Yields:
            asyncpg.Connection: 数据库连接
        """
        if self.pool is None:
            raise DatabaseConnectionError(
                message="Connection pool not initialized",
                code="CONNECTION_POOL_NOT_INITIALIZED",
                severity="CRITICAL",
            )

        connection = None
        connection_id = None
        acquire_time = time.time()

        try:
            # 记录获取连接前的内存使用
            await self._record_memory_snapshot("before_acquire")

            # 从连接池获取连接
            connection = await asyncio.wait_for(self.pool.acquire(), timeout=timeout)

            connection_id = id(connection)
            self._stats["pool_hits"] += 1
            self._stats["active_connections"] += 1
            self._connection_times[connection_id] = acquire_time

            # 记录获取连接后的内存使用
            await self._record_memory_snapshot(
                "after_acquire",
                connection_id=connection_id,
                total_connections=self._stats["active_connections"],
            )

            logger.debug(
                "获取数据库连接成功",
                connection_id=connection_id,
                active_connections=self._stats["active_connections"],
            )

            yield connection

        except asyncio.TimeoutError:
            self._stats["connection_timeouts"] += 1
            logger.error(
                "获取数据库连接超时",
                timeout=timeout,
                active_connections=self._stats["active_connections"],
            )
            raise DatabaseConnectionError(
                message=f"Connection timeout after {timeout} seconds",
                code="CONNECTION_TIMEOUT",
                severity="HIGH",
            )
        except Exception as e:
            self._stats["query_errors"] += 1
            logger.error("获取数据库连接失败", error=str(e))
            raise DatabaseConnectionError(
                message=f"Failed to get connection: {str(e)}",
                code="CONNECTION_ACQUISITION_FAILED",
                severity="HIGH",
                original_exception=e,
            )
        finally:
            if connection is not None:
                # 释放连接回连接池
                await self.pool.release(connection)

                # 计算连接持有时间
                hold_time = 0.0
                if connection_id in self._connection_times:
                    hold_time = time.time() - self._connection_times[connection_id]
                    del self._connection_times[connection_id]

                self._stats["active_connections"] -= 1

                # 记录释放连接后的内存使用
                await self._record_memory_snapshot(
                    "after_release",
                    connection_id=connection_id,
                    hold_time=hold_time,
                    total_connections=self._stats["active_connections"],
                )

                logger.debug(
                    "释放数据库连接",
                    connection_id=connection_id,
                    hold_time=hold_time,
                    active_connections=self._stats["active_connections"],
                )

    async def execute_query(self, query: str, params: tuple = None, timeout: int = 30) -> list:
        """
        执行查询语句

        Args:
            query: SQL查询语句
            params: 查询参数
            timeout: 超时时间

        Returns:
            list: 查询结果
        """
        async with self.get_connection(timeout) as connection:
            try:
                self._stats["total_queries"] += 1

                if params:
                    result = await connection.fetch(query, *params)
                else:
                    result = await connection.fetch(query)

                logger.debug(
                    "查询执行成功",
                    rows=len(result),
                    query=query[:100] + "..." if len(query) > 100 else query,
                )

                return result

            except Exception as e:
                self._stats["query_errors"] += 1
                logger.error(
                    "查询执行失败",
                    query=query[:100] + "..." if len(query) > 100 else query,
                    error=str(e),
                )
                raise DatabaseOperationError(
                    message=f"Query execution failed: {str(e)}",
                    code="QUERY_EXECUTION_FAILED",
                    severity="HIGH",
                    original_exception=e,
                )

    async def execute_command(self, command: str, params: tuple = None, timeout: int = 30) -> str:
        """
        执行命令语句

        Args:
            command: SQL命令语句
            params: 命令参数
            timeout: 超时时间

        Returns:
            str: 命令执行状态
        """
        async with self.get_connection(timeout) as connection:
            try:
                self._stats["total_queries"] += 1

                if params:
                    result = await connection.execute(command, *params)
                else:
                    result = await connection.execute(command)

                logger.debug(
                    "命令执行成功",
                    command=command[:100] + "..." if len(command) > 100 else command,
                )

                return result

            except Exception as e:
                self._stats["query_errors"] += 1
                logger.error(
                    "命令执行失败",
                    command=command[:100] + "..." if len(command) > 100 else command,
                    error=str(e),
                )
                raise DatabaseOperationError(
                    message=f"Command execution failed: {str(e)}",
                    code="COMMAND_EXECUTION_FAILED",
                    severity="HIGH",
                    original_exception=e,
                )

    def get_stats(self) -> Dict[str, Any]:
        """
        获取连接池统计信息

        Returns:
            Dict[str, Any]: 统计信息
        """
        return {
            **self._stats,
            "pool_size": self.pool.get_size() if self.pool else 0,
            "idle_connections": self.pool.get_idle_size() if self.pool else 0,
            "active_connections": self._stats["active_connections"],
            "pool_hit_rate": (
                (self._stats["pool_hits"] / (self._stats["pool_hits"] + self._stats["pool_misses"]))
                if (self._stats["pool_hits"] + self._stats["pool_misses"]) > 0
                else 0
            ),
            "error_rate": (
                (self._stats["query_errors"] / self._stats["total_queries"]) if self._stats["total_queries"] > 0 else 0
            ),
        }

    async def health_check(self) -> bool:
        """
        健康检查

        Returns:
            bool: 是否健康
        """
        try:
            if self.pool is None:
                return False

            # 执行简单的健康检查查询
            await self.execute_query("SELECT 1", timeout=5)
            return True

        except Exception as e:
            logger.error("数据库健康检查失败", error=str(e))
            return False

    async def _record_memory_snapshot(self, event_type: str, **kwargs):
        """记录内存使用快照"""
        if not MEMORY_MANAGEMENT_AVAILABLE:
            return

        try:
            memory_stats = get_memory_stats()
            snapshot = {
                "timestamp": time.time(),
                "event_type": event_type,
                "process_memory_mb": memory_stats["current"]["process_memory_mb"],
                "system_memory_percent": memory_stats["current"]["system_memory_percent"],
                "active_objects": memory_stats["current"]["active_objects"],
                "total_objects": memory_stats["current"]["total_objects"],
                "resource_manager_stats": memory_stats["resource_manager"],
                "connection_pool_stats": self.get_stats(),
                **kwargs,
            }

            self._stats["memory_snapshots"].append(snapshot)

            # 保持快照数量在合理范围内
            if len(self._stats["memory_snapshots"]) > 1000:
                self._stats["memory_snapshots"] = self._stats["memory_snapshots"][-1000:]

            # 记录异常内存使用
            current_memory = snapshot["process_memory_mb"]
            if current_memory > 500:  # 超过500MB警告
                logger.warning(
                    "内存使用量较高",
                    event_type=event_type,
                    memory_mb=current_memory,
                    active_connections=self._stats["active_connections"],
                )

        except Exception as e:
            logger.error("记录内存快照失败", error=str(e))

    def get_memory_analysis(self) -> Dict[str, Any]:
        """获取内存分析报告"""
        if not MEMORY_MANAGEMENT_AVAILABLE:
            return {"error": "Memory management not available"}

        try:
            snapshots = self._stats.get("memory_snapshots", [])
            if not snapshots:
                return {"error": "No memory snapshots available"}

            # 计算内存使用趋势
            memory_values = [s["process_memory_mb"] for s in snapshots]
            avg_memory = sum(memory_values) / len(memory_values)
            max_memory = max(memory_values)
            min_memory = min(memory_values)

            # 计算内存增长率
            if len(snapshots) > 1:
                first_memory = snapshots[0]["process_memory_mb"]
                last_memory = snapshots[-1]["process_memory_mb"]
                memory_growth = ((last_memory - first_memory) / first_memory) * 100 if first_memory > 0 else 0
            else:
                memory_growth = 0

            # 查找内存泄漏模式
            connection_correlation = []
            for snapshot in snapshots:
                correlation = {
                    "active_connections": snapshot.get("connection_pool_stats", {}).get("active_connections", 0),
                    "memory_mb": snapshot["process_memory_mb"],
                    "timestamp": snapshot["timestamp"],
                }
                connection_correlation.append(correlation)

            return {
                "current_memory_mb": memory_values[-1] if memory_values else 0,
                "average_memory_mb": avg_memory,
                "peak_memory_mb": max_memory,
                "minimum_memory_mb": min_memory,
                "memory_growth_percent": memory_growth,
                "total_snapshots": len(snapshots),
                "connection_correlation": connection_correlation,
                "latest_stats": self.get_stats(),
                "leak_indicators": self._detect_memory_leak_indicators(),
            }

        except Exception as e:
            logger.error("内存分析失败", error=str(e))
            return {"error": str(e)}

    def _detect_memory_leak_indicators(self) -> Dict[str, Any]:
        """检测内存泄漏指标"""
        try:
            snapshots = self._stats.get("memory_snapshots", [])
            if len(snapshots) < 10:  # 需要足够的数据点
                return {"error": "Not enough data for leak detection"}

            # 计算内存趋势
            recent_snapshots = snapshots[-50:]  # 最近50个快照
            memory_trend = [s["process_memory_mb"] for s in recent_snapshots]

            # 简单的线性回归计算趋势
            n = len(memory_trend)
            x_values = list(range(n))

            sum_x = sum(x_values)
            sum_y = sum(memory_trend)
            sum_xy = sum(x * y for x, y in zip(x_values, memory_trend))
            sum_x2 = sum(x * x for x in x_values)

            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x) if n > 1 else 0

            # 检测异常
            indicators = {
                "memory_increasing_trend": slope > 0.1,  # 每秒增长超过0.1MB
                "memory_spike_detected": False,
                "connection_leak_suspected": False,
                "recommendation": "Continue monitoring",
            }

            # 检测内存尖峰
            avg_recent = sum(memory_trend) / len(memory_trend)
            max_recent = max(memory_trend)
            if max_recent > avg_recent * 1.5:  # 超过平均值50%
                indicators["memory_spike_detected"] = True

            # 检测连接泄漏
            active_connections = [
                s.get("connection_pool_stats", {}).get("active_connections", 0) for s in recent_snapshots
            ]
            if active_connections and len(active_connections) > 10:
                # 如果连接数减少但内存仍在增加，可能是连接泄漏
                recent_connections = active_connections[-10:]
                decreasing_connections = all(
                    recent_connections[i] >= recent_connections[i + 1] for i in range(len(recent_connections) - 1)
                )

                if decreasing_connections and slope > 0.05:
                    indicators["connection_leak_suspected"] = True
                    indicators["recommendation"] = "Investigate potential connection leak"

            return indicators

        except Exception as e:
            logger.error("内存泄漏检测失败", error=str(e))
            return {"error": str(e)}

    async def cleanup_memory_snapshots(self):
        """清理内存快照数据"""
        self._stats["memory_snapshots"] = []
        logger.info("内存快照数据已清理")


# 全局连接池实例
_connection_pool = None


async def get_connection_pool() -> DatabaseConnectionPool:
    """
    获取全局连接池实例

    Returns:
        DatabaseConnectionPool: 连接池实例
    """
    global _connection_pool

    if _connection_pool is None:
        config = DatabaseConfig()
        _connection_pool = DatabaseConnectionPool(config)
        await _connection_pool.initialize()

    return _connection_pool


async def close_connection_pool():
    """关闭全局连接池"""
    global _connection_pool

    if _connection_pool is not None:
        await _connection_pool.close()
        _connection_pool = None


# 数据库连接管理器
class DatabaseConnectionManager:
    """数据库连接管理器"""

    def __init__(self):
        self.pool = None

    async def initialize(self):
        """初始化连接池"""
        self.pool = await get_connection_pool()

    async def get_connection(self, timeout: int = 30):
        """获取数据库连接"""
        if self.pool is None:
            await self.initialize()
        return self.pool.get_connection(timeout)

    async def execute_query(self, query: str, params: tuple = None, timeout: int = 30):
        """执行查询"""
        if self.pool is None:
            await self.initialize()
        return self.pool.execute_query(query, params, timeout)

    async def execute_command(self, command: str, params: tuple = None, timeout: int = 30):
        """执行命令"""
        if self.pool is None:
            await self.initialize()
        return self.pool.execute_command(command, params, timeout)

    async def get_stats(self):
        """获取统计信息"""
        if self.pool is None:
            await self.initialize()
        return self.pool.get_stats()

    async def health_check(self):
        """健康检查"""
        if self.pool is None:
            await self.initialize()
        return self.pool.health_check()


# 全局连接管理器实例
_connection_manager = DatabaseConnectionManager()


def get_db_manager():
    """获取数据库连接管理器"""
    return _connection_manager
