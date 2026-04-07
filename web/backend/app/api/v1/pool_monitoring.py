"""
连接池监控API - Phase 3 Task 19
提供PostgreSQL和TDengine连接池状态监控端点

Features:
- PostgreSQL连接池统计
- TDengine连接池统计
- 综合健康检查
- 连接泄漏检测
"""

from datetime import datetime, timezone
from typing import Any, Dict

import structlog
from fastapi import APIRouter, HTTPException

from app.core.database import get_postgresql_engine
from app.core.tdengine_manager import get_tdengine_manager

router = APIRouter(prefix="/pool-monitoring", tags=["Connection Pool Monitoring"])
logger = structlog.get_logger()


POOL_MONITORING_ERROR_RESPONSE = {
    500: {
        "description": "Connection pool monitoring failed because the backing pool manager or database engine is unavailable.",
        "content": {
            "application/json": {
                "example": {
                    "detail": "获取统计信息失败: database engine unavailable",
                }
            }
        },
    }
}

POOL_MONITORING_TDENGINE_UNAVAILABLE_RESPONSE = {
    503: {
        "description": "TDengine connection pool is not initialized or currently unavailable.",
        "content": {
            "application/json": {
                "example": {
                    "detail": "TDengine连接池未初始化或不可用",
                }
            }
        },
    }
}


def _success_response_spec(description: str, example: Dict[str, Any]) -> Dict[int, Dict[str, Any]]:
    return {
        200: {
            "description": description,
            "content": {"application/json": {"example": example}},
        }
    }


POSTGRESQL_POOL_STATS_RESPONSES = {
    **_success_response_spec(
        "当前 PostgreSQL 连接池容量、活跃连接和使用率统计快照。",
        {
            "pool_size": 10,
            "checked_in": 8,
            "checked_out": 2,
            "overflow": 0,
            "max_overflow": 20,
            "pool_capacity": 30,
            "usage_percentage": 6.67,
            "pool_status": "健康：连接池使用率正常",
            "timestamp": "2026-04-07T10:00:00+00:00",
        },
    ),
    **POOL_MONITORING_ERROR_RESPONSE,
}

TDENGINE_POOL_STATS_RESPONSES = {
    **_success_response_spec(
        "当前 TDengine 连接池容量、请求量、错误率和超时率统计快照。",
        {
            "total_created": 128,
            "total_closed": 124,
            "active_connections": 2,
            "idle_connections": 3,
            "connection_requests": 256,
            "connection_timeouts": 1,
            "connection_errors": 0,
            "pool_size": 5,
            "usage_percentage": 40.0,
            "pool_status": "健康：连接池使用率正常",
            "error_rate": 0.0,
            "timeout_rate": 0.39,
            "timestamp": "2026-04-07T10:00:00+00:00",
        },
    ),
    **POOL_MONITORING_TDENGINE_UNAVAILABLE_RESPONSE,
    **POOL_MONITORING_ERROR_RESPONSE,
}

POOL_MONITORING_HEALTH_RESPONSES = {
    **_success_response_spec(
        "PostgreSQL 与 TDengine 连接池的综合健康检查结果。",
        {
            "postgresql": {
                "status": "healthy",
                "details": {
                    "active_connections": 2,
                    "idle_connections": 8,
                    "usage_percentage": 6.67,
                },
            },
            "tdengine": {
                "status": "healthy",
                "details": {
                    "active_connections": 2,
                    "idle_connections": 3,
                    "usage_percentage": 40.0,
                    "error_rate": 0.0,
                },
            },
            "overall_status": "healthy",
            "timestamp": "2026-04-07T10:00:00+00:00",
        },
    ),
    **POOL_MONITORING_ERROR_RESPONSE,
}

POOL_MONITORING_ALERT_RESPONSES = {
    **_success_response_spec(
        "当前连接池告警列表，包括使用率、错误率和超时率阈值命中情况。",
        {
            "has_alerts": True,
            "alert_count": 2,
            "alerts": [
                {
                    "level": "warning",
                    "component": "postgresql",
                    "metric": "pool_usage",
                    "value": 83.5,
                    "threshold": 80,
                    "message": "PostgreSQL连接池使用率高达83.5%",
                },
                {
                    "level": "warning",
                    "component": "tdengine",
                    "metric": "timeout_rate",
                    "value": 3.1,
                    "threshold": 2,
                    "message": "TDengine连接超时率高达3.1%",
                },
            ],
            "timestamp": "2026-04-07T10:00:00+00:00",
        },
    ),
    **POOL_MONITORING_ERROR_RESPONSE,
}


