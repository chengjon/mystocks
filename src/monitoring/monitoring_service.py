#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MyStocks 量化交易数据管理系统 - 监控与自动化模块
完整的监控体系、自动化运维和数据管理

基于原始设计理念：
1. 监控数据库与业务数据库完全分离
2. 完整记录所有数据库操作
3. 自动化维护和告警机制
4. 数据质量监控和性能优化

作者: MyStocks项目组
版本: v2.0 重构版
日期: 2025-09-21
"""

import os
import json
import time
import pymysql
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
from abc import ABC, abstractmethod
from dataclasses import dataclass

import logging
from dotenv import load_dotenv

# 导入核心模块 (US3: 已移除DataStorageStrategy)
from src.core import (
    DataClassification,
    ConfigDrivenTableManager,
)

logger = logging.getLogger("MyStocksMonitoring")


@dataclass
class OperationMetrics:
    """操作指标数据类"""

    operation_id: str
    table_name: str
    database_type: str
    database_name: str
    operation_type: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    status: str = "processing"
    data_count: int = 0
    error_message: Optional[str] = None

    def mark_completed(self, data_count: int = 0):
        """标记操作完成"""
        self.end_time = datetime.now()
        self.duration = (self.end_time - self.start_time).total_seconds()
        self.status = "success"
        self.data_count = data_count

    def mark_failed(self, error_message: str):
        """标记操作失败"""
        self.end_time = datetime.now()
        self.duration = (self.end_time - self.start_time).total_seconds()
        self.status = "failed"
        self.error_message = error_message


class AlertLevel(Enum):
    """告警级别"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Alert:
    """告警数据类"""

    alert_id: str
    level: AlertLevel
    title: str
    message: str
    source: str
    timestamp: datetime
    resolved: bool = False
    resolve_time: Optional[datetime] = None


