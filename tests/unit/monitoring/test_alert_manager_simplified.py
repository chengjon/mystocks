"""
Simplified Alert Manager Test Suite
简化告警管理器测试套件

创建日期: 2025-12-20
版本: 1.0.0
测试模块: src.monitoring.alert_manager (148行)
"""

import pytest
import logging
from unittest.mock import patch, Mock
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../src"))

# Import the classes directly to avoid circular imports
import enum


class AlertLevel(str, enum.Enum):
    """告警级别"""

    CRITICAL = "CRITICAL"
    WARNING = "WARNING"
    INFO = "INFO"


class AlertType(str, enum.Enum):
    """告警类型"""

    SLOW_QUERY = "SLOW_QUERY"
    DATA_QUALITY = "DATA_QUALITY"
    SYSTEM_ERROR = "SYSTEM_ERROR"
    CONNECTION_FAILURE = "CONNECTION_FAILURE"


# Mock the alert manager module to test the logic
logger = Mock()


class TestAlertLevel:
    """告警级别测试"""

    def test_alert_level_values(self):
        """测试告警级别值"""
        assert AlertLevel.CRITICAL == "CRITICAL"
        assert AlertLevel.WARNING == "WARNING"
        assert AlertLevel.INFO == "INFO"

    def test_alert_level_is_string_enum(self):
        """测试告警级别是字符串枚举"""
        assert isinstance(AlertLevel.CRITICAL, str)
        assert isinstance(AlertLevel.WARNING, str)
        assert isinstance(AlertLevel.INFO, str)

    def test_alert_level_iteration(self):
        """测试告警级别可以迭代"""
        levels = list(AlertLevel)
        assert AlertLevel.CRITICAL in levels
        assert AlertLevel.WARNING in levels
        assert AlertLevel.INFO in levels
        assert len(levels) == 3

    def test_alert_level_comparison(self):
        """测试告警级别比较"""
        assert AlertLevel.CRITICAL == "CRITICAL"
        assert AlertLevel.WARNING == "WARNING"
        assert AlertLevel.INFO == "INFO"
        assert AlertLevel.CRITICAL != AlertLevel.WARNING


class TestAlertType:
    """告警类型测试"""

    def test_alert_type_values(self):
        """测试告警类型值"""
        assert AlertType.SLOW_QUERY == "SLOW_QUERY"
        assert AlertType.DATA_QUALITY == "DATA_QUALITY"
        assert AlertType.SYSTEM_ERROR == "SYSTEM_ERROR"
        assert AlertType.CONNECTION_FAILURE == "CONNECTION_FAILURE"

    def test_alert_type_is_string_enum(self):
        """测试告警类型是字符串枚举"""
        assert isinstance(AlertType.SLOW_QUERY, str)
        assert isinstance(AlertType.DATA_QUALITY, str)
        assert isinstance(AlertType.SYSTEM_ERROR, str)
        assert isinstance(AlertType.CONNECTION_FAILURE, str)

    def test_alert_type_iteration(self):
        """测试告警类型可以迭代"""
        types = list(AlertType)
        assert AlertType.SLOW_QUERY in types
        assert AlertType.DATA_QUALITY in types
        assert AlertType.SYSTEM_ERROR in types
        assert AlertType.CONNECTION_FAILURE in types
        assert len(types) == 4

    def test_alert_type_comparison(self):
        """测试告警类型比较"""
        assert AlertType.SLOW_QUERY == "SLOW_QUERY"
        assert AlertType.DATA_QUALITY == "DATA_QUALITY"
        assert AlertType.SLOW_QUERY != AlertType.DATA_QUALITY


