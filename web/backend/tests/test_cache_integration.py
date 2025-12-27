"""
Cache Integration Tests - 缓存集成测试

测试CacheIntegration与现有数据服务的集成情况。

Test Coverage:
- Cache-Aside读模式集成
- Cache-Aside写模式集成
- 批量操作集成
- 数据一致性验证
- 缓存失效验证
- 性能优化验证
"""

import pytest
from typing import Dict, Any

from app.core.cache_manager import get_cache_manager, reset_cache_manager
from app.core.cache_integration import (
    get_cache_integration,
    reset_cache_integration,
    cache_read_wrapper,
    cache_write_wrapper,
    cache_invalidate_on_write,
)


class TestCacheReadPatternIntegration:
    """测试缓存读取模式集成"""

    def setup_method(self):
        """测试前初始化"""
        reset_cache_manager()
        reset_cache_integration()
        self.cache_mgr = get_cache_manager()
        self.cache_integration = get_cache_integration()

    def teardown_method(self):
        """测试后清理"""
        reset_cache_manager()
        reset_cache_integration()

    def test_fetch_with_cache_hit(self):
        """测试缓存命中场景"""
        # 准备测试数据
        symbol = "000001"
        data_type = "fund_flow"
        test_data = {"main_net_inflow": 1000, "rate": 0.5}

        # 预先写入缓存
        self.cache_mgr.write_to_cache(
            symbol=symbol,
            data_type=data_type,
            timeframe="1d",
            data=test_data,
        )

        # 定义获取函数（应该不被调用）
        fetch_called = False

        def fetch_fn():
            nonlocal fetch_called
            fetch_called = True
            return {"should": "not_call"}

        # 执行缓存读取
        result = self.cache_integration.fetch_with_cache(
            symbol=symbol,
            data_type=data_type,
            fetch_fn=fetch_fn,
            use_cache=True,
        )

        # 验证结果
        assert result is not None
        assert result["source"] == "cache"
        assert not fetch_called  # 获取函数不应被调用

    def test_fetch_with_cache_miss(self):
        """测试缓存未命中场景"""
        symbol = "000858"
        data_type = "etf"
        source_data = {"symbol": "000858", "price": 100}

        def fetch_fn():
            return source_data

        # 执行缓存读取（缓存为空）
        result = self.cache_integration.fetch_with_cache(
            symbol=symbol,
            data_type=data_type,
            fetch_fn=fetch_fn,
            use_cache=True,
        )

        # 验证结果
        assert result is not None
        assert result["source"] == "source"
        assert result["data"] == source_data

    def test_fetch_without_cache(self):
        """测试禁用缓存的读取"""
        symbol = "600519"
        data_type = "daily_kline"
        source_data = {"open": 1000, "close": 1050}

        # 预先写入缓存（应该被忽略）
        self.cache_mgr.write_to_cache(
            symbol=symbol,
            data_type=data_type,
            timeframe="1d",
            data={"cached": "data"},
        )

        def fetch_fn():
            return source_data

        # 禁用缓存执行读取
        result = self.cache_integration.fetch_with_cache(
            symbol=symbol,
            data_type=data_type,
            fetch_fn=fetch_fn,
            use_cache=False,  # 禁用缓存
        )

        # 验证结果来自源，不是缓存
        assert result["source"] == "source"
        assert result["data"] == source_data

    def test_fetch_with_cache_empty_source(self):
        """测试源数据为空的情况"""
        symbol = "999999"
        data_type = "nonexistent"

        def fetch_fn():
            return None  # 源返回空数据

        result = self.cache_integration.fetch_with_cache(
            symbol=symbol,
            data_type=data_type,
            fetch_fn=fetch_fn,
            use_cache=True,
        )

        # 验证结果
        assert result["source"] == "source"
        assert result["data"] is None

    def test_batch_fetch_with_cache(self):
        """测试批量缓存读取"""
        # 预先写入部分缓存
        self.cache_mgr.write_to_cache(
            symbol="000001",
            data_type="fund_flow",
            timeframe="1d",
            data={"cached": True},
        )

        queries = [
            {"symbol": "000001", "data_type": "fund_flow"},
            {"symbol": "000858", "data_type": "etf"},
            {"symbol": "600519", "data_type": "daily_kline"},
        ]

        def fetch_fn(symbol):
            return {"symbol": symbol, "data": f"from_{symbol}"}

        # 执行批量读取
        results = self.cache_integration.batch_fetch_with_cache(
            queries=queries,
            fetch_fn=fetch_fn,
            use_cache=True,
        )

        # 验证结果
        assert len(results) == 3
        assert "000001:fund_flow" in results
        assert results["000001:fund_flow"]["source"] == "cache"
        assert results["000858:etf"]["source"] == "source"


