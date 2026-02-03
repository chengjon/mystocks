#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库连接修复工具
用于解决MyStocks项目中的数据库连接问题（MySQL已移除）
"""

import logging
import os
import sys

import psycopg2
from psycopg2 import sql

# 添加项目路径到模块搜索路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.storage.database.database_manager import DatabaseTableManager, DatabaseType

# 配置日志
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("DatabaseFixer")


def check_database_connections():
    """检查所有数据库连接配置"""
    logger.info("🔍 检查数据库连接配置...")

    databases = ["postgresql", "tdengine", "redis"]
    all_good = True

    for db in databases:
        try:
            # 检查环境变量配置
            host_key = f"{db.upper()}_HOST"
            if os.getenv(host_key):
                logger.info("✓ %s 配置正常", db)
            else:
                logger.warning("⚠ %s 配置缺失", db)
                all_good = False
        except Exception as e:
            logger.error("✗ %s 配置检查失败: %s", db, e)
            all_good = False

    return all_good


def fix_postgresql_hypertable():
    """修复PostgreSQL中的hypertable问题"""
    logger.info("🔧 修复PostgreSQL hypertable问题...")

    conn = None
    cur = None
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

        logger.info("✓ PostgreSQL hypertable问题修复成功")
        return True

    except Exception as e:
        logger.error("✗ PostgreSQL hypertable修复失败: %s", e)
        return False
    finally:
        if cur is not None:
            try:
                cur.close()
            except Exception:
                pass
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass


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
        logger.error("✗ TDengine数据库指定修复失败: %s", e)
        return False


def create_databases():
    """创建所需的数据库"""
    logger.info("🏗️  创建数据库...")
    print("正在创建所需的数据库...")

    conn = None
    cursor = None

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

        # 连接到管理数据库（默认postgres）
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
            os.getenv("POSTGRESQL_DATABASE", "mystocks"),
            os.getenv("MONITOR_DB_DATABASE", "mystocks_monitoring"),
            "quant_research",
        ]

        for db_name in databases_to_create:
            if db_name:  # 确保数据库名称不为空
                cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
                exists = cursor.fetchone() is not None
                if not exists:
                    cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))
                print(f"  ✓ 数据库 {db_name} 已确保存在")

        logger.info("✓ 数据库创建成功")
        return True

    except Exception as e:
        logger.error("✗ 数据库创建失败: %s", e)
        return False
    finally:
        if cursor is not None:
            try:
                cursor.close()
            except Exception:
                pass
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass
        # PostgreSQL 连接清理


def validate_connections():
    """验证所有数据库连接"""
    logger.info("🔍 验证数据库连接...")

    try:
        manager = DatabaseTableManager()
        databases = [
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
                    logger.info("✓ %s: 正常", db_name)
                    success_count += 1
                else:
                    logger.warning("⚠ %s: 连接失败", db_name)
            except Exception as e:
                logger.error("✗ %s: 连接错误 - %s", db_name, e)

        logger.info("数据库连接验证完成: %s/%s 成功", success_count, len(databases))
        # 允许最多一个数据库连接失败
        return success_count >= len(databases) - 1

    except Exception as e:
        logger.error("✗ 数据库连接验证失败: %s", e)
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
