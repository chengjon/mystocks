"""
Login Page Object for E2E Tests
"""

from playwright.sync_api import Page

from .base_page import BasePage


class LoginPage(BasePage):
    """登录页面"""

    USERNAME_INPUT = "#username"
    PASSWORD_INPUT = "#password"
    LOGIN_BUTTON = "#login-btn"
    ERROR_MESSAGE = ".error-message"
    REMEMBER_ME_CHECKBOX = "#remember-me"

    def __init__(self, page: Page, base_url: str = ""):
        super().__init__(page, base_url)
        self.base_url = base_url

    def navigate_to_login(self) -> None:
        """导航到登录页面"""
        self.navigate("/login")

    def login(self, username: str, password: str, remember_me: bool = False) -> None:
        """执行登录操作"""
        self.fill(self.USERNAME_INPUT, username)
        self.fill(self.PASSWORD_INPUT, password)

        if remember_me:
            self.check_checkbox(self.REMEMBER_ME_CHECKBOX)

        self.click(self.LOGIN_BUTTON)

    def login_success(self, username: str, password: str) -> "DashboardPage":
        """登录成功并跳转到仪表盘"""
        self.login(username, password)
        self.wait_for_url("**/dashboard", timeout=10000)
        return DashboardPage(self.page, self.base_url)

    def get_error_message(self) -> str:
        """获取错误消息"""
        if self.is_visible(self.ERROR_MESSAGE):
            return self.get_text(self.ERROR_MESSAGE)
        return ""

    def is_login_button_enabled(self) -> bool:
        """检查登录按钮是否可用"""
        return self.is_enabled(self.LOGIN_BUTTON)

    def clear_form(self) -> None:
        """清空表单"""
        self.fill(self.USERNAME_INPUT, "")
        self.fill(self.PASSWORD_INPUT, "")


class DashboardPage(BasePage):
    """仪表盘页面"""

    USER_MENU = "#user-menu"
    LOGOUT_BUTTON = "#logout"
    SIDEBAR = ".sidebar"
    MARKET_OVERVIEW = "text=行情概览"

    def is_user_logged_in(self) -> bool:
        """检查用户是否已登录"""
        return self.is_visible(self.USER_MENU)

    def logout(self) -> "LoginPage":
        """退出登录"""
        self.click(self.USER_MENU)
        self.click(self.LOGOUT_BUTTON)
        return LoginPage(self.page, self.base_url)

    def navigate_to_market_overview(self) -> None:
        """导航到行情概览"""
        self.click(self.MARKET_OVERVIEW)
