"""
# TDX适配器模块
# 作者：MyStocks Project
# 创建日期：2025-12-20
# 版本：1.0.0
# 说明：TDX数据源适配器的模块化实现
"""

from .base_tdx_adapter import BaseTdxAdapter, tdx_retry
from .config import TdxConfigManager, get_tdx_config, get_tdx_path, get_tdx_server_list
from .tdx_adapter import TdxDataSource

_OPTIONAL_EXPORTS = {
    "KlineDataService": ("kline_data_service", "KlineDataService"),
    "RealtimeService": ("realtime_service", "RealtimeService"),
    "TdxBlockReader": ("tdx_block_reader", "TdxBlockReader"),
    "get_tdx_block_reader": ("tdx_block_reader", "get_tdx_block_reader"),
}


def _load_optional_export(name: str):
    module_name, attr_name = _OPTIONAL_EXPORTS[name]
    module = __import__(f"{__name__}.{module_name}", fromlist=[attr_name])
    value = getattr(module, attr_name)
    globals()[name] = value
    return value


def __getattr__(name: str):
    if name not in _OPTIONAL_EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    try:
        return _load_optional_export(name)
    except ImportError as exc:
        raise AttributeError(f"optional TDX export {name!r} is unavailable") from exc


__all__ = [
    "BaseTdxAdapter",
    "tdx_retry",
    "TdxDataSource",
    "TdxConfigManager",
    "get_tdx_config",
    "get_tdx_server_list",
    "get_tdx_path",
]

# 版本信息
__version__ = "1.0.0"
__author__ = "MyStocks Project"


# 模块级别的便捷函数
def create_tdx_data_source():
    """创建TDX数据源实例的便捷函数"""
    # pylint: disable=abstract-class-instantiated
    return TdxDataSource()


def create_kline_service():
    """创建K线数据服务实例的便捷函数"""
    # pylint: disable=abstract-class-instantiated
    KlineDataService = _load_optional_export("KlineDataService")
    return KlineDataService()


def create_realtime_service():
    """创建实时数据服务实例的便捷函数"""
    # pylint: disable=abstract-class-instantiated
    RealtimeService = _load_optional_export("RealtimeService")
    return RealtimeService()
