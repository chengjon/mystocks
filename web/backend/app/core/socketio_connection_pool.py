"""WebSocket连接池管理
WebSocket Connection Pool - Connection Management and Pooling Strategy

Task 14.2: WebSocket性能优化

功能特性:
- 连接池管理（Min/Max连接数配置）
- 连接复用和回收机制
- 连接健康检查和自动恢复
- 内存使用优化
- 并发安全的连接获取/释放
- 性能监控和统计

Author: Claude Code
Date: 2025-11-12
"""

import asyncio
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set

import structlog


logger = structlog.get_logger()


class ConnectionState(str, Enum):
    """连接状态枚举"""

    IDLE = "idle"  # 空闲可用
    ACTIVE = "active"  # 活跃使用中
    STALE = "stale"  # 陈旧需要检查
    BROKEN = "broken"  # 已损坏不可用


@dataclass
class PooledConnection:
    """池化连接元数据"""

    sid: str  # Socket.IO会话ID
    user_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    state: ConnectionState = ConnectionState.IDLE
    activity_count: int = 0
    error_count: int = 0
    reuse_count: int = 0

    def is_stale(self, stale_timeout: int = 300) -> bool:
        """检查连接是否过期（5分钟无活动）"""
        elapsed = (datetime.now(timezone.utc) - self.last_activity).total_seconds()
        return elapsed > stale_timeout

    def is_healthy(self, max_errors: int = 5) -> bool:
        """检查连接是否健康"""
        return self.state != ConnectionState.BROKEN and self.error_count < max_errors

    def record_activity(self) -> None:
        """记录活动"""
        self.last_activity = datetime.now(timezone.utc)
        self.activity_count += 1

    def record_error(self) -> None:
        """记录错误"""
        self.error_count += 1
        if self.error_count >= 5:
            self.state = ConnectionState.BROKEN

    def reset_error_count(self) -> None:
        """重置错误计数"""
        self.error_count = 0
        self.state = ConnectionState.IDLE

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "sid": self.sid,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "state": self.state.value,
            "activity_count": self.activity_count,
            "error_count": self.error_count,
            "reuse_count": self.reuse_count,
        }


