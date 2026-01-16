"""
# 功能：财务适配器模块
# 作者：MyStocks Project
# 创建日期：2025-12-20
# 版本：1.0.0
# 说明：财务数据适配器的模块入口
"""

from .base_financial_adapter import BaseFinancialAdapter
from .stock_daily_adapter import StockDailyAdapter
from .financial_report_adapter import FinancialReportAdapter
from .financial_data_source import FinancialDataSource

__all__ = [
    "BaseFinancialAdapter",
    "StockDailyAdapter",
    "FinancialReportAdapter",
    "FinancialDataSource",
]
