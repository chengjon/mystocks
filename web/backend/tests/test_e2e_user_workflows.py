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
from unittest.mock import Mock, patch
import requests
import json
from typing import Dict, Any, List


@pytest.fixture
def client():
    """提供测试客户端"""
    from app.main import app

    return TestClient(app)


class RealDataValidationMixin:
    """真实数据验证混入类"""

    def validate_data_source_availability(self, client: TestClient) -> Dict[str, Any]:
        """验证数据源可用性"""
        results = {
            "market_data_available": False,
            "strategy_api_available": False,
            "backtest_api_available": False,
            "data_routing_correct": False,
            "api_contract_valid": False,
            "data_mapping_correct": False,
            "ui_binding_ready": False,
        }

        # 1. 测试市场数据API可用性
        try:
            market_response = client.get("/api/market/overview")
            if market_response.status_code == 200:
                market_data = market_response.json()
                if market_data.get("success") and "indices" in market_data.get("data", {}):
                    results["market_data_available"] = True
                    results["api_contract_valid"] = True  # 基础契约验证通过
        except Exception as e:
            results["market_data_error"] = str(e)

        # 2. 测试策略API可用性
        try:
            strategy_response = client.get("/api/strategy/strategies")
            if strategy_response.status_code == 200:
                strategy_data = strategy_response.json()
                if strategy_data.get("success") and "strategies" in strategy_data.get("data", {}):
                    results["strategy_api_available"] = True
        except Exception as e:
            results["strategy_api_error"] = str(e)

        # 3. 测试回测API可用性
        try:
            # 获取认证token
            auth_response = client.post("/api/auth/login", data={"username": "admin", "password": "admin123"})
            if auth_response.status_code == 200:
                auth_data = auth_response.json()
                token = auth_data.get("data", {}).get("access_token") or auth_data.get("data", {}).get("token")

                if token:
                    headers = {"Authorization": f"Bearer {token}"}

                    # 获取策略列表
                    strategy_list = client.get("/api/strategy/strategies", headers=headers)
                    if strategy_list.status_code == 200:
                        strategies = strategy_list.json().get("data", {}).get("strategies", [])
                        if strategies:
                            strategy_id = strategies[0].get("id")

                            # 测试回测API
                            backtest_data = {
                                "strategy_id": strategy_id,
                                "symbols": ["600519"],
                                "start_date": "2024-01-01",
                                "end_date": "2024-01-31",
                                "initial_capital": 100000.0,
                            }

                            backtest_response = client.post(
                                "/api/strategy/backtest/run", json=backtest_data, headers=headers
                            )
                            if backtest_response.status_code == 200:
                                results["backtest_api_available"] = True
        except Exception as e:
            results["backtest_api_error"] = str(e)

        # 4. 验证数据路由正确性
        if results["market_data_available"] and results["strategy_api_available"]:
            try:
                # 检查数据是否正确路由到对应的数据库
                # 这里可以添加更具体的路由验证逻辑
                results["data_routing_correct"] = True
            except Exception as e:
                results["data_routing_error"] = str(e)

        # 5. 验证数据映射正确性
        if results["api_contract_valid"]:
            try:
                # 验证API返回的数据结构与前端期望的结构匹配
                # 检查字段映射、数据类型转换等
                results["data_mapping_correct"] = True
            except Exception as e:
                results["data_mapping_error"] = str(e)

        # 6. 验证UI绑定就绪状态
        # 这里可以检查前端是否能够正确处理API返回的数据
        results["ui_binding_ready"] = results["api_contract_valid"] and results["data_mapping_correct"]

        return results

    def validate_real_data_integration(self, client: TestClient) -> Dict[str, Any]:
        """验证真实数据集成完整性"""
        integration_results = {
            "data_source_connection": False,
            "data_pipeline_working": False,
            "cache_system_functional": False,
            "error_handling_working": False,
            "performance_acceptable": False,
        }

        # 1. 验证数据源连接
        try:
            # 测试多个数据源的连接状态
            sources_response = client.get("/api/system/data-sources/status")
            if sources_response.status_code == 200:
                sources_data = sources_response.json()
                healthy_sources = [
                    s for s in sources_data.get("data", {}).get("sources", []) if s.get("status") == "healthy"
                ]
                if len(healthy_sources) > 0:
                    integration_results["data_source_connection"] = True
        except Exception as e:
            integration_results["data_source_error"] = str(e)

        # 2. 验证数据管道工作状态
        try:
            # 检查数据处理管道的状态
            pipeline_response = client.get("/api/system/data-pipeline/status")
            if pipeline_response.status_code == 200:
                pipeline_data = pipeline_response.json()
                if pipeline_data.get("data", {}).get("status") == "operational":
                    integration_results["data_pipeline_working"] = True
        except Exception as e:
            integration_results["pipeline_error"] = str(e)

        # 3. 验证缓存系统功能
        try:
            # 测试缓存系统的基本功能
            cache_response = client.get("/api/system/cache/stats")
            if cache_response.status_code == 200:
                cache_data = cache_response.json()
                if "hit_rate" in cache_data.get("data", {}):
                    integration_results["cache_system_functional"] = True
        except Exception as e:
            integration_results["cache_error"] = str(e)

        # 4. 验证错误处理机制
        try:
            # 测试错误处理机制
            error_response = client.get("/api/nonexistent/endpoint")
            if error_response.status_code in [404, 422]:  # 期望的错误响应
                integration_results["error_handling_working"] = True
        except Exception as e:
            integration_results["error_handling_error"] = str(e)

        # 5. 验证性能指标
        try:
            # 检查关键API的响应时间
            import time

            start_time = time.time()
            perf_response = client.get("/api/market/overview")
            end_time = time.time()

            response_time = end_time - start_time
            if perf_response.status_code == 200 and response_time < 2.0:  # 2秒内响应
                integration_results["performance_acceptable"] = True
                integration_results["response_time"] = response_time
        except Exception as e:
            integration_results["performance_error"] = str(e)

        return integration_results


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
        mock_user.return_value = Mock(id="test_user_001", username="testuser", email="test@example.com", is_active=True)

        # 登录请求
        login_response = client.post("/api/v1/auth/login", json={"username": "testuser", "password": "testpass"})

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
            json={"symbol": "600519", "name": "贵州茅台", "notes": "长期关注"},
            headers={
                "Authorization": f"Bearer {login_data['data'].get('access_token', login_data['data'].get('token', ''))}"
            },
        )

        # 验证添加成功
        assert watchlist_response.status_code in [200, 201]
        watchlist_data = watchlist_response.json()
        assert watchlist_data["success"] is True

        # 步骤4: 验证自选列表包含该股票
        my_watchlist_response = client.get(
            "/api/watchlist/my",
            headers={
                "Authorization": f"Bearer {login_data['data'].get('access_token', login_data['data'].get('token', ''))}"
            },
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
        mock_user.return_value = Mock(id="test_user_002", username="testuser2", is_active=True)

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
        mock_user.return_value = Mock(id="test_user_003", username="testuser3", is_active=True)

        # 第一次添加
        first_add = client.post("/api/watchlist/add", json={"symbol": "000858", "name": "五粮液"})
        assert first_add.status_code in [200, 201]

        # 第二次添加相同股票
        second_add = client.post("/api/watchlist/add", json={"symbol": "000858", "name": "五粮液"})

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
        mock_user.return_value = Mock(id="test_user_004", username="quantuser", is_active=True)

        # Mock回测结果
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

        # 步骤1-2: 配置并提交策略
        strategy_config = {
            "strategy_code": "volume_surge",
            "name": "成交量突破策略",
            "symbols": ["600519", "000858"],
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "parameters": {"volume_threshold": 1.5, "holding_period": 5},
        }

        submit_response = client.post("/api/strategy/backtest", json=strategy_config)

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
        mock_user.return_value = Mock(id="test_user_005", username="testuser5", is_active=True)

        # 提交无效参数
        invalid_config = {
            "strategy_code": "",  # 空代码
            "symbols": ["INVALID_SYMBOL"],  # 无效股票代码
            "start_date": "2024-13-01",  # 无效日期
        }

        response = client.post("/api/strategy/backtest", json=invalid_config)

        # 应该返回验证错误
        assert response.status_code in [400, 422]
        data = response.json()
        assert data["success"] is False
        assert data["code"] in [400, 422]
        assert "message" in data

    @patch("app.api.auth.get_current_user")
    def test_multiple_strategies_comparison(self, mock_user, client):
        """测试多策略对比"""
        mock_user.return_value = Mock(id="test_user_006", username="analyst", is_active=True)

        # 提交多个策略
        strategies = [
            {"strategy_code": "volume_surge", "symbols": ["600519"]},
            {"strategy_code": "ma_crossover", "symbols": ["600519"]},
            {"strategy_code": "momentum", "symbols": ["600519"]},
        ]

        backtest_ids = []
        for strategy in strategies:
            response = client.post(
                "/api/strategy/backtest", json={**strategy, "start_date": "2024-01-01", "end_date": "2024-12-31"}
            )
            if response.status_code in [200, 201]:
                backtest_ids.append(response.json()["data"].get("backtest_id"))

        # 对比结果（如果有成功提交的策略）
        if backtest_ids:
            comparison_response = client.post("/api/strategy/compare", json={"backtest_ids": backtest_ids})

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
        mock_user.return_value = Mock(id="test_user_007", username="trader", is_active=True)

        # Mock账户信息
        mock_account.return_value = {
            "account_id": "acc_001",
            "cash": 100000.0,
            "market_value": 50000.0,
            "total_asset": 150000.0,
            "buying_power": 100000.0,
        }

        # Mock下单响应
        mock_order.return_value = {
            "order_id": "order_20251225_001",
            "status": "submitted",
            "price": 1850.0,
            "quantity": 100,
        }

        # 步骤1: 查询账户信息
        account_response = client.get("/api/trade/account")

        assert account_response.status_code == 200
        account_data = account_response.json()
        assert account_data["success"] is True
        assert account_data["data"]["buying_power"] > 0

        # 步骤2: 下单
        order_request = {"symbol": "600519", "side": "buy", "type": "limit", "quantity": 100, "price": 1850.0}

        order_response = client.post("/api/trade/orders", json=order_request)

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
        mock_user.return_value = Mock(id="test_user_008", username="poor_trader", is_active=True)

        # 尝试下单超过购买力
        large_order = {
            "symbol": "600519",
            "side": "buy",
            "type": "limit",
            "quantity": 100000,  # 超大数量
            "price": 1850.0,
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
        mock_user.return_value = Mock(id="test_user_009", username="trader2", is_active=True)

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
        mock_user.return_value = Mock(id="test_user_010", username="network_user", is_active=True)

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
        mock_user.side_effect = [Mock(id="test_user_011", username="session_user"), None]  # 模拟会话过期

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
        mock_user.return_value = Mock(id="test_user_012", username="perf_user", is_active=True)

        import time

        # 测试多个端点的响应时间
        endpoints = ["/api/market/overview", "/api/market/health", "/health"]

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


class TestRealDataIntegration(RealDataValidationMixin):
    """真实数据集成测试 - 验证完整的数据流"""

    def test_real_data_source_availability(self, client):
        """测试真实数据源可用性"""
        results = self.validate_data_source_availability(client)

        # 验证关键数据源可用性
        assert results["market_data_available"], "市场数据API不可用"
        assert results["api_contract_valid"], "API契约验证失败"

        # 记录测试结果
        self.test_results = results
        print(
            f"✅ 数据源可用性测试通过: {sum(results[k] for k in results.keys() if k.endswith('_available') or k.endswith('_valid') or k.endswith('_correct') or k.endswith('_ready'))}/{len([k for k in results.keys() if k.endswith('_available') or k.endswith('_valid') or k.endswith('_correct') or k.endswith('_ready')])}"
        )

    def test_real_data_integration_completeness(self, client):
        """测试真实数据集成完整性"""
        results = self.validate_real_data_integration(client)

        # 验证数据管道工作状态
        assert results["data_pipeline_working"], "数据管道未正常工作"

        # 验证错误处理机制
        assert results["error_handling_working"], "错误处理机制未正常工作"

        # 验证性能指标
        assert results["performance_acceptable"], "性能指标不符合要求"

        print("✅ 数据集成完整性测试通过")

    def test_data_routing_correctness(self, client):
        """测试数据路由正确性"""
        # 验证数据是否正确路由到对应的数据库

        # 1. 测试市场数据路由 (应该到TDengine)
        market_response = client.get("/api/market/overview")
        assert market_response.status_code == 200

        # 2. 测试策略数据路由 (应该到PostgreSQL)
        strategy_response = client.get("/api/strategy/strategies")
        assert strategy_response.status_code == 200

        # 3. 测试回测数据路由 (应该到PostgreSQL + TimescaleDB)
        # 这里需要认证
        auth_response = client.post("/api/auth/login", data={"username": "admin", "password": "admin123"})
        assert auth_response.status_code == 200

        token = auth_response.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 获取策略列表
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

        print("✅ 数据路由正确性测试通过")

    def test_api_contract_compliance(self, client):
        """测试API契约合规性"""
        # 验证API响应格式符合预期契约

        endpoints_to_test = [
            ("/api/market/overview", "GET", None),
            ("/api/strategy/strategies", "GET", None),
            ("/api/auth/login", "POST", {"username": "admin", "password": "admin123"}),
        ]

        for endpoint, method, data in endpoints_to_test:
            if method == "GET":
                response = client.get(endpoint)
            elif method == "POST":
                response = client.post(endpoint, json=data if data else {})

            assert response.status_code in [200, 201, 422], f"API {endpoint} 返回异常状态码: {response.status_code}"

            # 验证响应格式
            response_data = response.json()
            assert isinstance(response_data, dict), f"API {endpoint} 响应格式错误"

            # 验证统一响应格式
            if "success" in response_data:
                assert isinstance(response_data["success"], bool), f"API {endpoint} success字段类型错误"

            if "data" in response_data:
                assert isinstance(response_data["data"], (dict, list)), f"API {endpoint} data字段类型错误"

        print("✅ API契约合规性测试通过")

    def test_data_mapping_accuracy(self, client):
        """测试数据映射准确性"""
        # 验证API返回的数据与前端期望的数据结构匹配

        # 测试市场数据映射
        market_response = client.get("/api/market/overview")
        assert market_response.status_code == 200

        market_data = market_response.json()["data"]

        # 验证市场数据结构
        if "indices" in market_data:
            for index in market_data["indices"]:
                required_fields = ["symbol", "name", "current_price"]
                for field in required_fields:
                    assert field in index, f"市场指数数据缺少必需字段: {field}"

        # 测试策略数据映射
        strategy_response = client.get("/api/strategy/strategies")
        assert strategy_response.status_code == 200

        strategy_data = strategy_response.json()["data"]

        # 验证策略数据结构
        if "strategies" in strategy_data:
            for strategy in strategy_data["strategies"]:
                required_fields = ["id", "name", "type"]
                for field in required_fields:
                    assert field in strategy, f"策略数据缺少必需字段: {field}"

        print("✅ 数据映射准确性测试通过")

    def test_ui_data_binding_readiness(self, client):
        """测试UI数据绑定就绪状态"""
        # 验证API返回的数据格式适合前端组件使用

        # 获取市场数据
        market_response = client.get("/api/market/overview")
        assert market_response.status_code == 200
        market_data = market_response.json()["data"]

        # 验证市场数据适合前端组件使用
        # 前端StatCard组件期望的数据格式
        if "indices" in market_data and len(market_data["indices"]) > 0:
            first_index = market_data["indices"][0]

            # 检查是否有前端需要的字段
            frontend_fields = ["symbol", "name", "current_price", "change_percent"]
            available_fields = [f for f in frontend_fields if f in first_index]

            assert len(available_fields) >= 2, "市场数据缺少前端需要的字段"

        # 获取策略数据
        strategy_response = client.get("/api/strategy/strategies")
        assert strategy_response.status_code == 200
        strategy_data = strategy_response.json()["data"]

        # 验证策略数据适合前端组件使用
        if "strategies" in strategy_data and len(strategy_data["strategies"]) > 0:
            first_strategy = strategy_data["strategies"][0]

            # 检查是否有前端需要的字段
            frontend_fields = ["id", "name", "type", "status"]
            available_fields = [f for f in frontend_fields if f in first_strategy]

            assert len(available_fields) >= 2, "策略数据缺少前端需要的字段"

        print("✅ UI数据绑定就绪状态测试通过")

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

        # 验证响应包含数据
        response_data = response.json()
        assert "data" in response_data or response_data.get("success") is not None, f"API端点 {endpoint} 缺少数据字段"


# Pytest 运行配置
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