@router.get(
    "/postgresql/stats",
    summary="PostgreSQL连接池统计",
    responses=POSTGRESQL_POOL_STATS_RESPONSES,
)
async def get_postgresql_pool_stats() -> Dict[str, Any]:
    """
    获取PostgreSQL连接池统计信息

    Returns:
        - pool_size: 当前连接池大小
        - checked_in: 空闲连接数
        - checked_out: 活跃连接数
        - overflow: 溢出连接数
        - pool_status: 连接池状态描述
        - timestamp: 查询时间戳
    """
    try:
        engine = get_postgresql_engine()
        pool = engine.pool

        # SQLAlchemy连接池统计
        stats = {
            "pool_size": pool.size(),
            "checked_in": pool.checkedin(),  # 空闲连接
            "checked_out": pool.checkedout(),  # 活跃连接
            "overflow": pool.overflow(),  # 溢出连接
            "max_overflow": pool._max_overflow,
            "pool_capacity": pool.size() + pool._max_overflow,
            "usage_percentage": round((pool.checkedout() / (pool.size() + pool._max_overflow)) * 100, 2),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # 连接池状态评估
        if stats["usage_percentage"] > 80:
            stats["pool_status"] = "警告：连接池使用率高于80%"
            logger.warning(
                "PostgreSQL连接池使用率高",
                usage=stats["usage_percentage"],
                active=stats["checked_out"],
            )
        elif stats["usage_percentage"] > 60:
            stats["pool_status"] = "正常：连接池使用率适中"
        else:
            stats["pool_status"] = "健康：连接池使用率正常"

        return stats

    except Exception as e:
        logger.error("获取PostgreSQL连接池统计失败", error=str(e))
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")


@router.get(
    "/tdengine/stats",
    summary="TDengine连接池统计",
    responses=TDENGINE_POOL_STATS_RESPONSES,
)
async def get_tdengine_pool_stats() -> Dict[str, Any]:
    """
    获取TDengine连接池统计信息

    Returns:
        - total_created: 总创建连接数
        - total_closed: 总关闭连接数
        - active_connections: 当前活跃连接数
        - idle_connections: 当前空闲连接数
        - connection_requests: 总连接请求数
        - connection_timeouts: 连接超时次数
        - connection_errors: 连接错误次数
        - pool_size: 当前连接池大小
        - timestamp: 查询时间戳
    """
    try:
        tdengine_mgr = get_tdengine_manager()
        stats = tdengine_mgr.get_pool_stats()

        if stats is None:
            raise HTTPException(status_code=503, detail="TDengine连接池未初始化或不可用")

        # 计算连接池使用率
        pool_size = stats.get("pool_size", 0)
        active = stats.get("active_connections", 0)

        if pool_size > 0:
            usage_percentage = round((active / pool_size) * 100, 2)
            stats["usage_percentage"] = usage_percentage

            # 连接池状态评估
            if usage_percentage > 80:
                stats["pool_status"] = "警告：连接池使用率高于80%"
                logger.warning(
                    "TDengine连接池使用率高",
                    usage=usage_percentage,
                    active=active,
                )
            elif usage_percentage > 60:
                stats["pool_status"] = "正常：连接池使用率适中"
            else:
                stats["pool_status"] = "健康：连接池使用率正常"
        else:
            stats["usage_percentage"] = 0
            stats["pool_status"] = "无连接"

        # 计算错误率
        total_requests = stats.get("connection_requests", 0)
        if total_requests > 0:
            error_rate = round((stats.get("connection_errors", 0) / total_requests) * 100, 2)
            timeout_rate = round((stats.get("connection_timeouts", 0) / total_requests) * 100, 2)
            stats["error_rate"] = error_rate
            stats["timeout_rate"] = timeout_rate

            if error_rate > 5:
                logger.warning("TDengine连接错误率高", error_rate=error_rate)

        return stats

    except HTTPException:
        raise
    except Exception as e:
        logger.error("获取TDengine连接池统计失败", error=str(e))
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")


@router.get(
    "/health",
    summary="连接池综合健康检查",
    responses=POOL_MONITORING_HEALTH_RESPONSES,
)
async def connection_pools_health_check() -> Dict[str, Any]:
    """
    检查所有连接池的健康状态

    Returns:
        - postgresql: PostgreSQL连接池健康状态
        - tdengine: TDengine连接池健康状态
        - overall_status: 总体健康状态
        - timestamp: 检查时间戳
    """
    result = {
        "postgresql": {"status": "unknown", "details": {}},
        "tdengine": {"status": "unknown", "details": {}},
        "overall_status": "unknown",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    # 检查PostgreSQL连接池
    try:
        pg_stats = await get_postgresql_pool_stats()
        result["postgresql"]["status"] = "healthy"
        result["postgresql"]["details"] = {
            "active_connections": pg_stats["checked_out"],
            "idle_connections": pg_stats["checked_in"],
            "usage_percentage": pg_stats["usage_percentage"],
        }
    except Exception as e:
        result["postgresql"]["status"] = "unhealthy"
        result["postgresql"]["error"] = str(e)
        logger.error("PostgreSQL连接池健康检查失败", error=str(e))

    # 检查TDengine连接池
    try:
        td_stats = await get_tdengine_pool_stats()
        result["tdengine"]["status"] = "healthy"
        result["tdengine"]["details"] = {
            "active_connections": td_stats["active_connections"],
            "idle_connections": td_stats["idle_connections"],
            "usage_percentage": td_stats.get("usage_percentage", 0),
            "error_rate": td_stats.get("error_rate", 0),
        }
    except HTTPException as e:
        if e.status_code == 503:
            result["tdengine"]["status"] = "not_initialized"
        else:
            result["tdengine"]["status"] = "unhealthy"
        result["tdengine"]["error"] = e.detail
        logger.warning("TDengine连接池健康检查失败", error=e.detail)
    except Exception as e:
        result["tdengine"]["status"] = "unhealthy"
        result["tdengine"]["error"] = str(e)
        logger.error("TDengine连接池健康检查失败", error=str(e))

    # 评估总体状态
    pg_healthy = result["postgresql"]["status"] == "healthy"
    td_healthy = result["tdengine"]["status"] in ["healthy", "not_initialized"]

    if pg_healthy and td_healthy:
        result["overall_status"] = "healthy"
    elif pg_healthy or td_healthy:
        result["overall_status"] = "degraded"
    else:
        result["overall_status"] = "unhealthy"

    return result


@router.get(
    "/alerts",
    summary="连接池告警检测",
    responses=POOL_MONITORING_ALERT_RESPONSES,
)
async def check_connection_pool_alerts() -> Dict[str, Any]:
    """
    检测连接池是否存在需要告警的情况

    告警条件:
    - 连接池使用率 > 80%
    - 连接错误率 > 5%
    - 连接超时率 > 2%

    Returns:
        - has_alerts: 是否存在告警
        - alerts: 告警列表
        - timestamp: 检查时间戳
    """
    alerts = []
    timestamp = datetime.now(timezone.utc).isoformat()

    # 检查PostgreSQL连接池
    try:
        pg_stats = await get_postgresql_pool_stats()
        if pg_stats["usage_percentage"] > 80:
            alerts.append(
                {
                    "level": "warning",
                    "component": "postgresql",
                    "metric": "pool_usage",
                    "value": pg_stats["usage_percentage"],
                    "threshold": 80,
                    "message": f"PostgreSQL连接池使用率高达{pg_stats['usage_percentage']}%",
                }
            )
    except Exception as e:
        alerts.append(
            {
                "level": "error",
                "component": "postgresql",
                "metric": "availability",
                "message": f"PostgreSQL连接池不可用: {str(e)}",
            }
        )

    # 检查TDengine连接池
    try:
        td_stats = await get_tdengine_pool_stats()

        # 使用率告警
        usage = td_stats.get("usage_percentage", 0)
        if usage > 80:
            alerts.append(
                {
                    "level": "warning",
                    "component": "tdengine",
                    "metric": "pool_usage",
                    "value": usage,
                    "threshold": 80,
                    "message": f"TDengine连接池使用率高达{usage}%",
                }
            )

        # 错误率告警
        error_rate = td_stats.get("error_rate", 0)
        if error_rate > 5:
            alerts.append(
                {
                    "level": "error",
                    "component": "tdengine",
                    "metric": "error_rate",
                    "value": error_rate,
                    "threshold": 5,
                    "message": f"TDengine连接错误率高达{error_rate}%",
                }
            )

        # 超时率告警
        timeout_rate = td_stats.get("timeout_rate", 0)
        if timeout_rate > 2:
            alerts.append(
                {
                    "level": "warning",
                    "component": "tdengine",
                    "metric": "timeout_rate",
                    "value": timeout_rate,
                    "threshold": 2,
                    "message": f"TDengine连接超时率高达{timeout_rate}%",
                }
            )

    except HTTPException:
        # TDengine未初始化，不算告警
        pass
    except Exception as e:
        alerts.append(
            {
                "level": "error",
                "component": "tdengine",
                "metric": "availability",
                "message": f"TDengine连接池不可用: {str(e)}",
            }
        )

    return {
        "has_alerts": len(alerts) > 0,
        "alert_count": len(alerts),
        "alerts": alerts,
        "timestamp": timestamp,
    }
