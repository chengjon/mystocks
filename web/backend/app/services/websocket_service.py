"""
WebSocket服务模块

提供WebSocket连接管理、消息推送、实时通知、订阅管理等功能
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

logger = __import__("logging").getLogger(__name__)


class WebSocketState(Enum):
    """WebSocket状态"""

    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"
    CLOSING = "closing"


class MessageType(Enum):
    """消息类型"""

    TICK = "tick"
    QUOTE = "quote"
    FUND_FLOW = "fund_flow"
    ALERT = "alert"
    NOTIFICATION = "notification"


class SubscriptionType(Enum):
    """订阅类型"""

    STOCK_QUOTE = "stock_quote"
    MARKET_DATA = "market_data"
    PORTFOLIO_UPDATE = "portfolio_update"
    RISK_ALERT = "risk_alert"


@dataclass
class WebSocketMessage:
    """WebSocket消息数据类"""

    message_id: str = ""
    message_type: MessageType = MessageType.TICK
    symbol: str = ""
    payload: Any = None
    timestamp: datetime = None
    sent_at: Optional[datetime] = None

    def to_dict(self) -> Dict:
        return {
            "message_id": self.message_id,
            "message_type": self.message_type.value,
            "symbol": self.symbol,
            "payload": self.payload,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
        }


@dataclass
class Subscription:
    """订阅数据类"""

    subscription_id: str = ""
    user_id: str = ""
    subscription_type: SubscriptionType = SubscriptionType.STOCK_QUOTE
    symbols: List[str] = None
    callback_url: Optional[str] = None
    created_at: Optional[datetime] = None
    is_active: bool = True
    last_message_at: Optional[datetime] = None
    message_count: int = 0

    def to_dict(self) -> Dict:
        return {
            "subscription_id": self.subscription_id,
            "user_id": self.user_id,
            "subscription_type": self.subscription_type.value,
            "symbols": self.symbols,
            "callback_url": self.callback_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "is_active": self.is_active,
            "last_message_at": self.last_message_at.isoformat() if self.last_message_at else None,
            "message_count": self.message_count,
        }


class WebSocketClient:
    """WebSocket客户端"""

    def __init__(self, url: str, user_id: str):
        self.url = url
        self.user_id = user_id
        self.websocket = None
        self.state = WebSocketState.DISCONNECTED
        self.subscriptions = {}  # user_id -> List[Subscription]
        self.last_heartbeat_at = None
        self.message_queue = []
        self.max_queue_size = 1000
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5

        logger.info(f"WebSocket客户端初始化: {url}")

    async def connect(self) -> bool:
        """连接WebSocket服务器"""
        try:
            import websockets

            self.state = WebSocketState.CONNECTING
            logger.info(f"尝试连接到: {self.url}")

            self.websocket = await websockets.connect(self.url, ping_interval=20, ping_timeout=10, close_timeout=10)

            self.state = WebSocketState.CONNECTED
            self.last_heartbeat_at = datetime.now()
            self.reconnect_attempts = 0

            # 启动心跳
            await self._start_heartbeat()

            # 发送认证消息
            auth_message = {"type": "auth", "user_id": self.user_id, "timestamp": datetime.now().isoformat()}

            await self.send_message(auth_message)

            logger.info(f"WebSocket连接成功: {self.url}")
            return True

        except Exception as e:
            self.state = WebSocketState.ERROR
            logger.error(f"WebSocket连接失败: {e}")
            return False

    async def disconnect(self) -> bool:
        """断开WebSocket连接"""
        try:
            if self.websocket:
                self.state = WebSocketState.CLOSING

                await self.websocket.close()
                self.state = WebSocketState.DISCONNECTED

                logger.info(f"WebSocket已断开: {self.url}")
                return True
            else:
                logger.warning("WebSocket未连接")
                return False

        except Exception as e:
            logger.error(f"断开WebSocket失败: {e}")
            return False

    async def send_message(self, message: Dict) -> bool:
        """发送WebSocket消息"""
        try:
            if not self.websocket or self.state != WebSocketState.CONNECTED:
                logger.warning("WebSocket未连接，无法发送消息")
                return False

            message_json = {
                "message_id": message.get("message_id", f"msg_{datetime.now().isoformat()}"),
                "type": message.get("type", "tick"),
                "symbol": message.get("symbol", ""),
                "payload": message.get("payload"),
                "timestamp": datetime.now().isoformat(),
            }

            await self.websocket.send_json(message_json)

            message_obj = WebSocketMessage(
                message_id=message_json["message_id"],
                message_type=MessageType[message.get("type", "TICK").upper()],
                symbol=message.get("symbol", ""),
                payload=message.get("payload"),
                timestamp=datetime.now(),
            )

            self.message_queue.append(message_obj)

            if len(self.message_queue) > self.max_queue_size:
                self.message_queue = self.message_queue[-self.max_queue_size :]
                logger.warning(f"消息队列已满，已丢弃{len(self.message_queue) - self.max_queue_size}条消息")

            logger.debug(f"发送消息: {message.get('type')} - {message.get('symbol', '')}")
            return True

        except Exception as e:
            logger.error(f"发送消息失败: {e}")
            return False

    async def subscribe(
        self, subscription_type: SubscriptionType, symbols: List[str], callback_url: Optional[str] = None
    ) -> bool:
        """添加订阅"""
        try:
            import uuid

            subscription_id = f"sub_{uuid.uuid4()}"

            subscription = Subscription(
                subscription_id=subscription_id,
                user_id=self.user_id,
                subscription_type=subscription_type,
                symbols=symbols,
                callback_url=callback_url,
                created_at=datetime.now(),
            )

            self.subscriptions[subscription_id] = subscription

            # 发送订阅消息到服务器
            subscribe_message = {
                "type": "subscribe",
                "subscription_id": subscription_id,
                "subscription_type": subscription_type.value,
                "symbols": symbols,
                "timestamp": datetime.now().isoformat(),
            }

            await self.send_message(subscribe_message)

            logger.info(f"添加订阅: {subscription_type.value} - {len(symbols)}只")
            return True

        except Exception as e:
            logger.error(f"添加订阅失败: {e}")
            return False

    async def unsubscribe(self, subscription_id: str) -> bool:
        """取消订阅"""
        try:
            if subscription_id not in self.subscriptions:
                logger.warning(f"订阅不存在: {subscription_id}")
                return False

            subscription = self.subscriptions[subscription_id]
            subscription.is_active = False

            # 发送取消订阅消息到服务器
            unsubscribe_message = {
                "type": "unsubscribe",
                "subscription_id": subscription_id,
                "timestamp": datetime.now().isoformat(),
            }

            await self.send_message(unsubscribe_message)

            logger.info(f"取消订阅: {subscription_id}")
            return True

        except Exception as e:
            logger.error(f"取消订阅失败: {e}")
            return False

    async def _start_heartbeat(self):
        """启动心跳"""
        try:
            import asyncio

            await asyncio.sleep(20)
            await self._send_heartbeat()

            while self.state == WebSocketState.CONNECTED:
                await asyncio.sleep(20)
                await self._send_heartbeat()

        except asyncio.CancelledError:
            logger.info("心跳已停止")
        except Exception as e:
            logger.error(f"心跳失败: {e}")

    async def _send_heartbeat(self):
        """发送心跳"""
        try:
            heartbeat_message = {"type": "heartbeat", "timestamp": datetime.now().isoformat()}

            await self.send_message(heartbeat_message)
            self.last_heartbeat_at = datetime.now()

        except Exception as e:
            logger.error(f"发送心跳失败: {e}")

    async def handle_message(self, message: Dict) -> bool:
        """处理服务器消息"""
        try:
            message_type = message.get("type", "")

            if message_type == "tick":
                await self._handle_tick_message(message)
            elif message_type == "quote":
                await self._handle_quote_message(message)
            elif message_type == "fund_flow":
                await self._handle_fund_flow_message(message)
            elif message_type == "alert":
                await self._handle_alert_message(message)
            elif message_type == "notification":
                await self._handle_notification_message(message)
            else:
                logger.warning(f"未知消息类型: {message_type}")
                return False

            return True

        except Exception as e:
            logger.error(f"处理消息失败: {e}")
            return False

    async def _handle_tick_message(self, message: Dict):
        """处理股票行情消息"""
        try:
            subscription_id = message.get("subscription_id", "")

            if subscription_id in self.subscriptions:
                subscription = self.subscriptions[subscription_id]
                subscription.last_message_at = datetime.now()
                subscription.message_count += 1

            logger.debug(f"收到行情: {message.get('symbol')} - {message.get('payload', {})}")

        except Exception as e:
            logger.error(f"处理行情消息失败: {e}")

    async def _handle_quote_message(self, message: Dict):
        """处理报价消息"""
        try:
            logger.debug(f"收到报价: {message.get('symbol')} - {message.get('payload', {})}")

        except Exception as e:
            logger.error(f"处理报价消息失败: {e}")

    async def _handle_fund_flow_message(self, message: Dict):
        """处理资金流向消息"""
        try:
            logger.debug(f"收到资金流向: {message.get('symbol')} - {message.get('payload', {})}")

        except Exception as e:
            logger.error(f"处理资金流向消息失败: {e}")

    async def _handle_alert_message(self, message: Dict):
        """处理告警消息"""
        try:
            alert_data = message.get("payload", {})
            symbol = alert_data.get("symbol", "")
            alert_type = alert_data.get("type", "info")
            message_content = alert_data.get("message", "")

            logger.warning(f"收到告警: {symbol} - {alert_type} - {message_content}")

            # 触发对应的订阅回调
            subscription_id = alert_data.get("subscription_id", "")
            if subscription_id and subscription_id in self.subscriptions:
                callback_url = self.subscriptions[subscription_id].callback_url

                if callback_url:
                    import aiohttp

                    try:
                        async with aiohttp.ClientSession() as session:
                            async with session.post(callback_url, json=alert_data, timeout=5) as response:
                                logger.info(f"告警回调已发送: {response.status}")
                    except Exception as e:
                        logger.error(f"发送告警回调失败: {e}")

        except Exception as e:
            logger.error(f"处理告警消息失败: {e}")

    async def _handle_notification_message(self, message: Dict):
        """处理通知消息"""
        try:
            logger.info(f"收到通知: {message.get('payload', {})}")

        except Exception as e:
            logger.error(f"处理通知消息失败: {e}")

    async def broadcast_to_subscribers(self, message: Dict, symbols: List[str] = None) -> int:
        """广播消息到订阅者"""
        try:
            message_type = message.get("type", "")
            message_symbols = symbols if symbols else []

            sent_count = 0

            for subscription_id, subscription in self.subscriptions.items():
                if not subscription.is_active:
                    continue

                if subscription.subscription_type == SubscriptionType.STOCK_QUOTE:
                    if not message_symbols or subscription.symbols in message_symbols:
                        continue

                    logger.debug(f"发送消息到订阅: {subscription_id}")
                    await self._send_to_subscription(subscription_id, message)
                    sent_count += 1

            logger.info(f"广播消息完成: {message_type.value} - {sent_count}只")
            return sent_count

        except Exception as e:
            logger.error(f"广播消息失败: {e}")
            return 0

    async def _send_to_subscription(self, subscription_id: str, message: Dict):
        """发送消息到订阅"""
        try:
            subscription_message = {
                "type": "push_message",
                "subscription_id": subscription_id,
                "message": message,
                "timestamp": datetime.now().isoformat(),
            }

            await self.send_message(subscription_message)

        except Exception as e:
            logger.error(f"发送订阅消息失败: {e}")

    def get_state(self) -> Dict:
        """获取WebSocket状态"""
        return {
            "state": self.state.value,
            "url": self.url,
            "user_id": self.user_id,
            "last_heartbeat_at": self.last_heartbeat_at.isoformat() if self.last_heartbeat_at else None,
            "queue_size": len(self.message_queue),
            "subscriptions_count": len(self.subscriptions),
            "reconnect_attempts": self.reconnect_attempts,
        }


class WebSocketService:
    """WebSocket服务"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.clients = {}  # user_id -> WebSocketClient
        self.active_subscriptions = {}  # subscription_id -> List[WebSocketClient]

        logger.info("WebSocket服务初始化")

    async def create_client(self, user_id: str, url: str) -> Optional[WebSocketClient]:
        """创建WebSocket客户端"""
        try:
            client = WebSocketClient(url, user_id)

            success = await client.connect()

            if success:
                self.clients[user_id] = client
                logger.info(f"为用户{user_id}创建WebSocket客户端")
                return client
            else:
                logger.warning(f"为用户{user_id}创建WebSocket客户端失败")
                return None

        except Exception as e:
            logger.error(f"创建客户端失败: {e}")
            return None

    async def broadcast_message(self, message: Dict, symbols: List[str] = None) -> int:
        """广播消息到所有订阅者"""
        try:
            sent_count = 0

            message_type = message.get("type", "")

            for client in self.clients.values():
                if client.state == WebSocketState.CONNECTED:
                    count = await client.broadcast_to_subscribers(message, symbols)
                    sent_count += count

            logger.info(f"广播消息完成: {message_type.value} - {sent_count}次")
            return sent_count

        except Exception as e:
            logger.error(f"广播消息失败: {e}")
            return 0

    async def send_to_user(self, user_id: str, message: Dict) -> bool:
        """发送消息给指定用户"""
        try:
            if user_id not in self.clients:
                logger.warning(f"用户{user_id}未连接")
                return False

            client = self.clients[user_id]

            if client.state != WebSocketState.CONNECTED:
                logger.warning(f"用户{user_id}的WebSocket未连接")
                return False

            success = await client.send_message(message)

            if success:
                logger.info(f"消息已发送给用户{user_id}")
                return True
            else:
                logger.error(f"发送消息给用户{user_id}失败")
                return False

        except Exception as e:
            logger.error(f"发送消息给用户失败: {user_id}: {e}")
            return False

    def get_client_state(self, user_id: str) -> Optional[Dict]:
        """获取客户端状态"""
        if user_id not in self.clients:
            return None

        client = self.clients[user_id]
        return client.get_state()

    def get_all_clients_state(self) -> List[Dict]:
        """获取所有客户端状态"""
        clients_state = []

        for user_id, client in self.clients.items():
            state = client.get_state()
            if state:
                clients_state.append(state)

        return clients_state

    def get_subscription_count(self, user_id: str, subscription_type: SubscriptionType = None) -> int:
        """获取用户订阅数量"""
        if user_id not in self.clients:
            return 0

        client = self.clients[user_id]

        if subscription_type:
            count = sum(1 for sub_id, sub in client.subscriptions.items() if sub.subscription_type == subscription_type)
        else:
            count = len(client.subscriptions)

        return count

    async def disconnect_all_clients(self) -> int:
        """断开所有客户端连接"""
        try:
            disconnected_count = 0

            for user_id, client in list(self.clients.items()):
                success = await client.disconnect()
                if success:
                    disconnected_count += 1

            logger.info(f"已断开{disconnected_count}个客户端连接")
            return disconnected_count

        except Exception as e:
            logger.error(f"断开所有客户端失败: {e}")
            return 0

    def get_service_stats(self) -> Dict:
        """获取服务统计"""
        total_clients = len(self.clients)
        total_subscriptions = sum(len(client.subscriptions) for client in self.clients.values())
        message_queue_size = sum(len(client.message_queue) for client in self.clients.values())

        return {
            "total_clients": total_clients,
            "connected_clients": sum(1 for client in self.clients.values() if client.state == WebSocketState.CONNECTED),
            "total_subscriptions": total_subscriptions,
            "active_subscriptions": sum(
                1
                for client in self.clients.values()
                if client.state == WebSocketState.CONNECTED
                for sub in client.subscriptions.values()
                if sub.is_active
            ),
            "message_queue_size": message_queue_size,
            "generated_at": datetime.now().isoformat(),
        }
