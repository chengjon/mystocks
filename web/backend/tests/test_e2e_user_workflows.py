"""
端到端 (E2E) 用户工作流测试

测试覆盖关键用户场景:
1. 用户登录 → 搜索股票 → 添加到自选
2. 策略配置 → 回测 → 查看结果
3. 下单 → 确认 → 持仓更新

版本: 1.0.0
日期: 2025-12-25
Phase: 4.1 - Comprehensive Testing
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta


@pytest.fixture
def client():
    """提供测试客户端"""
    from app.main import app
    return TestClient(app)


class TestUserWorkflowLoginSearchWatchlist:
    """测试工作流1: 用户登录 → 搜索股票 → 添加到自选"""

    @patch("app.api.auth.get_current_user")
    def test_complete_login_search_watchlist_flow(self, mock_user, client):
        """
        测试完整的登录、搜索、添加自选流程

        步骤:
        1. 用户登录 (获取认证token)
        2. 搜索股票 (600519)
        3. 添加到自选列表
        4. 验证自选列表包含该股票
        """
        # 步骤1: 模拟用户登录
        mock_user.return_value = Mock(
            id="test_user_001",
            username="testuser",
            email="test@example.com",
            is_active=True
        )

        # 登录请求
        login_response = client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "testpass"}
        )

        # 验证登录成功（统一响应格式）
        assert login_response.status_code in [200, 201]
        login_data = login_response.json()
        assert login_data["success"] is True
        assert "data" in login_data
        assert "access_token" in login_data["data"] or "token" in login_data["data"]

        # 步骤2: 搜索股票
        search_response = client.get("/api/market/stocks/search?query=600519")

        # 验证搜索成功
        assert search_response.status_code == 200
        search_data = search_response.json()
        assert search_data["success"] is True
        assert "data" in search_data

        # 步骤3: 添加到自选列表
        watchlist_response = client.post(
            "/api/watchlist/add",
            json={
                "symbol": "600519",
                "name": "贵州茅台",
                "notes": "长期关注"
            },
            headers={"Authorization": f"Bearer {login_data['data'].get('access_token', login_data['data'].get('token', ''))}"}
        )

        # 验证添加成功
        assert watchlist_response.status_code in [200, 201]
        watchlist_data = watchlist_response.json()
        assert watchlist_data["success"] is True

        # 步骤4: 验证自选列表包含该股票
        my_watchlist_response = client.get(
            "/api/watchlist/my",
            headers={"Authorization": f"Bearer {login_data['data'].get('access_token', login_data['data'].get('token', ''))}"}
        )

        assert my_watchlist_response.status_code == 200
        watchlist_data = my_watchlist_response.json()
        assert watchlist_data["success"] is True
        assert "data" in watchlist_data

        # 验证股票在列表中
        symbols = [item.get("symbol") for item in watchlist_data["data"]]
        assert "600519" in symbols


    @patch("app.api.auth.get_current_user")
    def test_search_stock_with_pagination(self, mock_user, client):
        """测试股票搜索分页功能"""
        mock_user.return_value = Mock(
            id="test_user_002",
            username="testuser2",
            is_active=True
        )

        # 第一页
        page1_response = client.get("/api/market/stocks/search?query=600&page=1&size=10")
        assert page1_response.status_code == 200
        page1_data = page1_response.json()
        assert page1_data["success"] is True
        assert "data" in page1_data
        # 检查分页信息
        if "pagination" in page1_data.get("data", {}):
            assert page1_data["data"]["pagination"]["page"] == 1
            assert page1_data["data"]["pagination"]["size"] == 10


    @patch("app.api.auth.get_current_user")
    def test_add_duplicate_stock_to_watchlist(self, mock_user, client):
        """测试添加重复股票到自选列表"""
        mock_user.return_value = Mock(
            id="test_user_003",
            username="testuser3",
            is_active=True
        )

        # 第一次添加
        first_add = client.post(
            "/api/watchlist/add",
            json={"symbol": "000858", "name": "五粮液"}
        )
        assert first_add.status_code in [200, 201]

        # 第二次添加相同股票
        second_add = client.post(
            "/api/watchlist/add",
            json={"symbol": "000858", "name": "五粮液"}
        )

        # 应该返回错误或成功（取决于业务逻辑）
        # 这里验证响应格式统一
        data = second_add.json()
        assert "success" in data
        assert "code" in data
        assert "message" in data


class TestUserWorkflowStrategyBacktest:
    """测试工作流2: 策略配置 → 回测 → 查看结果"""

    @patch("app.api.auth.get_current_user")
    @patch("app.api.strategy.run_backtest")
    def test_complete_strategy_backtest_flow(self, mock_backtest, mock_user, client):
        """
        测试完整的策略回测流程

        步骤:
        1. 配置策略参数
        2. 提交回测请求
        3. 等待回测完成
        4. 查看回测结果
        5. 分析性能指标
        """
        mock_user.return_value = Mock(
            id="test_user_004",
            username="quantuser",
            is_active=True
        )

        # Mock回测结果
        mock_backtest.return_value = {
            "backtest_id": "bt_20251225_001",
            "status": "completed",
            "results": {
                "total_return": 25.5,
                "sharpe_ratio": 1.8,
                "max_drawdown": -12.3,
                "win_rate": 0.65,
                "trades_count": 150
            }
        }

        # 步骤1-2: 配置并提交策略
        strategy_config = {
            "strategy_code": "volume_surge",
            "name": "成交量突破策略",
            "symbols": ["600519", "000858"],
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "parameters": {
                "volume_threshold": 1.5,
                "holding_period": 5
            }
        }

        submit_response = client.post(
            "/api/strategy/backtest",
            json=strategy_config
        )

        # 验证提交成功
        assert submit_response.status_code in [200, 201, 202]  # 202=Accepted
        submit_data = submit_response.json()
        assert submit_data["success"] is True
        assert "data" in submit_data
        assert "backtest_id" in submit_data["data"]

        backtest_id = submit_data["data"]["backtest_id"]

        # 步骤3: 查询回测状态
        status_response = client.get(f"/api/strategy/backtest/{backtest_id}/status")

        assert status_response.status_code == 200
        status_data = status_response.json()
        assert status_data["success"] is True
        assert status_data["data"]["status"] in ["pending", "running", "completed", "failed"]

        # 步骤4-5: 获取回测结果
        results_response = client.get(f"/api/strategy/backtest/{backtest_id}/results")

        assert results_response.status_code == 200
        results_data = results_response.json()
        assert results_data["success"] is True
        assert "data" in results_data

        # 验证关键指标存在
        results = results_data["data"]
        expected_keys = ["total_return", "sharpe_ratio", "max_drawdown", "win_rate"]
        for key in expected_keys:
            assert key in results or key in results.get("performance_metrics", {})


    @patch("app.api.auth.get_current_user")
    def test_strategy_validation_invalid_parameters(self, mock_user, client):
        """测试策略参数验证"""
        mock_user.return_value = Mock(
            id="test_user_005",
            username="testuser5",
            is_active=True
        )

        # 提交无效参数
        invalid_config = {
            "strategy_code": "",  # 空代码
            "symbols": ["INVALID_SYMBOL"],  # 无效股票代码
            "start_date": "2024-13-01",  # 无效日期
        }

        response = client.post(
            "/api/strategy/backtest",
            json=invalid_config
        )

        # 应该返回验证错误
        assert response.status_code in [400, 422]
        data = response.json()
        assert data["success"] is False
        assert data["code"] in [400, 422]
        assert "message" in data


    @patch("app.api.auth.get_current_user")
    def test_multiple_strategies_comparison(self, mock_user, client):
        """测试多策略对比"""
        mock_user.return_value = Mock(
            id="test_user_006",
            username="analyst",
            is_active=True
        )

        # 提交多个策略
        strategies = [
            {"strategy_code": "volume_surge", "symbols": ["600519"]},
            {"strategy_code": "ma_crossover", "symbols": ["600519"]},
            {"strategy_code": "momentum", "symbols": ["600519"]},
        ]

        backtest_ids = []
        for strategy in strategies:
            response = client.post(
                "/api/strategy/backtest",
                json={**strategy, "start_date": "2024-01-01", "end_date": "2024-12-31"}
            )
            if response.status_code in [200, 201]:
                backtest_ids.append(response.json()["data"].get("backtest_id"))

        # 对比结果（如果有成功提交的策略）
        if backtest_ids:
            comparison_response = client.post(
                "/api/strategy/compare",
                json={"backtest_ids": backtest_ids}
            )

            # 验证对比结果
            assert comparison_response.status_code == 200
            comparison_data = comparison_response.json()
            assert comparison_data["success"] is True
            assert "data" in comparison_data


class TestUserWorkflowOrderPlacement:
    """测试工作流3: 下单 → 确认 → 持仓更新"""

    @patch("app.api.auth.get_current_user")
    @patch("app.api.trade.place_order")
    @patch("app.api.trade.get_account_info")
    def test_complete_order_placement_flow(self, mock_account, mock_order, mock_user, client):
        """
        测试完整的下单流程

        步骤:
        1. 查询账户信息
        2. 下单
        3. 订单确认
        4. 验证持仓更新
        5. 查询交易历史
        """
        mock_user.return_value = Mock(
            id="test_user_007",
            username="trader",
            is_active=True
        )

        # Mock账户信息
        mock_account.return_value = {
            "account_id": "acc_001",
            "cash": 100000.0,
            "market_value": 50000.0,
            "total_asset": 150000.0,
            "buying_power": 100000.0
        }

        # Mock下单响应
        mock_order.return_value = {
            "order_id": "order_20251225_001",
            "status": "submitted",
            "price": 1850.0,
            "quantity": 100
        }

        # 步骤1: 查询账户信息
        account_response = client.get("/api/trade/account")

        assert account_response.status_code == 200
        account_data = account_response.json()
        assert account_data["success"] is True
        assert account_data["data"]["buying_power"] > 0

        # 步骤2: 下单
        order_request = {
            "symbol": "600519",
            "side": "buy",
            "type": "limit",
            "quantity": 100,
            "price": 1850.0
        }

        order_response = client.post(
            "/api/trade/orders",
            json=order_request
        )

        # 验证下单成功
        assert order_response.status_code in [200, 201]
        order_data = order_response.json()
        assert order_data["success"] is True
        assert "data" in order_data
        assert "order_id" in order_data["data"]

        order_id = order_data["data"]["order_id"]

        # 步骤3: 订单确认
        confirm_response = client.get(f"/api/trade/orders/{order_id}")

        assert confirm_response.status_code == 200
        confirm_data = confirm_response.json()
        assert confirm_data["success"] is True
        assert confirm_data["data"]["order_id"] == order_id
        assert confirm_data["data"]["status"] in ["submitted", "filled", "pending"]

        # 步骤4: 验证持仓更新
        positions_response = client.get("/api/trade/positions")

        assert positions_response.status_code == 200
        positions_data = positions_response.json()
        assert positions_data["success"] is True
        assert "data" in positions_data

        # 验证持仓包含新买入的股票（如果订单已成交）
        positions = positions_data["data"]
        symbol_positions = [p for p in positions if p.get("symbol") == "600519"]
        # 注意：订单可能还未成交，所以这里只验证格式
        assert isinstance(positions, list)

        # 步骤5: 查询交易历史
        history_response = client.get("/api/trade/orders/history?limit=10")

        assert history_response.status_code == 200
        history_data = history_response.json()
        assert history_data["success"] is True
        assert "data" in history_data
        assert isinstance(history_data["data"], list)


    @patch("app.api.auth.get_current_user")
    def test_order_validation_insufficient_funds(self, mock_user, client):
        """测试资金不足验证"""
        mock_user.return_value = Mock(
            id="test_user_008",
            username="poor_trader",
            is_active=True
        )

        # 尝试下单超过购买力
        large_order = {
            "symbol": "600519",
            "side": "buy",
            "type": "limit",
            "quantity": 100000,  # 超大数量
            "price": 1850.0
        }

        response = client.post("/api/trade/orders", json=large_order)

        # 应该返回验证错误
        assert response.status_code in [400, 422]
        data = response.json()
        assert data["success"] is False
        assert "insufficient" in data.get("message", "").lower() or "资金" in data.get("message", "")


    @patch("app.api.auth.get_current_user")
    def test_order_cancellation(self, mock_user, client):
        """测试订单取消"""
        mock_user.return_value = Mock(
            id="test_user_009",
            username="trader2",
            is_active=True
        )

        # 假设已经有一个订单
        order_id = "order_cancel_test_001"

        # 取消订单
        cancel_response = client.post(f"/api/trade/orders/{order_id}/cancel")

        # 验证取消结果
        assert cancel_response.status_code in [200, 404]  # 404=订单不存在
        cancel_data = cancel_response.json()
        assert "success" in cancel_data


class TestUserWorkflowErrorRecovery:
    """测试用户工作流错误恢复"""

    @patch("app.api.auth.get_current_user")
    def test_network_timeout_retry(self, mock_user, client):
        """测试网络超时重试机制"""
        mock_user.return_value = Mock(
            id="test_user_010",
            username="network_user",
            is_active=True
        )

        # 模拟网络超时场景
        # 实际E2E测试可能需要使用不稳定网络模拟器
        # 这里验证错误响应格式
        with patch("app.api.market.get_market_data_service") as mock_service:
            mock_service.side_effect = TimeoutError("Network timeout")

            response = client.get("/api/market/overview")

            # 应该返回超时错误
            assert response.status_code in [500, 504]
            data = response.json()
            assert "success" in data
            assert "code" in data


    @patch("app.api.auth.get_current_user")
    def test_session_expiry_handling(self, mock_user, client):
        """测试会话过期处理"""
        # 第一次调用返回用户，第二次调用模拟会话过期
        mock_user.side_effect = [
            Mock(id="test_user_011", username="session_user"),
            None  # 模拟会话过期
        ]

        # 第一次请求成功
        response1 = client.get("/api/watchlist/my")
        assert response1.status_code in [200, 401]

        # 第二次请求应该返回401
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
        mock_user.return_value = Mock(
            id="test_user_012",
            username="perf_user",
            is_active=True
        )

        import time

        # 测试多个端点的响应时间
        endpoints = [
            "/api/market/overview",
            "/api/market/health",
            "/health"
        ]

        for endpoint in endpoints:
            start_time = time.time()
            response = client.get(endpoint)
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # 毫秒

            # 验证响应时间合理（< 2秒）
            assert response_time < 2000, f"{endpoint} 响应时间过长: {response_time}ms"

            # 验证响应头包含处理时间
            if "x-process-time" in response.headers:
                header_time = float(response.headers["x-process-time"])
                assert header_time >= 0

            # 验证响应格式
            assert response.status_code == 200
            data = response.json()
            assert "success" in data
            assert "timestamp" in data or "request_id" in data


# Pytest 运行配置
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
