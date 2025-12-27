"""
Playwright E2E Test Configuration
Phase 5: Comprehensive Testing Solution
"""

import os

import pytest
from playwright.sync_api import Browser, BrowserContext, Page, Playwright
from pydantic import BaseModel


class E2EConfig(BaseModel):
    """E2E测试配置"""

    base_url: str = "http://localhost:8000"
    headless: bool = True
    browser: str = "chromium"
    viewport_width: int = 1280
    viewport_height: int = 720
    timeout: int = 30000
    retry_count: int = 2
    screenshot_on_failure: bool = True
    video_on_failure: bool = True
    trace_on_failure: bool = True


def get_config() -> E2EConfig:
    """获取E2E测试配置"""
    return E2EConfig(
        base_url=os.getenv("E2E_BASE_URL", "http://localhost:8000"),
        headless=os.getenv("E2E_HEADLESS", "true").lower() == "true",
        browser=os.getenv("E2E_BROWSER", "chromium"),
        viewport_width=int(os.getenv("E2E_VIEWPORT_WIDTH", "1280")),
        viewport_height=int(os.getenv("E2E_VIEWPORT_HEIGHT", "720")),
        timeout=int(os.getenv("E2E_TIMEOUT", "30000")),
        retry_count=int(os.getenv("E2E_RETRY_COUNT", "2")),
        screenshot_on_failure=os.getenv("E2E_SCREENSHOT_ON_FAILURE", "true").lower() == "true",
        video_on_failure=os.getenv("E2E_VIDEO_ON_FAILURE", "true").lower() == "true",
        trace_on_failure=os.getenv("E2E_TRACE_ON_FAILURE", "true").lower() == "true",
    )


@pytest.fixture(scope="session")
def playwright_instance() -> Playwright:
    """提供Playwright实例"""
    playwright = Playwright()
    yield playwright
    playwright.stop()


@pytest.fixture(scope="session")
def browser(playwright_instance: Playwright) -> Browser:
    """提供浏览器实例"""
    config = get_config()

    browser_type = playwright_instance.chromium
    if config.browser == "firefox":
        browser_type = playwright_instance.firefox
    elif config.browser == "webkit":
        browser_type = playwright_instance.webkit

    browser = browser_type.launch(
        headless=config.headless,
        args=["--no-sandbox", "--disable-setuid-sandbox"],
    )
    yield browser
    browser.close()


@pytest.fixture(scope="session")
def browser_context(browser: Browser) -> BrowserContext:
    """提供浏览器上下文"""
    config = get_config()

    context = browser.new_context(
        viewport={"width": config.viewport_width, "height": config.viewport_height},
        locale="zh-CN",
        timezone_id="Asia/Shanghai",
        permissions=["geolocation"],
    )
    yield context
    context.close()


@pytest.fixture
def page(browser_context: BrowserContext) -> Page:
    """提供页面实例"""
    page = browser_context.new_page()
    page.set_default_timeout(get_config().timeout)
    yield page
    page.close()


@pytest.fixture
def authenticated_page(page: Page) -> Page:
    """提供已认证的页面实例"""
    config = get_config()

    page.goto(f"{config.base_url}/login")

    try:
        page.fill("#username", "test_user")
        page.fill("#password", "test_password")
        page.click("#login-btn")
        page.wait_for_url("**/dashboard", timeout=10000)
    except Exception as e:
        print(f"Authentication failed: {e}")

    return page


@pytest.fixture
def test_data():
    """提供测试数据"""
    return {
        "user": {
            "username": "test_user",
            "password": "test_password",  # pragma: allowlist secret
            "email": "test@example.com",
        },
        "stock": {
            "code": "000001",
            "name": "平安银行",
        },
        "portfolio": {
            "name": "测试组合",
            "initial_balance": 100000,
        },
    }
