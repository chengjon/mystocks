"""
Base Page Object Model for E2E Tests
Provides common functionality for all page objects
"""

from typing import Optional
from playwright.sync_api import Page, Locator, TimeoutError as PlaywrightTimeoutError


class BasePage:
    """页面对象基类"""

    def __init__(self, page: Page, base_url: str = ""):
        self.page = page
        self.base_url = base_url

    def navigate(self, path: str, wait_until: str = "networkidle") -> None:
        """导航到页面"""
        url = f"{self.base_url}{path}" if not path.startswith("http") else path
        self.page.goto(url, wait_until=wait_until)

    def wait_for_url(self, pattern: str, timeout: int = 10000) -> bool:
        """等待URL匹配模式"""
        try:
            self.page.wait_for_url(pattern, timeout=timeout)
            return True
        except PlaywrightTimeoutError:
            return False

    def get_element(self, selector: str) -> Locator:
        """获取元素定位器"""
        return self.page.locator(selector)

    def click(self, selector: str, timeout: int = 10000) -> None:
        """点击元素"""
        self.page.wait_for_selector(selector, timeout=timeout)
        self.page.click(selector)

    def fill(self, selector: str, value: str) -> None:
        """填充输入框"""
        self.page.fill(selector, value)

    def type_text(self, selector: str, value: str, delay: int = 50) -> None:
        """逐字输入文本"""
        self.page.type(selector, value, delay=delay)

    def get_text(self, selector: str) -> str:
        """获取元素文本"""
        return self.page.text_content(selector).strip()

    def get_attribute(self, selector: str, attribute: str) -> Optional[str]:
        """获取元素属性"""
        return self.page.get_attribute(selector, attribute)

    def is_visible(self, selector: str) -> bool:
        """检查元素是否可见"""
        return self.page.is_visible(selector)

    def is_enabled(self, selector: str) -> bool:
        """检查元素是否可用"""
        return self.page.is_enabled(selector)

    def wait_for_selector(self, selector: str, timeout: int = 10000) -> Locator:
        """等待元素出现"""
        return self.page.wait_for_selector(selector, timeout=timeout)

    def wait_for_load_state(self, state: str = "networkidle") -> None:
        """等待页面加载状态"""
        self.page.wait_for_load_state(state)

    def wait_for_timeout(self, milliseconds: int) -> None:
        """等待指定时间"""
        self.page.wait_for_timeout(milliseconds)

    def take_screenshot(self, name: str = "screenshot") -> None:
        """截图"""
        self.page.screenshot(path=f"test-results/{name}.png")

    def get_page_title(self) -> str:
        """获取页面标题"""
        return self.page.title()

    def execute_js(self, script: str, *args):
        """执行JavaScript"""
        return self.page.evaluate(script, *args)

    def scroll_to_element(self, selector: str) -> None:
        """滚动到元素"""
        self.page.evaluate(f'document.querySelector("{selector}").scrollIntoView()')

    def hover(self, selector: str) -> None:
        """悬停元素"""
        self.page.hover(selector)

    def select_option(self, selector: str, value: str) -> None:
        """选择下拉框选项"""
        self.page.select_option(selector, value)

    def check_checkbox(self, selector: str) -> None:
        """勾选复选框"""
        if not self.page.is_checked(selector):
            self.page.check(selector)

    def uncheck_checkbox(self, selector: str) -> None:
        """取消勾选复选框"""
        if self.page.is_checked(selector):
            self.page.uncheck(selector)

    def press_key(self, key: str) -> None:
        """按下键盘键"""
        self.page.keyboard.press(key)

    def expect_url(self, url: str) -> bool:
        """检查当前URL"""
        return self.page.url == url
