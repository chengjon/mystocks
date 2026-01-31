"""
数据访问层模块

提供2种数据库的统一访问接口:
- TDengine: 高频时序数据
- PostgreSQL: 历史分析数据、参考数据和元数据

创建日期: 2025-10-11
版本: 2.0.0 (简化为TDengine + PostgreSQL双数据库架构)
"""

from .postgresql_access import PostgreSQLDataAccess
from .tdengine_access import TDengineDataAccess
from .factory import (
    DataAccessFactory,
    get_data_access_factory,
    initialize_data_access,
    get_data_access,
    smart_routing_access,
)

__all__ = [
    "TDengineDataAccess",
    "PostgreSQLDataAccess",
    "DataAccessFactory",
    "get_data_access_factory",
    "initialize_data_access",
    "get_data_access",
    "smart_routing_access",
]

__version__ = "2.0.0"
