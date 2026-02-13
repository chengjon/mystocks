"""
数据库连接服务

管理数据库连接池、连接状态和重连机制
"""

import logging
from typing import Dict, Any
from datetime import datetime
from psycopg2 import pool
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class ConnectionService:
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.connection_pool = None
        self.is_connected = False
        self.last_connected_at = None
        self.connection_count = 0

        self.pool_size = 10
        self.max_overflow = 5

        logger.info("ConnectionService initialized")

    def initialize_pool(self, minconn: int = 1, maxconn: int = None) -> bool:
        try:
            self.connection_pool = pool.SimpleConnectionPool(
                minconn=minconn,
                maxconn=maxconn or self.pool_size,
                maxoverflow=self.max_overflow,
                cur_limit=1,
                idle_timeout=300,
                conn_timeout=30,
                dbname="mystocks",
                user="mystocks_user",
                password="mystocks_password",
                host="localhost",
                port="5432",
            )
            self.is_connected = True
            self.last_connected_at = datetime.now()

            logger.info("数据库连接池初始化成功")
            return True
        except Exception as e:
            logger.error("数据库连接池初始化失败: %s", e)
            self.is_connected = False
            return False

    @contextmanager
    def get_connection(self):
        try:
            if not self.connection_pool:
                if not self.initialize_pool():
                    raise RuntimeError("无法获取数据库连接")

            conn = self.connection_pool.getconn()
            self.connection_count += 1

            logger.debug("获取数据库连接 #%d", self.connection_count)
            yield conn

        except Exception as e:
            logger.error("获取数据库连接失败: %s", e)
            raise
        finally:
            if "conn" in locals():
                conn.close()

    def check_connection(self) -> Dict[str, Any]:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()

            self.last_connected_at = datetime.now()

            return {
                "is_connected": True,
                "last_connected_at": self.last_connected_at.isoformat(),
                "connection_count": self.connection_count,
                "pool_size": self.connection_pool.size if self.connection_pool else 0,
            }
        except Exception as e:
            logger.error("检查连接失败: %s", e)
            return {
                "is_connected": False,
                "error": str(e),
                "last_connected_at": self.last_connected_at.isoformat() if self.last_connected_at else None,
            }

    def close_all_connections(self):
        try:
            if self.connection_pool:
                self.connection_pool.closeall()
                self.connection_pool = None
                self.is_connected = False
                self.connection_count = 0

            logger.info("已关闭所有数据库连接")
        except Exception as e:
            logger.error("关闭连接失败: %s", e)

    def get_pool_stats(self) -> Dict[str, Any]:
        if not self.connection_pool:
            return {"is_connected": False, "pool_size": 0}

        return {
            "is_connected": self.is_connected,
            "pool_size": self.connection_pool.size,
            "available": self.connection_pool.size - len(self.connection_pool._pool),
            "used": len(self.connection_pool._pool),
            "connection_count": self.connection_count,
        }
