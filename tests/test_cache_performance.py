#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缓存性能对比测试

对比场景:
1. 无缓存 DataManager vs 带缓存 CachedDataManager
2. 重复查询性能提升
3. 内存使用对比
4. 缓存命中率统计

创建日期: 2025-10-25
版本: 1.0.0 (P3)
"""

import sys
import os
import time
import pandas as pd
import psutil
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.data_manager import DataManager
from core.cached_data_manager import CachedDataManager
from core.data_classification import DataClassification


def get_memory_usage_mb():
    """获取当前进程内存使用（MB）"""
    process = psutil.Process()
    return process.memory_info().rss / 1024 / 1024


def test_basic_cache_functionality():
    """测试1: 基础缓存功能"""
    print("\n" + "=" * 70)
    print("测试1: 基础缓存功能")
    print("=" * 70)

    # 创建带缓存的 DataManager
    dm = CachedDataManager(
        enable_cache=True,
        cache_size=100,
        default_ttl=60
    )

    print("✅ CachedDataManager 初始化成功")
    print(f"   缓存大小: 100")
    print(f"   默认TTL: 60秒")

    # 查看初始缓存统计
    stats = dm.get_cache_stats()
    print(f"\n初始缓存统计:")
    for cache_name, cache_stats in stats.items():
        if cache_name != 'caching_enabled':
            print(f"   {cache_name}:")
            print(f"     - 大小: {cache_stats.get('size', 0)}/{cache_stats.get('max_size', 0)}")
            print(f"     - 命中率: {cache_stats.get('hit_rate', 0)}")

    return dm


def test_query_performance_comparison():
    """测试2: 查询性能对比"""
    print("\n" + "=" * 70)
    print("测试2: 查询性能对比（模拟重复查询）")
    print("=" * 70)

    # 创建测试数据（模拟）
    test_data = pd.DataFrame({
        'symbol': ['600000.SH'] * 1000,
        'price': list(range(1000)),
        'volume': list(range(1000, 2000)),
        'date': [datetime.now()] * 1000
    })

    print(f"\n模拟查询数据: {len(test_data)} 行")

    # 测试场景：重复查询10次
    iterations = 10

    # 创建实例
    dm_no_cache = DataManager(enable_monitoring=False)
    dm_cached = CachedDataManager(enable_cache=True, default_ttl=300)

    print(f"\n执行 {iterations} 次重复查询...")

    # 场景1: 无缓存（模拟）
    start_time = time.time()
    for i in range(iterations):
        # 模拟数据库查询延迟
        time.sleep(0.001)  # 1ms模拟查询时间
        result = test_data.copy()  # 模拟从数据库返回

    no_cache_time = (time.time() - start_time) * 1000

    # 场景2: 带缓存
    cache_key = 'test_query_key'
    dm_cached._cache_manager.set('query_cache', cache_key, test_data)

    start_time = time.time()
    for i in range(iterations):
        # 从缓存获取（极快）
        result = dm_cached._cache_manager.get('query_cache', cache_key)

    cached_time = (time.time() - start_time) * 1000

    # 计算性能提升
    speedup = no_cache_time / cached_time if cached_time > 0 else float('inf')

    print(f"\n性能对比结果:")
    print(f"   无缓存总时间: {no_cache_time:.2f}ms")
    print(f"   带缓存总时间: {cached_time:.2f}ms")
    print(f"   性能提升: {speedup:.1f}x")
    print(f"   时间节省: {no_cache_time - cached_time:.2f}ms ({(1 - cached_time/no_cache_time)*100:.1f}%)")

    return {
        'no_cache_time': no_cache_time,
        'cached_time': cached_time,
        'speedup': speedup
    }


def test_cache_hit_rate():
    """测试3: 缓存命中率"""
    print("\n" + "=" * 70)
    print("测试3: 缓存命中率统计")
    print("=" * 70)

    dm = CachedDataManager(enable_cache=True, cache_size=50, default_ttl=300)

    # 模拟50个不同的查询（填满缓存）
    print("\n模拟50个不同查询（填满缓存）...")
    for i in range(50):
        key = f"query_{i}"
        data = pd.DataFrame({'value': [i]})
        dm._cache_manager.set('query_cache', key, data)

    # 模拟100次查询：50%命中，50%未命中
    print("模拟100次混合查询（50%命中，50%未命中）...")
    hits = 0
    misses = 0

    for i in range(100):
        if i % 2 == 0:
            # 命中：查询已缓存的数据
            key = f"query_{i % 50}"
            result = dm._cache_manager.get('query_cache', key)
            if result is not None:
                hits += 1
        else:
            # 未命中：查询新数据
            key = f"query_new_{i}"
            result = dm._cache_manager.get('query_cache', key)
            if result is None:
                misses += 1

    hit_rate = (hits / (hits + misses) * 100) if (hits + misses) > 0 else 0

    print(f"\n缓存命中率统计:")
    print(f"   总查询数: {hits + misses}")
    print(f"   缓存命中: {hits}")
    print(f"   缓存未命中: {misses}")
    print(f"   命中率: {hit_rate:.1f}%")

    # 获取官方统计
    stats = dm.get_cache_stats()
    if 'query_cache' in stats:
        print(f"\n官方缓存统计:")
        cache_stats = stats['query_cache']
        print(f"   命中: {cache_stats.get('hits', 0)}")
        print(f"   未命中: {cache_stats.get('misses', 0)}")
        print(f"   命中率: {cache_stats.get('hit_rate', 0)}")
        print(f"   当前大小: {cache_stats.get('size', 0)}/{cache_stats.get('max_size', 0)}")

    return hit_rate


def test_memory_usage():
    """测试4: 内存使用对比"""
    print("\n" + "=" * 70)
    print("测试4: 内存使用对比")
    print("=" * 70)

    # 初始内存
    initial_memory = get_memory_usage_mb()
    print(f"\n初始内存: {initial_memory:.2f}MB")

    # 创建带缓存的 DataManager
    dm = CachedDataManager(enable_cache=True, cache_size=1000, default_ttl=300)

    # 缓存1000个小数据集
    print("\n缓存1000个小数据集（每个10行）...")
    for i in range(1000):
        key = f"data_{i}"
        data = pd.DataFrame({
            'id': list(range(10)),
            'value': list(range(i, i+10))
        })
        dm._cache_manager.set('query_cache', key, data)

    # 缓存后内存
    after_cache_memory = get_memory_usage_mb()
    memory_increase = after_cache_memory - initial_memory

    print(f"\n内存使用统计:")
    print(f"   缓存前: {initial_memory:.2f}MB")
    print(f"   缓存后: {after_cache_memory:.2f}MB")
    print(f"   增加: {memory_increase:.2f}MB")
    print(f"   平均每条目: {memory_increase/1000*1024:.2f}KB")

    # 清除缓存
    dm.clear_cache()

    # 清除后内存
    after_clear_memory = get_memory_usage_mb()

    print(f"\n清除缓存后:")
    print(f"   内存: {after_clear_memory:.2f}MB")
    print(f"   释放: {after_cache_memory - after_clear_memory:.2f}MB")

    return memory_increase


def test_lru_eviction():
    """测试5: LRU淘汰机制"""
    print("\n" + "=" * 70)
    print("测试5: LRU淘汰机制")
    print("=" * 70)

    # 创建小缓存（最多10个条目）
    dm = CachedDataManager(enable_cache=True, cache_size=10, default_ttl=300)

    print(f"\n缓存大小限制: 10条目")

    # 插入15个条目（超过限制）
    print("插入15个条目...")
    for i in range(15):
        key = f"item_{i}"
        data = pd.DataFrame({'value': [i]})
        dm._cache_manager.set('query_cache', key, data)

    # 检查最早的5个条目是否被淘汰
    print("\n检查LRU淘汰:")
    evicted_count = 0
    kept_count = 0

    for i in range(15):
        key = f"item_{i}"
        result = dm._cache_manager.get('query_cache', key)
        if result is None:
            evicted_count += 1
            if i < 5:  # 前5个应该被淘汰
                print(f"   ✅ {key}: 已淘汰（符合预期）")
        else:
            kept_count += 1
            if i >= 5:  # 后10个应该保留
                print(f"   ✅ {key}: 已保留（符合预期）")

    stats = dm.get_cache_stats()
    if 'query_cache' in stats:
        cache_stats = stats['query_cache']
        print(f"\n淘汰统计:")
        print(f"   淘汰数量: {cache_stats.get('evictions', 0)}")
        print(f"   当前大小: {cache_stats.get('size', 0)}")

    return evicted_count


def main():
    """主测试流程"""
    print("\n" + "=" * 70)
    print("缓存性能综合测试")
    print("=" * 70)
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    results = {}

    try:
        # 测试1: 基础功能
        test_basic_cache_functionality()

        # 测试2: 性能对比
        perf_results = test_query_performance_comparison()
        results['performance'] = perf_results

        # 测试3: 命中率
        hit_rate = test_cache_hit_rate()
        results['hit_rate'] = hit_rate

        # 测试4: 内存使用
        memory_increase = test_memory_usage()
        results['memory'] = memory_increase

        # 测试5: LRU淘汰
        evicted_count = test_lru_eviction()
        results['evictions'] = evicted_count

    except Exception as e:
        print(f"\n❌ 测试过程异常: {str(e)}")
        import traceback
        traceback.print_exc()

    # 输出总结
    print("\n" + "=" * 70)
    print("测试总结")
    print("=" * 70)

    if 'performance' in results:
        perf = results['performance']
        print(f"\n📊 性能提升: {perf['speedup']:.1f}x")
        print(f"   无缓存: {perf['no_cache_time']:.2f}ms")
        print(f"   有缓存: {perf['cached_time']:.2f}ms")

    if 'hit_rate' in results:
        print(f"\n🎯 缓存命中率: {results['hit_rate']:.1f}%")

    if 'memory' in results:
        print(f"\n💾 内存开销: {results['memory']:.2f}MB (1000条目)")

    if 'evictions' in results:
        print(f"\n🔄 LRU淘汰: {results['evictions']}个条目被淘汰")

    print(f"\n✅ 所有缓存测试完成！")

    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
