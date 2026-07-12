"""端到端用户工作流测试 - 策略配置与回测流程
"""

from unittest.mock import Mock, patch

from ._test_e2e_user_workflows_support import client


__all__ = ["TestUserWorkflowStrategyBacktest", "client"]


class TestUserWorkflowStrategyBacktest:
    """测试工作流2: 策略配置 → 回测 → 查看结果"""

    @patch("app.api.auth.get_current_user")
    @patch("app.api.strategy.run_backtest")
    def test_complete_strategy_backtest_flow(self, mock_backtest, mock_user, client):
        """测试完整的策略回测流程"""
        mock_user.return_value = Mock(id="test_user_004", username="quantuser", is_active=True)
        mock_backtest.return_value = {
            "backtest_id": "bt_20251225_001",
            "status": "completed",
            "results": {
                "total_return": 25.5,
                "sharpe_ratio": 1.8,
                "max_drawdown": -12.3,
                "win_rate": 0.65,
                "trades_count": 150,
            },
        }

        strategy_config = {
            "strategy_code": "volume_surge",
            "name": "成交量突破策略",
            "symbols": ["600519", "000858"],
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "parameters": {"volume_threshold": 1.5, "holding_period": 5},
        }

        submit_response = client.post("/api/strategy/backtest", json=strategy_config)

        assert submit_response.status_code in [200, 201, 202]
        submit_data = submit_response.json()
        assert submit_data["success"] is True
        assert "data" in submit_data
        assert "backtest_id" in submit_data["data"]

        backtest_id = submit_data["data"]["backtest_id"]

        status_response = client.get(f"/api/strategy/backtest/{backtest_id}/status")

        assert status_response.status_code == 200
        status_data = status_response.json()
        assert status_data["success"] is True
        assert status_data["data"]["status"] in ["pending", "running", "completed", "failed"]

        results_response = client.get(f"/api/strategy/backtest/{backtest_id}/results")

        assert results_response.status_code == 200
        results_data = results_response.json()
        assert results_data["success"] is True
        assert "data" in results_data

        results = results_data["data"]
        expected_keys = ["total_return", "sharpe_ratio", "max_drawdown", "win_rate"]
        for key in expected_keys:
            assert key in results or key in results.get("performance_metrics", {})

    @patch("app.api.auth.get_current_user")
    def test_strategy_validation_invalid_parameters(self, mock_user, client):
        """测试策略参数验证"""
        mock_user.return_value = Mock(id="test_user_005", username="testuser5", is_active=True)

        invalid_config = {
            "strategy_code": "",
            "symbols": ["INVALID_SYMBOL"],
            "start_date": "2024-13-01",
        }

        response = client.post("/api/strategy/backtest", json=invalid_config)

        assert response.status_code in [400, 422]
        data = response.json()
        assert data["success"] is False
        assert data["code"] in [400, 422]
        assert "message" in data

    @patch("app.api.auth.get_current_user")
    def test_multiple_strategies_comparison(self, mock_user, client):
        """测试多策略对比"""
        mock_user.return_value = Mock(id="test_user_006", username="analyst", is_active=True)

        strategies = [
            {"strategy_code": "volume_surge", "symbols": ["600519"]},
            {"strategy_code": "ma_crossover", "symbols": ["600519"]},
            {"strategy_code": "momentum", "symbols": ["600519"]},
        ]

        backtest_ids = []
        for strategy in strategies:
            response = client.post(
                "/api/strategy/backtest",
                json={**strategy, "start_date": "2024-01-01", "end_date": "2024-12-31"},
            )
            if response.status_code in [200, 201]:
                backtest_ids.append(response.json()["data"].get("backtest_id"))

        if backtest_ids:
            comparison_response = client.post("/api/strategy/compare", json={"backtest_ids": backtest_ids})

            assert comparison_response.status_code == 200
            comparison_data = comparison_response.json()
            assert comparison_data["success"] is True
            assert "data" in comparison_data
