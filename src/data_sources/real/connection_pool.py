"""
PostgreSQL连接池管理器
从 postgresql_relational.py 中提取，专门用于数据库连接池管理
"""

import logging
import queue
import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import psycopg2
import psycopg2.extensions
from psycopg2 import InterfaceError, OperationalError

logger = logging.getLogger(__name__)


@dataclass
class PoolConfig:
    """连接池配置"""

    min_connections: int = 2
    max_connections: int = 20
    max_idle_time: int = 300  # 5分钟
    max_lifetime: int = 3600  # 1小时
    retry_attempts: int = 3
    retry_delay: float = 1.0
    connection_timeout: int = 30
    health_check_interval: int = 60  # 健康检查间隔
    enable_health_check: bool = True


@dataclass
class ConnectionMetrics:
    """连接池指标"""

    total_created: int = 0
    total_closed: int = 0
    current_active: int = 0
    peak_active: int = 0
    total_requests: int = 0
    failed_requests: int = 0
    average_wait_time: float = 0.0
    last_health_check: Optional[datetime] = None


class PooledConnection:
    """池化连接包装器"""

    def __init__(
        self,
        connection: psycopg2.extensions.connection,
        pool: "PostgreSQLConnectionPool",
    ):
        self._connection = connection
        self._pool = pool
        self._created_at = datetime.now()
        self._last_used = datetime.now()
        self._is_valid = True
        self._use_count = 0

        # 设置连接为autocommit模式（根据需要）
        self._connection.autocommit = False

    @property
    def connection(self) -> psycopg2.extensions.connection:
        """获取原始连接对象"""
        return self._connection

    def is_expired(self) -> bool:
        """检查连接是否过期"""
        now = datetime.now()
        age = (now - self._created_at).total_seconds()
        idle_time = (now - self._last_used).total_seconds()

        return age > self._pool.config.max_lifetime or idle_time > self._pool.config.max_idle_time

    def is_healthy(self) -> bool:
        """检查连接是否健康"""
        if not self._is_valid or self.is_expired():
            return False

        try:
            # 执行简单查询检查连接
            cursor = self._connection.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            return True
        except (OperationalError, InterfaceError):
            self._is_valid = False
            return False

    def mark_used(self):
        """标记连接为已使用"""
        self._last_used = datetime.now()
        self._use_count += 1

    def close(self):
        """关闭连接"""
        if self._connection and not self._connection.closed:
            try:
                self._connection.close()
            except Exception:
                pass
            self._is_valid = False


