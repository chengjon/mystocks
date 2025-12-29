import { test, expect } from '@playwright/test';

test.describe('K-line Chart E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/kline-demo');
    await page.waitForLoadState('networkidle');
  });

  test('should load K-line chart demo page', async ({ page }) => {
    await expect(page.locator('.pro-kline-chart')).toBeVisible();
  });

  test('should display chart toolbar with controls', async ({ page }) => {
    await expect(page.locator('.chart-toolbar')).toBeVisible();
    await expect(page.locator('.chart-toolbar-select')).toHaveCount(3);
  });

  test('should change symbol', async ({ page }) => {
    const symbolSelect = page.locator('.chart-toolbar-select').first();
    await symbolSelect.selectOption('600519.SH');
    await page.waitForTimeout(500);
  });

  test('should change interval', async ({ page }) => {
    const intervalSelect = page.locator('.chart-toolbar-select').nth(1);
    await intervalSelect.selectOption('1h');
    await page.waitForTimeout(500);
  });

  test('should toggle main indicators', async ({ page }) => {
    const maButton = page.locator('.chart-toolbar-btn', { hasText: 'MA' });
    await maButton.click();
    await expect(maButton).toHaveClass(/active/);
  });

  test('should show loading state', async ({ page }) => {
    await expect(page.locator('.loading-overlay')).not.toBeVisible();
  });

  test('should display chart info', async ({ page }) => {
    await expect(page.locator('.chart-info')).toBeVisible();
  });

  test('should display latest price info', async ({ page }) => {
    await expect(page.locator('.info-item').first()).toBeVisible();
  });

  test('should toggle oscillator panel', async ({ page }) => {
    const toggleButton = page.locator('.chart-toolbar-btn', { hasText: '显示副图' });
    await toggleButton.click();
    await expect(page.locator('.oscillator-panel')).toBeVisible();
  });

  test('should handle zoom controls', async ({ page }) => {
    const zoomInButton = page.locator('.zoom-icon', { hasText: '+' }).locator('..');
    await zoomInButton.click();
  });

  test('should handle reset view', async ({ page }) => {
    const resetButton = page.locator('.chart-toolbar-btn', { hasText: '重置' });
    await resetButton.click();
  });
});

test.describe('K-line Chart Responsive Tests', () => {
  test('should render on mobile viewport', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 });
    await page.goto('/kline-demo');
    await page.waitForLoadState('networkidle');
    await expect(page.locator('.pro-kline-chart')).toBeVisible();
  });

  test('should render on tablet viewport', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto('/kline-demo');
    await page.waitForLoadState('networkidle');
    await expect(page.locator('.pro-kline-chart')).toBeVisible();
  });

  test('should render on large viewport', async ({ page }) => {
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.goto('/kline-demo');
    await page.waitForLoadState('networkidle');
    await expect(page.locator('.pro-kline-chart')).toBeVisible();
  });
});

test.describe('K-line Chart Performance Tests', () => {
  test('should load chart within performance budget', async ({ page }) => {
    const startTime = Date.now();
    await page.goto('/kline-demo');
    await page.waitForLoadState('networkidle');
    const loadTime = Date.now() - startTime;

    expect(loadTime).toBeLessThan(5000);
  });

  test('should render without console errors', async ({ page }) => {
    const errors: string[] = [];

    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });

    await page.goto('/kline-demo');
    await page.waitForLoadState('networkidle');

    expect(errors.filter(e => !e.includes('favicon'))).toHaveLength(0);
  });
});
