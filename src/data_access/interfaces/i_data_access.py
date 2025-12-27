"""
统一数据访问接口定义
为不同数据库提供一致的访问接口抽象
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, Callable, TypeVar
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

T = TypeVar("T")


class DatabaseType(Enum):
    """数据库类型枚举"""

    POSTGRESQL = "postgresql"
    TDENGINE = "tdengine"
    MYSQL = "mysql"
    MONGODB = "mongodb"


class QueryOperation(Enum):
    """查询操作类型"""

    SELECT = "select"
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"
    UPSERT = "upsert"
    BATCH_INSERT = "batch_insert"
    BATCH_UPDATE = "batch_update"


class IsolationLevel(Enum):
    """事务隔离级别"""

    READ_UNCOMMITTED = "read_uncommitted"
    READ_COMMITTED = "read_committed"
    REPEATABLE_READ = "repeatable_read"
    SERIALIZABLE = "serializable"


@dataclass
class DataQuery:
    """统一数据查询对象"""

    operation: QueryOperation
    table_name: str
    columns: Optional[List[str]] = None
    filters: Optional[Dict[str, Any]] = None
    parameters: Optional[Dict[str, Any]] = None
    order_by: Optional[List[str]] = None
    group_by: Optional[List[str]] = None
    having: Optional[Dict[str, Any]] = None
    limit: Optional[int] = None
    offset: Optional[int] = None
    join_clauses: Optional[List[Dict[str, Any]]] = None
    window_functions: Optional[List[Dict[str, Any]]] = None


@dataclass
class QueryCriteria:
    """查询条件对象"""

    table_name: str
    filters: Dict[str, Any]
    joins: Optional[List[Dict[str, Any]]] = None
    subqueries: Optional[Dict[str, Any]] = None


@dataclass
class DataRecord:
    """数据记录对象"""

    table_name: str
    data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None
    timestamp: Optional[datetime] = None


@dataclass
class SaveOptions:
    """保存选项配置"""

    batch_size: int = 1000
    upsert_mode: bool = False
    conflict_resolution: str = "ignore"  # ignore, update, error
    validate_data: bool = True
    return_ids: bool = False
    transactional: bool = True


@dataclass
class QueryResult:
    """查询结果对象"""

    success: bool
    data: List[Dict[str, Any]]
    total_count: Optional[int] = None
    execution_time: Optional[float] = None
    affected_rows: Optional[int] = None
    query_plan: Optional[Dict[str, Any]] = None
    warnings: Optional[List[str]] = None
    error: Optional[str] = None


@dataclass
class SaveResult:
    """保存结果对象"""

    success: bool
    inserted_count: int = 0
    updated_count: int = 0
    failed_count: int = 0
    inserted_ids: Optional[List[Any]] = None
    errors: Optional[List[str]] = None
    execution_time: Optional[float] = None


@dataclass
class UpdateResult:
    """更新结果对象"""

    success: bool
    matched_count: int = 0
    updated_count: int = 0
    execution_time: Optional[float] = None
    error: Optional[str] = None


@dataclass
class DeleteResult:
    """删除结果对象"""

    success: bool
    deleted_count: int = 0
    execution_time: Optional[float] = None
    error: Optional[str] = None


@dataclass
class TableSchema:
    """表结构信息"""

    table_name: str
    columns: List[Dict[str, Any]]
    indexes: List[Dict[str, Any]]
    constraints: List[Dict[str, Any]]
    table_type: str  # table, view, materialized_view
    partition_info: Optional[Dict[str, Any]] = None


@dataclass
class DatabaseInfo:
    """数据库信息"""

    database_type: DatabaseType
    version: str
    host: str
    port: int
    database_name: str
    available_features: List[str]
    limitations: List[str]
    performance_characteristics: Dict[str, Any]


@dataclass
class PoolStats:
    """连接池统计信息"""

    total_connections: int
    active_connections: int
    idle_connections: int
    waiting_requests: int
    average_response_time: float
    connection_utilization: float


class Transaction(ABC):
    """抽象事务接口"""

    @abstractmethod
    def commit(self) -> bool:
        """提交事务"""
        pass

    @abstractmethod
    def rollback(self) -> bool:
        """回滚事务"""
        pass

    @abstractmethod
    def is_active(self) -> bool:
        """检查事务是否活跃"""
        pass

    @abstractmethod
    def get_transaction_id(self) -> str:
        """获取事务ID"""
        pass


class IDataAccess(ABC):
    """统一数据访问接口"""

    @abstractmethod
    async def connect(self) -> bool:
        """建立数据库连接"""
        pass

    @abstractmethod
    async def disconnect(self) -> bool:
        """断开数据库连接"""
        pass

    @abstractmethod
    async def is_connected(self) -> bool:
        """检查连接状态"""
        pass

    @abstractmethod
    async def execute_query(self, query: DataQuery) -> QueryResult:
        """执行单个查询"""
        pass

    @abstractmethod
    async def execute_raw_query(self, sql: str, parameters: Optional[Dict[str, Any]] = None) -> QueryResult:
        """执行原生SQL查询"""
        pass

    @abstractmethod
    async def fetch_data(self, query: DataQuery) -> QueryResult:
        """获取数据 (SELECT操作)"""
        pass

    @abstractmethod
    async def save_data(self, records: List[DataRecord], options: Optional[SaveOptions] = None) -> SaveResult:
        """保存数据 (INSERT/UPDATE操作)"""
        pass

    @abstractmethod
    async def update_data(self, criteria: QueryCriteria, updates: Dict[str, Any]) -> UpdateResult:
        """更新数据"""
        pass

    @abstractmethod
    async def delete_data(self, criteria: QueryCriteria) -> DeleteResult:
        """删除数据"""
        pass

    @abstractmethod
    async def batch_fetch(self, queries: List[DataQuery]) -> List[QueryResult]:
        """批量获取数据"""
        pass

    @abstractmethod
    async def batch_save(
        self,
        record_batches: List[List[DataRecord]],
        options: Optional[SaveOptions] = None,
    ) -> List[SaveResult]:
        """批量保存数据"""
        pass

    @abstractmethod
    async def get_table_schema(self, table_name: str) -> TableSchema:
        """获取表结构信息"""
        pass

    @abstractmethod
    async def get_database_info(self) -> DatabaseInfo:
        """获取数据库信息"""
        pass

    @abstractmethod
    async def begin_transaction(self, isolation_level: IsolationLevel = IsolationLevel.READ_COMMITTED) -> Transaction:
        """开始事务"""
        pass

    @abstractmethod
    async def commit_transaction(self, transaction: Transaction) -> bool:
        """提交事务"""
        pass

    @abstractmethod
    async def rollback_transaction(self, transaction: Transaction) -> bool:
        """回滚事务"""
        pass

    @abstractmethod
    async def execute_in_transaction(
        self,
        operations: List[Callable],
        isolation_level: IsolationLevel = IsolationLevel.READ_COMMITTED,
    ) -> List[Any]:
        """在事务中执行多个操作"""
        pass

    @abstractmethod
    async def execute_query_with_stats(self, query: DataQuery) -> QueryResult:
        """执行查询并返回性能统计"""
        pass

    @abstractmethod
    async def get_connection_pool_stats(self) -> PoolStats:
        """获取连接池统计信息"""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """健康检查"""
        pass

    @abstractmethod
    def get_database_type(self) -> DatabaseType:
        """获取数据库类型"""
        pass

    @abstractmethod
    def supports_feature(self, feature: str) -> bool:
        """检查是否支持特定功能"""
        pass

    @abstractmethod
    def get_optimization_hints(self, query: DataQuery) -> Dict[str, Any]:
        """获取查询优化提示"""
        pass


class DatabaseCapabilities(ABC):
    """数据库能力抽象接口"""

    @abstractmethod
    def get_supported_operations(self) -> List[QueryOperation]:
        """获取支持的操作类型"""
        pass

    @abstractmethod
    def get_supported_data_types(self) -> List[str]:
        """获取支持的数据类型"""
        pass

    @abstractmethod
    def get_index_types(self) -> List[str]:
        """获取支持的索引类型"""
        pass

    @abstractmethod
    def supports_transactions(self) -> bool:
        """是否支持事务"""
        pass

    @abstractmethod
    def supports_concurrent_operations(self) -> bool:
        """是否支持并发操作"""
        pass

    @abstractmethod
    def get_batch_size_recommendations(self) -> Dict[str, int]:
        """获取批处理大小建议"""
        pass

    @abstractmethod
    def get_performance_characteristics(self) -> Dict[str, Any]:
        """获取性能特征"""
        pass


class IQueryRouter(ABC):
    """查询路由器接口"""

    @abstractmethod
    async def route_query(self, query: DataQuery) -> IDataAccess:
        """路由查询到合适的数据访问实例"""
        pass

    @abstractmethod
    async def route_operation(self, operation: QueryOperation, table_name: str) -> IDataAccess:
        """路由操作到合适的数据库"""
        pass

    @abstractmethod
    def add_routing_rule(self, rule: Callable[[DataQuery], bool], target: IDataAccess):
        """添加路由规则"""
        pass

    @abstractmethod
    def remove_routing_rule(self, rule: Callable):
        """移除路由规则"""
        pass


class IQueryOptimizer(ABC):
    """查询优化器接口"""

    @abstractmethod
    async def optimize_query(self, query: DataQuery, target_database: DatabaseType) -> DataQuery:
        """优化查询"""
        pass

    @abstractmethod
    async def analyze_query_plan(self, query: DataQuery, target_database: DatabaseType) -> Dict[str, Any]:
        """分析查询执行计划"""
        pass

    @abstractmethod
    async def suggest_indexes(self, query: DataQuery, target_database: DatabaseType) -> List[Dict[str, Any]]:
        """建议索引"""
        pass

    @abstractmethod
    async def estimate_query_cost(self, query: DataQuery, target_database: DatabaseType) -> float:
        """估算查询成本"""
        pass


class IDataMapper(ABC):
    """数据映射器接口"""

    @abstractmethod
    def map_row(self, row: Union[List, Dict[str, Any]]) -> Dict[str, Any]:
        """映射单行数据"""
        pass

    @abstractmethod
    def map_rows(self, rows: List[Union[List, Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """映射多行数据"""
        pass

    @abstractmethod
    def get_target_schema(self) -> Dict[str, Any]:
        """获取目标数据模式"""
        pass

    @abstractmethod
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """验证数据"""
        pass