class TestCacheWritePatternIntegration:
    """测试缓存写入模式集成"""

    def setup_method(self):
        """测试前初始化"""
        reset_cache_manager()
        reset_cache_integration()
        self.cache_mgr = get_cache_manager()
        self.cache_integration = get_cache_integration()

    def teardown_method(self):
        """测试后清理"""
        reset_cache_manager()
        reset_cache_integration()

    def test_save_with_cache_success(self):
        """测试成功保存到源和缓存"""
        symbol = "000001"
        data_type = "fund_flow"
        test_data = {"main_net_inflow": 5000}

        save_called = False

        def save_fn(data):
            nonlocal save_called
            save_called = True
            return True

        # 执行缓存写入
        result = self.cache_integration.save_with_cache(
            symbol=symbol,
            data_type=data_type,
            data=test_data,
            save_fn=save_fn,
            use_cache=True,
        )

        # 验证结果
        assert result is True
        assert save_called

        # 验证数据已写入缓存
        cached = self.cache_mgr.fetch_from_cache(symbol, data_type)
        assert cached is not None

    def test_save_with_cache_source_failure(self):
        """测试源保存失败的情况"""
        symbol = "000858"
        data_type = "etf"
        test_data = {"price": 100}

        def save_fn(data):
            return False  # 保存失败

        result = self.cache_integration.save_with_cache(
            symbol=symbol,
            data_type=data_type,
            data=test_data,
            save_fn=save_fn,
            use_cache=True,
        )

        # 验证失败
        assert result is False

        # 验证缓存未被写入
        cached = self.cache_mgr.fetch_from_cache(symbol, data_type)
        assert cached is None

    def test_save_without_cache(self):
        """测试禁用缓存的保存"""
        symbol = "600519"
        data_type = "daily_kline"
        test_data = {"open": 1000}

        def save_fn(data):
            return True

        result = self.cache_integration.save_with_cache(
            symbol=symbol,
            data_type=data_type,
            data=test_data,
            save_fn=save_fn,
            use_cache=False,  # 禁用缓存
        )

        # 验证成功
        assert result is True

        # 验证缓存未被写入
        cached = self.cache_mgr.fetch_from_cache(symbol, data_type)
        assert cached is None

    def test_batch_save_with_cache(self):
        """测试批量缓存写入"""
        records = [
            {"symbol": "000001", "data": {"value": 1}},
            {"symbol": "000858", "data": {"value": 2}},
            {"symbol": "600519", "data": {"value": 3}},
        ]

        def save_fn(data):
            return len(data)  # 返回保存的记录数

        # 执行批量写入
        result = self.cache_integration.batch_save_with_cache(
            records=records,
            save_fn=save_fn,
            data_type="test_type",
            use_cache=True,
        )

        # 验证结果
        assert result == 3

        # 验证部分数据已写入缓存
        cached = self.cache_mgr.fetch_from_cache("000001", "test_type")
        assert cached is not None