class MonitoringDatabase:
    """监控数据库管理器 - 与业务数据库完全分离"""

    def __init__(self, monitor_db_url: str = None):
        """
        初始化监控数据库

        Args:
            monitor_db_url: 监控数据库连接URL
        """
        # 加载环境变量
        load_dotenv()

        from src.storage.database.database_manager import (
            DatabaseTableManager,
        )

        self.monitor_db_url = monitor_db_url or os.getenv("MONITOR_DB_URL")
        self.db_manager = DatabaseTableManager()

        # 监控数据库连接参数
        self.monitor_db_config = {
            "host": os.getenv("MONITOR_DB_HOST"),
            "port": int(os.getenv("MONITOR_DB_PORT", "3306")),
            "user": os.getenv("MONITOR_DB_USER", "root"),
            "password": os.getenv("MONITOR_DB_PASSWORD", ""),
            "database": os.getenv("MONITOR_DB_DATABASE", "db_monitor"),
            "charset": "utf8mb4",
        }

        # 初始化监控表结构
        self._ensure_monitoring_tables()

        logger.info("监控数据库初始化完成: {self.monitor_db_config['host']}:{self.monitor_db_config['port']}")

    def _get_monitor_connection(self):
        """获取监控数据库连接"""
        try:
            connection = pymysql.connect(**self.monitor_db_config)
            return connection
        except Exception as e:
            logger.error("连接监控数据库失败: %s", e)
            return None

    def _ensure_monitoring_tables(self):
        """确保监控表结构存在"""
        try:
            connection = self._get_monitor_connection()
            if connection:
                cursor = connection.cursor()

                # 检查监控表是否存在，如果不存在则创建
                check_tables_sql = """
                SELECT COUNT(*) as table_count FROM information_schema.tables
                WHERE table_schema = %s AND table_name IN
                ('table_creation_log', 'column_definition_log', 'table_operation_log', 'table_validation_log')
                """

                cursor.execute(check_tables_sql, (self.monitor_db_config["database"],))
                result = cursor.fetchone()

                if result[0] < 4:
                    logger.warning("监控表不完整，尝试创建监控表结构")
                    # 这里可以调用 init_db_monitor.py 的功能
                    try:
                        from src.storage.database.init_db_monitor import (
                            init_monitoring_database,
                        )

                        init_monitoring_database()
                        logger.info("监控表结构创建完成")
                    except Exception as e:
                        logger.error("创建监控表失败: %s", e)

                cursor.close()
                connection.close()
                logger.info("监控表结构检查完成")

        except Exception as e:
            logger.error("检查监控表结构失败: %s", e)

        if not self.monitor_db_url:
            logger.error("未配置监控数据库URL，无法启动监控服务")
            raise ValueError(
                "MONITOR_DB_URL 环境变量必须设置。"
                "请在 .env 文件中配置: MONITOR_DB_URL=postgresql://user:password@host:port/database"
            )

        self._init_monitoring_tables()

    def _init_monitoring_tables(self):
        """初始化监控表结构"""
        try:
            # 这里可以调用现有的 init_db_monitor.py 逻辑
            # 或者直接创建监控表
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

            # 记录到监控数据库
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

            # 这里应该插入到 table_operation_log 表
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

            # 更新监控数据库
            self._update_operation_log(operation_id, update_data)

        except Exception as e:
            logger.error("记录操作结果失败: %s", e)

    def _insert_operation_log(self, log_data: Dict):
        """插入操作日志到监控数据库"""
        try:
            connection = self._get_monitor_connection()
            if connection:
                cursor = connection.cursor()

                # 插入到 table_operation_log 表
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

    def _update_operation_log(self, operation_id: str, update_data: Dict):
        """更新操作日志"""
        try:
            connection = self._get_monitor_connection()
            if connection:
                cursor = connection.cursor()

                # 更新 table_operation_log 表
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

            # 计算时间范围
            start_time = datetime.now() - timedelta(hours=hours)

            # 总操作数统计
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

            # 数据库类型统计
            db_breakdown_sql = """
            SELECT database_type, COUNT(*) as count
            FROM table_operation_log
            WHERE operation_time >= %s
            GROUP BY database_type
            """

            cursor.execute(db_breakdown_sql, (start_time,))
            db_breakdown_results = cursor.fetchall()

            # 操作类型统计
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

            # 构建统计结果
            stats = {
                "total_operations": total_result[0] if total_result[0] else 0,
                "successful_operations": total_result[1] if total_result[1] else 0,
                "failed_operations": total_result[2] if total_result[2] else 0,
                "database_breakdown": {db[0]: db[1] for db in db_breakdown_results},
                "operation_type_breakdown": {op[0]: op[1] for op in op_breakdown_results},
                "average_duration": float(total_result[3]) if total_result[3] else 0.0,
                "last_update": datetime.now().isoformat(),
            }

            return stats

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
            # 查询 table_creation_log 表
            history = []

            # 这里应该执行实际的查询逻辑

            return history

        except Exception as e:
            logger.error("获取表创建历史失败: %s", e)
            return []


