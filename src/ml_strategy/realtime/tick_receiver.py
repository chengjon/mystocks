"""
实时行情接收器 (Real-time Tick Receiver)

功能说明:
- 接收实时tick数据
- WebSocket连接管理
- 数据缓存和分发
- 支持多数据源

支持的数据源:
- TDX实时行情
- 自定义WebSocket源
- Redis发布/订阅

作者: MyStocks量化交易团队
创建时间: 2025-10-18
版本: 1.0.0
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, List, Optional, Callable, Any
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import logging
import threading
import queue
import time

# WebSocket支持（可选）
try:
    import websocket

    WEBSOCKET_AVAILABLE = True
except ImportError:
    WEBSOCKET_AVAILABLE = False
    print("警告: websocket-client未安装，WebSocket功能不可用")
    print("安装: pip install websocket-client")

# Redis支持（可选）
try:
    import redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class DataSourceType(Enum):
    """数据源类型"""

    TDX = "tdx"
    WEBSOCKET = "websocket"
    REDIS = "redis"
    CUSTOM = "custom"


@dataclass
class TickData:
    """Tick数据"""

    symbol: str  # 股票代码
    timestamp: datetime  # 时间戳
    last_price: float  # 最新价
    volume: int  # 成交量
    amount: float  # 成交额
    bid_price: float = 0.0  # 买一价
    bid_volume: int = 0  # 买一量
    ask_price: float = 0.0  # 卖一价
    ask_volume: int = 0  # 卖一量
    high: float = 0.0  # 最高价
    low: float = 0.0  # 最低价
    open: float = 0.0  # 开盘价
    prev_close: float = 0.0  # 昨收价


class TickReceiver:
    """
    实时行情接收器

    功能:
    - 管理多个数据源连接
    - 数据缓存和分发
    - 回调函数处理
    - 线程安全
    """

    def __init__(
        self, cache_size: int = 1000, source_type: DataSourceType = DataSourceType.TDX
    ):
        """
        初始化接收器

        参数:
            cache_size: 缓存大小
            source_type: 数据源类型
        """
        self.logger = logging.getLogger(f"{__name__}.TickReceiver")
        self.logger.setLevel(logging.INFO)

        self.source_type = source_type
        self.cache_size = cache_size

        # 数据缓存 {symbol: [TickData]}
        self.tick_cache: Dict[str, List[TickData]] = {}

        # 订阅符号
        self.subscribed_symbols: set = set()

        # 回调函数列表
        self.callbacks: List[Callable] = []

        # 数据队列
        self.data_queue = queue.Queue(maxsize=10000)

        # 运行标志
        self.running = False
        self.receiver_thread: Optional[threading.Thread] = None

        # 统计信息
        self.stats = {"total_ticks": 0, "ticks_per_second": 0, "last_update": None}

    def subscribe(self, symbols: List[str]):
        """
        订阅股票

        参数:
            symbols: 股票代码列表
        """
        for symbol in symbols:
            if symbol not in self.subscribed_symbols:
                self.subscribed_symbols.add(symbol)
                self.tick_cache[symbol] = []
                self.logger.info(f"✓ 已订阅: {symbol}")

    def unsubscribe(self, symbols: List[str]):
        """取消订阅"""
        for symbol in symbols:
            if symbol in self.subscribed_symbols:
                self.subscribed_symbols.remove(symbol)
                self.tick_cache.pop(symbol, None)
                self.logger.info(f"✓ 已取消订阅: {symbol}")

    def register_callback(self, callback: Callable[[TickData], None]):
        """
        注册回调函数

        参数:
            callback: 回调函数，接收TickData参数
        """
        self.callbacks.append(callback)
        self.logger.info(f"✓ 已注册回调函数: {callback.__name__}")

    def start(self):
        """启动接收器"""
        if self.running:
            self.logger.warning("接收器已在运行")
            return

        self.running = True

        # 启动接收线程
        self.receiver_thread = threading.Thread(target=self._receiver_loop, daemon=True)
        self.receiver_thread.start()

        # 启动处理线程
        self.processor_thread = threading.Thread(
            target=self._processor_loop, daemon=True
        )
        self.processor_thread.start()

        self.logger.info("=" * 70)
        self.logger.info("实时行情接收器已启动")
        self.logger.info(f"数据源: {self.source_type.value}")
        self.logger.info(f"订阅数量: {len(self.subscribed_symbols)}")
        self.logger.info("=" * 70)

    def stop(self):
        """停止接收器"""
        self.running = False

        if self.receiver_thread:
            self.receiver_thread.join(timeout=5)

        if self.processor_thread:
            self.processor_thread.join(timeout=5)

        self.logger.info("实时行情接收器已停止")

    def _receiver_loop(self):
        """接收线程主循环"""
        if self.source_type == DataSourceType.TDX:
            self._receive_from_tdx()
        elif self.source_type == DataSourceType.WEBSOCKET:
            self._receive_from_websocket()
        elif self.source_type == DataSourceType.REDIS:
            self._receive_from_redis()
        else:
            self._receive_mock_data()

    def _processor_loop(self):
        """处理线程主循环"""
        while self.running:
            try:
                # 从队列获取数据
                tick = self.data_queue.get(timeout=1)

                # 缓存数据
                self._cache_tick(tick)

                # 调用回调函数
                self._invoke_callbacks(tick)

                # 更新统计
                self._update_stats()

            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"处理数据失败: {e}")

    def _receive_from_tdx(self):
        """从TDX接收数据"""
        self.logger.info("开始接收TDX实时数据...")

        # 这里应该使用pytdx库连接TDX服务器
        # 简化实现：模拟数据
        self._receive_mock_data()

    def _receive_from_websocket(self):
        """从WebSocket接收数据"""
        if not WEBSOCKET_AVAILABLE:
            self.logger.error("WebSocket库未安装")
            return

        self.logger.info("开始接收WebSocket数据...")

        # WebSocket连接逻辑
        # ws = websocket.create_connection("ws://...")
        # while self.running:
        #     data = ws.recv()
        #     ... 处理数据

        # 简化实现：模拟数据
        self._receive_mock_data()

    def _receive_from_redis(self):
        """从Redis订阅数据"""
        if not REDIS_AVAILABLE:
            self.logger.error("Redis库未安装")
            return

        self.logger.info("开始接收Redis数据...")

        # Redis订阅逻辑
        # 简化实现：模拟数据
        self._receive_mock_data()

    def _receive_mock_data(self):
        """接收模拟数据（用于测试）"""
        import random

        self.logger.info("生成模拟数据...")

        while self.running:
            for symbol in self.subscribed_symbols:
                # 生成模拟tick数据
                tick = TickData(
                    symbol=symbol,
                    timestamp=datetime.now(),
                    last_price=10.0 + random.uniform(-0.5, 0.5),
                    volume=random.randint(100, 10000),
                    amount=random.uniform(1000, 100000),
                    bid_price=10.0 + random.uniform(-0.5, 0.5),
                    bid_volume=random.randint(100, 1000),
                    ask_price=10.0 + random.uniform(-0.5, 0.5),
                    ask_volume=random.randint(100, 1000),
                )

                # 放入队列
                try:
                    self.data_queue.put_nowait(tick)
                except queue.Full:
                    self.logger.warning("数据队列已满，丢弃数据")

            # 模拟数据延迟
            time.sleep(0.1)  # 100ms

    def _cache_tick(self, tick: TickData):
        """缓存tick数据"""
        if tick.symbol not in self.tick_cache:
            self.tick_cache[tick.symbol] = []

        cache = self.tick_cache[tick.symbol]
        cache.append(tick)

        # 限制缓存大小
        if len(cache) > self.cache_size:
            cache.pop(0)

    def _invoke_callbacks(self, tick: TickData):
        """调用所有回调函数"""
        for callback in self.callbacks:
            try:
                callback(tick)
            except Exception as e:
                self.logger.error(f"回调函数执行失败 {callback.__name__}: {e}")

    def _update_stats(self):
        """更新统计信息"""
        self.stats["total_ticks"] += 1
        self.stats["last_update"] = datetime.now()

    def get_latest_tick(self, symbol: str) -> Optional[TickData]:
        """
        获取最新tick数据

        参数:
            symbol: 股票代码

        返回:
            TickData: 最新数据，如果没有则返回None
        """
        cache = self.tick_cache.get(symbol, [])
        return cache[-1] if cache else None

    def get_tick_history(self, symbol: str, limit: int = 100) -> List[TickData]:
        """
        获取历史tick数据

        参数:
            symbol: 股票代码
            limit: 返回数量

        返回:
            List[TickData]: 历史数据列表
        """
        cache = self.tick_cache.get(symbol, [])
        return cache[-limit:]

    def get_statistics(self) -> Dict:
        """获取统计信息"""
        return {
            **self.stats,
            "subscribed_count": len(self.subscribed_symbols),
            "cache_size": sum(len(cache) for cache in self.tick_cache.values()),
            "queue_size": self.data_queue.qsize(),
        }


if __name__ == "__main__":
    # 测试代码
    print("实时行情接收器测试")
    print("=" * 70)

    # 设置日志
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    # 创建接收器
    receiver = TickReceiver(source_type=DataSourceType.CUSTOM)

    # 订阅股票
    receiver.subscribe(["sh600000", "sh600016", "sh600036"])

    # 注册回调函数
    def on_tick(tick: TickData):
        print(
            f"  收到数据: {tick.symbol} - {tick.last_price:.2f} @ {tick.timestamp.strftime('%H:%M:%S.%f')[:12]}"
        )

    receiver.register_callback(on_tick)

    # 启动接收器
    receiver.start()

    # 运行一段时间
    print("\n运行5秒...")
    time.sleep(5)

    # 获取统计
    print("\n统计信息:")
    stats = receiver.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    # 获取最新数据
    print("\n最新数据:")
    for symbol in ["sh600000", "sh600016"]:
        latest = receiver.get_latest_tick(symbol)
        if latest:
            print(f"  {symbol}: {latest.last_price:.2f}")

    # 停止接收器
    receiver.stop()

    print("\n" + "=" * 70)
    print("测试完成")
