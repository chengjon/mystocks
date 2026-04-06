"""
# 功能：监控数据库模块，独立记录所有操作日志和指标
# 作者：JohnC (ninjas@sina.com) & Claude
# 创建日期：2025-10-16
# 版本：2.1.0
# 依赖：详见requirements.txt或文件导入部分
# 注意事项：
#   本文件是MyStocks v2.1核心组件，遵循5-tier数据分类架构
# 版权：MyStocks Project © 2025
"""

import json
import logging
import uuid
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from src.storage.database.connection_manager import DatabaseConnectionManager

logger = logging.getLogger(__name__)


class MonitoringDatabaseCoreMixin:
    """MonitoringDatabase 方法集 Part 1"""

    def __init__(self, enable_monitoring: bool = True):
        """
        初始化监控数据库

        Args:
            enable_monitoring: 是否启用监控 (默认True)
        """
        self.enable_monitoring = enable_monitoring
        self.conn_manager = DatabaseConnectionManager()
        self._write_failures = 0
        self._total_writes = 0

        logger.info("✅ MonitoringDatabase initialized (enabled=%s)", enable_monitoring)

    @contextmanager
    def _get_connection(self):
        """获取监控数据库连接的上下文管理器"""
        pool = None
        conn = None
        try:
            pool = self.conn_manager.get_postgresql_connection()
            conn = pool.getconn()
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error("监控数据库连接错误: %s", e)
            raise
        finally:
            if conn and pool:
                pool.putconn(conn)

    def log_operation(
        self,
        operation_type: str,
        classification: str,
        target_database: str,
        table_name: Optional[str] = None,
        record_count: int = 0,
        operation_status: str = "SUCCESS",
        error_message: Optional[str] = None,
        execution_time_ms: Optional[int] = None,
        user_agent: Optional[str] = None,
        client_ip: Optional[str] = None,
        additional_info: Optional[Dict] = None,
    ) -> bool:
        """
        记录操作日志

        Args:
            operation_type: 操作类型 (SAVE/LOAD/DELETE/UPDATE)
            classification: 数据分类
            target_database: 目标数据库 (TDengine/PostgreSQL/Redis)
            table_name: 目标表名
            record_count: 影响记录数
            operation_status: 状态 (SUCCESS/FAILED/PARTIAL)
            error_message: 错误信息 (失败时)
            execution_time_ms: 执行时间(毫秒)
            user_agent: 调用来源
            client_ip: 客户端IP
            additional_info: 额外信息 (字典,会转为JSONB)

        Returns:
            bool: 记录是否成功
        """
        if not self.enable_monitoring:
            return True

        self._total_writes += 1

        try:
            operation_id = str(uuid.uuid4())

            with self._get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    INSERT INTO operation_logs (
                        operation_id, operation_type, classification,
                        target_database, table_name, record_count,
                        operation_status, error_message, execution_time_ms,
                        user_agent, client_ip, additional_info
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """,
                    (
                        operation_id,
                        operation_type,
                        classification,
                        target_database,
                        table_name,
                        record_count,
                        operation_status,
                        error_message,
                        execution_time_ms,
                        user_agent,
                        client_ip,
                        json.dumps(additional_info) if additional_info else None,
                    ),
                )

                cursor.close()

            return True

        except Exception as e:
            self._write_failures += 1
            logger.warning("记录操作日志失败 (降级到本地日志): %s", e)
            logger.info(
                "操作日志: %s %s -> %s.%s (%s records, %s, %sms)",
                operation_type,
                classification,
                target_database,
                table_name,
                record_count,
                operation_status,
                execution_time_ms,
            )
            return False

    def record_performance_metric(
        self,
        metric_name: str,
        metric_value: float,
        metric_type: str = "QUERY_TIME",
        metric_unit: str = "ms",
        classification: Optional[str] = None,
        database_type: Optional[str] = None,
        table_name: Optional[str] = None,
        is_slow_query: bool = False,
        query_sql: Optional[str] = None,
        execution_plan: Optional[str] = None,
        tags: Optional[Dict] = None,
    ) -> bool:
        """
        记录性能指标

        Args:
            metric_name: 指标名称
            metric_value: 指标值
            metric_type: 指标类型 (QUERY_TIME/CONNECTION_TIME/BATCH_SIZE)
            metric_unit: 单位 (ms/seconds/count)
            classification: 关联数据分类
            database_type: 关联数据库类型
            table_name: 关联表名
            is_slow_query: 是否慢查询 (>5秒)
            query_sql: SQL语句 (慢查询时记录)
            execution_plan: 执行计划
            tags: 标签 (字典)

        Returns:
            bool: 记录是否成功
        """
        if not self.enable_monitoring:
            return True

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    INSERT INTO performance_metrics (
                        metric_name, metric_type, metric_value, metric_unit,
                        classification, database_type, table_name,
                        is_slow_query, query_sql, execution_plan, tags
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """,
                    (
                        metric_name,
                        metric_type,
                        metric_value,
                        metric_unit,
                        classification,
                        database_type,
                        table_name,
                        is_slow_query,
                        query_sql,
                        execution_plan,
                        json.dumps(tags) if tags else None,
                    ),
                )

                cursor.close()

            return True

        except Exception as e:
            logger.warning("记录性能指标失败: %s", e)
            return False

    def log_quality_check(
        self,
        check_type: str,
        classification: str,
        database_type: str,
        table_name: str,
        check_status: str,
        total_records: Optional[int] = None,
        null_records: Optional[int] = None,
        missing_rate: Optional[float] = None,
        latest_timestamp: Optional[datetime] = None,
        data_delay_seconds: Optional[int] = None,
        invalid_records: Optional[int] = None,
        validation_rules: Optional[str] = None,
        check_message: Optional[str] = None,
        threshold_config: Optional[Dict] = None,
        check_duration_ms: Optional[int] = None,
    ) -> bool:
        """
        记录数据质量检查

        Args:
            check_type: 检查类型 (COMPLETENESS/FRESHNESS/ACCURACY)
            classification: 数据分类
            database_type: 数据库类型
            table_name: 表名
            check_status: 检查状态 (PASS/FAIL/WARNING)
            total_records: 总记录数
            null_records: 空值记录数
            missing_rate: 缺失率 (%)
            latest_timestamp: 最新时间戳
            data_delay_seconds: 数据延迟(秒)
            invalid_records: 无效记录数
            validation_rules: 验证规则
            check_message: 检查信息
            threshold_config: 阈值配置
            check_duration_ms: 检查耗时(毫秒)

        Returns:
            bool: 记录是否成功
        """
        if not self.enable_monitoring:
            return True

        try:
            check_id = str(uuid.uuid4())

            with self._get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    INSERT INTO data_quality_checks (
                        check_id, check_type, classification, database_type,
                        table_name, check_status, total_records, null_records,
                        missing_rate, latest_timestamp, data_delay_seconds,
                        invalid_records, validation_rules, check_message,
                        threshold_config, check_duration_ms
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """,
                    (
                        check_id,
                        check_type,
                        classification,
                        database_type,
                        table_name,
                        check_status,
                        total_records,
                        null_records,
                        missing_rate,
                        latest_timestamp,
                        data_delay_seconds,
                        invalid_records,
                        validation_rules,
                        check_message,
                        json.dumps(threshold_config) if threshold_config else None,
                        check_duration_ms,
                    ),
                )

                cursor.close()

            return True

        except Exception as e:
            logger.warning("记录质量检查失败: %s", e)
            return False

    def create_alert(
        self,
        alert_level: str,
        alert_type: str,
        alert_title: str,
        alert_message: str,
        source: Optional[str] = None,
        classification: Optional[str] = None,
        database_type: Optional[str] = None,
        table_name: Optional[str] = None,
        additional_data: Optional[Dict] = None,
        notification_channels: Optional[List[str]] = None,
    ) -> Optional[str]:
        """
        创建告警

        Args:
            alert_level: 告警级别 (CRITICAL/WARNING/INFO)
            alert_type: 告警类型 (SLOW_QUERY/DATA_QUALITY/SYSTEM_ERROR)
            alert_title: 告警标题
            alert_message: 告警详细信息
            source: 告警来源 (模块名称)
            classification: 关联数据分类
            database_type: 关联数据库类型
            table_name: 关联表名
            additional_data: 额外数据
            notification_channels: 通知渠道 ['email', 'webhook', 'log']

        Returns:
            str: 告警ID (失败返回None)
        """
        if not self.enable_monitoring:
            return None

        try:
            alert_id = str(uuid.uuid4())
            now = datetime.now()

            with self._get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    INSERT INTO alert_records (
                        alert_id, alert_level, alert_type, alert_title,
                        alert_message, source, classification, database_type,
                        table_name, first_occurred_at, last_occurred_at,
                        notification_channels, additional_data
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """,
                    (
                        alert_id,
                        alert_level,
                        alert_type,
                        alert_title,
                        alert_message,
                        source,
                        classification,
                        database_type,
                        table_name,
                        now,
                        now,
                        notification_channels,
                        json.dumps(additional_data) if additional_data else None,
                    ),
                )

                cursor.close()

            logger.warning("🚨 告警创建: [%s] %s", alert_level, alert_title)
            return alert_id

        except Exception as e:
            logger.error("创建告警失败: %s", e)
            logger.warning("告警内容: [%s] %s - %s", alert_level, alert_title, alert_message)
            return None

    def update_alert_status(
        self,
        alert_id: str,
        alert_status: str,
        operator: str,
        resolution_notes: Optional[str] = None,
    ) -> bool:
        """
        更新告警状态

        Args:
            alert_id: 告警ID
            alert_status: 新状态 (ACKNOWLEDGED/RESOLVED)
            operator: 操作人
            resolution_notes: 解决说明

        Returns:
            bool: 更新是否成功
        """
        if not self.enable_monitoring:
            return True

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                if alert_status == "ACKNOWLEDGED":
                    cursor.execute(
                        """
                        UPDATE alert_records
                        SET alert_status = %s,
                            acknowledged_by = %s,
                            acknowledged_at = CURRENT_TIMESTAMP,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE alert_id = %s
                    """,
                        (alert_status, operator, alert_id),
                    )

                elif alert_status == "RESOLVED":
                    cursor.execute(
                        """
                        UPDATE alert_records
                        SET alert_status = %s,
                            resolved_by = %s,
                            resolved_at = CURRENT_TIMESTAMP,
                            resolution_notes = %s,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE alert_id = %s
                    """,
                        (alert_status, operator, resolution_notes, alert_id),
                    )

                cursor.close()

            return True

        except Exception as e:
            logger.error("更新告警状态失败: %s", e)
            return False

    def get_slow_query_count(self, hours: int = 24) -> int:
        """
        获取慢查询数量

        Args:
            hours: 统计时间范围（小时）

        Returns:
            int: 慢查询数量
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                cutoff_time = datetime.now() - timedelta(hours=hours)

                # 查询性能指标表中的慢查询（假设执行时间超过阈值的查询为慢查询）
                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM performance_metrics
                    WHERE metric_name LIKE '%query%'
                    AND metric_value > 1000  -- 假设超过1秒的查询为慢查询
                    AND created_at > %s
                """,
                    (cutoff_time,),
                )

                result = cursor.fetchone()
                count = result[0] if result else 0
                cursor.close()

                return count
        except Exception as e:
            logger.warning("查询慢查询数量失败: %s", e)
            return 0

    def get_average_query_time(self, hours: int = 24) -> float:
        """
        获取平均查询时间

        Args:
            hours: 统计时间范围（小时）

        Returns:
            float: 平均查询时间（毫秒）
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                cutoff_time = datetime.now() - timedelta(hours=hours)

                # 查询性能指标表中的平均查询时间
                cursor.execute(
                    """
                    SELECT AVG(metric_value)
                    FROM performance_metrics
                    WHERE metric_name LIKE '%query%'
                    AND metric_type = 'QUERY_TIME'
                    AND created_at > %s
                """,
                    (cutoff_time,),
                )

                result = cursor.fetchone()
                avg_time = result[0] if result and result[0] else 0.0
                cursor.close()

                return float(avg_time)
        except Exception as e:
            logger.warning("查询平均查询时间失败: %s", e)
            return 0.0

    def get_max_query_time(self, hours: int = 24) -> float:
        """
        获取最大查询时间

        Args:
            hours: 统计时间范围（小时）

        Returns:
            float: 最大查询时间（毫秒）
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                cutoff_time = datetime.now() - timedelta(hours=hours)

                # 查询性能指标表中的最大查询时间
                cursor.execute(
                    """
                    SELECT MAX(metric_value)
                    FROM performance_metrics
                    WHERE metric_name LIKE '%query%'
                    AND metric_type = 'QUERY_TIME'
                    AND created_at > %s
                """,
                    (cutoff_time,),
                )

                result = cursor.fetchone()
                max_time = result[0] if result and result[0] else 0.0
                cursor.close()

                return float(max_time)
        except Exception as e:
            logger.warning("查询最大查询时间失败: %s", e)
            return 0.0

    def get_total_query_count(self, hours: int = 24) -> int:
        """
        获取总查询数量

        Args:
            hours: 统计时间范围（小时）

        Returns:
            int: 总查询数量
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                cutoff_time = datetime.now() - timedelta(hours=hours)

                # 查询性能指标表中的查询总数
                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM performance_metrics
                    WHERE metric_name LIKE '%query%'
                    AND metric_type = 'QUERY_TIME'
                    AND created_at > %s
                """,
                    (cutoff_time,),
                )

                result = cursor.fetchone()
                count = result[0] if result else 0
                cursor.close()

                return count
        except Exception as e:
            logger.warning("查询总查询数量失败: %s", e)
            return 0

    def get_statistics(self) -> Dict[str, Any]:
        """
        获取监控统计信息

        Returns:
            dict: 统计信息
        """
        stats = {
            "total_writes": self._total_writes,
            "write_failures": self._write_failures,
            "write_success_rate": 0.0,
        }

        if self._total_writes > 0:
            stats["write_success_rate"] = (self._total_writes - self._write_failures) / self._total_writes * 100

        return stats
