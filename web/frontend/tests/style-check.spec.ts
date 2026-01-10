import { test, expect } from '@playwright/test';

// 设置前端端口为3001（因为3000被占用）
test.use({
  baseURL: 'http://localhost:3001'
});

test.describe('MyStocks - Existing Pages Style Check', () => {
  test.setTimeout(15000);

  test('Check if fintech styles are applied to existing pages', async ({ page }) => {
    console.log('🧪 Checking existing pages for fintech styles...');

    // 测试仪表盘页面
    await page.goto('/dashboard');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(3000);

    // 检查页面是否有任何内容
    const bodyText = await page.locator('body').textContent();
    console.log(`📄 Dashboard page content length: ${bodyText?.length || 0}`);

    // 检查fintech样式类
    const fintechElements = page.locator('[class*="fintech"]');
    const fintechCount = await fintechElements.count();
    console.log(`💼 Fintech style elements in dashboard: ${fintechCount}`);

    // 检查bloomberg样式类
    const bloombergElements = page.locator('[class*="bloomberg"]');
    const bloombergCount = await bloombergElements.count();
    console.log(`🏢 Bloomberg style elements in dashboard: ${bloombergCount}`);

    // 检查CSS变量
    const cssVars = await page.evaluate(() => {
      const styles = getComputedStyle(document.documentElement);
      return {
        bgPrimary: styles.getPropertyValue('--fintech-bg-primary'),
        textPrimary: styles.getPropertyValue('--fintech-text-primary'),
        accentPrimary: styles.getPropertyValue('--fintech-accent-primary')
      };
    });

    console.log('🎨 CSS Variables:');
    console.log(`  --fintech-bg-primary: ${cssVars.bgPrimary}`);
    console.log(`  --fintech-text-primary: ${cssVars.textPrimary}`);
    console.log(`  --fintech-accent-primary: ${cssVars.accentPrimary}`);

    // 截图
    await page.screenshot({
      path: 'test-results/screenshots/dashboard-style-check.png',
      fullPage: true
    });

    // 检查页面结构
    const mainContent = page.locator('.dashboard-container, #app > div');
    const hasMainContent = await mainContent.count() > 0;
    console.log(`📱 Has main content: ${hasMainContent}`);

    console.log('✅ Style check completed');
  });

  test('Check if monitoring routes are configured correctly', async ({ page }) => {
    console.log('🧪 Checking monitoring route configuration...');

    // 检查路由配置是否在页面中
    const routeScript = await page.evaluate(() => {
      // 检查是否有Vue路由相关的脚本
      const scripts = Array.from(document.querySelectorAll('script'));
      return scripts.some(script => script.src && script.src.includes('chunk'));
    });

    console.log(`🔧 Has route chunks: ${routeScript}`);

    // 检查网络请求
    const requests = [];
    page.on('request', request => {
      if (request.url().includes('monitoring') || request.url().includes('watchlist')) {
        requests.push(request.url());
      }
    });

    await page.goto('/monitoring/watchlists');
    await page.waitForTimeout(2000);

    console.log(`🌐 Monitoring-related requests: ${requests.length}`);
    requests.forEach(url => console.log(`  - ${url}`));

    // 检查当前URL
    const currentUrl = page.url();
    console.log(`📍 Current URL: ${currentUrl}`);

    console.log('✅ Route configuration check completed');
  });
});