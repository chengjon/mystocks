# Phase 3: CI/CD Integration & Advanced Testing

## Overview

Phase 3 focuses on automating the E2E testing framework through CI/CD pipelines, adding real API integration, and implementing advanced testing features for production readiness.

## Phase 3 Milestones

### Milestone 1: GitHub Actions CI/CD (Week 1)

#### 1.1 Automated Test Execution

**Created**:
- `.github/workflows/e2e-tests.yml` - Multi-browser test workflow
  - Runs on: push to main/develop, PR, daily schedule (2 AM UTC)
  - Matrix: Chromium, Firefox, WebKit
  - Parallel execution with artifact uploads
  - Test report summary generation
  - PR comments with results

**Configuration**:
```yaml
Browsers: chromium, firefox, webkit
Timeout: 30 minutes per browser
Retries: 2 (CI), 1 (local)
Workers: Parallel (optimized for CI)
Reports: HTML, JSON, Line-based
Artifacts: 30-day retention
```

**Key Features**:
- ✅ Multi-browser parallel execution
- ✅ Automatic artifact collection
- ✅ PR comments with test status
- ✅ Daily scheduled runs
- ✅ Test result summaries

#### 1.2 Test Reporting

**Reports Configuration**:
- HTML report at `playwright-report/index.html`
- JSON test results for parsing
- Line-based console output
- Screenshot/video on failure

**Metrics Tracked**:
- Total tests, passed, failed, skipped
- Execution time per test
- Browser-specific results
- Flaky test detection

### Milestone 2: Real API Integration (Week 1-2)

#### 2.1 API Endpoint Configuration

**Create API configuration module**:
```typescript
// tests/config/api-config.ts
export const API_ENDPOINTS = {
  dashboard: '/api/dashboard/overview',
  market: '/api/market/overview',
  stock: '/api/market/stock/:symbol/detail',
  orders: '/api/trading/orders',
  positions: '/api/portfolio/positions',
  strategies: '/api/strategies',
  risk: '/api/risk/metrics',
  tasks: '/api/tasks',
  settings: '/api/settings'
};

export const getApiUrl = (endpoint: string, baseUrl: string = process.env.API_BASE_URL) => {
  return `${baseUrl}${endpoint}`;
};
```

#### 2.2 Environment-Based Test Configuration

**Setup environment detection**:
```typescript
// tests/helpers/test-env.ts
export const TEST_ENV = {
  USE_REAL_API: process.env.USE_REAL_API === 'true',
  USE_MOCK_API: process.env.USE_REAL_API !== 'true',
  API_BASE_URL: process.env.API_BASE_URL || 'http://localhost:8000',
  FRONTEND_BASE_URL: process.env.FRONTEND_BASE_URL || 'http://localhost:3000',
};

export const shouldUseMocks = () => TEST_ENV.USE_MOCK_API;
export const shouldUseRealApi = () => TEST_ENV.USE_REAL_API;
```

#### 2.3 Conditional Mock/Real API Tests

**Update test helpers**:
```typescript
// tests/helpers/conditional-mocking.ts
export async function setupApi(page: Page, options: { useMocks?: boolean } = {}) {
  const useMocks = options.useMocks ?? shouldUseMocks();

  if (useMocks) {
    await mockDashboardApis(page);
  } else {
    // Real API - no mocking
    console.log('Using real API endpoints from', TEST_ENV.API_BASE_URL);
  }
}
```

### Milestone 3: Visual Regression Testing (Week 2)

#### 3.1 Percy Integration

**Setup**:
```bash
npm install --save-dev @percy/cli @percy/playwright
```

**Configuration**:
```typescript
// tests/helpers/visual-regression.ts
import { percySnapshot } from '@percy/playwright';

export async function captureVisualSnapshot(
  page: Page,
  name: string,
  options?: PercySnapshotOptions
) {
  await percySnapshot(page, name, options);
}
```

**Usage**:
```typescript
test('Dashboard visual regression', async ({ page }) => {
  await page.goto('/dashboard');
  await captureVisualSnapshot(page, 'Dashboard - Full Page');

  // Interact and capture again
  await page.click('[data-testid="filter-button"]');
  await captureVisualSnapshot(page, 'Dashboard - With Filters');
});
```

#### 3.2 Key Pages for Visual Testing

- Dashboard overview with various themes
- Market list with different sort orders
- Stock detail chart with different timeframes
- Settings pages with form states
- Modal and dialog states

### Milestone 4: Performance Profiling (Week 2-3)

#### 4.1 Performance Monitoring Integration

**Setup performance tracking**:
```typescript
// tests/helpers/performance-monitor.ts
export interface PerformanceMetrics {
  pageLoadTime: number;
  timeToFirstPaint: number;
  largestContentfulPaint: number;
  firstInputDelay: number;
  cumulativeLayoutShift: number;
  apiResponseTime: number;
}

export async function capturePerformanceMetrics(page: Page): Promise<PerformanceMetrics> {
  const metrics = await page.evaluate(() => {
    const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
    const paintEntries = performance.getEntriesByType('paint');

    return {
      pageLoadTime: navigation.loadEventEnd - navigation.fetchStart,
      timeToFirstPaint: paintEntries.find(e => e.name === 'first-paint')?.startTime || 0,
      largestContentfulPaint: 0, // Will be captured separately
      firstInputDelay: 0, // Will be captured separately
      cumulativeLayoutShift: 0, // Will be captured separately
    };
  });

  return metrics;
}
```

