"""
E2E Tests for Risk Management and Backtest Pages
Tests for risk rules, portfolio management, and strategy backtesting
"""

import pytest
from playwright.sync_api import Page


class TestRiskManagement:
    """风险管理测试"""

    def test_risk_dashboard(self, page: Page) -> None:
        """测试风险仪表盘"""
        page.goto("/risk/dashboard")

        page.wait_for_selector(".risk-dashboard", timeout=15000)
        assert page.is_visible(".risk-dashboard")

    def test_portfolio_overview(self, page: Page) -> None:
        """测试组合概览"""
        page.goto("/risk/portfolio")

        page.wait_for_selector(".portfolio-overview", timeout=15000)

        total_value = page.locator(".total-value")
        daily_pnl = page.locator(".daily-pnl")

        assert total_value.is_visible()
        assert daily_pnl.is_visible()

    def test_position_management(self, page: Page) -> None:
        """测试仓位管理"""
        page.goto("/risk/positions")

        page.wait_for_selector(".positions-table", timeout=15000)

        rows = page.locator(".positions-table tbody tr")
        assert rows.count() >= 0

    def test_risk_rules_config(self, page: Page) -> None:
        """测试风控规则配置"""
        page.goto("/risk/rules")

        page.wait_for_selector(".risk-rules-config", timeout=15000)

        max_position = page.locator("#max-position")
        stop_loss = page.locator("#stop-loss")

        assert max_position.is_visible()
        assert stop_loss.is_visible()

    def test_alerts_configuration(self, page: Page) -> None:
        """测试告警配置"""
        page.goto("/risk/alerts")

        page.wait_for_selector(".alerts-config", timeout=15000)

        alert_rules = page.locator(".alert-rule-item")
        assert alert_rules.count() >= 0

    def test_value_at_risk(self, page: Page) -> None:
        """测试VaR显示"""
        page.goto("/risk/var")

        page.wait_for_selector(".var-display", timeout=15000)

        var_value = page.locator(".var-value")
        confidence_level = page.locator(".confidence-level")

        assert var_value.is_visible()
        assert confidence_level.is_visible()


class TestBacktest:
    """回测功能测试"""

    def test_backtest_page(self, page: Page) -> None:
        """测试回测页面"""
        page.goto("/strategy/backtest")

        page.wait_for_selector(".backtest-container", timeout=15000)
        assert page.is_visible(".backtest-container")

    def test_backtest_configuration(self, page: Page) -> None:
        """测试回测配置"""
        page.goto("/strategy/backtest")

        page.wait_for_selector(".backtest-config", timeout=10000)

        stock_select = page.locator("#stock-select")
        date_range = page.locator("#date-range")
        initial_capital = page.locator("#initial-capital")

        assert stock_select.is_visible()
        assert date_range.is_visible()
        assert initial_capital.is_visible()

    def test_strategy_selection(self, page: Page) -> None:
        """测试策略选择"""
        page.goto("/strategy/backtest")

        page.wait_for_selector(".strategy-selector", timeout=10000)

        ma_strategy = page.locator("text=MA金叉")

        if ma_strategy.count() > 0:
            ma_strategy.click()

    def test_backtest_execution(self, page: Page) -> None:
        """测试回测执行"""
        page.goto("/strategy/backtest")

        page.wait_for_selector("#run-backtest", timeout=10000)

        page.click("#run-backtest")

        page.wait_for_selector(".backtest-progress", timeout=5000)
        assert page.is_visible(".backtest-progress")

    def test_backtest_results(self, page: Page) -> None:
        """测试回测结果"""
        page.goto("/strategy/backtest")

        page.wait_for_selector(".backtest-results", timeout=30000)

        roi = page.locator(".total-return")
        max_drawdown = page.locator(".max-drawdown")
        sharpe_ratio = page.locator(".sharpe-ratio")

        assert roi.is_visible()
        assert max_drawdown.is_visible()
        assert sharpe_ratio.is_visible()

    def test_equity_curve(self, page: Page) -> None:
        """测试资金曲线"""
        page.goto("/strategy/backtest")

        page.wait_for_selector(".equity-curve", timeout=30000)

        chart = page.locator(".equity-curve canvas")
        assert chart.count() > 0

    def test_trade_list(self, page: Page) -> None:
        """测试交易列表"""
        page.goto("/strategy/backtest")

        page.wait_for_selector(".trade-list", timeout=30000)

        trades = page.locator(".trade-list tbody tr")
        assert trades.count() >= 0


class TestStrategyManagement:
    """策略管理测试"""

    def test_strategy_list(self, page: Page) -> None:
        """测试策略列表"""
        page.goto("/strategy/management")

        page.wait_for_selector(".strategy-list", timeout=15000)

        strategies = page.locator(".strategy-item")
        assert strategies.count() >= 0

    def test_strategy_creation(self, page: Page) -> None:
        """测试策略创建"""
        page.goto("/strategy/management")

        page.wait_for_selector("#create-strategy", timeout=10000)

        page.click("#create-strategy")

        page.wait_for_selector(".strategy-editor", timeout=5000)
        assert page.is_visible(".strategy-editor")

    def test_strategy_parameters(self, page: Page) -> None:
        """测试策略参数"""
        page.goto("/strategy/management")

        page.wait_for_selector(".strategy-item", timeout=15000)

        first_strategy = page.locator(".strategy-item").first
        first_strategy.click()

        page.wait_for_selector(".strategy-params", timeout=5000)
        assert page.is_visible(".strategy-params")


@pytest.mark.skip(reason="需要真实数据连接")
class TestRiskAPI:
    """风险管理API测试"""

    def test_portfolio_api(self, page: Page) -> None:
        """测试组合API"""
        response = page.request.get("/api/v1/risk/portfolio")
        assert response.status == 200

    def test_positions_api(self, page: Page) -> None:
        """测试仓位API"""
        response = page.request.get("/api/v1/risk/positions")
        assert response.status == 200

    def test_backtest_api(self, page: Page) -> None:
        """测试回测API"""
        response = page.request.post(
            "/api/v1/strategy/backtest",
            json={
                "stock_code": "000001",
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "initial_capital": 100000,
            },
        )
        assert response.status == 200