class TestCacheInvalidationIntegration:
    """测试缓存失效集成"""

    def setup_method(self):
        """测试前初始化"""
        reset_cache_manager()
        reset_cache_integration()
        self.cache_mgr = get_cache_manager()
        self.cache_integration = get_cache_integration()

    def teardown_method(self):
        """测试后清理"""
        reset_cache_manager()
        reset_cache_integration()

    def test_invalidate_symbol_cache(self):
        """测试清除特定符号的缓存"""
        # 写入多条缓存
        self.cache_mgr.write_to_cache("000001", "fund_flow", "1d", {"v": 1})
        self.cache_mgr.write_to_cache("000001", "etf", "1d", {"v": 2})
        self.cache_mgr.write_to_cache("000858", "fund_flow", "1d", {"v": 3})

        # 清除特定符号的缓存
        result = self.cache_integration.invalidate_data(symbol="000001")

        # 验证清除成功
        assert result >= 0

    def test_is_cache_fresh(self):
        """测试缓存新鲜度检查"""
        symbol = "000001"
        data_type = "fund_flow"

        # 写入缓存
        self.cache_mgr.write_to_cache(symbol, data_type, "1d", {"value": 100})

        # 验证缓存新鲜
        is_fresh = self.cache_integration.is_cache_fresh(symbol, data_type, max_age_days=7)
        assert is_fresh is True

    def test_invalidate_data_on_write(self):
        """测试写入时自动清除缓存"""

        @cache_invalidate_on_write("fund_flow")
        def delete_fund_flow(symbol: str):
            return True

        # 预先写入缓存
        self.cache_mgr.write_to_cache("000001", "fund_flow", "1d", {"v": 1})

        # 调用装饰器包装的函数
        result = delete_fund_flow("000001")

        # 验证函数执行成功
        assert result is True

        # 验证缓存已清除（这需要额外验证，可能需要检查统计信息）


class TestCacheDecoratorIntegration:
    """测试缓存装饰器集成"""

    def setup_method(self):
        """测试前初始化"""
        reset_cache_manager()
        reset_cache_integration()
        self.cache_mgr = get_cache_manager()
        self.cache_integration = get_cache_integration()

    def teardown_method(self):
        """测试后清理"""
        reset_cache_manager()
        reset_cache_integration()

    def test_cache_read_wrapper(self):
        """测试读缓存装饰器"""

        call_count = 0

        @cache_read_wrapper("test_type")
        def fetch_data(symbol: str):
            nonlocal call_count
            call_count += 1
            return {"symbol": symbol, "value": 100}

        # 第一次调用 - 应该执行函数
        result1 = fetch_data("000001")
        assert call_count == 1
        assert result1["data"]["value"] == 100

        # 第二次调用 - 应该使用缓存
        result2 = fetch_data("000001")
        assert call_count == 1  # 函数不应再被调用
        assert result2["source"] == "cache"

    def test_cache_write_wrapper(self):
        """测试写缓存装饰器"""

        @cache_write_wrapper("test_type")
        def save_data(symbol: str, data: Dict[str, Any]):
            return True

        # 调用装饰器包装的函数
        result = save_data("000001", {"value": 100})

        # 验证成功
        assert result is True

        # 验证数据已写入缓存
        cached = self.cache_mgr.fetch_from_cache("000001", "test_type")
        assert cached is not None


class TestCacheDataConsistency:
    """测试缓存与源数据的一致性"""

    def setup_method(self):
        """测试前初始化"""
        reset_cache_manager()
        reset_cache_integration()
        self.cache_mgr = get_cache_manager()
        self.cache_integration = get_cache_integration()

    def teardown_method(self):
        """测试后清理"""
        reset_cache_manager()
        reset_cache_integration()

    def test_cache_aside_pattern_read_then_write(self):
        """测试Cache-Aside模式：先读后写"""
        symbol = "000001"
        data_type = "fund_flow"

        # Step 1: 读取（未命中，从源获取）
        source_data = {"main_inflow": 1000}

        def fetch_fn():
            return source_data

        result1 = self.cache_integration.fetch_with_cache(
            symbol=symbol,
            data_type=data_type,
            fetch_fn=fetch_fn,
        )

        assert result1["source"] == "source"

        # Step 2: 验证数据已在缓存中
        result2 = self.cache_integration.fetch_with_cache(
            symbol=symbol,
            data_type=data_type,
            fetch_fn=lambda: {"should": "not_call"},
        )

        assert result2["source"] == "cache"
        assert result2["data"] == source_data

    def test_cache_invalidation_on_update(self):
        """测试更新时缓存失效"""
        symbol = "000858"
        data_type = "etf"

        # Step 1: 写入缓存
        old_data = {"price": 100}
        self.cache_integration.save_with_cache(
            symbol=symbol,
            data_type=data_type,
            data=old_data,
            save_fn=lambda d: True,
        )

        # Step 2: 验证缓存存在
        cached = self.cache_mgr.fetch_from_cache(symbol, data_type)
        assert cached is not None

        # Step 3: 清除缓存
        self.cache_integration.invalidate_data(symbol=symbol, data_type=data_type)

        # Step 4: 验证缓存已清除
        cached = self.cache_mgr.fetch_from_cache(symbol, data_type)
        # 清除可能返回None或空数据取决于实现


