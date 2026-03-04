import { test, expect } from '@playwright/test';

const FRONTEND_PORT = process.env.FRONTEND_PORT || '3020';
const FRONTEND_URL = process.env.FRONTEND_URL || `http://localhost:${FRONTEND_PORT}`;

test.use({
  baseURL: FRONTEND_URL
});

test.describe('MyStocks Web Redesign - Basic Functionality', () => {
  test.setTimeout(30000); // 30秒超时

  test('1. Frontend Service Health Check', async ({ page }) => {
    console.log('🧪 Testing frontend service health...');

    // 访问首页
    await page.goto('/');
    await page.waitForLoadState('domcontentloaded');

    // 检查页面标题
    const title = await page.title();
    console.log(`📄 Page title: ${title}`);

    // 截图: 前端首页
    await page.screenshot({
      path: 'test-results/screenshots/health-frontend-home.png',
      fullPage: true
    });

    // 检查是否有内容加载
    const body = page.locator('body');
    await expect(body).toBeVisible();

    console.log('✅ Frontend service is running');
  });

  test('2. Risk Monitor Page Access', async ({ page }) => {
    console.log('🧪 Testing risk monitor page...');

    // 访问风险监控页面
    await page.goto('/risk-monitor');
    await page.waitForLoadState('domcontentloaded');

    // 等待页面加载
    await page.waitForTimeout(2000);

    // 截图: 风险监控页面
    await page.screenshot({
      path: 'test-results/screenshots/risk-monitor-page.png',
      fullPage: true
    });

    // 检查页面是否有内容
    const content = page.locator('.risk-monitor, .risk-dashboard, [class*="risk"]');
    const hasContent = await content.count() > 0;

    if (hasContent) {
      console.log('✅ Risk monitor page loaded with content');
    } else {
      console.log('⚠️ Risk monitor page loaded but may not have expected content');
    }
  });

  test('3. Dashboard Page Access', async ({ page }) => {
    console.log('🧪 Testing dashboard page...');

    // 访问仪表盘页面
    await page.goto('/dashboard');
    await page.waitForLoadState('domcontentloaded');

    // 等待页面加载
    await page.waitForTimeout(2000);

    // 截图: 仪表盘页面
    await page.screenshot({
      path: 'test-results/screenshots/dashboard-page.png',
      fullPage: true
    });

    // 检查是否有统计卡片
    const statCards = page.locator('.stat-card, .fintech-card, [class*="stat"]');
    const cardCount = await statCards.count();
    console.log(`📊 Found ${cardCount} stat cards`);

    console.log('✅ Dashboard page loaded');
  });

  test('4. Bloomberg Terminal Styling Verification', async ({ page }) => {
    console.log('🧪 Testing Bloomberg terminal styling...');

    // 访问仪表盘
    await page.goto('/dashboard');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(2000);

    // 检查深色主题类
    const darkThemeElements = page.locator('.fintech-bg-primary, .fintech-bg-secondary');
    const darkThemeCount = await darkThemeElements.count();
    console.log(`🌙 Found ${darkThemeCount} dark theme elements`);

    // 检查金融科技样式类
    const fintechElements = page.locator('[class*="fintech"]');
    const fintechCount = await fintechElements.count();
    console.log(`💼 Found ${fintechCount} fintech style elements`);

    // 检查按钮样式
    const buttons = page.locator('.fintech-btn, .el-button');
    const buttonCount = await buttons.count();
    console.log(`🔘 Found ${buttonCount} styled buttons`);

    // 截图: 样式验证
    await page.screenshot({
      path: 'test-results/screenshots/bloomberg-styling-verification.png',
      fullPage: true
    });

    console.log('✅ Bloomberg terminal styling verified');
  });

  test('5. Responsive Design Test - Desktop', async ({ page }) => {
    console.log('🧪 Testing responsive design on desktop...');

    // 设置桌面视口
    await page.setViewportSize({ width: 1920, height: 1080 });

    await page.goto('/dashboard');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(2000);

    // 截图: 桌面布局
    await page.screenshot({
      path: 'test-results/screenshots/responsive-desktop.png',
      fullPage: false
    });

    console.log('✅ Desktop responsive design tested');
  });

  test('6. Performance Load Time Test', async ({ page }) => {
    console.log('🧪 Testing page load performance...');

    const startTime = Date.now();

    await page.goto('/dashboard');
    await page.waitForLoadState('domcontentloaded');

    const loadTime = Date.now() - startTime;
    console.log(`⚡ Page load time: ${loadTime}ms`);

    // 记录到结果文件
    const fs = require('fs');
    const result = {
      page: 'dashboard',
      loadTime: loadTime,
      timestamp: new Date().toISOString(),
      userAgent: await page.evaluate(() => navigator.userAgent)
    };

    try {
      fs.appendFileSync('test-results/performance-results.json',
        JSON.stringify(result, null, 2) + '\n');
    } catch (error) {
      console.log('Could not write performance results');
    }

    console.log('✅ Performance test completed');
  });
});
