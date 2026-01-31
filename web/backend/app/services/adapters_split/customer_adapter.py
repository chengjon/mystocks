"""
客户端数据源适配器

提供WebSocket实时行情推送功能，支持股票、基金、指数等
"""

import logging
import asyncio
from typing import Any, Dict, List, Optional
from datetime import datetime
import json
import websockets

from .base_adapter import BaseAdapter
from app.core.database import db_service
from app.services.data_quality_monitor import get_data_quality_monitor

logger = __import__("logging").getLogger(__name__)


class CustomerAdapter(BaseAdapter):
    """客户端数据源适配器"""

    def __init__(self, ws_url: str = "ws://localhost:8000/ws"):
        super().__init__(name="Customer", source_type="customer")
        self.db_service = db_service
        self.quality_monitor = get_data_quality_monitor()
        self.websocket = None
        self.subscriptions = set()
        self.max_retries = 3
        self.reconnect_interval = 5

        logger.info(f"初始化{self.name}适配器")
        asyncio.create_task(self._connect_websocket())

    async def _connect_websocket(self):
        """连接WebSocket"""
        try:
            logger.info(f"连接WebSocket: {self.ws_url}")
            self.websocket = await websockets.connect(self.ws_url)
            logger.info(f"{self.name} WebSocket连接成功")

            await self._subscribe_all_channels()

        except Exception as e:
            logger.error(f"{self.name} WebSocket连接失败: {e}")
            await asyncio.sleep(self.reconnect_interval)
            raise

    async def _subscribe_all_channels(self):
        """订阅所有频道"""
        try:
            channels = ["stock_realtime", "fund_flow", "board_data", "index_data"]

            for channel in channels:
                subscribe_message = {"channel": channel, "action": "subscribe"}
                await self.websocket.send(json.dumps(subscribe_message))
                self.subscriptions.add(channel)

                logger.debug(f"{self.name} 订阅频道: {channel}")

        except Exception as e:
            logger.error(f"{self.name} 订阅频道失败: {e}")

    async def get_stock_basic(self, stock_code: str) -> Optional[Dict]:
        """获取股票基本信息"""
        try:
            self._log_request_start("get_stock_basic", {"stock_code": stock_code})

            request_message = {"channel": "stock_basic", "action": "query", "params": {"code": stock_code}}

            await self.websocket.send(json.dumps(request_message))

            await asyncio.sleep(1)

            return await self._receive_message(stock_code)

        except Exception as e:
            self._log_request_error("get_stock_basic", e)
            return None

    async def get_stock_daily(self, stock_code: str, start_date: str, end_date: str) -> Optional[List[Dict]]:
        """获取日线数据"""
        try:
            self._log_request_start(
                "get_stock_daily", {"stock_code": stock_code, "start_date": start_date, "end_date": end_date}
            )

            request_message = {
                "channel": "stock_daily",
                "action": "query",
                "params": {"code": stock_code, "start_date": start_date, "end_date": end_date},
            }

            await self.websocket.send(json.dumps(request_message))

            await asyncio.sleep(1)

            return await self._receive_messages(stock_code)

        except Exception as e:
            self._log_request_error("get_stock_daily", e)
            return []

    async def get_realtime_quotes(self, stock_codes: List[str]) -> Optional[List[Dict]]:
        """获取实时行情"""
        try:
            self._log_request_start("get_realtime_quotes", {"stock_codes": stock_codes})

            request_message = {"channel": "stock_realtime", "action": "query", "params": {"codes": stock_codes}}

            await self.websocket.send(json.dumps(request_message))

            await asyncio.sleep(1)

            return await self._receive_messages()

        except Exception as e:
            self._log_request_error("get_realtime_quotes", e)
            return []

    async def _receive_message(self, stock_code: Optional[str] = None, timeout: float = 5.0) -> Optional[Dict]:
        """接收WebSocket消息"""
        try:
            message = await asyncio.wait_for(self.websocket.recv(), timeout=timeout)

            if message is None:
                return None

            data = json.loads(message)
            channel = data.get("channel", "")
            action = data.get("action", "")

            if channel == "stock_basic_response":
                if action == "query" and data.get("result"):
                    result = data["result"]
                    self._log_request_success("get_stock_basic", result)
                    self._log_data_quality(result, "get_stock_basic")
                    return result

            elif channel == "stock_daily_response":
                if action == "query" and data.get("result"):
                    results = data["result"]
                    self._log_request_success("get_stock_daily", f"返回{len(results)}条日线数据")
                    self._log_data_quality(results, "get_stock_daily")
                    return results

            elif channel == "stock_realtime_response":
                if action == "query" and data.get("result"):
                    results = data["result"]
                    self._log_request_success("get_realtime_quotes", f"返回{len(results)}条实时行情")
                    self._log_data_quality(results, "get_realtime_quotes")
                    return results

            return None

        except asyncio.TimeoutError:
            logger.warning(f"{self.name} 接收消息超时")
            return None
        except Exception as e:
            logger.error(f"{self.name} 接收消息失败: {e}")
            return None

    async def _receive_messages(self, stock_code: Optional[str] = None) -> Optional[List[Dict]]:
        """接收多条消息"""
        results = []

        for i in range(10):
            result = await self._receive_message(stock_code, timeout=2.0)

            if result:
                results.append(result)

            return results if results else None

    async def check_health(self) -> Optional[str]:
        """检查健康状态"""
        try:
            if self.websocket and self.websocket.open:
                return "healthy"
            else:
                return "unhealthy"

        except Exception as e:
            logger.error(f"{self.name} 健康检查失败: {e}")
            return "unhealthy"

    async def close_connection(self):
        """关闭连接"""
        try:
            if self.websocket:
                await self.websocket.close()
                self.websocket = None
                self.subscriptions.clear()
                logger.info(f"{self.name} WebSocket连接已关闭")
        except Exception as e:
            logger.error(f"{self.name} 关闭连接失败: {e}")