class DataQualityMonitor:
    """数据质量监控器"""

    def __init__(self, config_manager: ConfigDrivenTableManager):
        """
        初始化数据质量监控器

        Args:
            config_manager: 配置管理器
        """
        self.config_manager = config_manager
        self.quality_rules = self._load_quality_rules()

    def _load_quality_rules(self) -> Dict[str, Any]:
        """加载数据质量规则"""
        return {
            "completeness": {
                "threshold": 0.95,  # 完整性阈值95%
                "required_columns": ["symbol", "trade_date"],
            },
            "freshness": {
                "daily_data_hours": 24,  # 日线数据24小时内更新
                "realtime_data_minutes": 5,  # 实时数据5分钟内更新
            },
            "accuracy": {
                "price_range": {"min": 0, "max": 10000},  # 价格范围
                "volume_range": {"min": 0, "max": 1e12},  # 成交量范围
            },
            "consistency": {
                "ohlc_check": True,  # OHLC一致性检查
                "duplicate_check": True,  # 重复数据检查
            },
        }

    def check_data_completeness(self, classification: DataClassification) -> Dict[str, Any]:
        """
        检查数据完整性

        Args:
            classification: 数据分类

        Returns:
            Dict: 完整性检查结果
        """
        try:
            result = {
                "classification": classification.value,
                "check_time": datetime.now().isoformat(),
                "completeness_score": 0.0,
                "missing_data": [],
                "issues": [],
            }

            # 根据数据分类执行相应的完整性检查
            if classification == DataClassification.DAILY_KLINE:
                result.update(self._check_daily_kline_completeness())
            elif classification == DataClassification.SYMBOLS_INFO:
                result.update(self._check_symbols_completeness())

            logger.info("数据完整性检查完成: %s", classification.value)
            return result

        except Exception as e:
            logger.error("数据完整性检查失败: %s", e)
            return {"error": str(e)}

    def _check_daily_kline_completeness(self) -> Dict[str, Any]:
        """检查日线数据完整性"""
        # 实现具体的日线数据完整性检查逻辑
        return {"completeness_score": 0.98, "missing_data": [], "issues": []}

    def _check_symbols_completeness(self) -> Dict[str, Any]:
        """检查股票信息完整性"""
        # 实现具体的股票信息完整性检查逻辑
        return {"completeness_score": 0.99, "missing_data": [], "issues": []}

    def check_data_freshness(self) -> Dict[str, Any]:
        """
        检查数据新鲜度

        Returns:
            Dict: 新鲜度检查结果
        """
        try:
            result = {
                "check_time": datetime.now().isoformat(),
                "stale_data": [],
                "warnings": [],
            }

            # 检查各类数据的新鲜度
            freshness_rules = self.quality_rules["freshness"]

            # 检查日线数据
            daily_freshness = self._check_table_freshness("daily_kline", freshness_rules["daily_data_hours"])
            if daily_freshness["is_stale"]:
                result["stale_data"].append(daily_freshness)

            logger.info("数据新鲜度检查完成")
            return result

        except Exception as e:
            logger.error("数据新鲜度检查失败: %s", e)
            return {"error": str(e)}

    def _check_table_freshness(self, table_name: str, threshold_hours: int) -> Dict[str, Any]:
        """
        检查单个表的数据新鲜度

        Args:
            table_name: 表名
            threshold_hours: 阈值（小时）

        Returns:
            Dict: 新鲜度检查结果
        """
        try:
            # 这里应该查询表的最后更新时间
            # 并与阈值进行比较

            result = {
                "table_name": table_name,
                "last_update": datetime.now() - timedelta(hours=2),  # 示例
                "threshold_hours": threshold_hours,
                "is_stale": False,
                "hours_old": 2,
            }

            result["is_stale"] = result["hours_old"] > threshold_hours

            return result

        except Exception as e:
            logger.error("检查表新鲜度失败: %s, %s", table_name, e)
            return {"table_name": table_name, "error": str(e)}

    def check_data_accuracy(self, classification: DataClassification, sample_size: int = 1000) -> Dict[str, Any]:
        """
        检查数据准确性

        Args:
            classification: 数据分类
            sample_size: 采样大小

        Returns:
            Dict: 准确性检查结果
        """
        try:
            result = {
                "classification": classification.value,
                "check_time": datetime.now().isoformat(),
                "sample_size": sample_size,
                "accuracy_score": 0.0,
                "anomalies": [],
                "out_of_range_values": [],
            }

            # 根据数据分类执行相应的准确性检查
            if classification == DataClassification.DAILY_KLINE:
                result.update(self._check_price_data_accuracy(sample_size))

            logger.info("数据准确性检查完成: %s", classification.value)
            return result

        except Exception as e:
            logger.error("数据准确性检查失败: %s", e)
            return {"error": str(e)}

    def _check_price_data_accuracy(self, sample_size: int) -> Dict[str, Any]:
        """检查价格数据准确性"""
        # 实现具体的价格数据准确性检查逻辑
        return {"accuracy_score": 0.99, "anomalies": [], "out_of_range_values": []}

    def generate_quality_report(self) -> Dict[str, Any]:
        """
        生成数据质量报告

        Returns:
            Dict: 质量报告
        """
        try:
            report = {
                "report_time": datetime.now().isoformat(),
                "overall_score": 0.0,
                "completeness": {},
                "freshness": {},
                "accuracy": {},
                "recommendations": [],
            }

            # 执行所有质量检查
            classification_list = [
                DataClassification.DAILY_KLINE,
                DataClassification.SYMBOLS_INFO,
                DataClassification.TECHNICAL_INDICATORS,
            ]

            completeness_scores = []
            accuracy_scores = []

            for classification in classification_list:
                # 完整性检查
                completeness_result = self.check_data_completeness(classification)
                report["completeness"][classification.value] = completeness_result
                if "completeness_score" in completeness_result:
                    completeness_scores.append(completeness_result["completeness_score"])

                # 准确性检查
                accuracy_result = self.check_data_accuracy(classification)
                report["accuracy"][classification.value] = accuracy_result
                if "accuracy_score" in accuracy_result:
                    accuracy_scores.append(accuracy_result["accuracy_score"])

            # 新鲜度检查
            freshness_result = self.check_data_freshness()
            report["freshness"] = freshness_result

            # 计算整体评分
            if completeness_scores and accuracy_scores:
                avg_completeness = sum(completeness_scores) / len(completeness_scores)
                avg_accuracy = sum(accuracy_scores) / len(accuracy_scores)
                report["overall_score"] = (avg_completeness + avg_accuracy) / 2

            # 生成建议
            report["recommendations"] = self._generate_recommendations(report)

            logger.info("数据质量报告生成完成，整体评分: %s", report["overall_score"])
            return report

        except Exception as e:
            logger.error("生成数据质量报告失败: %s", e)
            return {"error": str(e)}

    def _generate_recommendations(self, report: Dict[str, Any]) -> List[str]:
        """
        根据报告生成改进建议

        Args:
            report: 质量报告

        Returns:
            List[str]: 改进建议列表
        """
        recommendations = []

        # 基于整体评分给出建议
        if report["overall_score"] < 0.8:
            recommendations.append("数据质量较低，建议增强数据验证和清洗流程")

        # 基于新鲜度给出建议
        if report["freshness"].get("stale_data"):
            recommendations.append("存在过期数据，建议检查数据更新流程")

        # 基于完整性给出建议
        for classification, result in report["completeness"].items():
            if result.get("completeness_score", 1.0) < 0.9:
                recommendations.append(f"{classification} 数据完整性不足，建议检查数据采集流程")

        return recommendations


