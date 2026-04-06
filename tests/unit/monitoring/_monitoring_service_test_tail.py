from datetime import datetime, timedelta
from unittest.mock import patch

from src.monitoring.monitoring_service import (
    Alert,
    AlertLevel,
    AlertManager,
    EmailAlertChannel,
    LogAlertChannel,
    WebhookAlertChannel,
)


class TestAlertManager:
    """告警管理器测试"""

    def test_alert_manager_initialization_default_config(self):
        """测试告警管理器默认配置初始化"""
        manager = AlertManager()

        assert isinstance(manager.config, dict)
        assert "alert_rules" in manager.config
        assert "channels" in manager.config
        assert manager.active_alerts == []
        assert isinstance(manager.alert_channels, dict)

    def test_alert_manager_initialization_custom_config(self):
        """测试告警管理器自定义配置初始化"""
        custom_config = {
            "alert_rules": {"custom_threshold": {"threshold": 50, "unit": "count"}},
            "channels": [{"type": "log", "level": "WARNING"}],
        }

        manager = AlertManager(custom_config)

        assert manager.config == custom_config
        assert "custom_threshold" in manager.config["alert_rules"]

    def test_create_alert_basic(self):
        """测试创建基本告警"""
        manager = AlertManager()

        alert = manager.create_alert(
            level=AlertLevel.ERROR,
            title="Test Error",
            message="This is a test error alert",
            source="test_module",
        )

        assert alert.level == AlertLevel.ERROR
        assert alert.title == "Test Error"
        assert alert.message == "This is a test error alert"
        assert alert.source == "test_module"
        assert alert.alert_id.startswith(datetime.now().strftime("%Y%m%d%H%M%S"))
        assert alert in manager.active_alerts

    def test_create_alert_all_levels(self):
        """测试创建所有级别的告警"""
        manager = AlertManager()
        levels = [
            AlertLevel.INFO,
            AlertLevel.WARNING,
            AlertLevel.ERROR,
            AlertLevel.CRITICAL,
        ]
        alerts = []

        for level in levels:
            alert = manager.create_alert(
                level=level,
                title=f"Test {level.value.title()}",
                message=f"Test message for {level.value}",
                source="test_module",
            )
            alerts.append(alert)

        for index, alert in enumerate(alerts):
            assert alert.level == levels[index]

    def test_resolve_alert_existing(self):
        """测试解决存在的告警"""
        manager = AlertManager()
        alert = manager.create_alert(
            level=AlertLevel.WARNING,
            title="Test Warning",
            message="This is a test warning",
            source="test_module",
        )

        manager.resolve_alert(alert.alert_id)

        assert alert.resolved is True
        assert alert.resolve_time is not None

    def test_resolve_alert_nonexistent(self):
        """测试解决不存在的告警"""
        manager = AlertManager()
        manager.resolve_alert("nonexistent_alert_id")

    def test_get_active_alerts_no_filter(self):
        """测试获取活跃告警（无过滤器）"""
        manager = AlertManager()
        alert1 = manager.create_alert(AlertLevel.INFO, "Info 1", "Info message", "test")
        alert2 = manager.create_alert(AlertLevel.WARNING, "Warning 1", "Warning message", "test")
        alert3 = manager.create_alert(AlertLevel.ERROR, "Error 1", "Error message", "test")

        assert len({alert1.alert_id, alert2.alert_id, alert3.alert_id}) == 3

        manager.resolve_alert(alert2.alert_id)

        active_alerts = manager.get_active_alerts()
        assert len(active_alerts) == 2
        assert alert1 in active_alerts
        assert alert3 in active_alerts

    def test_get_active_alerts_with_filter(self):
        """测试获取活跃告警（带过滤器）"""
        manager = AlertManager()
        manager.create_alert(AlertLevel.INFO, "Info 1", "Info message", "test")
        manager.create_alert(AlertLevel.WARNING, "Warning 1", "Warning message", "test")
        manager.create_alert(AlertLevel.ERROR, "Error 1", "Error message", "test")

        warning_alerts = manager.get_active_alerts(level=AlertLevel.WARNING)
        error_alerts = manager.get_active_alerts(level=AlertLevel.ERROR)

        assert len(warning_alerts) == 1
        assert len(error_alerts) == 1
        assert warning_alerts[0].level == AlertLevel.WARNING
        assert error_alerts[0].level == AlertLevel.ERROR

    def test_cleanup_old_alerts(self):
        """测试清理旧告警"""
        manager = AlertManager()
        old_time = datetime.now() - timedelta(days=10)
        recent_time = datetime.now() - timedelta(days=1)

        with patch("src.monitoring.monitoring_service.alert_manager.datetime") as mock_datetime:
            mock_datetime.now.return_value = old_time
            old_alert = manager.create_alert(AlertLevel.INFO, "Old Alert", "This is old", "test")
            manager.resolve_alert(old_alert.alert_id)

            mock_datetime.now.return_value = recent_time
            new_alert = manager.create_alert(AlertLevel.WARNING, "New Alert", "This is new", "test")

            assert len(manager.active_alerts) == 2
            assert old_alert.resolved
            assert not new_alert.resolved

            manager.cleanup_old_alerts(days=7)

            assert len(manager.active_alerts) == 1
            assert new_alert in manager.active_alerts

    def test_send_alert_to_log_channel(self):
        """测试发送告警到日志渠道"""
        config = {"channels": [{"type": "log", "level": "ERROR"}]}
        manager = AlertManager(config)

        alert = manager.create_alert(AlertLevel.ERROR, "Test Error", "Test error message", "test_module")

        assert "log" in manager.alert_channels
        assert isinstance(manager.alert_channels["log"], LogAlertChannel)