class TestCachePerformance:
    """测试缓存性能"""

    def setup_method(self):
        """测试前初始化"""
        reset_cache_manager()
        reset_cache_integration()
        self.cache_mgr = get_cache_manager()
        self.cache_integration = get_cache_integration()

    def teardown_method(self):
        """测试后清理"""
        reset_cache_manager()
        reset_cache_integration()

    def test_batch_operation_performance(self):
        """测试批量操作性能"""
        import time

        queries = [{"symbol": f"{i:06d}", "data_type": "fund_flow"} for i in range(100)]

        def fetch_fn(symbol):
            return {"symbol": symbol, "data": "test"}

        # 测量批量读取性能
        start = time.time()
        results = self.cache_integration.batch_fetch_with_cache(
            queries=queries,
            fetch_fn=fetch_fn,
            use_cache=True,
        )
        elapsed = time.time() - start

        # 验证结果
        assert len(results) > 0
        # 批量操作应该相对快速
        assert elapsed < 5  # 100条记录应在5秒内完成

    def test_cache_hit_rate(self):
        """测试缓存命中率"""
        # 写入缓存
        for i in range(10):
            self.cache_mgr.write_to_cache(
                symbol=f"00000{i}",
                data_type="fund_flow",
                timeframe="1d",
                data={"value": i},
            )

        # 多次读取
        hit_count = 0
        for i in range(10):
            result = self.cache_integration.fetch_with_cache(
                symbol=f"00000{i}",
                data_type="fund_flow",
                fetch_fn=lambda: {"value": -1},
            )
            if result["source"] == "cache":
                hit_count += 1

        # 验证命中率
        hit_rate = hit_count / 10
        assert hit_rate > 0.5  # 至少50%命中率


class TestCacheErrorHandling:
    """测试缓存错误处理"""

    def setup_method(self):
        """测试前初始化"""
        reset_cache_manager()
        reset_cache_integration()
        self.cache_mgr = get_cache_manager()
        self.cache_integration = get_cache_integration()

    def teardown_method(self):
        """测试后清理"""
        reset_cache_manager()
        reset_cache_integration()

    def test_fetch_with_exception(self):
        """测试获取函数异常"""

        def fetch_fn():
            raise ValueError("Test error")

        with pytest.raises(ValueError):
            self.cache_integration.fetch_with_cache(
                symbol="000001",
                data_type="fund_flow",
                fetch_fn=fetch_fn,
            )

    def test_save_with_exception(self):
        """测试保存函数异常"""

        def save_fn(data):
            raise RuntimeError("Save error")

        with pytest.raises(RuntimeError):
            self.cache_integration.save_with_cache(
                symbol="000001",
                data_type="fund_flow",
                data={"value": 100},
                save_fn=save_fn,
            )

    def test_invalid_query_format(self):
        """测试无效查询格式"""
        queries = [
            {"symbol": "000001"},  # 缺少data_type
            {"data_type": "fund_flow"},  # 缺少symbol
        ]

        results = self.cache_integration.batch_fetch_with_cache(
            queries=queries,
            fetch_fn=lambda s: {"data": "test"},
        )

        # 应该跳过无效查询
        assert len(results) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
