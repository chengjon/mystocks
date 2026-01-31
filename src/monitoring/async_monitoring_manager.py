"""
# 功能：异步监控管理器 - 向后兼容的异步监控接口
# 作者：Claude (基于多角色架构评估建议)
# 创建日期：2026-01-03
# 版本：1.0.0
# 注意事项：
#   本文件提供与MonitoringDatabase完全相同的接口
#   内部使用异步事件处理，对业务代码透明
#   通过ENABLE_ASYNC_MONITORING环境变量控制是否启用
# 版权：MyStocks Project © 2026
"""

import logging
import os
from datetime import datetime
from typing import Dict, List, Optional

from .async_monitoring import (
    MonitoringEvent,
    get_event_publisher,
    start_async_monitoring,
    stop_async_monitoring,
)
from .monitoring_database import MonitoringDatabase

logger = logging.getLogger(__name__)


class AsyncMonitoringManager(MonitoringDatabase):
    """
    异步监控管理器

    继承自MonitoringDatabase，提供完全相同的接口，
    但内部使用异步事件处理，避免阻塞业务操作。

    通过环境变量ENABLE_ASYNC_MONITORING=true启用
    """

    def __init__(self, enable_monitoring: bool = True):
        """
        初始化异步监控管理器

        Args:
            enable_monitoring: 是否启用监控 (默认True)
        """
        # 初始化父类（用于降级情况）
        super().__init__(enable_monitoring=enable_monitoring)

        # 检查是否启用异步模式
        self.async_enabled = os.getenv("ENABLE_ASYNC_MONITORING", "false").lower() == "true"

        if self.async_enabled:
            self.event_publisher = get_event_publisher()
            logger.info("✅ AsyncMonitoringManager initialized (async mode)")
        else:
            self.event_publisher = None
            logger.info("✅ AsyncMonitoringManager initialized (sync mode)")

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
        记录操作日志 (异步)

        Args: (同MonitoringDatabase.log_operation)
        Returns:
            bool: 记录是否成功
        """
        if not self.enable_monitoring:
            return True

        if self.async_enabled and self.event_publisher:
            # 异步模式：发布事件
            event = MonitoringEvent(
                event_type="operation",
                data={
                    "operation_type": operation_type,
                    "classification": classification,
                    "target_database": target_database,
                    "table_name": table_name,
                    "record_count": record_count,
                    "operation_status": operation_status,
                    "error_message": error_message,
                    "execution_time_ms": execution_time_ms,
                    "user_agent": user_agent,
                    "client_ip": client_ip,
                    "additional_info": additional_info,
                },
                timestamp=datetime.now(),
            )
            return self.event_publisher.publish_event(event)
        else:
            # 同步模式：直接调用父类方法
            return super().log_operation(
                operation_type=operation_type,
                classification=classification,
                target_database=target_database,
                table_name=table_name,
                record_count=record_count,
                operation_status=operation_status,
                error_message=error_message,
                execution_time_ms=execution_time_ms,
                user_agent=user_agent,
                client_ip=client_ip,
                additional_info=additional_info,
            )

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
        记录性能指标 (异步)

        Args: (同MonitoringDatabase.record_performance_metric)
        Returns:
            bool: 记录是否成功
        """
        if not self.enable_monitoring:
            return True

        if self.async_enabled and self.event_publisher:
            # 异步模式：发布事件
            event = MonitoringEvent(
                event_type="performance",
                data={
                    "metric_name": metric_name,
                    "metric_value": metric_value,
                    "metric_type": metric_type,
                    "metric_unit": metric_unit,
                    "classification": classification,
                    "database_type": database_type,
                    "table_name": table_name,
                    "is_slow_query": is_slow_query,
                    "query_sql": query_sql,
                    "execution_plan": execution_plan,
                    "tags": tags,
                },
                timestamp=datetime.now(),
            )
            return self.event_publisher.publish_event(event)
        else:
            # 同步模式：直接调用父类方法
            return super().record_performance_metric(
                metric_name=metric_name,
                metric_value=metric_value,
                metric_type=metric_type,
                metric_unit=metric_unit,
                classification=classification,
                database_type=database_type,
                table_name=table_name,
                is_slow_query=is_slow_query,
                query_sql=query_sql,
                execution_plan=execution_plan,
                tags=tags,
            )

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
        记录数据质量检查 (异步)

        Args: (同MonitoringDatabase.log_quality_check)
        Returns:
            bool: 记录是否成功
        """
        if not self.enable_monitoring:
            return True

        if self.async_enabled and self.event_publisher:
            # 异步模式：发布事件
            event = MonitoringEvent(
                event_type="quality_check",
                data={
                    "check_type": check_type,
                    "classification": classification,
                    "database_type": database_type,
                    "table_name": table_name,
                    "check_status": check_status,
                    "total_records": total_records,
                    "null_records": null_records,
                    "missing_rate": missing_rate,
                    "latest_timestamp": latest_timestamp,
                    "data_delay_seconds": data_delay_seconds,
                    "invalid_records": invalid_records,
                    "validation_rules": validation_rules,
                    "check_message": check_message,
                    "threshold_config": threshold_config,
                    "check_duration_ms": check_duration_ms,
                },
                timestamp=datetime.now(),
            )
            return self.event_publisher.publish_event(event)
        else:
            # 同步模式：直接调用父类方法
            return super().log_quality_check(
                check_type=check_type,
                classification=classification,
                database_type=database_type,
                table_name=table_name,
                check_status=check_status,
                total_records=total_records,
                null_records=null_records,
                missing_rate=missing_rate,
                latest_timestamp=latest_timestamp,
                data_delay_seconds=data_delay_seconds,
                invalid_records=invalid_records,
                validation_rules=validation_rules,
                check_message=check_message,
                threshold_config=threshold_config,
                check_duration_ms=check_duration_ms,
            )

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
        创建告警 (异步)

        注意：告警需要即时发送，所以即使异步模式下也同步写入

        Args: (同MonitoringDatabase.create_alert)
        Returns:
            str: 告警ID (失败返回None)
        """
        if not self.enable_monitoring:
            return None

        # 告警始终同步处理（需要即时通知）
        return super().create_alert(
            alert_level=alert_level,
            alert_type=alert_type,
            alert_title=alert_title,
            alert_message=alert_message,
            source=source,
            classification=classification,
            database_type=database_type,
            table_name=table_name,
            additional_data=additional_data,
            notification_channels=notification_channels,
        )


