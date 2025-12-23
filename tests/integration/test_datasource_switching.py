"""
测试Mock ↔ Real数据源切换

验证通过环境变量切换数据源的功能：
- 时序数据源: mock ↔ tdengine
- 关系数据源: mock ↔ postgresql
- 业务数据源: mock ↔ composite

版本: 1.0.0
日期: 2025-11-21
"""

import sys
import os
import pytest

# 添加项目根目录到Python路径
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, project_root)


class TestDataSourceSwitching:
    """测试数据源切换功能"""

    def test_timeseries_source_mock_to_real(self):
        """测试时序数据源从Mock切换到Real"""
        from src.data_sources.mock import MockTimeSeriesDataSource
        from src.data_sources.real import TDengineTimeSeriesDataSource

        # 1. 使用Mock数据源
        os.environ["TIMESERIES_DATA_SOURCE"] = "mock"

        # 重新导入以清除缓存
        import importlib
        import src.data_sources

        importlib.reload(src.data_sources)
        from src.data_sources import get_timeseries_source as get_ts_mock

        mock_source = get_ts_mock()
        assert isinstance(
            mock_source, MockTimeSeriesDataSource
        ), "应该返回MockTimeSeriesDataSource实例"

        # 验证Mock数据源可以正常工作
        mock_health = mock_source.health_check()
        assert mock_health["status"] in [
            "healthy",
            "mock",
        ], "Mock数据源应该返回健康状态"

        # 2. 切换到Real数据源
        os.environ["TIMESERIES_DATA_SOURCE"] = "tdengine"

        # 重新导入
        importlib.reload(src.data_sources)
        from src.data_sources import get_timeseries_source as get_ts_real

        real_source = get_ts_real()
        assert isinstance(
            real_source, TDengineTimeSeriesDataSource
        ), "应该返回TDengineTimeSeriesDataSource实例"

        # 验证Real数据源可以正常工作
        real_health = real_source.health_check()
        assert real_health["status"] in [
            "healthy",
            "degraded",
        ], "Real数据源应该返回健康状态"

        print("\n✅ 时序数据源切换测试通过")
        print(f"   Mock健康状态: {mock_health['status']}")
        print(f"   Real健康状态: {real_health['status']}")

    def test_relational_source_mock_to_real(self):
        """测试关系数据源从Mock切换到Real"""
        from src.data_sources.mock import MockRelationalDataSource
        from src.data_sources.real import PostgreSQLRelationalDataSource

        # 1. 使用Mock数据源
        os.environ["RELATIONAL_DATA_SOURCE"] = "mock"

        # 重新导入
        import importlib
        import src.data_sources

        importlib.reload(src.data_sources)
        from src.data_sources import get_relational_source as get_rel_mock

        mock_source = get_rel_mock()
        assert isinstance(
            mock_source, MockRelationalDataSource
        ), "应该返回MockRelationalDataSource实例"

        mock_health = mock_source.health_check()
        assert mock_health["status"] in ["healthy", "mock"]

        # 2. 切换到Real数据源
        os.environ["RELATIONAL_DATA_SOURCE"] = "postgresql"

        # 重新导入
        importlib.reload(src.data_sources)
        from src.data_sources import get_relational_source as get_rel_real

        real_source = get_rel_real()
        assert isinstance(
            real_source, PostgreSQLRelationalDataSource
        ), "应该返回PostgreSQLRelationalDataSource实例"

        real_health = real_source.health_check()
        assert real_health["status"] in ["healthy", "degraded"]

        print("\n✅ 关系数据源切换测试通过")
        print(f"   Mock健康状态: {mock_health['status']}")
        print(f"   Real健康状态: {real_health['status']}")

    def test_business_source_mock_to_real(self):
        """测试业务数据源从Mock切换到Real"""
        from src.data_sources.mock import MockBusinessDataSource
        from src.data_sources.real import CompositeBusinessDataSource

        # 1. 使用Mock数据源
        os.environ["BUSINESS_DATA_SOURCE"] = "mock"

        # 重新导入
        import importlib
        import src.data_sources

        importlib.reload(src.data_sources)
        from src.data_sources import get_business_source as get_biz_mock

        mock_source = get_biz_mock()
        assert isinstance(
            mock_source, MockBusinessDataSource
        ), "应该返回MockBusinessDataSource实例"

        mock_health = mock_source.health_check()
        assert mock_health["status"] in ["healthy", "mock"]

        # 2. 切换到Real数据源
        os.environ["BUSINESS_DATA_SOURCE"] = "composite"
        os.environ["TIMESERIES_DATA_SOURCE"] = "mock"  # Composite依赖时序数据源
        os.environ["RELATIONAL_DATA_SOURCE"] = "mock"  # Composite依赖关系数据源

        # 重新导入
        importlib.reload(src.data_sources)
        from src.data_sources import get_business_source as get_biz_real

        real_source = get_biz_real()
        assert isinstance(
            real_source, CompositeBusinessDataSource
        ), "应该返回CompositeBusinessDataSource实例"

        real_health = real_source.health_check()
        assert real_health["status"] in ["healthy", "degraded"]

        print("\n✅ 业务数据源切换测试通过")
        print(f"   Mock健康状态: {mock_health['status']}")
        print(f"   Real健康状态: {real_health['status']}")

    def test_all_sources_mock_mode(self):
        """测试所有数据源同时使用Mock模式"""
        # 设置所有数据源为Mock
        os.environ["TIMESERIES_DATA_SOURCE"] = "mock"
        os.environ["RELATIONAL_DATA_SOURCE"] = "mock"
        os.environ["BUSINESS_DATA_SOURCE"] = "mock"

        # 重新导入
        import importlib
        import src.data_sources

        importlib.reload(src.data_sources)

        from src.data_sources import (
            get_timeseries_source,
            get_relational_source,
            get_business_source,
        )
        from src.data_sources.mock import (
            MockTimeSeriesDataSource,
            MockRelationalDataSource,
            MockBusinessDataSource,
        )

        ts_source = get_timeseries_source()
        rel_source = get_relational_source()
        biz_source = get_business_source()

        assert isinstance(ts_source, MockTimeSeriesDataSource)
        assert isinstance(rel_source, MockRelationalDataSource)
        assert isinstance(biz_source, MockBusinessDataSource)

        # 验证所有数据源都正常工作
        assert ts_source.health_check()["status"] in ["healthy", "mock"]
        assert rel_source.health_check()["status"] in ["healthy", "mock"]
        assert biz_source.health_check()["status"] in ["healthy", "mock"]

        print("\n✅ 所有数据源Mock模式测试通过")

    def test_all_sources_real_mode(self):
        """测试所有数据源同时使用Real模式"""
        # 设置所有数据源为Real
        os.environ["TIMESERIES_DATA_SOURCE"] = "tdengine"
        os.environ["RELATIONAL_DATA_SOURCE"] = "postgresql"
        os.environ["BUSINESS_DATA_SOURCE"] = "composite"

        # 重新导入
        import importlib
        import src.data_sources

        importlib.reload(src.data_sources)

        from src.data_sources import (
            get_timeseries_source,
            get_relational_source,
            get_business_source,
        )
        from src.data_sources.real import (
            TDengineTimeSeriesDataSource,
            PostgreSQLRelationalDataSource,
            CompositeBusinessDataSource,
        )

        ts_source = get_timeseries_source()
        rel_source = get_relational_source()
        biz_source = get_business_source()

        assert isinstance(ts_source, TDengineTimeSeriesDataSource)
        assert isinstance(rel_source, PostgreSQLRelationalDataSource)
        assert isinstance(biz_source, CompositeBusinessDataSource)

        # 验证所有数据源都正常工作
        ts_health = ts_source.health_check()
        rel_health = rel_source.health_check()
        biz_health = biz_source.health_check()

        assert ts_health["status"] in ["healthy", "degraded"]
        assert rel_health["status"] in ["healthy", "degraded"]
        assert biz_health["status"] in ["healthy", "degraded"]

        print("\n✅ 所有数据源Real模式测试通过")
        print(f"   TDengine: {ts_health.get('version', 'unknown')}")
        print(f"   PostgreSQL: {rel_health.get('version', 'unknown')}")

    def test_mixed_mode(self):
        """测试混合模式 (部分Mock, 部分Real)"""
        # 设置混合模式
        os.environ["TIMESERIES_DATA_SOURCE"] = "mock"
        os.environ["RELATIONAL_DATA_SOURCE"] = "postgresql"
        os.environ["BUSINESS_DATA_SOURCE"] = "mock"

        # 重新导入
        import importlib
        import src.data_sources

        importlib.reload(src.data_sources)

        from src.data_sources import (
            get_timeseries_source,
            get_relational_source,
            get_business_source,
        )
        from src.data_sources.mock import (
            MockTimeSeriesDataSource,
            MockBusinessDataSource,
        )
        from src.data_sources.real import PostgreSQLRelationalDataSource

        ts_source = get_timeseries_source()
        rel_source = get_relational_source()
        biz_source = get_business_source()

        assert isinstance(ts_source, MockTimeSeriesDataSource)
        assert isinstance(rel_source, PostgreSQLRelationalDataSource)
        assert isinstance(biz_source, MockBusinessDataSource)

        print("\n✅ 混合模式测试通过 (Mock时序 + Real关系 + Mock业务)")


if __name__ == "__main__":
    # 运行所有测试
    pytest.main([__file__, "-v", "-s"])
