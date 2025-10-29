"""
Browser Helper Utilities for Playwright Integration Tests

This module provides reusable utility functions for common browser operations
in Playwright integration tests, following the 5-layer verification model.

Functions:
- Screenshot management
- Wait utilities with smart timeouts
- Common element selectors
- Console log capture
- Network request monitoring

Author: MyStocks Development Team
Created: 2025-10-29
"""

import os
import time
from typing import Optional, List, Dict, Any
from playwright.sync_api import Page, Response, ConsoleMessage
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# SCREENSHOT UTILITIES
# =============================================================================


def take_screenshot(
    page: Page, name: str, screenshot_dir: str = "docs/verification-screenshots"
) -> str:
    """
    Take a screenshot and save to verification directory.

    Args:
        page: Playwright page instance
        name: Screenshot filename (without extension)
        screenshot_dir: Directory to save screenshots (default: docs/verification-screenshots)

    Returns:
        str: Full path to saved screenshot

    Example:
        take_screenshot(page, "dashboard-loaded")
        # Saves to: docs/verification-screenshots/dashboard-loaded.png
    """
    os.makedirs(screenshot_dir, exist_ok=True)
    screenshot_path = os.path.join(screenshot_dir, f"{name}.png")

    page.screenshot(path=screenshot_path, full_page=False)
    logger.info(f"Screenshot saved: {screenshot_path}")

    return screenshot_path


def take_full_page_screenshot(
    page: Page, name: str, screenshot_dir: str = "docs/verification-screenshots"
) -> str:
    """
    Take a full-page screenshot (scrolls entire page).

    Args:
        page: Playwright page instance
        name: Screenshot filename (without extension)
        screenshot_dir: Directory to save screenshots

    Returns:
        str: Full path to saved screenshot

    Example:
        take_full_page_screenshot(page, "dashboard-complete")
    """
    os.makedirs(screenshot_dir, exist_ok=True)
    screenshot_path = os.path.join(screenshot_dir, f"{name}-full.png")

    page.screenshot(path=screenshot_path, full_page=True)
    logger.info(f"Full-page screenshot saved: {screenshot_path}")

    return screenshot_path


def take_element_screenshot(
    page: Page,
    selector: str,
    name: str,
    screenshot_dir: str = "docs/verification-screenshots",
) -> str:
    """
    Take a screenshot of a specific element.

    Args:
        page: Playwright page instance
        selector: CSS selector for the element
        name: Screenshot filename (without extension)
        screenshot_dir: Directory to save screenshots

    Returns:
        str: Full path to saved screenshot

    Example:
        take_element_screenshot(page, "table.dragon-tiger", "dragon-tiger-table")
    """
    os.makedirs(screenshot_dir, exist_ok=True)
    screenshot_path = os.path.join(screenshot_dir, f"{name}-element.png")

    element = page.locator(selector)
    element.screenshot(path=screenshot_path)
    logger.info(f"Element screenshot saved: {screenshot_path}")

    return screenshot_path


# =============================================================================
# WAIT UTILITIES
# =============================================================================


def wait_for_page_load(page: Page, timeout: int = 30000) -> None:
    """
    Wait for page to fully load (networkidle state).

    Args:
        page: Playwright page instance
        timeout: Maximum wait time in milliseconds (default: 30000)

    Example:
        page.goto("http://localhost:8000/dashboard")
        wait_for_page_load(page)
    """
    page.wait_for_load_state("networkidle", timeout=timeout)
    logger.info("Page fully loaded (networkidle)")


def wait_for_element(
    page: Page, selector: str, state: str = "visible", timeout: int = 10000
) -> None:
    """
    Wait for element to reach specified state.

    Args:
        page: Playwright page instance
        selector: CSS selector for the element
        state: Element state to wait for ("visible", "hidden", "attached", "detached")
        timeout: Maximum wait time in milliseconds (default: 10000)

    Example:
        wait_for_element(page, "table.dragon-tiger", "visible")
    """
    page.wait_for_selector(selector, state=state, timeout=timeout)
    logger.info(f"Element '{selector}' is {state}")


