"""缓存预热与监控路由。"""

from datetime import datetime, timezone
from typing import Any

import structlog
from fastapi import APIRouter, Depends

from app.core.cache_prewarming import CachePrewarmingStrategy, get_cache_monitor, get_prewarming_strategy
from app.core.exceptions import BusinessException
from app.core.security import User, get_current_user
from app.openapi_config import COMMON_RESPONSES

logger = structlog.get_logger()

CACHE_PREWARMING_ROUTE_RESPONSES = {
    500: COMMON_RESPONSES[500],
}

router = APIRouter(responses=CACHE_PREWARMING_ROUTE_RESPONSES)


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _success_response_spec(description: str, example: dict[str, Any]) -> dict[int, dict[str, Any]]:
    return {
        200: {
            "description": description,
            "content": {
                "application/json": {
                    "example": example,
                }
            },
        }
    }


PREWARM_TRIGGER_RESPONSES = {
    **_success_response_spec(
        "缓存预热触发结果",
        {
            "success": True,
            "message": "缓存预热成功",
            "prewarmed_count": 42,
            "failed_count": 0,
            "elapsed_seconds": 1.37,
            "timestamp": "2026-04-05T08:00:00+00:00",
        },
    ),
    500: COMMON_RESPONSES[500],
}

PREWARM_STATUS_RESPONSES = {
    **_success_response_spec(
        "缓存预热状态",
        {
            "success": True,
            "data": {
                "enabled": True,
                "last_prewarm_at": "2026-04-05T07:55:00+00:00",
                "next_prewarm_at": "2026-04-05T08:25:00+00:00",
                "status": "idle",
            },
            "timestamp": "2026-04-05T08:00:00+00:00",
        },
    ),
    500: COMMON_RESPONSES[500],
}

CACHE_MONITORING_METRICS_RESPONSES = {
    **_success_response_spec(
        "缓存监控指标",
        {
            "success": True,
            "data": {
                "hit_count": 1280,
                "miss_count": 320,
                "hit_rate": 0.8,
                "hit_rate_percent": "80.0%",
                "average_latency_ms": 12.4,
                "total_reads": 1600,
                "health_status": "healthy",
            },
            "timestamp": "2026-04-05T08:00:00+00:00",
        },
    ),
    500: COMMON_RESPONSES[500],
}

CACHE_MONITORING_HEALTH_RESPONSES = {
    **_success_response_spec(
        "缓存健康状态",
        {
            "success": True,
            "status": "healthy",
            "hit_rate": 80.0,
            "hit_rate_percent": "80.0%",
            "message": "缓存系统运行正常，命中率 80.0%",
            "total_reads": 1600,
            "average_latency_ms": 12.4,
            "timestamp": "2026-04-05T08:00:00+00:00",
        },
    ),
    500: COMMON_RESPONSES[500],
}


@router.post(
    "/prewarming/trigger",
    summary="触发缓存预热",
    description="立即执行一次缓存预热任务并返回预热数量、失败数量和耗时，供值班排障或发布后手动补热使用。",
    responses=PREWARM_TRIGGER_RESPONSES,
)
async def trigger_cache_prewarming(
    current_user: User = Depends(get_current_user),
    prewarming_strategy: CachePrewarmingStrategy = Depends(get_prewarming_strategy),
) -> dict[str, Any]:
    try:
        result = prewarming_strategy.prewarm_cache()
        logger.info(
            "✅ 缓存预热完成",
            prewarmed_count=result.get("prewarmed_count", 0),
            failed_count=result.get("failed_count", 0),
        )
        return {
            "success": result.get("success", False),
            "message": "缓存预热成功" if result.get("success") else "缓存预热失败",
            "prewarmed_count": result.get("prewarmed_count", 0),
            "failed_count": result.get("failed_count", 0),
            "elapsed_seconds": result.get("elapsed_seconds", 0),
            "timestamp": _timestamp(),
        }
    except Exception as error:
        logger.error("❌ 缓存预热失败", error=str(error))
        raise BusinessException(detail=str(error), status_code=500, error_code="CACHE_OPERATION_FAILED")


@router.get(
    "/prewarming/status",
    summary="获取缓存预热状态",
    description="返回缓存预热策略的当前状态、最近执行时间和下一次计划执行时间，供缓存运营监控使用。",
    responses=PREWARM_STATUS_RESPONSES,
)
async def get_prewarming_status(
    current_user: User = Depends(get_current_user),
    prewarming_strategy: CachePrewarmingStrategy = Depends(get_prewarming_strategy),
) -> dict[str, Any]:
    try:
        status = prewarming_strategy.get_prewarming_status()
        logger.info("✅ 获取预热状态")
        return {"success": True, "data": status, "timestamp": _timestamp()}
    except Exception as error:
        logger.error("❌ 获取预热状态失败", error=str(error))
        raise BusinessException(detail=str(error), status_code=500, error_code="CACHE_OPERATION_FAILED")


@router.get(
    "/monitoring/metrics",
    summary="获取缓存监控指标",
    description="返回缓存命中率、延迟和总读取次数等关键指标，供观察缓存效果和性能走势使用。",
    responses=CACHE_MONITORING_METRICS_RESPONSES,
)
async def get_cache_monitoring_metrics(current_user: User = Depends(get_current_user)) -> dict[str, Any]:
    try:
        metrics = get_cache_monitor().get_metrics()
        logger.info("✅ 获取缓存监控指标", hit_rate=metrics.get("hit_rate", 0))
        return {
            "success": True,
            "data": {
                "hit_count": metrics.get("hit_count", 0),
                "miss_count": metrics.get("miss_count", 0),
                "hit_rate": metrics.get("hit_rate", 0),
                "hit_rate_percent": metrics.get("hit_rate_percent", "0.0%"),
                "average_latency_ms": metrics.get("average_latency_ms", 0),
                "total_reads": metrics.get("total_reads", 0),
                "health_status": metrics.get("health_status", "unknown"),
            },
            "timestamp": _timestamp(),
        }
    except Exception as error:
        logger.error("❌ 获取监控指标失败", error=str(error))
        raise BusinessException(detail=str(error), status_code=500, error_code="CACHE_OPERATION_FAILED")


@router.get(
    "/monitoring/health",
    summary="获取缓存健康状态",
    description="根据缓存命中率和延迟计算当前健康状态，供健康面板和告警系统快速判定缓存是否需要人工干预。",
    responses=CACHE_MONITORING_HEALTH_RESPONSES,
)
async def get_cache_health_status(
    current_user: User = Depends(get_current_user),
    prewarming_strategy: CachePrewarmingStrategy = Depends(get_prewarming_strategy),
) -> dict[str, Any]:
    try:
        health = prewarming_strategy.get_health_status()
        status = health.get("status", "unknown")
        hit_rate = health.get("hit_rate", 0)
        message = (
            f"缓存系统运行正常，命中率 {hit_rate:.1f}%"
            if status == "healthy"
            else f"缓存系统警告：命中率 {hit_rate:.1f}%，建议手动预热"
        )
        logger.info("✅ 获取缓存健康状态", status=status, hit_rate=hit_rate)
        return {
            "success": True,
            "status": status,
            "hit_rate": hit_rate,
            "hit_rate_percent": health.get("hit_rate_percent", "0.0%"),
            "message": message,
            "total_reads": health.get("total_reads", 0),
            "average_latency_ms": health.get("average_latency_ms", 0),
            "timestamp": _timestamp(),
        }
    except Exception as error:
        logger.error("❌ 获取健康状态失败", error=str(error))
        raise BusinessException(detail=str(error), status_code=500, error_code="CACHE_OPERATION_FAILED")
