"""
Storage模块 - 数据存储和访问层

提供统一的数据存储访问接口：
- 数据库连接管理
- 连接池管理
- 数据访问层
"""

from .database.connection_manager import DatabaseConnectionManager

__all__ = ["DatabaseConnectionManager"]
