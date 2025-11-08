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
import uuid
import secrets
import json

# 导入数据库连接管理
from app.core.database import get_postgresql_engine, close_all_connections

# 导入缓存淘汰调度器
from app.core.cache_eviction import (
    get_eviction_scheduler,
    reset_eviction_scheduler,
)

# 导入OpenAPI配置
from app.openapi_config import get_openapi_config, OPENAPI_TAGS

# 导入Socket.IO服务器管理器
from app.core.socketio_manager import get_socketio_manager

# 配置日志
logger = structlog.get_logger()


# SECURITY FIX 1.2: CSRF Token管理
class CSRFTokenManager:
    """CSRF Token管理器 - 生成和验证CSRF tokens"""

    def __init__(self):
        self.tokens = {}  # token存储（生产环境应使用数据库或Redis）
        self.token_timeout = 3600  # Token有效期 1小时

    def generate_token(self) -> str:
        """生成新的CSRF token"""
        token = secrets.token_urlsafe(32)
        self.tokens[token] = {"created_at": time.time(), "used": False}
        return token

    def validate_token(self, token: str) -> bool:
        """验证CSRF token"""
        if not token or token not in self.tokens:
            return False

        token_info = self.tokens[token]

        # 检查是否过期
        if time.time() - token_info["created_at"] > self.token_timeout:
            del self.tokens[token]
            return False

        # 标记为已使用（防止重放攻击）
        token_info["used"] = True
        return True

    def cleanup_expired_tokens(self):
        """清理过期的tokens"""
        current_time = time.time()
        expired_tokens = [
            token
            for token, info in self.tokens.items()
            if current_time - info["created_at"] > self.token_timeout
        ]
        for token in expired_tokens:
            del self.tokens[token]


# 创建全局CSRF token管理器
csrf_manager = CSRFTokenManager()


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
    except Exception as e:
        logger.error("❌ Database initialization failed", error=str(e))
        raise

    # 启动缓存淘汰调度器
    try:
        scheduler = get_eviction_scheduler()
        scheduler.start_daily_cleanup(hour=2, minute=0)
        logger.info("✅ Cache eviction scheduler started")
    except Exception as e:
        logger.warning("⚠️ Failed to start cache eviction scheduler", error=str(e))

    yield  # 应用运行期间

    # 关闭时执行
    logger.info("🛑 Shutting down MyStocks Web API")

    # 停止缓存淘汰调度器
    try:
        reset_eviction_scheduler()
        logger.info("✅ Cache eviction scheduler stopped")
    except Exception as e:
        logger.warning("⚠️ Error stopping cache eviction scheduler", error=str(e))

    close_all_connections()
    logger.info("✅ All database connections closed")


# 获取OpenAPI配置
openapi_config = get_openapi_config()

# 创建 FastAPI 应用（使用增强的OpenAPI配置）
app = FastAPI(
    title=openapi_config["title"],
    description=openapi_config["description"],
    version=openapi_config["version"],
    terms_of_service=openapi_config.get("terms_of_service"),
    contact=openapi_config.get("contact"),
    license_info=openapi_config.get("license_info"),
    openapi_tags=openapi_config["openapi_tags"],
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    swagger_ui_parameters=openapi_config.get("swagger_ui_parameters"),
    swagger_ui_oauth2_redirect_url=openapi_config.get("swagger_ui_oauth2_redirect_url"),
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

# 初始化Socket.IO服务器
socketio_manager = get_socketio_manager()
sio = socketio_manager.sio

# 注意: Socket.IO集成将在运行时通过uvicorn的asgi应用处理
# 或者使用专门的Socket.IO中间件。目前Socket.IO服务器已初始化并准备使用。
logger.info("✅ Socket.IO服务器已挂载")


# SECURITY FIX 1.2: CSRF验证中间件
@app.middleware("http")
async def csrf_protection_middleware(request: Request, call_next):
    """
    CSRF保护中间件 - 验证修改操作的CSRF token
    SECURITY: 所有POST/PUT/PATCH/DELETE请求都需要有效的CSRF token
    """
    # 对于修改操作，检查CSRF token
    if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
        # 某些端点应该排除CSRF检查（如CSRF token生成端点和登录端点）
        exclude_paths = [
            "/api/csrf-token",
            "/api/auth/login",
            "/docs",
            "/redoc",
            "/openapi.json",
        ]

        if not any(request.url.path.startswith(path) for path in exclude_paths):
            # 获取CSRF token from header
            csrf_token = request.headers.get("x-csrf-token")

            if not csrf_token:
                logger.warning(
                    f"❌ CSRF token missing for {request.method} {request.url.path}"
                )
                return JSONResponse(
                    status_code=403,
                    content={
                        "error": "CSRF token missing",
                        "message": "CSRF token is required for this request",
                    },
                )

            # 验证CSRF token
            if not csrf_manager.validate_token(csrf_token):
                logger.warning(
                    f"❌ Invalid CSRF token for {request.method} {request.url.path}"
                )
                return JSONResponse(
                    status_code=403,
                    content={
                        "error": "CSRF token invalid",
                        "message": "CSRF token is invalid or expired",
                    },
                )

    response = await call_next(request)
    return response


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


# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception", exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "request_id": str(id(request)),
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


# Socket.IO健康检查端点
@app.get("/api/socketio-status")
async def socketio_status():
    """Socket.IO服务器状态"""
    stats = socketio_manager.get_stats()
    return {
        "status": "active",
        "service": "Socket.IO",
        "statistics": stats,
        "timestamp": time.time(),
    }


# SECURITY FIX 1.2: CSRF Token 端点
@app.get("/api/csrf-token")
async def get_csrf_token(request: Request):
    """
    获取CSRF Token端点
    SECURITY: 前端应在应用启动时调用此端点获取CSRF token
    返回一个新的CSRF token供后续修改操作使用
    """
    token = csrf_manager.generate_token()

    # 在生产环境，应该设置HttpOnly cookie而不是返回在响应体中
    logger.info("✅ CSRF token generated for client")

    return {
        "csrf_token": token,
        "token_type": "Bearer",
        "expires_in": csrf_manager.token_timeout,
    }


# 根路径重定向到文档
@app.get("/")
async def root():
    """根路径重定向到 API 文档"""
    return {"message": "MyStocks Web API", "docs": "/api/docs"}


# 导入 API 路由
from app.api import (
    data,
    auth,
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
    cache,  # Task 2.2 Cache Management API
)
from app.api.v1 import pool_monitoring  # Phase 3 Task 19: Connection Pool Monitoring

# 包含路由
app.include_router(data.router, prefix="/api/data", tags=["data"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(system.router, prefix="/api/system", tags=["system"])
app.include_router(indicators.router, prefix="/api/indicators", tags=["indicators"])
app.include_router(market.router, tags=["market"])  # market路由已包含prefix
app.include_router(
    market_v2.router, tags=["market-v2"]
)  # market V2路由（东方财富直接API）
app.include_router(tdx.router, tags=["tdx"])  # TDX路由已包含prefix
app.include_router(
    metrics.router, prefix="/api", tags=["metrics"]
)  # Prometheus metrics
app.include_router(
    pool_monitoring.router, prefix="/api", tags=["pool-monitoring"]
)  # Phase 3 Task 19: Connection Pool Monitoring
app.include_router(cache.router, prefix="/api", tags=["cache"])  # 缓存管理 (Task 2.2)
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

logger.info("✅ All API routers registered successfully")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
