"""
缓存预热系统测试

测试缓存预热策略、监控和API功能。

Test Coverage:
- CacheMonitor: 缓存监控
- CachePrewarmingStrategy: 预热策略
- API endpoints: 预热和监控端点
"""

import pytest
import time

from app.core.cache_prewarming import (
    CacheMonitor,
    CachePrewarmingStrategy,
    get_cache_monitor,
    get_prewarming_strategy,
    reset_cache_monitor,
    reset_prewarming_strategy,
)
from app.core.cache_manager import get_cache_manager, reset_cache_manager
from app.core.cache_eviction import reset_eviction_strategy


@pytest.fixture
def setup_teardown():
    """设置和清理"""
    reset_cache_manager()
    reset_eviction_strategy()
    reset_cache_monitor()
    reset_prewarming_strategy()
    yield
    reset_cache_manager()
    reset_eviction_strategy()
    reset_cache_monitor()
    reset_prewarming_strategy()


class TestCacheMonitor:
    """测试缓存监控器"""

    def test_monitor_initialization(self):
        """测试监控器初始化"""
        monitor = CacheMonitor()

        assert monitor.hit_count == 0
        assert monitor.miss_count == 0
        assert monitor.read_operations == 0

    def test_record_hit(self):
        """测试记录缓存命中"""
        monitor = CacheMonitor()

        monitor.record_hit(latency_ms=5.0)

        assert monitor.hit_count == 1
        assert monitor.read_operations == 1

    def test_record_miss(self):
        """测试记录缓存未命中"""
        monitor = CacheMonitor()

        monitor.record_miss(latency_ms=10.0)

        assert monitor.miss_count == 1
        assert monitor.read_operations == 1

    def test_get_hit_rate(self):
        """测试获取命中率"""
        monitor = CacheMonitor()

        # 模拟命中和未命中
        for _ in range(8):
            monitor.record_hit()
        for _ in range(2):
            monitor.record_miss()

        hit_rate = monitor.get_hit_rate()
        assert hit_rate == 80.0

    def test_get_hit_rate_empty(self):
        """测试空的命中率"""
        monitor = CacheMonitor()

        hit_rate = monitor.get_hit_rate()
        assert hit_rate == 0.0

    def test_get_average_latency(self):
        """测试获取平均延迟"""
        monitor = CacheMonitor()

        monitor.record_hit(latency_ms=5.0)
        monitor.record_hit(latency_ms=10.0)
        monitor.record_miss(latency_ms=15.0)

        avg_latency = monitor.get_average_latency()
        assert abs(avg_latency - 10.0) < 0.1

    def test_get_metrics(self):
        """测试获取监控指标"""
        monitor = CacheMonitor()

        for _ in range(85):
            monitor.record_hit()
        for _ in range(15):
            monitor.record_miss()

        metrics = monitor.get_metrics()

        assert metrics["hit_count"] == 85
        assert metrics["miss_count"] == 15
        assert metrics["hit_rate"] == 85.0
        assert metrics["total_reads"] == 100
        assert "timestamp" in metrics
        assert metrics["health_status"] == "healthy"

    def test_get_metrics_warning_status(self):
        """测试警告状态的指标"""
        monitor = CacheMonitor()

        for _ in range(70):
            monitor.record_hit()
        for _ in range(30):
            monitor.record_miss()

        metrics = monitor.get_metrics()

        assert metrics["hit_rate"] == 70.0
        assert metrics["health_status"] == "warning"

    def test_reset(self):
        """测试重置监控数据"""
        monitor = CacheMonitor()

        monitor.record_hit()
        monitor.record_miss()
        assert monitor.hit_count == 1

        monitor.reset()

        assert monitor.hit_count == 0
        assert monitor.miss_count == 0
        assert monitor.read_operations == 0


class TestCachePrewarmingStrategy:
    """测试缓存预热策略"""

    def test_strategy_initialization(self, setup_teardown):
        """测试预热策略初始化"""
        strategy = CachePrewarmingStrategy()

        assert strategy.cache_manager is not None
        assert strategy.eviction_strategy is not None
        assert strategy.monitor is not None

    def test_get_hot_data_list(self, setup_teardown):
        """测试获取热点数据列表"""
        strategy = CachePrewarmingStrategy()

        hot_data = strategy.get_hot_data_list(top_n=10)

        assert isinstance(hot_data, list)

    def test_prewarm_cache_empty(self, setup_teardown):
        """测试空缓存预热"""
        strategy = CachePrewarmingStrategy()

        result = strategy.prewarm_cache()

        assert result["success"] is True
        assert "prewarmed_count" in result
        assert "failed_count" in result
        assert "elapsed_seconds" in result

    def test_prewarm_cache_with_data_sources(self, setup_teardown):
        """测试带数据源的缓存预热"""
        strategy = CachePrewarmingStrategy()

        # 模拟数据源
        data_sources = {
            "000001:fund_flow:1d": lambda: {"value": 100},
            "000002:etf:1d": lambda: {"value": 200},
        }

        result = strategy.prewarm_cache(data_sources=data_sources)

        assert result["success"] is True

    def test_prewarm_cache_with_exception(self, setup_teardown):
        """测试带异常的缓存预热"""
        strategy = CachePrewarmingStrategy()

        # 模拟抛出异常的数据源
        def raise_error():
            raise Exception("Data source error")

        data_sources = {
            "000001:fund_flow:1d": raise_error,
        }

        result = strategy.prewarm_cache(data_sources=data_sources)

        # 应该返回失败但不抛出异常
        assert result["success"] is True

    def test_get_prewarming_status(self, setup_teardown):
        """测试获取预热状态"""
        strategy = CachePrewarmingStrategy()

        status = strategy.get_prewarming_status()

        assert "last_prewarming" in status
        assert "prewarmed_keys_count" in status
        assert "timestamp" in status

    def test_get_health_status(self, setup_teardown):
        """测试获取健康状态"""
        strategy = CachePrewarmingStrategy()

        # 模拟一些命中
        for _ in range(8):
            strategy.monitor.record_hit()
        for _ in range(2):
            strategy.monitor.record_miss()

        health = strategy.get_health_status()

        assert health["status"] == "healthy"
        assert health["hit_rate"] == 80.0
        assert "timestamp" in health

    def test_get_health_status_warning(self, setup_teardown):
        """测试警告状态的健康检查"""
        strategy = CachePrewarmingStrategy()

        # 模拟低命中率
        for _ in range(5):
            strategy.monitor.record_hit()
        for _ in range(95):
            strategy.monitor.record_miss()

        health = strategy.get_health_status()

        assert health["status"] == "warning"
        assert health["hit_rate"] == 5.0


