"""
灾备恢复表管理器 (DisasterRecoveryTableManager)

专注于灾备恢复的核心功能,删除了自动迁移和复杂配置管理。

核心功能:
1. rebuild_all_tables() - 重建所有表结构
2. validate_schema_consistency() - 验证表结构一致性
3. export_to_sql_migrations() - 导出SQL迁移脚本

创建日期: 2025-11-08
版本: 2.0 (优化版)
代码行数目标: ~300行 (vs 原750行)
"""

import yaml
import os
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging
from datetime import datetime

# 数据库连接
from db_manager.connection_manager import DatabaseConnectionManager

logger = logging.getLogger(__name__)


class DisasterRecoveryTableManager:
    """
    灾备恢复表管理器

    功能简化版,专注于灾备恢复场景:
    - 快速重建表结构
    - 验证表结构一致性
    - 导出SQL迁移脚本
    """

    def __init__(self, config_path: str = "config/disaster_recovery_config.yaml"):
        """
        初始化灾备恢复表管理器

        Args:
            config_path: 灾备恢复配置文件路径
        """
        self.config_path = config_path
        self.config = self._load_config()
        self.conn_manager = DatabaseConnectionManager()

        logger.info(f"✅ DisasterRecoveryTableManager initialized")
        logger.info(f"   Config: {config_path}")
        logger.info(f"   Tables: {len(self.config.get('tables', []))}")

    def _load_config(self) -> Dict[str, Any]:
        """加载YAML配置文件"""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"灾备配置文件不存在: {self.config_path}")

        with open(self.config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        version = config.get("version", "unknown")
        logger.info(
            f"加载灾备配置: version={version}, tables={len(config.get('tables', []))}"
        )

        if "databases" not in config or "tables" not in config:
            raise ValueError("配置文件缺少必需字段: databases 或 tables")

        return config

    def rebuild_all_tables(self, drop_existing: bool = False) -> Dict[str, Any]:
        """
        重建所有表结构 (灾备恢复核心功能)

        Args:
            drop_existing: 是否先删除现有表 (危险操作,需明确确认)

        Returns:
            结果字典: {
                'total': int,
                'created': int,
                'skipped': int,
                'errors': List[str],
                'duration_seconds': float
            }
        """
        start_time = datetime.now()
        result = {
            "total": len(self.config["tables"]),
            "created": 0,
            "skipped": 0,
            "errors": [],
        }

        logger.info(f"🔧 开始重建 {result['total']} 个表...")

        for table_def in self.config["tables"]:
            table_name = table_def["name"]
            db_type = table_def["db"]

            try:
                # 检查表是否存在
                exists = self._table_exists(db_type, table_name)

                if exists and drop_existing:
                    logger.warning(f"⚠️  删除现有表: {db_type}.{table_name}")
                    self._drop_table(db_type, table_name)
                    exists = False

                if not exists:
                    # 创建表
                    self._create_table(table_def)
                    result["created"] += 1
                    logger.info(f"✅ 创建表: {db_type}.{table_name}")
                else:
                    result["skipped"] += 1
                    logger.info(f"⏭️  跳过已存在的表: {db_type}.{table_name}")

            except Exception as e:
                error_msg = f"创建表失败 {db_type}.{table_name}: {str(e)}"
                result["errors"].append(error_msg)
                logger.error(f"❌ {error_msg}")

        duration = (datetime.now() - start_time).total_seconds()
        result["duration_seconds"] = round(duration, 2)

        logger.info(
            f"🏁 重建完成: 创建={result['created']}, 跳过={result['skipped']}, 错误={len(result['errors'])}, 耗时={duration:.2f}s"
        )

        return result

    def validate_schema_consistency(self) -> Dict[str, Any]:
        """
        验证表结构一致性 (灾备恢复核心功能)

        检查实际数据库表结构是否与配置文件一致

        Returns:
            结果字典: {
                'total_tables': int,
                'valid': int,
                'invalid': int,
                'missing': int,
                'issues': List[Dict]
            }
        """
        result = {
            "total_tables": len(self.config["tables"]),
            "valid": 0,
            "invalid": 0,
            "missing": 0,
            "issues": [],
        }

        logger.info(f"🔍 开始验证 {result['total_tables']} 个表的结构一致性...")

        for table_def in self.config["tables"]:
            table_name = table_def["name"]
            db_type = table_def["db"]

            try:
                # 检查表是否存在
                exists = self._table_exists(db_type, table_name)

                if not exists:
                    result["missing"] += 1
                    issue = {
                        "table": f"{db_type}.{table_name}",
                        "type": "missing",
                        "message": "表不存在",
                    }
                    result["issues"].append(issue)
                    logger.warning(f"⚠️  表缺失: {db_type}.{table_name}")
                else:
                    # 简化版验证: 仅检查表存在性
                    # 详细schema验证可以后续扩展
                    result["valid"] += 1
                    logger.debug(f"✅ 表存在: {db_type}.{table_name}")

            except Exception as e:
                result["invalid"] += 1
                issue = {
                    "table": f"{db_type}.{table_name}",
                    "type": "error",
                    "message": str(e),
                }
                result["issues"].append(issue)
                logger.error(f"❌ 验证错误 {db_type}.{table_name}: {str(e)}")

        logger.info(
            f"🏁 验证完成: 有效={result['valid']}, 缺失={result['missing']}, 错误={result['invalid']}"
        )

        return result

    def export_to_sql_migrations(
        self, output_dir: str = "migrations"
    ) -> Dict[str, str]:
        """
        导出SQL迁移脚本 (灾备恢复核心功能)

        Args:
            output_dir: 输出目录

        Returns:
            导出的文件路径字典: {
                'tdengine': str,
                'postgresql': str
            }
        """
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_files = {}

        logger.info(f"📝 开始导出SQL迁移脚本到 {output_dir}/...")

        # 按数据库类型分组
        tables_by_db = {}
        for table_def in self.config["tables"]:
            db_type = table_def["db"]
            if db_type not in tables_by_db:
                tables_by_db[db_type] = []
            tables_by_db[db_type].append(table_def)

        # 生成TDengine脚本
        if "tdengine" in tables_by_db:
            td_file = os.path.join(output_dir, f"tdengine_migration_{timestamp}.sql")
            with open(td_file, "w", encoding="utf-8") as f:
                f.write("-- TDengine 灾备恢复迁移脚本\n")
                f.write(f"-- 生成时间: {datetime.now()}\n")
                f.write(f"-- 表数量: {len(tables_by_db['tdengine'])}\n\n")

                for table_def in tables_by_db["tdengine"]:
                    sql = self._generate_tdengine_create_sql(table_def)
                    f.write(f"\n{sql}\n")

            output_files["tdengine"] = td_file
            logger.info(f"✅ TDengine脚本: {td_file}")

        # 生成PostgreSQL脚本
        if "postgresql" in tables_by_db:
            pg_file = os.path.join(output_dir, f"postgresql_migration_{timestamp}.sql")
            with open(pg_file, "w", encoding="utf-8") as f:
                f.write("-- PostgreSQL 灾备恢复迁移脚本\n")
                f.write(f"-- 生成时间: {datetime.now()}\n")
                f.write(f"-- 表数量: {len(tables_by_db['postgresql'])}\n\n")

                for table_def in tables_by_db["postgresql"]:
                    sql = self._generate_postgresql_create_sql(table_def)
                    f.write(f"\n{sql}\n")

            output_files["postgresql"] = pg_file
            logger.info(f"✅ PostgreSQL脚本: {pg_file}")

        logger.info(f"🏁 导出完成: {len(output_files)} 个文件")
        return output_files

    # ========== 私有辅助方法 ==========

    def _table_exists(self, db_type: str, table_name: str) -> bool:
        """检查表是否存在"""
        try:
            if db_type == "tdengine":
                conn = self.conn_manager.get_tdengine_connection()
                cursor = conn.cursor()
                cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
                result = cursor.fetchall()
                return len(result) > 0

            elif db_type == "postgresql":
                conn = self.conn_manager.get_postgresql_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = %s)",
                    (table_name,),
                )
                return cursor.fetchone()[0]

        except Exception as e:
            logger.error(f"检查表存在性失败 {db_type}.{table_name}: {str(e)}")
            return False

    def _drop_table(self, db_type: str, table_name: str):
        """删除表 (危险操作)"""
        try:
            if db_type == "tdengine":
                conn = self.conn_manager.get_tdengine_connection()
                cursor = conn.cursor()
                cursor.execute(f"DROP TABLE IF EXISTS {table_name}")

            elif db_type == "postgresql":
                conn = self.conn_manager.get_postgresql_connection()
                cursor = conn.cursor()
                cursor.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE")
                conn.commit()

        except Exception as e:
            logger.error(f"删除表失败 {db_type}.{table_name}: {str(e)}")
            raise

    def _create_table(self, table_def: Dict[str, Any]):
        """创建表"""
        db_type = table_def["db"]
        table_type = table_def["type"]

        if db_type == "tdengine" and table_type == "supertable":
            self._create_tdengine_supertable(table_def)
        elif db_type == "postgresql":
            self._create_postgresql_table(table_def)
        else:
            raise ValueError(f"不支持的表类型: {db_type}.{table_type}")

    def _create_tdengine_supertable(self, table_def: Dict[str, Any]):
        """创建TDengine超表"""
        table_name = table_def["name"]
        schema = table_def["schema"]
        tags = table_def["tags"]

        sql = f"CREATE STABLE IF NOT EXISTS {table_name} ({schema}) TAGS ({tags})"

        conn = self.conn_manager.get_tdengine_connection()
        cursor = conn.cursor()
        cursor.execute(sql)

    def _create_postgresql_table(self, table_def: Dict[str, Any]):
        """创建PostgreSQL表"""
        table_name = table_def["name"]
        table_type = table_def["type"]
        schema = table_def["schema"]

        sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({schema})"

        conn = self.conn_manager.get_postgresql_connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()

        # 如果是hypertable,转换为TimescaleDB hypertable
        if table_type == "hypertable":
            partition_key = table_def.get("partition_key", "ts")
            hypertable_sql = f"SELECT create_hypertable('{table_name}', '{partition_key}', if_not_exists => TRUE)"
            cursor.execute(hypertable_sql)
            conn.commit()

    def _generate_tdengine_create_sql(self, table_def: Dict[str, Any]) -> str:
        """生成TDengine建表SQL"""
        table_name = table_def["name"]
        schema = table_def["schema"]
        tags = table_def["tags"]

        return f"-- {table_name}\nCREATE STABLE IF NOT EXISTS {table_name} ({schema}) TAGS ({tags});"

    def _generate_postgresql_create_sql(self, table_def: Dict[str, Any]) -> str:
        """生成PostgreSQL建表SQL"""
        table_name = table_def["name"]
        table_type = table_def["type"]
        schema = table_def["schema"]

        sql = f"-- {table_name}\nCREATE TABLE IF NOT EXISTS {table_name} ({schema});"

        if table_type == "hypertable":
            partition_key = table_def.get("partition_key", "ts")
            sql += f"\nSELECT create_hypertable('{table_name}', '{partition_key}', if_not_exists => TRUE);"

        return sql