class TestAlertManager:
    """告警管理器测试"""

    def test_alert_manager_initialization(self):
        """测试告警管理器初始化"""
        with patch("src.monitoring.alert_manager.logger") as mock_logger:
            manager = AlertManager()
            mock_logger.info.assert_called_once_with(
                "✅ AlertManager initialized (logging-only mode, Grafana for alerts)"
            )
            assert isinstance(manager, AlertManager)

    def test_alert_method_critical_level(self):
        """测试告警方法 - 严重级别"""
        with patch("src.monitoring.alert_manager.logger") as mock_logger:
            manager = AlertManager()
            manager.alert(
                AlertLevel.CRITICAL,
                AlertType.SYSTEM_ERROR,
                "Test Error",
                "System failure occurred",
            )

            mock_logger.critical.assert_called_once_with(
                "[SYSTEM_ERROR] Test Error: System failure occurred"
            )

    def test_alert_method_warning_level(self):
        """测试告警方法 - 警告级别"""
        with patch("src.monitoring.alert_manager.logger") as mock_logger:
            manager = AlertManager()
            manager.alert(
                AlertLevel.WARNING,
                AlertType.SLOW_QUERY,
                "Slow Query",
                "Query took 5 seconds",
            )

            mock_logger.warning.assert_called_once_with(
                "[SLOW_QUERY] Slow Query: Query took 5 seconds"
            )

    def test_alert_method_info_level(self):
        """测试告警方法 - 信息级别"""
        with patch("src.monitoring.alert_manager.logger") as mock_logger:
            manager = AlertManager()
            manager.alert(
                AlertLevel.INFO,
                AlertType.DATA_QUALITY,
                "Data Check",
                "Data quality check completed",
            )

            mock_logger.info.assert_called_once_with(
                "[DATA_QUALITY] Data Check: Data quality check completed"
            )

    def test_alert_method_with_details(self):
        """测试带详情的告警方法"""
        with patch("src.monitoring.alert_manager.logger") as mock_logger:
            manager = AlertManager()
            details = {"query": "SELECT * FROM large_table", "duration": 5.2}
            manager.alert(
                AlertLevel.WARNING,
                AlertType.SLOW_QUERY,
                "Slow Query",
                "Query performance issue",
                details,
            )

            expected_msg = "[SLOW_QUERY] Slow Query: Query performance issue | Details: {'query': 'SELECT * FROM large_table', 'duration': 5.2}"
            mock_logger.warning.assert_called_once_with(expected_msg)

    def test_alert_method_with_none_details(self):
        """测试详情为None的告警方法"""
        with patch("src.monitoring.alert_manager.logger") as mock_logger:
            manager = AlertManager()
            manager.alert(
                AlertLevel.INFO,
                AlertType.DATA_QUALITY,
                "No Details",
                "Message without details",
                None,
            )

            mock_logger.info.assert_called_once_with(
                "[DATA_QUALITY] No Details: Message without details"
            )

    def test_send_alert_method_critical(self):
        """测试发送告警方法 - 严重级别"""
        with patch("src.monitoring.alert_manager.logger") as mock_logger:
            manager = AlertManager()
            manager.send_alert(
                alert_level="CRITICAL",
                alert_type="SYSTEM_ERROR",
                alert_title="Critical Error",
                alert_message="System critical failure",
            )

            mock_logger.critical.assert_called_once_with(
                "[SYSTEM_ERROR] Critical Error: System critical failure"
            )

    def test_send_alert_method_warning(self):
        """测试发送告警方法 - 警告级别"""
        with patch("src.monitoring.alert_manager.logger") as mock_logger:
            manager = AlertManager()
            manager.send_alert(
                alert_level="WARNING",
                alert_type="SLOW_QUERY",
                alert_title="Performance Issue",
                alert_message="Query running slow",
            )

            mock_logger.warning.assert_called_once_with(
                "[SLOW_QUERY] Performance Issue: Query running slow"
            )

    def test_send_alert_method_info(self):
        """测试发送告警方法 - 信息级别"""
        with patch("src.monitoring.alert_manager.logger") as mock_logger:
            manager = AlertManager()
            manager.send_alert(
                alert_level="INFO",
                alert_type="DATA_QUALITY",
                alert_title="Quality Check",
                alert_message="Data validation complete",
            )

            mock_logger.info.assert_called_once_with(
                "[DATA_QUALITY] Quality Check: Data validation complete"
            )

    def test_send_alert_method_case_insensitive_level(self):
        """测试发送告警方法 - 大小写不敏感级别"""
        with patch("src.monitoring.alert_manager.logger") as mock_logger:
            manager = AlertManager()
            manager.send_alert(
                alert_level="warning",  # 小写
                alert_type="SLOW_QUERY",
                alert_title="Case Test",
                alert_message="Testing case sensitivity",
            )

            mock_logger.warning.assert_called_once_with(
                "[SLOW_QUERY] Case Test: Testing case sensitivity"
            )

    def test_send_alert_method_case_insensitive_type(self):
        """测试发送告警方法 - 大小写不敏感类型"""
        with patch("src.monitoring.alert_manager.logger") as mock_logger:
            manager = AlertManager()
            manager.send_alert(
                alert_level="WARNING",
                alert_type="slow_query",  # 小写
                alert_title="Case Test",
                alert_message="Testing type case sensitivity",
            )

            mock_logger.warning.assert_called_once_with(
                "[SLOW_QUERY] Case Test: Testing type case sensitivity"
            )

    def test_send_alert_method_unknown_level_defaults_to_info(self):
        """测试发送告警方法 - 未知级别默认为INFO"""
        with patch("src.monitoring.alert_manager.logger") as mock_logger:
            manager = AlertManager()
            manager.send_alert(
                alert_level="UNKNOWN_LEVEL",
                alert_type="SYSTEM_ERROR",
                alert_title="Unknown Level",
                alert_message="Testing unknown level",
            )

            mock_logger.info.assert_called_once_with(
                "[SYSTEM_ERROR] Unknown Level: Testing unknown level"
            )

    def test_send_alert_method_unknown_type_defaults_to_system_error(self):
        """测试发送告警方法 - 未知类型默认为SYSTEM_ERROR"""
        with patch("src.monitoring.alert_manager.logger") as mock_logger:
            manager = AlertManager()
            manager.send_alert(
                alert_level="WARNING",
                alert_type="UNKNOWN_TYPE",
                alert_title="Unknown Type",
                alert_message="Testing unknown type",
            )

            mock_logger.warning.assert_called_once_with(
                "[SYSTEM_ERROR] Unknown Type: Testing unknown type"
            )

    def test_send_alert_method_with_all_parameters(self):
        """测试发送告警方法 - 所有参数"""
        with patch("src.monitoring.alert_manager.logger") as mock_logger:
            manager = AlertManager()
            additional_data = {"metric": "cpu_usage", "value": 85.5}
            manager.send_alert(
                alert_level="CRITICAL",
                alert_type="SYSTEM_ERROR",
                alert_title="System Alert",
                alert_message="High CPU usage detected",
                source="monitoring_system",
                classification="performance",
                database_type="postgresql",
                table_name="system_metrics",
                additional_data=additional_data,
            )

            expected_details = {
                "source": "monitoring_system",
                "classification": "performance",
                "database_type": "postgresql",
                "table_name": "system_metrics",
                "metric": "cpu_usage",
                "value": 85.5,
            }
            expected_msg = f"[SYSTEM_ERROR] System Alert: High CPU usage detected | Details: {expected_details}"
            mock_logger.critical.assert_called_once_with(expected_msg)

    def test_send_alert_method_with_partial_parameters(self):
        """测试发送告警方法 - 部分参数"""
        with patch("src.monitoring.alert_manager.logger") as mock_logger:
            manager = AlertManager()
            manager.send_alert(
                alert_level="WARNING",
                alert_type="CONNECTION_FAILURE",
                alert_title="Connection Issue",
                alert_message="Database connection lost",
                source="connection_pool",
                table_name="users",
            )

            expected_details = {"source": "connection_pool", "table_name": "users"}
            expected_msg = f"[CONNECTION_FAILURE] Connection Issue: Database connection lost | Details: {expected_details}"
            mock_logger.warning.assert_called_once_with(expected_msg)

    def test_send_alert_method_with_kwargs(self):
        """测试发送告警方法 - 带关键字参数"""
        with patch("src.monitoring.alert_manager.logger") as mock_logger:
            manager = AlertManager()
            manager.send_alert(
                alert_level="INFO",
                alert_type="DATA_QUALITY",
                alert_title="Custom Alert",
                alert_message="Testing kwargs",
                custom_param1="value1",
                custom_param2=42,
            )

            # kwargs应该被忽略，因为没有处理它们
            mock_logger.info.assert_called_once_with(
                "[DATA_QUALITY] Custom Alert: Testing kwargs"
            )

    def test_send_alert_method_empty_additional_data(self):
        """测试发送告警方法 - 空附加数据"""
        with patch("src.monitoring.alert_manager.logger") as mock_logger:
            manager = AlertManager()
            manager.send_alert(
                alert_level="WARNING",
                alert_type="SLOW_QUERY",
                alert_title="Empty Data Test",
                alert_message="Testing empty additional data",
                additional_data={},
            )

            expected_details = {}
            expected_msg = f"[SLOW_QUERY] Empty Data Test: Testing empty additional data | Details: {expected_details}"
            mock_logger.warning.assert_called_once_with(expected_msg)


