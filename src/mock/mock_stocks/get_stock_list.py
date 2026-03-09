"""
Mock数据文件: Stocks
提供接口:
1. get_stock_list() -> List[Dict] - 获取股票列表（支持按交易所筛选，支持分页）
2. get_real_time_quote() -> Dict - 获取实时行情（必填参数：股票代码）
3. get_history_profit() -> pd.DataFrame - 获取历史收益（默认30天，返回DataFrame）

使用说明:
- 所有函数参数需与真实API接口完全对齐
- 返回值字段名需与前端表格列字段一致
- 股票价格保留2位小数，百分比保留4位小数
- 时间字段使用datetime类型，格式：YYYY-MM-DD HH:MM:SS

作者: Claude Code
生成时间: 2025-11-13
"""

from ._stock_details import get_stock_detail, get_stock_financial_data, get_stock_indicators
from ._stock_listing import get_stock_list
from ._stock_quotes import generate_realistic_price, get_history_profit, get_real_time_quote, get_realtime_quotes
from ._stock_screening import get_stock_by_industry, search_stocks
from ._stock_watchlist import add_to_watchlist, get_watchlist, remove_from_watchlist

__all__ = [
    "add_to_watchlist",
    "generate_realistic_price",
    "get_history_profit",
    "get_real_time_quote",
    "get_realtime_quotes",
    "get_stock_by_industry",
    "get_stock_detail",
    "get_stock_financial_data",
    "get_stock_indicators",
    "get_stock_list",
    "get_watchlist",
    "remove_from_watchlist",
    "search_stocks",
]