class TestCachePrewarmingSingleton:
    """测试单例模式"""

    def test_get_cache_monitor_singleton(self, setup_teardown):
        """测试缓存监控器单例"""
        monitor1 = get_cache_monitor()
        monitor2 = get_cache_monitor()

        assert monitor1 is monitor2

    def test_get_prewarming_strategy_singleton(self, setup_teardown):
        """测试预热策略单例"""
        strategy1 = get_prewarming_strategy()
        strategy2 = get_prewarming_strategy()

        assert strategy1 is strategy2

    def test_reset_monitor(self, setup_teardown):
        """测试重置监控器"""
        monitor1 = get_cache_monitor()
        reset_cache_monitor()
        monitor2 = get_cache_monitor()

        assert monitor1 is not monitor2


class TestCachePrewarmingPerformance:
    """测试预热性能"""

    def test_prewarm_performance(self, setup_teardown):
        """测试预热性能"""
        strategy = CachePrewarmingStrategy()

        start_time = time.time()
        result = strategy.prewarm_cache()
        elapsed = time.time() - start_time

        # 预热应该在合理时间内完成
        assert elapsed < 5.0

    def test_monitor_performance_many_operations(self):
        """测试大量操作的监控性能"""
        monitor = CacheMonitor()

        start_time = time.time()

        for i in range(10000):
            if i % 10 < 8:
                monitor.record_hit(latency_ms=2.0)
            else:
                monitor.record_miss(latency_ms=5.0)

        elapsed = time.time() - start_time

        # 10000个操作应该在1秒内完成
        assert elapsed < 1.0

        metrics = monitor.get_metrics()
        assert metrics["total_reads"] == 10000


class TestCachePrewarmingIntegration:
    """测试预热集成"""

    def test_prewarming_with_eviction(self, setup_teardown):
        """测试预热与淘汰的集成"""
        cache_mgr = get_cache_manager()
        strategy = CachePrewarmingStrategy()

        # 写入缓存
        for i in range(5):
            cache_mgr.write_to_cache(
                symbol=f"symbol{i}",
                data_type="fund_flow",
                timeframe="1d",
                data={"value": i},
            )

        # 执行预热
        result = strategy.prewarm_cache()

        # 验证预热成功
        assert result["success"] is True

    def test_full_workflow(self, setup_teardown):
        """测试完整工作流"""
        cache_mgr = get_cache_manager()
        strategy = CachePrewarmingStrategy()

        # 1. 写入缓存
        cache_mgr.write_to_cache(
            symbol="000001",
            data_type="fund_flow",
            timeframe="1d",
            data={"value": 100},
        )

        # 2. 预热缓存
        result = strategy.prewarm_cache()
        assert result["success"] is True

        # 3. 模拟读取和监控
        cached = cache_mgr.fetch_from_cache(symbol="000001", data_type="fund_flow")
        if cached:
            strategy.monitor.record_hit(latency_ms=2.0)
        else:
            strategy.monitor.record_miss(latency_ms=5.0)

        # 4. 检查健康状态
        health = strategy.get_health_status()
        assert "status" in health


class TestCachePrewarmingEdgeCases:
    """测试边界情况"""

    def test_prewarm_with_none_data_sources(self, setup_teardown):
        """测试None数据源预热"""
        strategy = CachePrewarmingStrategy()

        result = strategy.prewarm_cache(data_sources=None)

        assert result["success"] is True

    def test_monitor_with_zero_operations(self):
        """测试零操作的监控"""
        monitor = CacheMonitor()

        metrics = monitor.get_metrics()

        assert metrics["hit_count"] == 0
        assert metrics["hit_rate"] == 0.0

    def test_prewarming_very_large_cache_key(self, setup_teardown):
        """测试非常大的缓存键"""
        strategy = CachePrewarmingStrategy()

        large_key = "a" * 1000 + ":data_type:1d"
        data_sources = {large_key: lambda: {"value": 1}}

        result = strategy.prewarm_cache(data_sources=data_sources)

        # 应该能够处理大键
        assert "success" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
