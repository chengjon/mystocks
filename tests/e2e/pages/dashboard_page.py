"""
仪表板页面对象 (Dashboard Page Object)
"""

from playwright.sync_api import Page
from .base_page import BasePage


class DashboardPage(BasePage):
    """仪表板页面"""

    # ============ 定位器 ============
    DASHBOARD_TITLE = "h1:has-text('仪表板')"
    USER_GREETING = ".user-greeting"
    STATS_CARDS = ".stats-card"
    CHART_CONTAINER = ".chart-container"
    DATA_REFRESH_BUTTON = "button:has-text('刷新')"
    TIME_RANGE_SELECT = "select[name='timeRange']"
    EXPORT_BUTTON = "button:has-text('导出')"
    NOTIFICATION_BADGE = ".notification-badge"
    PORTFOLIO_SUMMARY = ".portfolio-summary"
    PERFORMANCE_CHART = ".performance-chart"
    MARKET_OVERVIEW = ".market-overview"
    WATCH_LIST = ".watch-list"

    def __init__(self, page: Page):
        """初始化仪表板页面"""
        super().__init__(page)

    # ============ 验证页面加载 ============

    def is_dashboard_loaded(self) -> bool:
        """检查仪表板是否已加载"""
        return self.is_element_visible(self.DASHBOARD_TITLE)

    def wait_for_dashboard_load(self) -> None:
        """等待仪表板加载"""
        self.wait_for_element_visible(self.DASHBOARD_TITLE)

    def assert_dashboard_visible(self) -> None:
        """断言仪表板可见"""
        self.assert_element_visible(self.DASHBOARD_TITLE)

    # ============ 用户相关 ============

    def get_user_greeting(self) -> str:
        """获取用户问候文本"""
        return self.get_text(self.USER_GREETING)

    def is_user_greeting_visible(self) -> bool:
        """检查用户问候是否可见"""
        return self.is_element_visible(self.USER_GREETING)

    # ============ 统计卡片操作 ============

    def get_stats_cards_count(self) -> int:
        """获取统计卡片数量"""
        return len(self.get_elements(self.STATS_CARDS))

    def get_stats_card_value(self, index: int) -> str:
        """获取统计卡片的值 (从0开始)"""
        cards = self.get_elements(self.STATS_CARDS)
        if index < len(cards):
            return self.get_text_element(cards[index])
        return ""

    def assert_stats_cards_visible(self) -> None:
        """断言统计卡片可见"""
        self.assert_element_visible(self.STATS_CARDS)

    # ============ 图表操作 ============

    def is_chart_visible(self) -> bool:
        """检查图表是否可见"""
        return self.is_element_visible(self.CHART_CONTAINER)

    def wait_for_chart_load(self) -> None:
        """等待图表加载"""
        self.wait_for_element_visible(self.CHART_CONTAINER)
        # 等待图表数据加载
        self.wait(1000)

    def assert_chart_visible(self) -> None:
        """断言图表可见"""
        self.assert_element_visible(self.CHART_CONTAINER)

    # ============ 数据刷新 ============

    def click_refresh_button(self) -> None:
        """点击刷新按钮"""
        self.click(self.DATA_REFRESH_BUTTON)
        self.wait(500)  # 等待刷新完成

    def is_refresh_button_enabled(self) -> bool:
        """检查刷新按钮是否启用"""
        return self.is_element_enabled(self.DATA_REFRESH_BUTTON)

    # ============ 时间范围选择 ============

    def select_time_range(self, value: str) -> None:
        """选择时间范围"""
        self.select_option(self.TIME_RANGE_SELECT, value)
        self.wait_for_navigation()

    def select_time_range_day(self) -> None:
        """选择日期范围"""
        self.select_time_range("day")

    def select_time_range_week(self) -> None:
        """选择周范围"""
        self.select_time_range("week")

    def select_time_range_month(self) -> None:
        """选择月范围"""
        self.select_time_range("month")

    def select_time_range_year(self) -> None:
        """选择年范围"""
        self.select_time_range("year")

    # ============ 导出功能 ============

    def click_export_button(self) -> None:
        """点击导出按钮"""
        self.click(self.EXPORT_BUTTON)

    def is_export_button_visible(self) -> bool:
        """检查导出按钮是否可见"""
        return self.is_element_visible(self.EXPORT_BUTTON)

    # ============ 通知 ============

    def get_notification_count(self) -> str:
        """获取通知计数"""
        badge = self.page.locator(self.NOTIFICATION_BADGE)
        if badge.is_visible():
            return self.get_text_element(badge)
        return "0"

    def has_notifications(self) -> bool:
        """检查是否有通知"""
        return self.is_element_visible(self.NOTIFICATION_BADGE)

    # ============ 投资组合总结 ============

    def is_portfolio_summary_visible(self) -> bool:
        """检查投资组合总结是否可见"""
        return self.is_element_visible(self.PORTFOLIO_SUMMARY)

    def get_portfolio_summary_text(self) -> str:
        """获取投资组合总结文本"""
        return self.get_text(self.PORTFOLIO_SUMMARY)

    # ============ 性能图表 ============

    def is_performance_chart_visible(self) -> bool:
        """检查性能图表是否可见"""
        return self.is_element_visible(self.PERFORMANCE_CHART)

    def wait_for_performance_chart(self) -> None:
        """等待性能图表加载"""
        self.wait_for_element_visible(self.PERFORMANCE_CHART)

    # ============ 市场概览 ============

    def is_market_overview_visible(self) -> bool:
        """检查市场概览是否可见"""
        return self.is_element_visible(self.MARKET_OVERVIEW)

    def get_market_overview_text(self) -> str:
        """获取市场概览文本"""
        return self.get_text(self.MARKET_OVERVIEW)

    # ============ 关注列表 ============

    def is_watch_list_visible(self) -> bool:
        """检查关注列表是否可见"""
        return self.is_element_visible(self.WATCH_LIST)

    def wait_for_watch_list(self) -> None:
        """等待关注列表加载"""
        self.wait_for_element_visible(self.WATCH_LIST)
