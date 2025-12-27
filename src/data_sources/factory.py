"""
数据源工厂模块

本模块实现工厂模式，提供统一的数据源实例创建和管理机制。
支持通过环境变量配置切换不同的数据源实现（Mock/Database/API）。

核心功能：
1. 数据源实例化和生命周期管理
2. 环境变量驱动的配置管理
3. 数据源注册和发现机制
4. 单例模式优化避免重复实例化

作者: MyStocks Backend Team
创建日期: 2025-11-21
版本: 1.0.0
"""

import os
from typing import Optional, Dict, Type
from threading import Lock
from functools import wraps

from src.interfaces.timeseries_data_source import ITimeSeriesDataSource
from src.interfaces.relational_data_source import IRelationalDataSource
from src.interfaces.business_data_source import IBusinessDataSource


# ==================== 配置常量 ====================

# 环境变量名称
ENV_TIMESERIES_SOURCE = "TIMESERIES_DATA_SOURCE"
ENV_RELATIONAL_SOURCE = "RELATIONAL_DATA_SOURCE"
ENV_BUSINESS_SOURCE = "BUSINESS_DATA_SOURCE"

# 默认数据源类型
DEFAULT_TIMESERIES_SOURCE = "mock"
DEFAULT_RELATIONAL_SOURCE = "mock"
DEFAULT_BUSINESS_SOURCE = "mock"

# 支持的数据源类型
SUPPORTED_TIMESERIES_TYPES = ["mock", "tdengine", "api"]
SUPPORTED_RELATIONAL_TYPES = ["mock", "postgresql"]
SUPPORTED_BUSINESS_TYPES = ["mock", "composite"]


# ==================== 异常定义 ====================


