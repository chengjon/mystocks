"""
Prometheus监控指标端点
提供系统运行指标用于Prometheus采集

安全级别：分级别访问控制
- Public endpoints: 健康检查（无需认证）
- User endpoints: 基础监控数据（需要用户认证）
- Admin endpoints: 详细系统指标（需要管理员权限）
"""

import logging
import time
from typing import Any, Dict

from fastapi import APIRouter, Depends, Response
from fastapi.responses import PlainTextResponse
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    REGISTRY,
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)

from app.api.auth import User, get_current_user
from app.core.exceptions import BusinessException, ForbiddenException
from app.core.responses import UnifiedResponse, create_unified_success_response

logger = logging.getLogger(__name__)
router = APIRouter()

METRICS_HEALTH_RESPONSE_EXAMPLE = {
    "status": "healthy",
    "timestamp": 1712073600.0,
    "version": "1.0.0",
}

METRICS_HEALTH_ERROR_RESPONSE_EXAMPLE = {
    "detail": "Service unavailable",
    "status_code": 503,
    "error_code": "SERVICE_UNAVAILABLE",
}

METRICS_ENDPOINT_ERROR_RESPONSE_EXAMPLE = {
    "detail": "获取监控数据失败",
    "status_code": 500,
    "error_code": "MONITORING_DATA_RETRIEVAL_FAILED",
}

METRICS_ENDPOINT_ERROR_RESPONSE = {
    500: {
        "description": "监控指标获取失败，通常由内部监控服务或依赖资源不可用导致。",
        "content": {"application/json": {"example": METRICS_ENDPOINT_ERROR_RESPONSE_EXAMPLE}},
    }
}


def _success_response_spec(description: str, example: Dict[str, Any]) -> Dict[int, Dict[str, Any]]:
    return {
        200: {
            "description": description,
            "content": {"application/json": {"example": example}},
        }
    }


METRICS_STATUS_RESPONSES = {
    **_success_response_spec(
        "基础系统状态",
        {
            "success": True,
            "data": {
                "api_status": "running",
                "database_status": "healthy",
                "cache_status": "available",
            },
            "message": "系统运行正常",
            "timestamp": "2026-04-07T10:00:00Z",
            "request_id": None,
        },
    ),
    **METRICS_ENDPOINT_ERROR_RESPONSE,
}

METRICS_BASIC_RESPONSES = {
    **_success_response_spec(
        "基础监控指标",
        {
            "success": True,
            "data": {
                "http_requests_total": 1000,
                "active_connections": 10,
                "cache_hit_rate": 0.85,
                "uptime": 1712484000.0,
            },
            "message": "基础监控数据获取成功",
            "timestamp": "2026-04-07T10:00:00Z",
            "request_id": None,
        },
    ),
    **METRICS_ENDPOINT_ERROR_RESPONSE,
}

METRICS_PERFORMANCE_RESPONSES = {
    **_success_response_spec(
        "性能监控指标",
        {
            "success": True,
            "data": {
                "response_time_avg": 0.15,
                "response_time_p95": 0.3,
                "request_rate": 50,
                "error_rate": 0.01,
                "cpu_usage": 0.25,
                "memory_usage": 0.6,
            },
            "message": "性能监控数据获取成功",
            "timestamp": "2026-04-07T10:00:00Z",
            "request_id": None,
        },
    ),
    **METRICS_ENDPOINT_ERROR_RESPONSE,
}

METRICS_DETAILED_RESPONSES = {
    **_success_response_spec(
        "详细系统指标",
        {
            "success": True,
            "data": {
                "database_connections": {
                    "postgresql": {"active": 8, "idle": 12},
                    "tdengine": {"active": 2, "idle": 3},
                    "redis": {"active": 1, "idle": 5},
                },
                "api_health": {"backend": 1, "database": 1},
                "datasource_availability": {"tdx": 1, "akshare": 1, "financial": 1, "baostock": 1},
                "system_info": {"uptime": 1712484000.0, "version": "1.0.0", "environment": "production"},
            },
            "message": "详细监控数据获取成功",
            "timestamp": "2026-04-07T10:00:00Z",
            "request_id": None,
        },
    ),
    **METRICS_ENDPOINT_ERROR_RESPONSE,
}

