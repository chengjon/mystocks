"""
创建最小化配置测试
"""
import os

# 创建一个最小化的配置类，不包含任何列表字段
from pydantic_settings import BaseSettings
from typing import Optional, List


class MinimalSettings(BaseSettings):
    """最小化配置类，排除可能有问题的列表字段"""
    
    # 应用基础配置
    app_name: str = "MyStocks Web"
    app_version: str = "2.0.0"
    debug: bool = False

    # 服务器配置
    host: str = "0.0.0.0"
    port: int = 8000

    # 数据库配置
    postgresql_host: str = "192.168.123.104"
    postgresql_port: int = 5438
    postgresql_user: str = "postgres"
    postgresql_password: str = "c790414J"
    postgresql_database: str = "mystocks"

    # 监控数据库配置
    monitor_db_url: str = ""
    monitor_db_host: str = "192.168.123.104"
    monitor_db_user: str = "postgres"
    monitor_db_password: str = "c790414J"
    monitor_db_port: int = 5438
    monitor_db_database: str = "mystocks"

    # JWT 认证配置
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # 临时移除CORS配置以测试是否是它引起的问题
    # cors_origins: List[str] = [
    #     "http://localhost:3000",
    #     "http://localhost:8080",
    #     "http://localhost:5173",
    # ]

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"


if __name__ == "__main__":
    print("尝试创建最小化配置实例...")
    try:
        settings = MinimalSettings()
        print("最小化配置实例创建成功!")
        print(f"App Name: {settings.app_name}")
        print(f"Debug: {settings.debug}")
        print(f"PostgreSQL Host: {settings.postgresql_host}")
    except Exception as e:
        print(f"创建最小化配置实例失败: {e}")
        import traceback
        traceback.print_exc()