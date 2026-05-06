# Frontend Testing Guide

> **参考指南说明**:
> 本文件用于提供 Web 子系统的使用方法、操作指引、接口接入说明、排障提示或结构参考，帮助理解局部实现与协作方式。
> 其中的步骤、示例、端口、目录和操作建议应先与 `architecture/STANDARDS.md`、当前代码实现及最新验证结果核对；若涉及仓库执行流程、命令或协作约束，再补充参考根目录 `AGENTS.md`。本文件不得单独视为仓库共享规则或当前状态的唯一事实来源。


## Overview

This project has a comprehensive testing setup including unit tests, E2E tests, and CI/CD automation.

**Test Infrastructure**:
- **Unit/Integration Tests**: Vitest + Happy DOM + Vue Test Utils + MSW
- **E2E Tests**: Playwright (Chromium, Firefox, WebKit)
- **Accessibility Smoke**: `@axe-core/playwright`
- **Performance Gate**: Lighthouse CI (`lhci`)
- **CI/CD**: GitHub Actions
- **Coverage**: V8 (built into Vitest)

## Quick Start

### Port Configuration (.env)

```bash
FRONTEND_PORT=3020
FRONTEND_BACKUP_PORT=3021
BACKEND_PORT=8020
BACKEND_BACKUP_PORT=8021
```

Testing scripts should read ports from `.env` first, then use these defaults.

### Run All Tests Locally

```bash
# Install dependencies
npm install

# Run stable unit/integration gate
npm run test:unit:stable

# Run full unit suite
npm run test

# Run full E2E tests (Chromium only)
npm run test:e2e:chromium

# Run accessibility smoke
PLAYWRIGHT_EXTERNAL_FRONTEND=1 FRONTEND_BASE_URL=http://127.0.0.1:3020 E2E_FRONTEND_URL=http://127.0.0.1:3020 npm run test:e2e:axe

# Run Lighthouse CI smoke (isolated mock build, does not reuse PM2 frontend)
npm run test:e2e:lighthouse

# Run tests with coverage
npm run test:coverage
```

### Run Tests by Browser

```bash
# Chromium (Chrome/Edge)
npm run test:e2e:chromium

# Firefox
npm run test:e2e:firefox

# WebKit (Safari)
npm run test:e2e:webkit

# All browsers
npm run test:e2e
```

## Test Structure

```
web/frontend/
├── src/
│   ├── api/
│   │   ├── __tests__/          # Unit tests for API modules
│   │   │   ├── adapters/       # Adapter tests
│   │   │   ├── services/       # Service tests
│   │   │   └── types/          # Type validation tests
│   │   └── composables/
│   │       └── __tests__/      # Composable tests
│   └── mock/                   # Mock data for testing
├── tests/
│   ├── e2e/                    # E2E test suites
│   │   ├── market-data.spec.ts
│   │   └── strategy-management.spec.ts
│   └── unit/                   # Additional unit tests
├── vitest.config.mts           # Vitest configuration
├── playwright.config.js        # Playwright configuration
└── .github/
    └── workflows/
        └── test.yml            # CI/CD workflow
```

## Unit Tests (Vitest)

### Configuration

**File**: `vitest.config.mts`

- **Environment**: Happy DOM (lightweight DOM implementation)
- **Network Mocking**: MSW (`vitest.setup.ts` + `tests/mocks/server.ts`)
- **Coverage Provider**: V8
- **Reporters**: Text, JSON, HTML, LCOV

### Running Unit Tests

```bash
# Run once
npm run test

# Stable gate
npm run test:unit:stable

# Watch mode
npm run test:watch

# With coverage
npm run test:coverage
```

### Writing Unit Tests

```typescript
import { describe, it, expect } from 'vitest';
import { MarketAdapter } from '@/api/adapters/marketAdapter';

describe('MarketAdapter', () => {
  it('should adapt market overview data', () => {
    const mockResponse = {
      success: true,
      data: { /* ... */ }
    };

    const result = MarketAdapter.adaptMarketOverview(mockResponse);

    expect(result).toBeDefined();
    expect(result.marketStats).toBeDefined();
  });
});
```

## E2E Tests (Playwright)

### Configuration

**File**: `playwright.config.js`