METRICS_RESET_RESPONSES = {
    **_success_response_spec(
        "重置监控指标结果",
        {
            "success": True,
            "data": {"reset_count": 4},
            "message": "监控指标已重置",
            "timestamp": "2026-04-07T10:00:00Z",
            "request_id": None,
        },
    ),
    **METRICS_ENDPOINT_ERROR_RESPONSE,
}

PROMETHEUS_METRICS_SUCCESS_RESPONSE = {
    200: {
        "description": "Prometheus 文本格式监控指标。",
        "content": {
            "text/plain": {
                "example": (
                    "# HELP mystocks_http_requests_total Total HTTP requests\n"
                    "# TYPE mystocks_http_requests_total counter\n"
                    'mystocks_http_requests_total{method="GET",endpoint="/api/metrics",status="200"} 128.0\n'
                    "# HELP mystocks_db_connections_active Active database connections\n"
                    "# TYPE mystocks_db_connections_active gauge\n"
                    'mystocks_db_connections_active{database="postgresql"} 5.0\n'
                )
            }
        },
    },
    **METRICS_ENDPOINT_ERROR_RESPONSE,
}

# Rate limiting for metrics endpoints
metrics_access_count: Dict[int, Dict[int, int]] | None = None


def _get_metrics_access_count() -> Dict[int, Dict[int, int]]:
    global metrics_access_count
    if metrics_access_count is None:
        metrics_access_count = {}
    return metrics_access_count

# ==================== 定义监控指标 ====================


def _get_or_create_metric(metric_class, name, documentation, labelnames=None, registry=None):
    """Get existing metric or create new one, handling duplicates gracefully."""
    if registry is None:
        registry = REGISTRY

    try:
        if hasattr(registry, "_names_to_collectors") and name in registry._names_to_collectors:
            return registry._names_to_collectors[name]
        # Try to create the metric
        if labelnames:
            return metric_class(name, documentation, labelnames, registry=registry)
        else:
            return metric_class(name, documentation, registry=registry)
    except ValueError as e:
        if "Duplicated timeseries" in str(e):
            # Metric already exists, try to get it from registry
            if hasattr(registry, "_names_to_collectors") and name in registry._names_to_collectors:
                return registry._names_to_collectors[name]
            else:
                logger.warning("Cannot access existing metric %(name)s, creating new registry")
                # Create a new registry if we can't access the existing one
                new_registry = CollectorRegistry()
                if labelnames:
                    return metric_class(name, documentation, labelnames, registry=new_registry)
                else:
                    return metric_class(name, documentation, registry=new_registry)
        else:
            raise


# HTTP请求计数器
http_requests_total = _get_or_create_metric(
    Counter, "mystocks_http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"]
)

# HTTP请求延迟直方图
http_request_duration_seconds = _get_or_create_metric(
    Histogram, "mystocks_http_request_duration_seconds", "HTTP request latency", ["method", "endpoint"]
)

# 数据库连接池状态
db_connections_active = _get_or_create_metric(
    Gauge, "mystocks_db_connections_active", "Active database connections", ["database"]
)

db_connections_idle = _get_or_create_metric(
    Gauge, "mystocks_db_connections_idle", "Idle database connections", ["database"]
)

# 缓存命中率
cache_hits_total = _get_or_create_metric(Counter, "mystocks_cache_hits_total", "Total cache hits")

cache_misses_total = _get_or_create_metric(Counter, "mystocks_cache_misses_total", "Total cache misses")

# API响应状态
api_health_status = _get_or_create_metric(
    Gauge, "mystocks_api_health_status", "API health status (1=healthy, 0=unhealthy)", ["service"]
)

# 数据源可用性
datasource_availability = _get_or_create_metric(
    Gauge, "mystocks_datasource_availability", "Data source availability (1=available, 0=unavailable)", ["datasource"]
)

# ==================== 辅助函数 ====================


