"""Central router registration for the FastAPI app."""

from __future__ import annotations

import logging

from fastapi import FastAPI

from .api import contract
from .api import data_lineage
from .api import data_source_config
from .api import data_source_registry
from .api import governance_dashboard
from .api import gpu_monitoring
from .api import indicator_registry
from .api import monitoring_analysis
from .api import monitoring_watchlists
from .api import prometheus_exporter
from .api import realtime_market
from .api import signal_monitoring
from .api import strategy_list_mock
from .api import websocket
from .api import (
    announcement,
    auth,
    auth_compat,
    cache,
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
    trade,
    trading_runtime,
    tradingview,
    watchlist,
    wencai,
)
from .api import akshare_market
from .api.v1 import pool_monitoring
from .api.v1.router import api_v1_router as mystocks_v1_router
from .api.VERSION_MAPPING import VERSION_MAPPING


def register_api_routes(app: FastAPI, *, use_mock_apis: bool, logger: logging.Logger) -> None:
    """Register all API routers on the application."""
    router_modules = {
        "auth": auth.router,
        "market": market.router,
        "market_v2": market_v2.router,
        "strategy": strategy.router,
        "trade": trade.router,
        "trading_runtime": trading_runtime.router,
        "monitoring": monitoring.router,
        "technical": technical_analysis.router,
        "data": data.router,
        "system": system.router,
        "indicators": indicators.router,
        "tdx": tdx.router,
        "announcement": announcement.router,
    }

    for key, config in VERSION_MAPPING.items():
        if key in router_modules:
            app.include_router(router_modules[key], prefix=config["prefix"], tags=config["tags"])
            logger.info("✅ Registered %s router at %s", key, config["prefix"])

    app.include_router(auth_compat.compat_router, prefix="/api/auth", tags=["auth-compat"])
    app.include_router(akshare_market.router)

    app.include_router(data_quality.router, prefix="/api", tags=["data-quality"])
    app.include_router(metrics.router, prefix="/api", tags=["metrics"])
    app.include_router(pool_monitoring.router, prefix="/api", tags=["pool-monitoring"])
    app.include_router(cache.router, prefix="/api", tags=["cache"])
    app.include_router(ml.router, prefix="/api", tags=["machine-learning"])
    app.include_router(realtime_market.router, prefix="/api", tags=["realtime-market"])
    app.include_router(signal_monitoring.router, prefix="/api", tags=["signal-monitoring"])
    app.include_router(announcement.router, prefix="/api", tags=["announcement"])
    app.include_router(health.router, prefix="/api", tags=["health"])

    app.include_router(websocket.router)
    app.include_router(tasks.router, tags=["tasks"])
    app.include_router(wencai.router)
    app.include_router(dashboard.router, tags=["dashboard"])
    app.include_router(strategy_mgmt.router, tags=["strategy-mgmt"])
    app.include_router(
        multi_source.router,
        prefix=VERSION_MAPPING["multi_source"]["prefix"],
        tags=VERSION_MAPPING["multi_source"]["tags"],
    )

    app.include_router(stock_search.router, prefix="/api/stock-search", tags=["stock-search"])
    app.include_router(watchlist.router, prefix="/api/watchlist", tags=["watchlist"])
    app.include_router(tradingview.router, prefix="/api/tradingview", tags=["tradingview"])
    app.include_router(notification.router, prefix="/api/notification", tags=["notification"])

    app.include_router(
        monitoring_watchlists.router,
        prefix=VERSION_MAPPING["monitoring_watchlists"]["prefix"],
        tags=VERSION_MAPPING["monitoring_watchlists"]["tags"],
    )
    app.include_router(
        monitoring_analysis.router,
        prefix=VERSION_MAPPING["monitoring_analysis"]["prefix"],
        tags=VERSION_MAPPING["monitoring_analysis"]["tags"],
    )

    app.include_router(strategy_management.router)
    app.include_router(risk_management.router)
    app.include_router(sse_endpoints.router)
    app.include_router(industry_concept_analysis.router)

    app.include_router(mystocks_v1_router)

    app.include_router(contract.router)
    app.include_router(data_source_registry.router)
    app.include_router(data_source_config.router)
    app.include_router(data_lineage.router)
    app.include_router(governance_dashboard.router)
    app.include_router(indicator_registry.router)
    app.include_router(gpu_monitoring.router)
    app.include_router(prometheus_exporter.router, tags=["prometheus"])

    if use_mock_apis:
        app.include_router(strategy_list_mock.router)
        logger.info("✅ Mock API routes registered")

    logger.info("✅ All API routers registered successfully")
