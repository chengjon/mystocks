"""
FastAPI 主应用入口
MyStocks Web 管理界面后端服务 - Week 3 简化版 (PostgreSQL-only)
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from sqlalchemy import text
import structlog
import time

# 导入数据库连接管理
from app.core.database import get_postgresql_engine, close_all_connections

# 导入错误处理
from app.core.errors import UserFriendlyError, to_http_exception

# 配置日志
logger = structlog.get_logger()


# 定义生命周期管理
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("🚀 Starting MyStocks Web API (Week 3 Simplified - PostgreSQL-only)")

    try:
        # 初始化PostgreSQL连接
        engine = get_postgresql_engine()
        logger.info("✅ Database connection initialized", database="PostgreSQL")

        # 测试连接
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            logger.info("✅ Database connection verified", version=version[:50])

        # 启动定时任务调度器
        try:
            from app.services.scheduled_data_update import scheduler_service

            scheduler_service.start()
            logger.info("✅ Scheduled data update service started")
        except Exception as e:
            logger.warning(f"⚠️ Scheduled service failed to start: {e}")
            logger.info("Application will continue without scheduled updates")

    except Exception as e:
        logger.error("❌ Database initialization failed", error=str(e))
        raise

    yield  # 应用运行期间

    # 关闭时执行
    logger.info("🛑 Shutting down MyStocks Web API")

    # 停止定时任务调度器
    try:
        from app.services.scheduled_data_update import scheduler_service

        scheduler_service.stop()
        logger.info("✅ Scheduled data update service stopped")
    except Exception as e:
        logger.warning(f"⚠️ Error stopping scheduled service: {e}")

    close_all_connections()
    logger.info("✅ All database connections closed")


# 创建 FastAPI 应用
app = FastAPI(
    title="MyStocks Web API",
    description="MyStocks 量化交易数据管理系统 Web API - Week 3 Simplified",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,  # 添加生命周期管理
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:3003",
        "http://localhost:5173",  # Vite dev server
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    # 记录请求信息
    logger.info(
        "HTTP request started",
        method=request.method,
        url=str(request.url),
        client_host=request.client.host,
    )

    response = await call_next(request)

    # 记录响应信息
    process_time = time.time() - start_time
    logger.info(
        "HTTP request completed",
        method=request.method,
        url=str(request.url),
        status_code=response.status_code,
        process_time=round(process_time, 3),
    )

    return response


# 全局异常处理 - Week 3: 用户友好错误消息
@app.exception_handler(UserFriendlyError)
async def user_friendly_exception_handler(request: Request, exc: UserFriendlyError):
    """处理用户友好错误 - 返回中文友好消息"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.user_message,
            "type": exc.__class__.__name__,
            "request_id": str(id(request)),
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """处理所有未捕获的异常 - 返回通用错误消息"""
    logger.error(
        "Unhandled exception",
        exception_type=exc.__class__.__name__,
        exception_message=str(exc),
        request_method=request.method,
        request_url=str(request.url),
        exc_info=True,
    )

    # 转换为用户友好的HTTP异常
    http_exc = to_http_exception(exc)

    return JSONResponse(
        status_code=http_exc.status_code,
        content={
            **http_exc.detail,
            "request_id": str(id(request)),
            "timestamp": time.time(),
        },
    )


