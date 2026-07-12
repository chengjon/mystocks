"""端到端用户工作流测试 - 登录、搜索、自选流程"""

from unittest.mock import Mock, patch

from ._test_e2e_user_workflows_support import client


__all__ = ["TestUserWorkflowLoginSearchWatchlist", "client"]


class TestUserWorkflowLoginSearchWatchlist:
    """测试工作流1: 用户登录 → 搜索股票 → 添加到自选"""

    @patch("app.api.auth.get_current_user")
    def test_complete_login_search_watchlist_flow(self, mock_user, client):
        """测试完整的登录、搜索、添加自选流程"""
        mock_user.return_value = Mock(id="test_user_001", username="testuser", email="test@example.com", is_active=True)

        login_response = client.post("/api/v1/auth/login", json={"username": "testuser", "password": "testpass"})

        assert login_response.status_code in [200, 201]
        login_data = login_response.json()
        assert login_data["success"] is True
        assert "data" in login_data
        assert "access_token" in login_data["data"] or "token" in login_data["data"]

        search_response = client.get("/api/market/stocks/search?query=600519")

        assert search_response.status_code == 200
        search_data = search_response.json()
        assert search_data["success"] is True
        assert "data" in search_data

        watchlist_response = client.post(
            "/api/watchlist/add",
            json={"symbol": "600519", "name": "贵州茅台", "notes": "长期关注"},
            headers={
                "Authorization": f"Bearer {login_data['data'].get('access_token', login_data['data'].get('token', ''))}",
            },
        )

        assert watchlist_response.status_code in [200, 201]
        watchlist_data = watchlist_response.json()
        assert watchlist_data["success"] is True

        my_watchlist_response = client.get(
            "/api/watchlist/my",
            headers={
                "Authorization": f"Bearer {login_data['data'].get('access_token', login_data['data'].get('token', ''))}",
            },
        )

        assert my_watchlist_response.status_code == 200
        watchlist_data = my_watchlist_response.json()
        assert watchlist_data["success"] is True
        assert "data" in watchlist_data

        symbols = [item.get("symbol") for item in watchlist_data["data"]]
        assert "600519" in symbols

    @patch("app.api.auth.get_current_user")
    def test_search_stock_with_pagination(self, mock_user, client):
        """测试股票搜索分页功能"""
        mock_user.return_value = Mock(id="test_user_002", username="testuser2", is_active=True)

        page1_response = client.get("/api/market/stocks/search?query=600&page=1&size=10")
        assert page1_response.status_code == 200
        page1_data = page1_response.json()
        assert page1_data["success"] is True
        assert "data" in page1_data

        if "pagination" in page1_data.get("data", {}):
            assert page1_data["data"]["pagination"]["page"] == 1
            assert page1_data["data"]["pagination"]["size"] == 10

    @patch("app.api.auth.get_current_user")
    def test_add_duplicate_stock_to_watchlist(self, mock_user, client):
        """测试添加重复股票到自选列表"""
        mock_user.return_value = Mock(id="test_user_003", username="testuser3", is_active=True)

        first_add = client.post("/api/watchlist/add", json={"symbol": "000858", "name": "五粮液"})
        assert first_add.status_code in [200, 201]

        second_add = client.post("/api/watchlist/add", json={"symbol": "000858", "name": "五粮液"})

        data = second_add.json()
        assert "success" in data
        assert "code" in data
        assert "message" in data
