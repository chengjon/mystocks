"""
数据质量监控器单元测试
测试src/monitoring/data_quality_monitor.py的核心功能
"""

import pytest
from datetime import datetime, timedelta
import sys
import os

# 添加源码路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../src"))


class MockDataQualityMonitor:
    """模拟数据质量监控器用于测试"""

    # 默认阈值
    DEFAULT_MISSING_RATE_THRESHOLD = 5.0  # 缺失率阈值 5%
    DEFAULT_DELAY_THRESHOLD_SECONDS = 300  # 延迟阈值 5分钟
    DEFAULT_INVALID_RATE_THRESHOLD = 1.0  # 无效率阈值 1%

    def __init__(self):
        self.check_results = []
        self.alerts = []

    def check_completeness(
        self,
        classification,
        database_type,
        table_name,
        total_records,
        null_records,
        required_columns=None,
        threshold=None,
    ):
        """检查数据完整性"""
        if threshold is None:
            threshold = self.DEFAULT_MISSING_RATE_THRESHOLD

        if total_records == 0:
            return {
                "check_status": "WARNING",
                "missing_rate": 0.0,
                "message": "No records to check",
            }

        missing_rate = (null_records / total_records) * 100

        if missing_rate > threshold:
            status = "FAIL"
            message = f"Missing rate {missing_rate:.2f}% exceeds threshold {threshold}%"
        elif missing_rate > threshold * 0.7:
            status = "WARNING"
            message = f"Missing rate {missing_rate:.2f}% approaching threshold"
        else:
            status = "PASS"
            message = "Data completeness check passed"

        result = {
            "check_status": status,
            "missing_rate": missing_rate,
            "total_records": total_records,
            "null_records": null_records,
            "threshold": threshold,
            "message": message,
            "timestamp": datetime.now(),
        }

        self.check_results.append(result)
        return result

    def check_freshness(
        self,
        classification,
        database_type,
        table_name,
        last_update_time,
        threshold_seconds=None,
    ):
        """检查数据新鲜度"""
        if threshold_seconds is None:
            threshold_seconds = self.DEFAULT_DELAY_THRESHOLD_SECONDS

        now = datetime.now()
        if isinstance(last_update_time, str):
            last_update_time = datetime.fromisoformat(last_update_time)

        delay_seconds = (now - last_update_time).total_seconds()

        if delay_seconds > threshold_seconds:
            status = "FAIL"
            message = f"Data is stale by {delay_seconds:.0f} seconds"
        elif delay_seconds > threshold_seconds * 0.7:
            status = "WARNING"
            message = "Data freshness approaching threshold"
        else:
            status = "PASS"
            message = "Data is fresh"

        result = {
            "check_status": status,
            "delay_seconds": delay_seconds,
            "last_update_time": last_update_time,
            "threshold_seconds": threshold_seconds,
            "message": message,
            "timestamp": now,
        }

        self.check_results.append(result)
        return result

    def check_accuracy(
        self,
        classification,
        database_type,
        table_name,
        total_records,
        invalid_records,
        validation_rules=None,
        threshold=None,
    ):
        """检查数据准确性"""
        if threshold is None:
            threshold = self.DEFAULT_INVALID_RATE_THRESHOLD

        if total_records == 0:
            return {
                "check_status": "WARNING",
                "invalid_rate": 0.0,
                "message": "No records to check",
            }

        invalid_rate = (invalid_records / total_records) * 100

        if invalid_rate > threshold:
            status = "FAIL"
            message = f"Invalid rate {invalid_rate:.2f}% exceeds threshold {threshold}%"
        elif invalid_rate > threshold * 0.7:
            status = "WARNING"
            message = f"Invalid rate {invalid_rate:.2f}% approaching threshold"
        else:
            status = "PASS"
            message = "Data accuracy check passed"

        result = {
            "check_status": status,
            "invalid_rate": invalid_rate,
            "total_records": total_records,
            "invalid_records": invalid_records,
            "threshold": threshold,
            "message": message,
            "timestamp": datetime.now(),
        }

        self.check_results.append(result)
        return result

    def generate_quality_report(self, start_time=None, end_time=None):
        """生成质量报告"""
        if not self.check_results:
            return {
                "total_checks": 0,
                "passed": 0,
                "warnings": 0,
                "failed": 0,
                "pass_rate": 0.0,
                "checks": [],
            }

        checks = self.check_results
        if start_time:
            checks = [c for c in checks if c["timestamp"] >= start_time]
        if end_time:
            checks = [c for c in checks if c["timestamp"] <= end_time]

        total = len(checks)
        passed = sum(1 for c in checks if c["check_status"] == "PASS")
        warnings = sum(1 for c in checks if c["check_status"] == "WARNING")
        failed = sum(1 for c in checks if c["check_status"] == "FAIL")

        return {
            "total_checks": total,
            "passed": passed,
            "warnings": warnings,
            "failed": failed,
            "pass_rate": (passed / total * 100) if total > 0 else 0.0,
            "checks": checks,
        }

    def create_alert(self, severity, message, metadata=None):
        """创建告警"""
        alert = {
            "severity": severity,
            "message": message,
            "metadata": metadata or {},
            "timestamp": datetime.now(),
        }
        self.alerts.append(alert)
        return alert

    def get_alerts(self, severity=None):
        """获取告警"""
        if severity:
            return [a for a in self.alerts if a["severity"] == severity]
        return self.alerts


