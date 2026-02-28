#!/usr/bin/env python3
"""
多渠道告警处理器

支持邮件、Webhook、日志等多种告警渠道的统一处理器。
提供配置化的告警路由、格式化模板、错误处理和重试机制。

作者: MyStocks AI开发团队
创建日期: 2025-11-16
版本: 1.0.0
依赖: smtplib, requests, asyncio
版权: MyStocks Project © 2025
"""

import asyncio
import json
import logging
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


# 监控组件导入
try:
    from .ai_alert_manager import Alert, AlertSeverity
except ImportError:
    Alert = Any
    AlertSeverity = Any

logger = logging.getLogger(__name__)

class MultiChannelAlertManager:
    """多渠道告警管理器"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._get_default_config()
        self.handlers: Dict[str, AlertHandler] = {}
        self.alert_history: List[Dict[str, Any]] = []

        # 初始化默认处理器
        self._initialize_default_handlers()

        logger.info("✅ 多渠道告警管理器初始化完成")

    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "max_history_size": 1000,
            "enable_history": True,
            "template_dir": Path(__file__).parent / "templates",
            "default_retry_delay": 5,
            "enable_statistics": True,
        }

    def _initialize_default_handlers(self):
        """初始化默认处理器"""

        # 添加基础日志处理器
        log_config = AlertChannelConfig(
            name="default_log",
            channel_type="log",
            severity_filter=["critical", "warning", "info"],
        )

        log_handler = LogAlertHandler(log_config, LogConfig())
        self.add_handler(log_handler)

    def add_handler(self, handler: AlertHandler) -> bool:
        """添加告警处理器"""

        try:
            self.handlers[handler.config.name] = handler
            logger.info("✅ 已添加告警处理器: %s", handler.config.name)
            return True
        except Exception as e:
            logger.error("添加告警处理器失败: %s", e)
            return False

    def remove_handler(self, handler_name: str) -> bool:
        """移除告警处理器"""

        if handler_name in self.handlers:
            del self.handlers[handler_name]
            logger.info("✅ 已移除告警处理器: %s", handler_name)
            return True
        return False

    async def send_alert(self, alert: Alert) -> Dict[str, bool]:
        """发送告警到所有启用的处理器"""

        results = {}

        # 按优先级排序处理器
        sorted_handlers = sorted(self.handlers.values(), key=lambda h: h.config.priority)

        # 并发发送到所有处理器
        tasks = []
        for handler in sorted_handlers:
            if handler.config.enabled:
                task = asyncio.create_task(self._send_with_retry(handler, alert))
                tasks.append((handler.config.name, task))

        # 收集结果
        for handler_name, task in tasks:
            try:
                success = await task
                results[handler_name] = success
            except Exception as e:
                logger.error("告警发送到%s时发生异常: %s", handler_name, e)
                results[handler_name] = False

        # 记录告警历史
        if self.config["enable_history"]:
            self._record_alert_history(alert, results)

        # 统计发送结果
        success_count = sum(1 for success in results.values() if success)
        logger.info("告警已发送到%s个渠道，成功%s个", len(results), success_count)

        return results

    async def _send_with_retry(self, handler: AlertHandler, alert: Alert) -> bool:
        """带重试的发送"""

        max_retries = handler.config.retry_config.get("max_retries", 3)
        retry_delay = handler.config.retry_config.get("retry_delay", 5)
        backoff_factor = handler.config.retry_config.get("backoff_factor", 2.0)

        for attempt in range(max_retries + 1):
            try:
                success = await handler.handle_alert(alert)
                if success:
                    return True

                # 如果不是最后一次尝试，等待后重试
                if attempt < max_retries:
                    wait_time = retry_delay * (backoff_factor**attempt)
                    await asyncio.sleep(wait_time)

            except Exception as e:
                logger.warning("告警发送尝试%s失败: %s", attempt + 1, e)
                if attempt < max_retries:
                    wait_time = retry_delay * (backoff_factor**attempt)
                    await asyncio.sleep(wait_time)

        return False

    def _record_alert_history(self, alert: Alert, results: Dict[str, bool]):
        """记录告警历史"""

        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "alert_id": alert.id,
            "rule_name": alert.rule_name,
            "severity": alert.severity.value,
            "message": alert.message,
            "channels_results": results,
            "total_channels": len(results),
            "success_count": sum(1 for success in results.values() if success),
            "failure_count": sum(1 for success in results.values() if not success),
        }

        self.alert_history.append(history_entry)

        # 限制历史大小
        if len(self.alert_history) > self.config["max_history_size"]:
            self.alert_history = self.alert_history[-self.config["max_history_size"] :]

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""

        if not self.config["enable_statistics"]:
            return {"statistics_disabled": True}

        # 整体统计
        total_alerts = len(self.alert_history)
        successful_alerts = sum(1 for entry in self.alert_history if entry["success_count"] > 0)
        failed_alerts = sum(1 for entry in self.alert_history if entry["success_count"] == 0)

        # 处理器统计
        handler_stats = {}
        for handler_name, handler in self.handlers.items():
            handler_stats[handler_name] = handler.get_statistics()

        # 严重级别统计
        severity_stats = {}
        for entry in self.alert_history:
            severity = entry["severity"]
            if severity not in severity_stats:
                severity_stats[severity] = 0
            severity_stats[severity] += 1

        # 最近告警
        recent_alerts = self.alert_history[-10:] if self.alert_history else []

        return {
            "total_alerts": total_alerts,
            "successful_alerts": successful_alerts,
            "failed_alerts": failed_alerts,
            "success_rate": f"{(successful_alerts / max(1, total_alerts) * 100):.1f}%",
            "handler_statistics": handler_stats,
            "severity_distribution": severity_stats,
            "recent_alerts": recent_alerts,
            "active_handlers": len([h for h in self.handlers.values() if h.config.enabled]),
            "total_handlers": len(self.handlers),
        }

    def add_email_handler(
        self,
        handler_name: str,
        email_config: EmailConfig,
        priority: int = 1,
        severity_filter: Optional[List[str]] = None,
    ) -> bool:
        """添加邮件处理器"""

        try:
            channel_config = AlertChannelConfig(
                name=handler_name,
                channel_type="email",
                priority=priority,
                severity_filter=severity_filter or ["critical", "warning"],
            )

            handler = EmailAlertHandler(channel_config, email_config)
            return self.add_handler(handler)

        except Exception as e:
            logger.error("添加邮件处理器失败: %s", e)
            return False

    def add_webhook_handler(
        self,
        handler_name: str,
        webhook_config: WebhookConfig,
        priority: int = 1,
        severity_filter: Optional[List[str]] = None,
    ) -> bool:
        """添加Webhook处理器"""

        try:
            channel_config = AlertChannelConfig(
                name=handler_name,
                channel_type="webhook",
                priority=priority,
                severity_filter=severity_filter or ["critical", "warning", "info"],
            )

            handler = WebhookAlertHandler(channel_config, webhook_config)
            return self.add_handler(handler)

        except Exception as e:
            logger.error("添加Webhook处理器失败: %s", e)
            return False

    def add_log_handler(
        self,
        handler_name: str,
        log_config: LogConfig,
        priority: int = 5,
        severity_filter: Optional[List[str]] = None,
    ) -> bool:
        """添加日志处理器"""

        try:
            channel_config = AlertChannelConfig(
                name=handler_name,
                channel_type="log",
                priority=priority,
                severity_filter=severity_filter or ["critical", "warning", "info"],
            )

            handler = LogAlertHandler(channel_config, log_config)
            return self.add_handler(handler)

        except Exception as e:
            logger.error("添加日志处理器失败: %s", e)
            return False

    def export_configuration(self) -> str:
        """导出配置"""

        config_data = {
            "timestamp": datetime.now().isoformat(),
            "config": self.config,
            "handlers": {},
            "alert_history": self.alert_history[-100:],  # 最近100条
        }

        # 导出处理器配置
        for name, handler in self.handlers.items():
            handler_data = {
                "config": asdict(handler.config),
                "statistics": handler.get_statistics(),
            }

            if isinstance(handler, EmailAlertHandler):
                handler_data["email_config"] = asdict(handler.email_config)
            elif isinstance(handler, WebhookAlertHandler):
                handler_data["webhook_config"] = asdict(handler.webhook_config)
            elif isinstance(handler, LogAlertHandler):
                handler_data["log_config"] = asdict(handler.log_config)

            config_data["handlers"][name] = handler_data

        return json.dumps(config_data, indent=2, default=str, ensure_ascii=False)

    async def import_configuration(self, config_json: str) -> bool:
        """导入配置"""

        try:
            config_data = json.loads(config_json)

            # 清空现有处理器
            self.handlers.clear()

            # 恢复配置
            self.config.update(config_data.get("config", {}))

            # 恢复处理器
            for name, handler_data in config_data.get("handlers", {}).items():
                try:
                    config = AlertChannelConfig(**handler_data["config"])

                    if config.channel_type == "email":
                        email_config = EmailConfig(**handler_data["email_config"])
                        handler = EmailAlertHandler(config, email_config)
                    elif config.channel_type == "webhook":
                        webhook_config = WebhookConfig(**handler_data["webhook_config"])
                        handler = WebhookAlertHandler(config, webhook_config)
                    elif config.channel_type == "log":
                        log_config = LogConfig(**handler_data["log_config"])
                        handler = LogAlertHandler(config, log_config)
                    else:
                        logger.warning("未知的处理器类型: %s", config.channel_type)
                        continue

                    self.add_handler(handler)

                except Exception as e:
                    logger.error("恢复处理器%s失败: %s", name, e)
                    continue

            # 恢复告警历史
            self.alert_history = config_data.get("alert_history", [])

            logger.info("✅ 配置导入成功: %s个处理器", len(self.handlers))
            return True

        except Exception as e:
            logger.error("配置导入失败: %s", e)
            return False


def get_multi_channel_alert_manager() -> MultiChannelAlertManager:
    """获取多渠道告警管理器单例"""
    global _multi_channel_manager

    if _multi_channel_manager is None:
        _multi_channel_manager = MultiChannelAlertManager()

    return _multi_channel_manager


async def send_alert_to_all_channels(alert: Alert) -> Dict[str, bool]:
    """发送告警到所有渠道"""
    manager = get_multi_channel_alert_manager()
    return await manager.send_alert(alert)


def add_email_alert_handler(name: str, email_config: EmailConfig) -> bool:
    """添加邮件告警处理器"""
    manager = get_multi_channel_alert_manager()
    return manager.add_email_handler(name, email_config)


def add_webhook_alert_handler(name: str, webhook_config: WebhookConfig) -> bool:
    """添加Webhook告警处理器"""
    manager = get_multi_channel_alert_manager()
    return manager.add_webhook_handler(name, webhook_config)


def add_log_alert_handler(name: str, log_config: LogConfig) -> bool:
    """添加日志告警处理器"""
    manager = get_multi_channel_alert_manager()
    return manager.add_log_handler(name, log_config)


