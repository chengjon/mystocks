"""
Prometheus监控指标端点
提供系统运行指标用于Prometheus采集
"""

from fastapi import APIRouter, Response
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    generate_latest,
    CONTENT_TYPE_LATEST,
)
import time

router = APIRouter()

# ==================== 定义监控指标 ====================

# HTTP请求计数器
http_requests_total = Counter(
    "mystocks_http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)

# HTTP请求延迟直方图
http_request_duration_seconds = Histogram(
    "mystocks_http_request_duration_seconds",
    "HTTP request latency",
    ["method", "endpoint"],
)

# 数据库连接池状态
db_connections_active = Gauge(
    "mystocks_db_connections_active", "Active database connections", ["database"]
)

db_connections_idle = Gauge(
    "mystocks_db_connections_idle", "Idle database connections", ["database"]
)

# 缓存命中率
cache_hits_total = Counter("mystocks_cache_hits_total", "Total cache hits")

cache_misses_total = Counter("mystocks_cache_misses_total", "Total cache misses")

# API响应状态
api_health_status = Gauge(
    "mystocks_api_health_status",
    "API health status (1=healthy, 0=unhealthy)",
    ["service"],
)

# 数据源可用性
datasource_availability = Gauge(
    "mystocks_datasource_availability",
    "Data source availability (1=available, 0=unavailable)",
    ["datasource"],
)

# ==================== Metrics端点 ====================


@router.get("/metrics")
async def metrics():
    """
    Prometheus metrics端点

    返回Prometheus格式的监控指标
    """
    # 更新数据库连接状态（示例数据）
    try:
        # MySQL
        db_connections_active.labels(database="mysql").set(5)
        db_connections_idle.labels(database="mysql").set(10)

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

    except Exception as e:
        # 发生错误时标记服务不健康
        api_health_status.labels(service="backend").set(0)

    # 生成Prometheus格式的metrics
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


# ==================== 监控中间件辅助函数 ====================


def record_request_metric(
    method: str, endpoint: str, status_code: int, duration: float
):
    """
    记录请求指标

    Args:
        method: HTTP方法
        endpoint: 端点路径
        status_code: 响应状态码
        duration: 请求耗时（秒）
    """
    # 记录请求计数
    http_requests_total.labels(
        method=method, endpoint=endpoint, status=str(status_code)
    ).inc()

    # 记录请求延迟
    http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(
        duration
    )


def record_cache_hit():
    """记录缓存命中"""
    cache_hits_total.inc()


def record_cache_miss():
    """记录缓存未命中"""
    cache_misses_total.inc()
