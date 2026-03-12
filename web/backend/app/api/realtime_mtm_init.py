"""
Real-time MTM API Initialization
实时市值 API 初始化模块

在应用启动时初始化 Phase 12.4 的 DDD 架构适配器。

Author: Claude Code
Date: 2026-01-09
Phase: 12.4 - API Layer Integration
"""

from typing import Optional

import structlog
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.utils.redis_runtime_config import get_redis_connection_kwargs

logger = structlog.get_logger()


# 全局数据库会话
_db_session: Optional[Session] = None
_engine = None


def get_database_session() -> Session:
    """获取数据库会话"""
    global _db_session, _engine

    if _db_session is None:
        # 从配置读取数据库 URL
        from web.backend.app.core.config import settings

        # 创建数据库引擎
        database_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://")
        _engine = create_engine(database_url)
        SessionLocal = sessionmaker(bind=_engine)
        _db_session = SessionLocal()

        logger.info("✅ Database session created: %(database_url)s")

    return _db_session


def initialize_realtime_mtm():
    """
    初始化实时市值系统（在应用启动时调用）

    这个函数应该放在 FastAPI 应用的 startup 事件中
    """
    try:
        # 获取数据库会话
        db_session = get_database_session()

        # 尝试创建事件总线
        event_bus = None
        try:
            from src.infrastructure.messaging.redis_event_bus import RedisEventBus

            redis_kwargs = get_redis_connection_kwargs("monitoring_events", decode_responses=True)
            event_bus = RedisEventBus(host=redis_kwargs["host"], port=redis_kwargs["port"], db=redis_kwargs["db"], password=redis_kwargs["password"])
            logger.info("✅ Redis Event Bus connected for Real-time MTM")
        except Exception:
            logger.warning("⚠️ Redis not available for Real-time MTM: %(e)s")

        # 初始化适配器
        from web.backend.app.api.realtime_mtm_adapter import initialize_adapter

        adapter = initialize_adapter(db_session, event_bus)

        logger.info("✅ Real-time MTM system initialized successfully")
        return adapter

    except Exception:
        logger.error("❌ Failed to initialize Real-time MTM: %(e)s")
        raise


def get_realtime_mtm_adapter():
    """
    获取实时市值适配器（便捷方法）

    Returns:
        RealtimeMTMAdapter: 适配器实例
    """
    from web.backend.app.api.realtime_mtm_adapter import get_realtime_mtm_adapter as get_adapter

    return get_adapter()


def shutdown_realtime_mtm():
    """关闭实时市值系统（在应用关闭时调用）"""
    global _db_session, _engine

    try:
        if _db_session:
            _db_session.close()
            _db_session = None
            logger.info("✅ Database session closed")

        if _engine:
            _engine.dispose()
            _engine = None
            logger.info("✅ Database engine disposed")

    except Exception:
        logger.error("❌ Error shutting down Real-time MTM: %(e)s")


# FastAPI 生命周期事件处理器
def register_startup_events(app):
    """
    注册 FastAPI 启动事件

    Args:
        app: FastAPI 应用实例
    """

    @app.on_event("startup")
    async def startup_event():
        logger.info("🚀 Starting Real-time MTM system...")
        initialize_realtime_mtm()

    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info("🛑 Shutting down Real-time MTM system...")
        shutdown_realtime_mtm()


if __name__ == "__main__":
    """测试初始化"""
    initialize_realtime_mtm()

    adapter = get_realtime_mtm_adapter()
    if adapter:
        logger.info("Real-time MTM adapter ready")
        logger.info("Metrics: %s", adapter.get_metrics())
