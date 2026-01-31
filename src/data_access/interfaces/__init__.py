"""
数据访问接口包
统一数据访问相关的接口定义
"""

from .i_data_access import (
    DatabaseInfo,
    DatabaseType,
    DataQuery,
    DataRecord,
    DeleteResult,
    IDataAccess,
    IDataMapper,
    IQueryOptimizer,
    IQueryRouter,
    IsolationLevel,
    PoolStats,
    QueryCriteria,
    QueryOperation,
    QueryResult,
    SaveOptions,
    SaveResult,
    TableSchema,
    Transaction,
    UpdateResult,
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
