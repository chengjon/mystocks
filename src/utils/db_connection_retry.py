"""
数据库连接重试工具模块
为数据库连接操作添加重试逻辑，提高连接稳定性
"""

import time
import functools
from typing import Callable, Any
import structlog

logger = structlog.get_logger()


def db_retry(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    数据库连接重试装饰器

    Args:
        max_retries: 最大重试次数
        delay: 初始延迟时间（秒）
        backoff: 延迟倍数
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            retries = 0
            current_delay = delay

            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
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
                        ]
                    ):
                        if retries < max_retries:
                            logger.warning("数据库连接失败，%scurrent_delay秒后重试 (%sretries/%smax_retries")",
                                function=func.__name__,
                                error=str(e),
                            )
                            time.sleep(current_delay)
                            current_delay *= backoff
                        else:
                            logger.error(
                                "数据库连接重试失败",
                                function=func.__name__,
                                error=str(e),
                                retries=max_retries,
                            )
                            raise
                    else:
                        # 如果不是连接错误，直接抛出异常
                        raise

            return func(*args, **kwargs)

        return wrapper

    return decorator


class DatabaseConnectionHandler:
    """数据库连接处理器，提供统一的连接管理"""

    def __init__(self):
        self.connection_manager = None
        self._connection_cache = {}

    def get_connection_manager(self):
        """延迟加载连接管理器，避免在没有环境变量时出错"""
        if self.connection_manager is None:
            from src.storage.database.connection_manager import get_connection_manager

            self.connection_manager = get_connection_manager()
        return self.connection_manager

    @db_retry(max_retries=3, delay=1.0)
    def get_tdengine_connection(self):
        """获取TDengine连接（带重试）"""
        return self.get_connection_manager().get_tdengine_connection()

    @db_retry(max_retries=3, delay=1.0)
    def get_postgresql_connection(self):
        """获取PostgreSQL连接（带重试）"""
        pool = self.get_connection_manager().get_postgresql_connection()
        return pool.getconn()

    def return_postgresql_connection(self, conn):
        """归还PostgreSQL连接"""
        try:
            pool = self.get_connection_manager().get_postgresql_connection()
            pool.putconn(conn)
        except Exception as e:
            logger.error("归还PostgreSQL连接失败", error=str(e))

    def close_all_connections(self):
        """关闭所有连接"""
        if self.connection_manager:
            self.connection_manager.close_all_connections()


# 创建全局连接处理器实例
connection_handler = DatabaseConnectionHandler()


def get_tdengine_connection_with_retry():
    """获取TDengine连接（带重试）"""
    return connection_handler.get_tdengine_connection()


def get_postgresql_connection_with_retry():
    """获取PostgreSQL连接（带重试）"""
    return connection_handler.get_postgresql_connection()


def return_postgresql_connection(conn):
    """归还PostgreSQL连接"""
    return connection_handler.return_postgresql_connection(conn)


if __name__ == "__main__":
    """测试重试逻辑"""
    print("测试数据库连接重试功能...")

    try:
        # 测试TDengine连接
        print("测试TDengine连接...")
        conn = get_tdengine_connection_with_retry()
        print("✅ TDengine连接成功")

        # 测试PostgreSQL连接
        print("测试PostgreSQL连接...")
        pg_conn = get_postgresql_connection_with_retry()
        print("✅ PostgreSQL连接成功")

        # 归还PostgreSQL连接
        return_postgresql_connection(pg_conn)
        print("✅ PostgreSQL连接已归还")

        print("所有测试通过！")
    except Exception as e:
        print(f"测试失败: {e}")
