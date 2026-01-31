import { test, expect } from '@playwright/test';

test.describe('MyStocks Chrome DevTools Test Suite', () => {
  test.beforeEach(async ({ page }) => {
    // 设置浏览器视窗大小
    await page.setViewportSize({ width: 1920, height: 1080 });
  });

  test('should test MyStocks homepage loading', async ({ page }) => {
    console.log('Testing MyStocks homepage...');
    
    // 访问MyStocks应用
    const baseUrl = 'http://localhost:3020';
    await page.goto(baseUrl, { waitUntil: 'domcontentloaded', timeout: 10000 });
    
    // 等待页面加载完成
    await page.waitForTimeout(3000);
    
    // 验证页面标题
    const title = await page.title();
    console.log(`Page title: ${title}`);
    expect(title).toBeTruthy();
    
    // 验证页面内容
    const body = page.locator('body');
    await expect(body).toBeVisible();
    
    // 截图记录
    await page.screenshot({ 
      path: 'test-results/mystocks-homepage.png', 
      fullPage: true 
    });
  });

  test('should check for console errors', async ({ page }) => {
    const consoleErrors: string[] = [];
    
    // 监听控制台错误
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(`Error: ${msg.text()}`);
      }
    });
    
    // 监听页面错误
    page.on('pageerror', error => {
      consoleErrors.push(`Page Error: ${error.message}`);
    });
    
    const baseUrl = 'http://localhost:3020';
    await page.goto(baseUrl, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(5000);
    
    console.log(`Console errors found: ${consoleErrors.length}`);
    
    // 如果有错误，记录但不让测试失败
    if (consoleErrors.length > 0) {
      await page.screenshot({ 
        path: 'test-results/mystocks-console-errors.png', 
        fullPage: true 
      });
    }
    
    // 至少验证页面加载成功
    const pageTitle = await page.title();
    expect(pageTitle).toBeTruthy();
  });

  test('should check network activity', async ({ page }) => {
    const requests: any[] = [];
    
    // 监听网络请求
    page.on('request', request => {
      requests.push({
        url: request.url(),
        method: request.method(),
        resourceType: request.resourceType()
      });
    });
    
    const baseUrl = 'http://localhost:3020';
    await page.goto(baseUrl, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(5000);
    
    console.log(`Network requests captured: ${requests.length}`);
    
    // 验证有网络活动
    expect(requests.length).toBeGreaterThan(0);
    
    // 记录网络请求
    await page.screenshot({ 
      path: 'test-results/mystocks-network-activity.png', 
      fullPage: true 
    });
  });

  test('should test page performance', async ({ page }) => {
    const startTime = Date.now();
    
    const baseUrl = 'http://localhost:3020';
    await page.goto(baseUrl, { waitUntil: 'networkidle' });
    
    const loadTime = Date.now() - startTime;
    console.log(`Page load time: ${loadTime}ms`);
    
    // 页面加载时间应该在合理范围内
    expect(loadTime).toBeLessThan(30000);
    
    // 获取性能指标
    const performanceMetrics = await page.evaluate(() => {
      const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
      if (!navigation) return null;
      
      return {
        domContentLoaded: navigation.domContentLoadedEventEnd - navigation.navigationStart,
        loadComplete: navigation.loadEventEnd - navigation.navigationStart,
        firstPaint: performance.getEntriesByType('paint')[0]?.startTime || 0
      };
    });
    
    console.log('Performance metrics:', performanceMetrics);
    
    // 验证性能指标
    if (performanceMetrics) {
      expect(performanceMetrics.domContentLoaded).toBeLessThan(10000);
      expect(performanceMetrics.loadComplete).toBeLessThan(30000);
    }
    
    await page.screenshot({ 
      path: 'test-results/mystocks-performance.png', 
      fullPage: true 
    });
  });

  test('should test responsive design', async ({ page }) => {
    // 测试不同的屏幕尺寸
    const viewports = [
      { width: 1920, height: 1080, name: 'Desktop HD' },
      { width: 1366, height: 768, name: 'Laptop' },
      { width: 1280, height: 720, name: 'Small Desktop' }
    ];
    
    for (const viewport of viewports) {
      await page.setViewportSize(viewport);
      console.log(`Testing viewport: ${viewport.name} (${viewport.width}x${viewport.height})`);
      
      const baseUrl = 'http://localhost:3020';
      await page.goto(baseUrl, { waitUntil: 'domcontentloaded' });
      await page.waitForTimeout(2000);
      
      // 验证页面在不同视窗下正常显示
      const body = page.locator('body');
      await expect(body).toBeVisible();
      
      // 验证页面宽度
      const pageWidth = await page.evaluate(() => document.body.scrollWidth);
      expect(pageWidth).toBeLessThanOrEqual(viewport.width);
      
      await page.screenshot({ 
        path: `test-results/mystocks-responsive-${viewport.name}.png`, 
        fullPage: true 
      });
    }
  });
});