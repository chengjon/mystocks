"""
Signal Push Service Integration

信号推送服务集成示例 - 展示如何将监控装饰器与推送服务结合使用。

功能：
- 为推送服务添加监控指标
- 记录推送成功率和延迟
- 兼容现有NotificationManager

使用方式：
```python
from src.monitoring.signal_decorator import (
    monitor_signal_push,
    SignalMetricsCollector,
)
from src.ml_strategy.automation.notification_manager import (
    NotificationManager,
    NotificationChannel,
)

# 创建带监控的推送服务
class MonitoredNotificationManager(NotificationManager):
    '''带监控的NotificationManager'''

    @monitor_signal_push("email")
    def send_email(self, notification):
        '''发送邮件（带监控）'''
        return super()._send_email(notification)

    @monitor_signal_push("webhook")
    def send_webhook(self, notification):
        '''发送Webhook（带监控）'''
        return super()._send_webhook(notification)

# 或使用MetricsCollector批量收集指标
collector = SignalMetricsCollector(strategy_id="default")

# 在定时任务中更新指标
def update_metrics_task():
    collector.calculate_and_update()
```
"""

import time
import logging
from typing import List, Dict, Any, Optional, Callable
from functools import wraps
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    from src.monitoring.signal_decorator import (
        record_signal_push,
        record_push_latency,
        update_strategy_health,
    )
except ImportError:
    logger.warning("Signal decorator module not available")
    record_signal_push = None
    record_push_latency = None
    update_strategy_health = None


class PushServiceMonitor:
    """
    推送服务监控器 - 包装现有的推送方法，添加监控功能

    Usage:
        ```python
        from src.ml_strategy.automation.notification_manager import NotificationManager
        from src.monitoring.signal_decorator import PushServiceMonitor

        monitor = PushServiceMonitor(NotificationManager)

        class MonitoredNotificationManager(monitor.wrap()):
            pass
        ```
    """

    def __init__(self, strategy_id: str = "default"):
        self.strategy_id = strategy_id
        self._channel_stats: Dict[str, Dict[str, Any]] = {}

    def wrap_send_email(self, original_method: Callable) -> Callable:
        """包装邮件发送方法"""

        @wraps(original_method)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = original_method(*args, **kwargs)
                latency_ms = (time.time() - start_time) * 1000
                self._record_push_result("email", True, latency_ms)
                return result
            except Exception as e:
                latency_ms = (time.time() - start_time) * 1000
                self._record_push_result("email", False, latency_ms)
                raise

        return wrapper

    def wrap_send_webhook(self, original_method: Callable) -> Callable:
        """包装Webhook发送方法"""

        @wraps(original_method)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = original_method(*args, **kwargs)
                latency_ms = (time.time() - start_time) * 1000
                self._record_push_result("webhook", True, latency_ms)
                return result
            except Exception as e:
                latency_ms = (time.time() - start_time) * 1000
                self._record_push_result("webhook", False, latency_ms)
                raise

        return wrapper

    def _record_push_result(self, channel: str, success: bool, latency_ms: float) -> None:
        """记录推送结果"""
        status = "success" if success else "failed"

        if channel not in self._channel_stats:
            self._channel_stats[channel] = {"success": 0, "failed": 0, "total_latency_ms": 0.0}

        if success:
            self._channel_stats[channel]["success"] += 1
        else:
            self._channel_stats[channel]["failed"] += 1
        self._channel_stats[channel]["total_latency_ms"] += latency_ms

        if record_signal_push:
            record_signal_push(channel=channel, status=status)

        if record_push_latency:
            record_push_latency(channel=channel, latency_seconds=latency_ms / 1000)

    def get_channel_stats(self) -> Dict[str, Dict[str, Any]]:
        """获取各渠道统计"""
        return self._channel_stats.copy()

    def get_overall_success_rate(self) -> float:
        """计算整体成功率"""
        total = 0
        success = 0
        for stats in self._channel_stats.values():
            total += stats["success"] + stats["failed"]
            success += stats["success"]

        return (success / total * 100) if total > 0 else 0.0


def create_monitored_notification_manager(original_manager: Any, strategy_id: str = "default") -> Any:
    """
    创建带监控的NotificationManager

    Args:
        original_manager: 原始NotificationManager实例
        strategy_id: 策略ID

    Returns:
        包装后的Manager（保留所有原有方法）
    """

    class MonitoredNotificationManager(type(original_manager)):
        """带监控的NotificationManager"""

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._push_monitor = PushServiceMonitor(strategy_id)
            self._strategy_id = strategy_id

        def _send_email(self, notification):
            """发送邮件（带监控）"""
            wrapped = self._push_monitor.wrap_send_email(super()._send_email)
            return wrapped(notification)

        def _send_webhook(self, notification):
            """发送Webhook（带监控）"""
            wrapped = self._push_monitor.wrap_send_webhook(super()._send_webhook)
            return wrapped(notification)

        def get_push_stats(self) -> Dict[str, Any]:
            """获取推送统计"""
            return {
                "strategy_id": self._strategy_id,
                "channel_stats": self._push_monitor.get_channel_stats(),
                "overall_success_rate": self._push_monitor.get_overall_success_rate(),
            }

    return MonitoredNotificationManager(*original_manager.__dict__, strategy_id=strategy_id)


class AsyncPushServiceMonitor:
    """
    异步推送服务监控器 - 用于WebSocket等异步推送

    Usage:
        ```python
        class WebSocketPushService:
            def __init__(self):
                self.monitor = AsyncPushServiceMonitor("websocket")

            @monitor.decorate()
            async def broadcast(self, message):
                ...
        ```
    """

    def __init__(self, channel: str, strategy_id: str = "default"):
        self.channel = channel
        self.strategy_id = strategy_id

    def decorate(self, func: Callable) -> Callable:
        """装饰器工厂"""

        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                latency_ms = (time.time() - start_time) * 1000
                self._record_result(True, latency_ms)
                return result
            except Exception as e:
                latency_ms = (time.time() - start_time) * 1000
                self._record_result(False, latency_ms)
                raise

        return wrapper

    def _record_result(self, success: bool, latency_ms: float) -> None:
        """记录推送结果"""
        status = "success" if success else "failed"

        if record_signal_push:
            record_signal_push(channel=self.channel, status=status)

        if record_push_latency:
            record_push_latency(channel=self.channel, latency_seconds=latency_ms / 1000)


__all__ = [
    "PushServiceMonitor",
    "AsyncPushServiceMonitor",
    "create_monitored_notification_manager",
]
