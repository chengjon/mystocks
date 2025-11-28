"""
MyStocks统一数据管理器 - 根级别导入模块
重定向到核心模块以保持向后兼容性
"""

# 从核心模块导入统一管理器
from src.core.unified_manager import MyStocksUnifiedManager

# 导出主要类
__all__ = ["MyStocksUnifiedManager"]
