# Web Testing Tools Setup Guide

This document provides comprehensive setup and usage instructions for the web testing tools installed in the MyStocks project.

## 📋 All Available Tools Summary

### ✅ 已安装工具

| Tool | Version | Status | Purpose | Configuration |
|-------|----------|--------|----------|---------|
| **Playwright** | 1.56.1 | ✅ Active | E2E Testing | `web/frontend/playwright.config.ts` |
| **Cypress** | 15.8.2 | ✅ Installed | E2E Testing | `web/frontend/cypress.config.ts` |
| **K6** | Latest | ✅ Installed | Performance Testing | `tests/performance/k6-performance-test.ts` |
| **Lighthouse** | Latest | ✅ Installed | Performance Auditing | `lighthouse.config.json` |

### ✅ 原有工具

| Tool | Status | Purpose | Configuration |
|-------|----------|--------|---------|
| **Vitest** | ^4.0.16 | ✅ Active | Unit Testing | `pyproject.toml` |
| **Vue Test Utils** | ^2.4.6 | ✅ Active | Vue Component Testing | `package.json` |
| **Happy DOM** | ^20.0.11 | ✅ Active | Lightweight DOM Simulation | `package.json` |

---

## 🚀 工具使用策略

---

## 🚀 Quick Start Commands

### Cypress (E2E Testing)
```bash
# Open Cypress Test Runner (Interactive)
npm run test:cypress

# Run tests in headless mode (CI/CD)
npm run test:cypress:ci

# Run tests with recording enabled
npm run test:cypress:record
```

**Configuration**: `web/frontend/cypress.config.ts`
**Test Directory**: `web/frontend/cypress/e2e/`

### K6 (Performance Testing)
```bash
# Run performance test with default URL
npm run test:performance

# Run performance test with custom URL
npm run test:performance:custom BASE_URL=http://localhost:3000
```

**Configuration**: `tests/performance/k6-performance-test.ts`
**Scenarios**: Homepage, Market Data API, Technical Indicators, Login, Dashboard

### Lighthouse (Performance Auditing)
```bash
# Run Lighthouse locally
npm run test:lighthouse:local

# Run Lighthouse in CI mode
npm run test:lighthouse:ci
```

**Configuration**: `lighthouse.config.json`
**Scoring**: Performance ≥90, Accessibility ≥90, Best Practices ≥90, SEO ≥90

---

## 📚 Detailed Usage

### Cypress Configuration

**File**: `web/frontend/cypress.config.ts`

**Key Features**:
- Base URL: `http://localhost:3000`
- Video recording: Disabled (for faster execution)
- Screenshots on failure: Enabled
- Viewport: 1920x1080 (Desktop)
- Default timeout: 10 seconds
- Page load timeout: 60 seconds
- Response timeout: 30 seconds
- Chrome DevTools: Enabled
- Experimental Studio: Enabled

### K6 Performance Testing

**File**: `tests/performance/k6-performance-test.ts`

**Test Stages**:
1. **Warm up (2 minutes)**: 10 target users
2. **Normal load (5 minutes)**: 50 target users
3. **Peak load (3 minutes)**: 100 target users

**Performance Thresholds**:
- Response time: 95% of requests under 500ms
- Error rate: Less than 1%
- Check pass rate: More than 90%

**Scenarios**:
1. Homepage Load Test
2. Market Data API Load Test
3. Technical Indicators Load Test
4. Login Page Load Test
5. Dashboard Load Test

### Lighthouse Configuration

**File**: `lighthouse.config.json`

**Performance Budgets**:
- Performance: ≥90
- Accessibility: ≥90
- Best Practices: ≥90
- SEO: ≥90
- First Contentful Paint: ≤2000ms
- Time to Interactive: ≤5000ms
- Cumulative Layout Shift: ≤0.1

**Test Environment**:
- Preset: Desktop
- Form Factor: Desktop
- Throttling: 40ms RTT, 1.024 Mbps (4G-like)
- Runs per URL: 3

**Audits Disabled**:
- is-on-https (self-signed certificates)
- uses-http2 (insecure protocol)
- no-service-worker-reg (service worker registration)
- render-blocking-resources (performance optimization)

---

## 🔄 Integration with Existing Tools

### Playwright + Cypress

You can now use **both** E2E testing frameworks:

