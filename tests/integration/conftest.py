"""
Pytest Configuration for Playwright Integration Tests

This file provides shared fixtures and utilities for all integration tests.
It implements reusable test infrastructure aligned with the 5-layer verification model.

Layer Coverage:
- Layer 5 (Data): Database connection and data validation fixtures
- Layer 2 (API): Authentication and API client fixtures
- Layer 4 (UI): Browser setup and page fixtures
- Layer 3 (Integration): End-to-end test orchestration

Author: MyStocks Development Team
Created: 2025-10-29
"""

import os
import pytest
import psycopg2
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page
from typing import Generator, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# CONFIGURATION
# =============================================================================

# Load from environment variables
MYSTOCKS_URL = os.getenv("MYSTOCKS_URL", "http://localhost:8000")
MYSTOCKS_USER = os.getenv("MYSTOCKS_USER", "admin")
MYSTOCKS_PASS = os.getenv("MYSTOCKS_PASS", "admin123")

# Database configuration
DB_HOST = os.getenv("MYSTOCKS_DB_HOST", "localhost")
DB_PORT = os.getenv("MYSTOCKS_DB_PORT", "5432")
DB_USER = os.getenv("MYSTOCKS_DB_USER", "mystocks_user")
DB_PASS = os.getenv("MYSTOCKS_DB_PASS", "mystocks2025")
DB_NAME = os.getenv("MYSTOCKS_DB_NAME", "mystocks")

# Browser configuration
HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"
SLOW_MO = int(os.getenv("SLOW_MO", "0"))  # Milliseconds to slow down operations
SCREENSHOT_DIR = os.getenv("SCREENSHOT_DIR", "docs/verification-screenshots")


# =============================================================================
# LAYER 5: DATABASE FIXTURES
# =============================================================================


@pytest.fixture(scope="session")
def db_connection() -> Generator[psycopg2.extensions.connection, None, None]:
    """
    Provide PostgreSQL database connection for data validation (Layer 5).

    Scope: session (single connection reused across all tests)
    Cleanup: Connection closed after all tests complete

    Usage:
        def test_data_exists(db_connection):
            cursor = db_connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM cn_stock_top")
            assert cursor.fetchone()[0] > 0
    """
    logger.info(f"Connecting to PostgreSQL database: {DB_HOST}:{DB_PORT}/{DB_NAME}")

    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASS, database=DB_NAME
    )

    yield conn

    logger.info("Closing database connection")
    conn.close()


@pytest.fixture(scope="function")
def db_cursor(db_connection):
    """
    Provide database cursor for SQL queries (Layer 5).

    Scope: function (new cursor for each test)
    Cleanup: Auto-rollback and cursor close after each test

    Usage:
        def test_latest_data(db_cursor):
            db_cursor.execute("SELECT MAX(trade_date) FROM cn_stock_top")
            latest_date = db_cursor.fetchone()[0]
            assert latest_date is not None
    """
    cursor = db_connection.cursor()
    yield cursor
    db_connection.rollback()  # Rollback any changes (read-only tests)
    cursor.close()


# =============================================================================
# LAYER 4: BROWSER FIXTURES
# =============================================================================


@pytest.fixture(scope="session")
def browser() -> Generator[Browser, None, None]:
    """
    Provide Playwright browser instance (Layer 4).

    Scope: session (single browser instance for all tests)
    Configuration: Chromium, headless mode, slow motion support
    Cleanup: Browser closed after all tests complete

    Usage:
        def test_navigation(browser):
            context = browser.new_context()
            page = context.new_page()
            page.goto("http://localhost:8000")
    """
    logger.info(
        f"Launching Chromium browser (headless={HEADLESS}, slow_mo={SLOW_MO}ms)"
    )

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS, slow_mo=SLOW_MO)
        yield browser
        logger.info("Closing browser")
        browser.close()


@pytest.fixture(scope="function")
def context(browser: Browser) -> Generator[BrowserContext, None, None]:
    """
    Provide isolated browser context for each test (Layer 4).

    Scope: function (new context for each test - clean state)
    Features: Viewport set to 1920x1080, screenshot on failure
    Cleanup: Context closed after each test

    Usage:
        def test_login(context):
            page = context.new_page()
            page.goto(f"{MYSTOCKS_URL}/login")
    """
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        record_video_dir=None,  # Enable if video recording needed
    )

    yield context

    context.close()


