"""Cache Manager Tests - 缓存管理器集成测试
Task 2.2: 实现缓存读写逻辑

测试覆盖:
- 单条数据读写
- 批量读写操作
- 缓存失效机制
- Cache-Aside 模式
- 缓存统计与监控
- 错误处理
- 性能验证
"""

import os
import sys
import time
from datetime import datetime, timedelta, timezone

import pytest


# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.core.cache_manager import (
    CacheManager,
    get_cache_manager,
    reset_cache_manager,
)
from app.core.tdengine_manager import reset_tdengine_manager


class TestCacheManagerBasics:
    """基本功能测试"""

    def setup_method(self):
        """测试前设置"""
        reset_cache_manager()
        reset_tdengine_manager()
        self.manager = get_cache_manager()

    def teardown_method(self):
        """测试后清理"""
        if self.manager:
            self.manager.close()

    def test_initialization(self):
        """测试初始化"""
        assert self.manager is not None
        assert self.manager.tdengine is not None

    def test_singleton_pattern(self):
        """测试单例模式"""
        manager1 = get_cache_manager()
        manager2 = get_cache_manager()
        assert manager1 is manager2

    def test_health_check(self):
        """测试健康检查"""
        result = self.manager.health_check()
        assert isinstance(result, bool)


class TestSingleCacheOperations:
    """单条数据读写操作测试"""

    def setup_method(self):
        """测试前设置"""
        reset_cache_manager()
        reset_tdengine_manager()
        self.manager = get_cache_manager()
        try:
            self.manager.tdengine.initialize()
            # Clear cache data to ensure clean state for each test
            self.manager.invalidate_cache()
        except Exception as e:
            pytest.skip(f"TDengine may not be running: {e!s}")

    def teardown_method(self):
        """测试后清理"""
        if self.manager:
            self.manager.close()

    def test_write_cache_success(self):
        """测试缓存写入成功"""
        data = {"main_inflow": 1000000, "retail_inflow": 500000}

        result = self.manager.write_to_cache(symbol="000001", data_type="fund_flow", timeframe="1d", data=data)

        assert result is True

    def test_fetch_cache_after_write(self):
        """测试写入后读取缓存"""
        write_data = {
            "main_inflow": 1000000,
            "retail_inflow": 500000,
        }

        # 写入数据
        self.manager.write_to_cache(symbol="000001", data_type="fund_flow", timeframe="1d", data=write_data)

        # 读取数据
        result = self.manager.fetch_from_cache(symbol="000001", data_type="fund_flow")

        assert result is not None
        assert "data" in result
        assert result["source"] == "cache"
        assert result["data"]["main_inflow"] == 1000000

    def test_fetch_nonexistent_cache(self):
        """测试读取不存在的缓存"""
        result = self.manager.fetch_from_cache(symbol="999999", data_type="nonexistent")

        assert result is None

    def test_cache_with_metadata(self):
        """测试缓存包含元数据"""
        data = {"value": 100}

        self.manager.write_to_cache(
            symbol="000001",
            data_type="test",
            timeframe="1d",
            data=data,
            ttl_days=7,
        )

        result = self.manager.fetch_from_cache(symbol="000001", data_type="test")

        assert result is not None
        assert "_cached_at" in result["data"]
        assert "_ttl_days" in result["data"]
        assert result["data"]["_ttl_days"] == 7

    def test_cache_with_custom_timestamp(self):
        """测试自定义时间戳的缓存"""
        custom_time = datetime.now(timezone.utc) - timedelta(days=1)
        data = {"value": 100}

        result = self.manager.write_to_cache(
            symbol="000001",
            data_type="test",
            timeframe="1d",
            data=data,
            timestamp=custom_time,
        )

        assert result is True

    def test_write_invalid_data(self):
        """测试写入无效数据"""
        result = self.manager.write_to_cache(symbol="000001", data_type="test", timeframe="1d", data=None)

        assert result is False

    def test_write_empty_dict(self):
        """测试写入空字典"""
        result = self.manager.write_to_cache(symbol="000001", data_type="test", timeframe="1d", data={})

        # 空字典仍然是有效的字典
        assert result is True


