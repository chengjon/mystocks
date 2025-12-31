"""
API模块
包含所有API路由和业务逻辑
"""

from . import (
    announcement,
    auth,
    cache,
    contract,  # Phase 4: API契约管理
    dashboard,
    data,
    data_quality,
    health,
    indicators,
    industry_concept_analysis,
    market,
    market_v2,
    metrics,
    ml,
    monitoring,
    multi_source,
    notification,
    risk_management,
    sse_endpoints,
    stock_search,
    strategy,
    strategy_management,
    strategy_mgmt,
    system,
    tasks,
    tdx,
    technical_analysis,
    # trade,  # 临时注释: APIResponse泛型问题待修复
    tradingview,
    watchlist,
    wencai,
)

__all__ = [
    "announcement",
    "auth",
    "cache",
    "contract",  # Phase 4: API契约管理
    "dashboard",
    "data",
    "data_quality",
    "health",
    "indicators",
    "industry_concept_analysis",
    "market",
    "market_v2",
    "metrics",
    "ml",
    "monitoring",
    "multi_source",
    "notification",
    "risk_management",
    "sse_endpoints",
    "stock_search",
    "strategy",
    "strategy_management",
    "strategy_mgmt",
    "system",
    "tasks",
    "tdx",
    "technical_analysis",
    # "trade",  # 临时注释: APIResponse泛型问题待修复
    "tradingview",
    "watchlist",
    "wencai",
]
