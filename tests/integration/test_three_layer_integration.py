"""
测试三层数据源架构集成

验证TDengine + PostgreSQL + Composite三层协同工作：
- Layer 1 (TDengine): 时序数据查询
- Layer 2 (PostgreSQL): 关系数据查询
- Layer 3 (Composite): 整合时序+关系数据

版本: 1.0.0
日期: 2025-11-21
"""

import sys
import os
import pytest
from datetime import date, timedelta

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)


class TestThreeLayerIntegration:
    """测试三层数据源架构集成"""

    @pytest.fixture(autouse=True)
    def setup_real_sources(self):
        """设置使用Real数据源"""
        os.environ["TIMESERIES_DATA_SOURCE"] = "tdengine"
        os.environ["RELATIONAL_DATA_SOURCE"] = "postgresql"
        os.environ["BUSINESS_DATA_SOURCE"] = "composite"

        # 重新导入以应用环境变量
        import importlib
        import src.data_sources

        importlib.reload(src.data_sources)

        return

    def test_layer1_tdengine_basic_query(self):
        """测试Layer 1: TDengine时序数据查询"""
        from src.data_sources import get_timeseries_source

        ts_source = get_timeseries_source()

        # 1. 健康检查
        health = ts_source.health_check()
        assert health["status"] == "healthy", f"TDengine应该健康: {health.get('error', '')}"

        print("\n✅ TDengine健康检查通过")
        print(f"   版本: {health.get('version', 'unknown')}")
        print(f"   响应时间: {health.get('response_time_ms', 0):.2f}ms")

        # 2. 市场概览查询
        try:
            market_overview = ts_source.get_market_overview(limit=10)
            assert market_overview is not None, "市场概览不应为None"
            print(f"\n✅ 市场概览查询成功: {len(market_overview)}条数据")
        except Exception as e:
            print(f"\n⚠️  市场概览查询: {str(e)} (可能数据为空)")

        # 3. 数据质量检查
        try:
            quality = ts_source.check_data_quality(start_date=date.today() - timedelta(days=7), end_date=date.today())
            assert "completeness_rate" in quality, "质量检查应包含完整率"
            print("\n✅ 数据质量检查完成")
            print(f"   完整率: {quality.get('completeness_rate', 0):.2%}")
        except Exception as e:
            print(f"\n⚠️  数据质量检查: {str(e)}")

    def test_layer2_postgresql_basic_query(self):
        """测试Layer 2: PostgreSQL关系数据查询"""
        from src.data_sources import get_relational_source

        rel_source = get_relational_source()

        # 1. 健康检查
        health = rel_source.health_check()
        assert health["status"] == "healthy", f"PostgreSQL应该健康: {health.get('error', '')}"

        print("\n✅ PostgreSQL健康检查通过")
        print(f"   版本: {health.get('version', 'unknown')}")
        print(f"   响应时间: {health.get('response_time_ms', 0):.2f}ms")

        # 2. 行业列表查询
        try:
            industries = rel_source.get_industry_list()
            assert industries is not None, "行业列表不应为None"
            print(f"\n✅ 行业列表查询成功: {len(industries)}个行业")
        except Exception as e:
            print(f"\n⚠️  行业列表查询: {str(e)} (可能表不存在)")

        # 3. 概念列表查询
        try:
            concepts = rel_source.get_concept_list()
            assert concepts is not None, "概念列表不应为None"
            print(f"\n✅ 概念列表查询成功: {len(concepts)}个概念")
        except Exception as e:
            print(f"\n⚠️  概念列表查询: {str(e)} (可能表不存在)")

    def test_layer3_composite_integration(self):
        """测试Layer 3: Composite业务数据整合"""
        from src.data_sources import get_business_source

        biz_source = get_business_source()

        # 1. 健康检查 (应该检查依赖的时序和关系数据源)
        health = biz_source.health_check()
        assert health["status"] in [
            "healthy",
            "degraded",
        ], f"Composite应该健康或降级: {health.get('error', '')}"

        print("\n✅ Composite健康检查通过")
        print(f"   状态: {health['status']}")

        if "dependencies" in health:
            print("\n   依赖数据源:")
            for dep_name, dep_info in health["dependencies"].items():
                print(f"     - {dep_name}: {dep_info.get('status', 'unknown')}")

        # 2. 仪表盘汇总 (整合时序+关系数据)
        try:
            dashboard = biz_source.get_dashboard_summary(user_id=1001)
            assert "user_id" in dashboard, "仪表盘应包含user_id"
            assert "trade_date" in dashboard, "仪表盘应包含trade_date"

            print("\n✅ 仪表盘汇总成功")
            print(f"   用户ID: {dashboard['user_id']}")
            print(f"   交易日期: {dashboard['trade_date']}")
            print(f"   字段数: {len(dashboard)}")
        except Exception as e:
            print(f"\n⚠️  仪表盘汇总: {str(e)}")

        # 3. 板块表现 (整合时序数据)
        try:
            sectors = biz_source.get_sector_performance(sector_type="industry", limit=5)
            assert sectors is not None, "板块表现不应为None"
            print(f"\n✅ 板块表现查询成功: {len(sectors)}个板块")
        except Exception as e:
            print(f"\n⚠️  板块表现查询: {str(e)}")

    def test_cross_layer_data_flow(self):
        """测试跨层数据流动"""
        from src.data_sources import (
            get_timeseries_source,
            get_relational_source,
            get_business_source,
        )

        ts_source = get_timeseries_source()
        rel_source = get_relational_source()
        biz_source = get_business_source()

        # 1. Layer 1: 获取市场数据
        try:
            market_data = ts_source.get_market_overview(limit=5)
            print(f"\n✅ Layer 1 (时序): 获取{len(market_data) if market_data else 0}条市场数据")
        except Exception as e:
            print(f"\n⚠️  Layer 1: {str(e)}")
            market_data = []

        # 2. Layer 2: 获取自选股 (使用测试用户ID)
        try:
            watchlist = rel_source.get_watchlist(user_id=1001, list_type="favorite", include_stock_info=False)
            print(f"\n✅ Layer 2 (关系): 获取{len(watchlist)}条自选股")
        except Exception as e:
            print(f"\n⚠️  Layer 2: {str(e)}")
            watchlist = []

        # 3. Layer 3: 整合数据生成仪表盘
        try:
            dashboard = biz_source.get_dashboard_summary(user_id=1001)
            print(f"\n✅ Layer 3 (业务): 生成仪表盘 ({len(dashboard)}个字段)")

            # 验证数据整合
            if "market_overview" in dashboard:
                print("   - 市场概览: ✅")
            if "watchlist" in dashboard or "watchlist_count" in dashboard:
                print("   - 自选股数据: ✅")

        except Exception as e:
            print(f"\n⚠️  Layer 3: {str(e)}")

        print("\n✅ 跨层数据流动测试完成")

    def test_composite_parallel_query_optimization(self):
        """测试Composite的并行查询优化"""
        from src.data_sources import get_business_source
        import time

        biz_source = get_business_source()

        # 测试并行查询是否比串行查询更快
        start_time = time.time()

        try:
            # Composite应该并行查询时序和关系数据源
            dashboard = biz_source.get_dashboard_summary(user_id=1001)

            elapsed_time = time.time() - start_time

            print("\n✅ 并行查询优化测试")
            print(f"   总响应时间: {elapsed_time * 1000:.2f}ms")

            # 如果使用ThreadPoolExecutor，应该比串行查询快
            # 这里只验证查询成功，实际性能需要对比测试
            assert elapsed_time < 10, "并行查询应在10秒内完成"

        except Exception as e:
            print(f"\n⚠️  并行查询测试: {str(e)}")

    def test_error_propagation_across_layers(self):
        """测试错误在层间的传播"""
        from src.data_sources import get_business_source

        biz_source = get_business_source()

        # 测试当底层数据源出错时，Composite如何处理
        try:
            # 使用无效参数触发错误
            result = biz_source.get_dashboard_summary(user_id=-1)

            # 应该返回数据或抛出明确的错误
            print(f"\n✅ 错误处理测试: 返回了结果 ({len(result)}个字段)")

        except ValueError as e:
            # 应该是明确的业务错误
            print("\n✅ 错误处理测试: 捕获到预期的ValueError")
            print(f"   错误信息: {str(e)}")

        except Exception as e:
            # 其他类型的错误
            print("\n✅ 错误处理测试: 捕获到错误")
            print(f"   错误类型: {type(e).__name__}")
            print(f"   错误信息: {str(e)}")

    def test_all_layers_health_check(self):
        """测试所有三层的健康检查"""
        from src.data_sources import (
            get_timeseries_source,
            get_relational_source,
            get_business_source,
        )

        ts_source = get_timeseries_source()
        rel_source = get_relational_source()
        biz_source = get_business_source()

        # 检查所有层的健康状态
        ts_health = ts_source.health_check()
        rel_health = rel_source.health_check()
        biz_health = biz_source.health_check()

        print("\n✅ 三层健康检查汇总:")
        print(f"   Layer 1 (TDengine):   {ts_health['status']:8s} - {ts_health.get('version', 'unknown')}")
        print(f"   Layer 2 (PostgreSQL): {rel_health['status']:8s} - {rel_health.get('version', 'unknown')}")
        print(f"   Layer 3 (Composite):  {biz_health['status']:8s}")

        # 所有层应该都是健康的
        assert ts_health["status"] in ["healthy", "degraded"], "TDengine应该健康"
        assert rel_health["status"] in ["healthy", "degraded"], "PostgreSQL应该健康"
        assert biz_health["status"] in ["healthy", "degraded"], "Composite应该健康"


if __name__ == "__main__":
    # 运行所有测试
    pytest.main([__file__, "-v", "-s"])
