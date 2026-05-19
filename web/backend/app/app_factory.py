"""
Compatibility-retained FastAPI app factory.

Q2 closure note (2026-04):
- Canonical runtime composition truth is `app.main:app`
- This module remains available for test/bootstrap compatibility
- It MUST NOT be treated as a peer production runtime entrypoint
"""

import os
import secrets
import time
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from .adapters.akshare_extension import close_akshare_extension, install_akshare_extension
from .adapters.cninfo_adapter import close_cninfo_adapter, install_cninfo_adapter
from .adapters.eastmoney_adapter import close_eastmoney_adapter, install_eastmoney_adapter
from .adapters.eastmoney_enhanced import (
    close_eastmoney_enhanced_adapter,
    install_eastmoney_enhanced_adapter,
)
from .adapters.tqlex_adapter import close_tqlex_adapter, install_tqlex_adapter

# 导入缓存淘汰调度器
from .core.cache_eviction import get_eviction_scheduler, reset_eviction_scheduler

# 导入配置
from .core.config import settings

# 导入数据库连接管理
from .core.database import close_all_connections, get_postgresql_engine

# 导入全局异常处理器 (增强版 - UnifiedResponse格式)
from .core.global_exception_handlers import register_global_exception_handlers

# 导入响应模型，用于全局异常处理
from .core.responses import (
    BusinessCode,
    ErrorCodes,
    ErrorDetail,
    ResponseMessages,
    UnifiedResponse,
    create_health_response,
    create_success_response,
    create_unified_success_response,
)

# 导入Socket.IO服务器管理器
from .core._socketio_manager_singleton import get_socketio_manager

# 导入输入验证中间件
from .core.validation import request_middleware

# 导入统一响应格式中间件
from .middleware.response_format import ResponseFormatMiddleware

# 导入OpenAPI配置
from .openapi_config import get_openapi_config, install_openapi_schema_extra

logger = structlog.get_logger()

CANONICAL_RUNTIME_TRUTH = "app.main:app"
COMPOSITION_ROLE = "compatibility_test_factory"
PUBLIC_REALTIME_TRANSPORT_ROLE = "compatibility_retained_non_canonical"
BOOTSTRAP_SCOPE = "tests_and_legacy_bootstrap_only"
RUNTIME_DIVERGENCE_POLICY = "must_not_gain_new_runtime_only_behavior"

SOCKETIO_STATUS_RESPONSE_EXAMPLE = {
    "status": "active",
    "service": "Socket.IO",
    "statistics": {
        "connected_clients": 3,
        "active_rooms": 2,
    },
    "timestamp": 1712073600.0,
}

SOCKETIO_STATUS_ERROR_RESPONSE_EXAMPLE = {
    "detail": "Socket.IO status unavailable",
}

ROOT_RESPONSE_EXAMPLE = {
    "success": True,
    "message": "欢迎使用 MyStocks Web API",
    "data": {
        "message": "MyStocks Web API",
        "docs": "/api/docs",
        "swagger": "/api/docs",
        "redoc": "/api/redoc",
        "health": "/health",
        "version": "1.0.0",
    },
}

ROOT_ERROR_RESPONSE_EXAMPLE = {
    "success": False,
    "code": 500,
    "message": "根路径信息获取失败",
}


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


# 创建全局CSRF token管理器 (可以考虑将此实例放入应用State或通过工厂方法创建)
csrf_manager = CSRFTokenManager()


