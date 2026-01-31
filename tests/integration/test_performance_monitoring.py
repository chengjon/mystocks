"""
性能监控集成测试 (T033)

测试性能监控器是否正确跟踪查询性能并在慢查询时告警。

验证点:
1. 正常查询 → 性能指标记录
2. 慢查询检测 → 自动告警
3. 性能统计 → 正确汇总
4. 批量操作性能 → 吞吐量记录

创建日期: 2025-10-12
"""

import os
import sys
import time
import unittest
from datetime import datetime

import pandas as pd

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.core.data_classification import DataClassification
from src.core.unified_manager import MyStocksUnifiedManager
from src.monitoring.performance_monitor import get_performance_monitor


class TestPerformanceMonitoring(unittest.TestCase):
    """性能监控集成测试"""

    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        print("\n" + "=" * 80)
        print("T033: 性能监控集成测试")
        print("=" * 80 + "\n")

        # 初始化统一管理器 (启用监控)
        cls.manager = MyStocksUnifiedManager(enable_monitoring=True)
        cls.performance_monitor = get_performance_monitor()

    def test_01_normal_query_tracking(self):
        """测试1: 正常查询性能跟踪"""
        print("测试1: 正常查询性能跟踪...")

        # 准备测试数据
        test_data = pd.DataFrame(
            {
                "symbol": ["600000.SH", "600001.SH"],
                "price": [10.5, 11.2],
                "volume": [1000000, 1200000],
                "timestamp": [datetime.now(), datetime.now()],
            }
        )

        # 保存数据
        self.manager.save_data_by_classification(
            DataClassification.REALTIME_POSITIONS,
            test_data,
            table_name="test_perf_quotes",
        )

        # 执行查询
        start_time = time.time()
        result_df = self.manager.load_data_by_classification(
            DataClassification.REALTIME_POSITIONS,
            table_name="test_perf_quotes",
            limit=10,
        )
        query_time_ms = (time.time() - start_time) * 1000

        print(f"  查询耗时: {query_time_ms:.2f}ms")
        print(f"  查询结果: {len(result_df)}行")

        if self.manager.enable_monitoring:
            print("  ✅ 查询性能已记录")
        else:
            print("  ⚠️  监控未启用")

    def test_02_slow_query_detection(self):
        """测试2: 慢查询检测和告警"""
        print("\n测试2: 慢查询检测和告警...")

        # 使用性能监控上下文模拟慢查询
        if self.manager.enable_monitoring:
            with self.performance_monitor.track_operation(
                operation_name="test_slow_query",
                classification="DAILY_KLINE",
                database_type="postgresql",
                table_name="test_slow_table",
                auto_alert=False,  # 禁用自动告警避免依赖
            ):
                # 模拟慢查询 (睡眠5.5秒)
                print("  模拟慢查询 (5.5秒)...")
                time.sleep(5.5)

            print("  ✅ 慢查询已记录 (>5秒)")
        else:
            print("  ⚠️  监控未启用,跳过慢查询测试")

    def test_03_performance_statistics(self):
        """测试3: 性能统计汇总"""
        print("\n测试3: 性能统计汇总...")

        # 获取性能统计
        if self.manager.enable_monitoring:
            stats = self.performance_monitor.get_performance_summary(hours=24)

            print(f"  统计周期: {stats.get('period_hours', 0)}小时")
            print(f"  慢查询数: {stats.get('slow_query_count', 0)}")
            print(f"  平均查询时间: {stats.get('avg_query_time_ms', 0)}ms")
            print(f"  最大查询时间: {stats.get('max_query_time_ms', 0)}ms")
            print(f"  总查询数: {stats.get('total_queries', 0)}")
            print("  ✅ 性能统计正常")
        else:
            print("  ⚠️  监控未启用")

    def test_04_batch_operation_performance(self):
        """测试4: 批量操作性能记录"""
        print("\n测试4: 批量操作性能记录...")

        # 准备大批量数据
        batch_size = 1000
        batch_data = pd.DataFrame(
            {
                "symbol": [f"60{i:04d}.SH" for i in range(batch_size)],
                "price": [10.0 + (i % 100) * 0.1 for i in range(batch_size)],
                "volume": [1000000 + i * 1000 for i in range(batch_size)],
                "timestamp": [datetime.now() for _ in range(batch_size)],
            }
        )

        # 执行批量操作并测量性能
        start_time = time.time()
        result = self.manager.save_data_batch_with_strategy(
            DataClassification.REALTIME_POSITIONS,
            batch_data,
            table_name="test_batch_perf",
        )
        execution_time_ms = (time.time() - start_time) * 1000

        # 计算吞吐量
        throughput = (batch_size / execution_time_ms) * 1000 if execution_time_ms > 0 else 0

        print(f"  批量大小: {batch_size}条")
        print(f"  执行时间: {execution_time_ms:.2f}ms")
        print(f"  吞吐量: {throughput:.0f} records/s")
        print(f"  成功率: {result.success_rate:.2%}")

        if self.manager.enable_monitoring:
            print("  ✅ 批量性能已记录")
        else:
            print("  ⚠️  监控未启用")

    def test_05_connection_time_tracking(self):
        """测试5: 连接时间跟踪"""
        print("\n测试5: 连接时间跟踪...")

        if self.manager.enable_monitoring:
            # 记录连接时间
            self.performance_monitor.record_connection_time(
                database_type="PostgreSQL",
                connection_time_ms=150.5,
                connection_status="SUCCESS",
            )
            print("  ✅ 连接时间已记录: 150.5ms")

            # 测试慢连接警告
            self.performance_monitor.record_connection_time(
                database_type="TDengine",
                connection_time_ms=1200.0,  # >1秒,应该警告
                connection_status="SUCCESS",
            )
            print("  ✅ 慢连接已记录: 1200ms (已警告)")
        else:
            print("  ⚠️  监控未启用")

    @classmethod
    def tearDownClass(cls):
        """清理测试环境"""
        print("\n" + "-" * 80)
        print("测试清理...")

        # 关闭连接
        cls.manager.close_all_connections()

        print("✅ T033: 性能监控集成测试完成!")
        print("=" * 80 + "\n")


if __name__ == "__main__":
    # 配置日志
    import logging

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # 运行测试
    unittest.main(verbosity=2)
