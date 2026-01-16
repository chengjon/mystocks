#!/usr/bin/env python3
"""
接口适配器模块

向后兼容别名：从 src.adapters 导入

版本: 1.0.0
作者: JohnC& AI Dev Team (Claude, OpenCode, Gemini, IFLOW)
"""

from src.adapters.tushare_adapter import TushareDataSource
from src.adapters.efinance_adapter import EfinanceDataSource
from src.adapters.data_validator import DataValidator
from src.adapters.data_source_manager import DataSourceManager
from src.adapters.customer_adapter import CustomerDataSource
from src.adapters.byapi_adapter import ByapiAdapter
from src.adapters.baostock_adapter import BaostockDataSource
from src.adapters.akshare_proxy_adapter import AkshareProxyAdapter

__version__ = "1.0.0"
AUTHOR = "JohnC& AI Dev Team (Claude, OpenCode, Gemini, IFLOW)"

# 直接从适配器模块导入（检查实际存在的类名）

__all__ = [
    "AkshareProxyAdapter",
    "BaostockDataSource",
    "ByapiAdapter",
    "CustomerDataSource",
    "DataSourceManager",
    "DataValidator",
    "EfinanceDataSource",
    "TushareDataSource",
]