# 定义应用生命周期管理
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("🚀 Starting MyStocks Web API")

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

    # 初始化 #78 pilot 适配器生命周期
    try:
        install_eastmoney_enhanced_adapter(app)
        logger.info("✅ EastMoney enhanced adapter installed in app.state")
    except Exception as e:
        logger.warning("⚠️ Failed to initialize EastMoney enhanced adapter", error=str(e))

    try:
        install_eastmoney_adapter(app)
        logger.info("✅ EastMoney adapter installed in app.state")
    except Exception as e:
        logger.warning("⚠️ Failed to initialize EastMoney adapter", error=str(e))

    try:
        install_cninfo_adapter(app)
        logger.info("✅ Cninfo adapter installed in app.state")
    except Exception as e:
        logger.warning("⚠️ Failed to initialize Cninfo adapter", error=str(e))

    try:
        install_tqlex_adapter(app)
        logger.info("✅ TQLEX adapter installed in app.state")
    except Exception as e:
        logger.warning("⚠️ Failed to initialize TQLEX adapter", error=str(e))

    try:
        install_akshare_extension(app)
        logger.info("✅ Akshare extension installed in app.state")
    except Exception as e:
        logger.warning("⚠️ Failed to initialize Akshare extension", error=str(e))

    yield  # 应用运行期间

    # 关闭时执行
    logger.info("🛑 Shutting down MyStocks Web API")

    # 关闭 #78 pilot 适配器生命周期
    try:
        close_eastmoney_enhanced_adapter(app)
        logger.info("✅ EastMoney enhanced adapter closed")
    except Exception as e:
        logger.warning("⚠️ Error closing EastMoney enhanced adapter", error=str(e))

    try:
        close_eastmoney_adapter(app)
        logger.info("✅ EastMoney adapter closed")
    except Exception as e:
        logger.warning("⚠️ Error closing EastMoney adapter", error=str(e))

    try:
        close_cninfo_adapter(app)
        logger.info("✅ Cninfo adapter closed")
    except Exception as e:
        logger.warning("⚠️ Error closing Cninfo adapter", error=str(e))

    try:
        close_tqlex_adapter(app)
        logger.info("✅ TQLEX adapter closed")
    except Exception as e:
        logger.warning("⚠️ Error closing TQLEX adapter", error=str(e))

    try:
        close_akshare_extension(app)
        logger.info("✅ Akshare extension closed")
    except Exception as e:
        logger.warning("⚠️ Error closing Akshare extension", error=str(e))

    # 停止缓存淘汰调度器
    try:
        reset_eviction_scheduler()
        logger.info("✅ Cache eviction scheduler stopped")
    except Exception as e:
        logger.warning("⚠️ Error stopping cache eviction scheduler", error=str(e))

    close_all_connections()
    logger.info("✅ All database connections closed")


