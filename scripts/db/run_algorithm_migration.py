#!/usr/bin/env python3
"""
Algorithm Database Migration Script
Phase 1.4: Database Integration for Quantitative Trading Algorithms API

执行PostgreSQL数据库迁移，创建算法模型和执行结果相关的表结构
"""

import os
import sys
import logging
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# 添加项目根目录到Python路径
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, project_root)

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def get_db_connection():
    """获取PostgreSQL数据库连接"""
    # 从环境变量读取配置
    host = os.getenv("POSTGRESQL_HOST", "localhost")
    port = os.getenv("POSTGRESQL_PORT", "5432")
    user = os.getenv("POSTGRESQL_USER", "postgres")
    password = os.getenv("POSTGRESQL_PASSWORD", "")
    database = os.getenv("POSTGRESQL_DATABASE", "mystocks")

    logger.info(f"连接PostgreSQL数据库: {host}:{port}/{database}")

    try:
        conn = psycopg2.connect(
            host=host, port=port, user=user, password=password, database=database
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        logger.info("数据库连接成功")
        return conn
    except Exception as e:
        logger.error(f"数据库连接失败: {str(e)}")
        raise


def check_table_exists(conn, table_name):
    """检查表是否存在"""
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = %s
                )
                """,
                (table_name,),
            )
            exists = cursor.fetchone()[0]
            return exists
    except Exception as e:
        logger.error(f"检查表失败: {str(e)}")
        return False


def run_migration(conn, migration_file):
    """执行迁移脚本"""
    logger.info(f"执行迁移文件: {migration_file}")

    # 读取SQL文件
    try:
        with open(migration_file, "r", encoding="utf-8") as f:
            sql_content = f.read()
    except Exception as e:
        logger.error(f"读取迁移文件失败: {str(e)}")
        raise

    # 分割SQL语句并执行
    try:
        with conn.cursor() as cursor:
            # 执行整个SQL脚本
            cursor.execute(sql_content)
            logger.info("迁移脚本执行成功")
    except Exception as e:
        logger.error(f"执行迁移脚本失败: {str(e)}")
        raise


def verify_migration(conn):
    """验证迁移结果"""
    expected_tables = [
        "algorithm_models",
        "algorithm_execution_results",
        "algorithm_performance_metrics",
    ]

    logger.info("验证迁移结果...")

    all_exist = True
    for table_name in expected_tables:
        exists = check_table_exists(conn, table_name)
        if exists:
            logger.info(f"✓ 表 {table_name} 创建成功")

            # 查询表中的记录数
            try:
                with conn.cursor() as cursor:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0]
                    logger.info(f"  - 记录数: {count}")
            except Exception as e:
                logger.warning(f"  - 查询记录数失败: {str(e)}")
        else:
            logger.error(f"✗ 表 {table_name} 不存在")
            all_exist = False

    return all_exist


def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("Quantitative Trading Algorithms Database Migration")
    logger.info("Phase 1.4: Database Integration")
    logger.info("=" * 60)

    # 获取迁移文件路径
    migrations_dir = os.path.join(project_root, "scripts", "db", "migrations")
    migration_file = os.path.join(migrations_dir, "002_create_algorithm_tables.sql")

    if not os.path.exists(migration_file):
        logger.error(f"迁移文件不存在: {migration_file}")
        sys.exit(1)

    # 连接数据库
    try:
        conn = get_db_connection()
    except Exception:
        logger.error("数据库连接失败，退出")
        sys.exit(1)

    try:
        # 检查表是否已存在
        logger.info("检查表是否已存在...")
        tables_exist = []
        for table_name in [
            "algorithm_models",
            "algorithm_execution_results",
            "algorithm_performance_metrics",
        ]:
            exists = check_table_exists(conn, table_name)
            if exists:
                tables_exist.append(table_name)

        if tables_exist:
            logger.warning(f"以下表已存在: {', '.join(tables_exist)}")
            response = input("是否继续执行迁移 (可能会失败)? (y/N): ")
            if response.lower() != "y":
                logger.info("迁移已取消")
                conn.close()
                return

        # 执行迁移
        run_migration(conn, migration_file)

        # 验证迁移结果
        success = verify_migration(conn)

        if success:
            logger.info("=" * 60)
            logger.info("✓ 算法数据库迁移成功完成")
            logger.info("=" * 60)
            logger.info("创建的表:")
            logger.info("- algorithm_models: 算法模型存储表")
            logger.info("- algorithm_execution_results: 算法执行结果表")
            logger.info("- algorithm_performance_metrics: 算法性能监控表")
        else:
            logger.error("=" * 60)
            logger.error("✗ 迁移完成，但部分表未创建")
            logger.error("=" * 60)
            sys.exit(1)

    except Exception as e:
        logger.error(f"迁移过程中发生错误: {str(e)}")
        sys.exit(1)
    finally:
        conn.close()
        logger.info("数据库连接已关闭")


if __name__ == "__main__":
    main()
