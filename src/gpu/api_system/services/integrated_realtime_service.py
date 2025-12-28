"""
集成实时数据处理服务
Integrated Real-time Data Processing Service
"""

import logging
import time
import threading
from typing import Dict, List, Any, Iterator
from datetime import datetime, timedelta
from collections import deque
import json
import pandas as pd

from src.utils.gpu_utils import GPUResourceManager
from src.utils.redis_utils import RedisQueue
from src.utils.monitoring import MetricsCollector
from src.utils.cache_optimization import CacheManager
from src.utils.gpu_acceleration_engine import GPUAccelerationEngine
from api_proto.realtime_pb2 import (
    StreamDataRequest,
    StreamDataResponse,
    FeatureRequest,
    FeatureResponse,
)
from api_proto.realtime_pb2_grpc import RealTimeServiceServicer
import grpc

logger = logging.getLogger(__name__)


class IntegratedRealTimeService(RealTimeServiceServicer):
    """集成实时数据处理服务实现"""

    def __init__(
        self,
        gpu_manager: GPUResourceManager,
        redis_queue: RedisQueue,
        metrics_collector: MetricsCollector,
    ):
        # 基础组件
        super().__init__(gpu_manager, redis_queue, metrics_collector)

        # 集成组件
        self.cache_manager = CacheManager()
        self.gpu_engine = GPUAccelerationEngine(gpu_manager, metrics_collector)

        # 实时数据流管理
        self.active_streams = {}  # stream_id -> stream_info
        self.stream_lock = threading.RLock()

        # 数据缓冲区
        self.data_buffers = {}  # stock_code -> deque(maxlen=1000)
        self.buffer_lock = threading.RLock()

        # 特征计算缓存
        self.feature_cache = {}  # cache_key -> features
        self.feature_lock = threading.RLock()

        # 配置参数
        self.config = {
            "max_concurrent_streams": 10,
            "buffer_size": 1000,
            "feature_cache_ttl": 60,  # 特征缓存60秒
            "gpu_batch_size": 100,
            "stream_timeout": 3600,  # 1小时流超时
            "enable_compression": True,
            "enable_gpu_acceleration": True,
        }

        # 性能统计
        self.stats = {
            "total_data_points": 0,
            "total_features_computed": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "gpu_computations": 0,
            "cpu_computations": 0,
        }

        logger.info("集成实时数据处理服务初始化完成")

    def initialize(self):
        """初始化服务"""
        logger.info("正在初始化集成实时数据处理服务...")

        # 初始化缓存管理器
        self.cache_manager.initialize()

        # 初始化GPU加速引擎
        self.gpu_engine.initialize()

        # 启动后台任务
        self._start_background_tasks()

        logger.info("集成实时数据处理服务初始化完成")

    def _start_background_tasks(self):
        """启动后台任务"""
        # 数据流监控线程
        monitor_thread = threading.Thread(target=self._monitor_streams, daemon=True)
        monitor_thread.start()

        # 特征缓存清理线程
        cleanup_thread = threading.Thread(target=self._cleanup_feature_cache, daemon=True)
        cleanup_thread.start()

        # 性能统计线程
        stats_thread = threading.Thread(target=self._collect_stats, daemon=True)
        stats_thread.start()

        logger.info("后台任务启动完成")

    def _monitor_streams(self):
        """监控活动的数据流"""
        while True:
            try:
                time.sleep(60)  # 每分钟检查一次

                with self.stream_lock:
                    current_time = datetime.now()
                    expired_streams = []

                    for stream_id, stream_info in self.active_streams.items():
                        # 检查流超时
                        last_activity = datetime.fromisoformat(stream_info["last_activity"])
                        if current_time - last_activity > timedelta(seconds=self.config["stream_timeout"]):
                            logger.warning("数据流 %s 超时，关闭流", stream_id)
                            expired_streams.append(stream_id)

                        # 检查流健康状态
                        if stream_info.get("error_count", 0) > 10:
                            logger.warning("数据流 %s 错误过多，关闭流", stream_id)
                            expired_streams.append(stream_id)

                    # 清理过期流
                    for stream_id in expired_streams:
                        self._close_stream(stream_id)

            except Exception as e:
                logger.error("监控数据流失败: %s", e)

    def _cleanup_feature_cache(self):
        """清理过期的特征缓存"""
        while True:
            try:
                time.sleep(300)  # 每5分钟清理一次

                with self.feature_lock:
                    current_time = time.time()
                    expired_keys = []

                    for cache_key, feature_data in self.feature_cache.items():
                        if current_time - feature_data.get("timestamp", 0) > self.config["feature_cache_ttl"]:
                            expired_keys.append(cache_key)

                    for key in expired_keys:
                        del self.feature_cache[key]

                    if expired_keys:
                        logger.info("清理了 %s 个过期特征缓存", len(expired_keys))

            except Exception as e:
                logger.error("清理特征缓存失败: %s", e)

    def _collect_stats(self):
        """收集性能统计"""
        while True:
            try:
                time.sleep(60)  # 每分钟收集一次

                # 记录统计信息
                self.metrics_collector.record_custom_metric("realtime_data_points", self.stats["total_data_points"])
                self.metrics_collector.record_custom_metric(
                    "realtime_features_computed", self.stats["total_features_computed"]
                )

                # 计算缓存命中率
                total_requests = self.stats["cache_hits"] + self.stats["cache_misses"]
                if total_requests > 0:
                    hit_rate = self.stats["cache_hits"] / total_requests * 100
                    self.metrics_collector.record_custom_metric("feature_cache_hit_rate", hit_rate)

                # GPU使用统计
                gpu_total = self.stats["gpu_computations"] + self.stats["cpu_computations"]
                if gpu_total > 0:
                    gpu_ratio = self.stats["gpu_computations"] / gpu_total * 100
                    self.metrics_collector.record_custom_metric("gpu_computation_ratio", gpu_ratio)

            except Exception as e:
                logger.error("收集统计信息失败: %s", e)

    def StreamMarketData(
        self,
        request_iterator: Iterator[StreamDataRequest],
        context: grpc.ServicerContext,
    ) -> Iterator[StreamDataResponse]:
        """流式处理市场数据"""
        stream_id = f"stream_{int(time.time())}_{hash(str(context.peer()))}"

        try:
            logger.info("启动市场数据流: %s", stream_id)

            # 注册数据流
            with self.stream_lock:
                self.active_streams[stream_id] = {
                    "stream_id": stream_id,
                    "start_time": datetime.now().isoformat(),
                    "last_activity": datetime.now().isoformat(),
                    "data_count": 0,
                    "error_count": 0,
                    "status": "active",
                }

            # 批量处理缓冲区
            batch_buffer = []
            batch_size = self.config["gpu_batch_size"]

            for request in request_iterator:
                try:
                    # 更新流活动时间
                    with self.stream_lock:
                        if stream_id in self.active_streams:
                            self.active_streams[stream_id]["last_activity"] = datetime.now().isoformat()
                            self.active_streams[stream_id]["data_count"] += 1

                    # 添加到批量缓冲区
                    batch_buffer.append(request)

                    # 当缓冲区达到批量大小时处理
                    if len(batch_buffer) >= batch_size:
                        responses = self._process_data_batch(batch_buffer, stream_id)
                        for response in responses:
                            yield response
                        batch_buffer.clear()

                    # 更新统计
                    self.stats["total_data_points"] += 1

                except Exception as e:
                    logger.error("处理数据流 %s 失败: %s", stream_id, e)
                    with self.stream_lock:
                        if stream_id in self.active_streams:
                            self.active_streams[stream_id]["error_count"] += 1

            # 处理剩余数据
            if batch_buffer:
                responses = self._process_data_batch(batch_buffer, stream_id)
                for response in responses:
                    yield response

            logger.info("市场数据流 %s 正常结束", stream_id)

        except Exception as e:
            logger.error("市场数据流 %s 异常: %s", stream_id, e)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"流处理失败: {e}")

        finally:
            # 清理数据流
            self._close_stream(stream_id)

    def _process_data_batch(self, batch: List[StreamDataRequest], stream_id: str) -> List[StreamDataResponse]:
        """批量处理数据"""
        responses = []

        try:
            # 提取数据
            stock_codes = [req.stock_code for req in batch]
            prices = [req.price for req in batch]
            volumes = [req.volume for req in batch]
            timestamps = [req.timestamp for req in batch]

            # 更新数据缓冲区
            self._update_data_buffers(stock_codes, prices, volumes, timestamps)

            # GPU加速处理
            if self.config["enable_gpu_acceleration"]:
                try:
                    processed_data = self._gpu_process_batch(stock_codes, prices, volumes)
                    self.stats["gpu_computations"] += len(batch)
                except Exception as e:
                    logger.warning("GPU处理失败，回退到CPU: %s", e)
                    processed_data = self._cpu_process_batch(stock_codes, prices, volumes)
                    self.stats["cpu_computations"] += len(batch)
            else:
                processed_data = self._cpu_process_batch(stock_codes, prices, volumes)
                self.stats["cpu_computations"] += len(batch)

            # 生成响应
            for i, req in enumerate(batch):
                response = StreamDataResponse(
                    stock_code=req.stock_code,
                    processed_data=processed_data[i],
                    timestamp=datetime.now().isoformat(),
                    stream_id=stream_id,
                )
                responses.append(response)

        except Exception as e:
            logger.error("批量处理数据失败: %s", e)

        return responses

    def _update_data_buffers(
        self,
        stock_codes: List[str],
        prices: List[float],
        volumes: List[int],
        timestamps: List[str],
    ):
        """更新数据缓冲区"""
        with self.buffer_lock:
            for stock_code, price, volume, timestamp in zip(stock_codes, prices, volumes, timestamps):
                if stock_code not in self.data_buffers:
                    self.data_buffers[stock_code] = deque(maxlen=self.config["buffer_size"])

                self.data_buffers[stock_code].append({"price": price, "volume": volume, "timestamp": timestamp})

    def _gpu_process_batch(
        self, stock_codes: List[str], prices: List[float], volumes: List[int]
    ) -> List[Dict[str, Any]]:
        """GPU批量处理数据"""
        try:
            import cudf

            # 转换为cuDF DataFrame
            df = cudf.DataFrame({"stock_code": stock_codes, "price": prices, "volume": volumes})

            # GPU计算
            df["price_change"] = df["price"].pct_change()
            df["volume_ma"] = df.groupby("stock_code")["volume"].rolling(window=5).mean().reset_index(0, drop=True)

            # 转回CPU
            result_df = df.to_pandas()

            # 转换为字典列表
            processed_data = []
            for _, row in result_df.iterrows():
                processed_data.append(
                    {
                        "stock_code": row["stock_code"],
                        "price": row["price"],
                        "volume": row["volume"],
                        "price_change": (row["price_change"] if not pd.isna(row["price_change"]) else 0.0),
                        "volume_ma": (row["volume_ma"] if not pd.isna(row["volume_ma"]) else 0.0),
                    }
                )

            return processed_data

        except Exception as e:
            logger.error("GPU处理批量数据失败: %s", e)
            raise e

    def _cpu_process_batch(
        self, stock_codes: List[str], prices: List[float], volumes: List[int]
    ) -> List[Dict[str, Any]]:
        """CPU批量处理数据"""
        processed_data = []

        for stock_code, price, volume in zip(stock_codes, prices, volumes):
            # 简单处理
            processed_data.append(
                {
                    "stock_code": stock_code,
                    "price": price,
                    "volume": volume,
                    "price_change": 0.0,  # 需要历史数据计算
                    "volume_ma": 0.0,  # 需要历史数据计算
                }
            )

        return processed_data

    def ComputeFeatures(self, request: FeatureRequest, context: grpc.ServicerContext) -> FeatureResponse:
        """计算技术特征"""
        try:
            stock_code = request.stock_code
            feature_types = list(request.feature_types)

            # 生成缓存键
            cache_key = self._generate_feature_cache_key(stock_code, feature_types)

            # 检查缓存
            with self.feature_lock:
                if cache_key in self.feature_cache:
                    cache_data = self.feature_cache[cache_key]
                    if time.time() - cache_data["timestamp"] < self.config["feature_cache_ttl"]:
                        logger.info("使用缓存的特征: %s", stock_code)
                        self.stats["cache_hits"] += 1
                        return cache_data["response"]
                    else:
                        # 缓存过期
                        del self.feature_cache[cache_key]

            self.stats["cache_misses"] += 1

            # 获取历史数据
            with self.buffer_lock:
                if stock_code not in self.data_buffers:
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details(f"未找到股票数据: {stock_code}")
                    return FeatureResponse()

                historical_data = list(self.data_buffers[stock_code])

            if len(historical_data) < 20:  # 需要至少20个数据点
                context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
                context.set_details("数据点不足，无法计算特征")
                return FeatureResponse()

            # 计算特征
            if self.config["enable_gpu_acceleration"]:
                try:
                    features = self._compute_features_gpu(historical_data, feature_types)
                    self.stats["gpu_computations"] += 1
                except Exception as e:
                    logger.warning("GPU计算特征失败，回退到CPU: %s", e)
                    features = self._compute_features_cpu(historical_data, feature_types)
                    self.stats["cpu_computations"] += 1
            else:
                features = self._compute_features_cpu(historical_data, feature_types)
                self.stats["cpu_computations"] += 1

            # 构建响应
            response = FeatureResponse(
                stock_code=stock_code,
                features=features,
                timestamp=datetime.now().isoformat(),
            )

            # 缓存结果
            with self.feature_lock:
                self.feature_cache[cache_key] = {
                    "response": response,
                    "timestamp": time.time(),
                }

            self.stats["total_features_computed"] += 1

            return response

        except Exception as e:
            logger.error("计算特征失败: %s", e)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"内部错误: {e}")
            return FeatureResponse()

    def _generate_feature_cache_key(self, stock_code: str, feature_types: List[str]) -> str:
        """生成特征缓存键"""
        import hashlib

        key_str = f"{stock_code}_{','.join(sorted(feature_types))}"
        return hashlib.md5(key_str.encode()).hexdigest()

    def _compute_features_gpu(self, historical_data: List[Dict], feature_types: List[str]) -> Dict[str, float]:
        """GPU计算技术特征"""
        try:
            import cudf

            # 转换为DataFrame
            df = pd.DataFrame(historical_data)
            df_gpu = cudf.from_pandas(df)

            features = {}

            for feature_type in feature_types:
                if feature_type == "sma_20":
                    features["sma_20"] = float(df_gpu["price"].rolling(window=20).mean().iloc[-1])
                elif feature_type == "sma_50":
                    if len(df_gpu) >= 50:
                        features["sma_50"] = float(df_gpu["price"].rolling(window=50).mean().iloc[-1])
                    else:
                        features["sma_50"] = 0.0
                elif feature_type == "rsi":
                    features["rsi"] = self._calculate_rsi_gpu(df_gpu["price"])
                elif feature_type == "macd":
                    macd_values = self._calculate_macd_gpu(df_gpu["price"])
                    features.update(macd_values)
                elif feature_type == "bollinger":
                    bb_values = self._calculate_bollinger_gpu(df_gpu["price"])
                    features.update(bb_values)
                elif feature_type == "volume_ratio":
                    volume_ma = df_gpu["volume"].rolling(window=20).mean().iloc[-1]
                    current_volume = df_gpu["volume"].iloc[-1]
                    features["volume_ratio"] = float(current_volume / volume_ma) if volume_ma > 0 else 0.0

            return features

        except Exception as e:
            logger.error("GPU计算特征失败: %s", e)
            raise e

    def _compute_features_cpu(self, historical_data: List[Dict], feature_types: List[str]) -> Dict[str, float]:
        """CPU计算技术特征"""
        df = pd.DataFrame(historical_data)
        features = {}

        for feature_type in feature_types:
            if feature_type == "sma_20":
                features["sma_20"] = float(df["price"].rolling(window=20).mean().iloc[-1])
            elif feature_type == "sma_50":
                if len(df) >= 50:
                    features["sma_50"] = float(df["price"].rolling(window=50).mean().iloc[-1])
                else:
                    features["sma_50"] = 0.0
            elif feature_type == "rsi":
                features["rsi"] = self._calculate_rsi_cpu(df["price"])
            elif feature_type == "macd":
                macd_values = self._calculate_macd_cpu(df["price"])
                features.update(macd_values)
            elif feature_type == "bollinger":
                bb_values = self._calculate_bollinger_cpu(df["price"])
                features.update(bb_values)
            elif feature_type == "volume_ratio":
                volume_ma = df["volume"].rolling(window=20).mean().iloc[-1]
                current_volume = df["volume"].iloc[-1]
                features["volume_ratio"] = float(current_volume / volume_ma) if volume_ma > 0 else 0.0

        return features

    def _calculate_rsi_gpu(self, prices) -> float:
        """GPU计算RSI"""
        try:
            # 计算价格变化
            delta = prices.diff()

            # 分离上涨和下跌
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)

            # 计算平均值
            avg_gain = gain.rolling(window=14).mean().iloc[-1]
            avg_loss = loss.rolling(window=14).mean().iloc[-1]

            if avg_loss == 0:
                return 100.0

            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))

            return float(rsi)

        except Exception as e:
            logger.error("GPU计算RSI失败: %s", e)
            return 50.0

    def _calculate_rsi_cpu(self, prices: pd.Series) -> float:
        """CPU计算RSI"""
        delta = prices.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)

        avg_gain = gain.rolling(window=14).mean().iloc[-1]
        avg_loss = loss.rolling(window=14).mean().iloc[-1]

        if avg_loss == 0:
            return 100.0

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return float(rsi)

    def _calculate_macd_gpu(self, prices) -> Dict[str, float]:
        """GPU计算MACD"""
        try:
            ema_12 = prices.ewm(span=12, adjust=False).mean()
            ema_26 = prices.ewm(span=26, adjust=False).mean()
            macd_line = ema_12 - ema_26
            signal_line = macd_line.ewm(span=9, adjust=False).mean()

            return {
                "macd": float(macd_line.iloc[-1]),
                "macd_signal": float(signal_line.iloc[-1]),
                "macd_histogram": float(macd_line.iloc[-1] - signal_line.iloc[-1]),
            }
        except Exception as e:
            logger.error("GPU计算MACD失败: %s", e)
            return {"macd": 0.0, "macd_signal": 0.0, "macd_histogram": 0.0}

    def _calculate_macd_cpu(self, prices: pd.Series) -> Dict[str, float]:
        """CPU计算MACD"""
        ema_12 = prices.ewm(span=12, adjust=False).mean()
        ema_26 = prices.ewm(span=26, adjust=False).mean()
        macd_line = ema_12 - ema_26
        signal_line = macd_line.ewm(span=9, adjust=False).mean()

        return {
            "macd": float(macd_line.iloc[-1]),
            "macd_signal": float(signal_line.iloc[-1]),
            "macd_histogram": float(macd_line.iloc[-1] - signal_line.iloc[-1]),
        }

    def _calculate_bollinger_gpu(self, prices) -> Dict[str, float]:
        """GPU计算布林带"""
        try:
            sma = prices.rolling(window=20).mean()
            std = prices.rolling(window=20).std()

            upper_band = sma + (2 * std)
            lower_band = sma - (2 * std)

            return {
                "bb_upper": float(upper_band.iloc[-1]),
                "bb_middle": float(sma.iloc[-1]),
                "bb_lower": float(lower_band.iloc[-1]),
            }
        except Exception as e:
            logger.error("GPU计算布林带失败: %s", e)
            return {"bb_upper": 0.0, "bb_middle": 0.0, "bb_lower": 0.0}

    def _calculate_bollinger_cpu(self, prices: pd.Series) -> Dict[str, float]:
        """CPU计算布林带"""
        sma = prices.rolling(window=20).mean()
        std = prices.rolling(window=20).std()

        upper_band = sma + (2 * std)
        lower_band = sma - (2 * std)

        return {
            "bb_upper": float(upper_band.iloc[-1]),
            "bb_middle": float(sma.iloc[-1]),
            "bb_lower": float(lower_band.iloc[-1]),
        }

    def _close_stream(self, stream_id: str):
        """关闭数据流"""
        try:
            with self.stream_lock:
                if stream_id in self.active_streams:
                    stream_info = self.active_streams[stream_id]
                    logger.info("关闭数据流 %s, 处理了 %s 个数据点", stream_id, stream_info["data_count"])
                    del self.active_streams[stream_id]
        except Exception as e:
            logger.error("关闭数据流失败: %s", e)

    def GetStreamStats(self, request, context):
        """获取流统计信息"""
        try:
            with self.stream_lock:
                active_stream_count = len(self.active_streams)
                sum(stream["data_count"] for stream in self.active_streams.values())

            stats = {
                "timestamp": datetime.now().isoformat(),
                "active_streams": active_stream_count,
                "total_data_points": self.stats["total_data_points"],
                "total_features_computed": self.stats["total_features_computed"],
                "cache_hit_rate": (
                    self.stats["cache_hits"] / (self.stats["cache_hits"] + self.stats["cache_misses"]) * 100
                    if (self.stats["cache_hits"] + self.stats["cache_misses"]) > 0
                    else 0
                ),
                "gpu_computation_ratio": (
                    self.stats["gpu_computations"]
                    / (self.stats["gpu_computations"] + self.stats["cpu_computations"])
                    * 100
                    if (self.stats["gpu_computations"] + self.stats["cpu_computations"]) > 0
                    else 0
                ),
                "data_buffer_count": len(self.data_buffers),
                "feature_cache_count": len(self.feature_cache),
            }

            return json.dumps(stats, ensure_ascii=False)

        except Exception as e:
            logger.error("获取流统计失败: %s", e)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"内部错误: {e}")
            return json.dumps({"error": str(e)})

    def stop(self):
        """停止服务"""
        logger.info("正在停止集成实时数据处理服务...")

        # 关闭所有活动流
        with self.stream_lock:
            stream_ids = list(self.active_streams.keys())
            for stream_id in stream_ids:
                self._close_stream(stream_id)

        # 关闭缓存管理器
        self.cache_manager.shutdown()

        logger.info("集成实时数据处理服务已停止")
