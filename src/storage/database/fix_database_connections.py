#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库连接修复工具
用于解决MyStocks项目中的数据库连接问题
"""

import os
import sys
import logging
import psycopg2
import pymysql

# 添加项目路径到模块搜索路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.storage.database.database_manager import DatabaseTableManager, DatabaseType

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("DatabaseFixer")


def check_database_connections():
    """检查所有数据库连接配置"""
    logger.info("🔍 检查数据库连接配置...")

    databases = ["mysql", "postgresql", "tdengine", "redis", "mariadb"]
    all_good = True

    for db in databases:
        try:
            # 检查环境变量配置
            host_key = f"{db.upper()}_HOST"
            if os.getenv(host_key):
                logger.info(f"✓ {db} 配置正常")
            else:
                logger.warning(f"⚠ {db} 配置缺失")
                all_good = False
        except Exception as e:
            logger.error(f"✗ {db} 配置检查失败: {e}")
            all_good = False

    return all_good


def fix_postgresql_hypertable():
    """修复PostgreSQL中的hypertable问题"""
    logger.info("🔧 修复PostgreSQL hypertable问题...")

    try:
        # 直接使用psycopg2连接PostgreSQL
        conn = psycopg2.connect(
            host=os.getenv("POSTGRESQL_HOST", "localhost"),
            port=os.getenv("POSTGRESQL_PORT", "5432"),
            user=os.getenv("POSTGRESQL_USER", "postgres"),
            password=os.getenv("POSTGRESQL_PASSWORD", ""),
            database=os.getenv("POSTGRESQL_DATABASE", "postgres"),
        )
        cur = conn.cursor()

        # 检查TimescaleDB扩展
        cur.execute("SELECT extname FROM pg_extension WHERE extname = 'timescaledb';")
        result = cur.fetchone()

        if not result:
            logger.info("安装TimescaleDB扩展...")
            cur.execute("CREATE EXTENSION IF NOT EXISTS timescaledb;")
            conn.commit()
            logger.info("✓ TimescaleDB扩展安装完成")
        else:
            logger.info("✓ TimescaleDB扩展已安装")

        cur.close()
        conn.close()
        logger.info("✓ PostgreSQL hypertable问题修复成功")
        return True

    except Exception as e:
        logger.error(f"✗ PostgreSQL hypertable修复失败: {e}")
        return False


def fix_tdengine_database():
    """修复TDengine数据库指定问题"""
    logger.info("🔧 修复TDengine数据库指定问题...")

    try:
        # 检查TDengine是否已指定数据库
        if not os.getenv("TDENGINE_DATABASE"):
            logger.info("为TDengine添加默认数据库名称: market_data")
            # 更新环境变量（仅在当前进程中有效）
            os.environ["TDENGINE_DATABASE"] = "market_data"
            logger.info("✓ TDengine数据库指定问题修复成功")
            return True
        else:
            logger.info("✓ TDengine已正确指定数据库")
            return True
    except Exception as e:
        logger.error(f"✗ TDengine数据库指定修复失败: {e}")
        return False


def create_databases():
    """创建所需的数据库"""
    logger.info("🏗️  创建数据库...")
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
            os.getenv("TDENGINE_DATABASE", "market_data"),
            os.getenv("MYSQL_DATABASE", "quant_research"),
            os.getenv("POSTGRESQL_DATABASE", "mystocks"),
        ]

        for db_name in databases_to_create:
            if db_name:  # 确保数据库名称不为空
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
                print(f"  ✓ 数据库 {db_name} 已确保存在")

        conn.commit()
        cursor.close()
        conn.close()

        # 为MariaDB也创建数据库
        mariadb_host = os.getenv("MARIADB_HOST")
        mariadb_user = os.getenv("MARIADB_USER")
        mariadb_password = os.getenv("MARIADB_PASSWORD")
        mariadb_port = int(os.getenv("MARIADB_PORT", "3306"))

        if mariadb_host and mariadb_user and mariadb_password:
            print(f"连接到MariaDB服务器: {mariadb_user}@{mariadb_host}:{mariadb_port}")
            conn = pymysql.connect(
                host=mariadb_host,
                user=mariadb_user,
                password=mariadb_password,
                port=mariadb_port,
                connect_timeout=10,
            )

            cursor = conn.cursor()
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS {os.getenv('MARIADB_DATABASE', 'quant_research')}"
            )
            print(
                f"  ✓ MariaDB数据库 {os.getenv('MARIADB_DATABASE', 'quant_research')} 已确保存在"
            )
            conn.commit()
            cursor.close()
            conn.close()

        logger.info("✓ 数据库创建成功")
        return True

    except Exception as e:
        logger.error(f"✗ 数据库创建失败: {e}")
        return False


def validate_connections():
    """验证所有数据库连接"""
    logger.info("🔍 验证数据库连接...")

    try:
        manager = DatabaseTableManager()
        databases = [
            (
                DatabaseType.MYSQL,
                "mysql",
                os.getenv("MYSQL_DATABASE", "quant_research"),
            ),
            (
                DatabaseType.POSTGRESQL,
                "postgresql",
                os.getenv("POSTGRESQL_DATABASE", "mystocks"),
            ),
            (
                DatabaseType.TDENGINE,
                "tdengine",
                os.getenv("TDENGINE_DATABASE", "market_data"),
            ),
            (DatabaseType.REDIS, "redis", None),
            (
                DatabaseType.MARIADB,
                "mariadb",
                os.getenv("MARIADB_DATABASE", "quant_research"),
            ),
        ]
        success_count = 0

        for db_type, db_name, default_db in databases:
            try:
                # 尝试连接数据库
                db_to_connect = default_db if default_db else "test_db"
                if db_name == "redis":
                    # Redis不需要指定数据库名
                    conn = manager.get_connection(db_type, None)
                else:
                    conn = manager.get_connection(db_type, db_to_connect)

                if conn:
                    logger.info(f"✓ {db_name}: 正常")
                    success_count += 1
                else:
                    logger.warning(f"⚠ {db_name}: 连接失败")
            except Exception as e:
                logger.error(f"✗ {db_name}: 连接错误 - {e}")

        logger.info(f"数据库连接验证完成: {success_count}/{len(databases)} 成功")
        # 允许最多一个数据库连接失败
        return success_count >= len(databases) - 1

    except Exception as e:
        logger.error(f"✗ 数据库连接验证失败: {e}")
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("🚀 MyStocks 数据库连接修复工具")
    print("=" * 60)

    # 检查数据库连接配置
    if not check_database_connections():
        logger.error("数据库配置检查失败，请检查环境变量配置")
        return False

    # 修复PostgreSQL hypertable问题
    if not fix_postgresql_hypertable():
        logger.error("PostgreSQL hypertable修复失败")
        return False

    # 修复TDengine数据库指定问题
    if not fix_tdengine_database():
        logger.error("TDengine数据库指定修复失败")
        return False

    # 创建数据库
    if not create_databases():
        logger.error("数据库创建失败")
        return False

    # 验证连接
    if not validate_connections():
        logger.error("数据库连接验证失败")
        return False

    print("=" * 60)
    print("✅ 数据库连接修复工具执行完成")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
