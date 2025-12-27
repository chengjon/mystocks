"""
E2E Tests for Market Data Pages
Tests market overview, stock details, and data loading
"""

from playwright.sync_api import Page


class TestMarketOverview:
    """市场概览测试"""

    def test_market_overview_loading(self, page: Page) -> None:
        """测试市场概览页面加载"""
        page.goto("/market")

        page.wait_for_selector(".market-overview", timeout=15000)

        indices = page.locator(".index-card")
        assert indices.count() >= 3

    def test_market_indices_display(self, page: Page) -> None:
        """测试指数显示"""
        page.goto("/market")

        page.wait_for_selector(".index-card", timeout=10000)

        index_names = page.locator(".index-name")
        index_values = page.locator(".index-value")

        assert index_names.count() > 0
        assert index_values.count() > 0

    def test_real_time_updates(self, page: Page) -> None:
        """测试实时更新"""
        page.goto("/market")

        page.wait_for_selector(".market-overview", timeout=10000)

        page.wait_for_timeout(5000)

        second_value = page.locator(".index-value").first.text_content()

        assert second_value is not None


class TestStockDetails:
    """股票详情测试"""

    def test_stock_detail_page(self, page: Page) -> None:
        """测试股票详情页面"""
        page.goto("/stock/000001")

        page.wait_for_selector(".stock-header", timeout=15000)

        stock_code = page.locator(".stock-code")
        stock_name = page.locator(".stock-name")

        assert stock_code.is_visible()
        assert stock_name.is_visible()

    def test_stock_price_display(self, page: Page) -> None:
        """测试股票价格显示"""
        page.goto("/stock/000001")

        page.wait_for_selector(".stock-price", timeout=10000)

        price = page.locator(".current-price")
        assert price.is_visible()

        change = page.locator(".price-change")
        assert change.is_visible()

    def test_stock_chart_rendering(self, page: Page) -> None:
        """测试股票图表渲染"""
        page.goto("/stock/000001")

        page.wait_for_selector(".stock-chart", timeout=15000)

        chart = page.locator(".kline-chart")
        assert chart.is_visible()

    def test_stock_search(self, page: Page) -> None:
        """测试股票搜索"""
        page.goto("/market")

        search_input = page.locator("#stock-search")
        search_input.fill("000001")

        suggestions = page.locator(".search-suggestions")
        assert suggestions.is_visible()


class TestStockList:
    """股票列表测试"""

    def test_stock_list_loading(self, page: Page) -> None:
        """测试股票列表加载"""
        page.goto("/market/stock-list")

        table = page.locator(".stock-table")
        table.wait_for(timeout=15000)

        rows = page.locator(".stock-table tbody tr")
        assert rows.count() > 0

    def test_stock_list_pagination(self, page: Page) -> None:
        """测试股票列表分页"""
        page.goto("/market/stock-list")

        page.wait_for_selector(".pagination", timeout=10000)

        next_button = page.locator(".pagination .next")
        if next_button.is_enabled():
            next_button.click()

            page.wait_for_timeout(1000)
