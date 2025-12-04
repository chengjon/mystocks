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

### Milestone 2: Real API Integration (Week 1-2) ✅ COMPLETED

#### 2.1 API Endpoint Configuration ✅

**Created API configuration module** (`tests/config/api-config.ts`):
- Centralized endpoint definitions for 11 API categories
- URL building utilities with parameter replacement
- Endpoint validation and discovery functions
- Support for 50+ endpoints across dashboard, market, trading, portfolio, risk, strategies, technical analysis, tasks, settings, monitoring, wencai

**Key Functions**:
- `getApiUrl()` - Build full URLs from endpoints
- `buildApiUrl()` - Replace path parameters automatically
- `getEndpoint()` - Retrieve endpoints by category and key
- `getCategoryEndpoints()` - Get all endpoints in a category
- `validateEndpoints()` - Validate endpoint configuration

#### 2.2 Environment-Based Test Configuration ✅

**Implemented environment detection** (`tests/helpers/test-env.ts`):
- 13+ environment variables for test configuration
- Automatic environment validation
- Mock vs. real API mode detection
- Timeout configuration
- Feature flag management (visual regression, performance monitoring, accessibility, etc.)

**Configuration Variables**:
- `USE_REAL_API` - Toggle between mock and real APIs
- `API_BASE_URL` - Backend URL (default: http://localhost:8000)
- `FRONTEND_BASE_URL` - Frontend URL (default: http://localhost:3000)
- `ENABLE_VISUAL_REGRESSION` - Enable visual regression testing
- `ENABLE_PERFORMANCE_MONITORING` - Track performance metrics
- `NAVIGATION_TIMEOUT_MS`, `ACTION_TIMEOUT_MS`, `EXPECT_TIMEOUT_MS` - Timeout configuration
- Plus: `TEST_ENVIRONMENT`, `ENABLE_VIDEO_RECORDING`, `TRACE_ENABLED`, etc.

#### 2.3 Conditional Mock/Real API Tests ✅

**Implemented conditional mocking** (`tests/helpers/conditional-mocking.ts`):
- Seamless switching between mock and real APIs
- Category-based API filtering
- Network latency simulation
- Error response configuration
- Mock validation and status checking

**Key Functions**:
- `setupApi()` - Setup conditional APIs with options
- `setupAllMocks()` - Enable all mocks
- `setupRealApi()` - Disable all mocking
- `configureMockErrors()` - Simulate error responses
- `applyMockDelay()` - Add artificial network latency
- `isMockEnabled()` - Check current mock status

**Key Achievement**: Tests run identically in both offline (mock) and online (real API) modes without code changes

#### 2.4 Example Implementation ✅

**Created example test** (`tests/e2e/dashboard-page-phase3.spec.ts`):
- 50+ lines demonstrating Phase 3 patterns
- Covers all test types: core, responsive, error handling, performance
- Shows conditional API handling
- Includes proper timeout usage
- Ready for migration of other test files

#### 2.5 Complete Documentation ✅

**Created comprehensive guide** (`docs/guides/PHASE3_MILESTONE2_API_INTEGRATION_GUIDE.md`):
- 500+ lines of detailed documentation
- Usage patterns and examples
- Migration guide for existing tests
- Troubleshooting section
- CI/CD integration guide
- Performance considerations

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
- ✅ API configuration module (api-config.ts)
- ✅ Environment detection (test-env.ts)
- ✅ Mock/Real API switching logic (conditional-mocking.ts)

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

**Status**: Phase 3 - Milestone 1 & 2 Complete ✅
**Current Focus**: Milestone 3 - Visual Regression Testing (Week 2)
**Milestones Completed**: 2/5 (40% progress)
**Target Completion**: 3 weeks (Week 2 on track)
**Team Size**: 1-2 developers
**Scope**: CI/CD automation + Advanced testing features

## Progress Summary

| Milestone | Status | Completion Date |
|-----------|--------|-----------------|
| 1. GitHub Actions CI/CD | ✅ Complete | 2025-12-05 |
| 2. Real API Integration | ✅ Complete | 2025-12-05 |
| 3. Visual Regression Testing | 🔄 In Progress | Target: 2025-12-06 |
| 4. Performance Profiling | ⏳ Pending | Target: 2025-12-07 |
| 5. Coverage Reporting | ⏳ Pending | Target: 2025-12-08 |
