"""
E2E Tests for Authentication Flows
Tests login, logout, and session management
"""

import pytest
from playwright.sync_api import Page


class TestLogin:
    """登录测试"""

    def test_successful_login(self, page: Page) -> None:
        """测试成功登录"""
        page.goto("/login")
        page.fill("#username", "test_user")
        page.fill("#password", "test_password")
        page.click("#login-btn")

        page.wait_for_url("**/dashboard", timeout=10000)
        assert "dashboard" in page.url

    def test_login_with_invalid_credentials(self, page: Page) -> None:
        """测试无效凭据登录"""
        page.goto("/login")
        page.fill("#username", "invalid_user")
        page.fill("#password", "wrong_password")
        page.click("#login-btn")

        error_message = page.locator(".error-message")
        assert error_message.is_visible()
        assert "用户名或密码错误" in error_message.text_content()

    def test_login_empty_fields(self, page: Page) -> None:
        """测试空字段登录"""
        page.goto("/login")
        page.click("#login-btn")

        username_error = page.locator("#username + .error")
        password_error = page.locator("#password + .error")

        assert username_error.is_visible()
        assert password_error.is_visible()

    def test_session_persistence(self, page: Page) -> None:
        """测试会话持久化"""
        page.goto("/login")
        page.fill("#username", "test_user")
        page.fill("#password", "test_password")
        page.check("#remember-me")
        page.click("#login-btn")

        page.wait_for_url("**/dashboard")

        page.reload()

        assert "dashboard" in page.url or "login" not in page.url

    def test_logout(self, page: Page) -> None:
        """测试退出登录"""
        page.goto("/login")
        page.fill("#username", "test_user")
        page.fill("#password", "test_password")
        page.click("#login-btn")

        page.wait_for_url("**/dashboard")

        page.click("#user-menu")
        page.click("#logout")

        page.wait_for_url("**/login")
        assert "login" in page.url


@pytest.mark.skip(reason="需要真实API连接")
class TestAPIAuthentication:
    """API认证测试"""

    def test_api_token_generation(self, page: Page) -> None:
        """测试API令牌生成"""
        page.goto("/login")
        page.fill("#username", "test_user")
        page.fill("#password", "test_password")
        page.click("#login-btn")

        response = page.request.get("/api/v1/auth/me")
        assert response.status == 200

    def test_csrf_token_required(self, page: Page) -> None:
        """测试CSRF令牌要求"""
        import requests

        response = requests.post("http://localhost:8000/api/v1/data/stock", json={})
        assert response.status_code == 403
