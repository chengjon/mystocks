"""
缓存优化组件
Cache Optimization Component
"""

import hashlib
import json
import logging
import pickle
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import psutil
import redis

logger = logging.getLogger(__name__)


@dataclass
class CacheMetrics:
    """缓存指标"""

    hit_count: int = 0
    miss_count: int = 0
    eviction_count: int = 0
    memory_usage: int = 0
    avg_hit_time: float = 0.0
    total_accesses: int = 0

    def hit_rate(self) -> float:
        """计算命中率"""
        total = self.hit_count + self.miss_count
        return self.hit_count / total * 100 if total > 0 else 0.0


@dataclass
class CacheEntry:
    """缓存条目"""

    key: str
    value: Any
    created_at: datetime
    last_accessed: datetime
    access_count: int
    size: int
    ttl: Optional[int] = None
    compressed: bool = False
    checksum: Optional[str] = None

    def is_expired(self) -> bool:
        """检查是否过期"""
        if self.ttl is None:
            return False
        return (datetime.now() - self.created_at).total_seconds() > self.ttl

    def should_evict(self, memory_limit: int) -> bool:
        """检查是否应该淘汰"""
        return self.memory_usage > memory_limit


class CacheLayer:
    """缓存层基类"""

    def __init__(self, name: str, max_size: int = 1000, ttl: int = 300):
        self.name = name
        self.max_size = max_size
        self.ttl = ttl
        self.cache: Dict[str, CacheEntry] = {}
        self.metrics = CacheMetrics()
        self.lock = threading.RLock()
        self.memory_limit = psutil.virtual_memory().total * 0.3  # 使用30%内存

    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        with self.lock:
            if key in self.cache:
                entry = self.cache[key]
                if not entry.is_expired():
                    # 更新访问信息
                    entry.last_accessed = datetime.now()
                    entry.access_count += 1
                    self.metrics.hit_count += 1

                    # 更新平均访问时间
                    current_time = time.time()
                    self.metrics.total_accesses += 1  # 先增加访问计数
                    if self.metrics.total_accesses > 0:
                        self.metrics.avg_hit_time = (
                            self.metrics.avg_hit_time * (self.metrics.total_accesses - 1) + current_time
                        ) / self.metrics.total_accesses

                    return entry.value

                # 过期，删除
                self.metrics.eviction_count += 1
                del self.cache[key]

        self.metrics.miss_count += 1
        self.metrics.total_accesses += 1
        return None

    def put(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存值"""
        with self.lock:
            # 检查内存限制
            if self._check_memory_limit():
                self._evict_expired()
                if self._check_memory_limit():
                    self._evict_lru()

            # 计算值大小
            size = len(pickle.dumps(value))

            # 创建缓存条目
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=datetime.now(),
                last_accessed=datetime.now(),
                access_count=0,
                size=size,
                ttl=ttl or self.ttl,
            )

            self.cache[key] = entry
            self.metrics.memory_usage += size

            logger.debug("Cache put: %s (%s bytes)", key, size)
            return True

    def delete(self, key: str) -> bool:
        """删除缓存值"""
        with self.lock:
            if key in self.cache:
                entry = self.cache[key]
                self.metrics.memory_usage -= entry.size
                del self.cache[key]
                return True
            return False

    def clear(self):
        """清空缓存"""
        with self.lock:
            self.cache.clear()
            self.metrics = CacheMetrics()

    def size(self) -> int:
        """获取缓存大小"""
        with self.lock:
            return len(self.cache)

    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        with self.lock:
            return {
                "name": self.name,
                "size": len(self.cache),
                "max_size": self.max_size,
                "memory_usage": self.metrics.memory_usage,
                "hit_rate": self.metrics.hit_rate(),
                "hit_count": self.metrics.hit_count,
                "miss_count": self.metrics.miss_count,
                "eviction_count": self.metrics.eviction_count,
                "avg_hit_time": self.metrics.avg_hit_time,
                "total_accesses": self.metrics.total_accesses,
                "keys": list(self.cache.keys()),
            }

    def _check_memory_limit(self) -> bool:
        """检查内存限制"""
        return self.metrics.memory_usage > self.memory_limit

    def _evict_expired(self):
        """淘汰过期条目"""
        expired_keys = []
        for key, entry in self.cache.items():
            if entry.is_expired():
                expired_keys.append(key)
                self.metrics.memory_usage -= entry.size
                self.metrics.eviction_count += 1

        for key in expired_keys:
            del self.cache[key]

    def _evict_lru(self):
        """淘汰最少使用的条目"""
        if not self.cache:
            return

        # 找到最久未使用的条目
        lru_key = min(self.cache.keys(), key=lambda k: self.cache[k].last_accessed)
        entry = self.cache[lru_key]
        self.metrics.memory_usage -= entry.size
        self.metrics.eviction_count += 1
        del self.cache[lru_key]

        logger.debug("Cache LRU eviction: %s", lru_key)

    def get_hot_keys(self, threshold: int = 10) -> List[str]:
        """获取热点键"""
        with self.lock:
            sorted_keys = sorted(
                self.cache.keys(),
                key=lambda k: self.cache[k].access_count,
                reverse=True,
            )
            return sorted_keys[:threshold]


class L1Cache(CacheLayer):
    """L1内存缓存"""

    def __init__(self, max_size: int = 1000, ttl: int = 60):
        super().__init__("L1", max_size, ttl)


class L2Cache(CacheLayer):
    """L2本地缓存"""

    def __init__(self, cache_dir: str = "/tmp/gpu_api_cache", ttl: int = 300, max_size: int = 5000):
        super().__init__("L2", max_size, ttl)
        self.cache_dir = cache_dir


class RedisCache:
    """Redis缓存"""

    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0, ttl: int = 600):
        self.host = host
        self.port = port
        self.db = db
        self.ttl = ttl
        self.client = None
        self.connect()

    def connect(self):
        try:
            self.client = redis.Redis(host=self.host, port=self.port, db=self.db, decode_responses=True)
        except Exception as e:
            logger.error("Redis connection failed: %(e)s")

    def ping(self):
        if self.client:
            return self.client.ping()
        return False

    def get(self, key):
        if self.client:
            val = self.client.get(key)
            if val:
                try:
                    return json.loads(val)
                except:
                    return val
        return None

    def set(self, key, value, ttl=None):
        if self.client:
            val = json.dumps(value) if isinstance(value, (dict, list)) else value
            return self.client.set(key, val, ex=ttl or self.ttl)
        return False

    def hset(self, name, key, value):
        if self.client:
            return self.client.hset(name, key, value)
        return False

    def hgetall(self, name):
        if self.client:
            return self.client.hgetall(name)
        return {}

    def lpush(self, name, value):
        if self.client:
            return self.client.lpush(name, value)
        return False

    def rpop(self, name):
        if self.client:
            return self.client.rpop(name)
        return None

    def delete(self, key):
        if self.client:
            return self.client.delete(key)
        return False


class CacheStrategy:
    """缓存策略"""

    READ_THROUGH = "read_through"
    WRITE_THROUGH = "write_through"
    WRITE_BEHIND = "write_behind"


class MultiLevelCache:
    """多级缓存系统"""

    def __init__(self):
        # L1: 内存缓存 (最快)
        self.l1_cache = CacheLayer("L1", max_size=1000, ttl=60)

        # L2: 本地缓存 (中等)
        self.l2_cache = CacheLayer("L2", max_size=5000, ttl=300)

        # L3: Redis缓存 (慢但持久)
        self.redis_client = None
        self.redis_cache_name = "gpu_api_cache"

        # 缓存预热配置
        self.warmup_enabled = True
        self.warmup_configs = {"hot_keys": [], "preload_queries": []}

        # 缓存策略
        self.strategies = {
            "read_through": False,
            "write_through": False,
            "write_behind": True,
            "cache_compression": True,
        }

        # 后台线程
        self.cleanup_thread = None
        self.running = False

        logger.info("Multi-level cache system initialized")

    def initialize(self, redis_host: str = "localhost", redis_port: int = 6379):
        """初始化缓存系统"""
        try:
            # 连接Redis
            self.redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                decode_responses=True,
                socket_timeout=2,
                socket_connect_timeout=2,
            )
            # 测试连接
            self.redis_client.ping()
            logger.info("Redis cache connection established")
        except Exception as e:
            logger.warning("Redis connection failed: %s", e)
            self.redis_client = None

    def start_background_tasks(self):
        """启动后台任务"""
        self.running = True
        self.cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self.cleanup_thread.start()
        logger.info("Cache background tasks started")

    def stop_background_tasks(self):
        """停止后台任务"""
        self.running = False
        if self.cleanup_thread:
            self.cleanup_thread.join(timeout=5)
        logger.info("Cache background tasks stopped")

    def get(self, key: str) -> Optional[Any]:
        """多级缓存获取"""
        start_time = time.time()

        # L1缓存
        value = self.l1_cache.get(key)
        if value is not None:
            logger.debug("Cache hit in L1: %s", key)
            return value

        # L2缓存
        value = self.l2_cache.get(key)
        if value is not None:
            # 回填到L1
            self.l1_cache.put(key, value, ttl=60)
            logger.debug("Cache hit in L2: %s", key)
            return value

        # Redis缓存
        if self.redis_client:
            try:
                redis_value = self.redis_client.get(f"{self.redis_cache_name}:{key}")
                if redis_value:
                    value = json.loads(redis_value)
                    # 回填到L1和L2
                    self.l1_cache.put(key, value, ttl=60)
                    self.l2_cache.put(key, value, ttl=300)
                    logger.debug("Cache hit in Redis: %s", key)
                    return value
            except Exception as e:
                logger.error("Redis cache read failed: %s", e)

        access_time = time.time() - start_time
        logger.debug("Cache miss: %s (%ss)", key, access_time)
        return None

    def put(self, key: str, value: Any, ttl: Optional[int] = None):
        """多级缓存设置"""
        # L1缓存
        self.l1_cache.put(key, value, min(ttl or 60, 60))

        # L2缓存
        self.l2_cache.put(key, value, ttl or 300)

        # Redis缓存
        if self.redis_client:
            try:
                redis_key = f"{self.redis_cache_name}:{key}"
                redis_value = json.dumps(value, ensure_ascii=False)
                if ttl:
                    self.redis_client.setex(redis_key, ttl, redis_value)
                else:
                    self.redis_client.set(redis_key, redis_value)
            except Exception as e:
                logger.error("Redis cache write failed: %s", e)

        logger.debug("Cache put: %s", key)

    def delete(self, key: str):
        """删除缓存"""
        self.l1_cache.delete(key)
        self.l2_cache.delete(key)

        if self.redis_client:
            try:
                redis_key = f"{self.redis_cache_name}:{key}"
                self.redis_client.delete(redis_key)
            except Exception as e:
                logger.error("Redis cache delete failed: %s", e)

    def clear(self):
        """清空所有缓存"""
        self.l1_cache.clear()
        self.l2_cache.clear()

        if self.redis_client:
            try:
                pattern = f"{self.redis_cache_name}:*"
                keys = self.redis_client.keys(pattern)
                if keys:
                    self.redis_client.delete(*keys)
            except Exception as e:
                logger.error("Redis cache clear failed: %s", e)

    def get_composite_key(self, *args) -> str:
        """生成复合键"""
        key_str = ":".join(str(arg) for arg in args)
        return hashlib.md5(key_str.encode()).hexdigest()

    def batch_get(self, keys: List[str]) -> Dict[str, Any]:
        """批量获取"""
        results = {}

        for key in keys:
            value = self.get(key)
            if value is not None:
                results[key] = value

        return results

    def batch_put(self, data: Dict[str, Any], ttl: Optional[int] = None):
        """批量设置"""
        for key, value in data.items():
            self.put(key, value, ttl)

    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        stats = {
            "l1_cache": self.l1_cache.get_stats(),
            "l2_cache": self.l2_cache.get_stats(),
            "redis_cache": "connected" if self.redis_client else "disconnected",
            "total_memory_usage": self.l1_cache.metrics.memory_usage + self.l2_cache.metrics.memory_usage,
        }

        # 计算整体命中率
        total_accesses = self.l1_cache.metrics.total_accesses
        total_hits = self.l1_cache.metrics.hit_count + self.l2_cache.metrics.hit_count

        if total_accesses > 0:
            stats["overall_hit_rate"] = total_hits / total_accesses * 100
        else:
            stats["overall_hit_rate"] = 0.0

        return stats

    def _cleanup_loop(self):
        """清理循环"""
        while self.running:
            try:
                # 每分钟执行一次清理
                time.sleep(60)

                # 清理L1缓存
                self.l1_cache._evict_expired()
                self.l1_cache._evict_lru()

                # 清理L2缓存
                self.l2_cache._evict_expired()
                self.l2_cache._evict_lru()

                logger.debug("Cache cleanup completed")

            except Exception as e:
                logger.error("Cache cleanup error: %s", e)

    def preload_cache(self, keys: List[str]):
        """预热缓存"""
        if not self.warmup_enabled:
            return

        logger.info("Preloading cache with %s keys", len(keys))

        # 批量获取数据
        data = self.batch_get(keys)

        # 缓存热点数据
        for key, value in data.items():
            self.put(key, value, ttl=300)

    def optimize_cache_performance(self) -> Dict[str, Any]:
        """优化缓存性能"""
        optimization_report = {
            "timestamp": datetime.now().isoformat(),
            "actions_taken": [],
            "performance_improvements": {},
            "recommendations": [],
        }

        # 分析L1缓存
        l1_stats = self.l1_cache.get_stats()
        if l1_stats["hit_rate"] < 80:
            optimization_report["actions_taken"].append("Increase L1 cache size")
            optimization_report["recommendations"].append("L1 cache hit rate is low, consider increasing max_size")

        # 分析L2缓存
        l2_stats = self.l2_cache.get_stats()
        if l2_stats["hit_rate"] < 60:
            optimization_report["actions_taken"].append("Review L2 cache TTL")
            optimization_report["recommendations"].append("L2 cache hit rate is low, consider adjusting TTL")

        # 检查内存使用
        total_memory = l1_stats["memory_usage"] + l2_stats["memory_usage"]
        if total_memory > psutil.virtual_memory().total * 0.5:
            optimization_report["actions_taken"].append("Reduce cache memory usage")
            optimization_report["recommendations"].append("Cache memory usage is high, consider stricter limits")

        return optimization_report


class CacheManager:
    """缓存管理器"""

    def __init__(self):
        self.multi_level_cache = MultiLevelCache()
        self.cache_strategies = {}
        self.cache_policies = {}
        self.monitoring_enabled = True

        # 缓存策略配置
        self.setup_default_strategies()

        logger.info("Cache manager initialized")

    def setup_default_strategies(self):
        """设置默认缓存策略"""
        self.cache_strategies = {
            "market_data": {
                "ttl": 30,  # 30秒
                "compression": True,
                "strategy": "read_through",
            },
            "feature_data": {
                "ttl": 300,  # 5分钟
                "compression": True,
                "strategy": "write_through",
            },
            "model_data": {
                "ttl": 3600,  # 1小时
                "compression": False,
                "strategy": "write_behind",
            },
            "computation_results": {
                "ttl": 1800,  # 30分钟
                "compression": True,
                "strategy": "read_through",
            },
        }

    def initialize(self, redis_host: str = "localhost", redis_port: int = 6379):
        """初始化缓存管理器"""
        self.multi_level_cache.initialize(redis_host, redis_port)
        self.multi_level_cache.start_background_tasks()
        logger.info("Cache manager initialized with Redis")

    def get_data(self, key: str, data_type: str = "general") -> Optional[Any]:
        """获取数据"""
        # 应用缓存策略
        strategy = self.cache_strategies.get(data_type, self.cache_strategies["general"])

        # 根据策略处理
        if strategy["strategy"] == "read_through":
            return self.read_through_get(key, data_type)
        else:
            return self.multi_level_cache.get(key)

    def set_data(self, key: str, value: Any, data_type: str = "general") -> bool:
        """设置数据"""
        # 应用缓存策略
        strategy = self.cache_strategies.get(data_type, self.cache_strategies["general"])

        # 根据策略处理
        if strategy["strategy"] == "write_through":
            return self.write_through_set(key, value, data_type)
        elif strategy["strategy"] == "write_behind":
            return self.write_behind_set(key, value, data_type)
        else:
            self.multi_level_cache.put(key, value, strategy["ttl"])
            return True

    def read_through_get(self, key: str, data_type: str) -> Optional[Any]:
        """读穿透获取"""
        # 先检查缓存
        value = self.multi_level_cache.get(key)
        if value is not None:
            return value

        # 缓存未命中，需要从数据源获取
        # 这里可以添加数据源访问逻辑
        # value = self.fetch_from_data_source(key, data_type)

        # 写入缓存
        if value is not None:
            strategy = self.cache_strategies.get(data_type, self.cache_strategies["general"])
            self.multi_level_cache.put(key, value, strategy["ttl"])

        return value

    def write_through_set(self, key: str, value: Any, data_type: str) -> bool:
        """写穿透设置"""
        # 写入缓存
        strategy = self.cache_strategies.get(data_type, self.cache_strategies["general"])
        success = self.multi_level_cache.put(key, value, strategy["ttl"])

        if success:
            # 同时写入数据源
            # self.write_to_data_source(key, value, data_type)
            pass

        return success

    def write_behind_set(self, key: str, value: Any, data_type: str) -> bool:
        """写回设置"""
        # 仅写入缓存，异步写入数据源
        strategy = self.cache_strategies.get(data_type, self.cache_strategies["general"])
        return self.multi_level_cache.put(key, value, strategy["ttl"])

    def get_cache_performance_report(self) -> Dict[str, Any]:
        """获取缓存性能报告"""
        stats = self.multi_level_cache.get_cache_stats()

        # 添加策略分析
        strategy_analysis = {}
        for data_type, strategy in self.cache_strategies.items():
            strategy_analysis[data_type] = {
                "ttl": strategy["ttl"],
                "compression": strategy["compression"],
                "strategy": strategy["strategy"],
            }

        report = {
            "timestamp": datetime.now().isoformat(),
            "cache_stats": stats,
            "strategies": strategy_analysis,
            "optimization_suggestions": self.multi_level_cache.optimize_cache_performance(),
            "hot_keys": self.multi_level_cache.l1_cache.get_hot_keys(10),
        }

        return report

    def clear_cache_by_type(self, data_type: str):
        """按类型清空缓存"""
        if data_type in self.cache_strategies:
            # 清空相关缓存
            # 这里可以根据数据类型清空特定的缓存
            logger.info("Cleared cache for type: %s", data_type)

    def monitor_cache_performance(self):
        """监控缓存性能"""
        if not self.monitoring_enabled:
            return

        stats = self.get_cache_performance_report()

        # 检查警告条件
        if stats["cache_stats"]["overall_hit_rate"] < 70:
            logger.warning("Cache hit rate low: %s%", stats["cache_stats"]["overall_hit_rate"])

        if stats["cache_stats"]["total_memory_usage"] > psutil.virtual_memory().total * 0.7:
            logger.warning("Cache memory usage high: %s bytes", stats["cache_stats"]["total_memory_usage"])

        return stats

    def shutdown(self):
        """关闭缓存管理器"""
        self.multi_level_cache.stop_background_tasks()
        logger.info("Cache manager shutdown")
