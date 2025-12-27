"""
PostgreSQL连接适配器
为 postgresql_relational.py 提供连接池支持的无缝适配层
"""

import logging
from typing import Optional, Any, Dict, List
from contextlib import contextmanager

from src.data_sources.real.connection_pool import (
    PostgreSQLConnectionPool,
    PoolConfig,
    ConnectionPoolManager,
)
from src.storage.database.database_manager import DatabaseTableManager, DatabaseType

logger = logging.getLogger(__name__)


class PostgreSQLConnectionAdapter:
    """
    PostgreSQL连接适配器

    为现有代码提供连接池支持，同时保持API兼容性
    """

    def __init__(
        self,
        database_manager: DatabaseTableManager,
        pool_config: Optional[PoolConfig] = None,
    ):
        """
        初始化连接适配器

        Args:
            database_manager: 数据库管理器
            pool_config: 连接池配置
        """
        self.database_manager = database_manager
        self.pool_config = pool_config or PoolConfig()
        self._connection_pool: Optional[PostgreSQLConnectionPool] = None
        self._initialized = False

    def _ensure_pool_initialized(self) -> PostgreSQLConnectionPool:
        """确保连接池已初始化"""
        if not self._initialized or not self._connection_pool:
            self._initialize_pool()
        return self._connection_pool

    def _initialize_pool(self):
        """初始化连接池"""
        try:
            # 获取PostgreSQL连接配置
            db_config = self.database_manager.db_configs.get(DatabaseType.POSTGRESQL, {})

            # 构建DSN
            dsn_parts = []
            if db_config.get("host"):
                dsn_parts.append(f"host={db_config['host']}")
            if db_config.get("port"):
                dsn_parts.append(f"port={db_config['port']}")
            if db_config.get("user"):
                dsn_parts.append(f"user={db_config['user']}")
            if db_config.get("password"):
                dsn_parts.append(f"password={db_config['password']}")
            if db_config.get("database"):
                dsn_parts.append(f"dbname={db_config['database']}")

            dsn = " ".join(dsn_parts)

            # 创建连接池
            self._connection_pool = ConnectionPoolManager.get_pool(dsn, self.pool_config)
            self._initialized = True

            logger.info("PostgreSQL连接池初始化成功")

        except Exception as e:
            logger.error(f"连接池初始化失败: {e}")
            raise

    @contextmanager
    def get_connection(self, db_type: DatabaseType, db_name: str, **kwargs):
        """
        获取数据库连接（连接池版本）

        Args:
            db_type: 数据库类型
            db_name: 数据库名
            **kwargs: 额外参数

        Yields:
            数据库连接对象
        """
        if db_type != DatabaseType.POSTGRESQL:
            # 非PostgreSQL数据库，使用原有方式
            conn = self.database_manager.get_connection(db_type, db_name, **kwargs)
            try:
                yield conn
            finally:
                # PostgreSQL不需要手动关闭连接（由连接池管理）
                if db_type != DatabaseType.POSTGRESQL:
                    self.database_manager.return_connection(conn)
        else:
            # PostgreSQL数据库，使用连接池
            pool = self._ensure_pool_initialized()
            with pool.get_connection() as conn:
                # 转换为原有接口期望的格式
                yield conn.connection

    def execute_query(
        self,
        db_type: DatabaseType,
        db_name: str,
        query: str,
        params: Optional[tuple] = None,
        fetch: bool = True,
        **kwargs,
    ) -> Any:
        """
        执行查询（连接池版本）

        Args:
            db_type: 数据库类型
            db_name: 数据库名
            query: SQL查询
            params: 查询参数
            fetch: 是否获取结果
            **kwargs: 额外参数

        Returns:
            查询结果
        """
        if db_type != DatabaseType.POSTGRESQL:
            # 非PostgreSQL数据库，使用原有方式
            conn = self.database_manager.get_connection(db_type, db_name, **kwargs)
            try:
                cursor = conn.cursor()
                cursor.execute(query, params or ())

                if fetch:
                    result = cursor.fetchall()
                else:
                    result = cursor.rowcount

                # PostgreSQL不需要commit/rollback（由调用方管理）
                cursor.close()
                return result

            finally:
                if db_type != DatabaseType.POSTGRESQL:
                    self.database_manager.return_connection(conn)
        else:
            # PostgreSQL数据库，使用连接池
            pool = self._ensure_pool_initialized()
            return pool.execute_query(query, params, fetch)

    def execute_transaction(self, db_type: DatabaseType, db_name: str, queries: List[tuple], **kwargs) -> bool:
        """
        执行事务（连接池版本）

        Args:
            db_type: 数据库类型
            db_name: 数据库名
            queries: 查询列表
            **kwargs: 额外参数

        Returns:
            bool: 是否成功
        """
        if db_type != DatabaseType.POSTGRESQL:
            # 非PostgreSQL数据库，使用原有方式
            return self._execute_transaction_legacy(db_type, db_name, queries, **kwargs)
        else:
            # PostgreSQL数据库，使用连接池
            pool = self._ensure_pool_initialized()
            return pool.execute_transaction(queries)

    def _execute_transaction_legacy(self, db_type: DatabaseType, db_name: str, queries: List[tuple], **kwargs) -> bool:
        """传统事务执行方式"""
        conn = self.database_manager.get_connection(db_type, db_name, **kwargs)
        try:
            cursor = conn.cursor()

            # 关闭自动提交，开始事务
            conn.autocommit = False

            for query, params in queries:
                cursor.execute(query, params or ())

            conn.commit()
            cursor.close()
            return True

        except Exception as e:
            try:
                conn.rollback()
            except Exception:
                pass
            logger.error(f"事务执行失败: {e}")
            return False

        finally:
            self.database_manager.return_connection(conn)

    def get_pool_info(self) -> Optional[Dict[str, Any]]:
        """
        获取连接池信息

        Returns:
            Dict[str, Any]: 连接池统计信息
        """
        if not self._initialized:
            return None

        return self._connection_pool.get_pool_info()

    def health_check(self) -> Optional[Dict[str, Any]]:
        """
        执行连接池健康检查

        Returns:
            Dict[str, Any]: 健康检查结果
        """
        if not self._initialized:
            return None

        return self._connection_pool.health_check()

    def return_connection(self, connection):
        """
        返回连接到池（适配器方法，实际不执行操作）

        Args:
            connection: 数据库连接
        """
        # 连接池模式不需要手动返回连接
        # 这个方法是为了API兼容性保留的
        pass

    def close(self):
        """关闭连接适配器"""
        if self._connection_pool:
            self._connection_pool.close()
            self._connection_pool = None
            self._initialized = False

        logger.info("PostgreSQL连接适配器已关闭")


