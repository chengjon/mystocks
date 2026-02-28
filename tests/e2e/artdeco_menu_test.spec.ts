import { test, expect } from '@playwright/test';

/**
 * ArtDeco Menu & Breadcrumb Consistency Test
 * Verifies the fix for "Command Center" -> "Trading Room" and 404s.
 */
test.describe('ArtDeco Menu & Breadcrumb Tests', () => {
  
  test.beforeEach(async ({ page }) => {
    // Listen for console logs
    page.on('console', msg => {
        if (msg.type() === 'error' || msg.text().includes('Failed to load')) {
            console.log(`BROWSER ERROR LOG: ${msg.text()}`);
        }
    });
    
    // Listen for failed network requests
    page.on('requestfailed', request => {
        console.log(`NETWORK FAIL: ${request.url()} - ${request.failure()?.errorText}`);
    });

    page.on('response', response => {
        if (response.status() >= 400) {
            console.log(`HTTP ERROR ${response.status()}: ${response.url()}`);
        }
    });

    page.on('pageerror', err => console.log(`PAGE ERROR: ${err}`));

    // Basic login if needed
    await page.goto('/', { waitUntil: 'networkidle' });
    if (page.url().includes('/login')) {
      await page.fill('[data-testid="username-input"]', 'admin');
      await page.fill('[data-testid="password-input"]', 'admin123');
      await page.click('[data-testid="login-button"]');
      await expect(page).toHaveURL(/\/dealing-room$/, { timeout: 10000 });
    }
  });

  test('Dashboard should have correct title "QUANTIX"', async ({ page }) => {
    // We should already be on /dealing-room from beforeEach
    // Only goto if not there (which avoids clearing in-memory state if that's the issue)
    if (!page.url().endsWith('/dealing-room')) {
        await page.goto('/dealing-room');
    }
    console.log('Current URL:', page.url());
    
    try {
      // Check the main header title
      const headerTitle = page.locator('.artdeco-header .header-title');
      await expect(headerTitle).toContainText('QUANTIX', { timeout: 5000 });
    } catch (e) {
      console.log('Test Failed. Dumping content:');
      console.log(await page.content());
      throw e;
    }
    
    // Check the browser tab title (document.title)
    await expect(page).toHaveTitle(/交易室 - MyStocks/);
  });

  // Helper function for navigation
  const navigateTo = async (page: any, domain: string, item: string) => {
      // Find domain group
      // Target the clickable .domain-root specifically
      const domainGroup = page.locator('.nav-domain-group', { hasText: domain }).locator('.domain-root');
      
      // Check if child is visible
      const navItem = page.locator('a.nav-item', { hasText: item });
      
      if (!(await navItem.isVisible())) {
          await domainGroup.click();
      }
      
      await expect(navItem).toBeVisible();
      await navItem.click();
  };

  test('Breadcrumbs should show "交易室" and link correctly', async ({ page }) => {
    // Navigate to Market -> Realtime using UI
    await navigateTo(page, '市场行情', '实时行情流');
    
    await expect(page).toHaveURL(/\/market\/realtime$/);
    
    // Check breadcrumb container exists
    const breadcrumbNav = page.locator('.artdeco-breadcrumb');
    await expect(breadcrumbNav).toBeVisible();
    
    // Check for "交易室" in breadcrumbs
    const homeBreadcrumb = breadcrumbNav.locator('.breadcrumb-link').first();
    await expect(homeBreadcrumb).toContainText('交易室');
    
    // Click the home breadcrumb
    await homeBreadcrumb.click();
    
    // Verify we are back at the dealing room
    await expect(page).toHaveURL(/\/dealing-room$/);
    
    // Verify we are NOT on a 404 page
    const notFound = page.locator('text=Page Not Found');
    await expect(notFound).not.toBeVisible();
  });

  test('Verify critical menu items do not return 404', async ({ page }) => {
    // Test a few items
    // 1. Strategy Repo
    await navigateTo(page, '策略管理', '策略仓库');
    await expect(page).toHaveURL(/\/strategy\/repo$/);
    await expect(page.locator('.artdeco-breadcrumb')).toBeVisible();

    // 2. System Health
    await navigateTo(page, '系统设置', '健康矩阵');
    await expect(page).toHaveURL(/\/system\/health$/);
    await expect(page.locator('.artdeco-breadcrumb')).toBeVisible();
    
    // 3. Risk Overview
    await navigateTo(page, '风险管理', '风险概览');
    await expect(page).toHaveURL(/\/risk\/overview$/);
    await expect(page.locator('.artdeco-breadcrumb')).toBeVisible();
  });

});
