"""端到端用户工作流测试 - 真实数据集成校验"""

import pytest

from ._test_e2e_user_workflows_support import RealDataValidationMixin, client


__all__ = ["RealDataValidationMixin", "TestRealDataIntegration", "client"]


class TestRealDataIntegration(RealDataValidationMixin):
    """真实数据集成测试 - 验证完整的数据流"""

    def test_real_data_source_availability(self, client):
        """测试真实数据源可用性"""
        results = self.validate_data_source_availability(client)

        assert results["market_data_available"], "市场数据API不可用"
        assert results["api_contract_valid"], "API契约验证失败"
        self.test_results = results

    def test_real_data_integration_completeness(self, client):
        """测试真实数据集成完整性"""
        results = self.validate_real_data_integration(client)

        assert results["data_pipeline_working"], "数据管道未正常工作"
        assert results["error_handling_working"], "错误处理机制未正常工作"
        assert results["performance_acceptable"], "性能指标不符合要求"

    def test_data_routing_correctness(self, client):
        """测试数据路由正确性"""
        market_response = client.get("/api/market/overview")
        assert market_response.status_code == 200

        strategy_response = client.get("/api/strategy/strategies")
        assert strategy_response.status_code == 200

        auth_response = client.post("/api/auth/login", data={"username": "admin", "password": "admin123"})
        assert auth_response.status_code == 200

        token = auth_response.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        strategies = client.get("/api/strategy/strategies", headers=headers)
        assert strategies.status_code == 200
        strategy_list = strategies.json()["data"]["strategies"]

        if strategy_list:
            strategy_id = strategy_list[0]["id"]
            backtest_data = {
                "strategy_id": strategy_id,
                "symbols": ["600519"],
                "start_date": "2024-01-01",
                "end_date": "2024-01-31",
                "initial_capital": 100000.0,
            }

            backtest_response = client.post("/api/strategy/backtest/run", json=backtest_data, headers=headers)
            assert backtest_response.status_code == 200

    def test_api_contract_compliance(self, client):
        """测试API契约合规性"""
        endpoints_to_test = [
            ("/api/market/overview", "GET", None),
            ("/api/strategy/strategies", "GET", None),
            ("/api/auth/login", "POST", {"username": "admin", "password": "admin123"}),
        ]

        for endpoint, method, data in endpoints_to_test:
            if method == "GET":
                response = client.get(endpoint)
            else:
                response = client.post(endpoint, json=data or {})

            assert response.status_code in [200, 201, 422], f"API {endpoint} 返回异常状态码: {response.status_code}"

            response_data = response.json()
            assert isinstance(response_data, dict), f"API {endpoint} 响应格式错误"

            if "success" in response_data:
                assert isinstance(response_data["success"], bool), f"API {endpoint} success字段类型错误"

            if "data" in response_data:
                assert isinstance(response_data["data"], (dict, list)), f"API {endpoint} data字段类型错误"

    def test_data_mapping_accuracy(self, client):
        """测试数据映射准确性"""
        market_response = client.get("/api/market/overview")
        assert market_response.status_code == 200

        market_data = market_response.json()["data"]
        if "indices" in market_data:
            for index in market_data["indices"]:
                required_fields = ["symbol", "name", "current_price"]
                for field in required_fields:
                    assert field in index, f"市场指数数据缺少必需字段: {field}"

        strategy_response = client.get("/api/strategy/strategies")
        assert strategy_response.status_code == 200

        strategy_data = strategy_response.json()["data"]
        if "strategies" in strategy_data:
            for strategy in strategy_data["strategies"]:
                required_fields = ["id", "name", "type"]
                for field in required_fields:
                    assert field in strategy, f"策略数据缺少必需字段: {field}"

    def test_ui_data_binding_readiness(self, client):
        """测试UI数据绑定就绪状态"""
        market_response = client.get("/api/market/overview")
        assert market_response.status_code == 200
        market_data = market_response.json()["data"]

        if market_data.get("indices"):
            first_index = market_data["indices"][0]
            frontend_fields = ["symbol", "name", "current_price", "change_percent"]
            available_fields = [field for field in frontend_fields if field in first_index]
            assert len(available_fields) >= 2, "市场数据缺少前端需要的字段"

        strategy_response = client.get("/api/strategy/strategies")
        assert strategy_response.status_code == 200
        strategy_data = strategy_response.json()["data"]

        if strategy_data.get("strategies"):
            first_strategy = strategy_data["strategies"][0]
            frontend_fields = ["id", "name", "type", "status"]
            available_fields = [field for field in frontend_fields if field in first_strategy]
            assert len(available_fields) >= 2, "策略数据缺少前端需要的字段"

    @pytest.mark.parametrize(
        "endpoint,expected_status",
        [
            ("/api/market/overview", 200),
            ("/api/strategy/strategies", 200),
            ("/api/system/health", 200),
            ("/api/auth/login", 200),
        ],
    )
    def test_api_endpoints_real_data_availability(self, client, endpoint, expected_status):
        """参数化测试 - 验证关键API端点的真实数据可用性"""
        response = (
            client.get(endpoint)
            if "GET" in endpoint or not endpoint.endswith("/login")
            else client.post(endpoint, data={"username": "admin", "password": "admin123"})
        )

        assert response.status_code == expected_status, (
            f"API端点 {endpoint} 返回状态码 {response.status_code}, 期望 {expected_status}"
        )

        response_data = response.json()
        assert "data" in response_data or response_data.get("success") is not None, f"API端点 {endpoint} 缺少数据字段"
