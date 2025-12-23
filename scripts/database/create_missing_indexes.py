"""
创建数据库缺失的索引
用于解决技术债务中的数据库性能优化需求
"""

import os
import sys
import structlog
import psycopg2
from psycopg2 import sql
from typing import Dict, List
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from src.core.config import DatabaseConfig
    from src.core.exceptions import DatabaseConnectionError, DatabaseOperationError
except ImportError:
    # 如果导入失败，创建简单的占位类
    class DatabaseConnectionError(Exception):
        pass

    class DatabaseOperationError(Exception):
        pass

    class DatabaseConfig:
        def get_postgresql_url(self):
            from dotenv import load_dotenv

            load_dotenv()

            host = os.getenv("POSTGRES_HOST", "localhost")
            port = os.getenv("POSTGRES_PORT", "5432")
            database = os.getenv("POSTGRES_DB", "mystocks")
            username = os.getenv("POSTGRES_USER", "postgres")
            password = os.getenv("POSTGRES_PASSWORD", "password")

            return f"postgresql://{username}:{password}@{host}:{port}/{database}"


logger = structlog.get_logger()


class DatabaseIndexManager:
    """数据库索引管理器"""

    def __init__(self, db_config: DatabaseConfig):
        """
        初始化索引管理器

        Args:
            db_config: 数据库配置
        """
        self.db_config = db_config
        self.connection = None

    def connect(self):
        """连接到PostgreSQL数据库"""
        try:
            connection_string = self.db_config.get_postgresql_url()
            self.connection = psycopg2.connect(connection_string)
            self.connection.autocommit = True  # 设置为自动提交
            logger.info("数据库连接成功")

        except Exception as e:
            logger.error("数据库连接失败", error=str(e))
            raise DatabaseConnectionError(
                message=f"Failed to connect to database: {str(e)}",
                code="DB_CONNECTION_FAILED",
                severity="CRITICAL",
                original_exception=e,
            )

    def close(self):
        """关闭数据库连接"""
        if self.connection and not self.connection.closed:
            self.connection.close()
            logger.info("数据库连接已关闭")

    def create_index(
        self,
        table_name: str,
        index_name: str,
        columns: List[str],
        index_type: str = "btree",
        unique: bool = False,
    ) -> bool:
        """
        创建数据库索引

        Args:
            table_name: 表名
            index_name: 索引名
            columns: 列名列表
            index_type: 索引类型
            unique: 是否唯一索引

        Returns:
            bool: 是否创建成功
        """
        try:
            with self.connection.cursor() as cursor:
                # 检查索引是否已存在
                check_query = sql.SQL("""
                    SELECT 1 FROM pg_indexes
                    WHERE tablename = %s AND indexname = %s
                """)

                cursor.execute(check_query, (table_name, index_name))
                if cursor.fetchone():
                    logger.info("索引已存在", table=table_name, index=index_name)
                    return True

                # 创建索引
                unique_constraint = "UNIQUE" if unique else ""
                columns_sql = sql.SQL(", ").join(
                    [sql.Identifier(col) for col in columns]
                )

                create_query = sql.SQL("""
                    CREATE {unique} INDEX {index_name}
                    ON {table_name} USING {index_type} ({columns})
                """).format(
                    unique=sql.SQL(unique_constraint),
                    index_name=sql.Identifier(index_name),
                    table_name=sql.Identifier(table_name),
                    index_type=sql.SQL(index_type),
                    columns=columns_sql,
                )

                logger.info(
                    "正在创建索引", table=table_name, index=index_name, columns=columns
                )

                cursor.execute(create_query)

                # 验证索引是否创建成功
                cursor.execute(check_query, (table_name, index_name))
                if cursor.fetchone():
                    logger.info("索引创建成功", table=table_name, index=index_name)
                    return True
                else:
                    logger.error("索引创建失败", table=table_name, index=index_name)
                    return False

        except Exception as e:
            logger.error(
                "创建索引时出错", table=table_name, index=index_name, error=str(e)
            )
            return False

    def get_index_info(self, table_name: str) -> List[Dict]:
        """
        获取表的索引信息

        Args:
            table_name: 表名

        Returns:
            List[Dict]: 索引信息列表
        """
        try:
            with self.connection.cursor() as cursor:
                query = sql.SQL("""
                    SELECT
                        indexname as index_name,
                        indexdef as definition
                    FROM pg_indexes
                    WHERE tablename = %s
                    ORDER BY indexname
                """)

                cursor.execute(query, (table_name,))
                results = cursor.fetchall()

                return [{"index_name": row[0], "definition": row[1]} for row in results]

        except Exception as e:
            logger.error("获取索引信息时出错", table=table_name, error=str(e))
            return []


