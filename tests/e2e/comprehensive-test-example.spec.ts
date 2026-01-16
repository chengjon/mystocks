import { test, expect } from '@playwright/test';

/**
 * MyStocks - Extended Playwright Test Suite
 * Example test demonstrating comprehensive E2E testing patterns
 */

test.describe('MyStocks Comprehensive E2E Tests', () => {
  const BASE_URL = process.env.BASE_URL || 'http://localhost:3000';

  // Authentication setup
  test.beforeAll(async ({ page }) => {
    // Simulate login - replace with real auth if needed
    await page.goto(`${BASE_URL}/login`);
    await page.fill('[data-testid="username-input"]', 'admin');
    await page.fill('[data-testid="password-input"]', 'admin123');
    await page.click('[data-testid="submit-button"]');
    await page.waitForURL(`${BASE_URL}/dashboard`);
  });

  /**
   * Test Suite 1: Critical User Flows
   */
  test.describe('Critical User Flows', () => {
    test('should complete login flow successfully', async ({ page }) => {
      await page.goto(`${BASE_URL}/login`);
      await page.fill('[data-testid="username-input"]', 'admin');
      await page.fill('[data-testid="password-input"]', 'admin123');
      await page.click('[data-testid="submit-button"]');

      // Verify successful login
      await expect(page).toHaveURL(`${BASE_URL}/dashboard`);
      await expect(page.locator('[data-testid="user-menu"]')).toBeVisible();
    });

    test('should navigate through main menu', async ({ page }) => {
      await page.goto(`${BASE_URL}/dashboard`);

      // Click on market monitoring
      await page.click('[data-testid="menu-monitoring"]');
      await expect(page).toHaveURL(`${BASE_URL}/monitoring`);

      // Click on data analysis
      await page.click('[data-testid="menu-analysis"]');
      await expect(page).toHaveURL(`${BASE_URL}/analysis`);

      // Navigate back
      await page.click('[data-testid="menu-dashboard"]');
      await expect(page).toHaveURL(`${BASE_URL}/dashboard`);
    });
  });

  /**
   * Test Suite 2: Data Display and Interactions
   */
  test.describe('Data Display and Interactions', () => {
    test('should load and display market data table', async ({ page }) => {
      await page.goto(`${BASE_URL}/monitoring`);

      // Wait for data table to load
      await page.waitForSelector('[data-testid="stock-table"]', { state: 'visible' });

      // Verify table has data
      const rows = await page.locator('[data-testid="stock-table"] tbody tr').count();
      await expect(rows).toBeGreaterThan(0);

      // Verify table headers
      await expect(page.locator('th')).toContainText(['代码', '名称', '最新价', '涨跌幅']);
    });

    test('should filter stock data by search', async ({ page }) => {
      await page.goto(`${BASE_URL}/monitoring`);

      // Enter search query
      await page.fill('[data-testid="search-input"]', '平安银行');

      // Wait for filtered results
      await page.waitForTimeout(2000);
      await expect(page.locator('[data-testid="stock-table"]')).toContainText('平安银行');
    });

    test('should refresh data on button click', async ({ page }) => {
      await page.goto(`${BASE_URL}/monitoring`);

      // Get initial row count
      const initialCount = await page.locator('[data-testid="stock-table"] tbody tr').count();

      // Click refresh button
      await page.click('[data-testid="refresh-button"]');

      // Wait for loading indicator to disappear
      await page.waitForSelector('[data-testid="loading-indicator"]', { state: 'hidden' });

      // Verify data is refreshed (row count may have changed)
      await expect(page.locator('[data-testid="stock-table"]')).toBeVisible();
    });
  });

  /**
   * Test Suite 3: Form Interactions
   */
  test.describe('Form Interactions', () => {
    test('should validate form fields with real-time feedback', async ({ page }) => {
      await page.goto(`${BASE_URL}/settings`);

      // Test username validation
      await page.click('[data-testid="username-input"]');
      await page.fill('[data-testid="username-input"]', '');
      await page.click('[data-testid="username-input"]'); // Blur field
      await expect(page.locator('[data-testid="username-error"]')).toBeVisible();

      // Fill valid username
      await page.fill('[data-testid="username-input"]', 'testuser');
      await page.click('[data-testid="username-input"]');
      await expect(page.locator('[data-testid="username-error"]')).not.toBeVisible();
    });

    test('should handle form submission with loading state', async ({ page }) => {
      await page.goto(`${BASE_URL}/settings`);

      await page.fill('[data-testid="email-input"]', 'test@example.com');
      await page.click('[data-testid="save-button"]');

      // Verify loading state
      await expect(page.locator('[data-testid="save-button"]')).toBeDisabled();
      await expect(page.locator('[data-testid="loading-spinner"]')).toBeVisible();

      // Wait for success message
      await page.waitForSelector('[data-testid="success-message"]', { state: 'visible', timeout: 5000 });
      await expect(page.locator('[data-testid="success-message"]')).toContainText('保存成功');
    });
  });

  /**
   * Test Suite 4: API Error Handling
   */
  test.describe('API Error Handling', () => {
    test('should display friendly error message on API failure', async ({ page }) => {
      // Intercept API call to simulate error
      await page.route('**/api/market/**', route => route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Internal Server Error' })
      }));

      await page.goto(`${BASE_URL}/monitoring`);
      await page.click('[data-testid="refresh-button"]');

      // Verify error message is displayed
      await expect(page.locator('[data-testid="error-message"]')).toBeVisible();
      await expect(page.locator('[data-testid="error-message"]')).toContainText('数据加载失败，请稍后重试');
    });

    test('should handle network timeout gracefully', async ({ page }) => {
      // Simulate network timeout
      await page.route('**/api/market/**', route => new Promise(resolve => setTimeout(() => resolve(), 10000)));

      await page.goto(`${BASE_URL}/monitoring`);

      // Verify timeout message
      await expect(page.locator('[data-testid="timeout-message"]')).toBeVisible({ timeout: 12000 });
    });
  });

  /**
   * Test Suite 5: Responsive Design
   */
  test.describe('Responsive Design', () => {
    const viewports = [
      { width: 1920, height: 1080 },  // Desktop
      { width: 1366, height: 768 },   // Tablet
      { width: 1280, height: 720 },   // Small Tablet
    ];

    viewports.forEach((viewport) => {
      test(`should render correctly on ${viewport.width}x${viewport.height}`, async ({ page }) => {
        await page.setViewportSize(viewport.width, viewport.height);
        await page.goto(`${BASE_URL}/dashboard`);

        // Verify main layout is visible
        await expect(page.locator('[data-testid="main-layout"]')).toBeVisible();

        // Verify sidebar adapts (hidden on mobile)
        if (viewport.width < 1366) {
          await expect(page.locator('[data-testid="sidebar"]')).not.toBeVisible();
        } else {
          await expect(page.locator('[data-testid="sidebar"]')).toBeVisible();
        }

        // Verify menu adapts (hamburger menu on mobile)
        if (viewport.width < 1366) {
          await expect(page.locator('[data-testid="hamburger-menu"]')).toBeVisible();
        } else {
          await expect(page.locator('[data-testid="hamburger-menu"]')).not.toBeVisible();
        }
      });
    });
  });

  /**
   * Test Suite 6: Performance Metrics
   */
  test.describe('Performance Metrics', () => {
    test('should load homepage within performance budget', async ({ page }) => {
      const startTime = Date.now();

      await page.goto(`${BASE_URL}/`);

      const loadTime = Date.now() - startTime;

      // Verify page loads in under 3 seconds
      await expect(loadTime).toBeLessThan(3000);
    });

    test('should render charts efficiently', async ({ page }) => {
      await page.goto(`${BASE_URL}/analysis');

      // Wait for chart to render
      await page.waitForSelector('[data-testid="chart-canvas"]', { state: 'visible' });

      const renderStart = Date.now();
      await page.click('[data-testid="refresh-chart"]');
      await page.waitForSelector('[data-testid="chart-canvas"]', { state: 'visible' });

      const renderTime = Date.now() - renderStart;

      // Chart should update in under 1 second
      await expect(renderTime).toBeLessThan(1000);
    });
  });

  /**
   * Test Suite 7: Accessibility
   */
  test.describe('Accessibility', () => {
    test('should have proper ARIA labels', async ({ page }) => {
      await page.goto(`${BASE_URL}/dashboard`);

      // Verify all inputs have labels
      const inputs = page.locator('input[type="text"], 'input[type="password"]');
      const count = await inputs.count();

      for (let i = 0; i < count; i++) {
        const input = inputs.nth(i);
        await expect(input).toHaveAttribute('aria-label');
      }
    });

    test('should be keyboard navigable', async ({ page }) => {
      await page.goto(`${BASE_URL}/monitoring`);

      // Verify all interactive elements are keyboard accessible
      await page.keyboard.press('Tab');
      await expect(page.locator('[data-testid="search-input"]')).toBeFocused();
      await page.keyboard.press('Enter');
    });
  });

  /**
   * Test Suite 8: Cross-Browser Compatibility
   */
  test.describe('Cross-Browser Compatibility', () => {
    const browsers = ['chromium', 'firefox', 'webkit'];

    browsers.forEach((browserName) => {
      test(`should work in ${browserName}`, async ({ page, browserName }) => {
        await page.goto(`${BASE_URL}/login`);
        await page.fill('[data-testid="username-input"]', 'admin');
        await page.fill('[data-testid="password-input"]', 'admin123');
        await page.click('[data-testid="submit-button"]');

        // Verify successful login
        await expect(page).toHaveURL(`${BASE_URL}/dashboard`);
      });
    });
  });
});
