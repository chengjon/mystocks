"""
数据库连接管理器

管理4种数据库(TDengine/PostgreSQL/MySQL/Redis)的连接池和连接生命周期。
所有连接参数从环境变量读取,确保安全性。

创建日期: 2025-10-11
版本: 1.0.0
"""

import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class DatabaseConnectionManager:
    """
    数据库连接管理器基础类

    管理4种数据库的连接池,提供统一的连接获取接口
    """

    def __init__(self) -> None:
        """初始化连接管理器,验证必需的环境变量"""
        self._validate_env_variables()
        self._connections: Dict[str, Any] = {}

    def _validate_env_variables(self) -> None:
        """验证必需的环境变量是否存在 (US3: 移除MySQL和Redis依赖)"""
        required_vars = [
            # TDengine
            "TDENGINE_HOST",
            "TDENGINE_PORT",
            "TDENGINE_USER",
            "TDENGINE_PASSWORD",
            "TDENGINE_DATABASE",
            # PostgreSQL
            "POSTGRESQL_HOST",
            "POSTGRESQL_PORT",
            "POSTGRESQL_USER",
            "POSTGRESQL_PASSWORD",
            "POSTGRESQL_DATABASE",
        ]

        missing_vars = [var for var in required_vars if not os.getenv(var)]

        if missing_vars:
            raise EnvironmentError(
                f"缺少必需的环境变量: {', '.join(missing_vars)}\n"
                f"请参考 .env.example 文件配置环境变量\n"
                f"注意: MySQL和Redis已从US3架构中移除，不再需要这些环境变量"
            )
            raise ValueError(
                "Redis配置错误: REDIS_DB=0 已被PAPERLESS占用!\n"
                "请使用1-15号数据库 (建议REDIS_DB=1)"
            )

    def get_tdengine_connection(self):
        """
        获取TDengine WebSocket连接

        Returns:
            TDengine连接对象

        Raises:
            ConnectionError: 连接失败
        """
        try:
            import taosws

            if "tdengine" not in self._connections:
                # WebSocket连接优先使用REST端口(6041),否则使用默认端口(6030)
                tdengine_port = int(
                    os.getenv("TDENGINE_REST_PORT") or os.getenv("TDENGINE_PORT") or "6030"
                )

                conn = taosws.connect(
                    host=os.getenv("TDENGINE_HOST"),
                    port=tdengine_port,
                    user=os.getenv("TDENGINE_USER"),
                    password=os.getenv("TDENGINE_PASSWORD"),
                    database=os.getenv("TDENGINE_DATABASE"),
                )
                self._connections["tdengine"] = conn

            return self._connections["tdengine"]

        except ImportError:
            raise ImportError("TDengine驱动未安装: pip install taospy>=2.7.0")
        except Exception as e:
            port_str = os.getenv("TDENGINE_REST_PORT") or os.getenv("TDENGINE_PORT") or "6030"
            raise ConnectionError(
                f"TDengine连接失败: {e}\n"
                f"请检查配置: {os.getenv('TDENGINE_HOST')}:{port_str}"
            )

    def get_postgresql_connection(self):
        """
        获取PostgreSQL连接池

        Returns:
            PostgreSQL连接对象

        Raises:
            ConnectionError: 连接失败
        """
        try:
            import psycopg2
            from psycopg2 import pool

            if "postgresql" not in self._connections:
                connection_pool = pool.SimpleConnectionPool(
                    minconn=1,
                    maxconn=20,
                    host=os.getenv("POSTGRESQL_HOST", "192.168.123.104"),
                    port=int(os.getenv("POSTGRESQL_PORT", "5438")),
                    user=os.getenv("POSTGRESQL_USER", "postgres"),
                    password=os.getenv("POSTGRESQL_PASSWORD", ""),
                    database=os.getenv("POSTGRESQL_DATABASE", "mystocks"),
                )
                self._connections["postgresql"] = connection_pool

            return self._connections["postgresql"]

        except ImportError:
            raise ImportError(
                "PostgreSQL驱动未安装: pip install psycopg2-binary>=2.9.5"
            )
        except Exception as e:
            raise ConnectionError(
                f"PostgreSQL连接失败: {e}\n"
                f"请检查配置: {os.getenv('POSTGRESQL_HOST')}:{os.getenv('POSTGRESQL_PORT')}"
            )

    def _return_postgresql_connection(self, conn) -> None:
        """
        归还PostgreSQL连接到连接池

        Args:
            conn: PostgreSQL连接对象
        """
        if "postgresql" in self._connections:
            self._connections["postgresql"].putconn(conn)

    def get_mysql_connection(self):
        """
        获取MySQL连接池

        Returns:
            MySQL连接池对象

        Raises:
            ConnectionError: 连接失败
        """
        try:
            import pymysql
            from pymysql import cursors

            if "mysql" not in self._connections:
                conn = pymysql.connect(
                    host=os.getenv("MYSQL_HOST", "192.168.123.104"),
                    port=int(os.getenv("MYSQL_PORT", "3306")),
                    user=os.getenv("MYSQL_USER", "root"),
                    password=os.getenv("MYSQL_PASSWORD", ""),
                    database=os.getenv("MYSQL_DATABASE", "mystocks"),
                    charset="utf8mb4",
                    cursorclass=cursors.DictCursor,
                )
                self._connections["mysql"] = conn

            return self._connections["mysql"]

        except ImportError:
            raise ImportError("MySQL驱动未安装: pip install pymysql>=1.0.2")
        except Exception as e:
            raise ConnectionError(
                f"MySQL连接失败: {e}\n"
                f"请检查配置: {os.getenv('MYSQL_HOST')}:{os.getenv('MYSQL_PORT')}"
            )

    def get_redis_connection(self):
        """
        获取Redis连接池

        使用1号数据库(避开0号,已被PAPERLESS占用)

        Returns:
            Redis连接对象

        Raises:
            ConnectionError: 连接失败
        """
        try:
            import redis

            if "redis" not in self._connections:
                redis_db = int(os.getenv("REDIS_DB", "1"))

                conn = redis.Redis(
                    host=os.getenv("REDIS_HOST", "192.168.123.104"),
                    port=int(os.getenv("REDIS_PORT", "6379")),
                    db=redis_db,
                    password=os.getenv("REDIS_PASSWORD") or None,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                )

                # 测试连接
                conn.ping()

                self._connections["redis"] = conn

            return self._connections["redis"]

        except ImportError:
            raise ImportError("Redis驱动未安装: pip install redis>=4.5.0")
        except Exception as e:
            raise ConnectionError(
                f"Redis连接失败: {e}\n"
                f"请检查配置: {os.getenv('REDIS_HOST')}:{os.getenv('REDIS_PORT')} DB={os.getenv('REDIS_DB')}"
            )

    def close_all_connections(self) -> None:
        """关闭所有数据库连接"""
        for db_type, conn in self._connections.items():
            try:
                if db_type == "tdengine":
                    conn.close()
                elif db_type == "postgresql":
                    conn.closeall()
                elif db_type == "mysql":
                    conn.close()
                elif db_type == "redis":
                    conn.close()
            except Exception as e:
                print(f"警告: 关闭{db_type}连接失败: {e}")

        self._connections.clear()

    def test_all_connections(self) -> Dict[str, bool]:
        """
        测试所有数据库连接 (US3架构: 只测试TDengine和PostgreSQL)

        Returns:
            dict: 每个数据库的连接状态 {'tdengine': True, 'postgresql': True}
        """
        results = {}

        # 测试TDengine
        try:
            conn = self.get_tdengine_connection()
            results["tdengine"] = True
        except Exception as e:
            results["tdengine"] = False
            print(f"TDengine连接失败: {e}")

        # 测试PostgreSQL
        try:
            pool = self.get_postgresql_connection()
            conn = pool.getconn()
            conn.close()
            pool.putconn(conn)
            results["postgresql"] = True
        except Exception as e:
            results["postgresql"] = False
            print(f"PostgreSQL连接失败: {e}")

        return results


# 全局连接管理器实例
_connection_manager: Optional[DatabaseConnectionManager] = None


def get_connection_manager() -> DatabaseConnectionManager:
    """获取全局连接管理器实例 (单例模式)"""
    global _connection_manager
    if _connection_manager is None:
        _connection_manager = DatabaseConnectionManager()
    return _connection_manager


if __name__ == "__main__":
    """测试连接管理器"""
    print("正在测试数据库连接...")

    manager = DatabaseConnectionManager()
    results = manager.test_all_connections()

    print("\n连接测试结果:")
    for db_type, status in results.items():
        status_str = "✅ 成功" if status else "❌ 失败"
        print(f"  {db_type}: {status_str}")

    success_count = sum(results.values())
    total_count = len(results)

    print(f"\n总计: {success_count}/{total_count} 个数据库连接成功")

    manager.close_all_connections()
