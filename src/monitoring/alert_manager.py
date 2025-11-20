"""
简化告警管理器 (Simplified Alert Manager)

删除复杂的多渠道告警系统 (邮件、Webhook),保留基础Python logging。
告警功能迁移到Grafana内置告警系统。

创建日期: 2025-11-08
版本: 2.0 (简化版)
代码行数: ~50行 (vs 原473行)
"""

import logging
from enum import Enum
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class AlertLevel(str, Enum):
    """告警级别"""

    CRITICAL = "CRITICAL"
    WARNING = "WARNING"
    INFO = "INFO"


class AlertType(str, Enum):
    """告警类型"""

    SLOW_QUERY = "SLOW_QUERY"
    DATA_QUALITY = "DATA_QUALITY"
    SYSTEM_ERROR = "SYSTEM_ERROR"
    CONNECTION_FAILURE = "CONNECTION_FAILURE"


class AlertManager:
    """
    简化告警管理器 - 仅使用Python logging

    复杂的告警功能 (邮件、Webhook、多渠道) 已迁移到Grafana。
    """

    def __init__(self):
        """初始化简化告警管理器"""
        logger.info(
            "✅ AlertManager initialized (logging-only mode, Grafana for alerts)"
        )

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

        Args:
            level: 告警级别
            alert_type: 告警类型
            title: 告警标题
            message: 告警消息
            details: 附加详情
        """
        log_msg = f"[{alert_type.value}] {title}: {message}"
        if details:
            log_msg += f" | Details: {details}"

        # 根据级别记录日志
        if level == AlertLevel.CRITICAL:
            logger.critical(log_msg)
        elif level == AlertLevel.WARNING:
            logger.warning(log_msg)
        else:
            logger.info(log_msg)

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

        Args:
            alert_level: 告警级别 (WARNING, CRITICAL, INFO)
            alert_type: 告警类型
            alert_title: 告警标题
            alert_message: 告警消息
            source: 告警来源
            classification: 数据分类
            database_type: 数据库类型
            table_name: 表名
            additional_data: 附加数据
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


# 单例实例
_alert_manager_instance = None


def get_alert_manager() -> AlertManager:
    """获取告警管理器单例实例"""
    global _alert_manager_instance
    if _alert_manager_instance is None:
        _alert_manager_instance = AlertManager()
    return _alert_manager_instance
