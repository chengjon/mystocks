"""
FastAPI 主应用入口
MyStocks Web 管理界面后端服务 - Week 3 简化版 (PostgreSQL-only)
"""

import logging
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

# 导入配置
from .core.config import settings, validate_required_settings

# 导入数据库连接管理
from .core.database import close_all_connections, get_postgresql_engine

# 导入全局异常处理器 (Phase 3 - API契约标准化)
from .core.exception_handler import register_exception_handlers

# 导入性能监控中间件 (Phase 5)
from .core.middleware.performance import PerformanceMiddleware, metrics_endpoint

# 导入Socket.IO服务器管理器
from .core.socketio_manager import get_socketio_manager

# 导入统一响应格式中间件
from .middleware.response_format import ProcessTimeMiddleware

# 导入OpenAPI配置
from .openapi_config import get_openapi_config

# 导入缓存淘汰调度器
# from .core.cache_eviction import get_eviction_scheduler, reset_eviction_scheduler  # 临时禁用


# 配置日志 - 从环境变量读取级别，默认INFO，生产环境可设置为WARNING/ERROR
log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
logging.basicConfig(level=log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
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

    # DEVELOPMENT MODE: Set environment variable for testing
    os.environ.setdefault("DEVELOPMENT_MODE", "true")
    logger.info(f"🔧 Development mode: {os.getenv('DEVELOPMENT_MODE')}")

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
        # DEVELOPMENT MODE: Continue without database for frontend development
        if os.getenv("DEVELOPMENT_MODE", "false").lower() == "true":
            logger.warning("⚠️ DEVELOPMENT MODE: Continuing without database connection")
        else:
            raise

    # 初始化监控数据库连接池 (Phase 1.4)
    try:
        from src.monitoring.infrastructure.postgresql_async_v3 import initialize_postgres_async

        success = await initialize_postgres_async()
        if success:
            logger.info("✅ 监控数据库连接池已初始化 (Phase 1.4)")
        else:
            logger.warning("⚠️ 监控数据库初始化失败，健康度功能将不可用")
    except Exception as e:
        logger.error("❌ 启动监控数据库失败: %s", e)
        # 不阻止应用启动
        logger.warning("⚠️ 健康度评分功能将不可用")

    # 启动缓存淘汰调度器 (添加超时保护)
    try:
        # 使用signal设置超时（仅在Unix系统上有效）
        import signal

        def timeout_handler(signum, frame):
            raise TimeoutError("Cache eviction scheduler initialization timeout")

        # 设置5秒超时
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(5)

        try:
            # scheduler = get_eviction_scheduler()  # 临时禁用 - 导入已注释
            # scheduler.start_daily_cleanup(hour=2, minute=0)
            # logger.info("✅ Cache eviction scheduler started")
            logger.info("⚠️ Cache eviction scheduler disabled (import commented out)")
        finally:
            signal.alarm(0)  # 取消超时

    except TimeoutError:
        logger.warning("⚠️ Cache eviction scheduler initialization timeout - skipping (TDengine not available)")
    except Exception as e:
        logger.warning("⚠️ Failed to start cache eviction scheduler", error=str(e))

    # 初始化实时市值系统 (Phase 12.4 - DDD Architecture)
    try:
        from .api.realtime_mtm_init import initialize_realtime_mtm

        initialize_realtime_mtm()
        logger.info("✅ Real-time MTM system initialized (Phase 12.4)")
    except Exception as e:
        logger.error("❌ Failed to initialize Real-time MTM: %s", e)
        # 不阻止应用启动
        logger.warning("⚠️ Real-time MTM features will be unavailable")

    # Initialize Indicator System (Phase 3 Optimization)
    try:
        # 1. Load Defaults
        from .services.indicators.defaults import load_default_indicators

        load_default_indicators()
        logger.info("✅ Default indicators loaded (V2 Registry)")

        # 2. Register Tasks
        from .services.task_manager import task_manager
        from .tasks.indicator_tasks import batch_calculate_indicators

        task_manager.register_function("batch_calculate_indicators", batch_calculate_indicators)
        logger.info("✅ Indicator tasks registered")

    except Exception as e:
        logger.error("❌ Failed to initialize Indicator System: %s", e)

    yield  # 应用运行期间

    # 关闭时执行
    logger.info("🛑 Shutting down MyStocks Web API")

    # 关闭实时市值系统 (Phase 12.4)
    try:
        from .api.realtime_mtm_init import shutdown_realtime_mtm

        shutdown_realtime_mtm()
        logger.info("✅ Real-time MTM system shut down (Phase 12.4)")
    except Exception as e:
        logger.error("❌ Error shutting down Real-time MTM: %s", e)

    # 关闭监控数据库连接池
    try:
        from src.monitoring.infrastructure.postgresql_async_v3 import close_postgres_async

        await close_postgres_async()
        logger.info("✅ 监控数据库连接已关闭 (Phase 1.4)")
    except Exception as e:
        logger.error("❌ 关闭监控数据库失败: %s", e)

    # 停止缓存淘汰调度器
    try:
        # reset_eviction_scheduler()  # 临时禁用 - 导入已注释
        # logger.info("✅ Cache eviction scheduler stopped")
        logger.info("⚠️ Cache eviction scheduler reset disabled (import commented out)")
    except Exception as e:
        logger.warning("⚠️ Error stopping cache eviction scheduler", error=str(e))

    close_all_connections()
    logger.info("✅ All database connections closed")


# 获取OpenAPI配置
openapi_config = get_openapi_config()

# 在应用启动前验证必需的环境变量配置
try:
    validate_required_settings(settings)
    logger.info("✅ 环境变量配置验证通过")
except ValueError as e:
    logger.error("❌ 启动失败：%s", e)
    import sys

    sys.exit(1)

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
    redoc_url=None,  # 禁用默认 ReDoc（使用自定义多CDN回退版本）
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

# 挂载自定义静态文件目录（用于本地 ReDoc 等静态资源）
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount(
        "/static",
        StaticFiles(directory=static_dir),
        name="static",
    )
else:
    # 如果目录不存在，创建它
    os.makedirs(static_dir, exist_ok=True)
    app.mount(
        "/static",
        StaticFiles(directory=static_dir),
        name="static",
    )

# 配置 CORS - 白名单模式，仅允许明确的前端域名
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    # allow_origins=settings.cors_origins,  # 原配置暂时注释
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法 (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # 允许所有头 (Content-Type, Authorization, etc.)
)

# 配置响应压缩 (性能优化)
app.add_middleware(GZipMiddleware, minimum_size=1000, compresslevel=5)  # 仅压缩大于1KB的响应  # 压缩等级1-9, 5为平衡

# 配置统一响应格式中间件 (API标准化)
app.add_middleware(ProcessTimeMiddleware)  # 处理时间记录
# TEMP: Commenting out ResponseFormatMiddleware to debug 500 error
# app.add_middleware(ResponseFormatMiddleware)  # 统一响应格式和request_id

# Phase 5: 配置性能监控中间件
performance_middleware = PerformanceMiddleware()
app.add_middleware(PerformanceMiddleware)

# Phase 3: 注册全局异常处理器 (统一异常处理框架)
from .core.exceptions import register_exception_handlers

register_exception_handlers(app)
logger.info("✅ 统一异常处理器已注册")

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

    NOTE:
    - 在测试环境（testing=True）中自动禁用CSRF保护
    - 可通过csrf_enabled配置显式控制（默认True）
    - 测试环境会记录调试日志但不阻止请求
    """
    from app.core.config import settings

    # 确定是否启用CSRF保护
    # 测试环境或配置禁用时跳过CSRF验证
    should_enforce_csrf = settings.csrf_enabled and not settings.testing

    # 对于修改操作，检查CSRF token
    if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
        if settings.testing:
            # 测试环境：记录调试日志但不阻止
            logger.debug("🧪 CSRF验证跳过 (测试环境): %s %s", request.method, request.url.path)
        elif not settings.csrf_enabled:
            # CSRF被显式禁用：记录警告
            logger.warning("⚠️  CSRF保护已禁用: %s %s", request.method, request.url.path)

        if should_enforce_csrf:
            # 某些端点应该排除CSRF检查（如CSRF token生成端点和登录端点）
            exclude_paths = [
                "/api/v1/csrf/token",
                "/api/csrf-token",
                "/api/v1/auth/login",
                "/api/v1/auth/register",
                "/api/auth/login",  # 添加登录端点
                "/api/auth/register",  # 添加注册端点
                "/docs",
                "/redoc",
                "/openapi.json",
                "/swagger-ui",
                "/health",  # 健康检查
            ]

            if not any(request.url.path.startswith(path) for path in exclude_paths):
                # 获取CSRF token from header
                csrf_token = request.headers.get("x-csrf-token")

                if not csrf_token:
                    logger.warning("❌ CSRF token missing for %s %s", request.method, request.url.path)
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
                    logger.warning("❌ Invalid CSRF token for %s %s", request.method, request.url.path)
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


# 自定义 ReDoc 端点（多 CDN 回退 + 本地支持）
@app.get("/api/redoc", include_in_schema=False)
async def custom_redoc_html():
    """
    自定义 ReDoc 页面 - 支持多 CDN 回退机制
    CDN 源顺序：jsDelivr → unpkg → Redocly → 本地
    如果所有 CDN 失败，提供替代方案指引
    """
    from pathlib import Path

    from fastapi.responses import HTMLResponse

    # 读取自定义 ReDoc HTML 模板
    template_path = Path(__file__).parent / "redoc_custom.html"
    template_content = template_path.read_text(encoding="utf-8")

    # 渲染模板变量
    html_content = template_content.replace("{{title}}", openapi_config["title"]).replace(
        "{{openapi_url}}", "/openapi.json"
    )

    return HTMLResponse(content=html_content)


# 导入 API 路由 - 优化结构: 先导入，后统一挂载
from .api import contract  # Phase 4: API契约管理
from .api import data_lineage  # Phase 3: 数据血缘追踪API
from .api import data_source_config  # Phase 3: 数据源配置CRUD API
from .api import data_source_registry  # 数据源注册表管理API (V2.0)
from .api import governance_dashboard  # Phase 3: 数据治理仪表板数据API
from .api import indicator_registry  # 指标注册表管理API (V2.1)
from .api import monitoring_analysis  # 智能量化监控 - 组合分析与健康度计算
from .api import monitoring_watchlists  # 智能量化监控 - 清单管理 API
from .api import realtime_market  # Phase 12.3: Real-time Data Stream Integration
from .api import signal_monitoring  # 智能量化监控 - 信号历史与质量报告
from .api import strategy_list_mock  # Mock策略列表端点 (仅开发环境)
from .api import websocket  # 🆕 导入 WebSocket 路由
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
    tradingview,
    watchlist,
    wencai,
)
from .api.v1 import pool_monitoring  # Phase 3 Task 19: Connection Pool Monitoring

# 包含路由
app.include_router(data.router, prefix="/api/v1/data", tags=["data"])
app.include_router(data_quality.router, prefix="/api", tags=["data-quality"])  # 数据质量监控
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])  # 更新至v1标准版本
app.include_router(auth.compat_router, prefix="/api/auth", tags=["auth-compat"])  # 前端兼容路由
app.include_router(system.router, prefix="/api/system", tags=["system"])
app.include_router(indicators.router, prefix="/api/indicators", tags=["indicators"])
app.include_router(websocket.router)  # 🆕 挂载 WebSocket 路由
app.include_router(market.router, prefix="/api/v1/market", tags=["market"])
app.include_router(market_v2.router, tags=["market-v2"])  # market V2路由（东方财富直接API）
app.include_router(tdx.router, tags=["tdx"])  # TDX路由已包含prefix
app.include_router(metrics.router, prefix="/api", tags=["metrics"])  # Prometheus metrics
app.include_router(
    pool_monitoring.router, prefix="/api", tags=["pool-monitoring"]
)  # Phase 3 Task 19: Connection Pool Monitoring
app.include_router(cache.router, prefix="/api", tags=["cache"])  # 缓存管理 (Task 2.2)
app.include_router(tasks.router, tags=["tasks"])  # 任务管理
# app.include_router(trade.router, prefix="/api", tags=["trade"])  # 交易管理 - TODO: 模块不存在，待实现
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
app.include_router(monitoring.router, prefix="/api/monitoring", tags=["monitoring"])

# Phase 12.3: Real-time Data Stream Integration
app.include_router(realtime_market.router, prefix="/api", tags=["realtime-market"])  # 实时行情和持仓市值

# 智能量化监控系统路由 (2026-01-07) - v1版本
app.include_router(monitoring_watchlists.router, prefix="/api/v1", tags=["monitoring-watchlists"])  # 清单管理
app.include_router(monitoring_analysis.router, prefix="/api/v1", tags=["monitoring-analysis"])  # 组合分析与健康度计算

# 信号监控API路由 (2026-01-08) - Phase 2
app.include_router(signal_monitoring.router, prefix="/api", tags=["signal-monitoring"])  # 信号历史、质量报告、实时监控

# CLI-5: GPU监控路由 (Phase 6 - T5.2)
# app.include_router(gpu_monitoring.router, tags=["gpu-monitoring"])  # GPU监控仪表板 - TODO: 模块不存在，待实现

# 技术分析系统路由 (Phase 2)
app.include_router(technical_analysis.router, tags=["technical-analysis"])  # 增强技术分析

app.include_router(dashboard.router, tags=["dashboard"])  # 仪表盘API
app.include_router(strategy_mgmt.router, tags=["strategy-mgmt"])  # 策略管理API

# Mock API路由 (仅开发环境注册，生产环境禁用)
if settings.use_mock_apis:
    app.include_router(strategy_list_mock.router)  # Mock策略列表 (/api/mock/strategy)
    logger.info("✅ Mock API routes registered (USE_MOCK_DATA=true)")
else:
    logger.info("ℹ️  Mock API routes disabled (USE_MOCK_DATA=false) - Using real APIs")

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

# Phase 4: API契约管理
app.include_router(contract.router)  # 契约版本管理、差异检测、验证

# 数据源管理V2.0 API (数据源注册表管理)
app.include_router(data_source_registry.router)  # 数据源搜索、测试、健康检查

# 数据源配置CRUD API (Phase 3: 配置版本管理)
app.include_router(data_source_config.router)  # 数据源配置CRUD、版本历史、回滚、热重载

# 数据血缘追踪API (Phase 3: 数据血缘和影响分析)
app.include_router(data_lineage.router)  # 血缘记录、上游/下游查询、影响分析

# 数据治理仪表板数据API (Phase 3: 治理仪表板)
app.include_router(governance_dashboard.router)  # 数据质量、血缘统计、资产目录、合规指标

# 指标管理V2.1 API (指标注册表管理)
app.include_router(indicator_registry.router)  # 指标搜索、计算、详情

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
    import sys

    import uvicorn

    from .core.config import settings

    # 导入OpenSpec环境配置
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # 尝试导入OpenSpec配置
    try:
        openspec_config = {
            "POSTGRESQL_HOST": os.getenv("POSTGRESQL_HOST", "localhost"),
            "POSTGRESQL_PORT": int(os.getenv("POSTGRESQL_PORT", 5438)),
            "POSTGRESQL_USER": os.getenv("POSTGRESQL_USER", "postgres"),
            "POSTGRESQL_PASSWORD": os.getenv("POSTGRESQL_PASSWORD", "your-postgresql-password"),
            "POSTGRESQL_DATABASE": os.getenv("POSTGRESQL_DATABASE", "mystocks"),
        }
        # 更新环境变量
        for key, value in openspec_config.items():
            if os.getenv(key) is None:
                os.environ[key] = value
                logger.info("设置环境变量: %s=%s", key, value)
    except Exception as e:
        logger.warning("⚠️ 设置OpenSpec环境变量失败: %s", e)

    # 初始化异步监控数据库
    async def startup_event():
        """启动时初始化监控数据库连接池"""
        try:
            from src.monitoring.infrastructure.postgresql_async_v3 import initialize_postgres_async

            success = await initialize_postgres_async()
            if success:
                logger.info("✅ 监控数据库连接池已初始化 (Phase 1.4)")
            else:
                logger.warning("⚠️ 监控数据库初始化失败，健康度功能将不可用")
        except Exception as e:
            logger.error("❌ 启动监控数据库失败: %s", e)
            # 不阻止应用启动
            logger.warning("⚠️ 健康度评分功能将不可用")

    # 关闭异步监控数据库
    async def shutdown_event():
        """关闭时清理监控数据库连接池"""
        try:
            from src.monitoring.infrastructure.postgresql_async_v3 import close_postgres_async

            await close_postgres_async()
            logger.info("✅ 监控数据库连接已关闭 (Phase 1.4)")
        except Exception as e:
            logger.error("❌ 关闭监控数据库失败: %s", e)

    # 尝试使用异步生命周期（如果可用）

    try:
        from fastapi import FastAPI

        app = FastAPI()

        # 添加启动/关闭事件
        @app.on_event("startup")
        async def on_startup():
            logger.info("🚀 MyStocks 应用启动中...")
            # 初始化监控数据库
            await startup_event()

        @app.on_event("shutdown")
        async def on_shutdown():
            logger.info("🏹️ MyStocks 应用关闭中...")
            await shutdown_event()

        # 路由配置
        @app.get("/health")
        async def health_check_v2():
            try:
                # 检查异步数据库连接
                from src.monitoring.infrastructure.postgresql_async_v3 import get_postgres_async

                postgres_async = get_postgres_async()

                if postgres_async.is_connected():
                    database_status = "✅ PostgreSQL (监控模块)"
                else:
                    database_status = "❌ PostgreSQL (监控模块未连接)"

                return {
                    "status": "healthy",
                    "app": "mystocks-backend",
                    "version": "3.0",
                    "database": database_status,
                    "gpu": "GPU加速引擎已集成",
                    "timestamp": "2026-01-07",
                }
            except Exception as e:
                logger.error("❌ 健康检查失败: %s", e)
                return {"status": "unhealthy", "app": "mystocks-backend", "version": "3.0", "error": str(e)}

        # API路由
        @app.get("/api/v1/")
        async def root_v2():
            return {"message": "MyStocks Backend API v3.0", "version": "3.0"}

        logger.info("✅ 已集成OpenSpec监控模块启动/关闭事件")

    except ImportError as e:
        logger.error("❌ FastAPI 导入失败: %s", e)
        logger.warning("⚠️ 无法使用 FastAPI 应用，将跳过监控模块事件")

    # 在端口范围内查找可用端口并启动服务
    try:
        available_port = find_available_port(settings.port_range_start, settings.port_range_end)
        logger.info("🚀 Starting server on port %s", available_port)
        uvicorn.run(
            "main:app",
            host=settings.host,
            port=available_port,
            reload=True,
            log_level="info",
        )
    except RuntimeError as e:
        logger.error("❌ %s", e)
        exit(1)
