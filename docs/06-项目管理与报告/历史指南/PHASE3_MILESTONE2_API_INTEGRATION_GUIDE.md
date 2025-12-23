# Phase 3 Milestone 2: Real API Endpoint Integration Guide

**Status**: ✅ Completed
**Date**: 2025-12-05
**Target Completion**: Week 1-2 of Phase 3

## Overview

Milestone 2 introduces a flexible API integration system that allows tests to seamlessly switch between mock and real APIs without code changes. This enables:

- **Offline Development**: Tests run with mocks when backend is unavailable
- **Integration Testing**: Tests can connect to real backend for integration validation
- **CI/CD Compatibility**: Same tests work in both CI (mocks) and staging/production (real APIs)
- **Performance Testing**: Real API calls can be monitored for performance metrics

## New Modules Created

### 1. API Configuration Module (`tests/config/api-config.ts`)

**Purpose**: Centralized endpoint definitions and URL building utilities

**Key Functions**:

```typescript
// Get full API URL
const url = getApiUrl('/api/dashboard/overview');
// Returns: 'http://localhost:8000/api/dashboard/overview'

// Replace path parameters
const url = buildApiUrl('/api/market/stock/:symbol/detail', { symbol: 'AAPL' });
// Returns: 'http://localhost:8000/api/market/stock/AAPL/detail'

// Get endpoint from configuration
const endpoint = getEndpoint('dashboard', 'overview');
// Returns: '/api/dashboard/overview'

// Validate endpoint exists
if (endpointExists('market', 'overview')) {
  // Endpoint is available
}

// Get all endpoints in category
const dashboardEndpoints = getCategoryEndpoints('dashboard');
// Returns: { overview: '/api/dashboard/overview', portfolio: '...', ... }

// List all categories
const categories = getAvailableCategories();
// Returns: ['dashboard', 'market', 'trading', 'strategies', 'risk', ...]
```

**Supported Endpoint Categories**:

| Category | Endpoints | Purpose |
|----------|-----------|---------|
| `dashboard` | overview, portfolio, performance | Dashboard widgets |
| `market` | overview, search, stockDetail, indicators, historicalData | Market data |
| `trading` | orders, positions, executeOrder, cancelOrder | Trading operations |
| `portfolio` | positions, performance, allocation | Portfolio management |
| `risk` | metrics, alerts, analysis | Risk monitoring |
| `strategies` | list, create, detail, backtest, performance | Strategy management |
| `technicalAnalysis` | indicators, patterns, signals | Technical analysis |
| `tasks` | list, create, detail, update, delete | Task management |
| `settings` | account, notifications, apiKeys, preferences | User settings |
| `monitoring` | realTime, alerts | Real-time monitoring |
| `wencai` | queries, search | Natural language search |

### 2. Test Environment Configuration (`tests/helpers/test-env.ts`)

**Purpose**: Environment detection and test configuration management

**Key Functions**:

```typescript
// Check if mocks should be used
if (shouldUseMocks()) {
  // Use mock APIs
}

// Check if real APIs should be used
if (shouldUseRealApi()) {
  // Use real backend
}

// Get API base URL
const baseUrl = getApiBaseUrl();

// Get frontend base URL
const frontendUrl = getFrontendBaseUrl();

// Validate environment configuration
await validateTestEnvironment();

// Setup for specific mode
await setupTestMode('mock', {
  API_BASE_URL: 'http://localhost:8000',
  ENABLE_VISUAL_REGRESSION: false,
});

// Get environment summary
const env = getEnvironmentSummary();
console.log(env);
// {
//   USE_REAL_API: false,
//   USE_MOCK_API: true,
//   API_BASE_URL: 'http://localhost:8000',
//   FRONTEND_BASE_URL: 'http://localhost:3000',
//   ENABLE_VISUAL_REGRESSION: false,
//   ...
// }
```

**Environment Variables**:

