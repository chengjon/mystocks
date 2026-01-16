#!/usr/bin/env python3
"""
Check and Create Algorithm Tables Migration Script
检查并创建算法相关数据库表

此脚本检查algorithm_models表是否存在，如果不存在则创建它。
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


def create_algorithm_tables(conn):
    """创建算法相关表"""
    logger.info("创建算法相关表...")

    # 读取table_config.yaml来获取表结构
    try:
        import yaml

        config_path = os.path.join(project_root, "config", "table_config.yaml")
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        # 查找algorithm_models表配置
        algorithm_config = None
        for db_config in config:
            if db_config.get("table_name") == "algorithm_models":
                algorithm_config = db_config
                break

        if not algorithm_config:
            logger.error("在table_config.yaml中未找到algorithm_models表配置")
            return False

        # 构建CREATE TABLE语句
        columns = algorithm_config["columns"]
        column_defs = []

        for col in columns:
            col_def = f"{col['name']} {col['type']}"
            if col.get("length"):
                col_def += f"({col['length']})"
            if not col.get("nullable", True):
                col_def += " NOT NULL"
            if col.get("primary_key"):
                col_def += " PRIMARY KEY"
            if col.get("default"):
                if isinstance(col["default"], str):
                    col_def += f" DEFAULT '{col['default']}'"
                else:
                    col_def += f" DEFAULT {col['default']}"
            column_defs.append(col_def)

        create_sql = f"""
        CREATE TABLE IF NOT EXISTS algorithm_models (
            {",\\n            ".join(column_defs)}
        );
        """

        # 执行创建表
        with conn.cursor() as cursor:
            cursor.execute(create_sql)
            logger.info("algorithm_models表创建成功")

        # 创建索引
        indexes = []
        for col in columns:
            if col.get("index"):
                index_name = f"idx_{algorithm_config['table_name']}_{col['name']}"
                indexes.append(
                    f"CREATE INDEX IF NOT EXISTS {index_name} ON {algorithm_config['table_name']}({col['name']});"
                )

        for index_sql in indexes:
            with conn.cursor() as cursor:
                cursor.execute(index_sql)
                logger.info(f"索引创建成功: {index_sql.split()[3]}")

        return True

    except Exception as e:
        logger.error(f"创建算法表失败: {str(e)}")
        return False


def verify_table_creation(conn):
    """验证表创建成功"""
    expected_columns = [
        "model_id",
        "algorithm_type",
        "model_name",
        "model_version",
        "model_data",
        "metadata",
        "training_metrics",
        "symbol",
        "features",
        "is_active",
        "gpu_trained",
        "created_at",
        "updated_at",
    ]

    logger.info("验证表创建...")

    try:
        with conn.cursor() as cursor:
            # 检查表是否存在
            if not check_table_exists(conn, "algorithm_models"):
                logger.error("algorithm_models表不存在")
                return False

            # 检查列是否存在
            cursor.execute("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = 'algorithm_models'
                ORDER BY ordinal_position;
            """)

            existing_columns = [row[0] for row in cursor.fetchall()]

            missing_columns = []
            for expected_col in expected_columns:
                if expected_col not in existing_columns:
                    missing_columns.append(expected_col)

            if missing_columns:
                logger.error(f"缺少列: {missing_columns}")
                return False

            logger.info("✓ algorithm_models表结构验证通过")
            logger.info(f"✓ 表包含 {len(existing_columns)} 列: {existing_columns}")

            # 检查是否有示例数据
            cursor.execute("SELECT COUNT(*) FROM algorithm_models")
            count = cursor.fetchone()[0]
            logger.info(f"✓ 表中有 {count} 条记录")

            return True

    except Exception as e:
        logger.error(f"验证表创建失败: {str(e)}")
        return False


def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("Algorithm Tables Migration Script")
    logger.info("检查并创建算法相关数据库表")
    logger.info("=" * 60)

    # 连接数据库
    try:
        conn = get_db_connection()
    except Exception:
        logger.error("数据库连接失败，无法创建表")
        logger.info("请确保PostgreSQL服务正在运行，并且环境变量配置正确")
        sys.exit(1)

    try:
        # 检查表是否已存在
        logger.info("检查algorithm_models表是否已存在...")
        table_exists = check_table_exists(conn, "algorithm_models")

        if table_exists:
            logger.info("✓ algorithm_models表已存在")
        else:
            logger.info("algorithm_models表不存在，开始创建...")
            success = create_algorithm_tables(conn)
            if not success:
                logger.error("创建表失败")
                sys.exit(1)

        # 验证表创建
        success = verify_table_creation(conn)

        if success:
            logger.info("=" * 60)
            logger.info("✓ 算法表迁移成功完成")
            logger.info("algorithm_models表已准备就绪")
            logger.info("=" * 60)
        else:
            logger.error("=" * 60)
            logger.error("✗ 表验证失败")
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
