"""
# 功能：数据质量监控模块，检查完整性、新鲜度和准确性
# 作者：JohnC (ninjas@sina.com) & Claude
# 创建日期：2025-10-16
# 版本：2.1.0
# 依赖：详见requirements.txt或文件导入部分
# 注意事项：
#   本文件是MyStocks v2.1核心组件，遵循5-tier数据分类架构
# 版权：MyStocks Project © 2025
"""

import logging
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta

from src.monitoring.monitoring_database import (
    MonitoringDatabase,
    get_monitoring_database,
)

logger = logging.getLogger(__name__)


class DataQualityMonitor:
    """
    数据质量监控器

    负责检查数据完整性、新鲜度和准确性,
    自动生成质量报告和告警。
    """

    # 默认阈值
    DEFAULT_MISSING_RATE_THRESHOLD = 5.0  # 缺失率阈值 5%
    DEFAULT_DELAY_THRESHOLD_SECONDS = 300  # 延迟阈值 5分钟
    DEFAULT_INVALID_RATE_THRESHOLD = 1.0  # 无效率阈值 1%

    def __init__(self, monitoring_db: Optional[MonitoringDatabase] = None):
        """
        初始化数据质量监控器

        Args:
            monitoring_db: 监控数据库实例 (可选)
        """
        self.monitoring_db = monitoring_db or get_monitoring_database()
        self._check_results = []  # 检查结果缓存

        logger.info("✅ DataQualityMonitor initialized")

    def check_completeness(
        self,
        classification: str,
        database_type: str,
        table_name: str,
        total_records: int,
        null_records: int,
        required_columns: Optional[List[str]] = None,
        threshold: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        检查数据完整性

        Args:
            classification: 数据分类
            database_type: 数据库类型
            table_name: 表名
            total_records: 总记录数
            null_records: 空值记录数
            required_columns: 必需列列表
            threshold: 缺失率阈值 (%)

        Returns:
            dict: 检查结果 {
                'check_status': 'PASS/FAIL/WARNING',
                'missing_rate': float,
                'message': str
            }
        """
        if threshold is None:
            threshold = self.DEFAULT_MISSING_RATE_THRESHOLD

        # 计算缺失率
        missing_rate = (null_records / total_records * 100) if total_records > 0 else 0

        # 判断检查状态
        if missing_rate > threshold * 2:
            check_status = "FAIL"
            check_message = f"数据缺失率严重: {missing_rate:.2f}% (阈值: {threshold}%)"
        elif missing_rate > threshold:
            check_status = "WARNING"
            check_message = f"数据缺失率偏高: {missing_rate:.2f}% (阈值: {threshold}%)"
        else:
            check_status = "PASS"
            check_message = f"数据完整性良好: 缺失率 {missing_rate:.2f}%"

        # 记录检查结果
        self.monitoring_db.log_quality_check(
            check_type="COMPLETENESS",
            classification=classification,
            database_type=database_type,
            table_name=table_name,
            check_status=check_status,
            total_records=total_records,
            null_records=null_records,
            missing_rate=missing_rate,
            check_message=check_message,
            threshold_config={"missing_rate_threshold": threshold},
        )

        # 触发告警
        if check_status in ["FAIL", "WARNING"]:
            self._create_quality_alert(
                alert_level="CRITICAL" if check_status == "FAIL" else "WARNING",
                alert_title=f"数据完整性问题: {table_name}",
                alert_message=check_message,
                classification=classification,
                database_type=database_type,
                table_name=table_name,
                check_type="COMPLETENESS",
                metrics={"missing_rate": missing_rate, "threshold": threshold},
            )

        logger.info(
            f"✓ 完整性检查: {table_name} - {check_status} ({missing_rate:.2f}%)"
        )

        return {
            "check_status": check_status,
            "missing_rate": missing_rate,
            "message": check_message,
        }

    def check_freshness(
        self,
        classification: str,
        database_type: str,
        table_name: str,
        latest_timestamp: datetime,
        expected_update_interval: Optional[timedelta] = None,
        threshold_seconds: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        检查数据新鲜度

        Args:
            classification: 数据分类
            database_type: 数据库类型
            table_name: 表名
            latest_timestamp: 最新数据时间戳
            expected_update_interval: 预期更新间隔
            threshold_seconds: 延迟阈值(秒)

        Returns:
            dict: 检查结果
        """
        if threshold_seconds is None:
            threshold_seconds = self.DEFAULT_DELAY_THRESHOLD_SECONDS

        # 计算数据延迟
        now = datetime.now()
        data_delay = now - latest_timestamp
        data_delay_seconds = int(data_delay.total_seconds())

        # 判断检查状态
        if data_delay_seconds > threshold_seconds * 3:
            check_status = "FAIL"
            check_message = f"数据严重过期: 延迟 {data_delay_seconds}秒 (阈值: {threshold_seconds}秒)"
        elif data_delay_seconds > threshold_seconds:
            check_status = "WARNING"
            check_message = f"数据更新延迟: 延迟 {data_delay_seconds}秒 (阈值: {threshold_seconds}秒)"
        else:
            check_status = "PASS"
            check_message = f"数据新鲜度良好: 延迟 {data_delay_seconds}秒"

        # 记录检查结果
        self.monitoring_db.log_quality_check(
            check_type="FRESHNESS",
            classification=classification,
            database_type=database_type,
            table_name=table_name,
            check_status=check_status,
            latest_timestamp=latest_timestamp,
            data_delay_seconds=data_delay_seconds,
            check_message=check_message,
            threshold_config={"delay_threshold_seconds": threshold_seconds},
        )

        # 触发告警
        if check_status in ["FAIL", "WARNING"]:
            self._create_quality_alert(
                alert_level="CRITICAL" if check_status == "FAIL" else "WARNING",
                alert_title=f"数据新鲜度问题: {table_name}",
                alert_message=check_message,
                classification=classification,
                database_type=database_type,
                table_name=table_name,
                check_type="FRESHNESS",
                metrics={
                    "delay_seconds": data_delay_seconds,
                    "threshold": threshold_seconds,
                },
            )

        logger.info(
            f"✓ 新鲜度检查: {table_name} - {check_status} ({data_delay_seconds}秒)"
        )

        return {
            "check_status": check_status,
            "data_delay_seconds": data_delay_seconds,
            "message": check_message,
        }

    def check_accuracy(
        self,
        classification: str,
        database_type: str,
        table_name: str,
        total_records: int,
        invalid_records: int,
        validation_rules: Optional[str] = None,
        threshold: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        检查数据准确性

        Args:
            classification: 数据分类
            database_type: 数据库类型
            table_name: 表名
            total_records: 总记录数
            invalid_records: 无效记录数
            validation_rules: 验证规则描述
            threshold: 无效率阈值 (%)

        Returns:
            dict: 检查结果
        """
        if threshold is None:
            threshold = self.DEFAULT_INVALID_RATE_THRESHOLD

        # 计算无效率
        invalid_rate = (
            (invalid_records / total_records * 100) if total_records > 0 else 0
        )

        # 判断检查状态
        if invalid_rate > threshold * 2:
            check_status = "FAIL"
            check_message = (
                f"数据准确性严重问题: 无效率 {invalid_rate:.2f}% (阈值: {threshold}%)"
            )
        elif invalid_rate > threshold:
            check_status = "WARNING"
            check_message = (
                f"数据准确性偏差: 无效率 {invalid_rate:.2f}% (阈值: {threshold}%)"
            )
        else:
            check_status = "PASS"
            check_message = f"数据准确性良好: 无效率 {invalid_rate:.2f}%"

        # 记录检查结果
        self.monitoring_db.log_quality_check(
            check_type="ACCURACY",
            classification=classification,
            database_type=database_type,
            table_name=table_name,
            check_status=check_status,
            total_records=total_records,
            invalid_records=invalid_records,
            validation_rules=validation_rules,
            check_message=check_message,
            threshold_config={"invalid_rate_threshold": threshold},
        )

        # 触发告警
        if check_status in ["FAIL", "WARNING"]:
            self._create_quality_alert(
                alert_level="CRITICAL" if check_status == "FAIL" else "WARNING",
                alert_title=f"数据准确性问题: {table_name}",
                alert_message=check_message,
                classification=classification,
                database_type=database_type,
                table_name=table_name,
                check_type="ACCURACY",
                metrics={"invalid_rate": invalid_rate, "threshold": threshold},
            )

        logger.info(
            f"✓ 准确性检查: {table_name} - {check_status} ({invalid_rate:.2f}%)"
        )

        return {
            "check_status": check_status,
            "invalid_rate": invalid_rate,
            "message": check_message,
        }

    def generate_quality_report(
        self, classification: str, database_type: str, table_name: str
    ) -> Dict[str, Any]:
        """
        生成数据质量报告

        Args:
            classification: 数据分类
            database_type: 数据库类型
            table_name: 表名

        Returns:
            dict: 质量报告 {
                'overall_status': 'PASS/WARNING/FAIL',
                'completeness': {...},
                'freshness': {...},
                'accuracy': {...},
                'timestamp': datetime
            }
        """
        report = {
            "classification": classification,
            "database_type": database_type,
            "table_name": table_name,
            "timestamp": datetime.now(),
            "checks": {"completeness": None, "freshness": None, "accuracy": None},
            "overall_status": "PASS",
        }

        # TODO: 从监控数据库查询最近的检查结果
        # 这里简化为返回基本结构

        logger.info(f"📊 质量报告生成: {table_name}")

        return report

    def _create_quality_alert(
        self,
        alert_level: str,
        alert_title: str,
        alert_message: str,
        classification: str,
        database_type: str,
        table_name: str,
        check_type: str,
        metrics: Dict[str, Any],
    ):
        """创建质量告警"""
        from src.monitoring.alert_manager import get_alert_manager

        alert_manager = get_alert_manager()

        alert_manager.send_alert(
            alert_level=alert_level,
            alert_type="DATA_QUALITY",
            alert_title=alert_title,
            alert_message=alert_message,
            source="DataQualityMonitor",
            classification=classification,
            database_type=database_type,
            table_name=table_name,
            additional_data={"check_type": check_type, "metrics": metrics},
        )

    def set_thresholds(
        self,
        missing_rate_threshold: Optional[float] = None,
        delay_threshold_seconds: Optional[int] = None,
        invalid_rate_threshold: Optional[float] = None,
    ):
        """
        设置质量检查阈值

        Args:
            missing_rate_threshold: 缺失率阈值 (%)
            delay_threshold_seconds: 延迟阈值 (秒)
            invalid_rate_threshold: 无效率阈值 (%)
        """
        if missing_rate_threshold is not None:
            self.DEFAULT_MISSING_RATE_THRESHOLD = missing_rate_threshold
        if delay_threshold_seconds is not None:
            self.DEFAULT_DELAY_THRESHOLD_SECONDS = delay_threshold_seconds
        if invalid_rate_threshold is not None:
            self.DEFAULT_INVALID_RATE_THRESHOLD = invalid_rate_threshold

        logger.info(
            f"✓ 质量阈值已更新: 缺失率={self.DEFAULT_MISSING_RATE_THRESHOLD}%, "
            f"延迟={self.DEFAULT_DELAY_THRESHOLD_SECONDS}秒, "
            f"无效率={self.DEFAULT_INVALID_RATE_THRESHOLD}%"
        )


# 全局数据质量监控器实例 (单例模式)
_quality_monitor: Optional[DataQualityMonitor] = None


def get_quality_monitor() -> DataQualityMonitor:
    """获取全局数据质量监控器实例 (单例模式)"""
    global _quality_monitor
    if _quality_monitor is None:
        _quality_monitor = DataQualityMonitor()
    return _quality_monitor


if __name__ == "__main__":
    """测试数据质量监控器"""
    import sys

    sys.path.insert(0, ".")

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    print("\n测试DataQualityMonitor...\n")

    # 创建质量监控器
    monitor = DataQualityMonitor()

    # 测试1: 完整性检查 (通过)
    print("1. 测试完整性检查 (PASS)...")
    result = monitor.check_completeness(
        classification="DAILY_KLINE",
        database_type="PostgreSQL",
        table_name="daily_kline",
        total_records=10000,
        null_records=10,  # 0.1% 缺失率
        threshold=5.0,
    )
    print(f"   结果: {result['check_status']} - {result['message']}\n")

    # 测试2: 完整性检查 (警告)
    print("2. 测试完整性检查 (WARNING)...")
    result = monitor.check_completeness(
        classification="DAILY_KLINE",
        database_type="PostgreSQL",
        table_name="daily_kline",
        total_records=10000,
        null_records=600,  # 6% 缺失率
        threshold=5.0,
    )
    print(f"   结果: {result['check_status']} - {result['message']}\n")

    # 测试3: 新鲜度检查 (通过)
    print("3. 测试新鲜度检查 (PASS)...")
    latest_time = datetime.now() - timedelta(seconds=60)  # 1分钟前
    result = monitor.check_freshness(
        classification="TICK_DATA",
        database_type="TDengine",
        table_name="tick_data",
        latest_timestamp=latest_time,
        threshold_seconds=300,  # 5分钟阈值
    )
    print(f"   结果: {result['check_status']} - {result['message']}\n")

    # 测试4: 新鲜度检查 (警告)
    print("4. 测试新鲜度检查 (WARNING)...")
    latest_time = datetime.now() - timedelta(seconds=400)  # 6.7分钟前
    result = monitor.check_freshness(
        classification="TICK_DATA",
        database_type="TDengine",
        table_name="tick_data",
        latest_timestamp=latest_time,
        threshold_seconds=300,
    )
    print(f"   结果: {result['check_status']} - {result['message']}\n")

    # 测试5: 准确性检查 (通过)
    print("5. 测试准确性检查 (PASS)...")
    result = monitor.check_accuracy(
        classification="DAILY_KLINE",
        database_type="PostgreSQL",
        table_name="daily_kline",
        total_records=10000,
        invalid_records=5,  # 0.05% 无效率
        validation_rules="price > 0 AND volume >= 0",
        threshold=1.0,
    )
    print(f"   结果: {result['check_status']} - {result['message']}\n")

    # 测试6: 生成质量报告
    print("6. 测试生成质量报告...")
    report = monitor.generate_quality_report(
        classification="DAILY_KLINE",
        database_type="PostgreSQL",
        table_name="daily_kline",
    )
    print(f"   报告生成时间: {report['timestamp']}")
    print(f"   整体状态: {report['overall_status']}\n")

    print("✅ DataQualityMonitor 所有测试完成!")