| Variable | Default | Purpose |
|----------|---------|---------|
| `USE_REAL_API` | `'false'` | Switch to real API mode (true) or mock (false) |
| `API_BASE_URL` | `'http://localhost:8000'` | Base URL for real API calls |
| `FRONTEND_BASE_URL` | `'http://localhost:3000'` | Frontend URL for page navigation |
| `TEST_ENVIRONMENT` | `'development'` | Environment: development, staging, production |
| `ENABLE_VISUAL_REGRESSION` | `'false'` | Enable visual regression testing |
| `ENABLE_PERFORMANCE_MONITORING` | `'true'` | Enable performance metrics collection |
| `ENABLE_ACCESSIBILITY_TESTS` | `'false'` | Enable accessibility checks |
| `ENABLE_VIDEO_RECORDING` | `'false'` | Record test videos |
| `ENABLE_SCREENSHOTS_ON_FAILURE` | `'true'` | Capture screenshots on failures |
| `SLOW_MOTION_MS` | `'0'` | Add slowdown to interactions (ms) |
| `TRACE_ENABLED` | `'false'` | Enable Playwright trace recording |
| `NAVIGATION_TIMEOUT_MS` | `'30000'` | Navigation timeout (ms) |
| `ACTION_TIMEOUT_MS` | `'10000'` | Action timeout (ms) |
| `EXPECT_TIMEOUT_MS` | `'5000'` | Expectation timeout (ms) |

### 3. Conditional Mocking Module (`tests/helpers/conditional-mocking.ts`)

**Purpose**: Seamlessly switch between mock and real API calls based on environment

**Key Functions**:

```typescript
// Setup APIs conditionally based on environment
await setupApi(page, {
  // If USE_REAL_API=true: No mocking (real API calls)
  // If USE_MOCK_API=true: All APIs are mocked
  includeCategories: ['dashboard', 'market'],  // Specific categories
  mockDelay: 0,  // Simulate network latency
});

// Alternative: Setup all mocks
await setupAllMocks(page, mockDelay);

// Alternative: Disable all mocking (use real APIs)
await setupRealApi(page);

// Setup specific endpoint conditionally
await setupConditionalEndpoint(
  page,
  '**/api/dashboard/**',
  async (route) => {
    // Return mock data
    await route.respond({
      status: 200,
      body: JSON.stringify(mockData),
    });
  }
);

// Check if mocks are active
if (isMockEnabled()) {
  console.log('Using mock APIs');
}

// Get mock configuration
const config = getMockConfiguration();
// { enabled: true, apiBaseUrl: 'http://localhost:8000' }

// Configure error simulation
await configureMockErrors(page, {
  enabled: true,
  statusCode: 500,
  message: 'Internal Server Error',
  categories: ['dashboard', 'market'],
});

// Apply artificial delay to mocks (simulate slow network)
await applyMockDelay(page, 2000);  // 2 second delay
```

## Usage Patterns

### Pattern 1: Basic Setup with Conditional APIs

```typescript
test.beforeEach(async ({ page }) => {
  // Automatically use mocks or real APIs based on environment
  await setupApi(page);

  // Navigate using configured frontend URL
  await page.goto(TEST_ENV.FRONTEND_BASE_URL + '/dashboard');
});
```

**Environment Variables**:
```bash
# Use mocks (default)
npm test

# Use real APIs
USE_REAL_API=true npm test

# Use real APIs with custom URL
USE_REAL_API=true API_BASE_URL=https://api.staging.com npm test
```

### Pattern 2: Category-Specific Mocking

```typescript
test('test with specific mocks', async ({ page }) => {
  // Only mock dashboard APIs; use real APIs for market data
  await setupApi(page, {
    includeCategories: ['dashboard'],
    excludeCategories: ['market'],
  });

  await page.goto('/dashboard');
});
```

### Pattern 3: Simulate Network Issues

```typescript
test('test error handling', async ({ page }) => {
  if (isMockEnabled()) {
    // Simulate error responses
    await configureMockErrors(page, {
      enabled: true,
      statusCode: 500,
      categories: ['dashboard'],
    });
  }

  // Test error handling
  await page.goto('/dashboard');
  const errorMessage = page.locator('[data-testid="error-message"]');
  await expect(errorMessage).toBeVisible();
});
```

### Pattern 4: Conditional Real vs. Mock

