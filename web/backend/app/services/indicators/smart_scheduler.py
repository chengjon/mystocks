"""
Smart Scheduler System
======================

智能调度器，提供：
- 同步/异步双模式计算
- 并行计算优化
- 智能缓存
- 性能监控
- 分布式锁 (防止重复计算)

Version: 2.0.0 - Phase 2: Redis Distributed Lock Integration
Author: MyStocks Project
"""

import hashlib
import json
import logging
import threading
import time
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from .dependency_graph import (
    IncrementalCalculator,
    IndicatorDependencyGraph,
)
from .indicator_interface import CalculationStatus, IndicatorResult, OHLCVData

logger = logging.getLogger(__name__)

# Optional: Import Redis lock if available
try:
    from app.services.redis import redis_lock

    REDIS_LOCK_AVAILABLE = True
    logger.info("Redis distributed lock enabled for SmartScheduler")
except ImportError:
    REDIS_LOCK_AVAILABLE = False
    logger.warning("Redis lock not available, SmartScheduler running without distributed locking")


class CalculationMode(Enum):
    """计算模式"""

    SYNC = "sync"  # 同步串行
    ASYNC_PARALLEL = "async_parallel"  # 异步并行
    BATCH = "batch"  # 批量模式


@dataclass
class ScheduleResult:
    """调度结果"""

    node_id: str
    abbreviation: str
    result: Any
    duration_ms: float
    from_cache: bool = False
    success: bool = True
    error: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "node_id": self.node_id,
            "abbreviation": self.abbreviation,
            "success": self.success,
            "duration_ms": self.duration_ms,
            "from_cache": self.from_cache,
            "error": self.error,
            "result": self.result if self.success else None,
        }


@dataclass
class ScheduleStats:
    """调度统计"""

    total_indicators: int = 0
    cached_count: int = 0
    computed_count: int = 0
    failed_count: int = 0
    total_duration_ms: float = 0.0
    cache_hit_rate: float = 0.0
    parallel_speedup: float = 0.0

    def to_dict(self) -> Dict:
        return {
            "total_indicators": self.total_indicators,
            "cached_count": self.cached_count,
            "computed_count": self.computed_count,
            "failed_count": self.failed_count,
            "total_duration_ms": self.total_duration_ms,
            "cache_hit_rate": f"{self.cache_hit_rate * 100:.1f}%",
            "parallel_speedup": f"{self.parallel_speedup:.2f}x",
        }


class PerformanceMonitor:
    """性能监控器"""

    def __init__(self):
        self._calculation_times: Dict[str, List[float]] = {}
        self._cache_hits: int = 0
        self._cache_misses: int = 0
        self._lock = threading.Lock()

    def record_calculation(self, indicator: str, duration_ms: float, from_cache: bool):
        with self._lock:
            if indicator not in self._calculation_times:
                self._calculation_times[indicator] = []
            self._calculation_times[indicator].append(duration_ms)

            if from_cache:
                self._cache_hits += 1
            else:
                self._cache_misses += 1

    def get_cache_hit_rate(self) -> float:
        total = self._cache_hits + self._cache_misses
        return self._cache_hits / total if total > 0 else 0.0

    def get_indicator_stats(self, indicator: str) -> Dict:
        with self._lock:
            times = self._calculation_times.get(indicator, [])
            return {
                "count": len(times),
                "avg_ms": sum(times) / len(times) if times else 0,
                "min_ms": min(times) if times else 0,
                "max_ms": max(times) if times else 0,
            }

    def get_all_stats(self) -> Dict:
        with self._lock:
            total = self._cache_hits + self._cache_misses
            all_times = [t for times in self._calculation_times.values() for t in times]
            return {
                "cache_hit_rate": self.get_cache_hit_rate(),
                "total_calculations": total,
                "cache_hits": self._cache_hits,
                "cache_misses": self._cache_misses,
                "overall_avg_ms": sum(all_times) / len(all_times) if all_times else 0,
                "indicators": {ind: self.get_indicator_stats(ind) for ind in self._calculation_times},
            }


