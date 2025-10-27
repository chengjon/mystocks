#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
US3 DataManager 监控集成模块
用于记录 DataManager 路由性能和操作指标到 PostgreSQL 监控数据库

版本: 1.0.0
创建日期: 2025-10-25
用途: 与 Grafana 集成，实现 DataManager 性能可视化监控
"""

import os
import time
import psycopg2
from datetime import datetime
from typing import Optional, Dict, Any
from contextlib import contextmanager
import logging

logger = logging.getLogger('DataManagerMonitoring')


class DataManagerMonitor:
    """
    DataManager 监控器 - 记录路由性能到 PostgreSQL

    特点:
    - 记录 O(1) 路由决策时间
    - 记录数据库目标分布
    - 记录数据分类频率
    - 支持 Grafana 可视化
    """

    def __init__(self, db_config: Optional[Dict[str, Any]] = None):
        """
        初始化监控器

        Args:
            db_config: PostgreSQL 监控数据库配置
        """
        self.db_config = db_config or self._load_db_config()
        self.enabled = self._check_monitoring_enabled()

        if self.enabled:
            self._verify_monitoring_tables()
            logger.info("DataManager 监控已启用")
        else:
            logger.info("DataManager 监控已禁用")

    def _load_db_config(self) -> Dict[str, Any]:
        """从环境变量加载数据库配置"""
        from dotenv import load_dotenv
        load_dotenv()

        return {
            'host': os.getenv('POSTGRESQL_HOST', '192.168.123.104'),
            'port': int(os.getenv('POSTGRESQL_PORT', '5438')),
            'user': os.getenv('POSTGRESQL_USER', 'postgres'),
            'password': os.getenv('POSTGRESQL_PASSWORD', ''),
            'database': os.getenv('POSTGRESQL_DATABASE', 'mystocks')
        }

    def _check_monitoring_enabled(self) -> bool:
        """检查监控是否启用"""
        # 尝试连接数据库
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                return True
        except Exception as e:
            logger.warning(f"监控数据库连接失败: {e}")
            return False

    @contextmanager
    def _get_connection(self):
        """获取数据库连接（上下文管理器）"""
        conn = None
        try:
            conn = psycopg2.connect(**self.db_config)
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"数据库操作失败: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def _verify_monitoring_tables(self):
        """验证监控表是否存在"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    # 检查 monitoring schema
                    cursor.execute("""
                        SELECT COUNT(*)
                        FROM information_schema.schemata
                        WHERE schema_name = 'monitoring'
                    """)
                    if cursor.fetchone()[0] == 0:
                        logger.warning("监控 schema 不存在，请运行 init_us3_monitoring.sql")

                    # 检查 datamanager_routing_metrics 表
                    cursor.execute("""
                        SELECT COUNT(*)
                        FROM information_schema.tables
                        WHERE table_schema = 'monitoring'
                          AND table_name = 'datamanager_routing_metrics'
                    """)
                    if cursor.fetchone()[0] == 0:
                        logger.warning("监控表不存在，请运行 init_us3_monitoring.sql")
        except Exception as e:
            logger.error(f"验证监控表失败: {e}")

    def record_routing_operation(
        self,
        operation_id: str,
        classification: str,
        target_database: str,
        routing_decision_time_ms: float,
        operation_type: str,
        table_name: Optional[str] = None,
        data_count: int = 0,
        operation_success: bool = True,
        operation_duration_ms: Optional[float] = None,
        error_message: Optional[str] = None
    ):
        """
        记录路由操作到监控数据库

        Args:
            operation_id: 操作ID
            classification: 数据分类
            target_database: 目标数据库 (TDENGINE 或 POSTGRESQL)
            routing_decision_time_ms: 路由决策时间（毫秒）
            operation_type: 操作类型 (save_data, load_data)
            table_name: 表名
            data_count: 数据条数
            operation_success: 操作是否成功
            operation_duration_ms: 总操作时间（毫秒）
            error_message: 错误信息
        """
        if not self.enabled:
            return

        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    insert_sql = """
                    INSERT INTO monitoring.datamanager_routing_metrics (
                        operation_id, classification, target_database,
                        routing_decision_time_ms, operation_type, table_name,
                        data_count, operation_success, operation_duration_ms,
                        error_message
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                    """

                    cursor.execute(insert_sql, (
                        operation_id,
                        classification,
                        target_database,
                        routing_decision_time_ms,
                        operation_type,
                        table_name,
                        data_count,
                        operation_success,
                        operation_duration_ms,
                        error_message
                    ))

                    logger.debug(f"记录路由操作: {operation_id}, 路由时间: {routing_decision_time_ms}ms")

        except Exception as e:
            logger.error(f"记录路由操作失败: {e}")

    def create_routing_alert(
        self,
        alert_type: str,
        severity: str,
        classification: Optional[str] = None,
        target_database: Optional[str] = None,
        metric_value: Optional[float] = None,
        threshold_value: Optional[float] = None,
        message: str = ""
    ):
        """
        创建路由性能告警

        Args:
            alert_type: 告警类型 (SLOW_ROUTING, HIGH_FAILURE_RATE)
            severity: 严重程度 (INFO, WARNING, ERROR, CRITICAL)
            classification: 数据分类
            target_database: 目标数据库
            metric_value: 指标值
            threshold_value: 阈值
            message: 告警消息
        """
        if not self.enabled:
            return

        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    insert_sql = """
                    INSERT INTO monitoring.routing_performance_alerts (
                        alert_type, severity, classification, target_database,
                        metric_value, threshold_value, message
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s
                    )
                    """

                    cursor.execute(insert_sql, (
                        alert_type,
                        severity,
                        classification,
                        target_database,
                        metric_value,
                        threshold_value,
                        message
                    ))

                    logger.warning(f"创建路由告警: {alert_type} - {severity} - {message}")

        except Exception as e:
            logger.error(f"创建路由告警失败: {e}")

    def get_routing_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """
        获取路由统计信息

        Args:
            hours: 统计时间范围（小时）

        Returns:
            Dict: 统计信息
        """
        if not self.enabled:
            return {'error': '监控未启用'}

        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    # 使用预定义的视图
                    cursor.execute("SELECT * FROM monitoring.v_routing_performance_24h")
                    result = cursor.fetchone()

                    if result:
                        return {
                            'total_operations': result[0],
                            'successful_operations': result[1],
                            'failed_operations': result[2],
                            'avg_routing_time_ms': float(result[3]) if result[3] else 0,
                            'max_routing_time_ms': float(result[4]) if result[4] else 0,
                            'min_routing_time_ms': float(result[5]) if result[5] else 0,
                            'avg_operation_time_ms': float(result[6]) if result[6] else 0,
                            'total_data_count': result[7] if result[7] else 0
                        }
                    return {}

        except Exception as e:
            logger.error(f"获取路由统计失败: {e}")
            return {'error': str(e)}

    def get_database_distribution(self) -> Dict[str, Any]:
        """获取数据库目标分布统计"""
        if not self.enabled:
            return {'error': '监控未启用'}

        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT * FROM monitoring.v_database_distribution_24h")
                    results = cursor.fetchall()

                    distribution = {}
                    for row in results:
                        distribution[row[0]] = {
                            'operation_count': row[1],
                            'success_count': row[2],
                            'failure_count': row[3],
                            'success_rate_percent': float(row[4]) if row[4] else 0,
                            'total_data_count': row[5] if row[5] else 0,
                            'avg_routing_time_ms': float(row[6]) if row[6] else 0,
                            'avg_operation_time_ms': float(row[7]) if row[7] else 0
                        }
                    return distribution

        except Exception as e:
            logger.error(f"获取数据库分布失败: {e}")
            return {'error': str(e)}

    def get_classification_frequency(self) -> list:
        """获取数据分类频率统计"""
        if not self.enabled:
            return []

        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT * FROM monitoring.v_classification_frequency_24h LIMIT 20")
                    results = cursor.fetchall()

                    frequency_list = []
                    for row in results:
                        frequency_list.append({
                            'classification': row[0],
                            'target_database': row[1],
                            'operation_count': row[2],
                            'percentage': float(row[3]) if row[3] else 0,
                            'success_count': row[4],
                            'avg_routing_time_ms': float(row[5]) if row[5] else 0,
                            'avg_operation_time_ms': float(row[6]) if row[6] else 0,
                            'total_data_count': row[7] if row[7] else 0
                        })
                    return frequency_list

        except Exception as e:
            logger.error(f"获取分类频率失败: {e}")
            return []

    def update_aggregated_statistics(self):
        """更新聚合统计表"""
        if not self.enabled:
            return

        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    # 更新分类统计
                    cursor.execute("SELECT monitoring.update_classification_statistics()")

                    # 更新数据库分布统计
                    cursor.execute("SELECT monitoring.update_database_distribution()")

                    logger.info("聚合统计更新完成")

        except Exception as e:
            logger.error(f"更新聚合统计失败: {e}")

    def cleanup_old_data(self, days: int = 30) -> int:
        """
        清理旧监控数据

        Args:
            days: 保留天数

        Returns:
            int: 删除的记录数
        """
        if not self.enabled:
            return 0

        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT monitoring.cleanup_old_routing_metrics()")
                    deleted_count = cursor.fetchone()[0]
                    logger.info(f"清理旧监控数据: 删除 {deleted_count} 条记录")
                    return deleted_count

        except Exception as e:
            logger.error(f"清理旧数据失败: {e}")
            return 0


