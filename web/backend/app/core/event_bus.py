"""
Event Bus System - 事件总线系统

提供应用程序内部的事件驱动通信机制：
- 发布-订阅模式
- 异步事件处理
- 事件过滤和路由
- 性能监控

作者: Claude Code (Sisyphus)
日期: 2026-01-14
"""

import asyncio
import logging
from typing import Dict, List, Any, Callable, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class EventPriority(str, Enum):
    """事件优先级"""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Event:
    """事件对象"""

    id: str
    type: str
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    priority: EventPriority = EventPriority.NORMAL
    source: Optional[str] = None
    correlation_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "type": self.type,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "priority": self.priority.value,
            "source": self.source,
            "correlation_id": self.correlation_id,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Event":
        """从字典创建事件"""
        return cls(
            id=data["id"],
            type=data["type"],
            data=data["data"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            priority=EventPriority(data["priority"]),
            source=data.get("source"),
            correlation_id=data.get("correlation_id"),
        )


class EventFilter:
    """事件过滤器"""

    def __init__(
        self,
        event_types: Optional[List[str]] = None,
        sources: Optional[List[str]] = None,
        priorities: Optional[List[EventPriority]] = None,
    ):
        """
        初始化事件过滤器

        Args:
            event_types: 允许的事件类型列表
            sources: 允许的事件源列表
            priorities: 允许的优先级列表
        """
        self.event_types = set(event_types or [])
        self.sources = set(sources or [])
        self.priorities = set(priorities or [])

    def matches(self, event: Event) -> bool:
        """检查事件是否匹配过滤器"""
        if self.event_types and event.type not in self.event_types:
            return False
        if self.sources and event.source not in self.sources:
            return False
        if self.priorities and event.priority not in self.priorities:
            return False
        return True


class EventBus:
    """
    事件总线

    核心功能：
    1. 事件发布和订阅
    2. 异步事件处理
    3. 事件过滤和路由
    4. 性能监控
    5. 错误处理和重试
    """

    def __init__(self):
        """初始化事件总线"""
        self.subscribers: Dict[str, List[Dict[str, Any]]] = {}
        self.event_history: List[Event] = []
        self.max_history_size = 1000

        # 性能统计
        self.events_published = 0
        self.events_processed = 0
        self.processing_errors = 0

        # 处理队列
        self.event_queue = asyncio.Queue()
        self.processing_task: Optional[asyncio.Task] = None
        self.is_running = False

        logger.info("✅ Event Bus initialized")

    async def start(self) -> None:
        """启动事件总线"""
        if self.is_running:
            return

        self.is_running = True
        self.processing_task = asyncio.create_task(self._process_events())
        logger.info("✅ Event Bus started")

    async def stop(self) -> None:
        """停止事件总线"""
        if not self.is_running:
            return

        self.is_running = False

        if self.processing_task:
            self.processing_task.cancel()
            try:
                await self.processing_task
            except asyncio.CancelledError:
                pass

        logger.info("✅ Event Bus stopped")

    def subscribe(
        self,
        event_type: str,
        handler: Callable[[Event], None],
        filter: Optional[EventFilter] = None,
        subscriber_id: Optional[str] = None,
    ) -> str:
        """
        订阅事件

        Args:
            event_type: 事件类型
            handler: 事件处理函数
            filter: 事件过滤器
            subscriber_id: 订阅者ID

        Returns:
            订阅ID
        """
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []

        subscription_id = subscriber_id or f"{event_type}_{id(handler)}"

        subscription = {
            "id": subscription_id,
            "handler": handler,
            "filter": filter,
            "active": True,
            "events_processed": 0,
            "errors": 0,
        }

        self.subscribers[event_type].append(subscription)
        logger.debug(f"Subscribed to {event_type} with ID: {subscription_id}")
        return subscription_id

    def unsubscribe(self, event_type: str, subscription_id: str) -> bool:
        """
        取消订阅

        Args:
            event_type: 事件类型
            subscription_id: 订阅ID

        Returns:
            是否成功取消订阅
        """
        if event_type not in self.subscribers:
            return False

        for i, subscription in enumerate(self.subscribers[event_type]):
            if subscription["id"] == subscription_id:
                subscription["active"] = False
                self.subscribers[event_type].pop(i)
                logger.debug(f"Unsubscribed from {event_type} with ID: {subscription_id}")
                return True

        return False

    async def publish(self, event: Event) -> None:
        """
        发布事件

        Args:
            event: 事件对象
        """
        if not self.is_running:
            logger.warning("Event Bus is not running, event discarded")
            return

        try:
            await self.event_queue.put(event)
            self.events_published += 1

            # 添加到历史记录
            self.event_history.append(event)
            if len(self.event_history) > self.max_history_size:
                self.event_history.pop(0)

        except Exception as e:
            logger.error(f"Error publishing event {event.type}: {e}")

    async def publish_data(
        self,
        event_type: str,
        data: Dict[str, Any],
        priority: EventPriority = EventPriority.NORMAL,
        source: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> None:
        """
        发布数据事件（便捷方法）

        Args:
            event_type: 事件类型
            data: 事件数据
            priority: 事件优先级
            source: 事件源
            correlation_id: 关联ID
        """
        import uuid

        event = Event(
            id=str(uuid.uuid4()),
            type=event_type,
            data=data,
            priority=priority,
            source=source,
            correlation_id=correlation_id,
        )
        await self.publish(event)

    async def _process_events(self) -> None:
        """事件处理循环"""
        while self.is_running:
            try:
                event = await self.event_queue.get()

                await self._dispatch_event(event)
                self.event_queue.task_done()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error processing event: {e}")
                self.processing_errors += 1

    async def _dispatch_event(self, event: Event) -> None:
        """分发事件到订阅者"""
        if event.type not in self.subscribers:
            return

        active_subscribers = [sub for sub in self.subscribers[event.type] if sub["active"]]

        if not active_subscribers:
            return

        tasks = []
        for subscription in active_subscribers:
            if subscription["filter"] and not subscription["filter"].matches(event):
                continue

            task = asyncio.create_task(self._handle_event(subscription, event))
            tasks.append(task)

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _handle_event(self, subscription: Dict[str, Any], event: Event) -> None:
        """处理单个订阅者的事件"""
        try:
            await subscription["handler"](event)
            subscription["events_processed"] += 1
            self.events_processed += 1

        except Exception as e:
            subscription["errors"] += 1
            logger.error(f"Error in event handler {subscription['id']}: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        total_subscribers = sum(len(subs) for subs in self.subscribers.values())

        return {
            "events_published": self.events_published,
            "events_processed": self.events_processed,
            "processing_errors": self.processing_errors,
            "active_subscribers": total_subscribers,
            "event_types": list(self.subscribers.keys()),
            "queue_size": self.event_queue.qsize(),
            "history_size": len(self.event_history),
        }

    def get_subscribers(self, event_type: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """获取订阅者信息"""
        if event_type:
            return {event_type: self.subscribers.get(event_type, [])}
        return self.subscribers.copy()

    def clear_history(self) -> None:
        """清空事件历史"""
        self.event_history.clear()

    async def wait_for_event(
        self,
        event_type: str,
        timeout: float = 10.0,
        filter: Optional[EventFilter] = None,
    ) -> Optional[Event]:
        """
        等待特定事件

        Args:
            event_type: 事件类型
            timeout: 超时时间（秒）
            filter: 事件过滤器

        Returns:
            匹配的事件，如果超时则返回None
        """
        future = asyncio.Future()

        def handler(event: Event):
            if not future.done():
                if filter and not filter.matches(event):
                    return
                future.set_result(event)

        subscription_id = self.subscribe(event_type, handler)

        try:
            return await asyncio.wait_for(future, timeout=timeout)
        except asyncio.TimeoutError:
            return None
        finally:
            self.unsubscribe(event_type, subscription_id)


# 全局事件总线实例
_event_bus_instance: Optional[EventBus] = None


def get_event_bus() -> EventBus:
    """获取全局事件总线实例"""
    global _event_bus_instance
    if _event_bus_instance is None:
        _event_bus_instance = EventBus()
    return _event_bus_instance


async def start_event_bus() -> None:
    """启动全局事件总线"""
    bus = get_event_bus()
    await bus.start()


async def stop_event_bus() -> None:
    """停止全局事件总线"""
    bus = get_event_bus()
    await bus.stop()


# 便捷函数
async def publish_event(
    event_type: str,
    data: Dict[str, Any],
    priority: EventPriority = EventPriority.NORMAL,
    source: Optional[str] = None,
) -> None:
    """发布事件（便捷函数）"""
    bus = get_event_bus()
    await bus.publish_data(event_type, data, priority, source)


def subscribe_event(
    event_type: str,
    handler: Callable[[Event], None],
    filter: Optional[EventFilter] = None,
) -> str:
    """订阅事件（便捷函数）"""
    bus = get_event_bus()
    return bus.subscribe(event_type, handler, filter)
