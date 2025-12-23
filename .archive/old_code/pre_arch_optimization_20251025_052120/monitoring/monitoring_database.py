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

import uuid
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from contextlib import contextmanager

from db_manager.connection_manager import DatabaseConnectionManager

logger = logging.getLogger(__name__)


class MonitoringDatabase:
    """
    监控数据库访问类

    负责将所有监控数据写入独立的监控数据库。
    """

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

        logger.info(f"✅ MonitoringDatabase initialized (enabled={enable_monitoring})")

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
            logger.error(f"监控数据库连接错误: {e}")
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
            target_database: 目标数据库 (TDengine/PostgreSQL/MySQL/Redis)
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
                        additional_info,
                    ),
                )

                cursor.close()

            return True

        except Exception as e:
            self._write_failures += 1
            logger.warning(f"记录操作日志失败 (降级到本地日志): {e}")
            logger.info(
                f"操作日志: {operation_type} {classification} -> {target_database}.{table_name} "
                f"({record_count} records, {operation_status}, {execution_time_ms}ms)"
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
                        tags,
                    ),
                )

                cursor.close()

            return True

        except Exception as e:
            logger.warning(f"记录性能指标失败: {e}")
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
                        threshold_config,
                        check_duration_ms,
                    ),
                )

                cursor.close()

            return True

        except Exception as e:
            logger.warning(f"记录质量检查失败: {e}")
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
                        additional_data,
                    ),
                )

                cursor.close()

            logger.warning(f"🚨 告警创建: [{alert_level}] {alert_title}")
            return alert_id

        except Exception as e:
            logger.error(f"创建告警失败: {e}")
            logger.warning(f"告警内容: [{alert_level}] {alert_title} - {alert_message}")
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
            logger.error(f"更新告警状态失败: {e}")
            return False

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
            stats["write_success_rate"] = (
                (self._total_writes - self._write_failures) / self._total_writes * 100
            )

        return stats

    def cleanup_old_records(
        self, days_to_keep: Optional[Dict[str, int]] = None
    ) -> Dict[str, int]:
        """
        清理过期记录

        Args:
            days_to_keep: 各表保留天数配置 {
                'operation_logs': 30,
                'performance_metrics': 90,
                'data_quality_checks': 7,
                'alert_records': 90
            }

        Returns:
            dict: 各表删除的记录数
        """
        if not self.enable_monitoring:
            return {}

        if days_to_keep is None:
            days_to_keep = {
                "operation_logs": 30,
                "performance_metrics": 90,
                "data_quality_checks": 7,
                "alert_records": 90,
            }

        deleted_counts = {}

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                for table_name, days in days_to_keep.items():
                    cutoff_date = datetime.now() - timedelta(days=days)

                    cursor.execute(
                        f"""
                        DELETE FROM {table_name}
                        WHERE created_at < %s
                    """,
                        (cutoff_date,),
                    )

                    deleted_counts[table_name] = cursor.rowcount
                    logger.info(
                        f"清理 {table_name}: 删除 {cursor.rowcount} 条记录 (>{days}天)"
                    )

                cursor.close()

            return deleted_counts

        except Exception as e:
            logger.error(f"清理过期记录失败: {e}")
            return deleted_counts


# 全局监控数据库实例 (单例模式)
_monitoring_db: Optional[MonitoringDatabase] = None


def get_monitoring_database(enable_monitoring: bool = True) -> MonitoringDatabase:
    """获取全局监控数据库实例 (单例模式)"""
    global _monitoring_db
    if _monitoring_db is None:
        _monitoring_db = MonitoringDatabase(enable_monitoring=enable_monitoring)
    return _monitoring_db


if __name__ == "__main__":
    """测试监控数据库"""
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    print("\n测试MonitoringDatabase...")

    # 创建监控数据库实例
    monitor_db = MonitoringDatabase(enable_monitoring=True)

    # 测试1: 记录操作日志
    print("\n1. 测试记录操作日志...")
    success = monitor_db.log_operation(
        operation_type="SAVE",
        classification="DAILY_KLINE",
        target_database="PostgreSQL",
        table_name="daily_kline",
        record_count=100,
        operation_status="SUCCESS",
        execution_time_ms=45,
    )
    print(f"   记录操作日志: {'✅ 成功' if success else '❌ 失败'}")

    # 测试2: 记录性能指标
    print("\n2. 测试记录性能指标...")
    success = monitor_db.record_performance_metric(
        metric_name="query_daily_kline",
        metric_value=150.5,
        metric_type="QUERY_TIME",
        metric_unit="ms",
        classification="DAILY_KLINE",
        database_type="PostgreSQL",
        is_slow_query=False,
    )
    print(f"   记录性能指标: {'✅ 成功' if success else '❌ 失败'}")

    # 测试3: 记录质量检查
    print("\n3. 测试记录质量检查...")
    success = monitor_db.log_quality_check(
        check_type="COMPLETENESS",
        classification="DAILY_KLINE",
        database_type="PostgreSQL",
        table_name="daily_kline",
        check_status="PASS",
        total_records=10000,
        null_records=5,
        missing_rate=0.05,
    )
    print(f"   记录质量检查: {'✅ 成功' if success else '❌ 失败'}")

    # 测试4: 创建告警
    print("\n4. 测试创建告警...")
    alert_id = monitor_db.create_alert(
        alert_level="WARNING",
        alert_type="DATA_QUALITY",
        alert_title="数据缺失率偏高",
        alert_message="daily_kline表数据缺失率达到5%,超过阈值3%",
        source="DataQualityMonitor",
        classification="DAILY_KLINE",
        notification_channels=["log", "webhook"],
    )
    print(f"   创建告警: {'✅ 成功' if alert_id else '❌ 失败'} (ID={alert_id})")

    # 显示统计信息
    print("\n5. 监控统计信息:")
    stats = monitor_db.get_statistics()
    print(f"   总写入次数: {stats['total_writes']}")
    print(f"   写入失败次数: {stats['write_failures']}")
    print(f"   写入成功率: {stats['write_success_rate']:.2f}%")

    print("\n✅ MonitoringDatabase测试完成!")
