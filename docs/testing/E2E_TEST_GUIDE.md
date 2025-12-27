# MyStocks E2E Testing Guide

## Overview

End-to-End (E2E) testing framework for MyStocks using Playwright.

## Quick Start

```bash
# Install
pip install playwright
playwright install --with-deps chromium

# Run tests
pytest tests/e2e/test_login.py -v

# Run with headed browser
pytest tests/e2e/ --headed
```

## Project Structure

```
tests/e2e/
├── conftest.py              # pytest fixtures
├── playwright.config.ts     # Playwright config
├── pages/                   # Page Objects
│   ├── base_page.py
│   └── login_page.py
├── fixtures/
│   └── data_factory.py      # Test data
└── test_*.py               # Test modules
```

## Page Object Pattern

```python
from tests.e2e.pages.base_page import BasePage

class MarketPage(BasePage):
    OVERVIEW = ".market-overview"

    def is_loaded(self):
        return self.is_visible(self.OVERVIEW)
```

## Test Fixtures

```python
@pytest.fixture
def authenticated_page(page):
    page.goto("/login")
    page.fill("#username", "test_user")
    page.fill("#password", "test_password")
    page.click("#login-btn")
    page.wait_for_url("**/dashboard")
    return page
```

## Writing Tests

```python
def test_login_success(page):
    page.goto("/login")
    page.fill("#username", "user")
    page.fill("#password", "pass")
    page.click("#login-btn")
    expect(page).to_have_url("**/dashboard")
```

## Best Practices

1. Use Page Objects for selectors
2. Explicit waits over sleep
3. Independent tests
4. Use `expect()` assertions
5. Clean up test data

## CI/CD

GitHub Actions workflow in `.github/workflows/e2e-tests.yml`
