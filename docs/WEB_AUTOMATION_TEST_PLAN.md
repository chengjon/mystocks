# Web Automation Test Plan (AI-Enhanced Strategy V2)

This document outlines the **Revised AI-Enhanced Web Automation Testing Strategy**, incorporating multi-dimensional testing (Unit/Integration/E2E), test data management, and strict observability metrics to ensure the stability of the MyStocks web platform.

## 1. Core Testing Dimensions

We will expand beyond E2E to a Testing Pyramid approach:

| Type | Scope | Tool | Goal |
|------|-------|------|------|
| **Unit** | Components, Utils, Helpers | **Vitest** | Fast feedback on logic/rendering. |
| **Integration** | API <-> Frontend, Store State | **Vitest + Mocks** | Verify data flow and state mutations. |
| **E2E** | User Journeys, Menus, Auth | **Playwright** | Validate critical business paths. |
| **Visual** | UI Regression | **Playwright** | Detect CSS/Layout breaks. |
| **Performance** | Load Time, FCP, TTI | **Playwright** | Prevent performance regression. |

## 2. Architecture & Data Strategy

### 2.1 Directory Structure
```text
tests/
├── unit/               # [New] Vitest: Component & logic tests
│   ├── components/
│   └── utils/
├── e2e/                # Playwright: Browser tests
│   ├── critical/       # P0: Blockers (Menu, Auth)
│   ├── high/           # P1: Core Features (Trade, Data)
│   ├── medium/         # P2: UX/Edge cases
│   ├── visual/         # [New] Visual regression snapshots
│   └── performance/    # [New] Load time benchmarks
└── fixtures/
    ├── factory.ts      # [New] Test Data Factory
    ├── mocks/          # [New] API Mock definitions
    └── users.json
```

### 2.2 Test Data Factory (Standardized)
We will implement a Factory pattern to ensure data isolation and consistency.
```typescript
// tests/fixtures/factory.ts
export const TestDataFactory = {
  createValidUser: (role = 'user') => ({
    id: `user_${Date.now()}`,
    username: `test_${role}`,
    permissions: role === 'admin' ? ['*'] : ['read']
  }),
  createMockStockData: (symbol = 'AAPL') => ({
    symbol,
    price: Math.random() * 1000,
    timestamp: new Date().toISOString()
  }),
  createStandardApiResponse: (data) => ({
    success: true,
    code: 200,
    data: data,
    message: "Success"
  })
};
```

## 3. Implementation Roadmap

### Phase 1: Foundation & Critical Fixes (Current Week)
**Goal:** Fix broken menus (Immediate) + Establish Test Bed (Long-term).

1.  **Dependencies & Setup:**
    *   Install `vitest`, `@vitest/coverage-v8`.
    *   Configure Playwright for **Mocking** (Reduce backend dependency).
2.  **Menu Scanner (The "Fixer"):**
    *   Implement the automated "Menu Crawler" to identify 404/White Screens immediately.
3.  **Coverage & Isolation:**
    *   Enable coverage collection.
    *   Ensure tests do not share state (clean context per test).

### Phase 2: Report & Intelligence (2-4 Weeks)
1.  **Smart Reporting:** Implement a dashboard for test results.
2.  **Smart Selection:** Run only tests related to changed files (Git diff analysis).
3.  **Performance Baselines:** Fail builds if Main Menu load > 3s.

### Phase 3: AI & Self-Healing (1-2 Months)
1.  **Auto-Maintenance:** AI agent analyzes broken selectors and suggests fixes.
2.  **Flaky Detection:** Automated re-runs and logic analysis for unstable tests.

## 4. Key Metrics (KPIs)

| Metric | Target | Description |
|--------|--------|-------------|
| **Test Coverage** | ≥80% | Combined Statement/Branch coverage. |
| **Execution Time** | ≤10 min | Full suite parallel execution. |
| **Flaky Rate** | ≤2% | Percentage of tests requiring retries. |
| **Bug Detection** | ≥90% | Pre-production bug catch rate. |

## 5. Immediate Execution Plan (Day 1 Tasks)
1.  **Install Vitest** in `web/frontend`.
2.  **Create `TestDataFactory`**.
3.  **Implement `scan_menus.spec.ts`** (The Scanner) using the Factory mock data to ensure the frontend *can* render if data is correct, separating frontend bugs from backend 500s.

---
**Status:** Updated based on user feedback. Ready for execution of Phase 1.
