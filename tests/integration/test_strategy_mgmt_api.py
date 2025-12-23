"""
测试策略管理API (Phase 4 Day 2)

验证策略管理API的端到端功能:
- POST /api/strategy-mgmt/strategies - 创建策略
- GET /api/strategy-mgmt/strategies - 获取策略列表
- GET /api/strategy-mgmt/strategies/{id} - 获取策略详情
- PUT /api/strategy-mgmt/strategies/{id} - 更新策略
- DELETE /api/strategy-mgmt/strategies/{id} - 删除策略
- POST /api/strategy-mgmt/backtest/execute - 执行回测
- GET /api/strategy-mgmt/backtest/results/{id} - 获取回测结果
- GET /api/strategy-mgmt/backtest/results - 获取回测列表
- GET /api/strategy-mgmt/health - 健康检查

版本: 1.0.0
日期: 2025-11-21
"""

import sys
import os
import pytest
from fastapi.testclient import TestClient

# 添加项目根目录到Python路径
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
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


class TestStrategyManagementAPI:
    """测试策略管理API"""

    def test_health_check(self, client):
        """测试健康检查端点"""
        response = client.get("/api/strategy-mgmt/health")

        assert response.status_code == 200, f"健康检查应该返回200: {response.text}"

        data = response.json()
        assert "status" in data, "响应应包含status字段"
        assert "service" in data, "响应应包含service字段"
        assert data["service"] == "strategy-mgmt", "服务名称应为strategy-mgmt"

        print("\n✅ 健康检查测试通过")
        print(f"   状态: {data['status']}")
        print(f"   策略数: {data.get('strategies_count', 0)}")
        print(f"   回测数: {data.get('backtests_count', 0)}")

    def test_create_strategy(self, client):
        """测试创建策略"""
        strategy_data = {
            "user_id": 1001,
            "strategy_name": "双均线策略",
            "strategy_type": "momentum",
            "description": "基于5日和20日均线的金叉死叉策略",
            "parameters": [
                {
                    "name": "short_period",
                    "value": 5,
                    "description": "短期均线周期",
                    "data_type": "int",
                },
                {
                    "name": "long_period",
                    "value": 20,
                    "description": "长期均线周期",
                    "data_type": "int",
                },
            ],
            "max_position_size": 0.2,
            "stop_loss_percent": 5.0,
            "take_profit_percent": 10.0,
            "tags": ["均线", "趋势跟踪"],
        }

        response = client.post("/api/strategy-mgmt/strategies", json=strategy_data)

        assert response.status_code == 201, f"创建策略应该返回201: {response.text}"

        data = response.json()

        # 验证必需字段
        assert "strategy_id" in data, "响应应包含strategy_id"
        assert "user_id" in data, "响应应包含user_id"
        assert "strategy_name" in data, "响应应包含strategy_name"
        assert "status" in data, "响应应包含status"
        assert "created_at" in data, "响应应包含created_at"

        assert data["user_id"] == 1001, "user_id应该匹配"
        assert data["strategy_name"] == "双均线策略", "strategy_name应该匹配"
        assert data["status"] == "draft", "新策略状态应为draft"

        print("\n✅ 创建策略测试通过")
        print(f"   策略ID: {data['strategy_id']}")
        print(f"   策略名称: {data['strategy_name']}")
        print(f"   状态: {data['status']}")

    def test_list_strategies(self, client):
        """测试获取策略列表"""
        # 先创建一个策略
        strategy_data = {
            "user_id": 1001,
            "strategy_name": "测试策略",
            "strategy_type": "custom",
            "parameters": [],
        }
        client.post("/api/strategy-mgmt/strategies", json=strategy_data)

        # 获取策略列表
        response = client.get("/api/strategy-mgmt/strategies?user_id=1001")

        assert response.status_code == 200, f"获取策略列表应该返回200: {response.text}"

        data = response.json()

        assert "total_count" in data, "响应应包含total_count"
        assert "strategies" in data, "响应应包含strategies"
        assert "page" in data, "响应应包含page"
        assert "page_size" in data, "响应应包含page_size"

        assert data["total_count"] >= 1, "至少应有1个策略"
        assert len(data["strategies"]) >= 1, "策略列表不应为空"

        print("\n✅ 获取策略列表测试通过")
        print(f"   总数: {data['total_count']}")
        print(f"   当前页策略数: {len(data['strategies'])}")

    def test_get_strategy_detail(self, client):
        """测试获取策略详情"""
        # 先创建一个策略
        strategy_data = {
            "user_id": 1001,
            "strategy_name": "详情测试策略",
            "strategy_type": "breakout",
            "parameters": [],
        }
        create_response = client.post(
            "/api/strategy-mgmt/strategies", json=strategy_data
        )
        strategy_id = create_response.json()["strategy_id"]

        # 获取策略详情
        response = client.get(f"/api/strategy-mgmt/strategies/{strategy_id}")

        assert response.status_code == 200, f"获取策略详情应该返回200: {response.text}"

        data = response.json()

        assert data["strategy_id"] == strategy_id, "strategy_id应该匹配"
        assert data["strategy_name"] == "详情测试策略", "strategy_name应该匹配"

        print("\n✅ 获取策略详情测试通过")
        print(f"   策略ID: {data['strategy_id']}")
        print(f"   策略名称: {data['strategy_name']}")

    def test_update_strategy(self, client):
        """测试更新策略"""
        # 先创建一个策略
        strategy_data = {
            "user_id": 1001,
            "strategy_name": "更新前的策略",
            "strategy_type": "grid",
            "parameters": [],
        }
        create_response = client.post(
            "/api/strategy-mgmt/strategies", json=strategy_data
        )
        strategy_id = create_response.json()["strategy_id"]

        # 更新策略
        update_data = {
            "strategy_name": "更新后的策略",
            "description": "这是更新后的描述",
            "status": "active",
        }
        response = client.put(
            f"/api/strategy-mgmt/strategies/{strategy_id}", json=update_data
        )

        assert response.status_code == 200, f"更新策略应该返回200: {response.text}"

        data = response.json()

        assert data["strategy_name"] == "更新后的策略", "策略名称应该已更新"
        assert data["description"] == "这是更新后的描述", "描述应该已更新"
        assert data["status"] == "active", "状态应该已更新"

        print("\n✅ 更新策略测试通过")
        print(f"   新策略名称: {data['strategy_name']}")
        print(f"   新状态: {data['status']}")

    def test_delete_strategy(self, client):
        """测试删除策略"""
        # 先创建一个策略
        strategy_data = {
            "user_id": 1001,
            "strategy_name": "待删除策略",
            "strategy_type": "custom",
            "parameters": [],
        }
        create_response = client.post(
            "/api/strategy-mgmt/strategies", json=strategy_data
        )
        strategy_id = create_response.json()["strategy_id"]

        # 删除策略
        response = client.delete(f"/api/strategy-mgmt/strategies/{strategy_id}")

        assert (
            response.status_code == 204
        ), f"删除策略应该返回204: {response.status_code}"

        # 验证策略已被删除
        get_response = client.get(f"/api/strategy-mgmt/strategies/{strategy_id}")
        assert get_response.status_code == 404, "删除后的策略不应存在"

        print("\n✅ 删除策略测试通过")
        print(f"   删除的策略ID: {strategy_id}")

    def test_create_strategy_validation(self, client):
        """测试创建策略的参数验证"""
        # 测试无效的user_id
        invalid_data = {
            "user_id": -1,  # 无效的user_id
            "strategy_name": "测试",
            "strategy_type": "custom",
            "parameters": [],
        }
        response = client.post("/api/strategy-mgmt/strategies", json=invalid_data)
        assert response.status_code == 422, "无效user_id应该返回422"

        # 测试缺少必需字段
        incomplete_data = {
            "user_id": 1001
            # 缺少strategy_name和strategy_type
        }
        response = client.post("/api/strategy-mgmt/strategies", json=incomplete_data)
        assert response.status_code == 422, "缺少必需字段应该返回422"

        print("\n✅ 策略参数验证测试通过")

    def test_execute_backtest(self, client):
        """测试执行回测"""
        # 先创建一个策略
        strategy_data = {
            "user_id": 1001,
            "strategy_name": "回测策略",
            "strategy_type": "momentum",
            "parameters": [],
        }
        create_response = client.post(
            "/api/strategy-mgmt/strategies", json=strategy_data
        )
        strategy_id = create_response.json()["strategy_id"]

        # 执行回测
        backtest_data = {
            "strategy_id": strategy_id,
            "user_id": 1001,
            "symbols": ["000001.SZ", "600000.SH"],
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "initial_capital": 100000.0,
            "commission_rate": 0.0003,
            "slippage_rate": 0.001,
            "benchmark": "000300.SH",
            "include_analysis": True,
        }
        response = client.post(
            "/api/strategy-mgmt/backtest/execute", json=backtest_data
        )

        assert response.status_code == 202, f"执行回测应该返回202: {response.text}"

        data = response.json()

        assert "backtest_id" in data, "响应应包含backtest_id"
        assert "strategy_id" in data, "响应应包含strategy_id"
        assert "status" in data, "响应应包含status"
        assert "performance" in data, "响应应包含performance"

        assert data["strategy_id"] == strategy_id, "strategy_id应该匹配"
        assert data["status"] == "pending", "初始状态应为pending"

        print("\n✅ 执行回测测试通过")
        print(f"   回测ID: {data['backtest_id']}")
        print(f"   策略ID: {data['strategy_id']}")
        print(f"   状态: {data['status']}")

    def test_get_backtest_result(self, client):
        """测试获取回测结果"""
        # 先创建策略并执行回测
        strategy_data = {
            "user_id": 1001,
            "strategy_name": "回测结果测试策略",
            "strategy_type": "momentum",
            "parameters": [],
        }
        create_response = client.post(
            "/api/strategy-mgmt/strategies", json=strategy_data
        )
        strategy_id = create_response.json()["strategy_id"]

        backtest_data = {
            "strategy_id": strategy_id,
            "user_id": 1001,
            "symbols": ["000001.SZ"],
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "initial_capital": 100000.0,
        }
        backtest_response = client.post(
            "/api/strategy-mgmt/backtest/execute", json=backtest_data
        )
        backtest_id = backtest_response.json()["backtest_id"]

        # 获取回测结果
        response = client.get(f"/api/strategy-mgmt/backtest/results/{backtest_id}")

        assert response.status_code == 200, f"获取回测结果应该返回200: {response.text}"

        data = response.json()

        assert data["backtest_id"] == backtest_id, "backtest_id应该匹配"
        assert "performance" in data, "响应应包含performance"
        assert "equity_curve" in data, "响应应包含equity_curve"
        assert "trades" in data, "响应应包含trades"

        print("\n✅ 获取回测结果测试通过")
        print(f"   回测ID: {data['backtest_id']}")
        print(f"   总收益率: {data['performance']['total_return']}%")

    def test_list_backtests(self, client):
        """测试获取回测列表"""
        # 先创建策略并执行回测
        strategy_data = {
            "user_id": 1001,
            "strategy_name": "回测列表测试策略",
            "strategy_type": "momentum",
            "parameters": [],
        }
        create_response = client.post(
            "/api/strategy-mgmt/strategies", json=strategy_data
        )
        strategy_id = create_response.json()["strategy_id"]

        backtest_data = {
            "strategy_id": strategy_id,
            "user_id": 1001,
            "symbols": ["000001.SZ"],
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "initial_capital": 100000.0,
        }
        client.post("/api/strategy-mgmt/backtest/execute", json=backtest_data)

        # 获取回测列表
        response = client.get("/api/strategy-mgmt/backtest/results?user_id=1001")

        assert response.status_code == 200, f"获取回测列表应该返回200: {response.text}"

        data = response.json()

        assert "total_count" in data, "响应应包含total_count"
        assert "backtests" in data, "响应应包含backtests"
        assert "page" in data, "响应应包含page"
        assert "page_size" in data, "响应应包含page_size"

        assert data["total_count"] >= 1, "至少应有1个回测"

        print("\n✅ 获取回测列表测试通过")
        print(f"   总数: {data['total_count']}")
        print(f"   当前页回测数: {len(data['backtests'])}")

    def test_backtest_validation(self, client):
        """测试回测参数验证"""
        # 测试无效的日期范围
        backtest_data = {
            "strategy_id": 999,  # 不存在的策略ID
            "user_id": 1001,
            "symbols": ["000001.SZ"],
            "start_date": "2024-12-31",
            "end_date": "2024-01-01",  # 结束日期早于开始日期
            "initial_capital": 100000.0,
        }
        response = client.post(
            "/api/strategy-mgmt/backtest/execute", json=backtest_data
        )
        assert response.status_code in [400, 404, 422], "无效参数应该返回错误"

        print("\n✅ 回测参数验证测试通过")

    def test_concurrent_strategy_operations(self, client):
        """测试并发策略操作"""
        import concurrent.futures

        def create_strategy(index):
            strategy_data = {
                "user_id": 1001,
                "strategy_name": f"并发测试策略{index}",
                "strategy_type": "custom",
                "parameters": [],
            }
            return client.post("/api/strategy-mgmt/strategies", json=strategy_data)

        # 发起5个并发创建请求
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(create_strategy, i) for i in range(5)]
            responses = [f.result() for f in futures]

        # 所有请求都应该成功
        success_count = sum(1 for r in responses if r.status_code == 201)

        assert (
            success_count == 5
        ), f"5个并发创建请求应该都成功, 实际成功{success_count}个"

        print("\n✅ 并发策略操作测试通过")
        print(f"   成功: {success_count}/5")


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "-s"])