class TestBatchOperations:
    """批量操作测试"""

    def setup_method(self):
        """测试前设置"""
        reset_cache_manager()
        reset_tdengine_manager()
        self.manager = get_cache_manager()
        try:
            self.manager.tdengine.initialize()
            # Clear cache data to ensure clean state for each test
            self.manager.invalidate_cache()
        except Exception as e:
            pytest.skip(f"TDengine may not be running: {e!s}")

    def teardown_method(self):
        """测试后清理"""
        if self.manager:
            self.manager.close()

    def test_batch_write_success(self):
        """测试批量写入成功"""
        records = [
            {
                "symbol": "000001",
                "data_type": "fund_flow",
                "timeframe": "1d",
                "data": {"value": 100},
            },
            {
                "symbol": "000858",
                "data_type": "etf",
                "timeframe": "1d",
                "data": {"value": 200},
            },
            {
                "symbol": "000002",
                "data_type": "fund_flow",
                "timeframe": "1d",
                "data": {"value": 300},
            },
        ]

        count = self.manager.batch_write(records)
        assert count == 3

    def test_batch_read_success(self):
        """测试批量读取成功"""
        # 先写入数据
        write_records = [
            {
                "symbol": "000001",
                "data_type": "fund_flow",
                "timeframe": "1d",
                "data": {"value": 100},
            },
            {
                "symbol": "000858",
                "data_type": "etf",
                "timeframe": "1d",
                "data": {"value": 200},
            },
        ]
        self.manager.batch_write(write_records)

        # 批量读取
        read_queries = [
            {"symbol": "000001", "data_type": "fund_flow"},
            {"symbol": "000858", "data_type": "etf"},
        ]

        results = self.manager.batch_read(read_queries)

        assert "000001:fund_flow" in results
        assert "000858:etf" in results
        assert results["000001:fund_flow"] is not None
        assert results["000858:etf"] is not None

    def test_batch_write_with_invalid_records(self):
        """测试批量写入包含无效记录"""
        records = [
            {
                "symbol": "000001",
                "data_type": "fund_flow",
                "timeframe": "1d",
                "data": {"value": 100},
            },
            {
                "symbol": "000858",
                # 缺少 data_type
                "timeframe": "1d",
                "data": {"value": 200},
            },
            {
                "symbol": "000002",
                "data_type": "fund_flow",
                "timeframe": "1d",
                "data": {"value": 300},
            },
        ]

        count = self.manager.batch_write(records)
        # 应该只成功写入 2 条
        assert count == 2

    def test_batch_read_with_mixed_results(self):
        """测试批量读取返回部分命中"""
        # 只写入第一条记录
        self.manager.write_to_cache(
            symbol="000001",
            data_type="fund_flow",
            timeframe="1d",
            data={"value": 100},
        )

        # 尝试读取两条（只有第一条存在）
        queries = [
            {"symbol": "000001", "data_type": "fund_flow"},
            {"symbol": "000858", "data_type": "etf"},
        ]

        results = self.manager.batch_read(queries)

        assert results["000001:fund_flow"] is not None
        assert results["000858:etf"] is None


class TestCacheInvalidation:
    """缓存失效机制测试"""

    def setup_method(self):
        """测试前设置"""
        reset_cache_manager()
        reset_tdengine_manager()
        self.manager = get_cache_manager()
        try:
            self.manager.tdengine.initialize()
            # Clear cache data to ensure clean state for each test
            self.manager.invalidate_cache()
        except Exception as e:
            pytest.skip(f"TDengine may not be running: {e!s}")

    def teardown_method(self):
        """测试后清理"""
        if self.manager:
            self.manager.close()

    def test_invalidate_cache_basic(self):
        """测试基本的缓存失效"""
        # 写入数据
        self.manager.write_to_cache(
            symbol="000001",
            data_type="fund_flow",
            timeframe="1d",
            data={"value": 100},
        )

        # 清除缓存
        result = self.manager.invalidate_cache()
        assert result >= 0

    def test_invalidate_specific_symbol(self):
        """测试清除特定符号的缓存"""
        # 写入多个符号的数据
        self.manager.write_to_cache(
            symbol="000001",
            data_type="fund_flow",
            timeframe="1d",
            data={"value": 100},
        )
        self.manager.write_to_cache(
            symbol="000858",
            data_type="fund_flow",
            timeframe="1d",
            data={"value": 200},
        )

        # 清除特定符号
        result = self.manager.invalidate_cache(symbol="000001")
        assert result >= 0


