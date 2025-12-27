"""
登录页面对象 (Login Page Object)
"""

from playwright.sync_api import Page
from .base_page import BasePage


class LoginPage(BasePage):
    """登录页面"""

    # ============ 定位器 ============
    USERNAME_INPUT = "input[placeholder='请输入用户名或邮箱']"
    PASSWORD_INPUT = "input[placeholder='请输入密码']"
    LOGIN_BUTTON = "button:has-text('登 录')"
    ERROR_MESSAGE = ".el-message__content"
    REMEMBER_ME_CHECKBOX = "input[type='checkbox']"
    FORGOT_PASSWORD_LINK = "a:has-text('忘记密码')"

    def __init__(self, page: Page):
        """初始化登录页面"""
        super().__init__(page)

    # ============ 登录操作 ============

    def login(self, username: str, password: str) -> None:
        """执行登录操作"""
        self.fill(self.USERNAME_INPUT, username)
        self.fill(self.PASSWORD_INPUT, password)
        self.click(self.LOGIN_BUTTON)
        self.wait_for_navigation()

    def login_as_admin(self) -> None:
        """以管理员身份登录"""
        self.login("admin", "admin123")

    def login_as_user(self) -> None:
        """以普通用户身份登录"""
        self.login("user", "user123")

    def login_with_invalid_credentials(self, username: str, password: str) -> None:
        """使用无效凭证登录"""
        self.fill(self.USERNAME_INPUT, username)
        self.fill(self.PASSWORD_INPUT, password)
        self.click(self.LOGIN_BUTTON)

    # ============ 页面验证 ============

    def is_login_form_visible(self) -> bool:
        """检查登录表单是否可见"""
        return self.is_element_visible(self.USERNAME_INPUT) and self.is_element_visible(self.PASSWORD_INPUT)

    def get_error_message(self) -> str:
        """获取错误消息"""
        return self.get_text(self.ERROR_MESSAGE)

    def is_login_button_enabled(self) -> bool:
        """检查登录按钮是否启用"""
        return self.is_element_enabled(self.LOGIN_BUTTON)

    def is_remember_me_checked(self) -> bool:
        """检查记住密码是否勾选"""
        return self.page.locator(self.REMEMBER_ME_CHECKBOX).is_checked()

    # ============ 记住密码 ============

    def check_remember_me(self) -> None:
        """勾选记住密码"""
        self.check_checkbox(self.REMEMBER_ME_CHECKBOX)

    def uncheck_remember_me(self) -> None:
        """取消勾选记住密码"""
        self.uncheck_checkbox(self.REMEMBER_ME_CHECKBOX)

    # ============ 忘记密码 ============

    def click_forgot_password(self) -> None:
        """点击忘记密码链接"""
        self.click(self.FORGOT_PASSWORD_LINK)

    # ============ 验证辅助方法 ============

    def wait_for_login_form(self) -> None:
        """等待登录表单加载"""
        self.wait_for_element_visible(self.USERNAME_INPUT)

    def assert_login_form_visible(self) -> None:
        """断言登录表单可见"""
        self.assert_element_visible(self.USERNAME_INPUT)
        self.assert_element_visible(self.PASSWORD_INPUT)
        self.assert_element_visible(self.LOGIN_BUTTON)

    def assert_error_message_displayed(self) -> None:
        """断言显示错误消息"""
        self.assert_element_visible(self.ERROR_MESSAGE)

    def assert_error_message_contains(self, text: str) -> None:
        """断言错误消息包含特定文本"""
        self.assert_text_present(self.ERROR_MESSAGE, text)