class TestAlertChannels:
    """告警渠道测试"""

    def test_log_alert_channel_initialization(self):
        """测试日志告警渠道初始化"""
        channel = LogAlertChannel({"level": "WARNING"})
        assert channel.level == "WARNING"

    def test_log_alert_channel_default_level(self):
        """测试日志告警渠道默认级别"""
        channel = LogAlertChannel({})
        assert channel.level == "INFO"

    def test_log_alert_channel_send_critical(self):
        """测试发送严重日志告警"""
        channel = LogAlertChannel({})
        alert = Alert(
            alert_id="alert_001",
            level=AlertLevel.CRITICAL,
            title="Critical Alert",
            message="Critical error occurred",
            source="test",
            timestamp=datetime.now(),
        )

        with patch("src.monitoring.monitoring_service.alert_manager.logger.critical") as mock_critical:
            channel.send_alert(alert)
            mock_critical.assert_called_once()

    def test_log_alert_channel_send_error(self):
        """测试发送错误日志告警"""
        channel = LogAlertChannel({})
        alert = Alert(
            alert_id="alert_001",
            level=AlertLevel.ERROR,
            title="Error Alert",
            message="Error occurred",
            source="test",
            timestamp=datetime.now(),
        )

        with patch("src.monitoring.monitoring_service.alert_manager.logger.error") as mock_error:
            channel.send_alert(alert)
            mock_error.assert_called_once()

    def test_log_alert_channel_send_warning(self):
        """测试发送警告日志告警"""
        channel = LogAlertChannel({})
        alert = Alert(
            alert_id="alert_001",
            level=AlertLevel.WARNING,
            title="Warning Alert",
            message="Warning occurred",
            source="test",
            timestamp=datetime.now(),
        )

        with patch("src.monitoring.monitoring_service.alert_manager.logger.warning") as mock_warning:
            channel.send_alert(alert)
            mock_warning.assert_called_once()

    def test_log_alert_channel_send_info(self):
        """测试发送信息日志告警"""
        channel = LogAlertChannel({})
        alert = Alert(
            alert_id="alert_001",
            level=AlertLevel.INFO,
            title="Info Alert",
            message="Info occurred",
            source="test",
            timestamp=datetime.now(),
        )

        with patch("src.monitoring.monitoring_service.alert_manager.logger.info") as mock_info:
            channel.send_alert(alert)
            mock_info.assert_called_once()

    def test_email_alert_channel_initialization(self):
        """测试邮件告警渠道初始化"""
        config = {
            "recipients": ["admin@example.com"],
            "smtp_server": "smtp.example.com",
            "smtp_port": 587,
            "username": "user@example.com",
            "password": "password123",  # pragma: allowlist secret
        }
        channel = EmailAlertChannel(config)

        assert channel.recipients == ["admin@example.com"]
        assert channel.smtp_server == "smtp.example.com"
        assert channel.smtp_port == 587
        assert channel.username == "user@example.com"
        assert channel.password == "password123"  # pragma: allowlist secret

    def test_email_alert_channel_default_values(self):
        """测试邮件告警渠道默认值"""
        channel = EmailAlertChannel({})

        assert channel.recipients == []
        assert channel.smtp_server == "localhost"
        assert channel.smtp_port == 587
        assert channel.username == ""
        assert channel.password == ""

    def test_email_alert_channel_send_no_recipients(self):
        """测试邮件告警渠道无收件人"""
        channel = EmailAlertChannel({"recipients": []})
        alert = Alert(
            alert_id="alert_001",
            level=AlertLevel.ERROR,
            title="Test Alert",
            message="Test message",
            source="test",
            timestamp=datetime.now(),
        )

        with patch("src.monitoring.monitoring_service.alert_manager.logger") as mock_logger:
            channel.send_alert(alert)
            mock_logger.warning.assert_called_with("邮件告警: 未配置收件人")

    def test_email_alert_channel_send_with_recipients(self):
        """测试邮件告警渠道有收件人"""
        channel = EmailAlertChannel({"recipients": ["admin@example.com"]})
        alert = Alert(
            alert_id="alert_001",
            level=AlertLevel.ERROR,
            title="Test Alert",
            message="Test message",
            source="test",
            timestamp=datetime.now(),
        )

        with patch("src.monitoring.monitoring_service.alert_manager.logger") as mock_logger:
            channel.send_alert(alert)
            mock_logger.info.assert_called_with("邮件告警发送至: %s", ["admin@example.com"])

    def test_webhook_alert_channel_initialization(self):
        """测试Webhook告警渠道初始化"""
        config = {
            "url": "https://hooks.slack.com/test",
            "headers": {
                "Content-Type": "application/json",
                "Authorization": "Bearer token123",
            },
        }
        channel = WebhookAlertChannel(config)

        assert channel.url == "https://hooks.slack.com/test"
        assert channel.headers["Content-Type"] == "application/json"
        assert channel.headers["Authorization"] == "Bearer token123"

    def test_webhook_alert_channel_default_values(self):
        """测试Webhook告警渠道默认值"""
        channel = WebhookAlertChannel({})

        assert channel.url == ""
        assert channel.headers == {"Content-Type": "application/json"}

    def test_webhook_alert_channel_send_no_url(self):
        """测试Webhook告警渠道无URL"""
        channel = WebhookAlertChannel({"url": ""})
        alert = Alert(
            alert_id="alert_001",
            level=AlertLevel.ERROR,
            title="Test Alert",
            message="Test message",
            source="test",
            timestamp=datetime.now(),
        )

        with patch("src.monitoring.monitoring_service.alert_manager.logger") as mock_logger:
            channel.send_alert(alert)
            mock_logger.warning.assert_called_with("Webhook告警: 未配置URL")

    def test_webhook_alert_channel_send_with_url(self):
        """测试Webhook告警渠道有URL"""
        channel = WebhookAlertChannel({"url": "https://hooks.example.com/test"})
        alert = Alert(
            alert_id="alert_001",
            level=AlertLevel.ERROR,
            title="Test Alert",
            message="Test message",
            source="test",
            timestamp=datetime.now(),
        )

        with patch("src.monitoring.monitoring_service.alert_manager.logger") as mock_logger:
            channel.send_alert(alert)
            mock_logger.info.assert_called_once()
            message, url, payload = mock_logger.info.call_args[0]
            assert message == "Webhook告警发送至: %s, payload: %s"
            assert url == "https://hooks.example.com/test"
            assert payload["alert_id"] == "alert_001"
