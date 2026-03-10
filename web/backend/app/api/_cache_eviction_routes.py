"""缓存淘汰相关路由。"""

from datetime import datetime, timezone
from typing import Any

import structlog
from fastapi import APIRouter, Depends

from app.core.cache_eviction import get_eviction_scheduler, get_eviction_strategy
from app.core.exceptions import BusinessException
from app.core.security import User, get_current_user

logger = structlog.get_logger()

router = APIRouter()


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


@router.post("/evict/manual")
async def manual_cache_eviction(current_user: User = Depends(get_current_user)) -> dict[str, Any]:
    try:
        result = get_eviction_scheduler().manual_cleanup()
        if result.get("success"):
            logger.info("✅ 手动缓存淘汰成功", deleted_count=result.get("deleted_count", 0))
        else:
            logger.warning("⚠️ 手动缓存淘汰失败", message=result.get("message"))

        return {
            "success": result.get("success", False),
            "message": result.get("message", "缓存淘汰失败"),
            "deleted_count": result.get("deleted_count", 0),
            "timestamp": _timestamp(),
        }
    except Exception as error:
        logger.error("❌ 手动缓存淘汰异常", error=str(error))
        raise BusinessException(detail=str(error), status_code=500, error_code="CACHE_OPERATION_FAILED")


@router.get("/eviction/stats")
async def get_eviction_statistics(current_user: User = Depends(get_current_user)) -> dict[str, Any]:
    try:
        strategy = get_eviction_strategy()
        stats = strategy.get_eviction_statistics()
        hot_data = strategy.get_hot_data(top_n=10)
        logger.info("✅ 获取淘汰策略统计")
        return {
            "success": True,
            "data": {
                "ttl_days": stats.get("ttl_days", 7),
                "frequency_tracking": stats.get("frequency_tracking", {}),
                "hot_data": hot_data,
                "cache_stats": stats.get("cache_stats", {}),
            },
            "timestamp": _timestamp(),
        }
    except Exception as error:
        logger.error("❌ 获取淘汰统计失败", error=str(error))
        raise BusinessException(detail=str(error), status_code=500, error_code="CACHE_OPERATION_FAILED")