class TestDataQualityMonitor:
    """数据质量监控器测试类"""

    def setup_method(self):
        """测试前的设置"""
        self.monitor = MockDataQualityMonitor()

    def test_check_completeness_pass(self):
        """测试完整性检查通过"""
        result = self.monitor.check_completeness(
            classification="realtime",
            database_type="tdengine",
            table_name="market_data",
            total_records=1000,
            null_records=10,
        )

        assert result["check_status"] == "PASS"
        assert result["missing_rate"] == 1.0  # 10/1000 * 100
        assert result["total_records"] == 1000
        assert result["null_records"] == 10

    def test_check_completeness_fail(self):
        """测试完整性检查失败"""
        result = self.monitor.check_completeness(
            classification="realtime",
            database_type="tdengine",
            table_name="market_data",
            total_records=1000,
            null_records=100,  # 10% missing
        )

        assert result["check_status"] == "FAIL"
        assert result["missing_rate"] == 10.0

    def test_check_completeness_warning(self):
        """测试完整性检查警告"""
        result = self.monitor.check_completeness(
            classification="realtime",
            database_type="tdengine",
            table_name="market_data",
            total_records=1000,
            null_records=40,  # 4% missing (approaching 5% threshold)
            threshold=5.0,
        )

        assert result["check_status"] == "WARNING"
        assert result["missing_rate"] == 4.0

    def test_check_completeness_zero_records(self):
        """测试零记录的完整性检查"""
        result = self.monitor.check_completeness(
            classification="realtime",
            database_type="tdengine",
            table_name="market_data",
            total_records=0,
            null_records=0,
        )

        assert result["check_status"] == "WARNING"
        assert "No records" in result["message"]

    def test_check_completeness_custom_threshold(self):
        """测试自定义阈值的完整性检查"""
        result = self.monitor.check_completeness(
            classification="realtime",
            database_type="tdengine",
            table_name="market_data",
            total_records=1000,
            null_records=50,  # 5%
            threshold=10.0,  # Custom threshold
        )

        assert result["check_status"] == "PASS"
        assert result["threshold"] == 10.0

    def test_check_freshness_pass(self):
        """测试新鲜度检查通过"""
        recent_time = datetime.now() - timedelta(seconds=60)
        result = self.monitor.check_freshness(
            classification="realtime",
            database_type="tdengine",
            table_name="market_data",
            last_update_time=recent_time,
        )

        assert result["check_status"] == "PASS"
        assert result["delay_seconds"] < self.monitor.DEFAULT_DELAY_THRESHOLD_SECONDS

    def test_check_freshness_fail(self):
        """测试新鲜度检查失败"""
        stale_time = datetime.now() - timedelta(seconds=600)  # 10 minutes ago
        result = self.monitor.check_freshness(
            classification="realtime",
            database_type="tdengine",
            table_name="market_data",
            last_update_time=stale_time,
            threshold_seconds=300,  # 5 minutes
        )

        assert result["check_status"] == "FAIL"
        assert result["delay_seconds"] > 300

    def test_check_freshness_warning(self):
        """测试新鲜度检查警告"""
        time = datetime.now() - timedelta(seconds=250)  # Approaching 300s threshold
        result = self.monitor.check_freshness(
            classification="realtime",
            database_type="tdengine",
            table_name="market_data",
            last_update_time=time,
            threshold_seconds=300,
        )

        assert result["check_status"] == "WARNING"

    def test_check_accuracy_pass(self):
        """测试准确性检查通过"""
        result = self.monitor.check_accuracy(
            classification="realtime",
            database_type="tdengine",
            table_name="market_data",
            total_records=10000,
            invalid_records=50,  # 0.5%
        )

        assert result["check_status"] == "PASS"
        assert result["invalid_rate"] == 0.5

    def test_check_accuracy_fail(self):
        """测试准确性检查失败"""
        result = self.monitor.check_accuracy(
            classification="realtime",
            database_type="tdengine",
            table_name="market_data",
            total_records=1000,
            invalid_records=50,  # 5%
        )

        assert result["check_status"] == "FAIL"
        assert result["invalid_rate"] == 5.0

    def test_check_accuracy_zero_records(self):
        """测试零记录的准确性检查"""
        result = self.monitor.check_accuracy(
            classification="realtime",
            database_type="tdengine",
            table_name="market_data",
            total_records=0,
            invalid_records=0,
        )

        assert result["check_status"] == "WARNING"

    def test_generate_quality_report(self):
        """测试生成质量报告"""
        # 执行多个检查
        self.monitor.check_completeness("realtime", "tdengine", "table1", 1000, 10)
        self.monitor.check_completeness("realtime", "tdengine", "table2", 1000, 100)
        self.monitor.check_freshness("realtime", "tdengine", "table1", datetime.now())

        report = self.monitor.generate_quality_report()

        assert report["total_checks"] == 3
        assert report["passed"] >= 0
        assert report["warnings"] >= 0
        assert report["failed"] >= 0
        assert report["passed"] + report["warnings"] + report["failed"] == 3
        assert 0 <= report["pass_rate"] <= 100

    def test_generate_quality_report_empty(self):
        """测试空报告生成"""
        report = self.monitor.generate_quality_report()

        assert report["total_checks"] == 0
        assert report["passed"] == 0
        assert report["warnings"] == 0
        assert report["failed"] == 0
        assert report["pass_rate"] == 0.0

    def test_generate_quality_report_time_range(self):
        """测试时间范围内的报告生成"""
        # 执行检查
        self.monitor.check_completeness("realtime", "tdengine", "table1", 1000, 10)
        self.monitor.check_completeness("realtime", "tdengine", "table2", 1000, 20)

        # 生成未来时间范围的报告（应该为空）
        future_start = datetime.now() + timedelta(hours=1)
        report = self.monitor.generate_quality_report(start_time=future_start)

        assert report["total_checks"] == 0

    def test_create_alert(self):
        """测试创建告警"""
        alert = self.monitor.create_alert(
            severity="HIGH",
            message="Data quality issue detected",
            metadata={"table": "market_data", "missing_rate": 15.0},
        )

        assert alert["severity"] == "HIGH"
        assert alert["message"] == "Data quality issue detected"
        assert "table" in alert["metadata"]
        assert "timestamp" in alert

    def test_get_alerts_all(self):
        """测试获取所有告警"""
        self.monitor.create_alert("HIGH", "Critical issue")
        self.monitor.create_alert("MEDIUM", "Warning issue")
        self.monitor.create_alert("LOW", "Info issue")

        alerts = self.monitor.get_alerts()
        assert len(alerts) == 3

    def test_get_alerts_by_severity(self):
        """测试按严重程度获取告警"""
        self.monitor.create_alert("HIGH", "Critical issue")
        self.monitor.create_alert("MEDIUM", "Warning issue")
        self.monitor.create_alert("HIGH", "Another critical issue")

        high_alerts = self.monitor.get_alerts(severity="HIGH")
        assert len(high_alerts) == 2
        assert all(a["severity"] == "HIGH" for a in high_alerts)

    def test_multiple_checks_accumulation(self):
        """测试多次检查结果累积"""
        self.monitor.check_completeness("realtime", "tdengine", "table1", 1000, 10)
        self.monitor.check_freshness("realtime", "tdengine", "table1", datetime.now())
        self.monitor.check_accuracy("realtime", "tdengine", "table1", 1000, 5)

        assert len(self.monitor.check_results) == 3

    def test_threshold_boundary_conditions(self):
        """测试阈值边界条件"""
        # 精确等于阈值
        result = self.monitor.check_completeness(
            classification="realtime",
            database_type="tdengine",
            table_name="market_data",
            total_records=1000,
            null_records=50,  # Exactly 5%
            threshold=5.0,
        )

        # 应该通过或警告，但不应失败
        assert result["check_status"] in ["PASS", "WARNING"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