class TestCacheValidation:
    """缓存有效性检查测试"""

    def setup_method(self):
        """测试前设置"""
        reset_cache_manager()
        reset_tdengine_manager()
        self.manager = get_cache_manager()
        try:
            self.manager.tdengine.initialize()
            # Clear cache data to ensure clean state for each test
            self.manager.invalidate_cache()
        except Exception as e:
            pytest.skip(f"TDengine may not be running: {e!s}")

    def teardown_method(self):
        """测试后清理"""
        if self.manager:
            self.manager.close()

    def test_is_cache_valid_after_write(self):
        """测试写入后的缓存有效性"""
        self.manager.write_to_cache(
            symbol="000001",
            data_type="fund_flow",
            timeframe="1d",
            data={"value": 100},
        )

        is_valid = self.manager.is_cache_valid(symbol="000001", data_type="fund_flow")

        assert is_valid is True

    def test_is_cache_valid_nonexistent(self):
        """测试不存在的缓存有效性"""
        is_valid = self.manager.is_cache_valid(symbol="999999", data_type="nonexistent")

        assert is_valid is False

    def test_get_cache_key(self):
        """测试缓存键生成"""
        key = self.manager.get_cache_key(symbol="000001", data_type="fund_flow", timeframe="1d")

        assert key == "fund_flow:000001:1d"

    def test_cache_key_normalization(self):
        """测试缓存键的大小写规范化"""
        key1 = self.manager.get_cache_key(symbol="000001", data_type="FUND_FLOW", timeframe="1D")
        key2 = self.manager.get_cache_key(symbol="000001", data_type="fund_flow", timeframe="1d")

        assert key1 == key2


class TestCacheStatistics:
    """缓存统计测试"""

    def setup_method(self):
        """测试前设置"""
        reset_cache_manager()
        reset_tdengine_manager()
        self.manager = get_cache_manager()
        try:
            self.manager.tdengine.initialize()
            # Clear cache data to ensure clean state for each test
            self.manager.invalidate_cache()
        except Exception as e:
            pytest.skip(f"TDengine may not be running: {e!s}")

    def teardown_method(self):
        """测试后清理"""
        if self.manager:
            self.manager.close()

    def test_cache_stats_initial(self):
        """测试初始统计状态"""
        stats = self.manager.get_cache_stats()

        assert stats is not None
        assert "total_reads" in stats
        assert "total_writes" in stats
        assert "cache_hits" in stats
        assert "cache_misses" in stats
        assert "hit_rate" in stats

    def test_cache_stats_after_operations(self):
        """测试操作后的统计"""
        # 写入
        self.manager.write_to_cache(
            symbol="000001",
            data_type="fund_flow",
            timeframe="1d",
            data={"value": 100},
        )

        # 读取命中
        self.manager.fetch_from_cache(symbol="000001", data_type="fund_flow")

        # 读取未命中
        self.manager.fetch_from_cache(symbol="999999", data_type="nonexistent")

        stats = self.manager.get_cache_stats()

        assert stats["total_writes"] >= 1
        assert stats["total_reads"] >= 2
        assert stats["cache_hits"] >= 1
        assert stats["cache_misses"] >= 1

    def test_cache_hit_rate_calculation(self):
        """测试缓存命中率计算"""
        # 写入 10 条
        for i in range(10):
            self.manager.write_to_cache(
                symbol=f"00000{i}",
                data_type="test",
                timeframe="1d",
                data={"index": i},
            )

        # 命中 5 次
        for i in range(5):
            self.manager.fetch_from_cache(symbol=f"00000{i}", data_type="test")

        # 未命中 5 次
        for i in range(100, 105):
            self.manager.fetch_from_cache(symbol=f"0000{i}", data_type="test")

        stats = self.manager.get_cache_stats()

        assert stats["total_reads"] == 10
        assert stats["cache_hits"] == 5
        assert stats["cache_misses"] == 5
        assert stats["hit_rate"] == 0.5

    def test_reset_stats(self):
        """测试统计重置"""
        # 进行一些操作
        self.manager.write_to_cache(
            symbol="000001",
            data_type="fund_flow",
            timeframe="1d",
            data={"value": 100},
        )
        self.manager.fetch_from_cache(symbol="000001", data_type="fund_flow")

        # 重置
        self.manager.reset_stats()

        # 检查统计
        stats = self.manager.get_cache_stats()
        assert stats["total_reads"] == 0
        assert stats["total_writes"] == 0
        assert stats["cache_hits"] == 0


