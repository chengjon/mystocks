"""
Data Source Manager子模块

拆分自src/core/data_source_manager_v2.py，按功能组织为多个子模块。

子模块:
- base: DataSourceManagerV2基类、初始化逻辑
- registry: 数据源注册（从数据库和YAML加载）
- router: 数据源路由（查找最佳endpoint）
- handler: 数据调用处理（各种API handler）
- monitoring: 监控记录（成功/失败记录、调用历史）
- health_check: 健康检查（单个和批量endpoint检查）
- validation: 数据验证
- cache: LRUCache类
"""

from __future__ import annotations

import importlib
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from src.core.data_source.base import DataSourceManagerV2
    from src.core.data_source.cache import LRUCache
    from src.core.data_source.client import (
        CircuitOpenError,
        DataQualityFailedError,
        DataSourceClient,
        DataSourceClientError,
        DataSourceRequest,
        DataSourceResult,
        DataSourceTransport,
        InvalidRequestError,
        LocalDataSourceClient,
        ProviderTimeoutError,
        ProviderUnavailableError,
        RateLimitedError,
        RegistryNotFoundError,
        RemoteDataSourceClient,
        RouteDecision,
        UrlLibJsonTransport,
        create_data_source_client,
    )

__all__ = [
    "DataSourceManagerV2",
    "LRUCache",
    "CircuitOpenError",
    "DataQualityFailedError",
    "DataSourceClient",
    "DataSourceClientError",
    "DataSourceRequest",
    "DataSourceResult",
    "DataSourceTransport",
    "InvalidRequestError",
    "LocalDataSourceClient",
    "ProviderTimeoutError",
    "ProviderUnavailableError",
    "RateLimitedError",
    "RegistryNotFoundError",
    "RemoteDataSourceClient",
    "RouteDecision",
    "UrlLibJsonTransport",
    "create_data_source_client",
]

_CLIENT_EXPORTS = set(__all__[2:])


def __getattr__(name: str) -> Any:
    if name == "DataSourceManagerV2":
        from src.core.data_source.base import DataSourceManagerV2

        return DataSourceManagerV2

    if name == "LRUCache":
        from src.core.data_source.cache import LRUCache

        return LRUCache

    if name in _CLIENT_EXPORTS:
        client_module = importlib.import_module("src.core.data_source.client")
        return getattr(client_module, name)

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
