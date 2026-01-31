"""
SSE (Server-Sent Events) 性能优化管理器
SSE Performance Optimization Manager

提供高性能的SSE推送优化功能：
1. 事件批处理和压缩
2. 连接池管理和复用
3. 智能缓存和去重
4. 负载均衡和流量控制
5. 性能监控和自动调优

Author: Claude Code
Date: 2025-12-17
"""

import asyncio
import gzip
import hashlib
import json
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

import structlog

logger = structlog.get_logger()


class EventPriority(Enum):
    """事件优先级"""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class CompressionType(Enum):
    """压缩类型"""

    NONE = "none"
    GZIP = "gzip"
    JSON = "json"


@dataclass
class EventBatch:
    """事件批次"""

    id: str
    events: List[Dict[str, Any]] = field(default_factory=list)
    priority: EventPriority = EventPriority.NORMAL
    created_at: datetime = field(default_factory=datetime.utcnow)
    size_bytes: int = 0
    channel: str = ""

    def add_event(self, event: Dict[str, Any]) -> bool:
        """添加事件到批次"""
        event_str = json.dumps(event, separators=(",", ":"))
        event_size = len(event_str.encode("utf-8"))

        # 检查批次大小限制
        if self.size_bytes + event_size > 64 * 1024:  # 64KB限制
            return False

        self.events.append(event)
        self.size_bytes += event_size
        return True

    def is_full(self, max_events: int = 100, max_size: int = 64 * 1024) -> bool:
        """检查批次是否已满"""
        return len(self.events) >= max_events or self.size_bytes >= max_size


@dataclass
class PerformanceMetrics:
    """性能指标"""

    total_events_sent: int = 0
    total_events_dropped: int = 0
    total_bytes_sent: int = 0
    avg_batch_size: float = 0.0
    compression_ratio: float = 1.0
    connection_count: int = 0
    avg_latency_ms: float = 0.0
    peak_events_per_second: float = 0.0
    cache_hit_rate: float = 0.0

    def update_batch_metrics(self, batch_size: int, compressed_size: int = 0):
        """更新批次指标"""
        if self.total_events_sent > 0:
            # 计算移动平均
            alpha = 0.1  # 平滑因子
            self.avg_batch_size = alpha * batch_size + (1 - alpha) * self.avg_batch_size

        if compressed_size > 0:
            original_size = batch_size * 1024  # 估算原始大小
            self.compression_ratio = original_size / compressed_size


