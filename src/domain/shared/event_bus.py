"""
事件总线接口
Event Bus Interface

定义发布订阅模式的接口，用于解耦领域事件的发送和接收。
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Callable, Type

if TYPE_CHECKING:
    from .event import DomainEvent


class IEventBus(ABC):
    """
    事件总线接口

    职责：
    - 定义发布事件的方法
    - 定义订阅事件的方法
    - 解耦事件发送者和接收者
    """

    @abstractmethod
    def publish(self, event: "DomainEvent") -> None:
        """
        发布领域事件

        Args:
            event: 领域事件实例
        """

    @abstractmethod
    def subscribe(self, event_type: Type["DomainEvent"], handler: Callable[["DomainEvent"], None]) -> None:
        """
        订阅领域事件

        Args:
            event_type: 事件类型（类）
            handler: 事件处理函数
        """
