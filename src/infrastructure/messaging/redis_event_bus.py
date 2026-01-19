"""
Redis Event Bus Implementation
基于 Redis Pub/Sub 的分布式事件总线
"""

import json
import logging
import threading
import redis
from typing import Callable, Type, Dict, List, Any, Optional
from src.domain.shared.event import DomainEvent
from src.domain.shared.event_bus import IEventBus

logger = logging.getLogger(__name__)


class RedisEventBus(IEventBus):
    """
    异步分布式事件总线
    """

    def __init__(
        self,
        host="localhost",
        port=6379,
        db=0,
        password=None,
        channel_prefix="mystocks:events:",
        redis_client: Optional[redis.Redis] = None,
    ):
        if redis_client:
            self.redis_client = redis_client
        else:
            self.redis_client = redis.Redis(host=host, port=port, db=db, password=password, decode_responses=True)

        self.channel_prefix = channel_prefix
        self._handlers: Dict[str, List[Callable]] = {}
        self._pubsub = None
        self._listen_thread = None
        self._stop_event = threading.Event()
        self._event_types: Dict[str, Type[DomainEvent]] = {}

    def publish(self, event: DomainEvent):
        """发布事件到 Redis 频道"""
        channel = f"{self.channel_prefix}{event.event_name()}"
        payload = event.to_json()
        self.redis_client.publish(channel, payload)
        logger.debug(f"Event published to Redis: {channel}")

    def subscribe(self, event_type: Type[DomainEvent], handler: Callable):
        """订阅事件"""
        event_name = event_type.__name__
        if event_name not in self._handlers:
            self._handlers[event_name] = []
            self._event_types[event_name] = event_type

        self._handlers[event_name].append(handler)

        # 如果尚未启动监听线程，则启动
        if not self._listen_thread:
            self._start_listening()

        # 订阅对应的 Redis 频道
        if self._pubsub:
            channel = f"{self.channel_prefix}{event_name}"
            self._pubsub.subscribe(channel)
            logger.info(f"Subscribed to Redis channel: {channel}")

    def _start_listening(self):
        """启动后台监听线程"""
        self._pubsub = self.redis_client.pubsub()
        self._listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._listen_thread.start()
        logger.info("Redis Event Bus listening thread started.")

    def _listen_loop(self):
        """监听循环"""
        while not self._stop_event.is_set():
            try:
                # 获取消息，超时设置防止死锁
                message = self._pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if message:
                    self._handle_raw_message(message)
            except Exception as e:
                logger.error(f"Error in Redis listen loop: {e}")

    def _handle_raw_message(self, message: Dict[str, Any]):
        """处理原始 Redis 消息"""
        channel = message["channel"]
        data_str = message["data"]

        # 从频道名提取事件名称
        event_name = channel.replace(self.channel_prefix, "")

        if event_name in self._handlers:
            try:
                data_dict = json.loads(data_str)
                event_type = self._event_types.get(event_name)

                if event_type:
                    # 反序列化为领域事件对象
                    event = event_type.from_dict(data_dict)

                    # 执行处理器
                    for handler in self._handlers[event_name]:
                        handler(event)
            except Exception as e:
                logger.error(f"Failed to handle event {event_name}: {e}")

    def stop(self):
        """停止监听"""
        self._stop_event.set()
        if self._listen_thread:
            self._listen_thread.join(timeout=2.0)
        if self._pubsub:
            self._pubsub.close()