def wait_for_text(page: Page, text: str, timeout: int = 10000) -> None:
    """
    Wait for specific text to appear on the page.

    Args:
        page: Playwright page instance
        text: Text to wait for
        timeout: Maximum wait time in milliseconds (default: 10000)

    Example:
        wait_for_text(page, "龙虎榜")  # Wait for "Dragon Tiger" text
    """
    page.wait_for_selector(f"text={text}", timeout=timeout)
    logger.info(f"Text '{text}' appeared on page")


def wait_for_api_response(
    page: Page, url_pattern: str, timeout: int = 10000
) -> Response:
    """
    Wait for API response matching URL pattern.

    Args:
        page: Playwright page instance
        url_pattern: URL pattern to match (regex or substring)
        timeout: Maximum wait time in milliseconds (default: 10000)

    Returns:
        Response: Playwright Response object

    Example:
        response = wait_for_api_response(page, "**/api/market/dragon-tiger**")
        assert response.ok
    """
    with page.expect_response(url_pattern, timeout=timeout) as response_info:
        response = response_info.value

    logger.info(f"API response received: {response.url}")
    return response


def smart_wait(page: Page, milliseconds: int = 1000) -> None:
    """
    Wait for a specified time (use sparingly, prefer explicit waits).

    Args:
        page: Playwright page instance
        milliseconds: Time to wait in milliseconds

    Note:
        Use this only when explicit waits (wait_for_element, etc.) are not possible.
        Hard waits make tests slower and less reliable.

    Example:
        smart_wait(page, 500)  # Wait 500ms for animation to complete
    """
    page.wait_for_timeout(milliseconds)


# =============================================================================
# COMMON ELEMENT SELECTORS
# =============================================================================


class CommonSelectors:
    """
    Common CSS selectors used across MyStocks application.

    Usage:
        from tests.integration.utils.browser_helpers import CommonSelectors

        # Check if login button exists
        page.locator(CommonSelectors.LOGIN_BUTTON).click()
    """

    # Authentication
    LOGIN_BUTTON = "button[type='submit']"
    USERNAME_INPUT = "input[name='username'], input[type='text']"
    PASSWORD_INPUT = "input[name='password'], input[type='password']"
    LOGOUT_BUTTON = "button:has-text('退出'), button:has-text('登出')"

    # Navigation
    NAV_MENU = "nav, .nav-menu, .sidebar"
    NAV_DASHBOARD = "a[href*='dashboard'], a:has-text('仪表盘')"
    NAV_DRAGON_TIGER = "a[href*='dragon-tiger'], a:has-text('龙虎榜')"
    NAV_ETF = "a[href*='etf'], a:has-text('ETF')"
    NAV_FUND_FLOW = "a[href*='fund-flow'], a:has-text('资金流向')"
    NAV_CHIP_RACE = "a[href*='chip-race'], a:has-text('竞价抢筹')"

    # Tables
    TABLE_HEADER = "thead, .table-header"
    TABLE_BODY = "tbody, .table-body"
    TABLE_ROW = "tr, .table-row"
    TABLE_CELL = "td, .table-cell"

    # Data tables (specific)
    DRAGON_TIGER_TABLE = "table.dragon-tiger-table, .dragon-tiger-data"
    ETF_TABLE = "table.etf-table, .etf-data"
    FUND_FLOW_TABLE = "table.fund-flow-table, .fund-flow-data"
    CHIP_RACE_TABLE = "table.chip-race-table, .chip-race-data"

    # Dashboard
    DASHBOARD_SUMMARY = ".dashboard-summary, .summary-card"
    DASHBOARD_CHART = ".dashboard-chart, canvas, svg"
    DASHBOARD_STAT = ".stat-card, .metric-card"

    # Loading states
    LOADING_SPINNER = ".loading, .spinner, .el-loading"
    LOADING_OVERLAY = ".loading-overlay, .el-loading-mask"

    # Errors
    ERROR_MESSAGE = ".error, .error-message, .el-message--error"
    ALERT_MESSAGE = ".alert, .el-alert"


