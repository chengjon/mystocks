from fastapi import FastAPI
import structlog

# 导入所有 API 路由模块
from . import (
    akshare_market,
    announcement,
    auth,
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
    prometheus_exporter,
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
    tradingview,
    watchlist,
    wencai,
)
from .v1 import pool_monitoring

logger = structlog.get_logger()


def register_all_routers(app: FastAPI):
    """
    注册所有 API 路由器到 FastAPI 应用实例。
    """
    logger.info("开始注册所有API路由器...")

    # Standard API Routers
    app.include_router(akshare_market.router, tags=["akshare-market"])
    app.include_router(data.router, prefix="/api/data", tags=["data"])
    app.include_router(data_quality.router, prefix="/api", tags=["data-quality"])
    app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
    app.include_router(system.router, prefix="/api/system", tags=["system"])
    app.include_router(indicators.router, prefix="/api/indicators", tags=["indicators"])
    app.include_router(market.router, tags=["market"])
    app.include_router(market_v2.router, tags=["market-v2"])
    app.include_router(tdx.router, tags=["tdx"])
    app.include_router(metrics.router, prefix="/api", tags=["metrics"])
    app.include_router(pool_monitoring.router, prefix="/api", tags=["pool-monitoring"])
    app.include_router(cache.router, prefix="/api", tags=["cache"])
    app.include_router(tasks.router, tags=["tasks"])
    app.include_router(trade.router, prefix="/api", tags=["trade"])
    app.include_router(wencai.router)

    # OpenStock Migration Routers
    app.include_router(stock_search.router, prefix="/api/stock-search", tags=["stock-search"])
    app.include_router(watchlist.router, prefix="/api/watchlist", tags=["watchlist"])
    app.include_router(tradingview.router, prefix="/api/tradingview", tags=["tradingview"])
    app.include_router(notification.router, prefix="/api/notification", tags=["notification"])

    # PyProfiling ML Routers
    app.include_router(ml.router, prefix="/api", tags=["machine-learning"])

    # InStock Strategy System Routers
    app.include_router(strategy.router, tags=["strategy"])

    # Real-time Monitoring System Routers
    app.include_router(monitoring.router, tags=["monitoring"])

    # Technical Analysis System Routers
    app.include_router(technical_analysis.router, tags=["technical-analysis"])

    # Dashboard System Routers
    app.include_router(dashboard.router, tags=["dashboard"])
    app.include_router(strategy_mgmt.router, tags=["strategy-mgmt"])

    # Multi-Data Source System Routers
    app.include_router(multi_source.router, tags=["multi-source"])
    app.include_router(announcement.router, prefix="/api", tags=["announcement"])

    # Week 1 Architecture-Compliant APIs
    app.include_router(strategy_management.router)
    app.include_router(risk_management.router)

    # Week 2 SSE Real-time Push
    app.include_router(sse_endpoints.router)

    # Industry Concept Analysis API
    app.include_router(industry_concept_analysis.router)

    # Health Check API (General App Health, not the one moved to factory)
    app.include_router(health.router, prefix="/api")

    # Prometheus Metrics Exporter
    app.include_router(prometheus_exporter.router, tags=["prometheus"])

    logger.info("所有API路由器注册完成。")
