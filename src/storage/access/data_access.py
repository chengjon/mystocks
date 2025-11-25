#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MyStocks 量化交易数据管理系统 - 统一数据访问层

向后兼容的接口，包含模块化拆分的数据访问器

设计理念：
1. 5大数据分类：市场数据、参考数据、衍生数据、交易数据、元数据
2. 自动路由：根据数据特性自动选择最适合的数据库
3. TDengine为高频数据核心：专门处理Tick和分钟级数据
4. 监控集成：所有操作自动记录到监控数据库
5. 配置驱动：表结构和访问模式完全由配置文件管理

作者: MyStocks项目组
版本: v2.0 重构版
日期: 2025-11-25
"""

# 为了向后兼容，从模块中导入所有类
from .modules.base import (
    IDataAccessLayer as IDataAccessLayer,
    normalize_dataframe,
    validate_time_series_data,
    get_database_name_from_classification,
)

from .modules.tdengine import TDengineDataAccess
from .modules.postgresql import PostgreSQLDataAccess
from .modules.mysql import MySQLDataAccess
from .modules.redis import RedisDataAccess

# 为了向后兼容，提供别名
IDataAccess = IDataAccessLayer
TDengineAccess = TDengineDataAccess
PostgreSQLAccess = PostgreSQLDataAccess
MySQLAccess = MySQLDataAccess
RedisAccess = RedisDataAccess

# 导出所有接口和类
__all__ = [
    # 基础类和函数
    "IDataAccessLayer",
    "normalize_dataframe",
    "validate_time_series_data",
    "get_database_name_from_classification",
    
    # 数据访问器实现
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