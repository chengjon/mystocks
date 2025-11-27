"""
数据库连接管理 - Week 3 简化版
仅使用 PostgreSQL + TimescaleDB
复用现有 MyStocks 数据库连接
"""

import functools

# 添加重试逻辑
import time
from typing import Any, Dict, Optional

import pandas as pd
import structlog
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.core.config import get_postgresql_connection_string, settings


def db_retry(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    数据库连接重试装饰器

    Args:
        max_retries: 最大重试次数
        delay: 初始延迟时间（秒）
        backoff: 延迟倍数
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            current_delay = delay

            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    error_msg = str(e).lower()

                    # 检查是否是连接相关错误，需要重试
                    if any(
                        keyword in error_msg
                        for keyword in [
                            "connection",
                            "timeout",
                            "network",
                            "refused",
                            "closed",
                            "reset",
                            "db_connection",
                        ]
                    ):
                        retries += 1
                        if retries < max_retries:
                            logger.warning(
                                f"数据库连接失败，{current_delay}秒后重试 ({retries}/{max_retries})",
                                function=func.__name__,
                                error=str(e),
                            )
                            time.sleep(current_delay)
                            current_delay *= backoff
                        else:
                            logger.error(
                                "数据库连接重试失败", function=func.__name__, error=str(e), retries=max_retries
                            )
                            raise
                    else:
                        # 如果不是连接错误，直接抛出异常
                        raise

            return func(*args, **kwargs)

        return wrapper

    return decorator


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
        sessions["postgresql"] = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return sessions["postgresql"]()


# Week 3 兼容性别名 - 将MySQL请求重定向到PostgreSQL
def get_mysql_engine():
    """兼容性别名: Week 3简化后，MySQL请求重定向到PostgreSQL"""
    logger.warning("get_mysql_engine() called, redirecting to PostgreSQL (Week 3 simplified)")
    return get_postgresql_engine()


def get_mysql_session() -> Session:
    """兼容性别名: Week 3简化后，MySQL会话重定向到PostgreSQL"""
    logger.warning("get_mysql_session() called, redirecting to PostgreSQL (Week 3 simplified)")
    return get_postgresql_session()


def close_all_connections():
    """关闭所有数据库连接"""
    for name, engine in engines.items():
        engine.dispose()
        logger.info(f"{name} connection closed")


# 复用现有 MyStocks 数据访问逻辑 (可选，如果环境变量不完整则跳过)
try:
    import os
    import sys

    # 添加项目根目录到 Python 路径
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../"))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    from src.data_access import PostgreSQLDataAccess
    from src.monitoring import MonitoringDatabase

    # 初始化监控数据库
    monitoring_db = MonitoringDatabase(enable_monitoring=True)

    # 创建PostgreSQL数据访问实例（PostgreSQLDataAccess 不接受监控数据库参数）
    postgresql_access = PostgreSQLDataAccess()

    logger.info("MyStocks PostgreSQLDataAccess loaded successfully")

except (ImportError, OSError, EnvironmentError) as e:
    # Week 3 简化: 如果MyStocks核心模块不可用，跳过（web backend可独立运行）
    logger.warning(f"MyStocks data access modules not available (expected in Week 3 simplified mode): {e}")
    postgresql_access = None


class DatabaseService:
    """数据库服务类 - Week 3 简化版 (PostgreSQL-only)"""

    def __init__(self):
        """初始化数据库服务（仅PostgreSQL）"""
        self.postgresql_engine = get_postgresql_engine()
        logger.info("DatabaseService initialized (PostgreSQL-only, Week 3 simplified)")

    def get_cache_data(self, cache_key: str):
        """获取缓存数据 - 临时实现返回None以避免错误"""
        # 目前返回None，让查询直接进行
        return None

    def set_cache_data(self, cache_key: str, data, ttl: int = 600):
        """设置缓存数据 - 临时实现"""
        # 临时空实现
        pass

    @db_retry(max_retries=3, delay=1.0)
    def query_stocks_basic(self, limit: int = 100) -> pd.DataFrame:
        """查询股票基本信息"""
        try:
            # 参数验证
            if limit <= 0 or limit > 10000:
                logger.warning(f"Invalid limit parameter: {limit}, using default 100")
                limit = 100

            if postgresql_access:
                # 使用 PostgreSQLDataAccess
                result = postgresql_access.query("symbols_info", limit=limit)
                if result is None or (isinstance(result, pd.DataFrame) and result.empty):
                    logger.warning(f"Empty result from PostgreSQL access, symbol count=0")
                    return pd.DataFrame()
                return result
            else:
                # 直接查询 PostgreSQL
                session = None
                try:
                    session = get_postgresql_session()
                    query = text(
                        """
                        SELECT symbol, name, industry, area, market, list_date
                        FROM symbols_info
                        LIMIT :limit
                    """
                    )
                    result = session.execute(query, {"limit": limit})
                    df = pd.DataFrame(result.fetchall(), columns=result.keys())
                    if df.empty:
                        logger.warning(f"Empty stocks_basic result from database, limit={limit}")
                    else:
                        logger.info(f"Successfully fetched {len(df)} stocks from database")
                    return df
                except Exception as e:
                    logger.error(f"Database query error in query_stocks_basic: {e}", exc_info=True)
                    raise
                finally:
                    if session:
                        session.close()
        except Exception as e:
            logger.error(f"Failed to query stocks basic: {str(e)}", exc_info=True)
            raise

    @db_retry(max_retries=3, delay=1.0)
    def query_daily_kline(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """查询日线数据"""
        try:
            if postgresql_access:
                # 使用正确的列名 trade_date 而不是 date
                where_clause = "symbol = %s AND trade_date >= %s AND trade_date <= %s"
                params = [symbol, start_date, end_date]
                return postgresql_access.query(
                    "daily_kline", where=where_clause, order_by="trade_date ASC", params=params
                )
            else:
                # 直接查询 PostgreSQL
                with get_postgresql_session() as session:
                    query = text(
                        """
                        SELECT trade_date as date, open, high, low, close, volume, amount
                        FROM daily_kline
                        WHERE symbol = :symbol
                        AND trade_date >= :start_date
                        AND trade_date <= :end_date
                        ORDER BY trade_date
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
db_service = DatabaseService()


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
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_postgresql_engine())