**Features**:
- Multi-browser support (Chromium, Firefox, WebKit)
- Automatic dev server startup
- Screenshot/video on failure
- GitHub Actions annotations
- Canonical user-facing locator policy (`getByRole/getByText/getByTestId`)

**Test Timeouts**:
- Dev server startup: 120 seconds
- Test default: 30 seconds
- CI retries: 2 attempts

### Running E2E Tests

```bash
# All browsers
npm run test:e2e

# Stable shared-PM2 subset
PLAYWRIGHT_EXTERNAL_FRONTEND=1 FRONTEND_BASE_URL=http://127.0.0.1:3020 E2E_FRONTEND_URL=http://127.0.0.1:3020 npm run test:e2e:stable

# Full Chromium suite against the current PM2 frontend
PLAYWRIGHT_EXTERNAL_FRONTEND=1 FRONTEND_BASE_URL=http://127.0.0.1:3020 E2E_FRONTEND_URL=http://127.0.0.1:3020 npx playwright test --config playwright.config.js --project=chromium

# Specific browser
npm run test:e2e:chromium
npm run test:e2e:firefox
npm run test:e2e:webkit

# Accessibility smoke
PLAYWRIGHT_EXTERNAL_FRONTEND=1 FRONTEND_BASE_URL=http://127.0.0.1:3020 E2E_FRONTEND_URL=http://127.0.0.1:3020 npm run test:e2e:axe

# Lighthouse CI smoke
npm run test:e2e:lighthouse

# With UI (debugging)
npx playwright test --ui
```

Latest verified runtime note:
- `2026-05-07`: shared-PM2 stable subset `chromium 10/10` passed
- `2026-05-07`: shared-PM2 full Chromium project `295/295` passed via `PLAYWRIGHT_EXTERNAL_FRONTEND=1`

### Writing E2E Tests

```typescript
import { test, expect } from '@playwright/test';

test('should display market overview', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByTestId('market-overview')).toBeVisible();
  await expect(page.getByText('Market Statistics')).toBeVisible();
});
```

### Debugging E2E Tests

```bash
# Run in debug mode (with headed browser)
npx playwright test --debug

# Run with UI
npx playwright test --ui

# Show browser
npx playwright test --headed

# Specific test
npx playwright test --grep "should display market"
```

### Legacy Playwright Scripts

`web/frontend/playwright.config.ts` 仍保留给历史 PM2 / 视觉专项脚本使用，但它不是标准 Web E2E 主线。新增浏览器回归用例一律进入 `tests/e2e/**` 并由 `playwright.config.js` 执行。

## CI/CD Pipeline

### GitHub Actions Workflow

**File**: `.github/workflows/test.yml`

