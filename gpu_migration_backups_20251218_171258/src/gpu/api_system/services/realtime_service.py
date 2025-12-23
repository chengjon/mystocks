"""
实时数据服务
Real-time Data Service
"""

import logging
import time
import threading
from typing import Dict, List, Any
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from src.utils.gpu_utils import GPUResourceManager
from src.utils.redis_utils import RedisQueue
from src.utils.monitoring import MetricsCollector
from api_proto.realtime_pb2 import (
    MarketData,
    FeatureRequest,
    FeatureResponse,
    RealtimeStatistics,
    StreamRequest,
    StreamResponse,
)
from api_proto.realtime_pb2_grpc import RealTimeServiceServicer
import grpc

logger = logging.getLogger(__name__)


class RealTimeService(RealTimeServiceServicer):
    """实时数据服务实现"""

    def __init__(
        self,
        gpu_manager: GPUResourceManager,
        redis_queue: RedisQueue,
        metrics_collector: MetricsCollector,
    ):
        self.gpu_manager = gpu_manager
        self.redis_queue = redis_queue
        self.metrics_collector = metrics_collector
        self.running = False
        self.data_buffer = {}
        self.feature_cache = {}
        self.stream_clients = {}
        self.processing_thread = None
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.config = {
            "buffer_size": 10000,
            "cache_ttl": 300,  # 5分钟缓存
            "batch_size": 1000,
            "max_stream_clients": 100,
            "feature_calculation_interval": 1,
        }

    def initialize(self):
        """初始化服务"""
        logger.info("正在初始化实时数据服务...")

        # 启动数据处理线程
        self.running = True
        self.processing_thread = threading.Thread(
            target=self._data_processing_loop, daemon=True
        )
        self.processing_thread.start()

        logger.info("实时数据服务初始化完成")

    def _data_processing_loop(self):
        """数据处理主循环"""
        logger.info("实时数据处理循环启动")

        while self.running:
            try:
                # 处理数据缓冲区
                self._process_data_buffer()

                # 计算特征
                self._calculate_features()

                # 更新统计信息
                self._update_statistics()

                # 清理过期数据
                self._cleanup_expired_data()

                time.sleep(1)

            except Exception as e:
                logger.error(f"数据处理循环错误: {e}")
                time.sleep(5)

    def _process_data_buffer(self):
        """处理数据缓冲区"""
        try:
            current_time = datetime.now()

            # 按股票代码处理数据
            for stock_code, data_list in self.data_buffer.items():
                # 按时间排序
                data_list.sort(key=lambda x: x["timestamp"])

                # 批量处理数据
                batch_size = self.config["batch_size"]
                for i in range(0, len(data_list), batch_size):
                    batch = data_list[i : i + batch_size]

                    # 使用GPU进行批量处理
                    if self.gpu_manager.get_available_gpu_count() > 0:
                        self._process_batch_on_gpu(batch, stock_code)
                    else:
                        self._process_batch_on_cpu(batch, stock_code)

        except Exception as e:
            logger.error(f"处理数据缓冲区失败: {e}")

    def _process_batch_on_gpu(self, batch: List[Dict], stock_code: str):
        """使用GPU批量处理数据"""
        try:
            # 获取GPU资源
            gpu_id = self.gpu_manager.allocate_gpu(
                f"realtime_{stock_code}", priority="medium", memory_required=512
            )

            if gpu_id:
                # 这里应该调用实际的GPU处理逻辑
                # 目前模拟处理
                processed_data = []
                for data in batch:
                    # 模拟GPU加速处理
                    processed_data.append(
                        {
                            **data,
                            "gpu_processed": True,
                            "gpu_id": gpu_id,
                            "processed_time": datetime.now().isoformat(),
                        }
                    )

                # 释放GPU资源
                self.gpu_manager.release_gpu(f"realtime_{stock_code}", gpu_id)

                # 更新缓冲区
                self._update_processed_data(stock_code, processed_data)

        except Exception as e:
            logger.error(f"GPU处理失败: {e}")

    def _process_batch_on_cpu(self, batch: List[Dict], stock_code: str):
        """使用CPU批量处理数据"""
        try:
            # 模拟CPU处理
            processed_data = []
            for data in batch:
                processed_data.append(
                    {
                        **data,
                        "cpu_processed": True,
                        "processed_time": datetime.now().isoformat(),
                    }
                )

            # 更新缓冲区
            self._update_processed_data(stock_code, processed_data)

        except Exception as e:
            logger.error(f"CPU处理失败: {e}")

    def _update_processed_data(self, stock_code: str, processed_data: List[Dict]):
        """更新处理后的数据"""
        if stock_code not in self.data_buffer:
            self.data_buffer[stock_code] = []

        # 添加处理后的数据
        self.data_buffer[stock_code].extend(processed_data)

        # 保持缓冲区大小限制
        if len(self.data_buffer[stock_code]) > self.config["buffer_size"]:
            self.data_buffer[stock_code] = self.data_buffer[stock_code][
                -self.config["buffer_size"] :
            ]

    def _calculate_features(self):
        """计算特征"""
        try:
            current_time = datetime.now()

            # 对每只股票计算特征
            for stock_code, data_list in self.data_buffer.items():
                if len(data_list) < 10:  # 需要足够的数据点
                    continue

                # 检查缓存是否过期
                cache_key = f"{stock_code}_features"
                if cache_key in self.feature_cache:
                    cache_time = self.feature_cache[cache_key]["timestamp"]
                    if (
                        current_time - datetime.fromisoformat(cache_time)
                    ).seconds < self.config["cache_ttl"]:
                        continue

                # 计算技术指标
                features = self._calculate_technical_indicators(data_list)

                # 更新缓存
                self.feature_cache[cache_key] = {
                    "features": features,
                    "timestamp": current_time.isoformat(),
                }

                # 添加新数据到Redis队列
                feature_task = {
                    "task_id": f"feature_{stock_code}_{int(time.time())}",
                    "task_type": "realtime",
                    "priority": "medium",
                    "stock_code": stock_code,
                    "features": features,
                    "timestamp": current_time.isoformat(),
                }

                self.redis_queue.enqueue_task("realtime", feature_task)

        except Exception as e:
            logger.error(f"计算特征失败: {e}")

    def _calculate_technical_indicators(
        self, data_list: List[Dict]
    ) -> Dict[str, float]:
        """计算技术指标"""
        if not data_list:
            return {}

        try:
            prices = [d["price"] for d in data_list[-100:]]  # 最近100个价格点

            if len(prices) < 2:
                return {}

            # 计算简单移动平均
            sma_20 = (
                sum(prices[-20:]) / 20
                if len(prices) >= 20
                else sum(prices) / len(prices)
            )
            sma_50 = (
                sum(prices[-50:]) / 50
                if len(prices) >= 50
                else sum(prices) / len(prices)
            )

            # 计算指数移动平均
            ema_12 = self._calculate_ema(prices, 12)
            ema_26 = self._calculate_ema(prices, 26)

            # 计算MACD
            macd = ema_12 - ema_26
            macd_signal = (
                self._calculate_ema([macd] * len(prices), 9)[-1]
                if len(prices) >= 9
                else 0
            )
            macd_histogram = macd - macd_signal

            # 计算相对强弱指数
            rsi = self._calculate_rsi(prices, 14)

            # 计算布林带
            bb_middle = sma_20
            bb_std = (
                sum((p - sma_20) ** 2 for p in prices[-20:]) / 20
                if len(prices) >= 20
                else 0
            )
            bb_std = bb_std**0.5
            bb_upper = bb_middle + 2 * bb_std
            bb_lower = bb_middle - 2 * bb_std

            return {
                "sma_20": sma_20,
                "sma_50": sma_50,
                "ema_12": ema_12,
                "ema_26": ema_26,
                "macd": macd,
                "macd_signal": macd_signal,
                "macd_histogram": macd_histogram,
                "rsi": rsi,
                "bb_upper": bb_upper,
                "bb_middle": bb_middle,
                "bb_lower": bb_lower,
                "volatility": bb_std,
                "price_change": (
                    (prices[-1] - prices[0]) / prices[0] * 100 if len(prices) > 1 else 0
                ),
            }

        except Exception as e:
            logger.error(f"计算技术指标失败: {e}")
            return {}

    def _calculate_ema(self, prices: List[float], period: int) -> float:
        """计算指数移动平均"""
        if len(prices) < period:
            return sum(prices) / len(prices)

        multiplier = 2 / (period + 1)
        ema = prices[0]

        for price in prices[1:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))

        return ema

    def _calculate_rsi(self, prices: List[float], period: int) -> float:
        """计算相对强弱指数"""
        if len(prices) < period + 1:
            return 50

        deltas = []
        for i in range(1, len(prices)):
            deltas.append(prices[i] - prices[i - 1])

        gains = [d if d > 0 else 0 for d in deltas[-period:]]
        losses = [-d if d < 0 else 0 for d in deltas[-period:]]

        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period

        if avg_loss == 0:
            return 100

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    def _update_statistics(self):
        """更新统计信息"""
        try:
            total_records = sum(len(data) for data in self.data_buffer.values())
            total_stocks = len(self.data_buffer)
            cache_size = len(self.feature_cache)

            statistics = {
                "timestamp": datetime.now().isoformat(),
                "total_records": total_records,
                "total_stocks": total_stocks,
                "cache_size": cache_size,
                "stream_clients": len(self.stream_clients),
                "gpu_utilization": self.gpu_manager.get_gpu_stats().get(
                    "utilization", 0
                ),
            }

            # 更新到监控指标
            self.metrics_collector.record_system_metrics()

        except Exception as e:
            logger.error(f"更新统计信息失败: {e}")

    def _cleanup_expired_data(self):
        """清理过期数据"""
        try:
            current_time = datetime.now()
            expired_keys = []

            # 检查特征缓存
            for cache_key, cache_data in self.feature_cache.items():
                cache_time = datetime.fromisoformat(cache_data["timestamp"])
                if (current_time - cache_time).seconds > self.config["cache_ttl"]:
                    expired_keys.append(cache_key)

            # 删除过期缓存
            for key in expired_keys:
                del self.feature_cache[key]
                logger.info(f"清理过期特征缓存: {key}")

            # 限制数据缓冲区大小
            for stock_code in list(self.data_buffer.keys()):
                if len(self.data_buffer[stock_code]) > self.config["buffer_size"]:
                    self.data_buffer[stock_code] = self.data_buffer[stock_code][
                        -self.config["buffer_size"] :
                    ]

        except Exception as e:
            logger.error(f"清理过期数据失败: {e}")

    # gRPC服务实现
    def GetMarketData(
        self, request: StreamRequest, context: grpc.ServicerContext
    ) -> StreamResponse:
        """获取实时行情数据"""
        try:
            stock_code = request.stock_code
            start_time = request.start_time
            end_time = request.end_time

            # 从缓冲区获取数据
            if stock_code in self.data_buffer:
                data_list = self.data_buffer[stock_code]

                # 按时间过滤
                if start_time:
                    start_dt = datetime.fromisoformat(start_time)
                    data_list = [
                        d
                        for d in data_list
                        if datetime.fromisoformat(d["timestamp"]) >= start_dt
                    ]

                if end_time:
                    end_dt = datetime.fromisoformat(end_time)
                    data_list = [
                        d
                        for d in data_list
                        if datetime.fromisoformat(d["timestamp"]) <= end_dt
                    ]

                # 转换为MarketData消息
                market_data_list = []
                for data in data_list[-100:]:  # 返回最近100条数据
                    market_data = MarketData(
                        stock_code=data.get("stock_code", ""),
                        timestamp=data.get("timestamp", ""),
                        price=data.get("price", 0.0),
                        volume=data.get("volume", 0),
                        high=data.get("high", 0.0),
                        low=data.get("low", 0.0),
                        open_price=data.get("open", 0.0),
                        close_price=data.get("close", 0.0),
                    )
                    market_data_list.append(market_data)

                return StreamResponse(
                    stock_code=stock_code,
                    data=market_data_list,
                    total_count=len(market_data_list),
                    timestamp=datetime.now().isoformat(),
                )

            else:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"没有找到股票 {stock_code} 的数据")
                return StreamResponse()

        except Exception as e:
            logger.error(f"获取市场数据失败: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"内部错误: {e}")
            return StreamResponse()

    def CalculateFeatures(
        self, request: FeatureRequest, context: grpc.ServicerContext
    ) -> FeatureResponse:
        """计算特征"""
        try:
            stock_code = request.stock_code
            feature_types = request.feature_types

            # 检查缓存
            cache_key = f"{stock_code}_features"
            if cache_key in self.feature_cache:
                cached_data = self.feature_cache[cache_key]

                # 过滤请求的特征类型
                if feature_types:
                    filtered_features = {
                        k: v
                        for k, v in cached_data["features"].items()
                        if k in feature_types
                    }
                else:
                    filtered_features = cached_data["features"]

                return FeatureResponse(
                    stock_code=stock_code,
                    features=filtered_features,
                    timestamp=cached_data["timestamp"],
                    from_cache=True,
                )

            # 如果缓存中没有，计算实时特征
            else:
                if (
                    stock_code in self.data_buffer
                    and len(self.data_buffer[stock_code]) >= 10
                ):
                    features = self._calculate_technical_indicators(
                        self.data_buffer[stock_code]
                    )

                    # 过滤请求的特征类型
                    if feature_types:
                        features = {
                            k: v for k, v in features.items() if k in feature_types
                        }

                    return FeatureResponse(
                        stock_code=stock_code,
                        features=features,
                        timestamp=datetime.now().isoformat(),
                        from_cache=False,
                    )

            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"无法为股票 {stock_code} 计算特征")
            return FeatureResponse()

        except Exception as e:
            logger.error(f"计算特征失败: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"内部错误: {e}")
            return FeatureResponse()

    def GetRealtimeStatistics(self, request, context) -> RealtimeStatistics:
        """获取实时统计信息"""
        try:
            total_records = sum(len(data) for data in self.data_buffer.values())
            total_stocks = len(self.data_buffer)
            cache_size = len(self.feature_cache)
            gpu_stats = self.gpu_manager.get_gpu_stats()

            statistics = RealtimeStatistics(
                total_records=total_records,
                total_stocks=total_stocks,
                cache_size=cache_size,
                stream_clients=len(self.stream_clients),
                gpu_utilization=gpu_stats.get("utilization", 0),
                gpu_memory_usage=gpu_stats.get("memory_usage", 0),
                active_tasks=len(self.gpu_manager.active_tasks),
                timestamp=datetime.now().isoformat(),
            )

            return statistics

        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"内部错误: {e}")
            return RealtimeStatistics()

    def StreamMarketData(
        self, request: StreamRequest, context: grpc.ServicerContext
    ) -> StreamResponse:
        """流式市场数据"""
        try:
            stock_code = request.stock_code

            # 注册客户端
            client_id = f"{context.peer()}_{int(time.time())}"
            self.stream_clients[client_id] = {
                "stock_code": stock_code,
                "context": context,
                "created_at": datetime.now(),
            }

            logger.info(f"新的流数据客户端: {client_id} (股票: {stock_code})")

            # 持续推送数据
            while context.is_active():
                try:
                    if stock_code in self.data_buffer:
                        # 获取最新数据
                        latest_data = self.data_buffer[stock_code][-1:]  # 最近一条数据

                        if latest_data:
                            market_data = MarketData(
                                stock_code=latest_data[0].get("stock_code", ""),
                                timestamp=latest_data[0].get("timestamp", ""),
                                price=latest_data[0].get("price", 0.0),
                                volume=latest_data[0].get("volume", 0),
                                high=latest_data[0].get("high", 0.0),
                                low=latest_data[0].get("low", 0.0),
                                open_price=latest_data[0].get("open", 0.0),
                                close_price=latest_data[0].get("close", 0.0),
                            )

                            response = StreamResponse(
                                stock_code=stock_code,
                                data=[market_data],
                                total_count=1,
                                timestamp=datetime.now().isoformat(),
                            )

                            yield response

                    time.sleep(1)  # 每秒推送一次

                except Exception as e:
                    logger.error(f"流数据推送失败: {e}")
                    break
                # 清理客户端
                if client_id in self.stream_clients:
                    del self.stream_clients[client_id]
                    logger.info(f"客户端断开连接: {client_id}")

        except Exception as e:
            logger.error(f"流数据处理失败: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"内部错误: {e}")

    def add_market_data(self, market_data: Dict[str, Any]):
        """添加市场数据"""
        try:
            stock_code = market_data.get("stock_code", "")
            if stock_code:
                if stock_code not in self.data_buffer:
                    self.data_buffer[stock_code] = []

                self.data_buffer[stock_code].append(market_data)

        except Exception as e:
            logger.error(f"添加市场数据失败: {e}")

    def stop(self):
        """停止服务"""
        logger.info("正在停止实时数据服务...")
        self.running = False

        if self.processing_thread:
            self.processing_thread.join(timeout=10)

        self.executor.shutdown(wait=True)
        logger.info("实时数据服务已停止")
