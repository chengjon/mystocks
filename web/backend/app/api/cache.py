"""缓存管理路由聚合入口。"""

from datetime import datetime, timezone

import structlog
from fastapi import APIRouter, Depends, Query

from app.api._cache_basic_routes import router as basic_router
from app.api._cache_eviction_routes import router as eviction_router
from app.api._cache_prewarming_routes import router as prewarming_router
from app.core.cache_manager import get_cache_manager
from app.core.exceptions import BusinessException
from app.core.security import User, get_current_user


logger = structlog.get_logger()

router = APIRouter(prefix="/cache", tags=["cache"])


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


@router.delete("")
async def clear_all_cache(
    confirm: bool = Query(False), current_user: User = Depends(get_current_user)
) -> dict[str, object]:
    try:
        if not confirm:
            raise ValueError("需要确认才能清除所有缓存，请设置 confirm=true")

        deleted_count = get_cache_manager().invalidate_cache()
        logger.warning("🗑️ 所有缓存已清除", deleted_count=deleted_count)
        return {
            "success": True,
            "message": "所有缓存已清除",
            "deleted_count": deleted_count,
            "timestamp": _timestamp(),
        }
    except ValueError as error:
        logger.warning("⚠️ 输入验证失败", error=str(error))
        raise BusinessException(detail=str(error), status_code=400, error_code="INVALID_CACHE_REQUEST")
    except Exception as error:
        logger.error("❌ 清除所有缓存失败", error=str(error))
        raise BusinessException(detail=str(error), status_code=500, error_code="CACHE_OPERATION_FAILED")


router.include_router(basic_router)
router.include_router(eviction_router)
router.include_router(prewarming_router)

__all__ = ["router"]