**Triggered on**:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`
- Manual workflow dispatch

### Pipeline Stages

1. **Unit Tests**
   - Runs on Ubuntu latest
   - Node.js 20
   - Generates coverage report
   - Uploads to Codecov

2. **E2E Tests (Chromium)**
   - Runs on Ubuntu latest
   - Timeout: 30 minutes
   - Uploads test results and screenshots

3. **E2E Tests (Firefox)**
   - Same setup as Chromium
   - Separate job for cross-browser validation

4. **E2E Tests (WebKit)**
   - Same setup as Chromium
   - Safari-compatible rendering

5. **Test Summary**
   - Aggregates all test results
   - Fails if any job failed
   - Posts summary to GitHub

### CI/CD Artifacts

**Coverage Reports**:
- Retention: 30 days
- Format: HTML + LCOV
- Location: `coverage/`

**Playwright Reports**:
- Retention: 30 days
- Location: `playwright-report/`

**Screenshots** (on failure):
- Retention: 7 days
- Location: `test-results/`

## Test Coverage

### Current Coverage

| Module      | Coverage | Status |
|-------------|----------|--------|
| Strategy    | ~90%     | ✅     |
| Market      | ~80%     | ✅     |
| API Types   | ~95%     | ✅     |
| Adapters    | ~85%     | ✅     |
| Composables | ~85%     | ✅     |

### Coverage Goals

- **Unit Tests**: 80%+ coverage
- **E2E Tests**: Critical user journey coverage
- **Cross-Browser**: 100% feature parity

## Test Scenarios

### E2E Test Coverage

**Market Data Module** (19 scenarios):
- ✅ Page loading and navigation
- ✅ Market overview display
- ✅ Fund flow chart rendering
- ✅ K-line chart display
- ✅ Desktop layout validation (4 resolutions)
- ✅ API failure automatic degradation
- ✅ Error handling and recovery
- ✅ Accessibility validation

**Strategy Management Module** (21 scenarios):
- ✅ Strategy list and cards
- ✅ Create strategy dialog
- ✅ Strategy detail view
- ✅ Backtest panel
- ✅ Desktop layout validation
- ✅ Error handling

### Cross-Browser Testing

**Supported Browsers**:
- ✅ Chromium (Chrome, Edge)
- ✅ Firefox
- ✅ WebKit (Safari)

**Desktop Resolutions**:
- 1920x1080 (Full HD)
- 1680x1050 (Widescreen)
- 1440x900 (Laptop)
- 1366x768 (Small laptop)

## Best Practices

### Unit Tests

1. **Test Isolation**: Each test should be independent
2. **Mock External Dependencies**: Use mock data for API calls
3. **Descriptive Names**: Test names should describe what they test
4. **Arrange-Act-Assert**: Structure tests clearly

```typescript
it('should return mock data when API fails', () => {
  // Arrange
  const failedResponse = { success: false, data: null };

  // Act
  const result = MarketAdapter.adaptMarketOverview(failedResponse);

  // Assert
  expect(result).toBeDefined();
  expect(result.marketStats.totalStocks).toBe(10);
});
```

### E2E Tests

1. **User-Centric**: Test user workflows, not implementation details
2. **Wait Strategies**: Use Playwright's auto-waiting features
3. **Selective Testing**: Use test IDs instead of CSS selectors when possible
4. **Data Cleanup**: Reset state between tests

```typescript
test('should create strategy', async ({ page }) => {
  await page.goto('/strategy');
  await page.click('[data-testid="create-strategy-button"]');
  await page.fill('[data-testid="strategy-name-input"]', 'Test Strategy');
  await page.click('[data-testid="submit-button"]');

  // Wait for success message
  await expect(page.getByText('Strategy created')).toBeVisible();
});
```

## Troubleshooting

### Unit Tests Fail

**Issue**: Import resolution errors

**Solution**:
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Issue**: Type errors in tests

**Solution**:
```bash
# Regenerate types
npm run type-check
```

### E2E Tests Fail

**Issue**: Browser not installed

**Solution**:
```bash
# Install specific browser
npx playwright install chromium
npx playwright install firefox
npx playwright install webkit

# Install all
npx playwright install --with-deps
```

**Issue**: Port already in use

**Solution**:
```bash
# Kill process on frontend port (default 3020)
lsof -ti:${FRONTEND_PORT:-3020} | xargs kill -9

# Or override by env
FRONTEND_PORT=3020 npm run test:e2e
BACKEND_PORT=8020 npm run test:e2e
```

**Issue**: Tests timeout

**Solution**:
```bash
# Increase timeout in playwright.config.js
timeout: 120 * 1000  // 120 seconds
```

### CI/CD Failures

**Issue**: Tests pass locally but fail in CI

**Common causes**:
1. Environment variables not set
2. Browser dependencies missing
3. Timezone differences
4. Resource constraints

**Solution**: Check CI logs for specific errors

## Continuous Improvement

### Adding New Tests

1. **Unit Test**: Add alongside source code in `src/**/__tests__/`
2. **E2E Test**: Add to `tests/e2e/` directory
3. **Update Coverage**: Run `npm run test:coverage` to verify
4. **Update Docs**: Document new test scenarios

### Test Maintenance

**Weekly**:
- Review failed tests
- Update flaky tests
- Check coverage trends

**Monthly**:
- Remove obsolete tests
- Refactor duplicated test code
- Update test documentation

## Resources

- **Vitest Docs**: https://vitest.dev/
- **Playwright Docs**: https://playwright.dev/
- **GitHub Actions**: https://docs.github.com/en/actions
- **Testing Best Practices**: https://kentcdodds.com/blog/common-mistakes-with-react-testing-library

## Status

**Last Updated**: 2025-12-25

**Current Status**: ✅ All systems operational

- Unit Tests: ✅ Passing (15/15)
- E2E Tests: ✅ Configured
- CI/CD: ✅ Configured
- Coverage: ✅ >80% target met