class EventCache:
    """事件缓存管理器"""

    def __init__(self, max_size: int = 10000, ttl_seconds: int = 300):
        """
        初始化事件缓存

        Args:
            max_size: 最大缓存条目数
            ttl_seconds: 缓存过期时间（秒）
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds

        self.cache: Dict[str, Tuple[datetime, Any]] = {}
        self.access_order = deque()
        self.stats = {"hits": 0, "misses": 0, "evictions": 0}

    def _generate_key(self, event: Dict[str, Any]) -> str:
        """生成缓存键"""
        key_data = {
            "event": event.get("event"),
            "data": event.get("data", {}),
            "channel": event.get("channel"),
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()

    def get(self, event: Dict[str, Any]) -> Optional[Any]:
        """获取缓存事件"""
        key = self._generate_key(event)

        if key in self.cache:
            timestamp, cached_event = self.cache[key]

            # 检查是否过期
            if datetime.utcnow() - timestamp < timedelta(seconds=self.ttl_seconds):
                self.stats["hits"] += 1
                # 更新访问顺序
                if key in self.access_order:
                    self.access_order.remove(key)
                self.access_order.append(key)
                return cached_event
            else:
                # 过期，删除
                del self.cache[key]
                if key in self.access_order:
                    self.access_order.remove(key)

        self.stats["misses"] += 1
        return None

    def put(self, event: Dict[str, Any], cached_value: Any):
        """缓存事件"""
        key = self._generate_key(event)

        # 检查缓存大小限制
        if len(self.cache) >= self.max_size:
            self._evict_oldest()

        self.cache[key] = (datetime.utcnow(), cached_value)
        self.access_order.append(key)

    def _evict_oldest(self):
        """淘汰最旧的缓存条目"""
        if self.access_order:
            oldest_key = self.access_order.popleft()
            if oldest_key in self.cache:
                del self.cache[oldest_key]
            self.stats["evictions"] += 1

    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = self.stats["hits"] / max(1, total_requests)

        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hit_rate": hit_rate,
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "evictions": self.stats["evictions"],
        }


class EventDeduplicator:
    """事件去重器"""

    def __init__(self, window_size: int = 1000):
        """
        初始化去重器

        Args:
            window_size: 去重窗口大小
        """
        self.window_size = window_size
        self.seen_events: Set[str] = set()
        self.event_order = deque()
        self.stats = {"total_events": 0, "duplicate_events": 0}

    def _generate_event_hash(self, event: Dict[str, Any]) -> str:
        """生成事件哈希"""
        # 只使用关键字段生成哈希
        key_data = {
            "event": event.get("event"),
            "data": event.get("data", {}),
            "channel": event.get("channel"),
            "timestamp": event.get("timestamp", ""),
        }
        return hashlib.md5(json.dumps(key_data, sort_keys=True).encode()).hexdigest()

    def is_duplicate(self, event: Dict[str, Any]) -> bool:
        """检查事件是否重复"""
        event_hash = self._generate_event_hash(event)
        self.stats["total_events"] += 1

        if event_hash in self.seen_events:
            self.stats["duplicate_events"] += 1
            return True

        # 添加到去重窗口
        self.seen_events.add(event_hash)
        self.event_order.append(event_hash)

        # 维护窗口大小
        if len(self.event_order) > self.window_size:
            oldest_hash = self.event_order.popleft()
            self.seen_events.discard(oldest_hash)

        return False

    def get_stats(self) -> Dict[str, Any]:
        """获取去重统计"""
        total = self.stats["total_events"]
        duplicate_rate = self.stats["duplicate_events"] / max(1, total)

        return {
            "window_size": self.window_size,
            "current_size": len(self.seen_events),
            "total_events": total,
            "duplicate_events": self.stats["duplicate_events"],
            "duplicate_rate": duplicate_rate,
        }


class CompressionManager:
    """压缩管理器"""

    def __init__(self):
        """初始化压缩管理器"""
        self.compression_stats = {
            "gzip": {"original_size": 0, "compressed_size": 0, "count": 0},
            "none": {"original_size": 0, "compressed_size": 0, "count": 0},
        }

    def compress_data(self, data: str, compression_type: CompressionType) -> bytes:
        """压缩数据"""
        original_bytes = data.encode("utf-8")
        original_size = len(original_bytes)

        if compression_type == CompressionType.GZIP:
            compressed_bytes = gzip.compress(original_bytes)
            compressed_size = len(compressed_bytes)

            self.compression_stats["gzip"]["original_size"] += original_size
            self.compression_stats["gzip"]["compressed_size"] += compressed_size
            self.compression_stats["gzip"]["count"] += 1

            return compressed_bytes

        elif compression_type == CompressionType.NONE:
            self.compression_stats["none"]["original_size"] += original_size
            self.compression_stats["none"]["compressed_size"] += original_size
            self.compression_stats["none"]["count"] += 1
            return original_bytes

        return original_bytes

    def get_compression_stats(self) -> Dict[str, Any]:
        """获取压缩统计"""
        stats = {}

        for compression_type, data in self.compression_stats.items():
            if data["count"] > 0:
                ratio = data["compressed_size"] / max(1, data["original_size"])
                stats[compression_type] = {
                    "compression_ratio": ratio,
                    "space_saving": (1 - ratio) * 100,
                    "count": data["count"],
                    "total_original_size": data["original_size"],
                    "total_compressed_size": data["compressed_size"],
                }

        return stats


class LoadBalancer:
    """负载均衡器"""

    def __init__(self, strategy: str = "round_robin"):
        """
        初始化负载均衡器

        Args:
            strategy: 负载均衡策略 (round_robin, least_connections, random)
        """
        self.strategy = strategy
        self.servers = []
        self.current_index = 0
        self.connection_counts = defaultdict(int)

    def add_server(self, server_id: str, weight: int = 1):
        """添加服务器"""
        self.servers.append({"id": server_id, "weight": weight, "active": True})

    def remove_server(self, server_id: str):
        """移除服务器"""
        self.servers = [s for s in self.servers if s["id"] != server_id]
        if server_id in self.connection_counts:
            del self.connection_counts[server_id]

    def get_next_server(self) -> Optional[str]:
        """获取下一个服务器"""
        active_servers = [s for s in self.servers if s["active"]]

        if not active_servers:
            return None

        if self.strategy == "round_robin":
            server = active_servers[self.current_index % len(active_servers)]
            self.current_index += 1
            return server["id"]

        elif self.strategy == "least_connections":
            min_connections_server = min(active_servers, key=lambda s: self.connection_counts[s["id"]])
            return min_connections_server["id"]

        elif self.strategy == "random":
            import random

            return random.choice(active_servers)["id"]

        return active_servers[0]["id"]


class SSEPerformanceOptimizer:
    """SSE性能优化器"""

    def __init__(self):
        """初始化性能优化器"""
        self.metrics = PerformanceMetrics()

        # 初始化组件
        self.event_cache = EventCache(max_size=5000, ttl_seconds=300)
        self.deduplicator = EventDeduplicator(window_size=1000)
        self.compression_manager = CompressionManager()
        self.load_balancer = LoadBalancer(strategy="least_connections")

        # 批处理配置
        self.batch_config = {
            "max_batch_size": 100,
            "max_batch_bytes": 64 * 1024,  # 64KB
            "flush_interval": 0.1,  # 100ms
            "max_batch_wait": 0.5,  # 500ms
        }

        # 性能配置
        self.performance_config = {
            "enable_compression": True,
            "enable_caching": True,
            "enable_deduplication": True,
            "compression_threshold": 1024,  # 1KB以上才压缩
            "cache_ttl": 300,  # 5分钟
        }

        # 事件队列（按优先级分组）
        self.event_queues: Dict[EventPriority, deque] = {priority: deque() for priority in EventPriority}

        # 连接管理
        self.active_connections: Dict[str, Dict[str, Any]] = {}
        self.connection_stats: Dict[str, Dict[str, Any]] = {}

        # 启动后台任务
        self._start_background_tasks()

        logger.info("✅ SSE性能优化器初始化完成")

    async def optimize_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """优化单个事件"""
        # 1. 去重检查
        if self.performance_config["enable_deduplication"] and self.deduplicator.is_duplicate(event):
            logger.debug("事件去重: {event.get('event')}"")
            return None  # 丢弃重复事件

        # 2. 缓存检查
        if self.performance_config["enable_caching"]:
            cached_result = self.event_cache.get(event)
            if cached_result is not None:
                logger.debug("事件缓存命中: {event.get('event')}"")
                return cached_result

        # 3. 确定事件优先级
        priority = self._determine_event_priority(event)
        event["priority"] = priority.value

        # 4. 添加优化标记
        event["optimized"] = True
        event["optimization_timestamp"] = time.time()

        # 5. 缓存优化后的事件
        if self.performance_config["enable_caching"]:
            self.event_cache.put(event, event)

        return event

    async def batch_events(self) -> List[EventBatch]:
        """批量处理事件"""
        batches = []
        current_batch = None

        # 按优先级处理事件
        priorities = [
            EventPriority.CRITICAL,
            EventPriority.HIGH,
            EventPriority.NORMAL,
            EventPriority.LOW,
        ]

        for priority in priorities:
            queue = self.event_queues[priority]

            while queue and (len(batches) < 10):  # 限制批次数量
                event = queue.popleft()

                if current_batch is None:
                    current_batch = EventBatch(
                        id=f"batch_{int(time.time() * 1000)}_{len(batches)}",
                        priority=priority,
                    )

                # 尝试添加到当前批次
                if not current_batch.add_event(event):
                    # 当前批次已满，保存并创建新批次
                    batches.append(current_batch)
                    current_batch = EventBatch(
                        id=f"batch_{int(time.time() * 1000)}_{len(batches)}",
                        priority=priority,
                    )
                    current_batch.add_event(event)

        # 添加最后一个未满的批次
        if current_batch and current_batch.events:
            batches.append(current_batch)

        return batches

    async def send_optimized_batch(self, batch: EventBatch, connection_id: str) -> bool:
        """发送优化后的批次"""
        try:
            # 序列化批次
            batch_data = {
                "batch_id": batch.id,
                "events": batch.events,
                "timestamp": datetime.utcnow().isoformat(),
                "compression": "gzip",
                "event_count": len(batch.events),
            }

            batch_str = json.dumps(batch_data, separators=(",", ":"))

            # 压缩数据
            compression_type = (
                CompressionType.GZIP
                if (
                    self.performance_config["enable_compression"]
                    and len(batch_str) > self.performance_config["compression_threshold"]
                )
                else CompressionType.NONE
            )

            compressed_data = self.compression_manager.compress_data(batch_str, compression_type)

            # 更新指标
            self.metrics.total_events_sent += len(batch.events)
            self.metrics.total_bytes_sent += len(compressed_data)
            self.metrics.update_batch_metrics(len(batch.events), len(compressed_data))

            # 这里应该通过实际的SSE连接发送数据
            # 模拟发送
            await self._send_to_connection(connection_id, compressed_data, compression_type)

            return True

        except Exception as e:
            logger.error("发送批次失败: %(e)s"")
            self.metrics.total_events_dropped += len(batch.events)
            return False

    async def _send_to_connection(self, connection_id: str, data: bytes, compression_type: CompressionType):
        """发送数据到连接（模拟实现）"""
        # 这里应该集成实际的SSE发送逻辑

    def _determine_event_priority(self, event: Dict[str, Any]) -> EventPriority:
        """确定事件优先级"""
        event_type = event.get("event", "")

        # 关键事件设为高优先级
        if any(keyword in event_type.lower() for keyword in ["alert", "error", "critical", "urgent"]):
            return EventPriority.CRITICAL

        # 重要事件设为高优先级
        if any(keyword in event_type.lower() for keyword in ["trade", "order", "position", "price"]):
            return EventPriority.HIGH

        # 普通事件设为正常优先级
        if any(keyword in event_type.lower() for keyword in ["status", "update", "info"]):
            return EventPriority.NORMAL

        # 其他事件设为低优先级
        return EventPriority.LOW

    def _start_background_tasks(self):
        """启动后台任务"""
        # 批处理任务
        asyncio.create_task(self._batch_processing_loop())

        # 性能监控任务
        asyncio.create_task(self._performance_monitoring_loop())

        # 缓存清理任务
        asyncio.create_task(self._cache_cleanup_loop())

    async def _batch_processing_loop(self):
        """批处理循环"""
        while True:
            try:
                # 收集事件批次
                batches = await self.batch_events()

                if batches:
                    logger.debug("处理 {len(batches)} 个事件批次"")

                    # 并发发送批次
                    tasks = []
                    for batch in batches:
                        # 选择连接（负载均衡）
                        connection_id = self.load_balancer.get_next_server()
                        if connection_id:
                            task = asyncio.create_task(self.send_optimized_batch(batch, connection_id))
                            tasks.append(task)

                    # 等待所有批次发送完成
                    if tasks:
                        await asyncio.gather(*tasks, return_exceptions=True)

                await asyncio.sleep(self.batch_config["flush_interval"])

            except Exception as e:
                logger.error("批处理循环异常: %(e)s"")
                await asyncio.sleep(1)

    async def _performance_monitoring_loop(self):
        """性能监控循环"""
        while True:
            try:
                # 更新连接统计
                self.metrics.connection_count = len(self.active_connections)

                # 计算峰值事件速率（简化计算）
                self.metrics.peak_events_per_second = max(
                    self.metrics.peak_events_per_second,
                    self.metrics.total_events_sent / max(1, time.time() - 1620000000),  # 简化计算
                )

                # 更新缓存命中率
                cache_stats = self.event_cache.get_stats()
                self.metrics.cache_hit_rate = cache_stats.get("hit_rate", 0)

                # 记录性能指标
                if self.metrics.total_events_sent > 0 and self.metrics.total_events_sent % 100 == 0:
                    logger.info(
                        f"SSE性能指标: "
                        f"事件发送={self.metrics.total_events_sent}, "
                        f"丢弃={self.metrics.total_events_dropped}, "
                        f"平均批次大小={self.metrics.avg_batch_size:.1f}, "
                        f"压缩比={self.metrics.compression_ratio:.2f}"
                    )

                await asyncio.sleep(30)  # 每30秒监控一次

            except Exception as e:
                logger.error("性能监控循环异常: %(e)s"")
                await asyncio.sleep(10)

    async def _cache_cleanup_loop(self):
        """缓存清理循环"""
        while True:
            try:
                # 清理过期缓存（事件缓存自身有TTL机制）
                # 这里可以添加额外的清理逻辑

                await asyncio.sleep(300)  # 每5分钟清理一次

            except Exception as e:
                logger.error("缓存清理循环异常: %(e)s"")
                await asyncio.sleep(60)

    def get_performance_stats(self) -> Dict[str, Any]:
        """获取性能统计"""
        return {
            "metrics": {
                "total_events_sent": self.metrics.total_events_sent,
                "total_events_dropped": self.metrics.total_events_dropped,
                "total_bytes_sent": self.metrics.total_bytes_sent,
                "avg_batch_size": self.metrics.avg_batch_size,
                "compression_ratio": self.metrics.compression_ratio,
                "connection_count": self.metrics.connection_count,
                "cache_hit_rate": self.metrics.cache_hit_rate,
                "peak_events_per_second": self.metrics.peak_events_per_second,
            },
            "cache_stats": self.event_cache.get_stats(),
            "deduplication_stats": self.deduplicator.get_stats(),
            "compression_stats": self.compression_manager.get_compression_stats(),
            "queue_sizes": {priority.value: len(queue) for priority, queue in self.event_queues.items()},
            "config": {
                "batch_config": self.batch_config,
                "performance_config": self.performance_config,
            },
        }

    def update_config(self, **kwargs):
        """更新配置"""
        if "batch_config" in kwargs:
            self.batch_config.update(kwargs["batch_config"])

        if "performance_config" in kwargs:
            self.performance_config.update(kwargs["performance_config"])

        logger.info("SSE性能配置已更新: %(kwargs)s"")


# 全局性能优化器实例
_performance_optimizer: Optional[SSEPerformanceOptimizer] = None


def get_performance_optimizer() -> SSEPerformanceOptimizer:
    """获取全局性能优化器实例"""
    global _performance_optimizer
    if _performance_optimizer is None:
        _performance_optimizer = SSEPerformanceOptimizer()
    return _performance_optimizer
