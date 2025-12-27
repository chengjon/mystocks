"""
缓存淘汰系统测试

测试缓存淘汰策略、频率追踪和调度器功能。

Test Coverage:
- AccessFrequencyTracker: 访问频率追踪
- TimeWindowEvictionStrategy: 时间窗口淘汰策略
- EvictionScheduler: 淘汰调度器
"""

import pytest
from unittest.mock import patch
import time

from app.core.cache_eviction import (
    AccessFrequencyTracker,
    TimeWindowEvictionStrategy,
    EvictionScheduler,
    reset_eviction_strategy,
    reset_eviction_scheduler,
)
from app.core.cache_manager import get_cache_manager, reset_cache_manager


@pytest.fixture
def setup_teardown():
    """设置和清理"""
    reset_cache_manager()
    reset_eviction_strategy()
    reset_eviction_scheduler()
    yield
    reset_cache_manager()
    reset_eviction_strategy()
    reset_eviction_scheduler()


class TestAccessFrequencyTracker:
    """测试访问频率追踪器"""

    def test_tracker_initialization(self):
        """测试追踪器初始化"""
        tracker = AccessFrequencyTracker()

        assert tracker.access_counts == {}
        assert tracker.last_access_time == {}
        assert tracker.creation_time == {}

    def test_record_access(self):
        """测试记录访问"""
        tracker = AccessFrequencyTracker()
        cache_key = "000001:fund_flow:1d"

        tracker.record_access(cache_key)

        assert tracker.get_access_frequency(cache_key) == 1
        assert tracker.get_last_access_time(cache_key) is not None
        assert tracker.get_creation_time(cache_key) is not None

    def test_record_multiple_accesses(self):
        """测试记录多次访问"""
        tracker = AccessFrequencyTracker()
        cache_key = "000001:fund_flow:1d"

        for _ in range(5):
            tracker.record_access(cache_key)
            time.sleep(0.01)

        assert tracker.get_access_frequency(cache_key) == 5

    def test_get_hot_data(self):
        """测试获取热点数据"""
        tracker = AccessFrequencyTracker()

        # 模拟不同访问频率
        for i in range(15):
            cache_key = f"symbol{i}:data_type:1d"
            for j in range(i + 1):
                tracker.record_access(cache_key)

        hot_data = tracker.get_hot_data(top_n=5)

        assert len(hot_data) == 5
        # 最热的数据应该是最后一个
        assert hot_data[0][1] == 15

    def test_get_statistics(self):
        """测试获取统计信息"""
        tracker = AccessFrequencyTracker()

        # 添加访问数据
        for i in range(10):
            cache_key = f"symbol{i}:data_type:1d"
            for j in range(i + 1):
                tracker.record_access(cache_key)

        stats = tracker.get_statistics()

        assert stats["total_tracked"] == 10
        assert stats["total_accesses"] == sum(range(1, 11))
        assert stats["average_frequency"] > 0
        assert "timestamp" in stats

    def test_clear_stats(self):
        """测试清除统计数据"""
        tracker = AccessFrequencyTracker()

        # 添加访问数据
        tracker.record_access("000001:fund_flow:1d")
        assert tracker.get_access_frequency("000001:fund_flow:1d") == 1

        # 清除数据
        tracker.clear_stats()

        assert tracker.get_access_frequency("000001:fund_flow:1d") == 0
        assert tracker.get_statistics()["total_tracked"] == 0

    def test_multiple_cache_keys(self):
        """测试多个缓存键的访问追踪"""
        tracker = AccessFrequencyTracker()
        keys = ["key1:data:1d", "key2:data:1d", "key3:data:1d"]

        # 不同的访问频率
        for i, key in enumerate(keys):
            for _ in range(i + 1):
                tracker.record_access(key)

        frequencies = [tracker.get_access_frequency(key) for key in keys]
        assert frequencies == [1, 2, 3]