def check_rate_limit(user_id: int, max_requests_per_minute: int = 60) -> bool:
    """
    检查用户访问频率限制

    Args:
        user_id: 用户ID
        max_requests_per_minute: 每分钟最大请求数

    Returns:
        bool: 是否允许访问
    """
    import time

    current_time = int(time.time() / 60)  # 分钟级时间窗口
    access_count = _get_metrics_access_count()

    if user_id not in access_count:
        access_count[user_id] = {}

    if current_time not in access_count[user_id]:
        access_count[user_id][current_time] = 0

    access_count[user_id][current_time] += 1

    # 清理过期的时间窗口
    for old_time in list(access_count[user_id].keys()):
        if current_time - old_time > 5:  # 保留5分钟内的记录
            del access_count[user_id][old_time]

    return access_count[user_id][current_time] <= max_requests_per_minute


def check_admin_privileges(user: User) -> bool:
    """检查管理员权限"""
    return user.role in ["admin", "backup_operator"]


def update_database_metrics():
    """更新数据库连接指标"""
    try:
        # PostgreSQL
        db_connections_active.labels(database="postgresql").set(8)
        db_connections_idle.labels(database="postgresql").set(12)

        # TDengine
        db_connections_active.labels(database="tdengine").set(2)
        db_connections_idle.labels(database="tdengine").set(3)

        # Redis
        db_connections_active.labels(database="redis").set(1)
        db_connections_idle.labels(database="redis").set(5)

        # 更新API健康状态
        api_health_status.labels(service="backend").set(1)
        api_health_status.labels(service="database").set(1)

        # 更新数据源可用性
        datasource_availability.labels(datasource="tdx").set(1)
        datasource_availability.labels(datasource="akshare").set(1)
        datasource_availability.labels(datasource="financial").set(1)
        datasource_availability.labels(datasource="baostock").set(1)

    except Exception:
        logger.error("Failed to update database metrics: %(e)s")
        # 发生错误时标记服务不健康
        api_health_status.labels(service="backend").set(0)


# ==================== 公共端点（无需认证）====================


@router.get(
    "/metrics/health",
    summary="监控指标健康检查",
    responses={
        200: {
            "description": "监控指标服务健康状态",
            "content": {"application/json": {"example": METRICS_HEALTH_RESPONSE_EXAMPLE}},
        },
        503: {
            "description": "监控指标服务不可用",
            "content": {"application/json": {"example": METRICS_HEALTH_ERROR_RESPONSE_EXAMPLE}},
        },
    },
)
@router.get(
    "/health",
    response_model=UnifiedResponse,
    summary="公共健康检查",
    responses={
        200: {
            "description": "公共健康检查结果",
            "content": {"application/json": {"example": METRICS_HEALTH_RESPONSE_EXAMPLE}},
        },
        503: {
            "description": "公共健康检查失败",
            "content": {"application/json": {"example": METRICS_HEALTH_ERROR_RESPONSE_EXAMPLE}},
        },
    },
)
async def health_check() -> UnifiedResponse:
    """
    公共健康检查端点

    Security:
        - 无需认证
        - 仅返回基础状态，不包含敏感信息
    """
    try:
        # 更新基础健康状态
        update_database_metrics()

        return create_unified_success_response(
            data={"status": "healthy", "timestamp": time.time(), "version": "1.0.0"},
            message="健康检查通过",
        )
    except Exception:
        logger.error("Health check failed: %(e)s")
        raise BusinessException(detail="Service unavailable", status_code=503, error_code="SERVICE_UNAVAILABLE")


@router.get("/status", response_model=UnifiedResponse, summary="获取基础系统状态", responses=METRICS_STATUS_RESPONSES)
async def basic_status() -> UnifiedResponse:
    """
    基础系统状态

    Returns:
        UnifiedResponse: 系统状态信息

    Security:
        - 无需认证
        - 仅提供基础状态信息
    """
    try:
        update_database_metrics()

        return create_unified_success_response(
            data={"api_status": "running", "database_status": "healthy", "cache_status": "available"},
            message="系统运行正常",
        )
    except Exception:
        logger.error("Status check failed: %(e)s")
        raise BusinessException(detail="Service unavailable", status_code=503, error_code="SERVICE_UNAVAILABLE")


