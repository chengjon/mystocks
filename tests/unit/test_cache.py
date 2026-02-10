"""
Unit Tests for Multi-Level Cache Module
Tests for memory cache, redis cache, and cache decorators
"""

import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.core.cache.multi_level import (
    CacheConfig,
    CircuitBreaker,
    MemoryCache,
    MultiLevelCache,
    generate_cache_key,
)


class TestMemoryCache:
    """MemoryCache单元测试"""

    def setup_method(self):
        """Setup test fixtures"""
        self.cache = MemoryCache(max_size=100, default_ttl=60)

    @pytest.mark.asyncio
    async def test_set_and_get(self):
        """测试设置和获取缓存"""
        await self.cache.set("key1", "value1")
        result = await self.cache.get("key1")
        assert result == "value1"

    @pytest.mark.asyncio
    async def test_get_nonexistent_key(self):
        """测试获取不存在的键"""
        result = await self.cache.get("nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_key(self):
        """测试删除键"""
        await self.cache.set("key1", "value1")
        assert await self.cache.delete("key1") is True
        assert await self.cache.get("key1") is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent_key(self):
        """测试删除不存在的键"""
        assert await self.cache.delete("nonexistent") is False

    @pytest.mark.asyncio
    async def test_ttl_expiration(self):
        """测试TTL过期"""
        await self.cache.set("key1", "value1", ttl=1)
        await asyncio.sleep(1.5)
        result = await self.cache.get("key1")
        assert result is None

    @pytest.mark.asyncio
    async def test_clear(self):
        """测试清空缓存"""
        await self.cache.set("key1", "value1")
        await self.cache.set("key2", "value2")
        await self.cache.clear()
        assert await self.cache.get("key1") is None
        assert await self.cache.get("key2") is None

    @pytest.mark.asyncio
    async def test_max_size_eviction(self):
        """测试最大尺寸逐出"""
        for i in range(105):
            await self.cache.set(f"key{i}", f"value{i}")

        stats = self.cache.get_stats()
        assert stats["size"] <= 100

    def test_get_stats(self):
        """测试获取统计信息"""
        stats = self.cache.get_stats()
        assert "hits" in stats
        assert "misses" in stats
        assert "size" in stats
        assert "hit_rate" in stats


class TestCircuitBreaker:
    """CircuitBreaker单元测试"""

    def setup_method(self):
        """Setup test fixtures"""
        self.breaker = CircuitBreaker(timeout=1.0, failure_threshold=3)

    @pytest.mark.asyncio
    async def test_successful_call(self):
        """测试成功调用"""

        async def success_func():
            return "success"

        result = await self.breaker.call(success_func)
        assert result == "success"

    @pytest.mark.asyncio
    async def test_circuit_opens_after_failures(self):
        """测试故障后熔断器打开"""

        async def fail_func():
            raise ValueError("fail")

        for _ in range(3):
            with pytest.raises(ValueError):
                await self.breaker.call(fail_func)

        state = self.breaker.get_state()
        assert state["open"] is True

    @pytest.mark.asyncio
    async def test_circuit_recovers_after_timeout(self):
        """测试熔断器超时后恢复"""

        async def fail_func():
            raise ValueError("fail")

        for _ in range(3):
            with pytest.raises(ValueError):
                await self.breaker.call(fail_func)

        await asyncio.sleep(1.5)

        async def success_func():
            return "success"

        result = await self.breaker.call(success_func)
        assert result == "success"

    def test_get_state(self):
        """测试获取熔断器状态"""
        state = self.breaker.get_state()
        assert "open" in state
        assert "failure_count" in state


class TestCacheConfig:
    """CacheConfig单元测试"""

    def test_default_config(self):
        """测试默认配置"""
        config = CacheConfig()
        assert config.memory_max_size == 10000
        assert config.memory_ttl == 60
        assert config.redis_ttl == 300

    def test_custom_config(self):
        """测试自定义配置"""
        config = CacheConfig(
            memory_max_size=5000,
            memory_ttl=30,
            redis_ttl=600,
            redis_key_prefix="custom:",
        )
        assert config.memory_max_size == 5000
        assert config.memory_ttl == 30
        assert config.redis_ttl == 600
        assert config.redis_key_prefix == "custom:"


class TestGenerateCacheKey:
    """generate_cache_key单元测试"""

    def test_simple_key(self):
        """测试简单键生成"""
        key = generate_cache_key("test", param1="value1", param2="value2")
        assert key is not None
        assert len(key) == 32

    def test_sorted_params(self):
        """测试参数排序"""
        key1 = generate_cache_key("test", a="1", b="2", c="3")
        key2 = generate_cache_key("test", c="3", a="1", b="2")
        assert key1 == key2

    def test_different_prefix(self):
        """测试不同前缀"""
        key1 = generate_cache_key("prefix1", value="test")
        key2 = generate_cache_key("prefix2", value="test")
        assert key1 != key2


class TestMultiLevelCacheIntegration:
    """MultiLevelCache集成测试"""

    def setup_method(self):
        """Setup test fixtures"""
        self.cache = MultiLevelCache(CacheConfig(memory_max_size=100))
        
        # Mock Redis
        self.redis_store = {}
        self.cache._redis = AsyncMock()
        
        async def mock_get(key):
            return self.redis_store.get(key)
            
        async def mock_set(key, value, ex=None):
            self.redis_store[key] = value
            return True

        async def mock_setex(key, time, value):
            self.redis_store[key] = value
            return True
            
        async def mock_delete(*keys):
            count = 0
            for key in keys:
                if key in self.redis_store:
                    del self.redis_store[key]
                    count += 1
            return count

        async def mock_keys(pattern):
            # Simple implementation for pattern matching
            prefix = pattern.replace('*', '')
            # encode to bytes if needed by real redis? Mock usually returns what was put in
            # Assuming implementation handles str keys
            return [k for k in self.redis_store.keys() if k.startswith(prefix)]

        self.cache._redis.get.side_effect = mock_get
        self.cache._redis.set.side_effect = mock_set
        self.cache._redis.setex.side_effect = mock_setex
        self.cache._redis.delete.side_effect = mock_delete
        self.cache._redis.keys.side_effect = mock_keys
        self.cache._redis_connected = True

    @pytest.mark.asyncio
    async def test_memory_cache_hit(self):
        """测试内存缓存命中"""
        await self.cache.set("key1", "value1", memory_only=True)
        result, found, level = await self.cache.get("key1")
        assert result == "value1"
        assert found is True
        assert level == "memory"

    @pytest.mark.asyncio
    async def test_cache_promotion(self):
        """测试缓存提升（Redis -> Memory）"""
        await self.cache.set("key1", "value1")
        await self.cache._memory_cache.delete("key1")

        result, found, level = await self.cache.get("key1")
        assert result == "value1"
        assert found is True
        assert level == "redis"

        result2, _, level2 = await self.cache.get("key1")
        assert level2 == "memory"

    @pytest.mark.asyncio
    async def test_delete_pattern(self):
        """测试模式删除"""
        await self.cache.set("stock:000001:price", 100)
        await self.cache.set("stock:000001:volume", 1000)
        await self.cache.set("stock:000002:price", 200)

        count = await self.cache.delete_pattern("stock:000001")

        assert count >= 2

    def test_get_stats(self):
        """测试获取统计"""
        stats = self.cache.get_stats()
        assert "memory" in stats
        assert "redis" in stats


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