class TestTimeWindowEvictionStrategy:
    """测试时间窗口淘汰策略"""

    def test_strategy_initialization(self, setup_teardown):
        """测试淘汰策略初始化"""
        strategy = TimeWindowEvictionStrategy(ttl_days=7)

        assert strategy.ttl_days == 7
        assert strategy.frequency_tracker is not None

    def test_record_cache_access(self, setup_teardown):
        """测试记录缓存访问"""
        strategy = TimeWindowEvictionStrategy()
        symbol = "000001"
        data_type = "fund_flow"

        strategy.record_cache_access(symbol, data_type)

        tracker = strategy.frequency_tracker
        frequency = tracker.get_access_frequency(f"{symbol}:{data_type}:1d".lower())
        assert frequency == 1

    def test_evict_expired_cache(self, setup_teardown):
        """测试淘汰过期缓存"""
        cache_mgr = get_cache_manager()
        strategy = TimeWindowEvictionStrategy()

        # 写入缓存
        cache_mgr.write_to_cache(
            symbol="000001",
            data_type="fund_flow",
            timeframe="1d",
            data={"value": 100},
        )

        # 淘汰过期缓存
        deleted_count = strategy.evict_expired_cache(max_age_days=7)

        assert deleted_count >= 0

    def test_get_hot_data(self, setup_teardown):
        """测试获取热点数据"""
        strategy = TimeWindowEvictionStrategy()

        # 记录访问
        for i in range(10):
            strategy.record_cache_access(f"symbol{i}", "fund_flow")

        hot_data = strategy.get_hot_data(top_n=5)

        assert isinstance(hot_data, list)
        # 每个热点数据应该包含cache_key和access_count
        for item in hot_data:
            assert "cache_key" in item
            assert "access_count" in item

    def test_get_eviction_statistics(self, setup_teardown):
        """测试获取淘汰统计"""
        cache_mgr = get_cache_manager()
        strategy = TimeWindowEvictionStrategy()

        # 写入一些缓存数据
        for i in range(3):
            cache_mgr.write_to_cache(
                symbol=f"symbol{i}",
                data_type="fund_flow",
                timeframe="1d",
                data={"value": i},
            )

        stats = strategy.get_eviction_statistics()

        assert "timestamp" in stats
        assert stats["ttl_days"] == 7
        assert "frequency_tracking" in stats
        assert "cache_stats" in stats

    def test_custom_ttl_days(self):
        """测试自定义TTL天数"""
        strategy = TimeWindowEvictionStrategy(ttl_days=3)

        assert strategy.ttl_days == 3


class TestEvictionScheduler:
    """测试淘汰调度器"""

    def test_scheduler_initialization(self):
        """测试调度器初始化"""
        scheduler = EvictionScheduler()

        assert scheduler.eviction_strategy is not None
        assert scheduler.scheduler is not None
        assert scheduler._job_id is None

    def test_start_daily_cleanup(self):
        """测试启动每日清理任务"""
        scheduler = EvictionScheduler()

        scheduler.start_daily_cleanup(hour=2, minute=0)

        assert scheduler.scheduler.running
        assert scheduler._job_id is not None

    def test_stop_cleanup(self):
        """测试停止清理任务"""
        scheduler = EvictionScheduler()

        scheduler.start_daily_cleanup()
        assert scheduler.scheduler.running

        scheduler.stop_cleanup()
        assert not scheduler.scheduler.running

    def test_manual_cleanup_success(self, setup_teardown):
        """测试手动清理成功"""
        cache_mgr = get_cache_manager()
        scheduler = EvictionScheduler()

        # 写入缓存
        cache_mgr.write_to_cache(
            symbol="000001",
            data_type="fund_flow",
            timeframe="1d",
            data={"value": 100},
        )

        result = scheduler.manual_cleanup()

        assert result["success"] is True
        assert "message" in result
        assert "deleted_count" in result
        assert "timestamp" in result

    def test_manual_cleanup_empty_cache(self, setup_teardown):
        """测试在空缓存上手动清理"""
        scheduler = EvictionScheduler()

        result = scheduler.manual_cleanup()

        assert result["success"] is True
        assert result["deleted_count"] == 0

    def test_get_scheduler_status(self):
        """测试获取调度器状态"""
        scheduler = EvictionScheduler()

        scheduler.start_daily_cleanup()
        status = scheduler.get_scheduler_status()

        assert status["running"] is True
        assert "jobs_count" in status
        assert "next_cleanup" in status
        assert "timestamp" in status

    def test_scheduler_status_not_running(self):
        """测试未运行的调度器状态"""
        scheduler = EvictionScheduler()

        status = scheduler.get_scheduler_status()

        assert status["running"] is False

    def test_multiple_start_calls(self):
        """测试多次启动调度器"""
        scheduler = EvictionScheduler()

        scheduler.start_daily_cleanup(hour=2, minute=0)
        first_job_id = scheduler._job_id

        scheduler.start_daily_cleanup(hour=3, minute=0)
        second_job_id = scheduler._job_id

        # 应该替换掉旧任务
        assert scheduler.scheduler.running

    def test_cleanup_task_error_handling(self, setup_teardown):
        """测试清理任务的错误处理"""
        scheduler = EvictionScheduler()

        # 模拟错误
        with patch.object(
            scheduler.eviction_strategy,
            "evict_expired_cache",
            side_effect=Exception("Test error"),
        ):
            # 应该不抛出异常
            scheduler._cleanup_task()


