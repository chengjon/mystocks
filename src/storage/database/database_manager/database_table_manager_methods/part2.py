"""
# 功能：数据库管理器，负责连接管理、表创建和结构验证
# 作者：JohnC (ninjas@sina.com) & Claude
# 创建日期：2025-10-16
# 版本：2.1.0
# 依赖：详见requirements.txt或文件导入部分
# 注意事项：
#   本文件是MyStocks v2.1核心组件，遵循5-tier数据分类架构
# 版权：MyStocks Project © 2025
"""

import logging

import redis
from dotenv import load_dotenv

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DatabaseTableManager")


def _safe_load_dotenv() -> None:
    """导入期仅做非阻塞环境加载，避免因本地 .env 权限导致模块不可导入。"""
    try:
        load_dotenv()
    except OSError as error:
        logger.warning("skip load_dotenv during import: %s", error)


_safe_load_dotenv()


class DatabaseTableManagerCloseAllConnectionsMixin:
    """DatabaseTableManager 方法集 Part 2"""

    def close_all_connections(self) -> None:
        """关闭所有数据库连接"""
        for conn_key, conn in self.db_connections.items():
            try:
                if hasattr(conn, "close"):
                    conn.close()
                elif isinstance(conn, redis.Redis):
                    conn.close()
            except Exception as e:
                logger.warning("Error closing connection %s: %s", conn_key, str(e))
        self.db_connections = {}

        # 关闭监控会话
        if hasattr(self, "monitor_session"):
            self.monitor_session.close()

    def close(self) -> None:
        """关闭连接的别名，用于兼容性"""
        self.close_all_connections()

    def get_tdengine_connection(self, db_name: str = "market_data", **kwargs):
        """获取TDengine连接（兼容测试）"""
        return self.get_connection(DatabaseType.TDENGINE, db_name, **kwargs)

    def get_postgresql_connection(self, db_name: str = "postgres", **kwargs):
        """获取PostgreSQL连接（兼容测试）"""
        return self.get_connection(DatabaseType.POSTGRESQL, db_name, **kwargs)

    def get_tdx_connection(self, db_name: str = "market_data", **kwargs):
        """获取TDengine连接（兼容测试）"""
        return self.get_connection(DatabaseType.TDENGINE, db_name, **kwargs)

    def __enter__(self):
        """Context manager entry - 返回自身实例"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - 确保关闭所有连接"""
        self.close_all_connections()
        return False  # 不抑制异常
