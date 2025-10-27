"""
测试 DataManager 核心路由引擎 - 简化版本

目标:
- 验证 get_target_database() 的路由逻辑
- 验证所有数据分类的正确映射
- 验证 O(1) 性能

创建日期: 2025-10-28
"""

import pytest
import time
import sys
import os
from unittest.mock import Mock, MagicMock

# 添加项目根目录到 sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from core.data_manager import DataManager
from core.data_classification import DataClassification, DatabaseTarget


class TestDataManagerRouting:
    """测试 DataManager 路由逻辑"""

    @pytest.fixture
    def manager(self):
        """创建测试用的 DataManager (禁用监控避免依赖)"""
        return DataManager(enable_monitoring=False)

    def test_tick_data_routes_to_tdengine(self, manager):
        """测试 Tick 数据路由到 TDengine"""
        target = manager.get_target_database(DataClassification.TICK_DATA)
        assert target == DatabaseTarget.TDENGINE

    def test_minute_kline_routes_to_tdengine(self, manager):
        """测试分钟K线路由到 TDengine"""
        target = manager.get_target_database(DataClassification.MINUTE_KLINE)
        assert target == DatabaseTarget.TDENGINE

    def test_daily_kline_routes_to_postgresql(self, manager):
        """测试日线数据路由到 PostgreSQL"""
        target = manager.get_target_database(DataClassification.DAILY_KLINE)
        assert target == DatabaseTarget.POSTGRESQL

    def test_symbols_info_routes_to_postgresql(self, manager):
        """测试股票信息路由到 PostgreSQL"""
        target = manager.get_target_database(DataClassification.SYMBOLS_INFO)
        assert target == DatabaseTarget.POSTGRESQL

    def test_technical_indicators_routes_to_postgresql(self, manager):
        """测试技术指标路由到 PostgreSQL"""
        target = manager.get_target_database(DataClassification.TECHNICAL_INDICATORS)
        assert target == DatabaseTarget.POSTGRESQL

    def test_order_records_routes_to_postgresql(self, manager):
        """测试订单数据路由到 PostgreSQL"""
        target = manager.get_target_database(DataClassification.ORDER_RECORDS)
        assert target == DatabaseTarget.POSTGRESQL


class TestDataManagerRoutingPerformance:
    """性能测试"""

    @pytest.fixture
    def manager(self):
        """创建测试用的 DataManager"""
        return DataManager(enable_monitoring=False)

    def test_o1_routing_performance(self, manager):
        """验证 O(1) 路由性能"""
        # 单次查询应该非常快
        start = time.perf_counter()
        target = manager.get_target_database(DataClassification.TICK_DATA)
        elapsed = time.perf_counter() - start

        # 应该 < 1ms
        assert elapsed < 0.001
        assert target == DatabaseTarget.TDENGINE

    def test_routing_consistency_1000_calls(self, manager):
        """验证 1000 次调用的一致性"""
        results = [
            manager.get_target_database(DataClassification.TICK_DATA)
            for _ in range(1000)
        ]

        # 所有结果应该相同
        unique_results = set(results)
        assert len(unique_results) == 1
        assert unique_results.pop() == DatabaseTarget.TDENGINE


class TestDataManagerAllClassifications:
    """验证所有数据分类的映射"""

    @pytest.fixture
    def manager(self):
        """创建测试用的 DataManager"""
        return DataManager(enable_monitoring=False)

    def test_all_classifications_have_target(self, manager):
        """验证所有数据分类都有路由目标"""
        for classification in DataClassification:
            try:
                target = manager.get_target_database(classification)
                assert target in [DatabaseTarget.TDENGINE, DatabaseTarget.POSTGRESQL]
            except Exception as e:
                pytest.fail(f"分类 {classification} 没有有效的路由目标: {e}")

    def test_high_frequency_data_to_tdengine(self, manager):
        """验证所有高频数据都路由到 TDengine"""
        high_freq_data = [
            DataClassification.TICK_DATA,
            DataClassification.MINUTE_KLINE,
            DataClassification.ORDER_BOOK_DEPTH,
        ]

        for data_type in high_freq_data:
            target = manager.get_target_database(data_type)
            assert target == DatabaseTarget.TDENGINE, f"{data_type} 应路由到 TDengine"

    def test_reference_data_to_postgresql(self, manager):
        """验证所有参考数据都路由到 PostgreSQL"""
        reference_data = [
            DataClassification.SYMBOLS_INFO,
            DataClassification.TRADE_CALENDAR,
            DataClassification.INDUSTRY_CLASS,
        ]

        for data_type in reference_data:
            target = manager.get_target_database(data_type)
            assert (
                target == DatabaseTarget.POSTGRESQL
            ), f"{data_type} 应路由到 PostgreSQL"


class TestDataManagerAdapterManagement:
    """测试适配器注册和管理"""

    @pytest.fixture
    def manager(self):
        """创建测试用的 DataManager"""
        return DataManager(enable_monitoring=False)

    def test_register_adapter(self, manager):
        """测试适配器注册"""
        mock_adapter = Mock()
        manager.register_adapter("test_adapter", mock_adapter)

        # 验证适配器已注册
        registered = manager.get_adapter("test_adapter")
        assert registered == mock_adapter

    def test_unregister_adapter(self, manager):
        """测试适配器注销"""
        mock_adapter = Mock()
        manager.register_adapter("test_adapter", mock_adapter)

        # 注销适配器
        result = manager.unregister_adapter("test_adapter")
        assert result is True

        # 验证适配器已被移除
        registered = manager.get_adapter("test_adapter")
        assert registered is None

    def test_list_adapters(self, manager):
        """测试列出所有适配器"""
        adapters = {
            "adapter1": Mock(),
            "adapter2": Mock(),
            "adapter3": Mock(),
        }

        for name, adapter in adapters.items():
            manager.register_adapter(name, adapter)

        listed = manager.list_adapters()
        assert len(listed) == 3
        assert all(name in listed for name in adapters.keys())


class TestDataManagerErrorHandling:
    """测试错误处理"""

    @pytest.fixture
    def manager(self):
        """创建测试用的 DataManager"""
        return DataManager(enable_monitoring=False)

    def test_invalid_classification_returns_default(self, manager):
        """测试无效分类的默认行为"""
        # get_target_database 可能返回默认值或抛出异常
        # 根据实现，可能需要调整
        try:
            target = manager.get_target_database("INVALID_CLASS")
            # 如果返回，应该是有效的 DatabaseTarget
            assert target in [DatabaseTarget.TDENGINE, DatabaseTarget.POSTGRESQL]
        except (KeyError, AttributeError, TypeError):
            # 这也是有效的行为 - 抛出异常
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