#### 4.2 Performance Baselines

**Define performance budgets**:
```typescript
// tests/config/performance-budgets.ts
export const PERFORMANCE_BUDGETS = {
  dashboard: { pageLoadTime: 2000, apiResponseTime: 1500 },
  market: { pageLoadTime: 2000, apiResponseTime: 1500 },
  stockDetail: { pageLoadTime: 3000, apiResponseTime: 2000 },
  technicalAnalysis: { pageLoadTime: 2000, apiResponseTime: 1500 },
  tradeManagement: { pageLoadTime: 2000, apiResponseTime: 1500 },
  strategyManagement: { pageLoadTime: 2000, apiResponseTime: 1500 },
  riskMonitor: { pageLoadTime: 2000, apiResponseTime: 1500 },
  taskManagement: { pageLoadTime: 2000, apiResponseTime: 1500 },
  settings: { pageLoadTime: 2000, apiResponseTime: 1500 },
};
```

### Milestone 5: Test Coverage Reporting (Week 3)

#### 5.1 Coverage Dashboard

**Setup coverage tracking**:
```bash
npx playwright test --reporter=json > playwright-report/coverage.json
```

**Generate coverage reports**:
- Page coverage by test count
- Test category coverage
- Browser-specific coverage
- Trend analysis (weekly/monthly)

#### 5.2 Coverage Thresholds

**Define minimum coverage requirements**:
```typescript
export const COVERAGE_THRESHOLDS = {
  pages: { minimum: 8, target: 12 },
  tests: { minimum: 200, target: 300 },
  functionality: { minimum: 30, target: 50 },
  errorScenarios: { minimum: 10, target: 20 },
  performanceBenchmarks: { minimum: 15, target: 25 },
};
```

## Implementation Timeline

### Week 1
- ✅ GitHub Actions workflow setup (e2e-tests.yml)
- API configuration module (api-config.ts)
- Environment detection (test-env.ts)
- Mock/Real API switching logic

### Week 2
- Percy visual regression integration
- Baseline visual comparisons
- Performance monitoring setup
- API response time tracking

### Week 3
- Coverage dashboard setup
- Coverage threshold validation
- Trend reporting
- Documentation and handoff

## Success Criteria

### CI/CD Integration
- ✅ Tests run automatically on every push/PR
- ✅ Multi-browser execution completes in < 30 minutes
- ✅ PR comments show test status
- ✅ Artifacts retained for 30 days

### Real API Integration
- ✅ Tests can switch between mock and real APIs via environment variable
- ✅ Real API tests pass with valid backend
- ✅ Mock tests pass for offline development
- ✅ No code changes needed to switch between modes

### Visual Regression Testing
- ✅ Visual baselines captured for all critical pages
- ✅ Visual regressions detected automatically
- ✅ Diff reports available for review
- ✅ < 5% false positive rate

### Performance Profiling
- ✅ Page load times < 3 seconds
- ✅ API responses < 2 seconds
- ✅ Performance budgets tracked
- ✅ Performance regressions alerted

### Coverage Reporting
- ✅ Coverage dashboard shows page-by-page breakdown
- ✅ Coverage trends tracked over time
- ✅ Coverage threshold validation on PR
- ✅ Coverage reports generated weekly

## Files to Create/Modify

### New Files
1. `.github/workflows/e2e-tests.yml` - Main CI/CD workflow ✅
2. `tests/config/api-config.ts` - API endpoint configuration
3. `tests/helpers/test-env.ts` - Environment detection
4. `tests/helpers/conditional-mocking.ts` - Mock/Real API switching
5. `tests/helpers/visual-regression.ts` - Visual testing helpers
6. `tests/helpers/performance-monitor.ts` - Performance tracking
7. `tests/config/performance-budgets.ts` - Performance baselines
8. `.percy.yml` - Percy configuration
9. `docs/PHASE3_CI_CD_SETUP_GUIDE.md` - Setup documentation

### Modified Files
1. `playwright.config.ts` - Add reporting configuration
2. `tests/e2e/*.spec.ts` - Update tests for conditional mocking
3. `package.json` - Add dependencies and scripts

## Next Steps After Phase 3

- Phase 4: Advanced Features
  - WebSocket real-time data testing
  - Load testing integration
  - Security testing (XSS, CSRF, injection)
  - Accessibility testing enhancements

- Phase 5: Coverage Expansion
  - P2 page testing
  - Advanced user scenarios
  - Integration tests
  - Cross-browser compatibility

---

**Status**: Phase 3 Initiated ✅
**Target Completion**: 3 weeks
**Team Size**: 1-2 developers
**Scope**: CI/CD automation + Advanced testing features
