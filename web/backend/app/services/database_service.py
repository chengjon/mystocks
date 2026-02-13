"""
数据库服务模块

提供数据库连接、查询、事务管理、批量操作等功能
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

logger = __import__("logging").getLogger(__name__)


class DatabaseType(Enum):
    """数据库类型"""

    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"
    REDIS = "redis"


class QueryStatus(Enum):
    """查询状态"""

    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    ERROR = "error"


class DatabaseConnection:
    """数据库连接配置"""

    db_type: DatabaseType = DatabaseType.POSTGRESQL
    host: str = "localhost"
    port: int = 5432
    database: str = "mystocks"
    username: str = "mystocks_user"
    password: str = "mystocks_password"
    pool_size: int = 10
    max_overflow: int = 20
    is_connected: bool = False
    last_error: Optional[str] = None
    last_connected_at: Optional[datetime] = None
    connection_pool = None

    def to_dict(self) -> Dict:
        return {
            "db_type": self.db_type.value,
            "host": self.host,
            "port": self.port,
            "database": self.database,
            "pool_size": self.pool_size,
            "max_overflow": self.max_overflow,
            "is_connected": self.is_connected,
            "last_error": self.last_error,
            "last_connected_at": self.last_connected_at.isoformat() if self.last_connected_at else None,
        }


@dataclass
class QueryResult:
    """查询结果"""

    query: str = ""
    params: Dict[str, Any] = None
    result: Optional[Any] = None
    status: QueryStatus = QueryStatus.SUCCESS
    rows_affected: int = 0
    execution_time_ms: float = 0.0
    error_message: Optional[str] = None
    executed_at: Optional[datetime] = None

    def to_dict(self) -> Dict:
        return {
            "query": self.query,
            "params": self.params,
            "result": self.result,
            "status": self.status.value,
            "rows_affected": self.rows_affected,
            "execution_time_ms": self.execution_time_ms,
            "error_message": self.error_message,
            "executed_at": self.executed_at.isoformat() if self.executed_at else None,
        }


class DatabaseService:
    """数据库服务"""

    def __init__(self, config: DatabaseConnection):
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.connection = None
        self.is_transaction_active = False
        self.query_cache = {}

        logger.info("数据库服务初始化")

    async def connect(self) -> bool:
        """
        建立数据库连接

        Returns:
            bool: 是否连接成功
        """
        try:
            from psycopg2 import pool

            self.connection = pool.SimpleConnectionPool(
                minconn=1,
                maxconn=self.config.pool_size,
                max_overflow=self.config.max_overflow,
                cur_limit=1,
                host=self.config.host,
                port=self.config.port,
                database=self.config.database,
                user=self.config.username,
                password=self.config.password,
            )

            self.config.is_connected = True
            self.config.last_connected_at = datetime.now()
            self.config.last_error = None

            logger.info(f"数据库连接成功: {self.config.host}:{self.config.port}/{self.config.database}")
            return True

        except Exception as e:
            self.config.is_connected = False
            self.config.last_connected_at = datetime.now()
            self.config.last_error = str(e)

            logger.error(f"数据库连接失败: {e}")
            return False

    async def disconnect(self) -> bool:
        """
        断开数据库连接

        Returns:
            bool: 是否断开成功
        """
        try:
            if self.connection:
                self.connection.closeall()
                self.connection = None
                self.config.is_connected = False

                logger.info("数据库连接已关闭")
                return True
            else:
                logger.warning("数据库未连接")
                return False

        except Exception as e:
            logger.error(f"断开连接失败: {e}")
            return False

    async def execute_query(self, query: str, params: Dict[str, Any] = None) -> QueryResult:
        """
        执行SQL查询

        Args:
            query: SQL查询语句
            params: 查询参数

        Returns:
            QueryResult: 查询结果
        """
        try:
            start_time = datetime.now()

            conn = await self._get_connection()
            cursor = conn.cursor()

            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            result = cursor.fetchall()
            rows_affected = cursor.rowcount

            conn.close()

            end_time = datetime.now()
            execution_time_ms = (end_time - start_time).total_seconds() * 1000

            query_result = QueryResult(
                query=query,
                params=params,
                result=result,
                status=QueryStatus.SUCCESS,
                rows_affected=rows_affected,
                execution_time_ms=execution_time_ms,
                executed_at=end_time,
            )

            logger.info(f"查询执行成功: {len(result)} 行受影响")
            return query_result

        except Exception as e:
            end_time = datetime.now()
            execution_time_ms = (end_time - start_time).total_seconds() * 1000

            return QueryResult(
                query=query,
                params=params,
                result=None,
                status=QueryStatus.ERROR,
                rows_affected=0,
                execution_time_ms=execution_time_ms,
                error_message=str(e),
                executed_at=end_time,
            )

    async def execute_batch_queries(self, queries: List[Dict]) -> List[QueryResult]:
        """
        批量执行SQL查询

        Args:
            queries: SQL查询列表

        Returns:
            List[QueryResult]: 查询结果列表
        """
        try:
            results = []

            for query_config in queries:
                result = await self.execute_query(query=query_config["query"], params=query_config.get("params"))
                results.append(result)

            return results

        except Exception as e:
            logger.error(f"批量查询失败: {e}")
            return []

    async def fetch_one(self, query: str, params: Dict[str, Any] = None) -> Optional[Any]:
        """
        获取单条记录

        Args:
            query: SQL查询语句
            params: 查询参数

        Returns:
            Any: 查询结果，失败返回None
        """
        try:
            query_result = await self.execute_query(query, params)

            if query_result.status == QueryStatus.SUCCESS:
                return query_result.result

            return None

        except Exception as e:
            logger.error(f"获取单条记录失败: {e}")
            return None

    async def fetch_many(self, query: str, params: Dict[str, Any] = None, limit: int = 100) -> List[Any]:
        """
        获取多条记录

        Args:
            query: SQL查询语句
            params: 查询参数
            limit: 限制数量

        Returns:
            List[Any]: 查询结果列表，失败返回空列表
        """
        try:
            query_with_limit = query

            if params:
                params = {k: v for k, v in params.items() if k != "limit"}
            else:
                params = {}

            if limit:
                params["limit"] = limit

            query_result = await self.execute_query(query_with_limit, params)

            if query_result.status == QueryStatus.SUCCESS:
                return query_result.result

            return []

        except Exception as e:
            logger.error(f"获取多条记录失败: {e}")
            return []

    async def begin_transaction(self) -> bool:
        """
        开始事务

        Returns:
            bool: 是否成功
        """
        try:
            if not self.is_transaction_active:
                conn = await self._get_connection()
                conn.autocommit = False
                self.is_transaction_active = True

                logger.info("事务已开始")
                return True
            else:
                logger.warning("事务已活动")
                return False

        except Exception as e:
            logger.error(f"开始事务失败: {e}")
            return False

    async def commit_transaction(self) -> bool:
        """
        提交事务

        Returns:
            bool: 是否成功
        """
        try:
            if self.is_transaction_active:
                conn = await self._get_connection()
                conn.commit()
                self.is_transaction_active = False

                logger.info("事务已提交")
                return True
            else:
                logger.warning("无活动事务")
                return False

        except Exception as e:
            logger.error(f"提交事务失败: {e}")
            return False

    async def rollback_transaction(self) -> bool:
        """
        回滚事务

        Returns:
            bool: 是否成功
        """
        try:
            if self.is_transaction_active:
                conn = await self._get_connection()
                conn.rollback()
                self.is_transaction_active = False

                logger.info("事务已回滚")
                return True
            else:
                logger.warning("无活动事务")
                return False

        except Exception as e:
            logger.error(f"回滚事务失败: {e}")
            return False

    async def execute_in_transaction(self, operation: callable, *args, **kwargs) -> Any:
        """
        在事务中执行操作

        Args:
            operation: 操作函数
            *args: 函数参数
            **kwargs: 关键字参数

        Returns:
            Any: 操作结果，失败返回None
        """
        try:
            await self.begin_transaction()

            try:
                result = await operation(*args, **kwargs)
                await self.commit_transaction()
                return result
            except Exception:
                await self.rollback_transaction()
                raise

        except Exception as e:
            logger.error(f"事务执行失败: {e}")
            raise

    async def _get_connection(self):
        """获取数据库连接（内部方法）"""
        if not self.connection:
            success = await self.connect()
            if not success:
                raise RuntimeError("无法连接到数据库")

        return self.connection

    async def check_connection_health(self) -> Dict:
        """
        检查连接健康状态

        Returns:
            Dict: 健康状态
        """
        try:
            is_connected = self.config.is_connected
            last_connected_at = self.config.last_connected_at

            if is_connected:
                status = "healthy"
                message = f"连接正常，最后连接时间: {last_connected_at.isoformat()}"
            else:
                status = "unhealthy"
                message = "未连接到数据库"

            health_status = {
                "status": status,
                "message": message,
                "last_connected_at": last_connected_at.isoformat() if last_connected_at else None,
                "config": self.config.to_dict(),
            }

            return health_status

        except Exception as e:
            logger.error(f"检查连接健康状态失败: {e}")
            return {"status": "error", "message": str(e), "config": self.config.to_dict()}

    def get_connection_config(self) -> DatabaseConnection:
        """获取连接配置"""
        return self.config

    async def get_connection_pool_stats(self) -> Dict:
        """
        获取连接池统计

        Returns:
            Dict: 连接池统计
        """
        try:
            if not self.connection:
                return {"status": "disconnected", "pool_size": 0, "active_connections": 0, "idle_connections": 0}

            stats = self.connection._pool.get_stats()

            return {
                "status": "connected",
                "pool_size": self.config.pool_size,
                "max_overflow": self.config.max_overflow,
                "active_connections": stats.get("numcheckedout", 0),
                "idle_connections": stats.get("numcheckedin", 0),
            }

        except Exception as e:
            logger.error(f"获取连接池统计失败: {e}")
            return {"status": "error", "error": str(e)}
