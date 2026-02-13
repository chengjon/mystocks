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


# SECURITY FIX 1.2: CSRF Token管理 - Redis持久化（支持多worker共享和重启恢复）
class CSRFTokenManager:
    """CSRF Token管理器 - Redis优先，内存回退"""

    def __init__(self):
        self.tokens = {}  # 内存回退存储（Redis不可用时使用）
        self.token_timeout = 3600  # Token有效期 1小时
        self._redis_prefix = "csrf_token:"

    def _get_redis(self):
        """获取Redis客户端，不可用时返回None"""
        try:
            from app.core.redis_client import get_redis_client
            client = get_redis_client()
            if client is not None:
                client.ping()
                return client
        except Exception:
            pass
        return None

    def generate_token(self) -> str:
        """生成新的CSRF token"""
        token = secrets.token_urlsafe(32)
        created_at = time.time()

        redis_client = self._get_redis()
        if redis_client:
            try:
                import json
                token_data = json.dumps({"created_at": created_at, "used": False})
                redis_client.setex(f"{self._redis_prefix}{token}", self.token_timeout, token_data)
                return token
            except Exception:
                pass

        # 回退到内存
        self.tokens[token] = {"created_at": created_at, "used": False}
        return token

    def validate_token(self, token: str) -> bool:
        """验证CSRF token"""
        if not token:
            return False

        redis_client = self._get_redis()
        if redis_client:
            try:
                import json
                key = f"{self._redis_prefix}{token}"
                token_data_raw = redis_client.get(key)
                if not token_data_raw:
                    return False

                token_info = json.loads(token_data_raw)

                # 检查是否已使用（防止重放攻击）
                if token_info.get("used", False):
                    return False

                # 检查是否过期（Redis TTL已处理，但双重检查）
                if time.time() - token_info["created_at"] > self.token_timeout:
                    redis_client.delete(key)
                    return False

                # 标记为已使用
                token_info["used"] = True
                remaining_ttl = redis_client.ttl(key)
                if remaining_ttl > 0:
                    redis_client.setex(key, remaining_ttl, json.dumps(token_info))
                return True
            except Exception:
                pass

        # 回退到内存
        if token not in self.tokens:
            return False

        token_info = self.tokens[token]

        if token_info.get("used", False):
            return False

        if time.time() - token_info["created_at"] > self.token_timeout:
            del self.tokens[token]
            return False

        token_info["used"] = True
        return True

    def cleanup_expired_tokens(self):
        """清理过期的tokens（Redis自动通过TTL清理，此方法清理内存回退）"""
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
    allow_origins=settings.cors_origins,
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

# Phase Security: 配置速率限制中间件 (防止暴力破解)
# 【设计边界】本地部署默认禁用，仅公网暴露时通过 RATE_LIMIT_ENABLED=true 启用
import os as _os

_rate_limit_enabled = _os.getenv("RATE_LIMIT_ENABLED", "false").lower() == "true"
from .core.rate_limit import RateLimitConfig, setup_rate_limiting

rate_limit_config = RateLimitConfig(
    enabled=_rate_limit_enabled,  # 默认禁用，本地部署不需要
    requests_per_minute=10,  # 每分钟最多10次请求
    requests_per_hour=100,  # 每小时最多100次请求
    block_duration_seconds=300,  # 5分钟封禁
)
setup_rate_limiting(app, rate_limit_config)
if _rate_limit_enabled:
    logger.info("✅ Rate limiting middleware ENABLED (public network mode)")
else:
    logger.info("ℹ️ Rate limiting middleware DISABLED (local deployment mode)")

# Phase 3: 注册全局异常处理器 (统一异常处理框架)
# Note: register_exception_handlers is already imported at line 30
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

# 导入版本映射 (Phase 3: API 契约标准化)
from .api.VERSION_MAPPING import VERSION_MAPPING

# --- 1. 标准化路由注册 (基于 VERSION_MAPPING) ---
# 定义模块与路由器的映射
router_modules = {
    "auth": auth.router,
    "market": market.router,
    "market_v2": market_v2.router,
    "strategy": strategy.router,
    "monitoring": monitoring.router,
    "technical": technical_analysis.router,
    "data": data.router,
    "system": system.router,
    "indicators": indicators.router,
    "tdx": tdx.router,
    "announcement": announcement.router,
}

# 动态注册标准路由
for key, config in VERSION_MAPPING.items():
    if key in router_modules:
        app.include_router(
            router_modules[key],
            prefix=config["prefix"],
            tags=config["tags"]
        )
        logger.info(f"✅ Registered {key} router at {config['prefix']}")

# --- 2. 兼容性与特殊路由注册 ---
# 身份验证兼容路由
app.include_router(auth.compat_router, prefix="/api/auth", tags=["auth-compat"])

# 基础与监控类 (通常挂在 /api 下)
app.include_router(data_quality.router, prefix="/api", tags=["data-quality"])
app.include_router(metrics.router, prefix="/api", tags=["metrics"])
app.include_router(pool_monitoring.router, prefix="/api", tags=["pool-monitoring"])
app.include_router(cache.router, prefix="/api", tags=["cache"])
app.include_router(ml.router, prefix="/api", tags=["machine-learning"])
app.include_router(realtime_market.router, prefix="/api", tags=["realtime-market"])
app.include_router(signal_monitoring.router, prefix="/api", tags=["signal-monitoring"])
app.include_router(announcement.router, prefix="/api", tags=["announcement"])
app.include_router(health.router, prefix="/api", tags=["health"])

# 无前缀或自包含前缀的路由
app.include_router(websocket.router)
app.include_router(tasks.router, tags=["tasks"])
app.include_router(wencai.router)
app.include_router(dashboard.router, tags=["dashboard"])
app.include_router(strategy_mgmt.router, tags=["strategy-mgmt"])
app.include_router(multi_source.router, tags=["multi-source"])

# OpenStock / 迁移类
app.include_router(stock_search.router, prefix="/api/stock-search", tags=["stock-search"])
app.include_router(watchlist.router, prefix="/api/watchlist", tags=["watchlist"])
app.include_router(tradingview.router, prefix="/api/tradingview", tags=["tradingview"])
app.include_router(notification.router, prefix="/api/notification", tags=["notification"])

# 智能量化监控扩展 (v1 规范)
app.include_router(monitoring_watchlists.router, prefix="/api/v1", tags=["monitoring-watchlists"])
app.include_router(monitoring_analysis.router, prefix="/api/v1", tags=["monitoring-analysis"])

# Week 1/2 核心功能
app.include_router(strategy_management.router)
app.include_router(risk_management.router)
app.include_router(sse_endpoints.router)
app.include_router(industry_concept_analysis.router)

# Phase 3/4 数据治理
app.include_router(contract.router)
app.include_router(data_source_registry.router)
app.include_router(data_source_config.router)
app.include_router(data_lineage.router)
app.include_router(governance_dashboard.router)
app.include_router(indicator_registry.router)

# Mock API (仅开发环境)
if settings.use_mock_apis:
    app.include_router(strategy_list_mock.router)
    logger.info("✅ Mock API routes registered")

logger.info("✅ All API routers registered successfully")

if __name__ == "__main__":
    import uvicorn
    from .core.config import settings

    # 在端口范围内查找可用端口并启动服务
    try:
        available_port = find_available_port(settings.port_range_start, settings.port_range_end)
        logger.info("🚀 Starting server on port %s", available_port)
        uvicorn.run(
            "app.main:app",
            host=settings.host,
            port=available_port,
            reload=True,
            log_level="info",
        )
    except RuntimeError as e:
        logger.error("❌ %s", e)
        exit(1)

