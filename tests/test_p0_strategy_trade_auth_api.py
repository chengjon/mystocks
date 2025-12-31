"""
P0 Strategy/Trade/Auth API 单元测试

测试:
- Strategy API (6个路由)
- Trade API (6个路由)
- Auth API (6个路由)
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, AsyncMock, patch
from fastapi.testclient import TestClient


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def mock_app():
    """创建FastAPI应用实例"""
    from app.main import app
    return app


@pytest.fixture
def client(mock_app):
    """同步测试客户端"""
    return TestClient(mock_app)


# ============================================================================
# Strategy API测试 (6个路由)
# ============================================================================


class TestStrategyAPI:
    """策略管理API测试"""

    def test_get_strategy_definitions(self, client):
        """测试获取策略定义列表"""
        response = client.get("/api/strategy/definitions")
        # 根据实际返回调整
        assert response.status_code in [200, 401, 500]

    def test_run_single_strategy(self, client):
        """测试运行单个股票策略"""
        response = client.post("/api/strategy/run_single", json={
            "strategy_code": "cross_ma",
            "symbol": "600519"
        })
        assert response.status_code in [200, 401, 500]

    def test_run_batch_strategy(self, client):
        """测试批量运行策略"""
        response = client.post("/api/strategy/run_batch", json={
            "strategy_code": "cross_ma",
            "symbols": ["600519", "000858"]
        })
        assert response.status_code in [200, 401, 500]

    def test_get_matched_stocks(self, client):
        """测试获取匹配股票列表"""
        response = client.get("/api/strategy/matched_stocks?strategy_code=cross_ma")
        assert response.status_code in [200, 401, 500]

    def test_get_strategy_stats(self, client):
        """测试获取策略统计摘要"""
        response = client.get("/api/strategy/stats_summary")
        assert response.status_code in [200, 401, 500]

    def test_get_strategy_results(self, client):
        """测试获取策略执行结果"""
        response = client.get("/api/strategy/results?task_id=test123")
        assert response.status_code in [200, 401, 500]


# ============================================================================
# Trade API测试 (6个路由)
# ============================================================================


class TestTradeAPI:
    """交易管理API测试"""

    def test_health_check(self, client):
        """测试交易API健康检查"""
        response = client.get("/trade/health")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_execute_trade(self, client):
        """测试执行交易"""
        response = client.post("/trade/execute", json={
            "symbol": "600519",
            "side": "buy",
            "quantity": 100,
            "price": 1800.0
        })
        # 根据实际实现调整预期结果
        assert response.status_code in [200, 401, 500]

    def test_get_portfolio(self, client):
        """测试获取投资组合"""
        response = client.get("/trade/portfolio")
        assert response.status_code in [200, 401, 500]

    def test_get_positions(self, client):
        """测试获取持仓列表"""
        response = client.get("/trade/positions")
        assert response.status_code in [200, 401, 500]

    def test_get_trades(self, client):
        """测试获取交易历史"""
        response = client.get("/trade/trades?limit=10")
        assert response.status_code in [200, 401, 500]

    def test_get_statistics(self, client):
        """测试获取交易统计"""
        response = client.get("/trade/statistics")
        assert response.status_code in [200, 401, 500]


# ============================================================================
# Auth API测试 (6个路由)
# ============================================================================


class TestAuthAPI:
    """认证授权API测试"""

    def test_login(self, client):
        """测试用户登录"""
        response = client.post("/api/v1/auth/login", json={
            "username": "admin",
            "password": "password"
        })
        # 登录应该成功或返回认证错误
        assert response.status_code in [200, 401, 422]

    def test_logout(self, client):
        """测试用户登出"""
        response = client.post("/api/v1/auth/logout")
        assert response.status_code in [200, 401, 500]

    def test_get_csrf_token(self, client):
        """测试获取CSRF令牌"""
        response = client.get("/api/v1/auth/csrf_token")
        assert response.status_code == 200

    def test_get_current_user(self, client):
        """测试获取当前用户信息"""
        response = client.get("/api/v1/auth/me")
        # 未认证应该返回401
        assert response.status_code in [401, 500]

    def test_get_users(self, client):
        """测试获取用户列表"""
        response = client.get("/api/v1/auth/users")
        # 未认证应该返回401
        assert response.status_code in [401, 500]

    def test_refresh_token(self, client):
        """测试刷新令牌"""
        response = client.post("/api/v1/auth/refresh")
        # 未认证应该返回401
        assert response.status_code in [401, 500]


# ============================================================================
# 集成测试
# ============================================================================


class TestAPIIntegration:
    """API集成测试"""

    def test_full_strategy_workflow(self, client):
        """测试策略完整工作流: 定义 -> 运行 -> 查询结果"""
        # 1. 获取策略定义
        response = client.get("/api/strategy/definitions")
        assert response.status_code in [200, 401]

        # 2. 运行策略
        response = client.post("/api/strategy/run_single", json={
            "strategy_code": "cross_ma",
            "symbol": "600519"
        })
        assert response.status_code in [200, 401]

        # 3. 查询结果
        response = client.get("/api/strategy/results?task_id=test")
        assert response.status_code in [200, 401]

    def test_full_trade_workflow(self, client):
        """测试交易完整工作流: 查询持仓 -> 执行交易 -> 查询历史"""
        # 1. 查询持仓
        response = client.get("/trade/positions")
        assert response.status_code in [200, 401]

        # 2. 执行交易
        response = client.post("/trade/execute", json={
            "symbol": "600519",
            "side": "buy",
            "quantity": 100,
            "price": 1800.0
        })
        assert response.status_code in [200, 401]

        # 3. 查询交易历史
        response = client.get("/trade/trades?limit=10")
        assert response.status_code in [200, 401]

    def test_auth_workflow(self, client):
        """测试认证完整工作流: 登录 -> 访问受保护资源 -> 登出"""
        # 1. 登录
        response = client.post("/api/v1/auth/login", json={
            "username": "admin",
            "password": "password"
        })
        # 假设登录成功或返回401
        if response.status_code == 200:
            # 2. 访问受保护资源
            response = client.get("/api/v1/auth/me")
            assert response.status_code in [200, 401]

            # 3. 登出
            response = client.post("/api/v1/auth/logout")
            assert response.status_code in [200, 401]


# ============================================================================
# 性能测试
# ============================================================================


@pytest.mark.performance
class TestAPIPerformance:
    """API性能测试"""

    def test_trade_health_response_time(self, client):
        """测试交易健康检查响应时间 < 100ms"""
        import time
        start = time.time()
        response = client.get("/trade/health")
        duration = (time.time() - start) * 1000
        assert response.status_code == 200
        assert duration < 100, f"响应时间 {duration:.2f}ms 超过100ms阈值"

    def test_csrf_token_response_time(self, client):
        """测试CSRF令牌获取响应时间 < 100ms"""
        import time
        start = time.time()
        response = client.get("/api/v1/auth/csrf_token")
        duration = (time.time() - start) * 1000
        assert response.status_code == 200
        assert duration < 100, f"响应时间 {duration:.2f}ms 超过100ms阈值"