| Feature | Playwright | Cypress |
|---------|-----------|----------|
| Parallel execution | ✅ Yes | ✅ Yes |
| Multi-browser support | ✅ Yes (3 browsers) | ✅ Yes (Chrome, Edge, Electron) |
| Visual regression | ✅ Yes | ❌ No (need Percy/BackstopJS) |
| Time-travel debugging | ✅ Yes | ✅ Yes |
| Network interception | ✅ Yes | ✅ Yes |
| Video recording | ✅ Yes | ✅ Yes |
| Test Runner UI | ✅ Yes | ✅ Yes |
| CI/CD integration | ✅ Excellent | ✅ Good |
| Learning curve | ⭐⭐⭐ | ⭐⭐ |

**Recommendation**: Use **Playwright** as the primary E2E testing tool (already configured with comprehensive test suites). Use **Cypress** for specific scenarios that benefit from visual debugging or time-travel.

### Performance Testing Stack

Now you have a **complete performance testing pipeline**:

1. **K6** → Load testing and stress testing
2. **Lighthouse** → Performance auditing and optimization
3. **Playwright** → E2E testing with performance metrics

**Workflow**:
```bash
# Step 1: Run Lighthouse for baseline
npm run test:lighthouse:local

# Step 2: Fix performance issues
# (Make changes based on Lighthouse report)

# Step 3: Run E2E tests with Playwright
npm run test:e2e

# Step 4: Run load testing with K6
npm run test:performance

# Step 5: Compare results and optimize
```

---

## 📊 Test Coverage Strategy

### Unit Tests (Vitest)
- **Tool**: Vitest
- **Coverage**: @vitest/coverage-v8
- **Framework**: Vue Test Utils
- **Status**: ✅ Active

### E2E Tests
- **Primary Tool**: Playwright (comprehensive test suites)
- **Alternative Tool**: Cypress (quick visual debugging)
- **Status**: ✅ Both active

### Performance Tests
- **Load Testing**: K6
- **Performance Auditing**: Lighthouse
- **Status**: ✅ Both active

---

## 🛠️ Troubleshooting

### Cypress Installation Issue
Cypress 15.8.2 encountered installation issues. If you need to reinstall:

```bash
cd web/frontend
npm uninstall cypress
npm install --save-dev cypress@13.6.0
npx cypress install
```

### Browser Drivers
For Playwright and Cypress to work properly, ensure you have compatible browser versions installed:
- **Chromium**: Automatically managed by Playwright
- **Firefox**: Install separately if needed
- **WebKit**: Safari (macOS) or available via Playwright

### CI/CD Integration
All tools are CI/CD ready. Update your CI configuration (`.github/workflows/*.yml`) to include:
- Playwright tests
- Cypress tests
- K6 performance tests
- Lighthouse audits

---

## 📈 Performance Targets

Based on industry standards and MyStocks application requirements:

| Metric | Target | Rationale |
|--------|--------|-----------|
| **Performance Score** | ≥90 | Industry standard for financial apps |
| **Accessibility Score** | ≥90 | WCAG 2.1 AA compliance |
| **SEO Score** | ≥90 | Search engine visibility |
| **Response Time** | <300ms | Perceived as instant |
| **First Paint** | <2000ms | Fast visual feedback |
| **Time to Interactive** | <5000ms | Quick page interaction |
| **Load Test** | 50 concurrent users | Expected peak load |

---

## 📖 Related Documentation

- **Playwright Guide**: [https://playwright.dev/docs/intro](https://playwright.dev/docs/intro)
- **Cypress Documentation**: [https://docs.cypress.io](https://docs.cypress.io)
- **K6 Documentation**: [https://k6.io/docs](https://k6.io/docs)
- **Lighthouse CI**: [https://github.com/GoogleChrome/lighthouse-ci](https://github.com/GoogleChrome/lighthouse-ci)

---

## 🎯 Next Steps

1. ✅ **Cypress**: Installed and configured with basic test suite
2. ✅ **K6**: Installed with performance test scenarios
3. ✅ **Lighthouse**: Configured for CI/CD and local testing
4. ✅ **Package.json**: Updated with new test scripts
5. 🔄 **Playwright**: Expand existing test suites (see `tests/e2e/`)
6. 📊 **Coverage**: Maintain 80%+ test coverage with Vitest
7. 🚀 **CI/CD**: Integrate all testing tools into GitHub Actions

---

**Last Updated**: 2026-01-11
**Maintainer**: MyStocks Team
**Version**: 1.0.0
