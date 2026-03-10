"""
Stocks 路由的数据源辅助函数。
"""

from __future__ import annotations

import os


def check_use_mock_data() -> bool:
    """检查是否使用 Mock 数据。"""
    return os.getenv("USE_MOCK_DATA", "false").lower() == "true"


def get_stocks_mock_data():
    """获取股票管理 Mock 数据模块。"""
    from src.mock.mock_Stocks import (
        add_to_watchlist,
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

    return {
        "get_stock_list": get_stock_list,
        "get_stock_detail": get_stock_detail,
        "get_stock_financial_data": get_stock_financial_data,
        "get_stock_indicators": get_stock_indicators,
        "get_realtime_quotes": get_realtime_quotes,
        "search_stocks": search_stocks,
        "get_stock_by_industry": get_stock_by_industry,
        "get_watchlist": get_watchlist,
        "add_to_watchlist": add_to_watchlist,
        "remove_from_watchlist": remove_from_watchlist,
    }


def get_database_service():
    """获取数据库服务（真实数据源）。"""
    return None
