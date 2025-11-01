"""
实时数据模块 (Real-time Data Module)

提供实时行情接收和处理功能:
- Tick数据接收
- WebSocket连接管理
- 数据缓存和分发
- 回调函数处理

作者: MyStocks量化交易团队
创建时间: 2025-10-18
版本: 1.0.0
"""

from .tick_receiver import TickReceiver, TickData, DataSourceType

__all__ = ['TickReceiver', 'TickData', 'DataSourceType']

__version__ = '1.0.0'
