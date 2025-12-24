"""
缓存管理 API 路由

提供缓存数据的HTTP接口:
- 缓存统计查询
- 缓存数据读取
- 缓存数据写入
- 缓存清除

Endpoints:
- GET  /cache/status              - 获取缓存统计信息
- GET  /cache/{symbol}/{type}     - 读取特定缓存数据
- POST /cache/{symbol}/{type}     - 写入/更新缓存数据
- DELETE /cache/{symbol}          - 清除符号缓存
- DELETE /cache                   - 清除所有缓存
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from datetime import datetime
from typing import Dict, Any, Optional
import structlog

from app.core.cache_manager import get_cache_manager
from app.core.cache_eviction import (
    get_eviction_strategy,
    get_eviction_scheduler,
)
from app.core.cache_prewarming import (
    get_cache_monitor,
    get_prewarming_strategy,
)
from app.core.responses import create_health_response
from app.core.security import get_current_user, User

logger = structlog.get_logger()

router = APIRouter(prefix="/cache", tags=["cache"])


# ==================== 健康检查 ====================


@router.get("/health")
async def health_check():
    """
    缓存服务健康检查

    Returns:
        统一格式的健康检查响应
    """
    try:
        cache_mgr = get_cache_manager()
        stats = cache_mgr.get_cache_stats()
        strategy = get_eviction_strategy()

        return create_health_response(
            service="cache",
            status="healthy",
            details={
                "hit_rate": stats.get("hit_rate", 0),
                "cache_hits": stats.get("cache_hits", 0),
                "cache_misses": stats.get("cache_misses", 0),
                "total_reads": stats.get("total_reads", 0),
                "total_writes": stats.get("total_writes", 0),
                "ttl_days": strategy.get("ttl_days", 7) if strategy else 7,
                "version": "1.0.0",
            },
        )
    except Exception as e:
        return create_health_response(
            service="cache",
            status="unhealthy",
            details={"error": str(e), "version": "1.0.0"},
        )


# ==================== 缓存统计 ====================


@router.get("/status")
async def get_cache_status(
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    获取缓存统计信息

    Returns:
        缓存统计信息，包含:
        - hit_rate: 缓存命中率
        - cache_hits: 命中次数
        - cache_misses: 未命中次数
        - total_reads: 总读取次数
        - total_writes: 总写入次数
        - timestamp: 统计时间戳

    Examples:
        GET /api/cache/status
        Response:
        {
            "success": true,
            "timestamp": "2025-11-06T12:34:56.789Z",
            "data": {
                "total_reads": 1000,
                "total_writes": 500,
                "cache_hits": 850,
                "cache_misses": 150,
                "hit_rate": 0.85,
                "hit_rate_percent": "85.0%",
                ...
            }
        }
    """
    try:
        cache_mgr = get_cache_manager()
        stats = cache_mgr.get_cache_stats()

        logger.info("✅ 获取缓存统计", hit_rate=stats.get("hit_rate", 0))

        return {
            "success": True,
            "timestamp": datetime.utcnow().isoformat(),
            "data": stats,
        }

    except Exception as e:
        logger.error("❌ 获取缓存统计失败", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 缓存读取 ====================


@router.get("/{symbol}/{data_type}")
async def get_cached_data(
    symbol: str,
    data_type: str,
    timeframe: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    读取特定的缓存数据

    Args:
        symbol: 股票代码 (e.g., "000001")
        data_type: 数据类型 (e.g., "fund_flow", "etf", "chip_race")
        timeframe: 时间维度 (可选，e.g., "1d", "3d")

    Returns:
        缓存数据（如果存在），或错误信息

    Examples:
        GET /api/cache/000001/fund_flow
        GET /api/cache/000001/etf?timeframe=1d

        Response (缓存命中):
        {
            "success": true,
            "source": "cache",
            "timestamp": "2025-11-06T...",
            "data": {
                "main_net_inflow": 10000,
                ...
            }
        }

        Response (缓存未命中):
        {
            "success": false,
            "message": "缓存未找到",
            "data": null
        }
    """
    try:
        cache_mgr = get_cache_manager()

        # 验证输入
        if not symbol or len(symbol) == 0:
            raise ValueError("股票代码不能为空")
        if not data_type or len(data_type) == 0:
            raise ValueError("数据类型不能为空")

        timeframe = timeframe or "1d"

        # 读取缓存
        cached = cache_mgr.fetch_from_cache(
            symbol=symbol, data_type=data_type, timeframe=timeframe
        )

        if cached:
            logger.info(
                "✅ 缓存命中",
                symbol=symbol,
                data_type=data_type,
            )
            return {
                "success": True,
                "source": "cache",
                "timestamp": datetime.utcnow().isoformat(),
                "data": cached.get("data"),
                "cached_at": cached.get("timestamp"),
            }

        logger.debug(
            "⚠️ 缓存未命中",
            symbol=symbol,
            data_type=data_type,
        )
        return {
            "success": False,
            "message": "缓存未找到或已过期",
            "data": None,
        }

    except ValueError as e:
        logger.warning("⚠️ 输入验证失败", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("❌ 读取缓存失败", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 缓存写入 ====================


@router.post("/{symbol}/{data_type}")
async def write_cache_data(
    symbol: str,
    data_type: str,
    data: Dict[str, Any],
    timeframe: Optional[str] = Query(None),
    ttl_days: int = Query(7),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    写入或更新缓存数据

    Args:
        symbol: 股票代码
        data_type: 数据类型
        data: 要缓存的数据对象
        timeframe: 时间维度 (可选)
        ttl_days: 缓存生存时间 (天数，默认7天)

    Returns:
        写入结果

    Examples:
        POST /api/cache/000001/fund_flow
        Body:
        {
            "data": {
                "main_net_inflow": 10000,
                "rate": 0.5
            },
            "timeframe": "1d",
            "ttl_days": 1
        }

        Response:
        {
            "success": true,
            "message": "缓存写入成功",
            "symbol": "000001",
            "data_type": "fund_flow",
            "timestamp": "2025-11-06T..."
        }
    """
    try:
        cache_mgr = get_cache_manager()

        # 验证输入
        if not symbol or len(symbol) == 0:
            raise ValueError("股票代码不能为空")
        if not data_type or len(data_type) == 0:
            raise ValueError("数据类型不能为空")
        if not data or not isinstance(data, dict):
            raise ValueError("数据必须是有效的JSON对象")
        if ttl_days <= 0:
            raise ValueError("TTL天数必须大于0")

        timeframe = timeframe or "1d"

        # 写入缓存
        success = cache_mgr.write_to_cache(
            symbol=symbol,
            data_type=data_type,
            timeframe=timeframe,
            data=data,
            ttl_days=ttl_days,
        )

        if success:
            logger.info(
                "✅ 缓存写入成功",
                symbol=symbol,
                data_type=data_type,
                ttl_days=ttl_days,
            )
            return {
                "success": True,
                "message": "缓存写入成功",
                "symbol": symbol,
                "data_type": data_type,
                "timeframe": timeframe,
                "ttl_days": ttl_days,
                "timestamp": datetime.utcnow().isoformat(),
            }

        logger.warning(
            "⚠️ 缓存写入失败",
            symbol=symbol,
            data_type=data_type,
        )
        raise HTTPException(status_code=500, detail="缓存写入失败，请稍后重试")

    except ValueError as e:
        logger.warning("⚠️ 输入验证失败", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("❌ 缓存写入异常", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 缓存清除 ====================


@router.delete("/{symbol}")
async def invalidate_symbol_cache(
    symbol: str, current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    清除特定符号的缓存

    Args:
        symbol: 股票代码

    Returns:
        清除结果

    Examples:
        DELETE /api/cache/000001

        Response:
        {
            "success": true,
            "message": "缓存已清除",
            "symbol": "000001",
            "deleted_count": 3,
            "timestamp": "2025-11-06T..."
        }
    """
    try:
        cache_mgr = get_cache_manager()

        # 验证输入
        if not symbol or len(symbol) == 0:
            raise ValueError("股票代码不能为空")

        # 清除缓存
        deleted_count = cache_mgr.invalidate_cache(symbol=symbol)

        logger.info(
            "✅ 缓存已清除",
            symbol=symbol,
            deleted_count=deleted_count,
        )

        return {
            "success": True,
            "message": "缓存已清除",
            "symbol": symbol,
            "deleted_count": deleted_count,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except ValueError as e:
        logger.warning("⚠️ 输入验证失败", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("❌ 缓存清除失败", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("")
async def clear_all_cache(
    confirm: bool = Query(False), current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    清除所有缓存 (需要确认)

    Args:
        confirm: 确认标志，必须为True才能执行清除

    Returns:
        清除结果

    Examples:
        DELETE /api/cache?confirm=true

        Response:
        {
            "success": true,
            "message": "所有缓存已清除",
            "deleted_count": 100,
            "timestamp": "2025-11-06T..."
        }
    """
    try:
        if not confirm:
            raise ValueError("需要确认才能清除所有缓存，请设置 confirm=true")

        cache_mgr = get_cache_manager()

        # 清除所有缓存
        deleted_count = cache_mgr.invalidate_cache()

        logger.warning(
            "🗑️ 所有缓存已清除",
            deleted_count=deleted_count,
        )

        return {
            "success": True,
            "message": "所有缓存已清除",
            "deleted_count": deleted_count,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except ValueError as e:
        logger.warning("⚠️ 输入验证失败", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("❌ 清除所有缓存失败", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 缓存验证 ====================


@router.get("/{symbol}/{data_type}/fresh")
async def check_cache_freshness(
    symbol: str,
    data_type: str,
    max_age_days: int = Query(7),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    检查缓存是否新鲜（有效且未过期）

    Args:
        symbol: 股票代码
        data_type: 数据类型
        max_age_days: 最大缓存年龄（天）

    Returns:
        缓存新鲜度检查结果

    Examples:
        GET /api/cache/000001/fund_flow/fresh

        Response:
        {
            "success": true,
            "symbol": "000001",
            "data_type": "fund_flow",
            "is_fresh": true,
            "max_age_days": 7,
            "timestamp": "2025-11-06T..."
        }
    """
    try:
        cache_mgr = get_cache_manager()

        # 验证输入
        if not symbol or len(symbol) == 0:
            raise ValueError("股票代码不能为空")
        if not data_type or len(data_type) == 0:
            raise ValueError("数据类型不能为空")
        if max_age_days <= 0:
            raise ValueError("最大缓存年龄必须大于0")

        # 检查缓存新鲜度
        is_fresh = cache_mgr.is_cache_valid(
            symbol=symbol,
            data_type=data_type,
            max_age_days=max_age_days,
        )

        logger.debug(
            "缓存新鲜度检查",
            symbol=symbol,
            data_type=data_type,
            is_fresh=is_fresh,
        )

        return {
            "success": True,
            "symbol": symbol,
            "data_type": data_type,
            "is_fresh": is_fresh,
            "max_age_days": max_age_days,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except ValueError as e:
        logger.warning("⚠️ 输入验证失败", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("❌ 缓存新鲜度检查失败", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 缓存淘汰 ====================


@router.post("/evict/manual")
async def manual_cache_eviction(
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    手动触发缓存淘汰任务

    Returns:
        淘汰结果，包含:
        - success: 操作成功标志
        - message: 操作消息
        - deleted_count: 删除的缓存条数
        - timestamp: 操作时间戳

    Examples:
        POST /api/cache/evict/manual

        Response:
        {
            "success": true,
            "message": "缓存淘汰成功",
            "deleted_count": 150,
            "timestamp": "2025-11-06T..."
        }
    """
    try:
        scheduler = get_eviction_scheduler()
        result = scheduler.manual_cleanup()

        if result.get("success"):
            logger.info(
                "✅ 手动缓存淘汰成功",
                deleted_count=result.get("deleted_count", 0),
            )
        else:
            logger.warning(
                "⚠️ 手动缓存淘汰失败",
                message=result.get("message"),
            )

        return {
            "success": result.get("success", False),
            "message": result.get("message", "缓存淘汰失败"),
            "deleted_count": result.get("deleted_count", 0),
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error("❌ 手动缓存淘汰异常", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/eviction/stats")
async def get_eviction_statistics(
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    获取缓存淘汰策略统计信息

    Returns:
        淘汰策略统计，包含:
        - ttl_days: TTL天数
        - frequency_tracking: 访问频率追踪统计
        - hot_data: 热点数据列表
        - cache_stats: 缓存统计
        - timestamp: 统计时间戳

    Examples:
        GET /api/cache/eviction/stats

        Response:
        {
            "success": true,
            "data": {
                "ttl_days": 7,
                "frequency_tracking": {
                    "total_tracked": 100,
                    "total_accesses": 5000,
                    "average_frequency": 50.0
                },
                "hot_data": [
                    {
                        "cache_key": "000001:fund_flow:1d",
                        "access_count": 500,
                        "last_access": "2025-11-06T..."
                    }
                ],
                "cache_stats": {
                    "hit_rate": 0.85,
                    "cache_hits": 850,
                    "cache_misses": 150
                }
            },
            "timestamp": "2025-11-06T..."
        }
    """
    try:
        strategy = get_eviction_strategy()

        # 获取统计信息
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
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error("❌ 获取淘汰统计失败", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 缓存预热与监控 ====================


@router.post("/prewarming/trigger")
async def trigger_cache_prewarming(
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    触发缓存预热任务

    Returns:
        预热结果，包含:
        - success: 操作成功标志
        - prewarmed_count: 预热的缓存条数
        - failed_count: 失败的缓存条数
        - elapsed_seconds: 预热耗时

    Examples:
        POST /api/cache/prewarming/trigger

        Response:
        {
            "success": true,
            "message": "缓存预热成功",
            "prewarmed_count": 20,
            "failed_count": 0,
            "elapsed_seconds": 2.5,
            "timestamp": "2025-11-06T..."
        }
    """
    try:
        strategy = get_prewarming_strategy()
        result = strategy.prewarm_cache()

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
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error("❌ 缓存预热失败", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/prewarming/status")
async def get_prewarming_status(
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    获取缓存预热状态

    Returns:
        预热状态信息，包含:
        - last_prewarming: 最后预热时间
        - prewarmed_keys_count: 已预热的缓存键数

    Examples:
        GET /api/cache/prewarming/status

        Response:
        {
            "success": true,
            "data": {
                "last_prewarming": "2025-11-06T12:00:00.000000",
                "prewarmed_keys_count": 20
            },
            "timestamp": "2025-11-06T..."
        }
    """
    try:
        strategy = get_prewarming_strategy()
        status = strategy.get_prewarming_status()

        logger.info("✅ 获取预热状态")

        return {
            "success": True,
            "data": status,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error("❌ 获取预热状态失败", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/monitoring/metrics")
async def get_cache_monitoring_metrics(
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    获取缓存监控指标

    Returns:
        缓存性能指标，包含:
        - hit_rate: 命中率
        - hit_count: 命中次数
        - miss_count: 未命中次数
        - average_latency_ms: 平均延迟（毫秒）
        - health_status: 健康状态

    Examples:
        GET /api/cache/monitoring/metrics

        Response:
        {
            "success": true,
            "data": {
                "hit_count": 850,
                "miss_count": 150,
                "hit_rate": 85.0,
                "average_latency_ms": 2.5,
                "health_status": "healthy"
            },
            "timestamp": "2025-11-06T..."
        }
    """
    try:
        monitor = get_cache_monitor()
        metrics = monitor.get_metrics()

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
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error("❌ 获取监控指标失败", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/monitoring/health")
async def get_cache_health_status(
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    获取缓存系统健康状态

    Returns:
        缓存系统健康状态，包含:
        - status: 健康状态 (healthy/warning/critical)
        - hit_rate: 命中率
        - metrics: 详细指标

    Examples:
        GET /api/cache/monitoring/health

        Response:
        {
            "success": true,
            "status": "healthy",
            "hit_rate": 85.0,
            "message": "缓存系统运行正常，命中率 85.0%",
            "timestamp": "2025-11-06T..."
        }
    """
    try:
        strategy = get_prewarming_strategy()
        health = strategy.get_health_status()

        status = health.get("status", "unknown")
        hit_rate = health.get("hit_rate", 0)

        # 构建健康消息
        if status == "healthy":
            message = f"缓存系统运行正常，命中率 {hit_rate:.1f}%"
        else:
            message = f"缓存系统警告：命中率 {hit_rate:.1f}%，建议手动预热"

        logger.info("✅ 获取缓存健康状态", status=status, hit_rate=hit_rate)

        return {
            "success": True,
            "status": status,
            "hit_rate": hit_rate,
            "hit_rate_percent": health.get("hit_rate_percent", "0.0%"),
            "message": message,
            "total_reads": health.get("total_reads", 0),
            "average_latency_ms": health.get("average_latency_ms", 0),
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error("❌ 获取健康状态失败", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
