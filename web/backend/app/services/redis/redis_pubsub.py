"""
Redis Pub/Sub Message Bus
==========================

实时消息总线服务，基于Redis Pub/Sub实现。

功能:
1. 实时事件通知 (指标计算完成、价格更新等)
2. 系统消息广播 (配置更新、任务调度等)
3. 多订阅者支持 (一个消息可被多个消费者接收)

Version: 1.0.0
Author: MyStocks Project
"""

import json
import logging
import asyncio
from typing import Callable, Dict, Any, Optional, List
from concurrent.futures import ThreadPoolExecutor
from app.core.redis_client import get_redis_client
from app.core.config import settings

logger = logging.getLogger(__name__)


class RedisPubSubService:
    """
    Redis消息总线服务

    使用场景:
    - 指标计算完成通知: "indicator:calculated:000001:SMA"
    - 实时价格更新: "price:update:000001"
    - 任务状态变更: "task:updated:daily_calc"
    - 配置热更新: "config:reloaded"
    """

    def __init__(self):
        self.redis = get_redis_client()
        self.prefix = settings.redis_pubsub_channel_prefix
        self._pubsub = None
        self._listeners: Dict[str, List[Callable]] = {}
        self._executor = ThreadPoolExecutor(max_workers=10)
        self._running = False

    def _make_channel(self, channel: str) -> str:
        """生成带前缀的频道名"""
        return f"{self.prefix}{channel}"

    # ========== 发布 (Publisher) ==========

    def publish(self, channel: str, message: Dict[str, Any]) -> int:
        """
        发布消息到频道

        Args:
            channel: 频道名
            message: 消息内容 (字典，自动序列化为JSON)

        Returns:
            int: 接收到消息的订阅者数量
        """
        try:
            channel_name = self._make_channel(channel)
            message_str = json.dumps(message)
            count = self.redis.publish(channel_name, message_str)
            logger.debug(f"Published to {channel}: {count} subscribers")
            return count
        except Exception as e:
            logger.error(f"Failed to publish to {channel}: {e}")
            return 0

    # ========== 预定义消息发布方法 ==========

    def publish_indicator_calculated(
        self,
        stock_code: str,
        indicator_code: str,
        params: Dict[str, Any],
        success: bool = True
    ) -> int:
        """
        发布指标计算完成事件

        Args:
            stock_code: 股票代码
            indicator_code: 指标代码
            params: 计算参数
            success: 是否成功

        Returns:
            订阅者数量
        """
        return self.publish(
            "indicator:calculated",
            {
                "stock_code": stock_code,
                "indicator_code": indicator_code,
                "params": params,
                "success": success,
                "timestamp": asyncio.get_event_loop().time()
            }
        )

    def publish_price_update(
        self,
        stock_code: str,
        price: float,
        change: float,
        change_pct: float
    ) -> int:
        """
        发布实时价格更新事件

        Args:
            stock_code: 股票代码
            price: 当前价格
            change: 涨跌额
            change_pct: 涨跌幅

        Returns:
            订阅者数量
        """
        return self.publish(
            "price:update",
            {
                "stock_code": stock_code,
                "price": price,
                "change": change,
                "change_pct": change_pct,
                "timestamp": asyncio.get_event_loop().time()
            }
        )

    def publish_task_updated(
        self,
        task_id: str,
        status: str,
        progress: float,
        result: Optional[Dict] = None
    ) -> int:
        """
        发布任务状态更新事件

        Args:
            task_id: 任务ID
            status: 任务状态
            progress: 进度 (0-100)
            result: 任务结果 (可选)

        Returns:
            订阅者数量
        """
        return self.publish(
            "task:updated",
            {
                "task_id": task_id,
                "status": status,
                "progress": progress,
                "result": result,
                "timestamp": asyncio.get_event_loop().time()
            }
        )

    def publish_config_reloaded(self, config_type: str) -> int:
        """
        发布配置重载事件

        Args:
            config_type: 配置类型 (data_sources, indicators, etc.)

        Returns:
            订阅者数量
        """
        return self.publish(
            "config:reloaded",
            {
                "config_type": config_type,
                "timestamp": asyncio.get_event_loop().time()
            }
        )

    # ========== 订阅 (Subscriber) ==========

    def subscribe(self, channel: str, callback: Callable[[Dict[str, Any]], None]):
        """
        订阅频道消息

        Args:
            channel: 频道名
            callback: 消息处理回调函数

        使用示例:
        ```python
        def handler(message):
            print(f"Received: {message}")

        pubsub.subscribe("indicator:calculated", handler)
        ```
        """
        if channel not in self._listeners:
            self._listeners[channel] = []
        self._listeners[channel].append(callback)
        logger.info(f"Subscribed to channel: {channel}")

    def unsubscribe(self, channel: str, callback: Optional[Callable] = None):
        """
        取消订阅

        Args:
            channel: 频道名
            callback: 要取消的回调函数 (为None则取消该频道所有订阅)
        """
        if channel in self._listeners:
            if callback:
                self._listeners[channel].remove(callback)
                if not self._listeners[channel]:
                    del self._listeners[channel]
            else:
                del self._listeners[channel]
            logger.info(f"Unsubscribed from channel: {channel}")

    def _message_handler(self, message: Dict[str, Any]):
        """
        消息处理 (内部方法)

        Args:
            message: Redis消息对象
        """
        try:
            channel = message['channel'].replace(self.prefix, '')
            data = json.loads(message['data'])

            # 调用该频道的所有回调
            if channel in self._listeners:
                for callback in self._listeners[channel]:
                    try:
                        callback(data)
                    except Exception as e:
                        logger.error(f"Callback error for {channel}: {e}")

        except Exception as e:
            logger.error(f"Failed to handle message: {e}")

    def start_listening(self):
        """
        启动监听 (阻塞模式)

        在单独线程中运行，持续监听订阅的频道
        """
        if self._running:
            logger.warning("PubSub listener already running")
            return

        self._running = True
        self._pubsub = self.redis.pubsub()

        # 订阅所有频道
        if self._listeners:
            channels = [self._make_channel(ch) for ch in self._listeners.keys()]
            self._pubsub.subscribe(*channels)
            logger.info(f"Listening to {len(channels)} channels...")

        def _listen():
            while self._running:
                try:
                    message = self._pubsub.get_message(timeout=1.0)
                    if message:
                        self._message_handler(message)
                except Exception as e:
                    logger.error(f"PubSub listen error: {e}")

        self._executor.submit(_listen)
        logger.info("PubSub listener started")

    def stop_listening(self):
        """停止监听"""
        self._running = False
        if self._pubsub:
            self._pubsub.close()
        logger.info("PubSub listener stopped")

    # ========== 便捷方法 ==========

    async def async_publish(self, channel: str, message: Dict[str, Any]) -> int:
        """
        异步发布消息

        Args:
            channel: 频道名
            message: 消息内容

        Returns:
            订阅者数量
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._executor,
            self.publish,
            channel,
            message
        )

    def broadcast(self, message: Dict[str, Any], exclude_channel: Optional[str] = None) -> int:
        """
        广播消息到所有频道

        Args:
            message: 消息内容
            exclude_channel: 要排除的频道

        Returns:
            总订阅者数量
        """
        total = 0
        for channel in self._listeners.keys():
            if exclude_channel and channel == exclude_channel:
                continue
            total += self.publish(channel, message)
        return total


# 全局单例
redis_pubsub = RedisPubSubService()
