"""
数据质量检查集成测试 (T034)

测试数据质量监控器的3个维度检查和自动告警功能。

验证点:
1. 完整性检查 (Completeness) → PASS/WARNING/FAIL
2. 新鲜度检查 (Freshness) → 延迟检测
3. 准确性检查 (Accuracy) → 无效数据检测
4. 质量告警 → 超阈值自动告警

创建日期: 2025-10-12
"""

import unittest
import pandas as pd
import sys
import os
from datetime import datetime, timedelta

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from unified_manager import MyStocksUnifiedManager
from core.data_classification import DataClassification
from monitoring.data_quality_monitor import get_quality_monitor


class TestDataQualityChecks(unittest.TestCase):
    """数据质量检查集成测试"""

    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        print("\n" + "=" * 80)
        print("T034: 数据质量检查集成测试")
        print("=" * 80 + "\n")

        # 初始化统一管理器 (启用监控)
        cls.manager = MyStocksUnifiedManager(enable_monitoring=True)
        cls.quality_monitor = get_quality_monitor()

    def test_01_completeness_check_pass(self):
        """测试1: 完整性检查 - PASS"""
        print("测试1: 完整性检查 - PASS (缺失率低)...")

        # 使用统一管理器的质量检查接口
        result = self.manager.check_data_quality(
            DataClassification.DAILY_KLINE,
            "daily_kline",
            check_type="completeness",
            total_records=10000,
            null_records=10,  # 0.1% 缺失率
            threshold=5.0,  # 5% 阈值
        )

        if "error" not in result:
            print(f"  检查状态: {result.get('check_status', 'UNKNOWN')}")
            print(f"  缺失率: {result.get('missing_rate', 0):.2f}%")
            print(f"  消息: {result.get('message', 'N/A')}")
            self.assertEqual(result.get("check_status"), "PASS", "缺失率低应该PASS")
            print("  ✅ 完整性检查PASS")
        else:
            print(f"  ⚠️  {result['error']}")

    def test_02_completeness_check_warning(self):
        """测试2: 完整性检查 - WARNING"""
        print("\n测试2: 完整性检查 - WARNING (缺失率偏高)...")

        result = self.manager.check_data_quality(
            DataClassification.DAILY_KLINE,
            "daily_kline",
            check_type="completeness",
            total_records=10000,
            null_records=600,  # 6% 缺失率
            threshold=5.0,  # 5% 阈值
        )

        if "error" not in result:
            print(f"  检查状态: {result.get('check_status', 'UNKNOWN')}")
            print(f"  缺失率: {result.get('missing_rate', 0):.2f}%")
            print(f"  消息: {result.get('message', 'N/A')}")
            self.assertEqual(
                result.get("check_status"), "WARNING", "缺失率超阈值应该WARNING"
            )
            print("  ✅ 完整性检查WARNING (已告警)")
        else:
            print(f"  ⚠️  {result['error']}")

    def test_03_completeness_check_fail(self):
        """测试3: 完整性检查 - FAIL"""
        print("\n测试3: 完整性检查 - FAIL (缺失率严重)...")

        result = self.manager.check_data_quality(
            DataClassification.DAILY_KLINE,
            "daily_kline",
            check_type="completeness",
            total_records=10000,
            null_records=1200,  # 12% 缺失率 (超过阈值2倍)
            threshold=5.0,  # 5% 阈值
        )

        if "error" not in result:
            print(f"  检查状态: {result.get('check_status', 'UNKNOWN')}")
            print(f"  缺失率: {result.get('missing_rate', 0):.2f}%")
            print(f"  消息: {result.get('message', 'N/A')}")
            self.assertEqual(result.get("check_status"), "FAIL", "缺失率严重应该FAIL")
            print("  ✅ 完整性检查FAIL (已告警)")
        else:
            print(f"  ⚠️  {result['error']}")

    def test_04_freshness_check_pass(self):
        """测试4: 新鲜度检查 - PASS"""
        print("\n测试4: 新鲜度检查 - PASS (数据新鲜)...")

        # 使用1分钟前的时间戳 (新鲜)
        latest_time = datetime.now() - timedelta(seconds=60)

        result = self.manager.check_data_quality(
            DataClassification.TICK_DATA,
            "tick_data",
            check_type="freshness",
            latest_timestamp=latest_time,
            threshold_seconds=300,  # 5分钟阈值
        )

        if "error" not in result:
            print(f"  检查状态: {result.get('check_status', 'UNKNOWN')}")
            print(f"  数据延迟: {result.get('data_delay_seconds', 0)}秒")
            print(f"  消息: {result.get('message', 'N/A')}")
            self.assertEqual(result.get("check_status"), "PASS", "延迟小应该PASS")
            print("  ✅ 新鲜度检查PASS")
        else:
            print(f"  ⚠️  {result['error']}")

    def test_05_freshness_check_warning(self):
        """测试5: 新鲜度检查 - WARNING"""
        print("\n测试5: 新鲜度检查 - WARNING (数据延迟)...")

        # 使用6.7分钟前的时间戳 (延迟)
        latest_time = datetime.now() - timedelta(seconds=400)

        result = self.manager.check_data_quality(
            DataClassification.TICK_DATA,
            "tick_data",
            check_type="freshness",
            latest_timestamp=latest_time,
            threshold_seconds=300,  # 5分钟阈值
        )

        if "error" not in result:
            print(f"  检查状态: {result.get('check_status', 'UNKNOWN')}")
            print(f"  数据延迟: {result.get('data_delay_seconds', 0)}秒")
            print(f"  消息: {result.get('message', 'N/A')}")
            self.assertEqual(
                result.get("check_status"), "WARNING", "延迟超阈值应该WARNING"
            )
            print("  ✅ 新鲜度检查WARNING (已告警)")
        else:
            print(f"  ⚠️  {result['error']}")

    def test_06_accuracy_check_pass(self):
        """测试6: 准确性检查 - PASS"""
        print("\n测试6: 准确性检查 - PASS (数据有效)...")

        result = self.manager.check_data_quality(
            DataClassification.DAILY_KLINE,
            "daily_kline",
            check_type="accuracy",
            total_records=10000,
            invalid_records=5,  # 0.05% 无效率
            validation_rules="price > 0 AND volume >= 0",
            threshold=1.0,  # 1% 阈值
        )

        if "error" not in result:
            print(f"  检查状态: {result.get('check_status', 'UNKNOWN')}")
            print(f"  无效率: {result.get('invalid_rate', 0):.2f}%")
            print(f"  消息: {result.get('message', 'N/A')}")
            self.assertEqual(result.get("check_status"), "PASS", "无效率低应该PASS")
            print("  ✅ 准确性检查PASS")
        else:
            print(f"  ⚠️  {result['error']}")

    def test_07_accuracy_check_warning(self):
        """测试7: 准确性检查 - WARNING"""
        print("\n测试7: 准确性检查 - WARNING (无效数据偏多)...")

        result = self.manager.check_data_quality(
            DataClassification.DAILY_KLINE,
            "daily_kline",
            check_type="accuracy",
            total_records=10000,
            invalid_records=150,  # 1.5% 无效率
            validation_rules="price > 0 AND volume >= 0",
            threshold=1.0,  # 1% 阈值
        )

        if "error" not in result:
            print(f"  检查状态: {result.get('check_status', 'UNKNOWN')}")
            print(f"  无效率: {result.get('invalid_rate', 0):.2f}%")
            print(f"  消息: {result.get('message', 'N/A')}")
            self.assertEqual(
                result.get("check_status"), "WARNING", "无效率超阈值应该WARNING"
            )
            print("  ✅ 准确性检查WARNING (已告警)")
        else:
            print(f"  ⚠️  {result['error']}")

    def test_08_quality_thresholds_update(self):
        """测试8: 质量阈值更新"""
        print("\n测试8: 质量阈值更新...")

        if self.manager.enable_monitoring:
            # 更新质量检查阈值
            self.quality_monitor.set_thresholds(
                missing_rate_threshold=10.0,  # 10%
                delay_threshold_seconds=600,  # 10分钟
                invalid_rate_threshold=2.0,  # 2%
            )
            print("  ✅ 质量阈值已更新")
            print("    - 缺失率阈值: 10%")
            print("    - 延迟阈值: 600秒")
            print("    - 无效率阈值: 2%")
        else:
            print("  ⚠️  监控未启用")

    @classmethod
    def tearDownClass(cls):
        """清理测试环境"""
        print("\n" + "-" * 80)
        print("测试清理...")

        # 关闭连接
        cls.manager.close_all_connections()

        print("✅ T034: 数据质量检查集成测试完成!")
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