```typescript
test('integration test', async ({ page }) => {
  if (shouldUseRealApi()) {
    // Real API mode - connect to actual backend
    await setupRealApi(page);
    console.log(`Testing against: ${getApiBaseUrl()}`);
  } else {
    // Mock mode - use test data
    await setupAllMocks(page);
  }

  await page.goto('/dashboard');
});
```

### Pattern 5: Multiple Test Suites

```typescript
test.describe('Dashboard - Mock Mode', () => {
  test.beforeEach(async ({ page }) => {
    await setupAllMocks(page);
  });

  test('should show mock data', async ({ page }) => {
    // Tests run with mocks
  });
});

test.describe('Dashboard - Real API Mode', () => {
  test.beforeEach(async ({ page }) => {
    // Only run these if real API is available
    test.skip(!shouldUseRealApi(), 'Real API mode not enabled');
    await setupRealApi(page);
  });

  test('should connect to real backend', async ({ page }) => {
    // Integration tests with real API
  });
});
```

## Migration Guide: Updating Existing Tests

### Before (Phase 2)

```typescript
test.beforeEach(async ({ page }) => {
  // Only mocked APIs
  await mockDashboardApis(page);
  await page.goto('/dashboard');
});
```

### After (Phase 3)

```typescript
import { setupApi } from '../helpers/conditional-mocking';
import { TEST_ENV } from '../helpers/test-env';

test.beforeEach(async ({ page }) => {
  // Conditional APIs based on environment
  await setupApi(page, {
    includeCategories: ['dashboard'],
  });

  // Use configured frontend URL
  await page.goto(`${TEST_ENV.FRONTEND_BASE_URL}/dashboard`);
});
```

**Key Changes**:
1. Replace `mockDashboardApis()` with `setupApi()` and category configuration
2. Use `TEST_ENV.FRONTEND_BASE_URL` instead of hardcoded URLs
3. Tests now work with both mock and real APIs

## Example: Updated Test File

See `tests/e2e/dashboard-page-phase3.spec.ts` for a complete example demonstrating:

- Conditional API setup
- Environment validation
- Proper timeout usage
- Mock vs. real API handling
- Error simulation
- Performance measurement

## Implementation Checklist

### For New Tests

- [ ] Import `setupApi` from `conditional-mocking.ts`
- [ ] Import `TEST_ENV` from `test-env.ts`
- [ ] Use `setupApi()` in `beforeEach`
- [ ] Use `TEST_ENV.FRONTEND_BASE_URL` for navigation
- [ ] Use `TEST_ENV.NAVIGATION_TIMEOUT_MS` for timeouts
- [ ] Use `isMockEnabled()` to conditionally test error handling
- [ ] Run with both `npm test` (mocks) and `USE_REAL_API=true npm test` (real)

### For Existing Tests

Priority order for migration:

1. **High Priority** (Critical pages): Dashboard, Market, Stock Detail
2. **Medium Priority** (Important pages): Technical Analysis, Trading, Settings
3. **Low Priority** (Supporting pages): Risk Monitor, Task Management, Strategies

**Migration Template**:
```typescript
// Add imports
import { setupApi, isMockEnabled } from '../helpers/conditional-mocking';
import { TEST_ENV } from '../helpers/test-env';

// Update beforeEach
test.beforeEach(async ({ page }) => {
  // Replace mock function with setupApi
  await setupApi(page, {
    includeCategories: ['categoryName'],
  });

  // Replace hardcoded URL
  await page.goto(`${TEST_ENV.FRONTEND_BASE_URL}/path`);
});

// Update error handling tests
test('error handling', async ({ page }) => {
  if (isMockEnabled()) {
    await configureMockErrors(page, { enabled: true, statusCode: 500 });
  }
  // Rest of test
});
```

## CI/CD Integration

### GitHub Actions Configuration

The `e2e-tests.yml` workflow automatically:

1. **Mock Mode (CI)**: Runs tests with `USE_MOCK_API=true` (default)
2. **Real API Mode (Staging)**: Can be triggered with `USE_REAL_API=true`

**Example with multiple modes**:

