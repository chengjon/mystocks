"""数据访问层包"""
from .interface import IDataAccessLayer
from .tdengine_access import TDengineDataAccess
from .postgresql_access import PostgreSQLDataAccess

__all__ = ["IDataAccessLayer", "TDengineDataAccess", "PostgreSQLDataAccess"]
