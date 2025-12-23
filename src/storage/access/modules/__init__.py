#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MyStocks 量化交易数据管理系统 - 数据访问模块

模块化拆分的数据访问层实现

作者: MyStocks项目组
版本: v2.0 重构版
日期: 2025-11-25
"""

# 导入基础类和函数
from .base import (
    IDataAccessLayer,
    normalize_dataframe,
    validate_time_series_data,
    get_database_name_from_classification,
)

# 导入数据库特定实现
from .tdengine import TDengineDataAccess
from .postgresql import PostgreSQLDataAccess
from .mysql import MySQLDataAccess
from .redis import RedisDataAccess

# 向后兼容
IDataAccess = IDataAccessLayer
TDengineAccess = TDengineDataAccess
PostgreSQLAccess = PostgreSQLDataAccess
MySQLAccess = MySQLDataAccess
RedisAccess = RedisDataAccess

# 导出公共接口
__all__ = [
    "IDataAccessLayer",
    "normalize_dataframe",
    "validate_time_series_data",
    "get_database_name_from_classification",
    "TDengineDataAccess",
    "PostgreSQLDataAccess",
    "MySQLDataAccess",
    "RedisDataAccess",
    # 向后兼容别名
    "IDataAccess",
    "TDengineAccess",
    "PostgreSQLAccess",
    "MySQLAccess",
    "RedisAccess",
]
