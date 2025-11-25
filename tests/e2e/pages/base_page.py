"""
基础页面类 (Base Page Object Model)

提供所有页面对象的基础功能和通用方法
"""

from playwright.sync_api import Page, Locator, expect
from typing import Optional, List


class BasePage:
    """基础页面对象"""

    def __init__(self, page: Page):
        """初始化页面对象"""
        self.page = page
        self.timeout = 5000  # 5 seconds default timeout

    # ============ 导航方法 ============

    def goto(self, url: str) -> None:
        """导航到指定 URL"""
        self.page.goto(url, wait_until="networkidle")

    def go_back(self) -> None:
        """返回上一页"""
        self.page.go_back()

    def go_forward(self) -> None:
        """前进到下一页"""
        self.page.go_forward()

    def reload(self) -> None:
        """重新加载页面"""
        self.page.reload()

    # ============ 元素定位方法 ============

    def get_element(self, selector: str) -> Locator:
        """获取元素定位器"""
        return self.page.locator(selector)

    def get_elements(self, selector: str) -> List[Locator]:
        """获取多个元素定位器"""
        return self.page.locator(selector).all()

    # ============ 等待方法 ============

    def wait_for_element(self, selector: str, timeout: Optional[int] = None) -> Locator:
        """等待元素出现"""
        timeout = timeout or self.timeout
        locator = self.page.locator(selector)
        locator.wait_for(timeout=timeout)
        return locator

    def wait_for_element_visible(self, selector: str) -> Locator:
        """等待元素可见"""
        return self.wait_for_element(selector)

    def wait_for_element_hidden(self, selector: str) -> None:
        """等待元素隐藏"""
        expect(self.page.locator(selector)).to_be_hidden()

    def wait_for_navigation(self, action=None) -> None:
        """等待页面导航"""
        if action:
            with self.page.expect_navigation():
                action()
        else:
            self.page.wait_for_load_state("networkidle")

    # ============ 点击方法 ============

    def click(self, selector: str) -> None:
        """点击元素"""
        self.page.click(selector)

    def click_element(self, locator: Locator) -> None:
        """点击定位器对象"""
        locator.click()

    def double_click(self, selector: str) -> None:
        """双击元素"""
        self.page.dblclick(selector)

    def right_click(self, selector: str) -> None:
        """右击元素"""
        self.page.click(selector, button="right")

    # ============ 输入方法 ============

    def fill(self, selector: str, text: str) -> None:
        """填充输入框"""
        self.page.fill(selector, text)

    def fill_element(self, locator: Locator, text: str) -> None:
        """填充定位器对象对应的输入框"""
        locator.fill(text)

    def type_text(self, selector: str, text: str, delay: int = 50) -> None:
        """逐字输入文本"""
        self.page.locator(selector).type(text, delay=delay)

    def clear_input(self, selector: str) -> None:
        """清空输入框"""
        self.page.locator(selector).clear()

    def press_key(self, selector: str, key: str) -> None:
        """按键"""
        self.page.locator(selector).press(key)

    # ============ 选择方法 ============

    def select_option(self, selector: str, value: str) -> None:
        """选择下拉框选项"""
        self.page.select_option(selector, value)

    def check_checkbox(self, selector: str) -> None:
        """勾选复选框"""
        self.page.check(selector)

    def uncheck_checkbox(self, selector: str) -> None:
        """取消勾选复选框"""
        self.page.uncheck(selector)

    # ============ 获取文本方法 ============

    def get_text(self, selector: str) -> str:
        """获取元素文本"""
        return self.page.locator(selector).text_content() or ""

    def get_text_element(self, locator: Locator) -> str:
        """获取定位器对象的文本"""
        return locator.text_content() or ""

    def get_attribute(self, selector: str, attribute: str) -> str:
        """获取元素属性"""
        return self.page.locator(selector).get_attribute(attribute) or ""

    def get_input_value(self, selector: str) -> str:
        """获取输入框的值"""
        return self.page.locator(selector).input_value()

    # ============ 验证方法 ============

    def is_element_visible(self, selector: str) -> bool:
        """检查元素是否可见"""
        return self.page.locator(selector).is_visible()

    def is_element_hidden(self, selector: str) -> bool:
        """检查元素是否隐藏"""
        return self.page.locator(selector).is_hidden()

    def is_element_enabled(self, selector: str) -> bool:
        """检查元素是否启用"""
        return self.page.locator(selector).is_enabled()

    def is_element_disabled(self, selector: str) -> bool:
        """检查元素是否禁用"""
        return not self.is_element_enabled(selector)

    def element_exists(self, selector: str) -> bool:
        """检查元素是否存在"""
        return self.page.locator(selector).count() > 0

    # ============ 断言方法 ============

    def assert_element_visible(self, selector: str) -> None:
        """断言元素可见"""
        expect(self.page.locator(selector)).to_be_visible()

    def assert_element_hidden(self, selector: str) -> None:
        """断言元素隐藏"""
        expect(self.page.locator(selector)).to_be_hidden()

    def assert_text_present(self, selector: str, text: str) -> None:
        """断言文本存在"""
        expect(self.page.locator(selector)).to_contain_text(text)

    def assert_text_equals(self, selector: str, text: str) -> None:
        """断言文本等于"""
        expect(self.page.locator(selector)).to_have_text(text)

    def assert_url_contains(self, partial_url: str) -> None:
        """断言 URL 包含指定内容"""
        expect(self.page).to_have_url(f".*{partial_url}.*")

    def assert_url_equals(self, url: str) -> None:
        """断言 URL 等于"""
        expect(self.page).to_have_url(url)

    # ============ 表格相关方法 ============

    def get_table_rows(self, table_selector: str) -> List[Locator]:
        """获取表格行"""
        return self.page.locator(f"{table_selector} tbody tr").all()

    def get_table_cell_text(self, table_selector: str, row: int, col: int) -> str:
        """获取表格单元格文本 (从1开始计数)"""
        selector = f"{table_selector} tbody tr:nth-child({row}) td:nth-child({col})"
        return self.get_text(selector)

    def get_table_row_count(self, table_selector: str) -> int:
        """获取表格行数"""
        return len(self.get_table_rows(table_selector))

    # ============ 对话框相关方法 ============

    def accept_dialog(self) -> str:
        """接受对话框并获取消息"""
        with self.page.expect_dialog() as dialog_info:
            pass
        return dialog_info.value.message

    def dismiss_dialog(self) -> None:
        """拒绝对话框"""
        with self.page.expect_dialog() as dialog_info:
            self.page.close()

    # ============ 截图和视频 ============

    def take_screenshot(self, path: str) -> None:
        """拍摄截图"""
        self.page.screenshot(path=path)

    def take_screenshot_full_page(self, path: str) -> None:
        """拍摄整页截图"""
        self.page.screenshot(path=path, full_page=True)

    # ============ Cookie 和存储 ============

    def get_local_storage(self, key: str) -> Optional[str]:
        """获取 localStorage 值"""
        return self.page.evaluate(f"window.localStorage.getItem('{key}')")

    def set_local_storage(self, key: str, value: str) -> None:
        """设置 localStorage 值"""
        self.page.evaluate(f"window.localStorage.setItem('{key}', '{value}')")

    def get_session_storage(self, key: str) -> Optional[str]:
        """获取 sessionStorage 值"""
        return self.page.evaluate(f"window.sessionStorage.getItem('{key}')")

    def get_all_cookies(self) -> List[dict]:
        """获取所有 cookie"""
        return self.page.context.cookies()

    # ============ JavaScript 执行 ============

    def execute_script(self, script: str) -> any:
        """执行 JavaScript"""
        return self.page.evaluate(script)

    def scroll_to_element(self, selector: str) -> None:
        """滚动到元素"""
        self.page.locator(selector).scroll_into_view_if_needed()

    def scroll_to_top(self) -> None:
        """滚动到顶部"""
        self.page.evaluate("window.scrollTo(0, 0)")

    def scroll_to_bottom(self) -> None:
        """滚动到底部"""
        self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

    # ============ 等待和延迟 ============

    def wait(self, milliseconds: int) -> None:
        """等待指定毫秒"""
        self.page.wait_for_timeout(milliseconds)

    def wait_for_function(self, script: str, timeout: Optional[int] = None) -> None:
        """等待函数返回 true"""
        timeout = timeout or self.timeout
        self.page.wait_for_function(script, timeout=timeout)

    # ============ 获取当前页面信息 ============

    def get_current_url(self) -> str:
        """获取当前 URL"""
        return self.page.url

    def get_page_title(self) -> str:
        """获取页面标题"""
        return self.page.title()

    def get_page_source(self) -> str:
        """获取页面源代码"""
        return self.page.content()

    # ============ 清理方法 ============

    def close(self) -> None:
        """关闭页面"""
        self.page.close()