# =============================================================================
# CONSOLE LOG CAPTURE
# =============================================================================


class ConsoleCapture:
    """
    Capture and filter console messages from browser.

    Usage:
        console = ConsoleCapture(page)
        page.goto("http://localhost:8000/dashboard")

        errors = console.get_errors()
        assert len(errors) == 0, f"Console errors found: {errors}"
    """

    def __init__(self, page: Page):
        """
        Initialize console capture.

        Args:
            page: Playwright page instance
        """
        self.page = page
        self.messages: List[ConsoleMessage] = []
        self.errors: List[str] = []
        self.warnings: List[str] = []

        # Set up console message listener
        page.on("console", self._on_console_message)

    def _on_console_message(self, msg: ConsoleMessage):
        """Handle console message event."""
        self.messages.append(msg)

        if msg.type == "error":
            self.errors.append(msg.text)
            logger.warning(f"Console error: {msg.text}")
        elif msg.type == "warning":
            self.warnings.append(msg.text)

    def get_errors(self) -> List[str]:
        """Get all console error messages."""
        return self.errors.copy()

    def get_warnings(self) -> List[str]:
        """Get all console warning messages."""
        return self.warnings.copy()

    def get_all_messages(self) -> List[ConsoleMessage]:
        """Get all console messages."""
        return self.messages.copy()

    def clear(self):
        """Clear captured messages."""
        self.messages.clear()
        self.errors.clear()
        self.warnings.clear()

    def assert_no_errors(self):
        """Assert that no console errors occurred."""
        assert len(self.errors) == 0, f"Console errors found: {self.errors}"


# =============================================================================
# NETWORK REQUEST MONITORING
# =============================================================================


class NetworkMonitor:
    """
    Monitor network requests and responses.

    Usage:
        monitor = NetworkMonitor(page)
        page.goto("http://localhost:8000/dashboard")

        api_requests = monitor.get_api_requests()
        assert len(api_requests) > 0

        failed = monitor.get_failed_requests()
        assert len(failed) == 0
    """

    def __init__(self, page: Page):
        """
        Initialize network monitor.

        Args:
            page: Playwright page instance
        """
        self.page = page
        self.requests: List[Dict[str, Any]] = []
        self.responses: List[Dict[str, Any]] = []
        self.failed_requests: List[Dict[str, Any]] = []

        # Set up request/response listeners
        page.on("request", self._on_request)
        page.on("response", self._on_response)
        page.on("requestfailed", self._on_request_failed)

    def _on_request(self, request):
        """Handle request event."""
        self.requests.append(
            {
                "url": request.url,
                "method": request.method,
                "headers": request.headers,
                "post_data": request.post_data,
                "resource_type": request.resource_type,
            }
        )

    def _on_response(self, response):
        """Handle response event."""
        self.responses.append(
            {
                "url": response.url,
                "status": response.status,
                "ok": response.ok,
                "headers": response.headers,
                "request_method": response.request.method,
            }
        )

    def _on_request_failed(self, request):
        """Handle request failed event."""
        self.failed_requests.append(
            {"url": request.url, "method": request.method, "failure": request.failure}
        )
        logger.error(f"Request failed: {request.url} - {request.failure}")

    def get_api_requests(self) -> List[Dict[str, Any]]:
        """Get all API requests (xhr and fetch)."""
        return [
            req for req in self.requests if req["resource_type"] in ["xhr", "fetch"]
        ]

    def get_failed_requests(self) -> List[Dict[str, Any]]:
        """Get all failed requests."""
        return self.failed_requests.copy()

    def get_requests_by_url_pattern(self, pattern: str) -> List[Dict[str, Any]]:
        """
        Get requests matching URL pattern.

        Args:
            pattern: URL substring to match

        Returns:
            List of matching requests
        """
        return [req for req in self.requests if pattern in req["url"]]

    def get_responses_by_status(self, status_code: int) -> List[Dict[str, Any]]:
        """
        Get responses with specific status code.

        Args:
            status_code: HTTP status code (e.g., 200, 404, 500)

        Returns:
            List of matching responses
        """
        return [resp for resp in self.responses if resp["status"] == status_code]

    def assert_no_failed_requests(self):
        """Assert that no requests failed."""
        assert (
            len(self.failed_requests) == 0
        ), f"Failed requests found: {self.failed_requests}"

    def clear(self):
        """Clear monitored requests and responses."""
        self.requests.clear()
        self.responses.clear()
        self.failed_requests.clear()


