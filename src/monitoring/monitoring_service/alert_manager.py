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

import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Dict, List

from src.monitoring.monitoring_service._operation_metric_models import Alert, AlertLevel

# 导入核心模块 (US3: 已移除DataStorageStrategy)

logger = logging.getLogger("MyStocksMonitoring")

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