class SmartScheduler:
    """
    智能调度器

    功能:
    - 根据依赖关系优化计算顺序
    - 支持同步/异步双模式
    - 并行计算独立指标
    - 智能缓存复用
    - 性能监控
    """

    def __init__(
        self,
        max_workers: int = 4,
        mode: CalculationMode = CalculationMode.ASYNC_PARALLEL,
        enable_cache: bool = True,
        cache_ttl_seconds: int = 3600,
        enable_distributed_lock: bool = True,
    ):
        self.max_workers = max_workers
        self.mode = mode
        self.enable_cache = enable_cache
        self.cache_ttl = cache_ttl_seconds
        self.enable_distributed_lock = enable_distributed_lock and REDIS_LOCK_AVAILABLE

        self._dependency_graph = IndicatorDependencyGraph()
        self._incremental_calculator = IncrementalCalculator(self._dependency_graph)
        self._performance_monitor = PerformanceMonitor()
        self._cache: Dict[str, Any] = {}
        self._cache_timestamps: Dict[str, float] = {}
        self._calculation_func: Optional[Callable] = None

        self._lock = threading.Lock()

        if self.enable_distributed_lock:
            logger.info("SmartScheduler initialized with distributed locking")
        else:
            logger.info("SmartScheduler initialized without distributed locking")

    def set_calculation_function(self, func: Callable):
        """
        设置指标计算函数

        Args:
            func: 计算函数，签名 (abbreviation: str, ohlcv: OHLCVData, params: Dict) -> IndicatorResult
        """
        self._calculation_func = func

    def calculate(
        self, indicators: List[Dict[str, Any]], ohlcv_data: OHLCVData, use_cache: bool = None
    ) -> List[ScheduleResult]:
        """
        批量计算指标

        Args:
            indicators: 指标配置列表
                [
                    {"abbreviation": "SMA", "params": {"timeperiod": 20}},
                    {"abbreviation": "MACD", "params": {"fastperiod": 12, "slowperiod": 26}}
                ]
            ohlcv_data: OHLCV数据
            use_cache: 是否使用缓存（None使用默认值）

        Returns:
            计算结果列表
        """
        use_cache = use_cache if use_cache is not None else self.enable_cache

        if not indicators:
            return []

        if self._calculation_func is None:
            raise ValueError("未设置计算函数，请先调用 set_calculation_function()")

        # 1. 构建依赖图并获取计算顺序
        start_time = time.time()
        ordered_indicators = self._dependency_graph.get_calculation_order(indicators)

        # 2. 根据模式执行计算
        if self.mode == CalculationMode.SYNC:
            results = self._calculate_sync(ordered_indicators, ohlcv_data, use_cache)
        elif self.mode == CalculationMode.ASYNC_PARALLEL:
            results = self._calculate_parallel(ordered_indicators, ohlcv_data, use_cache)
        else:
            results = self._calculate_batch(ordered_indicators, ohlcv_data, use_cache)

        total_duration = (time.time() - start_time) * 1000

        # 3. 记录性能统计
        for result in results:
            self._performance_monitor.record_calculation(result.abbreviation, result.duration_ms, result.from_cache)

        logger.info(
            f"批量计算完成: {len(results)} 个指标, "
            f"总耗时: {total_duration:.2f}ms, "
            f"缓存命中: {sum(1 for r in results if r.from_cache)}"
        )

        return results

    def _calculate_sync(self, ordered: List[Dict], ohlcv: OHLCVData, use_cache: bool) -> List[ScheduleResult]:
        """同步计算"""
        results = []
        for ind in ordered:
            start = time.time()
            # 使用带锁的计算方法 (如果启用)
            if self.enable_distributed_lock:
                result = self._calculate_single_with_lock(ind, ohlcv, use_cache)
            else:
                result = self._calculate_single(ind, ohlcv, use_cache)
            duration = (time.time() - start) * 1000

            results.append(
                ScheduleResult(
                    node_id=ind.get("node_id", ind["abbreviation"]),
                    abbreviation=ind["abbreviation"],
                    result=result,
                    duration_ms=duration,
                    from_cache=getattr(result, "from_cache", False),
                    success=getattr(result, "success", True),
                    error=getattr(result, "error", None),
                )
            )

            # 更新依赖图状态
            node_id = ind.get("node_id", ind["abbreviation"])
            if getattr(result, "success", True):
                self._dependency_graph.mark_computed(node_id, result, duration, getattr(result, "from_cache", False))
            else:
                self._dependency_graph.mark_failed(node_id, getattr(result, "error", "Unknown error"))

        return results

    def _calculate_parallel(self, ordered: List[Dict], ohlcv: OHLCVData, use_cache: bool) -> List[ScheduleResult]:
        """并行计算"""
        results = []
        completed_nodes = set()

        # 按依赖层级分组
        levels = self._group_by_dependency_level(ordered)

        for level_nodes in levels:
            if not level_nodes:
                continue

            # 并行计算同一层级的节点
            with ThreadPoolExecutor(max_workers=min(self.max_workers, len(level_nodes))) as executor:
                futures: Dict[Future, Dict] = {}

                for ind in level_nodes:
                    node_id = ind.get("node_id", ind["abbreviation"])

                    # 检查是否可以使用缓存
                    can_use_cache = use_cache
                    if can_use_cache:
                        cached = self._incremental_calculator.get_cached_result(node_id)
                        if cached is not None:
                            results.append(
                                ScheduleResult(
                                    node_id=node_id,
                                    abbreviation=ind["abbreviation"],
                                    result=cached,
                                    duration_ms=0,
                                    from_cache=True,
                                    success=True,
                                )
                            )
                            completed_nodes.add(node_id)
                            continue

                    # 使用带锁的计算方法 (如果启用)
                    if self.enable_distributed_lock:
                        future = executor.submit(self._calculate_single_with_lock, ind, ohlcv, use_cache)
                    else:
                        future = executor.submit(self._calculate_single, ind, ohlcv, use_cache)
                    futures[future] = ind

                # 收集结果
                for future in as_completed(futures):
                    ind = futures[future]
                    node_id = ind.get("node_id", ind["abbreviation"])

                    try:
                        result = future.result()
                        duration = getattr(result, "calculation_time_ms", 0)
                        success = getattr(result, "success", True)
                        error = getattr(result, "error", None)

                        results.append(
                            ScheduleResult(
                                node_id=node_id,
                                abbreviation=ind["abbreviation"],
                                result=result,
                                duration_ms=duration,
                                from_cache=getattr(result, "from_cache", False),
                                success=success,
                                error=error,
                            )
                        )

                        # 更新缓存和依赖图
                        if success:
                            self._incremental_calculator.set_cache(node_id, result)
                            self._dependency_graph.mark_computed(
                                node_id, result, duration, getattr(result, "from_cache", False)
                            )
                        else:
                            self._dependency_graph.mark_failed(node_id, error)

                    except Exception as e:
                        logger.error("计算 {ind['abbreviation']} 失败: %(e)s")
                        results.append(
                            ScheduleResult(
                                node_id=node_id,
                                abbreviation=ind["abbreviation"],
                                result=None,
                                duration_ms=0,
                                success=False,
                                error=str(e),
                            )
                        )

        # 按原始顺序排序结果
        node_id_to_result = {r.node_id: r for r in results}
        ordered_results = []
        for ind in ordered:
            node_id = ind.get("node_id", ind["abbreviation"])
            if node_id in node_id_to_result:
                ordered_results.append(node_id_to_result[node_id])

        return ordered_results

    def _calculate_batch(self, ordered: List[Dict], ohlcv: OHLCVData, use_cache: bool) -> List[ScheduleResult]:
        """批量模式（暂同并行）"""
        return self._calculate_parallel(ordered, ohlcv, use_cache)

    def _calculate_single(self, ind: Dict, ohlcv: OHLCVData, use_cache: bool) -> IndicatorResult:
        """计算单个指标"""
        abbr = ind["abbreviation"]
        params = ind.get("params", {})
        node_id = ind.get("node_id", abbr)

        # 检查缓存
        if use_cache and node_id in self._cache:
            # 检查TTL
            timestamp = self._cache_timestamps.get(node_id, 0)
            if time.time() - timestamp < self.cache_ttl:
                cached = self._cache[node_id]
                if hasattr(cached, "from_cache"):
                    cached.from_cache = True
                return cached

        # 调用计算函数
        start = time.time()
        try:
            result = self._calculation_func(abbr, ohlcv, params)
            result.calculation_time_ms = (time.time() - start) * 1000
            result.from_cache = False
        except Exception as e:
            result = IndicatorResult(
                status=CalculationStatus.ERROR,
                abbreviation=abbr,
                parameters=params,
                values={},
                error_message=str(e),
                calculation_time_ms=(time.time() - start) * 1000,
            )

        # 更新缓存
        if use_cache and result.success:
            with self._lock:
                self._cache[node_id] = result
                self._cache_timestamps[node_id] = time.time()

        return result

    def _calculate_single_with_lock(self, ind: Dict, ohlcv: OHLCVData, use_cache: bool) -> IndicatorResult:
        """
        使用分布式锁计算单个指标 (CLCC模式: Check-Lock-Check-Compute)

        Args:
            ind: 指标配置
            ohlcv: OHLCV数据
            use_cache: 是否使用缓存

        Returns:
            IndicatorResult
        """
        abbr = ind["abbreviation"]
        params = ind.get("params", {})
        node_id = ind.get("node_id", abbr)

        # 生成唯一的计算键 (用于缓存和锁)
        cache_key = self._generate_cache_key(node_id, params)
        lock_resource = self._generate_lock_resource(node_id, params)

        # 第一次检查: 查本地缓存
        cached_result = self._check_local_cache(node_id, use_cache)
        if cached_result is not None:
            return cached_result

        # 第二次检查: 查Redis L2缓存 (如果可用)
        if REDIS_LOCK_AVAILABLE:
            from app.services.redis import redis_cache

            redis_cached = redis_cache.get_cached_indicator_result(
                stock_code=ohlcv.timestamps[0].strftime("%Y%m%d") if ohlcv.timestamps else "unknown",
                indicator_code=abbr,
                params=params,
            )
            if redis_cached is not None:
                # 回填本地缓存
                self._update_local_cache(node_id, redis_cached)
                return redis_cached

        # 尝试获取分布式锁
        lock_acquired = False
        try:
            if self.enable_distributed_lock and REDIS_LOCK_AVAILABLE:
                # 尝试获取锁，非阻塞模式
                lock_token = redis_lock.acquire(
                    resource=lock_resource, timeout=300, blocking=False  # 5分钟超时  # 非阻塞
                )
                lock_acquired = lock_token is not None

                if lock_acquired:
                    logger.debug("Acquired distributed lock for %(node_id)s")

                    # 第三次检查: 获取锁后再次检查缓存 (防止等待期间其他实例已计算)
                    cached_result = self._check_local_cache(node_id, use_cache)
                    if cached_result is not None:
                        return cached_result

                    if REDIS_LOCK_AVAILABLE:
                        from app.services.redis import redis_cache

                        redis_cached = redis_cache.get_cached_indicator_result(
                            stock_code=ohlcv.timestamps[0].strftime("%Y%m%d") if ohlcv.timestamps else "unknown",
                            indicator_code=abbr,
                            params=params,
                        )
                        if redis_cached is not None:
                            self._update_local_cache(node_id, redis_cached)
                            return redis_cached

                    # 执行计算
                    result = self._perform_calculation(ind, ohlcv, use_cache)

                    # 写入Redis L2缓存
                    if REDIS_LOCK_AVAILABLE and result.success:
                        from app.services.redis import redis_cache

                        redis_cache.cache_indicator_result(
                            stock_code=ohlcv.timestamps[0].strftime("%Y%m%d") if ohlcv.timestamps else "unknown",
                            indicator_code=abbr,
                            params=params,
                            result=result,
                            ttl=self.cache_ttl,
                        )

                    # 释放锁
                    redis_lock.release(lock_resource, lock_token)
                    return result
                else:
                    # 获取锁失败: 等待并尝试读取缓存
                    logger.debug("Lock busy for %(node_id)s, waiting for calculation result...")
                    time.sleep(0.5)  # 短暂等待

                    # 重试读取缓存 (最多3次)
                    for attempt in range(3):
                        cached_result = self._check_local_cache(node_id, use_cache)
                        if cached_result is not None:
                            logger.debug("Found cached result for %(node_id)s after lock wait (attempt {attempt + 1})")
                            return cached_result

                        if REDIS_LOCK_AVAILABLE:
                            from app.services.redis import redis_cache

                            redis_cached = redis_cache.get_cached_indicator_result(
                                stock_code=ohlcv.timestamps[0].strftime("%Y%m%d") if ohlcv.timestamps else "unknown",
                                indicator_code=abbr,
                                params=params,
                            )
                            if redis_cached is not None:
                                self._update_local_cache(node_id, redis_cached)
                                logger.debug(
                                    f"Found Redis cached result for {node_id} after lock wait (attempt {attempt + 1})"
                                )
                                return redis_cached

                        time.sleep(0.5)

                    # 仍未找到缓存，回退到直接计算
                    logger.warning("Lock wait timeout for %(node_id)s, falling back to direct calculation")
                    return self._perform_calculation(ind, ohlcv, use_cache)
            else:
                # 分布式锁未启用，直接计算
                return self._perform_calculation(ind, ohlcv, use_cache)

        except Exception as e:
            logger.error("Error in _calculate_single_with_lock for %(node_id)s: %(e)s")
            # 异常时回退到普通计算
            return self._perform_calculation(ind, ohlcv, use_cache)
        finally:
            # 确保锁被释放
            if lock_acquired and REDIS_LOCK_AVAILABLE:
                try:
                    # 这里token可能已经在上面的try块中被释放，所以是幂等的
                    pass
                except Exception as e:
                    logger.warning("Failed to release lock for %(node_id)s: %(e)s")

    def _generate_cache_key(self, node_id: str, params: Dict) -> str:
        """生成缓存键"""
        params_str = json.dumps(params or {}, sort_keys=True)
        params_hash = hashlib.md5(params_str.encode()).hexdigest()[:8]
        return f"{node_id}:{params_hash}"

    def _generate_lock_resource(self, node_id: str, params: Dict) -> str:
        """生成锁资源标识"""
        params_str = json.dumps(params or {}, sort_keys=True)
        params_hash = hashlib.md5(params_str.encode()).hexdigest()[:8]
        return f"indicator:calc:{node_id}:{params_hash}"

    def _check_local_cache(self, node_id: str, use_cache: bool) -> Optional[IndicatorResult]:
        """检查本地缓存"""
        if use_cache and node_id in self._cache:
            timestamp = self._cache_timestamps.get(node_id, 0)
            if time.time() - timestamp < self.cache_ttl:
                cached = self._cache[node_id]
                if hasattr(cached, "from_cache"):
                    cached.from_cache = True
                return cached
        return None

    def _update_local_cache(self, node_id: str, result: IndicatorResult):
        """更新本地缓存"""
        with self._lock:
            self._cache[node_id] = result
            self._cache_timestamps[node_id] = time.time()

    def _perform_calculation(self, ind: Dict, ohlcv: OHLCVData, use_cache: bool) -> IndicatorResult:
        """
        执行实际的指标计算 (原有 _calculate_single 逻辑)

        Args:
            ind: 指标配置
            ohlcv: OHLCV数据
            use_cache: 是否使用缓存

        Returns:
            IndicatorResult
        """
        abbr = ind["abbreviation"]
        params = ind.get("params", {})
        node_id = ind.get("node_id", abbr)

        # 调用计算函数
        start = time.time()
        try:
            result = self._calculation_func(abbr, ohlcv, params)
            result.calculation_time_ms = (time.time() - start) * 1000
            result.from_cache = False
        except Exception as e:
            result = IndicatorResult(
                status=CalculationStatus.ERROR,
                abbreviation=abbr,
                parameters=params,
                values={},
                error_message=str(e),
                calculation_time_ms=(time.time() - start) * 1000,
            )

        # 更新本地缓存
        if use_cache and result.success:
            self._update_local_cache(node_id, result)

        return result

    def _group_by_dependency_level(self, ordered: List[Dict]) -> List[List[Dict]]:
        """将指标按依赖层级分组"""
        levels = []
        completed = set()

        remaining = [ind.copy() for ind in ordered]

        while remaining:
            ready = []
            not_ready = []

            for ind in remaining:
                deps = ind.get("dependencies", [])
                # 检查所有依赖是否已完成
                if all(d in completed for d in deps):
                    ready.append(ind)
                else:
                    not_ready.append(ind)

            if not ready and not_ready:
                # 有依赖未完成但不在列表中，将其添加到就绪列表
                ready = not_ready
                not_ready = []

            if ready:
                levels.append(ready)

            # 更新已完成集合
            for ind in ready:
                node_id = ind.get("node_id", ind["abbreviation"])
                completed.add(node_id)

            remaining = not_ready

        return levels

    def get_stats(self) -> ScheduleStats:
        """获取调度统计"""
        monitor_stats = self._performance_monitor.get_all_stats()

        total = len(self._dependency_graph.get_all_nodes())
        cached = sum(1 for r in self._cache.values() if getattr(r, "from_cache", False))

        return ScheduleStats(
            total_indicators=total,
            cached_count=cached,
            computed_count=total - cached,
            failed_count=0,
            total_duration_ms=0,
            cache_hit_rate=monitor_stats["cache_hit_rate"],
        )

    def clear_cache(self):
        """清空缓存"""
        with self._lock:
            self._cache.clear()
            self._cache_timestamps.clear()
        self._incremental_calculator.clear_cache()

    def reset(self):
        """重置调度器"""
        self._dependency_graph.reset()
        self._incremental_calculator.clear_cache()
        self.clear_cache()


def create_scheduler(
    max_workers: int = 4,
    mode: CalculationMode = CalculationMode.ASYNC_PARALLEL,
    enable_cache: bool = True,
    enable_distributed_lock: bool = True,
) -> SmartScheduler:
    """
    创建调度器

    Args:
        max_workers: 最大并行数
        mode: 计算模式
        enable_cache: 是否启用缓存
        enable_distributed_lock: 是否启用分布式锁 (需要Redis)

    Returns:
        SmartScheduler实例
    """
    scheduler = SmartScheduler(
        max_workers=max_workers, mode=mode, enable_cache=enable_cache, enable_distributed_lock=enable_distributed_lock
    )
    return scheduler