@pytest.fixture(scope="function")
def page(context: BrowserContext) -> Generator[Page, None, None]:
    """
    Provide page instance for UI testing (Layer 4).

    Scope: function (new page for each test)
    Features: Auto-screenshot on test failure
    Cleanup: Page closed after each test

    Usage:
        def test_dashboard_loads(page):
            page.goto(f"{MYSTOCKS_URL}/dashboard")
            assert page.title() == "MyStocks Dashboard"
    """
    page = context.new_page()

    yield page

    # Take screenshot on failure (if test fails)
    # Note: pytest provides request fixture to check test outcome
    page.close()


# =============================================================================
# LAYER 2: API FIXTURES
# =============================================================================


@pytest.fixture(scope="session")
def auth_token(browser: Browser) -> str:
    """
    Obtain authentication token via API (Layer 2).

    Scope: session (single token reused across tests)
    Method: Uses Playwright API context for HTTP requests
    Returns: JWT access token string

    Usage:
        def test_protected_api(auth_token):
            # Use token in API requests
            headers = {"Authorization": f"Bearer {auth_token}"}
    """
    logger.info(f"Obtaining auth token for user: {MYSTOCKS_USER}")

    context = browser.new_context()
    page = context.new_page()

    # Navigate to login API endpoint
    response = page.request.post(
        f"{MYSTOCKS_URL}/api/auth/login",
        data={"username": MYSTOCKS_USER, "password": MYSTOCKS_PASS},
    )

    assert response.ok, f"Login failed: {response.status} {response.status_text}"

    data = response.json()
    token = data.get("access_token")

    assert token, "No access_token in login response"

    logger.info("Successfully obtained auth token")

    context.close()

    return token


@pytest.fixture(scope="function")
def api_client(page: Page, auth_token: str):
    """
    Provide authenticated API client for testing (Layer 2).

    Scope: function (new client for each test)
    Features: Pre-configured with auth token
    Returns: Playwright APIRequestContext with auth headers

    Usage:
        def test_api_endpoint(api_client):
            response = api_client.get("/api/market/dragon-tiger?limit=5")
            assert response.ok
            data = response.json()
            assert len(data) > 0
    """
    # Set default authorization header
    page.set_extra_http_headers({"Authorization": f"Bearer {auth_token}"})

    return page.request


# =============================================================================
# LAYER 3: INTEGRATION TEST UTILITIES
# =============================================================================


class LayerValidator:
    """
    Utility class for multi-layer verification in integration tests.

    Implements the 5-layer verification model:
    - Layer 5: Database data validation
    - Layer 2: API response validation
    - Layer 4: UI element validation
    - Layer 3: End-to-end integration validation
    """

    @staticmethod
    def check_database_layer(
        db_cursor, table_name: str, expected_min_count: int = 1
    ) -> Dict[str, Any]:
        """
        Validate Layer 5: Database data exists and is fresh.

        Args:
            db_cursor: Database cursor fixture
            table_name: Table to check
            expected_min_count: Minimum expected record count

        Returns:
            Dict with validation results:
                - exists: bool
                - count: int
                - latest_date: str
                - is_fresh: bool (within 3 days)
        """
        # Check record count
        db_cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = db_cursor.fetchone()[0]

        # Check latest date
        db_cursor.execute(f"SELECT MAX(trade_date) FROM {table_name}")
        latest_date = db_cursor.fetchone()[0]

        # Check freshness (within 3 days)
        db_cursor.execute(
            f"""
            SELECT CURRENT_DATE - MAX(trade_date) as days_old
            FROM {table_name}
        """
        )
        days_old = db_cursor.fetchone()[0]

        return {
            "exists": count >= expected_min_count,
            "count": count,
            "latest_date": str(latest_date) if latest_date else None,
            "is_fresh": days_old is not None and days_old <= 3,
            "days_old": days_old,
        }

    @staticmethod
    def check_api_layer(
        api_client, endpoint: str, expected_fields: list
    ) -> Dict[str, Any]:
        """
        Validate Layer 2: API returns valid response with expected fields.

        Args:
            api_client: Authenticated API client fixture
            endpoint: API endpoint to test
            expected_fields: List of expected field names in response

        Returns:
            Dict with validation results:
                - success: bool
                - status_code: int
                - has_data: bool
                - has_expected_fields: bool
                - data_sample: dict (first record)
        """
        response = api_client.get(f"{MYSTOCKS_URL}{endpoint}")

        if not response.ok:
            return {
                "success": False,
                "status_code": response.status,
                "error": response.status_text,
            }

        data = response.json()
        has_data = isinstance(data, list) and len(data) > 0

        if has_data:
            first_record = data[0]
            has_expected_fields = all(
                field in first_record for field in expected_fields
            )
        else:
            has_expected_fields = False
            first_record = None

        return {
            "success": True,
            "status_code": response.status,
            "has_data": has_data,
            "record_count": len(data) if isinstance(data, list) else None,
            "has_expected_fields": has_expected_fields,
            "data_sample": first_record,
        }

    @staticmethod
    def check_ui_layer(page: Page, expected_elements: Dict[str, str]) -> Dict[str, Any]:
        """
        Validate Layer 4: UI elements are visible and functional.

        Args:
            page: Playwright page fixture
            expected_elements: Dict of {element_name: css_selector}

        Returns:
            Dict with validation results:
                - all_visible: bool
                - visible_elements: list
                - missing_elements: list
                - console_errors: list
        """
        visible = []
        missing = []

        for name, selector in expected_elements.items():
            try:
                element = page.locator(selector)
                if element.is_visible(timeout=5000):
                    visible.append(name)
                else:
                    missing.append(name)
            except Exception as e:
                missing.append(name)
                logger.warning(f"Element '{name}' ({selector}) not found: {e}")

        # Check for console errors
        console_errors = []

        def handle_console_msg(msg):
            if msg.type == "error":
                console_errors.append(msg.text)

        page.on("console", handle_console_msg)

        return {
            "all_visible": len(missing) == 0,
            "visible_elements": visible,
            "missing_elements": missing,
            "console_errors": console_errors,
        }


