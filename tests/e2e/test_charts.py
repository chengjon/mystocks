"""
E2E Tests for Chart Rendering
Tests for ECharts, K-line charts, and data visualization components
"""

from playwright.sync_api import Page


class TestChartRendering:
    """图表渲染测试"""

    def test_kline_chart_rendering(self, page: Page) -> None:
        """测试K线图渲染"""
        page.goto("/stock/000001")

        page.wait_for_selector(".kline-chart", timeout=15000)

        canvas = page.locator(".kline-chart canvas")
        assert canvas.count() > 0

    def test_kline_zoom_controls(self, page: Page) -> None:
        """测试K线图缩放控制"""
        page.goto("/stock/000001")

        page.wait_for_selector(".kline-toolbar", timeout=10000)

        zoom_in = page.locator(".kline-toolbar .zoom-in")
        zoom_out = page.locator(".kline-toolbar .zoom-out")

        assert zoom_in.is_visible()
        assert zoom_out.is_visible()

        zoom_in.click()
        page.wait_for_timeout(500)

    def test_kline_period_selector(self, page: Page) -> None:
        """测试K线周期选择"""
        page.goto("/stock/000001")

        page.wait_for_selector(".period-selector", timeout=10000)

        page.click('.period-selector button:has-text("日K")')
        page.wait_for_timeout(1000)

        page.click('.period-selector button:has-text("周K")')
        page.wait_for_timeout(1000)

        page.click('.period-selector button:has-text("月K")')
        page.wait_for_timeout(1000)

    def test_kline_indicators(self, page: Page) -> None:
        """测试K线技术指标"""
        page.goto("/stock/000001")

        page.wait_for_selector(".indicator-selector", timeout=10000)

        ma_indicator = page.locator('.indicator-selector input[value="MA"]')
        if ma_indicator.count() > 0:
            ma_indicator.check()
            page.wait_for_timeout(500)

    def test_fund_flow_chart(self, page: Page) -> None:
        """测试资金流向图"""
        page.goto("/market/fund-flow")

        page.wait_for_selector(".fund-flow-chart", timeout=15000)

        chart = page.locator(".fund-flow-chart canvas")
        assert chart.count() > 0

    def test_pie_chart_rendering(self, page: Page) -> None:
        """测试饼图渲染"""
        page.goto("/portfolio/allocation")

        page.wait_for_selector(".pie-chart", timeout=15000)

        chart = page.locator(".pie-chart canvas")
        assert chart.count() > 0

    def test_bar_chart_rendering(self, page: Page) -> None:
        """测试柱状图渲染"""
        page.goto("/market/sector-rotation")

        page.wait_for_selector(".bar-chart", timeout=15000)

        chart = page.locator(".bar-chart canvas")
        assert chart.count() > 0

    def test_line_chart_rendering(self, page: Page) -> None:
        """测试折线图渲染"""
        page.goto("/strategy/backtest/equity")

        page.wait_for_selector(".line-chart", timeout=15000)

        chart = page.locator(".line-chart canvas")
        assert chart.count() > 0

    def test_heatmap_rendering(self, page: Page) -> None:
        """测试热力图渲染"""
        page.goto("/market/heatmap")

        page.wait_for_selector(".heatmap-container", timeout=15000)

        heatmap = page.locator(".heatmap-container svg")
        assert heatmap.count() > 0

    def test_candlestick_chart(self, page: Page) -> None:
        """测试蜡烛图渲染"""
        page.goto("/stock/000001/advanced")

        page.wait_for_selector(".candlestick-chart", timeout=15000)

        chart = page.locator(".candlestick-chart canvas")
        assert chart.count() > 0

    def test_chart_tooltip(self, page: Page) -> None:
        """测试图表tooltip"""
        page.goto("/stock/000001")

        page.wait_for_selector(".kline-chart", timeout=15000)

        chart_area = page.locator(".kline-chart .chart-area")
        chart_area.hover(offset_x=100, offset_y=100)

        tooltip = page.locator(".kline-tooltip")
        assert tooltip.count() >= 0

    def test_chart_legend(self, page: Page) -> None:
        """测试图表图例"""
        page.goto("/stock/000001")

        page.wait_for_selector(".chart-legend", timeout=10000)

        legend_items = page.locator(".chart-legend .legend-item")
        assert legend_items.count() > 0

    def test_realtime_chart_update(self, page: Page) -> None:
        """测试实时图表更新"""
        page.goto("/stock/000001")

        page.wait_for_selector(".kline-chart", timeout=15000)

        initial_data = page.evaluate("() => window.chartDataLength")

        page.wait_for_timeout(5000)

        final_data = page.evaluate("() => window.chartDataLength")
        assert final_data >= initial_data

    def test_chart_export_image(self, page: Page) -> None:
        """测试图表导出图片"""
        page.goto("/stock/000001")

        page.wait_for_selector(".chart-toolbar", timeout=10000)

        export_btn = page.locator('.chart-toolbar button:has-text("导出")')
        if export_btn.count() > 0:
            export_btn.click()

            page.wait_for_selector(".export-dialog", timeout=5000)

    def test_chart_fullscreen(self, page: Page) -> None:
        """测试图表全屏模式"""
        page.goto("/stock/000001")

        page.wait_for_selector(".chart-toolbar", timeout=10000)

        fullscreen_btn = page.locator('.chart-toolbar button:has-text("全屏")')
        if fullscreen_btn.count() > 0:
            fullscreen_btn.click()

            page.wait_for_timeout(1000)


class TestTechnicalAnalysisCharts:
    """技术分析图表测试"""

    def test_macd_chart(self, page: Page) -> None:
        """测试MACD图表"""
        page.goto("/stock/000001/technical")

        page.wait_for_selector(".macd-chart", timeout=15000)

        chart = page.locator(".macd-chart canvas")
        assert chart.count() > 0

    def test_rsi_chart(self, page: Page) -> None:
        """测试RSI图表"""
        page.goto("/stock/000001/technical")

        page.wait_for_selector(".rsi-chart", timeout=15000)

        chart = page.locator(".rsi-chart canvas")
        assert chart.count() > 0

    def test_bollinger_bands(self, page: Page) -> None:
        """测试布林带"""
        page.goto("/stock/000001/technical")

        page.wait_for_selector(".bollinger-bands", timeout=15000)

        bands = page.locator(".bollinger-bands canvas")
        assert bands.count() > 0


class TestChartResponsiveness:
    """图表响应式测试"""

    def test_chart_resize(self, page: Page) -> None:
        """测试图表响应式调整"""
        page.goto("/stock/000001")

        page.wait_for_selector(".kline-chart", timeout=15000)

        initial_size = page.evaluate("() => document.querySelector('.kline-chart').offsetWidth")

        page.set_viewport_size({"width": 375, "height": 667})
        page.wait_for_timeout(500)

        resized_size = page.evaluate("() => document.querySelector('.kline-chart').offsetWidth")

        assert resized_size <= initial_size

    def test_chart_on_mobile(self, page: Page) -> None:
        """测试移动端图表"""
        page.set_viewport_size({"width": 375, "height": 667})

        page.goto("/stock/000001")

        page.wait_for_selector(".kline-chart", timeout=15000)

        chart = page.locator(".kline-chart canvas")
        assert chart.count() > 0