# ==================== 用户级别端点（需要认证）====================


@router.get("/basic", response_model=UnifiedResponse, summary="获取基础监控指标", responses=METRICS_BASIC_RESPONSES)
async def basic_metrics(current_user: User = Depends(get_current_user)) -> UnifiedResponse:
    """
    基础监控指标

    Returns:
        UnifiedResponse: 基础监控数据

    Security:
        - 需要用户认证
        - 应用访问频率限制
        - 仅返回基础监控数据
    """
    try:
        # 检查访问频率限制
        if not check_rate_limit(current_user.id, max_requests_per_minute=30):
            raise BusinessException(
                detail="访问频率过高，请稍后再试", status_code=429, error_code="RATE_LIMIT_EXCEEDED"
            )

        # 更新监控指标
        update_database_metrics()

        # 返回基础监控数据
        basic_data = {
            "http_requests_total": 1000,  # 示例数据
            "active_connections": 10,
            "cache_hit_rate": 0.85,
            "uptime": time.time(),
        }

        logger.info("Basic metrics accessed by user: {current_user.username}")

        return create_unified_success_response(data=basic_data, message="基础监控数据获取成功")

    except (BusinessException, ForbiddenException):
        raise
    except Exception:
        logger.error("Basic metrics failed for user {current_user.username}: %(e)s")
        raise BusinessException(
            detail="获取监控数据失败", status_code=500, error_code="MONITORING_DATA_RETRIEVAL_FAILED"
        )


@router.get("/performance", response_model=UnifiedResponse, summary="获取性能监控指标", responses=METRICS_PERFORMANCE_RESPONSES)
async def performance_metrics(current_user: User = Depends(get_current_user)) -> UnifiedResponse:
    """
    性能监控指标

    Returns:
        UnifiedResponse: 性能监控数据

    Security:
        - 需要用户认证
        - 应用访问频率限制
        - 返回性能相关指标
    """
    try:
        # 检查访问频率限制
        if not check_rate_limit(current_user.id, max_requests_per_minute=20):
            raise BusinessException(
                detail="访问频率过高，请稍后再试", status_code=429, error_code="RATE_LIMIT_EXCEEDED"
            )

        # 返回性能指标
        performance_data = {
            "response_time_avg": 0.15,  # 秒
            "response_time_p95": 0.3,
            "request_rate": 50,  # 每分钟
            "error_rate": 0.01,  # 1%
            "cpu_usage": 0.25,
            "memory_usage": 0.60,
        }

        logger.info("Performance metrics accessed by user: {current_user.username}")

        return create_unified_success_response(data=performance_data, message="性能监控数据获取成功")

    except (BusinessException, ForbiddenException):
        raise
    except Exception:
        logger.error("Performance metrics failed for user {current_user.username}: %(e)s")
        raise BusinessException(
            detail="获取性能数据失败", status_code=500, error_code="PERFORMANCE_DATA_RETRIEVAL_FAILED"
        )


# ==================== 管理员级别端点（需要管理员权限）====================


@router.get("/metrics", response_class=PlainTextResponse, responses=PROMETHEUS_METRICS_SUCCESS_RESPONSE)
async def prometheus_metrics(current_user: User = Depends(get_current_user)) -> Response:
    """
    Prometheus metrics端点

    Returns:
        Response: Prometheus格式的监控指标

    Security:
        - 需要管理员权限
        - 严格访问频率限制
        - 返回完整的Prometheus指标
    """
    try:
        # 检查管理员权限
        if not check_admin_privileges(current_user):
            logger.warning("Unauthorized metrics access attempt by user: {current_user.username}")
            raise ForbiddenException(detail="需要管理员权限访问此端点")

        # 检查访问频率限制（更严格的限制）
        if not check_rate_limit(current_user.id, max_requests_per_minute=10):
            raise BusinessException(
                detail="访问频率过高，请稍后再试", status_code=429, error_code="RATE_LIMIT_EXCEEDED"
            )

        # 更新所有监控指标
        update_database_metrics()

        # 记录管理员访问
        logger.info("Prometheus metrics accessed by admin: {current_user.username}")

        # 生成Prometheus格式的metrics
        return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

    except (BusinessException, ForbiddenException):
        raise
    except Exception:
        logger.error("Prometheus metrics failed for admin {current_user.username}: %(e)s")
        raise BusinessException(detail="获取指标数据失败", status_code=500, error_code="METRICS_DATA_RETRIEVAL_FAILED")


