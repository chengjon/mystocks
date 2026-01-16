"""
# 功能：Akshare适配器主文件（向后兼容）
# 作者：MyStocks Project
# 创建日期：2025-12-20
# 版本：2.0.0（重构版本）
# 说明：本文件提供向后兼容的导入接口，所有实现已拆分到akshare/子模块
#
# 重构说明：
#   - 原文件752行已拆分为9个子模块
#   - 最大子模块：123行
#   - 主文件：本文件（向后兼容层）
#
# 子模块：
#   - base.py: AkshareDataSource基类、重试逻辑
#   - stock_daily.py: 股票日线数据
#   - index_daily.py: 指数日线数据
#   - stock_basic.py: 股票基本信息
#   - realtime_data.py: 实时数据
#   - financial_data.py: 财务数据
#   - industry_data.py: 行业数据
#   - misc_data.py: 分钟线、行业概念等
#   - market_data.py: 市场日历、新闻等
#
# 向后兼容：
#   本文件从akshare/__init__.py导入并重新导出AkshareDataSource
#   确保旧代码可以继续使用：from src.adapters.akshare_adapter import AkshareDataSource
"""

# 从子模块导入主类
from src.adapters.akshare import AkshareDataSource

# 向后兼容：重新导出所有旧接口
__all__ = [
    "AkshareDataSource",
]
