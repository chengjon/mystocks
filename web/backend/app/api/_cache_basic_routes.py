"""基础缓存管理路由。"""

from datetime import datetime, timezone
from typing import Any

import structlog
from fastapi import APIRouter, Body, Depends, Path, Query

from app.core.cache_manager import get_cache_manager
from app.core.exceptions import BusinessException
from app.core.security import User, get_current_user

logger = structlog.get_logger()

router = APIRouter()

CACHE_WRITE_REQUEST_EXAMPLES = {
    "daily_quote_cache": {
        "summary": "写入日线行情缓存",
        "value": {
            "close": 18.52,
            "open": 18.1,
            "high": 18.74,
            "low": 17.98,
            "volume": 1250034,
        },
    }
}


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _strip_cache_metadata(payload: Any) -> Any:
    if not isinstance(payload, dict):
        return payload
    return {key: value for key, value in payload.items() if not key.startswith("_")}


@router.get("/status")
async def get_cache_status(current_user: User = Depends(get_current_user)) -> dict[str, Any]:
    try:
        stats = get_cache_manager().get_cache_stats()
        logger.info("✅ 获取缓存统计", hit_rate=stats.get("hit_rate", 0))
        return {"success": True, "timestamp": _timestamp(), "data": stats}
    except Exception as error:
        logger.error("❌ 获取缓存统计失败", error=str(error))
        raise BusinessException(detail=str(error), status_code=500, error_code="CACHE_OPERATION_FAILED")


