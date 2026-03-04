"""
应用配置管理
"""

from typing import List

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# 环境变量文件配置
# 仅使用项目根目录的.env文件，便于管理和版本控制
_ENV_FILE_PATH = ".env"


class Settings(BaseSettings):
    """应用配置 - Week 3 简化版 (PostgreSQL-only)"""

    # 应用基础配置
    app_name: str = "MyStocks Web"
    app_version: str = "2.1.0"  # Week 4: 三数据库架构 (PostgreSQL + TDengine + Redis)
    debug: bool = False

    # 测试环境配置
    testing: bool = Field(default=False, env="TESTING")
    csrf_enabled: bool = Field(default=True)  # 默认启用CSRF，测试环境自动禁用

    # Mock API配置
    use_mock_apis: bool = Field(default=False, env="USE_MOCK_DATA")  # 控制是否注册Mock API路由
    mock_auth_enabled: bool = Field(default=False, env="MOCK_AUTH_ENABLED")  # 生产环境安全控制：禁用Mock认证

    # 服务器配置
    host: str = Field(default="0.0.0.0", env="BACKEND_HOST")  # nosec
    # Pydantic v2 no longer recommends Field(env=...), so use validation_alias for robust port mapping.
    port: int = Field(default=0, validation_alias=AliasChoices("BACKEND_PORT", "PORT", "port"))
    port_range_start: int = Field(default=0, validation_alias=AliasChoices("BACKEND_PORT", "PORT", "port"))
    port_range_end: int = Field(
        default=0,
        validation_alias=AliasChoices("BACKEND_BACKUP_PORT", "PORT_RANGE_END", "port_range_end"),
    )

    # 数据库配置 - PostgreSQL 主数据库 (Week 3 简化: 仅使用PostgreSQL)
    # 从环境变量读取，pydantic-settings会自动从.env文件加载
    postgresql_host: str = Field(default="", env="POSTGRESQL_HOST")
    postgresql_port: int = Field(default=5432, env="POSTGRESQL_PORT")
    postgresql_user: str = Field(default="", env="POSTGRESQL_USER")
    postgresql_password: str = Field(default="", env="POSTGRESQL_PASSWORD")
    postgresql_database: str = Field(default="", env="POSTGRESQL_DATABASE")

    # 监控数据库配置 (使用PostgreSQL，同库不同schema)
    monitor_db_url: str = Field(default="", env="MONITOR_DB_URL")
    monitor_db_host: str = Field(default="", env="POSTGRESQL_HOST")  # 默认与主库相同
    monitor_db_user: str = Field(default="", env="POSTGRESQL_USER")  # 默认与主库相同
    monitor_db_password: str = Field(default="", env="POSTGRESQL_PASSWORD")  # 默认与主库相同
    monitor_db_port: int = Field(default=5432, env="POSTGRESQL_PORT")  # 默认与主库相同
    monitor_db_database: str = Field(default="", env="POSTGRESQL_DATABASE")  # 默认与主库相同

    # JWT 认证配置
    # 注意: 字段名使用 jwt_secret_key 以便在 case_sensitive=False 时正确映射到 JWT_SECRET_KEY 环境变量
    jwt_secret_key: str = Field(default="", env="JWT_SECRET_KEY")  # 必须从环境变量设置，否则启动失败
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # 向后兼容: secret_key 属性指向 jwt_secret_key
    @property
    def secret_key(self) -> str:
        """向后兼容的 secret_key 属性"""
        return self.jwt_secret_key

    # 管理员初始密码配置
    admin_initial_password: str = Field(default="", env="ADMIN_INITIAL_PASSWORD")

    # CORS 配置 (使用字符串形式，避免pydantic-settings解析问题)
    # 默认仅允许固定前端端口，实际环境以 .env 的 CORS_ORIGINS 为准
    cors_origins_str: str = Field(
        default="http://localhost:3020,http://localhost:3021",
        env="CORS_ORIGINS",
    )

    @property
    def cors_origins(self) -> List[str]:
        """将CORS字符串转换为列表，仅保留非空域名"""
        return [origin.strip() for origin in self.cors_origins_str.split(",") if origin.strip()]

    # ===================================
    # Redis Configuration (三数据库架构)
    # ===================================
    # Redis功能:
    # 1. L2分布式缓存 - 指标计算结果、API响应缓存
    # 2. 消息总线 (Pub/Sub) - 实时事件通知
    # 3. 分布式锁 - 防止重复计算
    # 4. 会话存储 - JWT黑名单、用户会话

    # Redis连接配置
    redis_host: str = Field(default="", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    redis_password: str = Field(default="", env="REDIS_PASSWORD")
    redis_db: int = Field(default=1, env="REDIS_DB")

    # Redis连接池配置
    redis_max_connections: int = 50
    redis_socket_timeout: int = 5
    redis_socket_connect_timeout: int = 5
    redis_decode_responses: bool = True

    # 缓存配置
    redis_cache_ttl: int = 3600  # 默认缓存过期时间 (秒)
    redis_cache_prefix: str = "mystocks:"
    enable_cache: bool = True  # 启用Redis缓存 (Week 4: 三数据库架构)

    # 消息总线配置
    redis_pubsub_channel_prefix: str = "mystocks:"
    enable_pubsub: bool = True  # 启用消息总线

    # 分布式锁配置
    redis_lock_prefix: str = "mystocks:lock:"
    redis_lock_default_timeout: int = 30  # 默认锁超时 (秒)
    enable_lock: bool = True  # 启用分布式锁

    # 会话配置
    redis_session_prefix: str = "mystocks:session:"
    redis_session_ttl: int = 86400  # 会话过期时间 (24小时)

    # Celery 异步任务配置
    celery_broker_url: str = Field(default="redis://localhost:6379/0", env="CELERY_BROKER_URL")
    celery_result_backend: str = Field(default="redis://localhost:6379/1", env="CELERY_RESULT_BACKEND")
    celery_task_track_started: bool = True
    celery_task_time_limit: int = 3600  # 任务超时时间（秒），默认1小时
    celery_enable_utc: bool = True
    celery_timezone: str = "Asia/Shanghai"

    # 文件上传配置
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    upload_dir: str = "uploads"

    # 日志配置 - 从环境变量读取，默认INFO，生产环境可设置为WARNING/ERROR
    log_level: str = Field(default="INFO", env="LOG_LEVEL")

    # 指标计算配置
    enable_talib: bool = True
    max_indicator_period: int = 200

    # 问财API配置
    wencai_timeout: int = 30
    wencai_retry_count: int = 3
    wencai_default_pages: int = 1
    wencai_auto_refresh: bool = True

    model_config = SettingsConfigDict(
        env_file=_ENV_FILE_PATH, env_file_encoding="utf-8", case_sensitive=False, extra="allow"
    )  # 允许额外字段，使用动态查找的.env文件路径


def validate_required_settings(settings_obj: Settings):
    """
    验证必需的安全配置项

    在应用启动时验证所有必需的敏感信息是否已正确设置
    如果缺少必需配置，抛出ValueError

    Args:
        settings_obj: 配置对象实例

    Raises:
        ValueError: 当必需的配置项缺失时
    """
    required_fields = [
        ("postgresql_host", "POSTGRESQL_HOST"),
        ("postgresql_user", "POSTGRESQL_USER"),
        ("postgresql_password", "POSTGRESQL_PASSWORD"),
        ("jwt_secret_key", "JWT_SECRET_KEY"),
        ("port", "BACKEND_PORT"),
        ("port_range_end", "BACKEND_BACKUP_PORT"),
    ]

    missing_settings = []

    for attr_name, env_name in required_fields:
        value = getattr(settings_obj, attr_name, None)
        if not value or value == "":
            missing_settings.append(env_name)

    if missing_settings:
        error_msg = (
            f"启动失败：缺少必需的环境变量配置\n"
            f"缺失项：{', '.join(missing_settings)}\n"
            f"请检查项目根目录的 .env 文件，或复制 .env.example 并填写正确的值\n"
            f"生成安全的JWT密钥：openssl rand -hex 32"
        )
        raise ValueError(error_msg)


# 创建全局配置实例
settings = Settings()

# 验证必需的配置项
try:
    validate_required_settings(settings)
except ValueError as e:
    print(f"❌ 启动失败：{e}")
    print("🔧 请修复配置后重新启动应用")
    import sys

    sys.exit(1)  # 生产环境：配置错误时立即终止启动


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
