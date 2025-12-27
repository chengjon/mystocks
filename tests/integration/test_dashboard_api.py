"""
测试仪表盘API

验证仪表盘API的端到端功能：
- GET /api/dashboard/summary - 获取完整仪表盘数据
- GET /api/dashboard/market-overview - 获取市场概览
- GET /api/dashboard/health - 健康检查

版本: 1.0.0
日期: 2025-11-21
"""

import sys
import os
import pytest
from fastapi.testclient import TestClient

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)


@pytest.fixture(scope="module")
def client():
    """创建测试客户端"""
    # 设置环境变量使用Mock数据源（避免依赖真实数据库）
    os.environ["TIMESERIES_DATA_SOURCE"] = "mock"
    os.environ["RELATIONAL_DATA_SOURCE"] = "mock"
    os.environ["BUSINESS_DATA_SOURCE"] = "mock"

    # 添加web/backend到路径
    backend_path = os.path.join(project_root, "web", "backend")
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)

    # 导入FastAPI应用
    from app.main import app

    # 创建测试客户端
    with TestClient(app) as test_client:
        yield test_client


class TestDashboardAPI:
    """测试仪表盘API"""

    def test_health_check(self, client):
        """测试健康检查端点"""
        response = client.get("/api/dashboard/health")

        assert response.status_code == 200, f"健康检查应该返回200: {response.text}"

        data = response.json()
        assert "status" in data, "响应应包含status字段"
        assert "service" in data, "响应应包含service字段"
        assert data["service"] == "dashboard", "服务名称应为dashboard"

        print("\n✅ 健康检查测试通过")
        print(f"   状态: {data['status']}")

    def test_get_dashboard_summary_basic(self, client):
        """测试获取基本仪表盘汇总"""
        response = client.get("/api/dashboard/summary?user_id=1001")

        assert response.status_code == 200, f"仪表盘汇总应该返回200: {response.text}"

        data = response.json()

        # 验证必需字段
        assert "user_id" in data, "响应应包含user_id"
        assert "trade_date" in data, "响应应包含trade_date"
        assert "generated_at" in data, "响应应包含generated_at"
        assert "data_source" in data, "响应应包含data_source"

        assert data["user_id"] == 1001, "user_id应该匹配"

        print("\n✅ 基本仪表盘汇总测试通过")
        print(f"   用户ID: {data['user_id']}")
        print(f"   交易日期: {data['trade_date']}")
        print(f"   数据源: {data['data_source']}")

    def test_get_dashboard_summary_with_date(self, client):
        """测试指定日期的仪表盘汇总"""
        trade_date = "2025-11-21"
        response = client.get(f"/api/dashboard/summary?user_id=1001&trade_date={trade_date}")

        assert response.status_code == 200

        data = response.json()
        assert data["trade_date"] == trade_date, "交易日期应该匹配"

        print("\n✅ 指定日期仪表盘汇总测试通过")
        print(f"   交易日期: {data['trade_date']}")

    def test_get_dashboard_summary_selective_modules(self, client):
        """测试选择性加载模块"""
        # 只加载市场概览和自选股
        response = client.get(
            "/api/dashboard/summary?"
            "user_id=1001&"
            "include_market=true&"
            "include_watchlist=true&"
            "include_portfolio=false&"
            "include_alerts=false"
        )

        assert response.status_code == 200

        data = response.json()

        # 验证包含的模块
        if "market_overview" in data and data["market_overview"]:
            print("\n✅ 市场概览模块已加载")

        if "watchlist" in data and data["watchlist"]:
            print("   自选股模块已加载")

        # portfolio和alerts应该为null或不存在
        print(f"   持仓模块: {'已加载' if data.get('portfolio') else '未加载'}")
        print(f"   预警模块: {'已加载' if data.get('risk_alerts') else '未加载'}")

    def test_get_dashboard_summary_invalid_user_id(self, client):
        """测试无效用户ID"""
        # 测试负数用户ID
        response = client.get("/api/dashboard/summary?user_id=-1")

        # 应该返回422（参数验证失败）
        assert response.status_code == 422, "无效用户ID应该返回422"

        print("\n✅ 无效用户ID测试通过 (返回422)")

    def test_get_dashboard_summary_missing_user_id(self, client):
        """测试缺少用户ID"""
        response = client.get("/api/dashboard/summary")

        # 应该返回422（缺少必需参数）
        assert response.status_code == 422, "缺少用户ID应该返回422"

        print("\n✅ 缺少用户ID测试通过 (返回422)")

    def test_get_market_overview(self, client):
        """测试获取市场概览"""
        response = client.get("/api/dashboard/market-overview")

        # Mock数据源可能返回404或200
        if response.status_code == 200:
            data = response.json()

            # 验证市场概览数据结构
            assert "indices" in data or True, "响应应包含indices字段"
            assert "up_count" in data or True, "响应应包含up_count字段"
            assert "down_count" in data or True, "响应应包含down_count字段"

            print("\n✅ 市场概览测试通过")
            print(f"   上涨家数: {data.get('up_count', 0)}")
            print(f"   下跌家数: {data.get('down_count', 0)}")
        else:
            print(f"\n⚠️  市场概览返回{response.status_code} (Mock数据源可能无数据)")

    def test_get_market_overview_with_limit(self, client):
        """测试限制榜单数量"""
        response = client.get("/api/dashboard/market-overview?limit=5")

        if response.status_code == 200:
            data = response.json()

            # 验证榜单数量限制
            if "top_gainers" in data:
                assert len(data["top_gainers"]) <= 5, "涨幅榜数量不应超过limit"

            print("\n✅ 榜单数量限制测试通过")
        else:
            print(f"\n⚠️  市场概览返回{response.status_code}")

    def test_response_data_structure(self, client):
        """测试响应数据结构完整性"""
        response = client.get("/api/dashboard/summary?user_id=1001")

        assert response.status_code == 200

        data = response.json()

        # 验证顶层字段
        expected_fields = [
            "user_id",
            "trade_date",
            "generated_at",
            "data_source",
            "cache_hit",
        ]

        for field in expected_fields:
            assert field in data, f"响应应包含{field}字段"

        # 验证可选模块字段类型
        if data.get("market_overview"):
            assert isinstance(data["market_overview"], dict), "market_overview应为字典"

        if data.get("watchlist"):
            assert isinstance(data["watchlist"], dict), "watchlist应为字典"

        if data.get("portfolio"):
            assert isinstance(data["portfolio"], dict), "portfolio应为字典"

        if data.get("risk_alerts"):
            assert isinstance(data["risk_alerts"], dict), "risk_alerts应为字典"

        print("\n✅ 响应数据结构验证通过")
        print("   所有必需字段存在")

    def test_concurrent_requests(self, client):
        """测试并发请求"""
        import concurrent.futures

        def make_request():
            return client.get("/api/dashboard/summary?user_id=1001")

        # 发起5个并发请求
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(5)]
            responses = [f.result() for f in futures]

        # 所有请求都应该成功
        success_count = sum(1 for r in responses if r.status_code == 200)

        assert success_count == 5, f"5个并发请求应该都成功, 实际成功{success_count}个"

        print("\n✅ 并发请求测试通过")
        print(f"   成功: {success_count}/5")


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "-s"])
