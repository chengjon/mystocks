"""
Local Event Bus Implementation
内存中同步事件分发，适用于单体应用和原型验证
"""

import logging
from collections import defaultdict
from typing import Callable, Dict, List, Type

from src.domain.shared.event import DomainEvent
from src.domain.shared.event_bus import IEventBus

logger = logging.getLogger(__name__)


class LocalEventBus(IEventBus):
    """
    进程内同步事件总线
    """

    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = defaultdict(list)

    def publish(self, event: DomainEvent):
        """发布事件"""
        event_name = event.event_name()
        logger.debug("Publishing event: %(event_name)s")

        # 匹配具体的类名处理器
        handlers = list(self._handlers[event_name])

        # 也匹配基类处理器 (如果是通用的)
        if event_name != "DomainEvent":
            handlers.extend(self._handlers["DomainEvent"])

        for handler in handlers:
            try:
                handler(event)
            except Exception:
                handler_name = getattr(handler, "__name__", str(handler))
                logger.error("Error handling event %(event_name)s by %(handler_name)s: %(e)s")

    def subscribe(self, event_type: Type[DomainEvent], handler: Callable):
        """订阅事件"""
        event_name = event_type.__name__
        self._handlers[event_name].append(handler)
        handler_name = getattr(handler, "__name__", str(handler))
        logger.debug("Subscribed %(handler_name)s to %(event_name)s")

    def clear_handlers(self):
        """清除所有处理器 (主要用于测试)"""
        self._handlers.clear()