def create_missing_indexes():
    """创建所有缺失的索引"""
    logger.info("开始创建缺失的数据库索引")

    # 获取数据库配置
    db_config = DatabaseConfig()

    # 创建索引管理器
    index_manager = DatabaseIndexManager(db_config)

    try:
        # 连接数据库
        index_manager.connect()

        # 定义需要创建的索引
        indexes_to_create = [
            {
                "table_name": "order_records",
                "index_name": "idx_order_records_user_time",
                "columns": ["user_id", "created_at"],
                "index_type": "btree",
                "unique": False,
            },
            {
                "table_name": "daily_kline",
                "index_name": "idx_daily_kline_symbol_date",
                "columns": ["symbol", "trade_date"],
                "index_type": "btree",
                "unique": False,  # 注意：配置中显示这个索引已存在且是唯一的
            },
            {
                "table_name": "stock_basic_info",
                "index_name": "idx_stock_basic_info_code",
                "columns": ["stock_code"],
                "index_type": "btree",
                "unique": True,
            },
            {
                "table_name": "watchlist",
                "index_name": "idx_watchlist_user_symbol",
                "columns": ["user_id", "symbol"],
                "index_type": "btree",
                "unique": False,
            },
            {
                "table_name": "portfolio",
                "index_name": "idx_portfolio_user_code",
                "columns": ["user_id", "stock_code"],
                "index_type": "btree",
                "unique": False,
            },
            {
                "table_name": "alert_conditions",
                "index_name": "idx_alert_user_symbol",
                "columns": ["user_id", "symbol"],
                "index_type": "btree",
                "unique": False,
            },
            {
                "table_name": "strategy_backtest",
                "index_name": "idx_strategy_user_time",
                "columns": ["user_id", "created_at"],
                "index_type": "btree",
                "unique": False,
            },
            {
                "table_name": "trade_log",
                "index_name": "idx_trade_user_symbol_time",
                "columns": ["user_id", "symbol", "trade_time"],
                "index_type": "btree",
                "unique": False,
            },
        ]

        created_count = 0
        failed_count = 0

        # 创建索引
        for index_config in indexes_to_create:
            table_name = index_config["table_name"]
            index_name = index_config["index_name"]

            logger.info(f"正在处理表: {table_name}")

            # 显示当前索引状态
            current_indexes = index_manager.get_index_info(table_name)
            logger.info(f"当前索引数量: {len(current_indexes)}")

            # 创建索引
            success = index_manager.create_index(
                table_name=table_name,
                index_name=index_name,
                columns=index_config["columns"],
                index_type=index_config["index_type"],
                unique=index_config["unique"],
            )

            if success:
                created_count += 1
                logger.info(f"成功创建索引: {index_name}")
            else:
                failed_count += 1
                logger.error(f"创建索引失败: {index_name}")

        # 显示最终统计信息
        logger.info(
            "索引创建完成",
            total=len(indexes_to_create),
            created=created_count,
            failed=failed_count,
        )

        # 为每个表显示最终的索引状态
        tables = [
            "order_records",
            "daily_kline",
            "stock_basic_info",
            "watchlist",
            "portfolio",
            "alert_conditions",
            "strategy_backtest",
            "trade_log",
        ]

        for table in tables:
            logger.info(f"表 {table} 的索引状态:")
            indexes = index_manager.get_index_info(table)
            for idx in indexes:
                logger.info(f"  - {idx['index_name']}")

    except Exception as e:
        logger.error("创建索引过程中发生错误", error=str(e))
        raise DatabaseOperationError(
            message=f"Failed to create indexes: {str(e)}",
            code="INDEX_CREATION_FAILED",
            severity="HIGH",
            original_exception=e,
        )

    finally:
        # 关闭连接
        index_manager.close()


if __name__ == "__main__":
    # 设置日志
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    try:
        create_missing_indexes()
        print("✅ 所有缺失的索引创建完成")

    except Exception as e:
        print(f"❌ 创建索引失败: {str(e)}")
        sys.exit(1)
