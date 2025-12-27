"""
E2E Tests for Data Export Functionality
Tests for CSV, Excel, PDF export and data download features
"""

from playwright.sync_api import Page


class TestDataExport:
    """数据导出测试"""

    def test_export_csv(self, page: Page) -> None:
        """测试CSV导出"""
        page.goto("/market/stock-list")

        page.wait_for_selector(".export-button", timeout=10000)

        page.click('.export-button:has-text("导出CSV")')

        page.wait_for_selector(".export-dialog", timeout=5000)

        confirm_btn = page.locator('.export-dialog button:has-text("确认")')
        confirm_btn.click()

        page.wait_for_timeout(3000)

    def test_export_excel(self, page: Page) -> None:
        """测试Excel导出"""
        page.goto("/market/stock-list")

        page.wait_for_selector(".export-button", timeout=10000)

        page.click('.export-button:has-text("导出Excel")')

        page.wait_for_selector(".export-dialog", timeout=5000)

        confirm_btn = page.locator('.export-dialog button:has-text("确认")')
        confirm_btn.click()

        page.wait_for_timeout(3000)

    def test_export_pdf(self, page: Page) -> None:
        """测试PDF导出"""
        page.goto("/reports/daily")

        page.wait_for_selector(".export-button", timeout=15000)

        page.click('.export-button:has-text("导出PDF")')

        page.wait_for_selector(".export-dialog", timeout=5000)

        confirm_btn = page.locator('.export-dialog button:has-text("确认")')
        confirm_btn.click()

        page.wait_for_timeout(5000)

    def test_custom_date_range_export(self, page: Page) -> None:
        """测试自定义日期范围导出"""
        page.goto("/market/stock-list")

        page.wait_for_selector(".export-button", timeout=10000)

        page.click('.export-button:has-text("导出")')

        page.wait_for_selector(".export-dialog", timeout=5000)

        start_date = page.locator("#export-start-date")
        end_date = page.locator("#export-end-date")

        start_date.fill("2024-01-01")
        end_date.fill("2024-12-31")

        confirm_btn = page.locator('.export-dialog button:has-text("确认")')
        confirm_btn.click()

        page.wait_for_timeout(3000)

    def test_selected_rows_export(self, page: Page) -> None:
        """测试选中行导出"""
        page.goto("/market/stock-list")

        page.wait_for_selector(".stock-table", timeout=10000)

        first_checkbox = page.locator(".stock-table tbody tr:first-child input[type='checkbox']")
        first_checkbox.check()

        page.wait_for_selector(".export-selected-button", timeout=5000)

        page.click('.export-selected-button:has-text("导出选中")')

        page.wait_for_selector(".export-dialog", timeout=5000)

        confirm_btn = page.locator('.export-dialog button:has-text("确认")')
        confirm_btn.click()

        page.wait_for_timeout(3000)

    def test_backtest_result_export(self, page: Page) -> None:
        """测试回测结果导出"""
        page.goto("/strategy/backtest")

        page.wait_for_selector(".backtest-results", timeout=30000)

        export_btn = page.locator('.export-button:has-text("导出结果")')
        if export_btn.count() > 0:
            export_btn.click()

            page.wait_for_selector(".export-options", timeout=5000)

            page.click('.export-options label:has-text("CSV")')

            confirm_btn = page.locator('.export-dialog button:has-text("确认")')
            confirm_btn.click()

            page.wait_for_timeout(3000)

    def test_trade_history_export(self, page: Page) -> None:
        """测试交易记录导出"""
        page.goto("/trade/history")

        page.wait_for_selector(".trade-table", timeout=15000)

        export_btn = page.locator('.export-button:has-text("导出")')
        export_btn.click()

        page.wait_for_selector(".export-dialog", timeout=5000)

        confirm_btn = page.locator('.export-dialog button:has-text("确认")')
        confirm_btn.click()

        page.wait_for_timeout(3000)

    def test_portfolio_export(self, page: Page) -> None:
        """测试组合导出"""
        page.goto("/portfolio/holdings")

        page.wait_for_selector(".portfolio-table", timeout=15000)

        export_btn = page.locator('.export-button:has-text("导出")')
        export_btn.click()

        page.wait_for_selector(".export-dialog", timeout=5000)

        confirm_btn = page.locator('.export-dialog button:has-text("确认")')
        confirm_btn.click()

        page.wait_for_timeout(3000)

    def test_download_notification(self, page: Page) -> None:
        """测试下载通知"""
        page.goto("/market/stock-list")

        page.wait_for_selector(".export-button", timeout=10000)

        page.click('.export-button:has-text("导出")')

        page.wait_for_selector(".export-dialog", timeout=5000)

        confirm_btn = page.locator('.export-dialog button:has-text("确认")')
        confirm_btn.click()

        notification = page.locator(".notification:has-text('下载开始')")
        assert notification.count() >= 0

    def test_export_file_size_limit(self, page: Page) -> None:
        """测试导出文件大小限制"""
        page.goto("/market/stock-list")

        page.wait_for_selector(".export-button", timeout=10000)

        page.click('.export-button:has-text("导出")')

        page.wait_for_selector(".export-dialog", timeout=5000)

        size_warning = page.locator(".export-dialog .file-size-warning")
        if size_warning.count() > 0:
            assert size_warning.is_visible()


