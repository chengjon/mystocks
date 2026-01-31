"""
搜索页面对象 (Search Page Object)
"""

from typing import List

from playwright.sync_api import Page

from .base_page import BasePage


class SearchPage(BasePage):
    """搜索页面"""

    # ============ 定位器 ============
    SEARCH_INPUT = "input[placeholder*='搜索']"
    SEARCH_BUTTON = "button:has-text('搜索')"
    CLEAR_SEARCH_BUTTON = "button.clear-search"
    ADVANCED_SEARCH_BUTTON = "button:has-text('高级搜索')"
    SEARCH_RESULTS = ".search-results"
    RESULT_ITEM = ".result-item"
    RESULT_COUNT = ".result-count"
    NO_RESULTS_MESSAGE = ".no-results"
    FILTER_SIDEBAR = ".filter-sidebar"
    FILTER_CHECKBOX = "input[type='checkbox']"
    SORT_DROPDOWN = "select[name='sortBy']"
    PAGE_SIZE_SELECT = "select[name='pageSize']"
    LOADING_INDICATOR = ".loading-spinner"
    PAGINATION = ".pagination"
    RESULT_GRID_VIEW = "button.grid-view"
    RESULT_LIST_VIEW = "button.list-view"

    def __init__(self, page: Page):
        """初始化搜索页面"""
        super().__init__(page)

    # ============ 搜索基本操作 ============

    def search(self, query: str) -> None:
        """执行搜索"""
        self.fill(self.SEARCH_INPUT, query)
        self.click(self.SEARCH_BUTTON)
        self.wait_for_search_complete()

    def wait_for_search_complete(self) -> None:
        """等待搜索完成"""
        self.wait_for_element_hidden(self.LOADING_INDICATOR)

    def get_search_input_value(self) -> str:
        """获取搜索输入框的值"""
        return self.get_input_value(self.SEARCH_INPUT)

    def clear_search_input(self) -> None:
        """清空搜索输入框"""
        self.clear_input(self.SEARCH_INPUT)

    def click_search_button(self) -> None:
        """点击搜索按钮"""
        self.click(self.SEARCH_BUTTON)
        self.wait_for_search_complete()

    def click_clear_search(self) -> None:
        """点击清空搜索"""
        self.click(self.CLEAR_SEARCH_BUTTON)

    # ============ 搜索结果操作 ============

    def is_search_results_visible(self) -> bool:
        """检查搜索结果是否可见"""
        return self.is_element_visible(self.SEARCH_RESULTS)

    def is_no_results_displayed(self) -> bool:
        """检查是否显示无结果消息"""
        return self.is_element_visible(self.NO_RESULTS_MESSAGE)

    def get_result_count(self) -> str:
        """获取搜索结果数量"""
        return self.get_text(self.RESULT_COUNT)

    def get_result_count_number(self) -> int:
        """获取搜索结果数量（数字）"""
        count_text = self.get_result_count()
        # 提取数字，例如从 "找到 123 个结果" 中提取 123
        import re

        match = re.search(r"\d+", count_text)
        return int(match.group()) if match else 0

    def get_results_list(self) -> List:
        """获取搜索结果列表"""
        return self.get_elements(self.RESULT_ITEM)

    def get_result_count_from_elements(self) -> int:
        """从元素获取结果数量"""
        return len(self.get_results_list())

    def click_result(self, index: int) -> None:
        """点击搜索结果"""
        results = self.get_results_list()
        if index < len(results):
            self.click_element(results[index])

    def get_result_title(self, index: int) -> str:
        """获取搜索结果标题"""
        results = self.get_results_list()
        if index < len(results):
            return self.get_text_element(results[index].locator(".result-title"))
        return ""

    def get_result_description(self, index: int) -> str:
        """获取搜索结果描述"""
        results = self.get_results_list()
        if index < len(results):
            return self.get_text_element(results[index].locator(".result-description"))
        return ""

    # ============ 高级搜索 ============

    def click_advanced_search(self) -> None:
        """点击高级搜索"""
        self.click(self.ADVANCED_SEARCH_BUTTON)

    def is_advanced_search_panel_visible(self) -> bool:
        """检查高级搜索面板是否可见"""
        return self.is_element_visible(".advanced-search-panel")

    # ============ 筛选操作 ============

    def is_filter_sidebar_visible(self) -> bool:
        """检查筛选侧边栏是否可见"""
        return self.is_element_visible(self.FILTER_SIDEBAR)

    def apply_filter(self, filter_name: str) -> None:
        """应用筛选"""
        checkbox = self.page.locator(f"input[value='{filter_name}']")
        self.check_checkbox(f"input[value='{filter_name}']")
        self.wait_for_search_complete()

    def remove_filter(self, filter_name: str) -> None:
        """移除筛选"""
        self.uncheck_checkbox(f"input[value='{filter_name}']")
        self.wait_for_search_complete()

    def get_applied_filters(self) -> List[str]:
        """获取已应用的筛选"""
        checkboxes = self.get_elements(f"{self.FILTER_SIDEBAR} input[type='checkbox']:checked")
        return [self.get_attribute(checkbox, "value") for checkbox in checkboxes]

    # ============ 排序操作 ============

    def select_sort_option(self, option: str) -> None:
        """选择排序选项"""
        self.select_option(self.SORT_DROPDOWN, option)
        self.wait_for_search_complete()

    def select_sort_relevance(self) -> None:
        """按相关性排序"""
        self.select_sort_option("relevance")

    def select_sort_newest(self) -> None:
        """按最新排序"""
        self.select_sort_option("newest")

    def select_sort_oldest(self) -> None:
        """按最旧排序"""
        self.select_sort_option("oldest")

    # ============ 分页操作 ============

    def is_pagination_visible(self) -> bool:
        """检查分页是否可见"""
        return self.is_element_visible(self.PAGINATION)

    def go_to_next_page(self) -> None:
        """转到下一页"""
        next_button = self.page.locator(f"{self.PAGINATION} button:has-text('下一页')")
        if next_button.is_enabled():
            self.click_element(next_button)
            self.wait_for_search_complete()

    def go_to_prev_page(self) -> None:
        """转到上一页"""
        prev_button = self.page.locator(f"{self.PAGINATION} button:has-text('上一页')")
        if prev_button.is_enabled():
            self.click_element(prev_button)
            self.wait_for_search_complete()

    # ============ 视图切换 ============

    def switch_to_grid_view(self) -> None:
        """切换到网格视图"""
        self.click(self.RESULT_GRID_VIEW)

    def switch_to_list_view(self) -> None:
        """切换到列表视图"""
        self.click(self.RESULT_LIST_VIEW)

    # ============ 页面大小选择 ============

    def select_page_size(self, size: str) -> None:
        """选择每页显示数量"""
        self.select_option(self.PAGE_SIZE_SELECT, size)
        self.wait_for_search_complete()

    # ============ 搜索历史 ============

    def get_search_suggestions(self) -> List[str]:
        """获取搜索建议"""
        suggestions = self.get_elements(".search-suggestion")
        return [self.get_text_element(s) for s in suggestions]

    def click_search_suggestion(self, index: int) -> None:
        """点击搜索建议"""
        suggestions = self.get_elements(".search-suggestion")
        if index < len(suggestions):
            self.click_element(suggestions[index])

    # ============ 断言方法 ============

    def assert_search_input_visible(self) -> None:
        """断言搜索输入框可见"""
        self.assert_element_visible(self.SEARCH_INPUT)

    def assert_results_visible(self) -> None:
        """断言搜索结果可见"""
        self.assert_element_visible(self.SEARCH_RESULTS)

    def assert_no_results(self) -> None:
        """断言无搜索结果"""
        self.assert_element_visible(self.NO_RESULTS_MESSAGE)

    def assert_result_count_greater_than(self, count: int) -> None:
        """断言搜索结果数量大于指定数量"""
        actual_count = self.get_result_count_number()
        assert actual_count > count, f"Expected > {count}, got {actual_count}"

    def assert_filter_applied(self, filter_name: str) -> None:
        """断言筛选已应用"""
        applied = self.get_applied_filters()
        assert filter_name in applied, f"Filter '{filter_name}' not applied"
