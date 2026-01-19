#!/usr/bin/env python3
"""
文件分析数据库初始化脚本
用途：创建PostgreSQL数据库并初始化表结构
"""

import os
import sys
import psycopg2
from psycopg2 import sql
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 数据库配置
DB_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': int(os.getenv('POSTGRES_PORT', 5432)),
    'database': os.getenv('POSTGRES_DB', 'mystocks'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', 'postgres')
}

# 数据库名称
ANALYSIS_DB_NAME = 'file_analysis_db'


def create_connection(dbname=None):
    """创建数据库连接"""
    config = DB_CONFIG.copy()
    if dbname:
        config['database'] = dbname
    else:
        # 连接到postgres数据库以创建新数据库
        config['database'] = 'postgres'

    try:
        conn = psycopg2.connect(**config)
        conn.autocommit = True
        return conn
    except Exception as e:
        logger.error(f"数据库连接失败: {e}")
        raise


def create_database():
    """创建文件分析数据库"""
    logger.info(f"开始创建数据库: {ANALYSIS_DB_NAME}")

    conn = create_connection()
    cursor = conn.cursor()

    try:
        # 检查数据库是否已存在
        cursor.execute(
            sql.SQL("SELECT 1 FROM pg_database WHERE datname = {}").format(
                sql.Literal(ANALYSIS_DB_NAME)
            )
        )
        exists = cursor.fetchone()

        if exists:
            logger.info(f"数据库 {ANALYSIS_DB_NAME} 已存在")
        else:
            # 创建数据库
            cursor.execute(
                sql.SQL("CREATE DATABASE {}").format(
                    sql.Identifier(ANALYSIS_DB_NAME)
                )
            )
            logger.info(f"数据库 {ANALYSIS_DB_NAME} 创建成功")

        cursor.close()
        conn.close()

        # 连接到新数据库
        return create_connection(ANALYSIS_DB_NAME)

    except Exception as e:
        logger.error(f"创建数据库失败: {e}")
        cursor.close()
        conn.close()
        raise


def execute_schema_file(conn, schema_file_path):
    """执行schema.sql文件"""
    logger.info(f"开始执行schema文件: {schema_file_path}")

    if not os.path.exists(schema_file_path):
        logger.error(f"Schema文件不存在: {schema_file_path}")
        return False

    try:
        with open(schema_file_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()

        cursor = conn.cursor()
        cursor.execute(schema_sql)
        cursor.close()

        logger.info("Schema执行成功")
        return True

    except Exception as e:
        logger.error(f"执行Schema失败: {e}")
        return False


def verify_tables(conn):
    """验证表是否创建成功"""
    logger.info("开始验证表结构")

    expected_tables = [
        'analysis_runs',
        'file_categories',
        'file_metadata',
        'file_references'
    ]

    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)

        existing_tables = [row[0] for row in cursor.fetchall()]

        logger.info(f"已创建的表: {', '.join(existing_tables)}")

        # 检查所有期望的表是否存在
        missing_tables = set(expected_tables) - set(existing_tables)
        if missing_tables:
            logger.warning(f"缺少的表: {', '.join(missing_tables)}")
            return False
        else:
            logger.info("所有表创建成功")
            return True

    except Exception as e:
        logger.error(f"验证表失败: {e}")
        return False
    finally:
        cursor.close()


def insert_test_data(conn):
    """插入测试数据"""
    logger.info("开始插入测试数据")

    cursor = conn.cursor()

    try:
        # 创建一个测试分析运行记录
        test_run_id = "test-run-001"
        cursor.execute("""
            INSERT INTO analysis_runs (run_id, status, total_files)
            VALUES (%s, 'completed', 0)
            RETURNING id
        """, (test_run_id,))

        run_id = cursor.fetchone()[0]
        logger.info(f"测试分析运行记录创建成功，ID: {run_id}")

        conn.commit()
        cursor.close()
        return True

    except Exception as e:
        logger.error(f"插入测试数据失败: {e}")
        conn.rollback()
        return False
    finally:
        if cursor and not cursor.closed:
            cursor.close()


def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("文件分析数据库初始化开始")
    logger.info("=" * 60)

    try:
        # 创建数据库
        conn = create_database()

        # 执行schema文件
        schema_file = os.path.join(
            os.path.dirname(__file__),
            'schema.sql'
        )

        if not execute_schema_file(conn, schema_file):
            logger.error("Schema执行失败，退出")
            return 1

        # 验证表结构
        if not verify_tables(conn):
            logger.error("表验证失败，退出")
            return 1

        # 插入测试数据
        if not insert_test_data(conn):
            logger.warning("测试数据插入失败，但不影响系统运行")

        conn.close()

        logger.info("=" * 60)
        logger.info("文件分析数据库初始化完成")
        logger.info("=" * 60)
        logger.info(f"数据库名称: {ANALYSIS_DB_NAME}")
        logger.info(f"连接信息: host={DB_CONFIG['host']}, port={DB_CONFIG['port']}")
        logger.info("=" * 60)

        return 0

    except Exception as e:
        logger.error(f"初始化失败: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())