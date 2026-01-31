"""
数据表页面对象 (Data Table Page Object)
"""

from typing import List

from playwright.sync_api import Page

from .base_page import BasePage


class DataTablePage(BasePage):
    """数据表页面"""

    # ============ 定位器 ============
    TABLE_CONTAINER = ".table-container"
    TABLE_HEADER = "thead"
    TABLE_BODY = "tbody"
    TABLE_ROW = "tbody tr"
    TABLE_CELL = "td"
    PAGINATION_CONTAINER = ".pagination"
    PAGINATION_PREV = "button:has-text('上一页')"
    PAGINATION_NEXT = "button:has-text('下一页')"
    PAGE_SIZE_SELECT = "select[name='pageSize']"
    SORT_HEADER = "th[data-sortable='true']"
    FILTER_INPUT = "input[placeholder*='筛选']"
    COLUMNS_SELECTOR = ".columns-selector"
    EXPORT_DATA_BUTTON = "button:has-text('导出')"
    REFRESH_TABLE_BUTTON = "button:has-text('刷新')"
    LOADING_INDICATOR = ".loading-spinner"
    NO_DATA_MESSAGE = ".no-data"

    def __init__(self, page: Page):
        """初始化数据表页面"""
        super().__init__(page)

    # ============ 表格基本操作 ============

    def wait_for_table_load(self) -> None:
        """等待表格加载"""
        self.wait_for_element_visible(self.TABLE_CONTAINER)
        self.wait_for_loading_complete()

    def wait_for_loading_complete(self) -> None:
        """等待加载完成"""
        self.wait_for_element_hidden(self.LOADING_INDICATOR)

    def is_table_visible(self) -> bool:
        """检查表格是否可见"""
        return self.is_element_visible(self.TABLE_CONTAINER)

    def is_table_empty(self) -> bool:
        """检查表格是否为空"""
        return self.is_element_visible(self.NO_DATA_MESSAGE)

    # ============ 行操作 ============

    def get_row_count(self) -> int:
        """获取表格行数"""
        return self.get_table_row_count("table")

    def get_table_rows(self) -> List:
        """获取所有表格行"""
        return self.get_table_rows("table")

    def click_row(self, row_index: int) -> None:
        """点击指定行"""
        rows = self.get_elements(self.TABLE_ROW)
        if row_index < len(rows):
            self.click_element(rows[row_index])

    def get_row_text(self, row_index: int) -> List[str]:
        """获取行中的所有文本"""
        cells = self.page.locator(f"{self.TABLE_ROW}:nth-child({row_index + 1}) {self.TABLE_CELL}").all()
        return [self.get_text_element(cell) for cell in cells]

    # ============ 单元格操作 ============

    def get_cell_text(self, row_index: int, col_index: int) -> str:
        """获取单元格文本"""
        return self.get_table_cell_text("table", row_index + 1, col_index + 1)

    def click_cell(self, row_index: int, col_index: int) -> None:
        """点击单元格"""
        cell_selector = f"{self.TABLE_ROW}:nth-child({row_index + 1}) {self.TABLE_CELL}:nth-child({col_index + 1})"
        self.click(cell_selector)

    # ============ 排序操作 ============

    def get_sortable_headers(self) -> List:
        """获取所有可排序的列头"""
        return self.get_elements(self.SORT_HEADER)

    def sort_by_column(self, column_name: str) -> None:
        """按列排序"""
        header = self.page.locator(f"th:has-text('{column_name}')")
        self.click_element(header)
        self.wait_for_loading_complete()

    def is_sorted_ascending(self) -> bool:
        """检查是否按升序排序"""
        arrow = self.page.locator(".sort-arrow.ascending")
        return arrow.is_visible()

    def is_sorted_descending(self) -> bool:
        """检查是否按降序排序"""
        arrow = self.page.locator(".sort-arrow.descending")
        return arrow.is_visible()

    # ============ 筛选操作 ============

    def filter_table(self, filter_text: str) -> None:
        """筛选表格"""
        self.fill(self.FILTER_INPUT, filter_text)
        self.wait_for_loading_complete()

    def clear_filter(self) -> None:
        """清空筛选"""
        self.clear_input(self.FILTER_INPUT)
        self.wait_for_loading_complete()

    def is_filter_input_visible(self) -> bool:
        """检查筛选输入框是否可见"""
        return self.is_element_visible(self.FILTER_INPUT)

    # ============ 分页操作 ============

    def is_pagination_visible(self) -> bool:
        """检查分页是否可见"""
        return self.is_element_visible(self.PAGINATION_CONTAINER)

    def go_to_next_page(self) -> None:
        """转到下一页"""
        if self.is_element_enabled(self.PAGINATION_NEXT):
            self.click(self.PAGINATION_NEXT)
            self.wait_for_loading_complete()

    def go_to_prev_page(self) -> None:
        """转到上一页"""
        if self.is_element_enabled(self.PAGINATION_PREV):
            self.click(self.PAGINATION_PREV)
            self.wait_for_loading_complete()

    def is_next_page_button_enabled(self) -> bool:
        """检查下一页按钮是否启用"""
        return self.is_element_enabled(self.PAGINATION_NEXT)

    def is_prev_page_button_enabled(self) -> bool:
        """检查上一页按钮是否启用"""
        return self.is_element_enabled(self.PAGINATION_PREV)

    # ============ 页面大小选择 ============

    def select_page_size(self, size: str) -> None:
        """选择每页显示数量"""
        self.select_option(self.PAGE_SIZE_SELECT, size)
        self.wait_for_loading_complete()

    def select_page_size_10(self) -> None:
        """选择每页10条"""
        self.select_page_size("10")

    def select_page_size_25(self) -> None:
        """选择每页25条"""
        self.select_page_size("25")

    def select_page_size_50(self) -> None:
        """选择每页50条"""
        self.select_page_size("50")

    # ============ 列操作 ============

    def get_column_headers(self) -> List[str]:
        """获取列标题"""
        headers = self.get_elements("thead th")
        return [self.get_text_element(h) for h in headers]

    def is_column_visible(self, column_name: str) -> bool:
        """检查列是否可见"""
        return self.is_element_visible(f"th:has-text('{column_name}')")

    def show_column(self, column_name: str) -> None:
        """显示列"""
        checkbox = self.page.locator(f"input[value='{column_name}']")
        if not checkbox.is_checked():
            self.check_checkbox(f"input[value='{column_name}']")

    def hide_column(self, column_name: str) -> None:
        """隐藏列"""
        checkbox = self.page.locator(f"input[value='{column_name}']")
        if checkbox.is_checked():
            self.uncheck_checkbox(f"input[value='{column_name}']")

    # ============ 数据导出 ============

    def click_export_button(self) -> None:
        """点击导出按钮"""
        self.click(self.EXPORT_DATA_BUTTON)

    def is_export_button_visible(self) -> bool:
        """检查导出按钮是否可见"""
        return self.is_element_visible(self.EXPORT_DATA_BUTTON)

    # ============ 刷新操作 ============

    def click_refresh_button(self) -> None:
        """点击刷新按钮"""
        self.click(self.REFRESH_TABLE_BUTTON)
        self.wait_for_loading_complete()

    # ============ 断言方法 ============

    def assert_table_visible(self) -> None:
        """断言表格可见"""
        self.assert_element_visible(self.TABLE_CONTAINER)

    def assert_table_not_empty(self) -> None:
        """断言表格不为空"""
        self.assert_element_hidden(self.NO_DATA_MESSAGE)

    def assert_table_empty(self) -> None:
        """断言表格为空"""
        self.assert_element_visible(self.NO_DATA_MESSAGE)

    def assert_row_count_greater_than(self, count: int) -> None:
        """断言行数大于指定数量"""
        actual_count = self.get_row_count()
        assert actual_count > count, f"Expected > {count}, got {actual_count}"

    def assert_cell_contains_text(self, row: int, col: int, text: str) -> None:
        """断言单元格包含指定文本"""
        cell_text = self.get_cell_text(row, col)
        assert text in cell_text, f"Expected '{text}' in '{cell_text}'"