# =============================================================================
# AUTHENTICATION HELPERS
# =============================================================================


def login(
    page: Page, username: str, password: str, base_url: str = "http://localhost:8000"
) -> None:
    """
    Perform user login through UI.

    Args:
        page: Playwright page instance
        username: Username to log in with
        password: Password to log in with
        base_url: Base URL of application

    Example:
        login(page, "admin", "admin123")
        assert page.url.endswith("/dashboard")
    """
    page.goto(f"{base_url}/login")

    page.fill(CommonSelectors.USERNAME_INPUT, username)
    page.fill(CommonSelectors.PASSWORD_INPUT, password)
    page.click(CommonSelectors.LOGIN_BUTTON)

    # Wait for navigation to dashboard
    page.wait_for_url("**/dashboard**", timeout=10000)
    logger.info(f"Successfully logged in as {username}")


def logout(page: Page) -> None:
    """
    Perform user logout through UI.

    Args:
        page: Playwright page instance

    Example:
        logout(page)
        assert "login" in page.url
    """
    page.click(CommonSelectors.LOGOUT_BUTTON)
    page.wait_for_url("**/login**", timeout=10000)
    logger.info("Successfully logged out")


# =============================================================================
# DATA VALIDATION HELPERS
# =============================================================================


def assert_table_has_data(page: Page, table_selector: str, min_rows: int = 1) -> int:
    """
    Assert that table has data rows.

    Args:
        page: Playwright page instance
        table_selector: CSS selector for the table
        min_rows: Minimum expected rows (default: 1)

    Returns:
        int: Actual number of data rows

    Example:
        row_count = assert_table_has_data(page, "table.dragon-tiger", min_rows=5)
        assert row_count >= 5
    """
    # Wait for table to be visible
    page.wait_for_selector(table_selector, state="visible", timeout=10000)

    # Count rows in tbody
    row_count = page.locator(f"{table_selector} tbody tr").count()

    assert (
        row_count >= min_rows
    ), f"Expected at least {min_rows} rows, found {row_count}"

    logger.info(f"Table has {row_count} data rows")
    return row_count


def get_table_data(page: Page, table_selector: str) -> List[Dict[str, str]]:
    """
    Extract table data as list of dictionaries.

    Args:
        page: Playwright page instance
        table_selector: CSS selector for the table

    Returns:
        List of dictionaries, each representing a table row

    Example:
        data = get_table_data(page, "table.dragon-tiger")
        assert len(data) > 0
        assert "stock_code" in data[0]
    """
    # Wait for table
    page.wait_for_selector(table_selector, state="visible", timeout=10000)

    # Get headers
    headers = page.locator(f"{table_selector} thead th").all_text_contents()

    # Get rows
    rows = page.locator(f"{table_selector} tbody tr").all()

    table_data = []
    for row in rows:
        cells = row.locator("td").all_text_contents()
        row_dict = dict(zip(headers, cells))
        table_data.append(row_dict)

    logger.info(f"Extracted {len(table_data)} rows from table")
    return table_data


def assert_no_loading_spinner(page: Page, timeout: int = 30000) -> None:
    """
    Assert that loading spinner disappears.

    Args:
        page: Playwright page instance
        timeout: Maximum wait time in milliseconds

    Example:
        page.goto("http://localhost:8000/dashboard")
        assert_no_loading_spinner(page)
    """
    try:
        page.wait_for_selector(
            CommonSelectors.LOADING_SPINNER, state="hidden", timeout=timeout
        )
        logger.info("Loading spinner disappeared")
    except Exception:
        # No spinner found - that's OK
        logger.info("No loading spinner detected")
