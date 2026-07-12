"""mock_Stocks 拆分包"""

from .generate_realistic_volume import generate_realistic_volume
from .get_stock_list import (
    add_to_watchlist,
    generate_realistic_price,
    get_history_profit,
    get_real_time_quote,
    get_realtime_quotes,
    get_stock_by_industry,
    get_stock_detail,
    get_stock_financial_data,
    get_stock_indicators,
    get_stock_list,
    get_watchlist,
    remove_from_watchlist,
    search_stocks,
)


__all__ = [
    "add_to_watchlist",
    "generate_realistic_price",
    "generate_realistic_volume",
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
