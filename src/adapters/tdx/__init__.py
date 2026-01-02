"""
# TDX适配器模块
# 作者：MyStocks Project
# 创建日期：2025-12-20
# 版本：1.0.0
# 说明：TDX数据源适配器的模块化实现
"""

from .base_tdx_adapter import BaseTdxAdapter, tdx_retry
from .kline_data_service import KlineDataService
from .realtime_service import RealtimeService
from .tdx_data_source import TdxDataSource
from .config import TdxConfigManager, get_tdx_config, get_tdx_server_list, get_tdx_path

# 板块数据支持
try:
    from .tdx_block_reader import TdxBlockReader, get_tdx_block_reader
    BLOCK_READER_AVAILABLE = True
except ImportError:
    BLOCK_READER_AVAILABLE = False

__all__ = [
    "BaseTdxAdapter",
    "tdx_retry",
    "KlineDataService",
    "RealtimeService",
    "TdxDataSource",
    "TdxConfigManager",
    "get_tdx_config",
    "get_tdx_server_list",
    "get_tdx_path",
]

if BLOCK_READER_AVAILABLE:
    __all__.extend(["TdxBlockReader", "get_tdx_block_reader"])

# 版本信息
__version__ = "1.0.0"
__author__ = "MyStocks Project"


# 模块级别的便捷函数
def create_tdx_data_source():
    """创建TDX数据源实例的便捷函数"""
    return TdxDataSource()


def create_kline_service():
    """创建K线数据服务实例的便捷函数"""
    return KlineDataService()


def create_realtime_service():
    """创建实时数据服务实例的便捷函数"""
    return RealtimeService()
