"""
安全的数据库管理工具函数
避免在代码中硬编码敏感信息，统一从环境变量读取
"""

import os
import pymysql
from dotenv import load_dotenv
from typing import Dict, Optional


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
        # 从环境变量获取MySQL连接参数
        mysql_host = os.getenv("MYSQL_HOST")
        mysql_user = os.getenv("MYSQL_USER")
        mysql_password = os.getenv("MYSQL_PASSWORD")
        mysql_port = int(os.getenv("MYSQL_PORT", "3306"))

        # 验证必要的参数是否存在
        if not all([mysql_host, mysql_user, mysql_password]):
            missing_params = []
            if not mysql_host:
                missing_params.append("MYSQL_HOST")
            if not mysql_user:
                missing_params.append("MYSQL_USER")
            if not mysql_password:
                missing_params.append("MYSQL_PASSWORD")

            raise ValueError(f"MySQL连接参数不完整，缺少: {', '.join(missing_params)}")

        print(f"连接到MySQL服务器: {mysql_user}@{mysql_host}:{mysql_port}")

        # 创建连接
        conn = pymysql.connect(
            host=mysql_host,
            user=mysql_user,
            password=mysql_password,
            port=mysql_port,
            connect_timeout=10,
        )

        cursor = conn.cursor()

        # 创建所需的数据库
        databases_to_create = [
            "test_db",
            "market_data",  # 可能用于TDengine
            "quant_research",  # 可能用于PostgreSQL
        ]

        for db_name in databases_to_create:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
            print(f"  ✓ 数据库 {db_name} 已确保存在")

        conn.commit()
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
    :param db_type: 数据库类型 ('mysql', 'postgresql', 'tdengine', 'redis', 'mariadb')
    :return: 数据库配置字典或None
    """
    # 加载环境变量
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    load_dotenv(env_path)

    config_map = {
        "mysql": {
            "host": os.getenv("MYSQL_HOST"),
            "user": os.getenv("MYSQL_USER"),
            "password": os.getenv("MYSQL_PASSWORD"),
            "port": int(os.getenv("MYSQL_PORT", "3306")),
        },
        "postgresql": {
            "host": os.getenv("POSTGRESQL_HOST"),
            "user": os.getenv("POSTGRESQL_USER"),
            "password": os.getenv("POSTGRESQL_PASSWORD"),
            "port": int(os.getenv("POSTGRESQL_PORT", "5432")),
        },
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
        "mariadb": {
            "host": os.getenv("MARIADB_HOST"),
            "user": os.getenv("MARIADB_USER"),
            "password": os.getenv("MARIADB_PASSWORD"),
            "port": int(os.getenv("MARIADB_PORT", "3307")),
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
    for db_type in ["mysql", "postgresql", "tdengine", "redis", "mariadb"]:
        config = get_database_config(db_type)
        if config:
            print(f"✓ {db_type} 配置正常")
        else:
            print(f"✗ {db_type} 配置缺失")
