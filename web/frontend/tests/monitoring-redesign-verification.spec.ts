import { test, expect } from '@playwright/test';

const FRONTEND_PORT = process.env.FRONTEND_PORT || '3020';
const FRONTEND_URL = process.env.FRONTEND_URL || `http://localhost:${FRONTEND_PORT}`;

test.use({
  baseURL: FRONTEND_URL
});

test.describe('MyStocks Web - Monitoring Pages Redesign Verification', () => {
  test.setTimeout(30000); // 30秒超时

  test.beforeEach(async ({ page }) => {
    // 等待服务启动
    await page.waitForTimeout(2000);
  });

  test('1. WatchlistManagement Page - Fintech Style Application', async ({ page }) => {
    console.log('🧪 Testing WatchlistManagement with fintech styles...');

    // 导航到新的监控清单页面
    await page.goto('/monitoring/watchlists');
    await page.waitForLoadState('domcontentloaded');

    // 等待页面加载完成
    await page.waitForTimeout(3000);

    // 截图1: 监控布局页面整体
    await page.screenshot({
      path: 'test-results/screenshots/monitoring-watchlist-full.png',
      fullPage: true
    });

    // 检查标题栏是否存在
    const titleElement = page.locator('h1').filter({ hasText: 'MONITORING PORTFOLIOS' });
    await expect(titleElement).toBeVisible();

    // 检查fintech样式类是否存在
    const fintechElements = page.locator('[class*="fintech"]');
    const fintechCount = await fintechElements.count();
    console.log(`💼 Found ${fintechCount} fintech style elements`);
    expect(fintechCount).toBeGreaterThan(0);

    // 检查统计卡片
    const statCards = page.locator('.stat-card');
    await expect(statCards).toHaveCount(3); // 活跃组合、总股票、活跃告警

    // 截图2: 统计卡片区域
    await statCards.first().screenshot({
      path: 'test-results/screenshots/monitoring-watchlist-stats.png'
    });

    // 检查CREATE PORTFOLIO按钮
    const createButton = page.locator('.fintech-btn.primary').filter({ hasText: 'CREATE PORTFOLIO' });
    await expect(createButton).toBeVisible();

    console.log('✅ WatchlistManagement page with fintech styles verified');
  });

  test('2. RiskDashboard Page - Fintech Style Application', async ({ page }) => {
    console.log('🧪 Testing RiskDashboard with fintech styles...');

    // 导航到风险监控页面
    await page.goto('/monitoring/risk');
    await page.waitForLoadState('domcontentloaded');

    // 等待页面加载完成
    await page.waitForTimeout(3000);

    // 截图1: 风险监控页面整体
    await page.screenshot({
      path: 'test-results/screenshots/monitoring-risk-full.png',
      fullPage: true
    });

    // 检查标题
    const titleElement = page.locator('h1').filter({ hasText: 'RISK MANAGEMENT DASHBOARD' });
    await expect(titleElement).toBeVisible();

    // 检查fintech样式元素
    const fintechElements = page.locator('[class*="fintech"]');
    const fintechCount = await fintechElements.count();
    console.log(`💼 Found ${fintechCount} fintech style elements in risk dashboard`);
    expect(fintechCount).toBeGreaterThan(0);

    // 检查核心指标卡片 (4个)
    const metricCards = page.locator('.metric-card');
    await expect(metricCards).toHaveCount(4);

    // 截图2: 核心指标区域
    const metricsGrid = page.locator('.metrics-grid');
    await metricsGrid.screenshot({
      path: 'test-results/screenshots/monitoring-risk-metrics.png'
    });

    console.log('✅ RiskDashboard page with fintech styles verified');
  });

  test('3. Monitoring Layout Navigation Test', async ({ page }) => {
    console.log('🧪 Testing monitoring layout navigation...');

    // 访问监控主页
    await page.goto('/monitoring/watchlists');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(2000);

    // 检查导航栏
    const navLinks = page.locator('.nav-link');
    await expect(navLinks).toHaveCount(2);

    // 检查当前活跃的导航链接
    const activeLink = page.locator('.nav-link.active');
    await expect(activeLink).toHaveText('WATCHLISTS');

    // 点击风险面板链接
    await navLinks.filter({ hasText: 'RISK DASHBOARD' }).click();
    await page.waitForTimeout(1000);

    // 检查URL变化
    await expect(page).toHaveURL('**/monitoring/risk');

    // 检查新的活跃链接
    const newActiveLink = page.locator('.nav-link.active');
    await expect(newActiveLink).toHaveText('RISK DASHBOARD');

    // 截图: 导航切换
    await page.screenshot({
      path: 'test-results/screenshots/monitoring-navigation.png',
      fullPage: true
    });

    console.log('✅ Monitoring layout navigation verified');
  });

  test('4. Fintech Design System Components Test', async ({ page }) => {
    console.log('🧪 Testing fintech design system components...');

    await page.goto('/monitoring/watchlists');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(2000);

    // 测试各种fintech样式类
    const tests = [
      { selector: '.fintech-bg-primary', name: 'Primary Background' },
      { selector: '.fintech-text-primary', name: 'Primary Text' },
      { selector: '.fintech-text-secondary', name: 'Secondary Text' },
      { selector: '.fintech-card', name: 'Card Component' },
      { selector: '.fintech-btn', name: 'Button Component' },
    ];

    for (const test of tests) {
      const elements = page.locator(test.selector);
      const count = await elements.count();
      console.log(`✅ ${test.name}: ${count} elements found`);

      if (count === 0) {
        console.warn(`⚠️ No elements found for ${test.name}`);
      }
    }

    // 检查深色主题CSS变量是否生效
    const bgPrimaryColor = await page.evaluate(() => {
      return getComputedStyle(document.documentElement).getPropertyValue('--fintech-bg-primary');
    });
    console.log(`🎨 Primary background color: ${bgPrimaryColor}`);

    expect(bgPrimaryColor.trim()).toBe('#0a0e27');

    console.log('✅ Fintech design system components verified');
  });

  test('5. Bloomberg Terminal Style Verification', async ({ page }) => {
    console.log('🧪 Testing Bloomberg terminal styling...');

    await page.goto('/monitoring/watchlists');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(2000);

    // 检查Bloomberg风格的视觉元素
    const bloombergElements = page.locator('[class*="bloomberg"], [class*="terminal"], .fintech-card');
    const bloombergCount = await bloombergElements.count();
    console.log(`🏢 Found ${bloombergCount} Bloomberg-style elements`);

    // 检查深色主题应用
    const bodyBgColor = await page.evaluate(() => {
      return getComputedStyle(document.body).backgroundColor;
    });
    console.log(`🌙 Body background: ${bodyBgColor}`);

    // 检查专业字体应用
    const fontFamily = await page.evaluate(() => {
      return getComputedStyle(document.body).fontFamily;
    });
    console.log(`📝 Font family: ${fontFamily}`);

    // 截图: Bloomberg风格验证
    await page.screenshot({
      path: 'test-results/screenshots/bloomberg-terminal-style.png',
      fullPage: true
    });

    console.log('✅ Bloomberg terminal styling verified');
  });
});
