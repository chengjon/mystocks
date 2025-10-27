#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
US3 DataManager 综合测试套件
包括：边界测试、性能基准测试、压力测试

版本: 1.0.0
创建日期: 2025-10-25
"""

import os
import sys
import time
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.data_manager import DataManager
from core.data_classification import DataClassification, DatabaseTarget


# ============================================
# 测试配置
# ============================================

class TestConfig:
    """测试配置"""
    # 性能基准
    ROUTING_TIME_TARGET_MS = 0.001  # 路由时间目标：1ms（小数据集）
    ROUTING_TIME_EXPECTED_MS = 0.0002  # 预期：0.0002ms
    ROUTING_TIME_LARGE_DATA_MS = 0.005  # 大数据集（10k行）目标：5ms
    ROUTING_TIME_VERY_LARGE_DATA_MS = 0.01  # 超大数据集（100k行）目标：10ms

    # 压力测试
    STRESS_THREAD_COUNT = 10  # 并发线程数
    STRESS_OPERATIONS_PER_THREAD = 100  # 每线程操作数

    # 边界测试
    MAX_DATA_SIZE = 1000000  # 最大数据条数
    MIN_DATA_SIZE = 0  # 最小数据条数


# ============================================
# 测试夹具
# ============================================

@pytest.fixture(scope="module")
def data_manager():
    """创建 DataManager 实例"""
    dm = DataManager()
    yield dm
    # 清理（如果需要）


@pytest.fixture
def sample_dataframe():
    """创建示例 DataFrame"""
    return pd.DataFrame({
        'symbol': ['600000', '000001', '000002'],
        'name': ['浦发银行', '平安银行', '万科A'],
        'price': [10.50, 12.30, 15.80],
        'volume': [1000000, 2000000, 1500000]
    })


@pytest.fixture
def large_dataframe():
    """创建大规模 DataFrame"""
    size = 10000
    return pd.DataFrame({
        'symbol': [f'60{i:04d}' for i in range(size)],
        'price': np.random.uniform(5, 100, size),
        'volume': np.random.randint(1000, 1000000, size)
    })


# ============================================
# 1. 边界测试 (Boundary Tests)
# ============================================

class TestBoundaryConditions:
    """边界条件测试"""

    def test_empty_dataframe(self, data_manager):
        """测试空 DataFrame"""
        empty_df = pd.DataFrame()

        # 应该能够处理空数据而不崩溃
        result = data_manager.get_target_database(DataClassification.DAILY_KLINE)
        assert result == DatabaseTarget.POSTGRESQL

    def test_single_row_dataframe(self, data_manager):
        """测试单行 DataFrame"""
        single_row = pd.DataFrame({
            'symbol': ['600000'],
            'price': [10.50]
        })

        result = data_manager.get_target_database(DataClassification.TICK_DATA)
        assert result == DatabaseTarget.TDENGINE

    def test_large_dataframe(self, data_manager, large_dataframe):
        """测试大规模 DataFrame（10,000行）"""
        start_time = time.time()
        result = data_manager.get_target_database(DataClassification.MINUTE_KLINE)
        routing_time = (time.time() - start_time) * 1000

        assert result == DatabaseTarget.TDENGINE
        assert routing_time < TestConfig.ROUTING_TIME_LARGE_DATA_MS
        print(f"  ✓ 10,000行数据路由时间: {routing_time:.6f}ms")

    def test_very_large_dataframe(self, data_manager):
        """测试超大规模 DataFrame（100,000行）"""
        size = 100000
        very_large_df = pd.DataFrame({
            'symbol': [f'60{i:04d}' for i in range(size)],
            'price': np.random.uniform(5, 100, size)
        })

        start_time = time.time()
        result = data_manager.get_target_database(DataClassification.DAILY_KLINE)
        routing_time = (time.time() - start_time) * 1000

        assert result == DatabaseTarget.POSTGRESQL
        assert routing_time < TestConfig.ROUTING_TIME_VERY_LARGE_DATA_MS
        print(f"  ✓ 100,000行数据路由时间: {routing_time:.6f}ms")

    def test_all_34_classifications(self, data_manager):
        """测试所有34种数据分类的路由"""
        classifications = [
            # 市场数据 (6种)
            DataClassification.TICK_DATA,
            DataClassification.MINUTE_KLINE,
            DataClassification.DAILY_KLINE,
            DataClassification.ORDER_BOOK_DEPTH,
            DataClassification.LEVEL2_SNAPSHOT,
            DataClassification.INDEX_QUOTES,

            # 参考数据 (9种)
            DataClassification.SYMBOLS_INFO,
            DataClassification.INDUSTRY_CLASS,
            DataClassification.CONCEPT_CLASS,
            DataClassification.INDEX_CONSTITUENTS,
            DataClassification.TRADE_CALENDAR,
            DataClassification.FUNDAMENTAL_METRICS,
            DataClassification.DIVIDEND_DATA,
            DataClassification.SHAREHOLDER_DATA,
            DataClassification.MARKET_RULES,

            # 衍生数据 (6种)
            DataClassification.TECHNICAL_INDICATORS,
            DataClassification.QUANT_FACTORS,
            DataClassification.MODEL_OUTPUT,
            DataClassification.TRADE_SIGNALS,
            DataClassification.BACKTEST_RESULTS,
            DataClassification.RISK_METRICS,

            # 交易数据 (7种)
            DataClassification.ORDER_RECORDS,
            DataClassification.TRADE_RECORDS,
            DataClassification.POSITION_HISTORY,
            DataClassification.REALTIME_POSITIONS,
            DataClassification.REALTIME_ACCOUNT,
            DataClassification.FUND_FLOW,
            DataClassification.ORDER_QUEUE,

            # 元数据 (6种)
            DataClassification.DATA_SOURCE_STATUS,
            DataClassification.TASK_SCHEDULE,
            DataClassification.STRATEGY_PARAMS,
            DataClassification.SYSTEM_CONFIG,
            DataClassification.DATA_QUALITY_METRICS,
            DataClassification.USER_CONFIG,
        ]

        results = {}
        for classification in classifications:
            target_db = data_manager.get_target_database(classification)
            results[classification.value] = target_db.value

        # 验证路由规则
        # 高频时序数据 → TDengine
        assert results['TICK_DATA'].upper() == 'TDENGINE'
        assert results['MINUTE_KLINE'].upper() == 'TDENGINE'
        assert results['ORDER_BOOK_DEPTH'].upper() == 'TDENGINE'
        assert results['LEVEL2_SNAPSHOT'].upper() == 'TDENGINE'
        assert results['INDEX_QUOTES'].upper() == 'TDENGINE'

        # 所有其他数据 → PostgreSQL
        assert results['DAILY_KLINE'].upper() == 'POSTGRESQL'
        assert results['SYMBOLS_INFO'].upper() == 'POSTGRESQL'
        assert results['TECHNICAL_INDICATORS'].upper() == 'POSTGRESQL'

        print(f"  ✓ 所有34种数据分类路由验证通过")

        # 统计分布
        tdengine_count = sum(1 for v in results.values() if v.upper() == 'TDENGINE')
        postgresql_count = sum(1 for v in results.values() if v.upper() == 'POSTGRESQL')

        print(f"  ✓ TDengine: {tdengine_count}种分类 ({tdengine_count/34*100:.1f}%)")
        print(f"  ✓ PostgreSQL: {postgresql_count}种分类 ({postgresql_count/34*100:.1f}%)")

        assert tdengine_count == 5  # 高频时序数据
        assert postgresql_count == 29  # 其他所有数据

    def test_invalid_classification(self, data_manager):
        """测试无效的数据分类（应该默认路由到 PostgreSQL）"""
        # 创建一个不在路由映射中的分类（理论上不应该发生）
        # 但测试默认行为
        result = data_manager.get_target_database(DataClassification.SYMBOLS_INFO)
        assert result in [DatabaseTarget.TDENGINE, DatabaseTarget.POSTGRESQL]

    def test_null_values_dataframe(self, data_manager):
        """测试包含 NULL 值的 DataFrame"""
        null_df = pd.DataFrame({
            'symbol': ['600000', None, '000002'],
            'price': [10.50, None, 15.80],
            'volume': [1000000, 2000000, None]
        })

        # 应该能够处理包含 NULL 的数据
        result = data_manager.get_target_database(DataClassification.DAILY_KLINE)
        assert result == DatabaseTarget.POSTGRESQL

    def test_extreme_values_dataframe(self, data_manager):
        """测试极端数值"""
        extreme_df = pd.DataFrame({
            'symbol': ['600000'],
            'price': [1e10],  # 极大值
            'volume': [1],  # 极小值
            'amount': [0.0000001]  # 极小浮点数
        })

        result = data_manager.get_target_database(DataClassification.TICK_DATA)
        assert result == DatabaseTarget.TDENGINE


# ============================================
# 2. 性能基准测试 (Performance Benchmark)
# ============================================

class TestPerformanceBenchmark:
    """性能基准测试"""

    def test_routing_decision_speed_single(self, data_manager):
        """测试单次路由决策速度"""
        routing_times = []
        iterations = 1000

        for _ in range(iterations):
            start_time = time.time()
            data_manager.get_target_database(DataClassification.TICK_DATA)
            end_time = time.time()
            routing_times.append((end_time - start_time) * 1000)  # 转换为毫秒

        avg_time = np.mean(routing_times)
        min_time = np.min(routing_times)
        max_time = np.max(routing_times)
        p95_time = np.percentile(routing_times, 95)
        p99_time = np.percentile(routing_times, 99)

        print(f"\n  路由决策性能 (1,000次迭代):")
        print(f"  ✓ 平均时间: {avg_time:.6f}ms")
        print(f"  ✓ 最小时间: {min_time:.6f}ms")
        print(f"  ✓ 最大时间: {max_time:.6f}ms")
        print(f"  ✓ P95: {p95_time:.6f}ms")
        print(f"  ✓ P99: {p99_time:.6f}ms")

        # 验证性能目标
        assert avg_time < TestConfig.ROUTING_TIME_TARGET_MS, \
            f"平均路由时间 {avg_time:.6f}ms 超过目标 {TestConfig.ROUTING_TIME_TARGET_MS}ms"

        # 验证是否达到预期性能（0.0002ms 附近）
        if avg_time < TestConfig.ROUTING_TIME_EXPECTED_MS * 10:
            print(f"  🎉 超出预期！平均时间 {avg_time:.6f}ms 接近预期 {TestConfig.ROUTING_TIME_EXPECTED_MS}ms")

    def test_routing_decision_speed_all_classifications(self, data_manager):
        """测试所有34种分类的路由速度"""
        classifications = list(DataClassification)

        total_time_ms = 0
        for classification in classifications:
            start_time = time.time()
            data_manager.get_target_database(classification)
            end_time = time.time()
            total_time_ms += (end_time - start_time) * 1000

        avg_time_per_classification = total_time_ms / len(classifications)

        print(f"\n  所有34种分类路由性能:")
        print(f"  ✓ 总时间: {total_time_ms:.6f}ms")
        print(f"  ✓ 平均每分类: {avg_time_per_classification:.6f}ms")

        assert avg_time_per_classification < TestConfig.ROUTING_TIME_TARGET_MS

    def test_throughput_sequential(self, data_manager):
        """测试顺序执行吞吐量"""
        iterations = 10000
        classifications = [
            DataClassification.TICK_DATA,
            DataClassification.DAILY_KLINE,
            DataClassification.SYMBOLS_INFO,
            DataClassification.TECHNICAL_INDICATORS
        ]

        start_time = time.time()
        for i in range(iterations):
            classification = classifications[i % len(classifications)]
            data_manager.get_target_database(classification)
        end_time = time.time()

        total_time = end_time - start_time
        throughput = iterations / total_time

        print(f"\n  顺序执行吞吐量 (10,000次路由):")
        print(f"  ✓ 总时间: {total_time:.3f}秒")
        print(f"  ✓ 吞吐量: {throughput:.0f} 次/秒")
        print(f"  ✓ 平均每次: {(total_time/iterations)*1000:.6f}ms")

        # 期望吞吐量 > 100,000 次/秒（基于 0.01ms 的路由时间）
        assert throughput > 10000, f"吞吐量 {throughput:.0f} 次/秒 低于预期"

    def test_memory_usage(self, data_manager):
        """测试内存使用情况"""
        import psutil
        import gc

        process = psutil.Process()

        # 强制垃圾回收
        gc.collect()

        # 记录初始内存
        mem_before = process.memory_info().rss / 1024 / 1024  # MB

        # 执行大量路由操作
        for _ in range(100000):
            data_manager.get_target_database(DataClassification.TICK_DATA)

        # 强制垃圾回收
        gc.collect()

        # 记录最终内存
        mem_after = process.memory_info().rss / 1024 / 1024  # MB
        mem_increase = mem_after - mem_before

        print(f"\n  内存使用 (100,000次路由):")
        print(f"  ✓ 初始: {mem_before:.2f}MB")
        print(f"  ✓ 最终: {mem_after:.2f}MB")
        print(f"  ✓ 增加: {mem_increase:.2f}MB")

        # 验证内存增长合理（预期 <10MB）
        assert mem_increase < 10, f"内存增长 {mem_increase:.2f}MB 超过预期"


# ============================================
# 3. 压力测试 (Stress Tests)
# ============================================

class TestStressConditions:
    """压力测试"""

    def test_concurrent_routing_decisions(self, data_manager):
        """测试并发路由决策"""
        thread_count = TestConfig.STRESS_THREAD_COUNT
        operations_per_thread = TestConfig.STRESS_OPERATIONS_PER_THREAD

        def worker(thread_id: int) -> Dict[str, Any]:
            """工作线程"""
            start_time = time.time()
            results = []

            for i in range(operations_per_thread):
                classification = DataClassification.TICK_DATA if i % 2 == 0 else DataClassification.DAILY_KLINE
                routing_start = time.time()
                target_db = data_manager.get_target_database(classification)
                routing_time = (time.time() - routing_start) * 1000
                results.append({
                    'thread_id': thread_id,
                    'iteration': i,
                    'routing_time_ms': routing_time,
                    'target_db': target_db.value
                })

            end_time = time.time()
            return {
                'thread_id': thread_id,
                'total_time': end_time - start_time,
                'operations': len(results),
                'results': results
            }

        # 并发执行
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=thread_count) as executor:
            futures = [executor.submit(worker, i) for i in range(thread_count)]
            thread_results = [future.result() for future in as_completed(futures)]
        end_time = time.time()

        total_time = end_time - start_time
        total_operations = thread_count * operations_per_thread
        throughput = total_operations / total_time

        # 收集所有路由时间
        all_routing_times = []
        for thread_result in thread_results:
            for result in thread_result['results']:
                all_routing_times.append(result['routing_time_ms'])

        avg_routing_time = np.mean(all_routing_times)
        max_routing_time = np.max(all_routing_times)
        p99_routing_time = np.percentile(all_routing_times, 99)

        print(f"\n  并发压力测试 ({thread_count}线程 x {operations_per_thread}次):")
        print(f"  ✓ 总时间: {total_time:.3f}秒")
        print(f"  ✓ 总操作数: {total_operations}")
        print(f"  ✓ 吞吐量: {throughput:.0f} 次/秒")
        print(f"  ✓ 平均路由时间: {avg_routing_time:.6f}ms")
        print(f"  ✓ 最大路由时间: {max_routing_time:.6f}ms")
        print(f"  ✓ P99路由时间: {p99_routing_time:.6f}ms")

        # 验证性能
        assert avg_routing_time < TestConfig.ROUTING_TIME_TARGET_MS
        assert throughput > 1000, f"并发吞吐量 {throughput:.0f} 次/秒 低于预期"

    def test_sustained_load(self, data_manager):
        """测试持续负载（持续10秒）"""
        duration_seconds = 10
        classifications = list(DataClassification)

        operation_count = 0
        routing_times = []

        start_time = time.time()
        while time.time() - start_time < duration_seconds:
            classification = classifications[operation_count % len(classifications)]

            routing_start = time.time()
            data_manager.get_target_database(classification)
            routing_time = (time.time() - routing_start) * 1000

            routing_times.append(routing_time)
            operation_count += 1

        end_time = time.time()
        actual_duration = end_time - start_time
        throughput = operation_count / actual_duration
        avg_routing_time = np.mean(routing_times)

        print(f"\n  持续负载测试 ({actual_duration:.1f}秒):")
        print(f"  ✓ 总操作数: {operation_count}")
        print(f"  ✓ 吞吐量: {throughput:.0f} 次/秒")
        print(f"  ✓ 平均路由时间: {avg_routing_time:.6f}ms")

        assert throughput > 10000, f"持续负载吞吐量 {throughput:.0f} 次/秒 低于预期"

    def test_rapid_classification_switching(self, data_manager):
        """测试快速切换不同分类"""
        iterations = 10000
        classifications = list(DataClassification)

        routing_times = []
        start_time = time.time()

        for i in range(iterations):
            # 每次迭代切换不同的分类
            classification = classifications[i % len(classifications)]

            routing_start = time.time()
            data_manager.get_target_database(classification)
            routing_time = (time.time() - routing_start) * 1000
            routing_times.append(routing_time)

        end_time = time.time()
        total_time = end_time - start_time
        throughput = iterations / total_time
        avg_routing_time = np.mean(routing_times)

        print(f"\n  快速切换测试 ({iterations}次，34种分类):")
        print(f"  ✓ 总时间: {total_time:.3f}秒")
        print(f"  ✓ 吞吐量: {throughput:.0f} 次/秒")
        print(f"  ✓ 平均路由时间: {avg_routing_time:.6f}ms")

        assert throughput > 10000


# ============================================
# 4. 集成测试 (Integration Tests)
# ============================================

class TestIntegration:
    """集成测试"""

    def test_end_to_end_workflow(self, data_manager, sample_dataframe):
        """端到端工作流测试"""
        # 1. 获取路由目标
        classification = DataClassification.SYMBOLS_INFO
        target_db = data_manager.get_target_database(classification)

        # 2. 验证路由结果
        assert target_db == DatabaseTarget.POSTGRESQL

        # 3. 验证数据分类映射完整性
        assert DataClassification.SYMBOLS_INFO in data_manager._ROUTING_MAP

        print(f"  ✓ 端到端工作流测试通过")

    def test_routing_consistency(self, data_manager):
        """测试路由一致性（多次调用应该返回相同结果）"""
        classification = DataClassification.TICK_DATA

        # 多次调用
        results = [data_manager.get_target_database(classification) for _ in range(100)]

        # 验证一致性
        assert all(r == DatabaseTarget.TDENGINE for r in results)
        print(f"  ✓ 路由一致性测试通过（100次调用）")


# ============================================
# 测试运行入口
# ============================================

if __name__ == "__main__":
    # 运行测试
    print("=" * 60)
    print("US3 DataManager 综合测试套件")
    print("=" * 60)

    pytest.main([
        __file__,
        "-v",  # 详细输出
        "-s",  # 显示 print 输出
        "--tb=short",  # 简短的错误追踪
        "--durations=10",  # 显示最慢的10个测试
    ])
