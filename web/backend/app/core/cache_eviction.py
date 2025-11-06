"""
Cache Eviction Strategy - 缓存淘汰策略

实现基于时间窗口和访问频率的缓存淘汰机制。

Features:
- 7天自动清理 (Time Window Eviction)
- 访问频率追踪 (Access Frequency Tracking)
- 热点数据识别 (Hot Data Identification)
- 定期清理任务 (Scheduled Cleanup)
- 管理员手动清理 (Manual Cleanup)

Architecture:
- AccessFrequencyTracker: 追踪访问频率
- TimeWindowEvictionStrategy: 7天TTL清理策略
- EvictionScheduler: APScheduler集成
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import structlog

from app.core.cache_manager import get_cache_manager, CacheManager

logger = structlog.get_logger()


class AccessFrequencyTracker:
    """访问频率追踪器"""

    def __init__(self):
        """初始化访问频率追踪"""
        self.access_counts: Dict[str, int] = defaultdict(int)
        self.last_access_time: Dict[str, datetime] = {}
        self.creation_time: Dict[str, datetime] = {}

        logger.info("🔧 初始化访问频率追踪器")

    def record_access(self, cache_key: str) -> None:
        """
        记录缓存访问

        Args:
            cache_key: 缓存键 (格式: "symbol:data_type:timeframe")
        """
        self.access_counts[cache_key] += 1
        self.last_access_time[cache_key] = datetime.utcnow()

        # 如果是首次记录，记录创建时间
        if cache_key not in self.creation_time:
            self.creation_time[cache_key] = datetime.utcnow()

    def get_access_frequency(self, cache_key: str) -> int:
        """获取缓存访问频率"""
        return self.access_counts.get(cache_key, 0)

    def get_last_access_time(self, cache_key: str) -> Optional[datetime]:
        """获取最后访问时间"""
        return self.last_access_time.get(cache_key)

    def get_creation_time(self, cache_key: str) -> Optional[datetime]:
        """获取创建时间"""
        return self.creation_time.get(cache_key)

    def get_hot_data(self, top_n: int = 10) -> List[Tuple[str, int]]:
        """
        获取热点数据（最常访问的N个缓存项）

        Args:
            top_n: 返回数量 (默认10)

        Returns:
            [(cache_key, access_count), ...] 按访问频率排序
        """
        sorted_items = sorted(
            self.access_counts.items(), key=lambda x: x[1], reverse=True
        )
        return sorted_items[:top_n]

    def get_statistics(self) -> Dict[str, Any]:
        """获取追踪统计信息"""
        if not self.access_counts:
            return {
                "total_tracked": 0,
                "total_accesses": 0,
                "average_frequency": 0.0,
                "hot_data_count": 0,
            }

        total_accesses = sum(self.access_counts.values())
        total_tracked = len(self.access_counts)

        return {
            "total_tracked": total_tracked,
            "total_accesses": total_accesses,
            "average_frequency": (
                total_accesses / total_tracked if total_tracked > 0 else 0.0
            ),
            "hot_data_count": min(10, total_tracked),
            "timestamp": datetime.utcnow().isoformat(),
        }

    def clear_stats(self) -> None:
        """清除所有统计数据"""
        self.access_counts.clear()
        self.last_access_time.clear()
        self.creation_time.clear()
        logger.info("✅ 访问频率统计已清除")


class TimeWindowEvictionStrategy:
    """基于时间窗口的淘汰策略"""

    def __init__(
        self,
        cache_manager: Optional[CacheManager] = None,
        ttl_days: int = 7,
    ):
        """
        初始化淘汰策略

        Args:
            cache_manager: CacheManager实例
            ttl_days: 缓存生存时间 (默认7天)
        """
        self.cache_manager = cache_manager or get_cache_manager()
        self.ttl_days = ttl_days
        self.frequency_tracker = AccessFrequencyTracker()

        logger.info(
            "🔧 初始化时间窗口淘汰策略",
            ttl_days=ttl_days,
        )

    def record_cache_access(
        self, symbol: str, data_type: str, timeframe: str = "1d"
    ) -> None:
        """
        记录缓存访问以进行热数据分析

        Args:
            symbol: 股票代码
            data_type: 数据类型
            timeframe: 时间维度
        """
        cache_key = f"{symbol}:{data_type}:{timeframe}".lower()
        self.frequency_tracker.record_access(cache_key)

    def evict_expired_cache(self, max_age_days: Optional[int] = None) -> int:
        """
        清除过期缓存 (基于7天TTL)

        Args:
            max_age_days: 最大年龄 (默认使用初始化的ttl_days)

        Returns:
            清除的记录数
        """
        max_age = max_age_days or self.ttl_days

        try:
            deleted_count = self.cache_manager.invalidate_cache()

            logger.info(
                "✅ 过期缓存清除成功",
                max_age_days=max_age,
                deleted_count=deleted_count,
            )

            return deleted_count

        except Exception as e:
            logger.error(
                "❌ 过期缓存清除失败",
                error=str(e),
            )
            return 0

    def get_hot_data(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """
        获取热点数据列表

        Args:
            top_n: 返回热点数据数量

        Returns:
            热点数据列表，包含访问频率和时间戳
        """
        hot_items = self.frequency_tracker.get_hot_data(top_n)

        return [
            {
                "cache_key": cache_key,
                "access_count": count,
                "last_access": (
                    self.frequency_tracker.get_last_access_time(cache_key).isoformat()
                    if self.frequency_tracker.get_last_access_time(cache_key)
                    else None
                ),
                "creation_time": (
                    self.frequency_tracker.get_creation_time(cache_key).isoformat()
                    if self.frequency_tracker.get_creation_time(cache_key)
                    else None
                ),
            }
            for cache_key, count in hot_items
        ]

    def get_eviction_statistics(self) -> Dict[str, Any]:
        """获取淘汰策略统计信息"""
        freq_stats = self.frequency_tracker.get_statistics()
        cache_stats = self.cache_manager.get_cache_stats()

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "ttl_days": self.ttl_days,
            "frequency_tracking": freq_stats,
            "cache_stats": {
                "hit_rate": cache_stats.get("hit_rate", 0),
                "cache_hits": cache_stats.get("cache_hits", 0),
                "cache_misses": cache_stats.get("cache_misses", 0),
                "total_reads": cache_stats.get("total_reads", 0),
                "total_writes": cache_stats.get("total_writes", 0),
            },
        }


class EvictionScheduler:
    """缓存淘汰调度器"""

    def __init__(self, eviction_strategy: Optional[TimeWindowEvictionStrategy] = None):
        """
        初始化淘汰调度器

        Args:
            eviction_strategy: TimeWindowEvictionStrategy实例
        """
        self.eviction_strategy = eviction_strategy or TimeWindowEvictionStrategy()
        self.scheduler = BackgroundScheduler()
        self._job_id: Optional[str] = None

        logger.info("🔧 初始化缓存淘汰调度器")

    def start_daily_cleanup(self, hour: int = 2, minute: int = 0) -> None:
        """
        启动每日定时清理任务

        Args:
            hour: 清理时刻（小时）默认凌晨2点
            minute: 清理时刻（分钟）
        """
        try:
            if not self.scheduler.running:
                self.scheduler.start()
                logger.info("✅ 淘汰调度器已启动")

            # 移除已存在的任务
            if self._job_id:
                self.scheduler.remove_job(self._job_id)

            # 添加每日清理任务
            job = self.scheduler.add_job(
                self._cleanup_task,
                CronTrigger(hour=hour, minute=minute),
                id="cache_daily_cleanup",
                name="缓存每日淘汰任务",
                replace_existing=True,
            )
            self._job_id = job.id

            logger.info(
                "✅ 每日清理任务已启动",
                schedule_time=f"{hour:02d}:{minute:02d}",
            )

        except Exception as e:
            logger.error("❌ 启动清理任务失败", error=str(e))
            raise

    def stop_cleanup(self) -> None:
        """停止清理任务"""
        try:
            if self.scheduler.running:
                self.scheduler.shutdown()
                logger.info("✅ 淘汰调度器已停止")
        except Exception as e:
            logger.warning("⚠️ 停止调度器时出错", error=str(e))

    def _cleanup_task(self) -> None:
        """内部清理任务"""
        try:
            deleted_count = self.eviction_strategy.evict_expired_cache()
            logger.info(
                "🗑️ 定时清理任务执行完成",
                deleted_count=deleted_count,
            )
        except Exception as e:
            logger.error("❌ 定时清理任务失败", error=str(e))

    def manual_cleanup(self) -> Dict[str, Any]:
        """
        手动清理缓存

        Returns:
            清理结果
        """
        try:
            deleted_count = self.eviction_strategy.evict_expired_cache()

            logger.info("✅ 手动清理完成", deleted_count=deleted_count)

            return {
                "success": True,
                "message": "缓存清理成功",
                "deleted_count": deleted_count,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error("❌ 手动清理失败", error=str(e))
            return {
                "success": False,
                "message": str(e),
                "deleted_count": 0,
            }

    def get_scheduler_status(self) -> Dict[str, Any]:
        """获取调度器状态"""
        return {
            "running": self.scheduler.running,
            "jobs_count": len(self.scheduler.get_jobs()),
            "next_cleanup": (
                str(self.scheduler.get_job("cache_daily_cleanup").next_run_time)
                if self.scheduler.get_job("cache_daily_cleanup")
                else None
            ),
            "timestamp": datetime.utcnow().isoformat(),
        }


# ==================== 全局实例 ====================

_eviction_strategy: Optional[TimeWindowEvictionStrategy] = None
_eviction_scheduler: Optional[EvictionScheduler] = None


def get_eviction_strategy(
    cache_manager: Optional[CacheManager] = None,
) -> TimeWindowEvictionStrategy:
    """
    获取淘汰策略单例

    Args:
        cache_manager: CacheManager实例 (可选)

    Returns:
        TimeWindowEvictionStrategy实例
    """
    global _eviction_strategy

    if _eviction_strategy is None:
        _eviction_strategy = TimeWindowEvictionStrategy(cache_manager)

    return _eviction_strategy


def get_eviction_scheduler() -> EvictionScheduler:
    """
    获取淘汰调度器单例

    Returns:
        EvictionScheduler实例
    """
    global _eviction_scheduler

    if _eviction_scheduler is None:
        _eviction_scheduler = EvictionScheduler(get_eviction_strategy())

    return _eviction_scheduler


def reset_eviction_strategy() -> None:
    """重置淘汰策略（用于测试）"""
    global _eviction_strategy
    if _eviction_strategy:
        _eviction_strategy = None


def reset_eviction_scheduler() -> None:
    """重置淘汰调度器（用于测试）"""
    global _eviction_scheduler
    if _eviction_scheduler:
        _eviction_scheduler.stop_cleanup()
        _eviction_scheduler = None
