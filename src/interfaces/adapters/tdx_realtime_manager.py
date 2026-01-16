"""
TDX实时数据管理器 - 从 tdx_adapter.py 拆分
职责：实时行情数据、推送管理、缓存
遵循 TDD 原则：仅实现满足测试的最小功能
"""

import logging
import time
import uuid
from typing import Dict, Any, List, Optional, Callable
from threading import Lock

# 设置日志
logger = logging.getLogger(__name__)


class TdxRealtimeManager:
    """TDX实时数据管理器 - 专注于实时数据管理"""


def __init__(self):
    """初始化TDX实时数据管理器"""
    self.subscriptions = {}
    self.realtime_cache = {}
    self.cache_ttl = 5  # 5秒缓存
    self.lock = Lock()


def get_real_time_data(self, symbol: str) -> Dict[str, Any]:
    """
    获取实时数据

    Args:
        symbol: 股票代码

    Returns:
        Dict[str, Any]: 实时数据
    """
    # 检查缓存
    cache_key = f"realtime_{symbol}"
    cached_data = self._get_cached_realtime_data(cache_key)
    if cached_data:
        return cached_data

    # 获取新的实时数据
    realtime_data = self._fetch_realtime_quote(symbol)

    # 缓存数据
    self._set_cached_realtime_data(cache_key, realtime_data)

    return realtime_data


def fetch_realtime_batch(self, symbols: List[str]) -> List[Dict[str, Any]]:
    """
    批量获取实时数据

    Args:
        symbols: 股票代码列表

    Returns:
        List[Dict[str, Any]]: 实时数据列表
    """
    result = []

    try:
        # 获取批量数据
        batch_data = self._fetch_realtime_batch_internal(symbols)

        # 更新缓存
        for symbol, data in batch_data.items():
            cache_key = f"realtime_{symbol}"
            self._set_cached_realtime_data(cache_key, data)

        # 转换为列表格式
        for symbol in symbols:
            if symbol in batch_data:
                result.append(batch_data[symbol])

    except Exception as e:
        logger.error("Failed to fetch realtime batch: %s", str(e))

    return result


def subscribe_realtime_updates(self, symbol: str, callback: Callable) -> str:
    """
    订阅实时更新

    Args:
        symbol: 股票代码
        callback: 回调函数

    Returns:
        str: 订阅ID
    """
    # 设置实时订阅并获取返回的订阅ID
    subscription_id = self._setup_realtime_subscription(symbol)

    with self.lock:
        self.subscriptions[subscription_id] = {
            "symbol": symbol,
            "callback": callback,
            "created_at": time.time(),
            "active": True,
        }

    logger.info("Subscribed to realtime updates for %s, ID: %s", symbol, subscription_id)

    return subscription_id


def unsubscribe_realtime_updates(self, subscription_id: str) -> bool:
    """
    取消实时更新订阅

    Args:
        subscription_id: 订阅ID

    Returns:
        bool: 是否成功取消
    """
    with self.lock:
        if subscription_id in self.subscriptions:
            subscription = self.subscriptions[subscription_id]
            subscription["active"] = False
            del self.subscriptions[subscription_id]

            logger.info("Unsubscribed from realtime updates, ID: %s", subscription_id)
            return True

    return False


def get_subscriptions(self) -> Dict[str, Dict[str, Any]]:
    """
    获取所有订阅信息

    Returns:
        Dict[str, Dict[str, Any]]: 订阅信息
    """
    with self.lock:
        return {
            "count": len(self.subscriptions),
            "subscriptions": {
                sid: {
                    "symbol": sub["symbol"],
                    "created_at": sub["created_at"],
                    "active": sub["active"],
                }
                for sid, sub in self.subscriptions.items()
            },
        }


