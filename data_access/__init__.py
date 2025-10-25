"""
数据访问层模块

提供2种数据库的统一访问接口:
- TDengine: 高频时序数据
- PostgreSQL: 历史分析数据、参考数据和元数据

创建日期: 2025-10-11
版本: 2.0.0 (简化为TDengine + PostgreSQL双数据库架构)
"""

from data_access.tdengine_access import TDengineDataAccess
from data_access.postgresql_access import PostgreSQLDataAccess

__all__ = [
    "TDengineDataAccess",
    "PostgreSQLDataAccess",
]

__version__ = "2.0.0"