# 全局实例（替换MonitoringDatabase）
_async_monitoring_db: Optional[AsyncMonitoringManager] = None


def get_async_monitoring_database(enable_monitoring: bool = True) -> AsyncMonitoringManager:
    """
    获取全局异步监控数据库实例 (单例模式)

    这是get_monitoring_database()的异步版本，提供完全相同的接口。

    Args:
        enable_monitoring: 是否启用监控 (默认True)

    Returns:
        AsyncMonitoringManager: 异步监控管理器实例
    """
    global _async_monitoring_db
    if _async_monitoring_db is None:
        _async_monitoring_db = AsyncMonitoringManager(enable_monitoring=enable_monitoring)
    return _async_monitoring_db


def initialize_async_monitoring():
    """
    初始化异步监控系统

    在应用启动时调用，启动后台Worker。
    """
    if os.getenv("ENABLE_ASYNC_MONITORING", "false").lower() == "true":
        logger.info("🚀 初始化异步监控系统...")
        start_async_monitoring()
        logger.info("✅ 异步监控系统初始化完成")
    else:
        logger.info("ℹ️ 异步监控未启用 (设置ENABLE_ASYNC_MONITORING=true)")


def shutdown_async_monitoring():
    """
    关闭异步监控系统

    在应用关闭时调用，停止后台Worker。
    """
    if os.getenv("ENABLE_ASYNC_MONITORING", "false").lower() == "true":
        logger.info("⏹️ 关闭异步监控系统...")
        stop_async_monitoring()
        logger.info("✅ 异步监控系统已关闭")


if __name__ == "__main__":
    """测试异步监控管理器"""
    import os
    import sys
    import time

    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    print("\n测试AsyncMonitoringManager...\n")

    # 启用异步模式
    os.environ["ENABLE_ASYNC_MONITORING"] = "true"

    # 测试1: 初始化
    print("1. 测试初始化...")
    initialize_async_monitoring()
    print("   ✅ 初始化完成\n")

    # 测试2: 记录操作日志
    print("2. 测试记录操作日志...")
    async_monitor = get_async_monitoring_database()
    success = async_monitor.log_operation(
        operation_type="SAVE",
        classification="DAILY_KLINE",
        target_database="PostgreSQL",
        table_name="daily_kline",
        record_count=100,
        operation_status="SUCCESS",
        execution_time_ms=45,
    )
    print(f"   记录操作: {'✅ 成功' if success else '❌ 失败'}\n")

    # 测试3: 记录性能指标
    print("3. 测试记录性能指标...")
    success = async_monitor.record_performance_metric(
        metric_name="query_daily_kline",
        metric_value=150.5,
        metric_type="QUERY_TIME",
        classification="DAILY_KLINE",
        database_type="PostgreSQL",
    )
    print(f"   记录性能指标: {'✅ 成功' if success else '❌ 失败'}\n")

    # 等待Worker处理
    print("4. 等待Worker处理事件...")
    time.sleep(2)

    # 测试5: 关闭
    print("5. 关闭异步监控系统...")
    shutdown_async_monitoring()
    print("   ✅ 已关闭\n")

    print("✅ AsyncMonitoringManager测试完成!")
