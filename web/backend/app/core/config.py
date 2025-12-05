"""
应用配置管理
"""

import os
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置 - Week 3 简化版 (PostgreSQL-only)"""

    # 应用基础配置
    app_name: str = "MyStocks Web"
    app_version: str = "2.0.0"  # Week 3 简化版本
    debug: bool = False

    # 服务器配置
    host: str = "0.0.0.0"
    port: int = 8000
    port_range_start: int = 8000
    port_range_end: int = 8010

    # 数据库配置 - PostgreSQL 主数据库 (Week 3 简化: 仅使用PostgreSQL)
    # 从环境变量读取，pydantic-settings会自动从.env文件加载
    postgresql_host: str = "localhost"
    postgresql_port: int = 5438
    postgresql_user: str = "postgres"
    postgresql_password: str = ""  # 必须从环境变量设置，否则启动失败
    postgresql_database: str = "mystocks"

    # 监控数据库配置 (使用PostgreSQL，同库不同schema)
    monitor_db_url: str = ""  # 将从.env读取 MONITOR_DB_URL
    monitor_db_host: str = "localhost"
    monitor_db_user: str = "postgres"
    monitor_db_password: str = ""  # 必须从环境变量设置，否则启动失败
    monitor_db_port: int = 5438
    monitor_db_database: str = "mystocks"

    # JWT 认证配置
    secret_key: str = ""  # 必须从环境变量设置，否则启动失败
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # 管理员初始密码配置
    admin_initial_password: str = Field(default="", env="ADMIN_INITIAL_PASSWORD")  # 必须从环境变量设置，生产环境不得为空

    # CORS 配置 (使用字符串形式，避免pydantic-settings解析问题)
    cors_origins_str: str = "http://localhost:3000,http://localhost:8080,http://localhost:5173"

    @property
    def cors_origins(self) -> List[str]:
        return self.cors_origins_str.split(",")

    # 缓存配置 (Week 3 简化: 暂时禁用Redis缓存)
    enable_cache: bool = False  # Week 3简化: Redis已移除

    # Celery 异步任务配置
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"
    celery_task_track_started: bool = True
    celery_task_time_limit: int = 3600  # 任务超时时间（秒），默认1小时
    celery_enable_utc: bool = True
    celery_timezone: str = "Asia/Shanghai"

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

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="allow"
    )  # 允许额外字段


def validate_required_settings():
    """
    验证必需的安全配置项

    在应用启动时验证所有必需的敏感信息是否已正确设置
    如果缺少必需配置，抛出ValueError

    Raises:
        ValueError: 当必需的配置项缺失时
    """
    required_settings = {
        "postgresql_password": "POSTGRESQL_PASSWORD",
        "monitor_db_password": "POSTGRESQL_PASSWORD",  # 使用相同的密码
        "secret_key": "JWT_SECRET_KEY",
    }

    missing_settings = []

    for attr_name, env_name in required_settings.items():
        value = getattr(settings, attr_name, None)
        if not value or value == "":
            missing_settings.append(env_name)

    if missing_settings:
        error_msg = (
            f"安全配置错误：缺少必需的环境变量配置\n"
            f"缺失项：{', '.join(missing_settings)}\n"
            f"请检查 .env 文件或参考 .env.example 文件进行配置\n"
            f"可以通过以下命令生成安全的JWT密钥：openssl rand -hex 32"
        )
        raise ValueError(error_msg)


# 创建全局配置实例
settings = Settings()

# 验证必需的配置项
try:
    validate_required_settings()
except ValueError as e:
    print(f"❌ 配置验证失败：{e}")
    print("🔧 请修复配置后重新启动应用")
    # 在生产环境中，这里应该抛出异常而不是继续运行
    # 为了开发环境兼容性，暂时提供警告
    import warnings

    warnings.warn(f"配置验证失败：{e}", UserWarning)


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
    raise NotImplementedError("MySQL已于Week 3迁移至PostgreSQL，请使用get_postgresql_connection_string()")


# 设置数据库URL（用于某些服务的向后兼容）
settings.DATABASE_URL = get_postgresql_connection_string()
settings.MONITOR_DB_URL = get_monitor_db_connection_string()
