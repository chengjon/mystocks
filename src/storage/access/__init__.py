#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MyStocks 量化交易数据管理系统 - 数据访问层统一导出

向后兼容性模块，提供原始data_access.py的统一导入接口

作者: MyStocks项目组
版本: v2.0 重构版
日期: 2025-11-25
"""

# 导入所有主要类和函数，提供向后兼容性

# 导入基础层
from .base import IDataAccessLayer
from .base import get_database_name_from_classification
from .base import normalize_dataframe
from .base import validate_data_for_classification
from .base import validate_time_series_data

# 导入数据访问器
from .tdengine import TDengineDataAccess
from .postgresql import PostgreSQLDataAccess
from .akshare import AkshareDataAccess

# 保持向后兼容性，将原始类和函数重新导出
# 这样用户可以继续从src.data_access导入，但实际使用新的模块化实现

__all__ = [
    # 基础类和函数
    "IDataAccessLayer",
    "get_database_name_from_classification",
    "normalize_dataframe",
    "validate_data_for_classification",
    "validate_time_series_data",
    # 数据访问器
    "TDengineDataAccess",
    "PostgreSQLDataAccess",
    "AkshareDataAccess",
]


# 为了向后兼容性，提供单例的数据库管理器
class _DataAccessManager:
    """数据访问管理器 - 提供统一的数据访问入口"""

    def __init__(self):
        """初始化数据访问管理器"""
        self._monitordb = None
        self._tdengine_access = None
        self._postgresql_access = None
        self._akshare_access = None

    def initialize(self, monitoring_db):
        """初始化数据访问管理器"""
        self._monitordb = monitoring_db
        self._tdengine_access = TDengineDataAccess(monitoring_db)
        self._postgresql_access = PostgreSQLDataAccess(monitoring_db)
        self._akshare_access = AkshareDataAccess(monitoring_db)

    def get_data_access(self, database_type):
        """获取特定数据库类型的数据访问器"""
        if self._monitordb is None:
            from src.monitoring.monitoring_database import MonitoringDatabase

            self._monitordb = MonitoringDatabase()
            self.initialize(self._monitordb)

        if database_type == "TDengine" or database_type == "TDENGINE":
            return self._tdengine_access
        elif database_type == "PostgreSQL" or database_type == "POSTGRESQL":
            return self._postgresql_access
        elif database_type == "Akshare" or database_type == "AKSHARE":
            return self._akshare_access
        else:
            raise ValueError(f"未知的数据库类型: {database_type}")


# 创建全局数据访问管理器实例
_data_access_manager = _DataAccessManager()


def get_data_access(database_type):
    """获取数据访问器"""
    return _data_access_manager.get_data_access(database_type)


# 为了向后兼容性，提供全局函数
def get_database_name_from_classification_global(classification):
    """获取数据库名称 - 全局函数"""
    return get_database_name_from_classification(classification)


def normalize_dataframe_global(data):
    """标准化DataFrame - 全局函数"""
    return normalize_dataframe(data)
