"""
数据访问接口包
统一数据访问相关的接口定义
"""

from .i_data_access import (
    IDataAccess,
    DatabaseType,
    QueryOperation,
    IsolationLevel,
    DataQuery,
    QueryCriteria,
    DataRecord,
    SaveOptions,
    QueryResult,
    SaveResult,
    UpdateResult,
    DeleteResult,
    TableSchema,
    DatabaseInfo,
    PoolStats,
    Transaction,
    IQueryRouter,
    IQueryOptimizer,
    IDataMapper,
)

__all__ = [
    "IDataAccess",
    "DatabaseType",
    "QueryOperation",
    "IsolationLevel",
    "DataQuery",
    "QueryCriteria",
    "DataRecord",
    "SaveOptions",
    "QueryResult",
    "SaveResult",
    "UpdateResult",
    "DeleteResult",
    "TableSchema",
    "DatabaseInfo",
    "PoolStats",
    "Transaction",
    "IQueryRouter",
    "IQueryOptimizer",
    "IDataMapper",
]
