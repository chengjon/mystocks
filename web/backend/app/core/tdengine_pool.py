"""
TDengine连接池管理器 - Phase 3优化
Task 19: 数据库连接池优化

实现TDengine连接池，支持连接复用、超时处理和监控。

Features:
- 连接池管理（最小连接数、最大连接数）
- 连接复用机制
- 连接超时处理
- 连接健康检查
- 连接池状态监控
"""

import queue
import threading
import time
import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import structlog
from taos import TaosConnection, connect

logger = structlog.get_logger()


class TDengineConnectionPool:
    """
    TDengine连接池管理器

    实现连接池模式，支持：
    - 连接复用（避免频繁创建/销毁连接）
    - 连接健康检查（自动重连失效连接）
    - 连接超时管理（释放长时间空闲连接）
    - 连接池监控（统计连接使用情况）

    Usage:
        ```python
        pool = TDengineConnectionPool(
            host="localhost",
            min_size=5,
            max_size=20
        )

        # 获取连接
        conn = pool.get_connection(timeout=30)
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM table")
        finally:
            # 归还连接到池
            pool.release_connection(conn)

        # 或使用上下文管理器
        with pool.get_connection_context() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM table")
        ```
    """

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 6030,
        user: str = "root",
        password: Optional[str] = None,
        database: Optional[str] = None,
        min_size: int = 5,
        max_size: int = 20,
        max_idle_time: int = 600,  # 最大空闲时间（秒）
        health_check_interval: int = 60,  # 健康检查间隔（秒）
    ):
        """
        初始化TDengine连接池

        Args:
            host: TDengine服务器地址
            port: 端口号
            user: 用户名
            password: 密码
            database: 数据库名（可选）
            min_size: 最小连接数
            max_size: 最大连接数
            max_idle_time: 最大空闲时间（秒）
            health_check_interval: 健康检查间隔（秒）
        """
        self.host = host
        self.port = port
        self.user = user
        self.password = password or os.getenv("TDENGINE_PASSWORD")
        if not self.password:
            raise ValueError("TDENGINE_PASSWORD environment variable must be set")
        self.database = database
        self.min_size = min_size
        self.max_size = max_size
        self.max_idle_time = max_idle_time
        self.health_check_interval = health_check_interval

        # 连接池（使用队列管理）
        self._pool: queue.Queue = queue.Queue(maxsize=max_size)
        self._all_connections: list[Any] = []  # 跟踪所有创建的连接
        self._connection_meta: dict[str, Any] = {}  # 连接元数据（创建时间、最后使用时间等）
        self._lock = threading.Lock()

        # 统计信息
        self._stats = {
            "total_created": 0,
            "total_closed": 0,
            "active_connections": 0,
            "idle_connections": 0,
            "connection_requests": 0,
            "connection_timeouts": 0,
            "connection_errors": 0,
        }

        # 初始化最小连接数
        self._initialize_pool()

        # 启动健康检查线程
        self._health_check_thread = threading.Thread(target=self._health_check_loop, daemon=True)
        self._health_check_thread.start()

        logger.info("🔧 TDengine连接池已初始化", host=host, min_size=min_size, max_size=max_size)

    def _initialize_pool(self):
        """初始化连接池（创建最小连接数）"""
        for _ in range(self.min_size):
            try:
                conn = self._create_connection()
                self._pool.put(conn)
                self._stats["idle_connections"] += 1
            except Exception as e:
                logger.error("初始化连接失败", error=str(e))

    def _create_connection(self) -> TaosConnection:
        """
        创建新的TDengine连接

        Returns:
            TaosConnection实例
        """
        try:
            conn = connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
            )

            conn_id = str(id(conn))
            self._all_connections.append(conn)
            self._connection_meta[conn_id] = {
                "created_at": datetime.now(timezone.utc),
                "last_used_at": datetime.now(timezone.utc),
                "total_uses": 0,
            }

            self._stats["total_created"] += 1

            logger.debug(
                "创建新连接",
                conn_id=conn_id,
                total_created=self._stats["total_created"],
            )

            return conn

        except Exception as e:
            self._stats["connection_errors"] += 1
            logger.error("创建连接失败", error=str(e))
            raise

    def get_connection(self, timeout: int = 30) -> Optional[TaosConnection]:
        """
        从连接池获取连接

        Args:
            timeout: 超时时间（秒）

        Returns:
            TaosConnection实例，如果超时则返回None
        """
        self._stats["connection_requests"] += 1

        try:
            # 尝试从池中获取空闲连接
            conn = self._pool.get(timeout=timeout)

            # 更新连接元数据
            conn_id = str(id(conn))
            if conn_id in self._connection_meta:
                self._connection_meta[conn_id]["last_used_at"] = datetime.now(timezone.utc)
                self._connection_meta[conn_id]["total_uses"] += 1

            # 更新统计
            with self._lock:
                self._stats["idle_connections"] -= 1
                self._stats["active_connections"] += 1

            # 健康检查
            if not self._is_connection_healthy(conn):
                logger.warning("连接不健康，重新创建", conn_id=conn_id)
                self._close_connection(conn)
                return self._create_connection()

            logger.debug("获取连接", conn_id=conn_id, active=self._stats["active_connections"])

            return conn

        except queue.Empty:
            # 池中无可用连接，尝试创建新连接
            with self._lock:
                if len(self._all_connections) < self.max_size:
                    try:
                        conn = self._create_connection()
                        self._stats["active_connections"] += 1
                        return conn
                    except Exception as e:
                        logger.error("创建新连接失败", error=str(e))
                        self._stats["connection_errors"] += 1
                        return None
                else:
                    # 达到最大连接数，超时
                    self._stats["connection_timeouts"] += 1
                    logger.warning(
                        "连接池已满，获取连接超时",
                        max_size=self.max_size,
                        active=self._stats["active_connections"],
                    )
                    return None

    def release_connection(self, conn: TaosConnection):
        """
        归还连接到连接池

        Args:
            conn: 要归还的连接
        """
        if conn is None:
            return

        conn_id = id(conn)

        # 健康检查
        if not self._is_connection_healthy(conn):
            logger.warning("归还的连接不健康，关闭", conn_id=conn_id)
            self._close_connection(conn)
            return

        # 放���池中
        try:
            self._pool.put_nowait(conn)

            with self._lock:
                self._stats["active_connections"] -= 1
                self._stats["idle_connections"] += 1

            logger.debug("归还连接", conn_id=conn_id, idle=self._stats["idle_connections"])

        except queue.Full:
            # 池已满，关闭连接
            logger.debug("连接池已满，关闭多余连接", conn_id=conn_id)
            self._close_connection(conn)

    def _is_connection_healthy(self, conn: TaosConnection) -> bool:
        """
        检查连接是否健康

        Args:
            conn: 要检查的连接

        Returns:
            True如果连接健康，否则False
        """
        try:
            # 执行简单查询测试连接
            cursor = conn.cursor()
            cursor.execute("SELECT SERVER_VERSION()")
            cursor.fetchone()
            cursor.close()
            return True
        except Exception as e:
            logger.debug("连接健康检查失败", error=str(e))
            return False

    def _close_connection(self, conn: TaosConnection):
        """关闭连接"""
        try:
            conn_id = str(id(conn))
            conn.close()

            # 从跟踪列表中移除
            if conn in self._all_connections:
                self._all_connections.remove(conn)
            if conn_id in self._connection_meta:
                del self._connection_meta[conn_id]

            self._stats["total_closed"] += 1

            logger.debug("关闭连接", conn_id=conn_id)

        except Exception as e:
            logger.error("关闭连接失败", error=str(e))

    def _health_check_loop(self):
        """健康检查循环（后台线程）"""
        while True:
            try:
                time.sleep(self.health_check_interval)
                self._cleanup_idle_connections()
            except Exception as e:
                logger.error("健康检查循环错误", error=str(e))

    def _cleanup_idle_connections(self):
        """清理超时的空闲连接"""
        now = datetime.now(timezone.utc)
        closed_count = 0

        # 检查所有连接的空闲时间
        for conn in list(self._all_connections):
            conn_id = str(id(conn))
            if conn_id in self._connection_meta:
                last_used = self._connection_meta[conn_id]["last_used_at"]
                idle_seconds = (now - last_used).total_seconds()

                if idle_seconds > self.max_idle_time:
                    logger.info("清理空闲连接", conn_id=conn_id, idle_seconds=idle_seconds)
                    self._close_connection(conn)
                    closed_count += 1

        if closed_count > 0:
            logger.info(
                "清理空闲连接完成",
                closed_count=closed_count,
                remaining=len(self._all_connections),
            )

    def get_connection_context(self, timeout: int = 30):
        """
        获取连接上下文管理器

        Args:
            timeout: 超时时间（秒）

        Returns:
            ConnectionContext实例
        """
        return ConnectionContext(self, timeout)

    def get_stats(self) -> Dict[str, Any]:
        """
        获取连接池统计信息

        Returns:
            统计信息字典
        """
        return {
            **self._stats,
            "pool_size": len(self._all_connections),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def close_all(self):
        """关闭所有连接"""
        logger.info("关闭所有TDengine连接...")

        # 清空队列
        while not self._pool.empty():
            try:
                conn = self._pool.get_nowait()
                self._close_connection(conn)
            except queue.Empty:
                break

        # 关闭所有剩余连接
        for conn in list(self._all_connections):
            self._close_connection(conn)

        logger.info("所有TDengine连接已关闭", total_closed=self._stats["total_closed"])


class ConnectionContext:
    """连接上下文管理器"""

    def __init__(self, pool: TDengineConnectionPool, timeout: int = 30):
        """
        初始化上下文管理器

        Args:
            pool: 连接池实例
            timeout: 获取连接超时时间
        """
        self.pool = pool
        self.timeout = timeout
        self.conn = None

    def __enter__(self) -> TaosConnection:
        """进入上下文，获取连接"""
        self.conn = self.pool.get_connection(timeout=self.timeout)
        if self.conn is None:
            raise TimeoutError(f"无法在{self.timeout}秒内获取数据库连接")
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文，归还连接"""
        # self.conn is guaranteed to be non-None here because __enter__ raises TimeoutError if it's None
        self.pool.release_connection(self.conn)
