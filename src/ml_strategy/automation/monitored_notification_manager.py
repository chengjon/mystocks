"""
Monitored Notification Manager
带监控的通知管理器

为 NotificationManager 添加推送监控功能，记录推送成功率和延迟。
"""

import logging
import time
from typing import Dict, List, Optional, Any
from datetime import datetime

from .notification_manager import (
    NotificationManager,
    NotificationConfig,
    Notification,
    NotificationChannel,
    NotificationLevel,
)

logger = logging.getLogger(__name__)

try:
    from src.monitoring.signal_decorator import (
        record_signal_push,
        record_push_latency,
    )
    MONITORING_AVAILABLE = True
except ImportError:
    logger.warning("信号监控模块不可用，将不记录推送指标")
    MONITORING_AVAILABLE = False


class MonitoredNotificationManager(NotificationManager):
    """
    带监控的通知管理器

    功能：
    - 继承 NotificationManager 所有功能
    - 自动记录推送成功率和延迟到 Prometheus
    - 可选记录推送日志到监控数据库
    - 提供推送统计查询

    使用示例：
        ```python
        from src.ml_strategy.automation.monitored_notification_manager import (
            MonitoredNotificationManager,
            NotificationConfig,
            NotificationChannel,
        )

        config = NotificationConfig(
            channels=[NotificationChannel.EMAIL, NotificationChannel.WEBHOOK],
            # ... 其他配置
        )

        manager = MonitoredNotificationManager(config)
        manager.send_signal_notification(
            strategy_name="MACD策略",
            symbol="600519.SH",
            signal="BUY",
            price=1850.0
        )
        ```
    """

    def __init__(
        self,
        config: Optional[NotificationConfig] = None,
        strategy_id: str = "default",
        enable_db_logging: bool = True,
    ):
        """
        初始化带监控的通知管理器

        Args:
            config: 通知配置
            strategy_id: 策略ID（用于指标分组）
            enable_db_logging: 是否启用数据库日志记录
        """
        super().__init__(config)

        self.strategy_id = strategy_id
        self.enable_db_logging = enable_db_logging

        # 推送统计
        self.push_stats = {
            "email": {"success": 0, "failed": 0, "total_latency_ms": 0},
            "webhook": {"success": 0, "failed": 0, "total_latency_ms": 0},
            "sms": {"success": 0, "failed": 0, "total_latency_ms": 0},
            "app": {"success": 0, "failed": 0, "total_latency_ms": 0},
        }

    def _send_email(self, notification: Notification) -> bool:
        """发送邮件（带监控）"""
        start_time = time.time()
        success = False

        try:
            # 调用父类方法
            success = super()._send_email(notification)
        except Exception as e:
            logger.error(f"发送邮件失败: {e}")
            success = False
        finally:
            # 记录推送指标
            latency_ms = (time.time() - start_time) * 1000
            self._record_push_result("email", success, latency_ms)

        return success

    def _send_webhook(self, notification: Notification) -> bool:
        """发送Webhook（带监控）"""
        start_time = time.time()
        success = False

        try:
            # 调用父类方法
            success = super()._send_webhook(notification)
        except Exception as e:
            logger.error(f"发送Webhook失败: {e}")
            success = False
        finally:
            # 记录推送指标
            latency_ms = (time.time() - start_time) * 1000
            self._record_push_result("webhook", success, latency_ms)

        return success

    def send_signal_notification(
        self,
        strategy_name: str,
        symbol: str,
        signal: str,
        price: float,
        context: Optional[Dict] = None,
        signal_id: Optional[int] = None,
    ) -> bool:
        """
        发送交易信号通知（带监控）

        Args:
            strategy_name: 策略名称
            symbol: 标的代码
            signal: 信号类型 (BUY/SELL/HOLD)
            price: 价格
            context: 上下文信息
            signal_id: 信号ID（可选，用于关联数据库记录）

        Returns:
            是否成功
        """
        # 调用父类方法
        success = super().send_signal_notification(
            strategy_name=strategy_name,
            symbol=symbol,
            signal=signal,
            price=price,
            context=context,
        )

        # 如果启用数据库日志，记录推送日志
        if self.enable_db_logging and signal_id:
            try:
                import asyncio

                # 异步记录到数据库（不阻塞）
                asyncio.create_task(
                    self._log_push_to_database(
                        signal_id=signal_id,
                        notification_type="signal",
                        success=success,
                        context={
                            "strategy_name": strategy_name,
                            "symbol": symbol,
                            "signal": signal,
                            "price": price,
                        },
                    )
                )
            except Exception as e:
                logger.warning(f"异步记录推送日志失败（非关键）: {e}")

        return success

    def _record_push_result(
        self,
        channel: str,
        success: bool,
        latency_ms: float,
    ) -> None:
        """
        记录推送结果

        Args:
            channel: 推送渠道
            success: 是否成功
            latency_ms: 延迟（毫秒）
        """
        # 更新统计
        if channel not in self.push_stats:
            self.push_stats[channel] = {"success": 0, "failed": 0, "total_latency_ms": 0}

        if success:
            self.push_stats[channel]["success"] += 1
            status = "success"
        else:
            self.push_stats[channel]["failed"] += 1
            status = "failed"

        self.push_stats[channel]["total_latency_ms"] += latency_ms

        # 记录到 Prometheus
        if MONITORING_AVAILABLE:
            try:
                record_signal_push(channel=channel, status=status)
                record_push_latency(channel=channel, latency_seconds=latency_ms / 1000)
            except Exception as e:
                logger.warning(f"记录 Prometheus 指标失败: {e}")

    async def _log_push_to_database(
        self,
        signal_id: int,
        notification_type: str,
        success: bool,
        context: Dict[str, Any],
    ) -> None:
        """
        记录推送日志到数据库

        Args:
            signal_id: 信号ID
            notification_type: 通知类型
            success: 是否成功
            context: 上下文信息
        """
        try:
            from src.monitoring.signal_recorder import get_signal_recorder

            recorder = get_signal_recorder()

            # 确定推送渠道
            channel = self._determine_primary_channel()

            await recorder.record_push(
                signal_id=signal_id,
                channel=channel,
                status="success" if success else "failed",
                error_message="" if success else "Push notification failed",
            )

            logger.debug(f"记录推送日志到数据库: signal_id={signal_id}, channel={channel}, success={success}")

        except Exception as e:
            logger.warning(f"记录推送日志到数据库失败（非关键）: {e}")

    def _determine_primary_channel(self) -> str:
        """确定主要推送渠道"""
        if NotificationChannel.WEBHOOK in self.config.channels:
            return "webhook"
        elif NotificationChannel.EMAIL in self.config.channels:
            return "email"
        elif NotificationChannel.LOG in self.config.channels:
            return "log"
        else:
            return "unknown"

    def get_push_statistics(self) -> Dict[str, Any]:
        """
        获取推送统计信息

        Returns:
            统计信息字典
        """
        stats = {
            "strategy_id": self.strategy_id,
            "channels": {},
            "overall": {
                "total": 0,
                "success": 0,
                "failed": 0,
                "success_rate": 0.0,
                "avg_latency_ms": 0.0,
            },
        }

        total_success = 0
        total_failed = 0
        total_latency = 0.0
        total_count = 0

        for channel, channel_stats in self.push_stats.items():
            if channel_stats["success"] + channel_stats["failed"] == 0:
                continue

            channel_total = channel_stats["success"] + channel_stats["failed"]
            channel_success_rate = (
                (channel_stats["success"] / channel_total) * 100 if channel_total > 0 else 0
            )
            channel_avg_latency = (
                (channel_stats["total_latency_ms"] / channel_total) if channel_total > 0 else 0
            )

            stats["channels"][channel] = {
                "total": channel_total,
                "success": channel_stats["success"],
                "failed": channel_stats["failed"],
                "success_rate": channel_success_rate,
                "avg_latency_ms": channel_avg_latency,
            }

            total_success += channel_stats["success"]
            total_failed += channel_stats["failed"]
            total_latency += channel_stats["total_latency_ms"]
            total_count += channel_total

        # 计算整体统计
        if total_count > 0:
            stats["overall"]["total"] = total_count
            stats["overall"]["success"] = total_success
            stats["overall"]["failed"] = total_failed
            stats["overall"]["success_rate"] = (total_success / total_count) * 100
            stats["overall"]["avg_latency_ms"] = total_latency / total_count

        return stats

    def reset_statistics(self) -> None:
        """重置统计信息"""
        for channel in self.push_stats:
            self.push_stats[channel] = {"success": 0, "failed": 0, "total_latency_ms": 0}

        logger.info(f"重置推送统计: strategy_id={self.strategy_id}")


def create_monitored_notification_manager(
    config: Optional[NotificationConfig] = None,
    strategy_id: str = "default",
    enable_db_logging: bool = True,
) -> MonitoredNotificationManager:
    """
    创建带监控的通知管理器（工厂函数）

    Args:
        config: 通知配置
        strategy_id: 策略ID
        enable_db_logging: 是否启用数据库日志记录

    Returns:
        MonitoredNotificationManager 实例
    """
    return MonitoredNotificationManager(
        config=config,
        strategy_id=strategy_id,
        enable_db_logging=enable_db_logging,
    )


__all__ = [
    "MonitoredNotificationManager",
    "create_monitored_notification_manager",
]
