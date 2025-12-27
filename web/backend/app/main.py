"""
FastAPI 主应用入口
MyStocks Web 管理界面后端服务 - Week 3 简化版 (PostgreSQL-only)
"""

import os
import secrets
import time
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

# 导入 Swagger UI HTML 生成器
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

# 导入缓存淘汰调度器
from .core.cache_eviction import get_eviction_scheduler, reset_eviction_scheduler

# 导入配置
from .core.config import settings

# 导入数据库连接管理
from .core.database import close_all_connections, get_postgresql_engine

# 导入Socket.IO服务器管理器
from .core.socketio_manager import get_socketio_manager

# 导入统一响应格式中间件
from .middleware.response_format import ProcessTimeMiddleware, ResponseFormatMiddleware

# 导入性能监控中间件 (Phase 5)
from .core.middleware.performance import PerformanceMiddleware, metrics_endpoint

# 导入OpenAPI配置
from .openapi_config import get_openapi_config

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

        # 检查是否已使用（防止重放攻击）
        if token_info.get("used", False):
            return False

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
            token for token, info in self.tokens.items() if current_time - info["created_at"] > self.token_timeout
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
    docs_url=None,  # 禁用默认 Swagger UI（将手动配置本地版本）
    redoc_url="/api/redoc",
    swagger_ui_parameters=openapi_config.get("swagger_ui_parameters"),
    swagger_ui_oauth2_redirect_url=openapi_config.get("swagger_ui_oauth2_redirect_url"),
    lifespan=lifespan,  # 添加生命周期管理
)

# 挂载 Swagger UI 静态文件（来自 swagger-ui-py 包）
import swagger_ui

