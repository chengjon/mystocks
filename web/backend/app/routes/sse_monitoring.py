"""
SSE Performance Monitoring Routes

Provides REST API endpoints for monitoring SSE performance metrics,
health status, and system resource usage.
"""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from datetime import datetime

from ..core.sse_manager import get_sse_manager, get_sse_broadcaster

logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(prefix="/api/sse", tags=["SSE监控"])


@router.get("/performance/stats", summary="获取SSE性能统计")
async def get_performance_stats():
    """
    获取SSE系统的完整性能统计信息

    Returns:
        SSE性能统计数据，包括连接统计、系统资源使用等
    """
    try:
        manager = get_sse_manager()
        stats = manager.get_performance_stats()
        return {"success": True, "data": stats, "message": "SSE性能统计获取成功"}
    except Exception as e:
        logger.error(f"获取SSE性能统计失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取性能统计失败: {str(e)}")


@router.get("/performance/connections", summary="获取连接指标")
async def get_connection_metrics(
    client_id: Optional[str] = Query(None, description="特定客户端ID，不提供则返回所有连接"),
):
    """
    获取SSE连接的详细指标

    Args:
        client_id: 可选，特定客户端ID

    Returns:
        连接指标详情
    """
    try:
        manager = get_sse_manager()
        metrics = manager.get_connection_metrics(client_id)
        return {"success": True, "data": metrics, "message": "连接指标获取成功"}
    except Exception as e:
        logger.error(f"获取连接指标失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取连接指标失败: {str(e)}")


@router.get("/health/channel/{channel}", summary="获取频道健康状态")
async def get_channel_health(channel: str):
    """
    获取特定SSE频道的健康状态

    Args:
        channel: 频道名称 (training, backtest, alerts, dashboard)

    Returns:
        频道健康状态详情
    """
    try:
        manager = get_sse_manager()
        health = manager.get_channel_health(channel)
        return {
            "success": True,
            "data": health,
            "message": f"频道 {channel} 健康状态获取成功",
        }
    except Exception as e:
        logger.error(f"获取频道健康状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取频道健康状态失败: {str(e)}")


@router.get("/health/system", summary="获取系统健康状态")
async def get_system_health():
    """
    获取整个SSE系统的健康状态

    Returns:
        系统健康状态详情
    """
    try:
        manager = get_sse_manager()
        health = manager.get_system_health()
        return {"success": True, "data": health, "message": "系统健康状态获取成功"}
    except Exception as e:
        logger.error(f"获取系统健康状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取系统健康状态失败: {str(e)}")


@router.get("/channels", summary="获取活跃频道列表")
async def get_active_channels():
    """
    获取当前所有活跃的SSE频道列表

    Returns:
        活跃频道列表和连接数
    """
    try:
        manager = get_sse_manager()
        channels = manager.get_channels()
        channel_info = {}

        for channel in channels:
            client_count = manager.get_connection_count(channel)
            channel_info[channel] = {
                "client_count": client_count,
                "clients": manager.get_clients(channel),
            }

        return {
            "success": True,
            "data": {
                "active_channels": channels,
                "total_channels": len(channels),
                "channel_details": channel_info,
            },
            "message": "活跃频道列表获取成功",
        }
    except Exception as e:
        logger.error(f"获取活跃频道列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取频道列表失败: {str(e)}")


@router.post("/performance/reset-metrics", summary="重置性能指标")
async def reset_metrics():
    """
    重置SSE系统的性能指标

    Returns:
        重置操作结果
    """
    try:
        manager = get_sse_manager()
        success = manager.reset_metrics()

        if success:
            return {
                "success": True,
                "message": "性能指标重置成功",
                "timestamp": datetime.now().isoformat(),
            }
        else:
            return {
                "success": False,
                "message": "性能指标重置失败",
                "timestamp": datetime.now().isoformat(),
            }
    except Exception as e:
        logger.error(f"重置性能指标失败: {e}")
        raise HTTPException(status_code=500, detail=f"重置性能指标失败: {str(e)}")


@router.get("/status", summary="获取SSE服务状态")
async def get_sse_status():
    """
    获取SSE服务的基础状态信息

    Returns:
        SSE服务状态
    """
    try:
        manager = get_sse_manager()
        get_sse_broadcaster()

        # 基础状态
        total_connections = manager.get_connection_count()
        active_channels = manager.get_channels()

        # 系统健康检查
        system_health = manager.get_system_health()

        return {
            "success": True,
            "data": {
                "service_status": "running",
                "total_connections": total_connections,
                "active_channels": len(active_channels),
                "channel_list": active_channels,
                "system_health": system_health.get("status", "unknown"),
                "timestamp": datetime.now().isoformat(),
                "features": {
                    "performance_optimizer": True,
                    "event_caching": True,
                    "load_balancing": True,
                    "health_monitoring": True,
                },
            },
            "message": "SSE服务状态获取成功",
        }
    except Exception as e:
        logger.error(f"获取SSE服务状态失败: {e}")
        return {
            "success": False,
            "data": {
                "service_status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            },
            "message": "SSE服务状态获取失败",
        }


@router.get("/performance/optimizer-stats", summary="获取性能优化器统计")
async def get_optimizer_stats():
    """
    获取SSE性能优化器的详细统计信息

    Returns:
        性能优化器统计数据
    """
    try:
        manager = get_sse_manager()

        # 获取优化器统计
        if hasattr(manager, "performance_optimizer"):
            optimizer = manager.performance_optimizer
            optimizer_stats = optimizer.get_performance_stats() if hasattr(optimizer, "get_performance_stats") else {}

            return {
                "success": True,
                "data": {
                    "optimizer_stats": optimizer_stats,
                    "enabled": True,
                    "timestamp": datetime.now().isoformat(),
                },
                "message": "性能优化器统计获取成功",
            }
        else:
            return {
                "success": True,
                "data": {
                    "optimizer_stats": {},
                    "enabled": False,
                    "message": "性能优化器未启用",
                    "timestamp": datetime.now().isoformat(),
                },
                "message": "性能优化器未启用",
            }
    except Exception as e:
        logger.error(f"获取性能优化器统计失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取性能优化器统计失败: {str(e)}")


# 依赖函数：确保SSE管理器已初始化
async def ensure_sse_manager():
    """确保SSE管理器已初始化"""
    try:
        get_sse_manager()
        return True
    except Exception as e:
        logger.error(f"SSE管理器未初始化: {e}")
        raise HTTPException(status_code=503, detail="SSE服务不可用")


# 健康检查端点
@router.get("/health", summary="SSE健康检查")
async def health_check():
    """
    简单的健康检查端点

    Returns:
        健康状态
    """
    try:
        manager = get_sse_manager()
        # 简单检查管理器是否可用
        total_connections = manager.get_connection_count()

        return {
            "status": "healthy",
            "service": "sse",
            "connections": total_connections,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "sse",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


# 导出路由器
__all__ = ["router"]
