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
    efinance,  # Efinance数据源API
    health,
    indicators,
    industry_concept_analysis,
    market,
    market_v2,
    metrics,
    ml,
    monitoring,
    monitoring_analysis,  # 智能量化监控 - 组合分析与健康度计算
    monitoring_watchlists,  # 智能量化监控 - 清单管理 API
    multi_source,
    notification,
    risk_management,
    signal_monitoring,  # 信号监控 API - 信号历史、质量报告、实时监控
    sse_endpoints,
    stock_search,
    strategy,
    strategy_list_mock,  # Task 2.3.3: Mock策略列表端点
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
    "efinance",  # Efinance数据源API
    "health",
    "indicators",
    "industry_concept_analysis",
    "market",
    "market_v2",
    "metrics",
    "ml",
    "monitoring",
    "monitoring_analysis",  # 智能量化监控 - 组合分析与健康度计算
    "monitoring_watchlists",  # 智能量化监控 - 清单管理 API
    "multi_source",
    "notification",
    "risk_management",
    "signal_monitoring",  # 信号监控 API - 信号历史、质量报告、实时监控
    "sse_endpoints",
    "stock_search",
    "strategy",
    "strategy_list_mock",  # Task 2.3.3: Mock策略列表端点
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