class TestEvictionIntegration:
    """测试淘汰系统集成"""

    def test_cache_access_tracking_integration(self, setup_teardown):
        """测试缓存访问追踪集成"""
        cache_mgr = get_cache_manager()
        strategy = TimeWindowEvictionStrategy()

        # 写入和读取缓存
        cache_mgr.write_to_cache(
            symbol="000001",
            data_type="fund_flow",
            timeframe="1d",
            data={"value": 100},
        )

        # 多次读取
        for _ in range(5):
            cache_mgr.fetch_from_cache(symbol="000001", data_type="fund_flow")
            strategy.record_cache_access("000001", "fund_flow")

        # 验证频率追踪
        frequency = strategy.frequency_tracker.get_access_frequency("000001:fund_flow:1d")
        assert frequency == 5

    def test_hot_data_identification(self, setup_teardown):
        """测试热点数据识别"""
        strategy = TimeWindowEvictionStrategy()

        # 模拟不同访问频率的数据
        for i in range(10):
            for j in range(i + 1):
                strategy.record_cache_access(f"symbol{i}", "fund_flow")

        hot_data = strategy.get_hot_data(top_n=3)

        # 验证热点数据按频率排序
        assert len(hot_data) <= 3
        for i in range(len(hot_data) - 1):
            assert hot_data[i]["access_count"] >= hot_data[i + 1]["access_count"]

    def test_eviction_with_scheduler(self, setup_teardown):
        """测试淘汰调度器集成"""
        cache_mgr = get_cache_manager()
        scheduler = EvictionScheduler()

        # 写入缓存
        for i in range(5):
            cache_mgr.write_to_cache(
                symbol=f"symbol{i}",
                data_type="fund_flow",
                timeframe="1d",
                data={"value": i},
            )

        # 手动触发淘汰
        result = scheduler.manual_cleanup()

        assert result["success"] is True

    def test_frequency_stats_accuracy(self, setup_teardown):
        """测试频率统计的准确性"""
        strategy = TimeWindowEvictionStrategy()

        # 创建固定的访问模式
        test_data = {
            "symbol1": 10,
            "symbol2": 20,
            "symbol3": 5,
        }

        for symbol, count in test_data.items():
            for _ in range(count):
                strategy.record_cache_access(symbol, "fund_flow")

        stats = strategy.frequency_tracker.get_statistics()

        assert stats["total_tracked"] == 3
        assert stats["total_accesses"] == 35
        assert abs(stats["average_frequency"] - 35 / 3) < 0.1

    def test_cache_freshness_with_eviction(self, setup_teardown):
        """测试淘汰与缓存新鲜度的关系"""
        cache_mgr = get_cache_manager()
        strategy = TimeWindowEvictionStrategy()

        # 写入缓存
        write_success = cache_mgr.write_to_cache(
            symbol="000001",
            data_type="fund_flow",
            timeframe="1d",
            data={"value": 100},
            ttl_days=7,
        )

        # 如果写入成功，检查新鲜度
        if write_success:
            is_valid = cache_mgr.is_cache_valid(symbol="000001", data_type="fund_flow", max_age_days=7)
            assert is_valid is True
        else:
            # 如果写入失败（如TDengine不可用），验证is_cache_valid返回False
            is_valid = cache_mgr.is_cache_valid(symbol="000001", data_type="fund_flow", max_age_days=7)
            assert is_valid is False


class TestEvictionErrorHandling:
    """测试淘汰系统的错误处理"""

    def test_scheduler_stop_without_start(self):
        """测试停止未启动的调度器"""
        scheduler = EvictionScheduler()

        # 应该不抛出异常
        scheduler.stop_cleanup()

    def test_eviction_with_invalid_strategy(self):
        """测试无效的淘汰策略"""
        strategy = TimeWindowEvictionStrategy(ttl_days=-1)

        # 应该允许创建，但在使用时可能有问题
        assert strategy.ttl_days == -1

    def test_manual_cleanup_exception_handling(self, setup_teardown):
        """测试手动清理异常处理"""
        scheduler = EvictionScheduler()

        with patch.object(
            scheduler.eviction_strategy,
            "evict_expired_cache",
            side_effect=Exception("Database error"),
        ):
            result = scheduler.manual_cleanup()

            assert result["success"] is False
            assert "error" in result.get("message", "").lower()


class TestEvictionPerformance:
    """测试淘汰系统的性能"""

    def test_tracker_performance_large_dataset(self):
        """测试大数据集的追踪性能"""
        tracker = AccessFrequencyTracker()

        # 记录大量访问
        start_time = time.time()

        for i in range(1000):
            cache_key = f"symbol{i}:fund_flow:1d"
            for _ in range(10):
                tracker.record_access(cache_key)

        elapsed = time.time() - start_time

        # 性能基准：应该在合理时间内完成
        assert elapsed < 5.0

        stats = tracker.get_statistics()
        assert stats["total_tracked"] == 1000

    def test_hot_data_retrieval_performance(self):
        """测试热点数据检索性能"""
        tracker = AccessFrequencyTracker()

        # 创建大量数据
        for i in range(100):
            for j in range(100):
                tracker.record_access(f"symbol{i}:data:1d")

        # 测试热点数据检索
        start_time = time.time()
        hot_data = tracker.get_hot_data(top_n=10)
        elapsed = time.time() - start_time

        assert elapsed < 0.1
        assert len(hot_data) == 10

    def test_eviction_statistics_performance(self, setup_teardown):
        """测试淘汰统计性能"""
        cache_mgr = get_cache_manager()
        strategy = TimeWindowEvictionStrategy()

        # 写入大量缓存
        for i in range(100):
            cache_mgr.write_to_cache(
                symbol=f"symbol{i}",
                data_type="fund_flow",
                timeframe="1d",
                data={"value": i},
            )

        # 测试统计检索
        start_time = time.time()
        stats = strategy.get_eviction_statistics()
        elapsed = time.time() - start_time

        assert elapsed < 1.0
        assert "frequency_tracking" in stats


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