class DataSourceFactoryException(Exception):
    """数据源工厂异常基类"""

    def __init__(self, message: str, error_code: str = "FACTORY_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class UnsupportedDataSourceType(DataSourceFactoryException):
    """不支持的数据源类型异常"""

    def __init__(self, source_type: str, supported_types: list):
        message = f"Unsupported data source type: '{source_type}'. " f"Supported types: {', '.join(supported_types)}"
        super().__init__(message, error_code="UNSUPPORTED_TYPE")


class DataSourceNotRegistered(DataSourceFactoryException):
    """数据源未注册异常"""

    def __init__(self, source_type: str, category: str):
        message = (
            f"Data source '{source_type}' not registered for category '{category}'. "
            f"Please register the implementation before use."
        )
        super().__init__(message, error_code="NOT_REGISTERED")


# ==================== 单例装饰器 ====================


def singleton(cls):
    """
    单例模式装饰器

    确保类只有一个实例，避免重复创建数据源连接。
    使用线程锁保证线程安全。
    """
    instances = {}
    lock = Lock()

    @wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            with lock:
                # Double-checked locking
                if cls not in instances:
                    instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


# ==================== 数据源工厂 ====================


@singleton
class DataSourceFactory:
    """
    数据源工厂类

    提供统一的数据源实例创建接口，支持：
    1. 环境变量驱动的数据源类型配置
    2. 数据源实现的动态注册和发现
    3. 单例模式管理，避免重复实例化
    4. 自动降级和容错机制

    使用示例:
        # 获取时序数据源
        ts_source = DataSourceFactory.get_timeseries_source()
        quotes = ts_source.get_realtime_quotes(symbols=["600000"])

        # 获取关系数据源
        rel_source = DataSourceFactory.get_relational_source()
        watchlist = rel_source.get_watchlist(user_id=1)

        # 获取业务数据源
        biz_source = DataSourceFactory.get_business_source()
        dashboard = biz_source.get_dashboard_summary(user_id=1)
    """

    def __init__(self):
        """初始化数据源工厂"""
        # 数据源注册表
        self._timeseries_registry: Dict[str, Type[ITimeSeriesDataSource]] = {}
        self._relational_registry: Dict[str, Type[IRelationalDataSource]] = {}
        self._business_registry: Dict[str, Type[IBusinessDataSource]] = {}

        # 数据源实例缓存
        self._timeseries_instances: Dict[str, ITimeSeriesDataSource] = {}
        self._relational_instances: Dict[str, IRelationalDataSource] = {}
        self._business_instances: Dict[str, IBusinessDataSource] = {}

        # 线程锁
        self._lock = Lock()

        # 自动注册内置数据源
        self._register_builtin_sources()

    # ==================== 数据源注册 ====================

    def register_timeseries_source(self, source_type: str, source_class: Type[ITimeSeriesDataSource]) -> None:
        """
        注册时序数据源实现

        Args:
            source_type: 数据源类型标识 (如: "mock", "tdengine", "api")
            source_class: 实现ITimeSeriesDataSource接口的类

        Raises:
            TypeError: source_class未实现ITimeSeriesDataSource接口
        """
        if not issubclass(source_class, ITimeSeriesDataSource):
            raise TypeError(f"{source_class.__name__} must implement ITimeSeriesDataSource")

        with self._lock:
            self._timeseries_registry[source_type.lower()] = source_class

    def register_relational_source(self, source_type: str, source_class: Type[IRelationalDataSource]) -> None:
        """
        注册关系数据源实现

        Args:
            source_type: 数据源类型标识 (如: "mock", "postgresql")
            source_class: 实现IRelationalDataSource接口的类

        Raises:
            TypeError: source_class未实现IRelationalDataSource接口
        """
        if not issubclass(source_class, IRelationalDataSource):
            raise TypeError(f"{source_class.__name__} must implement IRelationalDataSource")

        with self._lock:
            self._relational_registry[source_type.lower()] = source_class

    def register_business_source(self, source_type: str, source_class: Type[IBusinessDataSource]) -> None:
        """
        注册业务数据源实现

        Args:
            source_type: 数据源类型标识 (如: "mock", "composite")
            source_class: 实现IBusinessDataSource接口的类

        Raises:
            TypeError: source_class未实现IBusinessDataSource接口
        """
        if not issubclass(source_class, IBusinessDataSource):
            raise TypeError(f"{source_class.__name__} must implement IBusinessDataSource")

        with self._lock:
            self._business_registry[source_type.lower()] = source_class

    # ==================== 数据源获取 ====================

    def get_timeseries_source(self, source_type: Optional[str] = None, **kwargs) -> ITimeSeriesDataSource:
        """
        获取时序数据源实例

        Args:
            source_type: 数据源类型，None时从环境变量读取
                        可选值: "mock", "tdengine", "api"
            **kwargs: 传递给数据源构造函数的额外参数

        Returns:
            ITimeSeriesDataSource: 时序数据源实例

        Raises:
            UnsupportedDataSourceType: 不支持的数据源类型
            DataSourceNotRegistered: 数据源未注册

        示例:
            # 从环境变量获取 (推荐)
            source = factory.get_timeseries_source()

            # 显式指定类型
            source = factory.get_timeseries_source(source_type="mock")

            # 传递额外参数
            source = factory.get_timeseries_source(
                source_type="tdengine",
                host="localhost",
                port=6041
            )
        """
        # 确定数据源类型
        if source_type is None:
            source_type = os.getenv(ENV_TIMESERIES_SOURCE, DEFAULT_TIMESERIES_SOURCE).lower()
        else:
            source_type = source_type.lower()

        # 验证数据源类型
        if source_type not in SUPPORTED_TIMESERIES_TYPES:
            raise UnsupportedDataSourceType(source_type, SUPPORTED_TIMESERIES_TYPES)

        # 检查是否已有缓存实例
        cache_key = f"{source_type}_{hash(frozenset(kwargs.items()))}"
        if cache_key in self._timeseries_instances:
            return self._timeseries_instances[cache_key]

        # 获取数据源类
        if source_type not in self._timeseries_registry:
            raise DataSourceNotRegistered(source_type, "timeseries")

        # 创建实例
        with self._lock:
            source_class = self._timeseries_registry[source_type]
            instance = source_class(**kwargs)
            self._timeseries_instances[cache_key] = instance
            return instance

    def get_relational_source(self, source_type: Optional[str] = None, **kwargs) -> IRelationalDataSource:
        """
        获取关系数据源实例

        Args:
            source_type: 数据源类型，None时从环境变量读取
                        可选值: "mock", "postgresql"
            **kwargs: 传递给数据源构造函数的额外参数

        Returns:
            IRelationalDataSource: 关系数据源实例

        Raises:
            UnsupportedDataSourceType: 不支持的数据源类型
            DataSourceNotRegistered: 数据源未注册

        示例:
            # 从环境变量获取 (推荐)
            source = factory.get_relational_source()

            # 显式指定类型
            source = factory.get_relational_source(source_type="postgresql")
        """
        # 确定数据源类型
        if source_type is None:
            source_type = os.getenv(ENV_RELATIONAL_SOURCE, DEFAULT_RELATIONAL_SOURCE).lower()
        else:
            source_type = source_type.lower()

        # 验证数据源类型
        if source_type not in SUPPORTED_RELATIONAL_TYPES:
            raise UnsupportedDataSourceType(source_type, SUPPORTED_RELATIONAL_TYPES)

        # 检查是否已有缓存实例
        cache_key = f"{source_type}_{hash(frozenset(kwargs.items()))}"
        if cache_key in self._relational_instances:
            return self._relational_instances[cache_key]

        # 获取数据源类
        if source_type not in self._relational_registry:
            raise DataSourceNotRegistered(source_type, "relational")

        # 创建实例
        with self._lock:
            source_class = self._relational_registry[source_type]
            instance = source_class(**kwargs)
            self._relational_instances[cache_key] = instance
            return instance

    def get_business_source(self, source_type: Optional[str] = None, **kwargs) -> IBusinessDataSource:
        """
        获取业务数据源实例

        Args:
            source_type: 数据源类型，None时从环境变量读取
                        可选值: "mock", "composite"
            **kwargs: 传递给数据源构造函数的额外参数

        Returns:
            IBusinessDataSource: 业务数据源实例

        Raises:
            UnsupportedDataSourceType: 不支持的数据源类型
            DataSourceNotRegistered: 数据源未注册

        示例:
            # 从环境变量获取 (推荐)
            source = factory.get_business_source()

            # 显式指定类型
            source = factory.get_business_source(source_type="composite")
        """
        # 确定数据源类型
        if source_type is None:
            source_type = os.getenv(ENV_BUSINESS_SOURCE, DEFAULT_BUSINESS_SOURCE).lower()
        else:
            source_type = source_type.lower()

        # 验证数据源类型
        if source_type not in SUPPORTED_BUSINESS_TYPES:
            raise UnsupportedDataSourceType(source_type, SUPPORTED_BUSINESS_TYPES)

        # 检查是否已有缓存实例
        cache_key = f"{source_type}_{hash(frozenset(kwargs.items()))}"
        if cache_key in self._business_instances:
            return self._business_instances[cache_key]

        # 获取数据源类
        if source_type not in self._business_registry:
            raise DataSourceNotRegistered(source_type, "business")

        # 创建实例
        with self._lock:
            source_class = self._business_registry[source_type]
            instance = source_class(**kwargs)
            self._business_instances[cache_key] = instance
            return instance

    # ==================== 数据源发现 ====================

    def list_registered_sources(self) -> Dict[str, list]:
        """
        列出所有已注册的数据源

        Returns:
            Dict: 包含所有类别的已注册数据源

        示例返回:
            {
                "timeseries": ["mock", "tdengine", "api"],
                "relational": ["mock", "postgresql"],
                "business": ["mock", "composite"]
            }
        """
        return {
            "timeseries": list(self._timeseries_registry.keys()),
            "relational": list(self._relational_registry.keys()),
            "business": list(self._business_registry.keys()),
        }

    def get_current_config(self) -> Dict[str, str]:
        """
        获取当前环境变量配置

        Returns:
            Dict: 当前生效的数据源配置

        示例返回:
            {
                "timeseries": "mock",
                "relational": "postgresql",
                "business": "composite"
            }
        """
        return {
            "timeseries": os.getenv(ENV_TIMESERIES_SOURCE, DEFAULT_TIMESERIES_SOURCE),
            "relational": os.getenv(ENV_RELATIONAL_SOURCE, DEFAULT_RELATIONAL_SOURCE),
            "business": os.getenv(ENV_BUSINESS_SOURCE, DEFAULT_BUSINESS_SOURCE),
        }

    # ==================== 缓存管理 ====================

    def clear_cache(self, category: Optional[str] = None) -> None:
        """
        清除数据源实例缓存

        Args:
            category: 要清除的类别，None时清除所有缓存
                     可选值: "timeseries", "relational", "business"

        使用场景:
            - 数据源配置更改后需要重新创建实例
            - 测试时需要重置数据源状态

        示例:
            # 清除所有缓存
            factory.clear_cache()

            # 只清除时序数据源缓存
            factory.clear_cache(category="timeseries")
        """
        with self._lock:
            if category is None or category == "timeseries":
                self._timeseries_instances.clear()
            if category is None or category == "relational":
                self._relational_instances.clear()
            if category is None or category == "business":
                self._business_instances.clear()

    # ==================== 内部方法 ====================

    def _register_builtin_sources(self) -> None:
        """
        注册内置数据源实现

        这里会自动注册所有已实现的数据源类型。
        目前支持Mock数据源，其他数据源在实现后自动注册。
        """
        # Phase 2 - 注册Mock数据源
        try:
            from src.data_sources.mock.timeseries_mock import MockTimeSeriesDataSource

            self.register_timeseries_source("mock", MockTimeSeriesDataSource)
        except ImportError:
            pass

        try:
            from src.data_sources.mock.relational_mock import MockRelationalDataSource

            self.register_relational_source("mock", MockRelationalDataSource)
        except ImportError:
            pass

        try:
            from src.data_sources.mock.business_mock import MockBusinessDataSource

            self.register_business_source("mock", MockBusinessDataSource)
        except ImportError:
            pass

        # Phase 3 - 注册真实数据源
        try:
            from src.data_sources.real.tdengine_timeseries import (
                TDengineTimeSeriesDataSource,
            )

            self.register_timeseries_source("tdengine", TDengineTimeSeriesDataSource)
        except ImportError:
            pass

        try:
            from src.data_sources.real.postgresql_relational import (
                PostgreSQLRelationalDataSource,
            )

            self.register_relational_source("postgresql", PostgreSQLRelationalDataSource)
        except ImportError:
            pass

        try:
            from src.data_sources.real.composite_business import (
                CompositeBusinessDataSource,
            )

            self.register_business_source("composite", CompositeBusinessDataSource)
        except ImportError:
            pass


# ==================== 便捷函数 ====================


def get_timeseries_source(**kwargs) -> ITimeSeriesDataSource:
    """
    便捷函数: 获取时序数据源

    等同于 DataSourceFactory().get_timeseries_source(**kwargs)
    """
    return DataSourceFactory().get_timeseries_source(**kwargs)


def get_relational_source(**kwargs) -> IRelationalDataSource:
    """
    便捷函数: 获取关系数据源

    等同于 DataSourceFactory().get_relational_source(**kwargs)
    """
    return DataSourceFactory().get_relational_source(**kwargs)


def get_business_source(**kwargs) -> IBusinessDataSource:
    """
    便捷函数: 获取业务数据源

    等同于 DataSourceFactory().get_business_source(**kwargs)
    """
    return DataSourceFactory().get_business_source(**kwargs)
