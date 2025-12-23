"""
详细调试配置加载问题
"""

import os
from pydantic_settings import BaseSettings
from typing import List


# 逐个测试字段
def test_field(field_name, field_type, default_value, env_value=None):
    """测试单个字段"""
    if env_value is not None:
        os.environ[field_name.upper()] = env_value

    class TestSettings(BaseSettings):
        if field_type == "str":
            test_field: str = default_value
        elif field_type == "int":
            test_field: int = default_value
        elif field_type == "bool":
            test_field: bool = default_value
        elif field_type == "list_str":
            test_field: List[str] = default_value

        class Config:
            env_file = ".env"
            case_sensitive = False
            extra = "allow"

    try:
        settings = TestSettings()
        print(f"✓ {field_name}: {getattr(settings, 'test_field')}")
        return True
    except Exception as e:
        print(f"✗ {field_name}: {e}")
        return False


if __name__ == "__main__":
    print("逐步测试配置字段...")

    # 测试基本字段
    test_field("app_name", "str", "MyStocks Web", "MyStocks Web")
    test_field("debug", "bool", False, "true")
    test_field("host", "str", "0.0.0.0", "0.0.0.0")
    test_field("port", "int", 8000, "8000")
    test_field(
        "secret_key", "str", "your-secret-key-change-in-production", "dev-secret-key"
    )
    test_field("algorithm", "str", "HS256", "HS256")
    test_field("access_token_expire_minutes", "int", 30, "1440")

    # 测试数据库字段
    test_field("postgresql_host", "str", "192.168.123.104", "192.168.123.104")
    test_field("postgresql_port", "int", 5438, "5438")
    test_field("postgresql_user", "str", "postgres", "postgres")
    test_field("postgresql_password", "str", "c790414J", "c790414J")
    test_field("postgresql_database", "str", "mystocks", "mystocks")

    # 测试监控数据库字段
    test_field("monitor_db_host", "str", "192.168.123.104", "192.168.123.104")
    test_field("monitor_db_user", "str", "postgres", "postgres")
    test_field("monitor_db_password", "str", "c790414J", "c790414J")
    test_field("monitor_db_port", "int", 5438, "5438")
    test_field("monitor_db_database", "str", "mystocks", "mystocks")

    # 测试CORS字段（可能的问题源）
    print("\n测试CORS配置...")
    # 清除环境变量
    if "CORS_ORIGINS" in os.environ:
        del os.environ["CORS_ORIGINS"]

    # 测试不设置环境变量的情况
    class TestCORSSettings1(BaseSettings):
        cors_origins: List[str] = [
            "http://localhost:3000",
            "http://localhost:8080",
            "http://localhost:5173",
        ]

        class Config:
            env_file = ".env"
            case_sensitive = False
            extra = "allow"

    try:
        settings = TestCORSSettings1()
        print(f"✓ CORS Origins (默认值): {settings.cors_origins}")
    except Exception as e:
        print(f"✗ CORS Origins (默认值): {e}")

    # 测试设置环境变量为逗号分隔的字符串
    os.environ["CORS_ORIGINS"] = "http://localhost:5173,http://localhost:3000"

    class TestCORSSettings2(BaseSettings):
        cors_origins: List[str] = [
            "http://localhost:3000",
            "http://localhost:8080",
            "http://localhost:5173",
        ]

        class Config:
            env_file = ".env"
            case_sensitive = False
            extra = "allow"

    try:
        settings = TestCORSSettings2()
        print(f"✓ CORS Origins (逗号分隔): {settings.cors_origins}")
    except Exception as e:
        print(f"✗ CORS Origins (逗号分隔): {e}")

    # 测试设置环境变量为JSON格式
    os.environ["CORS_ORIGINS"] = '["http://localhost:5173", "http://localhost:3000"]'

    class TestCORSSettings3(BaseSettings):
        cors_origins: List[str] = [
            "http://localhost:3000",
            "http://localhost:8080",
            "http://localhost:5173",
        ]

        class Config:
            env_file = ".env"
            case_sensitive = False
            extra = "allow"

    try:
        settings = TestCORSSettings3()
        print(f"✓ CORS Origins (JSON格式): {settings.cors_origins}")
    except Exception as e:
        print(f"✗ CORS Origins (JSON格式): {e}")
