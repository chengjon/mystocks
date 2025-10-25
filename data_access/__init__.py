"""
数据访问层模块

提供4种数据库的统一访问接口:
- TDengine: 高频时序数据
- PostgreSQL: 历史分析数据
- MySQL: 参考数据和元数据
- Redis: 实时热数据

创建日期: 2025-10-11
版本: 1.0.0
"""

from data_access.tdengine_access import TDengineDataAccess
from data_access.postgresql_access import PostgreSQLDataAccess
from data_access.mysql_access import MySQLDataAccess
from data_access.redis_access import RedisDataAccess

__all__ = [
    'TDengineDataAccess',
    'PostgreSQLDataAccess',
    'MySQLDataAccess',
    'RedisDataAccess',
]

__version__ = '1.0.0'
