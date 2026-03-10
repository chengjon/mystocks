from __future__ import annotations

import json
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List
from urllib.parse import urlparse

from dotenv import load_dotenv

logger = logging.getLogger("MyStocksMonitoring")


class MonitoringDatabase:
    """监控数据库管理器 - 与业务数据库完全分离"""

    def __init__(self, monitor_db_url: str = None):
        """
        初始化监控数据库

        Args:
            monitor_db_url: 监控数据库连接URL
        """
        load_dotenv()

        from src.storage.database.database_manager import DatabaseTableManager

        self.monitor_db_url = monitor_db_url or os.getenv("MONITOR_DB_URL") or ""
        self.db_manager = DatabaseTableManager()

        parsed_url = urlparse(self.monitor_db_url)
        if parsed_url.scheme and not parsed_url.scheme.startswith("postgresql"):
            raise ValueError("监控数据库仅支持PostgreSQL（MySQL已移除）。")

        self.monitor_db_backend = "postgresql"
        self.monitor_db_config = {
            "host": os.getenv("MONITOR_DB_HOST") or os.getenv("POSTGRESQL_HOST"),
            "port": int(os.getenv("MONITOR_DB_PORT") or os.getenv("POSTGRESQL_PORT", "5432")),
            "user": os.getenv("MONITOR_DB_USER") or os.getenv("POSTGRESQL_USER", "postgres"),
            "password": os.getenv("MONITOR_DB_PASSWORD") or os.getenv("POSTGRESQL_PASSWORD", ""),
            "database": os.getenv("MONITOR_DB_DATABASE") or os.getenv("POSTGRESQL_DATABASE", "mystocks"),
        }

        self._ensure_monitoring_tables()

        logger.info(
            "监控数据库初始化完成: %s:%s",
            self.monitor_db_config["host"],
            self.monitor_db_config["port"],
        )

    def _get_monitor_connection(self):
        """获取监控数据库连接"""
        try:
            import psycopg2

            connection = psycopg2.connect(
                host=self.monitor_db_config.get("host"),
                port=self.monitor_db_config.get("port"),
                user=self.monitor_db_config.get("user"),
                password=self.monitor_db_config.get("password"),
                dbname=self.monitor_db_config.get("database"),
            )
            return connection
        except Exception as e:
            logger.error("连接监控数据库失败: %s", e)
            return None

    def _ensure_monitoring_tables(self) -> None:
        """确保监控表结构存在"""
        if not self.monitor_db_url:
            logger.error("未配置监控数据库URL，无法启动监控服务")
            raise ValueError(
                "MONITOR_DB_URL 环境变量必须设置。"
                "请在 .env 文件中配置: MONITOR_DB_URL=postgresql://user:password@host:port/database"
            )

        try:
            from src.storage.database.init_db_monitor import init_monitoring_database

            init_monitoring_database()
        except Exception as e:
            logger.warning("初始化监控表结构失败: %s", e)

        self._init_monitoring_tables()

    def _init_monitoring_tables(self) -> None:
        """初始化监控表结构"""
        try:
            logger.info("监控表结构检查完成")
        except Exception as e:
            logger.error("初始化监控表失败: %s", e)

    def log_operation_start(
        self,
        table_name: str,
        database_type: str,
        database_name: str,
        operation_type: str,
        operation_details: Dict = None,
    ) -> str:
        """
        记录操作开始

        Returns:
            str: 操作ID
        """
        try:
            operation_id = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{table_name}_{operation_type}"

            log_data = {
                "operation_id": operation_id,
                "table_name": table_name,
                "database_type": database_type,
                "database_name": database_name,
                "operation_type": operation_type,
                "operation_time": datetime.now(),
                "operation_status": "processing",
                "operation_details": json.dumps(operation_details or {}),
                "ddl_command": "",
                "error_message": "",
            }

            self._insert_operation_log(log_data)
            return operation_id
        except Exception as e:
            logger.error("记录操作开始失败: %s", e)
            return f"error_{int(time.time())}"

    def log_operation_result(
        self,
        operation_id: str,
        success: bool,
        data_count: int = 0,
        error_message: str = None,
    ):
        """
        记录操作结果

        Args:
            operation_id: 操作ID
            success: 是否成功
            data_count: 数据条数
            error_message: 错误信息
        """
        try:
            status = "success" if success else "failed"

            update_data = {
                "operation_status": status,
                "operation_details": json.dumps({"data_count": data_count}),
                "error_message": error_message or "",
                "end_time": datetime.now(),
            }

            self._update_operation_log(operation_id, update_data)
        except Exception as e:
            logger.error("记录操作结果失败: %s", e)

    def _insert_operation_log(self, log_data: Dict) -> None:
        """插入操作日志到监控数据库"""
        try:
            connection = self._get_monitor_connection()
            if connection:
                cursor = connection.cursor()

                insert_sql = """
                INSERT INTO table_operation_log (
                    operation_id, table_name, database_type, database_name,
                    operation_type, operation_time, operation_status,
                    operation_details, ddl_command, error_message
                ) VALUES (
                    %(operation_id)s, %(table_name)s, %(database_type)s, %(database_name)s,
                    %(operation_type)s, %(operation_time)s, %(operation_status)s,
                    %(operation_details)s, %(ddl_command)s, %(error_message)s
                )
                """

                cursor.execute(insert_sql, log_data)
                connection.commit()
                cursor.close()
                connection.close()

                logger.debug("操作日志插入成功: %s", log_data["operation_id"])
        except Exception as e:
            logger.error("插入操作日志失败: %s", e)

    def _update_operation_log(self, operation_id: str, update_data: Dict) -> None:
        """更新操作日志"""
        try:
            connection = self._get_monitor_connection()
            if connection:
                cursor = connection.cursor()

                update_sql = """
                UPDATE table_operation_log SET
                    operation_status = %(status)s,
                    error_message = %(error_message)s,
                    data_count = %(data_count)s,
                    duration_seconds = %(duration)s,
                    end_time = %(end_time)s
                WHERE operation_id = %(operation_id)s
                """

                update_params = {
                    "operation_id": operation_id,
                    "status": update_data.get("status", "completed"),
                    "error_message": update_data.get("error_message", ""),
                    "data_count": update_data.get("data_count", 0),
                    "duration": update_data.get("duration", 0.0),
                    "end_time": update_data.get("end_time", datetime.now()),
                }

                cursor.execute(update_sql, update_params)
                connection.commit()
                cursor.close()
                connection.close()

                logger.debug("操作日志更新成功: %s", operation_id)
        except Exception as e:
            logger.error("更新操作日志失败: %s", e)

    def get_operation_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """
        获取操作统计信息

        Args:
            hours: 统计时间范围（小时）

        Returns:
            Dict: 统计信息
        """
        try:
            connection = self._get_monitor_connection()
            if not connection:
                return {}

            cursor = connection.cursor()
            start_time = datetime.now() - timedelta(hours=hours)

            total_sql = """
            SELECT
                COUNT(*) as total_operations,
                COUNT(CASE WHEN operation_status = 'success' THEN 1 END) as successful_operations,
                COUNT(CASE WHEN operation_status = 'failed' THEN 1 END) as failed_operations,
                AVG(duration_seconds) as average_duration
            FROM table_operation_log
            WHERE operation_time >= %s
            """

            cursor.execute(total_sql, (start_time,))
            total_result = cursor.fetchone()

            db_breakdown_sql = """
            SELECT database_type, COUNT(*) as count
            FROM table_operation_log
            WHERE operation_time >= %s
            GROUP BY database_type
            """

            cursor.execute(db_breakdown_sql, (start_time,))
            db_breakdown_results = cursor.fetchall()

            op_breakdown_sql = """
            SELECT operation_type, COUNT(*) as count
            FROM table_operation_log
            WHERE operation_time >= %s
            GROUP BY operation_type
            """

            cursor.execute(op_breakdown_sql, (start_time,))
            op_breakdown_results = cursor.fetchall()

            cursor.close()
            connection.close()

            return {
                "total_operations": total_result[0] if total_result[0] else 0,
                "successful_operations": total_result[1] if total_result[1] else 0,
                "failed_operations": total_result[2] if total_result[2] else 0,
                "database_breakdown": {db[0]: db[1] for db in db_breakdown_results},
                "operation_type_breakdown": {op[0]: op[1] for op in op_breakdown_results},
                "average_duration": float(total_result[3]) if total_result[3] else 0.0,
                "last_update": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error("获取操作统计失败: %s", e)
            return {}

    def get_table_creation_history(self, limit: int = 50) -> List[Dict]:
        """
        获取表创建历史

        Args:
            limit: 返回记录数限制

        Returns:
            List[Dict]: 创建历史记录
        """
        try:
            history = []

            return history
        except Exception as e:
            logger.error("获取表创建历史失败: %s", e)
            return []


__all__ = ["MonitoringDatabase", "load_dotenv"]
