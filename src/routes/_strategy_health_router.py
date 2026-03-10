"""Strategy health sub-router."""

import logging
from datetime import datetime

from fastapi import APIRouter

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health")
async def check_strategy_health():
    """检查策略服务健康状态"""
    try:
        from src.routes.strategy_routes import check_use_mock_data, get_database_service

        if check_use_mock_data():
            logger.info("检查Mock数据源健康状态")
            return {
                "status": "healthy",
                "service": "Strategy",
                "source": "mock",
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0",
            }

        logger.info("检查真实数据库健康状态")
        db_service = get_database_service()
        if db_service is None:
            return {
                "status": "unavailable",
                "service": "Strategy",
                "source": "database",
                "message": "数据库服务暂未实现",
                "timestamp": datetime.now().isoformat(),
            }

        try:
            from src.database.database_service import db_service

            logger.info("真实数据库健康检查: 策略服务")
            return {
                "status": "healthy",
                "service": "Strategy",
                "source": "database",
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0",
            }
        except Exception as e:
            logger.error("真实数据库健康检查失败: %s", str(e))
            return {
                "status": "unhealthy",
                "service": "Strategy",
                "source": "database",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    except Exception as e:
        logger.error("检查策略服务健康状态失败: %s", str(e))
        return {
            "status": "unhealthy",
            "service": "Strategy",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }
