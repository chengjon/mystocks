"""
连接池配置模块
定义数据库连接池的配置参数
"""

import os


class ConnectionPoolConfig:
    """连接池配置"""

    def __init__(self):
        # 连接池基本配置
        self.pool_min_connections = int(os.getenv("POOL_MIN_CONNECTIONS", "5"))
        self.pool_max_connections = int(os.getenv("POOL_MAX_CONNECTIONS", "20"))
        self.pool_timeout = int(os.getenv("POOL_TIMEOUT", "30"))
        self.pool_recycle = int(os.getenv("POOL_RECYCLE", "3600"))
        self.pool_max_queries = int(os.getenv("POOL_MAX_QUERIES", "50000"))
        self.pool_max_inactive_connection_lifetime = float(
            os.getenv("POOL_MAX_INACTIVE_CONNECTION_LIFETIME", "300")
        )

        # 连接健康检查配置
        self.health_check_interval = int(os.getenv("HEALTH_CHECK_INTERVAL", "60"))
        self.health_check_timeout = int(os.getenv("HEALTH_CHECK_TIMEOUT", "5"))

        # 监控配置
        self.enable_pool_monitoring = (
            os.getenv("ENABLE_POOL_MONITORING", "true").lower() == "true"
        )
        self.monitoring_interval = int(os.getenv("MONITORING_INTERVAL", "60"))

    # 环境变量配置
    @classmethod
    def from_env(cls) -> "ConnectionPoolConfig":
        """从环境变量加载配置"""
        return cls()

    def validate_config(self) -> bool:
        """
        验证配置是否有效

        Returns:
            bool: 配置是否有效
        """
        if self.pool_min_connections < 1:
            raise ValueError("Minimum connections must be at least 1")

        if self.pool_max_connections < self.pool_min_connections:
            raise ValueError(
                "Maximum connections must be greater than or equal to minimum connections"
            )

        if self.pool_timeout < 1:
            raise ValueError("Connection timeout must be at least 1")

        if self.pool_recycle < 0:
            raise ValueError("Connection recycle time must be non-negative")

        if self.health_check_interval < 1:
            raise ValueError("Health check interval must be at least 1")

        if self.health_check_timeout < 1:
            raise ValueError("Health check timeout must be at least 1")

        return True

    def get_pool_config_dict(self) -> dict:
        """
        获取连接池配置字典

        Returns:
            dict: 连接池配置
        """
        return {
            "min_connections": self.pool_min_connections,
            "max_connections": self.pool_max_connections,
            "timeout": self.pool_timeout,
            "recycle": self.pool_recycle,
            "max_queries": self.pool_max_queries,
            "max_inactive_connection_lifetime": self.pool_max_inactive_connection_lifetime,
        }


# 全局配置实例
_pool_config = None


def get_pool_config() -> ConnectionPoolConfig:
    """
    获取全局连接池配置

    Returns:
        ConnectionPoolConfig: 连接池配置
    """
    global _pool_config
    if _pool_config is None:
        _pool_config = ConnectionPoolConfig.from_env()
    return _pool_config


def get_optimal_pool_size() -> tuple:
    """
    根据系统资源获取最优连接池大小

    Returns:
        tuple: (min_connections, max_connections)
    """
    # 默认连接池大小，避免依赖psutil
    # 基础连接数
    base_connections = 5

    # 计算最优连接数
    optimal_min = base_connections
    optimal_max = base_connections * 4

    # 确保连接数在合理范围内
    optimal_max = min(optimal_max, 50)  # 最大50个连接

    return optimal_min, optimal_max


def get_production_pool_config() -> ConnectionPoolConfig:
    """
    获取生产环境连接池配置

    Returns:
        ConnectionPoolConfig: 生产环境配置
    """
    config = ConnectionPoolConfig.from_env()

    # 生产环境优化
    if os.getenv("ENVIRONMENT", "development") == "production":
        # 使用最优连接池大小
        min_conn, max_conn = get_optimal_pool_size()
        config.pool_min_connections = min_conn
        config.pool_max_connections = max_conn

        # 更严格的超时设置
        config.pool_timeout = 10
        config.pool_recycle = 1800  # 30分钟

        # 启用监控
        config.enable_pool_monitoring = True
        config.monitoring_interval = 30

    return config


# 环境特定的配置
def get_development_pool_config() -> ConnectionPoolConfig:
    """获取开发环境配置"""
    config = ConnectionPoolConfig.from_env()

    # 开发环境配置
    config.pool_min_connections = 2
    config.pool_max_connections = 5
    config.pool_timeout = 10
    config.pool_recycle = 7200  # 2小时

    return config


def get_test_pool_config() -> ConnectionPoolConfig:
    """获取测试环境配置"""
    config = ConnectionPoolConfig.from_env()

    # 测试环境配置
    config.pool_min_connections = 1
    config.pool_max_connections = 3
    config.pool_timeout = 5
    config.pool_recycle = 300  # 5分钟

    return config


def get_config_for_environment() -> ConnectionPoolConfig:
    """
    根据当前环境获取配置

    Returns:
        ConnectionPoolConfig: 环境特定的配置
    """
    env = os.getenv("ENVIRONMENT", "development").lower()

    if env == "production":
        return get_production_pool_config()
    elif env == "test":
        return get_test_pool_config()
    else:
        return get_development_pool_config()
