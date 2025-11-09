"""
数据库连接管理 - Week 3 简化版
仅使用 PostgreSQL + TimescaleDB
复用现有 MyStocks 数据库连接
"""

import structlog
from typing import Optional, Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import pandas as pd

from app.core.config import settings, get_postgresql_connection_string

logger = structlog.get_logger()

# SQLAlchemy 声明基类（用于ORM模型）
Base = declarative_base()

# 数据库连接池 - Week 3 简化: 仅PostgreSQL
engines = {}
sessions = {}


def get_postgresql_engine():
    """
    获取 PostgreSQL 数据库引擎（单例模式）

    连接池配置（Phase 3优化）:
    - pool_size=20: 核心连接数（从10提升至20）
    - max_overflow=40: 最大溢出连接（从20提升至40）
    - pool_timeout=30: 连接超时30秒
    - pool_pre_ping=True: 连接健康检查
    - pool_recycle=3600: 连接回收时间（1小时）
    - echo_pool=False: 连接池事件日志（生产环境关闭）
    """
    if "postgresql" not in engines:
        connection_string = get_postgresql_connection_string()
        engines["postgresql"] = create_engine(
            connection_string,
            pool_size=20,  # Phase 3: 10 → 20 (核心连接数提升)
            max_overflow=40,  # Phase 3: 20 → 40 (最大溢出连接提升)
            pool_timeout=30,  # Phase 3: 新增 (连接获取超时30秒)
            pool_pre_ping=True,  # 连接健康检查（每次使用前ping）
            pool_recycle=3600,  # 连接回收时间（3600秒=1小时）
            echo=settings.debug,  # 调试模式打印SQL
            echo_pool=False,  # Phase 3: 连接池事件日志（生产环境关闭）
        )
        logger.info(
            "PostgreSQL engine created (Phase 3 optimized pool)",
            database=settings.postgresql_database,
            pool_size=20,
            max_overflow=40,
            pool_timeout=30,
        )
    return engines["postgresql"]


def get_postgresql_session() -> Session:
    """获取 PostgreSQL 会话（工厂模式）"""
    if "postgresql" not in sessions:
        engine = get_postgresql_engine()
        sessions["postgresql"] = sessionmaker(
            autocommit=False, autoflush=False, bind=engine
        )
    return sessions["postgresql"]()


# Week 3 兼容性别名 - 将MySQL请求重定向到PostgreSQL
def get_mysql_engine():
    """兼容性别名: Week 3简化后，MySQL请求重定向到PostgreSQL"""
    logger.warning(
        "get_mysql_engine() called, redirecting to PostgreSQL (Week 3 simplified)"
    )
    return get_postgresql_engine()


def get_mysql_session() -> Session:
    """兼容性别名: Week 3简化后，MySQL会话重定向到PostgreSQL"""
    logger.warning(
        "get_mysql_session() called, redirecting to PostgreSQL (Week 3 simplified)"
    )
    return get_postgresql_session()


def close_all_connections():
    """关闭所有数据库连接"""
    for name, engine in engines.items():
        engine.dispose()
        logger.info(f"{name} connection closed")


# 复用现有 MyStocks 数据访问逻辑 (可选，如果环境变量不完整则跳过)
try:
    import sys
    import os

    # 添加项目根目录到 Python 路径
    project_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../../../")
    )
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    from src.data_access import PostgreSQLDataAccess

    # 创建PostgreSQL数据访问实例
    postgresql_access = PostgreSQLDataAccess()

    logger.info("MyStocks PostgreSQLDataAccess loaded successfully")

except (ImportError, OSError, EnvironmentError) as e:
    # Week 3 简化: 如果MyStocks核心模块不可用，跳过（web backend可独立运行）
    logger.warning(
        f"MyStocks data access modules not available (expected in Week 3 simplified mode): {e}"
    )
    postgresql_access = None


class DatabaseService:
    """数据库服务类 - Week 3 简化版 (PostgreSQL-only)"""

    def __init__(self):
        """初始化数据库服务（仅PostgreSQL）"""
        self.postgresql_engine = get_postgresql_engine()
        logger.info("DatabaseService initialized (PostgreSQL-only, Week 3 simplified)")

    def query_stocks_basic(self, limit: int = 100) -> pd.DataFrame:
        """查询股票基本信息"""
        try:
            if postgresql_access:
                # 使用 PostgreSQLDataAccess
                return postgresql_access.query("symbols_info", limit=limit)
            else:
                # 直接查询 PostgreSQL
                with get_postgresql_session() as session:
                    query = text(
                        """
                        SELECT symbol, name, industry, area, market, list_date
                        FROM symbols_info
                        LIMIT :limit
                    """
                    )
                    result = session.execute(query, {"limit": limit})
                    return pd.DataFrame(result.fetchall(), columns=result.keys())
        except Exception as e:
            logger.error(f"Failed to query stocks basic: {e}")
            return pd.DataFrame()

    def query_daily_kline(
        self, symbol: str, start_date: str, end_date: str
    ) -> pd.DataFrame:
        """查询日线数据"""
        try:
            if postgresql_access:
                filters = {
                    "symbol": symbol,
                    "date >= ": start_date,
                    "date <= ": end_date,
                }
                return postgresql_access.query("daily_kline", filters=filters)
            else:
                # 直接查询 PostgreSQL
                with get_postgresql_session() as session:
                    query = text(
                        """
                        SELECT date, open, high, low, close, volume, amount
                        FROM daily_kline
                        WHERE symbol = :symbol
                        AND date >= :start_date
                        AND date <= :end_date
                        ORDER BY date
                    """
                    )
                    result = session.execute(
                        query,
                        {
                            "symbol": symbol,
                            "start_date": start_date,
                            "end_date": end_date,
                        },
                    )
                    return pd.DataFrame(result.fetchall(), columns=result.keys())
        except Exception as e:
            logger.error(f"Failed to query daily kline: {e}")
            return pd.DataFrame()


# 创建全局数据库服务实例（延迟初始化）
db_service = None


def get_db_service() -> DatabaseService:
    """获取数据库服务实例（单例模式，延迟初始化）"""
    global db_service
    if db_service is None:
        db_service = DatabaseService()
    return db_service


# FastAPI 依赖注入函数 - Week 3 简化: 使用PostgreSQL
def get_db() -> Session:
    """获取数据库会话（用于FastAPI依赖注入）"""
    session = get_postgresql_session()
    try:
        yield session
    finally:
        session.close()


# Session工厂 - 用于向后兼容
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=get_postgresql_engine()
)
