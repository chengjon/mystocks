"""
安全的数据库管理工具函数
避免在代码中硬编码敏感信息，统一从环境变量读取
"""

import os
from typing import Dict, Optional

import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv


def create_databases_safely() -> bool:
    """
    安全地创建所需的数据库
    所有连接参数从环境变量中读取
    """
    # 加载环境变量
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    load_dotenv(env_path)

    print("正在创建所需的数据库...")

    try:
        # 从环境变量获取PostgreSQL连接参数
        pg_host = os.getenv("POSTGRESQL_HOST")
        pg_user = os.getenv("POSTGRESQL_USER")
        pg_password = os.getenv("POSTGRESQL_PASSWORD")
        pg_port = int(os.getenv("POSTGRESQL_PORT", "5432"))

        # 验证必要的参数是否存在
        if not all([pg_host, pg_user, pg_password]):
            missing_params = []
            if not pg_host:
                missing_params.append("POSTGRESQL_HOST")
            if not pg_user:
                missing_params.append("POSTGRESQL_USER")
            if not pg_password:
                missing_params.append("POSTGRESQL_PASSWORD")

            raise ValueError(f"PostgreSQL连接参数不完整，缺少: {', '.join(missing_params)}")

        print(f"连接到PostgreSQL服务器: {pg_user}@{pg_host}:{pg_port}")

        # 连接到默认数据库以创建其他数据库
        conn = psycopg2.connect(
            host=pg_host,
            user=pg_user,
            password=pg_password,
            port=pg_port,
            dbname=os.getenv("POSTGRESQL_ADMIN_DB", "postgres"),
            connect_timeout=10,
        )
        conn.autocommit = True
        cursor = conn.cursor()

        # 创建所需的数据库
        databases_to_create = [
            "test_db",
            "market_data",  # 可能用于TDengine
            "quant_research",  # 可能用于PostgreSQL
        ]

        for db_name in databases_to_create:
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
            exists = cursor.fetchone() is not None
            if not exists:
                cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))
            print(f"  ✓ 数据库 {db_name} 已确保存在")

        cursor.close()
        conn.close()

        print("✓ 数据库创建成功")
        return True

    except Exception as e:
        print(f"✗ 创建数据库时出现错误: {e}")
        return False


def get_database_config(db_type) -> Optional[Dict]:
    """
    安全地获取数据库配置
    :param db_type: 数据库类型 ('postgresql', 'tdengine', 'redis')
    :return: 数据库配置字典或None
    """
    # 加载环境变量
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    load_dotenv(env_path)

    postgresql_config = {
        "host": os.getenv("POSTGRESQL_HOST"),
        "user": os.getenv("POSTGRESQL_USER"),
        "password": os.getenv("POSTGRESQL_PASSWORD"),
        "port": int(os.getenv("POSTGRESQL_PORT", "5432")),
    }

    config_map = {
        "postgresql": postgresql_config,
        "tdengine": {
            "host": os.getenv("TDENGINE_HOST"),
            "user": os.getenv("TDENGINE_USER", "root"),
            "password": os.getenv("TDENGINE_PASSWORD", "taosdata"),
            "port": int(os.getenv("TDENGINE_PORT", "6041")),
        },
        "redis": {
            "host": os.getenv("REDIS_HOST"),
            "port": int(os.getenv("REDIS_PORT", "6379")),
            "password": os.getenv("REDIS_PASSWORD"),
            "db": int(os.getenv("REDIS_DB", "0")),
        },
    }

    if db_type.lower() not in config_map:
        raise ValueError(f"不支持的数据库类型: {db_type}")

    config = config_map[db_type.lower()]

    # 验证必要的配置项
    required_keys = ["host"]
    if db_type.lower() != "redis":
        required_keys.extend(["user", "password"])

    missing_keys = [key for key in required_keys if not config.get(key)]
    if missing_keys:
        print(f"警告: {db_type} 配置不完整，缺少: {', '.join(missing_keys)}")
        return None

    return config


if __name__ == "__main__":
    # 测试函数
    print("测试安全数据库工具函数...")

    # 测试数据库创建
    success = create_databases_safely()

    # 测试配置获取
    for db_type in ["postgresql", "tdengine", "redis"]:
        config = get_database_config(db_type)
        if config:
            print(f"✓ {db_type} 配置正常")
        else:
            print(f"✗ {db_type} 配置缺失")