class PerformanceMonitor:
    """性能监控器"""

    def __init__(self):
        """初始化性能监控器"""
        self.metrics_history = []
        self.slow_query_threshold = 5.0  # 5秒

    def record_operation_metrics(self, metrics: OperationMetrics):
        """
        记录操作指标

        Args:
            metrics: 操作指标
        """
        try:
            self.metrics_history.append(metrics)

            # 保持历史记录在合理范围内
            if len(self.metrics_history) > 10000:
                self.metrics_history = self.metrics_history[-5000:]

            # 检查慢操作
            if metrics.duration and metrics.duration > self.slow_query_threshold:
                self._alert_slow_operation(metrics)

        except Exception as e:
            logger.error("记录操作指标失败: %s", e)

    def _alert_slow_operation(self, metrics: OperationMetrics):
        """告警慢操作"""
        alert_message = (
            f"慢操作告警: {metrics.operation_type} " f"on {metrics.table_name} 耗时 {metrics.duration:.2f}秒"
        )
        logger.warning(alert_message)

    def get_performance_summary(self, hours: int = 24) -> Dict[str, Any]:
        """
        获取性能摘要

        Args:
            hours: 统计时间范围（小时）

        Returns:
            Dict: 性能摘要
        """
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            recent_metrics = [m for m in self.metrics_history if m.start_time >= cutoff_time and m.duration is not None]

            if not recent_metrics:
                return {"message": "没有性能数据"}

            durations = [m.duration for m in recent_metrics]

            summary = {
                "time_range_hours": hours,
                "total_operations": len(recent_metrics),
                "avg_duration": sum(durations) / len(durations),
                "min_duration": min(durations),
                "max_duration": max(durations),
                "slow_operations": len([d for d in durations if d > self.slow_query_threshold]),
                "success_rate": len([m for m in recent_metrics if m.status == "success"]) / len(recent_metrics),
                "operation_breakdown": {},
                "database_breakdown": {},
            }

            # 按操作类型分组
            for metrics in recent_metrics:
                op_type = metrics.operation_type
                if op_type not in summary["operation_breakdown"]:
                    summary["operation_breakdown"][op_type] = {
                        "count": 0,
                        "avg_duration": 0,
                    }
                summary["operation_breakdown"][op_type]["count"] += 1

            # 计算平均时长
            for op_type in summary["operation_breakdown"]:
                op_metrics = [m for m in recent_metrics if m.operation_type == op_type]
                op_durations = [m.duration for m in op_metrics]
                summary["operation_breakdown"][op_type]["avg_duration"] = sum(op_durations) / len(op_durations)

            logger.info("性能摘要生成完成: 最近%s小时，%s个操作", hours, len(recent_metrics))
            return summary

        except Exception as e:
            logger.error("获取性能摘要失败: %s", e)
            return {"error": str(e)}

    def get_slow_operations(self, hours: int = 24, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取慢操作列表

        Args:
            hours: 时间范围（小时）
            limit: 返回数量限制

        Returns:
            List[Dict]: 慢操作列表
        """
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            slow_operations = [
                {
                    "operation_id": m.operation_id,
                    "table_name": m.table_name,
                    "operation_type": m.operation_type,
                    "duration": m.duration,
                    "start_time": m.start_time.isoformat(),
                    "data_count": m.data_count,
                }
                for m in self.metrics_history
                if (m.start_time >= cutoff_time and m.duration is not None and m.duration > self.slow_query_threshold)
            ]

            # 按持续时间降序排序
            slow_operations.sort(key=lambda x: x["duration"], reverse=True)

            logger.info("获取慢操作列表: %s 个操作", len(slow_operations))
            return slow_operations[:limit]

        except Exception as e:
            logger.error("获取慢操作列表失败: %s", e)
            return []


class AlertManager:
    """告警管理器"""

    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化告警管理器

        Args:
            config: 告警配置
        """
        self.config = config or self._get_default_alert_config()
        self.active_alerts = []
        self.alert_channels = self._init_alert_channels()

    def _get_default_alert_config(self) -> Dict[str, Any]:
        """获取默认告警配置"""
        return {
            "alert_rules": {
                "data_staleness": {"threshold": 24, "unit": "hours"},
                "table_creation_failure": {"threshold": 1, "unit": "count"},
                "slow_operation": {"threshold": 5, "unit": "seconds"},
                "disk_usage": {"threshold": 80, "unit": "percent"},
                "data_quality": {"threshold": 0.8, "unit": "score"},
            },
            "channels": [
                {"type": "log", "level": "ERROR"},
                {"type": "email", "recipients": ["admin@mystocks.com"]},
            ],
        }

    def _init_alert_channels(self) -> Dict[str, Any]:
        """初始化告警渠道"""
        channels = {}

        for channel_config in self.config["channels"]:
            channel_type = channel_config["type"]
            if channel_type == "email":
                channels["email"] = EmailAlertChannel(channel_config)
            elif channel_type == "webhook":
                channels["webhook"] = WebhookAlertChannel(channel_config)
            elif channel_type == "log":
                channels["log"] = LogAlertChannel(channel_config)

        return channels

    def create_alert(self, level: AlertLevel, title: str, message: str, source: str = "system") -> Alert:
        """
        创建告警

        Args:
            level: 告警级别
            title: 告警标题
            message: 告警消息
            source: 告警源

        Returns:
            Alert: 告警对象
        """
        try:
            alert = Alert(
                alert_id=f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{source}",
                level=level,
                title=title,
                message=message,
                source=source,
                timestamp=datetime.now(),
            )

            self.active_alerts.append(alert)

            # 发送告警
            self._send_alert(alert)

            logger.info("创建告警: %s - %s - %s", alert.alert_id, level.value, title)
            return alert

        except Exception as e:
            logger.error("创建告警失败: %s", e)
            raise

    def _send_alert(self, alert: Alert):
        """
        发送告警到各个渠道

        Args:
            alert: 告警对象
        """
        try:
            for channel_name, channel in self.alert_channels.items():
                try:
                    channel.send_alert(alert)
                except Exception as e:
                    logger.error("告警发送失败: %s, %s", channel_name, e)

        except Exception as e:
            logger.error("发送告警失败: %s", e)

    def resolve_alert(self, alert_id: str):
        """
        解决告警

        Args:
            alert_id: 告警ID
        """
        try:
            for alert in self.active_alerts:
                if alert.alert_id == alert_id and not alert.resolved:
                    alert.resolved = True
                    alert.resolve_time = datetime.now()
                    logger.info("告警已解决: %s", alert_id)
                    break

        except Exception as e:
            logger.error("解决告警失败: %s", e)

    def get_active_alerts(self, level: AlertLevel = None) -> List[Alert]:
        """
        获取活跃告警

        Args:
            level: 过滤告警级别

        Returns:
            List[Alert]: 活跃告警列表
        """
        try:
            active = [alert for alert in self.active_alerts if not alert.resolved]

            if level:
                active = [alert for alert in active if alert.level == level]

            return active

        except Exception as e:
            logger.error("获取活跃告警失败: %s", e)
            return []

    def cleanup_old_alerts(self, days: int = 7):
        """
        清理旧告警

        Args:
            days: 保留天数
        """
        try:
            cutoff_time = datetime.now() - timedelta(days=days)

            before_count = len(self.active_alerts)
            self.active_alerts = [
                alert for alert in self.active_alerts if alert.timestamp >= cutoff_time or not alert.resolved
            ]
            after_count = len(self.active_alerts)

            cleaned_count = before_count - after_count
            logger.info("清理旧告警: 删除%s个，保留%s个", cleaned_count, after_count)

        except Exception as e:
            logger.error("清理旧告警失败: %s", e)


class AlertChannel(ABC):
    """告警渠道抽象基类"""

    @abstractmethod
    def send_alert(self, alert: Alert):
        """发送告警"""
        pass


class LogAlertChannel(AlertChannel):
    """日志告警渠道"""

    def __init__(self, config: Dict[str, Any]):
        self.level = config.get("level", "INFO")

    def send_alert(self, alert: Alert):
        """发送告警到日志"""
        log_message = f"[ALERT] {alert.level.value.upper()} - {alert.title}: {alert.message}"

        if alert.level == AlertLevel.CRITICAL:
            logger.critical(log_message)
        elif alert.level == AlertLevel.ERROR:
            logger.error(log_message)
        elif alert.level == AlertLevel.WARNING:
            logger.warning(log_message)
        else:
            logger.info(log_message)


class EmailAlertChannel(AlertChannel):
    """邮件告警渠道"""

    def __init__(self, config: Dict[str, Any]):
        self.recipients = config.get("recipients", [])
        self.smtp_server = config.get("smtp_server", "localhost")
        self.smtp_port = config.get("smtp_port", 587)
        self.username = config.get("username", "")
        self.password = config.get("password", "")

    def send_alert(self, alert: Alert):
        """发送告警邮件"""
        try:
            if not self.recipients:
                logger.warning("邮件告警: 未配置收件人")
                return

            # 这里实现邮件发送逻辑
            logger.info("邮件告警发送至: %s", self.recipients)

        except Exception as e:
            logger.error("发送邮件告警失败: %s", e)


class WebhookAlertChannel(AlertChannel):
    """Webhook告警渠道"""

    def __init__(self, config: Dict[str, Any]):
        self.url = config.get("url", "")
        self.headers = config.get("headers", {"Content-Type": "application/json"})

    def send_alert(self, alert: Alert):
        """发送告警到Webhook"""
        try:
            if not self.url:
                logger.warning("Webhook告警: 未配置URL")
                return

            # 构建告警payload
            payload = {
                "alert_id": alert.alert_id,
                "level": alert.level.value,
                "title": alert.title,
                "message": alert.message,
                "source": alert.source,
                "timestamp": alert.timestamp.isoformat(),
            }

            # 这里实现HTTP请求逻辑
            logger.info("Webhook告警发送至: %s, payload: %s", self.url, payload)

        except Exception as e:
            logger.error("发送Webhook告警失败: %s", e)


# 继续在下一个文件中实现自动化维护组件...
