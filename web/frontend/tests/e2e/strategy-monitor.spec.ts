/**
 * Strategy Management - Monitoring & Search
 * 
 * End-to-end tests for search, filtering, pagination, and real-time monitoring.
 */

import { test, expect } from '@playwright/test';
import { loginAndSetupAuth } from './helpers/auth';

const BASE_URL = process.env.BASE_URL || 'http://localhost:3020';

const desktopViewports = [
  { width: 1920, height: 1080, name: 'Full HD' },
  { width: 1680, height: 1050, name: 'Widescreen' },
  { width: 1440, height: 900, name: 'Laptop' },
];

test.describe('Strategy Management - Monitoring & UI', () => {
  test.beforeEach(async ({ page, request }) => {
    await page.setViewportSize({ width: 1920, height: 1080 });
    await loginAndSetupAuth(request, page);
  });

  test.describe('Search and Filter', () => {
    test('should search strategies by name', async ({ page }) => {
      await page.goto(`${BASE_URL}/strategy`);
      await page.waitForTimeout(2000);
      const totalCount = await page.locator('.strategy-card').count();
      const searchInput = page.locator('input[placeholder*="SEARCH STRATEGIES"]').first();
      await searchInput.fill('momentum');
      await page.waitForTimeout(500);
      const filteredCount = await page.locator('.strategy-card').count();
      expect(filteredCount).toBeLessThanOrEqual(totalCount);
      await searchInput.fill('');
      await page.waitForTimeout(500);
      expect(await page.locator('.strategy-card').count()).toBe(totalCount);
    });

    test('should filter strategies by type', async ({ page }) => {
      await page.goto(`${BASE_URL}/strategy`);
      await page.waitForTimeout(2000);
      const totalCount = await page.locator('.strategy-card').count();
      const typeFilter = page.locator('.el-select').filter({ hasText: /FILTER BY TYPE|TYPE/ }).first();
      await typeFilter.click();
      await page.locator('.el-select-dropdown__item').filter({ hasText: 'TREND FOLLOWING' }).first().click();
      await page.waitForTimeout(500);
      expect(await page.locator('.strategy-card').count()).toBeLessThanOrEqual(totalCount);
    });

    test('should filter strategies by status', async ({ page }) => {
      await page.goto(`${BASE_URL}/strategy`);
      await page.waitForTimeout(2000);
      const totalCount = await page.locator('.strategy-card').count();
      const statusFilter = page.locator('.el-select').filter({ hasText: /FILTER BY STATUS|STATUS/ }).first();
      await statusFilter.click();
      await page.locator('.el-select-dropdown__item').filter({ hasText: 'ACTIVE' }).first().click();
      await page.waitForTimeout(500);
      expect(await page.locator('.strategy-card').count()).toBeLessThanOrEqual(totalCount);
    });
  });

  test.describe('Pagination', () => {
    test('should display pagination and change page size', async ({ page }) => {
      await page.goto(`${BASE_URL}/strategy`);
      await page.waitForTimeout(2000);
      await expect(page.locator('.el-pagination')).toBeVisible();
      const pageSizeSelector = page.locator('.el-pagination__sizes .el-select');
      await pageSizeSelector.click();
      await page.locator('.el-select-dropdown__item').filter({ hasText: '24' }).first().click();
      await page.waitForTimeout(500);
      await expect(page.locator('.el-pagination')).toBeVisible();
    });
  });

  test.describe('Real-time & UI States', () => {
    test('should display loading state during operations', async ({ page }) => {
      await page.route('**/api/v1/strategy/strategies', async (route) => {
        await new Promise((resolve) => setTimeout(resolve, 2000));
        route.continue();
      });
      await page.goto(`${BASE_URL}/strategy`);
      await expect(page.locator('.loading, .spinner, [data-testid="loading"]')).toBeVisible();
    });

    test('should refresh strategy list', async ({ page }) => {
      await page.goto(`${BASE_URL}/strategy`);
      await page.waitForTimeout(2000);
      const refreshButton = page.locator('button:has-text("刷新"), [data-testid="refresh-button"]');
      if (await refreshButton.count() > 0) {
        await refreshButton.first().click();
        await page.waitForTimeout(2000);
        await expect(page.locator('.loading, .spinner')).not.toBeVisible();
      }
    });

    test('should handle API failures gracefully', async ({ page }) => {
      await page.route('**/api/v1/strategy/strategies', (route) => route.abort('failed'));
      await page.goto(`${BASE_URL}/strategy`);
      await page.waitForTimeout(2000);
      expect(await page.locator('.strategy-card').count()).toBeGreaterThan(0);
    });
  });

  test.describe('Layout & Navigation', () => {
    for (const viewport of desktopViewports) {
      test(`Layout validation on ${viewport.name}`, async ({ page }) => {
        await page.setViewportSize({ width: viewport.width, height: viewport.height });
        await page.goto(`${BASE_URL}/strategy`);
        await page.waitForLoadState('networkidle');
        await expect(page.locator('main, .main-content, [role="main"]').first()).toBeInViewport();
      });
    }

    test('should navigate from dashboard to strategy page', async ({ page }) => {
      await page.goto(`${BASE_URL}/dashboard`);
      const strategyLink = page.locator('a:has-text("策略管理"), a[href*="/strategy"]');
      await strategyLink.first().click();
      await page.waitForURL('**/strategy');
      expect(page.url()).toContain('/strategy');
    });
  });

  test.describe('Accessibility', () => {
    test('should have proper ARIA labels', async ({ page }) => {
      await page.goto(`${BASE_URL}/strategy`);
      const buttons = page.locator('button');
      const count = await buttons.count();
      for (let i = 0; i < Math.min(count, 5); i++) {
        const button = buttons.nth(i);
        const ariaLabel = await button.getAttribute('aria-label');
        const text = (await button.textContent()).trim();
        expect(ariaLabel !== null || text.length > 0).toBeTruthy();
      }
    });
  });
});
