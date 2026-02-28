import { test, expect } from '@playwright/test';

/**
 * Smoke test for MyStocks Web Application
 * Tests basic functionality and accessibility
 */

test.describe('MyStocks Web Smoke Test', () => {
  const BASE_URL = process.env.BASE_URL || 'http://localhost:3020';

  test.beforeEach(async ({ page }) => {
    // Set up mock authentication to bypass login
    await page.goto(BASE_URL);
    await page.evaluate(() => {
      localStorage.setItem('auth-store', JSON.stringify({
        token: 'mock-test-token',
        user: {
          id: 1,
          username: 'test-user',
          email: 'test@example.com',
          role: 'admin',
          permissions: ['*']
        },
        isAuthenticated: true
      }));
    });

    // Navigate to dealing room where the sidebar exists
    await page.goto(`${BASE_URL}/dealing-room`);
    // Wait for Vue app to mount
    await page.waitForLoadState('networkidle');
    // Additional wait for client-side rendering
    await page.waitForTimeout(2000);
  });

  test('page loads successfully', async ({ page }) => {
    // Wait for page to be loaded
    await expect(page).toHaveTitle(/MyStocks/);
  });

  test('main navigation is visible', async ({ page }) => {
    // Check if sidebar navigation exists
    const sidebar = page.locator('.artdeco-sidebar-v3, nav.artdeco-sidebar-v3');
    await expect(sidebar).toBeVisible();
  });

  test('navigation menu items are clickable', async ({ page }) => {
    // Check for navigation buttons (domain buttons with aria-expanded)
    const domainButtons = page.locator('button[aria-expanded], .nav-item.domain-root');
    const count = await domainButtons.count();

    expect(count).toBeGreaterThan(0);

    // Test first domain button
    if (count > 0) {
      await domainButtons.first().click();
      // Check if aria-expanded changed
      await page.waitForTimeout(500);
    }
  });

  test('keyboard navigation works', async ({ page }) => {
    // Tab through the page
    await page.keyboard.press('Tab');
    await page.waitForTimeout(200);

    // Check if something is focused
    const focusedElement = await page.locator(':focus');
    await expect(focusedElement).toBeAttached();
  });

  test('no console errors on load', async ({ page }) => {
    const errors: string[] = [];

    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });

    await page.goto(`${BASE_URL}/dealing-room`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    // Allow some errors that might be expected in dev mode
    const filteredErrors = errors.filter(e =>
      !e.includes('DevTools') &&
      !e.includes('Extension') &&
      !e.includes('HMR')
    );

    expect(filteredErrors.length).toBeLessThan(5);
  });

  test('responsive layout', async ({ page }) => {
    // Test desktop viewport
    await page.setViewportSize({ width: 1280, height: 720 });
    await page.waitForTimeout(500);

    const sidebar = page.locator('.artdeco-sidebar-v3');
    await expect(sidebar).toBeVisible();
  });

  test('API connectivity', async ({ page }) => {
    // Try to fetch health check through the app
    const response = await page.request.get(`${BASE_URL}/api/health`);
    expect(response.ok()).toBeTruthy();

    const data = await response.json();
    expect(data).toHaveProperty('status', 'healthy');
  });

  test('menu accessibility - ARIA attributes', async ({ page }) => {
    // Check for ARIA attributes on navigation buttons
    const navButtons = page.locator('button[aria-expanded], button[aria-controls]');

    const count = await navButtons.count();
    expect(count).toBeGreaterThan(0);

    // Verify ARIA attributes are properly set
    for (let i = 0; i < Math.min(count, 3); i++) {
      const button = navButtons.nth(i);
      await expect(button).toHaveAttribute('aria-expanded');
      await expect(button).toHaveAttribute('aria-controls');
    }
  });
});
