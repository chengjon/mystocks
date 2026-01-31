"""
测试监控告警系统模块

提供全面的测试监控、告警管理、指标分析和通知功能。
"""

from .test_integration_notifications import EmailNotificationChannel as IntegrationEmailChannel
from .test_integration_notifications import (
    IntegrationConfig,
)
from .test_integration_notifications import NotificationChannel as IntegrationNotificationChannel
from .test_integration_notifications import (
    NotificationLevel,
    NotificationManager,
    NotificationMessage,
    NotificationTemplate,
    NotificationType,
)
from .test_integration_notifications import SlackNotificationChannel as IntegrationSlackChannel
from .test_integration_notifications import (
    TemplateEngine,
    TestIntegrationManager,
)
from .test_integration_notifications import WebhookNotificationChannel as IntegrationWebhookChannel
from .test_metrics_analytics import (
    MetricCollector,
    MetricDefinition,
    MetricType,
    TestMetricsAnalyzer,
    TestVisualization,
    TimeSeriesPoint,
)
from .test_monitoring_alerts import (
    Alert,
    AlertRule,
    AlertSeverity,
    AlertStatus,
    EmailNotificationChannel,
    MetricData,
    NotificationChannel,
    SlackNotificationChannel,
    TestAlertManager,
    TestMonitor,
    WebhookNotificationChannel,
)

__all__ = [
    # 告警系统
    "AlertSeverity",
    "AlertStatus",
    "AlertRule",
    "Alert",
    "MetricData",
    "NotificationChannel",
    "EmailNotificationChannel",
    "WebhookNotificationChannel",
    "SlackNotificationChannel",
    "TestMonitor",
    "TestAlertManager",
    # 指标分析
    "MetricType",
    "MetricDefinition",
    "TimeSeriesPoint",
    "MetricCollector",
    "TestMetricsAnalyzer",
    "TestVisualization",
    # 集成通知
    "NotificationLevel",
    "NotificationType",
    "NotificationTemplate",
    "NotificationMessage",
    "IntegrationConfig",
    "NotificationChannel",
    "EmailNotificationChannel",
    "WebhookNotificationChannel",
    "SlackNotificationChannel",
    "TemplateEngine",
    "NotificationManager",
    "TestIntegrationManager",
]


# 版本信息
__version__ = "1.0.0"
__author__ = "MyStocks Testing Team"
__description__ = "Test Monitoring and Alerting System"
