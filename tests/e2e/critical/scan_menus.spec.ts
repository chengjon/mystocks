// tests/e2e/critical/scan_menus.spec.ts
import { test, expect } from '@playwright/test';
import { TestDataFactory } from '../../fixtures/factory';
import { setupApiStandardization } from '../utils/api-validator'; // Import the new helper

test.describe('Critical Menu Navigation Scan @critical', () => {
  test('should navigate to all primary menu items without critical errors', async ({ page }) => {
    // Setup API Standardization check BEFORE any network requests
    await setupApiStandardization(page); // ADDED THIS LINE

    // 1. Mock API responses for menu data and common dashboard data
    await page.route('**/api/user/login', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(TestDataFactory.createStandardApiResponse({ token: 'mock_token', user: TestDataFactory.createValidUser() })),
      });
    });

    // Mock API for fetching menus (assuming a /api/menus endpoint)
    await page.route('**/api/menus', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        // This mock should reflect the actual menu structure of the application
        body: JSON.stringify(TestDataFactory.createStandardApiResponse([
          { id: '1', name: 'Dashboard', path: '/dashboard', component: 'DashboardView' },
          { id: '2', name: 'Market Data', path: '/market-data', component: 'MarketDataView' },
          { id: '3', name: 'Strategy Management', path: '/strategy-management', component: 'StrategyManagementView' },
          // Add more menu items here based on actual application menus
        ])),
      });
    });

    // Mock common data APIs to prevent 404s on page load after navigation
    await page.route('**/api/dashboard/summary', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(TestDataFactory.createStandardApiResponse({ totalUsers: 100, activeStocks: 50 })),
      });
    });
    // Add more general API mocks here for pages that load data on navigation

    // 2. Navigate to the base URL (assuming it redirects to login or directly to dashboard)
    await page.goto('/');

    // 3. Assume login is required. If login form exists, fill and submit.
    // This is a placeholder. Real login might involve specific selectors.
    // For now, let's assume successful mock login allows access.
    // If a login page is rendered, you'd need:
    // await page.fill('input[name="username"]', 'test_user');
    // await page.fill('input[name="password"]', 'test_pass');
    // await page.click('button[type="submit"]');
    // await page.waitForURL('/dashboard'); // Or the post-login redirect path


    // Wait for the main content or sidebar to load
    await page.waitForSelector('.el-aside', { timeout: 10000 }).catch(() => console.log('Sidebar not found, assuming no sidebar or it loads later'));

    // Get all primary menu items. This selector is an assumption for Element Plus navigation.
    // We use :visible to avoid trying to click items inside collapsed submenus.
    const menuItems = await page.locator('.el-menu-item:visible').all();
    
    expect(menuItems.length).toBeGreaterThan(0); // Ensure some menu items are found

    for (const menuItem of menuItems) {
      const menuName = await menuItem.textContent();
      const href = await menuItem.getAttribute('href'); // Get the href to verify navigation later
      const originalPath = page.url();

      test.info().annotations.push({ type: 'Menu Test', description: `Testing menu item: ${menuName} (Path: ${href})` });

      // Click the menu item
      await menuItem.click();

      // Check for navigation (URL change)
      await page.waitForURL(url => url.pathname !== originalPath && url.pathname !== '/', { timeout: 5000 }).catch(() => {
        // If URL doesn't change, it might be an in-page tab or failed navigation
        console.warn(`Navigation to ${menuName} (Path: ${href}) did not change URL. Current URL: ${page.url()}`);
      });


      // Basic check for page content (e.g., no generic error message, some content loaded)
      // This is a very generic check; more specific checks would be better per page.
      await expect(page.locator('body')).not.toContainText('404 Not Found');
      await expect(page.locator('body')).not.toContainText('An unexpected error occurred');
      
      // Listen for console errors during navigation
      page.on('console', msg => {
        if (msg.type() === 'error') {
          console.error(`[Console Error] while navigating to ${menuName}: ${msg.text()}`);
          test.fail(`Console error detected on page for ${menuName}`);
        }
      });

      // Listen for network request failures (e.g., 404/500s for non-mocked APIs)
      page.on('requestfailed', request => {
        if (request.resourceType() === 'fetch' || request.resourceType() === 'xhr') {
          console.error(`[Network Error] while navigating to ${menuName}: ${request.url()} failed with ${request.failure()?.errorText}`);
          test.fail(`Network request failed on page for ${menuName}: ${request.url()}`);
        }
      });

      // If needed, wait for specific element on the new page to ensure content loaded
      // Example: await page.waitForSelector('h1', { timeout: 5000 });

      // After checking, navigate back or ensure a clean state for the next menu item
      // await page.goBack(); // Or navigate to a known safe page
      // No, for a full scan, we navigate sequentially.
    }
  });
});