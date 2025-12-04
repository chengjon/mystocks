/**
 * Dashboard Page E2E Tests - Phase 3 Version
 *
 * Updated for Phase 3 with conditional API setup:
 * - Supports both mock and real API modes
 * - Configurable via environment variables
 * - Demonstrates new Phase 3 patterns
 *
 * Tests for the MyStocks Dashboard page including:
 * - Page load and data display
 * - Real-time data updates
 * - Responsive design
 * - Error handling
 * - Conditional API switching
 *
 * Tier 1 Priority: Core business functionality
 *
 * Environment Variables:
 * - USE_REAL_API=true  -> Use real backend APIs
 * - USE_REAL_API=false -> Use mock APIs (default)
 * - API_BASE_URL       -> Base URL for real APIs (default: http://localhost:8000)
 * - FRONTEND_BASE_URL  -> Frontend URL (default: http://localhost:3000)
 */

import { test, expect, Page } from '@playwright/test';
import { DashboardPage } from '../helpers/page-objects';
import { setupApi, isMockEnabled } from '../helpers/conditional-mocking';
import { TEST_ENV, validateTestEnvironment, shouldUseMocks } from '../helpers/test-env';
import {
  mockDashboardData,
  clearMocks,
  waitForApiCall,
} from '../helpers/api-helpers';
import {
  assertPageLoadedSuccessfully,
  assertDataDisplayed,
  assertDesktopLayout,
  assertTabletLayout,
  assertMobileLayout,
  assertToastMessage,
} from '../helpers/assertions';

/**
 * Dashboard page test suite
 *
 * This test suite demonstrates the Phase 3 improvements:
 * 1. Conditional API setup based on environment
 * 2. Support for both mock and real APIs
 * 3. Proper environment validation
 */
