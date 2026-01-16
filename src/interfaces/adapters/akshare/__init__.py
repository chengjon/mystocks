"""
Akshare Adapter子模块

拆分自src/adapters/akshare_adapter.py，按功能组织为多个子模块。

子模块:
- base: AkshareDataSource基类、重试逻辑
- stock_daily: 股票日线数据
- index_daily: 指数日线数据
- stock_basic: 股票基本信息、指数成分股
- realtime_data: 实时数据
- financial_data: 财务数据
- market_data: 市场日历、新闻数据
- industry_data: 行业数据
- misc_data: 其他数据（分钟线、行业概念）
"""

from src.adapters.akshare.base import AkshareDataSource

__all__ = ["AkshareDataSource"]
