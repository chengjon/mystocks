"""
WebSocket连接生命周期管理

Connection Lifecycle Management - Handle connect/disconnect/timeout events

Task 4.2: 实现连接管理

包括：
- 连接建立处理
- 连接断开处理
- 连接超时检测
- 心跳保活机制
- 连接状态验证

Author: Claude Code
Date: 2025-11-06
"""

import asyncio
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, Optional

import structlog

logger = structlog.get_logger()


class ConnectionState(str, Enum):
    """连接状态枚举"""

    CONNECTING = "connecting"  # 连接中
    CONNECTED = "connected"  # 已连接
    IDLE = "idle"  # 空闲
    TIMEOUT = "timeout"  # 已超时
    DISCONNECTING = "disconnecting"  # 断开中
    DISCONNECTED = "disconnected"  # 已断开


class HeartbeatConfig:
    """心跳配置"""

    def __init__(
        self,
        interval: float = 30.0,
        timeout: float = 60.0,
        max_retries: int = 3,
    ):
        """
        初始化心跳配置

        Args:
            interval: 心跳间隔（秒）
            timeout: 心跳超时时间（秒）
            max_retries: 最大重试次数
        """
        self.interval = interval
        self.timeout = timeout
        self.max_retries = max_retries


class ConnectionLifecycleManager:
    """WebSocket连接生命周期管理器"""

    def __init__(self, heartbeat_config: Optional[HeartbeatConfig] = None):
        """初始化连接生命周期管理器"""
        self.heartbeat_config = heartbeat_config or HeartbeatConfig()
        self.connection_states: Dict[str, ConnectionState] = {}
        self.connection_times: Dict[str, datetime] = {}
        self.last_heartbeat: Dict[str, datetime] = {}
        self.heartbeat_failures: Dict[str, int] = {}
        self.connection_callbacks: Dict[str, Callable] = {}

    def register_connection(self, sid: str) -> None:
        """注册新连接"""
        self.connection_states[sid] = ConnectionState.CONNECTING
        self.connection_times[sid] = datetime.now(timezone.utc)
        self.last_heartbeat[sid] = datetime.now(timezone.utc)
        self.heartbeat_failures[sid] = 0

        logger.info(
            "📝 Connection registered",
            sid=sid,
            state=ConnectionState.CONNECTING,
        )

    def mark_connected(self, sid: str) -> None:
        """标记连接为已连接"""
        if sid not in self.connection_states:
            self.register_connection(sid)

        self.connection_states[sid] = ConnectionState.CONNECTED
        self.last_heartbeat[sid] = datetime.now(timezone.utc)

        logger.info(
            "✅ Connection established",
            sid=sid,
            connected_at=self.connection_times[sid].isoformat(),
        )

    def mark_disconnected(self, sid: str) -> None:
        """标记连接为已断开"""
        if sid not in self.connection_states:
            return

        self.connection_states[sid] = ConnectionState.DISCONNECTED
        connected_duration = (datetime.now(timezone.utc) - self.connection_times[sid]).total_seconds()

        logger.info(
            "🛑 Connection closed",
            sid=sid,
            connected_duration_seconds=connected_duration,
        )

        # 清理资源
        self._cleanup_connection(sid)

    def record_heartbeat(self, sid: str) -> None:
        """记录心跳"""
        if sid not in self.connection_states:
            return

        self.last_heartbeat[sid] = datetime.now(timezone.utc)
        self.heartbeat_failures[sid] = 0  # 重置失败计数

        logger.debug("💓 Heartbeat received", sid=sid)

    def check_heartbeat_timeout(self, sid: str) -> bool:
        """检查心跳是否超时"""
        if sid not in self.connection_states:
            return False

        state = self.connection_states[sid]
        if state in [ConnectionState.DISCONNECTED, ConnectionState.TIMEOUT]:
            return False

        last_beat = self.last_heartbeat.get(sid)
        if not last_beat:
            return False

        elapsed = (datetime.now(timezone.utc) - last_beat).total_seconds()
        is_timeout = elapsed > self.heartbeat_config.timeout

        if is_timeout:
            self.heartbeat_failures[sid] = self.heartbeat_failures.get(sid, 0) + 1
            logger.warning(
                "⚠️ Heartbeat timeout detected",
                sid=sid,
                elapsed_seconds=elapsed,
                failures=self.heartbeat_failures[sid],
            )

        return is_timeout

    def check_connection_timeout(self, sid: str) -> bool:
        """检查连接是否已超时"""
        if self.check_heartbeat_timeout(sid):
            # 检查是否超过最大重试次数
            if self.heartbeat_failures.get(sid, 0) >= self.heartbeat_config.max_retries:
                self.connection_states[sid] = ConnectionState.TIMEOUT
                logger.error(
                    "❌ Connection timeout",
                    sid=sid,
                    max_retries=self.heartbeat_config.max_retries,
                )
                return True

        return False

    def is_healthy(self, sid: str) -> bool:
        """检查连接是否健康"""
        if sid not in self.connection_states:
            return False

        state = self.connection_states[sid]
        if state not in [ConnectionState.CONNECTED, ConnectionState.IDLE]:
            return False

        return not self.check_heartbeat_timeout(sid)

    def get_connection_state(self, sid: str) -> Optional[ConnectionState]:
        """获取连接状态"""
        return self.connection_states.get(sid)

    def get_connection_duration(self, sid: str) -> Optional[float]:
        """获取连接持续时间（秒）"""
        if sid not in self.connection_times:
            return None

        return (datetime.now(timezone.utc) - self.connection_times[sid]).total_seconds()

    def get_heartbeat_age(self, sid: str) -> Optional[float]:
        """获取心跳年龄（秒）"""
        if sid not in self.last_heartbeat:
            return None

        return (datetime.now(timezone.utc) - self.last_heartbeat[sid]).total_seconds()

    def get_all_healthy_connections(self) -> list[str]:
        """获取所有健康连接"""
        return [sid for sid in self.connection_states if self.is_healthy(sid)]

    def get_all_timeout_connections(self) -> list[str]:
        """获取所有超时连接"""
        return [sid for sid in self.connection_states if self.connection_states[sid] == ConnectionState.TIMEOUT]

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        total = len(self.connection_states)
        connected = sum(1 for state in self.connection_states.values() if state == ConnectionState.CONNECTED)
        idle = sum(1 for state in self.connection_states.values() if state == ConnectionState.IDLE)
        timeout = sum(1 for state in self.connection_states.values() if state == ConnectionState.TIMEOUT)
        disconnected = sum(1 for state in self.connection_states.values() if state == ConnectionState.DISCONNECTED)

        return {
            "total_connections": total,
            "connected": connected,
            "idle": idle,
            "timeout": timeout,
            "disconnected": disconnected,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def _cleanup_connection(self, sid: str) -> None:
        """清理连接资源"""
        self.last_heartbeat.pop(sid, None)
        self.heartbeat_failures.pop(sid, None)
        self.connection_times.pop(sid, None)


# 全局单例
_lifecycle_manager: Optional[ConnectionLifecycleManager] = None


def get_connection_lifecycle_manager(
    heartbeat_config: Optional[HeartbeatConfig] = None,
) -> ConnectionLifecycleManager:
    """获取连接生命周期管理器单例"""
    global _lifecycle_manager
    if _lifecycle_manager is None:
        _lifecycle_manager = ConnectionLifecycleManager(heartbeat_config)
    return _lifecycle_manager


def reset_connection_lifecycle_manager() -> None:
    """重置连接生命周期管理器（仅用于测试）"""
    global _lifecycle_manager
    _lifecycle_manager = None


class ConnectionHealthMonitor:
    """连接健康状态监控器"""

    def __init__(
        self,
        lifecycle_manager: ConnectionLifecycleManager,
        check_interval: float = 10.0,
    ):
        """
        初始化连接健康监控器

        Args:
            lifecycle_manager: 连接生命周期管理器
            check_interval: 检查间隔（秒）
        """
        self.lifecycle_manager = lifecycle_manager
        self.check_interval = check_interval
        self.is_running = False
        self.monitor_task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        """启动监控"""
        if self.is_running:
            return

        self.is_running = True
        self.monitor_task = asyncio.create_task(self._monitor_loop())
        logger.info("✅ Connection health monitor started")

    async def stop(self) -> None:
        """停止监控"""
        if not self.is_running:
            return

        self.is_running = False
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass

        logger.info("✅ Connection health monitor stopped")

    async def _monitor_loop(self) -> None:
        """监控循环"""
        while self.is_running:
            try:
                await asyncio.sleep(self.check_interval)

                # 检查超时连接
                timeout_connections = self.lifecycle_manager.get_all_timeout_connections()
                if timeout_connections:
                    logger.warning(
                        "⚠️ Timeout connections detected",
                        count=len(timeout_connections),
                        sids=timeout_connections,
                    )

                # 获取统计信息
                stats = self.lifecycle_manager.get_stats()
                logger.info("📊 Connection health stats", **stats)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(
                    "❌ Error in connection health monitor",
                    error=str(e),
                )
