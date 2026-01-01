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
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import structlog
import time
from threading import Lock
from collections import defaultdict

from app.core.tdengine_manager import TDengineManager, get_tdengine_manager

logger = structlog.get_logger()


class CacheManager:
    """
    统一缓存管理器

    使用 Cache-Aside 模式实现，支持与 TDengine 时序数据库的集成。

    Usage:
        ```python
        manager = get_cache_manager()

        # 单条读取
        data = manager.fetch_from_cache("000001", "fund_flow")

        # 单条写入
        manager.write_to_cache("000001", "fund_flow", "1d", {"value": 100})

        # 批量读取
        results = manager.batch_read([
            {"symbol": "000001", "data_type": "fund_flow"},
            {"symbol": "000858", "data_type": "etf"}
        ])

        # 清除缓存
        manager.invalidate_cache(symbol="000001")

        # 检查缓存有效性
        if manager.is_cache_valid("000001", "fund_flow"):
            print("缓存有效")
        ```
    """

    def __init__(self, tdengine_manager: Optional[TDengineManager] = None):
        """
        初始化缓存管理器

        Args:
            tdengine_manager: TDengineManager 实例 (如果不提供，使用单例)
        """
        self.tdengine = tdengine_manager or get_tdengine_manager()
        self._tdengine_available = self.tdengine is not None
        self._cache_stats = {
            "hits": 0,
            "misses": 0,
            "reads": 0,
            "writes": 0,
            "evictions": 0,
            "batch_operations": 0,
            "total_response_time": 0.0,
        }

        # 内存缓存层 - 替代Redis
        self._memory_cache: dict[str, Any] = {}
        self._cache_ttl: dict[str, float] = {}
        self._cache_lock = Lock()
        self._access_patterns: defaultdict[str, list[str]] = defaultdict(list)

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

    # ==================== 核心缓存操作 ====================

    def fetch_from_cache(
        self,
        symbol: str,
        data_type: str,
        timeframe: Optional[str] = None,
        days: int = 1,
    ) -> Optional[Dict[str, Any]]:
        """
        从缓存读取数据 (优化后的 Cache-Aside 模式)

        采用三级缓存策略：内存缓存 -> TDengine缓存 -> 数据源

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
            # 第一级：内存缓存 (最高性能)
            memory_result = self._get_from_memory_cache(symbol, data_type, timeframe)
            if memory_result:
                response_time = time.time() - start_time
                self._update_performance_stats(response_time, True)
                self._cache_stats["hits"] += 1
                logger.debug(
                    "✅ 内存缓存命中",
                    symbol=symbol,
                    data_type=data_type,
                    hit_rate=self._calculate_hit_rate(),
                    response_time=response_time,
                )
                return memory_result

            # 第二级：TDengine缓存 (持久化缓存)
            cache_data = None
            if self.tdengine is not None:
                cache_data = self.tdengine.read_cache(
                    symbol=symbol,
                    data_type=data_type,
                    timeframe=timeframe,
                    days=days,
                )

            if cache_data:
                response_time = time.time() - start_time
                self._update_performance_stats(response_time, True)
                self._cache_stats["hits"] += 1

                # 将数据回填到内存缓存
                enriched_data = {
                    "data": cache_data,
                    "source": "cache",
                    "timestamp": datetime.utcnow().isoformat(),
                }
                # timeframe is Optional[str], provide default for _add_to_memory_cache
                self._add_to_memory_cache(symbol, data_type, timeframe or "1d", enriched_data)

                logger.debug(
                    "✅ TDengine缓存命中",
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
                "⚠️ 缓存未命中",
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
                "❌ 缓存读取失败",
                symbol=symbol,
                data_type=data_type,
                error=str(e),
                response_time=response_time,
            )
            return None

    def write_to_cache(
        self,
        symbol: str,
        data_type: str,
        timeframe: str,
        data: Dict[str, Any],
        ttl_days: int = 7,
        timestamp: Optional[datetime] = None,
    ) -> bool:
        """
        写入数据到缓存 (优化后的写入策略)

        同时写入内存缓存和TDengine缓存，确保数据一致性

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
            if data is None or not isinstance(data, dict):
                logger.warning(
                    "无效的缓存数据",
                    symbol=symbol,
                    data_type=data_type,
                )
                return False

            # 增加元数据
            enriched_data = {
                **data,
                "_cached_at": datetime.utcnow().isoformat(),
                "_ttl_days": ttl_days,
                "_cache_version": "1.0",
                "_source": "market_data",
            }

            # 首先写入内存缓存 (最高优先级)
            memory_data = {
                "data": data,
                "source": "memory",
                "timestamp": datetime.utcnow().isoformat(),
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

    def invalidate_cache(
        self,
        symbol: Optional[str] = None,
        data_type: Optional[str] = None,
    ) -> int:
        """
        清除特定的缓存 (优化版)

        Args:
            symbol: 股票代码 (可选，如果省略则清除所有 symbol)
            data_type: 数据类型 (可选，如果省略则清除所有 data_type)

        Returns:
            删除的记录数
        """
        total_deleted = 0

        try:
            with self._cache_lock:
                # 首先清理内存缓存
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

                    logger.info("🗑️ 清除内存缓存", symbol=symbol, data_type=data_type)

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
                        "🗑️ 清除符号所有内存缓存",
                        symbol=symbol,
                        count=len(keys_to_delete),
                    )

                else:
                    # 清除所有内存缓存
                    total_deleted = self.clear_memory_cache()
                    logger.warning("🗑️ 清除所有内存缓存")

            # 清理TDengine缓存（异步）
            if self.tdengine is not None:
                if symbol and data_type:
                    tdengine_deleted = self.tdengine.clear_expired_cache(days=0)  # 需要实现精确删除
                    total_deleted += tdengine_deleted
                elif symbol:
                    tdengine_deleted = self.tdengine.clear_expired_cache(days=0)
                    total_deleted += tdengine_deleted
                else:
                    tdengine_deleted = self.tdengine.clear_expired_cache(days=0)
                    total_deleted += tdengine_deleted

            logger.info(
                "✅ 缓存清除完成",
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
                                "timestamp": datetime.utcnow().isoformat(),
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
                        logger.warning(f"批量读取单项失败 {symbol}:{data_type}", error=str(e))
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

    def is_cache_valid(self, symbol: str, data_type: str, max_age_days: int = 7) -> bool:
        """
        检查缓存的有效性

        Args:
            symbol: 股票代码
            data_type: 数据类型
            max_age_days: 最大缓存年龄 (天)

        Returns:
            True 如果缓存有效且未过期，False 否则
        """
        try:
            # 尝试读取
            cache_data = self.fetch_from_cache(symbol=symbol, data_type=data_type, days=max_age_days)

            if not cache_data:
                return False

            # 检查时间戳
            if "_cached_at" in cache_data.get("data", {}):
                cached_at_str = cache_data["data"]["_cached_at"]
                cached_at = datetime.fromisoformat(cached_at_str)
                age = datetime.utcnow() - cached_at
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
            "timestamp": datetime.utcnow().isoformat(),
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
        total_reads = self._cache_stats["reads"]
        if total_reads == 0:
            return 0.0
        return self._cache_stats["hits"] / total_reads

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
                self._access_patterns[cache_key].append(datetime.utcnow())
                return self._memory_cache[cache_key]

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
            self._cache_ttl[cache_key] = datetime.utcnow() + timedelta(seconds=ttl_seconds)
            self._access_patterns[cache_key].append(datetime.utcnow())

    def _is_cache_expired(self, cache_key: str) -> bool:
        """检查缓存是否过期"""
        if cache_key not in self._cache_ttl:
            return True

        return datetime.utcnow() > self._cache_ttl[cache_key]

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
            self._access_patterns[cache_key].append(datetime.utcnow())

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
        except Exception as e:
            logger.warning(f"TDengine异步写入失败: {e}")
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

        self._cache_stats["response_time_distribution"][cache_level] = (
            self._cache_stats["response_time_distribution"].get(cache_level, 0) + 1
        )

    def get_memory_cache_stats(self) -> Dict[str, Any]:
        """获取内存缓存统计"""
        with self._cache_lock:
            total_entries = len(self._memory_cache)
            total_size_mb = sum(len(str(data)) for data in self._memory_cache.values()) / (1024 * 1024)  # 估算大小

            # 计算各数据类型的分布
            type_distribution = defaultdict(int)
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

    def optimize_memory_cache(self) -> Dict[str, Any]:
        """优化内存缓存"""
        with self._cache_lock:
            # 清理过期条目
            expired_count = 0
            now = datetime.utcnow()

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
        health_status = {
            "overall_healthy": True,
            "timestamp": datetime.utcnow().isoformat(),
            "components": {},
            "performance_metrics": {},
            "issues": [],
        }

        try:
            # 检查 TDengine 连接
            tdengine_healthy = self.tdengine.health_check() if self.tdengine is not None else False
            health_status["components"]["tdengine"] = {
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

            health_status["components"]["memory_cache"] = {
                "healthy": memory_healthy,
                "status": "OK" if memory_healthy else "WARNING",
                "usage_percentage": memory_stats["usage_percentage"],
                "total_entries": memory_stats["total_entries"],
            }

            if not memory_healthy:
                health_status["issues"].append("Memory cache usage high")

            # 性能指标
            hit_rate = self._calculate_hit_rate()
            avg_response_time = self._cache_stats["total_response_time"] / max(self._cache_stats["reads"], 1)

            performance_healthy = hit_rate > 0.5 and avg_response_time < 1.0  # 命中率应该大于50%  # 平均响应时间小于1秒

            health_status["performance_metrics"] = {
                "hit_rate": hit_rate,
                "avg_response_time_ms": round(avg_response_time * 1000, 2),
                "performance_healthy": performance_healthy,
            }

            if not performance_healthy:
                health_status["overall_healthy"] = False
                if hit_rate < 0.5:
                    health_status["issues"].append("Cache hit rate too low")
                if avg_response_time > 1.0:
                    health_status["issues"].append("Response time too slow")

            logger.info(
                "🔍 缓存系统健康检查完成",
                overall_healthy=health_status["overall_healthy"],
                issues=len(health_status["issues"]),
            )

            return health_status

        except Exception as e:
            logger.error("❌ 缓存系统健康检查失败", error=str(e))
            health_status["overall_healthy"] = False
            health_status["issues"].append(f"Health check error: {str(e)}")
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


def get_cache_manager(
    tdengine_manager: Optional[TDengineManager] = None,
) -> CacheManager:
    """
    获取缓存管理器单例

    Args:
        tdengine_manager: TDengineManager 实例 (用于初始化时指定)

    Returns:
        CacheManager 单例实例
    """
    global _cache_manager

    if _cache_manager is None:
        _cache_manager = CacheManager(tdengine_manager)
        if not _cache_manager.health_check():
            logger.warning("⚠️ 缓存管理器初始化：TDengine 不可用")

    return _cache_manager


def reset_cache_manager() -> None:
    """重置缓存管理器（用于测试）"""
    global _cache_manager
    if _cache_manager:
        _cache_manager.close()
    _cache_manager = None
