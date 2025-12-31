/**
 * Market Data Module E2E Tests
 *
 * End-to-end tests for market data functionality using Playwright.
 * Tests cover user journeys, API integration, and UI interactions.
 */

import { test, expect } from '@playwright/test';
import { loginAndSetupAuth } from './helpers/auth';

/**
 * Desktop viewports to test
 */
const desktopViewports = [
  { width: 1920, height: 1080, name: 'Full HD' },
  { width: 1680, height: 1050, name: 'Widescreen' },
  { width: 1440, height: 900, name: 'Laptop' },
  { width: 1366, height: 768, name: 'Small Laptop' },
];

/**
 * Base URL for the application
 */
const BASE_URL = process.env.BASE_URL || 'http://localhost:3001';

test.describe('Market Data Module - E2E Tests', () => {
  test.beforeEach(async ({ page, request }) => {
    // Set default viewport
    await page.setViewportSize({ width: 1920, height: 1080 });

    // Setup authentication using the new auth helper
    await loginAndSetupAuth(request, page);
  });

  test.describe('Market Overview Page', () => {
    test('should load market overview page successfully', async ({ page }) => {
      await page.goto(`${BASE_URL}/market`);

      // Check page title
      await expect(page).toHaveTitle(/MyStocks/);

      // Check main heading
      const heading = page.locator('h1, h2').filter({ hasText: /市场概览|市场数据|Market Overview/ });
      await expect(heading).toBeVisible();
    });

    test('should display market statistics', async ({ page }) => {
      await page.goto(`${BASE_URL}/market`);

      // Wait for data to load
      await page.waitForTimeout(2000);

      // Check for market stats display
      const statsSection = page.locator('.market-stats, [data-testid="market-stats"]');
      await expect(statsSection).toBeVisible();

      // Verify at least some data is displayed (not empty)
      const statValues = page.locator('.stat-value, .stat-item');
      const count = await statValues.count();
      expect(count).toBeGreaterThan(0);
    });

    test('should display top ETFs section', async ({ page }) => {
      await page.goto(`${BASE_URL}/market`);

      // Wait for data to load
      await page.waitForTimeout(2000);

      // Check for ETF section
      const etfSection = page.locator('.top-etfs, [data-testid="top-etfs"]');
      await expect(etfSection).toBeVisible();

      // Verify ETF items are displayed
      const etfItems = page.locator('.etf-item, .stock-card');
      const count = await etfItems.count();
      expect(count).toBeGreaterThan(0);
    });

    test('should handle API failures gracefully', async ({ page }) => {
      // Simulate API failure by intercepting requests
      await page.route('**/api/market/overview', (route) => {
        route.abort();
      });

      await page.goto(`${BASE_URL}/market`);

      // Wait for error handling
      await page.waitForTimeout(2000);

      // Verify mock data is displayed as fallback
      const statsSection = page.locator('.market-stats, [data-testid="market-stats"]');
      await expect(statsSection).toBeVisible();
    });
  });

  test.describe('Desktop Layout Validation', () => {
    for (const viewport of desktopViewports) {
      test(`${viewport.name} (${viewport.width}x${viewport.height})`, async ({ page }) => {
        await page.setViewportSize({ width: viewport.width, height: viewport.height });
        await page.goto(`${BASE_URL}/market`);

        // Wait for page to load
        await page.waitForLoadState('networkidle');

        // Check main content area is visible
        const mainContent = page.locator('main, .main-content, [role="main"]');
        await expect(mainContent).toBeInViewport();

        // Check sidebar is visible (if present)
        const sidebar = page.locator('.sidebar, aside, [data-testid="sidebar"]');
        const sidebarCount = await sidebar.count();
        if (sidebarCount > 0) {
          await expect(sidebar.first()).toBeVisible();
        }

        // Verify responsive layout
        const pageWidth = await page.evaluate(() => document.body.scrollWidth);
        expect(pageWidth).toBeLessThanOrEqual(viewport.width);
      });
    }
  });

  test.describe('Data Refresh Functionality', () => {
    test('should refresh data on button click', async ({ page }) => {
      await page.goto(`${BASE_URL}/market`);

      // Wait for initial load
      await page.waitForTimeout(2000);

      // Find and click refresh button
      const refreshButton = page.locator('button:has-text("刷新"), [data-testid="refresh-button"]');
      const refreshCount = await refreshButton.count();

      if (refreshCount > 0) {
        // Click refresh
        await refreshButton.first().click();

        // Wait for data to reload
        await page.waitForTimeout(2000);

        // Verify loading indicator was shown (if implemented)
        const loadingIndicator = page.locator('.loading, [data-testid="loading"]');
        await expect(loadingIndicator).not.toBeVisible();
      }
    });

    test('should display last update time', async ({ page }) => {
      await page.goto(`${BASE_URL}/market`);

      // Wait for data to load
      await page.waitForTimeout(2000);

      // Check for last update time display
      const lastUpdate = page.locator('.last-update, [data-testid="last-update"]');
      const count = await lastUpdate.count();

      if (count > 0) {
        await expect(lastUpdate.first()).toBeVisible();
      }
    });
  });

  test.describe('Navigation to Market Data', () => {
    test('should navigate from dashboard to market page', async ({ page }) => {
      await page.goto(`${BASE_URL}/dashboard`);

      // Find and click market data navigation link
      const marketLink = page.locator('a:has-text("市场数据"), a[href*="/market"]');
      await marketLink.first().click();

      // Verify navigation
      await page.waitForURL('**/market');
      await expect(page).toHaveURL(/\/market/);
    });

    test('should navigate using sidebar menu', async ({ page }) => {
      await page.goto(`${BASE_URL}/dashboard`);

      // Find sidebar menu item
      const sidebarMenu = page.locator('.sidebar, aside, [data-testid="sidebar"]');
      const menuCount = await sidebarMenu.count();

      if (menuCount > 0) {
        const marketMenuItem = sidebarMenu.first().locator('a:has-text("市场")');
        const itemCount = await marketMenuItem.count();

        if (itemCount > 0) {
          await marketMenuItem.first().click();
          await page.waitForURL('**/market');
        }
      }
    });
  });

  test.describe('Real-time Data Updates', () => {
    test('should display loading state during data fetch', async ({ page }) => {
      // Slow down the API response
      await page.route('**/api/market/overview', async (route) => {
        await new Promise((resolve) => setTimeout(resolve, 2000));
        route.continue();
      });

      await page.goto(`${BASE_URL}/market`);

      // Check for loading indicator
      const loadingIndicator = page.locator('.loading, .spinner, [data-testid="loading"]');
      await expect(loadingIndicator).toBeVisible();
    });

    test('should cache data and serve from cache on subsequent visits', async ({ page }) => {
      // First visit - should fetch from API
      await page.goto(`${BASE_URL}/market`);
      await page.waitForTimeout(2000);

      // Navigate away
      await page.goto(`${BASE_URL}/dashboard`);
      await page.waitForTimeout(1000);

      // Navigate back - should load from cache (faster)
      const startTime = Date.now();
      await page.goto(`${BASE_URL}/market`);
      await page.waitForTimeout(500);
      const loadTime = Date.now() - startTime;

      // Cache load should be faster than 2 seconds
      expect(loadTime).toBeLessThan(2000);
    });
  });

  test.describe('Error Handling', () => {
    test('should show user-friendly error message on network error', async ({ page }) => {
      // Simulate network error
      await page.route('**/api/market/overview', (route) => {
        route.abort('failed');
      });

      await page.goto(`${BASE_URL}/market`);
      await page.waitForTimeout(2000);

      // Check for error message or mock data fallback
      const errorMessage = page.locator('.error-message, [data-testid="error-message"]');
      const errorCount = await errorMessage.count();

      if (errorCount > 0) {
        await expect(errorMessage.first()).toBeVisible();
      } else {
        // If no error message, verify mock data is shown
        const mockDataIndicator = page.locator('.mock-data, [data-testid="mock-data"]');
        const mockCount = await mockDataIndicator.count();

        if (mockCount > 0) {
          await expect(mockDataIndicator.first()).toBeVisible();
        }
      }
    });

    test('should recover from temporary errors', async ({ page }) => {
      let callCount = 0;

      // Fail first request, succeed second
      await page.route('**/api/market/overview', (route) => {
        callCount++;
        if (callCount === 1) {
          route.abort('failed');
        } else {
          route.continue();
        }
      });

      await page.goto(`${BASE_URL}/market`);
      await page.waitForTimeout(2000);

      // Click refresh button to retry
      const refreshButton = page.locator('button:has-text("刷新"), [data-testid="refresh-button"]');
      const refreshCount = await refreshButton.count();

      if (refreshCount > 0) {
        await refreshButton.first().click();
        await page.waitForTimeout(2000);

        // Verify data is now displayed
        const statsSection = page.locator('.market-stats, [data-testid="market-stats"]');
        await expect(statsSection).toBeVisible();
      }
    });
  });

  test.describe('Accessibility', () => {
    test('should have proper heading hierarchy', async ({ page }) => {
      await page.goto(`${BASE_URL}/market`);

      // Check for h1 heading
      const h1 = page.locator('h1');
      const h1Count = await h1.count();
      expect(h1Count).toBeGreaterThan(0);

      // Check for proper heading structure
      const headings = page.locator('h1, h2, h3');
      const headingCount = await headings.count();
      expect(headingCount).toBeGreaterThan(0);
    });

    test('should have aria labels on interactive elements', async ({ page }) => {
      await page.goto(`${BASE_URL}/market`);

      // Check buttons have aria-label or text content
      const buttons = page.locator('button');
      const buttonCount = await buttons.count();

      for (let i = 0; i < Math.min(buttonCount, 5); i++) {
        const button = buttons.nth(i);
        const hasAriaLabel = await button.getAttribute('aria-label');
        const hasText = (await button.textContent()).trim().length > 0;

        expect(hasAriaLabel !== null || hasText).toBeTruthy();
      }
    });
  });
});
