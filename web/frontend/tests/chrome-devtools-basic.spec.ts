import { test, expect } from '@playwright/test';

test.describe('Chrome DevTools Basic Functionality Test', () => {
  const BASE_URL = process.env.BASE_URL || 'http://localhost:3020';

  test('should load the main application', async ({ page }) => {
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(3000);
    
    const title = await page.title();
    console.log(`Page title: ${title}`);
    
    const body = page.locator('body');
    await expect(body).toBeVisible();
    
    await page.screenshot({ 
      path: 'test-results/homepage-loaded.png', 
      fullPage: true 
    });
  });

  test('should check browser console for errors', async ({ page }) => {
    const consoleMessages: string[] = [];
    
    page.on('console', msg => {
      const type = msg.type();
      const text = msg.text();
      console.log(`Console [${type}]: ${text}`);
      
      if (type === 'error') {
        consoleMessages.push(`ERROR: ${text}`);
      }
    });
    
    page.on('pageerror', error => {
      console.error('Page Error:', error.message);
      consoleMessages.push(`PAGE_ERROR: ${error.message}`);
    });
    
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(5000);
    
    if (consoleMessages.length > 0) {
      console.log('Console messages found:', consoleMessages);
      await page.screenshot({ 
        path: 'test-results/console-errors.png', 
        fullPage: true 
      });
    }
  });

  test('should check network requests', async ({ page }) => {
    const requests: string[] = [];
    
    page.on('request', request => {
      const url = request.url();
      if (url.includes('/api/') || url.includes('/static/')) {
        requests.push(`${request.method()} ${url}`);
        console.log('Request:', `${request.method()} ${url}`);
      }
    });
    
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(5000);
    
    console.log(`Total requests captured: ${requests.length}`);
    expect(requests.length).toBeGreaterThan(0);
    
    await page.screenshot({ 
      path: 'test-results/network-requests.png', 
      fullPage: true 
    });
  });

  test('should check page performance metrics', async ({ page }) => {
    const startTime = Date.now();
    
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
    await page.waitForLoadState('networkidle');
    
    const loadTime = Date.now() - startTime;
    console.log(`Page load time: ${loadTime}ms`);
    
    const performanceMetrics = await page.evaluate(() => {
      const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
      if (!navigation) return { loadTime: 0 };
      
      return {
        domContentLoaded: navigation.domContentLoadedEventEnd - navigation.navigationStart,
        loadComplete: navigation.loadEventEnd - navigation.navigationStart,
        totalTime: navigation.loadEventEnd - navigation.navigationStart
      };
    });
    
    console.log('Performance metrics:', performanceMetrics);
    
    expect(loadTime).toBeLessThan(30000);
    expect(performanceMetrics.totalTime).toBeLessThan(30000);
  });
});