@pytest.fixture(scope="function")
def layer_validator(db_cursor, api_client, page) -> LayerValidator:
    """
    Provide layer validation utility for integration tests.

    Usage:
        def test_dragon_tiger_integration(layer_validator):
            # Layer 5: Check database
            db_result = layer_validator.check_database_layer(db_cursor, "cn_stock_top")
            assert db_result["exists"]

            # Layer 2: Check API
            api_result = layer_validator.check_api_layer(
                api_client,
                "/api/market/dragon-tiger?limit=5",
                ["stock_code", "stock_name", "trade_date"]
            )
            assert api_result["success"]

            # Layer 4: Check UI
            ui_result = layer_validator.check_ui_layer(page, {
                "table": "table.dragon-tiger-table",
                "header": "h1"
            })
            assert ui_result["all_visible"]
    """
    return LayerValidator()


# =============================================================================
# SCREENSHOT UTILITIES
# =============================================================================


@pytest.fixture(scope="function")
def take_screenshot(page: Page, request):
    """
    Provide screenshot utility for documentation and debugging.

    Usage:
        def test_dashboard(page, take_screenshot):
            page.goto(f"{MYSTOCKS_URL}/dashboard")
            take_screenshot("dashboard-loaded")
    """

    def _take_screenshot(name: str):
        """Take screenshot and save to docs/verification-screenshots/"""
        os.makedirs(SCREENSHOT_DIR, exist_ok=True)

        test_name = request.node.name
        screenshot_path = os.path.join(SCREENSHOT_DIR, f"{test_name}-{name}.png")

        page.screenshot(path=screenshot_path)
        logger.info(f"Screenshot saved: {screenshot_path}")

        return screenshot_path

    return _take_screenshot


# =============================================================================
# TEST HOOKS
# =============================================================================


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hook to take screenshot on test failure.

    This hook runs after each test and captures a screenshot if the test failed.
    """
    outcome = yield
    report = outcome.get_result()

    # Only capture screenshot on test failure in call phase
    if report.when == "call" and report.failed:
        # Check if page fixture was used
        if "page" in item.funcargs:
            page = item.funcargs["page"]

            os.makedirs(SCREENSHOT_DIR, exist_ok=True)
            screenshot_path = os.path.join(SCREENSHOT_DIR, f"{item.name}-FAILED.png")

            try:
                page.screenshot(path=screenshot_path)
                logger.error(f"Test failed, screenshot saved: {screenshot_path}")
            except Exception as e:
                logger.error(f"Failed to capture screenshot: {e}")