@router.get(
    "/{symbol}/{data_type}",
    description="读取指定标的和数据类型的缓存内容，可按 timeframe 进一步区分缓存分片。",
)
async def get_cached_data(
    symbol: str = Path(..., description="股票或资产代码。"),
    data_type: str = Path(..., description="缓存中的数据类型标识。"),
    timeframe: str | None = Query(None, description="缓存时间粒度，例如 1d、1h 或 5m。"),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    try:
        if not symbol:
            raise ValueError("股票代码不能为空")
        if not data_type:
            raise ValueError("数据类型不能为空")

        cached = get_cache_manager().fetch_from_cache(symbol=symbol, data_type=data_type, timeframe=timeframe or "1d")
        if cached:
            logger.info("✅ 缓存命中", symbol=symbol, data_type=data_type)
            return {
                "success": True,
                "source": "cache",
                "timestamp": _timestamp(),
                "data": _strip_cache_metadata(cached.get("data")),
                "cached_at": cached.get("timestamp"),
            }

        logger.debug("⚠️ 缓存未命中", symbol=symbol, data_type=data_type)
        return {"success": False, "message": "缓存未找到或已过期", "data": None}
    except ValueError as error:
        logger.warning("⚠️ 输入验证失败", error=str(error))
        raise BusinessException(detail=str(error), status_code=400, error_code="INVALID_CACHE_REQUEST")
    except Exception as error:
        logger.error("❌ 读取缓存失败", error=str(error))
        raise BusinessException(detail=str(error), status_code=500, error_code="CACHE_OPERATION_FAILED")


@router.post(
    "/{symbol}/{data_type}",
    description="写入指定标的和数据类型的缓存数据，可设置粒度和缓存保留天数。",
)
async def write_cache_data(
    symbol: str = Path(..., description="股票或资产代码。"),
    data_type: str = Path(..., description="缓存中的数据类型标识。"),
    data: dict[str, Any] = Body(..., openapi_examples=CACHE_WRITE_REQUEST_EXAMPLES),
    timeframe: str | None = Query(None, description="缓存时间粒度，例如 1d、1h 或 5m。"),
    ttl_days: int = Query(7, description="缓存保留天数，必须大于 0。"),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    try:
        if not symbol:
            raise ValueError("股票代码不能为空")
        if not data_type:
            raise ValueError("数据类型不能为空")
        if not data or not isinstance(data, dict):
            raise ValueError("数据必须是有效的JSON对象")
        if ttl_days <= 0:
            raise ValueError("TTL天数必须大于0")

        resolved_timeframe = timeframe or "1d"
        success = get_cache_manager().write_to_cache(
            symbol=symbol,
            data_type=data_type,
            timeframe=resolved_timeframe,
            data=data,
            ttl_days=ttl_days,
        )
        if not success:
            logger.warning("⚠️ 缓存写入失败", symbol=symbol, data_type=data_type)
            raise BusinessException(detail="缓存写入失败，请稍后重试", status_code=500, error_code="CACHE_WRITE_FAILED")

        logger.info("✅ 缓存写入成功", symbol=symbol, data_type=data_type, ttl_days=ttl_days)
        return {
            "success": True,
            "message": "缓存写入成功",
            "symbol": symbol,
            "data_type": data_type,
            "timeframe": resolved_timeframe,
            "ttl_days": ttl_days,
            "timestamp": _timestamp(),
        }
    except ValueError as error:
        logger.warning("⚠️ 输入验证失败", error=str(error))
        raise BusinessException(detail=str(error), status_code=400, error_code="INVALID_CACHE_REQUEST")
    except Exception as error:
        logger.error("❌ 缓存写入异常", error=str(error))
        raise BusinessException(detail=str(error), status_code=500, error_code="CACHE_OPERATION_FAILED")


@router.delete("/{symbol}")
async def invalidate_symbol_cache(symbol: str, current_user: User = Depends(get_current_user)) -> dict[str, Any]:
    try:
        if not symbol:
            raise ValueError("股票代码不能为空")

        deleted_count = get_cache_manager().invalidate_cache(symbol=symbol)
        logger.info("✅ 缓存已清除", symbol=symbol, deleted_count=deleted_count)
        return {
            "success": True,
            "message": "缓存已清除",
            "symbol": symbol,
            "deleted_count": deleted_count,
            "timestamp": _timestamp(),
        }
    except ValueError as error:
        logger.warning("⚠️ 输入验证失败", error=str(error))
        raise BusinessException(detail=str(error), status_code=400, error_code="INVALID_CACHE_REQUEST")
    except Exception as error:
        logger.error("❌ 缓存清除失败", error=str(error))
        raise BusinessException(detail=str(error), status_code=500, error_code="CACHE_OPERATION_FAILED")


@router.get(
    "/{symbol}/{data_type}/fresh",
    description="检查指定缓存键是否仍在允许的新鲜度窗口内，适合调度器或读取前探测。",
)
async def check_cache_freshness(
    symbol: str = Path(..., description="股票或资产代码。"),
    data_type: str = Path(..., description="缓存中的数据类型标识。"),
    max_age_days: int = Query(7, description="允许的最大缓存年龄，单位为天。"),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    try:
        if not symbol:
            raise ValueError("股票代码不能为空")
        if not data_type:
            raise ValueError("数据类型不能为空")
        if max_age_days <= 0:
            raise ValueError("最大缓存年龄必须大于0")

        is_fresh = get_cache_manager().is_cache_valid(symbol=symbol, data_type=data_type, max_age_days=max_age_days)
        logger.debug("缓存新鲜度检查", symbol=symbol, data_type=data_type, is_fresh=is_fresh)
        return {
            "success": True,
            "symbol": symbol,
            "data_type": data_type,
            "is_fresh": is_fresh,
            "max_age_days": max_age_days,
            "timestamp": _timestamp(),
        }
    except ValueError as error:
        logger.warning("⚠️ 输入验证失败", error=str(error))
        raise BusinessException(detail=str(error), status_code=400, error_code="INVALID_CACHE_REQUEST")
    except Exception as error:
        logger.error("❌ 缓存新鲜度检查失败", error=str(error))
        raise BusinessException(detail=str(error), status_code=500, error_code="CACHE_OPERATION_FAILED")
