"""缓存管理器子模块"""

import logging
import time
import asyncio
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, Optional, TYPE_CHECKING
from asyncio import Lock


if TYPE_CHECKING:
    from app.core.cache.multi_level import MultiLevelCache

# Mock/Fallback constants if not imported
REDIS_CACHE_AVAILABLE = False

logger = logging.getLogger(__name__)

def get_tdengine_manager():
    return None

class CacheCoreInit:
    """缓存管理器核心：初始化与内部工具方法"""

class CacheManager:
    """
    统一缓存管理器 - 三级缓存架构
    """

    def __init__(
        self, tdengine_manager: Optional[Any] = None, redis_cache: Optional[Any] = None
    ):
        """
        初始化缓存管理器

        Args:
            tdengine_manager: TDengineManager 实例
            redis_cache: Redis多级缓存服务实例
        """
        self.tdengine = tdengine_manager or get_tdengine_manager()
        self._tdengine_available = self.tdengine is not None

        # Redis缓存服务 (L2)
        if redis_cache:
            self.redis_cache = redis_cache
            self._redis_available = True
        elif REDIS_CACHE_AVAILABLE:
            self.redis_cache = MultiLevelCache()
            self._redis_available = False  # 需要异步初始化
        else:
            self.redis_cache = None
            self._redis_available = False

        self._cache_stats: Dict[str, Any] = {
            "hits": 0,
            "misses": 0,
            "reads": 0,
            "writes": 0,
            "evictions": 0,
            "batch_operations": 0,
            "total_response_time": 0.0,
        }

        # 内存缓存层 (L1) - 仅作为Redis的快速缓存
        self._memory_cache: dict[str, Any] = {}
        self._cache_ttl: dict[str, datetime] = {}
        self._cache_lock = Lock()
        self._access_patterns: defaultdict[str, list[datetime]] = defaultdict(list)

        # 配置参数
        self._max_memory_entries = 10000  # 内存缓存最大条目数
        self._default_ttl = 300  # 默认TTL 5分钟
        self._tiered_ttl = {
            "tick_data": 30,  # 30秒
            "realtime_quote": 60,  # 1分钟
            "minute_kline": 300,  # 5分钟
            "fund_flow": 600,  # 10分钟
            "etf": 1800,  # 30分钟
            "default": 300,  # 默认5分钟
        }

    def _with_tdengine(self, fallback_value=None):
        """
        安全地执行需要 tdengine 的操作

        Args:
            fallback_value: 如果 tdengine 不可用时的返回值

        Returns:
            上下文管理器，确保 tdengine 可用
        """
        if self.tdengine is None:
            return fallback_value
        return self.tdengine

    # ==================== 三级缓存核心操作 ====================

    async def fetch_from_cache(
        self,
        symbol: str,
        data_type: str,
        timeframe: Optional[str] = None,
        days: int = 1,
    ) -> Optional[Dict[str, Any]]:
        """
        从三级缓存读取数据 (L1 -> L2 -> L3)

        采用三级缓存策略：L1(内存) -> L2(Redis) -> L3(TDengine)

        Args:
            symbol: 股票代码 (e.g., "000001")
            data_type: 数据类型 (e.g., "fund_flow", "etf")
            timeframe: 时间维度 (可选，e.g., "1d", "3d")
            days: 回溯天数 (默认 1)

        Returns:
            缓存数据字典，或 None 如果未找到
        """
        start_time = time.time()
        self._cache_stats["reads"] += 1

        # 记录访问模式
        self._record_access_pattern(symbol, data_type)

        try:
            # L1: 内存缓存 (最高性能)
            memory_result = self._get_from_memory_cache(symbol, data_type, timeframe)
            if memory_result:
                response_time = time.time() - start_time
                self._update_performance_stats(response_time, True)
                self._cache_stats["hits"] += 1
                logger.debug(
                    "✅ L1内存缓存命中",
                    symbol=symbol,
                    data_type=data_type,
                    hit_rate=self._calculate_hit_rate(),
                    response_time=response_time,
                )
                return memory_result

            # L2: Redis缓存 (分布式共享)
            cache_key = self.get_cache_key(symbol, data_type, timeframe or "1d")
            if self._redis_available and self.redis_cache:
                redis_result, found, level = await self.redis_cache.get(cache_key)
                if found:
                    response_time = time.time() - start_time
                    self._update_performance_stats(response_time, True)
                    self._cache_stats["hits"] += 1

                    # 将数据回填到L1内存缓存
                    enriched_data = {
                        "data": redis_result,
                        "source": "redis",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                    self._add_to_memory_cache(symbol, data_type, timeframe or "1d", enriched_data)

                    logger.debug(
                        f"✅ L2{level}缓存命中",
                        symbol=symbol,
                        data_type=data_type,
                        hit_rate=self._calculate_hit_rate(),
                        response_time=response_time,
                    )
                    return enriched_data

            # L3: TDengine缓存 (持久化存储)
            cache_data = None
            if self.tdengine is not None:
                cache_data = await self._write_to_tdengine(  # 复用异步TDengine方法
                    symbol=symbol,
                    data_type=data_type,
                    timeframe=timeframe or "1d",
                    data={},  # 读取模式
                    timestamp=None,
                )

            if cache_data:
                response_time = time.time() - start_time
                self._update_performance_stats(response_time, True)
                self._cache_stats["hits"] += 1

                # 将数据回填到L1+L2缓存
                enriched_data = {
                    "data": cache_data,
                    "source": "tdengine",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
                self._add_to_memory_cache(symbol, data_type, timeframe or "1d", enriched_data)

                # 异步回填到Redis (不阻塞响应)
                if self._redis_available and self.redis_cache:
                    asyncio.create_task(
                        self.redis_cache.set(cache_key, enriched_data, ttl=self._get_tiered_ttl(data_type))
                    )

                logger.debug(
                    "✅ L3 TDengine缓存命中",
                    symbol=symbol,
                    data_type=data_type,
                    hit_rate=self._calculate_hit_rate(),
                    response_time=response_time,
                )
                return enriched_data

            # 缓存未命中
            self._cache_stats["misses"] += 1
            response_time = time.time() - start_time
            self._update_performance_stats(response_time, False)

            logger.debug(
                "⚠️ 三级缓存全部未命中",
                symbol=symbol,
                data_type=data_type,
                hit_rate=self._calculate_hit_rate(),
                response_time=response_time,
            )
            return None

        except Exception as e:
            response_time = time.time() - start_time
            self._update_performance_stats(response_time, False)
            logger.error(
                "❌ 三级缓存读取失败",
                symbol=symbol,
                data_type=data_type,
                error=str(e),
                response_time=response_time,
            )
            return None