# 健康检查端点
@app.get("/health")
async def health_check():
    """系统健康检查"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "mystocks-web-api",
    }


# 根路径重定向到文档
@app.get("/")
async def root():
    """根路径重定向到 API 文档"""
    return {"message": "MyStocks Web API", "docs": "/api/docs"}


# 导入 API 路由
from app.api import (
    data,
    dashboard,  # Week 3 Dashboard Real Data
    market_v3,  # Week 3 Market Data PostgreSQL-Only
    auth,
    oauth2,  # Task 2.1 Phase 2: OAuth2 Integration
    mfa,  # Task 2.1 Phase 3: MFA Integration
    system,
    indicators,
    market,
    tdx,
    metrics,
    tasks,
    wencai,
    stock_search,
    watchlist,
    tradingview,
    notification,
    ml,
    market_v2,
    strategy,
    monitoring,
    technical_analysis,
    multi_source,
    announcement,
    strategy_management,
    risk_management,  # Week 1 Architecture-Compliant APIs
    sse_endpoints,  # Week 2 SSE Real-time Push
    scheduled_jobs,  # Task 6: Scheduled Data Updates
    data_export,  # Task 7: Data Export (Excel/CSV)
)

# 包含路由
app.include_router(data.router, prefix="/api/data", tags=["data"])
app.include_router(
    dashboard.router, prefix="/api/data/dashboard", tags=["dashboard"]
)  # Week 3 Dashboard Real Data
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(
    oauth2.router, prefix="/api/auth", tags=["oauth2"]
)  # Task 2.1 Phase 2
app.include_router(mfa.router, prefix="/api/auth", tags=["mfa"])  # Task 2.1 Phase 3
app.include_router(system.router, prefix="/api/system", tags=["system"])
app.include_router(indicators.router, prefix="/api/indicators", tags=["indicators"])
app.include_router(market.router, tags=["market"])  # market路由已包含prefix
app.include_router(
    market_v2.router, tags=["market-v2"]
)  # market V2路由（东方财富直接API）
app.include_router(
    market_v3.router, prefix="/api/market/v3", tags=["market-v3"]
)  # Week 3 Market Data PostgreSQL-Only (4 panels)
app.include_router(tdx.router, tags=["tdx"])  # TDX路由已包含prefix
app.include_router(
    metrics.router, prefix="/api", tags=["metrics"]
)  # Prometheus metrics
app.include_router(tasks.router, tags=["tasks"])  # 任务管理
app.include_router(wencai.router)  # 问财筛选路由，已包含prefix /api/market/wencai

# OpenStock 迁移功能路由
app.include_router(
    stock_search.router, prefix="/api/stock-search", tags=["stock-search"]
)  # 股票搜索
app.include_router(
    watchlist.router, prefix="/api/watchlist", tags=["watchlist"]
)  # 自选股管理
app.include_router(
    tradingview.router, prefix="/api/tradingview", tags=["tradingview"]
)  # TradingView widgets
app.include_router(
    notification.router, prefix="/api/notification", tags=["notification"]
)  # 邮件通知

# PyProfiling 机器学习功能路由
app.include_router(ml.router, prefix="/api", tags=["machine-learning"])  # ML预测和分析

# InStock 策略系统路由
app.include_router(strategy.router, tags=["strategy"])  # 股票策略筛选

# ValueCell 实时监控系统路由
app.include_router(monitoring.router, tags=["monitoring"])  # 实时监控和告警

# ValueCell 技术分析系统路由 (Phase 2)
app.include_router(
    technical_analysis.router, tags=["technical-analysis"]
)  # 增强技术分析

# ValueCell 多数据源系统路由 (Phase 3)
app.include_router(multi_source.router, tags=["multi-source"])  # 多数据源管理
app.include_router(announcement.router, tags=["announcement"])  # 公告监控

# Week 1 Architecture-Compliant APIs (策略管理和风险管理)
app.include_router(
    strategy_management.router
)  # 策略管理 (MyStocksUnifiedManager + MonitoringDatabase)
app.include_router(
    risk_management.router
)  # 风险管理 (MyStocksUnifiedManager + MonitoringDatabase)

# Week 2 SSE Real-time Push (实时推送)
app.include_router(
    sse_endpoints.router
)  # SSE实时推送 (training, backtest, alerts, dashboard)

# Task 6: Scheduled Data Updates (定时数据更新)
app.include_router(
    scheduled_jobs.router, prefix="/api/jobs", tags=["scheduled-jobs"]
)  # 定时任务管理 (状态查询, 手动触发, 下次执行时间)

# Task 7: Data Export (数据导出)
app.include_router(
    data_export.router, prefix="/api/export", tags=["data-export"]
)  # 数据导出 (Excel, CSV)

logger.info("✅ All API routers registered successfully")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
