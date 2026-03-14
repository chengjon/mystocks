import structlog
from fastapi import FastAPI

from app.core.config import settings
from app.router_registry import register_api_routes

logger = structlog.get_logger()


def register_all_routers(app: FastAPI):
    """
    兼容旧工厂入口，统一委托到 central router registry。
    """
    logger.info("开始注册所有API路由器（delegating to router_registry）...")
    register_api_routes(app, use_mock_apis=settings.use_mock_apis, logger=logger)
    logger.info("所有API路由器注册完成。")
