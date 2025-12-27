"""
E2E Tests for Fund Flow and Dragon Tiger Pages
Tests for capital flow data and trading activity monitoring
"""

import pytest
from playwright.sync_api import Page


class TestFundFlow:
    """资金流向测试"""

    def test_fund_flow_page_loading(self, page: Page) -> None:
        """测试资金流向页面加载"""
        page.goto("/market/fund-flow")

        page.wait_for_selector(".fund-flow-container", timeout=15000)
        assert page.is_visible(".fund-flow-container")

    def test_fund_flow_data_display(self, page: Page) -> None:
        """测试资金流向数据显示"""
        page.goto("/market/fund-flow")

        page.wait_for_selector(".fund-flow-chart", timeout=10000)

        main_net_inflow = page.locator(".main-net-inflow")
        small_net_inflow = page.locator(".small-net-inflow")

        assert main_net_inflow.is_visible()
        assert small_net_inflow.is_visible()

    def test_fund_flow_chart_rendering(self, page: Page) -> None:
        """测试资金流向图表渲染"""
        page.goto("/market/fund-flow")

        page.wait_for_selector(".fund-flow-chart canvas", timeout=10000)

        chart = page.locator(".fund-flow-chart canvas")
        assert chart.count() > 0

    def test_fund_flow_period_filter(self, page: Page) -> None:
        """测试资金流向时间段筛选"""
        page.goto("/market/fund-flow")

        page.wait_for_selector(".period-selector", timeout=10000)

        page.click(".period-selector button:has-text('5日')")

        page.wait_for_timeout(2000)

        page.click(".period-selector button:has-text('10日')")

        page.wait_for_timeout(2000)

    def test_industry_fund_flow(self, page: Page) -> None:
        """测试行业资金流向"""
        page.goto("/market/fund-flow/industry")

        page.wait_for_selector(".industry-table", timeout=15000)

        rows = page.locator(".industry-table tbody tr")
        assert rows.count() > 0


class TestDragonTiger:
    """龙虎榜测试"""

    def test_dragon_tiger_page_loading(self, page: Page) -> None:
        """测试龙虎榜页面加载"""
        page.goto("/market/dragon-tiger")

        page.wait_for_selector(".dragon-tiger-container", timeout=15000)
        assert page.is_visible(".dragon-tiger-container")

    def test_dragon_tiger_list_display(self, page: Page) -> None:
        """测试龙虎榜列表显示"""
        page.goto("/market/dragon-tiger")

        page.wait_for_selector(".dragon-tiger-table", timeout=10000)

        rows = page.locator(".dragon-tiger-table tbody tr")
        assert rows.count() > 0

    def test_dragon_tiger_detail(self, page: Page) -> None:
        """测试龙虎榜详情"""
        page.goto("/market/dragon-tiger")

        page.wait_for_selector(".dragon-tiger-table tbody tr", timeout=10000)

        first_row = page.locator(".dragon-tiger-table tbody tr").first
        first_row.click()

        page.wait_for_selector(".dragon-tiger-detail", timeout=5000)
        assert page.is_visible(".dragon-tiger-detail")

    def test_institutional_trading(self, page: Page) -> None:
        """测试机构买卖数据"""
        page.goto("/market/dragon-tiger/institutional")

        page.wait_for_selector(".institutional-table", timeout=15000)

        buy_amount = page.locator(".buy-amount")
        sell_amount = page.locator(".sell-amount")

        assert buy_amount.is_visible()
        assert sell_amount.is_visible()

    def test_dragon_tiger_calendar(self, page: Page) -> None:
        """测试龙虎榜日历"""
        page.goto("/market/dragon-tiger")

        page.wait_for_selector(".date-picker", timeout=10000)

        page.click(".date-picker input")

        page.wait_for_selector(".ant-calendar", timeout=5000)


class TestTradingActivity:
    """交易活跃度测试"""

    def test_trading_activity_overview(self, page: Page) -> None:
        """测试交易活跃度概览"""
        page.goto("/market/activity")

        page.wait_for_selector(".activity-overview", timeout=15000)

        turnover_rate = page.locator(".turnover-rate")
        trading_volume = page.locator(".trading-volume")

        assert turnover_rate.is_visible()
        assert trading_volume.is_visible()

    def test_hot_stocks(self, page: Page) -> None:
        """测试热门股票"""
        page.goto("/market/activity/hot-stocks")

        page.wait_for_selector(".hot-stocks-list", timeout=15000)

        stocks = page.locator(".hot-stocks-list .stock-item")
        assert stocks.count() > 0

    def test_sector_rotation(self, page: Page) -> None:
        """测试板块轮动"""
        page.goto("/market/activity/sector-rotation")

        page.wait_for_selector(".sector-rotation-chart", timeout=15000)

        sector_list = page.locator(".sector-list .sector-item")
        assert sector_list.count() > 0


@pytest.mark.skip(reason="需要真实数据连接")
class TestFundFlowAPI:
    """资金流向API测试"""

    def test_fund_flow_api(self, page: Page) -> None:
        """测试资金流向API"""
        response = page.request.get("/api/v1/market/fund-flow")
        assert response.status == 200
        data = response.json()
        assert "main_inflow" in data
        assert "small_inflow" in data

    def test_dragon_tiger_api(self, page: Page) -> None:
        """测试龙虎榜API"""
        response = page.request.get("/api/v1/market/dragon-tiger")
        assert response.status == 200
        data = response.json()
        assert "stocks" in data