def create_app() -> FastAPI:
    """
    Compatibility-retained FastAPI app factory.

    This factory is currently used by tests and compatibility-oriented callers.
    It is not the canonical production runtime composition path; deployment and
    runtime truth remain anchored on `app.main:app`.
    """
    # 获取OpenAPI配置
    openapi_config = get_openapi_config()

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
    app.state.runtime_truth_source = CANONICAL_RUNTIME_TRUTH
    app.state.composition_role = COMPOSITION_ROLE
    app.state.public_realtime_transport_role = PUBLIC_REALTIME_TRANSPORT_ROLE
    app.state.bootstrap_scope = BOOTSTRAP_SCOPE
    app.state.runtime_divergence_policy = RUNTIME_DIVERGENCE_POLICY
    install_openapi_schema_extra(app)

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
    app.add_middleware(
        GZipMiddleware, minimum_size=1000, compresslevel=5
    )  # 仅压缩大于1KB的响应  # 压缩等级1-9, 5为平衡

    # SECURITY FIX 1.3: 输入验证中间件 - 防止SQL注入和XSS攻击
    app.middleware("http")(request_middleware)

    # 配置统一响应格式中间件 (API标准化)
    # app.add_middleware(ProcessTimeMiddleware)  # 已移除，功能由 ResponseFormatMiddleware 覆盖
    app.add_middleware(ResponseFormatMiddleware)  # 统一响应格式和request_id

    # 初始化Socket.IO服务器
    socketio_manager = get_socketio_manager()
    # sio = socketio_manager.sio # sio instance is part of manager now

    logger.info("✅ Socket.IO服务器已挂载")

    # SECURITY FIX 1.2: CSRF验证中间件
    @app.middleware("http")
    async def csrf_protection_middleware(request: Request, call_next):
        """
        CSRF保护中间件 - 验证修改操作的CSRF token
        SECURITY: 所有POST/PUT/PATCH/DELETE请求都需要有效的CSRF token
        """
        # OPTIONS请求用于CORS预检，跳过CSRF检查
        if request.method == "OPTIONS":
            response = await call_next(request)
            return response

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
                    request_id = getattr(request.state, "request_id", None)
                    unified_response = UnifiedResponse(
                        success=False,
                        code=BusinessCode.FORBIDDEN,
                        message="CSRF token is required for this request",
                        errors=[
                            ErrorDetail(code=ErrorCodes.FORBIDDEN, message="CSRF token is required for this request")
                        ],
                        request_id=request_id,
                    )
                    return JSONResponse(
                        status_code=403,
                        content=unified_response.model_dump(exclude_unset=True),
                    )

                # 验证CSRF token
                if not csrf_manager.validate_token(csrf_token):
                    logger.warning("❌ Invalid CSRF token for {request.method} {request.url.path}")
                    request_id = getattr(request.state, "request_id", None)
                    unified_response = UnifiedResponse(
                        success=False,
                        code=BusinessCode.FORBIDDEN,
                        message="CSRF token is invalid or expired",
                        errors=[ErrorDetail(code=ErrorCodes.FORBIDDEN, message="CSRF token is invalid or expired")],
                        request_id=request_id,
                    )
                    return JSONResponse(
                        status_code=403,
                        content=unified_response.model_dump(exclude_unset=True),
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

    # 注册增强版全局异常处理器 (UnifiedResponse格式)
    register_global_exception_handlers(app)
    logger.info("✅ Global exception handlers registered (UnifiedResponse format)")

    # 兜底全局异常处理 - 使用统一响应格式 (增强版)
    @app.exception_handler(Exception)
    async def fallback_global_exception_handler(request: Request, exc: Exception):
        """
        兜底全局异常处理器 - 捕获所有未被注册处理器处理的异常
        使用 UnifiedResponse 格式 (success, code, message, data, errors, request_id)
        """
        logger.error("Unhandled exception", exc_info=exc)

        # 获取请求ID
        request_id = getattr(request.state, "request_id", str(id(request)))

        unified_response = UnifiedResponse(
            success=False,
            code=BusinessCode.INTERNAL_ERROR,
            message=ResponseMessages.INTERNAL_ERROR,
            data=None,
            errors=[
                ErrorDetail(
                    code=ErrorCodes.INTERNAL_SERVER_ERROR,
                    message=f"{type(exc).__name__}: {str(exc)}",
                )
            ],
            request_id=request_id,
        )

        return JSONResponse(
            status_code=500,
            content=unified_response.model_dump(exclude_unset=True),
        )

    # 健康检查端点 - 使用统一响应格式
    @app.get("/health")
    async def health_check(request: Request):
        """系统健康检查"""
        # 获取请求ID
        request_id = getattr(request.state, "request_id", None)

        return create_health_response(
            service="mystocks-web-api",
            status="healthy",
            details={
                "timestamp": time.time(),
                "version": "1.0.0",
                "middleware": "response_format_enabled",
            },
            request_id=request_id,
        )

    # Compatibility-retained Socket.IO status endpoint.
    # Presence here does not upgrade this factory into a canonical realtime
    # runtime path; current public transport truth remains the main app's
    # FastAPI WebSocket route family.
    @app.get(
        "/api/socketio-status",
        summary="Socket.IO 服务状态",
        description="返回 Socket.IO 服务运行状态、连接统计与时间戳，用于实时通信链路巡检。",
        tags=["system"],
        responses={
            200: {
                "description": "Socket.IO 服务状态",
                "content": {"application/json": {"example": SOCKETIO_STATUS_RESPONSE_EXAMPLE}},
            },
            503: {
                "description": "Socket.IO 状态不可用",
                "content": {"application/json": {"example": SOCKETIO_STATUS_ERROR_RESPONSE_EXAMPLE}},
            },
        },
    )
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

        # 使用统一响应格式 (v2.0.0)
        return create_unified_success_response(
            data={
                "csrf_token": token,
                "token_type": "Bearer",
                "expires_in": csrf_manager.token_timeout,
            },
            message="CSRF token generated successfully",
        )

    # 根路径重定向到文档 - 使用统一响应格式
    @app.get(
        "/",
        summary="API 根入口",
        description="返回 API 文档、健康检查与版本等入口信息，作为后端服务的轻量导航响应。",
        tags=["system"],
        responses={
            200: {
                "description": "API 根入口信息",
                "content": {"application/json": {"example": ROOT_RESPONSE_EXAMPLE}},
            },
            500: {
                "description": "API 根入口信息获取失败",
                "content": {"application/json": {"example": ROOT_ERROR_RESPONSE_EXAMPLE}},
            },
        },
    )
    async def root(request: Request):
        """根路径重定向到 API 文档"""
        # 获取请求ID
        request_id = getattr(request.state, "request_id", None)

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

    # 添加 /docs 重定向到 /api/docs
    @app.get("/docs", include_in_schema=False)
    async def docs_redirect():
        """重定向 /docs 到 /api/docs"""
        return RedirectResponse(url="/api/docs")

    # Compatibility-retained router registration path for tests/bootstrap.
    # This call site is intentionally kept explicit so future cleanup can
    # narrow or delegate it without implying parity with app.main:app.
    from .api.register_routers import register_all_routers

    register_all_routers(app)
    logger.info("✅ All API routers registered successfully")

    return app
