"""
数据源工厂模式单元测试 (Week 1 Day 1)
验证环境变量驱动的模式切换、Hybrid fallback机制、动态配置热更新
"""

from ._test_data_source_factory_convenience import TestConvenienceFunctions, TestIntegrationScenarios
from ._test_data_source_factory_management import (
    TestDataSourceFactory,
    TestDynamicConfigManager,
    TestEnvironmentVariables,
)
from ._test_data_source_factory_sources import (
    TestDataSourceConfig,
    TestHybridDataSource,
    TestMockDataSource,
    TestRealDataSource,
)

__all__ = [
    "TestConvenienceFunctions",
    "TestDataSourceConfig",
    "TestDataSourceFactory",
    "TestDynamicConfigManager",
    "TestEnvironmentVariables",
    "TestHybridDataSource",
    "TestIntegrationScenarios",
    "TestMockDataSource",
    "TestRealDataSource",
]


if __name__ == "__main__":
    import pytest

    pytest.main([__file__, "-v", "--tb=short"])
