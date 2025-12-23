"""
统一数据访问管理器
集成路由器、优化器、连接管理等所有组件，提供统一的数据访问入口
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from .interfaces.i_data_access import (
    IDataAccess,
    DataQuery,
    QueryResult,
    SaveResult,
    UpdateResult,
    DeleteResult,
    DatabaseType,
    QueryOperation,
    Transaction,
    IsolationLevel,
    DataRecord,
    SaveOptions,
    QueryCriteria,
)
from .routers.query_router import QueryRouter, get_global_router
from .optimizers.query_optimizer import QueryOptimizer, get_global_optimizer
from .capabilities.database_detector import (
    DatabaseCapabilityDetector,
    get_global_detector,
)
from .postgresql_access import PostgreSQLDataAccess
from .tdengine_access import TDengineDataAccess

logger = logging.getLogger(__name__)


class DataAccessMode(Enum):
    """数据访问模式"""

    AUTO = "auto"  # 自动路由
    POSTGRESQL_ONLY = "postgresql_only"
    TDENGINE_ONLY = "tdengine_only"
    FAILOVER = "failover"
    LOAD_BALANCE = "load_balance"


@dataclass
class DataAccessConfig:
    """数据访问配置"""

    mode: DataAccessMode = DataAccessMode.AUTO
    enable_query_optimization: bool = True
    enable_caching: bool = True
    enable_metrics: bool = True
    max_connections_per_db: int = 10
    query_timeout: int = 30
    retry_attempts: int = 3
    retry_delay: float = 1.0
    failover_enabled: bool = True
    health_check_interval: int = 60


@dataclass
class QueryMetrics:
    """查询指标"""

    query_count: int = 0
    total_execution_time: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0
    error_count: int = 0
    database_usage: Dict[DatabaseType, int] = field(default_factory=dict)
    operation_distribution: Dict[QueryOperation, int] = field(default_factory=dict)


@dataclass
class HealthStatus:
    """健康状态"""

    status: str = "healthy"  # healthy, degraded, unhealthy
    databases: Dict[DatabaseType, bool] = field(default_factory=dict)
    last_health_check: Optional[datetime] = None
    issues: List[str] = field(default_factory=list)
    uptime: float = 0.0


class UnifiedDataAccessManager:
    """统一数据访问管理器"""

    def __init__(self, config: Optional[DataAccessConfig] = None):
        self.config = config or DataAccessConfig()
        self.adapters: Dict[DatabaseType, List[IDataAccess]] = {}
        self.router: QueryRouter = get_global_router()
        self.optimizer: QueryOptimizer = get_global_optimizer()
        self.capability_detector: DatabaseCapabilityDetector = get_global_detector()
        self.metrics: QueryMetrics = QueryMetrics()
        self.health_status: HealthStatus = HealthStatus()
        self._start_time = datetime.now()
        self._cache: Dict[str, Any] = {}
        self._connection_managers: Dict[DatabaseType, Any] = {}
        self._shutdown_event = asyncio.Event()

    async def initialize(self):
        """初始化管理器"""
        logger.info("初始化统一数据访问管理器...")

        try:
            # 初始化适配器
            await self._initialize_adapters()

            # 注册适配器到路由器
            await self._register_adapters_to_router()

            # 启动健康检查
            if self.config.health_check_interval > 0:
                asyncio.create_task(self._health_check_loop())

            logger.info("统一数据访问管理器初始化完成")

        except Exception as e:
            logger.error(f"初始化失败: {e}")
            raise

    async def _initialize_adapters(self):
        """初始化适配器"""
        # 初始化PostgreSQL适配器
        try:
            pg_adapter = PostgreSQLDataAccess()
            await pg_adapter.connect()
            self.adapters.setdefault(DatabaseType.POSTGRESQL, []).append(pg_adapter)
            logger.info("PostgreSQL适配器初始化成功")
        except Exception as e:
            logger.warning(f"PostgreSQL适配器初始化失败: {e}")

        # 初始化TDengine适配器
        try:
            td_adapter = TDengineDataAccess()
            await td_adapter.connect()
            self.adapters.setdefault(DatabaseType.TDENGINE, []).append(td_adapter)
            logger.info("TDengine适配器初始化成功")
        except Exception as e:
            logger.warning(f"TDengine适配器初始化失败: {e}")

    async def _register_adapters_to_router(self):
        """注册适配器到路由器"""
        for db_type, adapters in self.adapters.items():
            for adapter in adapters:
                self.router.register_adapter(adapter)

    async def execute_query(self, query: DataQuery) -> QueryResult:
        """执行查询（主要入口点）"""
        start_time = datetime.now()
        self.metrics.query_count += 1

        try:
            # 1. 查询优化
            if self.config.enable_query_optimization:
                target_db = await self._determine_target_database(query)
                optimized_query = await self.optimizer.optimize_query(query, target_db)
            else:
                optimized_query = query

            # 2. 缓存检查
            if self.config.enable_caching:
                cached_result = await self._check_cache(optimized_query)
                if cached_result is not None:
                    self.metrics.cache_hits += 1
                    return cached_result
                else:
                    self.metrics.cache_misses += 1

            # 3. 路由查询
            adapter = await self.router.route_query(optimized_query)

            # 4. 执行查询
            if self.config.mode == DataAccessMode.AUTO:
                result = await adapter.execute_query(optimized_query)
            else:
                result = await self._execute_with_mode(optimized_query, adapter)

            # 5. 缓存结果
            if self.config.enable_caching and result.success:
                await self._cache_result(optimized_query, result)

            # 6. 更新指标
            self._update_metrics(
                adapter.get_database_type(), query.operation, start_time, success=True
            )

            logger.debug(
                f"查询执行成功: {query.table_name}, 耗时: {(datetime.now() - start_time).total_seconds():.3f}s"
            )
            return result

        except Exception as e:
            self._update_metrics(
                DatabaseType.POSTGRESQL, query.operation, start_time, success=False
            )
            self.metrics.error_count += 1

            logger.error(f"查询执行失败: {e}")

            # 尝试故障转移
            if self.config.failover_enabled:
                return await self._execute_with_failover(optimized_query, e)

            raise

    async def _determine_target_database(self, query: DataQuery) -> DatabaseType:
        """确定目标数据库"""
        if self.config.mode == DataAccessMode.POSTGRESQL_ONLY:
            return DatabaseType.POSTGRESQL
        elif self.config.mode == DataAccessMode.TDENGINE_ONLY:
            return DatabaseType.TDENGINE

        # 使用路由器确定
        adapter = await self.router.route_query(query)
        return adapter.get_database_type()

    async def _execute_with_mode(
        self, query: DataQuery, adapter: IDataAccess
    ) -> QueryResult:
        """根据模式执行查询"""
        if self.config.mode in [
            DataAccessMode.POSTGRESQL_ONLY,
            DataAccessMode.TDENGINE_ONLY,
        ]:
            return await adapter.execute_query(query)
        elif self.config.mode == DataAccessMode.LOAD_BALANCE:
            return await self._execute_with_load_balance(query)
        else:
            return await adapter.execute_query(query)

    async def _execute_with_load_balance(self, query: DataQuery) -> QueryResult:
        """负载均衡执行"""
        # 简化的负载均衡：选择负载最轻的适配器
        best_adapter = None
        best_stats = None

        for db_type, adapters in self.adapters.items():
            if not adapters:
                continue

            for adapter in adapters:
                try:
                    stats = await adapter.get_connection_pool_stats()
                    if (
                        best_stats is None
                        or stats.average_response_time
                        < best_stats.average_response_time
                    ):
                        best_stats = stats
                        best_adapter = adapter
                except Exception:
                    continue

        if best_adapter:
            return await best_adapter.execute_query(query)
        else:
            raise ValueError("没有可用的适配器")

    async def _execute_with_failover(
        self, query: DataQuery, original_error: Exception
    ) -> QueryResult:
        """故障转移执行"""
        logger.warning(f"主查询失败，尝试故障转移: {original_error}")

        # 获取替代数据库
        decision = await self.router.route_query(query)
        alternatives = decision.alternative_options

        for alt_db, alt_adapter, reason in alternatives:
            try:
                logger.info(f"尝试故障转移到: {alt_db.value}, 原因: {reason}")
                result = await alt_adapter.execute_query(query)
                logger.info(f"故障转移成功: {alt_db.value}")
                return result
            except Exception as e:
                logger.warning(f"故障转移失败 {alt_db.value}: {e}")
                continue

        raise Exception(f"所有故障转移尝试都失败，原始错误: {original_error}")

    async def fetch_data(self, query: DataQuery) -> QueryResult:
        """获取数据"""
        query.operation = QueryOperation.SELECT
        return await self.execute_query(query)

    async def save_data(
        self, records: List[DataRecord], options: Optional[SaveOptions] = None
    ) -> SaveResult:
        """保存数据"""
        if not records:
            return SaveResult(success=True, inserted_count=0)

        # 按表名分组
        grouped_records = {}
        for record in records:
            table_name = record.table_name
            if table_name not in grouped_records:
                grouped_records[table_name] = []
            grouped_records[table_name].append(record)

        results = []
        for table_name, table_records in grouped_records.items():
            query = DataQuery(operation=QueryOperation.INSERT, table_name=table_name)

            # 路由到合适的数据库
            adapter = await self.router.route_query(query)

            # 转换数据格式
            data_dicts = [record.data for record in table_records]

            # 执行保存
            if hasattr(adapter, "save_data"):
                result = await adapter.save_data(table_records, options)
            else:
                # 使用通用执行方法
                for record_dict in data_dicts:
                    query_result = await adapter.execute_query(query)
                    # 这里需要根据实际适配器实现调整
                    result = SaveResult(success=query_result.success, inserted_count=1)

            results.append(result)

        # 合并结果
        total_inserted = sum(r.inserted_count for r in results)
        total_failed = sum(r.failed_count for r in results)
        success = all(r.success for r in results)

        return SaveResult(
            success=success,
            inserted_count=total_inserted,
            failed_count=total_failed,
            errors=[error for r in results if r.errors for error in r.errors],
        )

    async def update_data(
        self, criteria: QueryCriteria, updates: Dict[str, Any]
    ) -> UpdateResult:
        """更新数据"""
        query = DataQuery(
            operation=QueryOperation.UPDATE,
            table_name=criteria.table_name,
            filters=criteria.filters,
        )

        adapter = await self.router.route_query(query)

        # 这里需要根据实际适配器实现调整
        query_result = await adapter.execute_query(query)

        return UpdateResult(
            success=query_result.success,
            matched_count=query_result.affected_rows or 0,
            updated_count=query_result.affected_rows or 0,
            error=query_result.error,
        )

    async def delete_data(self, criteria: QueryCriteria) -> DeleteResult:
        """删除数据"""
        query = DataQuery(
            operation=QueryOperation.DELETE,
            table_name=criteria.table_name,
            filters=criteria.filters,
        )

        adapter = await self.router.route_query(query)
        query_result = await adapter.execute_query(query)

        return DeleteResult(
            success=query_result.success,
            deleted_count=query_result.affected_rows or 0,
            error=query_result.error,
        )

    async def batch_fetch(self, queries: List[DataQuery]) -> List[QueryResult]:
        """批量获取数据"""
        tasks = [self.fetch_data(query) for query in queries]
        return await asyncio.gather(*tasks, return_exceptions=True)

    async def batch_save(
        self,
        record_batches: List[List[DataRecord]],
        options: Optional[SaveOptions] = None,
    ) -> List[SaveResult]:
        """批量保存数据"""
        tasks = [self.save_data(batch, options) for batch in record_batches]
        return await asyncio.gather(*tasks, return_exceptions=True)

    async def begin_transaction(
        self, isolation_level: IsolationLevel = IsolationLevel.READ_COMMITTED
    ) -> Transaction:
        """开始事务"""
        # 选择支持事务的数据库（主要是PostgreSQL）
        query = DataQuery(operation=QueryOperation.SELECT, table_name="dummy")
        adapter = await self.router.route_query(query)

        if adapter.supports_feature("transactions"):
            return await adapter.begin_transaction(isolation_level)
        else:
            raise NotImplementedError(
                f"数据库 {adapter.get_database_type().value} 不支持事务"
            )

    async def execute_in_transaction(
        self,
        operations: List[Callable],
        isolation_level: IsolationLevel = IsolationLevel.READ_COMMITTED,
    ) -> List[Any]:
        """在事务中执行多个操作"""
        transaction = await self.begin_transaction(isolation_level)
        results = []

        try:
            for operation in operations:
                result = await operation()
                results.append(result)

            await self.commit_transaction(transaction)
            return results

        except Exception:
            await self.rollback_transaction(transaction)
            raise

    async def commit_transaction(self, transaction: Transaction) -> bool:
        """提交事务"""
        return await transaction.commit()

    async def rollback_transaction(self, transaction: Transaction) -> bool:
        """回滚事务"""
        return await transaction.rollback()

    async def _check_cache(self, query: DataQuery) -> Optional[QueryResult]:
        """检查缓存"""
        if not self.config.enable_caching:
            return None

        cache_key = self._generate_cache_key(query)
        return self._cache.get(cache_key)

    async def _cache_result(self, query: DataQuery, result: QueryResult):
        """缓存结果"""
        if not self.config.enable_caching:
            return

        cache_key = self._generate_cache_key(query)
        self._cache[cache_key] = result

        # 简单的缓存大小限制
        if len(self._cache) > 1000:
            # 删除最旧的一半缓存
            items_to_remove = list(self._cache.keys())[:500]
            for key in items_to_remove:
                del self._cache[key]

    def _generate_cache_key(self, query: DataQuery) -> str:
        """生成缓存键"""
        import hashlib
        import json

        # 将查询对象序列化为字符串
        query_dict = {
            "table": query.table_name,
            "operation": query.operation.value,
            "columns": query.columns,
            "filters": query.filters,
            "limit": query.limit,
            "offset": query.offset,
        }

        query_str = json.dumps(query_dict, sort_keys=True)
        return hashlib.md5(query_str.encode()).hexdigest()

    def _update_metrics(
        self,
        db_type: DatabaseType,
        operation: QueryOperation,
        start_time: datetime,
        success: bool,
    ):
        """更新指标"""
        if not self.config.enable_metrics:
            return

        execution_time = (datetime.now() - start_time).total_seconds()
        self.metrics.total_execution_time += execution_time

        # 更新数据库使用统计
        self.metrics.database_usage[db_type] = (
            self.metrics.database_usage.get(db_type, 0) + 1
        )

        # 更新操作分布
        self.metrics.operation_distribution[operation] = (
            self.metrics.operation_distribution.get(operation, 0) + 1
        )

        if not success:
            self.metrics.error_count += 1

    async def _health_check_loop(self):
        """健康检查循环"""
        while not self._shutdown_event.is_set():
            try:
                await self.perform_health_check()
                await asyncio.sleep(self.config.health_check_interval)
            except Exception as e:
                logger.error(f"健康检查失败: {e}")
                await asyncio.sleep(10)  # 出错时短暂等待

    async def perform_health_check(self) -> Dict[str, Any]:
        """执行健康检查"""
        health_info = {
            "status": "healthy",
            "databases": {},
            "timestamp": datetime.now().isoformat(),
            "uptime": (datetime.now() - self._start_time).total_seconds(),
        }

        all_healthy = True

        for db_type, adapters in self.adapters.items():
            db_healthy = False
            for adapter in adapters:
                try:
                    is_healthy = await adapter.health_check()
                    if is_healthy:
                        db_healthy = True
                        break
                except Exception as e:
                    logger.warning(f"健康检查失败 {db_type.value}: {e}")

            health_info["databases"][db_type.value] = db_healthy
            if not db_healthy:
                all_healthy = False

        # 更新健康状态
        self.health_status.status = "healthy" if all_healthy else "degraded"
        self.health_status.databases = {
            db_type: status for db_type, status in health_info["databases"].items()
        }
        self.health_status.last_health_check = datetime.now()

        return health_info

    async def get_database_info(self) -> Dict[str, Any]:
        """获取数据库信息"""
        db_info = {}

        for db_type, adapters in self.adapters.items():
            if adapters:
                try:
                    info = await adapters[0].get_database_info()
                    db_info[db_type.value] = info
                except Exception as e:
                    logger.warning(f"获取数据库信息失败 {db_type.value}: {e}")
                    db_info[db_type.value] = {"error": str(e)}

        return db_info

    def get_metrics(self) -> QueryMetrics:
        """获取查询指标"""
        return self.metrics

    def get_routing_metrics(self) -> Dict[str, Any]:
        """获取路由指标"""
        return self.router.get_routing_metrics()

    def get_optimization_statistics(self) -> Dict[str, Any]:
        """获取优化统计"""
        return self.optimizer.get_optimization_statistics()

    async def shutdown(self):
        """关闭管理器"""
        logger.info("关闭统一数据访问管理器...")

        # 设置关闭事件
        self._shutdown_event.set()

        # 关闭所有适配器
        for db_type, adapters in self.adapters.items():
            for adapter in adapters:
                try:
                    await adapter.disconnect()
                    logger.info(f"已断开 {db_type.value} 适配器连接")
                except Exception as e:
                    logger.warning(f"断开连接失败 {db_type.value}: {e}")

        # 清空缓存
        self._cache.clear()

        logger.info("统一数据访问管理器已关闭")

    def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.shutdown()


# 全局管理器实例
_global_manager = None


def get_global_manager(
    config: Optional[DataAccessConfig] = None,
) -> UnifiedDataAccessManager:
    """获取全局管理器实例"""
    global _global_manager
    if _global_manager is None:
        _global_manager = UnifiedDataAccessManager(config)
    return _global_manager
