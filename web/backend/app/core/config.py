"""
应用配置管理
"""

from pydantic_settings import BaseSettings
from typing import Optional, List
import os


class Settings(BaseSettings):
    """应用配置 - Week 3 简化版 (PostgreSQL-only)"""

    # 应用基础配置
    app_name: str = "MyStocks Web"
    app_version: str = "2.0.0"  # Week 3 简化版本
    debug: bool = False

    # 服务器配置
    host: str = "0.0.0.0"
    port: int = 8000

    # 数据库配置 - PostgreSQL 主数据库 (Week 3 简化: 仅使用PostgreSQL)
    # 从环境变量读取，pydantic-settings会自动从.env文件加载
    postgresql_host: str = "192.168.123.104"
    postgresql_port: int = 5438
    postgresql_user: str = "postgres"
    postgresql_password: str = "c790414J"  # 将从.env覆盖
    postgresql_database: str = "mystocks"

    # 监控数据库配置 (使用PostgreSQL，同库不同schema)
    monitor_db_url: str = ""  # 将从.env读取 MONITOR_DB_URL
    monitor_db_host: str = "192.168.123.104"
    monitor_db_user: str = "postgres"
    monitor_db_password: str = "c790414J"
    monitor_db_port: int = 5438
    monitor_db_database: str = "mystocks"

    # JWT 认证配置
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # CORS 配置
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:5173",
    ]

    # 缓存配置 (Week 3 简化: 暂时禁用Redis缓存)
    enable_cache: bool = False  # Week 3简化: Redis已移除

    # 文件上传配置
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    upload_dir: str = "uploads"

    # 日志配置
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # 指标计算配置
    enable_talib: bool = True
    max_indicator_period: int = 200

    # 问财API配置
    wencai_timeout: int = 30
    wencai_retry_count: int = 3
    wencai_default_pages: int = 1
    wencai_auto_refresh: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"  # 允许额外字段


# 创建全局配置实例
settings = Settings()


# 数据库连接字符串 - Week 3 简化版 (仅PostgreSQL)
def get_postgresql_connection_string() -> str:
    """获取PostgreSQL主数据库连接字符串"""
    return f"postgresql://{settings.postgresql_user}:{settings.postgresql_password}@{settings.postgresql_host}:{settings.postgresql_port}/{settings.postgresql_database}"


def get_monitor_db_connection_string() -> str:
    """获取监控数据库连接字符串（PostgreSQL同库）"""
    if settings.monitor_db_url:
        return settings.monitor_db_url
    return get_postgresql_connection_string()  # 使用主数据库


# 为兼容性保留（部分服务可能引用）
def get_mysql_connection_string() -> str:
    """已废弃: Week 3简化后不再使用MySQL"""
    raise NotImplementedError(
        "MySQL已于Week 3迁移至PostgreSQL，请使用get_postgresql_connection_string()"
    )


# 设置数据库URL（用于某些服务的向后兼容）
settings.DATABASE_URL = get_postgresql_connection_string()
settings.MONITOR_DB_URL = get_monitor_db_connection_string()
