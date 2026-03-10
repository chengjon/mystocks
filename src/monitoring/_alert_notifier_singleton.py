"""Singleton helpers for `alert_notifier.py`."""

from __future__ import annotations

import os
from datetime import datetime
from typing import Optional

from src.monitoring.alert_notifier import Alert, AlertNotificationManager, NotificationChannel

_notification_manager: Optional[AlertNotificationManager] = None


def get_notification_manager() -> AlertNotificationManager:
    """Get or create global notification manager instance."""
    global _notification_manager
    if _notification_manager is None:
        _notification_manager = AlertNotificationManager()
    return _notification_manager


async def send_test_notification(channel: NotificationChannel):
    """Send test notification to verify channel configuration."""
    manager = get_notification_manager()

    test_alert = Alert(
        alertname="TestAlert",
        severity="info",
        service="monitoring",
        category="testing",
        instance="test-instance",
        summary="This is a test notification",
        description="If you received this, the notification channel is working correctly!",
        timestamp=datetime.now().isoformat(),
        labels={},
        annotations={},
    )

    recipients_map = {channel: [os.getenv(f"{channel.name}_RECIPIENT", "")]}
    return await manager.send_alert(test_alert, recipients_map)
