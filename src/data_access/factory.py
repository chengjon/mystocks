#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据访问层工厂模式
根据数据类型和配置创建合适的数据访问器实例

作者: MyStocks项目组
版本: v2.0 重构版
日期: 2025-12-16
"""

import logging

from .interfaces import IDataAccess as IDataAccessLayer
from .tdengine_access import TDengineDataAccess
from .postgresql_access import PostgreSQLDataAccess
from src.storage.database.database_manager import DatabaseTableManager, DatabaseType
from src.monitoring import MonitoringDatabase

logger = logging.getLogger("MyStocksDataAccessFactory")


class DataAccessFactory:
    """数据访问器工厂类"""

    def __init__(self):
        """初始化工厂"""
        self._db_manager = None
        self._monitoring_db = None
        self._tdengine_access = None
        self._postgresql_access = None

    def initialize(self, db_manager: DatabaseTableManager, monitoring_db: MonitoringDatabase) -> None:
        """
        初始化工厂

        Args:
            db_manager: 数据库表管理器
            monitoring_db: 监控数据库
        """
        self._db_manager = db_manager
        self._monitoring_db = monitoring_db

        # 预创建访问器实例
        self._tdengine_access = TDengineDataAccess(db_manager, monitoring_db)
        self._postgresql_access = PostgreSQLDataAccess(db_manager, monitoring_db)

    def get_data_access(self, database_type: DatabaseType, classification=None) -> IDataAccessLayer:
        """
        根据数据库类型获取数据访问器

        Args:
            database_type: 数据库类型
            classification: 数据分类（可选，用于路由决策）

        Returns:
            IDataAccessLayer: 数据访问器实例
        """
        if not self._db_manager:
            raise RuntimeError("Factory not initialized. Call initialize() first.")

        if database_type == DatabaseType.TDENGINE:
            return self._tdengine_access
        elif database_type == DatabaseType.POSTGRESQL:
            return self._postgresql_access
        else:
            raise ValueError(f"Unsupported database type: {database_type}")

    def get_timeseries_access(self) -> IDataAccessLayer:
        """
        获取时序数据访问器（TDengine）

        Returns:
            IDataAccessLayer: TDengine数据访问器
        """
        return self.get_data_access(DatabaseType.TDENGINE)

    def get_relational_access(self) -> IDataAccessLayer:
        """
        获取关系数据访问器（PostgreSQL）

        Returns:
            IDataAccessLayer: PostgreSQL数据访问器
        """
        return self.get_data_access(DatabaseType.POSTGRESQL)

    def smart_routing_access(self, classification, symbol: str = None, data_volume: str = "small") -> IDataAccessLayer:
        """
        智能路由：根据数据特征选择最合适的数据库

        Args:
            classification: 数据分类
            symbol: 股票代码
            data_volume: 数据量估算 (small/medium/large)

        Returns:
            IDataAccessLayer: 最合适的数据访问器
        """
        # 路由决策逻辑
        if self._should_use_tdengine(classification, data_volume):
            logger.info(f"使用TDengine处理: {classification} - {symbol}")
            return self.get_timeseries_access()
        else:
            logger.info(f"使用PostgreSQL处理: {classification} - {symbol}")
            return self.get_relational_access()

    def _should_use_tdengine(self, classification, data_volume: str) -> bool:
        """
        判断是否应该使用TDengine

        Args:
            classification: 数据分类
            data_volume: 数据量估算

        Returns:
            bool: 是否使用TDengine
        """
        # 时序数据和高频数据优先使用TDengine
        timeseries_classifications = ["TICK_DATA", "MINUTE_KLINE", "REALTIME_DATA"]

        # 大量数据使用TDengine
        if data_volume in ["medium", "large"]:
            return True

        # 时序数据使用TDengine
        if hasattr(classification, "name") and classification.name in timeseries_classifications:
            return True

        return False

    def check_all_connections(self) -> dict:
        """
        检查所有数据源连接状态

        Returns:
            dict: 连接状态字典
        """
        status = {}

        try:
            # 检查TDengine连接
            if self._tdengine_access:
                status["tdengine"] = self._tdengine_access.check_connection()
            else:
                status["tdengine"] = False

            # 检查PostgreSQL连接
            if self._postgresql_access:
                status["postgresql"] = self._postgresql_access.check_connection()
            else:
                status["postgresql"] = False

        except Exception as e:
            logger.error(f"检查数据库连接状态失败: {str(e)}")
            status["error"] = str(e)

        return status

    def get_connection_status(self) -> dict:
        """
        获取连接状态（向后兼容方法）

        Returns:
            dict: 连接状态字典
        """
        return self.check_all_connections()

    def create_data_access_for_test(self, database_type: DatabaseType) -> IDataAccessLayer:
        """
        为测试创建数据访问器（简化版）

        Args:
            database_type: 数据库类型

        Returns:
            IDataAccessLayer: 数据访问器实例
        """
        if not self._db_manager:
            from src.storage.database.database_manager import DatabaseTableManager
            from src.monitoring import MonitoringDatabase

            # 创建测试用的数据库管理器
            self._db_manager = DatabaseTableManager()
            self._monitoring_db = MonitoringDatabase()

            # 重新初始化访问器
            self._tdengine_access = TDengineDataAccess(self._db_manager, self._monitoring_db)
            self._postgresql_access = PostgreSQLDataAccess(self._db_manager, self._monitoring_db)

        return self.get_data_access(database_type)


# 全局工厂实例
_data_access_factory = DataAccessFactory()


def get_data_access_factory() -> DataAccessFactory:
    """
    获取全局数据访问工厂实例

    Returns:
        DataAccessFactory: 工厂实例
    """
    return _data_access_factory


def initialize_data_access(db_manager: DatabaseTableManager, monitoring_db: MonitoringDatabase) -> None:
    """
    初始化全局数据访问工厂

    Args:
        db_manager: 数据库表管理器
        monitoring_db: 监控数据库
    """
    _data_access_factory.initialize(db_manager, monitoring_db)


def get_data_access(database_type: DatabaseType, classification=None) -> IDataAccessLayer:
    """
    获取数据访问器（全局工厂）

    Args:
        database_type: 数据库类型
        classification: 数据分类（可选）

    Returns:
        IDataAccessLayer: 数据访问器实例
    """
    return _data_access_factory.get_data_access(database_type, classification)


def smart_routing_access(classification, symbol: str = None, data_volume: str = "small") -> IDataAccessLayer:
    """
    智能路由获取数据访问器（全局工厂）

    Args:
        classification: 数据分类
        symbol: 股票代码
        data_volume: 数据量估算

    Returns:
        IDataAccessLayer: 最合适的数据访问器
    """
    return _data_access_factory.smart_routing_access(classification, symbol, data_volume)
