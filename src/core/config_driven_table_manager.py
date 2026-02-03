"""
配置驱动的表管理器

根据table_config.yaml自动创建和管理数据库表结构,支持安全模式和版本管理。

创建日期: 2025-10-11
版本: 1.0.0
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

# 数据库连接
from src.storage.database.connection_manager import DatabaseConnectionManager

logger = logging.getLogger(__name__)


class ConfigDrivenTableManager:
    """配置驱动的表管理器"""

    def __init__(self, config_path: str = "config/table_config.yaml", safe_mode: bool = True) -> None:
        """
        初始化表管理器

        Args:
            config_path: 配置文件路径
            safe_mode: 是否启用安全模式(默认True)
        """
        self.config_path = Path(config_path)
        self.safe_mode = safe_mode
        self.conn_manager = DatabaseConnectionManager()
        self.logger = logger

        if not self.config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")

        # 加载配置
        self.config = self.load_config()

        logger.info("✅ ConfigDrivenTableManager initialized (safe_mode=%s)", self.safe_mode)

    def load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        with open(self.config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        version = config.get("version", "1.0.0")
        logger.info("加载配置文件: %s (version=%s)", self.config_path, version)
        logger.info("配置文件包含 %s 个表定义", len(config["tables"]))

        return dict(config) if config else {}

    def _normalize_db_type(self, db_type: str) -> str:
        if db_type in {"MySQL", "MariaDB"}:
            raise ValueError("MySQL/MariaDB已移除，请使用PostgreSQL")
        return db_type

    def initialize_tables(self) -> Dict[str, Any]:
        """根据配置初始化所有表"""
        config = self.load_config()
        result: Dict[str, Any] = {
            "tables_created": 0,
            "tables_skipped": 0,
            "errors": [],
        }

        logger.info("开始初始化表 (total=%s)", len(config["tables"]))

        for table_def in config["tables"]:
            try:
                created = self._create_table(table_def)
                if created:
                    result["tables_created"] += 1
                    logger.info("创建表: %s (%s)", table_def['table_name'], table_def['database_type'])
                else:
                    result["tables_skipped"] += 1
                    logger.info("⏭️ 跳过表: %s (已存在)", table_def["table_name"])

            except Exception as e:
                error_msg = f"{table_def['table_name']}: {str(e)}"
                result["errors"].append(error_msg)
                logger.error("❌ 创建表失败: %s", error_msg)

        self.logger.info("配置驱动表管理器初始化完成")
        logger.info(
            "表初始化完成: created=%s, skipped=%s, errors=%s",
            result["tables_created"],
            result["tables_skipped"],
            len(result["errors"]),
        )

        return result

    def _create_table(self, table_def: Dict[str, Any]) -> bool:
        """
        创建单个表

        Args:
            table_def: 表定义字典

        Returns:
            True表示创建成功,False表示表已存在
        """
        db_type = self._normalize_db_type(table_def["database_type"])
        table_name = table_def["table_name"]

        # 检查表是否已存在
        if self._table_exists(db_type, table_name, table_def.get("database_name")):
            return False

        # 根据数据库类型调用相应的创建方法
        if db_type == "TDengine":
            return self._create_tdengine_super_table(table_def)
        elif db_type == "PostgreSQL":
            return self._create_postgresql_table(table_def)
        elif db_type == "Redis":
            # Redis不需要预先创建表结构
            logger.info("Redis数据结构 %s 无需预创建", table_name)
            return False
        else:
            raise ValueError(f"不支持的数据库类型: {db_type}")

    def _table_exists(self, db_type: str, table_name: str, database_name: Optional[str] = None) -> bool:
        """检查表是否存在"""
        try:
            db_type = self._normalize_db_type(db_type)
            if db_type == "TDengine":
                conn = self.conn_manager.get_tdengine_connection()
                cursor = conn.cursor()
                # 验证表名只包含字母、数字和下划线，防止SQL注入
                import re

                if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", table_name):
                    raise ValueError(f"Invalid table name: {table_name}")

                query = f"SHOW STABLES LIKE '{table_name}'"
                cursor.execute(query)
                result = cursor.fetchall()
                cursor.close()
                return len(result) > 0

            elif db_type == "PostgreSQL":
                conn = self.conn_manager.get_postgresql_connection()
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_name = %s
                    )
                """,
                    (table_name,),
                )
                exists = cursor.fetchone()[0]
                cursor.close()
                self.conn_manager._return_postgresql_connection(conn)
                return bool(exists)

            else:
                return False

        except Exception as e:
            logger.warning("检查表存在性时出错 (%s): %s", table_name, e)
            return False

    def _create_tdengine_super_table(self, table_def: Dict[str, Any]) -> bool:
        """创建TDengine Super Table"""
        conn = self.conn_manager.get_tdengine_connection()
        cursor = conn.cursor()

        try:
            table_name = table_def["table_name"]
            columns = table_def["columns"]
            tags = table_def.get("tags", [])

            # 验证表名防止SQL注入
            import re

            if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", table_name):
                raise ValueError(f"Invalid table name: {table_name}")

            # 构建列定义
            col_defs = []
            for col in columns:
                col_type = col["type"]
                if "length" in col:
                    col_type += f"({col['length']})"
                nullable = "" if col.get("nullable", True) else " NOT NULL"
                col_defs.append(f"{col['name']} {col_type}{nullable}")

            # 构建标签定义
            tag_defs = []
            for tag in tags:
                tag_type = tag["type"]
                if "length" in tag:
                    tag_type += f"({tag['length']})"
                tag_defs.append(f"{tag['name']} {tag_type}")

            # 构建CREATE语句
            create_sql = f"""
                CREATE STABLE IF NOT EXISTS {table_name} (
                    {", ".join(col_defs)}
                ) TAGS (
                    {", ".join(tag_defs)}
                )
            """

            cursor.execute(create_sql)

            # 设置压缩和保留策略
            compression = table_def.get("compression", {})
            if compression.get("enabled"):
                codec = compression.get("codec", "zstd").upper()
                level = compression.get("level", "medium").upper()
                # TDengine 3.0+ 压缩配置 (注:实际语法可能需要调整)
                logger.info("TDengine表 %s 压缩配置: %s / %s", table_name, codec, level)

            retention_days = table_def.get("retention_days")
            if retention_days:
                # 验证保留天数防止SQL注入
                if not isinstance(retention_days, int) or retention_days <= 0:
                    raise ValueError(f"Invalid retention days: {retention_days}")
                query = f"ALTER STABLE {table_name} KEEP {retention_days}"
                cursor.execute(query)

            cursor.close()
            return True

        except Exception as e:
            cursor.close()
            raise RuntimeError(f"创建TDengine Super Table失败: {e}")

    def _create_postgresql_table(self, table_def: Dict[str, Any]) -> bool:
        """创建PostgreSQL表 (支持TimescaleDB)"""
        pool = self.conn_manager.get_postgresql_connection()
        conn = pool.getconn()
        cursor = conn.cursor()

        try:
            table_name = table_def["table_name"]
            columns = table_def["columns"]
            indexes = table_def.get("indexes", [])
            is_hypertable = table_def.get("is_timescale_hypertable", False)
            time_column = table_def.get("time_column", "created_at")

            # 构建列定义
            col_defs = []
            primary_keys = []

            for col in columns:
                col_type = col["type"]
                if "length" in col and "VARCHAR" in col_type:
                    col_type = f"VARCHAR({col['length']})"
                elif "precision" in col and "scale" in col:
                    col_type = f"NUMERIC({col['precision']},{col['scale']})"

                nullable = "" if col.get("nullable", True) else " NOT NULL"
                default = f" DEFAULT {col['default']}" if col.get("default") else ""
                unique = " UNIQUE" if col.get("unique") else ""

                # PostgreSQL uses SERIAL instead of AUTO_INCREMENT
                if col.get("auto_increment"):
                    if "INT" in col_type.upper():
                        col_type = "SERIAL"
                    nullable = ""  # SERIAL is NOT NULL by default

                col_defs.append(f"{col['name']} {col_type}{nullable}{default}{unique}")

                if col.get("primary_key"):
                    primary_keys.append(col["name"])

            # 添加主键约束
            if primary_keys:
                col_defs.append(f"PRIMARY KEY ({', '.join(primary_keys)})")

            # 构建CREATE语句
            create_sql = f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    {", ".join(col_defs)}
                )
            """

            cursor.execute(create_sql)

            # 如果是TimescaleDB超表
            if is_hypertable:
                try:
                    cursor.execute(f"SELECT create_hypertable('{table_name}', '{time_column}')")
                    logger.info("✅ 转换为Hypertable: %s", table_name)
                except Exception as e:
                    logger.warning("转换为Hypertable失败: %s", e)

            # 创建索引
            for idx in indexes:
                idx_name = idx.get("name", f"idx_{table_name}_{idx['columns'][0]}")
                idx_columns = idx["columns"]
                is_unique = idx.get("unique", False)

                if is_unique:
                    idx_sql = f"CREATE UNIQUE INDEX IF NOT EXISTS {idx_name} ON {table_name} ({', '.join(idx_columns)})"
                else:
                    idx_sql = f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table_name} ({', '.join(idx_columns)})"

                try:
                    cursor.execute(idx_sql)
                    logger.info("✅ 创建索引: %s", idx_name)
                except Exception as e:
                    logger.warning("创建索引时出错 (%s): %s", idx_name, e)

            cursor.close()
            conn.commit()
            self.conn_manager._return_postgresql_connection(conn)
            return True

        except Exception as e:
            cursor.close()
            conn.rollback()
            self.conn_manager._return_postgresql_connection(conn)
            raise RuntimeError(f"创建PostgreSQL表失败: {e}")

    def validate_table_structure(self, table_def: Dict[str, Any]) -> bool:
        """验证表结构是否符合配置"""
        db_type = self._normalize_db_type(table_def["database_type"])
        table_name = table_def["table_name"]

        try:
            # 检查表是否存在
            if not self._table_exists(db_type, table_name, table_def.get("database_name")):
                logger.warning("表不存在: %s (%s)", table_name, db_type)
                return False

            # 获取实际表结构
            actual_structure = self._get_table_structure(db_type, table_name)
            if not actual_structure:
                logger.error("无法获取表结构 %s: 结构为空", table_name)
                return False

            # 验证列结构
            expected_columns = {col["name"]: col for col in table_def["columns"]}
            actual_columns = {col["name"]: col for col in actual_structure}

            # 检查缺失的列
            missing_columns = set(expected_columns.keys()) - set(actual_columns.keys())
            if missing_columns:
                logger.warning("表 %s 缺少列: %s", table_name, ", ".join(missing_columns))
                return False

            # 检查多余的列
            extra_columns = set(actual_columns.keys()) - set(expected_columns.keys())
            if extra_columns:
                logger.info("表 %s 存在配置外的列: %s", table_name, ", ".join(extra_columns))

            # 检查列类型
            for col_name, expected_col in expected_columns.items():
                if col_name in actual_columns:
                    actual_col = actual_columns[col_name]
                    expected_type = expected_col["type"]
                    actual_type = actual_col["type"]

                    # 简单类型匹配检查
                    if expected_type.upper() != actual_type.upper():
                        logger.warning(
                            "表 %s 列 %s 类型不匹配: 期望 %s, 实际 %s", table_name, col_name, expected_type, actual_type
                        )
                        return False

            logger.info("✅ 表结构验证通过: %s", table_name)
            return True

        except Exception as e:
            logger.error("表结构验证失败 %s: %s", table_name, e)
            return False

            logger.info("✅ 表结构验证通过: %s", table_name)
            return True

        except Exception as e:
            logger.error("表结构验证失败 %s: %s", table_name, e)
            return False

    def _get_table_structure(self, db_type: str, table_name: str) -> Optional[List[Dict]]:
        """获取表结构信息"""
        try:
            db_type = self._normalize_db_type(db_type)
            if db_type == "PostgreSQL":
                conn = self.conn_manager.get_postgresql_connection()
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT column_name, data_type
                    FROM information_schema.columns
                    WHERE table_name = %s
                    ORDER BY ordinal_position
                """,
                    (table_name,),
                )
                result = cursor.fetchall()
                cursor.close()
                self.conn_manager._return_postgresql_connection(conn)

                return [{"name": row[0], "type": row[1]} for row in result]

            elif db_type == "TDengine":
                conn = self.conn_manager.get_tdengine_connection()
                cursor = conn.cursor()
                cursor.execute(f"DESCRIBE {table_name}")
                result = cursor.fetchall()
                cursor.close()

                return [{"name": row[0], "type": row[1]} for row in result]

            else:
                logger.warning("不支持的数据库类型: %s", db_type)
                return None

        except Exception as e:
            logger.error("获取表结构失败 %s: %s", table_name, e)
            return None


def main():
    """主函数 - 用于测试"""
    try:
        manager = ConfigDrivenTableManager()
        result = manager.initialize_tables()

        print("\n表创建结果:")
        print(f"  创建: {result['tables_created']}个表")
        print(f"  跳过: {result['tables_skipped']}个表")
        print(f"  错误: {len(result['errors'])}个")

        if result["errors"]:
            print("\n错误详情:")
            for error in result["errors"]:
                print(f"  - {error}")

    except Exception as e:
        print(f"❌ 初始化失败: {e}")


if __name__ == "__main__":
    main()
