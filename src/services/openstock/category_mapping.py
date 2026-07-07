"""OpenStock data_category 常量与 Adapter 方法签名映射.

本文件将项目内 Adapter 方法签名统一映射到 OpenStock `data_category` 字符串,
避免业务代码硬编码字符串。当 OpenStock 调整 category 命名时,只需在此处更新。

参考:
- /opt/claude/openstock/docs/API_REFERENCE.md
- /opt/claude/openstock/docs/DATA_CAPABILITY_SCOPE.md
"""

from __future__ import annotations

from enum import StrEnum


class DataCategory(StrEnum):
    """OpenStock 已实现的 70 个 data_category 枚举.

    按业务域分组排列,与 DATA_CAPABILITY_SCOPE.md 的 Business Domain Inventory 对应。
    阶段 2 Adapter 迁移时,每个 Adapter 方法对应一个 category。
    """

    # Quotes and depth
    REALTIME_QUOTES = "REALTIME_QUOTES"
    MARKET_DEPTH = "MARKET_DEPTH"
    LIMITS = "LIMITS"
    INDEX_QUOTES = "INDEX_QUOTES"
    ETF_SPOT = "ETF_SPOT"
    HK_QUOTES = "HK_QUOTES"
    US_QUOTES = "US_QUOTES"

    # K-lines, adjustment, minute data
    KLINES = "KLINES"
    ADJUSTED_KLINES = "ADJUSTED_KLINES"
    HISTORICAL_KLINES = "HISTORICAL_KLINES"
    INDEX_KLINES = "INDEX_KLINES"
    MINUTE_DATA = "MINUTE_DATA"
    HK_KLINES = "HK_KLINES"
    US_KLINES = "US_KLINES"
    ADJUST_FACTOR = "ADJUST_FACTOR"

    # Tick and call auction
    TICK_DATA = "TICK_DATA"
    CALL_AUCTION = "CALL_AUCTION"

    # Security master and calendar
    STOCK_CODES = "STOCK_CODES"
    ALL_STOCKS = "ALL_STOCKS"
    STOCK_BASIC = "STOCK_BASIC"
    STOCK_INDUSTRY = "STOCK_INDUSTRY"
    TRADE_DATES = "TRADE_DATES"
    WORKDAYS = "WORKDAYS"
    INDEX_CONSTITUENTS = "INDEX_CONSTITUENTS"

    # Fundamentals and financials
    FINANCIAL_DATA = "FINANCIAL_DATA"
    FINANCIAL_STATEMENTS = "FINANCIAL_STATEMENTS"
    DIVIDEND_DATA = "DIVIDEND_DATA"
    FORECAST_DATA = "FORECAST_DATA"
    STOCK_PROFILE = "STOCK_PROFILE"
    F10_DATA = "F10_DATA"
    SHAREHOLDER_COUNT = "SHAREHOLDER_COUNT"
    SHAREHOLDER_CHANGE = "SHAREHOLDER_CHANGE"
    RESTRICTED_RELEASE = "RESTRICTED_RELEASE"
    INSTITUTION_HOLDING = "INSTITUTION_HOLDING"

    # Company news, valuation, ratings
    ANNOUNCEMENTS = "ANNOUNCEMENTS"
    STOCK_NEWS = "STOCK_NEWS"
    RESEARCH_REPORTS = "RESEARCH_REPORTS"
    VALUATION = "VALUATION"
    CONSENSUS_FORECAST = "CONSENSUS_FORECAST"
    ROADSHOWS = "ROADSHOWS"
    REGULATORY_ACTIONS = "REGULATORY_ACTIONS"
    STOCK_RATING = "STOCK_RATING"

    # Sectors, topics, themes
    TOPICS_CONCEPTS = "TOPICS_CONCEPTS"
    TOPIC_DETAIL = "TOPIC_DETAIL"
    TOPIC_HEAT = "TOPIC_HEAT"
    SECTOR_QUOTES = "SECTOR_QUOTES"
    SECTOR_CONSTITUENTS = "SECTOR_CONSTITUENTS"
    SECTOR_KLINES = "SECTOR_KLINES"
    SECTOR_FUND_FLOW = "SECTOR_FUND_FLOW"

    # Fund flow, dragon-tiger, block trade
    FUND_FLOW = "FUND_FLOW"
    NORTHBOUND_HOLDING = "NORTHBOUND_HOLDING"
    NORTHBOUND_FLOW = "NORTHBOUND_FLOW"
    DRAGON_TIGER = "DRAGON_TIGER"
    DRAGON_TIGER_TRADER = "DRAGON_TIGER_TRADER"
    DRAGON_TIGER_STOCK_HISTORY = "DRAGON_TIGER_STOCK_HISTORY"
    BLOCK_TRADE = "BLOCK_TRADE"

    # Limit-up review and sentiment
    LIMIT_UP_POOL = "LIMIT_UP_POOL"
    LIMIT_UP_REASON = "LIMIT_UP_REASON"
    LIMIT_UP_HISTORY = "LIMIT_UP_HISTORY"
    CONSECUTIVE_LIMIT_UP = "CONSECUTIVE_LIMIT_UP"
    UPDOWN_DISTRIBUTION = "UPDOWN_DISTRIBUTION"
    MARKET_SENTIMENT = "MARKET_SENTIMENT"
    SENTIMENT_TREND = "SENTIMENT_TREND"
    SENTIMENT_DAILY_EFFECT = "SENTIMENT_DAILY_EFFECT"
    MOVEMENT_ALERTS = "MOVEMENT_ALERTS"
    HOT_RANK = "HOT_RANK"

    # Cross-market, funds, convertible bonds
    FUND_NAV = "FUND_NAV"
    CONVERTIBLE_BONDS = "CONVERTIBLE_BONDS"

    # Macro
    MACRO_DATA = "MACRO_DATA"


# 阶段 2 Adapter 方法签名 → data_category 映射表
# 在 Phase 2 各 Adapter 迁移 PR 中按域扩充,Phase 1 只提供 ADAPTER_METHOD_CATEGORIES 字典骨架。
ADAPTER_METHOD_CATEGORIES: dict[str, dict[str, DataCategory]] = {
    # domain-01 市场数据
    "AkshareMarketAdapter.get_realtime_quote": DataCategory.REALTIME_QUOTES,
    "AkshareMarketAdapter.get_market_depth": DataCategory.MARKET_DEPTH,
    "AkshareStockInfo.get_all_stocks": DataCategory.ALL_STOCKS,
    "AkshareStockInfo.get_stock_basic": DataCategory.STOCK_BASIC,
    "BaostockAdapter.get_kline_data": DataCategory.HISTORICAL_KLINES,
    "BaostockAdapter.get_stock_industry": DataCategory.STOCK_INDUSTRY,
    "BaostockAdapter.get_trade_dates": DataCategory.TRADE_DATES,
    "ByapiAdapter.get_realtime_quote": DataCategory.REALTIME_QUOTES,
    "TushareAdapter.get_stock_basic": DataCategory.STOCK_BASIC,
    "TushareAdapter.get_financial_statements": DataCategory.FINANCIAL_STATEMENTS,

    # domain-02 行情与图表 (将在阶段 2.2 扩充)
    # domain-03/04 基本面与财务 (将在阶段 2.3 扩充)
    # domain-06 板块/资金流/龙虎榜 (将在阶段 2.4 扩充)
    # domain-10 公告 (将在阶段 2.5 扩充)
}


__all__ = ["DataCategory", "ADAPTER_METHOD_CATEGORIES"]
