"""MyStocks AI告警管理器。"""

from __future__ import annotations

import logging
from typing import Optional

from src.monitoring.monitoring_database import MonitoringDatabase, get_monitoring_database

from ._ai_alert_handlers import EmailAlertHandler, LogAlertHandler, WebhookAlertHandler
from ._ai_alert_manager_core import (
    _check_threshold,
    _generate_alert_message,
    _get_metric_value,
    _handle_alert,
    _load_default_alert_rules,
    _resolve_alert,
    _save_alert_history,
    _serialize_metrics,
    _trigger_alert,
    _update_alert_stats,
    acknowledge_alert,
    add_alert_handler,
    add_alert_rule,
    check_alert_conditions,
    get_active_alerts,
    get_alert_rules,
    get_alert_summary,
    initialize_manager_state,
    remove_alert_rule,
    test_all_handlers,
    update_alert_rule,
)
from ._ai_alert_models import Alert, AlertRule, AlertSeverity, AlertType, IAlertHandler, SystemMetrics

logger = logging.getLogger(__name__)


class AIAlertManager:
    """AI告警管理器。"""

    def __init__(self, monitoring_db: Optional[MonitoringDatabase] = None):
        self._logger = logger
        self.monitoring_db = monitoring_db or get_monitoring_database()
        initialize_manager_state(self)

    _load_default_alert_rules = _load_default_alert_rules
    add_alert_handler = add_alert_handler
    add_alert_rule = add_alert_rule
    remove_alert_rule = remove_alert_rule
    check_alert_conditions = check_alert_conditions
    _get_metric_value = _get_metric_value
    _check_threshold = _check_threshold
    _trigger_alert = _trigger_alert
    _resolve_alert = _resolve_alert
    _generate_alert_message = _generate_alert_message
    _serialize_metrics = _serialize_metrics
    _save_alert_history = _save_alert_history
    _update_alert_stats = _update_alert_stats
    _handle_alert = _handle_alert
    get_active_alerts = get_active_alerts
    acknowledge_alert = acknowledge_alert
    get_alert_summary = get_alert_summary
    test_all_handlers = test_all_handlers
    get_alert_rules = get_alert_rules
    update_alert_rule = update_alert_rule


_ai_alert_manager: Optional[AIAlertManager] = None



def get_ai_alert_manager() -> AIAlertManager:
    """获取全局AI告警管理器实例。"""
    global _ai_alert_manager
    if _ai_alert_manager is None:
        _ai_alert_manager = AIAlertManager()
    return _ai_alert_manager


__all__ = [
    "AlertType",
    "AlertSeverity",
    "AlertRule",
    "Alert",
    "IAlertHandler",
    "SystemMetrics",
    "EmailAlertHandler",
    "WebhookAlertHandler",
    "LogAlertHandler",
    "AIAlertManager",
    "get_ai_alert_manager",
]
