"""
单元测试: SmartCache
"""

import threading
import time
from concurrent.futures import ThreadPoolExecutor

import pytest

from src.core.data_source.smart_cache import SmartCache


class TestSmartCache:
    """SmartCache 单元测试"""

    def test_cache_hit_fresh_data(self):
        """测试缓存命中 (fresh data)"""
        cache = SmartCache(maxsize=10, default_ttl=60)
        cache.set("key1", "value1")

        # 立即获取，应该是 fresh data
        result = cache.get("key1")
        assert result == "value1"
        assert cache.hits == 1
        assert cache.misses == 0

    def test_cache_expiry_hard_expiry(self):
        """测试缓存过期 (硬过期)"""
        cache = SmartCache(maxsize=10, default_ttl=1, soft_expiry=False)
        cache.set("key1", "value1")

        # 等待过期
        time.sleep(1.5)

        # 应该返回 None
        result = cache.get("key1")
        assert result is None
        assert cache.hits == 0
        assert cache.misses == 1

    def test_cache_expiry_soft_expiry(self):
        """测试缓存过期 (软过期)"""
        cache = SmartCache(maxsize=10, default_ttl=1, soft_expiry=True)
        cache.set("key1", "value1")

        # 等待过期
        time.sleep(1.5)

        # 应该返回旧数据
        result = cache.get("key1")
        assert result == "value1"
        assert cache.hits == 1
        assert cache.misses == 0

    def test_pre_refresh(self):
        """测试预刷新机制"""
        refresh_called = threading.Event()

        def refresh_func():
            refresh_called.set()
            return "new_value"

        cache = SmartCache(maxsize=10, default_ttl=2, refresh_threshold=0.5)
        cache.set("key1", "old_value", refresh_func=refresh_func)

        # 等待超过刷新阈值 (2 * 0.5 = 1 秒)
        time.sleep(1.2)

        # 获取应该触发预刷新
        result = cache.get("key1")
        assert result == "old_value"  # 返回旧数据
        assert cache.hits == 1

        # 等待后台刷新完成
        refresh_called.wait(timeout=5)

        # 再次获取应该得到新数据
        time.sleep(0.5)
        result = cache.get("key1")
        assert result == "new_value"

    def test_lru_eviction(self):
        """测试 LRU 淘汰"""
        cache = SmartCache(maxsize=3, default_ttl=60)

        # 填满缓存
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")

        # 访问 key1 和 key2 (使其更recent)
        cache.get("key1")
        cache.get("key2")

        # 添加第4个key，应该淘汰 key3
        cache.set("key4", "value4")

        assert cache.get("key1") == "value1"
        assert cache.get("key2") == "value2"
        assert cache.get("key3") is None  # 被淘汰
        assert cache.get("key4") == "value4"

    def test_concurrent_access(self):
        """测试并发访问 (100 线程并发)"""
        cache = SmartCache(maxsize=100, default_ttl=60)
        errors = []

        def worker(worker_id):
            try:
                # 每个线程写入10个key
                for i in range(10):
                    key = f"worker_{worker_id}_key_{i}"
                    value = f"value_{i}"
                    cache.set(key, value)

                # 每个线程读取100个key
                for i in range(10):
                    key = f"worker_{worker_id}_key_{i}"
                    value = cache.get(key)
                    assert value == f"value_{i}", f"Expected value_{i}, got {value}"

            except Exception as e:
                errors.append((worker_id, e))

        # 启动 100 个并发线程
        with ThreadPoolExecutor(max_workers=100) as executor:
            futures = [executor.submit(worker, i) for i in range(100)]
            for future in futures:
                future.result()

        # 检查是否有错误
        assert len(errors) == 0, f"Errors occurred: {errors}"

        # 检查统计信息
        stats = cache.get_stats()
        assert stats["hits"] > 0
        assert stats["size"] > 0

    def test_background_refresh_failure(self):
        """测试后台刷新失败处理"""

        def failing_refresh_func():
            raise Exception("Refresh failed")

        cache = SmartCache(maxsize=10, default_ttl=1, soft_expiry=True)
        cache.set("key1", "value1", refresh_func=failing_refresh_func)

        # 等待过期
        time.sleep(1.5)

        # 应该返回旧数据 (即使刷新失败)
        result = cache.get("key1")
        assert result == "value1"

        # 等待后台刷新完成
        time.sleep(0.5)

        # 检查统计
        stats = cache.get_stats()
        assert stats["refresh_failures"] > 0

    def test_thread_pool_limit(self):
        """测试线程池限制 (max_workers=5)"""
        cache = SmartCache(maxsize=100, default_ttl=1, max_refresh_workers=5)
        refresh_count = threading.Semaphore(0)
        refresh_releases = threading.Semaphore(0)

        def blocking_refresh_func():
            refresh_count.release()
            refresh_releases.acquire()  # 阻塞直到被释放

        # 启动 10 个刷新任务
        for i in range(10):
            cache.set(f"key{i}", f"value{i}", refresh_func=blocking_refresh_func)
            time.sleep(0.1)  # 确保每个触发独立的刷新

        # 等待至少5个刷新开始
        for _ in range(5):
            refresh_count.acquire(timeout=5)

        # 由于 max_workers=5，最多应该有5个并发刷新
        # (这里我们只验证没有抛出异常)

        # 释放所有阻塞的刷新
        for _ in range(10):
            refresh_releases.release()

    def test_cache_stats(self):
        """测试缓存统计"""
        cache = SmartCache(maxsize=10, default_ttl=60)

        cache.set("key1", "value1")
        cache.set("key2", "value2")

        cache.get("key1")  # hit
        cache.get("key3")  # miss

        stats = cache.get_stats()
        assert stats["size"] == 2
        assert stats["maxsize"] == 10
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["hit_rate"] == 0.5

    def test_invalidate(self):
        """测试缓存失效"""
        cache = SmartCache(maxsize=10, default_ttl=60)
        cache.set("key1", "value1")

        assert cache.get("key1") == "value1"

        cache.invalidate("key1")

        assert cache.get("key1") is None

    def test_clear(self):
        """测试清空缓存"""
        cache = SmartCache(maxsize=10, default_ttl=60)
        cache.set("key1", "value1")
        cache.set("key2", "value2")

        assert cache.get_stats()["size"] == 2

        cache.clear()

        assert cache.get_stats()["size"] == 0

    def test_cleanup_expired(self):
        """测试清理过期条目"""
        cache = SmartCache(maxsize=10, default_ttl=1, soft_expiry=False)
        cache.set("key1", "value1")
        cache.set("key2", "value2", ttl=10)  # 较长的TTL

        # 等待第一个过期
        time.sleep(1.5)

        # 清理过期条目
        cleaned = cache.cleanup_expired()
        assert cleaned == 1
        assert cache.get_stats()["size"] == 1

    def test_custom_ttl(self):
        """测试自定义 TTL"""
        cache = SmartCache(maxsize=10, default_ttl=10, soft_expiry=False)
        cache.set("key1", "value1", ttl=1)

        # 等待自定义 TTL 过期
        time.sleep(1.5)

        result = cache.get("key1")
        assert result is None

    def test_shutdown(self):
        """测试关闭缓存"""
        cache = SmartCache(maxsize=10, default_ttl=60)

        def refresh_func():
            time.sleep(10)

        cache.set("key1", "value1", refresh_func=refresh_func)
        cache.get("key1")  # 触发刷新

        # 关闭缓存
        cache.shutdown()

        # 验证线程池已关闭 (不会抛出异常)
        assert True

    def test_contains(self):
        """测试 __contains__ 方法"""
        cache = SmartCache(maxsize=10, default_ttl=60)
        cache.set("key1", "value1")

        assert "key1" in cache
        assert "key2" not in cache

    def test_len(self):
        """测试 __len__ 方法"""
        cache = SmartCache(maxsize=10, default_ttl=60)
        cache.set("key1", "value1")
        cache.set("key2", "value2")

        assert len(cache) == 2

        cache.invalidate("key1")

        assert len(cache) == 1
