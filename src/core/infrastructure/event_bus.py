import logging
from typing import Any, Callable, Dict, List

logger = logging.getLogger(__name__)


class EventBus:
    """
    简单的同步事件总线，用于模块间解耦。
    主要用于将监控、告警等非核心业务逻辑从核心流程中分离。
    """

    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, handler: Callable):
        """订阅事件"""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)
        logger.debug("Handler subscribed to %(event_type)s")

    def emit(self, event_type: str, data: Dict[str, Any]):
        """
        发出事件
        注意：这是同步执行，处理函数应尽量轻量或自行实现异步处理
        """
        if event_type not in self._subscribers:
            return

        for handler in self._subscribers[event_type]:
            try:
                handler(data)
            except Exception as e:
                logger.error("Error handling event %(event_type)s: %(e)s")
