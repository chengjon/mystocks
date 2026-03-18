"""
# 功能：数据库表管理 DDL 与信息查询方法集
"""

import logging
from typing import Dict, List, Optional

from .._build_monitor_db_url import DatabaseType

logger = logging.getLogger("DatabaseTableManager")


class DatabaseTableManagerDDLInfoMixin:
    """DatabaseTableManager 方法集 Part 3"""

    def _generate_alter_ddl(self, db_type: DatabaseType, table_name: str, alterations: List[Dict]) -> str:
        """生成ALTER TABLE语句"""
        ddl_parts = []

        for alteration in alterations:
            operation = alteration.get("operation")

            if operation == "ADD":
                col_def = self._generate_column_definition(alteration)
                ddl_parts.append(f"ADD COLUMN {col_def}")
            elif operation == "DROP":
                ddl_parts.append(f"DROP COLUMN {alteration['column_name']}")
            elif operation == "MODIFY":
                col_def = self._generate_column_definition(alteration)
                ddl_parts.append(f"MODIFY COLUMN {col_def}")
            elif operation == "RENAME":
                ddl_parts.append(f"RENAME COLUMN {alteration['old_name']} TO {alteration['new_name']}")

        return f"ALTER TABLE {table_name} {', '.join(ddl_parts)}"

    def _generate_column_definition(self, col_def: Dict) -> str:
        """生成列定义字符串"""
        definition = f"{col_def['name']} {col_def['type']}"

        if col_def.get("length") and col_def["type"].lower() in ["varchar", "char"]:
            definition += f"({col_def['length']})"
        elif col_def.get("precision") and col_def["type"].lower() in ["numeric", "decimal"]:
            if col_def.get("scale"):
                definition += f"({col_def['precision']}, {col_def['scale']})"
            else:
                definition += f"({col_def['precision']})"

        if not col_def.get("nullable", True):
            definition += " NOT NULL"
        if col_def.get("default") is not None:
            definition += f" DEFAULT {col_def['default']}"
        if col_def.get("comment"):
            definition += f" COMMENT '{col_def['comment']}'"

        return definition

    def _generate_tdengine_ddl(self, table_name: str, columns: List[Dict], tags: List[Dict], **kwargs) -> str:
        """生成TDengine的DDL语句"""
        normal_cols = [col for col in columns if not col.get("is_tag", False)]
        tag_cols = [col for col in columns if col.get("is_tag", False)]

        if not tags and tag_cols:
            tags = tag_cols

        col_defs = []
        for col in normal_cols:
            col_def = f"{col['name']} {col['type']}"
            if col.get("length"):
                col_def += f"({col['length']})"
            col_defs.append(col_def)

        tag_defs = []
        for tag in tags:
            tag_def = f"{tag['name']} {tag['type']}"
            if tag.get("length"):
                tag_def += f"({tag['length']})"
            tag_defs.append(tag_def)

        if kwargs.get("is_super_table", False):
            return f"CREATE STABLE IF NOT EXISTS {table_name} ({', '.join(col_defs)}) TAGS ({', '.join(tag_defs)})"

        return f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(col_defs + tag_defs)})"

    def _generate_postgresql_ddl(self, table_name: str, columns: List[Dict], **kwargs) -> str:
        """生成PostgreSQL的DDL语句"""
        col_defs = []
        primary_keys = []

        for col in columns:
            col_def = f"{col['name']} {col['type']}"

            if col.get("length") and col["type"].lower() in ["varchar", "char"]:
                col_def += f"({col['length']})"
            elif col.get("precision") and col["type"].lower() in ["numeric", "decimal"]:
                if col.get("scale"):
                    col_def += f"({col['precision']}, {col['scale']})"
                else:
                    col_def += f"({col['precision']})"

            if not col.get("nullable", True):
                col_def += " NOT NULL"
            if col.get("primary_key", False):
                primary_keys.append(col["name"])
            if col.get("default") is not None:
                col_def += f" DEFAULT {col['default']}"

            col_defs.append(col_def)

        if primary_keys:
            col_defs.append(f"PRIMARY KEY ({', '.join(primary_keys)})")

        ddl = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(col_defs)})"

        if kwargs.get("is_timescale_hypertable", False):
            time_column = kwargs.get("time_column", "ts")
            ddl += f"; SELECT create_hypertable('{table_name}', '{time_column}')"

        return ddl

    def _initialize_redis_structure(self, conn, key_prefix: str, columns: List[Dict]):
        """初始化Redis数据结构"""
        template_key = f"{key_prefix}:template"
        template_data = {}

        for col in columns:
            default_value = col.get("default", "")
            if default_value is None:
                default_value = ""
            template_data[col["name"]] = str(default_value)

        conn.hmset(template_key, template_data)
        index_key = f"{key_prefix}:index"
        conn.sadd(index_key, template_key)

    def get_table_info(self, db_type: DatabaseType, db_name: str, table_name: str, **kwargs) -> Optional[Dict]:
        """获取表结构信息"""
        try:
            conn = self.get_connection(db_type, db_name, **kwargs)
            cursor = conn.cursor()
            columns = []

            if db_type == DatabaseType.TDENGINE:
                cursor.execute(f"DESCRIBE {table_name}")
                result = cursor.fetchall()
                for row in result:
                    columns.append({"name": row[0], "type": row[1], "length": row[2], "nullable": row[4] == "YES"})
            elif db_type == DatabaseType.POSTGRESQL:
                cursor.execute(
                    f"""
                    SELECT column_name, data_type, is_nullable, column_default,
                           character_maximum_length, numeric_precision, numeric_scale
                    FROM information_schema.columns
                    WHERE table_name = '{table_name}'
                    ORDER BY ordinal_position
                """
                )
                result = cursor.fetchall()
                for row in result:
                    columns.append(
                        {
                            "name": row[0],
                            "type": row[1],
                            "nullable": row[2] == "YES",
                            "default": row[3],
                            "length": row[4],
                            "precision": row[5],
                            "scale": row[6],
                        }
                    )
            else:
                return None

            return {"table_name": table_name, "columns": columns}

        except Exception as error:
            logger.error("Failed to get table info for %s: %s", table_name, str(error))
            return None
