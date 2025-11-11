# E2E Testing Guide - Playwright Framework

**Task 6: 核心E2E测试 (Core E2E Testing)**

This guide covers the end-to-end testing framework for MyStocks using Playwright browser automation. The framework provides comprehensive testing of core user workflows: login → subscription → data query.

## Table of Contents

- [Quick Start](#quick-start)
- [Framework Architecture](#framework-architecture)
- [Test Structure](#test-structure)
- [Running Tests](#running-tests)
- [Writing Tests](#writing-tests)
- [Test Coverage](#test-coverage)
- [Troubleshooting](#troubleshooting)

## Quick Start

### Installation

1. **Install dependencies:**

```bash
# Install Python requirements including Playwright
pip install -r requirements.txt

# Install Playwright browser binaries
playwright install chromium

# Optional: Install other browsers
playwright install firefox
playwright install webkit
```

2. **Verify installation:**

```bash
pytest tests/test_e2e_playwright.py --collect-only
```

### Running Your First Test

```bash
# Run all E2E tests
pytest tests/test_e2e_playwright.py -v

# Run specific test class
pytest tests/test_e2e_playwright.py::TestLoginFlow -v

# Run with visible browser
pytest tests/test_e2e_playwright.py --headed --slow-mo=500

# Run specific marker
pytest tests/test_e2e_playwright.py -m login -v
```

## Framework Architecture

### 6.1: Playwright Framework Setup

The framework is built on modern async/await patterns with comprehensive fixture support:

```
test_e2e_playwright.py
├── Session Fixtures (browser_instance, page)
├── Test User Credentials
├── Test Data Management
├── Test Classes
│   ├── TestLoginFlow (6.2)
│   ├── TestSubscriptionFlow (6.3)
│   ├── TestDataManagement (6.4)
│   ├── TestCompleteWorkflows (6.3)
│   └── TestPerformanceAndErrors (6.4)
└── Configuration (conftest_playwright.py)
    ├── Event Loop Setup
    ├── Browser Configuration
    ├── Page Fixtures
    └── Test Data Fixtures
```

### Key Components

**Browser Lifecycle:**
- **Session-scoped browser**: Reused across all tests for performance
- **Per-test page**: Fresh page context for each test ensures isolation
- **Auto-close**: Resources properly cleaned up after tests

**Configuration:**
- Headless mode by default (set `--headed` for debugging)
- Slow-mo support for debugging (`--slow-mo=500`)
- Multiple browser support (chromium, firefox, webkit)

## Test Structure

### 6.2: Login Flow Tests

Tests the user authentication workflow:

```python
class TestLoginFlow:
    async def test_login_page_loads(self, page, base_url):
        """Verify login page loads correctly"""
        await page.goto(f"{base_url}/login")
        # Assertions on page elements...

    async def test_login_with_valid_credentials(self, page, base_url, test_user_credentials):
        """Test successful login"""
        # Fill form, submit, verify redirect...

    async def test_login_with_invalid_credentials(self, page, base_url):
        """Test login fails with invalid credentials"""
        # Verify error message...

    async def test_remember_me_functionality(self, page, base_url):
        """Test remember me checkbox"""
        # Verify functionality...
```

**Key Assertions:**
- Login form elements exist
- Valid credentials allow login
- Invalid credentials show error
- Redirect occurs on success
- Remember me checkbox functions

### 6.3: Subscription & Query Flow Tests

Tests the core market data subscription and query workflows:

```python
class TestSubscriptionFlow:
    async def test_market_data_page_loads(self, page, base_url):
        """Verify market data page loads"""

    async def test_subscribe_to_stock_symbol(self, page, base_url, test_symbols):
        """Test subscribing to stock symbols"""

    async def test_query_market_data(self, page, base_url, test_symbols):
        """Test querying market data with date range"""

    async def test_filter_market_data(self, page, base_url):
        """Test filtering results by criteria"""

class TestCompleteWorkflows:
    async def test_complete_user_journey(self, page, base_url, ...):
        """Complete workflow: Login -> Subscribe -> Query"""
```

**Key Workflows:**
1. Navigation to market pages
2. Symbol subscription
3. Data query execution
4. Results filtering
5. Complete user journey

### 6.4: Test Data Management & Reporting

Manages test data lifecycle and generates reports:

```python
class TestDataManagement:
    async def test_generate_test_report(self, test_data_manager):
        """Generate test execution report"""

    async def test_data_isolation(self, page, test_data_manager):
        """Verify test data isolation"""

class TestPerformanceAndErrors:
    async def test_page_load_performance(self, page, base_url):
        """Measure page load performance"""

    async def test_error_handling(self, page, base_url):
        """Verify error handling"""
```

**Report Structure:**
```json
{
  "total_resources_created": 5,
  "resources": [
    {"type": "login_session", "id": "user@example.com", "created_at": "2025-11-11T..."},
    {"type": "subscription", "id": "600519.SH", "created_at": "2025-11-11T..."}
  ],
  "created_at": "2025-11-11T..."
}
```

## Running Tests

### Basic Commands

```bash
# Run all E2E tests with verbose output
pytest tests/test_e2e_playwright.py -v

# Run with short traceback (easier to read)
pytest tests/test_e2e_playwright.py -v --tb=short

# Show print statements
pytest tests/test_e2e_playwright.py -v -s

# Run specific test
pytest tests/test_e2e_playwright.py::TestLoginFlow::test_login_page_loads -v

# Run tests matching pattern
pytest tests/test_e2e_playwright.py -k "login" -v

# Run tests with marker
pytest tests/test_e2e_playwright.py -m login -v
```

### Debug Options

```bash
# Run with visible browser (helpful for debugging)
pytest tests/test_e2e_playwright.py --headed

# Slow down actions by 1 second (see what's happening)
pytest tests/test_e2e_playwright.py --headed --slow-mo=1000

# Use different browser
pytest tests/test_e2e_playwright.py --browser=firefox --headed

# Stop on first failure
pytest tests/test_e2e_playwright.py -x

# Show print statements and logging
pytest tests/test_e2e_playwright.py -vv -s
```

### Parallel Execution

```bash
# Run tests in parallel (requires pytest-xdist)
# pip install pytest-xdist
pytest tests/test_e2e_playwright.py -n auto
```

## Writing Tests

### Test Template

```python
@pytest.mark.asyncio
class TestFeatureName:
    """Test feature description"""

    async def test_specific_functionality(self, page, base_url):
        """
        Test description with clear purpose

        Steps:
        1. Navigate to page
        2. Interact with elements
        3. Verify expected behavior
        """
        # Navigate
        await page.goto(f"{base_url}/path")

        # Interact
        await page.fill('input[type="email"]', "test@example.com")
        await page.click('button[type="submit"]')

        # Wait for condition
        await page.wait_for_url(lambda url: "dashboard" in url)

        # Verify
        element = await page.query_selector('[data-testid="user-menu"]')
        assert element is not None
```

### Common Selectors

```python
# By CSS selector
await page.click('button.login-btn')
await page.fill('input[type="email"]', "user@example.com")

# By test ID (recommended)
await page.click('[data-testid="login-button"]')
await page.fill('[data-testid="email-input"]', "user@example.com")

# By text content
await page.click('button:has-text("Login")')

# By role (accessibility)
await page.click('button[role="submit"]')
```

### Wait Strategies

```python
# Wait for element to appear
await page.wait_for_selector('[data-testid="success-message"]')

# Wait for navigation
await page.wait_for_url(lambda url: "dashboard" in url)

# Wait for load state
await page.wait_for_load_state("networkidle")

# Wait for function condition
await page.wait_for_function(lambda: page.evaluate("() => document.readyState === 'complete'"))

# Wait for timeout (last resort)
await page.wait_for_timeout(2000)
```

### Error Handling

```python
# Check if element exists (optional element)
element = await page.query_selector('[data-testid="optional-element"]')
if element:
    await element.click()
else:
    print("Element not found - skipping")

# Handle timeout gracefully
try:
    await page.wait_for_selector('[data-testid="element"]', timeout=5000)
    # Element exists
except TimeoutError:
    print("Element not found - may indicate API unavailable")
    pytest.skip("Required element not available")

# Check page for errors
content = await page.text_content("body")
assert "error" not in content.lower() or "expected error" in content.lower()
```

## Test Coverage

### 6.2: Login Flow (4 tests)

- ✅ Login page loads
- ✅ Valid credentials work
- ✅ Invalid credentials show error
- ✅ Remember me checkbox functions

**Coverage:** User authentication, form validation, error handling, persistence

### 6.3: Subscription & Query Flows (5 tests)

- ✅ Market data page loads
- ✅ Subscribe to symbols
- ✅ Query market data
- ✅ Filter results
- ✅ Complete user journey

**Coverage:** Market data access, subscriptions, queries, filtering, end-to-end workflows

### 6.4: Data Management & Performance (5 tests)

- ✅ Generate test reports
- ✅ Data isolation
- ✅ Page load performance
- ✅ Error handling
- ✅ Browser functionality

**Coverage:** Test infrastructure, performance metrics, error handling, browser compatibility

### Total Coverage: 14+ comprehensive E2E tests

## Troubleshooting

### Common Issues

**Issue: "Browser is not launched"**
```bash
# Solution: Install browsers
playwright install chromium
```

**Issue: Tests timeout on localhost**
```bash
# Solution: Ensure application is running
# Frontend: npm start (port 3000)
# Backend: uvicorn app.main:app (port 8000)

# Or skip tests if not running
pytest tests/test_e2e_playwright.py --tb=short
# Will show pytest.skip messages
```

**Issue: Cannot find element selector**
```python
# Solution: Debug with headed mode
pytest tests/test_e2e_playwright.py::TestLoginFlow::test_login_page_loads --headed -s

# Or inspect page content
content = await page.content()
print(content)  # With -s flag to see output
```

**Issue: Tests fail intermittently**
```python
# Solution: Use better wait strategies
# Instead of: await page.wait_for_timeout(2000)
# Use: await page.wait_for_load_state("networkidle")

# Or increase timeout for slower environments
page.set_default_timeout(60000)  # 60 seconds
```

### Debugging Tips

1. **Run with headed browser:**
   ```bash
   pytest tests/test_e2e_playwright.py --headed --slow-mo=1000 -s
   ```

2. **Add debug prints:**
   ```python
   print(f"Page URL: {page.url}")
   print(f"Page content: {await page.text_content('body')}")
   screenshot = await page.screenshot()
   ```

3. **Check console errors:**
   ```python
   def on_console(msg):
       print(f"Console {msg.type}: {msg.text}")
   page.on("console", on_console)
   ```

4. **Take screenshots:**
   ```python
   await page.screenshot(path="debug_screenshot.png")
   ```

5. **Trace recordings:**
   ```bash
   pytest tests/test_e2e_playwright.py --tracing=on
   playwright show-trace trace.zip
   ```

## Best Practices

1. **Use data-testid attributes** for reliable selectors
2. **Wait for conditions** rather than fixed timeouts
3. **Use fixtures** for shared setup
4. **Track test data** for cleanup
5. **Test core workflows** (happy path)
6. **Handle missing elements** gracefully
7. **Use markers** for test organization
8. **Keep tests isolated** (no cross-test dependencies)
9. **Use async/await** for async operations
10. **Document test purpose** clearly

## Integration with CI/CD

```yaml
# GitHub Actions example
- name: Run E2E tests
  run: |
    pip install -r requirements.txt
    playwright install chromium
    pytest tests/test_e2e_playwright.py -v --tb=short

- name: Upload artifacts on failure
  if: failure()
  uses: actions/upload-artifact@v2
  with:
    name: test-artifacts
    path: .test_artifacts/
```

## Performance Metrics

Expected performance on modern hardware:

- Page load: < 2 seconds
- Element interaction: < 500ms
- Full test suite: < 5 minutes
- Single test: < 30 seconds

## Additional Resources

- **Playwright Documentation:** https://playwright.dev/python/
- **Pytest Documentation:** https://docs.pytest.org/
- **Best Practices Guide:** https://playwright.dev/python/docs/best-practices

---

**Task 6 Implementation Status:**
- ✅ 6.1: Playwright Framework Setup (complete)
- ✅ 6.2: Login Flow Tests (4 tests)
- ✅ 6.3: Subscription & Query Tests (5 tests + 1 complete workflow)
- ✅ 6.4: Test Data Management & Reporting (4 tests)

**Total: 14+ comprehensive E2E tests with full framework support**
