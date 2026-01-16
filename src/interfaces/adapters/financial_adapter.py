"""
# 功能：财务适配器主文件（向后兼容）
# 作者：MyStocks Project
# 创建日期：2025-12-20
# 版本：2.0.0（重构版本）
# 说明：本文件提供向后兼容的导入接口，所有实现已拆分到financial/子模块
#
# 重构说明：
#   - 原文件1,148行已拆分为9个子模块
#   - 最大子模块：169行
#   - 主文件：本文件（向后兼容层）
#
# 子模块：
#   - base.py: FinancialDataSource基类、缓存逻辑
#   - stock_daily.py: get_stock_daily()
#   - index_daily.py: get_index_daily()
#   - stock_basic.py: get_stock_basic()
#   - realtime_data.py: get_real_time_data()
#   - index_components.py: get_index_components()
#   - financial_data.py: get_financial_data()
#   - market_calendar.py: get_market_calendar()
#   - news_data.py: get_news_data()
#
# 向后兼容：
#   本文件从financial/__init__.py导入并重新导出FinancialDataSource
#   确保旧代码可以继续使用：from src.adapters.financial_adapter import FinancialDataSource
"""

# 从子模块导入主类
from src.adapters.financial import FinancialDataSource

# 向后兼容：重新导出所有旧接口
__all__ = [
    "FinancialDataSource",
]