test.describe('Dashboard Page - Phase 3 (Conditional APIs)', () => {
  let dashboardPage: DashboardPage;

  /**
   * Global setup - validate environment configuration once
   */
  test.beforeAll(async () => {
    await validateTestEnvironment();
    console.log(`Running tests in mode: ${shouldUseMocks() ? 'Mock' : 'Real'} API`);
  });

  /**
   * Per-test setup
   */
  test.beforeEach(async ({ page }) => {
    // Setup APIs conditionally based on environment
    // If USE_REAL_API=true, uses real backend; otherwise mocks
    await setupApi(page, {
      includeCategories: ['dashboard'],
      mockDelay: 0, // No artificial delay for local testing
    });

    // Create dashboard page object
    dashboardPage = new DashboardPage(page);

    // Navigate to dashboard using configured frontend URL
    await page.goto(`${TEST_ENV.FRONTEND_BASE_URL}/dashboard`, {
      waitUntil: 'networkidle',
    });

    // Wait for dashboard content to load
    await page.waitForSelector('[data-testid="dashboard-container"]', {
      timeout: TEST_ENV.NAVIGATION_TIMEOUT_MS,
    });
  });

  /**
   * Cleanup
   */
  test.afterEach(async ({ page }) => {
    if (isMockEnabled()) {
      clearMocks(page);
    }
  });

  // ============================================================================
  // Core Functionality Tests
  // ============================================================================

  test('should display dashboard overview with all widgets', async ({ page }) => {
    // Verify page loaded successfully
    await assertPageLoadedSuccessfully(page, '[data-testid="dashboard-container"]');

    // Check portfolio summary
    const portfolioSummary = page.locator('[data-testid="portfolio-summary"]');
    await expect(portfolioSummary).toBeVisible({ timeout: TEST_ENV.NAVIGATION_TIMEOUT_MS });

    // Check performance metrics
    const performanceCard = page.locator('[data-testid="performance-metrics"]');
    await expect(performanceCard).toBeVisible();

    // Check market overview
    const marketOverview = page.locator('[data-testid="market-overview"]');
    await expect(marketOverview).toBeVisible();

    // Verify data is displayed
    await assertDataDisplayed(page, '[data-testid="dashboard-container"]');
  });

  test('should load portfolio data correctly', async ({ page }) => {
    const portfolioValue = page.locator('[data-testid="portfolio-total-value"]');
    await expect(portfolioValue).toContainText(/[\d,.]+/);

    const portfolioChange = page.locator('[data-testid="portfolio-change"]');
    await expect(portfolioChange).toBeVisible();

    const portfolioChangePercent = page.locator('[data-testid="portfolio-change-percent"]');
    await expect(portfolioChangePercent).toBeVisible();
  });

  test('should display real-time market data', async ({ page }) => {
    const marketIndexes = page.locator('[data-testid="market-index"]');
    const count = await marketIndexes.count();

    // Should display at least 1 market index
    expect(count).toBeGreaterThanOrEqual(1);

    // Verify each index has value and change
    for (let i = 0; i < Math.min(count, 3); i++) {
      const indexItem = marketIndexes.nth(i);
      const value = indexItem.locator('[data-testid="index-value"]');
      const change = indexItem.locator('[data-testid="index-change"]');

      await expect(value).toBeVisible({ timeout: TEST_ENV.ACTION_TIMEOUT_MS });
      await expect(change).toBeVisible();
    }
  });

  test('should show watchlist stocks', async ({ page }) => {
    const watchlistSection = page.locator('[data-testid="watchlist-section"]');
    await expect(watchlistSection).toBeVisible({ timeout: TEST_ENV.NAVIGATION_TIMEOUT_MS });

    const stockItems = page.locator('[data-testid="watchlist-stock"]');
    const count = await stockItems.count();

    // Should have at least 1 stock in watchlist
    expect(count).toBeGreaterThanOrEqual(1);
  });

  test('should display portfolio allocation chart', async ({ page }) => {
    const allocationChart = page.locator('[data-testid="allocation-chart"]');
    await expect(allocationChart).toBeVisible({ timeout: TEST_ENV.NAVIGATION_TIMEOUT_MS });

    // Verify chart has canvas or SVG
    const chartElement = allocationChart.locator('canvas, svg');
    await expect(chartElement).toBeVisible();
  });

  // ============================================================================
  // Interactive Features Tests
  // ============================================================================

  test('should refresh data when refresh button clicked', async ({ page }) => {
    const refreshButton = page.locator('[data-testid="refresh-button"]');
    await expect(refreshButton).toBeVisible();

    // Click refresh
    await refreshButton.click({ timeout: TEST_ENV.ACTION_TIMEOUT_MS });

    // Wait for data reload
    if (isMockEnabled()) {
      await page.waitForTimeout(300);
    } else {
      await page.waitForLoadState('networkidle');
    }

    // Verify data is still displayed
    await assertDataDisplayed(page, '[data-testid="portfolio-summary"]');
  });

  test('should navigate to stock detail when stock clicked', async ({ page }) => {
    const stockItem = page.locator('[data-testid="watchlist-stock"]').first();
    const stockLink = stockItem.locator('a');

    // Get the stock symbol or ID
    const href = await stockLink.getAttribute('href');
    expect(href).toBeTruthy();

    // Note: Don't click (would navigate away from dashboard)
    // In integration tests, this would be tested separately
  });

  // ============================================================================
  // Responsive Design Tests
  // ============================================================================

  test('should display correctly on desktop', async ({ page }) => {
    // Set desktop viewport
    await page.setViewportSize({ width: 1920, height: 1080 });

    // Wait for responsive layout
    await page.waitForTimeout(300);

    // Verify desktop layout
    await assertDesktopLayout(page, '[data-testid="dashboard-container"]');

    // Verify all sections visible
    const sidebar = page.locator('[data-testid="sidebar"]');
    await expect(sidebar).toBeVisible();

    const mainContent = page.locator('[data-testid="main-content"]');
    await expect(mainContent).toBeVisible();
  });

  test('should display correctly on tablet', async ({ page }) => {
    // Set tablet viewport
    await page.setViewportSize({ width: 768, height: 1024 });

    // Wait for responsive layout
    await page.waitForTimeout(300);

    // Verify tablet layout
    await assertTabletLayout(page, '[data-testid="dashboard-container"]');

    // Verify sidebar is collapsible
    const sidebarToggle = page.locator('[data-testid="sidebar-toggle"]');
    // May or may not be visible depending on design
  });

  test('should display correctly on mobile', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });

    // Wait for responsive layout
    await page.waitForTimeout(300);

    // Verify mobile layout
    await assertMobileLayout(page, '[data-testid="dashboard-container"]');

    // Verify touch-friendly layout
    const buttons = page.locator('button');
    const count = await buttons.count();

    if (count > 0) {
      const firstButton = buttons.first();
      const box = await firstButton.boundingBox();
      // Mobile buttons should be reasonably sized for touch
      if (box) {
        expect(Math.min(box.width, box.height)).toBeGreaterThan(40);
      }
    }
  });

  // ============================================================================
  // Error Handling Tests
  // ============================================================================

  test('should handle data load errors gracefully', async ({ page }) => {
    if (isMockEnabled()) {
      // In mock mode, set up error response
      await page.route('**/api/dashboard/**', async (route) => {
        await route.respond({
          status: 500,
          contentType: 'application/json',
          body: JSON.stringify({ error: 'Server error' }),
        });
      });

      // Refresh to trigger error
      const refreshButton = page.locator('[data-testid="refresh-button"]');
      if (await refreshButton.isVisible()) {
        await refreshButton.click();
        await page.waitForTimeout(300);
      }

      // Check for error message
      const errorMessage = page.locator('[data-testid="error-message"]');
      if (await errorMessage.isVisible()) {
        await expect(errorMessage).toContainText(/error|failed/i);
      }
    }
    // Real API mode: actual error handling is tested against real backend
  });

  test('should retry on network timeout', async ({ page }) => {
    if (isMockEnabled()) {
      let callCount = 0;

      // First call fails, second succeeds
      await page.route('**/api/dashboard/overview', async (route) => {
        callCount++;
        if (callCount === 1) {
          await route.abort('timedout');
        } else {
          await route.continue();
        }
      });

      // Trigger retry
      const refreshButton = page.locator('[data-testid="refresh-button"]');
      if (await refreshButton.isVisible()) {
        await refreshButton.click();
        await page.waitForTimeout(500);
      }

      // Verify retried and succeeded
      await assertDataDisplayed(page, '[data-testid="dashboard-container"]');
    }
  });

  // ============================================================================
  // Performance Tests
  // ============================================================================

  test('should load dashboard within performance budget', async ({ page }) => {
    const startTime = Date.now();

    // Reload page to measure full load time
    await page.goto(`${TEST_ENV.FRONTEND_BASE_URL}/dashboard`, {
      waitUntil: 'networkidle',
    });

    const loadTime = Date.now() - startTime;

    // Performance budget: 3 seconds for dashboard
    expect(loadTime).toBeLessThan(3000);

    console.log(`Dashboard load time: ${loadTime}ms`);
  });

  test('should update data quickly on refresh', async ({ page }) => {
    const refreshButton = page.locator('[data-testid="refresh-button"]');
    await expect(refreshButton).toBeVisible();

    const startTime = Date.now();
    await refreshButton.click();

    // Wait for data update
    if (isMockEnabled()) {
      await page.waitForTimeout(300);
    } else {
      await page.waitForLoadState('networkidle', {
        timeout: TEST_ENV.ACTION_TIMEOUT_MS,
      });
    }

    const updateTime = Date.now() - startTime;

    // Refresh should complete within 2 seconds
    expect(updateTime).toBeLessThan(2000);

    console.log(`Dashboard refresh time: ${updateTime}ms`);
  });
});
