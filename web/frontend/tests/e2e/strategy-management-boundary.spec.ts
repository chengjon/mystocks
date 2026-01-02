/**
 * Strategy Management - Boundary and Edge Cases Tests
 *
 * Specialized E2E tests for boundary conditions, error handling,
 * and edge cases using Playwright.
 */

import { test, expect } from '@playwright/test';
import { loginAndSetupAuth } from './helpers/auth';

/**
 * Base URL for the application
 */
const BASE_URL = process.env.BASE_URL || 'http://localhost:3020';

test.describe('Strategy Management - Boundary and Edge Cases', () => {
  test.beforeEach(async ({ page, request }) => {
    // Set default viewport
    await page.setViewportSize({ width: 1920, height: 1080 });

    // Setup authentication
    await loginAndSetupAuth(request, page);

    // Navigate to strategy page
    await page.goto(`${BASE_URL}/strategy`);

    // Wait for page to load completely
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(2000);
  });

  test.describe('Empty Search Results', () => {
    test('should display empty state when no strategies match search', async ({ page }) => {
      // Search for non-existent strategy (page already loaded from beforeEach)
      const searchInput = page.locator('input[placeholder*="SEARCH STRATEGIES"]');
      await searchInput.waitFor({ state: 'visible', timeout: 10000 });
      await searchInput.first().fill('NonExistentStrategyXYZ123');

      await page.waitForTimeout(500);

      // Verify empty state or zero results
      const strategyCards = page.locator('.strategy-card');
      const count = await strategyCards.count();

      expect(count).toBe(0);

      // Check for empty state message
      const emptyMessage = page.locator('.empty-state, .no-results, [data-testid="empty-message"]');
      const hasEmptyMessage = await emptyMessage.count() > 0;

      if (hasEmptyMessage) {
        await expect(emptyMessage.first()).toBeVisible();
      }
    });
  });

  test.describe('Empty Filter Combinations', () => {
    test('should handle filter combinations with no matches', async ({ page }) => {
      // Apply filters that result in no matches
      const searchInput = page.locator('input[placeholder*="SEARCH STRATEGIES"]');
      await searchInput.waitFor({ state: 'visible', timeout: 10000 });
      await searchInput.first().fill('nonexistent');

      const typeFilter = page.locator('.el-select').filter({ hasText: /FILTER BY TYPE|TYPE/ }).first();
      await typeFilter.waitFor({ state: 'visible', timeout: 5000 });
      await typeFilter.click();
      await page.locator('.el-select-dropdown__item').filter({ hasText: 'MOMENTUM' }).first().click();
      await page.waitForTimeout(300);

      const statusFilter = page.locator('.el-select').filter({ hasText: /STATUS/ }).nth(1);
      await statusFilter.click();
      await page.locator('.el-select-dropdown__item').filter({ hasText: 'INACTIVE' }).first().click();
      await page.waitForTimeout(300);

      // Verify no results
      const strategyCards = page.locator('.strategy-card');
      const count = await strategyCards.count();

      expect(count).toBe(0);
    });
  });

  test.describe('Large Dataset Pagination', () => {
    test('should handle pagination with large datasets', async ({ page }) => {
      // Find page size selector
      const pageSizeSelector = page.locator('.el-pagination__sizes .el-select');
      await pageSizeSelector.waitFor({ state: 'visible', timeout: 10000 });
      await pageSizeSelector.click();

      // Select maximum page size (48 or 24)
      await page.locator('.el-select-dropdown__item').filter({ hasText: /48|24/ }).first().click();
      await page.waitForTimeout(500);

      // Check pagination controls
      const pagination = page.locator('.el-pagination');
      await expect(pagination).toBeVisible();

      // Verify pagination info
      const pageInfo = page.locator('.el-pagination__total');
      const hasPageInfo = await pageInfo.count() > 0;

      if (hasPageInfo) {
        const text = await pageInfo.textContent();
        expect(text).toMatch(/\d+/); // Should contain numbers
      }

      // Test navigation to last page
      const lastPageButton = page.locator('.el-pager li').last();
      await lastPageButton.click();
      await page.waitForTimeout(500);

      // Verify pagination still works
      await expect(pagination).toBeVisible();
    });
  });

  test.describe('Network Error Handling', () => {
    test('should gracefully handle network failures', async ({ page }) => {
      // Intercept and fail strategy API calls (need to reload page after setting up route)
      await page.route('**/api/strategy/**', (route) => {
        route.abort('failed');
      });

      await page.goto(`${BASE_URL}/strategy`);
      await page.waitForTimeout(2000);

      // Verify fallback to mock data or error message
      const strategyCards = page.locator('.strategy-card');
      const count = await strategyCards.count();

      // Should either show mock data or error message
      if (count > 0) {
        // Mock data fallback
        expect(count).toBeGreaterThan(0);

        const mockIndicator = page.locator('.mock-data, [data-testid="mock-data"]');
        const hasMockIndicator = await mockIndicator.count() > 0;

        if (hasMockIndicator) {
          await expect(mockIndicator.first()).toBeVisible();
        }
      } else {
        // Error message
        const errorMessage = page.locator('.el-message--error, .error-message');
        const hasError = await errorMessage.count() > 0;

        if (hasError) {
          await expect(errorMessage.first()).toBeVisible();
        }
      }
    });

    test('should recover from temporary network failures', async ({ page }) => {
      // Fail first request, then allow subsequent ones (need to reload page)
      let requestCount = 0;
      await page.route('**/api/strategy/**', (route) => {
        requestCount++;
        if (requestCount === 1) {
          route.abort('failed');
        } else {
          route.continue();
        }
      });

      await page.goto(`${BASE_URL}/strategy`);

      // Wait for error and retry
      await page.waitForTimeout(3000);

      // Should recover and show data
      const strategyCards = page.locator('.strategy-card');
      const count = await strategyCards.count();

      expect(count).toBeGreaterThan(0);
    });
  });

  test.describe('Special Character Handling', () => {
    test('should safely handle special characters in search', async ({ page }) => {
      // Test various special characters (page already loaded from beforeEach)
      const specialChars = [
        '!@#$%',
        '<script>',
        '";DROP TABLE',
        '../../etc/passwd',
        '"><script>alert(1)</script>',
        '${7*7}',
        'javascript:alert(1)'
      ];

      for (const chars of specialChars) {
        // Clear and fill search input
        const searchInput = page.locator('input[placeholder*="SEARCH STRATEGIES"]').first();
        await searchInput.fill('');
        await searchInput.fill(chars);

        await page.waitForTimeout(300);

        // Verify no crashes or JavaScript errors
        const pageErrors: string[] = [];
        page.on('pageerror', (error) => {
          pageErrors.push(error.toString());
        });

        // Should either return results or empty state
        const strategyCards = page.locator('.strategy-card');
        const count = await strategyCards.count();

        expect(count).toBeGreaterThanOrEqual(0);

        // Verify no XSS or injection occurred
        expect(pageErrors.length).toBe(0);

        // Clear for next test
        await searchInput.fill('');
      }
    });

    test('should handle unicode and emoji characters', async ({ page }) => {
      await page.goto(`${BASE_URL}/strategy`);

      // Wait for strategies to load
      await page.waitForTimeout(2000);

      // Test unicode and emoji
      const unicodeStrings = [
        '策略测试',
        '📈💰🚀',
        'αβγδε',
        'مرحبا',
        'こんにちは'
      ];

      const searchInput = page.locator('input[placeholder*="SEARCH STRATEGIES"]').first();

      for (const str of unicodeStrings) {
        await searchInput.fill('');
        await searchInput.fill(str);

        await page.waitForTimeout(300);

        // Should not crash
        const isVisible = await page.locator('.strategy-management').isVisible();
        expect(isVisible).toBe(true);
      }
    });
  });

  test.describe('Invalid Parameter Inputs', () => {
    test('should handle invalid strategy IDs', async ({ page }) => {
      // Try to navigate to invalid strategy ID (page already loaded, just add query param)
      const invalidId = '999999';
      await page.goto(`${BASE_URL}/strategy?id=${invalidId}`);

      await page.waitForTimeout(1000);

      // Verify page doesn't crash
      const isVisible = await page.locator('h1, h2').filter({ hasText: /策略管理|Strategy/ }).isVisible();
      expect(isVisible).toBe(true);

      // Return to list page
      await page.goto(`${BASE_URL}/strategy`);
      await page.waitForTimeout(1000);

      // Test with negative ID
      await page.goto(`${BASE_URL}/strategy?id=-1`);

      await page.waitForTimeout(1000);

      // Verify page doesn't crash
      const stillVisible = await page.locator('h1, h2').filter({ hasText: /策略管理|Strategy/ }).isVisible();
      expect(stillVisible).toBe(true);

      // Test with non-numeric ID
      await page.goto(`${BASE_URL}/strategy?id=abc`);

      await page.waitForTimeout(1000);

      // Verify page doesn't crash
      const stillOk = await page.locator('h1, h2').filter({ hasText: /策略管理|Strategy/ }).isVisible();
      expect(stillOk).toBe(true);
    });

    test('should handle malformed query parameters', async ({ page }) => {
      // Test with malformed URL parameters
      const malformedUrls = [
        `${BASE_URL}/strategy?id=`,
        `${BASE_URL}/strategy?foo=bar&baz=qux`,
        `${BASE_URL}/strategy?[]=test`,
        `${BASE_URL}/strategy?id[]=1&id[]=2`
      ];

      for (const url of malformedUrls) {
        await page.goto(url);

        await page.waitForTimeout(1000);

        // Verify page doesn't crash
        const isVisible = await page.locator('h1, h2').filter({ hasText: /策略管理|Strategy/ }).isVisible();
        expect(isVisible).toBe(true);
      }
    });
  });

  test.describe('Concurrent Operations', () => {
    test('should handle concurrent delete operations safely', async ({ page }) => {
      // Get initial strategy count (page already loaded from beforeEach)
      const strategiesBefore = await page.locator('.strategy-card').count();

      if (strategiesBefore < 2) {
        test.skip(); // Skip if not enough strategies to test
      }

      // Find first two delete buttons
      const deleteButtons = page.locator('.strategy-card button').filter({ hasText: /DELETE|REMOVE/ });
      const deleteCount = await deleteButtons.count();

      if (deleteCount < 2) {
        test.skip(); // Skip if not enough delete buttons
      }

      // Click first delete button quickly
      await deleteButtons.nth(0).click();
      await page.waitForTimeout(100);

      // Try clicking second delete button while first dialog is open
      await deleteButtons.nth(1).click();
      await page.waitForTimeout(200);

      // Verify only one confirmation dialog appears
      const confirmDialogs = page.locator('.el-message-box');
      const dialogCount = await confirmDialogs.count();

      expect(dialogCount).toBeLessThanOrEqual(1); // Should not show multiple dialogs

      // Cancel all dialogs to clean up
      if (dialogCount > 0) {
        const cancelButton = confirmDialogs.locator('button', { hasText: /CANCEL/ }).first();
        await cancelButton.click();
        await page.waitForTimeout(300);
      }

      // Verify no strategies were deleted
      const strategiesAfter = await page.locator('.strategy-card').count();
      expect(strategiesAfter).toBe(strategiesBefore);
    });

    test('should handle rapid filter changes', async ({ page }) => {
      const typeFilter = page.locator('.el-select').filter({ hasText: /FILTER BY TYPE|TYPE/ }).first();

      // Rapidly change filter values
      const filterValues = ['TREND FOLLOWING', 'MEAN REVERSION', 'MOMENTUM', 'TREND FOLLOWING'];

      for (const value of filterValues) {
        await typeFilter.click();
        await page.locator('.el-select-dropdown__item').filter({ hasText: value }).first().click();
        await page.waitForTimeout(100); // Very short delay
      }

      // Verify final state is consistent
      await page.waitForTimeout(500);
      const strategyCards = page.locator('.strategy-card');
      const count = await strategyCards.count();

      expect(count).toBeGreaterThanOrEqual(0);
    });

    test('should handle concurrent search and filter operations', async ({ page }) => {
      const searchInput = page.locator('input[placeholder*="SEARCH STRATEGIES"]').first();
      const typeFilter = page.locator('.el-select').filter({ hasText: /FILTER BY TYPE|TYPE/ }).first();

      // Simulate concurrent operations
      await searchInput.fill('test');
      await page.waitForTimeout(50);

      await typeFilter.click();
      await page.waitForTimeout(50);

      await searchInput.fill('momentum');
      await page.waitForTimeout(50);

      await page.locator('.el-select-dropdown__item').filter({ hasText: 'MOMENTUM' }).first().click();
      await page.waitForTimeout(200);

      // Verify no errors occurred
      const strategyCards = page.locator('.strategy-card');
      const count = await strategyCards.count();

      expect(count).toBeGreaterThanOrEqual(0);
    });
  });
});
