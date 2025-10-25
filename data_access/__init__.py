"""
数据访问层模块 (Week 3简化后 - PostgreSQL-only)

统一路由所有数据到PostgreSQL+TimescaleDB

创建日期: 2025-10-11
版本: 2.0.0 (Week 3 PostgreSQL-only架构)
"""

from data_access.postgresql_access import PostgreSQLDataAccess

__all__ = [
    "PostgreSQLDataAccess",
]

__version__ = "2.0.0"