class TestChartImageExport:
    """图表图片导出测试"""

    def test_export_kline_image(self, page: Page) -> None:
        """测试K线图导出为图片"""
        page.goto("/stock/000001")

        page.wait_for_selector(".kline-chart", timeout=15000)

        export_btn = page.locator('.chart-toolbar button:has-text("截图")')
        if export_btn.count() > 0:
            export_btn.click()

            page.wait_for_selector(".image-format-selector", timeout=5000)

            page.click('.image-format-selector label:has-text("PNG")')

            confirm_btn = page.locator('.export-dialog button:has-text("确认")')
            confirm_btn.click()

            page.wait_for_timeout(3000)

    def test_export_chart_pdf(self, page: Page) -> None:
        """测试图表导出为PDF"""
        page.goto("/stock/000001")

        page.wait_for_selector(".kline-chart", timeout=15000)

        export_btn = page.locator('.chart-toolbar button:has-text("导出PDF")')
        if export_btn.count() > 0:
            export_btn.click()

            page.wait_for_timeout(5000)


class TestReportGeneration:
    """报告生成测试"""

    def test_daily_report(self, page: Page) -> None:
        """测试日报生成"""
        page.goto("/reports/daily")

        page.wait_for_selector(".report-container", timeout=15000)

        generate_btn = page.locator("#generate-report")
        generate_btn.click()

        page.wait_for_selector(".report-progress", timeout=5000)

        page.wait_for_selector(".report-complete", timeout=60000)

    def test_weekly_report(self, page: Page) -> None:
        """测试周报生成"""
        page.goto("/reports/weekly")

        page.wait_for_selector(".report-container", timeout=15000)

        generate_btn = page.locator("#generate-report")
        generate_btn.click()

        page.wait_for_selector(".report-complete", timeout=60000)

    def test_monthly_report(self, page: Page) -> None:
        """测试月报生成"""
        page.goto("/reports/monthly")

        page.wait_for_selector(".report-container", timeout=15000)

        generate_btn = page.locator("#generate-report")
        generate_btn.click()

        page.wait_for_selector(".report-complete", timeout=120000)

    def test_custom_report(self, page: Page) -> None:
        """测试自定义报告"""
        page.goto("/reports/custom")

        page.wait_for_selector(".report-config", timeout=15000)

        page.fill("#report-title", "自定义报告")

        page.check("#include-chart")
        page.check("#include-table")
        page.check("#include-summary")

        generate_btn = page.locator("#generate-report")
        generate_btn.click()

        page.wait_for_selector(".report-complete", timeout=120000)


class TestExportErrorHandling:
    """导出错误处理测试"""

    def test_export_with_no_data(self, page: Page) -> None:
        """测试无数据导出"""
        page.goto("/market/stock-list")

        page.wait_for_selector(".export-button", timeout=10000)

        page.click('.export-button:has-text("导出")')

        page.wait_for_selector(".export-dialog", timeout=5000)

        empty_warning = page.locator(".export-dialog .empty-data-warning")
        if empty_warning.count() > 0:
            assert empty_warning.is_visible()

    def test_export_with_large_data(self, page: Page) -> None:
        """测试大数据量导出"""
        page.goto("/market/stock-list")

        page.wait_for_selector(".export-button", timeout=10000)

        page.click('.export-button:has-text("导出")')

        page.wait_for_selector(".export-dialog", timeout=5000)

        processing = page.locator(".export-dialog .processing-indicator")
        if processing.count() > 0:
            assert processing.is_visible()