class RoutingOperationContext:
    """
    路由操作上下文管理器 - 自动记录操作性能

    用法:
    ```python
    monitor = DataManagerMonitor()
    with RoutingOperationContext(monitor, classification, target_db, operation_type) as ctx:
        # 执行操作
        result = perform_operation()
        ctx.set_result(success=True, data_count=100)
    ```
    """

    def __init__(
        self,
        monitor: DataManagerMonitor,
        classification: str,
        target_database: str,
        operation_type: str,
        table_name: Optional[str] = None
    ):
        self.monitor = monitor
        self.classification = classification
        self.target_database = target_database
        self.operation_type = operation_type
        self.table_name = table_name

        self.operation_id = f"{datetime.now().strftime('%Y%m%d%H%M%S%f')}_{classification}"
        self.start_time = None
        self.routing_start_time = None
        self.routing_decision_time_ms = None

        self.data_count = 0
        self.operation_success = False
        self.error_message = None

    def __enter__(self):
        """进入上下文"""
        self.start_time = time.time()
        self.routing_start_time = time.time()
        return self

    def mark_routing_complete(self):
        """标记路由决策完成"""
        if self.routing_start_time:
            self.routing_decision_time_ms = (time.time() - self.routing_start_time) * 1000

    def set_result(self, success: bool, data_count: int = 0, error_message: Optional[str] = None):
        """设置操作结果"""
        self.operation_success = success
        self.data_count = data_count
        self.error_message = error_message

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文，记录监控数据"""
        if exc_type is not None:
            # 发生异常
            self.operation_success = False
            self.error_message = str(exc_val)

        # 计算总操作时间
        operation_duration_ms = (time.time() - self.start_time) * 1000 if self.start_time else None

        # 确保路由时间已记录
        if self.routing_decision_time_ms is None:
            self.mark_routing_complete()

        # 记录到监控数据库
        self.monitor.record_routing_operation(
            operation_id=self.operation_id,
            classification=self.classification,
            target_database=self.target_database,
            routing_decision_time_ms=self.routing_decision_time_ms,
            operation_type=self.operation_type,
            table_name=self.table_name,
            data_count=self.data_count,
            operation_success=self.operation_success,
            operation_duration_ms=operation_duration_ms,
            error_message=self.error_message
        )

        # 检查路由性能告警（如果路由时间 > 1ms）
        if self.routing_decision_time_ms and self.routing_decision_time_ms > 1.0:
            self.monitor.create_routing_alert(
                alert_type='SLOW_ROUTING',
                severity='WARNING',
                classification=self.classification,
                target_database=self.target_database,
                metric_value=self.routing_decision_time_ms,
                threshold_value=1.0,
                message=f"路由决策时间过长: {self.routing_decision_time_ms:.4f}ms (预期: <1ms)"
            )

        return False  # 不抑制异常


if __name__ == "__main__":
    # 测试监控器
    logging.basicConfig(level=logging.INFO)

    monitor = DataManagerMonitor()

    # 测试记录路由操作
    with RoutingOperationContext(
        monitor,
        classification="TICK_DATA",
        target_database="TDENGINE",
        operation_type="save_data",
        table_name="tick_data"
    ) as ctx:
        # 模拟路由决策
        time.sleep(0.0002)
        ctx.mark_routing_complete()

        # 模拟数据操作
        time.sleep(0.1)
        ctx.set_result(success=True, data_count=1000)

    # 获取统计信息
    print("\n=== 路由统计 ===")
    stats = monitor.get_routing_statistics()
    for key, value in stats.items():
        print(f"{key}: {value}")

    print("\n=== 数据库分布 ===")
    distribution = monitor.get_database_distribution()
    for db, info in distribution.items():
        print(f"{db}: {info}")

    print("\n=== 分类频率 ===")
    frequency = monitor.get_classification_frequency()
    for item in frequency[:5]:
        print(f"{item['classification']}: {item['operation_count']} 次 ({item['percentage']}%)")
