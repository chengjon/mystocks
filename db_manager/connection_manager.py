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

    def __init__(self):
        """初始化连接管理器,验证必需的环境变量"""
        self._validate_env_variables()
        self._connections: Dict[str, Any] = {}

    def _validate_env_variables(self):
        """验证必需的环境变量是否存在 (Week 3简化后 - 仅PostgreSQL)"""
        required_vars = [
            # PostgreSQL
            "POSTGRESQL_HOST",
            "POSTGRESQL_PORT",
            "POSTGRESQL_USER",
            "POSTGRESQL_PASSWORD",
            "POSTGRESQL_DATABASE",
            # Monitoring (使用PostgreSQL)
            "MONITOR_DB_URL",
        ]

        missing_vars = [var for var in required_vars if not os.getenv(var)]

        if missing_vars:
            raise EnvironmentError(
                f"缺少必需的环境变量: {', '.join(missing_vars)}\n"
                f"请参考 .env.example 文件配置环境变量\n"
                f"注意: Week 3简化后仅需PostgreSQL配置 (TDengine/MySQL/Redis已移除)"
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
                    host=os.getenv("POSTGRESQL_HOST"),
                    port=int(os.getenv("POSTGRESQL_PORT")),
                    user=os.getenv("POSTGRESQL_USER"),
                    password=os.getenv("POSTGRESQL_PASSWORD"),
                    database=os.getenv("POSTGRESQL_DATABASE"),
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

    def _return_postgresql_connection(self, conn):
        """
        归还PostgreSQL连接到连接池

        Args:
            conn: PostgreSQL连接对象
        """
        if "postgresql" in self._connections:
            self._connections["postgresql"].putconn(conn)

    def close_all_connections(self):
        """关闭所有数据库连接 (Week 3简化后 - 仅PostgreSQL)"""
        for db_type, conn in self._connections.items():
            try:
                if db_type == "postgresql":
                    conn.closeall()
                else:
                    # 兜底: 尝试通用close方法
                    if hasattr(conn, "close"):
                        conn.close()
            except Exception as e:
                print(f"警告: 关闭{db_type}连接失败: {e}")

        self._connections.clear()

    def test_all_connections(self) -> Dict[str, bool]:
        """
        测试所有数据库连接 (Week 3简化后 - 仅PostgreSQL)

        Returns:
            dict: 每个数据库的连接状态 {'postgresql': True}
        """
        results = {}

        # 测试PostgreSQL
        try:
            pool = self.get_postgresql_connection()
            conn = pool.getconn()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
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
    """测试连接管理器 (Week 3简化后 - 仅PostgreSQL)"""
    print("正在测试数据库连接...")
    print("Week 3架构: PostgreSQL-only (TDengine/MySQL/Redis已移除)\n")

    manager = DatabaseConnectionManager()
    results = manager.test_all_connections()

    print("连接测试结果:")
    for db_type, status in results.items():
        status_str = "✅ 成功" if status else "❌ 失败"
        print(f"  {db_type}: {status_str}")

    success_count = sum(results.values())
    total_count = len(results)

    print(f"\n总计: {success_count}/{total_count} 个数据库连接成功")

    if success_count == total_count:
        print("✅ PostgreSQL-only架构验证通过!")
    else:
        print("❌ 连接测试失败,请检查 .env 配置")

    manager.close_all_connections()
