"""
数据库配置模块
提供数据库连接配置和环境变量管理
"""

import os


def _get_env_value(*names: str, default=None):
    """按优先级读取环境变量，兼容新旧命名。"""
    for name in names:
        if name in os.environ:
            return os.environ[name]
    return default


class DatabaseConfig:
    """数据库配置"""

    def __init__(self):
        # PostgreSQL配置
        self.postgresql_host = _get_env_value("POSTGRESQL_HOST", "DB_POSTGRESQL_HOST", default="localhost")
        self.postgresql_port = int(_get_env_value("POSTGRESQL_PORT", "DB_POSTGRESQL_PORT", default="5432"))
        self.postgresql_username = _get_env_value("POSTGRESQL_USER", "DB_POSTGRESQL_USERNAME", default="postgres")
        self.postgresql_password = _get_env_value("POSTGRESQL_PASSWORD", "DB_POSTGRESQL_PASSWORD")
        if not self.postgresql_password:
            raise ValueError("POSTGRESQL_PASSWORD or DB_POSTGRESQL_PASSWORD environment variable must be set")
        self.postgresql_database = _get_env_value("POSTGRESQL_DATABASE", "DB_POSTGRESQL_DATABASE", default="mystocks")

        # TDengine配置
        self.tdengine_host = _get_env_value("TDENGINE_HOST", "DB_TDENGINE_HOST", default="localhost")
        self.tdengine_port = int(_get_env_value("TDENGINE_PORT", "DB_TDENGINE_PORT", default="6030"))
        self.tdengine_username = _get_env_value("TDENGINE_USER", "DB_TDENGINE_USERNAME", default="root")
        self.tdengine_password = _get_env_value("TDENGINE_PASSWORD", "DB_TDENGINE_PASSWORD")
        if not self.tdengine_password:
            raise ValueError("TDENGINE_PASSWORD or DB_TDENGINE_PASSWORD environment variable must be set")
        self.tdengine_database = _get_env_value("TDENGINE_DATABASE", "DB_TDENGINE_DATABASE", default="mystocks")

    def get_postgresql_url(self) -> str:
        """获取PostgreSQL连接字符串"""
        return (
            f"postgresql://"
            f"{self.postgresql_username}:"
            f"{self.postgresql_password}@"
            f"{self.postgresql_host}:"
            f"{self.postgresql_port}/"
            f"{self.postgresql_database}"
        )

    def get_tdengine_url(self) -> str:
        """获取TDengine连接字符串"""
        return f"taosws://{self.tdengine_username}:{self.tdengine_password}@{self.tdengine_host}:{self.tdengine_port}/"

    def validate_config(self) -> bool:
        """验证配置是否有效"""
        # 验证必填字段
        if not all(
            [
                self.postgresql_host,
                self.postgresql_username,
                self.postgresql_password,
                self.postgresql_database,
            ]
        ):
            raise ValueError("PostgreSQL配置不完整")

        if not all(
            [
                self.tdengine_host,
                self.tdengine_username,
                self.tdengine_password,
                self.tdengine_database,
            ]
        ):
            raise ValueError("TDengine配置不完整")

        # 验证端口范围
        if not (1 <= self.postgresql_port <= 65535):
            raise ValueError("PostgreSQL端口必须在1-65535之间")

        if not (1 <= self.tdengine_port <= 65535):
            raise ValueError("TDengine端口必须在1-65535之间")

        return True


# 全局配置实例
_db_config = None


def get_database_config() -> DatabaseConfig:
    """获取全局数据库配置"""
    global _db_config
    if _db_config is None:
        _db_config = DatabaseConfig()
    return _db_config