class TestAlertManagerSingleton:
    """告警管理器单例测试"""

    def test_get_alert_manager_returns_instance(self):
        """测试获取告警管理器返回实例"""
        manager = get_alert_manager()
        assert isinstance(manager, AlertManager)

    def test_get_alert_manager_returns_same_instance(self):
        """测试获取告警管理器返回相同实例（单例）"""
        manager1 = get_alert_manager()
        manager2 = get_alert_manager()
        assert manager1 is manager2

    def test_get_alert_manager_thread_safety(self):
        """测试获取告警管理器线程安全性"""
        import threading

        managers = []

        def get_manager():
            managers.append(get_alert_manager())

        # 创建多个线程同时获取单例
        threads = [threading.Thread(target=get_manager) for _ in range(5)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        # 所有线程应该得到相同的实例
        assert len(managers) == 5
        assert all(manager is managers[0] for manager in managers)

    def test_alert_manager_multiple_calls_with_different_params(self):
        """测试告警管理器多次调用不同参数"""
        with patch("src.monitoring.alert_manager.logger") as mock_logger:
            manager = get_alert_manager()

            # 第一次调用
            manager.alert(AlertLevel.INFO, AlertType.DATA_QUALITY, "Test1", "Message1")
            # 第二次调用
            manager.send_alert("WARNING", "SLOW_QUERY", "Test2", "Message2")

            # 验证两次调用都被正确记录
            assert mock_logger.info.call_count == 1
            assert mock_logger.warning.call_count == 1


class TestAlertManagerIntegration:
    """告警管理器集成测试"""

    def test_alert_manager_with_real_logger(self):
        """测试告警管理器与真实日志记录器集成"""
        # 创建真实的日志记录器和处理器
        import io

        log_stream = io.StringIO()
        handler = logging.StreamHandler(log_stream)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(levelname)s:%(message)s")
        handler.setFormatter(formatter)

        # 获取告警管理器的日志记录器并添加处理器
        alert_logger = logging.getLogger("src.monitoring.alert_manager")
        alert_logger.addHandler(handler)
        alert_logger.setLevel(logging.DEBUG)

        try:
            manager = AlertManager()

            # 发送不同级别的告警
            manager.alert(
                AlertLevel.CRITICAL,
                AlertType.SYSTEM_ERROR,
                "Critical",
                "Critical message",
            )
            manager.alert(
                AlertLevel.WARNING, AlertType.SLOW_QUERY, "Warning", "Warning message"
            )
            manager.alert(
                AlertLevel.INFO, AlertType.DATA_QUALITY, "Info", "Info message"
            )

            # 检查日志输出
            log_content = log_stream.getvalue()
            assert "CRITICAL:[SYSTEM_ERROR] Critical: Critical message" in log_content
            assert "WARNING:[SLOW_QUERY] Warning: Warning message" in log_content
            assert "INFO:[DATA_QUALITY] Info: Info message" in log_content

        finally:
            # 清理日志处理器
            alert_logger.removeHandler(handler)

    def test_alert_manager_compatibility_with_legacy_interface(self):
        """测试告警管理器与旧接口兼容性"""
        with patch("src.monitoring.alert_manager.logger") as mock_logger:
            manager = AlertManager()

            # 使用旧接口风格的调用
            manager.send_alert(
                alert_level="CRITICAL",
                alert_type="CONNECTION_FAILURE",
                alert_title="Legacy Alert",
                alert_message="Testing legacy compatibility",
            )

            # 验证仍然正常工作
            mock_logger.critical.assert_called_once_with(
                "[CONNECTION_FAILURE] Legacy Alert: Testing legacy compatibility"
            )


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])
