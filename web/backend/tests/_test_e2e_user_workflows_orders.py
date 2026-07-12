"""端到端用户工作流测试 - 交易、恢复与性能流程
"""

from unittest.mock import Mock, patch

from ._test_e2e_user_workflows_support import client


__all__ = [
    "TestUserWorkflowErrorRecovery",
    "TestUserWorkflowOrderPlacement",
    "TestUserWorkflowPerformance",
    "client",
]


class TestUserWorkflowOrderPlacement:
    """测试工作流3: 下单 → 确认 → 持仓更新"""

    @patch("app.api.auth.get_current_user")
    @patch("app.api.trade.place_order")
    @patch("app.api.trade.get_account_info")
    def test_complete_order_placement_flow(self, mock_account, mock_order, mock_user, client):
        """测试完整的下单流程"""
        mock_user.return_value = Mock(id="test_user_007", username="trader", is_active=True)
        mock_account.return_value = {
            "account_id": "acc_001",
            "cash": 100000.0,
            "market_value": 50000.0,
            "total_asset": 150000.0,
            "buying_power": 100000.0,
        }
        mock_order.return_value = {
            "order_id": "order_20251225_001",
            "status": "submitted",
            "price": 1850.0,
            "quantity": 100,
        }

        account_response = client.get("/api/trade/account")

        assert account_response.status_code == 200
        account_data = account_response.json()
        assert account_data["success"] is True
        assert account_data["data"]["buying_power"] > 0

        order_request = {"symbol": "600519", "side": "buy", "type": "limit", "quantity": 100, "price": 1850.0}
        order_response = client.post("/api/trade/orders", json=order_request)

        assert order_response.status_code in [200, 201]
        order_data = order_response.json()
        assert order_data["success"] is True
        assert "data" in order_data
        assert "order_id" in order_data["data"]

        order_id = order_data["data"]["order_id"]

        confirm_response = client.get(f"/api/trade/orders/{order_id}")

        assert confirm_response.status_code == 200
        confirm_data = confirm_response.json()
        assert confirm_data["success"] is True
        assert confirm_data["data"]["order_id"] == order_id
        assert confirm_data["data"]["status"] in ["submitted", "filled", "pending"]

        positions_response = client.get("/api/trade/positions")

        assert positions_response.status_code == 200
        positions_data = positions_response.json()
        assert positions_data["success"] is True
        assert "data" in positions_data
        assert isinstance(positions_data["data"], list)

        history_response = client.get("/api/trade/orders/history?limit=10")

        assert history_response.status_code == 200
        history_data = history_response.json()
        assert history_data["success"] is True
        assert "data" in history_data
        assert isinstance(history_data["data"], list)

    @patch("app.api.auth.get_current_user")
    def test_order_validation_insufficient_funds(self, mock_user, client):
        """测试资金不足验证"""
        mock_user.return_value = Mock(id="test_user_008", username="poor_trader", is_active=True)

        large_order = {
            "symbol": "600519",
            "side": "buy",
            "type": "limit",
            "quantity": 100000,
            "price": 1850.0,
        }

        response = client.post("/api/trade/orders", json=large_order)

        assert response.status_code in [400, 422]
        data = response.json()
        assert data["success"] is False
        assert "insufficient" in data.get("message", "").lower() or "资金" in data.get("message", "")

    @patch("app.api.auth.get_current_user")
    def test_order_cancellation(self, mock_user, client):
        """测试订单取消"""
        mock_user.return_value = Mock(id="test_user_009", username="trader2", is_active=True)

        order_id = "order_cancel_test_001"
        cancel_response = client.post(f"/api/trade/orders/{order_id}/cancel")

        assert cancel_response.status_code in [200, 404]
        cancel_data = cancel_response.json()
        assert "success" in cancel_data


class TestUserWorkflowErrorRecovery:
    """测试用户工作流错误恢复"""

    @patch("app.api.auth.get_current_user")
    def test_network_timeout_retry(self, mock_user, client):
        """测试网络超时重试机制"""
        mock_user.return_value = Mock(id="test_user_010", username="network_user", is_active=True)

        with patch("app.api.market.get_market_data_service") as mock_service:
            mock_service.side_effect = TimeoutError("Network timeout")

            response = client.get("/api/market/overview")

            assert response.status_code in [500, 504]
            data = response.json()
            assert "success" in data
            assert "code" in data

    @patch("app.api.auth.get_current_user")
    def test_session_expiry_handling(self, mock_user, client):
        """测试会话过期处理"""
        mock_user.side_effect = [Mock(id="test_user_011", username="session_user"), None]

        response1 = client.get("/api/watchlist/my")
        assert response1.status_code in [200, 401]

        response2 = client.get("/api/watchlist/my")
        assert response2.status_code == 401
        data = response2.json()
        assert data["success"] is False
        assert data["code"] == 401


class TestUserWorkflowPerformance:
    """测试用户工作流性能指标"""

    @patch("app.api.auth.get_current_user")
    def test_response_time_tracking(self, mock_user, client):
        """测试响应时间追踪"""
        mock_user.return_value = Mock(id="test_user_012", username="perf_user", is_active=True)

        import time

        endpoints = ["/api/market/overview", "/api/market/health", "/health"]

        for endpoint in endpoints:
            start_time = time.time()
            response = client.get(endpoint)
            response_time = (time.time() - start_time) * 1000

            assert response_time < 2000, f"{endpoint} 响应时间过长: {response_time}ms"

            if "x-process-time" in response.headers:
                header_time = float(response.headers["x-process-time"])
                assert header_time >= 0

            assert response.status_code == 200
            data = response.json()
            assert "success" in data
            assert "timestamp" in data or "request_id" in data