class WebSocketConnectionPool:
    """WebSocket连接池管理器"""

    def __init__(
        self,
        min_size: int = 10,
        max_size: int = 1000,
        stale_timeout: int = 300,
        cleanup_interval: int = 60,
    ):
        """初始化连接池

        Args:
            min_size: 最小连接池大小
            max_size: 最大连接池大小
            stale_timeout: 连接陈旧超时（秒）
            cleanup_interval: 清理间隔（秒）

        """
        self.min_size = min_size
        self.max_size = max_size
        self.stale_timeout = stale_timeout
        self.cleanup_interval = cleanup_interval

        # 连接池存储
        self.idle_connections: asyncio.Queue = asyncio.Queue(maxsize=max_size)
        self.active_connections: Dict[str, PooledConnection] = {}
        self.all_connections: Dict[str, PooledConnection] = {}

        # 用户连接映射
        self.user_connections: Dict[str, Set[str]] = {}  # user_id -> set of sids

        # 统计信息
        self.total_acquired = 0
        self.total_released = 0
        self.total_recycled = 0
        self.cleanup_task: Optional[asyncio.Task] = None

        logger.info(
            "✅ WebSocket Connection Pool initialized",
            min_size=min_size,
            max_size=max_size,
            stale_timeout=stale_timeout,
        )

    async def acquire_connection(self, user_id: Optional[str] = None) -> PooledConnection:
        """获取一个连接
        - 优先从空闲队列获取
        - 如果队列空，新建连接
        - 如果达到max_size，等待空闲连接

        Args:
            user_id: 用户ID

        Returns:
            可用的连接

        """
        try:
            # 尝试从空闲队列获取
            try:
                connection = self.idle_connections.get_nowait()
                # 验证连接健康状态
                if connection.is_healthy() and not connection.is_stale(self.stale_timeout):
                    connection.state = ConnectionState.ACTIVE
                    connection.record_activity()
                    connection.reuse_count += 1
                    self.active_connections[connection.sid] = connection
                    self.total_acquired += 1

                    logger.debug(
                        "♻️ Reused connection from pool",
                        sid=connection.sid,
                        reuse_count=connection.reuse_count,
                    )
                    return connection
                # 连接不健康，标记为回收
                logger.warning(
                    "⚠️ Unhealthy connection discarded",
                    sid=connection.sid,
                    healthy=connection.is_healthy(),
                    stale=connection.is_stale(self.stale_timeout),
                )
            except asyncio.QueueEmpty:
                pass

            # 如果现有连接数少于max_size，创建新连接
            if len(self.all_connections) < self.max_size:
                sid = f"conn_{int(time.time() * 1000)}_{len(self.all_connections)}"
                connection = PooledConnection(sid=sid, user_id=user_id)
                connection.state = ConnectionState.ACTIVE
                self.all_connections[sid] = connection
                self.active_connections[sid] = connection
                self.total_acquired += 1

                logger.debug(
                    "🆕 Created new connection",
                    sid=sid,
                    total_connections=len(self.all_connections),
                )
                return connection

            # 达到max_size，等待空闲连接（超时3秒）
            logger.warning(
                "⏳ Connection pool exhausted, waiting for available connection",
                active=len(self.active_connections),
                idle=self.idle_connections.qsize(),
                max_size=self.max_size,
            )
            connection = await asyncio.wait_for(self.idle_connections.get(), timeout=3.0)
            connection.state = ConnectionState.ACTIVE
            connection.record_activity()
            self.active_connections[connection.sid] = connection
            self.total_acquired += 1
            return connection

        except asyncio.TimeoutError:
            logger.error(
                "❌ Failed to acquire connection (timeout)",
                max_size=self.max_size,
                active=len(self.active_connections),
            )
            raise RuntimeError("Connection pool exhausted, no available connections")

    async def release_connection(self, sid: str, error: bool = False) -> None:
        """释放连接回到池中

        Args:
            sid: 连接ID
            error: 是否有错误发生

        """
        connection = self.active_connections.pop(sid, None)
        if not connection:
            logger.warning("⚠️ Attempted to release unknown connection", sid=sid)
            return

        if error:
            connection.record_error()
            logger.warning(
                "⚠️ Connection released with error",
                sid=sid,
                error_count=connection.error_count,
            )

        connection.state = ConnectionState.IDLE

        # 如果连接健康且未超过错误阈值，放回队列
        if connection.is_healthy():
            try:
                self.idle_connections.put_nowait(connection)
                self.total_released += 1
                logger.debug("✅ Connection returned to pool", sid=sid)
            except asyncio.QueueFull:
                # 队列满，移除连接
                self._remove_connection(sid)
        else:
            # 连接不健康，直接移除
            self._remove_connection(sid)

    def _remove_connection(self, sid: str) -> None:
        """移除连接

        Args:
            sid: 连接ID

        """
        connection = self.all_connections.pop(sid, None)
        if connection:
            # 从用户映射中移除
            if connection.user_id and connection.user_id in self.user_connections:
                self.user_connections[connection.user_id].discard(sid)
                if not self.user_connections[connection.user_id]:
                    del self.user_connections[connection.user_id]

            self.total_recycled += 1
            logger.debug(
                "🗑️ Connection removed from pool",
                sid=sid,
                total_connections=len(self.all_connections),
            )

    def register_connection(self, sid: str, user_id: Optional[str] = None) -> None:
        """注册新连接到池中

        Args:
            sid: 连接ID
            user_id: 用户ID

        """
        connection = PooledConnection(sid=sid, user_id=user_id)
        self.all_connections[sid] = connection
        self.idle_connections.put_nowait(connection)

        # 记录用户连接映射
        if user_id:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = set()
            self.user_connections[user_id].add(sid)

        logger.debug(
            "📝 Connection registered in pool",
            sid=sid,
            user_id=user_id,
            total_connections=len(self.all_connections),
        )

    def get_user_connections(self, user_id: str) -> List[PooledConnection]:
        """获取用户的所有连接

        Args:
            user_id: 用户ID

        Returns:
            连接列表

        """
        sids = self.user_connections.get(user_id, set())
        return [self.all_connections[sid] for sid in sids if sid in self.all_connections]

    async def start_cleanup(self) -> None:
        """启动定期清理任务"""
        if self.cleanup_task and not self.cleanup_task.done():
            logger.warning("⚠️ Cleanup task already running")
            return

        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info("✅ Connection pool cleanup task started")

    async def stop_cleanup(self) -> None:
        """停止清理任务"""
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
            logger.info("✅ Connection pool cleanup task stopped")

    async def _cleanup_loop(self) -> None:
        """定期清理陈旧和损坏的连接"""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)
                await self._cleanup_stale_connections()
                await self._cleanup_broken_connections()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("❌ Error in cleanup loop", error=str(e))

    async def _cleanup_stale_connections(self) -> None:
        """清理陈旧连接"""
        stale_sids = []
        for sid, conn in self.all_connections.items():
            if conn.state == ConnectionState.IDLE and conn.is_stale(self.stale_timeout):
                stale_sids.append(sid)

        if stale_sids:
            logger.info(
                "🧹 Cleaning stale connections",
                count=len(stale_sids),
                timeout_seconds=self.stale_timeout,
            )
            for sid in stale_sids:
                self._remove_connection(sid)

    async def _cleanup_broken_connections(self) -> None:
        """清理损坏的连接"""
        broken_sids = [sid for sid, conn in self.all_connections.items() if conn.state == ConnectionState.BROKEN]

        if broken_sids:
            logger.info("🧹 Cleaning broken connections", count=len(broken_sids))
            for sid in broken_sids:
                self._remove_connection(sid)

    def get_stats(self) -> Dict[str, Any]:
        """获取连接池统计"""
        idle_count = self.idle_connections.qsize()
        active_count = len(self.active_connections)
        total_count = len(self.all_connections)

        # 连接状态分布
        states: Dict[str, int] = {
            ConnectionState.IDLE.value: 0,
            ConnectionState.ACTIVE.value: 0,
            ConnectionState.STALE.value: 0,
            ConnectionState.BROKEN.value: 0,
        }

        stale_count = 0
        for conn in self.all_connections.values():
            states[conn.state.value] = states.get(conn.state.value, 0) + 1
            if conn.is_stale(self.stale_timeout):
                stale_count += 1

        return {
            "pool_size": {
                "min": self.min_size,
                "max": self.max_size,
                "current": total_count,
                "idle": idle_count,
                "active": active_count,
            },
            "connection_states": states,
            "stale_connections": stale_count,
            "statistics": {
                "total_acquired": self.total_acquired,
                "total_released": self.total_released,
                "total_recycled": self.total_recycled,
                "reuse_rate": (self.total_released / max(1, self.total_acquired) if self.total_acquired > 0 else 0),
            },
            "users": len(self.user_connections),
            "utilization": (active_count / self.max_size * 100 if self.max_size > 0 else 0),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def get_connection_details(self, sid: str) -> Optional[Dict[str, Any]]:
        """获取特定连接的详细信息"""
        connection = self.all_connections.get(sid)
        return connection.to_dict() if connection else None

    async def drain(self) -> None:
        """清空所有连接（用于关闭）"""
        logger.info("🧹 Draining connection pool")

        # 停止清理任务
        await self.stop_cleanup()

        # 清空所有连接
        self.all_connections.clear()
        self.active_connections.clear()
        self.user_connections.clear()

        # 清空队列
        while not self.idle_connections.empty():
            try:
                self.idle_connections.get_nowait()
            except asyncio.QueueEmpty:
                break

        logger.info("✅ Connection pool drained")


# 全局单例
_connection_pool: Optional[WebSocketConnectionPool] = None


def get_connection_pool(
    min_size: int = 10,
    max_size: int = 1000,
    stale_timeout: int = 300,
    cleanup_interval: int = 60,
) -> WebSocketConnectionPool:
    """获取连接池单例"""
    global _connection_pool
    if _connection_pool is None:
        _connection_pool = WebSocketConnectionPool(
            min_size=min_size,
            max_size=max_size,
            stale_timeout=stale_timeout,
            cleanup_interval=cleanup_interval,
        )
    return _connection_pool


def reset_connection_pool() -> None:
    """重置连接池（仅用于测试）"""
    global _connection_pool
    _connection_pool = None