class TestCacheAsidesPattern:
    """Cache-Aside 模式测试"""

    def setup_method(self):
        """测试前设置"""
        reset_cache_manager()
        reset_tdengine_manager()
        self.manager = get_cache_manager()
        try:
            self.manager.tdengine.initialize()
            # Clear cache data to ensure clean state
            self.manager.invalidate_cache()
        except Exception as e:
            pytest.skip(f"TDengine may not be running: {e!s}")

    def teardown_method(self):
        """测试后清理"""
        if self.manager:
            self.manager.close()

    def test_cache_aside_flow(self):
        """测试 Cache-Aside 的完整流程"""
        symbol = "000001"
        data_type = "fund_flow"

        # 1. 首次读取（未命中）
        result1 = self.manager.fetch_from_cache(symbol=symbol, data_type=data_type)
        assert result1 is None

        # 2. 从源读取并写入缓存（模拟）
        source_data = {"main_inflow": 1000000}
        self.manager.write_to_cache(symbol=symbol, data_type=data_type, timeframe="1d", data=source_data)

        # 3. 第二次读取（命中）
        result2 = self.manager.fetch_from_cache(symbol=symbol, data_type=data_type)
        assert result2 is not None
        assert result2["source"] == "cache"
        assert result2["data"]["main_inflow"] == 1000000


class TestErrorHandling:
    """错误处理测试"""

    def setup_method(self):
        """测试前设置"""
        reset_cache_manager()
        reset_tdengine_manager()
        self.manager = get_cache_manager()
        try:
            self.manager.tdengine.initialize()
            # Clear cache data to ensure clean state for each test
            self.manager.invalidate_cache()
        except Exception as e:
            pytest.skip(f"TDengine may not be running: {e!s}")

    def teardown_method(self):
        """测试后清理"""
        if self.manager:
            self.manager.close()

    def test_write_with_special_characters(self):
        """测试写入包含特殊字符的数据"""
        data = {
            "name": "测试数据 中文",
            "desc": "Special: !@#$%^&*()",
            "emoji": "🚀📈💰",
        }

        result = self.manager.write_to_cache(symbol="000001", data_type="test", timeframe="1d", data=data)

        assert result is True

    def test_write_with_large_data(self):
        """测试写入大数据"""
        large_data = {f"key_{i}": f"value_{i}" * 100 for i in range(50)}

        result = self.manager.write_to_cache(symbol="000001", data_type="large", timeframe="1d", data=large_data)

        assert isinstance(result, bool)


class TestPerformance:
    """性能测试"""

    def setup_method(self):
        """测试前设置"""
        reset_cache_manager()
        reset_tdengine_manager()
        self.manager = get_cache_manager()
        try:
            self.manager.tdengine.initialize()
            # Clear cache data to ensure clean state for each test
            self.manager.invalidate_cache()
        except Exception as e:
            pytest.skip(f"TDengine may not be running: {e!s}")

    def teardown_method(self):
        """测试后清理"""
        if self.manager:
            self.manager.close()

    def test_write_performance(self):
        """测试写入性能"""
        num_records = 50
        start_time = time.time()

        for i in range(num_records):
            self.manager.write_to_cache(
                symbol=f"00000{i % 10}",
                data_type="test",
                timeframe="1d",
                data={"value": i},
            )

        elapsed_time = time.time() - start_time
        ops_per_sec = num_records / elapsed_time

        print(f"\n写入性能: {ops_per_sec:.0f} ops/sec")
        assert ops_per_sec > 10, "写入性能低于预期"

    def test_read_performance(self):
        """测试读取性能"""
        # 先写入数据
        for i in range(20):
            self.manager.write_to_cache(
                symbol=f"00000{i % 5}",
                data_type="test",
                timeframe="1d",
                data={"value": i},
            )

        # 测试读取性能
        num_reads = 50
        start_time = time.time()

        for i in range(num_reads):
            self.manager.fetch_from_cache(symbol=f"00000{i % 5}", data_type="test")

        elapsed_time = time.time() - start_time
        ops_per_sec = num_reads / elapsed_time

        print(f"\n读取性能: {ops_per_sec:.0f} ops/sec")
        assert ops_per_sec > 20, "读取性能低于预期"


# Pytest fixtures
@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """设置测试环境"""
    # 检查 TDengine 是否可用
    temp_manager = CacheManager()
    if not temp_manager.health_check():
        pytest.skip(
            "TDengine service is not running. Start with: docker-compose -f docker-compose.tdengine.yml up -d",
        )
    temp_manager.close()


if __name__ == "__main__":
    # 运行测试: pytest web/backend/tests/test_cache_manager.py -v
    pytest.main([__file__, "-v", "--tb=short"])
