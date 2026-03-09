"""Control-route helpers extracted from `check_use_mock_data.py`."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Callable, Dict


async def get_today_stats_impl(
    *,
    check_use_mock_data: Callable[[], bool],
    get_database_service: Callable[[], Any],
    logger: logging.Logger,
) -> Dict[str, Any]:
    """获取今日统计数据。"""
    try:
        logger.info("获取今日统计数据")

        if check_use_mock_data():
            logger.info("使用Mock数据源: 获取今日统计")
            today_stats = {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "market_stats": {
                    "total_stocks": 4000,
                    "rising_stocks": 2500,
                    "falling_stocks": 1200,
                    "flat_stocks": 300,
                    "limit_up_count": 45,
                    "limit_down_count": 8,
                    "volume_rank_20": [],
                },
                "alert_stats": {
                    "total_alerts": 25,
                    "price_alerts": 15,
                    "volume_alerts": 8,
                    "other_alerts": 2,
                },
            }

            return {
                "success": True,
                "data": today_stats,
                "timestamp": datetime.now().isoformat(),
                "source": "mock",
            }

        logger.info("使用真实数据库: 获取今日统计")
        db_service = get_database_service()
        if db_service is None:
            return {
                "success": False,
                "message": "数据库服务暂未实现，请使用Mock数据源",
                "timestamp": datetime.now().isoformat(),
                "source": "database",
            }

        try:
            from src.database.database_service import db_service

            result = db_service.get_monitoring_alerts()
            logger.info("真实数据库查询成功: 告警记录")

            return {
                "success": True,
                "data": result,
                "timestamp": datetime.now().isoformat(),
                "source": "database",
            }
        except Exception as error:
            logger.error("真实数据库查询失败: %s", str(error))
            return {
                "success": False,
                "message": f"真实数据库查询失败: {str(error)}",
                "timestamp": datetime.now().isoformat(),
                "source": "database",
            }

    except Exception as error:
        logger.error("获取今日统计失败: %s", str(error))
        return {
            "success": False,
            "message": f"获取今日统计失败: {str(error)}",
            "timestamp": datetime.now().isoformat(),
        }


async def start_monitoring_impl(
    *,
    check_use_mock_data: Callable[[], bool],
    get_database_service: Callable[[], Any],
    logger: logging.Logger,
) -> Dict[str, Any]:
    """启动监控。"""
    try:
        logger.info("启动监控")

        if check_use_mock_data():
            logger.info("使用Mock数据源: 启动监控")
            return {
                "success": True,
                "message": "监控已启动",
                "timestamp": datetime.now().isoformat(),
                "source": "mock",
            }

        logger.info("使用真实数据库: 启动监控")
        db_service = get_database_service()
        if db_service is None:
            return {
                "success": False,
                "message": "数据库服务暂未实现，请使用Mock数据源",
                "timestamp": datetime.now().isoformat(),
                "source": "database",
            }

        try:
            from src.database.database_service import db_service

            logger.info("真实数据库操作: 启动监控")
            return {
                "success": True,
                "message": "监控已启动",
                "timestamp": datetime.now().isoformat(),
                "source": "database",
            }
        except Exception as error:
            logger.error("真实数据库操作失败: %s", str(error))
            return {
                "success": False,
                "message": f"真实数据库操作失败: {str(error)}",
                "timestamp": datetime.now().isoformat(),
                "source": "database",
            }

    except Exception as error:
        logger.error("启动监控失败: %s", str(error))
        return {
            "success": False,
            "message": f"启动监控失败: {str(error)}",
            "timestamp": datetime.now().isoformat(),
        }


async def stop_monitoring_impl(
    *,
    check_use_mock_data: Callable[[], bool],
    get_database_service: Callable[[], Any],
    logger: logging.Logger,
) -> Dict[str, Any]:
    """停止监控。"""
    try:
        logger.info("停止监控")

        if check_use_mock_data():
            logger.info("使用Mock数据源: 停止监控")
            return {
                "success": True,
                "message": "监控已停止",
                "timestamp": datetime.now().isoformat(),
                "source": "mock",
            }

        logger.info("使用真实数据库: 停止监控")
        db_service = get_database_service()
        if db_service is None:
            return {
                "success": False,
                "message": "数据库服务暂未实现，请使用Mock数据源",
                "timestamp": datetime.now().isoformat(),
                "source": "database",
            }

        try:
            from src.database.database_service import db_service

            logger.info("真实数据库操作: 停止监控")
            return {
                "success": True,
                "message": "监控已停止",
                "timestamp": datetime.now().isoformat(),
                "source": "database",
            }
        except Exception as error:
            logger.error("真实数据库操作失败: %s", str(error))
            return {
                "success": False,
                "message": f"真实数据库操作失败: {str(error)}",
                "timestamp": datetime.now().isoformat(),
                "source": "database",
            }

    except Exception as error:
        logger.error("停止监控失败: %s", str(error))
        return {
            "success": False,
            "message": f"停止监控失败: {str(error)}",
            "timestamp": datetime.now().isoformat(),
        }


async def get_monitoring_status_impl(
    *,
    check_use_mock_data: Callable[[], bool],
    get_database_service: Callable[[], Any],
    logger: logging.Logger,
) -> Dict[str, Any]:
    """获取监控状态。"""
    try:
        logger.info("获取监控状态")

        if check_use_mock_data():
            logger.info("使用Mock数据源: 获取监控状态")
            status = {
                "is_running": True,
                "start_time": "2024-11-13 09:00:00",
                "last_update": datetime.now().isoformat(),
                "monitored_symbols": 100,
                "active_alerts": 12,
                "status": "healthy",
            }

            return {
                "success": True,
                "data": status,
                "timestamp": datetime.now().isoformat(),
                "source": "mock",
            }

        logger.info("使用真实数据库: 获取监控状态")
        db_service = get_database_service()
        if db_service is None:
            return {
                "success": False,
                "message": "数据库服务暂未实现，请使用Mock数据源",
                "timestamp": datetime.now().isoformat(),
                "source": "database",
            }

        try:
            from src.database.database_service import db_service

            result = db_service.get_monitoring_alerts()
            logger.info("真实数据库查询成功: 实时监控数据")

            return {
                "success": True,
                "data": result,
                "timestamp": datetime.now().isoformat(),
                "source": "database",
            }
        except Exception as error:
            logger.error("真实数据库查询失败: %s", str(error))
            return {
                "success": False,
                "message": f"真实数据库查询失败: {str(error)}",
                "timestamp": datetime.now().isoformat(),
                "source": "database",
            }

    except Exception as error:
        logger.error("获取监控状态失败: %s", str(error))
        return {
            "success": False,
            "message": f"获取监控状态失败: {str(error)}",
            "timestamp": datetime.now().isoformat(),
        }
