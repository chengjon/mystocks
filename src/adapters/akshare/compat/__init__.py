"""Compatibility-only AkShare helper exports."""

from .legacy_market_data import (
    get_market_overview_sse,
    get_market_overview_szse,
    get_sse_daily_deal_summary,
    get_szse_area_trading_summary,
    get_szse_sector_trading_summary,
)

__all__ = [
    "get_market_overview_sse",
    "get_market_overview_szse",
    "get_szse_area_trading_summary",
    "get_szse_sector_trading_summary",
    "get_sse_daily_deal_summary",
]
