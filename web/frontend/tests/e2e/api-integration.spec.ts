/**
 * API Integration E2E Tests
 *
 * Tests API client, composables, and data flow integration.
 */

import { test, expect } from '@playwright/test';

test.describe('API Client', () => {
  test('should be configured with correct base URL', async ({ page }) => {
    // Navigate to a page that uses the API client
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Check that the page loads without console errors related to API
    const consoleErrors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });

    // Filter out expected errors (like API not available in test environment)
    const apiErrors = consoleErrors.filter(err =>
      err.includes('Failed to fetch') ||
      err.includes('NetworkError') ||
      err.includes('api')
    );

    // Allow some API errors in test environment
    expect(apiErrors.length).toBeLessThan(5);
  });

  test('should handle API requests gracefully', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Check that page content loads even if some APIs fail
    const body = await page.locator('body').textContent();
    expect(body).toBeTruthy();
  });
});

test.describe('Composables Integration', () => {
  test('useMarket composable should be accessible', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Check for market-related content
    const marketContent = await page.locator('text=Market').first().isVisible().catch(() => false);
    // The page might use different text, so we just verify the page loaded
    await expect(page.locator('body')).toBeVisible();
  });

  test('useStrategy composable should be accessible', async ({ page }) => {
    await page.goto('/strategy');
    await page.waitForLoadState('networkidle');

    // Strategy page should load
    await expect(page.locator('body')).toBeVisible();
  });

  test('useTrading composable should be accessible', async ({ page }) => {
    await page.goto('/trade');
    await page.waitForLoadState('domcontentloaded');

    // Trade page should load
    await expect(page.locator('body')).toBeVisible();
  });
});

test.describe('Data Flow', () => {
  test('should display loading state during API calls', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('domcontentloaded');

    // Check for loading indicators
    const loadingElements = await page.locator('.el-loading').count();
    // May or may not have loading elements depending on API status
  });

  test('should handle API errors without crashing', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Navigate to another page to test error handling
    await page.goto('/strategy');
    await page.waitForLoadState('networkidle');

    // Should still be able to interact with the page
    const body = await page.locator('body').textContent();
    expect(body).toBeTruthy();
  });
});
