import { test, expect } from '@playwright/test';

const FRONTEND_PORT = process.env.FRONTEND_PORT || '3020';
const FRONTEND_URL = process.env.FRONTEND_URL || `http://localhost:${FRONTEND_PORT}`;

test.use({
  baseURL: FRONTEND_URL
});

test.describe('MyStocks - Quick Route Test', () => {
  test.setTimeout(10000);

  test('Check monitoring routes are accessible', async ({ page }) => {
    console.log('🧪 Checking monitoring routes...');

    // 测试监控清单页面
    await page.goto('/monitoring/watchlists');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(2000);

    // 截图看看实际加载了什么
    await page.screenshot({
      path: 'test-results/screenshots/quick-route-check.png',
      fullPage: true
    });

    // 检查页面是否有任何内容
    const bodyText = await page.locator('body').textContent();
    console.log(`📄 Page content length: ${bodyText?.length || 0}`);

    // 检查是否有错误信息
    const errorElements = page.locator('.error, .not-found, [class*="error"]');
    const errorCount = await errorElements.count();
    console.log(`❌ Error elements found: ${errorCount}`);

    // 检查路由相关的元素
    const routerElements = page.locator('[class*="router"], [class*="view"]');
    const routerCount = await routerElements.count();
    console.log(`🔗 Router elements found: ${routerCount}`);

    // 检查控制台错误
    const errors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });

    await page.waitForTimeout(1000);

    if (errors.length > 0) {
      console.log(`🚨 Console errors: ${errors.length}`);
      errors.forEach(error => console.log(`  - ${error}`));
    } else {
      console.log('✅ No console errors');
    }

    // 检查页面标题
    const title = await page.title();
    console.log(`📋 Page title: "${title}"`);

    console.log('✅ Route check completed');
  });
});