swagger_ui_path = os.path.join(os.path.dirname(swagger_ui.__file__), "static")
app.mount(
    "/swagger-ui-static",
    StaticFiles(directory=swagger_ui_path),
    name="swagger-ui-static",
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 配置响应压缩 (性能优化)
app.add_middleware(GZipMiddleware, minimum_size=1000, compresslevel=5)  # 仅压缩大于1KB的响应  # 压缩等级1-9, 5为平衡

# 配置统一响应格式中间件 (API标准化)
app.add_middleware(ProcessTimeMiddleware)  # 处理时间记录
app.add_middleware(ResponseFormatMiddleware)  # 统一响应格式和request_id

# Phase 5: 配置性能监控中间件
performance_middleware = PerformanceMiddleware()
app.add_middleware(PerformanceMiddleware)

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
            "/api/v1/csrf/token",
            "/api/csrf-token",
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/swagger-ui",
        ]

        if not any(request.url.path.startswith(path) for path in exclude_paths):
            # 获取CSRF token from header
            csrf_token = request.headers.get("x-csrf-token")

            if not csrf_token:
                logger.warning(f"❌ CSRF token missing for {request.method} {request.url.path}")
                return JSONResponse(
                    status_code=403,
                    content={
                        "code": "CSRF_TOKEN_MISSING",
                        "message": "CSRF token is required for this request",
                        "data": None,
                    },
                )

            # 验证CSRF token
            if not csrf_manager.validate_token(csrf_token):
                logger.warning(f"❌ Invalid CSRF token for {request.method} {request.url.path}")
                return JSONResponse(
                    status_code=403,
                    content={
                        "code": "CSRF_TOKEN_INVALID",
                        "message": "CSRF token is invalid or expired",
                        "data": None,
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


# 全局异常处理 - 使用统一响应格式
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception", exc_info=exc)

    # 获取请求ID
    request_id = getattr(request.state, "request_id", str(id(request)))

    # 使用统一响应格式
    from .core.responses import ErrorCodes, ResponseMessages, create_error_response

    return JSONResponse(
        status_code=500,
        content=create_error_response(
            error_code=ErrorCodes.INTERNAL_SERVER_ERROR,
            message=ResponseMessages.INTERNAL_ERROR,
            details={"exception": str(exc), "type": type(exc).__name__},
            request_id=request_id,
        ).dict(exclude_unset=True),
    )


# 健康检查端点 - 使用统一响应格式
@app.get("/health")
async def health_check(request: Request):
    """系统健康检查"""
    # 获取请求ID
    request_id = getattr(request.state, "request_id", None)

    from .core.responses import create_unified_success_response

    return create_unified_success_response(
        data={
            "service": "mystocks-web-api",
            "status": "healthy",
            "timestamp": time.time(),
            "version": "1.0.0",
            "middleware": "response_format_enabled",
        },
        message="系统健康检查完成",
        request_id=request_id,
    )


# Phase 5: Prometheus指标端点
@app.get("/metrics", include_in_schema=False)
async def prometheus_metrics():
    """Prometheus指标端点"""
    return metrics_endpoint()


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
    # 获取请求ID
    request_id = getattr(request.state, "request_id", None)

    from .core.responses import create_unified_success_response

    token = csrf_manager.generate_token()

    # 在生产环境，应该设置HttpOnly cookie而不是返回在响应体中
    logger.info("✅ CSRF token generated for client")

    return create_unified_success_response(
        data={
            "csrf_token": token,
            "token_type": "Bearer",
            "expires_in": csrf_manager.token_timeout,
        },
        message="CSRF token生成成功",
        request_id=request_id,
    )


# 根路径重定向到文档 - 使用统一响应格式
@app.get("/")
async def root(request: Request):
    """根路径重定向到 API 文档"""
    # 获取请求ID
    request_id = getattr(request.state, "request_id", None)

    from .core.responses import create_success_response

    return create_success_response(
        data={
            "message": "MyStocks Web API",
            "docs": "/api/docs",
            "swagger": "/api/docs",
            "redoc": "/api/redoc",
            "health": "/health",
            "version": "1.0.0",
        },
        message="欢迎使用 MyStocks Web API",
        request_id=request_id,
    )


# 自定义 Swagger UI 端点（使用本地静态文件）
@app.get("/api/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """
    自定义 Swagger UI 页面 - 使用本地静态文件
    解决 CDN 被墙问题
    """
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title=f"{openapi_config['title']} - Swagger UI",
        swagger_js_url="/swagger-ui-static/swagger-ui-bundle.js",
        swagger_css_url="/swagger-ui-static/swagger-ui.css",
        swagger_favicon_url="/swagger-ui-static/favicon-32x32.png",
    )


# 导入 API 路由 - 优化结构: 先导入，后统一挂载
from .api import (
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
from .api.v1 import pool_monitoring  # Phase 3 Task 19: Connection Pool Monitoring

# 包含路由
app.include_router(data.router, prefix="/api/data", tags=["data"])
app.include_router(data_quality.router, prefix="/api", tags=["data-quality"])  # 数据质量监控
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])  # 更新至v1标准版本
app.include_router(system.router, prefix="/api/system", tags=["system"])
app.include_router(indicators.router, prefix="/api/indicators", tags=["indicators"])
app.include_router(market.router, tags=["market"])  # market路由已包含prefix
app.include_router(market_v2.router, tags=["market-v2"])  # market V2路由（东方财富直接API）
app.include_router(tdx.router, tags=["tdx"])  # TDX路由已包含prefix
app.include_router(metrics.router, prefix="/api", tags=["metrics"])  # Prometheus metrics
app.include_router(
    pool_monitoring.router, prefix="/api", tags=["pool-monitoring"]
)  # Phase 3 Task 19: Connection Pool Monitoring
app.include_router(cache.router, prefix="/api", tags=["cache"])  # 缓存管理 (Task 2.2)
app.include_router(tasks.router, tags=["tasks"])  # 任务管理
app.include_router(trade.router, prefix="/api", tags=["trade"])  # 交易管理
app.include_router(wencai.router)  # 问财筛选路由，已包含prefix /api/market/wencai

# OpenStock 迁移功能路由
app.include_router(stock_search.router, prefix="/api/stock-search", tags=["stock-search"])  # 股票搜索
app.include_router(watchlist.router, prefix="/api/watchlist", tags=["watchlist"])  # 自选股管理
app.include_router(tradingview.router, prefix="/api/tradingview", tags=["tradingview"])  # TradingView widgets
app.include_router(notification.router, prefix="/api/notification", tags=["notification"])  # 邮件通知

# PyProfiling 机器学习功能路由
app.include_router(ml.router, prefix="/api", tags=["machine-learning"])  # ML预测和分析

# InStock 策略系统路由
app.include_router(strategy.router, tags=["strategy"])  # 股票策略筛选

#  实时监控系统路由
app.include_router(monitoring.router, tags=["monitoring"])  # 实时监控和告警

#  技术分析系统路由 (Phase 2)
app.include_router(technical_analysis.router, tags=["technical-analysis"])  # 增强技术分析

#  仪表盘系统路由 (Phase 4)
app.include_router(dashboard.router, tags=["dashboard"])  # 仪表盘API
app.include_router(strategy_mgmt.router, tags=["strategy-mgmt"])  # 策略管理API

#  多数据源系统路由 (Phase 3)
app.include_router(multi_source.router, tags=["multi-source"])  # 多数据源管理
app.include_router(announcement.router, prefix="/api", tags=["announcement"])  # 公告监控

# Week 1 Architecture-Compliant APIs (策略管理和风险管理)
app.include_router(strategy_management.router)  # 策略管理 (MyStocksUnifiedManager + MonitoringDatabase)
app.include_router(risk_management.router)  # 风险管理 (MyStocksUnifiedManager + MonitoringDatabase)

# Week 2 SSE Real-time Push (实时推送)
app.include_router(sse_endpoints.router)  # SSE实时推送 (training, backtest, alerts, dashboard)

# 行业概念分析API
app.include_router(industry_concept_analysis.router)  # 行业概念分析

# 健康检查API
app.include_router(health.router, prefix="/api")

logger.info("✅ All API routers registered successfully")


def find_available_port(start_port: int, end_port: int) -> int:
    """在指定范围内查找可用端口"""
    import socket

    for port in range(start_port, end_port + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            result = sock.connect_ex(("localhost", port))
            if result != 0:  # 端口未被占用
                return port
    raise RuntimeError(f"No available port found in range {start_port}-{end_port}")


if __name__ == "__main__":
    import uvicorn

    from .core.config import settings

    try:
        # 在端口范围内查找可用端口
        available_port = find_available_port(settings.port_range_start, settings.port_range_end)
        logger.info(f"🚀 Starting server on port {available_port}")
        uvicorn.run(
            "main:app",
            host=settings.host,
            port=available_port,
            reload=True,
            log_level="info",
        )
    except RuntimeError as e:
        logger.error(f"❌ {e}")
        exit(1)