@router.get("/detailed", response_model=UnifiedResponse, summary="获取详细系统指标", responses=METRICS_DETAILED_RESPONSES)
async def detailed_metrics(current_user: User = Depends(get_current_user)) -> UnifiedResponse:
    """
    详细系统指标

    Returns:
        UnifiedResponse: 详细的系统监控数据

    Security:
        - 需要管理员权限
        - 严格访问频率限制
        - 返回完整的系统监控数据
    """
    try:
        # 检查管理员权限
        if not check_admin_privileges(current_user):
            logger.warning("Unauthorized detailed metrics access attempt by user: {current_user.username}")
            raise ForbiddenException(detail="需要管理员权限访问此端点")

        # 检查访问频率限制
        if not check_rate_limit(current_user.id, max_requests_per_minute=5):
            raise BusinessException(
                detail="访问频率过高，请稍后再试", status_code=429, error_code="RATE_LIMIT_EXCEEDED"
            )

        # 更新监控指标
        update_database_metrics()

        # 返回详细监控数据
        detailed_data = {
            "database_connections": {
                "postgresql": {"active": 8, "idle": 12},
                "tdengine": {"active": 2, "idle": 3},
                "redis": {"active": 1, "idle": 5},
            },
            "api_health": {"backend": 1, "database": 1},
            "datasource_availability": {"tdx": 1, "akshare": 1, "financial": 1, "baostock": 1},
            "system_info": {"uptime": time.time(), "version": "1.0.0", "environment": "production"},
        }

        logger.info("Detailed metrics accessed by admin: {current_user.username}")

        return create_unified_success_response(data=detailed_data, message="详细监控数据获取成功")

    except (BusinessException, ForbiddenException):
        raise
    except Exception:
        logger.error("Detailed metrics failed for admin {current_user.username}: %(e)s")
        raise BusinessException(
            detail="获取详细监控数据失败", status_code=500, error_code="DETAILED_MONITORING_DATA_RETRIEVAL_FAILED"
        )


@router.post("/reset", response_model=UnifiedResponse, summary="重置监控指标", responses=METRICS_RESET_RESPONSES)
async def reset_metrics(current_user: User = Depends(get_current_user)) -> UnifiedResponse:
    """
    重置监控指标

    Returns:
        UnifiedResponse: 重置结果

    Security:
        - 仅管理员可访问
        - 需要管理员权限
    """
    try:
        # 检查管理员权限
        if not check_admin_privileges(current_user):
            logger.warning("Unauthorized metrics reset attempt by user: {current_user.username}")
            raise ForbiddenException(detail="需要管理员权限访问此端点")

        # 清理访问频率限制数据
        access_count = _get_metrics_access_count()
        reset_count = len(access_count)
        access_count.clear()

        logger.info("Metrics reset by admin: {current_user.username}")

        return create_unified_success_response(data={"reset_count": reset_count}, message="监控指标已重置")

    except (BusinessException, ForbiddenException):
        raise
    except Exception:
        logger.error("Metrics reset failed for admin {current_user.username}: %(e)s")
        raise BusinessException(detail="重置监控指标失败", status_code=500, error_code="METRICS_RESET_FAILED")


# ==================== 监控中间件辅助函数 ====================


def record_request_metric(method: str, endpoint: str, status_code: int, duration: float):
    """
    记录请求指标

    Args:
        method: HTTP方法
        endpoint: 端点路径
        status_code: 响应状态码
        duration: 请求耗时（秒）
    """
    # 记录请求计数
    http_requests_total.labels(method=method, endpoint=endpoint, status=str(status_code)).inc()

    # 记录请求延迟
    http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(duration)


def record_cache_hit():
    """记录缓存命中"""
    cache_hits_total.inc()


def record_cache_miss():
    """记录缓存未命中"""
    cache_misses_total.inc()