def _fetch_realtime_quote(self, symbol: str) -> Dict[str, Any]:
    """
    获取实时行情（内部方法）

    Args:
        symbol: 股票代码

    Returns:
        Dict[str, Any]: 实时行情数据
    """
    logger.debug("Fetching realtime quote for %s", symbol)

    # 模拟实时数据
    base_price = 10.0 + hash(symbol) % 100  # 基于股票代码生成基础价格
    current_time = time.time()

    return {
        "symbol": symbol,
        "price": round(base_price + (current_time % 10) * 0.1, 2),
        "change": round((current_time % 3 - 1) * 0.1, 2),
        "change_percent": round((current_time % 5 - 2) * 0.5, 2),
        "volume": int(10000 + current_time % 50000),
        "timestamp": current_time,
        "bid": round(base_price - 0.01, 2),
        "ask": round(base_price + 0.01, 2),
        "high": round(base_price + 0.5, 2),
        "low": round(base_price - 0.5, 2),
    }


def _fetch_realtime_batch_internal(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
    """
    批量获取实时数据（内部方法）

    Args:
        symbols: 股票代码列表

    Returns:
        Dict[str, Dict[str, Any]]: 实时数据字典
    """
    logger.debug("Fetching realtime batch for %s symbols", len(symbols))

    result = {}
    current_time = time.time()

    for symbol in symbols:
        # 为每个股票生成模拟数据
        base_price = 10.0 + hash(symbol) % 100

        result[symbol] = {
            "symbol": symbol,
            "price": round(base_price + (current_time % 10) * 0.1, 2),
            "change": round((current_time % 3 - 1) * 0.1, 2),
            "volume": int(10000 + (hash(symbol) % 40000)),
            "timestamp": current_time,
        }

    return result


def _setup_realtime_subscription(self, symbol: str) -> str:
    """
    设置实时订阅（内部方法）

    Args:
        symbol: 股票代码

    Returns:
        str: 订阅ID
    """
    # 生成订阅ID
    subscription_id = str(uuid.uuid4())

    logger.debug("Setting up realtime subscription for %s, ID: %s", symbol, subscription_id)

    # 在实际实现中，这里会建立WebSocket连接或其他推送机制
    # 这里只是模拟设置并返回订阅ID

    return subscription_id


def _handle_realtime_callback(self, subscription_id: str, data: Dict[str, Any]):
    """
    处理实时回调（内部方法）

    Args:
        subscription_id: 订阅ID
        data: 实时数据
    """
    with self.lock:
        if subscription_id in self.subscriptions:
            subscription = self.subscriptions[subscription_id]
            if subscription["active"]:
                try:
                    callback = subscription["callback"]
                    callback(data)
                except Exception as e:
                    logger.error("Error in realtime callback for %s: %s", subscription_id, str(e))


def _get_cached_realtime_data(self, key: str) -> Optional[Dict[str, Any]]:
    """
    获取缓存的实时数据

    Args:
        key: 缓存键

    Returns:
        Optional[Dict[str, Any]]: 缓存数据
    """
    if key in self.realtime_cache:
        data, timestamp = self.realtime_cache[key]

        # 检查是否过期
        if time.time() - timestamp < self.cache_ttl:
            return data
        else:
            # 缓存过期，删除
            del self.realtime_cache[key]

    return None


def _set_cached_realtime_data(self, key: str, data: Dict[str, Any]):
    """
    设置缓存的实时数据

    Args:
        key: 缓存键
        data: 实时数据
    """
    self.realtime_cache[key] = (data.copy(), time.time())


def clear_cache(self):
    """清空实时数据缓存"""
    self.realtime_cache.clear()
    logger.info("Realtime data cache cleared")


def get_cache_status(self) -> Dict[str, Any]:
    """
    获取缓存状态

    Returns:
        Dict[str, Any]: 缓存状态
    """
    return {
        "cache_size": len(self.realtime_cache),
        "cache_ttl": self.cache_ttl,
        "cached_symbols": [key.replace("realtime_", "") for key in self.realtime_cache.keys()],
    }