class PostgreSQLConnectionPool:
    """
    PostgreSQL连接池管理器

    提供高性能、安全的数据库连接池服务，支持：
    - 连接复用和生命周期管理
    - 自动重试和错误恢复
    - 健康检查和监控
    - 线程安全的并发访问
    """

    def __init__(self, dsn: str, config: Optional[PoolConfig] = None):
        """
        初始化连接池

        Args:
            dsn: 数据库连接字符串
            config: 连接池配置
        """
        self.dsn = dsn
        self.config = config or PoolConfig()
        self.metrics = ConnectionMetrics()

        # 连接管理
        self._pool = queue.Queue(maxsize=self.config.max_connections)
        self._active_connections = set()
        self._lock = threading.RLock()

        # 后台任务
        self._shutdown_event = threading.Event()
        self._health_check_thread = None
        self._cleanup_thread = None

        logger.info(
            "PostgreSQL连接池初始化完成: min=%s, max=%s", self.config.min_connections, self.config.max_connections
        )

        # 预热连接池
        self._initialize_pool()

        # 启动后台任务
        if self.config.enable_health_check:
            self._start_background_tasks()

    def _initialize_pool(self):
        """初始化连接池"""
        with self._lock:
            # 创建最小连接数
            for _ in range(self.config.min_connections):
                try:
                    conn = self._create_connection()
                    if conn:
                        self._pool.put(conn)
                except Exception as e:
                    logger.warning("创建初始连接失败: %s", e)

    def _create_connection(self) -> Optional[PooledConnection]:
        """创建新连接"""
        raw_conn = None
        try:
            # 基础连接配置
            raw_conn = psycopg2.connect(
                self.dsn,
                connect_timeout=self.config.connection_timeout,
                **self._get_connection_kwargs(),
            )

            # 创建池化连接包装器
            pooled_conn = PooledConnection(raw_conn, self)

            with self._lock:
                self.metrics.total_created += 1

            logger.debug("创建新数据库连接: %s", id(raw_conn))
            return pooled_conn

        except Exception as e:
            logger.error("创建数据库连接失败: %s", e)
            with self._lock:
                self.metrics.failed_requests += 1
            return None
        finally:
            if raw_conn is not None:
                try:
                    raw_conn.close()
                except Exception:
                    pass

    def _get_connection_kwargs(self) -> Dict[str, Any]:
        """获取连接参数"""
        return {
            "application_name": "mystocks_connection_pool",
            "options": "-c default_transaction_isolation=read_committed",
        }

    @contextmanager
    def get_connection(self, timeout: Optional[float] = None):
        """
        获取数据库连接的上下文管理器

        Args:
            timeout: 超时时间

        Yields:
            PooledConnection: 池化连接
        """
        conn = None
        start_time = time.time()

        try:
            conn = self._acquire_connection(timeout)
            yield conn
        finally:
            if conn:
                self._release_connection(conn)

                # 更新等待时间统计
                wait_time = time.time() - start_time
                with self._lock:
                    self.metrics.average_wait_time = self.metrics.average_wait_time * 0.9 + wait_time * 0.1

    def _acquire_connection(self, timeout: Optional[float] = None) -> PooledConnection:
        """获取连接"""
        timeout = timeout or 30.0
        start_time = time.time()

        with self._lock:
            self.metrics.total_requests += 1

        # 尝试获取空闲连接
        try:
            # 从池中获取连接
            conn = self._pool.get(timeout=timeout)

            # 检查连接是否健康
            if conn.is_healthy():
                conn.mark_used()
                with self._lock:
                    self._active_connections.add(conn)
                    self.metrics.current_active = len(self._active_connections)
                    self.metrics.peak_active = max(self.metrics.peak_active, self.metrics.current_active)

                logger.debug("从池中获取连接: %s", id(conn.connection))
                return conn
            else:
                # 连接不健康，关闭并创建新连接
                self._close_connection(conn)
                return self._create_and_acquire_connection(timeout - (time.time() - start_time))

        except queue.Empty:
            # 池中没有可用连接，尝试创建新连接
            return self._create_and_acquire_connection(timeout - (time.time() - start_time))

    def _create_and_acquire_connection(self, timeout: float) -> PooledConnection:
        """创建并获取新连接"""
        max(timeout, 1.0)

        for attempt in range(self.config.retry_attempts):
            try:
                conn = self._create_connection()
                if conn:
                    with self._lock:
                        self._active_connections.add(conn)
                        self.metrics.current_active = len(self._active_connections)

                    return conn

            except Exception as e:
                logger.warning("创建连接失败 (尝试 %s/%s): %s", attempt + 1, self.config.retry_attempts, e)

                if attempt < self.config.retry_attempts - 1:
                    time.sleep(self.config.retry_delay * (2**attempt))
                else:
                    raise

        raise TimeoutError(f"获取数据库连接超时: {timeout}秒")

    def _release_connection(self, conn: PooledConnection):
        """释放连接回池"""
        if not conn:
            return

        try:
            with self._lock:
                if conn in self._active_connections:
                    self._active_connections.remove(conn)
                    self.metrics.current_active = len(self._active_connections)

                # 检查连接是否还能使用
                if conn.is_healthy() and not self._pool.full():
                    conn.mark_used()
                    self._pool.put(conn, block=False)
                    logger.debug("连接返回池中: %s", id(conn.connection))
                else:
                    # 连接不健康或池已满，关闭连接
                    self._close_connection(conn)

        except Exception as e:
            logger.error("释放连接时出错: %s", e)
            self._close_connection(conn)

    def _close_connection(self, conn: PooledConnection):
        """关闭连接"""
        if not conn:
            return

        try:
            conn.close()
            with self._lock:
                if conn in self._active_connections:
                    self._active_connections.remove(conn)
                self.metrics.total_closed += 1
                self.metrics.current_active = len(self._active_connections)

            logger.debug("关闭数据库连接: %s", id(conn.connection))

        except Exception as e:
            logger.error("关闭连接时出错: %s", e)

    def execute_query(self, query: str, params: Optional[tuple] = None, fetch: bool = True) -> Any:
        """
        执行SQL查询

        Args:
            query: SQL语句
            params: 查询参数
            fetch: 是否获取结果

        Returns:
            查询结果
        """
        start_time = time.time()
        try:
            with self.get_connection() as conn:
                try:
                    cursor = conn.connection.cursor()
                    cursor.execute(query, params or ())

                    if fetch:
                        if cursor.description:
                            # 返回字典格式结果
                            columns = [desc[0] for desc in cursor.description]
                            rows = cursor.fetchall()
                            result = [{columns[i]: row[i] for i in range(len(columns))} for row in rows]
                        else:
                            result = cursor.fetchall()
                    else:
                        result = cursor.rowcount

                    cursor.close()
                    return result

                except Exception as e:
                    conn.connection.rollback()
                    logger.error("查询执行失败: %s, 错误: %s", query, e)
                    raise

        finally:
            execution_time = time.time() - start_time
            if execution_time > 1.0:  # 记录慢查询
                logger.warning("慢查询检测: 执行时间 %ss, SQL: %s...", execution_time, query[:100])

    def execute_transaction(self, queries: List[tuple]) -> bool:
        """
        执行事务

        Args:
            queries: 查询列表，每个元素为 (sql, params) 元组

        Returns:
            bool: 是否成功
        """
        with self.get_connection() as conn:
            try:
                cursor = conn.connection.cursor()

                # 开始事务
                conn.connection.autocommit = False

                for sql, params in queries:
                    cursor.execute(sql, params or ())

                # 提交事务
                conn.connection.commit()
                cursor.close()
                return True

            except Exception as e:
                # 回滚事务
                try:
                    conn.connection.rollback()
                except Exception:
                    pass
                logger.error("事务执行失败: %s", e)
                return False

    def get_pool_info(self) -> Dict[str, Any]:
        """获取连接池信息"""
        with self._lock:
            return {
                "total_created": self.metrics.total_created,
                "total_closed": self.metrics.total_closed,
                "current_active": self.metrics.current_active,
                "peak_active": self.metrics.peak_active,
                "total_requests": self.metrics.total_requests,
                "failed_requests": self.metrics.failed_requests,
                "average_wait_time": self.metrics.average_wait_time,
                "pool_size": self._pool.qsize(),
                "active_connections": len(self._active_connections),
                "config": {
                    "min_connections": self.config.min_connections,
                    "max_connections": self.config.max_connections,
                    "max_idle_time": self.config.max_idle_time,
                    "max_lifetime": self.config.max_lifetime,
                },
                "last_health_check": self.metrics.last_health_check,
            }

    def health_check(self) -> Dict[str, Any]:
        """执行健康检查"""
        healthy_connections = 0
        unhealthy_connections = 0

        with self._lock:
            for conn in list(self._active_connections):
                if conn.is_healthy():
                    healthy_connections += 1
                else:
                    unhealthy_connections += 1

        status = "healthy" if unhealthy_connections == 0 else "degraded"

        self.metrics.last_health_check = datetime.now()

        return {
            "status": status,
            "healthy_connections": healthy_connections,
            "unhealthy_connections": unhealthy_connections,
            "total_connections": healthy_connections + unhealthy_connections,
            "pool_utilization": f"{(healthy_connections + unhealthy_connections)}/{self.config.max_connections}",
            "last_check": self.metrics.last_health_check.isoformat(),
        }

    def _start_background_tasks(self):
        """启动后台任务"""
        # 启动健康检查线程
        self._health_check_thread = threading.Thread(
            target=self._health_check_worker, daemon=True, name="PostgreSQL-HealthCheck"
        )
        self._health_check_thread.start()

        # 启动清理线程
        self._cleanup_thread = threading.Thread(target=self._cleanup_worker, daemon=True, name="PostgreSQL-Cleanup")
        self._cleanup_thread.start()

    def _health_check_worker(self):
        """健康检查工作线程"""
        while not self._shutdown_event.is_set():
            try:
                # 检查池中所有连接
                unhealthy = []

                # 检查活跃连接
                with self._lock:
                    for conn in list(self._active_connections):
                        if not conn.is_healthy():
                            unhealthy.append(conn)

                # 处理不健康连接
                for conn in unhealthy:
                    logger.warning("发现不健康连接，准备替换: %s", id(conn.connection))
                    self._release_connection(conn)

                # 记录健康检查结果
                health_status = self.health_check()
                if health_status["status"] != "healthy":
                    logger.warning("连接池健康检查: %s", health_status)

            except Exception as e:
                logger.error("健康检查失败: %s", e)

            # 等待下次检查
            if self._shutdown_event.wait(self.config.health_check_interval):
                break

    def _cleanup_worker(self):
        """清理工作线程"""
        while not self._shutdown_event.is_set():
            try:
                # 清理过期连接
                expired_connections = []

                with self._lock:
                    for conn in list(self._active_connections):
                        if conn.is_expired():
                            expired_connections.append(conn)

                # 处理过期连接
                for conn in expired_connections:
                    logger.info("清理过期连接: %s", id(conn.connection))
                    self._close_connection(conn)

                # 如果连接数少于最小值，补充连接
                current_size = self._pool.qsize()
                with self._lock:
                    len(self._active_connections)

                if current_size < self.config.min_connections:
                    needed = self.config.min_connections - current_size
                    for _ in range(needed):
                        try:
                            conn = self._create_connection()
                            if conn:
                                self._pool.put(conn, block=False)
                        except Exception:
                            pass

            except Exception as e:
                logger.error("连接清理失败: %s", e)

            # 等待下次清理
            if self._shutdown_event.wait(300):  # 5分钟
                break

    def close(self):
        """关闭连接池"""
        logger.info("开始关闭PostgreSQL连接池...")

        # 停止后台任务
        self._shutdown_event.set()

        if self._health_check_thread and self._health_check_thread.is_alive():
            self._health_check_thread.join(timeout=5)

        if self._cleanup_thread and self._cleanup_thread.is_alive():
            self._cleanup_thread.join(timeout=5)

        # 关闭所有连接
        with self._lock:
            # 关闭活跃连接
            for conn in list(self._active_connections):
                self._close_connection(conn)

            # 关闭池中的连接
            while not self._pool.empty():
                try:
                    conn = self._pool.get(block=False)
                    self._close_connection(conn)
                except queue.Empty:
                    break

        logger.info("PostgreSQL连接池已关闭")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# 连接池管理器工厂
class ConnectionPoolManager:
    """连接池管理器工厂"""

    _instances: Dict[str, PostgreSQLConnectionPool] = {}
    _lock = threading.Lock()

    @classmethod
    def get_pool(cls, dsn: str, config: Optional[PoolConfig] = None) -> PostgreSQLConnectionPool:
        """
        获取连接池实例（单例模式）

        Args:
            dsn: 数据库连接字符串
            config: 连接池配置

        Returns:
            PostgreSQLConnectionPool: 连接池实例
        """
        # 使用DSN作为键，确保每个数据库只有一个连接池
        with cls._lock:
            if dsn not in cls._instances:
                cls._instances[dsn] = PostgreSQLConnectionPool(dsn, config)
            return cls._instances[dsn]

    @classmethod
    def close_pool(cls, dsn: str):
        """关闭指定连接池"""
        with cls._lock:
            if dsn in cls._instances:
                cls._instances[dsn].close()
                del cls._instances[dsn]

    @classmethod
    def close_all_pools(cls):
        """关闭所有连接池"""
        with cls._lock:
            for dsn, pool in list(cls._instances.items()):
                pool.close()
            cls._instances.clear()
