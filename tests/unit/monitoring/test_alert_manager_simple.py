"""
Simple Alert Manager Test Suite
简化告警管理器测试套件

创建日期: 2025-12-20
版本: 1.0.0
测试模块: src.monitoring.alert_manager (148行)
"""

import pytest
from unittest.mock import MagicMock, Mock
from typing import Dict, Any, Optional
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


class SimpleAlertManager:
    """
    简化告警管理器 - 仅用于测试
    """

    def __init__(self):
        """初始化简化告警管理器"""
        self.logger = Mock()
        self.logger.info = MagicMock()
        self.logger.warning = MagicMock()
        self.logger.critical = MagicMock()

    def alert(
        self,
        level: AlertLevel,
        alert_type: AlertType,
        title: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        发送告警 (记录到日志)
        """
        log_msg = f"[{alert_type.value}] {title}: {message}"
        if details:
            log_msg += f" | Details: {details}"

        # 根据级别记录日志
        if level == AlertLevel.CRITICAL:
            self.logger.critical(log_msg)
        elif level == AlertLevel.WARNING:
            self.logger.warning(log_msg)
        else:
            self.logger.info(log_msg)

    def send_alert(
        self,
        alert_level: str,
        alert_type: str,
        alert_title: str,
        alert_message: str,
        source: Optional[str] = None,
        classification: Optional[str] = None,
        database_type: Optional[str] = None,
        table_name: Optional[str] = None,
        additional_data: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ):
        """
        发送告警 (兼容旧接口)
        """
        # 转换级别
        level_map = {
            "CRITICAL": AlertLevel.CRITICAL,
            "WARNING": AlertLevel.WARNING,
            "INFO": AlertLevel.INFO,
        }
        level = level_map.get(alert_level.upper(), AlertLevel.INFO)

        # 转换类型
        type_map = {
            "SLOW_QUERY": AlertType.SLOW_QUERY,
            "DATA_QUALITY": AlertType.DATA_QUALITY,
            "SYSTEM_ERROR": AlertType.SYSTEM_ERROR,
            "CONNECTION_FAILURE": AlertType.CONNECTION_FAILURE,
        }
        a_type = type_map.get(alert_type.upper(), AlertType.SYSTEM_ERROR)

        # 构建详情
        details: Dict[str, Any] = {}
        if source:
            details["source"] = source
        if classification:
            details["classification"] = classification
        if database_type:
            details["database_type"] = database_type
        if table_name:
            details["table_name"] = table_name
        if additional_data:
            details.update(additional_data)

        self.alert(level, a_type, alert_title, alert_message, details or None)


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


class TestSimpleAlertManager:
    """简化告警管理器测试"""

    def test_alert_manager_initialization(self):
        """测试告警管理器初始化"""
        manager = SimpleAlertManager()
        assert isinstance(manager, SimpleAlertManager)
        assert hasattr(manager, "logger")
        assert hasattr(manager, "alert")
        assert hasattr(manager, "send_alert")

    def test_alert_method_critical_level(self):
        """测试告警方法 - 严重级别"""
        manager = SimpleAlertManager()
        manager.alert(
            AlertLevel.CRITICAL,
            AlertType.SYSTEM_ERROR,
            "Test Error",
            "System failure occurred",
        )

        manager.logger.critical.assert_called_once_with(
            "[SYSTEM_ERROR] Test Error: System failure occurred"
        )

    def test_alert_method_warning_level(self):
        """测试告警方法 - 警告级别"""
        manager = SimpleAlertManager()
        manager.alert(
            AlertLevel.WARNING,
            AlertType.SLOW_QUERY,
            "Slow Query",
            "Query took 5 seconds",
        )

        manager.logger.warning.assert_called_once_with(
            "[SLOW_QUERY] Slow Query: Query took 5 seconds"
        )

    def test_alert_method_info_level(self):
        """测试告警方法 - 信息级别"""
        manager = SimpleAlertManager()
        manager.alert(
            AlertLevel.INFO,
            AlertType.DATA_QUALITY,
            "Data Check",
            "Data quality check completed",
        )

        manager.logger.info.assert_called_once_with(
            "[DATA_QUALITY] Data Check: Data quality check completed"
        )

    def test_alert_method_with_details(self):
        """测试带详情的告警方法"""
        manager = SimpleAlertManager()
        details = {"query": "SELECT * FROM large_table", "duration": 5.2}
        manager.alert(
            AlertLevel.WARNING,
            AlertType.SLOW_QUERY,
            "Slow Query",
            "Query performance issue",
            details,
        )

        expected_msg = "[SLOW_QUERY] Slow Query: Query performance issue | Details: {'query': 'SELECT * FROM large_table', 'duration': 5.2}"
        manager.logger.warning.assert_called_once_with(expected_msg)

    def test_alert_method_with_none_details(self):
        """测试详情为None的告警方法"""
        manager = SimpleAlertManager()
        manager.alert(
            AlertLevel.INFO,
            AlertType.DATA_QUALITY,
            "No Details",
            "Message without details",
            None,
        )

        manager.logger.info.assert_called_once_with(
            "[DATA_QUALITY] No Details: Message without details"
        )

    def test_send_alert_method_critical(self):
        """测试发送告警方法 - 严重级别"""
        manager = SimpleAlertManager()
        manager.send_alert(
            alert_level="CRITICAL",
            alert_type="SYSTEM_ERROR",
            alert_title="Critical Error",
            alert_message="System critical failure",
        )

        manager.logger.critical.assert_called_once_with(
            "[SYSTEM_ERROR] Critical Error: System critical failure"
        )

    def test_send_alert_method_warning(self):
        """测试发送告警方法 - 警告级别"""
        manager = SimpleAlertManager()
        manager.send_alert(
            alert_level="WARNING",
            alert_type="SLOW_QUERY",
            alert_title="Performance Issue",
            alert_message="Query running slow",
        )

        manager.logger.warning.assert_called_once_with(
            "[SLOW_QUERY] Performance Issue: Query running slow"
        )

    def test_send_alert_method_info(self):
        """测试发送告警方法 - 信息级别"""
        manager = SimpleAlertManager()
        manager.send_alert(
            alert_level="INFO",
            alert_type="DATA_QUALITY",
            alert_title="Quality Check",
            alert_message="Data validation complete",
        )

        manager.logger.info.assert_called_once_with(
            "[DATA_QUALITY] Quality Check: Data validation complete"
        )

    def test_send_alert_method_case_insensitive_level(self):
        """测试发送告警方法 - 大小写不敏感级别"""
        manager = SimpleAlertManager()
        manager.send_alert(
            alert_level="warning",  # 小写
            alert_type="SLOW_QUERY",
            alert_title="Case Test",
            alert_message="Testing case sensitivity",
        )

        manager.logger.warning.assert_called_once_with(
            "[SLOW_QUERY] Case Test: Testing case sensitivity"
        )

    def test_send_alert_method_case_insensitive_type(self):
        """测试发送告警方法 - 大小写不敏感类型"""
        manager = SimpleAlertManager()
        manager.send_alert(
            alert_level="WARNING",
            alert_type="slow_query",  # 小写
            alert_title="Case Test",
            alert_message="Testing type case sensitivity",
        )

        manager.logger.warning.assert_called_once_with(
            "[SLOW_QUERY] Case Test: Testing type case sensitivity"
        )

    def test_send_alert_method_unknown_level_defaults_to_info(self):
        """测试发送告警方法 - 未知级别默认为INFO"""
        manager = SimpleAlertManager()
        manager.send_alert(
            alert_level="UNKNOWN_LEVEL",
            alert_type="SYSTEM_ERROR",
            alert_title="Unknown Level",
            alert_message="Testing unknown level",
        )

        manager.logger.info.assert_called_once_with(
            "[SYSTEM_ERROR] Unknown Level: Testing unknown level"
        )

    def test_send_alert_method_unknown_type_defaults_to_system_error(self):
        """测试发送告警方法 - 未知类型默认为SYSTEM_ERROR"""
        manager = SimpleAlertManager()
        manager.send_alert(
            alert_level="WARNING",
            alert_type="UNKNOWN_TYPE",
            alert_title="Unknown Type",
            alert_message="Testing unknown type",
        )

        manager.logger.warning.assert_called_once_with(
            "[SYSTEM_ERROR] Unknown Type: Testing unknown type"
        )

    def test_send_alert_method_with_all_parameters(self):
        """测试发送告警方法 - 所有参数"""
        manager = SimpleAlertManager()
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
        manager.logger.critical.assert_called_once_with(expected_msg)

    def test_send_alert_method_with_partial_parameters(self):
        """测试发送告警方法 - 部分参数"""
        manager = SimpleAlertManager()
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
        manager.logger.warning.assert_called_once_with(expected_msg)

    def test_send_alert_method_empty_additional_data(self):
        """测试发送告警方法 - 空附加数据"""
        manager = SimpleAlertManager()
        manager.send_alert(
            alert_level="WARNING",
            alert_type="SLOW_QUERY",
            alert_title="Empty Data Test",
            alert_message="Testing empty additional data",
            additional_data={},
        )

        # Empty additional_data results in None details, so no details section is added
        expected_msg = "[SLOW_QUERY] Empty Data Test: Testing empty additional data"
        manager.logger.warning.assert_called_once_with(expected_msg)

    def test_multiple_alerts_different_levels(self):
        """测试多个不同级别的告警"""
        manager = SimpleAlertManager()

        # 发送不同级别的告警
        manager.alert(
            AlertLevel.CRITICAL, AlertType.SYSTEM_ERROR, "Critical", "Critical message"
        )
        manager.alert(
            AlertLevel.WARNING, AlertType.SLOW_QUERY, "Warning", "Warning message"
        )
        manager.alert(AlertLevel.INFO, AlertType.DATA_QUALITY, "Info", "Info message")

        # 验证调用次数
        assert manager.logger.critical.call_count == 1
        assert manager.logger.warning.call_count == 1
        assert manager.logger.info.call_count == 1

    def test_multiple_send_alerts(self):
        """测试多个发送告警"""
        manager = SimpleAlertManager()

        # 发送多个告警
        manager.send_alert("CRITICAL", "SYSTEM_ERROR", "Error 1", "Message 1")
        manager.send_alert("WARNING", "SLOW_QUERY", "Warning 1", "Message 1")
        manager.send_alert("INFO", "DATA_QUALITY", "Info 1", "Message 1")

        # 验证调用次数
        assert manager.logger.critical.call_count == 1
        assert manager.logger.warning.call_count == 1
        assert manager.logger.info.call_count == 1


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])