```yaml
strategy:
  matrix:
    test-mode: ['mock', 'real']
    browser: [chromium, firefox, webkit]

steps:
  - name: Run E2E tests
    env:
      USE_REAL_API: ${{ matrix.test-mode == 'real' }}
      API_BASE_URL: ${{ secrets.STAGING_API_URL || 'http://localhost:8000' }}
    run: npm test
```

## Testing Matrix

### Local Development

```bash
# 1. Start backend
python -m uvicorn web.backend.app.main:app --port 8000

# 2. Start frontend
npm run dev -- --port 3000

# 3. Run tests with mocks (no backend needed)
npm test

# 4. Run tests against real backend
USE_REAL_API=true npm test

# 5. Run tests with visual regression
ENABLE_VISUAL_REGRESSION=true npm test

# 6. Run tests with performance monitoring
ENABLE_PERFORMANCE_MONITORING=true npm test
```

### CI/CD Pipeline

```bash
# Pull Request (mocks only - fast)
npm test  # ~5 minutes

# Merge to main (mocks + real API staging)
USE_REAL_API=true API_BASE_URL=https://api.staging.com npm test  # ~10 minutes

# Deploy to production (real API validation)
USE_REAL_API=true API_BASE_URL=https://api.prod.com npm test --testNamePattern="critical"
```

## Performance Considerations

### Mock API Mode
- ✅ Fast test execution (no network latency)
- ✅ Deterministic results
- ✅ No backend dependency
- ✅ Offline testing
- ❌ Doesn't catch backend issues

### Real API Mode
- ✅ Tests actual API behavior
- ✅ Catches integration issues
- ✅ Realistic data validation
- ❌ Slower test execution
- ❌ Requires backend availability
- ❌ Network-dependent flakiness

### Recommended Strategy

```
Development:  Mock APIs (fast feedback)
              ↓
Pre-commit:   Both Mock and Real APIs (quality gate)
              ↓
CI on PR:     Mock APIs only (speed, no backend)
              ↓
Merge to main: Real APIs on staging (integration validation)
              ↓
Deploy:       Real APIs on production (smoke tests)
```

## Troubleshooting

### Tests fail with real API but pass with mocks

**Problem**: Test works with mocks but fails against real backend

**Solution**:
```typescript
// Add debugging
if (shouldUseRealApi()) {
  test.step(`[Real API] ${test.info().title}`, async () => {
    // Add console logging
    console.log(`API Base: ${getApiBaseUrl()}`);
    console.log(`Frontend: ${getFrontendBaseUrl()}`);
  });
}
```

### API requests timeout in CI

**Problem**: Real API tests timeout in CI pipeline

**Solution**:
```typescript
// Increase timeout for CI
const timeout = isEnvironment('production') ? 30000 : 10000;
await page.goto(url, { timeout });
```

### Environment variables not applied

**Problem**: Environment variables not being read

**Solution**:
```bash
# Verify environment variables are set
echo $USE_REAL_API
echo $API_BASE_URL

# Run tests with explicit environment
USE_REAL_API=true API_BASE_URL=http://localhost:8000 npm test
```

## Next Steps

### Milestone 3: Visual Regression Testing
- [ ] Integrate Percy for visual baselines
- [ ] Capture visual snapshots for all critical pages
- [ ] Set up visual diff reporting

### Milestone 4: Performance Profiling
- [ ] Create performance monitoring helpers
- [ ] Set performance budgets per page
- [ ] Add performance alerts to CI

### Milestone 5: Coverage Reporting
- [ ] Generate coverage dashboards
- [ ] Track coverage trends
- [ ] Set coverage thresholds

## References

- [api-config.ts](../tests/config/api-config.ts) - Endpoint definitions
- [test-env.ts](../tests/helpers/test-env.ts) - Environment configuration
- [conditional-mocking.ts](../tests/helpers/conditional-mocking.ts) - API switching logic
- [dashboard-page-phase3.spec.ts](../tests/e2e/dashboard-page-phase3.spec.ts) - Example implementation
- [PHASE3_CI_CD_INTEGRATION_PLAN.md](./PHASE3_CI_CD_INTEGRATION_PLAN.md) - Phase 3 overview

---

**Created**: 2025-12-05
**Phase**: Phase 3 Milestone 2 - Real API Endpoint Integration
**Status**: Complete ✅