class EnhancedPostgreSQLRelationalDataSource:
    """
    增强的PostgreSQL关系数据源
    使用连接池管理器提升性能和可靠性
    """

    def __init__(self, connection_pool_size: int = 20, pool_config: Optional[PoolConfig] = None):
        """
        初始化增强的PostgreSQL关系数据源

        Args:
            connection_pool_size: 连接池大小（保持向后兼容）
            pool_config: 连接池详细配置
        """
        # 兼容原有参数
        if pool_config is None:
            pool_config = PoolConfig(
                min_connections=max(2, connection_pool_size // 4),
                max_connections=connection_pool_size,
            )

        # 原有初始化逻辑
        from src.storage.database.database_manager import (
            DatabaseTableManager,
            DatabaseType,
        )
        from src.monitoring import MonitoringDatabase
        from src.data_access import get_data_access_factory, initialize_data_access

        db_manager = DatabaseTableManager()
        monitoring_db = MonitoringDatabase()
        initialize_data_access(db_manager, monitoring_db)

        factory = get_data_access_factory()
        self.pg_access = factory.get_data_access(DatabaseType.POSTGRESQL)

        # 初始化连接适配器
        self.connection_adapter = PostgreSQLConnectionAdapter(db_manager, pool_config)
        self._connection_pool_size = connection_pool_size

        logger.info(f"增强PostgreSQL关系数据源初始化完成 (连接池: {connection_pool_size})")

    # ==================== 连接池管理方法 ====================

    def get_pool_info(self) -> Dict[str, Any]:
        """
        获取连接池信息

        Returns:
            Dict[str, Any]: 连接池统计信息
        """
        pool_info = self.connection_adapter.get_pool_info()
        if pool_info:
            return {
                "pool_size": self._connection_pool_size,
                "actual_size": pool_info["current_active"] + pool_info["pool_size"],
                **pool_info,
            }
        else:
            return {"status": "未初始化"}

    def health_check(self) -> Dict[str, Any]:
        """
        执行连接池健康检查

        Returns:
            Dict[str, Any]: 健康检查结果
        """
        health_status = self.connection_adapter.health_check()
        if health_status:
            return {
                "overall_status": "healthy" if health_status["status"] == "healthy" else "degraded",
                **health_status,
            }
        else:
            return {"status": "未初始化"}

    def close_connection_pool(self):
        """关闭连接池"""
        self.connection_adapter.close()
        logger.info("连接池已关闭")

    # ==================== 重构后的示例方法 ====================

    def get_watchlist_pool_enhanced(
        self, user_id: int, list_type: str = "favorite", include_stock_info: bool = True
    ) -> List[Dict[str, Any]]:
        """
        获取自选股列表（使用连接池版本）

        这是原有方法的增强版本，展示了如何使用连接池
        """
        from src.data_sources.real.query_builder import QueryBuilder

        try:
            # 使用查询构建器 + 连接池
            query_builder = QueryBuilder(self.connection_adapter)

            if include_stock_info:
                query = (
                    query_builder.select(
                        "w.id",
                        "w.user_id",
                        "w.symbol",
                        "w.list_type",
                        "w.note",
                        "w.added_at",
                        "s.name",
                        "s.industry",
                        "s.market",
                        "s.pinyin",
                    )
                    .from_table("watchlist", "w")
                    .left_join("stock_basic_info s", "w.symbol = s.symbol")
                    .where("w.user_id = %s", user_id)
                    .where("w.list_type = %s", list_type)
                    .order_by("w.added_at", "DESC")
                )
            else:
                query = (
                    query_builder.select("id", "user_id", "symbol", "list_type", "note", "added_at")
                    .from_table("watchlist", "w")
                    .where("w.user_id = %s", user_id)
                    .where("list_type = %s", list_type)
                    .order_by("added_at", "DESC")
                )

            result = query.fetch_all()

            logger.info(f"使用连接池获取自选股成功: user_id={user_id}, list_type={list_type}, count={len(result)}")
            return result

        except Exception as e:
            logger.error(f"获取自选股失败 (连接池版本): {e}")
            raise

    def execute_batch_operations(self, operations: List[Dict[str, Any]]) -> bool:
        """
        执行批量操作（事务版本）

        Args:
            operations: 操作列表，每个操作包含 {'sql': str, 'params': tuple}

        Returns:
            bool: 是否成功
        """
        try:
            # 转换为事务查询格式
            queries = [(op["sql"], op.get("params")) for op in operations]

            # 使用连接池执行事务
            success = self.connection_adapter.execute_transaction(DatabaseType.POSTGRESQL, "mystocks", queries)

            logger.info(f"批量操作执行成功: 操作数={len(operations)}, 成功={success}")
            return success

        except Exception as e:
            logger.error(f"批量操作执行失败: {e}")
            return False

    def monitor_connection_pool_performance(self) -> Dict[str, Any]:
        """
        监控连接池性能

        Returns:
            Dict[str, Any]: 性能统计信息
        """
        pool_info = self.get_pool_info()
        health_status = self.health_check()

        return {
            "timestamp": "2025-12-18T11:47:00Z",  # 实际应该使用datetime.now()
            "pool_info": pool_info,
            "health_status": health_status,
            "performance_metrics": {
                "average_wait_time_ms": pool_info.get("average_wait_time", 0) * 1000,
                "failed_request_rate": (
                    pool_info.get("failed_requests", 0) / max(pool_info.get("total_requests", 1), 1.0)
                )
                * 100,
                "connection_utilization": (pool_info.get("current_active", 0) / pool_info.get("max_connections", 1))
                * 100,
            },
        }
