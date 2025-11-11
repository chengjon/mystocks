"""
Pytest configuration for Playwright E2E tests
Provides shared fixtures and configuration for browser-based testing

Reference: web/backend/tests/test_e2e_playwright.py (Task 6 implementation)
"""

import pytest
import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


# ============================================================================
# Async Event Loop Configuration
# ============================================================================


@pytest.fixture(scope="session")
def event_loop_policy():
    """Set event loop policy for async tests"""
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    return asyncio.get_event_loop_policy()


@pytest.fixture(scope="session")
def event_loop(event_loop_policy):
    """Create session-scoped event loop for async tests"""
    loop = event_loop_policy.new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# Browser Configuration
# ============================================================================


def pytest_addoption(parser):
    """Add custom command line options"""
    parser.addoption(
        "--headed",
        action="store_true",
        default=False,
        help="Run tests with visible browser (default: headless)",
    )
    parser.addoption(
        "--slow-mo",
        action="store",
        default=100,
        type=int,
        help="Slow down browser actions by N milliseconds (default: 100)",
    )
    parser.addoption(
        "--browser",
        action="store",
        default="chromium",
        choices=["chromium", "firefox", "webkit"],
        help="Browser to use for testing (default: chromium)",
    )


# ============================================================================
# Browser Lifecycle Fixtures
# ============================================================================


@pytest.fixture(scope="session")
async def playwright_context(pytestconfig):
    """Get Playwright context for browser selection"""
    from playwright.async_api import async_playwright

    browser_type = pytestconfig.getoption("--browser")

    async with async_playwright() as p:
        if browser_type == "firefox":
            yield p.firefox
        elif browser_type == "webkit":
            yield p.webkit
        else:  # chromium
            yield p.chromium


@pytest.fixture(scope="session")
async def browser(pytestconfig, playwright_context):
    """Session-scoped browser instance"""
    headless = not pytestconfig.getoption("--headed")
    slow_mo = pytestconfig.getoption("--slow-mo")

    browser = await playwright_context.launch(
        headless=headless,
        slow_mo=slow_mo,
        args=[
            "--disable-dev-shm-usage",
            "--no-first-run",
            "--no-default-browser-check",
        ],
    )
    yield browser
    await browser.close()


@pytest.fixture
async def context(browser):
    """Per-test browser context"""
    context = await browser.new_context(
        viewport={"width": 1920, "height": 1080},
        ignore_https_errors=True,
        locale="en-US",
        timezone_id="UTC",
    )
    yield context
    await context.close()


@pytest.fixture
async def page(context):
    """Per-test browser page with sensible defaults"""
    page = await context.new_page()

    # Set default timeouts
    page.set_default_timeout(30000)  # 30 seconds
    page.set_default_navigation_timeout(30000)  # 30 seconds

    # Add console log listener for debugging
    def log_console_message(msg):
        if msg.type == "error":
            print(f"🔴 Browser console error: {msg.text}")
        elif msg.type == "warning":
            print(f"🟡 Browser console warning: {msg.text}")

    page.on("console", log_console_message)

    yield page
    await page.close()


# ============================================================================
# Application URLs
# ============================================================================


@pytest.fixture
def app_url():
    """Frontend application URL"""
    return os.getenv("APP_URL", "http://localhost:3000")


@pytest.fixture
def api_url():
    """Backend API URL"""
    return os.getenv("API_URL", "http://localhost:8000")


@pytest.fixture
def ws_url():
    """WebSocket URL"""
    api_url = os.getenv("API_URL", "http://localhost:8000")
    return api_url.replace("http://", "ws://").replace("https://", "wss://")


# ============================================================================
# Test Data and Fixtures
# ============================================================================


@pytest.fixture
def test_credentials():
    """Test user credentials"""
    return {
        "email": os.getenv("TEST_USER_EMAIL", "test@example.com"),
        "password": os.getenv("TEST_USER_PASSWORD", "TestPassword123!"),
        "username": os.getenv("TEST_USERNAME", "testuser"),
    }


@pytest.fixture
def test_data_cleanup():
    """Fixture for tracking and cleaning up test data"""

    class DataCleanup:
        def __init__(self):
            self.resources = []

        def track(self, resource_type: str, resource_id: str):
            """Track resource for cleanup"""
            self.resources.append({"type": resource_type, "id": resource_id})

        async def cleanup(self):
            """Clean up all tracked resources"""
            # In a real scenario, would delete from database
            self.resources.clear()

    cleanup = DataCleanup()
    yield cleanup
    # Cleanup runs after test
    asyncio.run(cleanup.cleanup())


# ============================================================================
# Markers and Test Configuration
# ============================================================================


def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line("markers", "login: test login functionality (Task 6.2)")
    config.addinivalue_line(
        "markers", "subscription: test subscription workflow (Task 6.3)"
    )
    config.addinivalue_line(
        "markers", "query: test data query functionality (Task 6.3)"
    )
    config.addinivalue_line(
        "markers", "performance: test performance metrics (Task 6.4)"
    )
    config.addinivalue_line("markers", "e2e: end-to-end workflow tests (Task 6.3)")
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (use -m 'not slow' to skip)"
    )


# ============================================================================
# Utility Functions
# ============================================================================


def pytest_collection_modifyitems(config, items):
    """Modify test items during collection"""
    # Add asyncio marker to all async tests if not already present
    for item in items:
        if asyncio.iscoroutinefunction(item.function):
            if "asyncio" not in item.keywords:
                item.add_marker(pytest.mark.asyncio)

        # Add skip marker for tests that require specific URLs
        if item.nodeid.endswith("test_e2e_playwright.py"):
            # These tests require running application
            pass


# ============================================================================
# Test Reporting and Hooks
# ============================================================================


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Hook to capture test results and screenshots on failure"""
    outcome = yield

    if outcome.excinfo is not None and call.when == "call":
        # Test failed
        if hasattr(item, "funcargs") and "page" in item.funcargs:
            page = item.funcargs["page"]

            # Take screenshot on failure
            screenshot_path = f".test_artifacts/screenshots/{item.name}_failure.png"
            Path(".test_artifacts/screenshots").mkdir(parents=True, exist_ok=True)

            try:
                asyncio.run(page.screenshot(path=screenshot_path))
                print(f"📸 Screenshot saved: {screenshot_path}")
            except Exception as e:
                print(f"Failed to save screenshot: {e}")


# ============================================================================
# Pytest Configuration
# ============================================================================


def pytest_configure_asyncio(config):
    """Configure asyncio mode"""
    config.asyncio_mode = "auto"
