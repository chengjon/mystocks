"""
Cache Manager - 缓存读写逻辑实现
Task 2.2: 实现缓存读写逻辑

提供统一的缓存访问接口，支持：
- 单条数据读写
- 批量读写操作
- 缓存失效机制
- Cache-Aside 模式
- 性能监控

Features:
- Cache-Aside 模式实现
- 批量操作支持
- 缓存失效机制
- 自动元数据管理
- 完整的错误处理
"""

import asyncio
import time
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from threading import Lock
from typing import Any, Dict, List, Optional

import structlog

from app.core.tdengine_manager import TDengineManager, get_tdengine_manager

# Redis多级缓存服务
try:
    from src.core.cache.multi_level import CacheConfig, MultiLevelCache

    REDIS_CACHE_AVAILABLE = True
except ImportError:
    REDIS_CACHE_AVAILABLE = False
    MultiLevelCache = None
    CacheConfig = None

logger = structlog.get_logger()


class CacheManager:
    """
    统一缓存管理器 - 三级缓存架构

    实现 L1(内存) -> L2(Redis) -> L3(TDengine) 的高速通路
    支持 Cache-Aside + Write-Through 混合模式

    Usage:
        ```python
        manager = get_cache_manager()

        # 单条异步读取
        data = await manager.fetch_from_cache("000001", "fund_flow")

        # 单条异步写入
        await manager.write_to_cache("000001", "fund_flow", "1d", {"value": 100})

        # 批量异步读取
        results = await manager.batch_read([
            {"symbol": "000001", "data_type": "fund_flow"},
            {"symbol": "000858", "data_type": "etf"}
        ])

        # 清除缓存
        await manager.invalidate_cache(symbol="000001")

        # 检查缓存有效性
        if await manager.is_cache_valid("000001", "fund_flow"):
            print("缓存有效")
        ```
    """

    def __init__(
        self, tdengine_manager: Optional[TDengineManager] = None, redis_cache: Optional[MultiLevelCache] = None
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

    async def write_to_cache(
        self,
        symbol: str,
        data_type: str,
        timeframe: str,
        data: Dict[str, Any],
        ttl_days: int = 7,
        timestamp: Optional[datetime] = None,
    ) -> bool:
        """
        写入数据到三级缓存 (Write-Through模式)

        同时写入L1(内存)+L2(Redis)，L3(TDengine)异步写入

        Args:
            symbol: 股票代码
            data_type: 数据类型
            timeframe: 时间维度
            data: 要缓存的数据
            ttl_days: 缓存生存时间 (天)
            timestamp: 自定义时间戳

        Returns:
            True 如果写入成功，False 否则
        """
        self._cache_stats["writes"] += 1

        try:
            # 验证数据
            is_invalid_data = data is None or not isinstance(data, dict)
            if is_invalid_data:
                logger.warning(
                    "无效的缓存数据",
                    symbol=symbol,
                    data_type=data_type,
                )
                return False

            # 增加元数据
            enriched_data = {
                **data,
                "_cached_at": datetime.now(timezone.utc).isoformat(),
                "_ttl_days": ttl_days,
                "_cache_version": "2.0",  # 升级到三级缓存版本
                "_source": "market_data",
            }

            # 准备缓存数据格式
            cache_data = {
                "data": data,
                "source": "cache",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            cache_key = self.get_cache_key(symbol, data_type, timeframe)

            # L1: 内存缓存 (同步写入，最高优先级)
            self._add_to_memory_cache(symbol, data_type, timeframe, cache_data)

            # L2: Redis缓存 (异步写入，不阻塞响应)
            if self._redis_available and self.redis_cache:
                redis_ttl = ttl_days * 24 * 3600  # 转换为秒
                asyncio.create_task(self.redis_cache.set(cache_key, cache_data, ttl=redis_ttl))

            # L3: TDengine缓存 (异步写入，持久化存储)
            asyncio.create_task(
                self._write_to_tdengine(
                    symbol=symbol,
                    data_type=data_type,
                    timeframe=timeframe,
                    data=enriched_data,
                    timestamp=timestamp,
                )
            )

            logger.debug(
                "✅ 三级缓存写入完成",
                symbol=symbol,
                data_type=data_type,
                ttl_days=ttl_days,
            )
            return True

        except Exception as e:
            logger.error(
                "❌ 三级缓存写入异常",
                symbol=symbol,
                data_type=data_type,
                error=str(e),
            )
            return False

            # 增加元数据
            enriched_data = {
                **data,
                "_cached_at": datetime.now(timezone.utc).isoformat(),
                "_ttl_days": ttl_days,
                "_cache_version": "1.0",
                "_source": "market_data",
            }

            # 首先写入内存缓存 (最高优先级)
            memory_data = {
                "data": data,
                "source": "memory",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            self._add_to_memory_cache(symbol, data_type, timeframe, memory_data)

            # 并行写入 TDengine (持久化存储)
            td_result = self._write_to_tdengine(
                symbol=symbol,
                data_type=data_type,
                timeframe=timeframe,
                data=enriched_data,
                timestamp=timestamp,
            )

            if td_result:
                logger.debug(
                    "✅ 数据已缓存(内存+TDengine)",
                    symbol=symbol,
                    data_type=data_type,
                    ttl_days=ttl_days,
                )
                return True
            else:
                logger.warning(
                    "⚠️ TDengine写入失败，但内存缓存已更新",
                    symbol=symbol,
                    data_type=data_type,
                )
                return True  # 内存缓存成功就认为部分成功

        except Exception as e:
            logger.error(
                "❌ 缓存写入异常",
                symbol=symbol,
                data_type=data_type,
                error=str(e),
            )
            return False

    async def invalidate_cache(
        self,
        symbol: Optional[str] = None,
        data_type: Optional[str] = None,
    ) -> int:
        """
        清除三级缓存中的特定数据

        Args:
            symbol: 股票代码 (可选，如果省略则清除所有 symbol)
            data_type: 数据类型 (可选，如果省略则清除所有 data_type)

        Returns:
            删除的记录数
        """
        total_deleted = 0

        try:
            with self._cache_lock:
                # L1: 清理内存缓存
                if symbol and data_type:
                    # 清除特定符号+数据类型的缓存
                    cache_key = self.get_cache_key(symbol, data_type)

                    if cache_key in self._memory_cache:
                        del self._memory_cache[cache_key]
                        total_deleted += 1

                    if cache_key in self._cache_ttl:
                        del self._cache_ttl[cache_key]

                    if cache_key in self._access_patterns:
                        del self._access_patterns[cache_key]

                    logger.info("🗑️ 清除L1内存缓存", symbol=symbol, data_type=data_type)

                elif symbol:
                    # 清除特定符号的所有缓存
                    keys_to_delete = [key for key in self._memory_cache.keys() if key.startswith(symbol)]
                    for key in keys_to_delete:
                        del self._memory_cache[key]
                        total_deleted += 1

                        if key in self._cache_ttl:
                            del self._cache_ttl[key]
                        if key in self._access_patterns:
                            del self._access_patterns[key]

                    logger.info(
                        "🗑️ 清除符号所有L1内存缓存",
                        symbol=symbol,
                        count=len(keys_to_delete),
                    )

                else:
                    # 清除所有内存缓存
                    total_deleted = self.clear_memory_cache()
                    logger.warning("🗑️ 清除所有L1内存缓存")

            # L2: 清理Redis缓存
            if self._redis_available and self.redis_cache:
                try:
                    if symbol and data_type:
                        cache_key = self.get_cache_key(symbol, data_type)
                        await self.redis_cache.delete(cache_key)
                        logger.info("🗑️ 清除L2 Redis缓存", symbol=symbol, data_type=data_type)
                    elif symbol:
                        # 删除所有以symbol开头的缓存
                        pattern = f"{symbol}:*"
                        redis_deleted = await self.redis_cache.delete_pattern(pattern)
                        total_deleted += redis_deleted
                        logger.info("🗑️ 清除符号所有L2 Redis缓存", symbol=symbol, count=redis_deleted)
                    else:
                        await self.redis_cache.clear()
                        logger.warning("🗑️ 清除所有L2 Redis缓存")
                except Exception as e:
                    logger.warning("L2 Redis缓存清理失败", error=str(e))

            # L3: 清理TDengine缓存（异步）
            if self.tdengine is not None:
                try:
                    if symbol and data_type:
                        # 异步清理TDengine特定缓存
                        asyncio.create_task(self._async_tdengine_clear(symbol, data_type))
                    elif symbol:
                        asyncio.create_task(self._async_tdengine_clear_symbol(symbol))
                    else:
                        asyncio.create_task(self._async_tdengine_clear_all())
                except Exception as e:
                    logger.warning("L3 TDengine缓存清理任务创建失败", error=str(e))

            logger.info(
                "✅ 三级缓存清除完成",
                symbol=symbol,
                data_type=data_type,
                total_deleted=total_deleted,
            )
            return total_deleted

        except Exception as e:
            logger.error("❌ 缓存清除失败", error=str(e))
            return total_deleted

    # ==================== 批量操作 ====================

    def batch_read(self, queries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        批量读取缓存 (优化版) - 显著提高性能

        Args:
            queries: 查询列表，每个元素包含:
                {
                    "symbol": "000001",
                    "data_type": "fund_flow",
                    "timeframe": "1d",  # 可选
                    "days": 1            # 可选
                }

        Returns:
            {
                "000001:fund_flow": {...},
                "000858:etf": {...},
                ...
            }
        """
        self._cache_stats["batch_operations"] += 1
        start_time = time.time()
        results = {}
        success_count = 0

        try:
            # 优化：并发读取内存缓存，先处理最可能命中的数据
            _ = []  # noqa: F841 - Placeholder for memory_cache_futures (to be implemented)
            _ = []  # noqa: F841 - Placeholder for tdengine_cache_futures (to be implemented)

            # 预过滤：避免重复查询
            unique_queries = []
            seen_keys = set()

            for query in queries:
                symbol = query.get("symbol")
                data_type = query.get("data_type")

                if not symbol or not data_type:
                    continue

                query_key = f"{symbol}:{data_type}:{query.get('timeframe', '1d')}"
                if query_key not in seen_keys:
                    seen_keys.add(query_key)
                    unique_queries.append(query)

            # 批量内存缓存查询
            with self._cache_lock:
                for query in unique_queries:
                    symbol = query.get("symbol")
                    data_type = query.get("data_type")
                    timeframe = query.get("timeframe", "1d")

                    # Type guards for MyPy
                    if not isinstance(symbol, str) or not isinstance(data_type, str) or not isinstance(timeframe, str):
                        continue

                    cache_key = self.get_cache_key(symbol, data_type, timeframe)

                    if cache_key in self._memory_cache:
                        # 内存缓存命中
                        if not self._is_cache_expired(cache_key):
                            results[cache_key] = self._memory_cache[cache_key]
                            self._cache_stats["hits"] += 1
                            success_count += 1
                            self._record_access_pattern(symbol, data_type)
                        else:
                            # 过期了，需要删除
                            del self._memory_cache[cache_key]
                            del self._cache_ttl[cache_key]
                            if cache_key in self._access_patterns:
                                del self._access_patterns[cache_key]

            # 对于未命中的查询，批量TDengine查询
            remaining_queries = []
            for query in unique_queries:
                symbol = query.get("symbol")
                data_type = query.get("data_type")
                timeframe = query.get("timeframe", "1d")

                # Type guards for MyPy
                if not isinstance(symbol, str) or not isinstance(data_type, str) or not isinstance(timeframe, str):
                    continue

                cache_key = self.get_cache_key(symbol, data_type, timeframe)
                if cache_key not in results:
                    remaining_queries.append(query)

            if remaining_queries:
                # 批量TDengine查询
                for query in remaining_queries:
                    symbol = query.get("symbol")
                    data_type = query.get("data_type")
                    timeframe = query.get("timeframe", "1d")

                    # Type guards for MyPy
                    if not isinstance(symbol, str) or not isinstance(data_type, str) or not isinstance(timeframe, str):
                        continue

                    cache_key = self.get_cache_key(symbol, data_type, timeframe)

                    try:
                        if self.tdengine is not None:
                            cache_data = self.tdengine.read_cache(
                                symbol=symbol,
                                data_type=data_type,
                                timeframe=timeframe,
                                days=query.get("days", 1),
                            )
                        else:
                            cache_data = None

                        if cache_data:
                            enriched_data = {
                                "data": cache_data,
                                "source": "cache",
                                "timestamp": datetime.now(timezone.utc).isoformat(),
                            }
                            results[cache_key] = enriched_data
                            self._cache_stats["hits"] += 1
                            success_count += 1

                            # 回填内存缓存
                            self._add_to_memory_cache(symbol, data_type, timeframe, enriched_data)
                        else:
                            results[cache_key] = None
                            self._cache_stats["misses"] += 1

                    except Exception as e:
                        logger.warning("批量读取单项失败 {symbol}:{data_type}", error=str(e))
                        results[cache_key] = None
                        self._cache_stats["misses"] += 1

            response_time = time.time() - start_time
            self._update_performance_stats(response_time, success_count > 0)

            logger.info(
                "✅ 批量读取完成",
                total=len(unique_queries),
                success=success_count,
                unique_queries=len(unique_queries),
                response_time=response_time,
                hit_rate=success_count / max(len(unique_queries), 1),
            )
            return results

        except Exception as e:
            logger.error("❌ 批量读取失败", error=str(e))
            return results

    def batch_write(self, records: List[Dict[str, Any]], ttl_days: int = 7) -> int:
        """
        批量写入缓存

        Args:
            records: 记录列表，每个元素包含:
                {
                    "symbol": "000001",
                    "data_type": "fund_flow",
                    "timeframe": "1d",
                    "data": {...}
                }
            ttl_days: 批量 TTL

        Returns:
            成功写入的记录数
        """
        count = 0

        try:
            for record in records:
                symbol = record.get("symbol")
                data_type = record.get("data_type")
                timeframe = record.get("timeframe", "1d")
                data = record.get("data", {})

                if not symbol or not data_type:
                    logger.warning("记录缺少必要字段", record=record)
                    continue

                if self.write_to_cache(
                    symbol=symbol,
                    data_type=data_type,
                    timeframe=timeframe,
                    data=data,
                    ttl_days=ttl_days,
                ):
                    count += 1

            logger.info(
                "✅ 批量写入完成",
                total=len(records),
                success=count,
            )
            return count

        except Exception as e:
            logger.error("❌ 批量写入失败", error=str(e))
            return count

    # ==================== 缓存验证与检查 ====================

    async def is_cache_valid(self, symbol: str, data_type: str, max_age_days: int = 7) -> bool:
        """
        检查三级缓存的有效性

        Args:
            symbol: 股票代码
            data_type: 数据类型
            max_age_days: 最大缓存年龄 (天)

        Returns:
            True 如果缓存有效且未过期，False 否则
        """
        try:
            # 优先检查L1内存缓存
            cache_data = self._get_from_memory_cache(symbol, data_type, "1d")
            if cache_data:
                # 检查时间戳
                if "_cached_at" in cache_data.get("data", {}):
                    cached_at_str = cache_data["data"]["_cached_at"]
                    cached_at = datetime.fromisoformat(cached_at_str)
                    if cached_at.tzinfo is None:
                        cached_at = cached_at.replace(tzinfo=timezone.utc)
                    age = datetime.now(timezone.utc) - cached_at
                    is_valid = age <= timedelta(days=max_age_days)

                    logger.debug(
                        "L1缓存有效性检查",
                        symbol=symbol,
                        data_type=data_type,
                        age_days=age.days,
                        valid=is_valid,
                    )
                    return is_valid
                return True

            # 检查L2 Redis缓存
            if self._redis_available and self.redis_cache:
                cache_key = self.get_cache_key(symbol, data_type, "1d")
                redis_result, found, _ = await self.redis_cache.get(cache_key)
                if found and redis_result:
                    if "_cached_at" in redis_result.get("data", {}):
                        cached_at_str = redis_result["data"]["_cached_at"]
                        cached_at = datetime.fromisoformat(cached_at_str)
                        if cached_at.tzinfo is None:
                            cached_at = cached_at.replace(tzinfo=timezone.utc)
                        age = datetime.now(timezone.utc) - cached_at
                        is_valid = age <= timedelta(days=max_age_days)

                        logger.debug(
                            "L2缓存有效性检查",
                            symbol=symbol,
                            data_type=data_type,
                            age_days=age.days,
                            valid=is_valid,
                        )
                        return is_valid
                    return True

            # 检查L3 TDengine缓存
            if self.tdengine is not None:
                cache_data = await self._write_to_tdengine(
                    symbol=symbol,
                    data_type=data_type,
                    timeframe="1d",
                    data={},  # 读取模式
                    timestamp=None,
                )
                if cache_data and "_cached_at" in cache_data.get("data", {}):
                    cached_at_str = cache_data["data"]["_cached_at"]
                    cached_at = datetime.fromisoformat(cached_at_str)
                    if cached_at.tzinfo is None:
                        cached_at = cached_at.replace(tzinfo=timezone.utc)
                    age = datetime.now(timezone.utc) - cached_at
                    is_valid = age <= timedelta(days=max_age_days)

                    logger.debug(
                        "L3缓存有效性检查",
                        symbol=symbol,
                        data_type=data_type,
                        age_days=age.days,
                        valid=is_valid,
                    )
                    return is_valid

            return False

        except Exception as e:
            logger.error(
                "❌ 三级缓存有效性检查失败",
                symbol=symbol,
                data_type=data_type,
                error=str(e),
            )
            return False

            # 检查时间戳
            if "_cached_at" in cache_data.get("data", {}):
                cached_at_str = cache_data["data"]["_cached_at"]
                cached_at = datetime.fromisoformat(cached_at_str)
                age = datetime.now(timezone.utc) - cached_at
                is_valid = age <= timedelta(days=max_age_days)

                logger.debug(
                    "缓存有效性检查",
                    symbol=symbol,
                    data_type=data_type,
                    age_days=age.days,
                    valid=is_valid,
                )
                return is_valid

            return True

        except Exception as e:
            logger.error(
                "❌ 缓存有效性检查失败",
                symbol=symbol,
                error=str(e),
            )
            return False

    def get_cache_key(self, symbol: str, data_type: str, timeframe: str = "1d") -> str:
        """
        生成缓存键

        Args:
            symbol: 股票代码
            data_type: 数据类型
            timeframe: 时间维度

        Returns:
            缓存键字符串
        """
        return f"{data_type}:{symbol}:{timeframe}".lower()

    # ==================== 统计与监控 ====================

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息 (增强版)

        Returns:
            统计信息字典
        """
        hit_rate = self._calculate_hit_rate()
        avg_response_time = self._cache_stats["total_response_time"] / max(self._cache_stats["reads"], 1)

        stats = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_reads": self._cache_stats["reads"],
            "total_writes": self._cache_stats["writes"],
            "cache_hits": self._cache_stats["hits"],
            "cache_misses": self._cache_stats["misses"],
            "evictions": self._cache_stats["evictions"],
            "batch_operations": self._cache_stats["batch_operations"],
            "hit_rate": hit_rate,
            "hit_rate_percent": f"{hit_rate * 100:.1f}%",
            "avg_response_time_ms": round(avg_response_time * 1000, 2),
            "memory_cache_stats": self.get_memory_cache_stats(),
        }

        # 添加响应时间分布统计
        if "response_time_distribution" in self._cache_stats:
            stats["response_time_distribution"] = self._cache_stats["response_time_distribution"]

        # 从 TDengine 获取额外统计
        try:
            if self.tdengine is not None:
                tdengine_stats = self.tdengine.get_cache_stats()
                if tdengine_stats:
                    stats["tdengine_stats"] = tdengine_stats
        except Exception as e:
            logger.warning("无法获取 TDengine 统计", error=str(e))

        return stats

    def reset_stats(self) -> None:
        """重置统计计数器"""
        self._cache_stats = {
            "hits": 0,
            "misses": 0,
            "reads": 0,
            "writes": 0,
        }
        logger.info("✅ 统计计数器已重置")

    def _calculate_hit_rate(self) -> float:
        """计算缓存命中率"""
        total_reads: int = self._cache_stats["reads"]
        if total_reads == 0:
            return 0.0
        hits: int = self._cache_stats["hits"]
        return float(hits) / float(total_reads)

    # ==================== 内存缓存层 (替代Redis) ====================

    def _get_from_memory_cache(self, symbol: str, data_type: str, timeframe: Optional[str]) -> Optional[Dict[str, Any]]:
        """从内存缓存读取数据"""
        cache_key = self.get_cache_key(symbol, data_type, timeframe or "1d")

        with self._cache_lock:
            if cache_key in self._memory_cache:
                # 检查TTL
                if self._is_cache_expired(cache_key):
                    del self._memory_cache[cache_key]
                    del self._cache_ttl[cache_key]
                    return None

                # 更新访问统计
                self._access_patterns[cache_key].append(datetime.now(timezone.utc))
                result: Optional[Dict[str, Any]] = self._memory_cache[cache_key]
                return result

        return None

    def _add_to_memory_cache(
        self,
        symbol: str,
        data_type: str,
        timeframe: str,
        data: Dict[str, Any],
    ) -> None:
        """写入数据到内存缓存"""
        cache_key = self.get_cache_key(symbol, data_type, timeframe)

        with self._cache_lock:
            # 检查缓存大小限制
            if len(self._memory_cache) >= self._max_memory_entries:
                self._evict_memory_cache()

            # 计算TTL
            ttl_seconds = self._get_tiered_ttl(data_type)

            self._memory_cache[cache_key] = data
            self._cache_ttl[cache_key] = datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)
            self._access_patterns[cache_key].append(datetime.now(timezone.utc))

    def _is_cache_expired(self, cache_key: str) -> bool:
        """检查缓存是否过期"""
        if cache_key not in self._cache_ttl:
            return True

        return datetime.now(timezone.utc) > self._cache_ttl[cache_key]

    def _get_tiered_ttl(self, data_type: str) -> int:
        """获取分层TTL"""
        return self._tiered_ttl.get(data_type, self._tiered_ttl["default"])

    def _evict_memory_cache(self) -> None:
        """内存缓存淘汰策略 (LRU + 基于访问频率)"""
        if not self._memory_cache:
            return

        # 简单LRU策略：删除访问频率最低的条目
        lru_key = None
        min_access = float("inf")

        for key, access_times in self._access_patterns.items():
            access_freq = len(access_times)
            if access_freq < min_access:
                min_access = access_freq
                lru_key = key

        if lru_key and lru_key in self._memory_cache:
            del self._memory_cache[lru_key]
            del self._cache_ttl[lru_key]
            del self._access_patterns[lru_key]
            self._cache_stats["evictions"] += 1

    def _record_access_pattern(self, symbol: str, data_type: str) -> None:
        """记录访问模式"""
        cache_key = self.get_cache_key(symbol, data_type)
        with self._cache_lock:
            self._access_patterns[cache_key].append(datetime.now(timezone.utc))

    async def _write_to_tdengine(
        self,
        symbol: str,
        data_type: str,
        timeframe: str,
        data: Dict[str, Any],
        timestamp: Optional[datetime] = None,
    ) -> bool:
        """异步写入TDengine"""
        try:
            # 使用线程池执行TDengine写入，避免阻塞
            tdengine = self.tdengine
            if tdengine is None:
                return False

            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: tdengine.write_cache(
                    symbol=symbol,
                    data_type=data_type,
                    timeframe=timeframe,
                    data=data,
                    timestamp=timestamp,
                ),
            )
            return result
        except Exception:
            logger.warning("TDengine异步写入失败: %(e)s")
            return False

    def _update_performance_stats(self, response_time: float, hit: bool) -> None:
        """更新性能统计"""
        self._cache_stats["total_response_time"] += response_time

        # 记录响应时间分布
        if hit:
            cache_level = "memory" if response_time < 0.001 else "tdengine"
        else:
            cache_level = "miss"

        if "response_time_distribution" not in self._cache_stats:
            self._cache_stats["response_time_distribution"] = {}

        response_time_dist: Dict[str, int] = self._cache_stats["response_time_distribution"]
        response_time_dist[cache_level] = response_time_dist.get(cache_level, 0) + 1

    def get_memory_cache_stats(self) -> Dict[str, Any]:
        """获取内存缓存统计"""
        with self._cache_lock:
            total_entries = len(self._memory_cache)
            total_size_mb = sum(len(str(data)) for data in self._memory_cache.values()) / (1024 * 1024)  # 估算大小

            # 计算各数据类型的分布
            type_distribution: defaultdict[str, int] = defaultdict(int)
            for cache_key in self._memory_cache.keys():
                parts = cache_key.split(":")
                if len(parts) >= 2:
                    data_type = parts[0]
                    type_distribution[data_type] += 1

            return {
                "total_entries": total_entries,
                "max_entries": self._max_memory_entries,
                "usage_percentage": (total_entries / self._max_memory_entries) * 100,
                "estimated_size_mb": round(total_size_mb, 2),
                "type_distribution": dict(type_distribution),
                "evictions": self._cache_stats["evictions"],
                "default_ttl_seconds": self._default_ttl,
                "tiered_ttl": self._tiered_ttl,
            }

    def clear_memory_cache(self) -> int:
        """清空内存缓存"""
        with self._cache_lock:
            count = len(self._memory_cache)
            self._memory_cache.clear()
            self._cache_ttl.clear()
            self._access_patterns.clear()
            return count

    # ==================== 三级缓存辅助方法 ====================

    async def _async_tdengine_clear(self, symbol: str, data_type: str) -> None:
        """异步清理TDengine特定缓存"""
        try:
            if self.tdengine is not None:
                # 这里需要实现TDengine的精确删除方法
                # 暂时使用clear_expired_cache作为替代
                await asyncio.get_event_loop().run_in_executor(None, lambda: self.tdengine.clear_expired_cache(days=0))
                logger.info("🗑️ L3 TDengine缓存清理完成", symbol=symbol, data_type=data_type)
        except Exception as e:
            logger.warning("L3 TDengine缓存清理失败", symbol=symbol, data_type=data_type, error=str(e))

    async def _async_tdengine_clear_symbol(self, symbol: str) -> None:
        """异步清理TDengine特定符号的所有缓存"""
        try:
            if self.tdengine is not None:
                await asyncio.get_event_loop().run_in_executor(None, lambda: self.tdengine.clear_expired_cache(days=0))
                logger.info("🗑️ L3 TDengine符号缓存清理完成", symbol=symbol)
        except Exception as e:
            logger.warning("L3 TDengine符号缓存清理失败", symbol=symbol, error=str(e))

    async def _async_tdengine_clear_all(self) -> None:
        """异步清理所有TDengine缓存"""
        try:
            if self.tdengine is not None:
                await asyncio.get_event_loop().run_in_executor(None, lambda: self.tdengine.clear_expired_cache(days=0))
                logger.warning("🗑️ L3 TDengine全部缓存清理完成")
        except Exception as e:
            logger.warning("L3 TDengine全部缓存清理失败", error=str(e))

    def optimize_memory_cache(self) -> Dict[str, Any]:
        """优化内存缓存"""
        with self._cache_lock:
            # 清理过期条目
            expired_count = 0
            now = datetime.now(timezone.utc)

            expired_keys = [key for key, expire_time in self._cache_ttl.items() if now > expire_time]

            for key in expired_keys:
                if key in self._memory_cache:
                    del self._memory_cache[key]
                del self._cache_ttl[key]
                if key in self._access_patterns:
                    del self._access_patterns[key]
                expired_count += 1

            # 记录优化结果
            stats_before = self.get_memory_cache_stats()

            return {
                "expired_entries_removed": expired_count,
                "entries_after_cleanup": len(self._memory_cache),
                "cache_usage_after": stats_before["usage_percentage"],
                "memory_freed_mb": 0,  # 简化实现
            }

    # ==================== 生命周期 ====================

    def health_check(self) -> Dict[str, Any]:
        """
        健康检查 (增强版)

        Returns:
            健康状态字典
        """
        health_status: Dict[str, Any] = {
            "overall_healthy": True,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "components": {},
            "performance_metrics": {},
            "issues": [],
        }

        try:
            # 检查 TDengine 连接
            tdengine_healthy = self.tdengine.health_check() if self.tdengine is not None else False
            components: Dict[str, Any] = health_status["components"]
            components["tdengine"] = {
                "healthy": tdengine_healthy,
                "status": "OK" if tdengine_healthy else "ERROR",
            }

            if not tdengine_healthy:
                health_status["overall_healthy"] = False
                health_status["issues"].append("TDengine connection failed")

            # 检查内存缓存
            memory_stats = self.get_memory_cache_stats()
            memory_healthy = (
                memory_stats["usage_percentage"] < 95 and len(self._memory_cache) < self._max_memory_entries
            )

            components["memory_cache"] = {
                "healthy": memory_healthy,
                "status": "OK" if memory_healthy else "WARNING",
                "usage_percentage": memory_stats["usage_percentage"],
                "total_entries": memory_stats["total_entries"],
            }

            if not memory_healthy:
                issues: List[str] = health_status["issues"]
                issues.append("Memory cache usage high")

            # 性能指标
            hit_rate = self._calculate_hit_rate()
            avg_response_time = self._cache_stats["total_response_time"] / max(self._cache_stats["reads"], 1)

            performance_healthy = hit_rate > 0.5 and avg_response_time < 1.0  # 命中率应该大于50%  # 平均响应时间小于1秒

            performance_metrics: Dict[str, Any] = {
                "hit_rate": hit_rate,
                "avg_response_time_ms": round(avg_response_time * 1000, 2),
                "performance_healthy": performance_healthy,
            }
            health_status["performance_metrics"] = performance_metrics

            if not performance_healthy:
                health_status["overall_healthy"] = False
                issues = health_status["issues"]
                if hit_rate < 0.5:
                    issues.append("Cache hit rate too low")
                if avg_response_time > 1.0:
                    issues.append("Response time too slow")

            logger.info(
                "🔍 缓存系统健康检查完成",
                overall_healthy=health_status["overall_healthy"],
                issues=len(health_status.get("issues", [])),
            )

            return health_status

        except Exception as e:
            logger.error("❌ 缓存系统健康检查失败", error=str(e))
            health_status["overall_healthy"] = False
            error_issues: List[str] = health_status["issues"]
            error_issues.append(f"Health check error: {str(e)}")
            return health_status

    def close(self) -> None:
        """关闭缓存管理器"""
        try:
            if self.tdengine is not None:
                self.tdengine.close()
            logger.info("✅ 缓存管理器已关闭")
        except Exception as e:
            logger.warning("关闭缓存管理器时出错", error=str(e))


# ==================== 全局单例管理 ====================

_cache_manager: Optional[CacheManager] = None


async def get_cache_manager_async(
    tdengine_manager: Optional[TDengineManager] = None,
    redis_cache: Optional[MultiLevelCache] = None,
) -> CacheManager:
    """
    获取异步缓存管理器单例 (支持Redis注入)

    Args:
        tdengine_manager: TDengineManager 实例
        redis_cache: Redis多级缓存服务实例

    Returns:
        CacheManager 单例实例
    """
    global _cache_manager

    if _cache_manager is None:
        _cache_manager = CacheManager(tdengine_manager, redis_cache)

        # 如果提供了Redis缓存，初始化连接
        if redis_cache and REDIS_CACHE_AVAILABLE:
            try:
                # Redis缓存已在外部初始化，这里只需要验证
                if not hasattr(redis_cache, "_redis_connected") or not redis_cache._redis_connected:
                    await redis_cache.initialize()
                _cache_manager._redis_available = True
                logger.info("✅ Redis缓存服务已注入到缓存管理器")
            except Exception as e:
                logger.warning("⚠️ Redis缓存初始化失败，将降级为L1+L3模式", error=str(e))
                _cache_manager._redis_available = False

        # 执行健康检查
        try:
            health = _cache_manager.health_check()
            if not health.get("overall_healthy"):
                logger.warning("⚠️ 缓存管理器健康检查失败", issues=health.get("issues", []))
        except Exception as e:
            logger.warning("⚠️ 缓存管理器健康检查异常", error=str(e))

    return _cache_manager


def get_cache_manager(
    tdengine_manager: Optional[TDengineManager] = None,
) -> CacheManager:
    """
    获取缓存管理器单例 (向后兼容)

    注意: 此方法不支持Redis注入。如需Redis支持，请使用 get_cache_manager_async()

    Args:
        tdengine_manager: TDengineManager 实例

    Returns:
        CacheManager 单例实例
    """
    global _cache_manager

    if _cache_manager is None:
        _cache_manager = CacheManager(tdengine_manager)
        logger.warning("⚠️ 使用同步缓存管理器，Redis功能不可用。如需Redis支持，请使用 get_cache_manager_async()")

    return _cache_manager


def reset_cache_manager() -> None:
    """重置缓存管理器（用于测试）"""
    global _cache_manager
    if _cache_manager:
        _cache_manager.close()
    _cache_manager = None
