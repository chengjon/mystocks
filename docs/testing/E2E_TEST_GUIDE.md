# MyStocks E2E Testing Guide

> **使用说明**:
> 本文件保留早期 E2E 设计草稿与 Python/pytest 风格示例，不是当前 Web E2E 主线、当前 Playwright 配置或测试门禁的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及测试执行流程、E2E 规范或协作约束，再结合 `docs/testing/TESTING_GUIDE.md`、`docs/testing/e2e/README.md` 与根目录 `AGENTS.md`。
>
> 2026-04 当前主线默认执行 `web/frontend/playwright.config.js`（`tests/e2e`），推荐命令为 `npm run test:e2e`、`npm run test:e2e:chromium`。

## Overview

End-to-End (E2E) testing framework for MyStocks using Playwright.

## Quick Start

```bash
cd /opt/claude/mystocks_spec/web/frontend
npx playwright install --with-deps chromium

# Run current standard suites
npm run test:e2e:chromium
npm run test:e2e

# Debug legacy/special cases only when the target doc explicitly requires it
npm run test:e2e:debug
```

> 下文保留的是历史 Page Object / pytest 风格示例，仅作背景参考。

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
